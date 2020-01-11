from abc import ABC, abstractmethod

class AbstractFileStorageService(ABC):
    @abstractmethod
    def save_form_file(cls, f, folder, filename):
        pass

    @abstractmethod
    def get_file(cls, file_id):
        pass
    
    @abstractmethod
    def download_file(self, file_id):
        pass

    @abstractmethod
    def save_event_data(self, event_data, start_date, filename):
        pass

    @abstractmethod
    def save_profile(self, selector, start_date, device_id, profile_type):
        pass