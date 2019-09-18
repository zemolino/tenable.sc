
# import required python modules
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import time

# ===================================================================
# --- Email Sender
# ===================================================================


def EmailSender(link, name, email_addr, reportname):

    msg = MIMEMultipart()

    # msg['From'] == the sender's email address
    # msg['To'] == the recipient's email address
    msg['Subject'] = "Vulnerability Report for " + name + " service "
    msg['From'] = "Vulnerability Management <{0}>".format(
        'vmgroup@example.com')
    msg['To'] = email_addr

    with open("email_msg.html", 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()

    # Parsing HTML file for particular tag names
    soup = BeautifulSoup(template_file_content, 'html.parser')

    a = soup.find('a')
    a['href'] = ("https:" + link + "/" + reportname)
    a.string = name + " service"

    print('{0} is a matched report and ready to send to the recipient'.format(name))

    text_name = soup.find('strong')
    text_name.string = name + " service "

    msg.attach(MIMEText(soup, 'html'))

    server = smtplib.SMTP('smtp.domainname.com')

    #server.login(msg['From'], )
    server.sendmail(msg['From'], msg['To'], msg.as_string())

    print('successfully sent the mail')

    server.quit()

# --------------------------------------------------------------------------------
# --- MAIN body of the script. This is where the pieces come together
# --------------------------------------------------------------------------------


if __name__ == '__main__':

    EmailSender(link, name, email_addr, reportname)
