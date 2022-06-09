#! /usr/bin/env python

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

# This program does parse a given ASA configuration and audits different translations configured.
# It also suggests when objects are not explictly defined
#
# usage: pix_to_asa.py -i INPUT [-h]
#
# arguments:
#   -i INPUT, --input INPUT input file containing PIX configuration to parse
#
#  optional arguments:
#   -h, --help              show this help message and exit

import argparse, ipaddress
import re
from ciscoconfparse import CiscoConfParse

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

parser = argparse.ArgumentParser()
parser._action_groups.pop()
required = parser.add_argument_group('required arguments')
required.add_argument("-i", "--input", help = "input file configuration (source PIX config)", type = str, required = True)

class network_object:
    def __init__(self, line):      
        if len(line.split(" ")) == 1:
            self.type = "host"
            self.name = "HOST_" + line + "-32"
            self.ip_address = line
            self.netmask = "255.255.255.255"
            self.content = ""
            try:
                ipaddress.IPv4Address(line)
                self.content = " host " + line
            except (ValueError):
                self.content = ""
        elif len(line.split(" ")) == 2 or len(line.split(" ")) == 3:
            if line.split(" ")[-1] == "255.255.255.255":
                self.type = "host"
                self.name = "HOST_" + str(ipaddress.IPv4Interface(line.split(" ")[0])).replace("/", "-")
                self.ip_address = line.split(" ")[0]
                self.netmask = line.split(" ")[-1]
                self.content = " host " + self.ip_address
            else:
                self.type = "network"
                self.name = "SUBNET_" + str(ipaddress.IPv4Interface(line.split(" ")[0] + "/" + line.split(" ")[-1])).replace("/", "-")
                self.ip_address = line.split(" ")[0]
                self.netmask = line.split(" ")[-1]
                self.content = " subnet " + self.ip_address + " " + self.netmask
        else:
            print(bcolors.FAIL + "UNEXPECTED NETWORK OBJECT!" + bcolors.ENDC)

    def printme(self):
        print("object network " + self.name)
        if self.content:
            print(self.content)

class access_list:
    def __init__(self, line):
        self.name = line.split(" ")[1]
        if line.split(" ")[2] == "standard":
            if line.split(" ")[4] == "host":
                self.source = network_object(line.split(" ")[5])
            else:
                self.source = network_object(line.split(" ")[4] + " " + line.split(" ")[5])
            self.destination = ""
        elif line.split(" ")[2] == "extended":
            if line.split(" ")[5] == "host":
                self.source = network_object(line.split(" ")[6])
            elif line.split(" ")[5] == "object":
                self.source = line.split(" ")[6]
            elif line.split(" ")[5] == "object-group":
                self.source = line.split(" ")[6]
            else:
                self.source = network_object(line.split(" ")[5] + " " + line.split(" ")[6])

            if line.split(" ")[7] == "host":
                self.destination = network_object(line.split(" ")[8])
            elif line.split(" ")[7] == "object":
                self.destination = line.split(" ")[8]
            elif line.split(" ")[7] == "object-group":
                self.destination = line.split(" ")[8]
            else:
                self.destination = network_object(line.split(" ")[7] + " " + line.split(" ")[8])
        else:
            print(bcolors.FAIL + "SOMETHING WENT WRONG!" + bcolors.ENDC)

    def printme(self):
        print(bcolors.WARNING + "ACL name: " + bcolors.ENDC)
        print(self.name)
        print(bcolors.WARNING + "ACL source: " + bcolors.ENDC)
        if isinstance(self.source, str):
            print(self.source)
        else:
            self.source.printme()
        if self.destination:
            print(bcolors.WARNING + "ACL destination: " + bcolors.ENDC)
            if isinstance(self.destination, str):
                print(self.destination)
            else:
                self.destination.printme()

class pix_nat:
    def __init__(self, id, global_interface, global_address):
        self.id = id
        self.global_interface = global_interface
        self.global_address = network_object(global_address)
        self.local_interface = []
        self.local_address = []
        self.type = 0            

    def add_local(self, local_interface, local_address, type):
        self.local_interface.append(local_interface)
        if type == 2 or type == 4:
            self.local_address.append(access_list(local_address))
        else:
            self.local_address.append(network_object(local_address))
        self.type = type
    
    def printme(self):
        if self.type == 1:
            print(bcolors.HEADER + "NAT ID: " + self.id + " - DYNAMIC" + bcolors.ENDC)
            self.global_address.printme()
                               
            for _, __ in zip(self.local_interface, self.local_address):
                __.printme()
                print("nat (" + _ + "," + self.global_interface + ") after-auto source dynamic " + __.name + " " + self.global_address.name)

        elif self.type == 2:
            print(bcolors.HEADER + "NAT ID: " + self.id + " - DYNAMIC" + bcolors.ENDC)
            self.global_address.printme()

            for _, __ in zip(self.local_interface, self.local_address):
                if isinstance(__.source, str):
                    s = __.source
                else:
                    s = __.source.name
                    __.source.printme()
                if isinstance(__.destination, str):
                    d = __.destination
                else:
                    d = __.destination.name
                    __.destination.printme()
                print("nat (" + _ + ", " + self.global_interface + ") after-auto source dynamic " + s + " " + self.global_address.name + " destination static " + d + " " + d)

        elif self.type == 3:
            print(bcolors.HEADER + "NAT ID: " + str(self.id) + " - STATIC" + bcolors.ENDC)
            self.global_address.printme()
            self.local_address[0].printme()
            print("nat (" + self.local_interface[0] + "," + self.global_interface + ") source static " + self.global_address.name + " " + self.local_address[0].name)

        elif self.type == 4:
            print(bcolors.HEADER + "NAT ID: " + str(self.id) + " - STATIC " + bcolors.ENDC)
            self.global_address.printme()

            for _, __ in zip(self.local_interface, self.local_address):
                if isinstance(__.source, str):
                    s = __.source
                else:
                    s = __.source.name
                    __.source.printme()
                if isinstance(__.destination, str):
                    d = __.destination
                else:
                    d = __.destination.name
                    __.destination.printme()
                print("nat (" + self.local_interface[0] + "," + self.global_interface + ") source static " + s + " " + self.global_address.name + " destination static " + d + " " + d)
        else:
            print(bcolors.FAIL + "UNEXPECTED TRANSLATION" + bcolors.ENDC)

def translate_dynamic(pix_config):
    pix_config_nat_global = pix_config.find_objects(r"^global")
    pix_config_nat_local = pix_config.find_objects(r"^nat")
    
    pix_nat_lines = []
    pix_nat_list = []        
    for global_ in pix_config_nat_global:
        pix_nat_lines.append(global_.text)
        pix_nat_id = global_.text.split(" ")[2]
        pix_nat_gi = global_.text.split(" ")[1].replace("(", "").replace(")", "")
        pix_nat_ga = ' '.join(global_.text.split(" ")[3:])
        pix_nat_list.append(pix_nat(pix_nat_id, pix_nat_gi, pix_nat_ga))
        for local_ in pix_config_nat_local:
            if local_.text.split(" ")[2] == pix_nat_id:
                pix_nat_lines.append(local_.text)              
                pix_nat_li = local_.text.split(" ")[1].replace("(", "").replace(")", "")
                pix_nat_la = ' '.join(local_.text.split(" ")[3:]).replace("'", "").replace("[", "").replace("]", "").replace(",", "")
                for _ in pix_nat_list:
                    if _.id == pix_nat_id:        
                        if pix_nat_la.split(" ")[0] == "access-list":
                            pix_acl = pix_config.find_objects(r"^" + pix_nat_la.split(" ")[0] + " " + pix_nat_la.split(" ")[1])
                            for __ in pix_acl:                        
                                _.add_local(pix_nat_li, __.text, 2)
                                pix_nat_lines.append(__.text)
                        else:
                            _.add_local(pix_nat_li, ' '.join(pix_nat_la.split(" ")[:2]), 1)
    #print(bcolors.HEADER + "Old dynamic translations:" + bcolors.ENDC)
    #for _ in pix_nat_lines:
    #    print(_)
    
    pix_nat_list.sort(key = lambda x: x.id)
    #print(bcolors.HEADER + "New dynamic translations:" + bcolors.ENDC)
    for object in pix_nat_list:
        object.printme()

def translate_static(pix_config):
    pix_config_static = pix_config.find_objects(r"^static")

    pix_nat_list = []
    i = 1000
    for _ in pix_config_static:
        pix_nat_li = re.search("\((.*),", _.text).group(1)
        pix_nat_gi = re.search(",(.*)\)", _.text).group(1)
        if re.search("access-list", _.text):
            pix_nat_ga = _.text.split(" ")[2]
            pix_nat_list.append(pix_nat(i, pix_nat_gi, pix_nat_ga))
            for __ in pix_nat_list:
                if __.id == i:
                    pix_acl = pix_config.find_objects(r"^access-list" + _.text.strip(" norandomseq").split("access-list")[1])
                    for ____ in pix_acl:
                        pix_nat_la = ____.text
                        __.add_local(pix_nat_li, pix_nat_la, 4)
        else:
            pix_nat_la = _.text.split(" ")[2]
            pix_nat_ga = ' '.join(_.text.strip(" norandomseq").split(" ")[3:])
            pix_nat_list.append(pix_nat(i, pix_nat_gi, pix_nat_ga))
            for _ in pix_nat_list:
                if _.id == i:
                    _.add_local(pix_nat_li, pix_nat_la, 3)        
        i = i + 1

    for object in pix_nat_list:
        object.printme()

args=parser.parse_args()
if args.input:
    try:        
        pix_config = CiscoConfParse(args.input)

        translate_dynamic(pix_config)

        translate_static(pix_config)

    except EnvironmentError as e:
            print(str(e))
