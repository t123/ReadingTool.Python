import os, json
from PyQt4 import QtCore, QtGui, Qt
from PyQt4.Qsci import QsciScintilla, QsciLexerJavaScript

from lib.misc import Application
from lib.stringutil import StringUtil
from lib.models.model import Plugin
from lib.services.service import PluginService
from ui.views.plugins import Ui_Plugins
from PyQt4.Qt import QFileDialog


class PluginsForm(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Plugins()
        self.ui.setupUi(self)
        
        self._setupCode()
        
        QtCore.QObject.connect(self.ui.lvPlugins, QtCore.SIGNAL("currentItemChanged(QListWidgetItem*,QListWidgetItem*)"), self.populateItem)
        QtCore.QObject.connect(self.ui.pbSave, QtCore.SIGNAL("clicked()"), self.savePlugin)
        QtCore.QObject.connect(self.ui.pbAdd, QtCore.SIGNAL("clicked()"), self.addPlugin)
        QtCore.QObject.connect(self.ui.pbDelete, QtCore.SIGNAL("clicked()"), self.deletePlugin)
        QtCore.QObject.connect(self.ui.pbCancel, QtCore.SIGNAL("clicked()"), self.cancel)
        QtCore.QObject.connect(self.ui.leName, QtCore.SIGNAL("textChanged(QString)"), self.changed)
        QtCore.QObject.connect(self.ui.teDescription, QtCore.SIGNAL("textChanged()"), self.changed)
        QtCore.QObject.connect(self.ui.teCode, QtCore.SIGNAL("textChanged()"), self.changed)
        QtCore.QObject.connect(self.ui.tbExport, QtCore.SIGNAL("clicked()"), self.exportPlugins)
                
        self.setupExportImport()
        self.pluginService = PluginService()
        self.updatePlugins();
        
        self.ui.splitter.setStretchFactor(0,0)
        self.ui.splitter.setStretchFactor(1,1)
        
    def _setupCode(self):
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.ui.teCode.setFont(font)
        self.ui.teCode.setMarginsFont(font)
        
        fontmetrics = QtGui.QFontMetrics(font)
        self.ui.teCode.setMarginsFont(font)
        self.ui.teCode.setMarginWidth(0, fontmetrics.width("00000"))
        self.ui.teCode.setMarginLineNumbers(0, True)
        self.ui.teCode.setMarginsBackgroundColor(QtGui.QColor("#cccccc"))
        
        self.ui.teCode.setCaretLineVisible(True)
        self.ui.teCode.setCaretLineBackgroundColor(QtGui.QColor("#ffe4e4"))
        self.ui.teCode.setAutoIndent(True)
        
        lexer = QsciLexerJavaScript()
        lexer.setDefaultFont(font)
        self.ui.teCode.setLexer(lexer)

    def _currentPlugin(self):
        if self.ui.lvPlugins.currentItem() is None:
            return None
        
        return self.pluginService.findOne(self.ui.lvPlugins.currentItem().data(QtCore.Qt.UserRole).pluginId)
    
    def setupExportImport(self):
        menu = QtGui.QMenu()
        
        action = QtGui.QAction(self)
        action.setText("Import plugins")
        action.connect(action, QtCore.SIGNAL("triggered()"), self.importPlugins)
        menu.addAction(action)
        self.ui.tbExport.setMenu(menu)
        
    def exportPlugins(self):
        path = QFileDialog.getExistingDirectory()
        
        if StringUtil.isEmpty(path):
            return
    
        for plugin in self.pluginService.findAll():
            filename = str(plugin.uuid) + ".js"
            
            with open (os.path.join(path, filename), "w") as file:
                t = {
                     "name": plugin.name,
                     "uuid": str(plugin.uuid),
                     "description": plugin.description,
                     "content": plugin.content
                     }
                
                file.write(json.dumps(t))
                
        QtGui.QMessageBox.information(self, "Export complete", "All plugins were exported.")
    
    def importPlugins(self):
        path = QFileDialog.getExistingDirectory()
        
        if StringUtil.isEmpty(path):
            return
        
        files = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]
        
        count = 0
        for filename in files:
            try:
                with open (os.path.join(path, filename), "r") as file:
                    content = json.load(file)
                    plugin = self.pluginService.findOneByName(content["name"])
                    
                    if plugin is None:
                        plugin = Plugin()
                    
                    plugin.content = content["content"]
                    plugin.name = content["name"]
                    plugin.description = content["description"]
                    plugin.uuid = content["uuid"]
                    
                    self.pluginService.save(plugin)
                    count +=1
            except Exception as e:
                continue
            
        self.updatePlugins()
        self.ui.lvPlugins.setCurrentRow(0)
        self.resetForm()
        QtGui.QMessageBox.information(self, "Import complete", "{0} of {1} plugins were imported.".format(count, len(files)))
                
    def changed(self):
        self.ui.pbCancel.setEnabled(True)
        self.ui.pbSave.setEnabled(True)
        self.ui.lvPlugins.setEnabled(False)
        self.ui.pbAdd.setEnabled(False)
        self.ui.pbDelete.setEnabled(False)
        self.changed = True
        
    def resetForm(self):
        self.ui.pbCancel.setEnabled(False)
        self.ui.pbSave.setEnabled(False)
        self.ui.lvPlugins.setEnabled(True)
        self.ui.pbAdd.setEnabled(True)
        self.ui.pbDelete.setEnabled(True)
        self.changed = False
        
    def cancel(self):
        currentRow = self.ui.lvPlugins.currentRow()
        self.ui.lvPlugins.setCurrentRow(-1)
        self.ui.lvPlugins.setCurrentRow(currentRow)
        self.resetForm()
        
    def populateItem(self, current, previous):
        if current is None:
            return
        
        plugin = self.pluginService.findOne(current.data(QtCore.Qt.UserRole).pluginId)
        self.ui.leName.setText(plugin.name)
        self.ui.leUUID.setText(plugin.uuid)
        self.ui.teDescription.setPlainText(plugin.description)
        self.ui.teCode.setText(plugin.content)
        
        self.resetForm()
        
    def savePlugin(self):
        plugin = None
        
        if self.ui.lvPlugins.currentItem() is None:
            plugin = Plugin()
        else:
            plugin = self._currentPlugin()            
        
        currentRow = self.ui.lvPlugins.currentRow()
        
        plugin.name = self.ui.leName.text()
        plugin.description = self.ui.teDescription.toPlainText()
        plugin.content = self.ui.teCode.text()
        
        self.pluginService.save(plugin)
        self.updatePlugins()
        self.ui.lvPlugins.setCurrentRow(currentRow)
        
        self.resetForm()
        
    def deletePlugin(self):
        plugin = self._currentPlugin()
        
        if plugin is None or self.changed:
            return
        
        currentRow = self.ui.lvPlugins.currentRow()
        self.pluginService.delete(plugin.pluginId)
        self.updatePlugins()
        
        if currentRow>=self.ui.lvPlugins.count():
            self.ui.lvPlugins.setCurrentRow(self.ui.lvPlugins.count()-1)
        else:
            self.ui.lvPlugins.setCurrentRow(currentRow)
            
        self.resetForm()
        
    def addPlugin(self):
        counter = 1
        name = "New Plugin"
        
        while self.pluginService.findOneByName(name) is not None:
            name = "New Plugin  %d" % counter
            counter += 1
            
        plugin = Plugin()
        plugin.name = name
        plugin = plugin = self.pluginService.save(plugin)
        self.updatePlugins(plugin.pluginId)
        
        self.resetForm()
        
    def updatePlugins(self, selectedId=None):
        plugins = self.pluginService.findAll()
        
        self.ui.lvPlugins.clear()
        for plugin in plugins:
            item = QtGui.QListWidgetItem(plugin.name)
            item.setData(QtCore.Qt.UserRole, plugin)
                
            self.ui.lvPlugins.addItem(item)
            
            if selectedId is not None and plugin.pluginId==selectedId:
                self.ui.lvPlugins.setCurrentItem(item)
                
        if self.ui.lvPlugins.currentItem() is None and self.ui.lvPlugins.count()>0:
            self.ui.lvPlugins.setCurrentItem(self.ui.lvPlugins.item(0))
            
    def keyPressEvent(self, event):
        if(self._currentPlugin() is None):
            return
        
        if event.key()==QtCore.Qt.Key_Delete:
            self.deletePlugin()
            return
        
        if event.key()==QtCore.Qt.Key_Escape:
            self.cancel()
            return
            
        if event.modifiers() & QtCore.Qt.ControlModifier:
            if event.key()==QtCore.Qt.Key_S:
                self.savePlugin()
                return
            
        return QtGui.QDialog.keyPressEvent(self, event)