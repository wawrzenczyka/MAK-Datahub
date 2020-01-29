import os, pickle, joblib
from tempfile import NamedTemporaryFile

from django.core.files.storage import default_storage
from django.core.files import File

from MAKDataHub.settings import MEDIA_ROOT

class StorageService():
    def create_pickle_file(self, event_data, start_date, filename):
        tmp_f = NamedTemporaryFile(delete=False)
        pickle.dump(event_data, tmp_f)
        return File(tmp_f, name=f'{filename}.pkl')

    def create_joblib_file(self, selector, start_date, device_id, profile_type):
        tmp_f = NamedTemporaryFile(delete=False)
        joblib.dump(selector, tmp_f)
        return File(tmp_f, name=f'{device_id}_{profile_type}.joblib')

    def dispose(self, f):
        f.close()
        os.remove(f.file.name)