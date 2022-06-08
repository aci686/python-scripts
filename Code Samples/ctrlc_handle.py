#! /usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

#

import sys, signal
from time import sleep
from random import randrange
from pwn import *

def CTRL_C(sig, frame):
    print("\b\b\r[!] Exiting...\n")
    sys.exit(1)

signal.signal(signal.SIGINT, CTRL_C)

letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'O','P', 'Q', 'R', 'S','T', 'U', 'V', 'W', 'X', 'Y', 'Z']
p1 = log.progress("Reading letters")
p1.status("Starting lettes read")
sleep(2)
for i in range(len(letters)):
    p1.status("Current letter %s" % letters[i])
    sleep(randrange(3))
    print("Letter read: " + letters[i])
