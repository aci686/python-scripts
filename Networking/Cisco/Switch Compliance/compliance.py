#! /usr/bin/env python

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

# This program does compliance checks on the device configuration
#
# usage: compliance.py [-h] (-i INPUT | -d DEVICE) [-o OUTPUT | -c] -f FILE
#                      [-s SECTION] [-x] [-v] [-u USER]
# 
# optional arguments:
#   -h, --help            show this help message and exit
#   -i INPUT, --input INPUT
#                         input ip addresses file
#   -d DEVICE, --device DEVICE
#                         ip address of device to check
#   -o OUTPUT, --output OUTPUT
#                         output log file
#   -c, --color           add colored output
#   -f FILE, --file FILE  file containing checks
#   -s SECTION, --section SECTION
#                         section to check
#   -x, --fix             runs suggested fixes
#   -v, --verbose         output verbosity
#   -u USER, --user USER  username to log on

import paramiko, getpass, base64, time, io, code, re, csv, sys, argparse, os, logging
from netaddr import *

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def send_string_and_wait_for_string(command, wait_string, should_print):
    shell.send(command)
    receive_buffer = ""

    while not wait_string in receive_buffer:		
        receive_buffer += shell.recv(1024).decode()
    if should_print:
        print (receive_buffer)

    return receive_buffer

fixes_list_raw = []

def global_check(pattern, data):
	status = " Fail"
	dataline = data.splitlines()
	
	if args.verbose:
		print ("\t\t\""+pattern+"\"...", end='')
	for line in dataline:
		if(re.match("^"+pattern, line)):
			status = " OK"
	if args.verbose:
		if args.color:
			if status==" Warning":
				print (bcolors.WARNING + status + bcolors.ENDC)
			if status==" Fail":
				print (bcolors.FAIL + status + bcolors.ENDC)
			else:
				print (bcolors.OKGREEN + status + bcolors.ENDC)
		else:
			print (status)
				
	return status
		
def tline_check(pattern, data):
	status = " Fail"
	dataline = data.splitlines()
	
	if args.verbose:
		print ("\t\t\""+pattern+"\"...", end='')
	for line in dataline:
		if(re.match("^ "+pattern, line)):
			status = " OK"
	if args.verbose:
		if status == " OK":
			if args.color:
				print (bcolors.OKGREEN + status + bcolors.ENDC)
			else:
				print (status)
		elif status == " Warning":
			if args.color:
				print (bcolors.WARNING + status + bcolors.ENDC)
			else:
				print (status)
		else:
			if args.color:
				print (bcolors.FAIL + status + bcolors.ENDC)
			else:
				print (status)
				
	return status

def phyinterfaces_check():
	status = " Fail"
	data = send_string_and_wait_for_string("show interfaces status\n", "#", False)
	dataline = data.splitlines()
	
	for line in dataline:
		datafields = line.split()
		if(re.match("^Gi", line) or re.match("^Te", line) or re.match("^Fa", line)):
			if(re.search("trunk", line)):
				compliance=" OK"
				if args.verbose:
					print ("\tChecking interface " + datafields[0]+"...")
				else:
					print ("\tChecking interface " + datafields[0]+"...", end='')
				inter = send_string_and_wait_for_string("show run interface " + datafields[0] + "\n", "#", False)
				with open(args.file) as input_data:
					for line in input_data:
						if line.strip() == 'interface trunk {':
							break
					for line in input_data:
						if line.strip() == '}':
							break
						if interface_check (datafields[0], line.strip('\n'), inter) == " Fail":
							compliance=" Fail"
				if args.verbose:
					nothing=0
				else:
					if compliance==" Fail":
						if args.color:
							print (bcolors.FAIL + compliance + bcolors.ENDC)
						else:
							print(compliance)
					else:
						print(bcolors.OKGREEN + compliance+ bcolors.ENDC)
			else:
				compliance=" OK"
				if args.verbose:
					print ("\tChecking interface " + datafields[0]+"...")
				else:
					print ("\tChecking interface " + datafields[0]+"...", end='')
				inter = send_string_and_wait_for_string("show run interface " + datafields[0] + "\n", "#", False)
				with open(args.file) as input_data:
					for line in input_data:
						if line.strip() == 'interface access {':
							break
					for line in input_data:
						if line.strip() == '}':
							break
						if interface_check (datafields[0], line.strip('\n'), inter) == " Fail":
							compliance=" Fail"
				if args.verbose:
					nothing=0
				else:
					if compliance==" Fail":
						if args.color:
							print (bcolors.FAIL + compliance + bcolors.ENDC)
						else:
							print(compliance)
					else:
						print(bcolors.OKGREEN + compliance+ bcolors.ENDC)

def virinterfaces_check():
	status = " Fail"
	data = send_string_and_wait_for_string("show ip interface brief\n", "#", False)
	dataline = data.splitlines()
	
	for line in dataline:
		datafields = line.split()
		compliance=" OK"
		if(re.match("^Vlan", line)):
			if args.verbose:
				print ("\tChecking interface " + datafields[0]+"...")
			else:
				print ("\tChecking interface " + datafields[0]+"...", end='')
			inter = send_string_and_wait_for_string("show run interface " + datafields[0] + "\n", "#", False)
			with open(args.file) as input_data:
				for line in input_data:
					if line.strip() == 'interface vlan {':
						break
				for line in input_data:
					if line.strip() == '}':
						break
					if interface_check (datafields[0], line.strip('\n'), inter) == " Fail":
						compliance=" Fail"						
			if args.verbose:
				nothing=0
			else:
				if compliance==" Fail":
					if args.color:
						print (bcolors.FAIL + compliance + bcolors.ENDC)
					else:
						print(compliance)
				else:
						print(bcolors.OKGREEN + compliance + bcolors.ENDC)
			
def interface_check(interface, pattern, data):
	status = " Fail"
	dataline = data.splitlines()
	
	if args.verbose:
		print ("\t\tChecking \""+pattern+"\"...", end='')
	for line in dataline:		
		if(re.match("^ "+pattern, line)):
			status = " OK"
	if args.verbose:
		if status == " OK":
			if args.color:
				print (bcolors.OKGREEN + status + bcolors.ENDC)
			else:
				print (status)
		elif status == " Warning":
			if args.color:
				print (bcolors.WARNING + status + bcolors.ENDC)
			else:
				print (status)
		else:
			if args.color:
				print (bcolors.FAIL + status + bcolors.ENDC)
			else:
				print (status)
				
	return status
	
def global_section_check():
	compliance=" OK"
	data = send_string_and_wait_for_string("show run\n", "#", False)
	
	if args.verbose:
		print ("\tChecking global options...")
	else:
		print ("\tChecking global options...", end='')
	with open(args.file) as input_data:
		for line in input_data:
			if line.strip() == 'global {':
				break
		for line in input_data:
			if line.strip() == '}':
				break
			if global_check (line.strip('\n'), data) == " Fail":
				fixes_list_raw.append(line.strip('\n'))
				compliance=" Fail"
	if args.verbose:
		nothing=0
	else:
		if compliance==" Fail":
			if args.color:
				print (bcolors.FAIL + compliance + bcolors.ENDC)
			else:
				print(bcolors.OKGREEN+compliance+bcolors.ENDC)
				
def line_section_check():
	compliance=" OK"
	if args.verbose:
		print ("\tChecking console line options...")
	else:
		print ("\tChecking console line options...", end='')
	data = send_string_and_wait_for_string("show run | section line con 0\n", "#", False)
	with open(args.file) as input_data:
		for line in input_data:
			if line.strip() == 'line console {':
				break
		for line in input_data:
			if line.strip() == '}':
				break
			if tline_check (line.strip('\n'), data) == " Fail":
				compliance=" Fail"
	if args.verbose:
		nothing=0
	else:
		if compliance==" Fail":
			if args.color:
				print (bcolors.FAIL + compliance + bcolors.ENDC)
		else:
			print(bcolors.OKGREEN+compliance+ bcolors.ENDC)
			
	compliance=" OK"
	if args.verbose:
		print ("\tChecking vty lines 0 to 4 options...")
	else:
		print ("\tChecking vty lines 0 to 4 options...", end='')
	data = send_string_and_wait_for_string("show run | section line vty 0 4\n", "#", False)
	with open(args.file) as input_data:
		for line in input_data:
			if line.strip() == 'line vty {':
				break
		for line in input_data:
			if line.strip() == '}':
				break
			if tline_check (line.strip('\n'), data) == " Fail":
				compliance= " Fail"
	if args.verbose:
		nothing=0
	else:
		if compliance==" Fail":
			if args.color:
				print (bcolors.FAIL + compliance + bcolors.ENDC)
		else:
			print(bcolors.OKGREEN+compliance+ bcolors.ENDC)
	
	compliance=" OK"
	if args.verbose:
		print ("\tChecking vty lines 5 to 15 options...")
	else:
		print ("\tChecking vty lines 5 to 15 options...", end='')
	data = send_string_and_wait_for_string("show run | section line vty 5 15\n", "#", False)
	with open(args.file) as input_data:
		for line in input_data:
			if line.strip() == 'line vty {':
				break
		for line in input_data:
			if line.strip() == '}':
				break
			if tline_check (line.strip('\n'), data) == " Fail":
				compliance= " Fail"
	if args.verbose:
		nothing=0
	else:
		if compliance==" Fail":
			if args.color:
				print (bcolors.FAIL + compliance + bcolors.ENDC)
			else:
				print(bcolors.OKGREEN+compliance+ bcolors.ENDC)
		else:
			print(compliance)
			
def iosversion_check():
	compliance=" OK"
	print ("\tChecking IOS version...", end='')	
	data = send_string_and_wait_for_string("show version\n", "#", False)
	dataline = data.splitlines()
	for line in dataline:	
		if(re.match("^\*", line)):
			datafields = line.split()
	with open(args.file) as input_data:
		for line in input_data:
			if line.strip() == 'software version {':
				break
		for line in input_data:
			if line.strip() == '}':
				break
			if line.strip('\n')!=datafields[4]:
				compliance=" Fail"
	if args.verbose:
		print(compliance)
	else:
		if compliance==" Fail":
			if args.color:
				print (bcolors.FAIL + compliance + bcolors.ENDC)
			else:
				print(bcolors.OKGREEN+compliance+ bcolors.ENDC)
		else:
			print(compliance)
	
				
def check_compliance(hostname, section):
	if args.color:
		print (bcolors.HEADER + "["+hostname+"]" + bcolors.ENDC + " Checking compliance...")
	else:
		print ("["+hostname+"] Checking compliance...")
	
	if section=="all":
		iosversion_check()
		global_section_check()				
		line_section_check()
		phyinterfaces_check()
		virinterfaces_check()
		
	elif section=="ios":
		iosversion_check()	
		
	elif section=="global":
		global_section_check()
					
	elif section=="line":
		line_section_check()
	
	elif section=="physinterfaces":
		phyinterfaces_check()
		
	elif section=="virtinterfaces":
		virinterfaces_check()
		
	elif section=="version":
		iosversion_check()

def run_fix(command):
	print (bcolors.HEADER + "["+datafields[1]+"]" + bcolors.ENDC + " Running command ["+command+"]...", end='')
	send_string_and_wait_for_string("configure terminal\n", "#", False)
	send_string_and_wait_for_string(command+'\n', "#", False)
	send_string_and_wait_for_string("end\n", "#", False)
	print (" OK")
	client.close()

class multifile(object):
    def __init__(self, files):
        self._files = files
    def __getattr__(self, attr, *args):
        return self._wrap(attr, *args)
    def _wrap(self, attr, *args):
        def g(*a, **kw):
            for f in self._files:
                res = getattr(f, attr, *args)(*a, **kw)
            return res
        return g

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
global ipadd
global shell
	
parser = argparse.ArgumentParser()
group1=parser.add_mutually_exclusive_group(required=True)
group1.add_argument("--input", help="input ip addresses file", type=str)
group1.add_argument("--device", help="ip address of device to check", type=str)
group1.add_argument("--range", help="ip address range to check", type=str)
group2=parser.add_mutually_exclusive_group()
group2.add_argument("--output", help="output log file", type=str)
group2.add_argument("--color", help="add colored output", action="store_true")
parser.add_argument("--file", help="file containing checks", type=str, required=True)
parser.add_argument("--section", help="section to check", type=str, default='all')
parser.add_argument("--fix", help="runs suggested fixes", action="store_true")
parser.add_argument("--verbose", help="output verbosity", action="store_true")
parser.add_argument("--user", help="username to log on", type=str, required=True)

args = parser.parse_args()
if args.user:
	username = args.user
	password = getpass.getpass()
else:
	print("\n\nNo username found. Please add the right option to the command line.")
	exit()
if args.output:
	sys.stdout = multifile([ sys.stdout, open(args.output, 'w') ])
if args.input:
	sourcedata = args.input
	ipaddress = [lines.rstrip('\n') for lines in open(sourcedata)]
	for ipadd in ipaddress:
		if args.color:
			print (bcolors.HEADER + "[DEV]" + bcolors.ENDC + " Connecting to " + ipadd)
		else:
			print ("[DEV] Connecting to " + ipadd)
		try:
			client.connect(ipadd, username=username, password=password, timeout=10)
			shell = client.invoke_shell()
			send_string_and_wait_for_string("", "#", False)
			send_string_and_wait_for_string("terminal length 0\n", "#", False)
			data = send_string_and_wait_for_string("show run | i hostname\n", "#", False)
			dataline = data.splitlines()
			for line in dataline:	
				if(re.match("^hostname", line)):
					datafields = line.split()
			check_compliance(datafields[1], args.section)
			if args.fix:
				fixes_list=set(fixes_list_raw)
				for i in fixes_list:
					answer = input (bcolors.HEADER + "["+datafields[1]+"]" + bcolors.ENDC + " Suggested fix "+bcolors.WARNING+"["+i+"]"+bcolors.ENDC+". Do you want to apply it (y/N)?")
					if not answer or answer[0].lower() != 'y':
						continue
					else:
						run_fix(i)
		except:
			if args.color:
				print(bcolors.HEADER + "[DEV]" + bcolors.ENDC + " Connection error")
			else:
				print("[DEV] Connection error")
			continue
if args.device:
	ipadd=args.device
	if args.color:
		print (bcolors.HEADER + "[DEV]" + bcolors.ENDC + " Connecting to " + ipadd)
	else:
		print ("[DEV] Connecting to " + ipadd)
	try:
		client.connect(ipadd, username=username, password=password, timeout=10)
		shell = client.invoke_shell()
		send_string_and_wait_for_string("", "#", False)
		send_string_and_wait_for_string("terminal length 0\n", "#", False)
		data = send_string_and_wait_for_string("show run | i hostname\n", "#", False)
		dataline = data.splitlines()
		for line in dataline:	
			if(re.match("^hostname", line)):
				datafields = line.split()
		check_compliance(datafields[1], args.section)
		if args.fix:
			fixes_list=set(fixes_list_raw)
			for i in fixes_list:
				answer = input (bcolors.HEADER + "["+datafields[1]+"]" + bcolors.ENDC + " Suggested fix "+bcolors.WARNING+"["+i+"]"+bcolors.ENDC+". Do you want to apply it (y/N)?")
				if not answer or answer[0].lower() != 'y':
					continue
				else:
					run_fix(i)
		client.close()				
	except:
		if args.color:
			print(bcolors.HEADER + "[DEV]" + bcolors.ENDC + " Connection error")
		else:
			print("[DEV] Connection error")
if args.range:
	iplist = IPNetwork (args.range)
	for ipaddress in iplist.iter_hosts():
		ipadd=str(ipaddress)
		if args.color:
			print (bcolors.HEADER + "[DEV]" + bcolors.ENDC + " Connecting to " + ipadd)
		else:
			print ("[DEV] Connecting to " + ipadd)
		try:
			client.connect(ipadd, username=username, password=password, timeout=10)
			shell = client.invoke_shell()
			send_string_and_wait_for_string("", "#", False)
			send_string_and_wait_for_string("terminal length 0\n", "#", False)
			data = send_string_and_wait_for_string("show run | i hostname\n", "#", False)
			dataline = data.splitlines()
			for line in dataline:	
				if(re.match("^hostname", line)):
					datafields = line.split()
			check_compliance(datafields[1], args.section)
			if args.fix:
				fixes_list=set(fixes_list_raw)
				for i in fixes_list:
					answer = input (bcolors.HEADER + "["+datafields[1]+"]" + bcolors.ENDC + " Suggested fix "+bcolors.WARNING+"["+i+"]"+bcolors.ENDC+". Do you want to apply it (y/N)?")
					if not answer or answer[0].lower() != 'y':
						continue
					else:
						run_fix(i)
		except:
			if args.color:
				print(bcolors.HEADER + "[DEV]" + bcolors.ENDC + " Connection error")
			else:
				print("[DEV] Connection error")
			continue

			
if __name__ == "__main__":
	args = parser.parse_args()