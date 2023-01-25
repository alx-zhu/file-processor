from fileProcessor_globals import *
from fileProcessor_cloud import process_files, send_emails
from fileProcessor_autofill import download_all_files
from webscraperFunc import runWebscraper

def get_menu():
    menu = '''
----------------------------------------------------
Studyfind File Processor: Choose an option (1-3) 
to perform the desired action, or type 'q' to quit.
----------------------------------------------------
1. Download files from clinicaltrials.gov.
2. Process csv files to prepare for emailing.
3. Send emails from a processed csv file.
----------------------------------------------------
'''
    return menu

if __name__ == "__main__":
    while True:
        option = input(get_menu())
        if option == '1':
            print("DOWNLOADING FILES")
            download_all_files(keyword_terms=TERMS, countries=COUNTRY_TERMS, upload_to_drive=True)
        elif option == '2':
            print("PROCESSING CSV FILES")
            process_files(processingFn=runWebscraper)
        elif option == '3':
            print("SENDING EMAILS")
            send_emails()
        elif option == 'q':
            break
        else:
            continue


    
