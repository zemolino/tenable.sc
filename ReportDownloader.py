'''-------------------------------------------------------------------------------
  Name:           ReportDownloader.py (Main Script)

  Date:           16/09/2019

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

# import required python modules
from configparser import ConfigParser
from datetime import date, datetime, timedelta
import os
import time
import sys
import email_sender as email
import getpass
import struct
from socket import inet_aton
import requests
requests.packages.urllib3.disable_warnings()
import json
from pyLogger import Logger
import email_sender as Email

# ===================================================================
# --- Define Global Logging Variables
# ===================================================================

# --- Prevent the creation of compiled import modules ---
sys.dont_write_bytecode = True

# --- Get location and name of script and store as variables ---
scriptloc = os.path.join(os.path.dirname(os.path.realpath(__file__)), '')

# What to save all files as (leave out file extension)
scriptname = os.path.splitext(os.path.basename(__file__))[0]

# --- Begin Logging Configuration Section ---
# Initialize logging
loginstance = Logger(scriptloc, scriptname)
logger = loginstance.setup()

logger.info('Running on Python version {}'.format(sys.version))

# ===================================================================
# --- Global call to configuration file
# ===================================================================

# Path to configuration file
configfile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'config.conf')
config = ConfigParser(delimiters=('=', ','))
config.read(configfile)

# ===================================================================
# --- Report Downloader
# ===================================================================


def report_downloader(SharePoint_path, cfiles):

    # Lets get the list of reports parameters that we will be working with...
    params={'startTime': cfiles, 'fields': 'name,type,status,finishTime'}

    reports = sc.HTTPRequest('GET', 'report', data=params)
                     

    # Now we will work our way through the resulting dataset and attempt
    # to download the reports if they meet the criteria.
    for report in reports.json()['response']['usable']:


        # We can only download completed reports, so we have no reason
        # to even try to download anything that isn't in the completed
        # status.
        if report['status'] == 'Completed':

        
            try:
                
                # Now to actually download the report...
                report_data = sc.HTTPRequest('POST', 'report/{0}/download'.format(report['id']),
                                        data={'id': int(report['id'])})

            except Exception:
                # Log error and exit script
                logger.error(
                    'Failed to downlaod particular report Completed in SC')
                logger.error(
                    'Likely cause is that th report name is not exists!',
                    exc_info=True)
                closeexit(1)

            # Report Folder name
            report_Fldname = report['name']

            # convert the the time to readable format
            srv_timestamp = int(report['finishTime'])
            local_time = time.localtime(srv_timestamp)
            srv_finTime = (time.strftime("%Y-%m-%d-%H.%M", local_time))

            # compute a report name.
            report_name = '%s-%s.%s' % (report['name'], srv_finTime,
                                        report['type'])

            # create a dynamic report name followed by report path, like "D:\path to SharePoint\report name"
            SharePoint_Fld_path = os.path.join(SharePoint_path, '%s' % report_Fldname)

            # ===========================================================================
            try:
                # if the download path doesn't exist, we need to create it.
                if not os.path.exists(SharePoint_Fld_path):
                    logger.debug(
                        'The report directory path does not exist. creating one: ' +
                        SharePoint_Fld_path)
                    os.makedirs(SharePoint_Fld_path)

            except OSError:
                print('Error: Creating directory. ' + SharePoint_Fld_path)
                # Log error and exit script
                logger.error('Failed creating a new report path directory. ')
                logger.error(
                    'Likely cause is that the server does not have access to create or not created already!',
                    exc_info=True)
                closeexit(1)

            try:
                # check if the download report file doesn't exist, it will add in the existing folder.
                if not os.path.exists(os.path.join(SharePoint_Fld_path, report_name)):
                    print('It is a new report file, creating...')

                    # Write file content to SharePoint_Fld_path = "\\workspaces.example.com\sites\Shared
                    # Documents\asset reports"
                    with open(os.path.join(SharePoint_Fld_path, report_name), 'wb') as report_file:

                        report_file.write(report_data.content)

            except OSError:
                print('Error: creating new report file. ' +
                        os.path.join(SharePoint_Fld_path, report_name))
                # Log error and exit script
                logger.error('Failed creating a new report file. ')
                logger.error(
                    'Likely cause is that the server does not have access to create or not created already!',
                    exc_info=True)
                closeexit(1)

        
            # ===========================================================================
            # Try to find and match the same report name and its value into
            # tenable.sc report results
            try:
                # Create a list to insert the all report names
                itemname = []

                # Calling Configuration file to fetch "Emails" section items into a dictionary
                email_dict = dict(config.items('Emails'))

                for key in email_dict:
                    if key.upper() == report['name'].upper():

                        # If report name is not in the list of,
                        # will sent an email to the particular person.
                        if report_Fldname not in itemname:

                            # Append to the list
                            itemname.append(report['name'])
                            itemvalue = email_dict[key]

                            
                            # Calling email sender file to send an email to the recipient
                            Email.EmailSender(SharePoint_Fld_path, report_Fldname,
                                            itemvalue, report_name)

            except Exception:
                # Log error and exit script
                logger.error(
                    'Failed to find a similar report name to send email')
                logger.error(
                    'Likely cause is that an input parameter is malformed!',
                    exc_info=True)
                closeexit(1)

# ===================================================================
# --- Exit status
# ===================================================================


def closeexit(exit_code):
    """Function to handle exiting the script either cleanly or with an error
    exit_code - 0 for clean exit, 1 for exiting due to script error
    """

    if exit_code == 0:  # Script completed without an error

        logger.info('Script complete')
    else:  # Script had an error
        logger.info('Exiting script due to an error')

    # Cleanly close the logging files
    # Function below comes from logging script
    loginstance.closeHandlers()
    sys.exit()


# --------------------------------------------------------------------------------
# --- MAIN body of the script. This is where the pieces come together
# --------------------------------------------------------------------------------

if __name__ == '__main__':
    
    # Get credential data from "config.conf" file.
    sc_host = config.get('tenable.sc', 'sc_host')
    sc_username = config.get('tenable.sc', 'sc_username')
    sc_password = config.get('tenable.sc', 'sc_password')


    try:
        #--- Connect to tenable.sc ---

        # Create connection to tenable.sc server using variables.
        # Results are returned as a series of dictionary objects within the 'SC' list variable
        import pyTenableAPI
        # This calls the credential function and passes it.
        sc = pyTenableAPI.TenablescAPI(url=sc_host, username=sc_username, password=sc_password)
        sc.LoginTenable()
        print("Logged in successfully to tenable.sc!")

    except Exception:
        # Log error and exit script
        logger.error('Failed to connect to tenable.sc server')
        logger.error(
            'Likely cause is that the credentials to login into tenable.sc are incorrect', exc_info=True)
        closeexit(1)

    print("\nChecking out...")

    # Path to download report in SharePoint
    SharePoint_path = config.get('Reports', 'SharePoint_path')

    # Get the last run value
    Last_run = config.get('Reports', 'Last_run')

    print("\n=====================\n")

    if Last_run != "":

        print("\nThe Last run date: ", Last_run)

        # Convert date string to timestamps
        dt_obj = datetime.strptime(Last_run, "%Y-%m-%d %H:%M:%S")
        LastRunObj = time.mktime(dt_obj.timetuple())

        # Call to check matching reports
        report_downloader(SharePoint_path, LastRunObj)

    elif Last_run == "":

        print("Looks there is no input for Last Run in 'config.conf' Insert one with"
              "a format of 2019-02-11 12:00:00")

        # Looks there is no input for Last Run. Insert one with"
        # a format of 2019-02-11 12: 00: 00
        LastRunIn = config.set('Reports', 'Last_run', input('Last_run : '))

        # Convert date string to timestamps
        dt_obj = datetime.strptime(LastRunIn, "%Y-%m-%d %H:%M:%S")
        LastRunObj = time.mktime(dt_obj.timetuple())


        # Call to check matching reports
        report_downloader(SharePoint_path, LastRunObj)

    # Write the last ending time to Last_run
    print("Current time: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    CTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    FileWrite = open('config.conf', 'w')
    print("Last run before: ", config.get('Reports', 'Last_run'))
    config.set('Reports', 'Last_run', '{}'.format(CTime))
    config.write(FileWrite)
    print("Last_run now: ", config.get('Reports', 'Last_run'))
    FileWrite.close()

    # Close log file and exit script cleanly
    closeexit(0)

    
