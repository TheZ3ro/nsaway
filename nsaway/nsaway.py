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

__version__ = "0.1.3"

import subprocess
import multiprocessing
import os, sys, signal
from time import sleep
import logging
from utils import *
from ex_thread import PropagatingThread

try:
  from tray import *
except ImportError:
  pass

# Sources Path
SOURCES_PATH = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(SOURCES_PATH)
halt = False
do_report = False

help_message = """
NSAway is a simple Snooper Detection System for Paranoid people
Settings can be changed in /etc/nsaway.ini
This program needs to run as root.
Executing without arguments will demonize the process (if possible)

Options:
  -h --help:         Show this help
     --version:      Print version and exit
     --cs:           Copy local settings ./nsaway.ini to /etc/nsaway.ini
"""

# For the plugin loader, just bunch of s**t
# Should be made better
def load_plugin(plug, name):
  mod = local_import("plugin/%s" % name)
  plug[name] = mod

def call_plugin(plug, name, fn, *args, **kwargs):
  plugin = plug[name]
  return getattr(plugin, fn)(*args, **kwargs)

def plugin_attr(plug, name, attr):
  plugin = plug[name]
  return getattr(plugin, attr)

plugins = {}

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
  settings = dict({})
  settings['config'] = {
    'timeout_cycle' : get_setting('timeout', 'INT'),
    'sleep_time' : get_setting('sleep', 'FLOAT'),
    'plugins' : jsonloads(get_setting('plugins').strip()),
    'show_notify' : get_setting('show_notify', 'BOOL')
  }

  try:
    settings['config']['alert_program'] = get_setting('alert_program')
  except configparser.NoOptionError:
    pass

  for section_name in config.sections():
    if section_name != "config":
      settings[section_name] = {}
      for name, value in config.items(section_name):
        settings[section_name][name] = value

  return settings

"""
Main loop that checks every 'sleep_time' seconds if computer is 'compromised'
"""
def loop(settings, p_settings):
  # Write to logs that loop is starting
  msg = "Started patrolling on module: " + str(settings['plugins']) + " every " + str(settings['sleep_time']) + " seconds"
  logger.info(msg)
  print("[INFO] "+ msg)

  threads = []

  # Wake up all the plugin (or who want a start-up)
  for plugin in plugins:
    # Maybe plugin has some settings in the ini file :thumbsup:
    if plugin in p_settings:
        # call_plugin(plugins, plugin, 'start', p_settings[plugin])
        t = PropagatingThread(target=call_plugin, args=(plugins, plugin, 'start', p_settings[plugin],))
        t.start()
        threads.append(t)
    else:
        # call_plugin(plugins, plugin, 'start')
        t = PropagatingThread(target=call_plugin, args=(plugins, plugin, 'start',))
        t.start()
        threads.append(t)

  try:
      for x in threads:
          x.join()
          threads.remove(x)
  except AttributeError:
      pass

  timeout = {}
  tmpl = "{2}{0}{3} : {1}"
  report = []

  # Fix for X11 on some Linux Distro
  os.environ['DISPLAY'] = ':0.0'

  global halt
  global do_report

  # Main loop
  while True:
    # Partolling
    for plugin in plugins:
      if not plugin in timeout:
        msg = call_plugin(plugins, plugin, 'tick') # Plugin tick
        if msg != None:
          mod_name = plugin_attr(plugins,plugin,"__module_name__")
          if halt == False:
              # Log without HTML
              logger.warn(tmpl.format(mod_name,msg,"",""))
              # Check if show_notify is enabled
              if settings['show_notify'] == True:
                 # Safe call, don't use os.system here!
                 subprocess.call(["notify-send", "-i",ICON_FILE,'NSAway',tmpl.format(mod_name,msg,"<b>","</b>")])
              if 'alert_program' in settings:
                 if settings['alert_program'] != "" and settings['alert_program'] != None:
                    subprocess.call([settings['alert_program'],msg])
          else:
              # Fill the report list. We will print this later.
              report.append((mod_name,msg))
          timeout[plugin] = settings['timeout_cycle']
      else:
        if timeout[plugin]<=0:
          timeout.pop(plugin)
        else:
          timeout[plugin] -= 1

    if do_report == True:
        do_report = False
        if len(report)>0:
            msg_report = ""
            for rep in report:
                # Log every single alert
                logger.warn(tmpl.format(rep[0],rep[1],"",""))
                # Make the Report message
                msg_report += tmpl.format(rep[0],rep[1],"<b>","</b>")
            # Safe call, don't use os.system here!
            subprocess.call(["notify-send", "-i",ICON_FILE,'NSAway',msg_report])

    sleep(settings['sleep_time'])

"""
Make some checks on startup, like if program are available or something else...
"""
def startup_checks():
  # Check arguments
  args = sys.argv[1:]

  # Check for help
  if '-h' in args or '--help' in args:
    sys.exit(help_message)

  if '--version' in args:
    print(sys.argv[0], __version__)
    sys.exit(0)

  plugin_list = False
  if '--plugins' in args:
    args.remove('--plugins')
    plugin_list = True
  if '-P' in args:
    args.remove('-P')
    plugin_list = True

  halt_settings = False
  if '--halt' in args:
    args.remove('--halt')
    halt_settings = True

  running_settings = False
  if '--running' in args:
    args.remove('--running')
    running_settings = True

  copy_settings = False
  if '--cs' in args:
    args.remove('--cs')
    copy_settings = True

  # Check if program is run as root, else exit.
  # Root is needed to patrolling.
  if not os.geteuid() == 0:
    # Can't do exit_log because we don't have permission :D
    sys.exit("[ERROR] This program needs to run as root.")

  # Starts logs rotation system
  create_timed_rotating_log(LOG_FILE)

  # Check all other args
  if len(args) > 0:
    exit_log("Argument not understood. Try with `{1} -h`".format(sys.argv[0]))

  # On first use copy nsaway.ini to /etc/nsaway.ini
  if not os.path.isfile(SETTINGS_FILE) or copy_settings:
    source = os.path.join(SOURCES_PATH, "../config/nsaway.ini")
    if not os.path.isfile(source):
      exit_log("You have lost your settings file. Get a new copy of the nsaway.ini and place it in /etc/ or in " + SOURCES_PATH + "/")
    print("[NOTICE] Copying config/nsaway.ini to " + SETTINGS_FILE )
    logger.debug("Copying config/nsaway.ini to " + SETTINGS_FILE )
    os.system("cp " + source + " " + SETTINGS_FILE)

  # On first use check if there is icon file
  if not os.path.isfile(ICON_FILE):
    source = os.path.join(SOURCES_PATH, "../icons/")
    if not os.path.isdir(source):
      exit_log("You have lost your icon file. Get a new copy of the icons/ folder and place it in " + SOURCES_PATH + "/")
    print("[NOTICE] Copying icons/ to " + ICON_FILE )
    logger.debug("Copying icons/ to " + ICON_FILE )
    os.system("cp -R " + source + " " + ICON_PATH)

  # Load settings
  settings = load_settings(SETTINGS_FILE)

  if plugin_list == True:
    print("Installed Plugin: "+str(list_installed_plugin(os.path.join(SOURCES_PATH,"plugin"))))
    print("Enabled Plugin: "+str(settings['config']['plugins']))
    sys.exit(0)

  # Make sure notify-send is present.
  if not is_installed('notify-send') and settings['config']['show_notify'] == True:
    exit_log("notify-send not installed. If you are on a server disable the 'show_notify' option in nsaway.ini file")

  # Loading plugin form plugin folder ;)
  for plugin in settings['config']['plugins']:
      load_plugin(plugins,plugin) # Put plugin into plugins
      ret = call_plugin(plugins, plugin, 'require')
      if ret != None:
          if is_str(ret):
              if not is_installed(ret):
                  exit_log(ret)
          else:
              for p in ret:
                  if not is_installed(p):
                        exit_log(ret)

  if not os.path.isfile(PID_FILE):
      # PID_FILE don't exist. No prob
      if halt_settings == True or running_settings == True:
          sys.exit("[ERROR] nsaway is not running!!")
      else:
          with open(PID_FILE, 'a+') as pidf:
              pidf.write(str(os.getpid()))
  else:
      with open(PID_FILE, 'r') as pidf:
          pid = pidf.read()
          if halt_settings == True:
            print("Halted notify on PID "+pid)
            os.system("/bin/kill -SIGUSR1 "+pid)
            sys.exit(0)
          elif running_settings == True:
            print("nsaway is running with PID "+pid)
            sys.exit(0)
          else:
            exit_log("nsaway is already running.")

  return settings

"""
Start-up function, very nice :)
"""
def go():
  # Run startup checks and load settings
  settings = startup_checks()
  plug_settings = settings.copy()
  del plug_settings['config']
  settings = settings['config']

  # TrayIcon setup
  d = multiprocessing.Process(name='daemon', target=tray)
  d.daemon = True
  d.start()

  # Define exit handler now that settings are loaded...
  def exit_handler(signum, frame):
    # We don't use exit_log because we want to exit without errors
    if d.is_alive() == True:
      d.terminate()
    d.join()
    logger.info("Exiting because exit signal was received")
    os.remove(PID_FILE)
    sys.exit(0)

  # Define also an halt handler
  def halt_handler(signum, frame):
    global halt
    global do_report
    if halt == False:
        halt = True
        do_report = False
        logger.info("Notification will be halted")
    else:
        halt = False
        do_report = True
        logger.info("Notification will be resumed")

  # Register handlers for clean exit of program
  for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGQUIT, ]:
    signal.signal(sig, exit_handler)

  signal.signal(signal.SIGUSR1, halt_handler)

  # Start main loop
  loop(settings, plug_settings)

if __name__=="__main__":
  go()
