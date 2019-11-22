from django.core.files.storage import FileSystemStorage

from .abstract_file_handler_service import AbstractFileHandlerService

class FileSystemService(AbstractFileHandlerService):
    @classmethod
    def save_file(cls, f, folder, filename):
        fs = FileSystemStorage()
        fs.save(f'{folder}/{filename}', f)
        return fs.url(filename)
        
    @classmethod
    def get_file(cls, file_id):
        with open(file_id, 'rb') as f:
            return f.read()