#!/usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

# Until now this script only works with Cisco IOS, Cisco ASA, Cisco SG and Motorola WiNG devices

import argparse, sys, re
import paramiko
import getpass

# Class to put some color on the print output
class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

# Get all our CLI arguments
def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", required=True)
    parser.add_argument("-u", "--user", type=str, required = True)
    parser.add_argument("-p", "--password", type=str, required=True)
    parser.add_argument("-d", "--device", required=True)

    args = parser.parse_args()

    return(args)

# Sends a command to the device, then gets ouput back in reveive_buffer
# Expects to see "wait_string; at the end of receive_buffer to return
# should_print enables verbose ouput for troubleshooting
# command will be the sent command
def send_string_and_wait_for_string(shell, command, wait_string, should_print):
    shell.send(command)
    receive_buffer = ""

    while not wait_string in receive_buffer:		
        receive_buffer += shell.recv(1024).decode()
    if should_print:
        print(receive_buffer)

    return(receive_buffer)

# Prepares connections. Gets device ready and removes paged output
def start_prep_connection(shell, device, username = None, password = None):
    if device == "ios":
        send_string_and_wait_for_string(shell, "", "#", False)
        send_string_and_wait_for_string(shell, "terminal length 0\n", "#", False)
    elif device == "asa" and not password:
        sys.exit()
    elif device == "asa":
        send_string_and_wait_for_string(shell, "\n", "> ", False)
        send_string_and_wait_for_string(shell, "enable\n", ": ", False)
        send_string_and_wait_for_string(shell, password + "\n", "# ", False)
        send_string_and_wait_for_string(shell, "terminal pager 0\n", "# ", False)
    elif device == "motorola":
        send_string_and_wait_for_string(shell, "\n", ">", False)
        send_string_and_wait_for_string(shell, "enable\n", "#", False)
        send_string_and_wait_for_string(shell, "terminal length 0\n", "#", False)
    elif device == "ios-sg":
        send_string_and_wait_for_string(shell, "", "#", False)
        send_string_and_wait_for_string(shell, "terminal datadump\n", "#", False)
    elif device == "ruckus":
        send_string_and_wait_for_string(shell, "\n", ": ", False)
        send_string_and_wait_for_string(shell, username + "\n", ": ", False)
        send_string_and_wait_for_string(shell, password + "\n", "> ", False)
        send_string_and_wait_for_string(shell, "enable\n", "# ", False)

# Gets device hostname
def get_hostname(shell, device):
    dataretrieved = ""
    
    if device == "ios":
        data = send_string_and_wait_for_string(shell, "show run | i hostname\n", "# ", False)
    elif device == "asa":
        data = send_string_and_wait_for_string(shell, "show run | i hostname\n", "# ", False)
    elif device == "motorola":
        data = send_string_and_wait_for_string(shell, "show run | i hostname\n", "#", False)
    elif device == "ios-sg":
        data = send_string_and_wait_for_string(shell, "show run\n", "#", False)
    elif device == "ruckus":
        data = send_string_and_wait_for_string(shell, "show config\n", "#", False)

    dataline = data.splitlines()
    for line in dataline:
        if device == "ios" or device == "asa" or device == "ios-sg":
            if(re.match("^hostname", line)):
                datafields = line.split()
                dataretrieved = datafields[1]
        elif device == "motorola":
            if(re.match("^ hostname", line)):
                datafields = line.split()
                dataretrieved = datafields[1]
        elif device == "ruckus":
            if(re.match("^  Name", line)):
                datafields = line.split()
                dataretrieved = datafields[1]
                return(dataretrieved)

    return(dataretrieved)

# Gets device configuration
def get_config(shell, device, config = "running"):
    dataretrieved = ""
    
    if device == "ios" or device == "ios-sg":
        if config == "running":
            dataretrieved = send_string_and_wait_for_string(shell, "show running\n", "#", False)
        if config == "startup":
            dataretrieved = send_string_and_wait_for_string(shell, "show startup\n", "#", False)
    elif device == "asa":
        if config == "running":
            dataretrieved = send_string_and_wait_for_string(shell, "show running\n", "# ", False)
        if config == "startup":
            dataretrieved = send_string_and_wait_for_string(shell, "show startup\n", "# ", False)
    elif device == "motorola":
        if config == "running":
            dataretrieved = send_string_and_wait_for_string(shell, "show running\n", "#", False)
        if config == "startup":
            dataretrieved = send_string_and_wait_for_string(shell, "show startup\n", "#", False)
    elif device == "ruckus":
        dataretrieved = send_string_and_wait_for_string(shell, "show config\n", "#", False)
            
    return(dataretrieved.strip("show running").lstrip("\r\n").rstrip(get_hostname(shell, device) + "#").rstrip("ruckus#").rstrip("\r\n").rstrip("exit").rstrip("\r\n"))

# Main function      
def main():
    args = get_arguments()
    # Initialize credentials for devices
    if args.user and not args.password:
        username = args.user
        password = getpass.getpass()
    elif args.user and args.password:
        username = args.user
        password = args.password

    # Connects and gets its config file
    if args.ip and args.device:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(args.ip, username=username, password=password, timeout=10)
        shell=client.invoke_shell()
        start_prep_connection(shell, args.device, username, password)
        runningconfig = get_config(shell, args.device, "running")
        # Put the output in a file with the hostname
        file = open(get_hostname(shell, args.device) + ".cfg","w")
        for line in runningconfig:
            file.write(line.strip("\n"))
        file.close()

if __name__ == "__main__":
    main()
