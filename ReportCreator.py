
'''-------------------------------------------------------------------------------
  Name:           ReportCreator.py (Main Script)

  Date:           16/09/2019 (Updated)

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

# Import python modules
from pyLogger import Logger
import json
import os
import sys
import getpass
from configparser import ConfigParser
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
# --- Asalysis Vulnerability Existance
# ===================================================================


def VulnAnalyser(assettid, assetname):
    # Query lastseen 30 days vulns for particular asset
    data = {
        "query":
            {
                "type": "vuln",
                "tool": "vulndetails",
                "startOffset": "0",
                "endOffset": "10000",
                "filters": [
                    {
                        "filterName": "lastSeen",
                        "operator": "=",
                        "value": "00:30"
                    },
                    {
                        "filterName": "asset",
                        "operator": "=", 
                        "value": {"id": assettid}
                    }
                    ]
            },
        "type": "vuln",
        "sourceType": "cumulative"}

    query_result = sc.HTTPRequest('POST', 'analysis', data=data).json()["response"]["results"]
     
    for qry in query_result:
        # Any severity over 0 (informative one) - Low = 1 , Medium = 2, High = 3 and Critical = 4
        if qry["severity"]["id"] > "0":
            print("\nThe vulnerablea asset name is: %s With a severity: %s" %
                  (assetname, qry["severity"]))

            return qry["severity"]

# ===================================================================
# --- CreatReport Function/Method
# ===================================================================

def CreateReport(assettid, assetname):

    try:
        # Analysis each asset for any vulnerability
        Severity = VulnAnalyser(assettid, assetname)

        if Severity:
            # A custom report template
            reportdata = {'name': assetname,
                                                "template": {'id': "57"}, 
                                                "definition": {'chapters': [
                                                {
                                                    "name": "Executive Summary",
                                                    "tag": "chapter",
                                                    "elements": [
                                                        {
                                                            "name": 2.1,
                                                            "tag": "group",
                                                            "elements": [
                                                                {
                                                                    "name": "2.1.1",
                                                                    "tag": "paragraph",
                                                                    "text": "This chapter presents a high-level overview of the vulnerability status of the network.",
                                                                }
                                                            ],
                                                        },
                                                        {
                                                                    "name": "2.2",
                                                                    "tag": "group",
                                                                    "elements": [
                                                                        {
                                                                            "name": "2.2.3",
                                                                            "tag": "paragraph",
                                                                            "text": "",
                                                                        },
                                                                        {
                                                                            "name": "Vulnerability Trend",
                                                                            "tag": "component",
                                                                            "definition": {
                                                                                "timeFrame": "90d",
                                                                                "startTime": 0,
                                                                                "endTime": 0,
                                                                                "lines": [
                                                                                    {
                                                                                        "id": 96918,
                                                                                        "name": "",
                                                                                        "description": "",
                                                                                        "context": "",
                                                                                        "status": -1,
                                                                                        "createdTime": 0,
                                                                                        "modifiedTime": 0,
                                                                                        "axisNum": 1,
                                                                                        "label": "Vulnerabilities",
                                                                                        "dataSource": {
                                                                                        "querySourceID": "",
                                                                                        "querySourceView": "",
                                                                                        "querySourceType": "cumulative",
                                                                                        "startTime": 0,
                                                                                        "endTime": 0,
                                                                                        "timeFrame": "90d",
                                                                                        "query": {
                                                                                            "name": "",
                                                                                            "description": "",
                                                                                            "tool": "trend",
                                                                                            "type": "vuln",
                                                                                            "tags": "",
                                                                                            "context": "report",
                                                                                            "browseColumns": "",
                                                                                            "browseSortColumn": "",
                                                                                            "browseSortDirection": "ASC",
                                                                                            "filters": [
                                                                                                {
                                                                                                    "filterName": "pluginID",
                                                                                                    "operator": "<=",
                                                                                                    "value": "999999"
                                                                                                },
                                                                                                {
                                                                                                    "filterName": "lastSeen",
                                                                                                    "operator": "=",
                                                                                                    "value": "00:07"
                                                                                                },
                                                                                                {
                                                                                                    "filterName": "asset",
                                                                                                    "operator": "=",
                                                                                                    "value": {"id": assettid}
                                                                                                }
                                                                                                ],
                                                                                            "groups": [],
                                                                                            "ownerGroup": {
                                                                                                "id": "0",
                                                                                                "name": "Full Access",
                                                                                                "description": "Full Access group"
                                                                                                        },
                                                                                            "targetGroup": {
                                                                                                "id": -1,
                                                                                                "name": "",
                                                                                                "description": ""
                                                                                                }
                                                                                                }
                                                                                                },
                                                                                            "columns": [
                                                                                                {
                                                                                                    "name": "severityLow"
                                                                                                },
                                                                                                {
                                                                                                    "name": "severityMedium"
                                                                                                },
                                                                                                {
                                                                                                    "name": "severityHigh"
                                                                                                },
                                                                                                {
                                                                                                    "name": "severityCritical"
                                                                                                }
                                                                                                ]
                                                                                    }
                                                                                        ]
                                                                            },
                                                                            "componentType": "lineChart",
                                                                            "sourceLabel": 0,
                                                                            "iteratorID": -1,
                                                                        },
                                                                        {
                                                                        "styleID": 31,
                                                                        "name": "Scoring",
                                                                        "tag": "paragraph",
                                                                        "text": "CVSSv2 scale based on NIST guidelines is used to set severities:\n\nSeverity                        CVSSv2 rating\n\nCritical                                 10 \nHigh                                 7.0 - <10 \nMedium                            4.0 - 6.9 \nLow                                   >0 - 3.9 \nInfo                                        0",
                                                                        }
                                                                        ],
                                                                    }
                                                                ]
                                                            },
                                                    {
                                                        "name": "Vulnerability Scan Results",
                                                        "tag": "chapter",
                                                        "elements": [
                                                            {
                                                                "name": "Scanned systems",
                                                                "tag": "component",
                                                                "definition": {
                                                                    "dataPoints": "2147483647",
                                                                    "displayDataPoints": "10",
                                                                    "columns": [
                                                                        {
                                                                            "name": "ip"
                                                                        },
                                                                        {
                                                                            "name": "dnsName"
                                                                        },
                                                                        {
                                                                            "name": "severityInfo"
                                                                        },
                                                                        {
                                                                            "name": "severityLow"
                                                                        },
                                                                        {
                                                                            "name": "severityMedium"
                                                                        },
                                                                        {
                                                                            "name": "severityHigh"
                                                                        },
                                                                        {
                                                                            "name": "severityCritical"
                                                                        },
                                                                        {
                                                                            "name": "total"
                                                                        }
                                                                        ],
                                                                    "dataSource": {
                                                                        "querySourceID": "",
                                                                        "querySourceView": "",
                                                                        "querySourceType": "cumulative",
                                                                        "sortColumn": "severityCritical",
                                                                        "sortDirection": "desc",
                                                                        "styleID": -2,
                                                                        "query": {
                                                                            "name": "",
                                                                            "description": "",
                                                                            "tool": "sumip",
                                                                            "type": "vuln",
                                                                            "tags": "",
                                                                            "context": "report",
                                                                            "browseColumns": "",
                                                                            "browseSortColumn": "",
                                                                            "browseSortDirection": "ASC",
                                                                            "filters": [
                                                                                {
                                                                                    "filterName": "asset",
                                                                                    "operator": "=",
                                                                                    "value": {"id": assettid}
                                                                                }
                                                                                ],
                                                                            "groups": [],
                                                                            "ownerGroup": {
                                                                                "id": "0",
                                                                                "name": "Full Access",
                                                                                "description": "Full Access group"
                                                                                },
                                                                            "targetGroup": {
                                                                                "id": -1,
                                                                                "name": "",
                                                                                "description": ""
                                                                                }
                                                                        }
                                                                    }
                                                        },
                                                        "componentType": "table"
                                                    },
                                                    {
                                                        "name": "Vulnerability Summary - IP details",
                                                        "tag": "component",
                                                        "definition": {
                                                            "dataPoints": "2147483647",
                                                            "displayDataPoints": "10",
                                                            "columns": [
                                                                {
                                                                    "name": "pluginID"
                                                                },
                                                                {
                                                                    "name": "name"
                                                                },
                                                                {
                                                                    "name": "severity"
                                                                },
                                                                {
                                                                    "name": "total"
                                                                },
                                                                {
                                                                    "name": "hosts"
                                                                }
                                                            ],
                                                            "dataSource": {
                                                                "querySourceID": "",
                                                                "querySourceView": "",
                                                                "querySourceType": "cumulative",
                                                                "sortColumn": "severity",
                                                                "sortDirection": "desc",
                                                                "styleID": -2,
                                                                "query": {
                                                                    "name": "",
                                                                    "description": "",
                                                                    "tool": "vulnipdetail",
                                                                    "type": "vuln",
                                                                    "tags": "",
                                                                    "context": "report",
                                                                    "browseColumns": "",
                                                                    "browseSortColumn": "",
                                                                    "browseSortDirection": "ASC",
                                                                    "filters": [
                                                                        {
                                                                            "filterName": "severity",
                                                                            "operator": "=",
                                                                            "value": [
                                                                                {
                                                                                    "id": "1",
                                                                                    "name": "Low",
                                                                                    "description": "Low Severity"
                                                                                },
                                                                                {
                                                                                    "id": "2",
                                                                                    "name": "Medium",
                                                                                    "description": "Medium Severity"
                                                                                },
                                                                                {
                                                                                    "id": "3",
                                                                                    "name": "High",
                                                                                    "description": "High Severity"
                                                                                },
                                                                                {
                                                                                    "id": "4",
                                                                                    "name": "Critical",
                                                                                    "description": "Critical Severity"
                                                                                }
                                                                            ]
                                                                        },
                                                                        {
                                                                            "filterName": "asset",
                                                                            "operator": "=",
                                                                            "value": {"id": assettid}
                                                                        }
                                                                    ],
                                                                    "groups": [],
                                                                    "ownerGroup": {
                                                                        "id": "0",
                                                                        "name": "Full Access",
                                                                        "description": "Full Access group"
                                                                    },
                                                                    "targetGroup": {
                                                                        "id": -1,
                                                                        "name": "",
                                                                        "description": ""
                                                                    }
                                                                    }
                                                            }
                                                            },
                                                            "componentType": "table"
                                                            },
                                                    {
                                                        "name": "Vulnerability details",
                                                        "tag": "group",
                                                        "elements": [
                                                            {
                                                                "name": "Host Vulnerability Summary",
                                                                "tag": "component",
                                                                "definition": {
                                                                    "dataPoints": "254",
                                                                    "displayDataPoints": "10",
                                                                    "columns": [
                                                                            {
                                                                                "name": "pluginID"
                                                                            },
                                                                            {
                                                                                "name": "pluginName"
                                                                            },
                                                                            {
                                                                                "name": "severity"
                                                                            },
                                                                            {
                                                                                "name": "ip"
                                                                            },
                                                                            {
                                                                                "name": "protocol"
                                                                            },
                                                                            {
                                                                                "name": "port"
                                                                            },
                                                                            {
                                                                                "name": "dnsName"
                                                                            },
                                                                            {
                                                                                "name": "synopsis"
                                                                            },
                                                                            {
                                                                                "name": "description"
                                                                            },
                                                                            {
                                                                                "name": "solution"
                                                                            },
                                                                            {
                                                                                "name": "baseScore"
                                                                            },
                                                                            {
                                                                                "name": "cvssVector"
                                                                            },
                                                                            {
                                                                                "name": "cve"
                                                                            },
                                                                            {
                                                                                "name": "firstSeen"
                                                                            },
                                                                            {
                                                                                "name": "lastSeen"
                                                                            }
                                                                    ],
                                                                    "dataSource": {
                                                                        "querySourceID": "",
                                                                        "querySourceView": "",
                                                                        "querySourceType": "cumulative",
                                                                        "sortColumn": "pluginID",
                                                                        "sortDirection": "desc",
                                                                        "styleID": -2,
                                                                        "query": {
                                                                            "name": "",
                                                                            "description": "",
                                                                            "tool": "vulndetails",
                                                                            "type": "vuln",
                                                                            "tags": "",
                                                                            "context": "report",
                                                                            "browseColumns": "",
                                                                            "browseSortColumn": "",
                                                                            "browseSortDirection": "ASC",
                                                                            "filters": [
                                                                                {
                                                                                    "filterName": "pluginID",
                                                                                    "operator": "<=",
                                                                                    "value": "999999"
                                                                                },
                                                                                {
                                                                                    "filterName": "severity",
                                                                                    "operator": "=",
                                                                                    "value": [
                                                                                        {
                                                                                            "id": "4",
                                                                                            "name": "Critical",
                                                                                            "description": "Critical Severity"
                                                                                        },
                                                                                        {
                                                                                            "id": "3",
                                                                                            "name": "High",
                                                                                            "description": "High Severity"
                                                                                        },
                                                                                        {
                                                                                            "id": "2",
                                                                                            "name": "Medium",
                                                                                            "description": "Medium Severity"
                                                                                        },
                                                                                        {
                                                                                            "id": "1",
                                                                                            "name": "Low",
                                                                                            "description": "Low Severity"
                                                                                        }
                                                                                    ]
                                                                                },
                                                                                {
                                                                                    "filterName": "asset",
                                                                                    "operator": "=",
                                                                                    "value": {"id": assettid}
                                                                                }
                                                                            ],
                                                                            "groups": [],
                                                                            "ownerGroup": {
                                                                                "id": "0",
                                                                                "name": "Full Access",
                                                                                "description": "Full Access group"
                                                                            },
                                                                            "targetGroup": {
                                                                                "id": -1,
                                                                                "name": "",
                                                                                "description": ""
                                                                            }
                                                                        }
                                                                    }
                                                                    },
                                                                    "componentType": "table"
                                                                    },
                                                                    {
                                                                "name": "Scan Results",
                                                                "tag": "iterator",
                                                                "definition": {
                                                                        "dataSource": {
                                                                            "querySourceID": "",
                                                                            "querySourceView": "",
                                                                            "querySourceType": "cumulative",
                                                                            "sortColumn": "score",
                                                                            "sortDirection": "desc",
                                                                            "query": {
                                                                                "name": "",
                                                                                "description": "",
                                                                                "tool": "sumip",
                                                                                "type": "vuln",
                                                                                "tags": "",
                                                                                "context": "report",
                                                                                "browseColumns": "",
                                                                                "browseSortColumn": "",
                                                                                "browseSortDirection": "ASC",
                                                                                "filters": [
                                                                                    {
                                                                                        "filterName": "pluginID",
                                                                                        "operator": "<=",
                                                                                        "value": "999999"
                                                                                    },
                                                                                    {
                                                                                        "filterName": "severity",
                                                                                        "operator": "=",
                                                                                        "value": [
                                                                                            {
                                                                                                "id": "3",
                                                                                                "name": "High",
                                                                                                "description": "High Severity"
                                                                                            },
                                                                                            {
                                                                                                "id": "4",
                                                                                                "name": "Critical",
                                                                                                "description": "Critical Severity"
                                                                                            },
                                                                                            {
                                                                                                "id": "2",
                                                                                                "name": "Medium",
                                                                                                "description": "Medium Severity"
                                                                                            },
                                                                                            {
                                                                                                "id": "1",
                                                                                                "name": "Low",
                                                                                                "description": "Low Severity"
                                                                                            },
                                                                                            {
                                                                                                "id": "0",
                                                                                                "name": "Info",
                                                                                                "description": "Info Severity"
                                                                                            }
                                                                                        ]
                                                                                    },
                                                                                    {
                                                                                        "filterName": "asset",
                                                                                        "operator": "=",
                                                                                        "value": {"id": assettid}
                                                                                    }
                                                                                ],
                                                                                "groups": [],
                                                                                "ownerGroup": {
                                                                                    "id": "0",
                                                                                    "name": "Full Access",
                                                                                    "description": "Full Access group"
                                                                                },
                                                                                "targetGroup": {
                                                                                    "id": -1,
                                                                                    "name": "",
                                                                                    "description": ""
                                                                                }
                                                                            }
                                                                        },
                                                                        "columns": [
                                                                            {
                                                                                "name": "dnsName"
                                                                            },
                                                                            {
                                                                                "name": "osCPE"
                                                                            },
                                                                            {
                                                                                "name": "macAddress"
                                                                            },
                                                                            {
                                                                                "name": "total"
                                                                            },
                                                                            {
                                                                                "name": "severityAll"
                                                                            }
                                                                        ],
                                                                        "dataPoints": "254"
                                                                    },
                                                                    "elements": [
                                                                        {
                                                                            "name": 3.1,
                                                                            "tag": "group",
                                                                            "elements": [
                                                                                {
                                                                                    "name": "3.1.3",
                                                                                    "tag": "paragraph",
                                                                                    "text": "The Scan Results iterator includes detailed information about each host detected with high and critical severity vulnerabilities. For each host, four elements are included. The Vulnerability Results bar chart displays the counts of vulnerabilities on that host by severity. The PCI Vulnerability Remediation Opportunities table lists the ten remediation options for the host with the highest risk reduction percentages. The Critical Vulnerability Summary table lists information about all critical severity vulnerabilities detected on the host. The High Vulnerability Summary table lists information about all high severity vulnerabilities detected on the host. The Remediated Critical Vulnerabilities table lists all critical vulnerabilities that were remediated on the host in the past 30 days. The Remediated High Vulnerabilities table lists all high vulnerabilities that were remediated on the host in the past 30 days. All of this information can be used to identify steps for remediating vulnerabilities on specific hosts."
                                                                                }
                                                                            ]
                                                                        },
                                                                        {
                                                                            "name": "Remediated Critical Vulnerabilities",
                                                                            "tag": "component",
                                                                            "definition": {
                                                                                "dataPoints": "100",
                                                                                "displayDataPoints": "10",
                                                                                "columns": [
                                                                                    {
                                                                                        "name": "pluginID"
                                                                                    },
                                                                                    {
                                                                                        "name": "name"
                                                                                    },
                                                                                    {
                                                                                        "name": "familyID"
                                                                                    },
                                                                                    {
                                                                                        "name": "severity"
                                                                                    },
                                                                                    {
                                                                                        "name": "total"
                                                                                    }
                                                                                ],
                                                                                "dataSource": {
                                                                                    "querySourceID": "",
                                                                                    "querySourceView": "",
                                                                                    "querySourceType": "patched",
                                                                                    "sortColumn": "severity",
                                                                                    "sortDirection": "desc",
                                                                                    "styleID": -2,
                                                                                    "query": {
                                                                                        "name": "",
                                                                                        "description": "",
                                                                                        "tool": "sumid",
                                                                                        "type": "vuln",
                                                                                        "tags": "",
                                                                                        "context": "report",
                                                                                        "browseColumns": "",
                                                                                        "browseSortColumn": "",
                                                                                        "browseSortDirection": "ASC",
                                                                                        "filters": [
                                                                                            {
                                                                                                "filterName": "severity",
                                                                                                "operator": "=",
                                                                                                "value": [
                                                                                                    {
                                                                                                        "id": "4",
                                                                                                        "name": "Critical",
                                                                                                        "description": "Critical Severity"
                                                                                                    }
                                                                                                ]
                                                                                            },
                                                                                            {
                                                                                                "filterName": "lastMitigated",
                                                                                                "operator": "=",
                                                                                                "value": "0:30"
                                                                                            },
                                                                                            {
                                                                                                "filterName": "asset",
                                                                                                "operator": "=",
                                                                                                "value": {"id": assettid}
                                                                                            }
                                                                                        ],
                                                                                        "groups": [],
                                                                                        "ownerGroup": {
                                                                                            "id": "0",
                                                                                            "name": "Full Access",
                                                                                            "description": "Full Access group"
                                                                                        },
                                                                                        "targetGroup": {
                                                                                            "id": -1,
                                                                                            "name": "",
                                                                                            "description": ""
                                                                                        }
                                                                                    }
                                                                                }
                                                                            },
                                                                            "componentType": "table"
                                                                        },
                                                                        {
                                                                        "name": "Remediated High Vulnerabilities",
                                                                        "tag": "component",
                                                                        "definition": {
                                                                        "dataPoints": "100",
                                                                        "displayDataPoints": "10",
                                                                        "columns": [
                                                                            {
                                                                                "name": "pluginID"
                                                                            },
                                                                            {
                                                                                "name": "name"
                                                                            },
                                                                            {
                                                                                "name": "familyID"
                                                                            },
                                                                            {
                                                                                "name": "severity"
                                                                            },
                                                                            {
                                                                                "name": "total"
                                                                            }
                                                                        ],
                                                                        "dataSource": {
                                                                            "querySourceID": "",
                                                                            "querySourceView": "",
                                                                            "querySourceType": "patched",
                                                                            "sortColumn": "severity",
                                                                            "sortDirection": "desc",
                                                                            "styleID": -2,
                                                                            "query": {
                                                                                "name": "",
                                                                                "description": "",
                                                                                "tool": "sumid",
                                                                                "type": "vuln",
                                                                                "tags": "",
                                                                                "context": "report",
                                                                                "browseColumns": "",
                                                                                "browseSortColumn": "",
                                                                                "browseSortDirection": "ASC",
                                                                                "filters": [
                                                                                    {
                                                                                        "filterName": "severity",
                                                                                        "operator": "=",
                                                                                        "value": [
                                                                                            {
                                                                                                "id": "3",
                                                                                                "name": "High",
                                                                                                "description": "High Severity"
                                                                                            }
                                                                                        ]
                                                                                    },
                                                                                    {
                                                                                        "filterName": "lastMitigated",
                                                                                        "operator": "=",
                                                                                        "value": "0:30"
                                                                                    },
                                                                                    {
                                                                                        "filterName": "asset",
                                                                                        "operator": "=",
                                                                                        "value": {"id": assettid}
                                                                                    }
                                                                                ],
                                                                                "ownerGroup": {
                                                                                    "id": "0",
                                                                                    "name": "Full Access",
                                                                                    "description": "Full Access group"
                                                                                },
                                                                                "targetGroup": {
                                                                                    "id": -1,
                                                                                    "name": "",
                                                                                    "description": ""
                                                                                }
                                                                            }
                                                                        }
                                                                    },
                                                                    "componentType": "table"
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ], "coverPage": {}, "paper": {}, 
                                            "tableOfContents": [], "footer": {}, 
                                            "header": {}}, "type": "pdf", 
                                            "schedule": {"type": "template"}, 
                                            "styleFamily": {"id": 1, "name": "Tenable, Letter", 
                                            "description": "Default Tenable style, letter"}, 
                                            "schedule": {"start": "TZID=Europe/Stockholm:20190327T110000", 
                                            "repeatRule": "FREQ=NOW;INTERVAL=1", 
                                            "type": "now"}}

            # Create & launch report using custom template
            sc.HTTPRequest('POST', 'reportDefinition', data=reportdata)


    except Exception:
        # Problem with trying to get data from tenable.sc
        # Log error and exit script
        logger.error('Failed to create a report in tenable.sc')
        logger.error('Likely cause is the query is malformed', exc_info=True)
        closeexit(1)

# ===================================================================
# --- Exit status
# ===================================================================

def closeexit(exit_code):

    """Function to handle exiting the script either cleanly or with an error
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

    # Get credential data from "config.conf" file.
    sc_host = config.get('tenable.sc', 'sc_host')
    sc_username = config.get('tenable.sc', 'sc_username')
    sc_password = config.get('tenable.sc', 'sc_password')


    try:
        #--- Connect to tenable.sc ---

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
     

    try:

        # Loop through assets and fetch their IDs and names
        for asset in sc.HTTPRequest('GET', 'asset').json()['response']['usable']:
                    
            # Read through all report names in "CustomReport"
            for key in config.options('CustomReport'):

                if key.upper() == asset['name'].upper():
                    
                    CreateReport(asset['id'], asset['name'])

    except Exception:
        # Problem with trying to get data from SecurityCenter
        # Log error and exit script
        logger.error('Failed to invoke ReportCreator method')
        logger.error('Likely cause is the query is malformed', exc_info=True)
        closeexit(1)
        
    # Close log file and exit script cleanly
    closeexit(0)
