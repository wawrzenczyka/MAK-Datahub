import logging
from datetime import datetime

from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

from ..models import DataFileInfo, Device

class DataFileService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_data_file(self, id):
        try:
            data_file = DataFileInfo.objects.get(id = id)
            return data_file
        except DataFileInfo.DoesNotExist:
            return None

    def get_event_files_for_device(self, device_id):
        try:
            device = Device.objects.get(id = device_id)
            return device.datafileinfo_set.filter(file_type = 'Event').order_by('start_date')
        except DataFileInfo.DoesNotExist:
            return None

    def get_sensor_files_for_device(self, device_id):
        try:
            device = Device.objects.get(id = device_id)
            return device.datafileinfo_set.filter(file_type = 'Sensor').order_by('start_date')
        except DataFileInfo.DoesNotExist:
            return None