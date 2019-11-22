import logging
from services.google_drive_service import GoogleDriveService

from uploader.models import DataFile

class DataFileService:
    logger = logging.getLogger(__name__)

    @classmethod
    def create_data_file(cls, file_data, device, start_date, file_type):
        data_file = DataFile(device = device, start_date = start_date, file_type = file_type)
        sensor_filename = f'{device.id}_{file_data.name}'
        file_uri = GoogleDriveService.save_file(file_data, device.id, sensor_filename)
        data_file.file_uri = file_uri
        data_file.save()
        return data_file

    @classmethod
    def get_data_file_list(cls):
        return DataFile.objects.order_by('device_id', '-start_date')

    @classmethod
    def get_data_file(cls, id):
        try:
            data_file = DataFile.objects.get(id = id)
            return data_file
        except DataFile.DoesNotExist:
            return None
