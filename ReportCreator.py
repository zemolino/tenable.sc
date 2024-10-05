
'''-------------------------------------------------------------------------------
  Name:           ReportCreator.py (Main Script)

  Date:           16/09/2019

  Last update:    05/10/2024

  Purpose:        Tenable SecurityCenter Report Creator

  The following steps will be performed by the script:

            1. A custom report template defined here.
            2. Create only reports if finds a vulnerability
            3. Create a path as 'config.conf' file if not exists.
            4. All errors occurring during the API calls or unexpected values would be logged
               with the same name of scripts + .log
    


  Author:         Morteza Zeinali
 -------------------------------------------------------------------------------
  Requirements:

     Please first place the credential data into 'config.conf' before running the script.
     The following Python modules needs to be downloaded and installed before running
     the script:

        json
        configparser
        time
        getpass
        logging


'''

# Import necessary Python modules
import os
import sys
import json
import time
import getpass
import struct
import requests
import codecs
import re
from socket import inet_aton
from configparser import ConfigParser
from datetime import date, datetime, timedelta
from pyLogger import Logger

# Disable warnings from urllib3
requests.packages.urllib3.disable_warnings()

# ===================================================================
# Global Variables and Configuration
# ===================================================================

# Prevent the creation of compiled import modules
sys.dont_write_bytecode = True

# Get the script's directory and filename
scriptloc = os.path.dirname(os.path.realpath(__file__))
scriptname = os.path.splitext(os.path.basename(__file__))[0]

# Initialize logging
loginstance = Logger(scriptloc, scriptname)
logger = loginstance.setup()

logger.info(f'Running on Python version {sys.version}')

# Path to configuration file
configfile = os.path.join(scriptloc, 'config.conf')
config = ConfigParser(delimiters=('=', ','))
config.read(configfile)

# ===================================================================
# Vulnerability Analysis Function
# ===================================================================

def VulnAnalyser(assettid, assetname):
    """
    Analyzes vulnerabilities for the given asset within the last 30 days.
    Returns the highest severity found.
    """
    data = {
        "query": {
            "type": "vuln",
            "tool": "vulndetails",
            "startOffset": "0",
            "endOffset": "10000",
            "filters": [
                {"filterName": "lastSeen", "operator": "=", "value": "00:30"},
                {"filterName": "asset", "operator": "=", "value": {"id": assettid}}
            ]
        },
        "type": "vuln",
        "sourceType": "cumulative"
    }

    try:
        query_result = sc.HTTPRequest('POST', 'analysis', data=data).json()["response"]["results"]

        for qry in query_result:
            severity = int(qry["severity"]["id"])
            if severity > 0:  # Severity over 0 (Low, Medium, High, Critical)
                print(f"\nVulnerable asset: {assetname}, Severity: {qry['severity']}")
                return severity
    except Exception as e:
        logger.error(f"Failed to analyze vulnerabilities for {assetname}: {e}")
        return None

# ===================================================================
# Report Creation Function
# ===================================================================

def CreateReport(assettid, assetname):
    """
    Creates a report for the given asset based on its vulnerability analysis.
    """
    try:
        severity = VulnAnalyser(assettid, assetname)
        
        if severity:
            reportdata = {}  # Customize report data as needed
            sc.HTTPRequest('POST', 'reportDefinition', data=reportdata)
    except Exception as e:
        logger.error(f"Failed to create report for {assetname}: {e}", exc_info=True)
        closeexit(1)

# ===================================================================
# Exit Handler
# ===================================================================

def closeexit(exit_code):
    """
    Handles exiting the script, closing logs and performing any cleanup.
    """
    if exit_code == 0:
        logger.info('Script completed successfully')
    else:
        logger.error('Script exiting due to an error')

    loginstance.closeHandlers()
    sys.exit(exit_code)

# ===================================================================
# Main Script Execution
# ===================================================================

if __name__ == '__main__':
    # Get credentials from configuration file
    try:
        sc_host = config.get('tenable.sc', 'sc_host')
        sc_username = config.get('tenable.sc', 'sc_username')
        sc_password = config.get('tenable.sc', 'sc_password')

        # Connect to Tenable.sc
        import pyTenableAPI
        sc = pyTenableAPI.TenablescAPI(url=sc_host, username=sc_username, password=sc_password)
        sc.LoginTenable()
        logger.info("Logged in successfully to Tenable.sc")
    except Exception as e:
        logger.error(f"Failed to connect to Tenable.sc: {e}", exc_info=True)
        closeexit(1)

    # Process assets and generate reports
    try:
        assets = sc.HTTPRequest('GET', 'asset').json()['response']['usable']
        for asset in assets:
            for key in config.options('CustomReport'):
                if key.upper() == asset['name'].upper():
                    CreateReport(asset['id'], asset['name'])
    except Exception as e:
        logger.error(f"Error during report creation: {e}", exc_info=True)
        closeexit(1)

    # Exit the script cleanly
    closeexit(0)
