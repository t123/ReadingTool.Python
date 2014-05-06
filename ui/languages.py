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
        
        self.languageService = LanguageService()
        self.languageCodeService = LanguageCodeService()
        self.updateLanguages();        
        
    def _currentLanguage(self):
        if self.ui.lvLanguages.currentItem() is None:
            return None
        
        return self.languageService.findOne(self.ui.lvLanguages.currentItem().data(QtCore.Qt.UserRole).languageId)
        
    def populateItem(self, current, previous):
        if current is None:
            return
        
        language = self.languageService.findOne(current.data(QtCore.Qt.UserRole).languageId)
        self.ui.leName.setText(language.name)
        self.ui.leSentenceRegex.setText(language.sentenceRegex)
        self.ui.leTermRegex.setText(language.termRegex)
        self.ui.cbIsArchived.setChecked(language.isArchived)

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
            
    def saveLanguage(self):
        if self.ui.lvLanguages.currentItem() is None:
            return
        
        language = self._currentLanguage()
        language.name = self.ui.leName.text()
        language.sentenceRegex = self.ui.leSentenceRegex.text()
        language.termRegex = self.ui.leTermRegex.text()
        language.isArchived = self.ui.cbIsArchived.isChecked()
        language.direction = LanguageDirection.LeftToRight if self.ui.rbLTR.isChecked() else LanguageDirection.RightToLeft
        language.languageCode = self.ui.cbLanguageCodes.itemData(self.ui.cbLanguageCodes.currentIndex())
        
        self.languageService.save(language)
        self.updateLanguages()
        
    def deleteLanguage(self):
        language = self._currentLanguage()
        
        if language is None:
            return
        
        self.languageService.delete(language.languageId)
        self.updateLanguages()
        
    def addLanguage(self):
        counter = 1
        name = "New Language"
        
        while self.languageService.findOneByName(name) is not None:
            name = "New Language %d" % counter
            counter += 1
            
        language = Language()
        language.name = name
        self.languageService.save(language)
        self.updateLanguages()
        
    def updateLanguages(self):
        self._updateLanguageCodes()
        languages = self.languageService.findAll()
        
        self.ui.lvLanguages.clear()
        for language in languages:
            item = QtGui.QListWidgetItem(language.name)
            item.setData(QtCore.Qt.UserRole, language)
            self.ui.lvLanguages.addItem(item)
        
        if self.ui.lvLanguages.currentItem() is None:
            self.ui.lvLanguages.setCurrentItem(self.ui.lvLanguages.item(0))
            
    def _updateLanguageCodes(self):
        codes = self.languageCodeService.findAll()
        self.ui.cbLanguageCodes.clear()
        
        for code in codes:
            self.ui.cbLanguageCodes.addItem(code.name, code.code)