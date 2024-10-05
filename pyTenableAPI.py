"""
-------------------------------------------------------------------------------
Name:           pyTenableAPI.py

Date:           09/09/2019 

Last Update:    05/10/2024

Purpose:        Logs into Tenable.sc, utilizes the "requests" module for HTTP methods.
                
Author:         Morteza Zeinali
-------------------------------------------------------------------------------
Requirements:
   1. Define credential data in 'config.conf' before running the script.
   2. Ensure the 'requests' module is installed on your system. You can install it using pip:
      $ pip install requests
-------------------------------------------------------------------------------
"""

# Import required Python modules
import json
import re
import sys
import requests
requests.packages.urllib3.disable_warnings()  # Disable SSL warnings

class TenablescAPI:
    """
    A class to handle Tenable.sc API calls.
    Handles authentication, token management, and HTTP requests.
    """

    def __init__(self, username: str, password: str, url: str):
        """
        Initialize the Tenable.sc API client with username, password, and URL.
        
        Args:
            username (str): Tenable.sc username
            password (str): Tenable.sc password
            url (str): Base URL of the Tenable.sc instance
        """
        self.username = username
        self.password = password
        self.url = url
        self.cookie = None
        self.token = None

    def create_url(self, endpoint: str) -> str:
        """
        Formats the full URL for the Tenable.sc API.

        Args:
            endpoint (str): API endpoint to append to the base URL

        Returns:
            str: Full API URL
        """
        return f"{self.url}{endpoint}"

    def HTTPRequest(self, method: str, endpoint: str, data: dict = None, headers: dict = None):
        """
        Handles HTTP requests to the Tenable.sc API.
        
        Args:
            method (str): HTTP method ('GET', 'POST', 'PATCH', 'DELETE')
            endpoint (str): API endpoint to hit
            data (dict): Optional request payload for 'POST', 'PATCH', etc.
            headers (dict): Optional HTTP headers
        
        Returns:
            requests.Response: Response object from the API call

        Raises:
            SystemExit: Exits the script if the response status code is not 200
        """
        if headers is None:
            headers = {'Content-Type': 'application/json', 'X-SecurityCenter': str(self.token)}

        if data is not None:
            data = json.dumps(data)

        # Make the appropriate HTTP request based on the method
        url = self.create_url(endpoint)
        response = None
        if method == 'GET':
            response = requests.get(url, data=data, headers=headers, cookies=self.cookie, verify=False)
        elif method == 'POST':
            response = requests.post(url, data=data, headers=headers, cookies=self.cookie, verify=False)
        elif method == 'PATCH':
            response = requests.patch(url, data=data, headers=headers, cookies=self.cookie, verify=False)
        elif method == 'DELETE':
            response = requests.delete(url, data=data, headers=headers, cookies=self.cookie, verify=False)

        # Check if the response status code is not 200, exit with error message
        if response.status_code != 200:
            error_msg = response.json().get('error_msg', 'Unknown error')
            sys.exit(f"Error: {error_msg}")

        # Extract and store the session cookie, if present in the response headers
        if 'set-cookie' in response.headers:
            session_match = re.findall(r"TNS_SESSIONID=[^,]*", response.headers['set-cookie'])
            if session_match:
                self.cookie = session_match[0]

        return response

    def LoginTenable(self):
        """
        Logs into Tenable.sc and retrieves the session token and cookie.

        Returns:
            tuple: Cookie and token retrieved from Tenable.sc
        """
        headers = {'Content-Type': 'application/json'}
        login_payload = {'username': self.username, 'password': self.password}

        # Perform login request to obtain token
        response = self.HTTPRequest('POST', 'token', data=login_payload, headers=headers)

        # Store the cookie and token from the response
        self.cookie = response.cookies
        self.token = response.json().get('response', {}).get('token')

        # Return the cookie and token for future requests
        return self.cookie, self.token
