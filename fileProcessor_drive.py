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

############################# getGoogleDriveCreds ##############################

def getGoogleDriveCreds():
  # From the Google Drive API
  creds = None
  SCOPES = ['https://www.googleapis.com/auth/drive']
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          'credentials.json', SCOPES)
      creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
    with open('token.json', 'w') as token:
      token.write(creds.to_json())



########################### fetch_GoogleDriveFolder ############################

def fetch_GoogleDriveFolder(folderName, emails=None):
  creds = None
  SCOPES = ['https://www.googleapis.com/auth/drive']
  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

  try:
    # create drive api client
    service = build('drive', 'v3', credentials=creds)
    response = service.files().list(q=f"mimeType='application/vnd.google-apps.folder' and name = '{folderName}'",
                                      # spaces='drive',
                                      fields='files(id, name)').execute()
    files = response.get('files', [])

    if (len(files) == 0):
      print(f'{folderName} was not found in Google Drive.')
      folderId = create_GoogleDriveFolder(folderName)
      share_GoogleDriveFile(folderId, *emails)
      print(f'{folderName} created in Google Drive.')
      return folderId
    elif (len(files) > 1):
      print(f'More than one folder of name {folderName} were found in Google Drive. Make sure the folder name is unique.')
      return None

  except HttpError as error:
    print(F'An error occurred: {error}')
    files = None

  return files[0].get('id')



########################### create_GoogleDriveFolder ############################

def create_GoogleDriveFolder(folderName, togglePrint=True):
  creds = None
  SCOPES = ['https://www.googleapis.com/auth/drive']
  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

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



########################### storeFile_GoogleDrive ##############################

def storeFile_GoogleDrive(fileName, filePath, mimeType='text/csv', togglePrint=True):
  # confirming credentials
  creds = None
  SCOPES = ['https://www.googleapis.com/auth/drive']
  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
  
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

def storeFile_GoogleFolder(fileName, filePath, googleFolderId, mimeType='text/csv', togglePrint=True):
  creds = None
  SCOPES = ['https://www.googleapis.com/auth/drive']
  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

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

def share_GoogleDriveFile(fileId, *emails, togglePrint=True):
  creds = None
  SCOPES = ['https://www.googleapis.com/auth/drive']
  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

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

def download_GoogleDriveFile(fileId, dirPath):
  creds = None
  SCOPES = ['https://www.googleapis.com/auth/drive']
  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
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



####################### downloadFiles_GoogleDriveFolder ########################

def downloadFiles_GoogleDriveFolder(folderId, dirPath):
  files = fetchFiles_GoogleDriveFolder(folderId)
  for file in files:
    # file fields
    fileId = file.get('id')
    fileName = file.get('name')

    # download and write to file.
    byteFile = download_GoogleDriveFile(fileId, dirPath)
    f = open(fileName, "wb")
    f.write(byteFile)


######################### fetchFiles_GoogleDriveFolder #########################

def fetchFiles_GoogleDriveFolder(folderId, mimeType='text/csv'):
  creds = None
  SCOPES = ['https://www.googleapis.com/auth/drive']
  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
  try:
    # create drive api client
    service = build('drive', 'v3', credentials=creds)
    files = []
    page_token = None
    while True:
      # pylint: disable=maybe-no-member
      response = service.files().list(q=f"mimeType='{mimeType}' and '{folderId}' in parents",
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



################################ Test Functions ################################

# Tries to download files from the test folder onto the local directory.
def test_driveDownlaod_functions():
  getGoogleDriveCreds()
  folderId = fetch_GoogleDriveFolder('test')
  files = fetchFiles_GoogleDriveFolder(folderId)

  # file names
  fileNames = []
  for file in files:
    print(file.get("name"))
    fileNames.append(file.get("name"))

  # download byte code to file
  fileUrls = downloadFiles_GoogleDriveFolder(folderId, os.getcwd())
  for i, url in enumerate(fileUrls):
    # wget.download(url)
    f = open(fileNames[i], "wb")
    f.write(url)
    print('Complete')


# finds a folder with name 'test'
def test_findFolder():
  creds = None
  SCOPES = ['https://www.googleapis.com/auth/drive']
  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
  try:
    # create drive api client
    service = build('drive', 'v3', credentials=creds)
    files = []
    page_token = None
    while True:
      # pylint: disable=maybe-no-member
      # mimeType='application/vnd.google-apps.folder'
      response = service.files().list(q="name='test' and mimeType='application/vnd.google-apps.folder'",
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

# testDownloadCSV()
test_driveDownlaod_functions()
# test_findFolder()
# new issues: tokens may need to be refreshed periodically





############################## Obselete Functions ##############################

# Does not work.
def downloadCSV_GoogleDriveFile(fileId, dirPath):
  creds = None
  SCOPES = ['https://www.googleapis.com/auth/drive']
  if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
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