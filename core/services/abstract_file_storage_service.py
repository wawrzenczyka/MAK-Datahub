from abc import ABC, abstractmethod

class AbstractFileStorageService(ABC):
    @abstractmethod
    def save_form_file(cls, f, folder, filename):
        pass

    @abstractmethod
    def get_file(cls, file_id):
        pass