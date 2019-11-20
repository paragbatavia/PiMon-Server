import sys
import os
import platform
import subprocess
import time
import gpiozero
import smtplib, ssl, email
import yaml
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

relayGPIO = 21



def ping(host, printOutput):
    """
    Returns True if host (str) responds to a ping request
    Code taken from: https://stackoverflow.com/questions/2953462/pinging-servers-in-python
    """

    # Option for the number of packets as a function of OS
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Build the command
    command = ['ping', param, '1', host]

    if not printOutput:
        FNULL = subprocess.DEVNULL
    else:
        FNULL = sys.stdout # only this works - subprocess.STDOUT fails
        
    return subprocess.call(command, stdout=FNULL, stderr=FNULL) == 0


def resetRouter(downTime, waitTime):
    """
    Does a simple sequence to reset the router
    downTime: how long to power down the router (float, seconds)
    waitTime: how long to wait before testing the router for activity
    """

    # send a power down command
    relay.on()
    time.sleep(downTime)

    # send a power up command
    relay.off()
    # wait for everything to come back up
    time.sleep(waitTime)

    # did it work?
    return ping(host, False)
    
def readMailParams(fileName):
    """
    Reads SMTP params from a YAML file - since we don't want to hard code that
    fileName: string of param file name
    """
    
    with open(fileName) as f:
        smtpParams = yaml.load(f, Loader=yaml.FullLoader)

    return smtpParams

def sendMail(smtpParams, subjectText, mailText):
    """
    Sends email based on SMTP params
    Partially taken from https://realpython.com/python-send-email/
    smtpParams = (string) filename of YAML file with SMTP params
    subject = (string) subject of email
    mailText = (string) full text of email to send
    """

    server = smtpParams["mailServer"]
    port = smtpParams["mailPort"]
    user = smtpParams["mailUsername"]
    password = smtpParams["mailPassword"]

    sender = smtpParams["senderEmail"]
    recipient = smtpParams["recipientEmail"]

    message = MIMEMultipart("alternative")
    message["Subject"] = subjectText
    message["From"] = sender
    message["To"] = recipient
    part1 = MIMEText(mailText, "plain")
    message.attach(part1)
    
    context = ssl.create_default_context()

    #    with smtplib.SMTP_SSL(server, port, context=context) as server:
    #
    #        server.login(user, password)
    #        server.sendmail(senderEmail, recipientEmail, mailText)

    try:
        server = smtplib.SMTP(server, port)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(user, password)
        server.sendmail(sender, recipient, message.as_string())
    except Exception as e:
        print(e)
    finally:
        server.quit()
        


smtpParams = readMailParams("smtpParams.yaml")

subject = "mail test"
message = """\
This is a test email.
"""

# sendMail(smtpParams, subject, message)

        
relay = gpiozero.LED(relayGPIO)

# how long to sleep between checks (seconds)
sleepTime = 5.0
# how long internet must be down before restarting (seconds)
restartDelay = 60.0
# how long internet has been down
downTime = 0.0
mailSent = False

while 1:
    # first, check to see if we have internet
    retVal = ping(host, true)
    if not retVal:
        # internet is down
        downTime = downTime + sleepTime
    else:
        downTime = 0.0


    if downTime >= restartDelay:
        itWorked = resetRouter(15.0, 120.0)

    # if a successful restart, then reset downtime counter. If not, it'll end up resetting again
    if itWorked:
        downTime = 0.0
        # send email
        now = datetime.now()
        dtStr = now.strftime("%d/%m/%Y %H:%M:%S")
        subject = "Internet Restarted"
        message = "The cable modem and router were rebooted successful on " + dtStr + "\n")
        sendMail(smtpParams, subject, message)
        
        
    time.sleep(sleepTime)
        

