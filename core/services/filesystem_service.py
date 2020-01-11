import logging, pickle, os

from pathlib import Path

from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

from .abstract_file_storage_service import AbstractFileStorageService

class FileSystemService(AbstractFileStorageService):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.fs = FileSystemStorage()

    def save_form_file(self, f, folder, filename):
        assert (type(f) is InMemoryUploadedFile or type(f) is TemporaryUploadedFile) and type(folder) is str and type(filename) is str

        self.fs.save(f'{folder}/{filename}', f)
        return self.fs.url(filename)
        
    def get_file(self, file_id):
        assert type(file_id) is str
        with open(file_id, 'rb') as f:
            return f.read()
        
    def download_file(self, file_id):
        assert type(file_id) is str
        return file_id
    
    def save_event_data(self, event_data, start_date, filename):
        dir = Path('event_info') / f'{start_date.strftime("%Y%m%d_%H%M%S")}'
        dir.mkdir(exist_ok=True, parents=True)
        path = dir / f'{filename}.pkl'
        with path.open('wb') as f:
            pickle.dump(event_data, f)
            return str(path.resolve())

    def save_profile(self, selector, start_date, device_id, profile_type):
        dir = Path('profiles') / f'{start_date.strftime("%Y%m%d_%H%M%S")}'
        dir.mkdir(exist_ok=True, parents=True)
        path = dir / f'{device_id}_{profile_type}.joblib'
        with path.open('wb') as f:
            joblib.dump(selector, f)
            return str(path.resolve())