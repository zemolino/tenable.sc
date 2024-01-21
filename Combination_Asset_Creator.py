#-------------------------------------------------------------------------------
# Name:         Combination_Asset_Creator.py (main script)
# Purpose:      Creates Combination Assets
# Author:       Morteza Zeinali               
#
# Import standard library modules
import os
import time
from configparser import ConfigParser

# Import third-party modules
import requests
import pyTenableAPI

# ===================================================================
# --- Global call to the configuration file
# ===================================================================

# Path to configuration file
configfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.conf')
config = ConfigParser(delimiters=('=', ','))

# ===================================================================
# --- Create | Update combination assets in Tenable.sc
# ===================================================================

def update_comb_assets(comb_asset_list, comb_asset_Name, sc):
    # Matching asset names with asset Ids in Tenable.sc
    asset_ids = [asset['id'] for asset in sc.HTTPRequest('GET', 'asset').json()['response']['usable']
                 if asset['name'] in comb_asset_list]

    # A dict template for 2 asset
    comb = {"operator": "union", "operand1": {"id": asset_ids[0]}, "operand2": {"id": asset_ids[1]}}

    # Call to create combination asset having two assets
    if len(asset_ids) == 2:
        combination_assets = comb
    elif len(asset_ids) > 2:
        combination_assets = {"operator": "union", "operand1": comb, "operand2": {"id": asset_ids[2]}}
        combination_assets = {"operator": "union", "operand1": combination_assets, "operand2": {"id": item}
                              for item in asset_ids[3:]}

    # Create combination asset if it does not already exist in Tenable.sc
    if comb_asset_Name not in [a['name'] for a in sc.HTTPRequest('GET', 'asset').json()['response']['usable']]:
        time.sleep(2)
        sc.HTTPRequest('POST', 'asset', data={"tags": "BA Group", "name": comb_asset_Name, "groups": [],
                                               "type": "combination", "combinations": combination_assets})
        print(f'{comb_asset_Name} has been created')
    else:
        for dict_item in sc.HTTPRequest('GET', 'asset').json()['response']['usable']:
            if comb_asset_Name == dict_item["name"]:
                print('\nThe asset already exists, updating combination asset...')
                time.sleep(2)
                sc.HTTPRequest('PATCH', f'asset/{dict_item["id"]}', data={"combinations": combination_assets})
                print('\nThe combination asset has been updated!')

# --------------------------------------------------------------------------------
# --- MAIN body of the script. This is where the pieces come together
# --------------------------------------------------------------------------------

def main():
    # Get credential data from "config.conf" file
    sc_host = config.get('tenable.sc', 'sc_host')
    sc_username = config.get('tenable.sc', 'sc_username')
    sc_password = config.get('tenable.sc', 'sc_password')

    # Connect to Tenable.sc
    try:
        sc = pyTenableAPI.TenablescAPI(url=sc_host, username=sc_username, password=sc_password)
        sc.LoginTenable()
        print("Logged in successfully to Tenable.sc!")
    except pyTenableAPI.TenableAPIError as e:
        print(f'Failed to connect to Tenable.sc server: {e}')
        sys.exit(1)

    # A sample combination asset input includes "comb_asset_list" and combination asset name here named: "Combination Asset"
    comb_asset_Name = "Combination Asset"
    comb_asset_list = ['740', '741', '742', '743']

    update_comb_assets(comb_asset_list, comb_asset_Name, sc)

    
    
    
    
