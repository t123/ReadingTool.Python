import os, json
from PyQt4 import QtCore, QtGui, Qt

from lib.misc import Application
from lib.stringutil import StringUtil
from lib.models.model import Plugin
from lib.services.service import PluginService
from ui.views.plugins import Ui_Plugins
from lib.services.web import WebService


class PluginsForm(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Plugins()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.pluginService = PluginService()
        QtCore.QObject.connect(self.ui.pbInstall, QtCore.SIGNAL("clicked()"), self.install)
        QtCore.QObject.connect(self.ui.pbRemove, QtCore.SIGNAL("clicked()"), self.remove)
        QtCore.QObject.connect(self.ui.pbUpdate, QtCore.SIGNAL("clicked()"), self.update)
        
        QtCore.QObject.connect(self.ui.lwInstalled, QtCore.SIGNAL("currentItemChanged(QListWidgetItem*,QListWidgetItem*)"), self.updateInstalledDescription)
        QtCore.QObject.connect(self.ui.lwAvailable, QtCore.SIGNAL("currentItemChanged(QListWidgetItem*,QListWidgetItem*)"), self.updateAvailableDescription)
        QtCore.QObject.connect(self.ui.lwUpdate, QtCore.SIGNAL("currentItemChanged(QListWidgetItem*,QListWidgetItem*)"), self.updateUpdateDescription)
        
    def bindPlugins(self):
        plugins = self.pluginService.findAll()
        
        self.ui.lwInstalled.clear()
        
        for plugin in plugins:
            item = QtGui.QListWidgetItem(plugin.name)
            item.setData(QtCore.Qt.UserRole, plugin)
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Unchecked)
            
            self.ui.lwInstalled.addItem(item)
            
        self.ui.lwInstalled.setCurrentRow(0)
        
        self.bindRemote()
        
    def bindRemote(self):
        webService = WebService()
        
        plugins = self.pluginService.findAll()
        available = webService.getAvailablePlugins()
        
        self.ui.lwAvailable.clear()
        self.ui.lwUpdate.clear()
        
        for plugin in available:
            exists = None
            
            for p in plugins:
                if p.uuid==plugin["uuid"]:
                    exists = p
                    break
            
            if exists is None:
                item = QtGui.QListWidgetItem(plugin["name"])
                item.setData(QtCore.Qt.UserRole, plugin)
                item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                item.setCheckState(QtCore.Qt.Unchecked)
            
                self.ui.lwAvailable.addItem(item)
            else:
                if int(exists.version)<int(plugin["version"]):
                    item = QtGui.QListWidgetItem(plugin["name"])
                    item.setData(QtCore.Qt.UserRole, plugin)
                    item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                    item.setCheckState(QtCore.Qt.Unchecked)
                    self.ui.lwUpdate.addItem(item)
            
        self.ui.lwAvailable.setCurrentRow(0)
        
    def updateInstalledDescription(self, item, previous):
        if item is None:
            return
        
        plugin = item.data(QtCore.Qt.UserRole)
        
        if StringUtil.isEmpty(plugin.description):
            self.ui.pteInstalled.setPlainText("No description available for {0}".format(plugin.name))
        else:
            self.ui.pteInstalled.setPlainText(plugin.description)
        
    def updateAvailableDescription(self, item, previous):
        if item is None:
            return

        plugin = item.data(QtCore.Qt.UserRole)
        
        if StringUtil.isEmpty(plugin["description"]):
            self.ui.pteAvailable.setPlainText("No description available for {0}".format(plugin["name"]))
        else:
            self.ui.pteAvailable.setPlainText(plugin["description"])
        
    def updateUpdateDescription(self, item, previous):
        if item is None:
            return

        plugin = item.data(QtCore.Qt.UserRole)
        
        if StringUtil.isEmpty(plugin["description"]):
            self.ui.pteUpdate.setPlainText("No description available for {0}".format(plugin["name"]))
        else:
            self.ui.pteUpdate.setPlainText(plugin["description"])
        
    def install(self):
        webService = WebService()
        
        uuids = []
        
        for index in range(0, self.ui.lwAvailable.count()):
            item = self.ui.lwAvailable.item(index)
            
            if item.checkState()==QtCore.Qt.Checked:
                plugin = item.data(QtCore.Qt.UserRole)
                uuids.append(plugin["uuid"])
                
        plugins = webService.getPlugins(uuids)
        
        for plugin in plugins:
            p = Plugin()
            p.name = plugin["name"]
            p.description = plugin["description"] 
            p.content = plugin["content"] 
            p.name = plugin["name"] 
            p.uuid = plugin["uuid"] 
            p.version = plugin["version"]
            
            self.pluginService.save(p)
             
        self.bindPlugins()
                
    def update(self):
        webService = WebService()
        
        uuids = []
        
        for index in range(0, self.ui.lwUpdate.count()):
            item = self.ui.lwUpdate.item(index)
            
            if item.checkState()==QtCore.Qt.Checked:
                plugin = item.data(QtCore.Qt.UserRole)
                uuids.append(plugin["uuid"])
                
        plugins = webService.getPlugins(uuids)
        
        for plugin in plugins:
            p = self.pluginService.findOneByUuid(plugin["uuid"])
            
            if p is None:
                continue
            
            p.name = plugin["name"]
            p.description = plugin["description"] 
            p.content = plugin["content"] 
            p.name = plugin["name"] 
            p.version = plugin["version"]
            
            self.pluginService.save(p)
             
        self.bindPlugins()
        
    def remove(self):
        for index in range(0, self.ui.lwInstalled.count()):
            item = self.ui.lwInstalled.item(index)
             
            if item.checkState()==QtCore.Qt.Checked:
                plugin = item.data(QtCore.Qt.UserRole)
                self.pluginService.delete(plugin.pluginId)
                
        self.bindPlugins()