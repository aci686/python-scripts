#! /usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

#

import sys, signal
import argparse
import re
import pdb

# Extracts file section between start and end
def extract_block(start, end, file):
    block = []  

    l = [i for i, x in enumerate(file) if x == end] # Gets indexes for all occurences
    e = list(filter(lambda i: i > file.index(start), l))[0] # Gets the first end index after start

    for _ in file[file.index(start) + 1:e]: # Get file slice
        block.append(_)

    return(block)

# Defines a fortigate object
# Assuming the line:
#   forti_section("edit \"quarantine\"")
# Will create an object containing "edit "quarantine""
# If the line does not start with "edit ", it will raise an exception
class forti_object:
    def __init__(self, line, file):
        self.name = ""
        self.commands = []

        if line.lstrip().startswith("edit "):
            self.name = line.lstrip().replace("edit ", "")
            for command in extract_block("edit " + self.name, "next", file):
                self.commands.append(command.lstrip().replace("set ", ""))
        else:
            raise Exception

    def __str__(self):
        string = "edit " + self.name + "\n"
        for _ in self.commands:
            string += "set " + _ + "\n"
        string += "next"

        return(string)

# Defines a section object
# Assuming the line:
#   forti_section("config switch-controller policy")
# Will create an object containing "switch-controller policy"py
# If the line does not start with "config ", it will raise an exception
class forti_section:
    def __init__(self, line, file):
        self.name = ""
        self.objects = []

        if line.lstrip().startswith("config "):
            self.name = line.lstrip().replace("config ", "")
            for _ in extract_block("config " + self.name, "end", file):
                if "edit " in _:
                    self.objects.append(forti_object(_, file))
        else:
            raise Exception

    def __str__(self):
        string = "config " + self.name + "\n"
        for _ in self.objects:
            string += _.__str__() + "\n"
        string += "end"

        return(string)

sample_config_file = "fortisample.config"
sample_config = []

# CTRL+C Handler
def signal_handler(signal, frame):
    print("\r[!] Interrupted! Exiting...")
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Arument Parser
def get_arguments():
    parser = argparse.ArgumentParser()
    parser._action_groups.pop()
    parser.add_argument("-i", "--input", help="FortiGate configuration file", type=str, default="", required=True)
    
    args = parser.parse_args()

    return(args)

# Loads config file into memory
def load_config(config_file):
    with open(config_file, "r") as file:
        sample_config = file.read().splitlines()

    #r_c = []
    #for _ in sample_config:
    #    r_c.append(_.strip())

    return(sample_config)

# Returns 4 first lines with config metadata
def get_header(config_file):
    header = {
        "config_version": "=".join(config_file[0].split("=")[1:]), # Splits and pus together params after the first = sign
        "conf_file_ver": config_file[1].split("=")[1],
        "buildno": config_file[2].split("=")[1],
        "global_vdom": config_file[3].split("=")[1]
    }

    del config_file[0:4] # Delete headers from config in memory

    return(header)

# Returns VDOM list
def get_vdoms(config_file):
    vdoms = []

    for _ in config_file[config_file.index("config vdom") + 1:config_file.index("end") - 1]:
        if _.startswith("edit "):
            vdoms.append(_.split(" ")[1])

    # Remove vdom declare section from config in memory
    config_file.remove("config vdom")
    for _ in vdoms:
        config_file.remove("edit " + _)
        config_file.remove("next")
    config_file.remove("end")

    return(vdoms)

# Returns Global config section
def get_global(config_file):
    global_config = []

    # Get every config line between
    #   config global
    #   and
    #   first VDOM
    for _ in config_file[config_file.index("config global") + 1:config_file.index("config vdom") - 1]:
        global_config.append(_)

    # Delete Global section from config in memory
    del config_file[config_file.index("config global"):config_file.index("config vdom")]
    
    return(global_config)

# Returns argument VDOM config section
def get_vdom(vdom, config_file):
    this = []
    start = mark = False # Flags to mark start and end of section

    for _ in config_file:
        if _ == "config vdom":
            mark = True # VDOM config start
        if _ == "edit " + vdom:
            start = True # Argument VDOM
        if start and mark:
            this.append(_)
            if not _: # First empty line breaks loop (empty line separates VDOM sections)
                break

    return(this)

def main():
    args = get_arguments()

    config = load_config(args.input)
    print(extract_block(config[273], "    next", config))
    ##! Get object + commands
    #test = forti_object(config[344], config)
    #print(test)

    #! Ger section + objects
    #test = forti_section(config[56], config)
    #print(test)
    #for _ in test.objects:
    #    print(_)
    #    for __ in _.commands:
    #        print(__)
    
    
    #config = load_config(args.input)
    #header_data = get_header(config)
    #vdom_list = get_vdoms(config)
    #global_config = get_global(config)
    #with open("global.config", "w") as file:
    #    file.write("\n".join(global_config))
    #for _ in vdom_list:
    #    this_vdom = get_vdom(_, config)
    #    with open(_ + ".vdom.config", "w") as f:
    #        f.write("\n".join(this_vdom))

if __name__ == "__main__":
    main()
