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

import sys, os
from nsaway.nsaway import __version__
from nsaway.utils import SETTINGS_FILE, ICON_PATH

setup = {
    "name":"nsaway",
    "version":__version__,
    "description":"NSAway.",
    "long_description":"For a detailed description, see https://github.com/TheZ3ro/nsaway.",
    "url":"https://github.com/TheZ3ro/nsaway",
    "author":"TheZero",
    "author_email":"io@thezero.org",
    "license":"GPLv3",
    "dest_dir":"",
    "data_files":[
      (SETTINGS_FILE, ['config/nsaway.ini']),
      (ICON_PATH, ['icons/nsaway_large.png','icons/nsaway_mini.png','icons/nsaway.png'])
    ],
    "scripts":[
      ['nsaway','nsaway.py']
    ]
}

help_message = """
Setup for {0}-{1} by {3}<{4}>
Released under {5} license
Project Link {2}

Options:
  -h --help:         Show this help
  build:             Build a DEB package
  install:           Install {0}
""".format(setup["name"],setup["version"],setup["url"],setup["author"],setup["author_email"],setup["license"])

if __name__=="__main__":
    args = sys.argv[1:]

    if len(args) == 0:
      sys.exit(help_message)

    # Check for help
    if '-h' in args or '--help' in args:
      sys.exit(help_message)

    print("This setup is custom made. It isn't Python-setuptool compatible.")
    sys.exit(0)
