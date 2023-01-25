# Written by Alexander Zhu
from __future__ import print_function
import os
import time
import pandas as pd

from fileProcessor_drive import *
from fileProcessor_emailer import studyfind_sendEmails
from fileProcessor_globals import *


def process_files(processingFn=None, fileType='.csv',
  splitSizes=[], defaultSplitSize=1000, removeDuplicatesFn=None, processedFolderName='processed', 
  EMAIL_FOLDER_NAME=EMAIL_FOLDER_NAME, togglePrint=True, emails=[]):

  # get creds and refresh if needed.
  creds = google_get_creds()

  # Get the path for the directory with baseFolderName
  baseFolderPath = getDirectoryPath(BASE_FOLDER_NAME, togglePrint=togglePrint)
  if (baseFolderPath == None):
    print("*** No directory found. Ending program. ***")
    return
  else:
    togglePrint and print(f"Directory found with name '{BASE_FOLDER_NAME}' \n")

  # Clear the folder of all old files.
  clearFolder(baseFolderPath)

  # Download files from folder 'BASE_FOLDER_NAME' in Google Drive into the folder.
  # Find Google Drive Folder
  baseFolderId = google_fetch_folder(creds, BASE_FOLDER_NAME)
  if (baseFolderId == 0):
    baseFolderId = google_create_folder(creds, BASE_FOLDER_NAME)
    google_share_file(creds, baseFolderId, *emails)
    print(f"'{BASE_FOLDER_NAME}' created in Google Drive. Please fill this folder with files to be processed.")
    return
  elif (baseFolderId == -1):
    print(f"Error fetching or creating '{BASE_FOLDER_NAME}' on Google Drive.")
    return

  emailFolderId = google_fetch_folder(creds, EMAIL_FOLDER_NAME)
  if (emailFolderId == 0):
    emailFolderId = google_create_folder(creds, EMAIL_FOLDER_NAME)
    google_share_file(creds, emailFolderId, *emails)
    print(f"'{EMAIL_FOLDER_NAME}' created in Google Drive. This folder will be used to store files prepared for emailing.")
  elif (emailFolderId == -1):
    print(f"Error fetching or creating '{EMAIL_FOLDER_NAME}' on Google Drive.")
    return

  # Download contents into baseFolderName folder.
  filesInfo = google_download_from_folder(creds, baseFolderId, baseFolderPath)
  if (len(filesInfo) == 0):
    print("No files in the google drive folder.")
  # move the files into the processed folder in Google Drive
  processedFolderId = google_fetch_folder(creds, processedFolderName)
  if (processedFolderId == 0):
    processedFolderId = google_create_folder(creds, processedFolderName)
    google_add_parent(creds, processedFolderId, baseFolderId)
    google_share_file(creds, baseFolderId, *emails)
    print(f"'{processedFolderName}' created in Google Drive.")
  elif (processedFolderId == -1):
    return
  
  # Warning
  print("\n***ATTENTION! Processed files will be deleted.***")
  emailFolderPath = getDirectory(baseFolderPath, EMAIL_FOLDER_NAME)

  # Loop through all files
  for fileName in os.listdir(baseFolderPath):
    filePath = fixFileName(os.path.join(baseFolderPath, fileName))
    # only process files
    if (os.path.isfile(filePath)):
      if (fileName.endswith(fileType)):
        togglePrint and print(f"Processing {fileName}...")
        newFilePath = processFile(filePath, processingFn)

        # check for errors
        if (newFilePath == -1):
          continue

        # delete the old file
        if (os.path.isfile(filePath)):
          os.remove(filePath)

        # move the new one into the folder
        filePath = newFilePath

        # If a removeDuplicates function is provided, use it.
        if (removeDuplicatesFn):
          removeDuplicatesFn(filePath)
          togglePrint and print(f"--> Duplicates have been removed.")
        
        # If files need to be split, split them (only for .csv files for now)
        # other options will be added as needed.
        if (fileType == '.csv'):
          splitCSV(creds, filePath, emailFolderPath, emailFolderId, splitSizes, defaultSize=defaultSplitSize, togglePrint=togglePrint, emails=emails)
        else:
          print("Invalid file type.")
          continue
        
        # delete the file that was used to create split files
        if (os.path.isfile(filePath)):
          os.remove(filePath)
        
        # after processing is done, move the file into the processed folder.
        google_add_parent(creds, filesInfo[fileName], processedFolderId)
        print(f"{fileName} moved to processed folder in Google Drive")

        togglePrint and print(f"Complete!\n")

      # if file is not a .fileType file, does not process it.
      else:
        print(f"*** '{fileName}' is not a '{fileType}' file. Skipped this file in processing. ***\n")
    
  print("ALL FILES PROCESSED!")


########################### sendEmailsFromFolder ###############################
  
def send_emails(delay=5, fileType='.csv', processedFolderName="emailed", togglePrint=True, emails=[]):
  # get creds and refresh if needed.
  creds = google_get_creds()

  # Get the path for the directory with baseFolderName
  emailFolderPath = getDirectoryPath(EMAIL_FOLDER_NAME, togglePrint=togglePrint)
  if (emailFolderPath == None):
    print("*** No directory found. Ending program. ***")
    return
  else:
    togglePrint and print("Directory found! \n")

  # Clear the folder of all old files.
  clearFolder(emailFolderPath)

  # Download files from folder 'baseFolderName' in Google Drive into the folder.
  # Find Google Drive Folder
  emailFolderId = google_fetch_folder(creds, EMAIL_FOLDER_NAME)
  if (emailFolderId == 0):
    emailFolderId = google_create_folder(creds, EMAIL_FOLDER_NAME)
    google_share_file(creds, emailFolderId, *emails)
    print(f"'{EMAIL_FOLDER_NAME}' created in Google Drive. Please fill this folder with files to be processed.")
    return
  elif (emailFolderId == -1):
    print(f"Error fetching or creating '{EMAIL_FOLDER_NAME}' on Google Drive.")
    return

  # Download contents into EMAIL_FOLDER_NAME folder.
  filesInfo = google_download_n_from_folder(creds, emailFolderId, emailFolderPath, 1)
  if (len(filesInfo) == 0):
    print("No emails to send.")

  # create the processed folder in Google Drive
  processedFolderId = google_fetch_folder(creds, processedFolderName)
  if (processedFolderId == 0):
    processedFolderId = google_create_folder(creds, processedFolderName)
    google_add_parent(creds, processedFolderId, emailFolderId)
    google_share_file(creds, emailFolderId, *emails)
    print(f"'{processedFolderName}' created in Google Drive.")
  elif (processedFolderId == -1):
    return
  
  # Warning
  print("\n***ATTENTION! Processed files will be deleted.***")

  # Loop through all files
  for fileName in os.listdir(emailFolderPath):
    filePath = fixFileName(os.path.join(emailFolderPath, fileName))
    # only process files
    if (os.path.isfile(filePath)):
      if (fileName.endswith(fileType)):
        togglePrint and print(f"Emailing from {fileName}...")
        studyfind_sendEmails(filePath, subject_lines=SUBJECT_LINES, email_body=EMAIL_BODY)
        time.sleep(delay)

        # delete the file that was used to create split files
        if (os.path.isfile(filePath)):
          os.remove(filePath)
        
        # after emailing is done, move the file into the processed folder.
        google_add_parent(creds, filesInfo[fileName], processedFolderId)
        print(f"{fileName} moved to '{processedFolderName} folder in Google Drive")

        togglePrint and print(f"Complete!\n")

      # if file is not a .fileType file, does not process it.
      else:
        print(f"*** '{fileName}' is not a '{fileType}' file. Skipped this file in processing. ***\n")
    
  print("ALL EMAILS SENT!")


############################ getDirectoryPath ##################################

# Gets the path to the directory containing all csv files, makes a new 
# directory with 'baseFolderName' if none is found.

def getDirectoryPath(baseFolderName, togglePrint=True):
  baseFolderPath = os.path.join(os.getcwd(), baseFolderName)
  if (not os.path.exists(baseFolderPath)):
    os.mkdir(baseFolderPath)
  return baseFolderPath



############################## getDirectory ####################################

def getDirectory(path, folderName):
  folderPath = os.path.join(path, folderName)
  if (not os.path.exists(folderPath)):
    os.mkdir(folderPath)
  return folderPath


############################### processFile ####################################

# Processes a file using its filePath (insert function inside)
# This function MUST return the filePath of the processed file.
def processFile(filePath, processingFn):
  return processingFn(filePath)



############################# moveFileToFolder #################################

# Moves a file to a specified folder
def moveFileToFolder(filePath, folderPath, togglePrint=True):
  folderName = os.path.basename(folderPath)
  fileName = os.path.basename(filePath)

  # create the 'to_split' directory if it does not exist
  if (not os.path.exists(folderPath)):
    os.mkdir(folderPath)
    togglePrint and print(f"--> Created the '{folderName}' folder because the folder was not found.")
  
  # move the new file into the 'to_split' folder. make sure the file exists.
  if (os.path.isfile(filePath)):
    newPath = os.path.join(folderPath, fileName)
    os.rename(filePath, newPath)
    togglePrint and print(f"Moved '{fileName}' to the '{folderName}' folder.")
    return newPath
  else:
    togglePrint and print(f"--> '{fileName}' is not a file in the current folder.")
    return None


############################# splitCSV ###############################

# For splitting one file into specific sized chunks
# will split file into all defined chunkSizes if possible
# any remaining rows in the file will be split according to defaultSize
# if defaultSize=None, any remaining rows will be added into a single file.
def splitCSV(creds, filePath, parentFolderPath, parentFolderId, splitSizes, defaultSize=None, togglePrint=True, emails=[]):
  # creates a folder with the same name as the file to hold the split files.
  fileName = os.path.basename(filePath)
  # childFolderName = str(fileName.split('.')[0])
  # childFolderPath = getDirectory(parentFolderPath, childFolderName)
  childFolderPath = parentFolderPath
  
  # creates a google folder for the files
  # googleFolderId = google_create_folder(creds, childFolderName, togglePrint=togglePrint)
  # google_share_file(creds, googleFolderId, *emails, togglePrint=togglePrint)

  data = pd.read_csv(filePath)
  data = data.rename(columns={' Contact Name':'Name', ' Contact Email':'Email'})
  dataIndex, fileIndex = 0, 0

  # split into specified chunk sizes
  for chunk in splitSizes:
    df = data[dataIndex:min(dataIndex+chunk, len(data))]
    splitFileName = f"{fileIndex}_{fileName}"
    splitFilePath = os.path.join(childFolderPath, splitFileName) 
    df.to_csv(splitFilePath, index=False)

    # increment indices
    dataIndex += chunk
    if (dataIndex >= len(data)):
      break
    fileIndex += 1

    togglePrint and print(f"Created split file of size {chunk} named '{splitFileName}'")
    googleFileId = google_upload_into_folder(creds, splitFilePath, parentFolderId, togglePrint=togglePrint)
  
  # if there is still data left after the chunks are made
  if (dataIndex < len(data)):
    # if there is a default size, split the remaining data into default size files
    if (defaultSize):
      while (dataIndex < len(data)):
        df = data[dataIndex:min(dataIndex+defaultSize, len(data))]
        splitFileName = f"{fileIndex}_{fileName}"
        splitFilePath = os.path.join(childFolderPath, splitFileName) 
        df.to_csv(splitFilePath, index=False)

        # increment indices
        dataIndex += defaultSize
        fileIndex += 1

        togglePrint and print(f"No chunk sizes remaining. Created split file of default size {defaultSize} named: '{splitFileName}'")
        googleFileId = google_upload_into_folder(creds, splitFilePath, parentFolderId, togglePrint=togglePrint)

    # if there is no default size, put all the remaining data into one file
    else:
      df = data[dataIndex:len(data)]
      splitFileName=f"{fileIndex}_{fileName}"
      splitFilePath = os.path.join(childFolderPath, splitFileName) 
      df.to_csv(splitFilePath, index=False)
      togglePrint and print(f"No chunk sizes remaining. No defaultSize provided, so all remaining data is stored in: '{splitFileName}'")
      google_upload_into_folder(creds, splitFilePath, parentFolderId, togglePrint=togglePrint)



########################## studyfind_removeDupEmails ###########################

def studyfind_removeDupEmails_inPlace(filePath):
  df = pd.read_csv(filePath)
  df.drop_duplicates(subset=[' Contact Email'], inplace=True)
  # erases the current content of the file
  file = open(filePath, 'w')
  df.to_csv(filePath, mode='a', index=False)
  file.close()


################################ fixFileName ###################################

def fixFileName(filePath):
  newName = os.path.basename(filePath).replace(" ", "_")
  newParent = os.path.dirname(filePath)
  newPath = os.path.join(newParent, newName)
  os.rename(filePath, newPath)
  return newPath


################################ clearFolder ###################################

def clearFolder(folderPath):
  for fileName in os.listdir(folderPath):
    filePath = os.path.join(folderPath, fileName)
    if (os.path.isfile(filePath)):
      os.remove(filePath)
