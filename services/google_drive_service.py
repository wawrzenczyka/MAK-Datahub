# from __future__ import print_function
# import pickle
# import os.path

# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request

# SCOPES = ['https://www.googleapis.com/auth/drive.file']

# creds = None
# # The file token.pickle stores the user's access and refresh tokens, and is
# # created automatically when the authorization flow completes for the first
# # time.
# if os.path.exists('token.pickle'):
#     with open('token.pickle', 'rb') as token:
#         creds = pickle.load(token)
# # If there are no (valid) credentials available, let the user log in.
# if not creds or not creds.valid:
#     if creds and creds.expired and creds.refresh_token:
#         creds.refresh(Request())
#     else:
#         flow = InstalledAppFlow.from_client_secrets_file(
#             'credentials.json', SCOPES)
#         creds = flow.run_local_server(port=0)
#     # Save the credentials for the next run
#     with open('token.pickle', 'wb') as token:
#         pickle.dump(creds, token)

# service = build('drive', 'v3', credentials=creds)

# # Call the Drive v3 API

# def upload_file(f):
#     file_metadata = {'name': f.name}
#     media = MediaFileUpload(f.path, mimetype='text/csv')
#     file = service.files().create(body=file_metadata,
#                                         media_body=media,
#                                         fields='id').execute()
#     print('File ID: %s' % file.get('id'))
#     return file.get('id')

# # results = service.files().list(
# #     pageSize=10, fields="nextPageToken, files(id, name)").execute()
# # items = results.get('files', [])

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

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

def save_file(f, filename):
    content = b''

    for chunk in f.chunks():
        content += chunk

    drive_file = drive.CreateFile({ 'title': filename })
    drive_file.SetContentString(content.decode("utf-8"))
    drive_file.Upload()

    return drive_file['id']

def get_file(file_id):
    drive_file = drive.CreateFile({ 'id': file_id })
    return drive_file.GetContentString()