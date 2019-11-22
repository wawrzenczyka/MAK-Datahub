from abc import ABC, abstractmethod

class AbstractFileHandlerService(ABC):
    @classmethod
    @abstractmethod
    def save_file(cls, f, folder, filename):
        pass

    @classmethod
    @abstractmethod
    def get_file(cls, file_id):
        pass