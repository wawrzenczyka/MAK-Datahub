# from django.conf import settings
# settings.configure(
#     DATABASE_ENGINE = 'django.db.backends.mysql',
#     DATABASE_NAME = 'makengineering$makdb',
#     DATABASE_USER = 'makengineering',
#     DATABASE_PASSWORD = 'admin123$',
#     DATABASE_HOST = 'makengineering.mysql.pythonanywhere-services.com',
# )

from django.core.management.base import BaseCommand, CommandError

from ProfileCreator.parsers.sensors_parser import SensorParser
from core.services.data_file_service import DataFileService
from core.services.device_service import DeviceService
from core.services.google_drive_service import GoogleDriveService
from core.models import DataFile, Device

class Command(BaseCommand):
    help = 'Performs data processing'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        parser = SensorParser(open('ProfileCreator/parsers/sensor_config.json'))
        data_file_service = DataFileService()
        device_service = DeviceService()
        google_drive_service = GoogleDriveService()

        devices = device_service.get_all_devices()
        for device in devices:
            assert type(device) is Device
            datafiles = data_file_service.get_data_files_for_device(device.id)
            for df in datafiles:
                assert type(df) is DataFile
                # TODO: move this part to service
                filename = device_id + '/' + str(df)
                google_drive_service.download_file(df.file_id, filename) # local download
                __get_file_data(filename)
                # TODO: remove file

            __process_device_data(device.id)
    
    def __get_file_data(self, filename):
        # TODO: parser.parseFile(open(filename, 'rb'))
        # TODO: add data to private collection (map?)
        pass

    def __process_device_data(self, device_id):
        # TODO: create vectors
        # TODO: create profile (probably here because $$$)