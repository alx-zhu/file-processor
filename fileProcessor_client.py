# Written by Alexander Zhu
from webscraperFunc import runWebscraper
from fileProcessor_lib import processFilesInDir, studyfind_removeDupEmails_inPlace, splitCSVIntoChunks, sendEmails_indexed
from emailerIndexed import studyfind_sendEmails_indexed
from fileProcessor_cloud import *


### Processes all csv files in the directory named 'dirName'
  # dirName: the folder name where the files to be processed are stored.
  # processingFunc: the function used to process the files.
    # function must take 2 parameters: fileName and filePath
    
# processFilesInDir('TEST_data_sheets', runWebscraper, moveNewFiles=True, 
#   newFilesFolderName="to_split", splitFileFolderName="_to_email", splitFiles=True, splitSize=5, 
#   removeDuplicatesFn=studyfind_removeDupEmails_inPlace, uploadToGoogleDrive=False) 

# processFilesInDir(dirName, processingFunc, fileType='.csv', createDir=True, 
#   moveNewFiles=False, splitFiles=False, splitSize=50, deleteProcessed=False, 
#   deleteNewFiles=False, removeDuplicatesFn=None, processedFolderName='processed', 
#   newFilesFolderName='new_files', togglePrint=True, uploadToGoogleDrive=False)

### Optional parameters:
  # suffix: '.csv' by default. change to match the type of file being processed.
  # createDir: when True, creates new folders if they are not found (default: True)
    # works best when set to True
  # moveNewFiles: set to True if the processing writes a NEW file, that has to be stored
  # splitFiles: set to False by default, calls the split file function and splits the files into smaller segments.
  # splitSize: set to 50 by default, changes the size of splits if you want to split the file.
  # deleteProcessed: set to False by default, if enabled, deletes files that have the 'p-' label
    # NOTE: For studyfind, set this to True to prevent clutter of files.
  # deleteNewFiles: set to False by default, if enabled, deletes new files created from processing
  # processedFolderName: the name of the folder created for processed files
  # newFilesFolderName: the name of the folder created for new files written from processing
  # splitFileFOlderName: the name of the folder that holds the split files
  # removeDuplicatesFn: default None. pass in a function that takes a file path, and removes duplicates.
    # if this is not None, duplicates will be removed using the function provided.
  # newFilesFolderName: set the folder name where the NEW files will be stored.
  # togglePrint: default True. sets whether print statements will be shown or not. 
    # NOTE: essential warnings will still be printed regardless of the setting.
    # NOTE: recommend to keep print statements ON unless there is explicit need to turn them OFF.
      # information in print statements explain any issues/actions taken
  # uploadToGoogleDrive: default False. sets whether final files will be uploaded to Google Drive.
  # emails: default None. If files should be shared with specific people, emails=[list/tuple of emails to share with


# sendEmails_indexed(r'C:\Users\alexa\ProgrammingProjects\studyfind\file-processor\data_sheets\_to_email\MentalHealth-Data\5_MentalHealth-Data.csv', studyfind_sendEmails_indexed, numEmails=50, delay=70)



