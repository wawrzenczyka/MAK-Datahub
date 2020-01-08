import logging, os, datetime, pytz, pickle

from django.core.management.base import BaseCommand, CommandError

from core.services.data_file_service import DataFileService
from core.services.device_service import DeviceService
from core.services.google_drive_service import GoogleDriveService
from core.services.data_extraction_service import DataExtractionService
from core.services.profile_service import ProfileService
from core.services.ml_service import MLService
from core.models import DataFile, Device

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

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.logger.info('Data processing started...')

        processing_start_date = datetime.datetime.now()
        devices = [x for x in self.device_service.get_all_devices()]
        device_event_files = { device.id: [x for x in self.data_file_service.get_event_files_for_device(device.id)] for device in devices }
        device_sensor_files = { device.id: [x for x in self.data_file_service.get_sensor_files_for_device(device.id)] for device in devices }

        unlock_data = []
        parsed_unlock_files = {}

        last_run = self.profile_service.get_last_profile_creation_run()

        if last_run is not None:
            parsed_unlock_files = pickle.loads(self.google_drive_service.get_file(last_run).parsed_unlock_files_uri)
            unlock_data.append(pickle.loads(self.google_drive_service.get_file(last_run).unlock_data_uri))

        # if os.path.exists('unlocks.pkl'):
        #     with open('unlocks.pkl', 'rb') as f:
        #         old_unlocks = pickle.load(f)
        
        for device in devices:
            
            assert type(device) is Device
            event_files = device_event_files[device.id]
            sensor_files = device_sensor_files[device.id]
            self.logger.info(f'Data processing: device {device.id}, {len(event_files)} event files, {len(sensor_files)} sensor files')

            if device.id not in parsed_unlock_files:
                parsed_unlock_files[device.id] = set()

            self.logger.info(f'Data processing: device {device.id}, {len(event_files)} new event files')

            unlocks = []
            for ef in event_files:
                if ef.id in parsed_unlock_files[device.id]:
                    continue
                else:
                    parsed_unlock_files[device.id].add(ef.id)
                
                filename = self.google_drive_service.download_file(ef.file_uri)
                file_events = self.data_extraction_service.extract_events(filename)
                unlocks += file_events
                os.remove(filename)

                break

            self.logger.info(f'Data processing: device {device.id}, {len(unlocks)} new unlocks')
            
            unlocks.sort()

            prev_sensor_file = None
            current_sensor_file = None
            next_sensor_file = None

            prev_reading_list = []
            current_reading_list = []
            next_reading_list = []

            index = 0

            # TODO: if len == 0|1|2
            unlock_dfs = []

            for unlock_number, unlock_timestamp in enumerate(unlocks):                
                utc = pytz.UTC
                unlock_date = utc.localize(datetime.datetime.utcfromtimestamp(unlock_timestamp/1000))
                while index < len(sensor_files) - 1 and unlock_date >= sensor_files[index + 1].start_date:
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
                        and unlock_date - datetime.timedelta(milliseconds=self.PREUNLOCK_TIME) < sensor_files[index].start_date:
                    # download prev file
                    prev_sensor_file = self.google_drive_service.download_file(sensor_files[index - 1].file_uri)
                    prev_reading_list = \
                        self.data_extraction_service.get_readings_from_sensor_files(prev_sensor_file)

                if next_sensor_file is None and index < len(sensor_files) - 1 \
                        and unlock_date + datetime.timedelta(milliseconds=self.POSTUNLOCK_TIME) > sensor_files[index + 1].start_date:
                    # download next file
                    next_sensor_file = self.google_drive_service.download_file(sensor_files[index + 1].file_uri)
                    next_reading_list = \
                        self.data_extraction_service.get_readings_from_sensor_files(next_sensor_file)

                # TODO: move this part to service
                reading_list = prev_reading_list + current_reading_list + next_reading_list

                unlock_df = self.data_extraction_service.create_unlock_df_from_readings(unlock_timestamp, reading_list)
                unlock_df = self.data_extraction_service.aggregate_df_with_stats_functions(unlock_df)
                unlock_df = self.data_extraction_service.add_device_id_to_unlock_df(unlock_df, device.id)
                
                if unlock_df is not None:
                    unlock_dfs.append(unlock_df)
                
                if (unlock_number + 1) % 100 == 0:
                    self.logger.info(f'Data processing: device {device.id}, {unlock_number + 1}/{len(unlocks)} unlocks processed')

            if prev_sensor_file is not None:
                os.remove(prev_sensor_file)
            if current_sensor_file is not None:
                os.remove(current_sensor_file)
            if next_sensor_file is not None:
                os.remove(next_sensor_file)

            device_unlock_data = self.data_extraction_service.transform_df_list_to_df(unlock_dfs)
            self.logger.info(f'Data processing: device {device.id}, {len(device_unlock_data)} samples extracted')
            unlock_data.append(device_unlock_data)

        unlock_data = self.data_extraction_service.transform_df_list_to_df(unlock_data)
        # unlock_data.to_pickle('unlock_data.pkl')
        # with open('unlocks.pkl', 'wb') as f:
        #     pickle.dump(parsed_unlock_files, f)

        parsed_unlock_files_uri, unlock_data_uri = \
            self.google_drive_service.save_unlock_data(processing_start_date, parsed_unlock_files, unlock_data)

        run = self.profile_service.create_profile_creation_run(processing_start_date, parsed_unlock_files_uri, unlock_data_uri)

        self.logger.info('Data processing finished...')
        self.logger.info('Profile creation started...')

        self.profile_service.create_profiles(run, unlock_data)

        self.logger.info('Profile creation finished...')