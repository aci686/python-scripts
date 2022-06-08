#! /usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

#

import paramiko, getpass, base64, time, io, code, re, csv, sys, argparse, os, logging, datetime, pymssql

def send_string_and_wait_for_string(command, wait_string, should_print):
    shell.send(command)
    receive_buffer = ""

    while not wait_string in receive_buffer:		
        receive_buffer += shell.recv(1024).decode()
    if should_print:
        print(receive_buffer)

    return(receive_buffer)
	
def write_data_to_csv(ipaddress, timestamp, xcoord, ycoord):
	with open(args.output, "a", newline ="") as csvfile:
		writer = csv.writer(csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
		writer.writerow([ipaddress, timestamp, xcoord, ycoord])
	return(True)
	
def write_data_to_sql(timestamp, name, ipadd, xcoord, ycoord):
	conn = mymssql.connect(dbserver, dbuser, dbpassword, database)
	cursor = conn.cursor()
	cursor.execute("", ())
	conn.commit()

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
parser = argparse.ArgumentParser()
parser.add_argument("--input", help="csv input filename", type=str, required=True)
parser.add_argument("--user", help="username to log on", type=str, required=True)
group1 = parser.add_mutually_exclusive_group(required=True)
group1.add_argument("--output-csv", help="csv output filename", type=str)
group1.add_argument("--output-sql", help="sql output connection string", type=str)
args = parser.parse_args()

print("\nInput csv filename: " + args.input)
if args.output-csv:
	outputfilename = args.output
	print("Output csv filename: " + outputfilename)
else:
	outputfilename = "coordinates.csv"
	print("Output csv filename: " + outputfilename)
if args.output-sql:
	print("Using SQL DB")
else:
	print("Using SQL DB")
	
print("Using username: " + args.user)
password = getpass.getpass()

ipaddress = [lines.rstrip("\n") for lines in open(args.input)]
for ipadd in ipaddress:
	try:
		print("[" + ipadd + "]")
		client.connect(ipadd, username=args.user, password=password, timeout=10)
		shell = client.invoke_shell()
		send_string_and_wait_for_string("", "#", False)
		data = send_string_and_wait_for_string("cat /proc/sys/dev/ubnt_poll/gps_info\n", "#", False)
		dataline = data.splitlines()
		for line in dataline:
			if not line.startswith ("cat"):
				if not line.startswith ("XW"):
					datafields = line.split(",")
					xcoord = datafields[6]
					ycoord = datafields[7]
					print("X: " + xcoord + " " + "Y: " + ycoord)
					write_data_to_csv(ipadd, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), xcoord, ycoord)				
		client.close()
	except:
		print("Connection error")
	
if __name__ == "__main__":
	args = parser.parse_args()
	