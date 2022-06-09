#! /usr/bin/env python

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

import serial,sys,time,re,imp
from colorama import Fore,init,Style
from array import array

init()

READ_TIMEOUT=8

commands=[]

def read_serial(console):
	out = ""
	bytes_to_read =- 1
	while console.inWaiting() == 0:
		pass
	while bytes_to_read<console.inWaiting():
		bytes_to_read = console.inWaiting()
		out += console.read(bytes_to_read).decode()
		bytes_to_read = 0
		time.sleep(1)
	return out
		
def check_logged_in(console):
	console.write("\r\n\r\n".encode())
	time.sleep(1)
	prompt = read_serial(console)
	if ">" in prompt or "#" in prompt:
		return True
	else:
		return False
		
def login(console):
	login_status = check_logged_in(console)
	if login_status:
		send_command(console, cmd = "terminal length 0")
		print (Fore.BLUE + "[O]" + Fore.GREEN + " Already logged in")
		return None
	
	print ("[O] Login into device")
	while True:
		console.write("\r\n".encode())
		time.sleep(1)
		input_data = read_serial(console)
		if not "Username" in input_data:
			continue
		console.write(credentials.password + "\r\n")
		time.sleep(1)
		login_status = check_logged_in(console)
		if login_status:
			print ("[O] We are logged in\n")
			break

def logout(console, saveconfig="No"):
	print(Fore.BLUE + "[O]" + Fore.GREEN + " End configuration")
	send_command(console, cmd="end")
	if saveconfig == "Yes":
		print(Fore.BLUE + "[O]" + Fore.GREEN + " Saving configuration")
		send_command(console, cmd="copy run start")
	print (Fore.BLUE + "[O]" + Fore.GREEN + " Logging out from device")
	while check_logged_in(console):
		console.write("exit\r\n".encode())
		time.sleep(.5)
	print (Fore.BLUE + "[O]" + Fore.GREEN + " Successfully logged out from device")
	
def send_command(console, cmd="", returns="NO"):
	cmd = cmd + "\r\n"
	console.write(cmd.encode())
	time.sleep(1)
	if returns == "YES":
		return read_serial(console)
	else:
		return

def conf_section(console, section="", returns="NO"):
	print(Fore.YELLOW + "[C]" + Fore.GREEN + " Configuring ", end="", flush=True)
	for command in section:
		send_command(console, command)
		print(".")
	print("COMPLETED!")

def conf_section_banner(console):
	print(Fore.YELLOW + "[C]" + Fore.GREEN + " Configuring Banner",end="", flush=True)
	send_command(console, cmd="banner motd ^C")
	print(".",end="", flush=True)
	send_command(console, cmd="+----------------------------------------------------------------------------+")
	print(".",end="", flush=True)
	send_command(console, cmd="|                            WARNING                                         |")
	print(".",end="", flush=True)
	send_command(console, cmd="|     THE PROGRAMS AND DATA STORED ON THIS SYSTEM ARE LICENSED               |")
	print(".",end="", flush=True)
	send_command(console, cmd="|     TO OR ARE PRIVATE PROPERTY OF THIS COMPANY AND ARE LAWFULLY            |")
	print(".",end="", flush=True)
	send_command(console, cmd="|     AVAILABLE ONLY TO AUTHORIZED USERS FOR APPROVED PURPOSES.              |")
	print(".",end="", flush=True)
	send_command(console, cmd="|     UNAUTHORIZED ACCESS TO ANY PROGRAM OR DATA ON THIS SYSTEM IS           |")
	print(".",end="", flush=True)
	send_command(console, cmd="|     NOT PERMITTED, AND ANY UNAUTHORIZED ACCESS BEYOND THIS POINT           |")
	print(".",end="", flush=True)
	send_command(console, cmd="|     MAY LEAD TO PROSECUTION. THIS SYSTEM MAY BE MONITORED AT ANY           |")
	print(".",end="", flush=True)
	send_command(console, cmd="|     TIME FOR OPERATIONAL REASONS. THEREFORE, IF YOU ARE NOT AN             |")
	print(".",end="", flush=True)
	send_command(console, cmd="|     AUTHORIZED USER, DO NOT ATTEMPT TO LOG ON.                             |")
	print(".",end="", flush=True)
	send_command(console, cmd="|                                                                            |")
	print(".",end="", flush=True)
	send_command(console, cmd="|                            AVERTISSEMENT                                   |")
	print(".",end="", flush=True)
	send_command(console, cmd="|                                                                            |")
	print(".",end="", flush=True)
	send_command(console, cmd="|     LES PROGRAMMES ET LES DONNEES STOCKES DANS CE SYSTEME                  |")
	print(".",end="", flush=True)
	send_command(console, cmd="|     SONT VISES PAR UNE LICENCE OU SONT PROPRIETE PRIVEE DE CETTE           |")
	print(".",end="", flush=True)
	send_command(console, cmd="|     COMPAGNIE ET ILS NE SONT ACCESSIBLES LEGALEMENT QU'AUX                 |")
	print(".",end="", flush=True)
	send_command(console, cmd="|     USAGERS AUTORISES A DES FINS AUTORISEES. IL EST INTERDIT D'Y           |")
	print(".",end="", flush=True)
	send_command(console, cmd="|     ACCEDER SANS AUTORISATION, ET TOUT ACCES NON AUTORISE AU DELA          |")
	print(".",end="", flush=True)
	send_command(console, cmd="|     DE CE POINT PEUT ENTRAINER DES POURSUITES. LE SYSTEME PEUT EN          |")
	print(".",end="", flush=True)
	send_command(console, cmd="|     TOUT TEMPS FAIRE L'OBJET D'UNE SURVEILLANCE. SI VOUS N'ETES            |")
	print(".",end="", flush=True)
	send_command(console, cmd="|     PAS UN USAGER AUTORISE, N'ESSAYEZ PAS D'Y ACCEDER.                     |")
	print(".",end="", flush=True)
	send_command(console, cmd="+----------------------------------------------------------------------------+")
	print(".",end="", flush=True)
	send_command(console, cmd="^C")
	print(".")

def question(question="", options=[], defaultanswer=""):
	print(Fore.RED + "[I]" + Fore.GREEN + " " + question + "[", end="",flush=True)
	for option in options:
		if option == defaultanswer:
			print (Style.BRIGHT + option + Style.NORMAL + "/", end="",flush=True)
		else:
			print (option + "/", end="",flush=True)
	print("\b]? ", end="", flush=True)
	answer = input()
	if answer == "":
		answer=defaultanswer
	return answer

def question_section():
	del commands[:]
	configfile="config.txt"
	location=question("Which site will this device be in ", ["L","T","N", "None"], "None")
	if configfile:
		with open(configfile) as input_data:
			for line in input_data:
				if line.split(" = ")[0] == "common":
					if not line.split(" = ")[1].startswith("#"):
						commands.append(line.split(" = ")[1].strip("\n"))
					else:
						answer = question(line.split(" = ")[1].strip("\n").strip("#") + " ", [""], "")
						if answer:
							commands.append(line.split(" = ")[1].strip("\n").strip("#") + " " + answer)
				if line.split(" = ")[0] == location:
					if not line.split(" = ")[1].startswith("#"):
						commands.append(line.split(" = ")[1].strip("\n"))
					else:
						answer = question(line.split(" = ")[1].strip("\n").strip("#") + " ", [""], "")
						if answer:
							commands.append(line.split(" = ")[1].strip("\n").strip("#") + " " + answer)
	
	uplinkports = question("Configure uplink ", ["Yes", "No"], "No")
	if uplinkports == "Yes":
		ethercmembers = question("Uplink interfaces (comma separated) ", [""], "")
		uplinkdevice = question("Hostname of the uplink device ", [""], "")
		uplinkvlan = question("Native VLAN# of the ports ", [""], "")
		commands.append("interface Po1")
		commands.append("switchport mode trunk")
		commands.append("ip dhcp snooping trust")
		if uplinkdevice:
			commands.append("description " + uplinkdevice)
		if uplinkvlan:
			commands.append("switchport trunk native vlan " + uplinkvlan)
		commands.append("no shutdown")
		if ethercmembers:
			commands.append("interface range " + ethercmembers)
			commands.append("switchport mode trunk")
			commands.append("ip dhcp snooping trust")
			commands.append("channel-group 1 mode on")
			if uplinkvlan:
				commands.append("switchport trunk native vlan " + uplinkvlan)
			commands.append("no shutdown")
			
	apports = question("Configure Access point interfaces ", ["Yes", "No"], "No")
	if apports == "Yes":
		apinterfaces = question("Access point interfaces (comma separated) ", [""], "")
		apvlan = question("Native VLAN# of the ports ", ["21"], "21")
		if apinterfaces:
			commands.append("interface range " + apinterfaces)
			commands.append("description AP Port")
			commands.append("switchport mode trunk")
			commands.append("switchport trunk native vlan " +  apvlan)
	
	dataports = question("Configure Access interfaces ", ["Yes", "No"], "No")
	if dataports == "Yes":
		datainterfaces = question("Access port interfaces (comma separated) ", [""], "")
		if datainterfaces:
			failovervlan = question("Failover VLAN# ", ["999"], "999")
			voicevlan = question("Voice VLAN# ", ["51"], "51")
			guestvlan = question("Guest VLAN# ", ["141"], "141")
			commands.append("interface range " + datainterfaces)
			commands.append("description Access Port")
			commands.append("switchport access vlan " + failovervlan)
			commands.append("switchport mode access")
			commands.append("switchport block unicast")
			commands.append("switchport voice vlan " + voicevlan)
			commands.append("ip arp inspection limit rate 5")
			if location == "L":
				commands.append("ip access-group PreAuth_Traffic in")
			if location == "T":
				commands.append("ip access-group PreAuth_Traffic in")
			if location == "N":
				commands.append("ip access-group PreAuth_Traffic in")
			commands.append("authentication event fail action next-method")
			commands.append("authentication event server dead action reinitialize vlan " + guestvlan)
			commands.append("authentication event server dead action authorize voice")
			commands.append("authentication event no-response action authorize vlan " + guestvlan)
			commands.append("authentication event server alive action reinitialize")
			commands.append("authentication host-mode multi-domain")
			commands.append("authentication order dot1x mab")
			commands.append("authentication priority dot1x mab")
			commands.append("authentication port-control auto")
			commands.append("authentication periodic")
			commands.append("authentication timer reauthenticate server")
			commands.append("authentication violation restrict")
			commands.append("mab")
			commands.append("snmp trap mac-notification change added")
			commands.append("mls qos trust cos")
			commands.append("dot1x pae authenticator")
			commands.append("spanning-tree portfast")
			commands.append("spanning-tree bpduguard enable")
			commands.append("spanning-tree guard root")
			commands.append("ip dhcp snooping limit rate 50")
			commands.append("no shutdown")

	return question("Is the information correct ", ["Yes", "No"], "Yes")
	
	
def main():
	print(Fore.RED + "[I]" + Fore.GREEN + " Serial Port [COM1]?",end="", flush=True)
	sp = input(" ")
	if not sp:
		sp = "COM1"
	correct = "No"
	while correct != "Yes":
		correct = question_section()
	
	print (Fore.BLUE + "[O]" + Fore.GREEN + " Initializing serial connection")
	console = serial.Serial(
        port=sp,
        baudrate=9600,
        parity="N",
        stopbits=1,
        bytesize=8,
        timeout=READ_TIMEOUT
    )
	if not console.isOpen():
		sys.exit()
	print(Fore.BLUE + "[O]" + Fore.GREEN + " Serial connection ready")
	login(console)
	print(Fore.BLUE + "[O]" + Fore.GREEN + " Entering configuration mode")
	send_command(console, cmd="enable")
	print(Fore.YELLOW + "[C]" + Fore.GREEN + " Erasing startup configuration",end="", flush=True)
	send_command(console, cmd="erase startup-config")
	print(".",end="", flush=True)
	send_command(console, cmd="\r\n\r\n\r\n")
	send_command(console, cmd="conf t")
	print(".")
	conf_section(commands)
	print(Fore.RED + "[I]" + Fore.GREEN + " Save configuration [Yes/" + Style.BRIGHT + "No" + Style.NORMAL + "]?",end="", flush=True)
	saveconfig = input(" ")
	if saveconfig == "Yes":
		logout(console, saveconfig)
	else:
		logout(console)	
	
if __name__ == "__main__":
    main()