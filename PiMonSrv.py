import os
import platform
import subprocess

def ping(host):
    """
    Returns True if host (str) responds to a ping request
    """

    # Option for the number of packets as a function of OS
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Build the command
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0


host = str("8.8.8.8")

retVal = ping(host)
print ("returned " + str(retVal))

