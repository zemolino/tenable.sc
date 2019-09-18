# Tenable.sc Scripts
*Important: See Requirements and Setup Instructions below before trying to run the script*

We need only to run scripts that are noted with (Main script) comment: other scripts work as modules during run-time and will be called.

- **config.conf** saves all file paths and credentials that we need to use as input.
- **Combination_Asset_Creator.py** (Main Script) Creates combination asset.
- **email_msg.html** will be called to fetch email message body(It's responsive one).
- **email_sender.py** will be called to send email when find email addresses matched from “Config.conf” file.
- **pyLogger.py** logs all errors or unexpected values if occurs during API run-time with the name of main script name + .log
- **pyServiceNowAPI.py** Logs into ServiceNow, uses "requests" module for Http method.
- **pyTenableAPI.py** Logs into tenable.sc, uses "requests" module for Http method.
- **ReportCreator.py** (Main Script) tenable.sc vuln Report Creator.
- **ReportDownloader.py** (Main Script) Download tenable.sc report results in SharePoint.
- **ServiceNow_2_Tenable.sc.py** (Main Script) A custom tenable.sc Asset Data integration with ServiceNow.









## Requirements

- Tenable.sc 5+
- Python 3 (script was designed using Python 3.6)

Aside from the standard library of modules that come with Python 3 you will need to install the following modules:

- [configparser](https://pypi.org/project/configparser/)
- [codecs](https://pypi.org)
- [struct](https://pypi.org)
- [datetime](https://pypi.org/project/DateTime/)
- [getpass](https://pypi.org/search/?q=%22getpass%22&page=1)
- [smtplib](https://pypi.org/project/secure-smtplib/)
- [bs4](https://pypi.org/project/BeautifulSoup/)
- [logging](https://pypi.org/project/logging/)


To run this script, your folder structure should look like this

    \---Tenable.sc Scripts
        | config.conf
        | Combination_Asset_Creator.py
        | email_msg.html
        | email_sender.py
        | pyLogger.py 
        | pyServiceNowAPI.py
        | pyTenableAPI.py
        | ReportCreator.py
        | ReportDownloader.py
        | ServiceNow_2_Tenable.sc.py
        


        


        

If your system running Python has access to the internet, you can install the modules using the commands:

```
pip install requests
pip install configparser

```



## Setup Instructions
A config.conf file containing the IP address of your tenable.sc server, a user account with at least full read privileges (Auditor), a password.  This config.conf file will be required for all of tenable.sc scripts.

If you don't already have the config.conf file, running the script from a command line for the first time you'll be asked a series of questions (IP, username, password, path) and the config.conf file will be built for you automatically and stored in the parent directory.

See below for an example of the config.conf file:

    [tenable.sc]
    host = 10.10.10.100
    user = username
    pass = password

## Run Instructions

Just run 'ServiceNow_2_Tenable.py' from your favorite Python IDE.

Or you can run it from command line.  If you use the command line, use -m option to run from every directory you are!

    python -m ServiceNow_2_Tenable.py

There are also some other optional arguments you can use as well.


# tenable.sc
