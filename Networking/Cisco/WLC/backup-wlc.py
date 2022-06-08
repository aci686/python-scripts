#!/usr/bin/env python
"""
    Script to backup Cisco WLCs using netmiko

    # Version 1.0 28.Aug.2017
    # Nick Bettison - Linickx.com

    # External Credit...
    # https://github.com/AlexMunoz905/Cisco-Backup-Config/blob/master/WLC.py
    # Thanks to ^that^ for getting me started! :)
"""
import logging
import getpass
import re
import datetime
import sys

try:
    import netmiko
except:
    print("Error Netmiko not installed - https://github.com/ktbyers/netmiko")
    sys.exit()

"""
    This array stores a list if IPS to connect to
    eg.
        one device: `ips = ["10.1.2.12"]`
        two devices: `ips = ["10.1.2.12", "10.1.3.13"]
`
"""
ips = ["10.211.48.30", "10.212.11.70"]

"""
    By default, ths scipt prompts for credentials.
    If you're feeling insecure and want to store them in the file, replace below with...
    um = "admin"
    pw = "insecure_password"
"""
un = input('Username: ')
pw = getpass.getpass()

"""
    No Need to change below here!
"""
logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s', level=logging.INFO)
logger = logging.getLogger("wlc_backup")
devices = [] # Empty array to store wlcs
files = [] # Empty array to store filenames

for ip in ips:
    # device definition
    cisco_wlc = {
        'device_type': 'cisco_wlc',
        'ip': ip,
        'username': un,
        'password': pw,
    }
    devices.append(cisco_wlc)

for device in devices:
    logger.info("Connecting to %s", device['ip'])
    # connect to the device w/ netmiko
    try:
        net_connect = netmiko.ConnectHandler(**device)
    except:
        logger.error("Failed to connect to %s", device['ip'])
        logger.debug("Exception: %s", sys.exc_info()[0])
        continue

    # get the prompt as a string
    prompt = net_connect.find_prompt()

    logger.debug("prompt: %s", prompt)

    regex = r'^\((.*)\)[\s]>'

    regmatch = re.match(regex, prompt)
    if regmatch:
        hostname = regmatch.group(1)
        logger.info("Working on %s", hostname)
    else:
        logger.error("Hostname Not Found!")
        logger.debug(regmatch)

    filetime = datetime.datetime.now().strftime("%y%m%d-%H%M%S") # File timestamp
    config_filename = hostname + "_" + filetime + ".txt" # Filname with hostname
    files.append(config_filename)
    logger.info("Filename: %s", config_filename)

    commands = ['show run-config commands'] # commands to run

    for cmd in commands:
        logger.info("Sending cmd: %s", cmd)
        this_cmd = net_connect.send_command(cmd)
        config_filename_f = open(config_filename, 'a')
        config_filename_f.write(this_cmd)
        config_filename_f.write('\n')
        config_filename_f.close()

print("Finished:")
for fname in files:
    print(" %s " % fname)
