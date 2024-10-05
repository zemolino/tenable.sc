'''-------------------------------------------------------------------------------
Name:           ReportDownloader.py (Main Script)

Date:           11/09/2019 

Last update:    05/10/2024 

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

# Constants for HTTP methods and report status
GET_METHOD = 'GET'
POST_METHOD = 'POST'
COMPLETED_STATUS = 'Completed'

# Initialize logging
sys.dont_write_bytecode = True
script_location = os.path.join(os.path.dirname(os.path.realpath(__file__)), '')
script_name = os.path.splitext(os.path.basename(__file__))[0]

log_instance = Logger(script_location, script_name)
logger = log_instance.setup()
logger.info(f'Running on Python version {sys.version}')

# Global configuration setup
config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.conf')
config = ConfigParser(delimiters=('=', ','))
config.read(config_file)

def handle_error(message, exit_code=1):
    """Log error messages and exit the script."""
    logger.error(message, exc_info=True)
    close_exit(exit_code)

def close_exit(exit_code):
    """Exit script cleanly or with an error."""
    log_instance.closeHandlers()
    sys.exit(exit_code)

def create_directory(directory_path):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
        except OSError as e:
            handle_error(f'Failed to create directory: {directory_path}, {e}')

def download_report(sc, report_id):
    """Download a report from Tenable.sc."""
    try:
        return sc.HTTPRequest(POST_METHOD, f'report/{report_id}/download', data={'id': int(report_id)})
    except Exception as e:
        handle_error(f'Failed to download report (ID: {report_id}): {e}')

def report_downloader(sharepoint_path, last_run_time):
    """Download and save reports from Tenable.sc to SharePoint."""
    try:
        params = {'startTime': last_run_time, 'fields': 'name,type,status,finishTime'}
        reports = sc.HTTPRequest(GET_METHOD, 'report', data=params)
    except Exception as e:
        handle_error(f'Failed to fetch reports from Tenable.sc: {e}')

    for report in reports.json().get('response', {}).get('usable', []):
        if report['status'] == COMPLETED_STATUS:
            report_data = download_report(sc, report['id'])
            report_folder_name = report['name']
            report_timestamp = int(report['finishTime'])
            local_time = time.localtime(report_timestamp)
            formatted_time = time.strftime("%Y-%m-%d-%H.%M", local_time)
            report_filename = f'{report_folder_name}-{formatted_time}.{report["type"]}'
            report_folder_path = os.path.join(sharepoint_path, report_folder_name)

            create_directory(report_folder_path)

            try:
                report_file_path = os.path.join(report_folder_path, report_filename)
                if not os.path.exists(report_file_path):
                    with open(report_file_path, 'wb') as file:
                        file.write(report_data.content)
                logger.info(f'Report saved: {report_file_path}')
            except OSError as e:
                handle_error(f'Failed to save report: {report_file_path}, {e}')

            try:
                email_reports(report_folder_name, report_filename)
            except Exception as e:
                handle_error(f'Failed to send email for report: {report_folder_name}, {e}')

def email_reports(report_folder_name, report_filename):
    """Send an email notification for the downloaded reports."""
    try:
        email_recipients = dict(config.items('Emails'))
        for service_name, recipient in email_recipients.items():
            if service_name.upper() == report_folder_name.upper():
                Email.EmailSender(sharepoint_path, report_folder_name, recipient, report_filename)
                logger.info(f'Email sent for report: {report_filename}')
    except Exception as e:
        handle_error(f'Failed to send email for report: {report_folder_name}, {e}')

if __name__ == '__main__':
    # Fetch Tenable.sc credentials from config
    sc_host = config.get('tenable.sc', 'sc_host')
    sc_username = config.get('tenable.sc', 'sc_username')
    sc_password = config.get('tenable.sc', 'sc_password')

    # Initialize Tenable.sc API
    try:
        sc = TenablescAPI(url=sc_host, username=sc_username, password=sc_password)
        sc.LoginTenable()
        logger.info("Successfully logged into Tenable.sc")
    except Exception as e:
        handle_error(f'Failed to connect to Tenable.sc: {e}')

    sharepoint_path = config.get('Reports', 'SharePoint_path')
    last_run = config.get('Reports', 'Last_run')

    # Convert last run time
    if last_run:
        last_run_obj = time.mktime(datetime.strptime(last_run, "%Y-%m-%d %H:%M:%S").timetuple())
        report_downloader(sharepoint_path, last_run_obj)
    else:
        logger.warning("No 'Last_run' in config. Please provide a valid date.")
        last_run_input = input('Enter Last_run (format: YYYY-MM-DD HH:MM:SS): ')
        last_run_obj = time.mktime(datetime.strptime(last_run_input, "%Y-%m-%d %H:%M:%S").timetuple())
        report_downloader(sharepoint_path, last_run_obj)

    # Update last run time in config
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    config.set('Reports', 'Last_run', current_time)
    with open(config_file, 'w') as config_write:
        config.write(config_write)
        logger.info(f'Updated Last_run to: {current_time}')

    close_exit(0)
