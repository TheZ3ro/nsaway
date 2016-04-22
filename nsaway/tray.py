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

from PyQt4 import QtGui, QtCore
import os, sys
import signal
from os.path import join
from utils import get_icon_path

class SystemTrayIcon(QtGui.QSystemTrayIcon):

  def __init__(self, icon, parent=None):
    QtGui.QSystemTrayIcon.__init__(self, icon, parent)
    menu = QtGui.QMenu(parent)
    #changeicon = menu.addAction("Update")
    exitAction = menu.addAction("Exit")
    self.setContextMenu(menu)
    exitAction.triggered.connect(quit)
    #changeicon.triggered.connect(self.updateIcon)

def quit():
  QtGui.qApp.quit()
  os.kill(os.getppid(), signal.SIGTERM)

def update_tray_icon(tray,staus):
  # status can only be (good, alert)
  tray.setIcon(QtGui.QIcon(get_icon_path(status+".ico")))

def tray():
  app = QtGui.QApplication(['NSAway'])
  style = app.style()
  ico = QtGui.QIcon(style.standardPixmap(QtGui.QStyle.SP_FileIcon))
  w = QtGui.QWidget()

  trayIcon = SystemTrayIcon(ico, w)
  trayIcon.show()
  trayIcon.setIcon(QtGui.QIcon(get_icon_path("good.ico")))

  sys.exit(app.exec_())
