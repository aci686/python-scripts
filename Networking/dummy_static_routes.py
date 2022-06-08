#! /usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

# Simple script yo create dummy static ip routes (prefixes) to add to any lab router's routing table
# It creates around 650K routes

text_file = open("dummy_routes.txt", "w")
second_octet = 1
while second_octet <= 10:
  second = str(second_octet)
  third_octet = 1
  while third_octet <= 255:
    third = str(third_octet)
    last_octet = 1
    while last_octet <= 254:
      last=str(last_octet)
      text_file.write("ip route 10." + second + "." + third + "." + last + " 255.255.255.255 Null0\n")
      last_octet += 1
    third_octet += 1
  second_octet += 1
text_file.close()
