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

import sys, os, errno
from os.path import join
from nsaway.nsaway import __version__
from nsaway.utils import SETTINGS_FILE, ICON_PATH, is_installed

setup = {
    "name":"nsaway",
    "version":__version__,
    "description":"NSAway.",
    "long_description":"For a detailed description, see https://github.com/TheZ3ro/nsaway.",
    "url":"https://github.com/TheZ3ro/nsaway",
    "author":"TheZero",
    "author_email":"io@thezero.org",
    "license":"GPLv3",
    "dest_dir":"/usr/share/", # will be added a *name* folder
    "data_files":[
      (SETTINGS_FILE, ['config/nsaway.ini']),
      (ICON_PATH, ['icons/nsaway_large.png','icons/nsaway_mini.png','icons/nsaway.png','icons/good.ico','icons/alert.ico']),
      ('/usr/share/icons/hicolor/48x48/apps/', ['icons/nsaway.png']),
      ('/etc/init.d/nsaway', ['config/daemon_nsaway.sh'], '+x'),
      ('/usr/share/applications/', ['config/nsaway.desktop']),
    ],
    "console_entry":[
      ['nsaway','nsaway/nsaway.py'],
      ['nsaway-tray','nsaway/tray.py']
    ],
    "postinst":["service nsaway start"],
}

debug = False

help_message = """
Setup for {0}-{1} by {3}<{4}>
Released under {5} license
Project Link {2}

Options:
  -h --help:         Show this help
  build:             Build a DEB package
  install:           Install {0}
  uninstall:         Remove {0}
""".format(setup["name"],setup["version"],setup["url"],setup["author"],setup["author_email"],setup["license"])


def system_call(str):
    if debug == True:
        print("[DEBUG] "+str)
    else:
        os.system(str)

def install(dest_dir,data_files,console_entry,path_dir):
    print("Copying program folder to: "+join(dest_dir,setup["name"])+"/")
    system_call("cp -R "+setup["name"]+" "+dest_dir)
    print("Copying data files")
    for data_pair in data_files:
        # If it's a folder but don't exists
        if len(data_pair[1]) > 1 and not os.path.isdir(data_pair[0]):
            system_call("mkdir -p "+data_pair[0])
        for ele in data_pair[1]:
            print(" | "+ele+" -> "+data_pair[0])
            system_call("cp "+ele+" "+data_pair[0])
            if len(data_pair) == 3:
                print(" | Fixing permission "+data_pair[0]+" to "+data_pair[2])
                system_call("chmod "+data_pair[2]+" "+data_pair[0])
    if path_dir != None:
        print("Creating symbolic link for executable files")
        for exe_pair in console_entry:
            if os.path.isfile(join("/usr/bin",exe_pair[0])):
                print(" | -Deleting old sym-link "+join(path_dir,exe_pair[0]))
                system_call("rm "+join(path_dir,exe_pair[0]))
            print(" | "+join(dest_dir,exe_pair[1])+" -> "+join(path_dir,exe_pair[0]))
            system_call("ln -s "+join(dest_dir,exe_pair[1])+" "+join(path_dir,exe_pair[0]))
            print(" | -Fixing executable permission for "+join(path_dir,exe_pair[0]))
            system_call("chmod +x "+join(path_dir,exe_pair[0]))
        print("Checking if "+setup["name"]+" is in $PATH")
        print("Executing postinst script")
        for pi in setup["postinst"]:
            system_call(pi)
        if debug == False:
            if is_installed(setup["name"]):
                print("Installed Successfully")
            else:
                print("ERROR: Not found in in $PATH")
        else:
            print("Printed Debug")
    else:
        if debug == False:
            print("Installed Successfully")
        else:
            print("Printed Debug")


def uninstall(dest_dir,data_files,console_entry,path_dir):
    print("Deleting sym-link")
    for exe_pair in console_entry:
        if os.path.isfile(join(path_dir,exe_pair[0])):
            print(" | "+join(path_dir,exe_pair[0]))
            system_call("rm "+join(path_dir,exe_pair[0]))
    print("Deleting data files")
    for data_pair in data_files:
        if len(data_pair[1]) == 1:
            # Should be a file
            if os.path.exists(data_pair[0]):
                print(" | "+data_pair[0])
                system_call("rm "+data_pair[0])
        else:
            # Must be a folder
            if os.path.isdir(data_pair[0]):
                print(" | "+data_pair[0])
                system_call("rm -r "+data_pair[0])
    print("Deleting program folder")
    if os.path.isdir(join(dest_dir,setup["name"])):
        print(" | "+join(dest_dir,setup["name"]))
        system_call("rm -r "+join(dest_dir,setup["name"]))
    if debug == False:
        print("Finished")
    else:
        print("Printed Debug")

def build():
    build_dir = join("build",setup["name"])
    print("Making the build folder: "+build_dir)
    system_call("mkdir -p "+build_dir)
    b_dest_dir = join(build_dir,setup["dest_dir"][1:])
    pardirs(os.path.dirname(b_dest_dir))
    b_data_files = []
    for data_pair in setup["data_files"]:
        # rebuild tuple by tuple
        b_data_files.append((join(build_dir,data_pair[0][1:]),data_pair[1]))
        pardirs(os.path.dirname(join(build_dir,data_pair[0][1:])))
    install(b_dest_dir,b_data_files,setup["console_entry"],None)
    print("Making DEBIAN/control file")
    contents = """Package: {0}
Version: {1}
Architecture: all
Maintainer: {2} <{3}>
Depends: python (>=2.7)
Section: extras
Priority: optional
Homepage: {4}
Description: {5}
 {6}\n""".format(setup["name"],setup["version"],setup["author"],setup["author_email"],setup["url"],setup["description"],setup["long_description"])
    system_call("mkdir -p "+join(build_dir,"DEBIAN"))
    with open(join(build_dir,"DEBIAN/control"), 'w+') as control:
      control.write(contents)
    print("Making DEBIAN/postinst file for sym-link")
    postinst = "#!/bin/bash\n"
    for exe_pair in setup["console_entry"]:
        if os.path.isfile(join("/usr/bin",exe_pair[0])):
            postinst += "ln -s {0} {1}\nchmod +x {1}\n".format(join(setup["dest_dir"],exe_pair[1]),join("/usr/bin",exe_pair[0]))
    for pi in setup["postinst"]:
        postinst += pi + "\n"
    with open(join(build_dir,"DEBIAN/postinst"), 'w+') as pi:
      pi.write(postinst)
    system_call("chmod 775 "+join(build_dir,"DEBIAN/postinst"))
    system_call("dpkg -b "+build_dir)

def pardirs(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
        else:
            pass

if __name__=="__main__":
    args = sys.argv[1:]

    if '--debug' in args:
        debug = True
        args.remove('--debug')

    if len(args) != 1:
      sys.exit("ERROR: One option is needed\n" + help_message)

    # Check for help
    if '-h' in args or '--help' in args:
      sys.exit(help_message)

    print("This setup is custom made. It isn't Python-setuptool compatible.")

    if 'install' in args:
        if not os.geteuid() == 0:
            print("ERROR: This Installation program needs to run as root.")
        else:
            install(setup["dest_dir"],setup["data_files"],setup["console_entry"],"/usr/bin")

    if 'uninstall' in args:
        if not os.geteuid() == 0:
            print("ERROR: This Installation program needs to run as root.")
        else:
            uninstall(setup["dest_dir"],setup["data_files"],setup["console_entry"],"/usr/bin")

    if 'build' in args:
        build()

    sys.exit(0)
