import logging
from PyQt4 import QtCore, QtGui, Qt

from lib.services.service import StorageService
from ui.views.definition import Ui_Definition

class DefinitionForm(QtGui.QDialog):
    def __init__(self, definition, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Definition()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Popup | QtCore.Qt.Window)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFixedSize(self.size())
        self.ui.pteDefinition.setPlainText(definition)
        
    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Escape:
            self.deleteLater()
            return