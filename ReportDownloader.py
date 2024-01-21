'''-------------------------------------------------------------------------------
Name:           ReportDownloader.py (Main Script)

Date:           11/09/2019 

Last update:    21/01/2024 

Purpose:        Download Tenable.sc report results in SharePoint. 

The following steps will be performed by the script:

 
            1. Loop through all report results available after the last run - incremental report downloader -
               created already by "ReportCreator.py" in tenable.sc, download and save them in the specified 
               path of the SharePoint.
            2. Create a folder for each asset in SharePoint if not exits.
            3. Create and name reports found in tenable.sc and format it based on "report name + finished date time.pdf"
            4. Email report names found to the particular recipient pulling from "config.conf" file.
            5. All errors occuring during API calls or unexpected values would be logged
               with the same name of script anme + .log



  Author:         Morteza Zeinali
 -------------------------------------------------------------------------------
  Requirements:

     Please first place the credential data into 'config.conf' before running the script.
     Some of following Python modules needs to be downloaded and installed before running
     the script:

        json
        csv
        configparser
        codecs
        struct
        datetime
        getpass
        smtplib
        email.mime.multipart
        email.mime.text
        BeautifulSoup

'''

# Import required Python modules
import os
import time
import sys
from configparser import ConfigParser
from datetime import datetime
import requests
from pyLogger import Logger
from pyTenableAPI import TenablescAPI
from email_sender import Email

# Use constants for magic values
GET_METHOD = 'GET'
POST_METHOD = 'POST'
COMPLETED_STATUS = 'Completed'

# Define global logging variables
sys.dont_write_bytecode = True
scriptloc = os.path.join(os.path.dirname(os.path.realpath(__file__)), '')
scriptname = os.path.splitext(os.path.basename(__file__))[0]

# Initialize logging
log_instance = Logger(scriptloc, scriptname)
logger = log_instance.setup()
logger.info('Running on Python version {}'.format(sys.version))

# Global call to configuration file
configfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.conf')
config = ConfigParser(delimiters=('=', ','))
config.read(configfile)

def handle_error(message, exit_code=1):
    """Handle errors by logging the message and exiting with the specified code."""
    logger.error(message, exc_info=True)
    close_exit(exit_code)

def close_exit(exit_code):
    """Function to handle exiting the script either cleanly or with an error."""
    if exit_code == 0:
        logger.info('Script complete')
    else:
        logger.info('Exiting script due to an error')
    log_instance.closeHandlers()
    sys.exit()

def create_directory(directory_path):
    """Create a directory if it doesn't exist."""
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
    except OSError:
        handle_error('Failed creating a new directory: {}'.format(directory_path))

def download_report(sc, report_id):
    """Download a report using the specified Tenable.sc instance and report ID."""
    try:
        return sc.HTTPRequest(POST_METHOD, 'report/{}/download'.format(report_id), data={'id': int(report_id)})
    except Exception as e:
        handle_error('Failed to download report (ID: {}) from Tenable.sc: {}'.format(report_id, e))

def report_downloader(sharepoint_path, cfiles):
    """Download reports from Tenable.sc and save them to the specified SharePoint path."""
    try:
        params = {'startTime': cfiles, 'fields': 'name,type,status,finishTime'}
        reports = sc.HTTPRequest(GET_METHOD, 'report', data=params)
    except Exception as e:
        handle_error('Failed to fetch reports from Tenable.sc: {}'.format(e))

    for report in reports.json()['response']['usable']:
        if report['status'] == COMPLETED_STATUS:
            try:
                report_data = download_report(sc, report['id'])
            except Exception:
                handle_error('Failed to download report (ID: {}) from Tenable.sc'.format(report['id']))
                close_exit(1)

            report_folder_name = report['name']
            srv_timestamp = int(report['finishTime'])
            local_time = time.localtime(srv_timestamp)
            srv_fin_time = time.strftime("%Y-%m-%d-%H.%M", local_time)
            report_name = '{}-{}.{}'.format(report['name'], srv_fin_time, report['type'])
            sharepoint_folder_path = os.path.join(sharepoint_path, report_folder_name)

            create_directory(sharepoint_folder_path)

            try:
                report_file_path = os.path.join(sharepoint_folder_path, report_name)
                if not os.path.exists(report_file_path):
                    with open(report_file_path, 'wb') as report_file:
                        report_file.write(report_data.content)
            except OSError as e:
                handle_error('Failed creating a new report file: {}'.format(report_file_path))

            try:
                email_reports(report_folder_name, report_name)
            except Exception:
                handle_error('Failed to send email for report: {}'.format(report['name']))

def email_reports(report_folder_name, report_name):
    """Send email for matching reports based on configuration."""
    try:
        email_dict = dict(config.items('Emails'))
        for key in email_dict:
            if key.upper() == report_folder_name.upper():
                if report_folder_name not in itemname:
                    itemname.append(report_folder_name)
                    itemvalue = email_dict[key]
                    Email.EmailSender(sharepoint_path, report_folder_name, itemvalue, report_name)
    except Exception as e:
        handle_error('Failed to send email for report: {}'.format(report_folder_name))

if __name__ == '__main__':
    sc_host = config.get('tenable.sc', 'sc_host')
    sc_username = config.get('tenable.sc', 'sc_username')
    sc_password = config.get('tenable.sc', 'sc_password')

    try:
        sc = TenablescAPI(url=sc_host, username=sc_username, password=sc_password)
        sc.LoginTenable()
        print("Logged in successfully to Tenable.sc!")
    except Exception as e:
        handle_error('Failed to connect to Tenable.sc server: {}'.format(e))

    print("\nChecking out...")

    sharepoint_path = config.get('Reports', 'SharePoint_path')
    last_run = config.get('Reports', 'Last_run')

    print("\n=====================\n")

    if last_run != "":
        print("\nThe Last run date: ", last_run)
        dt_obj = datetime.strptime(last_run, "%Y-%m-%d %H:%M:%S")
        last_run_obj = time.mktime(dt_obj.timetuple())
        report_downloader(sharepoint_path, last_run_obj)
    else:
        print("Looks there is no input for Last Run in 'config.conf' Insert one with"
              "a format of 2019-02-11 12:00:00")
        last_run_input = config.set('Reports', 'Last_run', input('Last_run: '))
        dt_obj = datetime.strptime(last_run_input, "%Y-%m-%d %H:%M:%S")
        last_run_obj = time.mktime(dt_obj.timetuple())
        report_downloader(sharepoint_path, last_run_obj)

    print("Current time: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open('config.conf', 'w') as file_write:
        print("Last run before: ", config.get('Reports', 'Last_run'))
        config.set('Reports', 'Last_run', '{}'.format(current_time))
        config.write(file_write)
        print("Last_run now: ", config.get('Reports', 'Last_run'))

    close_exit(0)

    
