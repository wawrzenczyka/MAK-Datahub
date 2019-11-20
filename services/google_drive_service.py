import os

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from tempfile import NamedTemporaryFile, mkdtemp

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

drive = GoogleDrive(gauth)

def save_file(f, folder, filename):
    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()

    folder_id = None
    for root_file in file_list:
        if root_file['title'] == folder:
            folder_id = root_file['id']

    if (folder_id == None):
        drive_folder = drive.CreateFile({ 'title': folder, "mimeType": "application/vnd.google-apps.folder" })
        drive_folder.Upload()
        folder_id = drive_folder['id']

    drive_file = drive.CreateFile({ 'title': filename, "parents": [{ "kind": "drive#fileLink", "id": folder_id }] })

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
        del drive_file

        os.remove(tmp_filename)

    return drive_file_id

def get_file(file_id):
    drive_file = drive.CreateFile({ 'id': file_id })

    tmp_filename = os.path.join(mkdtemp(), str(file_id))
    drive_file.GetContentFile(tmp_filename)
    del drive_file

    content = None
    with open(tmp_filename, 'rb') as tmp_f:
        content = tmp_f.read()

    os.remove(tmp_filename)
    return content
