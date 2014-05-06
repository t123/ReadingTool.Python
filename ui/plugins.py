from PyQt4 import QtCore, QtGui, Qt
from PyQt4.Qsci import QsciScintilla, QsciLexerJavaScript

from lib.misc import Application
from lib.models.model import Plugin
from lib.services.service import PluginService
from ui.views.plugins import Ui_Plugins


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
        
        self.pluginService = PluginService()
        self.updatePlugins();
        
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
        
        lexer = QsciLexerJavaScript()
        lexer.setDefaultFont(font)
        self.ui.teCode.setLexer(lexer)
        #self.ui.teCode.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1, 'Courier')     

    def _currentPlugin(self):
        if self.ui.lvPlugins.currentItem() is None:
            return None
        
        return self.pluginService.findOne(self.ui.lvPlugins.currentItem().data(QtCore.Qt.UserRole).pluginId)
    
    def populateItem(self, current, previous):
        if current is None:
            return
        
        plugin = self.pluginService.findOne(current.data(QtCore.Qt.UserRole).pluginId)
        self.ui.leName.setText(plugin.name)
        self.ui.teDescription.setPlainText(plugin.description)
        self.ui.teCode.setText(plugin.content)
        
    def savePlugin(self):
        if self.ui.lvPlugins.currentItem() is None:
            return
        
        plugin = self._currentPlugin()
        plugin.name = self.ui.leName.text()
        plugin.description = self.ui.teDescription.toPlainText()
        plugin.content = self.ui.teCode.text()
        
        self.pluginService.save(plugin)
        self.updatePlugins()
        
    def deletePlugin(self):
        plugin = self._currentPlugin()
        
        if plugin is None:
            return
        
        self.pluginService.delete(plugin.pluginId)
        self.updatePlugins()
        
    def addPlugin(self):
        counter = 1
        name = "New Plugin"
        
        while self.pluginService.findOneByName(name) is not None:
            name = "New Plugin  %d" % counter
            counter += 1
            
        plugin = Plugin()
        plugin.name = name
        self.pluginService.save(plugin)
        self.updatePlugins()
        
    def updatePlugins(self):
        plugins = self.pluginService.findAll()
        
        self.ui.lvPlugins.clear()
        for plugin in plugins:
            item = QtGui.QListWidgetItem(plugin.name)
            item.setData(QtCore.Qt.UserRole, plugin)
            self.ui.lvPlugins.addItem(item)
        
        if self.ui.lvPlugins.currentItem() is None:
            self.ui.lvPlugins.setCurrentItem(self.ui.lvPlugins.item(0))