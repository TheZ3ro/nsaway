#!/usr/bin/env python

# Author: TheZero <io@thezero.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

__version__ = "0.1.0"

import subprocess
import platform
import os, sys, signal
from time import sleep
from utils import *

# Sources Path
SOURCES_PATH = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(SOURCES_PATH)

help_message = """
NSAway is a simple Snooper Detection System for Paranoid people
Settings can be changed in /etc/nsaway.ini
This program needs to run as root.
Executing without argoment will demonize the process (if possible)

Options:
  -h --help:         Show this help
     --version:      Print version and exit
     --cs:           Copy local settings ./nsaway.ini to /etc/nsaway.ini
"""

# For the plugin loader, just bunch of s**t
# Should be made better
def load_plugin(name):
    mod = local_import("plugin/%s" % name)
    return mod

def call_plugin(name, fn, *args, **kwargs):
    plugin = load_plugin(name)
    return getattr(plugin, fn)(*args, **kwargs)

"""
Load settings from filename
"""
def load_settings(filename):
  # Libraries that are only needed in this function:
  from json import loads as jsonloads
  if sys.version_info[0] == 3:
    # Python3
    import configparser
    def get_setting(name, gtype=''):
      """
        configparser: Compatibility layer for Python 2/3
        Function currently depends on a side effect, which is not necessary.
      """
      section = config['config']
      if gtype == 'FLOAT':
        return section.getfloat(name)
      elif gtype == 'INT':
        return section.getint(name)
      elif gtype == 'BOOL':
        return section.getboolean(name)
      return section[name]
  else:
    #Python2
    import ConfigParser as configparser
    def get_setting(name, gtype=''):
      if gtype == 'FLOAT':
        return config.getfloat('config', name)
      elif gtype == 'INT':
        return config.getint('config', name)
      elif gtype == 'BOOL':
        return config.getboolean('config', name)
      return config.get('config', name)

  config = configparser.ConfigParser()

  # Read all lines of settings file
  config.read(filename)

  # Build settings
  settings = dict({
    'timeout_cycle' : get_setting('timeout', 'INT'),
    'sleep_time' : get_setting('sleep', 'FLOAT'),
    'plugins' : jsonloads(get_setting('plugins').strip())
  })

  return settings

"""
Main loop that checks every 'sleep_time' seconds if computer is 'compromised'
"""
def loop(settings):
  # TODO Starting safepoint

  # Write to logs that loop is starting
  msg = "Started patrolling on module: " + str(settings['plugins']) + " every " + str(settings['sleep_time']) + " seconds"
  log(LogLevel.INFO, msg)
  print("[INFO] "+ msg)

  for plugin in settings['plugins']:
    call_plugin(plugin, 'start', settings)

  if settings['daemon'] == False:
    sys.exit(1)

  timeout = {}

  # Main loop
  while True:
    # Partolling
    for plugin in settings['plugins']:
      if not plugin in timeout:
        msg = call_plugin(plugin, 'tick')
        if msg != None:
          # Safe call, don't use os.system here!
          subprocess.call(["notify-send", "-i",ICON_FILE,'NSAway',msg])
          timeout[plugin] = settings['timeout_cycle']
      else:
        if timeout[plugin]<=0:
          timeout.pop(plugin)
        else:
          timeout[plugin] -= 1

    sleep(settings['sleep_time'])

"""
Make some checks on startup, like if program are available or something else...
"""
def startup_checks():
  # Check arguments
  args = sys.argv[1:]

  # Daemon or not?
  daemon = False
  if len(args) == 0:
    daemon = True

  # Check for help
  if '-h' in args or '--help' in args:
    sys.exit(help_message)

  if '--version' in args:
    print(sys.argv[0], __version__)
    sys.exit(0)

  copy_settings = False
  if '--cs' in args:
    args.remove('--cs')
    copy_settings = True

  # Check all other args
  if len(args) > 0:
    exit_log(LogLevel.ERROR, "Argument not understood. Try with `{1} -h`".format(sys.argv[0]))

  # Check if program is run as root, else exit.
  # Root is needed to patrolling.
  if not os.geteuid() == 0:
    exit_log(LogLevel.ERROR, "This program needs to run as root.")

  # On first use copy nsaway.ini to /etc/nsaway.ini
  if not os.path.isfile(SETTINGS_FILE) or copy_settings:
    source = os.path.join(SOURCES_PATH, "../config/nsaway.ini")
    if not os.path.isfile(source):
      exit_log(LogLevel.ERROR,"You have lost your settings file. Get a new copy of the nsaway.ini and place it in /etc/ or in " + SOURCES_PATH + "/")
    if not daemon:
      print("[NOTICE] Copying config/nsaway.ini to " + SETTINGS_FILE )
    log(LogLevel.NOTICE,"Copying config/nsaway.ini to " + SETTINGS_FILE )
    os.system("cp " + source + " " + SETTINGS_FILE)

  # On first use check if there is icon file
  if not os.path.isfile(ICON_FILE):
    source = os.path.join(SOURCES_PATH, "../icons/")
    if not os.path.isdir(source):
      exit_log(LogLevel.ERROR,"You have lost your icon file. Get a new copy of the icons/ folder and place it in " + SOURCES_PATH + "/")
    if not daemon:
      print("[NOTICE] Copying icons/ to " + ICON_FILE )
    log(LogLevel.NOTICE,"Copying icons/ to " + ICON_FILE )
    os.system("cp -R " + source + " " + ICON_PATH)

  # Load settings
  settings = load_settings(SETTINGS_FILE)

  # Make sure notify-send is present.
  if not is_installed('notify-send'):
    exit_log(LogLevel.ERROR,"notify-send not installed.")

  # Make sure sdmem is present if it will be used.
  if 'mic' in settings['plugins']:
    if not is_installed('pacmd'):
      exit_log(LogLevel.ERROR,"pacmd (pulse-audio) not installed.")
  # Make sure sswap is present if it will be used.
  if 'port' in settings['plugins']:
    if not is_installed('netstat'):
      exit_log(LogLevel.ERROR,"netstat not installed.")

  settings['daemon'] = daemon
  return settings

"""
Start-up function, very nice :)
"""
def go():
  # Run startup checks and load settings
  settings = startup_checks()

  # Define exit handler now that settings are loaded...
  def exit_handler(signum, frame):
    # We don't use exit_log because we want to exit without errors
    log(LogLevel.INFO,"Exiting because exit signal was received")
    sys.exit(0)

  # Define also an halt handler
  def halt_handler(signum, frame):
    # TODO
    log(LogLevel.INFO,"Halt handler, what?")
    # sys.exit(0)

  # Register handlers for clean exit of program
  for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGQUIT, ]:
    signal.signal(sig, exit_handler)

  signal.signal(signal.SIGUSR1, halt_handler)

  # Start main loop
  loop(settings)

if __name__=="__main__":
  go()
