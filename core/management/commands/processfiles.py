import logging, os, datetime, pytz, pickle

from django.core.management.base import BaseCommand, CommandError

from MAKDataHub.services import Services

from ProfileCreator.parsers.event_parser import EventType
from core.models import DataFileInfo, Device, ProfileInfo

class Command(BaseCommand):
    help = 'Performs data processing'
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_extraction_service = Services.data_extraction_service()
        self.data_file_service = Services.data_file_service()
        self.device_service = Services.device_service()
        self.storage = Services.storage_service()
        self.ml_service = Services.ml_service()
        self.profile_service = Services.profile_service()

        self.PREUNLOCK_TIME = self.data_extraction_service.PREUNLOCK_TIME
        self.POSTUNLOCK_TIME = self.data_extraction_service.POSTUNLOCK_TIME
        self.CONTINUOUS_AUTH_INTERVAL = self.data_extraction_service.CONTINUOUS_AUTH_INTERVAL

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        try:
            processing_start_date = datetime.datetime.now()

            self.logger.info('Data processing started...')
            run, unlock_data, checkpoint_data = self.perform_data_processing(processing_start_date)
            self.logger.info('Data processing finished...')
            
            self.logger.info('Profile creation started...')
            self.create_profiles(run, unlock_data, checkpoint_data)
            self.logger.info('Profile creation finished...')
        except Exception as e:
            self.logger.exception(e)
            return

    def perform_data_processing(self, processing_start_date):
        devices = [x for x in self.device_service.get_all_devices()]
        device_event_files = { device.id: [x for x in self.data_file_service.get_event_files_for_device(device.id)] for device in devices }
        device_sensor_files = { device.id: [x for x in self.data_file_service.get_sensor_files_for_device(device.id)] for device in devices }

        parsed_event_files = {}
        unlock_data = []
        checkpoint_data = []

        # last_run = self.profile_service.get_last_profile_creation_run()
        # if last_run is not None:
        #     parsed_event_files = pickle.load(last_run.parsed_event_files.open('rb'))
        #     unlock_data.append(pickle.load(last_run.unlock_data.open('rb')))
        #     checkpoint_data.append(pickle.load(last_run.checkpoint_data.open('rb')))
        
        for device in devices:
            event_files = device_event_files[device.id]
            sensor_files = device_sensor_files[device.id]
            self.logger.info(f'Data processing: device {device.id}, {len(event_files)} event files, {len(sensor_files)} sensor files')

            if device.id not in parsed_event_files:
                parsed_event_files[device.id] = set()
            new_event_files = [ef for ef in event_files if ef.id not in parsed_event_files[device.id]]
            parsed_event_files[device.id] = parsed_event_files[device.id].union({ef.id for ef in new_event_files})

            events = self.get_events_from_files(device.id, new_event_files)
            device_unlock_data, device_checkpoint_data = self.process_events(device.id, events, sensor_files)

            if device_unlock_data is not None:
                unlock_data.append(device_unlock_data)
            if device_checkpoint_data is not None:
                checkpoint_data.append(device_checkpoint_data)

        unlock_data = self.data_extraction_service.transform_df_list_to_df(unlock_data)
        checkpoint_data = self.data_extraction_service.transform_df_list_to_df(checkpoint_data)

        run = self.save_processing_results(processing_start_date, unlock_data, checkpoint_data, parsed_event_files)
        return run, unlock_data, checkpoint_data


    def save_processing_results(self, processing_start_date, unlock_data, checkpoint_data, parsed_event_files):
        unlock_data = \
            self.storage.create_pickle_file(unlock_data, processing_start_date, 'unlock_data')
        checkpoint_data = \
            self.storage.create_pickle_file(checkpoint_data, processing_start_date, 'checkpoint_data')
        parsed_event_files = \
            self.storage.create_pickle_file(parsed_event_files, processing_start_date, 'parsed_event_files')

        run = self.profile_service.create_profile_creation_run(processing_start_date, parsed_event_files, unlock_data, checkpoint_data)

        self.storage.dispose(unlock_data)
        self.storage.dispose(checkpoint_data)
        self.storage.dispose(parsed_event_files)

        return run

    def get_events_from_files(self, device_id, new_event_files):
        unlocks = []
        screen_offs = []

        for ef in new_event_files:
            file_unlocks, file_screen_offs = self.data_extraction_service.extract_events(ef.data)

            unlocks += file_unlocks
            screen_offs += file_screen_offs

        self.logger.info(f'Data processing: device {device_id}, {len(new_event_files)} new event files')

        checkpoints = self.data_extraction_service.generate_continuous_auth_checkpoints(unlocks, screen_offs)
        self.logger.info(f'Data processing: device {device_id}, {len(unlocks)} new unlocks')
        self.logger.info(f'Data processing: device {device_id}, {len(checkpoints)} new continuous data points')

        events = unlocks + checkpoints
        events.sort(key=lambda e: e.Timestamp)

        return events

    def process_events(self, device_id, events, sensor_files):
        prev_sensor_file = None
        current_sensor_file = None
        next_sensor_file = None

        prev_reading_list = []
        current_reading_list = []
        next_reading_list = []

        index = 0
        unlock_dfs = []
        checkpoint_dfs = []

        for event_number, event in enumerate(events):
            utc = pytz.UTC
            event_timestamp = event.Timestamp
            event_date = utc.localize(datetime.datetime.utcfromtimestamp(event_timestamp/1000))

            if len(sensor_files) == 0:
                break

            while index < len(sensor_files) - 1 and event_date >= sensor_files[index + 1].start_date:
                index += 1
                prev_sensor_file = current_sensor_file
                current_sensor_file = next_sensor_file
                next_sensor_file = None

                prev_reading_list = current_reading_list
                current_reading_list = next_reading_list
                next_reading_list = []

            if current_sensor_file is None:
                # download current file
                current_sensor_file = sensor_files[index].data
                current_reading_list = \
                    self.data_extraction_service.get_readings_from_sensor_file(current_sensor_file)

            if prev_sensor_file is None and index > 0 \
                    and ( \
                        (event.EventType == EventType.SCREEN_ON and event_date - datetime.timedelta(milliseconds=self.PREUNLOCK_TIME) < sensor_files[index].start_date) \
                        or (event.EventType == EventType.CONTINUOUS_AUTH_CHECKPOINT and event_date - datetime.timedelta(milliseconds=self.CONTINUOUS_AUTH_INTERVAL) < sensor_files[index].start_date) \
                    ):
                # download prev file
                prev_sensor_file = sensor_files[index - 1].data
                prev_reading_list = \
                    self.data_extraction_service.get_readings_from_sensor_file(prev_sensor_file)

            if next_sensor_file is None and index < len(sensor_files) - 1 \
                    and event.EventType == EventType.SCREEN_ON \
                    and event_date + datetime.timedelta(milliseconds=self.POSTUNLOCK_TIME) > sensor_files[index + 1].start_date:
                # download next file
                next_sensor_file = sensor_files[index + 1].data
                next_reading_list = \
                    self.data_extraction_service.get_readings_from_sensor_file(next_sensor_file)

            reading_list = prev_reading_list + current_reading_list + next_reading_list

            if event.EventType == EventType.SCREEN_ON:
                unlock_df = self.data_extraction_service.create_df_from_readings(event_timestamp, reading_list, \
                    self.PREUNLOCK_TIME, self.POSTUNLOCK_TIME)
                unlock_df = self.data_extraction_service.aggregate_df_with_stats_functions(unlock_df)
                unlock_df = self.data_extraction_service.add_device_id_to_df(unlock_df, device_id)
                
                if unlock_df is not None:
                    unlock_dfs.append(unlock_df)
            
            elif event.EventType == EventType.CONTINUOUS_AUTH_CHECKPOINT:
                checkpoint_df = self.data_extraction_service.create_df_from_readings(event_timestamp, reading_list, \
                    self.CONTINUOUS_AUTH_INTERVAL, 0)
                checkpoint_df = self.data_extraction_service.aggregate_df_with_stats_functions(checkpoint_df)
                checkpoint_df = self.data_extraction_service.add_device_id_to_df(checkpoint_df, device_id)
                
                if checkpoint_df is not None:
                    checkpoint_dfs.append(checkpoint_df)
            
            if (event_number + 1) % 100 == 0:
                self.logger.info(f'Data processing: device {device_id}, {event_number + 1}/{len(events)} events processed')

        device_unlock_data = self.data_extraction_service.transform_df_list_to_df(unlock_dfs)
        device_checkpoint_data = self.data_extraction_service.transform_df_list_to_df(checkpoint_dfs)

        self.logger.info(f'Data processing: device {device_id}, {len(device_unlock_data) if device_unlock_data is not None else "no"} unlock samples extracted')
        self.logger.info(f'Data processing: device {device_id}, {len(device_checkpoint_data) if device_checkpoint_data is not None else "no"} continuous data samples extracted')
        
        return device_unlock_data, device_checkpoint_data

    def create_profiles(self, run, unlock_data, checkpoint_data):
        self.logger.info('Profile creation: creating unlock profiles...')
        self.profile_service.create_profiles(run, unlock_data, ProfileInfo.ProfileType.Unlock.value)
        self.logger.info('Profile creation: unlock profiles created')

        self.logger.info('Profile creation: creating continuous profiles...')
        self.profile_service.create_profiles(run, checkpoint_data, ProfileInfo.ProfileType.Continuous.value)
        self.logger.info('Profile creation: continuous profiles created')