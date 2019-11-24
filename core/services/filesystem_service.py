from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import InMemoryUploadedFile

from .abstract_file_handler_service import AbstractFileHandlerService

class FileSystemService(AbstractFileHandlerService):
    @classmethod
    def save_file(cls, f, folder, filename):
        assert type(f) is InMemoryUploadedFile and type(folder) is str and type(filename) is str

        fs = FileSystemStorage()
        fs.save(f'{folder}/{filename}', f)
        return fs.url(filename)
        
    @classmethod
    def get_file(cls, file_id):
        assert type(file_id) is str
        with open(file_id, 'rb') as f:
            return f.read()