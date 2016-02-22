#!/usr/bin/env python
import os, sys
sys.path.append(os.path.abspath('..'))
import utils

def require():
    return None # video.py don't require external program

# start isn't required
# def start(*args, **kwargs):

def tick(*args, **kwargs):
    msg = None
    f = os.popen("ls -l -R /proc 2> /dev/null | grep -m1 /dev/video | awk -F'-> ' '{print $2}'")
    result = f.read()
    if result != "":
        msg = "Some application is using " + result
    return msg
