
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
import csv
import os
import sys
import getpass
import time
from socket import inet_aton
import struct
from configparser import ConfigParser
import codecs
from datetime import date, datetime, timedelta
import re
import requests
requests.packages.urllib3.disable_warnings()

# ===================================================================
# --- Define Global Logging Variables
# ===================================================================

# Import Logger 
from pyLogger import Logger

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
configfile = os.path.join(os.path.dirname(
  os.path.abspath(__file__)), 'config.conf')
config = ConfigParser(delimiters=('=', ','))
config.read(configfile)

# ===================================================================
# --- Create or Update tenable.sc using Static IPs fetching from 
# --- ServiceNow
# ===================================================================

def update_tenable_assets(srv_name, ipaddr):

    '''
    Collect and parse the Assets from tenable.sc and returns it at as a list of dictionaries

    Parameters
    ----------
    srv_name : str
        Service code/Name of ServiceNow
    ipaddr : str
        Static IP Addresses of relevant service code/Name in ServiceNow
    tags : str
        An instance tag named here - "SVC"
    -------
    '''

    try:
        # Create assets If they are not already in tenable.sc
        if srv_name not in [a['name'] 
                                for a in sc.HTTPRequest('GET', 'asset').json()['response']['usable']]:
            
            # Create custom - static IP list - asset
            # Explicitly defined list of managed IPs
            time.sleep(2)
            sc.HTTPRequest('POST', 'asset').json={'name': srv_name,
                                    "description": "", "groups": [],
                                    'definedIPs': ipaddr,
                                    'type': 'static',
                                    "tags": "SVC",
                                    }
            print(srv_name,'has been created')
            
        else:

            print('\nThe asset already exists, updating IPs...')

            for dict_item in sc.HTTPRequest('GET', 'asset').json()['response']['usable']:

                # If ServiceNow asset exits in tenabe.sc assets, get that asset ID from tenable asset, 
                # and update its static IP list.
                if (srv_name == dict_item['name']):

                    # Update IP Addresses
                    time.sleep(2)
                    sc.HTTPRequest('PATCH', 'asset/{0}'.format(dict_item['id'])).json={'definedIPs': ipaddr}

                    print('\nThe asset has been updated!')

    except Exception:
        # Problem with trying to get data from tenable.sc
        # Log error and exit script
        logger.error('Failed to create|update asset data into tenable.sc')
        logger.error(
            'Likely cause is the input parameters are malformed', exc_info=True)
        closeexit(1)



# ===================================================================
# --- Sync assets and delete retired assets from Tenable.sc
# ===================================================================


def delete_retired_assets(retired_asset):

    try:

        for asset in sc.HTTPRequest('GET', 'asset').json()['response']['usable']:
            
            if retired_asset == asset["name"]:

                print(retired_asset)

                sc.HTTPRequest('DELETE', 'asset/{0}'.format(asset['id']))
                print("The asset name", asset["name"], "has been retired and deleted from Tenable.sc.")

    except Exception:
        # Problem with trying to delete data from tenable.sc
        # Log error and exit script
        logger.error('Failed to delete asset data from tenable.sc')
        logger.error(
            'Likely cause is the input parameters are malformed', exc_info=True)
        closeexit(1)


#=====================
# Service Now method
#=====================

def SrvNow_asset_data():


    SrvNow_asset_lists = sn.HTTPRequest('GET', 'service_list').json()['result']['service_codes']


    # Decoding the JSON response into a dictionary and use the data
    dict_SrvNow = json.loads(SrvNow_asset_lists)

    # Loop looking for service codes
    for SrvNow_list in dict_SrvNow:

        # Find retired service codes and call to delete from tenable.sc assets
        if SrvNow_list["operational_status"] == "Retired":
            delete_retired_assets(SrvNow_list['code'])

        else:

            try:
                print("\n\n==============================================")               
                
                # Sevice code as body message
                data = {'w_service_id': SrvNow_list['code']}
                
                
                # Digging for each service code data
                SrvNow_ip_list = sn.HTTPRequest('POST', 'asset', data=data).json()['result']
                
            
                # Loop through service codes for fetching its data
                if SrvNow_ip_list['server_ip_list'] != "[]":

                    ips_lists = json.loads(SrvNow_ip_list['server_ip_list'])
                    

                    # Create a new list for the service code IPs 
                    ips_prod = []
                

                    # loop through each asset IP found
                    for ip in ips_lists:

                        if is_ipv4(ip['ip_address']) != 'False' and ip['ip_address'] != "" and ip['ip_address'] != 'DHCP':
                            
                            if ip['used_for'] == "Production":

                                
                                if ip not in ips_prod:
                                    ips_prod.append(ip['ip_address'])
                                else:
                                    print('Iterated IP %s' %
                                            ip['ip_address'])
                            

                            

                    # ============================================
                    # collection of production IPs start from here
                    # ============================================

                    # sort IPs if exists
                    sorted_ips_prod = sorted(
                        ips_prod, key=lambda ip: struct.unpack("!L", inet_aton(ip))[0])

                    # join service code's IPs 
                    srv_ips_prod = ', '.join(sorted_ips_prod)
                    if srv_ips_prod != "":

                        time.sleep(4)

                        print('\nThe service %s with production IPs: %s' % (SrvNow_list['code'], srv_ips_prod))
                        
                        update_tenable_assets(SrvNow_list['code'], srv_ips_prod)
                        

            except Exception:
                # Problem with trying to fetch and parse data from ServiceNow Portal
                # Log error and exit script
                logger.error('Failed to get data from ServiceNow function')
                logger.error('Likely cause is the query is malformed',
                                exc_info=True)
                closeexit(1)




# ===================================================================
# --- IPv4 verification
# ===================================================================

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


# ===================================================================
# --- Exit status
# ===================================================================

def closeexit(exit_code):

    """
    Function to handle exiting the script either cleanly or with an error
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

#--------------------------------------------------------------------------------
# --- MAIN body of the script. This is where the pieces come together
#--------------------------------------------------------------------------------

if __name__ == '__main__':


    # ===================================================================
    # --- Logging info
    # ===================================================================

    if not os.path.exists(configfile):

        # In case there wasn't a config file located in the current directory
        # so it creates one.
        config.add_section('tenable.sc')

        config.set('tenable.sc', 'SC_host', input(
            'tenable.sc IP Address | Hostname : '))
        config.set('tenable.sc', 'sc_username', input(
            'tenable.sc Username : '))
        config.set('tenable.sc', 'sc_password', getpass.getpass(
            'tenable.sc Password : '))

        config.add_section('SrvNow')

        config.set('SrvNow', 'SrvNow_url', input(
            'SrvNow Service API link : '))
        config.set('SrvNow', 'SrvNow_username', input(
            'SrvNow Username : '))
        config.set('SrvNow', 'SrvNow_password', getpass.getpass(
            'SrvNow Password : '))

        print('Stared Processing...')

        with open(configfile, 'w') as f:
            config.write(f)
    else:
        # Get credential data from "config.conf" file
        sc_host = config.get('tenable.sc', 'sc_host')
        sc_username = config.get('tenable.sc', 'sc_username')
        sc_password = config.get('tenable.sc', 'sc_password')


        #--- Connect to tenable.sc ---
        try:
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

        
        # Setting the ServiceNow request credential parameters stored in config file
        SrvNow_url = config.get('SrvNow', 'SrvNow_url')
        SrvNow_username = config.get('SrvNow', 'SrvNow_username')
        SrvNow_password = config.get('SrvNow', 'SrvNow_password')



        #--- Connect to ServiceNow ---
        try:
            # Create connection to ServiceNow server using variables.
            # Results are returned as a series of dictionary objects within the 'SN' list variable
            import pyServiceNowAPI
            # This calls the credential function and passes it.
            sn = pyServiceNowAPI.SrvNowAPI(url=SrvNow_url, username=SrvNow_username, password=SrvNow_password)
            print("Logged in successfully to ServiceNow!")

            # Pull data from ServiceNow
            print("Proccessing Methods...")
            SrvNow_asset_data()
            

        except Exception:
            # Log error and exit script
            logger.error('Failed to connect to ServiceNow server')
            logger.error(
                'Likely cause is that the credentials to login into ServiceNow are incorrect', exc_info=True)
            closeexit(1)


    # Close log file and exit script cleanly
    closeexit(0)
