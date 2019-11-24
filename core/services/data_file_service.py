import logging
from datetime import datetime

from django.core.files.uploadedfile import InMemoryUploadedFile

from ..models import DataFile, Device
from .google_drive_service import GoogleDriveService

class DataFileService:
    logger = logging.getLogger(__name__)

    @classmethod
    def create_data_file(cls, file_data, device, start_date, file_type):
        assert type(file_data) is InMemoryUploadedFile and type(device) is Device and (type(start_date) is str or type(start_date) is datetime)
        assert file_type == 'S' or file_type == 'E'

        data_file = DataFile(device = device, start_date = start_date, file_type = file_type)
        sensor_filename = f'{device.id}_{file_data.name}'
        file_uri = GoogleDriveService.save_file(file_data, device.id, sensor_filename)
        data_file.file_uri = file_uri
        data_file.save()
        return data_file

    @classmethod
    def get_data_file_list(cls):
        return DataFile.objects.order_by('-start_date', 'device_id')

    @classmethod
    def get_data_file(cls, id):
        assert type(id) is int

        try:
            data_file = DataFile.objects.get(id = id)
            return data_file
        except DataFile.DoesNotExist:
            return None
