#! /usr/bin/env python

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

# This program does parse a given ASA configuration and audits different objects configured.
# It also suggests when objects are not explictly defined
#
# usage: object_parse_audit.py -i INPUT [-h]
#
# arguments:
#   -i INPUT, --input INPUT input file containing ASA configuration to parse
#
# optional arguments:
#   -h, --help              show this help message and exit

import argparse, ipaddress
from ciscoconfparse import CiscoConfParse

parser = argparse.ArgumentParser()
parser._action_groups.pop()
required=parser.add_argument_group('required arguments')
required.add_argument("-i", "--input", help = "input file configuration", type = str, required = True)

# Find all dictionary keys containing the specified value
def getKeysByValue(dictOfElements, valueToFind):
    listOfKeys = list()
    listOfItems = dictOfElements.items()
    for item  in listOfItems:
        if item[1] == valueToFind:
            listOfKeys.append(item[0])
    return  listOfKeys

# Returns a dictionary with all the object network containing hosts defined in the config
# {'OBJECT NAME': 'OBJECT_VALUE'}
# IE
# {'SOURCE_L2L_1': '10.1.100.10', 'SOURCE_MAPPED_L2L_1': '10.173.3.10', 'SOURCE_L2L_2': '172.17.30.13'}
def get_object_host_list(config_file):
    hosts = {}

    configured_objects_network = config.find_objects(r"^object network ")
    for configured_object_network in configured_objects_network: 
        for configured_object_network_children in configured_object_network.children:
            if configured_object_network_children.text.startswith(" host"):
                hosts[configured_object_network.text.split("object network ")[1]] = configured_object_network_children.text.split(" host ")[1]
    
    return(hosts)

# Returns a dictionary with all the object network containing subnets defined in the config
# {'OBJECT NAME': 'OBJECT_VALUE'}
# IE
# {'DESTINATION_L2L_57': '57.8.81.0 255.255.255.0', 'DESTINATION_L2L_L12': '172.31.255.0 255.255.255.0', 'NAT_EXEMPT_SRC': '10.70.172.0 255.255.254.0'}
def get_object_subnet_list(config_file):
    subnets = {}

    configured_objects_network = config.find_objects(r"^object network ")
    for configured_object_network in configured_objects_network: 
        for configured_object_network_children in configured_object_network.children:
            if configured_object_network_children.text.startswith(" subnet"):
                subnets[configured_object_network.text.split("object network ")[1]] = configured_object_network_children.text.split(" subnet ")[1]
    
    return(subnets)

# Returns a dictionary with all the object-group network defined in the config
# {'OBJECT NAME': ['OBJECT_VALUE_1', 'OBJECT_VALUE_2']}
# IE
# {'VPN_Client_Local_LAN_Default': ['host 0.0.0.0'], 'esb_local_subnets_Coolkeeragh': ['10.70.172.0 255.255.254.0', '10.70.174.0 255.255.254.0']}
def get_object_group_list(config_file):
    object_groups = {}

    configured_objects_group = config.find_objects(r"^object-group network ")
    for configured_object_group in configured_objects_group:
        network_objects = []
        for configured_object_group_children in configured_object_group.children:
            if configured_object_group_children.text.startswith(" network-object "):
                network_objects.append(configured_object_group_children.text.split(" network-object ")[1])
        if network_objects:
            object_groups[configured_object_group.text.split("object-group network ")[1]] = network_objects

    return(object_groups)

args=parser.parse_args()
if args.input:
    try:
        host_objects = {}
        subnet_objects = {}
        group_objects = {}

        # Parse and populate dictionaries
        config = CiscoConfParse(args.input)
        host_objects = get_object_host_list(config)
        subnet_objects = get_object_subnet_list(config)
        group_objects = get_object_group_list(config)

        # Look for object-group network entries
        for (key, value) in group_objects.items():
            print("GROUP: " + key)
            for entry in value:
                # Look for all the entries whithin
                if entry.startswith("object "):
                    # If it is defined in object network host dictionary
                    if entry.split("object ")[1] in host_objects.keys():
                        print("\tHOST: " + entry.split("object ")[1])
                        print("\t\t" + host_objects[entry.split("object ")[1]])
                    # If it is defined in object network subnet dictionary
                    if entry.split("object ")[1] in subnet_objects.keys():
                        print("\tSUBNET: " + entry.split("object ")[1])
                        print("\t\t" + subnet_objects[entry.split("object ")[1]])
                else:
                    if "host " in entry:
                        # If this entry exists in object network hosts but not used
                        # Suggest adding the defined object network host
                        # IE
                        # 10.70.203.24 IS DEFINED IN: SOURCE_L2L_10
		                # SUGGESTED FIX:
		                # 	conf t
		                # 	object-group network paypoint_local
		                # 	no network-object host 10.70.203.24
		                # 	network-object object SOURCE_L2L_10
		                # 	exit
                        if entry.split("host ")[1] in host_objects.values():
                            for ekey in getKeysByValue(host_objects, entry.split("host ")[1]):
                                print("\t" + entry.split("host ")[1] + " IS DEFINED IN: " + ekey)
                                print("\t\tSUGGESTED FIX:")
                                print("\t\t\tconf t")
                                print("\t\t\tobject-group network " + key)
                                print("\t\t\tno network-object " + entry)
                                print("\t\t\tnetwork-object object " + ekey)
                                print("\t\t\texit")
                        # If it is not in object network hosts
                        # Suggest creation of a new one and use it in the object-group network
                        # IE
                        # 57.8.81.113 IS NOT DEFINED AS OBJECT
		                # SUGGESTED FIX:
		                # 	conf t
		                # 	object network HOST_57.8.81.113
		                # 	host 57.8.81.113
		                # 	exit
		                # 	object-group network galileo_remote
		                # 	no network-object host 57.8.81.113
		                # 	network-object object HOST_57.8.81.113
		                # 	exit 
                        else:
                            print("\t" + entry.split("host ")[1] + " IS NOT DEFINED AS OBJECT")
                            print("\t\tSUGGESTED FIX:")
                            print("\t\t\tconf t")
                            print("\t\t\tobject network HOST_" + entry.split("host ")[1])
                            print("\t\t\thost " + entry.split("host ")[1])
                            print("\t\t\texit")
                            print("\t\t\tobject-group network " + key)
                            print("\t\t\tno network-object " + entry)
                            print("\t\t\tnetwork-object object HOST_" + entry.split("host ")[1])
                            print("\t\t\texit")
                    else:
                        # If this entry exists in object network subnets but not used
                        # Suggest adding the defined object network host
                        # IE
                        # 10.70.229.0 255.255.255.0 IS DEFINED IN: Net_10.70.229.0
		                # SUGGESTED FIX:
		                # 	conf t
		                # 	object-group network Junifer_local
		                # 	no network-object 10.70.229.0 255.255.255.0
		                # 	network-object object Net_10.70.229.0
		                # 	exit
                        if entry in subnet_objects.values():
                            for ekey in getKeysByValue(subnet_objects, entry):
                                print("\t" + entry + " IS DEFINED IN: " + ekey)
                                print("\t\tSUGGESTED FIX:")
                                print("\t\t\tconf t")
                                print("\t\t\tobject-group network " + key)
                                print("\t\t\tno network-object " + entry)
                                print("\t\t\tnetwork-object object " + ekey)
                                print("\t\t\texit")
                        # If it is not in object network subnets
                        # Suggest creation of a new one and use it in the object-group network
                        # IE
                        # 10.80.26.0 255.255.255.0 IS NOT DEFINED AS OBJECT
		                # SUGGESTED FIX:
		                # 	conf t
		                # 	object network NET_10.80.26.0_24
		                # 	subnet 10.80.26.0 255.255.255.0
		                # 	exit
		                # 	object-group network Junifer_local
		                # 	no network-object 10.80.26.0 255.255.255.0
		                # 	network-object object NET_10.80.26.0_24
		                # 	exit
                        else:
                            print("\t" + entry + " IS NOT DEFINED AS OBJECT")
                            print("\t\tSUGGESTED FIX:")
                            print("\t\t\tconf t")
                            # Convert netmask to cidr
                            # IE
                            # 255.255.192.0 to 18
                            mask = entry.split(" ")
                            mask[1] = sum([bin(int(x)).count('1') for x in mask[1].split('.')])
                            print("\t\t\tobject network NET_" + mask[0] + "_" + str(mask[1]))
                            print("\t\t\tsubnet " + entry)
                            print("\t\t\texit")
                            print("\t\t\tobject-group network " + key)
                            print("\t\t\tno network-object " + entry)
                            print("\t\t\tnetwork-object object NET_" + mask[0] + "_" + str(mask[1]))
                            print("\t\t\texit")

    except EnvironmentError as e:
            print(str(e))