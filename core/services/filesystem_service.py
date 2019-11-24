from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

from .abstract_file_storage_service import AbstractFileStorageService

class FileSystemService(AbstractFileStorageService):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def save_file(self, f, folder, filename):
        assert (type(f) is InMemoryUploadedFile or type(f) is TemporaryUploadedFile) and type(folder) is str and type(filename) is str

        fs = FileSystemStorage()
        fs.save(f'{folder}/{filename}', f)
        return fs.url(filename)
        
    def get_file(self, file_id):
        assert type(file_id) is str
        with open(file_id, 'rb') as f:
            return f.read()