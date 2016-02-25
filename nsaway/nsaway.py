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

__version__ = "0.1.2"

import subprocess
import platform
import os, sys, signal
from time import sleep
import logging
from utils import *

# Sources Path
SOURCES_PATH = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(SOURCES_PATH)

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
    'plugins' : jsonloads(get_setting('plugins').strip())
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

  # Wake up all the plugin (or who want a start-up)
  for plugin in plugins:
    try:
        # Maybe plugin has some settings in the ini file :thumbsup:
        if plugin in p_settings:
            call_plugin(plugins, plugin, 'start', p_settings[plugin])
        else:
            call_plugin(plugins, plugin, 'start')
    except AttributeError:
        pass

  timeout = {}

  # Main loop
  while True:
    # Partolling
    for plugin in plugins:
      if not plugin in timeout:
        msg = call_plugin(plugins, plugin, 'tick') # Plugin tick
        if msg != None:
          mod_name = plugin_attr(plugins,plugin,"__module_name__")
          tmpl = "{2}{0}{3} : {1}"
          # Log without HTML
          logger.warn(tmpl.format(mod_name,msg,"",""))
          # Safe call, don't use os.system here!
          os.environ['DISPLAY'] = ':0.0'
          subprocess.call(["notify-send", "-i",ICON_FILE,'NSAway',tmpl.format(mod_name,msg,"<b>","</b>")])
          if 'alert_program' in settings:
             if settings['alert_program'] != "" and settings['alert_program'] != None:
                subprocess.call([settings['alert_program'],msg])
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

  # Make sure notify-send is present.
  if not is_installed('notify-send'):
    exit_log("notify-send not installed.")

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

  # Define exit handler now that settings are loaded...
  def exit_handler(signum, frame):
    # We don't use exit_log because we want to exit without errors
    logger.info("Exiting because exit signal was received")
    sys.exit(0)

  # Define also an halt handler
  def halt_handler(signum, frame):
    # TODO
    logger.info("Halt handler, what?")
    # sys.exit(0)

  # Register handlers for clean exit of program
  for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGQUIT, ]:
    signal.signal(sig, exit_handler)

  signal.signal(signal.SIGUSR1, halt_handler)

  # Start main loop
  loop(settings, plug_settings)

if __name__=="__main__":
  go()
