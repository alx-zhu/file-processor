import bs4
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import csv
import pandas as pd
import os


# def runWebscraper(filePath):
#   #open and write csv file
#   fileName = os.path.basename(filePath)
#   parentPath = os.path.dirname(filePath)
#   newPath = os.path.join(parentPath, "p-" + fileName)
#   f = open(newPath, "w", encoding="utf-8")

#   #excel headers
#   headers = "Title, Study Status, Description, Location, Posted Date, Condition or Disease, Contact Name, Contact Phone, Contact Email, Domain, URL\n"

#   f.write(headers)
#   #read the CSV file
#   data = pd.read_csv(filePath)

#   #setting up all the lists to store the data from the downloaded CSV file
#   titles = []
#   status = []
#   locations = []
#   urls = []

#   #pull columns from the downloaded CSV file and store them into lists
#   for title in data.Title:
#       titles.append(title)

#   for stats in data.Status:
#       status.append(stats)

#   for location in data.Locations:
#       locations.append(location)

#   for url in data.URL:
#       urls.append(url)

#   #variables - to avoid uninitiated variable errors and placeholder for not found data
#   title = "N/A"
#   stat = "N/A"
#   description = "N/A"
#   location = "N/A"
#   posted_date = "N/A"
#   condition_or_disease = "N/A"
#   contactName = "N/A"
#   contactPhone = "N/A"
#   contactEmail = "N/A"
#   domain = "N/A"
#   url = "N/A"

#   print("HERE")

#   #loop through all of the urls in the state from the list
#   for i in range(len(urls)):
#     print(i)
#     my_url = urls[i]

#     #opening up connection, grabbing the page
#     uClient = uReq(my_url)
#     page_html = uClient.read()
#     uClient.close()

#     #html parsing
#     page_soup = soup(page_html, "html.parser")

#     #grabs each product
#     title_container = page_soup.findAll("h1", {"class":"tr-h1 ct-sans-serif"})
#     summary_container = page_soup.findAll("div", {"class":"ct-body3 tr-indent2"})
#     location_container = page_soup.findAll("td", {"headers":"locName"})
#     #locations = page_soup.findAll("td", {"style":"padding:0;padding-left:4em;"})
#     posted_date_container = page_soup.findAll("div", {"style":"font-size:inherit"})
#     condition_or_disease_container = page_soup.findAll("td", {"class":"ct-body3"})
#     recruitmentStatus_container = page_soup.findAll("div", {"class":"tr-status tr-recruiting-colors"})

#     contactName_container = page_soup.findAll("td", {"headers":"contactName"})
#     contactPhone_container = page_soup.findAll("td", {"headers":"contactPhone"})
#     contactEmail_container = page_soup.findAll("td", {"headers":"contactEmail"})

#     #variables of data scraped to be written into csv file
#     #title = title_container[0].text
#     title = titles[i].replace("\n", " ")
#     stat = status[i].replace("\n", " ")
#     location = str(locations[i]).replace("\n", " ")
#     url = urls[i]

#   #implement error exception catches
#   try:
#     description = summary_container[0].text.replace("\n", " ")
#   except Exception as e:
#     # print("moving on")
#     pass

#   try:
#     posted_date = posted_date_container[0].text.replace("\nFirst Posted  : " , "")
#   except Exception as e:
#     # print("moving on")
#     pass

#   try:
#     condition_or_disease = condition_or_disease_container[0].text.replace("\n", " ")
#   except Exception as e:
#     # print("moving on")
#     pass

#   try:
#     contactName = contactName_container[0].text.replace("Contact: ", "")
#   except Exception as e:
#     # print("moving on")
#     pass

#   try:
#     contactPhone = contactPhone_container[0].text
#   except Exception as e:
#     # print("moving on")
#     pass

#   try:
#     contactEmail = contactEmail_container[0].text
#     domain = contactEmail.split('@')[1]
#   except Exception as e:
#     # print("moving on")
#     pass

#   #print variables to visually see progress in terminal
#   # print("Title: " + title)
#   # print("Status: " + stat)
#   # print("Description: " + description)
#   # print("Location: " + location)
#   # print("Posted Date: " + posted_date)
#   # print("Condition or Disease: " + condition_or_disease)
#   # print("Contact Name: " + contactName)
#   # print("Contact Phone: " + contactPhone)
#   # print("Contact Email: " + contactEmail)
#   # print("Contact Domain: " + domain)
#   # print("URL: " + url)

#   #write in all the scraped data into CSV file
#   f.write(
#       title.replace("," , " |") + "," +
#       stat.replace("," , "| ") + "," +
#       description.replace("," , "| ") + "," +
#       location.replace("," , "| ") + "," +
#       posted_date.replace("," , " |") + "," +
#       condition_or_disease.replace("," , " |") + "," +
#       contactName.replace("," , "| ") + "," +
#       contactPhone.replace("," , " |") + "," +
#       contactEmail.replace("," , "| ") + "," +
#       domain.replace("," , " |") + "," +
#       url.replace("," , "| ") +
#       "\n"
#   )
#   # try:
#   # except:
#   #   print("Error encountered when processing. Skipping file.")
#   #   return -1
  
#   f.close()
#   return newPath


def runWebscraper(filePath):
    #open and write csv file
    fileName = os.path.basename(filePath)
    parentPath = os.path.dirname(filePath)
    newPath = os.path.join(parentPath, "p-" + fileName)
    f = open(newPath, "w", encoding="utf-8")

    #excel headers
    headers = "Title, Study Status, Description, Location, Posted Date, Condition or Disease, Contact Name, Contact Phone, Contact Email, Domain, URL\n"

    f.write(headers)

    #read the CSV file
    data = pd.read_csv(filePath)

    #setting up all the lists to store the data from the downloaded CSV file
    titles = []
    status = []
    locations = []
    urls = []

    #pull columns from the downloaded CSV file and store them into lists
    for title in data.Title:
        titles.append(title)

    for stats in data.Status:
        status.append(stats)

    for location in data.Locations:
        locations.append(location)

    for url in data.URL:
        urls.append(url)

    #variables - to avoid uninitiated variable errors and placeholder for not found data
    title = "N/A"
    stat = "N/A"
    description = "N/A"
    location = "N/A"
    posted_date = "N/A"
    condition_or_disease = "N/A"
    contactName = "N/A"
    contactPhone = "N/A"
    contactEmail = "N/A"
    domain = "N/A"
    url = "N/A"

    #loop through all of the urls in the state from the list
    for i in range(len(urls)):
        my_url = urls[i]

        #opening up connection, grabbing the page
        uClient = uReq(my_url)
        page_html = uClient.read()
        uClient.close()

        #html parsing
        page_soup = soup(page_html, "html.parser")

        #grabs each product
        title_container = page_soup.findAll("h1", {"class":"tr-h1 ct-sans-serif"})
        summary_container = page_soup.findAll("div", {"class":"ct-body3 tr-indent2"})
        location_container = page_soup.findAll("td", {"headers":"locName"})
        #locations = page_soup.findAll("td", {"style":"padding:0;padding-left:4em;"})
        posted_date_container = page_soup.findAll("div", {"style":"font-size:inherit"})
        condition_or_disease_container = page_soup.findAll("td", {"class":"ct-body3"})
        recruitmentStatus_container = page_soup.findAll("div", {"class":"tr-status tr-recruiting-colors"})

        contactName_container = page_soup.findAll("td", {"headers":"contactName"})
        contactPhone_container = page_soup.findAll("td", {"headers":"contactPhone"})
        contactEmail_container = page_soup.findAll("td", {"headers":"contactEmail"})

        #variables of data scraped to be written into csv file
        #title = title_container[0].text
        title = titles[i].replace("\n", " ")
        stat = status[i].replace("\n", " ")
        location = str(locations[i]).replace("\n", " ")
        url = urls[i]

        # implement error exception catches
        try:
            description = summary_container[0].text.replace("\n", " ")
            posted_date = posted_date_container[0].text.replace("\nFirst Posted  : " , "")
            condition_or_disease = condition_or_disease_container[0].text.replace("\n", " ")
            contactName = contactName_container[0].text.replace("Contact: ", "")
            contactPhone = contactPhone_container[0].text
            contactEmail = contactEmail_container[0].text
            domain = contactEmail.split('@')[1]
        except Exception as e:
            print("moving on")

        # write in all the scraped data into CSV file
        f.write(
            title.replace("," , " |") + "," +
            stat.replace("," , "| ") + "," +
            description.replace("," , "| ") + "," +
            location.replace("," , "| ") + "," +
            posted_date.replace("," , " |") + "," +
            condition_or_disease.replace("," , " |") + "," +
            contactName.replace("," , "| ") + "," +
            contactPhone.replace("," , " |") + "," +
            contactEmail.replace("," , "| ") + "," +
            domain.replace("," , " |") + "," +
            url.replace("," , "| ") +
            "\n"
        )

    f.close()
    return newPath


runWebscraper(r'C:\Users\alexa\ProgrammingProjects\studyfind\file-processor\test\GenderLGBTQTest.csv')