#!/usr/bin/env python
import os, sys
sys.path.append(os.path.abspath('..'))
import utils

__module_name__ = "WebCam"

def require():
    return None # video.py don't require external program

# start isn't required
# def start(*args, **kwargs):

def tick(*args, **kwargs):
    msg = None
    result = os.popen("ls -l -R /proc 2> /dev/null | grep -m1 /dev/video | awk -F'-> ' '{print $2}'").read()
    if result != "":
        msg = "Some application is using " + result
    return msg
