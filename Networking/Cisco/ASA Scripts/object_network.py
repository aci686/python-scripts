#!/usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

import ipaddress

#
# Network Object Class
#
# Usage example:
#
# print(object_network("10.1.100.10"))
#     object network HOST_10.1.100.10
#      host 10.1.100.10
# 
# print(object_network("87.198.212.34 255.255.255.255"))
#     object network HOST_87.198.212.34
#      host 87.198.212.34
#
# print(object_network("172.31.255.11 netmask 255.255.255.255"))
#     object network HOST_172.31.255.11
#      host 172.31.255.11
#
# print(object_network("57.8.81.0 255.255.255.0"))
#     object network SUBNET_57.8.81.0-24
#      subnet 57.8.81.0 255.255.255.0
# 
# print(object_network("10.70.204.27 255.255.255.0"))
#     There was an error creating this object: 10.70.204.27 255.255.255.0
# 
# print(object_network("host 172.16.220.21"))
#     There was an error creating this object: host 172.16.220.21
# 
# print(object_network("172.16.225.0 netmask 255.255.255.0"))
#     object network SUBNET_172.16.225.0-24
#      subnet 172.16.225.0 255.255.255.0
# 
# print(object_network("172.16.221.21 netmask 255.255.255.0"))
#     There was an error creating this object: 172.16.221.21 netmask 255.255.255.0

class object_network:
    def __init__(self, line):
        if len(line.split(' ')) == 1:
            try:
                ipaddress.IPv4Network(line + '/32')
                self.type = 'host'
                self.name = self.type.upper() + '_' + line
                self.ip_address = line
                self.netmask = ''
            except (ValueError):
                self.type = 'ERROR'
                self.name = line
        if len(line.split(' ')) == 2 or len(line.split(' ')) == 3:
            try:
                ipaddress.IPv4Network(line.split(' ')[0] + '/' + line.split(' ')[-1])
                if line.split(' ')[-1] == '255.255.255.255':
                    self.type = 'host'
                    self.name = self.type.upper() + '_' + str(ipaddress.IPv4Interface(line.split(' ')[0]+'/'+line.split(' ')[-1])).split('/')[0]
                    self.ip_address = line.split(' ')[0]
                    self.netmask = line.split(' ')[-1]
                else:
                    self.type = 'subnet'
                    self.name = self.type.upper() + '_' + str(ipaddress.IPv4Interface(line.split(' ')[0]+'/'+line.split(' ')[-1])).replace('/', '-')
                    self.ip_address = line.split(' ')[0]
                    self.netmask = line.split(' ')[-1]
            except (ValueError):                
                self.type = 'ERROR'
                self.name = 'There was an error creating this object: ' + line

    def __str__(self):
        if not self.type == 'ERROR':
            if self.type == 'host':
                return 'object network %s\n %s %s' % (self.name, self.type, self.ip_address)
            else:
                return 'object network %s\n %s %s %s' % (self.name, self.type, self.ip_address, self.netmask)
        else:
            return '%s' % (self.name)