# Written by Alexander Zhu
from __future__ import print_function
import os
import time
import pandas as pd

from fileProcessor_drive import *
from emailerFunc import studyfind_sendEmails
from emailerIndexed import studyfind_sendEmails_indexed
from webscraperFunc import runWebscraper



# look up how to get a refresh token

def processFilesInFolder(baseFolderName, processingFn=None, fileType='.csv',
  splitSizes=[], defaultSplitSize=50, removeDuplicatesFn=None, processedFolderName='processed', 
  toEmailFolderName='to_email', togglePrint=True, emails=[]):

  # get creds and refresh if needed.
  creds = google_get_creds()

  # Get the path for the directory with baseFolderName
  baseFolderPath = getDirectoryPath(baseFolderName, togglePrint=togglePrint)
  if (baseFolderPath == None):
    print("*** No directory found. Ending program. ***")
    return
  else:
    togglePrint and print("Directory found! \n")

  # Download files from folder 'baseFolderName' in Google Drive into the folder.
  # Find Google Drive Folder
  baseFolderId = google_fetch_folder(creds, baseFolderName)
  if (baseFolderId == 0):
    baseFolderId = google_create_folder(creds, baseFolderName)
    google_share_file(creds, baseFolderId, *emails)
    print(f"'{baseFolderName}' created in Google Drive. Please fill this folder with files to be processed.")
    return
  elif (baseFolderId == 1):
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
  elif (processedFolderId == 1):
    return
  
  # Warning
  print("\n***ATTENTION! Processed files will be deleted.***")
  emailFolderPath = createFolder(baseFolderPath, toEmailFolderName)

  # Loop through all files
  for fileName in os.listdir(baseFolderPath):
    filePath = os.path.join(baseFolderPath, fileName)
    # only process files
    if (os.path.isfile(filePath)):
      if (fileName.endswith(fileType)):
        togglePrint and print(f"Processing {fileName}...")
        newFilePath = processFile(filePath, processingFn)
        # delete the old file
        if (os.path.isfile(filePath)):
          os.remove(filePath)
        # move the new one into the folder
        filePath = moveFileToFolder(newFilePath, baseFolderPath, togglePrint=togglePrint)

        # If a removeDuplicates function is provided, use it.
        if (removeDuplicatesFn):
          removeDuplicatesFn(filePath)
          togglePrint and print(f"--> Duplicates have been removed.")
        
        # If files need to be split, split them (only for .csv files for now)
        # other options will be added as needed.
        if (fileType == '.csv'):
          splitCSVIntoChunks(creds, filePath, emailFolderPath, splitSizes, defaultSize=defaultSplitSize, togglePrint=togglePrint, emails=emails)
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



############################ getDirectoryPath ##################################

# Gets the path to the directory containing all csv files, makes a new 
# directory with 'baseFolderName' if none is found. Disable folder creation by setting
# createDir to False.
def getDirectoryPath(baseFolderName, togglePrint=True):
  baseFolderPath = os.path.join(os.getcwd(), baseFolderName)
  if (not os.path.exists(baseFolderPath)):
    os.mkdir(baseFolderPath)
    # print(f"*** Created a '{baseFolderName}' folder. Please add files into this folder for processing. ***")
  return baseFolderPath



############################## createFolder ####################################

def createFolder(path, folderName):
  folderPath = os.path.join(path, folderName)
  if (not os.path.exists(folderPath)):
    os.mkdir(folderPath)
    # print(f"*** Created a '{baseFolderName}' folder. Please add files into this folder for processing. ***")
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


############################# splitCSVIntoChunks ###############################

# For splitting one file into specific sized chunks
# will split file into all defined chunkSizes if possible
# any remaining rows in the file will be split according to defaultSize
# if defaultSize=None, any remaining rows will be added into a single file.
def splitCSVIntoChunks(creds, filePath, parentFolderPath, chunkSizes, defaultSize=None, togglePrint=True, emails=[]):
  # creates a folder with the same name as the file to hold the split files.
  fileName = os.path.basename(filePath)
  childFolderName = str(fileName.split('.')[0])
  childFolderPath = os.path.join(parentFolderPath, childFolderName)
  if (not os.path.exists(childFolderPath)):
    os.mkdir(childFolderPath)
    togglePrint and print(f"--> Created the '{childFolderName}' folder to store the split files.")
  
  # creates a google folder for the files
  googleFolderId = google_create_folder(creds, childFolderName, togglePrint=togglePrint)
  google_share_file(creds, googleFolderId, *emails, togglePrint=togglePrint)

  data = pd.read_csv(filePath)
  data = data.rename(columns={' Contact Name':'Name', ' Contact Email':'Email'})
  dataIndex, fileIndex = 0, 0

  # split into specified chunk sizes
  for chunk in chunkSizes:
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
    googleFileId = google_upload_into_folder(creds, splitFilePath, googleFolderId, togglePrint=togglePrint)
  
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
        googleFileId = google_upload_into_folder(creds, splitFilePath, googleFolderId, togglePrint=togglePrint)

    # if there is no default size, put all the remaining data into one file
    else:
      df = data[dataIndex:len(data)]
      splitFileName=f"{fileIndex}_{fileName}"
      splitFilePath = os.path.join(childFolderPath, splitFileName) 
      df.to_csv(splitFilePath, index=False)
      togglePrint and print(f"No chunk sizes remaining. No defaultSize provided, so all remaining data is stored in: '{splitFileName}'")
      google_upload_into_folder(creds, splitFilePath, googleFolderId, togglePrint=togglePrint)



########################## studyfind_removeDupEmails ###########################

def studyfind_removeDupEmails_inPlace(filePath):
  df = pd.read_csv(filePath)
  df.drop_duplicates(subset=[' Contact Email'], inplace=True)
  # erases the current content of the file
  file = open(filePath, 'w')
  df.to_csv(filePath, mode='a', index=False)
  file.close()


################################ sendEmails ####################################

# to add: function that sends emails without using split files.
# by default, will use the current directory as the path to create folders
# indexedEmailsFn MUST take: filePath, startIndex, numberOfEmails
def sendEmails_indexed(filePath, indexedEmailsFn, baseFolderPath=None, fileType='.csv', 
        sentFolderName='sent', startIndex=0, endIndex=-1, numEmails=50, delay=30, togglePrint=True):

  # if baseFolderPath is none, use the parent directory of the current file
  if (not baseFolderPath):
    baseFolderPath = os.path.baseFolderName(filePath)

  folderPath = os.path.join(baseFolderPath, sentFolderName)
  if (not os.path.exists(folderPath)):
    os.mkdir(folderPath)
  
  if (fileType == '.csv'):
    if (endIndex == -1):
      fileLen = len(pd.read_csv(filePath))
    else:
      fileLen = min(endIndex, len(pd.read_csv(filePath)))
    
    emailIndex = startIndex
    while (emailIndex < fileLen):
      emailsToSend = min(numEmails, fileLen-emailIndex)

      # send email
      indexedEmailsFn(filePath, startIndex=emailIndex, numEmails=emailsToSend)
      togglePrint and print(f"--> ({min(emailsToSend, fileLen)}) total emails have been sent.")
      
      # delay between sends
      time.sleep(delay)
      # update index
      emailIndex += numEmails
  
  # move file
  fileName = os.path.baseFoldername(filePath)
  os.rename(filePath, os.path.join(folderPath, fileName))
  togglePrint and print(f"All '{fileName}' emails have been sent. File moved to the '{sentFolderName}' folder.")


############################ TESTING FUNCTIONS #################################


processFilesInFolder('test', processingFn=runWebscraper)
