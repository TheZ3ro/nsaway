#
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

import imp
import os, sys
import logging
from datetime import datetime
import time
from logging.handlers import TimedRotatingFileHandler
from log_formatter import NsaFormatter

# Set the settings filename here
SETTINGS_FILE = '/etc/nsaway.ini'
# Logfile is hardcoded
LOG_FILE = '/var/log/nsaway.log'
# PID file is hardcoded
PID_FILE = '/var/run/nsaway.pid'
# iconfile is hardcoded
ICON_PATH = '/usr/share/pixmaps/nsaway/'
ICON_FILE = ICON_PATH+'nsaway_mini.png'
logger = logging.getLogger("Rotating Log")

def local_import(name, globals=None, locals=None, fromlist=None):
    # Fast path: see if the module has already been imported.
    try:
        return sys.modules[name]
    except KeyError:
        pass

    # If any of the following calls raises an exception,
    # there's a problem we can't handle -- let the caller handle it.

    fp, pathname, description = imp.find_module(name)

    try:
        return imp.load_module(name, fp, pathname, description)
    finally:
        # Since we may exit via an exception, close fp explicitly.
        if fp:
            fp.close()

def create_timed_rotating_log(path):
    logFormatter = NsaFormatter()
    logger.setLevel(logging.INFO)               # See https://docs.python.org/2/library/logging.html#levels
    handler = TimedRotatingFileHandler(LOG_FILE,  # https://docs.python.org/2/library/logging.handlers.html#timedrotatingfilehandler
                                       when="midnight",
                                       interval=1,
                                       backupCount=30)
    handler.setFormatter(logFormatter)
    handler.suffix = "%Y%m%d"
    logger.addHandler(handler)


"""
Return a list of PY file from a folder
"""
def list_installed_plugin(d_path):
  # list py files from a folder
  files = [x.split(".")[0] for x in os.listdir(d_path) if os.path.isfile(d_path+os.sep+x) and x.split(".")[1] == 'py']
  return files

"""
Write message in the log file and exit with message
"""
def exit_log(msg):
  logger.error(msg)
  os.remove(PID_FILE)
  sys.exit("[ERROR] {0}".format(msg))

"""
Return the PID of a process
"""
def pidof(process):
  return os.popen('pidof %s' % process).read().rstrip()

"""
Check is "s" is a string
"""
def is_str(s):
  if hasattr(s, 'lower'):
      return True
  return False

"""
Check if a program is installed
"""
def is_installed(program):
  if sys.version_info[0] == 3:
    # Python3
    from shutil import which
    return which(program) != None

  else:
    """
      Test if an executable exist in Python2
      -> http://stackoverflow.com/a/377028
    """
    def is_exe(fpath):
      return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath and is_exe(program):
      return True
    else:
      for path in os.environ["PATH"].split(os.pathsep):
        path = path.strip('"')
        exe_file = os.path.join(path, program)
        if is_exe(exe_file):
          return True
    return False
