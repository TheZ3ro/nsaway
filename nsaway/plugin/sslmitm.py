#!/usr/bin/env python
import os, sys
sys.path.append(os.path.abspath('..'))
import utils

__module_name__ = "SSL MiTM"

from urlparse import urlparse

sites = {}

def require():
    return ["openssl"] # sslmitm.py require "openssl"

def start(*args, **kwargs):
    if args != ():
        sites[0] = args[0]['test_site']
    else:
        # Default hardcoded Trusted website
        sites[0] = ["https://www.google.com","https://thezero.org"]

def tick(*args, **kwargs):
    msg = None
    import random
    site = random.choice(sites[0])
    u = urlparse(site)
    line = os.popen("echo | openssl s_client -connect "+u.netloc+":443 2>/dev/null | openssl x509 -noout -subject").read().rstrip()
    sections = line.split("/")
    for l in sections:
        if "CN=" in l:
            subject = l.split("=")[1]
            if not u.netloc in subject:
                msg = "Wrong certificate for "+subject+" "+u.netloc
    return msg
