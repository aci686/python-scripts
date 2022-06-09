#! /usr/bin/env python

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

# Network Bits Cisco Management Library v.0.5
#
# Always use the following at the very begining of your python program
# 	send_string_and_wait_for_string shell, "", "#", False)
# 	send_string_and_wait_for_string(shell, "terminal length 0\n", "#", False)
#
# List of function definitions
#
#	send_string_and_wait_for_string(shell, command, wait_string, should_print) -> Returns buffer
#	start_prep_connection(shell) -> Prepares the connection, skips banner and sets terminal length
#
#	get_users(shell) -> Returns list with all local users created
#	get_config(shell, config = "") -> Returns list with all the configuration lines
#	get_nameservers(shell) -> Returns list with configured name servers
#	get_domainname(shell) -> Returns list with configured domains
#	get_ntpserver(shell) -> Returns list with configured ntp servers
#	get_radiusservers(shell, servername = "all") -> Returns a list of all configured radius servers
#	get_servergroups(shell, name = "all") -> Returns list of all configured server groups
#	get_cdp_neighbors(shell) -> Prints neighbors formatted
#	get_trunks(shell) -> Prints trunk interfaces formatted
#	get_hostname(shell) -> Returns device hostname
#	get_model(shell) -> Returns device model
#	get_version(shell) -> Returns device ios version running
#	get_serial(shell) -> Returns device serial number
#	get_uptime(shell) -> Returns device uptime
#	get_flashimagefile(shell) -> Returns device image file
#	get_bootimagefile(shell) -> Returns device boot image file
#	get_accesslists(shell, type) -> Returns device access lists by type
#	get_accesslist(shell, name) -> Returns access list
#	get_vlans(shell) -> Returns VLANs created
#
#	set_default_interface(shell, interface) -> Reset interface to defaults
#	set_access_interface(shell, interface) -> Configure interface to access mode. Array with commands: access_interface_commands
#	set_trunk_interface(shell, interface) -> Configure interface to trunk mode. Array with commands: trunk_interface_commands

import re, sys

STDACL = "Standard"
EXTACL = "Extended"
RADIUS = "radius"
TACACS = "tacacs+"

##########################################################
# Sends output to a file
# Usage:
#	sys.stdout=multifile([ sys.stdout, open('filepath+name', 'w') ])
#
##########################################################
class multifile(object):
    def __init__(self, files):
        self._files=files
    def __getattr__(self, attr, *args):
        return self._wrap(attr, *args)
    def _wrap(self, attr, *args):
        def g(*a, **kw):
            for f in self._files:
                res=getattr(f, attr, *args)(*a, **kw)
            return res
        return g
##########################################################

def send_string_and_wait_for_string(shell, command, wait_string, should_print):
    shell.send(command)
    receive_buffer = ""

    while not wait_string in receive_buffer:		
        receive_buffer += shell.recv(1024).decode()
    if should_print:
        print(receive_buffer)

    return receive_buffer

def start_prep_connection(shell, password = None, device = "ios"):
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

def get_users(shell, device = "ios"):
	dataretrieved = []
	
	if device == "ios":
		data=send_string_and_wait_for_string(shell, "show run | i username\n", "#", False)
		dataline = data.splitlines()
		for line in dataline:
			datafields = line.split()
			if datafields[0] == "username":
				dataretrieved.append(datafields[1])
				dataretrieved.append(datafields[3])
	elif device == "asa":
		data=send_string_and_wait_for_string(shell, "show run | i username\n", "# ", False)
		dataline = data.splitlines()
		for line in dataline:
			if not line.startswith("show run"):
				datafields = line.split()
				if datafields[0] == "username":
					dataretrieved.append(datafields[1])
					dataretrieved.append(datafields[3])

	return(dataretrieved)
	
def get_config(shell, config = "running", device = "ios"):
	dataretrieved = ""
	
	if device == "ios":
		if config == "running":
			dataretrieved = send_string_and_wait_for_string(shell, "show running\n", "#", False)
		if config == "startup":
			dataretrieved = send_string_and_wait_for_string(shell, "show startup\n", "#", False)
	elif device == "asa":
		if config == "running":
			dataretrieved = send_string_and_wait_for_string(shell, "show running\n", "# ", False)
		if config == "startup":
			dataretrieved = send_string_and_wait_for_string(shell, "show startup\n", "# ", False)		
		
	return(dataretrieved)

def get_nameservers(shell, device = "ios"):
	dataretrieved = []
	
	if device == "ios":
		data = send_string_and_wait_for_string(shell, "show run | i name-server\n", "#", False)
		dataline = data.splitlines()
		for line in dataline:
			if(re.search("ip name-server", line)):
				datafields = line.split()
				dataretrieved.append(datafields[2])
	elif device == "asa":
		data = send_string_and_wait_for_string(shell, "show run | i name-server\n", "# ", True)
		dataline = data.splitlines()
		for line in dataline:
			if not line.startswith("show run"):
				if(re.search("name-server", line)):
					datafields = line.split()
					dataretrieved.append(datafields[1])
	
	return(dataretrieved)

def get_domainname(shell, device = "ios"):
	dataretrieved = []
	
	if device == "ios":
		data = send_string_and_wait_for_string(shell, "show run | i domain\n", "#", False)
		dataline = data.splitlines()
		for line in dataline:
			if(re.search("ip domain name", line)):
				datafields = line.split()
				dataretrieved.append(datafields[3])
	elif device == "asa":
		data = send_string_and_wait_for_string(shell, "show run | i domain\n", "# ", False)
		dataline = data.splitlines()
		for line in dataline:
			if(re.search(" domain-name ", line)):
				datafields = line.split()
				dataretrieved.append(datafields[1])
	
	return(dataretrieved)

def get_ntpserver(shell, device = "ios"):
	dataretrieved = []
	
	if device == "ios":
		data = send_string_and_wait_for_string(shell, "show run | i ntp\n", "#", False)
		dataline = data.splitlines()
		for line in dataline:
			if(re.search("ntp server", line)):
				datafields = line.split()
				dataretrieved.append(datafields[2])
	elif device == "asa":
		data = send_string_and_wait_for_string(shell, "show run | i ntp\n", "# ", False)
		dataline = data.splitlines()
		for line in dataline:
			if(re.search("ntp server", line)):
				datafields = line.split()
				dataretrieved.append(datafields[2])
	
	return(dataretrieved)
	
def get_radiusservers(shell, servername = "all"):
	dataretrieved = []
	
	if servername == "all":
		data = send_string_and_wait_for_string(shell, "show run | i radius server\n", "#", False)
		dataline = data.splitlines()
		for line in dataline:
			if(re.search("radius server", line)):
				datafields = line.split()
				if not datafields[2] == '|':
					dataretrieved.append(datafields[2])
	else:
		data = send_string_and_wait_for_string(shell, "show run | s radius server " + servername + "\n", "#", False)
		dataline = data.splitlines()
		for line in dataline:
			if line[0] == ' ':
				if line [1] == 'a':
					datafields = line.split()
					dataretrieved.append(datafields[1])
					dataretrieved.append(datafields[2])
				if line [1] == "k":
					datafields = line.split()
					dataretrieved.append(datafields[2])
	
	return(dataretrieved)

def get_servergroups(shell, name = "all"):
	dataretrieved = []
	
	if name == "all":
			data = send_string_and_wait_for_string(shell, "show run | i aaa group server\n", "#", False)
			dataline = data.splitlines()
			for line in dataline:
				if(re.search("aaa group server", line)):				
					datafields = line.split()
					if not datafields[2] == "|":
						dataretrieved.append(datafields[3])
						dataretrieved.append(datafields[4])
	if name == "radius":
		data = send_string_and_wait_for_string(shell, "show run | i aaa group server radius\n", "#", False)
		dataline = data.splitlines()
		for line in dataline:
			if(re.search("aaa group server radius", line)):
				if(re.search(name, line)):
					datafields = line.split()
					if not datafields[2] == "|":
						dataretrieved.append(datafields[4])
	
	return(dataretrieved)

def get_cdp_neighbors(shell):
	dataretrieved = []

	data = send_string_and_wait_for_string(shell, "show cdp neighbors detail\n", "#", False)
	dataline = data.splitlines()
	for line in dataline:
		if(re.match("^Device ID", line)):
			dataretrieved.append(line.split()[2])
		if(re.match("^  IP address", line)):
			dataretrieved.append(line.split()[2])
		if(re.match("^Interface", line)):
			dataretrieved.append(line.split()[1])
			
	return(dataretrieved)

def get_trunks(shell):
	dataretrieved = []

	data = send_string_and_wait_for_string(shell, "show interfaces trunk | i trunking\n", "#", False)
	dataline = data.splitlines()
	for line in dataline:
		if(re.match("^Po", line)):
			dataretrieved.append(line)
		elif(re.match("^Gi", line)):
			dataretrieved.append(line)
		elif(re.match("^Fa", line)):
			dataretrieved.append(line)
			
	return(dataretrieved)
			
def get_hostname(shell):
	dataretrieved = ""
	
	data = send_string_and_wait_for_string(shell, "show run | i hostname\n", "#", False)
	dataline = data.splitlines()
	for line in dataline:	
		if(re.match("^hostname", line)):
			datafields = line.split()
			dataretrieved = datafields[1]
	
	return(dataretrieved)

def get_model(shell):
	dataretrieved = ""
	
	data = send_string_and_wait_for_string(shell, "show version\n", "#", False)
	dataline = data.splitlines()
	for line in dataline:	
		if(re.match("^Model number", line)):
			datafields = line.split()
			dataretrieved = datafields[3]

	return(dataretrieved)

def get_version(shell):
	dataretrieved = ""
	
	data = send_string_and_wait_for_string(shell, "show version\n", "#", False)
	dataline = data.splitlines()
	for line in dataline:	
		if(re.match("^\*", line)):
			datafields = line.split()
			dataretrieved = datafields[4]

	return(dataretrieved)
	
def get_bootimagefile(shell):
	dataretrieved = ""
	
	data = send_string_and_wait_for_string(shell, "show boot\n", "#", False)
	dataline = data.splitlines()
	for line in dataline:	
		if(re.match("^BOOT path-list", line)):
			datafields = line.split()
			dataretrieved = datafields[3]
	
	return(dataretrieved)
	
def get_flashimagefile(shell):
	dataretrieved = ""
	
	data = send_string_and_wait_for_string(shell, "show version\n", "#", False)
	dataline = data.splitlines()
	for line in dataline:	
		if(re.match("^System image file", line)):
			datafields = line.split()
			dataretrieved = datafields[4].strip('"')

	return(dataretrieved)

def get_serial(shell):
	dataretrieved = ""
	
	data = send_string_and_wait_for_string(shell, "show version\n", "#", False)
	dataline = data.splitlines()
	for line in dataline:	
		if(re.match("^System serial", line)):
			datafields = line.split()
			dataretrieved = datafields[4]
	
	return(dataretrieved)

def get_uptime(shell):
	dataretrieved = ""
	
	data = send_string_and_wait_for_string(shell, "show version\n", "#", False)
	dataline = data.splitlines()
	for line in dataline:	
		if(re.search("uptime", line)):
			dataretrieved = line
	
	return(dataretrieved)
	
def get_accesslists(shell, type):
	dataretrieved = []
	
	data = send_string_and_wait_for_string(shell, "show ip access-lists\n", "#", False)
	dataline = data.splitlines()
	for line in dataline:
		if(re.search("access list", line) and re.search(type, line)):
			datafields = line.split()			
			dataretrieved.append(datafields[4])
	
	return(dataretrieved)
	
def get_accesslist(shell, name):
	dataretrieved = []
	
	data = send_string_and_wait_for_string(shell, "show ip access-lists "+name+"\n", "#", False)
	dataline = data.splitlines()
	for line in dataline:
		if line[0] == ' ':
			dataretrieved.append(re.sub(r'\(.*?\)', '', line))

	return(dataretrieved)
	
def get_vlans(shell):
	dataretrieved = []
	
	data = send_string_and_wait_for_string(shell, "show vlan brief\n", "#", False)
	dataline = data.splitlines()
	for line in dataline:
		if(re.search("act", line)):
				datafields = line.split()			
				dataretrieved.append(datafields[0])
				dataretrieved.append(datafields[1])
	
	return(dataretrieved)
	
#def get_interface_list(shell, mode):
#	interfacelist = []
#	interfacemode = []
#	
#	if mode == "any":
#		data = send_string_and_wait_for_string(shell, "sh ip interface brief\n", "#", False)
#		dataline = data.split()
#		for line in dataline:
#			datafields = line.split()
#			if(re.match("^Gi", line) or re.match("^Te", line) or re.match("^Fa", line) or re.match("^Vl", line) or re.match("^Po", line)):
#				interfacelist.append(datafields[0])
#		return(interfacelist)
#		
#	else:
#		data = send_string_and_wait_for_string(shell, "sh ip interface brief\n", "#", False)
#		dataline = data.split()
#		for line in dataline:
#			datafields = line.split()
#			if(re.match("^Gi", line) or re.match("^Te", line) or re.match("^Fa", line) or re.match("^Vl", line) or re.match("^Po", line)):
#				interfacelist.append(datafields[0])
#		for line in interfacelist:
#			data = send_string_and_wait_for_string(shell, "show run interface " + line + " | i switchport mode\n", "#", False)
#			if(re.search(mode, data)):
#				dataline = data.split()
#				interfacemode.append(line)
#		return(interfacemode)
	
def set_default_interface(shell, interface):
	send_string_and_wait_for_string(shell, "conf t\n", "#", False)
	send_string_and_wait_for_string(shell, "default interface " + interface + "\n", "#", False)
	send_string_and_wait_for_string(shell, "end\n", "#", False)

def get_cdp_neighbor(shell, interface):
	nextdevice = {}
	isportchannel = 0
	
	if("Po" in interface):
		isportchannel = 1
	if(isportchannel==0):
		data = send_string_and_wait_for_string(shell, "show cdp neighbors " + interface + " detail\n", "#", False)
		dataline = data.splitlines()
		i = 0
		for line in dataline:
			if(re.match("^-", line)):
				i+=1
				nextdevice[i] = {}
			if(re.match("^Device ID", line)):
				nextdevice[i][0] = line.split()[2]
			if(re.match("^  IP address", line)):
				nextdevice[i][1] = line.split()[2]
			if(re.match("^Interface", line)):
				nextdevice[i][2] = line.split()[1]
			if(re.search("Switch", line)):
				nextdevice[i][3] = "1"
		
	#else:
	#	data = send_string_and_wait_for_string(shell, "show etherc summ\n", "#", False)
	#	dataline = data.splitlines()
	#	for line in dataline:
	#		if(re.search(interface, line)):
	#			entire = line.split()[3]
	#			sep = "("
	#			interface = entire.split(sep, 1)[0]
	#			data = send_string_and_wait_for_string(shell, "show cdp neighbors " + interface + " detail\n", "#", False)
	#			dataline = data.splitlines()
	#			for line in dataline:
	#				if(re.match("^Device ID", line)):
	#					nextdevice.append(line.split()[2])
	#				if(re.match("^  IP address", line)):
	#					nextdevice.append(line.split()[2])
	#				if(re.match("^Interface", line)):
	#					nextdevice.append(line.split()[1])
	#				if(re.search("Switch", line)):
	#					nextdevice.append("1")
	
	return(nextdevice)

def tracemac(shell, mac):
	interface = ""
	
	data = send_string_and_wait_for_string(shell, "show mac address-table address " + mac + "\n", "#", False)
	dataline = data.splitlines()
	for line in dataline:	
		if(re.search(mac, line)):
			datafields = line.split()
			interface = datafields[3]
	
	return(get_cdp_neighbor(shell, interface))
	
def get_macfromip(shell, ipadd):
	data = send_string_and_wait_for_string(shell, "show ip arp\n", "#", False)
	dataline = data.splitlines()
	for line in dataline:
		if(re.search(ipadd, line)):
			datafields = line.split()
			mac = datafields[3]
	return(mac)
