import os, logging, pickle, joblib

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import ApiRequestError
from tempfile import NamedTemporaryFile, mkdtemp, TemporaryFile
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

from .abstract_file_storage_service import AbstractFileStorageService

def create_drive_connection():
    gauth = GoogleAuth()

    # Try to load saved client credentials
    gauth.LoadCredentialsFile("token.json")
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile("token.json")

    return GoogleDrive(gauth)

class GoogleDriveService(AbstractFileStorageService):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.drive = create_drive_connection()

    def save_form_file(self, f, folder, filename):
        assert (type(f) is InMemoryUploadedFile or type(f) is TemporaryUploadedFile) and type(folder) is str and type(filename) is str
        
        self.__get_or_create_folder_id(folder, None)

        drive_file = self.drive.CreateFile({ 'title': filename, "parents": [{ "kind": "drive#fileLink", "id": folder_id }] })

        tmp_filename = None
        with NamedTemporaryFile(delete=False) as tmp_f:
            for chunk in f.chunks():
                tmp_f.write(chunk)
            tmp_filename = tmp_f.name    # save the file name

        drive_file_id = None
        if tmp_filename is not None:
            drive_file.SetContentFile(tmp_filename)
            drive_file.Upload()
            drive_file_id = drive_file['id']

            drive_file.SetContentFile(os.devnull)

            os.remove(tmp_filename)

        return drive_file_id

    def save_event_data(self, event_data, start_date, filename):
        event_data_folder_id = self.__get_or_create_folder_id('event_info', None)
        current_event_data_folder_id = self.__get_or_create_folder_id(start_date.strftime("%Y%m%d_%H%M%S"), 
            event_data_folder_id)

        event_data_file = self.drive.CreateFile({ 'title': f'{filename}.pkl', 
            "parents": [{ "kind": "drive#fileLink", "id": current_event_data_folder_id }] })

        self.__upload_bytes(pickle.dumps(event_data), event_data_file)
        return event_data_file['id']

    def upload_profile(self, selector, start_date, device_id):
        profiles_folder_id = self.__get_or_create_folder_id('profiles', None)
        current_profiles_folder_id = self.__get_or_create_folder_id(start_date.strftime("%Y%m%d_%H%M%S"), 
            profiles_folder_id)
        
        profile_file = self.drive.CreateFile({ 'title': f'{device_id}.joblib', 
            "parents": [{ "kind": "drive#fileLink", "id": current_profiles_folder_id }] })
        
        bytes_obj = None
        with TemporaryFile() as f:
            joblib.dump(selector, f)
            f.seek(0)
            bytes_obj = f.read()

        self.__upload_bytes(bytes_obj, profile_file)

        return profile_file['id']

    def __get_or_create_folder_id(self, folder_name, parent_id):
        if parent_id is None:
            parent_id = 'root'
        
        file_list = self.drive.ListFile({'q': f"'{parent_id}' in parents and trashed=false"}).GetList()

        folder_id = None
        for root_file in file_list:
            if root_file['title'] == folder_name:
                folder_id = root_file['id']

        if folder_id == None:
            if parent_id == 'root':
                drive_folder = self.drive.CreateFile({ 
                    'title': folder_name, 
                    "mimeType": "application/vnd.google-apps.folder" 
                })
            else:
                drive_folder = self.drive.CreateFile({ 
                    'title': folder_name, 
                    "mimeType": "application/vnd.google-apps.folder",
                    "parents": [{ "kind": "drive#fileLink", "id": parent_id }] 
                })
            drive_folder.Upload()
            folder_id = drive_folder['id']
        
        return folder_id

    def __upload_bytes(self, bytes_obj, drive_file):
        tmp_filename = None
        with NamedTemporaryFile(delete=False) as tmp_f:
            tmp_f.write(bytes_obj)
            tmp_filename = tmp_f.name    # save the file name

        drive_file_id = None
        if tmp_filename is not None:
            drive_file.SetContentFile(tmp_filename)
            drive_file.Upload()
            drive_file_id = drive_file['id']
            
            drive_file.SetContentFile(os.devnull)

            os.remove(tmp_filename)

        return drive_file_id

    def get_file(self, file_id):
        assert type(file_id) is str
        drive_file = self.drive.CreateFile({ 'id': file_id })

        tmp_filename = os.path.join(mkdtemp(), str(file_id))
        drive_file.GetContentFile(tmp_filename)
        del drive_file

        content = None
        with open(tmp_filename, 'rb') as tmp_f:
            content = tmp_f.read()

        os.remove(tmp_filename)
        return content

    def download_file(self, file_id):
        assert type(file_id) is str
        drive_file = self.drive.CreateFile({ 'id': file_id })

        tmp_filename = os.path.join(mkdtemp(), str(file_id))

        retry_counter = 0
        max_retries = 10
        try:
            drive_file.GetContentFile(tmp_filename)
        except ApiRequestError as err:
            while retry_counter < max_retries:
                retry_counter += 1
                self.logger.error(f'API request failed for file {file_id}, retrying ({retry_counter}/{max_retries})...')
                drive_file.GetContentFile(tmp_filename)
            self.logger.error(f'API request failed: {err}')
            return None
        
        del drive_file
        
        return tmp_filename