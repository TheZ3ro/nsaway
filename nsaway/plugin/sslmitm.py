#!/usr/bin/env python
import os, sys
sys.path.append(os.path.abspath('..'))
import utils

__module_name__ = "SSL MiTM"

from urlparse import urlparse

safe = {}

def ssl_fingerprint(site):
    u = urlparse(site)
    line = os.popen("echo | openssl s_client -connect "+u.netloc+":443 2>/dev/null | openssl x509 -noout -fingerprint").read().rstrip()
    if "Fingerprint=" in line:
        fp = line.split("=")[1]
        return fp
    return None

def require():
    return ["openssl"] # sslmitm.py require "openssl"

def start(*args, **kwargs):
    sites = []
    if args != ():
        sites = args[0]['safe_site']
    else:
        # Default hardcoded Trusted website
        sites = ["https://www.google.com","https://thezero.org"]
    for site in sites:
        fp = ssl_fingerprint(site)
        if fp != None:
            safe[site] = fp

def tick(*args, **kwargs):
    msg = None
    tamp = False
    import random
    rand_site = random.choice(safe.keys())
    r = ssl_fingerprint(rand_site)
    if r != None and r != safe[rand_site]:
        tamp = True

    if tamp == True:
        n = 1 # The random site is already changed
        for site in safe.keys():
            if site == rand_site:
                break
            r = ssl_fingerprint(site)
            if r != None and r != safe[site]:
                n+=1
        if n > 2:
            msg = n+" Trusted Certificate has been tampered!"
    return msg
