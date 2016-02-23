#!/usr/bin/env python
import os, sys
sys.path.append(os.path.abspath('..'))
import utils

__module_name__ = "ARP"

gateway = {
    'ip':None,
    'mac':None
}

def require():
    return ["ip","arp"] # arp_poison.py require "ip" and "arp"

def start(*args, **kwargs):
    gateway["ip"] = os.popen("ip route show | awk '(NR == 1) { print $3}'").read().rstrip()
    gateway["mac"] = os.popen("arp "+gateway["ip"]+" | awk '(NR == 2) { print $3}'").read().rstrip()

def tick(*args, **kwargs):
    msg = None
    curr_ip = os.popen("ip route show | awk '(NR == 1) { print $3}'").read().rstrip()
    if gateway["ip"] == curr_ip:
        curr_mac = os.popen("arp "+gateway["ip"]+" | awk '(NR == 2) { print $3}'").read().rstrip()
        if gateway["mac"] != curr_mac:
            msg = "Gateway MAC changed! Probably under MiTM by "+curr_mac
    else:
        msg = "Gateway IP changed to "+curr_ip
        gateway["ip"] = curr_ip
    return msg
