from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import os
import time
from fileProcessor_drive import *
from fileProcessor_globals import *


# downloads files for all keyword terms provided and all countries provided.
def download_all_files(keyword_terms="", countries="", directory_name="to_upload", default_filename="SearchResults.csv", upload_to_drive=False):
  if upload_to_drive:
    creds = google_get_creds()
  
  download_path = os.path.join(os.getcwd(), directory_name)
  if (not os.path.exists(download_path)):
    os.mkdir(download_path)
  
  clear_folder(download_path)

  options = webdriver.ChromeOptions()
  prefs = {"download.default_directory" : download_path}
  options.add_experimental_option("prefs" , prefs)

  browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
  # browser = webdriver.Chrome(chrome_options=options)
  browser.get(r'https://clinicaltrials.gov/')

  # Download file for each keyword provided.
  for term in keyword_terms:
    autofill_clinicaltrials(browser, download_path, keywords=term)
    new_file_name = update_file_name(keywords=term)

    # move into a "To_Upload" folder 
    old_file_path = os.path.join(download_path, default_filename)
    new_file_path = os.path.join(download_path, new_file_name)
    os.rename(old_file_path, new_file_path)

    # Upload the retrieved file to the Google Drive folder.
    upload_to_drive and upload_file_to_drive(creds, new_file_path)

  # Download file for each country provided.
  for country in countries:
    autofill_clinicaltrials(browser, download_path, country=country)
    new_file_name = update_file_name(country=country)

    old_file_path = os.path.join(download_path, default_filename)
    new_file_path = os.path.join(download_path, new_file_name)
    os.rename(old_file_path, new_file_path)

    upload_to_drive and upload_file_to_drive(creds, new_file_path)



# Downloads a single file from clinicaltrials.gov
def download_file(keywords="", other_keys="", country="", directory_name="to_upload", default_filename="SearchResults.csv", upload_to_drive=False):
  if upload_to_drive:
    creds = google_get_creds()
  
  # Create the folder to store downloads if it does not exist
  download_path = os.path.join(os.getcwd(), directory_name)
  if (not os.path.exists(download_path)):
    os.mkdir(download_path)

  options = webdriver.ChromeOptions()
  prefs = {"download.default_directory" : download_path}
  options.add_experimental_option("prefs" , prefs)

  browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
  # browser = webdriver.Chrome(chrome_options=options)
  browser.get(r'https://clinicaltrials.gov/')

  # Autofill the form to download the file
  autofill_clinicaltrials(browser, download_path, keywords, other_keys, country)

  # update the name
  new_file_name = update_file_name(keywords, other_keys, country)

  # move into a "To_Upload" folder 
  old_file_path = os.path.join(download_path, default_filename)
  new_file_path = os.path.join(download_path, new_file_name)
  os.rename(old_file_path, new_file_path)

  # Upload the retrieved file to the Google Drive folder.
  upload_to_drive and upload_file_to_drive(creds, new_file_path)

  browser.quit()



# Upload a file to the base folder in google drive
def upload_file_to_drive(creds, file_path):
  upload_folder_id = google_fetch_folder(creds, BASE_FOLDER_NAME)
  
  if (upload_folder_id == 0):
    upload_folder_id = google_create_folder(creds, BASE_FOLDER_NAME)
  
  google_upload_into_folder(creds, file_path, upload_folder_id)



# update the name of a file to reflect the search terms used.
def update_file_name(keywords="", other_keys="", country=""):
  new_file_name = f"{keywords}_{other_keys}_{country}"
  while (new_file_name.startswith("_")):
    new_file_name = new_file_name[1:]
  while (new_file_name.endswith("_")):
    new_file_name = new_file_name[:-2]
  return new_file_name + ".csv"



# autofill the clinicaltrials.gov form to download a csv file.
def autofill_clinicaltrials(browser, download_path, keywords="", other_keys="", country="", default_filename="SearchResults.csv"):
  file_path = os.path.join(download_path, default_filename)
  
  # Condition or Disease
  condition_or_disease = browser.find_element(By.ID, 'home-search-condition-query')
  condition_or_disease.send_keys(keywords)

  # Other Terms
  other_terms = browser.find_element(By.ID, 'home-search-other-query')
  other_terms.send_keys(other_keys)

  # Country
  country_dropdown = Select(browser.find_element(By.ID, 'Country'))
  country and country_dropdown.select_by_visible_text(country)

  # Search Button
  search = browser.find_element(By.XPATH, '/html/body/div[8]/div[4]/div[1]/div[2]/form/fieldset/div[7]/div/input')
  search.click()

  # Download Button
  download = browser.find_element(By.ID, 'save-list-link')
  download.click()

  # Number of Studies: Select the highest number of studies possible up to 10000
  number_of_studies = Select(browser.find_element(By.ID, 'number-of-studies'))
  values = ['10000', '1000', '100', '10']
  for value in values:
    try:
      number_of_studies.select_by_value(value)
    except:
      continue
    break

  # Select table columns: select all available columns
  table_columns = Select(browser.find_element(By.ID, 'which-fields'))
  table_columns.select_by_value('all')

  # Select file format: select csv
  table_columns = Select(browser.find_element(By.ID, 'which-format'))
  table_columns.select_by_value('csv')
      
  # Final Download Button
  final_download = browser.find_element(By.XPATH, '/html/body/div[8]/div[3]/div[2]/div[1]/div/div[2]/div[1]/div[4]/div/div/div/form[1]/div[5]/input')
  final_download.click()

  # wait until the file is downloaded.
  while (not os.path.exists(file_path)):
    pass

  time.sleep(1)

  # Start over button
  start_over = browser.find_element(By.ID, 'modify-start-over')
  start_over.click()



# Clears a folder
def clear_folder(folderPath):
  for fileName in os.listdir(folderPath):
    filePath = os.path.join(folderPath, fileName)
    if (os.path.isfile(filePath)):
      os.remove(filePath)