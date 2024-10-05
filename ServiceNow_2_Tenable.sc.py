
'''-------------------------------------------------------------------------------
Name:           ServiceNow_2_Tenable.sc.py (Main Script)

Date:           11/09/2019 

Last update:     05/10/2024 

Purpose:        A custom Tenable.sc Asset Data integration with ServiceNow.

The following steps will be performed by the script:

                1. Query a list of the active assets from ServiceNow portal.
                2. Create custom assets - Static IPs on Tenable Security Center.
                3. Update/Sync tenable.sc asset data from ServiceNow portal.
                4. Delete retired assets from tenable.sc on each run.
                5. logging script by calling 'pyLogger.py' & create a log file with
                   the same name of script 'SrvNow2Tenable.sc.log'
                6. Pull all credential data from a configuration file named: 'config.conf'
  


Author:         Morteza Zeinali
-------------------------------------------------------------------------------
Requirements:

   Please first define the credential data into 'config.conf' before running the script.
   The following Python modules needs to be downloaded and installed before running
   the script:

      json
      csv
      requests
      configparser
      codecs
      struct
      logging
      datetime
      
'''

# Import python modules
import json
import os
import sys
import getpass
import time
import struct
from socket import inet_aton
from configparser import ConfigParser
from datetime import datetime
import requests
from pyLogger import Logger
import pyTenableAPI
import pyServiceNowAPI

# Disable urllib3 warnings
requests.packages.urllib3.disable_warnings()

# Initialize global logging and configuration variables
scriptloc = os.path.join(os.path.dirname(os.path.realpath(__file__)), '')
scriptname = os.path.splitext(os.path.basename(__file__))[0]
configfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.conf')

# Initialize logging
log_instance = Logger(scriptloc, scriptname)
logger = log_instance.setup()
logger.info(f'Running on Python version {sys.version}')

# Global variables for Tenable and ServiceNow connections
sc = None
sn = None

def initialize_tenable_sc(config):
    """Initialize connection to Tenable.sc"""
    global sc
    try:
        sc_host = config.get('tenable.sc', 'SC_host')
        sc_username = config.get('tenable.sc', 'sc_username')
        sc_password = config.get('tenable.sc', 'sc_password')

        sc = pyTenableAPI.TenablescAPI(url=sc_host, username=sc_username, password=sc_password)
        sc.LoginTenable()
        logger.info("Logged in successfully to Tenable.sc!")
    except Exception as e:
        logger.error('Failed to connect to Tenable.sc server', exc_info=True)
        close_exit(1)

def initialize_servicenow(config):
    """Initialize connection to ServiceNow"""
    global sn
    try:
        srv_now_url = config.get('SrvNow', 'SrvNow_url')
        srv_now_username = config.get('SrvNow', 'SrvNow_username')
        srv_now_password = config.get('SrvNow', 'SrvNow_password')

        sn = pyServiceNowAPI.SrvNowAPI(url=srv_now_url, username=srv_now_username, password=srv_now_password)
        logger.info("Logged in successfully to ServiceNow!")
    except Exception as e:
        logger.error('Failed to connect to ServiceNow server', exc_info=True)
        close_exit(1)

def close_exit(exit_code):
    """Handle script exit with proper cleanup"""
    if exit_code == 0:
        logger.info('Script completed successfully')
    else:
        logger.error('Exiting script due to an error')

    log_instance.closeHandlers()
    sys.exit(exit_code)

def update_tenable_assets(srv_name, ipaddr):
    """Update or create Tenable.sc assets based on ServiceNow data"""
    try:
        existing_assets = sc.HTTPRequest('GET', 'asset').json()['response']['usable']
        asset_names = [a['name'] for a in existing_assets]

        if srv_name not in asset_names:
            # Create new asset in Tenable.sc
            time.sleep(2)
            sc.HTTPRequest('POST', 'asset').json = {
                'name': srv_name,
                'description': "",
                'groups': [],
                'definedIPs': ipaddr,
                'type': 'static',
                "tags": "SVC",
            }
            logger.info(f'Created new asset: {srv_name}')
        else:
            # Update existing asset IP addresses
            for asset in existing_assets:
                if srv_name == asset['name']:
                    time.sleep(2)
                    sc.HTTPRequest('PATCH', f'asset/{asset["id"]}').json = {'definedIPs': ipaddr}
                    logger.info(f'Updated asset: {srv_name}')
    except Exception as e:
        logger.error('Failed to create or update asset in Tenable.sc', exc_info=True)
        close_exit(1)

def delete_retired_assets(retired_asset):
    """Delete retired assets from Tenable.sc"""
    try:
        assets = sc.HTTPRequest('GET', 'asset').json()['response']['usable']
        for asset in assets:
            if retired_asset == asset["name"]:
                sc.HTTPRequest('DELETE', f'asset/{asset["id"]}')
                logger.info(f'Deleted retired asset: {retired_asset}')
    except Exception as e:
        logger.error('Failed to delete asset in Tenable.sc', exc_info=True)
        close_exit(1)

def srv_now_asset_data():
    """Fetch and process asset data from ServiceNow"""
    try:
        srv_now_assets = sn.HTTPRequest('GET', 'service_list').json()['result']['service_codes']
        assets = json.loads(srv_now_assets)

        for asset in assets:
            if asset["operational_status"] == "Retired":
                delete_retired_assets(asset['code'])
            else:
                process_active_assets(asset)
    except Exception as e:
        logger.error('Failed to fetch data from ServiceNow', exc_info=True)
        close_exit(1)

def process_active_assets(asset):
    """Process active assets from ServiceNow"""
    try:
        data = {'w_service_id': asset['code']}
        srv_now_ip_list = sn.HTTPRequest('POST', 'asset', data=data).json()['result']
        ips_lists = json.loads(srv_now_ip_list['server_ip_list'])

        if ips_lists:
            ips_prod = [ip['ip_address'] for ip in ips_lists if is_ipv4(ip['ip_address']) and ip['used_for'] == "Production"]
            if ips_prod:
                sorted_ips_prod = sorted(ips_prod, key=lambda ip: struct.unpack("!L", inet_aton(ip))[0])
                srv_ips_prod = ', '.join(sorted_ips_prod)
                logger.info(f'Service {asset["code"]} with production IPs: {srv_ips_prod}')
                update_tenable_assets(asset['code'], srv_ips_prod)
    except Exception as e:
        logger.error('Error processing active assets', exc_info=True)

def is_ipv4(ip):
    """Validate if a string is a valid IPv4 address"""
    try:
        parts = ip.split('.')
        return len(parts) == 4 and all(0 <= int(part) < 256 for part in parts)
    except:
        return False

def setup_config():
    """Setup or read configuration file"""
    config = ConfigParser(delimiters=('=', ','))
    if not os.path.exists(configfile):
        config.add_section('tenable.sc')
        config.set('tenable.sc', 'SC_host', input('Tenable.sc Hostname or IP: '))
        config.set('tenable.sc', 'sc_username', input('Tenable.sc Username: '))
        config.set('tenable.sc', 'sc_password', getpass.getpass('Tenable.sc Password: '))

        config.add_section('SrvNow')
        config.set('SrvNow', 'SrvNow_url', input('ServiceNow API URL: '))
        config.set('SrvNow', 'SrvNow_username', input('ServiceNow Username: '))
        config.set('SrvNow', 'SrvNow_password', getpass.getpass('ServiceNow Password: '))

        with open(configfile, 'w') as f:
            config.write(f)
    else:
        config.read(configfile)
    return config

if __name__ == '__main__':
    config = setup_config()
    initialize_tenable_sc(config)
    initialize_servicenow(config)
    
    logger.info("Processing ServiceNow asset data...")
    srv_now_asset_data()

    close_exit(0)
