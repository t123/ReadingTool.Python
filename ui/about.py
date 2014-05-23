import logging
from PyQt4 import QtCore, QtGui, Qt

from lib.services.service import StorageService
from ui.views.about import Ui_About

class AboutForm(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_About()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFixedSize(self.size())
        self.ui.lblVersion.setText("Version {0}".format(StorageService.sfind(StorageService.SOFTWARE_VERSION, "Unknown")))