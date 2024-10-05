"""
-------------------------------------------------------------------------------
Name:           pyServiceNowAPI.py

Date:           09/09/2019 

Last Update:    05/10/2024

Purpose:        Logs into ServiceNow, utilizes the "requests" module for HTTP methods.
                
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
import sys
import requests
requests.packages.urllib3.disable_warnings()  # Disable SSL warnings if necessary

# ===================================================================
# ServiceNow API Class
# ===================================================================

class SrvNowAPI:
    """
    A class to handle ServiceNow API calls, providing methods for making authenticated requests.
    """

    def __init__(self, username: str, password: str, url: str):
        """
        Initialize the ServiceNow API client with username, password, and base URL.
        
        Args:
            username (str): ServiceNow username
            password (str): ServiceNow password
            url (str): Base URL of the ServiceNow instance
        """
        self.username = username
        self.password = password
        self.url = url

    def create_url(self, endpoint: str) -> str:
        """
        Formats the full URL for the ServiceNow API.

        Args:
            endpoint (str): API endpoint to append to the base URL

        Returns:
            str: Full API URL
        """
        return f"{self.url}{endpoint}"

    def HTTPRequest(self, method: str, endpoint: str, data: dict = None, headers: dict = None):
        """
        Makes an HTTP request to the ServiceNow API with the provided method, endpoint, and data.
        
        Args:
            method (str): HTTP method ('GET', 'POST', 'PATCH', 'DELETE')
            endpoint (str): API endpoint to call
            data (dict, optional): Data payload for POST, PATCH, etc. Defaults to None.
            headers (dict, optional): Custom headers. Defaults to None.

        Returns:
            requests.Response: The response object from the API call

        Raises:
            SystemExit: Exits the script if the response status code is not 200
        """
        if headers is None:
            headers = {"Content-Type": "application/json"}

        # Authentication tuple for requests (username, password)
        auth = (self.username, self.password)

        # Convert the data to JSON format, if provided
        if data is not None:
            data = json.dumps(data)

        # Determine the HTTP method and make the corresponding API call
        url = self.create_url(endpoint)
        response = None
        if method == 'GET':
            response = requests.get(url, auth=auth, headers=headers, verify=True)
        elif method == "POST":
            response = requests.post(url, auth=auth, headers=headers, data=data, verify=True)
        elif method == 'PATCH':
            response = requests.patch(url, auth=auth, headers=headers, data=data, verify=True)
        elif method == "DELETE":
            response = requests.delete(url, auth=auth, headers=headers, data=data, verify=True)

        # Check if the response status code indicates an error
        if response.status_code != 200:
            error_msg = response.json().get('error_msg', 'Unknown error')
            sys.exit(f"API call failed: {error_msg}")

        return response
