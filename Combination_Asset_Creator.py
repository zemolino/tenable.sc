#-------------------------------------------------------------------------------
# Name:         Combination_Asset_Creator.py (main script)
# Purpose:      Creates Combination Assets
# Author:       Morteza Zeinali               
#
#-------------------------------------------------------------------------------
# Import python modules
import json
import csv
import time
import os
import sys
from configparser import ConfigParser
import re
import requests
requests.packages.urllib3.disable_warnings()

# ===================================================================
# --- Global call to configuration file
# ===================================================================

# Path to configuration file
configfile = os.path.join(os.path.dirname(
  os.path.abspath(__file__)), 'config.conf')
config = ConfigParser(delimiters=('=', ','))
config.read(configfile)

# ===================================================================
# --- Create | Update combination assets in Tenable.sc
# ===================================================================


def update_comb_assets(comb_asset_list, comb_asset_Name):


    # Matching asset names with asset Ids in tenable.sc
    assetids = []
    for i in comb_asset_list:
        for j in sc.HTTPRequest('GET', 'asset').json()['response']['usable']:
            if i == j['name']:
                assetids.append(j['id'])

    # A dict template for 2 asset        
    comb = {"operator":"union", "operand1":{"id":assetids[0]}, "operand2":{"id":assetids[1]}}
    
    # Call to create combination asset having two assets
    if len(assetids) == 2:
        combination_assets = comb
    elif len(assetids) > 2:

        combination_assets = {"operator":"union", "operand1":comb, "operand2":{"id":assetids[2]}}

        for item in assetids[3:]:
            combination_assets = {"operator":"union", "operand1":combination_assets, "operand2":{"id":item}}

    
    # Create  combination asset it is not already exists in tenable.sc
    if comb_asset_Name not in [a['name']
                        for a in sc.HTTPRequest('GET', 'asset').json()['response']['usable']]:
        
        time.sleep(2)
        sc.HTTPRequest('POST', 'asset', data={"tags":"BA Group","name":comb_asset_Name,"groups":[],"type":"combination",
        "combinations":combination_assets})
        print(comb_asset_Name,'has been created')
    
    else:
        for dict_item in sc.HTTPRequest('GET', 'asset').json()['response']['usable']:

            # If ServiceNow asset exits in SC, get that asset ID, then update its IP list.
            if (comb_asset_Name == dict_item["name"]):
                print('\nThe asset already exists, updating combination asset...')

                # Update IP Address
                time.sleep(2)
                sc.HTTPRequest('PATCH', 'asset/%s' %
                            dict_item['id'], data={"combinations":combination_assets})
                print('\nThe combination asset has been updated!')
        
    
# --------------------------------------------------------------------------------
# --- MAIN body of the script. This is where the pieces come together
# --------------------------------------------------------------------------------


if __name__ == '__main__':
    
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

    # A sample combination includes asset list and asset name here called: "Combination Asset"
    comb_asset_Name = "Combination Asset"
    comb_asset_list = ['740', '741', '742', '743']

    update_comb_assets(comb_asset_list, comb_asset_Name)
    
    
    
    
    
