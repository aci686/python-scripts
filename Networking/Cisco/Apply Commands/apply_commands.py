#! /usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

# usage: apply_commands.py [-h] (-i INPUT | -d DEVICE) [-o OUTPUT | -c] -f FILE
#                      [-s SECTION] [-x] [-v] [-u USER]
#
# optional arguments:
#   -h, --help            
#							show this help message and exit
#   -i INPUT, --input INPUT
#							input ip addresses file
#   -d DEVICE, --device DEVICE
#							ip address of device to check
#	-r RANGE, --range RANGE
#							ip address range of devices 
#   -o OUTPUT, --output OUTPUT
#							output log file
#   -c FILE, --commands FILE
#							file containing commands to be applied
#   -u USER, --user USER
#							username to log on -has to be the same for all devices

import paramiko, getpass, base64, time, io, code, re, csv, sys, argparse, os, logging, math
from netaddr import *
import nbcml

client=paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
global ipadd
global shell
commands=[]

parser=argparse.ArgumentParser()
group1=parser.add_mutually_exclusive_group(required=True)
group1.add_argument("--input", help="input ip addresses file", type=str)
group1.add_argument("--device", help="ip address of device to check", type=str)
group1.add_argument("--range", help="ip address range to check", type=str)
group2=parser.add_mutually_exclusive_group()
group2.add_argument("--output", help="output log file", type=str)
parser.add_argument("--user", help="username to log on", type=str, required=True)
parser.add_argument("--commands", help="file containing commands",type=str, required=True)

def question(question="", options=[], defaultanswer=""):
	print(question + "[", end="", flush=True)
	for option in options:
		if option==defaultanswer:
			print (option + "/", end="", flush=True)
		else:
			print (option + "/", end="", flush=True)
	print("\b]? ", end="", flush=True)
	answer = input()
	if answer=="":
		answer=defaultanswer
	return answer
	
def send_command(shell, hostname, command):
	print("["+hostname+"] "+command)
	nbcml.send_string_and_wait_for_string(shell, command + "\n", "#", False)
	
args=parser.parse_args()
if args.user:
	username=args.user
	password=getpass.getpass()

if args.output:
	sys.stdout=nbcml.multifile([sys.stdout,open(args.output, 'w')])

if args.input:
	sourcedata=args.input
	ipaddress=[lines.rstrip('\n') for lines in open(sourcedata)]
	for ipadd in ipaddress:
		print("[DEV] Connecting to " + ipadd)
		client.connect(ipadd, username=username, password=password, timeout=10)
		shell = client.invoke_shell()
		nbcml.start_prep_connection(shell)
		hostname=nbcml.get_hostname(shell)
		with open(args.commands) as input_data:
			for line in input_data:
				commands.append(line.strip("\n"))
		send_command(shell, hostname, "conf t")
		for command in commands:
			send_command(shell, hostname, command)
		send_command(shell, hostname, "end")
		if question("[" + hostname + "] Save configuration ", ["Yes"," No"], "No")=="Yes":
			send_command(shell, hostname, "wr")
		client.close()

if args.range:
	iplist= IPNetwork(args.range)
	for ipaddress in iplist.iter_hosts():
		ipadd=str(ipaddress)
		print("[DEV] Connecting to " + ipadd)
		client.connect(ipadd, username=username, password=password, timeout=10)
		shell = client.invoke_shell()
		nbcml.start_prep_connection(shell)
		hostname=nbcml.get_hostname(shell)
		with open(args.commands) as input_data:
			for line in input_data:
				commands.append(line.strip("\n"))
		send_command(shell, hostname, "conf t")
		for command in commands:
			send_command(shell, hostname, command)
		send_command(shell, hostname, "end")
		if question("["+hostname+"] Save configuration ",["Yes", "No"], "No")=="Yes":
			send_command(shell, hostname, "wr")
		client.close()

if args.device:
	ipadd=args.device
	print("[DEV] Connecting to " + ipadd)

	client.connect(ipadd, username=username, password=password, timeout=10)
	shell=client.invoke_shell()
	nbcml.start_prep_connection(shell)
	hostname=nbcml.get_hostname(shell)
	with open(args.commands) as input_data:
		for line in input_data:
			commands.append(line.strip("\n"))
	send_command(shell, hostname, "conf t")
	for command in commands:
		send_command(shell, hostname, command)
	send_command(shell,hostname, "end")
	if question("["+hostname+"] Save configuration ",["Yes", "No"], "No")=="Yes":
		send_command(shell, hostname, "wr")
	client.close()

if __name__ == "__main__":
	args=parser.parse_args()
