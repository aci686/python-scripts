#! /usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

#

import paramiko, getpass, base64, time, io, code, re, csv, sys, argparse, os, logging, datetime, pymssql, _mssql, decimal

def send_string_and_wait_for_string(command, wait_string, should_print):
    shell.send(command)
    receive_buffer = ""

    while not wait_string in receive_buffer:		
        receive_buffer += shell.recv(1024).decode()
    if should_print:
        print(receive_buffer)

    return receive_buffer
	
def write_data_to_sql(assetid, timestamp, xcoord, ycoord):
	conn = pymssql.connect(dbserver, dbuser, dbpassword, database)
	cursor = conn.cursor()
	cursor.execute("INSERT into PositionHistory (asset_id, timestamp, latitude, longitude) VALUES (%s, %s, %s, %s)", (assetid, timestamp, xcoord, ycoord))
	conn.commit ()

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

rocketuser = ""
rocketpass = ""
dbserver = ""
dbuser = ""
dbpassword = ""
database = ""
assets = []

print("Rocket username: " + rocketuser)
print("Output csv filename: " + outputfilename)
print("SQL username: " + dbuser)
print("Output SQL DataBase: " + dbserver + "\\" + database)

conn = pymssql.connect(dbserver, dbuser, dbpassword, database)
cursor = conn.cursor()
cursor.execute("SELECT Asset_id, Asset_Name, IP_Address FROM Assets")
for row in cursor:
	try:
		print("[" + row[1] + "]")
		client.connect(row[2], username=rocketuser, password=rocketpass, timeout=5)
		shell = client.invoke_shell()
		send_string_and_wait_for_string("", "#", False)
		data = send_string_and_wait_for_string("cat /proc/sys/dev/ubnt_poll/gps_info\n", "#", False)
		dataline = data.splitlines()
		for line in dataline:
			if not line.startswith("cat"):
				if not line.startswith("XW"):
					datafields = line.split(",")
					xcoord = datafields[6]
					ycoord = datafields[7]
					print("X: " + xcoord + " " + "Y: " + ycoord)
					write_data_to_csv(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), row[2], row[1], xcoord, ycoord)				
					write_data_to_sql(row[0], datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), xcoord, ycoord)
		client.close()
	except:
		print("Connection error")
	
conn.commit()
