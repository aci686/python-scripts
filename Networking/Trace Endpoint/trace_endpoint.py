#! /usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

#

import paramiko, getpass, base64, time, io, code, re, csv, sys, argparse, os, logging
from netaddr import *
sys.path.insert(0, "../Cisco/NBCML/")
import nbcml

global ipadd
global shell

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

parser = argparse.ArgumentParser()
parser.add_argument("--user", help="username to log on", type=str)
parser.add_argument("--device", help="core device", type=str)
group1=parser.add_mutually_exclusive_group(required=True)
group1.add_argument("--ip", help="ip address to trace", type=str)
group1.add_argument("--mac", help="mac address to trace", type=str)

args = parser.parse_args()
if args.user:
	username = args.user
	password = getpass.getpass()
else:
	print("\n\nNo username found. Please add the right option to the command line.")
	exit()
if args.device:
	ipadd = args.device
	if args.mac:
		mac = args.mac
		startTime = time.time()
		
		print("\nTracing MAC address " + mac + "\n")
		nextdevice = {}
		print("\n[DEV] Connecting to " + ipadd)
		client.connect(ipadd, username=username, password=password, timeout=10)
		shell = client.invoke_shell()
		nbcml.start_prep_connection(shell)
		nextdevice =nbcml.tracemac(shell, mac)
		if not nextdevice:
			data = nbcml.send_string_and_wait_for_string(shell, "sh mac address-table address " + mac + "\n", "#", False)
			dataline = data.splitlines()
			interf =[]
			for line in dataline:
				if(re.search(mac, line)):
					interf.append(line.split()[3])
			print("\n\nMAC address " + mac + " is connected to " + nbcml.get_hostname(shell) + " on interface " + interf[1] + "\n\n")
		else:
			for i in nextdevice.keys():
				if(nextdevice[i][3] == "1"):
					ipadd =nextdevice[i][1]
					thereisnext =nextdevice[i][3]
					client.close()
					while(thereisnext == "1"):
						print("[DEV] Connecting to " + ipadd)
						client.connect(ipadd, username=username, password=password, timeout=10)
						shell = client.invoke_shell()
						nbcml.start_prep_connection(shell)
						nextdevice =nbcml.tracemac(shell, mac)
						if not nextdevice:
							data = nbcml.send_string_and_wait_for_string(shell, "sh mac address-table address " + mac + "\n", "#", False)
							dataline = data.splitlines()
							interf = []
							for line in dataline:
								if(re.search(mac, line)):
									interf.append(line.split()[3])
							print("\n\nMAC address " + mac + " is connected to " + nbcml.get_hostname(shell) + " on interface " + interf[1] + "\n\n")
							thereisnext = "0"
						else:
							ipadd = nextdevice[i+1][1]
							thereisnext = nextdevice[i+1][3]
							client.close()
					print("\n\nMAC address " + mac + " is connected to " + nextdevice[0] + " on interface " + nextdevice[2] + "\n\n")
		
		client.close()
			
		print("[TIME] {0} seconds".format(time.time() - startTime))
	
	if args.ip:
		startTime = time.time()
		ip = args.ip
		print("\nTracing IP address " + ip + "\n")
		client.connect(ipadd, username=username, password=password, timeout=10)
		shell = client.invoke_shell()
		nbcml.start_prep_connection(shell)
		mac = nbcml.get_macfromip(shell, ip)
		try:
			startTime = time.time()
			print("\nTracing MAC address " + mac + "\n")
			nextdevice = {}
			print("\n[DEV] Connecting to " + ipadd)
			client.connect(ipadd, username=username, password=password, timeout=10)
			shell = client.invoke_shell()
			nbcml.start_prep_connection(shell)
			nextdevice = nbcml.tracemac(shell, mac)
			if not nextdevice:
				data = nbcml.send_string_and_wait_for_string(shell, "sh mac address-table address " + mac + "\n", "#", False)
				dataline = data.splitlines()
				interf = []
				for line in dataline:
					if(re.search(mac, line)):
						interf.append(line.split()[3])
				print("\n\nMAC address " + mac + " is connected to " + nbcml.get_hostname(shell) + " on interface " + interf[1] + "\n\n")
			else:
				for i in nextdevice.keys():
					if(nextdevice[i][3] == "1"):
						ipadd = nextdevice[i][1]
						thereisnext = nextdevice[i][3]
						client.close()
						while(thereisnext == "1"):
							print("[DEV] Connecting to " + ipadd)
							client.connect(ipadd, username=username, password=password, timeout=10)
							shell = client.invoke_shell()
							nbcml.start_prep_connection(shell)
							nextdevice = nbcml.tracemac(shell, mac)
							if not nextdevice:
								data = nbcml.send_string_and_wait_for_string(shell, "sh mac address-table address " + mac + "\n", "#", False)
								dataline = data.splitlines()
								interf = []
								for line in dataline:
									if(re.search(mac, line)):
										interf.append(line.split()[3])
								print("\n\nMAC address " + mac + " is connected to " + nbcml.get_hostname(shell) + " on interface " + interf[1] + "\n\n")
								thereisnext = "0"
							else:
								ipadd = nextdevice[i+1][1]
								thereisnext = nextdevice[i+1][3]
								client.close()
						print("\n\nMAC address " + mac + " is connected to " + nextdevice[0] + " on interface " + nextdevice[2] + "\n\n")
			
			client.close()
			
		except:
			print("[DEV] Connection error")
		print("[TIME] {0} seconds".format(time.time() - startTime))
		
else:
	print("\n\nNo root device specified")

if __name__ == "__main__":
	args = parser.parse_args()
	