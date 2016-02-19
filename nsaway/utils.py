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

from datetime import datetime
import imp
import os, sys

# Set the settings filename here
SETTINGS_FILE = '/etc/nsaway.ini'

# Logfile is hardcoded
LOG_FILE = '/var/log/nsaway.log'

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

class LogLevel:
  INFO = "I" # Just some info, almost useless
  WARN = "W" # Warning situation on the system
  ERROR = "E" # Errors running nsaway
  NOTICE = "N" # Notice about some unwanted action on nsaway

"""
Write message in the log file
"""
def log(level, msg):
  contents = '[{0}] {1} | {2}\n'.format(str(datetime.now()), level, msg)
  with open(LOG_FILE, 'a+') as log:
    log.write(contents)

"""
Write message in the log file and exit with message
"""
def exit_log(level, msg):
  contents = '[{0}] {1} | {2}\n'.format(str(datetime.now()), level, msg)
  with open(LOG_FILE, 'a+') as log:
    log.write(contents)
  sys.exit("[{0}] {1}".format(level,msg))

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
