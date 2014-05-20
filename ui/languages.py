from PyQt4 import QtCore, QtGui, Qt

from lib.misc import Application
from lib.models.model import Language, LanguageDirection
from lib.services.service import LanguageService, LanguageCodeService
from ui.views.languages import Ui_Languages

class LanguagesForm(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Languages()
        self.ui.setupUi(self)
        
        QtCore.QObject.connect(self.ui.lvLanguages, QtCore.SIGNAL("currentItemChanged(QListWidgetItem*,QListWidgetItem*)"), self.populateItem)
        QtCore.QObject.connect(self.ui.pbSave, QtCore.SIGNAL("clicked()"), self.saveLanguage)
        QtCore.QObject.connect(self.ui.pbAdd, QtCore.SIGNAL("clicked()"), self.addLanguage)
        QtCore.QObject.connect(self.ui.pbDelete, QtCore.SIGNAL("clicked()"), self.deleteLanguage)
        QtCore.QObject.connect(self.ui.pbCancel, QtCore.SIGNAL("clicked()"), self.cancel)
        QtCore.QObject.connect(self.ui.leName, QtCore.SIGNAL("textChanged(QString)"), self.changed)
        QtCore.QObject.connect(self.ui.leTheme, QtCore.SIGNAL("textChanged(QString)"), self.changed)
        QtCore.QObject.connect(self.ui.leTermRegex, QtCore.SIGNAL("textChanged(QString)"), self.changed)
        QtCore.QObject.connect(self.ui.cbIsArchived, QtCore.SIGNAL("stateChanged(int)"), self.changed)
        QtCore.QObject.connect(self.ui.cbLanguageCodes, QtCore.SIGNAL("currentIndexChanged(int)"), self.changed)
        QtCore.QObject.connect(self.ui.lvPlugins, QtCore.SIGNAL("itemChanged(QListWidgetItem*)"), self.changed)
        
        self.languageService = LanguageService()
        self.languageCodeService = LanguageCodeService()
        self.updateLanguages();
        
        self.ui.splitter.setStretchFactor(0,0)
        self.ui.splitter.setStretchFactor(1,1)        
        
    def _currentLanguage(self):
        if self.ui.lvLanguages.currentItem() is None:
            return None
        
        return self.languageService.findOne(self.ui.lvLanguages.currentItem().data(QtCore.Qt.UserRole).languageId)
        
    def changed(self):
        self.changed = True
        self.ui.pbCancel.setEnabled(True)
        self.ui.pbSave.setEnabled(True)
        self.ui.lvLanguages.setEnabled(False)
        self.ui.pbAdd.setEnabled(False)
        self.ui.pbDelete.setEnabled(False)
        
    def resetForm(self):
        self.changed = False
        self.ui.pbCancel.setEnabled(False)
        self.ui.pbSave.setEnabled(False)
        self.ui.lvLanguages.setEnabled(True)
        self.ui.pbAdd.setEnabled(True)
        self.ui.pbDelete.setEnabled(True)
        
    def cancel(self):
        currentRow = self.ui.lvLanguages.currentRow()
        self.ui.lvLanguages.setCurrentRow(-1)
        self.ui.lvLanguages.setCurrentRow(currentRow)
        self.resetForm()
        
    def populateItem(self, current, previous):
        if current is None:
            return
        
        language = self.languageService.findOne(current.data(QtCore.Qt.UserRole).languageId)
        self.ui.leName.setText(language.name)
        self.ui.leTermRegex.setText(language.termRegex)
        self.ui.cbIsArchived.setChecked(language.isArchived)
        self.ui.leTheme.setText(language.theme)

        index = self.ui.cbLanguageCodes.findData(language.languageCode)
        
        if index<0:
            index = self.ui.cbLanguageCodes.findData("--")
            
        self.ui.cbLanguageCodes.setCurrentIndex(index)
        
        if language.direction==LanguageDirection.LeftToRight:
            self.ui.rbLTR.setChecked(True)
            self.ui.rbRTL.setChecked(False)
        else:
            self.ui.rbLTR.setChecked(False)
            self.ui.rbRTL.setChecked(True)
            
        self.ui.lvPlugins.clear()
        plugins = self.languageService.findAllPlugins(language.languageId)
            
        for plugin in plugins:
            p = QtGui.QListWidgetItem(plugin.name)
            p.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            
            if plugin.enabled:
                p.setCheckState(QtCore.Qt.Checked)
            else:
                p.setCheckState(QtCore.Qt.Unchecked)
                
            p.setData(QtCore.Qt.UserRole, plugin)
            self.ui.lvPlugins.addItem(p)
            
        self.resetForm()
            
    def saveLanguage(self):
        language = None
        
        if self.ui.lvLanguages.currentItem() is None:
            language = Language()
        else:
            language = self._currentLanguage()
                        
        currentRow = self.ui.lvLanguages.currentRow()
        
        language.name = self.ui.leName.text()
        language.termRegex = self.ui.leTermRegex.text()
        language.isArchived = self.ui.cbIsArchived.isChecked()
        language.direction = LanguageDirection.LeftToRight if self.ui.rbLTR.isChecked() else LanguageDirection.RightToLeft
        language.languageCode = self.ui.cbLanguageCodes.itemData(self.ui.cbLanguageCodes.currentIndex())
        language.theme = self.ui.leTheme.text()
        
        plugins = []
        
        for index in range(0, self.ui.lvPlugins.count()):
            item = self.ui.lvPlugins.item(index)
            
            if item.checkState()==QtCore.Qt.Checked:
                data = item.data(QtCore.Qt.UserRole)
                plugins.append(data.pluginId)
                
        self.languageService.save(language, plugins)
        self.updateLanguages()
        self.ui.lvLanguages.setCurrentRow(currentRow)
        self.resetForm()
        
    def deleteLanguage(self):
        language = self._currentLanguage()
        
        if language is None or self.changed:
            return
        
        currentRow = self.ui.lvLanguages.currentRow()
        self.languageService.delete(language.languageId)
        self.updateLanguages()
        
        if currentRow>=self.ui.lvLanguages.count():
            self.ui.lvLanguages.setCurrentRow(self.ui.lvLanguages.count()-1)
        else:
            self.ui.lvLanguages.setCurrentRow(currentRow)
        
        self.resetForm()
        
    def addLanguage(self):
        counter = 1
        name = "New Language"
        
        while self.languageService.findOneByName(name) is not None:
            name = "New Language %d" % counter
            counter += 1
            
        language = Language()
        language.name = name
        language = self.languageService.save(language)
        self.updateLanguages(language.languageId)
        self.resetForm()
        
    def updateLanguages(self, selectedId=None):
        self._updateLanguageCodes()
        languages = self.languageService.findAll()
        
        self.ui.lvLanguages.clear()
        for language in languages:
            item = QtGui.QListWidgetItem(language.name)
            item.setData(QtCore.Qt.UserRole, language)
            self.ui.lvLanguages.addItem(item)
            
            if selectedId is not None and language.languageId==selectedId:
                self.ui.lvPlugins.setCurrentItem(item)
            
        if self.ui.lvLanguages.currentItem() is None and self.ui.lvLanguages.count()>0:
            self.ui.lvLanguages.setCurrentItem(self.ui.lvLanguages.item(0))
            
        if self.ui.lvLanguages.count()==0:
            self.resetForm()
         
    def _updateLanguageCodes(self):
        codes = self.languageCodeService.findAll()
        self.ui.cbLanguageCodes.clear()
        
        for code in codes:
            self.ui.cbLanguageCodes.addItem(code.name, code.code)
            
    def keyPressEvent(self, event):
        if(self._currentLanguage() is None):
            return
        
        if event.key()==QtCore.Qt.Key_Delete:
            self.deleteLanguage()
            return
        
        if event.key()==QtCore.Qt.Key_Escape:
            self.cancel()
            return
            
        if event.modifiers() & QtCore.Qt.ControlModifier:
            if event.key()==QtCore.Qt.Key_S:
                self.saveLanguage()
                return
            
        return QtGui.QDialog.keyPressEvent(self, event)