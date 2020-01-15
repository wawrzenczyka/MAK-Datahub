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

# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive
# from pydrive.files import ApiRequestError
# from tempfile import NamedTemporaryFile, mkdtemp, TemporaryFile
# from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

# def create_drive_connection():
#     gauth = GoogleAuth()

#     # Try to load saved client credentials
#     gauth.LoadCredentialsFile("token.json")
#     if gauth.credentials is None:
#         # Authenticate if they're not there
#         gauth.LocalWebserverAuth()
#     elif gauth.access_token_expired:
#         # Refresh them if expired
#         gauth.Refresh()
#     else:
#         # Initialize the saved creds
#         gauth.Authorize()
#     # Save the current credentials to a file
#     gauth.SaveCredentialsFile("token.json")

#     return GoogleDrive(gauth)

# class GoogleDriveService(AbstractFileStorageService):
#     def __init__(self):
#         self.logger = logging.getLogger(__name__)
#         self.drive = create_drive_connection()

#     def save_form_file(self, f, folder, filename):
#         assert (type(f) is InMemoryUploadedFile or type(f) is TemporaryUploadedFile) and type(folder) is str and type(filename) is str
        
#         folder_id = self.__get_or_create_folder_id(folder, None)

#         drive_file = self.drive.CreateFile({ 'title': filename, "parents": [{ "kind": "drive#fileLink", "id": folder_id }] })

#         tmp_filename = None
#         with NamedTemporaryFile(delete=False) as tmp_f:
#             for chunk in f.chunks():
#                 tmp_f.write(chunk)
#             tmp_filename = tmp_f.name    # save the file name

#         drive_file_id = None
#         if tmp_filename is not None:
#             drive_file.SetContentFile(tmp_filename)
#             drive_file.Upload()
#             drive_file_id = drive_file['id']

#             drive_file.SetContentFile(os.devnull)

#             os.remove(tmp_filename)

#         return drive_file_id

#     def save_event_data(self, event_data, start_date, filename):
#         event_data_folder_id = self.__get_or_create_folder_id('event_info', None)
#         current_event_data_folder_id = self.__get_or_create_folder_id(start_date.strftime("%Y%m%d_%H%M%S"), 
#             event_data_folder_id)

#         event_data_file = self.drive.CreateFile({ 'title': f'{filename}.pkl', 
#             "parents": [{ "kind": "drive#fileLink", "id": current_event_data_folder_id }] })

#         self.__upload_bytes(pickle.dumps(event_data), event_data_file)
#         return event_data_file['id']

#     def save_profile(self, selector, start_date, device_id, profile_type):
#         profiles_folder_id = self.__get_or_create_folder_id('profiles', None)
#         current_profiles_folder_id = self.__get_or_create_folder_id(start_date.strftime("%Y%m%d_%H%M%S"), 
#             profiles_folder_id)
        
#         profile_file = self.drive.CreateFile({ 'title': f'{device_id}_{profile_type}.joblib', 
#             "parents": [{ "kind": "drive#fileLink", "id": current_profiles_folder_id }] })
        
#         bytes_obj = None
#         with TemporaryFile() as f:
#             joblib.dump(selector, f)
#             f.seek(0)
#             bytes_obj = f.read()

#         self.__upload_bytes(bytes_obj, profile_file)

#         return profile_file['id']

#     def __get_or_create_folder_id(self, folder_name, parent_id):
#         if parent_id is None:
#             parent_id = 'root'
        
#         file_list = self.drive.ListFile({'q': f"'{parent_id}' in parents and trashed=false"}).GetList()

#         folder_id = None
#         for root_file in file_list:
#             if root_file['title'] == folder_name:
#                 folder_id = root_file['id']

#         if folder_id == None:
#             if parent_id == 'root':
#                 drive_folder = self.drive.CreateFile({ 
#                     'title': folder_name, 
#                     "mimeType": "application/vnd.google-apps.folder" 
#                 })
#             else:
#                 drive_folder = self.drive.CreateFile({ 
#                     'title': folder_name, 
#                     "mimeType": "application/vnd.google-apps.folder",
#                     "parents": [{ "kind": "drive#fileLink", "id": parent_id }] 
#                 })
#             drive_folder.Upload()
#             folder_id = drive_folder['id']
        
#         return folder_id

#     def __upload_bytes(self, bytes_obj, drive_file):
#         tmp_filename = None
#         with NamedTemporaryFile(delete=False) as tmp_f:
#             tmp_f.write(bytes_obj)
#             tmp_filename = tmp_f.name    # save the file name

#         drive_file_id = None
#         if tmp_filename is not None:
#             drive_file.SetContentFile(tmp_filename)
#             drive_file.Upload()
#             drive_file_id = drive_file['id']
            
#             drive_file.SetContentFile(os.devnull)

#             os.remove(tmp_filename)

#         return drive_file_id

#     def get_file(self, file_id):
#         assert type(file_id) is str
#         drive_file = self.drive.CreateFile({ 'id': file_id })

#         tmp_filename = os.path.join(mkdtemp(), str(file_id))
#         drive_file.GetContentFile(tmp_filename)
#         del drive_file

#         content = None
#         with open(tmp_filename, 'rb') as tmp_f:
#             content = tmp_f.read()

#         os.remove(tmp_filename)
#         return content

#     def download_file(self, file_id):
#         assert type(file_id) is str
#         drive_file = self.drive.CreateFile({ 'id': file_id })

#         tmp_filename = os.path.join(mkdtemp(), str(file_id))

#         retry_counter = 0
#         max_retries = 10
#         try:
#             drive_file.GetContentFile(tmp_filename)
#         except ApiRequestError as err:
#             while retry_counter < max_retries:
#                 retry_counter += 1
#                 self.logger.error(f'API request failed for file {file_id}, retrying ({retry_counter}/{max_retries})...')
#                 drive_file.GetContentFile(tmp_filename)
#             self.logger.error(f'API request failed: {err}')
#             return None
        
#         del drive_file
        
#         return tmp_filename

# import logging, pickle, os

# from pathlib import Path

# from django.core.files.storage import FileSystemStorage
# from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

# class LocalFileSystemService(AbstractFileStorageService):
#     def __init__(self):
#         self.logger = logging.getLogger(__name__)
#         self.fs = FileSystemStorage()

#     def save_form_file(self, f, folder, filename):
#         assert (type(f) is InMemoryUploadedFile or type(f) is TemporaryUploadedFile) and type(folder) is str and type(filename) is str

#         self.fs.save(f'{folder}/{filename}', f)
#         return self.fs.url(filename)
        
#     def get_file(self, file_id):
#         assert type(file_id) is str
#         with open(file_id, 'rb') as f:
#             return f.read()
        
#     def download_file(self, file_id):
#         assert type(file_id) is str
#         return file_id
    
#     def save_event_data(self, event_data, start_date, filename):
#         dir = Path('event_info') / f'{start_date.strftime("%Y%m%d_%H%M%S")}'
#         dir.mkdir(exist_ok=True, parents=True)
#         path = dir / f'{filename}.pkl'
#         with path.open('wb') as f:
#             pickle.dump(event_data, f)
#             return str(path.resolve())

#     def save_profile(self, selector, start_date, device_id, profile_type):
#         dir = Path('profiles') / f'{start_date.strftime("%Y%m%d_%H%M%S")}'
#         dir.mkdir(exist_ok=True, parents=True)
#         path = dir / f'{device_id}_{profile_type}.joblib'
#         with path.open('wb') as f:
#             joblib.dump(selector, f)
#             return str(path.resolve())