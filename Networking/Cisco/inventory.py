#! /usr/bin/env python

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

# This program reads sourcedata.txt ip addresses and gets basic information of the 
# devices like hostname, ip address, model serial number and version

import paramiko, getpass, base64, time, io, code, re, csv, sys, argparse, os, logging, nbcml, pymssql
from netaddr import *

def write_data_to_csv(hostname, ipaddress, model, version):
	with open("basic_inventory.csv", "a", newline ="") as csvfile:
		writer = csv.writer(csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
		writer.writerow([hostname, ipaddress, model, version])
	return True
	
def write_basic_data_to_sql(hostname, ipaddress, model, serial, version):
	conn = pymssql.connect(dbserver, dbuser, dbpassword, database)
	cursor = conn.cursor()
	cursor.execute("INSERT INTO devices (dev_hostname, dev_ip_address, dev_model, dev_serial) VALUES (%s, %s, %s, %s)", (hostname, ipaddress, model, serial, version))
	conn.commit()
	
def get_int_status(status):
	conn = pymssql.connect(dbserver, dbuser, dbpassword, database)
	cursor = conn.cursor()
	cursor.execute("SELECT ifst_id FROM ifstatus WHERE ifst_description=%s", status)
	row = cursor.fetchone()
	conn.close()

	return(row[0])
	
def write_interface_data_to_sql(device, shell, interfacename):
	status = ""
	
	interdata = nbcml.get_interface_data(shell, interfacename)
	status = get_int_status(interdata[0])
	conn = pymssql.connect(dbserver, dbuser, dbpassword, database)
	cursor = conn.cursor()
	cursor.execute("INSERT INTO interfaces (if_dev, if_name, if_status, if_haddr, if_mtu, if_bandwidth) VALUES (%s, %s, %s, %s, %s, %s)", (device, interfacename, status, interdata[1], interdata[2], interdata[3]))
	conn.commit()
	conn.close()
	
def device_exist(device):
	conn = pymssql.connect(dbserver, dbuser, dbpassword, database)
	cursor = conn.cursor()
	cursor.execute("SELECT dev_id FROM devices WHERE dev_serial=%s", nbcml.get_serial(device))
	row = cursor.fetchone()
	
	return(row)
	
def interface_exist(device, interface):
	conn = pymssql.connect(dbserver, dbuser, dbpassword, database)
	cursor = conn.cursor()
	cursor.execute("SELECT if_id, if_dev, if_name FROM interfaces WHERE if_dev=%s AND if_name=%s",(device,interface))
	row = cursor.fetchone()
	
	return(row)	

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
dbserver = ""
dbuser = ""
dbpassword = ""

parser = argparse.ArgumentParser()
group1=parser.add_mutually_exclusive_group(required=True)
group1.add_argument("--range", help="ip address range to check", type=str)
group1.add_argument("--device", help="device ip address to check", type=str)
group2=parser.add_mutually_exclusive_group(required=True)
group2.add_argument("--init", help="create blank database", type=str)
group2.add_argument("--database", help="database to be used", type=str)
parser.add_argument("--user", help="username to log on", type=str, required=True)

args = parser.parse_args()

if args.database:
	database = args.database
if args.init:
	try:
		conn = pymssql.connect(dbserver, dbuser, dbpassword)
		conn.autocommit(True)
		cursor = conn.cursor()
		cursor.execute("CREATE DATABASE " + args.init)
		conn.autocommit(False)
		cursor.execute("USE " + args.init)
		conn.commit()
		cursor.execute("CREATE TABLE [dbo].[devices]([dev_id] [int] IDENTITY(1,1) NOT NULL,[dev_hostname] [varchar](100) NULL,[dev_ip_address] [varchar](50) NULL,[dev_model] [varchar](50) NULL,[dev_serial] [varchar](50) NULL,[dev_timestamp] [datetime2](7) DEFAULT GETDATE()) ON [PRIMARY]")
		conn.commit()
		cursor.execute("CREATE TABLE [dbo].[interfaces]([if_id] [int] IDENTITY(1,1) NOT NULL,[if_dev] [int] NULL,[if_name] [nvarchar](100) NULL,[if_status] [int] NULL,[if_haddr] [nvarchar](50) NULL,[if_mtu] [int] NULL,	[if_bandwidth] [int] NULL,[if_timestamp] [datetime] DEFAULT GETDATE()) ON [PRIMARY]")
		conn.commit()
		conn.close()
	except:
		print("Error while accessing/creating/initializing database " + args.init)
		exit()
else:
	if args.user:
		devusername = args.user
		devpassword = getpass.getpass()
	if args.range:
		iplist = IPNetwork(args.range)
		for ipaddress in iplist.iter_hosts():
			ipadd=str(ipaddress)
			print("[DEV] Connecting to " + ipadd)
			try:
				client.connect(ipadd, username=devusername, password=devpassword, timeout=10)
				shell = client.invoke_shell()
				nbcml.send_string_and_wait_for_string(shell, "", "#", False)
				nbcml.send_string_and_wait_for_string(shell, "terminal length 0\n", "#", False)
				print("[" + ipadd + "] Retrieving data...")
				thisdevice = device_exist(shell)
				if not thisdevice:
					write_basic_data_to_sql(nbcml.get_hostname(shell),nbcml.get_mgmt_ipaddress(shell,"Vlan11"),nbcml.get_model(shell),nbcml.get_serial(shell),nbcml.get_version(shell))
				interfaces = nbcml.get_interface_list(shell, "any")
				thisdevice = device_exist(shell)
				for line in interfaces:
					if not interface_exist(thisdevice[0], line):
						write_interface_data_to_sql(thisdevice[0], shell, line)
				client.close()
			except:
				print("[DEV] Connection error")
				continue
	if args.device:
		ipadd = args.device
		print("[DEV] Connecting to " + ipadd)
		try:
			client.connect(ipadd, username=devusername, password=devpassword, timeout=10)
			shell = client.invoke_shell()
			nbcml.send_string_and_wait_for_string(shell, "", "#", False)
			nbcml.send_string_and_wait_for_string(shell, "terminal length 0\n", "#", False)
			print("[" + ipadd + "] Retrieving data...")
			thisdevice = device_exist(shell)
			if not thisdevice:
				write_basic_data_to_sql(nbcml.get_hostname(shell),nbcml.get_mgmt_ipaddress(shell,"Vlan11"),nbcml.get_model(shell),nbcml.get_serial(shell),nbcml.get_version(shell))
			interfaces = nbcml.get_interface_list(shell, "any")
			thisdevice = device_exist(shell)
			for line in interfaces:
				if not interface_exist(thisdevice[0], line):
					write_interface_data_to_sql(thisdevice[0], shell, line)
			client.close()
		except:
			print("[DEV] Connection error")
		
if __name__ == "__main__":
	args = parser.parse_args()