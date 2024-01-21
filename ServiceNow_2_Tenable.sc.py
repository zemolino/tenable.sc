
'''-------------------------------------------------------------------------------
Name:           ServiceNow_2_Tenable.sc.py (Main Script)

Date:           11/09/2019 

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
from socket import inet_aton
import struct
from configparser import ConfigParser
from datetime import datetime
import requests
from pyLogger import Logger
import pyTenableAPI
import pyServiceNowAPI

# Disable urllib3 warnings
requests.packages.urllib3.disable_warnings()

# Define global logging variables
scriptloc = os.path.join(os.path.dirname(os.path.realpath(__file__)), '')
scriptname = os.path.splitext(os.path.basename(__file__))[0]

# Initialize logging
log_instance = Logger(scriptloc, scriptname)
logger = log_instance.setup()
logger.info('Running on Python version {}'.format(sys.version))

# Global configuration file path
configfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.conf')

# Global variables for Tenable and ServiceNow connections
sc = None
sn = None

def initialize_tenable_sc():
    global sc
    try:
        sc_host = config.get('tenable.sc', 'SC_host')
        sc_username = config.get('tenable.sc', 'sc_username')
        sc_password = config.get('tenable.sc', 'sc_password')

        # Create connection to tenable.sc server
        sc = pyTenableAPI.TenablescAPI(url=sc_host, username=sc_username, password=sc_password)
        sc.LoginTenable()
        logger.info("Logged in successfully to tenable.sc!")
    except Exception as e:
        logger.error('Failed to connect to tenable.sc server')
        logger.error('Likely cause is incorrect credentials', exc_info=True)
        close_exit(1)

def initialize_servicenow():
    global sn
    try:
        srv_now_url = config.get('SrvNow', 'SrvNow_url')
        srv_now_username = config.get('SrvNow', 'SrvNow_username')
        srv_now_password = config.get('SrvNow', 'SrvNow_password')

        # Create connection to ServiceNow server
        sn = pyServiceNowAPI.SrvNowAPI(url=srv_now_url, username=srv_now_username, password=srv_now_password)
        logger.info("Logged in successfully to ServiceNow!")
    except Exception as e:
        logger.error('Failed to connect to ServiceNow server')
        logger.error('Likely cause is incorrect credentials', exc_info=True)
        close_exit(1)

def close_exit(exit_code):
    """
    Function to handle exiting the script either cleanly or with an error
    exit_code - 0 for clean exit, 1 for exiting due to script error
    """
    if exit_code == 0:
        logger.info('Script complete')
    else:
        logger.info('Exiting script due to an error')

    # Cleanly close the logging files
    log_instance.closeHandlers()
    sys.exit()

def update_tenable_assets(srv_name, ipaddr):
    try:
        # Create assets if they are not already in tenable.sc
        if srv_name not in [a['name'] for a in sc.HTTPRequest('GET', 'asset').json()['response']['usable']]:
            # Create custom - static IP list - asset
            time.sleep(2)
            sc.HTTPRequest('POST', 'asset').json = {
                'name': srv_name,
                "description": "",
                "groups": [],
                'definedIPs': ipaddr,
                'type': 'static',
                "tags": "SVC",
            }
            logger.info(f'{srv_name} has been created')
        else:
            logger.info('\nThe asset already exists, updating IPs...')
            for dict_item in sc.HTTPRequest('GET', 'asset').json()['response']['usable']:
                if srv_name == dict_item['name']:
                    # Update IP Addresses
                    time.sleep(2)
                    sc.HTTPRequest('PATCH', 'asset/{0}'.format(dict_item['id'])).json = {'definedIPs': ipaddr}
                    logger.info('\nThe asset has been updated!')
    except Exception as e:
        logger.error('Failed to create|update asset data into tenable.sc')
        logger.error('Likely cause is the input parameters are malformed', exc_info=True)
        close_exit(1)

def delete_retired_assets(retired_asset):
    try:
        for asset in sc.HTTPRequest('GET', 'asset').json()['response']['usable']:
            if retired_asset == asset["name"]:
                logger.info(f'{retired_asset} has been retired and deleted from Tenable.sc.')
                sc.HTTPRequest('DELETE', 'asset/{0}'.format(asset['id']))
    except Exception as e:
        logger.error('Failed to delete asset data from tenable.sc')
        logger.error('Likely cause is the input parameters are malformed', exc_info=True)
        close_exit(1)

def srv_now_asset_data():
    srv_now_asset_lists = sn.HTTPRequest('GET', 'service_list').json()['result']['service_codes']
    dict_srv_now = json.loads(srv_now_asset_lists)

    for srv_now_list in dict_srv_now:
        if srv_now_list["operational_status"] == "Retired":
            delete_retired_assets(srv_now_list['code'])
        else:
            try:
                logger.info("\n\n==============================================")
                data = {'w_service_id': srv_now_list['code']}
                srv_now_ip_list = sn.HTTPRequest('POST', 'asset', data=data).json()['result']
                
                if srv_now_ip_list['server_ip_list'] != "[]":
                    ips_lists = json.loads(srv_now_ip_list['server_ip_list'])
                    ips_prod = []

                    for ip in ips_lists:
                        if is_ipv4(ip['ip_address']) and ip['ip_address'] != "" and ip['ip_address'] != 'DHCP':
                            if ip['used_for'] == "Production":
                                if ip['ip_address'] not in ips_prod:
                                    ips_prod.append(ip['ip_address'])
                                else:
                                    logger.info('Iterated IP %s' % ip['ip_address'])

                    sorted_ips_prod = sorted(ips_prod, key=lambda ip: struct.unpack("!L", inet_aton(ip))[0])
                    srv_ips_prod = ', '.join(sorted_ips_prod)
                    if srv_ips_prod != "":
                        time.sleep(4)
                        logger.info('\nThe service %s with production IPs: %s' % (srv_now_list['code'], srv_ips_prod))
                        update_tenable_assets(srv_now_list['code'], srv_ips_prod)
                        
            except Exception as e:
                logger.error('Failed to get data from ServiceNow function')
                logger.error('Likely cause is the query is malformed', exc_info=True)
                close_exit(1)

def is_ipv4(i):
    if '.' in i:
        nodot_ip = i.split('.')
    else:
        return False
    if len(nodot_ip) != 4:
        return False
    try:
        return all(0 <= int(p) < 256 for p in nodot_ip)
    except:
        return False

if __name__ == '__main__':
    if not os.path.exists(configfile):
        config = ConfigParser(delimiters=('=', ','))
        config.add_section('tenable.sc')
        config.set('tenable.sc', 'SC_host', input('tenable.sc IP Address | Hostname : '))
        config.set('tenable.sc', 'sc_username', input('tenable.sc Username : '))
        config.set('tenable.sc', 'sc_password', getpass.getpass('tenable.sc Password : '))

        config.add_section('SrvNow')
        config.set('SrvNow', 'SrvNow_url', input('SrvNow Service API link : '))
        config.set('SrvNow', 'SrvNow_username', input('SrvNow Username : '))
        config.set('SrvNow', 'SrvNow_password', getpass.getpass('SrvNow Password : '))

        print('Stared Processing...')

        with open(configfile, 'w') as f:
            config.write(f)
    else:
        config = ConfigParser(delimiters=('=', ','))
        config.read(configfile)

        initialize_tenable_sc()
        initialize_servicenow()

        logger.info("Proccessing Methods...")
        srv_now_asset_data()

    close_exit(0)

