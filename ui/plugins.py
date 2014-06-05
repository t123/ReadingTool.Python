import os, json, uuid, time
from PyQt4 import QtCore, QtGui, Qt

from lib.misc import Application, Time
from lib.stringutil import StringUtil
from lib.models.model import Plugin
from lib.services.service import PluginService, StorageService
from ui.views.plugins import Ui_Plugins
from lib.services.web import WebService
from uuid import uuid1


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
        QtCore.QObject.connect(self.ui.pbAdd, QtCore.SIGNAL("clicked()"), self.add)
        QtCore.QObject.connect(self.ui.pbSave, QtCore.SIGNAL("clicked()"), self.save)
        QtCore.QObject.connect(self.ui.pbCheckNow, QtCore.SIGNAL("clicked()"), self.updateRemotePlugins)
        
        QtCore.QObject.connect(self.ui.lwInstalled, QtCore.SIGNAL("currentItemChanged(QListWidgetItem*,QListWidgetItem*)"), self.updateInstalledDescription)
        QtCore.QObject.connect(self.ui.lwAvailable, QtCore.SIGNAL("currentItemChanged(QListWidgetItem*,QListWidgetItem*)"), self.updateAvailableDescription)
        QtCore.QObject.connect(self.ui.lwUpdate, QtCore.SIGNAL("currentItemChanged(QListWidgetItem*,QListWidgetItem*)"), self.updateUpdateDescription)
        QtCore.QObject.connect(self.ui.lwLocal, QtCore.SIGNAL("currentItemChanged(QListWidgetItem*,QListWidgetItem*)"), self.updateLocal)
        
        self.bindAll()
        
    def bindAll(self):
        self.bindPlugins()
        self.bindLocal()
        self.bindRemote()
        
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
        
    def getRemotePlugins(self):
        webService = WebService()
        available = webService.getAvailablePlugins()
        StorageService.ssave(StorageService.PLUGIN_LAST_CHECK, time.time())
        StorageService.ssave(StorageService.PLUGIN_CACHE, json.dumps(available, sort_keys=True))
        
        return available
    
    def updateRemotePlugins(self):
        self.getRemotePlugins()
        self.bindRemote()
        
    def bindRemote(self):
        lastCheck = StorageService.sfind(StorageService.PLUGIN_LAST_CHECK, time.time())
        cached = StorageService.sfind(StorageService.PLUGIN_CACHE, "")
        
        try:
            if time.time()-float(lastCheck)>60*60*24 or StringUtil.isEmpty(cached):
                available = self.getRemotePlugins()            
            else:
                try:
                    available = json.loads(cached)
                except:
                    raise
        except:
            available = self.getRemotePlugins()
        
        lastCheck = StorageService.sfind(StorageService.PLUGIN_LAST_CHECK, -1)
        self.ui.lblLastChecked.setText("Last checked: " + Time.toHuman(float(lastCheck)))
        plugins = self.pluginService.findAll()
        
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
        
    def bindLocal(self):
        plugins = self.pluginService.findLocal()
        
        self.ui.lwLocal.clear()
        
        if len(plugins)==0:
            self.ui.pbSave.setEnabled(False)
            self.ui.leName.setEnabled(False)
            self.ui.pteDescription.setEnabled(False)
            self.ui.pteContent.setEnabled(False)
        else:
            self.ui.pbSave.setEnabled(True)
            self.ui.leName.setEnabled(True)
            self.ui.pteDescription.setEnabled(True)
            self.ui.pteContent.setEnabled(True)
            
            for plugin in plugins:
                item = QtGui.QListWidgetItem(plugin.name)
                item.setData(QtCore.Qt.UserRole, plugin)
                
                self.ui.lwLocal.addItem(item)
                
            self.ui.lwLocal.setCurrentRow(0)
        
    def reset(self):
        self.ui.leName.setText("")
        self.ui.pteDescription.setPlainText("")
        self.ui.pteContent.setPlainText("")
        
        self.ui.leName.setEnabled(False)
        self.ui.pteDescription.setEnabled(False)
        self.ui.pteContent.setEnabled(False)
        self.ui.pbSave.setEnabled(False)
            
    def updateLocal(self, item, previous):
        if item is None:
            self.reset()
            return
            
        pluginId = item.data(QtCore.Qt.UserRole).pluginId
        plugin = self.pluginService.findOne(pluginId)
        
        if plugin is None:
            self.reset()
            return
        
        self.ui.pbSave.setEnabled(True)
        self.ui.leName.setEnabled(True)
        self.ui.pteDescription.setEnabled(True)
        self.ui.pteContent.setEnabled(True)
        
        self.ui.leName.setText(plugin.name)
        self.ui.pteDescription.setPlainText(plugin.description)
        self.ui.pteContent.setPlainText(plugin.content)
    
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
        
    def add(self):
        name = "New Plugin"
        counter = 1
        
        while self.pluginService.findOneByName(name) is not None:
            name = "New Plugin {0}".format(counter)
            counter += 1
            
        plugin = Plugin()
        plugin.name = name
        plugin.local = True
        plugin.uuid = str(uuid.uuid1())
        self.pluginService.save(plugin)
        
        self.bindLocal()
        self.bindPlugins()
        
    def save(self):
        currentIndex = self.ui.lwLocal.currentIndex()
        item = self.ui.lwLocal.currentItem()
        
        if item is None:
            return
        
        plugin = item.data(QtCore.Qt.UserRole)
        
        if plugin is None:
            return
        
        plugin.name = self.ui.leName.text()
        plugin.description = self.ui.pteDescription.toPlainText()
        plugin.content = self.ui.pteContent.toPlainText()
        
        self.pluginService.save(plugin)
        
        self.bindPlugins()
        self.bindLocal()
        
        self.ui.lwLocal.setCurrentIndex(currentIndex)
        
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
        self.getRemotePlugins()
        self.bindRemote()
                
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
        self.updateRemotePlugins()
        
    def remove(self):
        for index in range(0, self.ui.lwInstalled.count()):
            item = self.ui.lwInstalled.item(index)
             
            if item.checkState()==QtCore.Qt.Checked:
                plugin = item.data(QtCore.Qt.UserRole)
                self.pluginService.delete(plugin.pluginId)
                
        self.bindPlugins()
        self.bindLocal()