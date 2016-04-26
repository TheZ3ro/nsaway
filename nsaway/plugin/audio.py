#!/usr/bin/env python
import os, sys
sys.path.append(os.path.abspath('..'))
import utils

__module_name__ = "Microphone"

default = ["0","0"]

def require():
    return None

def start(*args, **kwargs):
    result = os.popen("cat /proc/asound/devices | grep capture | awk -F: '{print $2}'").read()
    # [ 1- 0]
    default[0] = result[3]
    default[1] = result[6]

def tick(*args, **kwargs):
    msg = None
    #cat /proc/asound/card1/pcm0c/info | grep count | awk -F: '{print $2}'
    total = os.popen("cat /proc/asound/card"+default[0]+"/pcm"+default[1]+"c/info | grep count | awk -F: '{print $2}'").read()
    avail = os.popen("cat /proc/asound/card"+default[0]+"/pcm"+default[1]+"c/info | grep avail | awk -F: '{print $2}'").read()
    if int(total)-int(avail) > 0:
        msg = "Some application is using /proc/asound/card"+default[0]
    return msg
