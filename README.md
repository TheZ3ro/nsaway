# NSAway

### Work In Progress.

![nsaway](icons/nsaway.png)

NSAway is a Military-Grade® Snooper Detection System (last generation IDS).

I'm kidding, It's just a daemon that listen for some (suspicious) events.

The name comes from NSA-Away (keep the NSA away from your PC) or from NSA-Way (do things the NSA way, Paranoid mode On).

### Why?
If you are **Edward Snowden** or **Mr.Robot** this script won't help you.<br/>
Go fry your PC!

Otherwise this program can be useful if:
 - You are Paranoid
 - You think that you will be Pwn3d (Hacked)
 - You are in an insecure network

**And you want to detect suspicious behavior**

### Installation (only on GNU/Linux)

#### On Desktop

Make sure you have installed "*notify-send*" and **root** can send notify.

    $ sudo su
    % notify-send "Hello World, who is listening?"

Download a .deb package *(not available)* or Clone this repo and run **setup.py**

    $ git clone https://github.com/TheZ3ro/nsaway
    $ sudo python setup.py install

#### On Server

Download a .deb package *(not available)* or Clone this repo and run **setup.py**

    $ git clone https://github.com/TheZ3ro/nsaway
    $ sudo python setup.py install

Edit the ***/etc/nsaway.ini*** file:
 - Set '*show_notify*' to **False**


    $ sudo sed -i '' 's/show_notify = True/show_notify = False/g' /etc/nsaway.ini

 - Edit the '*plugin*' list as you wish based on the plugin installed


### Credits
Based on code from [hephaest0s/USBkill](https://github.com/hephaest0s/usbkill/)<br/>
Based on idea from [LCyberspazio/eyecatcher](https://github.com/LCyberspazio/eyefinder)<br/><br/>
Eagle Icon by: Martin Berube<br/>
Alert Icon by: [Nitish Kumar](https://www.iconfinder.com/nitishkmrk)<br/>
