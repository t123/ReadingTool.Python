import logging
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
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.storageService = StorageService()
        QtCore.QObject.connect(self.ui.actionCancel, QtCore.SIGNAL("triggered()"), self.reset)
        QtCore.QObject.connect(self.ui.actionSave, QtCore.SIGNAL("triggered()"), self.save)
        
        self.bindSettings()
        self.bindUserSettings()
    
    def bindSettings(self):
        self.ui.twSettings.clear()
        headers = ["Key", "Value"]
        
        self.ui.twSettings.setColumnCount(len(headers))
        self.ui.twSettings.setHorizontalHeaderLabels(headers)
        self.ui.twSettings.setSortingEnabled(True)
         
        index = 0
        settings = self.storageService.findAll(uuid=None)
        
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
        
    def bindUserSettings(self):
        self.ui.twUserSettings.clear()
        headers = ["Key", "Value"]
        
        self.ui.twUserSettings.setColumnCount(len(headers))
        self.ui.twUserSettings.setHorizontalHeaderLabels(headers)
        self.ui.twUserSettings.setSortingEnabled(True)
         
        index = 0
        settings = self.storageService.findAll(uuid=Application.user.userId)
        
        self.ui.twUserSettings.setRowCount(len(settings))
         
        for setting in settings:
            i = QtGui.QTableWidgetItem(setting.key)
            i.setData(QtCore.Qt.UserRole, setting)
            i.setFlags(i.flags() ^ QtCore.Qt.ItemIsEditable)
 
            self.ui.twUserSettings.setItem(index, 0, i)
            self.ui.twUserSettings.setItem(index, 1, QtGui.QTableWidgetItem(setting.value))

            index +=1
         
        self.ui.twUserSettings.resizeColumnsToContents()
        self.ui.twUserSettings.horizontalHeader().setStretchLastSection(True)
        
    def reset(self):
        self.bindSettings()
        self.bindUserSettings()
        
    def save(self):
        currentLocal = self.storageService.find(StorageService.SERVER_LOCAL, "http://localhost:8080")
        
        for index in range(0, self.ui.twSettings.rowCount()):
            item = self.ui.twSettings.item(index, 0).data(QtCore.Qt.UserRole)
            value = self.ui.twSettings.item(index, 1).text()
            self.storageService.save(item.key, value, None)
            
        for index in range(0, self.ui.twUserSettings.rowCount()):
            item = self.ui.twUserSettings.item(index, 0).data(QtCore.Qt.UserRole)
            value = self.ui.twUserSettings.item(index, 1).text()
            self.storageService.save(item.key, value, Application.user.userId)
                
        local = self.storageService.find(StorageService.SERVER_LOCAL, "http://localhost:8080") 
        remote = self.storageService.find(StorageService.SERVER_REMOTE, "http://api.readingtool.net")
            
        if currentLocal!=local:
            from server.server import Server
            from ui.reader import ReaderWindow
                        
            Application.server = Server(embed=True)
            Application.server.stop()
            Application.server.start()
            Application.apiServer = local
            
            Found = False
            
            for widget in QtGui.QApplication.allWidgets():
                if isinstance(widget, ReaderWindow):
                    Found = True            
        
            if Found:
                QtGui.QMessageBox.information(self, "Local Server Changed", "The address of your local server has changed. Please close and reopen all of your reading windows.")
                
        Application.remoteServer = remote
        
        logging.debug("Local server=%s" % Application.apiServer) 
        logging.debug("Remote server=%s" % Application.remoteServer) 
        
        self.bindSettings()
        self.bindUserSettings()
            