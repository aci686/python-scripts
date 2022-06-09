#! /usr/bin/env python

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

import paramiko, getpass, base64, time, io, code, re, csv, sys, argparse, os, logging, nbcml
from netaddr import *

global ipadd
global shell

#class multifile(object):
#    def __init__(self, files):
#        self._files = files
#    def __getattr__(self, attr, *args):
#        return self._wrap(attr, *args)
#    def _wrap (self, attr, *args):
#        def g (*a, **kw):
#            for f in self._files:
#                res = getattr (f, attr, *args)(*a, **kw)
#            return res
#        return g

client = paramiko.SSHClient ()
client.load_system_host_keys ()
client.set_missing_host_key_policy (paramiko.AutoAddPolicy ())

parser = argparse.ArgumentParser()
parser.add_argument ("--user", help="username to log on", type=str)
#parser.add_argument ("--output", help="output log file", type=str)
group1=parser.add_mutually_exclusive_group(required=True)
group1.add_argument ("--device", help="network device", type=str)
#group1.add_argument ("--range", help="network device range", type=str)

args = parser.parse_args()
if args.user:
	username = args.user
	password = getpass.getpass()
else:
	print ("\n\nNo username found. Please add the right option to the command line.")
	exit ()
#if args.output:
#	sys.stdout = multifile ([ sys.stdout, open(args.output, 'w') ])
if args.device:
	ipadd=args.device
	try:
		startTime=time.time()
		print("[DEV] Connecting to " + ipadd)
		client.connect (ipadd, username=username, password=password, timeout=10)
		shell = client.invoke_shell ()
		nbcml.start_prep_connection (shell)
		
		print (nbcml.get_servergroups (shell, RADIUS))
		
		client.close ()
		print ('[TIME] {0} seconds'.format(time.time() - startTime))
	except:
		print ("[DEV] Connection error")

#if args.range:
#	iplist = IPNetwork(args.range)
#	for ipaddress in iplist.iter_hosts():
#		ipadd=str(ipaddress)
#		try:
#			print("[DEV] Connecting to " + ipadd)
#			client.connect (ipadd, username=username, password=password, timeout=10)
#			shell = client.invoke_shell ()
#			nbcml.start_prep_connection (shell)
#			
#			print (nbcml.get_trunks (shell))
#						
#			client.close ()
#		except:
#			print ("[DEV] Connection error")

if __name__ == "__main__":
	args = parser.parse_args()