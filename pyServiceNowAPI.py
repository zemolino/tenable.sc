
'''-------------------------------------------------------------------------------
Name:           pyServiceNowAPI.py

Date:           09/09/2019 

Purpose:        Logs into ServiceNow, uses "requests" module for Http method
                

Author:         Morteza Zeinali
-------------------------------------------------------------------------------
Requirements:

   Please first define the credential data into 'config.conf' before running the script.
   you also have to make sure the 'requests' module installed on your system. You can install
   it using pip.
      
'''

# Import python modules
import json
import csv
import os
import sys
import re
import requests
requests.packages.urllib3.disable_warnings()

# ===================================================================
# --- Get ServiceNow Asset Data
# ===================================================================


class SrvNowAPI(object):

    """
    A Class to handle Tenable ServiceNow API calls.

    """
    # Initializer / Instance Attributes
    def __init__(self, username: str, password: str, url: str):
        self.username = username
        self.password = password
        self.url = url

    def create_url(self, URL):
    
        """
        Formats the tenable.SC URL with the requested URL.
        """

        return '{0}{1}'.format(self.url, URL)
        

    def HTTPRequest(self, method: str, URL: str, data: dict = None, headers: dict = None):

        """ The HTTPRequest method is used to pass API calls."""

        if headers is None:
            headers = {"Content-Type":"application/json"}

        login = (self.username, self.password)

        if data is not None:
            data = json.dumps(data)

        if method == 'GET':
            response = requests.get(self.create_url(URL), auth=login, data=data, headers=headers, verify=False)
        elif method == "POST":
            response = requests.post(self.create_url(URL), auth=login, data=data, headers=headers, verify=False)
        elif method == 'PATCH':
            response = requests.patch(self.create_url(URL), auth=login, data=data, headers=headers, verify=False)
        elif method == "DELETE":
            response = requests.delete(self.create_url(URL), auth=login, data=data, headers=headers, verify=False)

     
        if response.status_code != 200:
            e = response.json()
            sys.exit(e['error_msg'])

        return response
     

    
    
    
