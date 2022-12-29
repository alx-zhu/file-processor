from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import os
import time

# To do: Get search terms standardized for each group

def download_file(keywords="", other_keys="", country="United States", directory_name="to_upload", default_filename="SearchResults.csv"):
  # Create the folder to store downloads if it does not exist
  download_path = os.path.join(os.getcwd(), directory_name)
  if (not os.path.exists(download_path)):
    os.mkdir(download_path)

  options = webdriver.ChromeOptions()
  prefs = {"download.default_directory" : download_path}
  options.add_experimental_option("prefs" , prefs)
  # browser.maximize_window()

  browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
  # browser = webdriver.Chrome(chrome_options=options)
  browser.get(r'https://clinicaltrials.gov/')

  # Condition or Disease
  condition_or_disease = browser.find_element(By.ID, 'home-search-condition-query')
  condition_or_disease.send_keys(keywords)

  # Other Terms
  other_terms = browser.find_element(By.ID, 'home-search-other-query')
  other_terms.send_keys(other_keys)

  # Country
  country_dropdown = Select(browser.find_element(By.ID, 'Country'))
  country_dropdown.select_by_visible_text(country)

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
  time.sleep(5)

  # update the name
  new_file_name = f"{keywords}_{other_keys}_{country}.csv"
  while (new_file_name.startswith("_")):
    new_file_name = new_file_name[1:]

  # upload into a "To_Upload" folder 
  old_file_path = os.path.join(download_path, default_filename)
  new_file_path = os.path.join(download_path, new_file_name)
  os.rename(old_file_path, new_file_path)

  browser.quit()


download_file(country="Mexico")