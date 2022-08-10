# Written by Alexander Zhu
from __future__ import print_function
import os
import pandas as pd

# import google.auth
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials


############################ ProcessFilesInDir #################################

def processFilesInDir(dirName, processingFunc, fileType='.csv', createDir=True, 
  moveNewFiles=False, splitFiles=False, splitSize=50, deleteProcessed=False, 
  deleteNewFiles=False, removeDuplicatesFn=None, processedFolderName='processed', 
  newFilesFolderName='new_files', togglePrint=True, uploadToGoogleDrive=False):

  # Get the path for the directory with dirName
  dirPath = getDirectoryPath(dirName, createDir, togglePrint=togglePrint)
  if (dirPath == None):
    print("*** No directory found. Ending program. ***")
    return
  else:
    togglePrint and print("Directory found! \n")

  # If the folder is empty, give a warning
  folderContents = os.listdir(dirPath)
  if (len(folderContents) == 0):
    print(f"*** The '{dirName}' folder is empty. Please add '{fileType}' files into this folder for processing. ***")
    return
  
  # To prevent accidentally deleting files. Prompt only accepts 'y' to continue
  # to prevent accidental key presses from continuing the program.
  if (deleteProcessed or deleteNewFiles):
    cont = input(f"*** ATTENTION! Running program with deleteProcessed={deleteProcessed} and deleteNewFiles={deleteNewFiles}. Files will be deleted! ***\nContinue (y/n)? ").lower()
    if (cont != 'y'):
      print(f"Program aborted. To change delete preferences, edit the 'deleteProcessed' and 'deleteNewFiles' values when calling the 'processFilesInDir' function.")
      return
  
  # If deleteDuplicatesFn is provided, provide a warning message.
  if (removeDuplicatesFn):
    togglePrint and print(f"Duplicates will be removed using the '{removeDuplicatesFn}' function.\n")

  # Loop through all files
  for fileName in os.listdir(dirPath):
    filePath = os.path.join(dirPath, fileName)
    # only process files
    if (os.path.isfile(filePath)):
      if (fileName.endswith(fileType)):
        # First check if this file has already been processed (or one with the same name as this causes errors)
        if (checkIfAlreadyProcessed(fileName, dirPath, processedFolderName)):
          print(f"*** A file with name '{fileName}' has already been processed. Please delete the previously processed file, or change the name of the current file to avoid errors. ***")
          return

        togglePrint and print(f'Processing {fileName}...')
        processFile(fileName, filePath, processingFunc)
        storeFile(fileName, filePath, dirPath, processedFolderName, createDir=createDir, deleteProcessed=deleteProcessed, togglePrint=togglePrint)
        # If there are NEW files that are written and moveNewFiles=True, move them.
        if (moveNewFiles):
          filePath = moveNewFile(fileName, dirPath, newFilesFolderName, createDir=createDir, togglePrint=togglePrint)
        # If a removeDuplicates function is provided, use it.
        if (removeDuplicatesFn):
          removeDuplicatesFn(filePath)
          togglePrint and print(f"--> Duplicates have been removed.")
        # If files need to be split, split them (only for .csv files for now)
        # other options will be added as needed.
        if (splitFiles):
          if (fileType == '.csv'):
            splitCSVFile(fileName, filePath, dirPath, splitSize, togglePrint=togglePrint, uploadToGoogleDrive=uploadToGoogleDrive)
          elif (fileType == '.tsv'):
            pass
        # If files are not to be split, but they should be uploaded to Google Drive
        elif (uploadToGoogleDrive):
          storeFileInGoogleDrive(fileName, filePath, togglePrint=togglePrint)

        # If deleteNewFiles is enabled, delete the new file via 'filePath'
        if (deleteNewFiles and os.path.isfile(filePath)):
          os.remove(filePath)
          togglePrint and print(f"'{fileName}' deleted.")

        togglePrint and print(f"Complete!\n")

      # if file is not a .fileType file, does not process it.
      else:
        print(f"*** '{fileName}' is not a '{fileType}' file. Skipped this file in processing. ***\n")
  
  print("ALL FILES PROCESSED!")



########################### checkIfAlreadyProcessed ############################

# checks if a file with 'fileName' has already been processed
def checkIfAlreadyProcessed(fileName, dirPath, processedFolderName):
  processedFolderPath = os.path.join(dirPath, processedFolderName)
  processedFileName = 'p-' + fileName
  # check if the processed folder exists, and see if the fileName is already there.
  if (os.path.isdir(processedFolderPath)):
    return processedFileName in os.listdir(processedFolderPath)
  # if the folder does not exist, just check in the current folder, or the data sheets folder
  else:
    return (processedFileName in os.listdir(os.getcwd())) or (processedFileName in os.listdir(dirPath))




############################ getDirectoryPath ##################################

# Gets the path to the directory containing all csv files, makes a new 
# directory with 'dirName' if none is found. Disable folder creation by setting
# createDir to False.
def getDirectoryPath(dirName, createDir=True, togglePrint=True):
  dirPath = os.path.join(os.getcwd(), dirName)
  if (dirName not in os.listdir()):
    if (createDir):
      # if no folder with target name is found, create it.
      os.mkdir(dirPath)
      print(f"*** Created a '{dirName}' folder. Please add files into this folder for processing. ***")
    else:
      print(f"*** No folder created (createDir=False). Please change the name of the target folder, or create a folder manually. ***")
      dirPath = None
  return dirPath



############################### processFile ####################################

# Processes a file using its fileName and pathName (insert function inside)
def processFile(fileName, filePath, processingFunc):
  processingFunc(fileName, filePath)



################################ storeFile #####################################

# After a file is processed, store it in a folder called 'processed'
def storeFile(fileName, filePath, dirPath, folderName, createDir=True, deleteProcessed=False, togglePrint=True):
  # if the file is to be deleted, delete it and return from the function
  if (deleteProcessed and os.path.isfile(filePath)):
    os.remove(filePath)
    togglePrint and print(f"'p-{fileName}' deleted.")
    return

  folderPath = os.path.join(dirPath, folderName)
  folderExists = False
  
  # create the 'processed' folder if it does not exist
  if (folderName not in os.listdir(dirPath)):
    if (createDir):
      os.mkdir(folderPath)
      togglePrint and print(f"--> Created the '{folderName}' folder because the folder was not found.")
      folderExists = True
    else:
      togglePrint and print(f"--> '{folderName}' folder was not found. No new folders created (createDir is set to False).")
  else:
    folderExists = True

  # move the current file to the 'processed' folder if it exists.
  if (folderExists):
    os.rename(filePath, os.path.join(folderPath, 'p-' + fileName))
    togglePrint and print(f"Moved '{fileName}' to the '{folderName}' folder. 'p-' tag added to file name.")
  # otherwise, just add the tag to the file.
  else:
    os.rename(filePath, os.path.join(os.getcwd(), 'p-' + fileName))
    togglePrint and print(f"'{folderName}' folder does not exist. 'p-' tag added to file name.")



############################### moveNewFile ####################################

# For Studyfind Automation: moves new webscraped files into a "to_split" folder.
# This function relies on the fact that the webscraper code writes the data
# into a NEW csv file with the same file name, but creates it in the current directory.
# RETURNS the path to the new file.
def moveNewFile(fileName, dirPath, folderName, createDir=True, togglePrint=True):
  folderPath = os.path.join(dirPath, folderName)
  folderExists = False

  # create the 'to_split' directory if it does not exist
  if (folderName not in os.listdir(dirPath)):
    if (createDir):
      os.mkdir(folderPath)
      togglePrint and print(f"--> Created the '{folderName}' folder because the folder was not found.")
      folderExists = True
    else:
      togglePrint and print(f"--> '{folderName}' folder was not found. No new folders created (createDir is set to False).")
  else:
    folderExists = True
  
  # move the new file into the 'to_split' folder. make sure the file exists.
  if (folderExists):
    newFilePath = os.path.join(os.getcwd(), fileName)
    if (os.path.isfile(newFilePath)):
      newPath = os.path.join(folderPath, fileName)
      os.rename(newFilePath, newPath)
      togglePrint and print(f"Moved the new version of '{fileName}' to the '{folderName}' folder.")
      return newPath
    else:
      togglePrint and print(f"--> '{fileName}' is not a file in the current folder.")



############################### splitCSVFile ###################################

# Splits a .csv file into files of a maximum size
# This function has NO createDir parameter, as folders MUST be created.
def splitCSVFile(fileName, filePath, dirPath, splitSize, folderName="split_files", togglePrint=True, uploadToGoogleDrive=False):
  parentFolderPath = os.path.join(dirPath, folderName)

  # create the 'to_split' directory if it does not exist
  if (folderName not in os.listdir(dirPath)):
    os.mkdir(parentFolderPath)
    togglePrint and print(f"--> Created the '{folderName}' folder because the folder was not found.")
  
  # creates a folder with the same name as the file to hold the split files.
  childFolderName = str(fileName.split('.')[0])
  if (childFolderName not in os.listdir(parentFolderPath)):   
    childFolderPath = os.path.join(parentFolderPath, childFolderName)
    os.mkdir(childFolderPath)
    togglePrint and print(f"--> Created the '{childFolderName}' folder to store the split files.")

  # creates a google folder for the files if uploadToGoogleDrive=True
  googleFolderId = None
  if (uploadToGoogleDrive):
    googleFolderId = createGoogleDriveFolder(childFolderName, togglePrint=togglePrint)

  # splits the files
  data = pd.read_csv(filePath)
  data.rename(columns={' Contact Name':'Name'})
  data.rename(columns={' Contact Email':'Email'})
  total = len(data)
  splits = (total//splitSize + 1) if (total % splitSize != 0) else (total//splitSize)
  for i in range(splits):
    # gets a data frame of size 'size' and converts it into a csv file.
    df = data[splitSize*i:splitSize*(i+1)]
    splitFileName = f"{i}_{fileName}"
    splitFilePath = os.path.join(childFolderPath, splitFileName)
    df.to_csv(splitFilePath, index=False)

    # adds file to the google folder created previously
    if (uploadToGoogleDrive):
      googleFileId = storeFileInGoogleFolder(splitFileName, splitFilePath, googleFolderId, togglePrint=togglePrint)

  togglePrint and print(f"{splits} split file(s) added to the '{childFolderName}' folder.")



########################## studyfind_removeDupEmails ###########################

def studyfind_removeDupEmails_inPlace(filePath):
  df = pd.read_csv(filePath)
  df.drop_duplicates(subset=[' Contact Email'], inplace=True)
  # erases the current content of the file
  file = open(filePath, 'w')
  df.to_csv(filePath, mode='a', index=False)
  file.close()



########################### createGoogleDriveFolder ############################

def createGoogleDriveFolder(folderName, togglePrint=True):
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
    togglePrint and print(F'*GOOGLE* Google Drive folder has been created with ID: "{file.get("id")}".')

  except HttpError as error:
    print(F'***An error occurred: {error}***')
    file = None

  return file.get('id')



########################### storeFileInGoogleDrive #############################

def storeFileInGoogleDrive(fileName, filePath, mimeType='text/csv', togglePrint=True):
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
    togglePrint and print(F'*GOOGLE* File ID: {file.get("id")} was uploaded to Google Drive.')

  except HttpError as error:
    print(F'***An error occurred: {error}***')
    file = None

  return file.get('id')



########################### storeFileInGoogleDrive #############################

def storeFileInGoogleFolder(fileName, filePath, googleFolderId, mimeType='text/csv', togglePrint=True):
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
    togglePrint and print(F'*GOOGLE* File with ID: "{file.get("id")}" has been added to the Google Drive folder with '
          F'ID "{googleFolderId}".')

  except HttpError as error:
    print(F'***An error occurred: {error}***')
    file = None

  return file.get('id')



############################# studyfind_sendEmail ##############################

def studyfind_sendEmail(dirPath):
  pass