#! /usr/bin/env python3
"""

"""

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

# This program does parse a given ASA configuration and splits different L2L VPN tunnels
#
# usage: vpn_parse.py -i INPUT [-h]
#
# arguments:
#   -i INPUT, --input INPUT input file containing ASA configuration to parse
#
# optional arguments:
#   -h, --help              show this help message and exit

## IMPORTANT NOTE
## OBJECTS, AND OBJECT GROUP SEARCH FAIL IF THE NAME IS LONGER
## I.E.: IT WILL MATCH BOTH OBJECTS "azure" AND "azure_anythingelse" AS IT ONLY LOOKS FOR "azure"
## IT DOESN'T LOOK FOR OBJECT DEFINITIONS WHITHIN THE OBJECTS FOUND. IT IS NOT RECURSIVE

import argparse, ipaddress
from ciscoconfparse import CiscoConfParse

def get_arguments():
    parser = argparse.ArgumentParser()
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    required.add_argument("-i", "--input", help = "input file configuration", type = str, required = True)    

    args = parser.parse_args()

    return(args)

def show_banner():
    print("    _ _____ ____  _____")
    print("   (_) ___/( __ )/ ___/")
    print("  / / __ \/ __  / __ \\")
    print(" / / /_/ / /_/ / /_/ /")
    print("/_/\____/\____/\____/")
    print("\n\n\tv.0.1\n\n")

def get_vpn_config(peer, config):
    print("[+] Processing peer " + peer + "...")
    crypto_maps = []
    crypto_interfaces = []
    transform_sets = []
    crypto_acls = []
    group_policies = []
    tunnel_groups = []
    objects = []
    ikev2_proposals = []
    ikev1_policies = []
    ikev2_policies = []

    config_tunnel_group = config.find_objects(r"^tunnel-group " + peer)
    for tunnel_group in config_tunnel_group:
        tunnel_groups.append(tunnel_group.text)
        for tunnel_group_children in tunnel_group.children:
            tunnel_groups.append(tunnel_group_children.text)
            if "default-group-policy " in tunnel_group_children.text:
                group_policy_to_find = tunnel_group_children.text.split("default-group-policy ")

    config_group_policy = config.find_objects(r"^group-policy " + group_policy_to_find[1])
    for group_policy in config_group_policy:
            group_policies.append(group_policy.text)
            for group_policy_children in group_policy.children:
                group_policies.append(group_policy_children.text)

    config_crypto_map = config.find_objects(r"^crypto map")
    crypto_map_name = "/"
    crypto_map_seq_number_to_find = "/"
    crypto_map_transform_set_name = "/"
    crypto_map_acl_name = "/"
    for crypto_map in config_crypto_map:
        if peer in crypto_map.text:
            crypto_map_name = crypto_map.text.split(" ", 4)[2]
            crypto_map_seq_number_to_find = crypto_map.text.split(" ", 4)[3]
    for crypto_map in config_crypto_map:
        if crypto_map_name + " " + crypto_map_seq_number_to_find + " " in crypto_map.text:
            crypto_maps.append(crypto_map.text)
        if crypto_map_name + " " + crypto_map_seq_number_to_find + " " in crypto_map.text and " transform-set " in crypto_map.text:
            crypto_map_transform_set_name = crypto_map.text.split(" ")[7]
        if crypto_map_name + " " + crypto_map_seq_number_to_find + " " in crypto_map.text and " address " in crypto_map.text:
            crypto_map_acl_name = crypto_map.text.split(" ")[6]
        if "crypto map " + crypto_map_name + " interface " in crypto_map.text:
            crypto_interfaces.append(crypto_map.text)

    config_transform_set = config.find_objects("transform-set")
    for transform_set in config_transform_set:
        if "crypto ipsec " in transform_set.text and crypto_map_transform_set_name + " " in transform_set.text:
            transform_sets.append(transform_set.text)

    config_access_list = config.find_objects(r"^access-list")
    for access_list in config_access_list:
        if crypto_map_acl_name + " " in access_list.text:
            crypto_acls.append(access_list.text)
    
    config_objects = config.find_objects(r"^object")
    first_object = "/"
    second_object = "/"
    if crypto_acls:
        for entry in crypto_acls:
            if " object" in entry:
                entry_slices = entry.split(" object")
                if len(entry_slices) == 3:
                    first_object = entry_slices[1].strip("-group").strip()
                    second_object = entry_slices[2].strip("-group").strip()
                if len(entry_slices) == 2:
                    first_object = entry_slices[1].strip("-group").strip()
        if first_object != "/":
            for entry in config_objects:
                if first_object in entry.text:
                    objects.append(entry.text)
                    for entry_children in entry.children:
                        objects.append(entry_children.text)
        if second_object != "/":
            for entry in config_objects:
                if second_object in entry.text:
                    objects.append(entry.text)
                    for entry_children in entry.children:
                        objects.append(entry_children.text)

    # GET ALL PROPOSALS IN CONFIG. THIS IS LINKED TO THE IPSEC SA DURING NEGOTIATION
    config_ikev2_proposal = config.find_objects(r"^crypto ipsec ikev2 ipsec-proposal")
    for ikev2_proposal in config_ikev2_proposal:
        ikev2_proposals.append(ikev2_proposal.text)
        for ikev2_proposal_children in ikev2_proposal.children:
            ikev2_proposals.append(ikev2_proposal_children.text)
    
    config_ikev1_policy = config.find_objects(r"^crypto ikev1 policy")
    for ikev1_policy in config_ikev1_policy:
        if crypto_map_seq_number_to_find in ikev1_policy.text and ikev1_policy.text.endswith(" " + crypto_map_seq_number_to_find):
            ikev1_policies.append(ikev1_policy.text)
            for ikev1_policy_children in ikev1_policy.children:
                ikev1_policies.append(ikev1_policy_children.text)

    config_ikev2_policy = config.find_objects(r"^crypto ikev2 policy")
    for ikev2_policy in config_ikev2_policy:
        if crypto_map_seq_number_to_find in ikev2_policy.text and ikev2_policy.text.endswith(" " + crypto_map_seq_number_to_find):
            ikev2_policies.append(ikev2_policy.text)
            for ikev2_policy_children in ikev2_policy.children:
                ikev2_policies.append(ikev2_policy_children.text)

    output = open("VPN_" + peer + ".cfg", "w")
    for entry in objects:
        output.write(entry + "\n")
    output.write("!\n")
    for entry in crypto_acls:
        output.write(entry + "\n")
    output.write("!\n")
    for entry in transform_sets:
        output.write(entry + "\n")
    output.write("!\n")
    for entry in ikev2_proposals:
        output.write(entry + "\n")
    output.write("!\n")
    for entry in crypto_maps:
        output.write(entry + "\n")
    output.write("!\n")
    for entry in crypto_interfaces:
        output.write(entry + "\n")
    output.write("!\n")
    for entry in ikev1_policies:
        output.write(entry + "\n")
    output.write("!\n")
    for entry in ikev2_policies:
        output.write(entry + "\n")
    output.write("!\n")
    for entry in group_policies:
        output.write(entry + "\n")
    output.write("!\n")
    for entry in tunnel_groups:
        output.write(entry + "\n")
    output.write("!\n")
    output.close()


def main():
    show_banner()
    args = get_arguments()

    if args.input:
        try:
            # Create peers list
            peers = []
            # Parse configuration file using library
            config = CiscoConfParse(args.input)
            # Find all tunnel-group sections
            print("[+] Looking for tunnel groups...")
            t_n = config.find_objects(r" type ipsec-l2l")
            print("[i] Found " + str(len(t_n)) + " tunnels configured...")
            config_tunnel_groups = config.find_objects(r"^tunnel-group")
            # Loop all the tunnel group
            for tunnel_group in config_tunnel_groups:
                # Split to get the peer address
                s_t_g = tunnel_group.text.split(" ", 2)
                # Add address to peers list
                if s_t_g[1] not in peers:
                    try:
                        ip = ipaddress.ip_address(s_t_g[1])
                        peers.append(s_t_g[1])
                    except ValueError:
                        pass

            # Loop all peers found
            for peer in peers:
                get_vpn_config(peer, config)

        except EnvironmentError as e:
            print(str(e))

if __name__ == '__main__':
    main()
