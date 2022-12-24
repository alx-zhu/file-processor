import os
import io
import wget
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaIoBaseDownload

# creds = None
# SCOPES = ['https://www.googleapis.com/auth/drive']
# if os.path.exists('token.json'):
#   creds = Credentials.from_authorized_user_file('token.json', SCOPES)

############################# getGoogleDriveCreds ##############################

def google_get_creds():
  # From the Google Drive API
  SCOPES = ['https://www.googleapis.com/auth/drive']
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if (os.path.exists('token.json')):
      os.remove('token.json')
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
      token.write(creds.to_json())
  return creds


########################### fetch_GoogleDriveFolder ############################

def google_fetch_folder(creds, folderName):

  try:
    # create drive api client
    service = build('drive', 'v3', credentials=creds)
    response = service.files().list(q=f"mimeType='application/vnd.google-apps.folder' and name = '{folderName}' and trashed = False",
                                      spaces='drive',
                                      fields='files(id, name)').execute()
    files = response.get('files', [])

    if (len(files) == 0):
      print(f"'{folderName}' was not found in Google Drive.")
      return 0
    elif (len(files) > 1):
      print(f"More than one folder of name '{folderName}' were found in Google Drive. Make sure the folder name is unique.")
      return -1

  except HttpError as error:
    print(F'An error occurred: {error}')
    files = None

  return files[0].get('id')



############################# google_create_folder #############################

def google_create_folder(creds, folderName, togglePrint=True):

  try:
    # create drive api client
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {
      'name': folderName,
      'mimeType': 'application/vnd.google-apps.folder'
    }

    # pylint: disable=maybe-no-member
    file = service.files().create(body=file_metadata, fields='id'
                                    ).execute()
    togglePrint and print(F'----> Google Drive folder has been created with ID: "{file.get("id")}".')

  except HttpError as error:
    print(F'***An error occurred: {error}***')
    file = None

  return file.get('id')



############################ google_upload_file ################################

def google_upload_file(creds, filePath, mimeType='text/csv', togglePrint=True):
  fileName = os.path.basename(filePath)
  try:
    # create drive api client
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': fileName}
    media = MediaFileUpload(filePath, mimetype=mimeType)
    # pylint: disable=maybe-no-member
    file = service.files().create(body=file_metadata, media_body=media,
                                  fields='id').execute()
    togglePrint and print(F'----> File ID: {file.get("id")} was uploaded to Google Drive.')

  except HttpError as error:
    print(F'***An error occurred: {error}***')
    file = None

  return file.get('id')



############################ storeFile_GoogleFolder ############################

def google_upload_into_folder(creds, filePath, googleFolderId, mimeType='text/csv', togglePrint=True):
  fileName = os.path.basename(filePath)
  try:
    # create drive api client
    service = build('drive', 'v3', credentials=creds)

    folder_id = googleFolderId
    file_metadata = {
      'name': fileName,
        'parents': [folder_id]
    }
    media = MediaFileUpload(filePath,
                            mimetype=mimeType, resumable=True)
    # pylint: disable=maybe-no-member
    file = service.files().create(body=file_metadata, media_body=media,
                                  fields='id').execute()
    togglePrint and print(F'----> File with ID: "{file.get("id")}" has been added to the Google Drive folder with '
          F'ID "{googleFolderId}".')

  except HttpError as error:
    print(F'***An error occurred: {error}***')
    file = None

  return file.get('id')



############################ share_GoogleDriveFile #############################

def google_share_file(creds, fileId, *emails, togglePrint=True):

  try:
    # create drive api client
    service = build('drive', 'v3', credentials=creds)

    # share with all emails listed
    if (emails):
      for email in emails:
        service.permissions().create(body={"role": "writer", "type": "user", 
            "emailAddress": email}, fileId=fileId).execute()
        togglePrint and print(F'----> File with ID: "{fileId}" was shared with {email}')

  except HttpError as error:
    print(F'***An error occurred: {error}***')



########################## download_GoogleDriveFile ############################

def google_download_file(creds, fileId, fileName, localFolderPath):
  try:
    # create drive api client
    service = build('drive', 'v3', credentials=creds)

    # pylint: disable=maybe-no-member
    request = service.files().get_media(fileId=fileId)
    
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)
    done = False
    while done is False:
      status, done = downloader.next_chunk()
      print(F'Download {int(status.progress() * 100)}.')

  except HttpError as error:
    print(F'An error occurred: {error}')
    file = None

  return file.getvalue()



######################### google_get_files_from_folder #########################

def google_get_files_from_folder(creds, folderId, mimeType='text/csv'):
  try:
    # create drive api client
    service = build('drive', 'v3', credentials=creds)
    files = []
    page_token = None
    while True:
      # pylint: disable=maybe-no-member
      response = service.files().list(q=f"mimeType='{mimeType}' and '{folderId}' in parents and trashed = False",
                                      spaces='drive',
                                      fields='nextPageToken, '
                                              'files(id, name)',
                                      pageToken=page_token).execute()
      for file in response.get('files', []):
        # Process change
        print(F'Found file: {file.get("name")}, {file.get("id")}')
      files.extend(response.get('files', []))
      page_token = response.get('nextPageToken', None)
      if page_token is None:
        break

  except HttpError as error:
    print(F'An error occurred: {error}')
    files = None

  return files



  ######################### google_download_from_folder ##########################

def google_download_from_folder(creds, folderId, localFolderPath):
  files = google_get_files_from_folder(creds, folderId)
  filesInfo = dict()
  for file in files:
    # file fields
    fileId = file.get('id')
    fileName = file.get('name')
    filesInfo[fileName] = fileId
    # download and write to file.
    byteFile = google_download_file(creds, fileId, fileName, localFolderPath)
    f = open(os.path.join(localFolderPath, fileName), "wb")
    f.write(byteFile)
  return filesInfo



################################ move_to_folder ################################

def google_move_to_folder(creds, fileId, folderId):
    try:
        # call drive api client
        service = build('drive', 'v3', credentials=creds)

        # pylint: disable=maybe-no-member
        # Retrieve the existing parents to remove
        file = service.files().get(fileId=fileId, fields='parents').execute()
        previous_parents = ",".join(file.get('parents'))
        # Move the file to the new folder
        file = service.files().update(fileId=fileId, addParents=folderId,
                                      removeParents=previous_parents,
                                      fields='id, parents').execute()

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return file.get('parents')



################################## add_parent ##################################

def google_add_parent(creds, fileId, parentId):
    try:
        # call drive api client
        service = build('drive', 'v3', credentials=creds)

        file = service.files().get(fileId=fileId, fields='parents').execute()
        file = service.files().update(fileId=fileId, addParents=parentId,
                                      fields='id, parents').execute()

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None

    return file.get('parents')



################################ Test Functions ################################

# Tries to download files from the test folder onto the local directory.
def test_driveDownload_functions():
  creds = google_get_creds()
  folderId = google_fetch_folder(creds, 'test')
  google_download_from_folder(creds, folderId, r"C:\Users\alexa\ProgrammingProjects\studyfind\file-processor\test")



# finds a folder with name 'test'
def test_findFolder(creds):
  try:
    # create drive api client
    service = build('drive', 'v3', credentials=creds)
    files = []
    page_token = None
    while True:
      # pylint: disable=maybe-no-member
      # mimeType='application/vnd.google-apps.folder'
      response = service.files().list(q="name='test' and mimeType='application/vnd.google-apps.folder' and trashed = False",
                                      spaces='drive',
                                      fields='nextPageToken, '
                                              'files(id, name)',
                                      pageToken=page_token).execute()
      for file in response.get('files', []):
        # Process change
        print(F'Found file: {file.get("name")}, {file.get("id")}')
      files.extend(response.get('files', []))
      page_token = response.get('nextPageToken', None)
      if page_token is None:
        break

  except HttpError as error:
    print(F'An error occurred: {error}')
    files = None

  for file in files:
    print(file.get('name'))
  return files





############################## Obselete Functions ##############################

# Does not work.
def downloadCSV_GoogleDriveFile(creds, fileId, dirPath):
  try:
    # create drive api client
    # code for downloading files from https://www.casuallycoding.com/download-docs-from-google-drive-api/
    service = build('drive', 'v3', credentials=creds)

    # get fields
    googleDoc = service.files().get(fileId=fileId, fields="name").execute()

    # export
    request = service.files().export_media(fileId=fileId, mimeType='text/csv')
    fh = io.FileIO(googleDoc.get("name")+".csv", mode='w')

    # download
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
      status, done = downloader.next_chunk()
      print(F'Download {int(status.progress() * 100)}.')

  except HttpError as error:
    print(F'An error occurred: {error}')
    fh = None

google_get_creds()