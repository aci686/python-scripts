#!/usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

import ipaddress, re
from object_network import object_network

#
# Network Group Object Class
#
# Usage example:
#
# test_group = object_group_network("Test_Group")
# print(test_group)
#     object-group network Test_Group
#
# test_group = object_group_network("Test_Group")
# test_group.add_object_network(object_network("172.16.225.1 netmask 255.255.255.255"))
# print(test_group)
#     object-group network Test_Group
#      network-object object HOST_172.16.225.1
#
# test_group = object_group_network("Test_Group")
# test_group.add_object_network("192.168.1.0 255.255.255.0")
# print(test_group)
#     object-group network Test_Group
#      network-object object SUBNET_192.168.1.0-24

class object_group_network:
    def __init__(self, line):
        self.name = line
        self.network_objects = []

    def add_object_network(self, line):
        if isinstance(line, str):
            self.network_objects.append(object_network(line))
        elif isinstance(line, object_network):
            self.network_objects.append(line)

    def __str__(self):
        output = 'object-group network %s' % (self.name)
        if self.network_objects:
            for _ in self.network_objects:
                if re.search('error', _.name):
                    output = 'There was an error creating this object: ' + self.name
                else:
                    if _.type == 'host' or _.type == 'subnet':
                        output = output + '\n network-object object %s' % (_.name)
                                       
        return output

test_group = object_group_network('Test_Group')
test_group.add_object_network(object_network('172.16.225.1 netmask 255.255.255.255'))
print(test_group)
test_group.add_object_network('192.168.1.0 255.255.255.0')
print(test_group)