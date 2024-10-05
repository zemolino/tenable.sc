
# Import required Python modules
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import time

# ===================================================================
# Email Sender Function
# ===================================================================

def EmailSender(link, name, email_addr, reportname):
    """
    Sends an email with the vulnerability report for a specific service.
    
    Parameters:
    link (str): The URL link for the report.
    name (str): Name of the service.
    email_addr (str): Recipient's email address.
    reportname (str): Name of the report file.
    """
    try:
        # Create the email message container
        msg = MIMEMultipart()
        msg['Subject'] = f"Vulnerability Report for {name} service"
        msg['From'] = "Vulnerability Management <vmgroup@example.com>"
        msg['To'] = email_addr

        # Load the HTML template for the email body
        with open("email_msg.html", 'r', encoding='utf-8') as template_file:
            template_content = template_file.read()

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(template_content, 'html.parser')

        # Update the <a> tag with the appropriate link and service name
        a_tag = soup.find('a')
        if a_tag:
            a_tag['href'] = f"https:{link}/{reportname}"
            a_tag.string = f"{name} service"

        # Update any <strong> tag with the service name
        strong_tag = soup.find('strong')
        if strong_tag:
            strong_tag.string = f"{name} service"

        # Attach the modified HTML content to the email
        msg.attach(MIMEText(soup.prettify(), 'html'))

        # Send the email
        print(f'{name} report is ready and being sent to {email_addr}')

        with smtplib.SMTP('smtp.domainname.com') as server:
            # Uncomment and modify if login is required for SMTP
            # server.login('your_username', 'your_password')
            server.sendmail(msg['From'], msg['To'], msg.as_string())

        print('Email successfully sent to', email_addr)

    except Exception as e:
        print(f"Failed to send email to {email_addr}: {e}")

# --------------------------------------------------------------------------------
# Main Script Execution
# --------------------------------------------------------------------------------

if __name__ == '__main__':
    # These variables should be defined before calling the EmailSender function
    link = "https://yourreportlink.com"
    name = "ServiceName"
    email_addr = "recipient@example.com"
    reportname = "vulnerability_report.pdf"

    EmailSender(link, name, email_addr, reportname)
