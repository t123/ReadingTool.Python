from PyQt4 import QtCore, QtGui, Qt

from lib.misc import Application
from lib.models.model import Term, TermState
from lib.services.service import StorageService
from ui.views.settings import Ui_Settings

class SettingsForm(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Settings()
        self.ui.setupUi(self)
        
        self.storageService = StorageService()
        QtCore.QObject.connect(self.ui.actionCancel, QtCore.SIGNAL("triggered()"), self.reset)
        QtCore.QObject.connect(self.ui.actionSave, QtCore.SIGNAL("triggered()"), self.save)
    
    def bindSettings(self):
        self.ui.twSettings.clear()
        headers = ["Key", "Value"]
        
        self.ui.twSettings.setColumnCount(len(headers))
        self.ui.twSettings.setHorizontalHeaderLabels(headers)
        self.ui.twSettings.setSortingEnabled(True)
         
        index = 0
        settings = self.storageService.findAll(uuid="")
        
        self.ui.twSettings.setRowCount(len(settings))
         
        for setting in settings:
            i = QtGui.QTableWidgetItem(setting.key)
            i.setData(QtCore.Qt.UserRole, setting)
            i.setFlags(i.flags() ^ QtCore.Qt.ItemIsEditable)
 
            self.ui.twSettings.setItem(index, 0, i)
            self.ui.twSettings.setItem(index, 1, QtGui.QTableWidgetItem(setting.value))

            index +=1
         
        self.ui.twSettings.resizeColumnsToContents()
        self.ui.twSettings.horizontalHeader().setStretchLastSection(True)
        
    def reset(self):
        self.bindSettings()
        
    def save(self):
        for index in range(0, self.ui.twSettings.rowCount()):
            item = self.ui.twSettings.item(index, 0).data(QtCore.Qt.UserRole)
            value = self.ui.twSettings.item(index, 1).text()
            self.storageService.save(item.key, value, "")
            
        self.bindSettings()