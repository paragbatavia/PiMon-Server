import os
import platform
import subprocess
import time
import sys

host = str("8.8.8.8")


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

    time.sleep(downTime)

    # send a power up command

    # wait for everything to come back up
    time.sleep(waitTime)

    # did it work?
    return ping(host)
    


while 1:
    retVal = ping(host, True)
    print ("returned " + str(retVal))
    time.sleep(2.0)

