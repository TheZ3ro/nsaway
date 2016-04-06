#!/usr/bin/env python
import os, sys
sys.path.append(os.path.abspath('..'))
import utils

__module_name__ = "SSLstrip"

import httplib, ssl, socket, hashlib
from urlparse import urlparse

safe = {}

def connect(url):
    URL = urlparse(url)
    conn = httplib.HTTPSConnection(URL.hostname)
    sock = socket.create_connection((conn.host, conn.port), conn.timeout, conn.source_address)
    conn.sock = ssl.wrap_socket(sock, conn.key_file, conn.cert_file, ssl_version=ssl.PROTOCOL_SSLv23)
    conn.request('GET', URL.path)
    resp = conn.getresponse()
    if resp.status == 302 or resp.status == 301: # Follow Redirect
        return connect(resp.getheader("Location",''))
    else:
        return resp

def require():
    return None # sslstrip.py

def start(*args, **kwargs):
    if args != ():
        sites = args[0]['safe_site']
    else:
        # Default hardcoded Trusted website
        sites = ["https://www.google.com","https://thezero.org"]
    for site in sites:
        r = connect(site)
        if r.status == 200:
            # We make an hash of the current page (can change :( )
            safe[site] = hashlib.sha256(r.read()).hexdigest()
    # Now (if we are in a safe environ) we have safe hash

def tick(*args, **kwargs):
    msg = None
    tamp = False
    # Check random hash if it's tampered
    # If it's tampered check all the other sites!
    # It's better than check all the sites every time.
    import random
    rand_site = random.choice(safe.keys())
    r = connect(rand_site)
    if r.status == 200:
        curr_hash = hashlib.sha256(r.read()).hexdigest()
        if safe[rand_site] != curr_hash:
            tamp = True

    if tamp == True:
        n = 1 # The random site is already changed
        for site in safe.keys():
            if site == rand_site:
                break
            r = connect(site)
            if r.status == 200:
                curr_hash = hashlib.sha256(r.read()).hexdigest()
                if safe[site] != curr_hash:
                    n+=1
        if n > 2:
            msg = n+" Trusted website has been tampered!"
    return msg
