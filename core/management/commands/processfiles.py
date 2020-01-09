import logging, os, datetime, pytz, pickle

from django.core.management.base import BaseCommand, CommandError

from core.services.data_file_service import DataFileService
from core.services.device_service import DeviceService
from core.services.google_drive_service import GoogleDriveService
from core.services.data_extraction_service import DataExtractionService
from core.services.profile_service import ProfileService
from core.services.ml_service import MLService
from core.models import DataFile, Device

from ProfileCreator.parsers.event_parser import EventType

class Command(BaseCommand):
    help = 'Performs data processing'
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_extraction_service = DataExtractionService()
        self.device_service = DeviceService()
        self.google_drive_service = GoogleDriveService()
        self.data_file_service = DataFileService(self.google_drive_service)
        self.ml_service = MLService()
        self.profile_service = ProfileService(self.ml_service, self.google_drive_service)

        self.PREUNLOCK_TIME = 3000
        self.POSTUNLOCK_TIME = 1000
        self.CONTINUOUS_AUTH_INTERVAL = 20000

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.logger.info('Data processing started...')

        processing_start_date = datetime.datetime.now()
        devices = [x for x in self.device_service.get_all_devices()]
        device_event_files = { device.id: [x for x in self.data_file_service.get_event_files_for_device(device.id)] for device in devices }
        device_sensor_files = { device.id: [x for x in self.data_file_service.get_sensor_files_for_device(device.id)] for device in devices }

        unlock_data = []
        checkpoint_data = []
        parsed_event_files = {}

        last_run = self.profile_service.get_last_profile_creation_run()

        if last_run is not None:
            parsed_event_files = pickle.loads(self.google_drive_service.get_file(last_run.parsed_event_files_uri))
            unlock_data.append(pickle.loads(self.google_drive_service.get_file(last_run.unlock_data_uri)))
            checkpoint_data.append(pickle.loads(self.google_drive_service.get_file(last_run.checkpoint_data_uri)))

        # TODO: local profile reading
        # if os.path.exists('unlocks.pkl'):
        #     with open('unlocks.pkl', 'rb') as f:
        #         old_unlocks = pickle.load(f)
        
        for device in devices:
            
            assert type(device) is Device
            event_files = device_event_files[device.id]
            sensor_files = device_sensor_files[device.id]
            self.logger.info(f'Data processing: device {device.id}, {len(event_files)} event files, {len(sensor_files)} sensor files')

            if device.id not in parsed_event_files:
                parsed_event_files[device.id] = set()

            self.logger.info(f'Data processing: device {device.id}, {len(event_files)} new event files')

            unlocks = []
            screen_offs = []
            for ef in event_files:
                if ef.id in parsed_event_files[device.id]:
                    continue
                else:
                    parsed_event_files[device.id].add(ef.id)
                
                filename = self.google_drive_service.download_file(ef.file_uri)
                file_unlocks, file_screen_offs = self.data_extraction_service.extract_events(filename)
                os.remove(filename)

                unlocks += file_unlocks
                screen_offs += file_screen_offs

            checkpoints = self.data_extraction_service.generate_continuous_auth_checkpoints(unlocks, screen_offs)
            self.logger.info(f'Data processing: device {device.id}, {len(unlocks)} new unlocks')
            self.logger.info(f'Data processing: device {device.id}, {len(checkpoints)} new continuous data points')

            events = unlocks + checkpoints
            events.sort(key=lambda e: e.Timestamp)

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
                while index < len(sensor_files) - 1 and event_date >= sensor_files[index + 1].start_date:
                    index += 1
                    if prev_sensor_file is not None:
                        os.remove(prev_sensor_file)
                    prev_sensor_file = current_sensor_file
                    prev_reading_list = current_reading_list
                    current_sensor_file = next_sensor_file
                    current_reading_list = next_reading_list
                    next_sensor_file = None
                    next_reading_list = []

                if current_sensor_file is None:
                    # download current file
                    current_sensor_file = self.google_drive_service.download_file(sensor_files[index].file_uri)
                    current_reading_list = \
                        self.data_extraction_service.get_readings_from_sensor_files(current_sensor_file)

                if prev_sensor_file is None and index > 0 \
                        and ( \
                            (event.EventType == EventType.USER_PRESENT and event_date - datetime.timedelta(milliseconds=self.PREUNLOCK_TIME) < sensor_files[index].start_date) \
                            or (event.EventType == EventType.CONTINUOUS_AUTH_CHECKPOINT and event_date - datetime.timedelta(milliseconds=self.CONTINUOUS_AUTH_INTERVAL) < sensor_files[index].start_date) \
                        ):
                    # download prev file
                    prev_sensor_file = self.google_drive_service.download_file(sensor_files[index - 1].file_uri)
                    prev_reading_list = \
                        self.data_extraction_service.get_readings_from_sensor_files(prev_sensor_file)

                if next_sensor_file is None and index < len(sensor_files) - 1 \
                        and event.EventType == EventType.USER_PRESENT \
                        and event_date + datetime.timedelta(milliseconds=self.POSTUNLOCK_TIME) > sensor_files[index + 1].start_date:
                    # download next file
                    next_sensor_file = self.google_drive_service.download_file(sensor_files[index + 1].file_uri)
                    next_reading_list = \
                        self.data_extraction_service.get_readings_from_sensor_files(next_sensor_file)

                reading_list = prev_reading_list + current_reading_list + next_reading_list

                if event.EventType == EventType.USER_PRESENT:
                    unlock_df = self.data_extraction_service.create_df_from_readings(event_timestamp, reading_list, \
                        self.PREUNLOCK_TIME, self.POSTUNLOCK_TIME)
                    unlock_df = self.data_extraction_service.aggregate_df_with_stats_functions(unlock_df)
                    unlock_df = self.data_extraction_service.add_device_id_to_df(unlock_df, device.id)
                    
                    if unlock_df is not None:
                        unlock_dfs.append(unlock_df)
                elif event.EventType == EventType.CONTINUOUS_AUTH_CHECKPOINT:
                    checkpoint_df = self.data_extraction_service.create_df_from_readings(event_timestamp, reading_list, \
                        self.CONTINUOUS_AUTH_INTERVAL, 0)
                    checkpoint_df = self.data_extraction_service.aggregate_df_with_stats_functions(checkpoint_df)
                    checkpoint_df = self.data_extraction_service.add_device_id_to_df(checkpoint_df, device.id)
                    
                    if checkpoint_df is not None:
                        checkpoint_dfs.append(checkpoint_df)
                
                if (event_number + 1) % 100 == 0:
                    self.logger.info(f'Data processing: device {device.id}, {event_number + 1}/{len(events)} events processed')

            if prev_sensor_file is not None:
                os.remove(prev_sensor_file)
            if current_sensor_file is not None:
                os.remove(current_sensor_file)
            if next_sensor_file is not None:
                os.remove(next_sensor_file)

            device_unlock_data = self.data_extraction_service.transform_df_list_to_df(unlock_dfs)
            device_checkpoint_data = self.data_extraction_service.transform_df_list_to_df(checkpoint_dfs)

            self.logger.info(f'Data processing: device {device.id}, {len(device_unlock_data) if device_unlock_data is not None else "no"} unlock samples extracted')
            self.logger.info(f'Data processing: device {device.id}, {len(device_checkpoint_data) if device_unlock_data is not None else "no"} continuous data samples extracted')
            if device_unlock_data is not None:
                unlock_data.append(device_unlock_data)            
            if device_checkpoint_data is not None:
                checkpoint_data.append(device_checkpoint_data)

        unlock_data = self.data_extraction_service.transform_df_list_to_df(unlock_data)
        checkpoint_data = self.data_extraction_service.transform_df_list_to_df(checkpoint_data)

        # TODO: local profile saving
        # unlock_data.to_pickle('unlock_data.pkl')
        # with open('unlocks.pkl', 'wb') as f:
        #     pickle.dump(parsed_event_files, f)

        unlock_data_uri = \
            self.google_drive_service.save_event_data(unlock_data, processing_start_date, 'unlock_data')
        checkpoint_data_uri = \
            self.google_drive_service.save_event_data(checkpoint_data, processing_start_date, 'checkpoint_data')
        parsed_event_files_uri = \
            self.google_drive_service.save_event_data(parsed_event_files, processing_start_date, 'parsed_event_files')

        run = self.profile_service.create_profile_creation_run(processing_start_date, parsed_event_files_uri, unlock_data_uri, checkpoint_data_uri)

        self.logger.info('Data processing finished...')
        self.logger.info('Profile creation started...')

        self.logger.info('Profile creation: creating unlock profiles...')
        self.profile_service.create_profiles(run, unlock_data, 'UNLOCK')
        self.logger.info('Profile creation: unlock profiles created')
        self.logger.info('Profile creation: creating continuous profiles...')
        self.profile_service.create_profiles(run, checkpoint_data, 'CONTINUOUS')
        self.logger.info('Profile creation: continuous profiles created')

        self.logger.info('Profile creation finished...')