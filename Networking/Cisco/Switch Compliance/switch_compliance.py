#! /usr/bin/env python

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

# This program does compliance checks on the device configuration
#
# usage: switch_compliance.py [-h] (-i INPUT | -d DEVICE | -r RANGE) [-o OUTPUT] -b BASELINE (-u USER)
#
# optional arguments:
#   -h, --help				show this help message and exit
#   -i INPUT, --input INPUT
#							input file containing ip addresses to check
#   -d DEVICE, --device DEVICE
#							ip address of device to check
#	-r RANGE, --range RANGE
#							ip address range of devices to check
#   -o OUTPUT, --output OUTPUT
#							output log file
#   -b BASELINE, --baseline BASELINE 
#							file containing baseline checks
#   -u USER, --user USER
#							username to log into the devices

import paramiko, getpass, base64, time, io, code, re, csv, sys, argparse, os, logging, math
from netaddr import *
import nbcml

keywords=[

		]
		
template=[
			"no service pad",
			"service timestamps debug datetime msec",
			"service timestamps log datetime msec",
			"service password-encryption",
			"service sequence-numbers",
			"boot-start-marker",
			"boot-end-marker",
			"logging buffered 8192 informational",
			"no logging console",
			"no logging monitor",
			"aaa new-model",
			"aaa authorization console",
			"aaa accounting update periodic 15",
			"aaa session-id common",
			"clock timezone GMT 0 0",
			"no ip source-route",
			"no ip gratuitous-arps",
			"ip icmp rate-limit unreachable 1000",
			"ip dhcp snooping vlan 1-4094",
			"no ip dhcp snooping information option",
			"ip dhcp snooping",
			"no ip domain-lookup",
			"ip domain-name KinrossGold.com",
			"ip device tracking probe delay 5",
			"authentication mac-move permit",
			"authentication critical recovery delay 1000",
			"epm logging",
			"mls qos",
			"dot1x system-auth-control",
			"dot1x guest-vlan supplicant",
			"dot1x critical eapol",
			"spanning-tree mode rapid-pvst",
			"spanning-tree extend system-id",
			"errdisable recovery cause udld",
			"errdisable recovery cause bpduguard",
			"errdisable recovery cause security-violation",
			"errdisable recovery cause channel-misconfig",
			"errdisable recovery cause pagp-flap",
			"errdisable recovery cause dtp-flap",
			"errdisable recovery cause link-flap",
			"errdisable recovery cause sfp-config-mismatch",
			"errdisable recovery cause gbic-invalid",
			"errdisable recovery cause psecure-violation",
			"errdisable recovery cause port-mode-failure",
			"errdisable recovery cause dhcp-rate-limit",
			"errdisable recovery cause pppoe-ia-rate-limit",
			"errdisable recovery cause mac-limit",
			"errdisable recovery cause vmps",
			"errdisable recovery cause storm-control",
			"errdisable recovery cause inline-power",
			"errdisable recovery cause arp-inspection",
			"errdisable recovery cause loopback",
			"errdisable recovery cause small-frame",
			"errdisable recovery cause psp",
			"vlan internal allocation policy ascending",
			"ip tcp synwait-time 10",
			"ip tftp blocksize 8192",
			"ip http server",
			"no ip http secure-server",
			"ip http secure-active-session-modules none",
			"ip http active-session-modules none",
			"ip ssh time-out 10",
			"ip ssh version 2",
			"ip radius source-interface Vlan11 ",
			"logging trap notifications",
			"logging origin-id hostname",
			"logging source-interface Vlan11",
			"logging host 10.20.5.90",
			"logging host 10.20.9.190",
			"snmp-server view no-table iso included",
			"snmp-server view no-table at excluded",
			"snmp-server view no-table snmpUsmMIB excluded",
			"snmp-server view no-table snmpVacmMIB excluded",
			"snmp-server view no-table snmpCommunityMIB excluded",
			"snmp-server view no-table ip.21 excluded",
			"snmp-server view no-table ip.22 excluded",
			"snmp-server enable traps snmp authentication linkdown linkup coldstart warmstart",
			"snmp-server enable traps transceiver all",
			"snmp-server enable traps call-home message-send-fail server-fail",
			"snmp-server enable traps tty",
			"snmp-server enable traps license",
			"snmp-server enable traps auth-framework sec-violation",
			"snmp-server enable traps config-copy",
			"snmp-server enable traps config",
			"snmp-server enable traps config-ctid",
			"snmp-server enable traps fru-ctrl",
			"snmp-server enable traps entity",
			"snmp-server enable traps event-manager",
			"snmp-server enable traps power-ethernet group 1",
			"snmp-server enable traps power-ethernet group 2",
			"snmp-server enable traps power-ethernet police",
			"snmp-server enable traps cpu threshold",
			"snmp-server enable traps vstack",
			"snmp-server enable traps bridge newroot topologychange",
			"snmp-server enable traps stpx inconsistency root-inconsistency loop-inconsistency",
			"snmp-server enable traps syslog",
			"snmp-server enable traps vtp",
			"snmp-server enable traps vlancreate",
			"snmp-server enable traps vlandelete",
			"snmp-server enable traps flash insertion removal",
			"snmp-server enable traps port-security",
			"snmp-server enable traps envmon fan shutdown supply temperature status",
			"snmp-server enable traps stackwise",
			"snmp-server enable traps errdisable",
			"snmp-server enable traps mac-notification change move threshold",
			"snmp-server enable traps vlan-membership",
			"radius-server attribute 6 on-for-login-auth",
			"radius-server attribute 6 support-multiple",
			"radius-server attribute 8 include-in-access-req",
			"radius-server attribute 25 access-request include",
			"radius-server attribute 31 mac format ietf ",
			"radius-server dead-criteria time 1 tries 3",
			"radius-server retry method reorder",
			"radius-server timeout 3",
			"radius-server vsa send cisco-nas-port",
			"ntp source Vlan11",
			"mac address-table notification change interval 0",
			"mac address-table notification change",
			"mac address-table notification mac-move"
		]

# Command class
#
# command[]:				List of words that complete a command
# nroparams:				Number of words
#
# set_command():			Changes the command
# get_name():				Returns a String containing the full command
class command(object):
	def __init__(self,args=""):
		self.command=[]
		self.nroparams=0
		if args:
			for ar in args.split():
				self.nroparams+=1
				self.command.append(ar)

	def __iter__(self):
		for param in self.command:
			yield param

	def set_command(self,args):
		self.nroparams=0
		for ar in args.split():
			self.nroparams+=1
			self.command.append(ar)
		print("con "+str(self.nroparams)+" parametros")

	def get_name(self):
		cadena=""
		for param in self.command:
			cadena+=param+" "
		return cadena

	def get_name_aliased(self):
		cadena=""
		param=""
		if len(keywords)>0:
			for param in self.command:
				if param in self.get_aliases():
					cadena+="<"+param+"> "
				else:
					cadena+=param+" "
		else:
			for param in self.command:
				cadena+=param+" "
		return cadena

	def get_aliases(self):
		occurences = [param for param in self.command if param not in keywords]
		return occurences

# Section class
#
# name:						Command  instance for the section name
# commands[]:				List containing all commands in this section
#
# get_name():				Returns a String containing the section name
# append_command():			Adds a new command to the list
# get_commands():			Returns the list of commands in this section
# find_command():			Return true if command is in command
# find_commands():			Returns a list with all ocurrences of a command in this section
class section (object):
	def __init__(self,args):
		self.name=command(args)
		self.commands=[]

	def __iter__(self):
		for command in self.commands:
			yield command

	def nrof_commands(self):
		return len(self.commands)

	def get_name(self):
		return self.name.get_name()

	def append_command(self,command):
		self.commands.append(command)

	def get_commands(self):
		return self.commands

	def find_command(self,command):
		for each in self.commands:
			if command in each.get_name():
				return True

	def find_commands(self,command):
		occurences=[]
		for each in self.commands:
			if command in each.get_name():
				occurences.append(each)
		return occurences

# Config class
#
# sections[]:				List of Sections fo this configuration
#
# get_nrof_sections():		Returns the number of sections
# get_commands():			Returns all commands
# find_commands():			Returns all commands containing some string
# get_sections():			Returns all sections
# find_sections():			Returns the list of sections with some name
# find_sections_w():		Returns the list of sections with some name that contain some command
# find_sections_wo():		Returns the list of sections with some name that dont contain some command
class config(object):
	def __init__(self,file):
		self.sections=[]
		try:
			with open(file) as input_data:
				i=0
				for line in input_data:
					if not line.startswith("!") and not line.startswith("show") and not line.startswith("Building") and not line.startswith("Current") and not line.startswith("version") and not line.startswith("end") and len(line)>1 and not line.endswith("#"):
						comando=command(line.strip("\n"))
						if not line.strip("\n").startswith(" "):
							self.sections.append(section(line.strip("\n")))
						else:
							self.sections[-1].append_command(comando)
		except EnvironmentError as e:
			print(str(e))

	def __iter__(self):
		for config_section in self.sections:
			yield config_section

	def nrof_sections(self):
		return len(self.sections)

	def get_commands(self):
		occurences=[]
		for each in self.sections:
			if each.nrof_commands()==0:
				occurences.append(each)
		return occurences

	def find_command(self, search):
		for command in self.get_commands():
			if search in command.get_name():
				return True
		return False

	def find_commands(self,search):
		occurences=[]
		commands=self.get_commands()
		for command in commands:
			if search in command.get_name():
				occurences.append(command)
		return occurences

	def get_sections(self):
		occurences=[]
		for each in self.sections:
			if each.nrof_commands()!=0:
				occurences.append(each)
		return occurences

	def find_sections(self,command):
		occurences=[]
		for each in self.sections:
			if command in each.get_name():
				occurences.append(each)
		return occurences

	def find_sections_w(self,command1,command2):
		occurences=[]
		for each in self.sections:
			if each.nrof_commands()>0:
				if command1 in each.get_name():
					if each.find_command(command2):
						occurences.append(each)
		return occurences

	def find_sections_wo(self,command1,command2):
		occurences=[]
		for each in self.sections:
			if each.nrof_commands()>0:
				if command1 in each.get_name():
					if not each.find_command(command2):
						occurences.append(each)
		return occurences

client=paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
global ipadd
global shell

parser=argparse.ArgumentParser()
group1=parser.add_mutually_exclusive_group(required=True)
group1.add_argument("--input",help="input ip addresses file",type=str)
group1.add_argument("--device",help="ip address of device to check",type=str)
group1.add_argument("--range",help="ip address range to check",type=str)
parser.add_argument("--output",help="output log file",type=str)
parser.add_argument("--baseline",help="file containing baseline",type=str,required=True)
parser.add_argument("--user",help="username to log on",type=str,required=True)

def question(question="", options=[], defaultanswer=""):
	print(question+"[", end="",flush=True)
	for option in options:
		if option==defaultanswer:
			print (option+"/", end="",flush=True)
		else:
			print (option+"/", end="",flush=True)
	print("\b]? ", end="", flush=True)
	answer=input()
	if answer=="":
		answer=defaultanswer
	return answer

def send_command(shell,hostname,command):
	nbcml.send_string_and_wait_for_string(shell,command+"\n","#",False)


args=parser.parse_args()
if args.user:
	username=args.user
	password=getpass.getpass()

if args.output:
	sys.stdout=nbcml.multifile([sys.stdout,open(args.output,'w')])

if args.input:
	sourcedata=args.input
	tempfile="/tmp/runningconfig.txt"
	baseline=args.baseline
	ipaddress=[lines.rstrip('\n') for lines in open(sourcedata)]
	for ipadd in ipaddress:	
		hostname="DEV"
		print("["+hostname+"] Connecting to "+ipadd)
		try:
			client.connect(ipadd,username=username,password=password,timeout=10)
			shell=client.invoke_shell()
			nbcml.start_prep_connection(shell)
			hostname=nbcml.get_hostname(shell)
			runningconfig=nbcml.get_config(shell,"running")
			file=open(tempfile,"w")
			for line in runningconfig:
				file.write(line.strip("\n"))
			file.close()
		except EnvironmentError as e:
			print("["+ipadd+"] "+str(e))
		runningconfig=config(tempfile)
		print("["+hostname+"]")
		for interface in runningconfig.find_sections_w("interface", "switchport mode access"):
			has_dot1x=interface.find_command("dot1x pae authenticator")
			if not has_dot1x:
				print ("\t["+interface.get_name().strip().strip("interface ")+"] Missing Dot1X configuration")
		client.close()
	
if args.range:
	#iplist= IPNetwork(args.range)
	#for ipaddress in iplist.iter_hosts():
	#	ipadd=str(ipaddress)
	#	print("[DEV] Connecting to "+ipadd)
	print("Not yet implemented")
	
if args.device:
	ipadd=args.device
	tempfile="/tmp/runningconfig.txt"
	baseline=args.baseline
	hostname="DEV"
	
	print("["+hostname+"] Connecting to "+ipadd)
	try:
		client.connect(ipadd,username=username,password=password,timeout=10)
		shell=client.invoke_shell()
		nbcml.start_prep_connection(shell)
		hostname=nbcml.get_hostname(shell)
		#print("["+hostname+"] Gathering running configuration")
		runningconfig=nbcml.get_config(shell,"running")
		file=open(tempfile,"w")
		for line in runningconfig:
			file.write(line.strip("\n"))
		file.close()
		#print("["+hostname+"] Dumped to "+tempfile)
	except EnvironmentError as e:
		print("[E] "+str(e))
	
	#print("["+hostname+"] Parsing configuration "+tempfile)
	runningconfig=config(tempfile)
	
	print("["+hostname+"]")
	for interface in runningconfig.find_sections_w("interface", "switchport mode access"):
		has_dot1x=interface.find_command("dot1x pae authenticator")
		if not has_dot1x:
			print ("\t["+interface.get_name().strip().strip("interface ")+"] Missing Dot1X configuration")
	
	client.close()

if __name__=="__main__":
	#######################################################################
	# To format output in 2 columns, topleft and topright
	#hw = os.get_terminal_size() #print("Height:", hw[1], "Width:", hw[0])
	#left,right='Template','Running Config'
	#print('{}{}{}{}{}'.format(left,' '*(math.floor((hw[0]-len(left+right))/2)-1),'->',' '*(math.floor((hw[0]-len(left+right))/2)-1),right))
	#######################################################################

	args=parser.parse_args()