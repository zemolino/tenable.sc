
'''-------------------------------------------------------------------------------
Name:           pyTenableAPI.py

Date:           09/09/2019 

Purpose:        Logs into Tenable.sc, uses "requets" module for Http method
                

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


class TenablescAPI(object):

    """
    A Class to handle Tenable.sc API calls.

    """
    # Initializer / Instance Attributes
    def __init__(self, username: str, password: str, url: str):
        self.username = username
        self.password = password
        self.url = url
        self.cookie = None
        self.token = None

    def create_url(self, URL):

        """
        Formats the tenable.SC URL with the requested URL.

        """
        return '{0}{1}'.format(self.url, URL)

    def HTTPRequest(self, method: str, URL: str, data: dict = None, headers: dict = None):

        """ The HTTPRequest method is used to pass API calls."""

        if headers is None:
            headers = {'Content-type': 'application/json', 'X-SecurityCenter': str(self.token)}

        if data is not None:
            data = json.dumps(data)
        
        if method == 'GET':
            response = requests.get(self.create_url(URL), data=data, headers=headers, cookies=self.cookie,
                                verify=False)
        elif method == "POST":
            response = requests.post(self.create_url(URL), data=data, headers=headers, cookies=self.cookie,
                                 verify=False)
        elif method == 'PATCH':
            response = requests.patch(self.create_url(URL), data=data, headers=headers, cookies=self.cookie,
                                  verify=False)
        elif method == "DELETE":
            response = requests.delete(self.create_url(URL), data=data, headers=headers, cookies=self.cookie,
                                   verify=False)  
     
        
        if response.status_code != 200:
            e = response.json()
            sys.exit(e['error_msg'])

        if response.headers.get('set-cookie') is not None:
            match = re.findall("TNS_SESSIONID=[^,]*", response.headers.get('set-cookie'))
            self.cookie = match[1]

        return response

    def LoginTenable(self):

        """
        Logs into tenable.sc and retrieves our token and cookie. Creates a separate header 
        since it does not have a X-SecurityCenter token yet.

        """
        headers = {'Content-Type': 'application/json'}
        login = {'username': self.username, 'password': self.password}

        # Used the HTTPRequest function and pass it to a POST method, token URL,
        # and login credentials as data.  It also passes headers from above for this function.
        data = self.HTTPRequest('POST', 'token', data=login, headers=headers)

        # It pulls the cookie out of exisiting data object and store it as a variable.
        self.cookie = data.cookies

        # It pulls the token out from the returned data as well.
        self.token = data.json()['response']['token']
        return self.cookie, self.token


    