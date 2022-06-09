#! /usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

# This program leverages InfoBlox API to speed up browsing with CLI instead of using the slow GUI
#
# usage: infoblox.py [argument1]... [argument2]... [argument N]
#
# arguments:
#   -s [ip|fqdn], --server [ip|fqdn] IP address or FQDN of a Grid Master
#   -q [member|zone_auth|zone_forward|host|a] record, --query [member|zone_auth|zone_forward|host|a] record queries for "record" in the specified database
#
# optional arguments:
#   -u, --user              if not provided will use current useraname as login
#   -r, --raw               output will be in raw (json) format
#   -h, --help              show this help message and exit

import argparse, getpass, os, sys, threading, time
import re, json
import requests, pickle

objects = ("member", "zone_auth", "zone_forward", "network", "networkcontainer", "host", "a", "ptr")
tmpcookiefile = "/tmp/infoblox.cookie"

def get_arguments():
    parser = argparse.ArgumentParser()
    parser._action_groups.pop()
    parser.add_argument("-s", "--server", help="IP address or FQDN of a Grid Master", type=str, required=True)
    parser.add_argument("-u", "--user", help="Login username", type=str)
    option = parser.add_mutually_exclusive_group()
    option.add_argument("-q", "--query", nargs="+")
    #option.add_argument("-c", "--create")
    #option.add_argument("-m", "--modify")
    parser.add_argument("-r", "--raw", help="Don't format output", action="store_true")

    args = parser.parse_args()

    return(args)

def load_animation(done):
    print("\x1b[?25l")
    load_str = "Loading..."
    ls_len = len(load_str)
    animation = "|/-\\"
    anicount = 0
    i = 0                     
    while True:
        if done():
            sys.stdout.write("\r               \r")
            sys.stdout.flush()
            break
        time.sleep(0.1) 
        load_str_list = list(load_str) 
        x = ord(load_str_list[i])
        y = 0             
        if x != 32 and x != 46:             
            if x>90:
                y = x-32
            else:
                y = x + 32
            load_str_list[i]= chr(y)
        res =""             
        for j in range(ls_len):
            res = res + load_str_list[j]
        sys.stdout.write("\r[" + animation[anicount] + "] " + res)
        sys.stdout.flush()
        load_str = res
        anicount = (anicount + 1) % 4
        i = (i + 1) % ls_len
    sys.stdout.write("\r               \r")
    sys.stdout.flush()
    sys.stdout.write("\x1b[?25h")

def save_cookies(cookie, filename):
    with open(filename, "wb") as f:
        pickle.dump(cookie, f)

def load_cookies(filename):
    with open(filename, "rb") as f:
        return(pickle.load(f))

def auth_query(qtype, query, connection_string, user, passw):
    if query == "all":
        query = ".*"
    if qtype == "member":
        filter = ""
        query = ""
    if re.search(r"^zone_*", qtype):
        filter = "?fqdn~="
    elif re.search(r"^a&", qtype) or re.search(r"^host$", qtype):
        qtype = "record:" + qtype
        filter = "?name~="
    elif re.search(r"^network*", qtype):
        filter = "?network~="
    elif re.search(r"^ptr$", qtype):
        qtype = "record:" + qtype
        filter = "?ptrdname~="
    else:
        filter = ""

    response = requests.Session()
    response = requests.get(connection_string + qtype + filter + query, auth=(user, passw))    
    save_cookies(response.cookies, tmpcookiefile)

    return(response)

def cookie_query(qtype, query, connection_string, cookie):
    if query == "all":
        query = ".*"
    if qtype == "member":
        filter = ""
        query = ""
    if re.search(r"^zone_*", qtype):
        filter = "?fqdn~="
    elif re.search(r"^a&", qtype) or re.search(r"^host$", qtype):
        qtype = "record:" + qtype
        filter = "?name~="
    elif re.search(r"^network*", qtype):
        filter = "?network~="
    elif re.search(r"^ptr$", qtype):
        qtype = "record:" + qtype
        filter = "?ptrdname~="
    else:
        filter = ""

    response = requests.get(connection_string + qtype + filter + query, cookies=cookie)
    
    return(response)

def parse_result(result):
    result = json.loads(result)
    if isinstance(result, dict) and re.search(r"(> 1000)", result["text"]):
        print("[-] Result too large. Add some filter.\n")
    elif isinstance(result, list):
        if len(result) == 0:
            print("[-] Empty result set.\n")
        else:
            total = 0
            for member in result:
                if re.search(r"member", member["_ref"]):
                    print("[+] Hostname: " + member["host_name"])
                elif re.search(r"^zone_*", member["_ref"]):
                    print("[+] View: " + member["view"] + "\tFQDN: " + member["fqdn"])
                elif re.search(r"^record:host", member["_ref"]):
                    for ipv4 in member["ipv4addrs"]:
                        print("[+] View: " + member["view"] + "\tHOST: " + member["name"] + "\tIPv4: " + ipv4["ipv4addr"])
                elif re.search(r"^record:a/", member["_ref"]):
                    print("[+] View: " + member["view"] + "\tHOST: " + member["name"] + "\tIPv4: " + member["ipv4addr"])
                elif re.search(r"^network", member["_ref"]) or re.search(r"^networkcontainer", member["_ref"]):
                    try:
                        print("[+] View:{:>15}     Network:{:>20}     Comment: {:<}".format(member["network_view"], member["network"], member["comment"]))
                    except KeyError:
                        print("[+] View:{:>15}     Network:{:>20}     Comment: ".format(member["network_view"], member["network"]))
                elif re.search(r"^record:ptr/", member["_ref"]):
                    ipv4 = re.split(":", member["_ref"])[2]
                    ipv4 = re.split("/", ipv4)[0]
                    print("[+] View:{:>15}     HOST:{:>25}     IPv4: {:<}".format(member["view"], member["ptrdname"], ipv4))
                total += 1
            print("\n[i] {:>5} records.\n".format(total))

def main():
    args = get_arguments()

    conn = "https://" + args.server + "/wapi/v2.7/"
    qtype = "member"
    query = "all"
    cookiexist = False

    if args.user:
        try:
            with open(tmpcookiefile, "rb") as f:
                cookiexist = True
        except IOError:
            upass = getpass.getpass(prompt="\n[?] " + args.user + "\'s password? ", stream=None)
            username = args.user
    else:
        username = os.environ["USER"]
        print(username)
        upass = getpass.getpass(prompt="[?] " + username + "\'s password? ", stream=None)

    if len(args.query) == 1:
        if args.query[0] in objects:
            query = "all"
        else:
            print("[!] Invalid query format\n")
            os._exit(127)
    elif len(args.query) == 2:
        if args.query[0] in objects:
            query = args.query[1]            
        else:
            print("[!] Invalid query format\n")
            os._exit(127)
    else:
        print("[!] Invalid query format\n")
        os._exit(127)
    
    done = False
    anim = threading.Thread(target=load_animation, args=(lambda:done, ))
    anim.start()
    if cookiexist:
        result = cookie_query(args.query[0], query, conn, load_cookies(tmpcookiefile))
        if result.status_code == 401:
            os.remove(tmpcookiefile)
            done = True
            anim.join()
            print("[!] Invalid authentication token. Please try again\n")
            os._exit(127)
    else:
        result = auth_query(args.query[0], query, conn, username, upass)
        if result.status_code == 401:
            os.remove(tmpcookiefile)
            done = True
            anim.join()
            print("[!] Invalid password. Please try again\n")
            os._exit(127)
    done = True
    anim.join()

    if args.raw:
        print(result.text + "\n")
    else:
        parse_result(result.text) 

if __name__ == "__main__":
    main()
