import logging
import services.google_drive_service as drive

from uploader.models import DataFile

class DataFileService:
    logger = logging.getLogger(__name__)

    @classmethod
    def create_data_file(cls, file_data, device, start_date, file_type):
        data_file = DataFile(device = device, start_date = start_date, file_type = file_type)            
        sensor_filename = f'{device.id}_{file_data.name}'
        file_uri = drive.save_file(file_data, device.id, sensor_filename)
        data_file.file_uri = file_uri
        data_file.save()
        return data_file
        