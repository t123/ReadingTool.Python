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

        self.languageService = LanguageService()
        self.languageCodeService = LanguageCodeService()
        
        self.hasSaved = False
        self.setLanguageCodes()

        QtCore.QObject.connect(self.ui.actionSave, QtCore.SIGNAL("triggered(bool)"), self.saveLanguage)
        QtCore.QObject.connect(self.ui.actionCancel, QtCore.SIGNAL("triggered(bool)"), self.resetLanguage)
        
    def setLanguage(self, id=None):
        if id==0 or id is None:
            self.language = Language()
            self.setWindowTitle("Add a new language")
        else:
            self.language = self.languageService.findOne(id)
            self.setWindowTitle("Edit language - {0}".format(self.language.name))
            
    def setLanguageCodes(self):
        codes = self.languageCodeService.findAll()
        self.ui.cbLanguageCodes.clear()
         
        for code in codes:
            self.ui.cbLanguageCodes.addItem(code.name, code.code)

    def bindLanguage(self):
        self.ui.leName.setText(self.language.name)
        #self.ui.leTermRegex.setText(self.language.termRegex)
        self.ui.cbIsArchived.setChecked(self.language.isArchived)
        self.ui.leTheme.setText(self.language.theme)
 
        index = self.ui.cbLanguageCodes.findData(self.language.languageCode)
         
        if index<0:
            index = self.ui.cbLanguageCodes.findData("--")
             
        self.ui.cbLanguageCodes.setCurrentIndex(index)
         
        if self.language.direction==LanguageDirection.LeftToRight:
            self.ui.rbLTR.setChecked(True)
            self.ui.rbRTL.setChecked(False)
        else:
            self.ui.rbLTR.setChecked(False)
            self.ui.rbRTL.setChecked(True)
             
        self.ui.lwPlugins.clear()
        plugins = self.languageService.findAllPlugins(self.language.languageId)
             
        for plugin in plugins:
            p = QtGui.QListWidgetItem(plugin.name)
            p.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
             
            if plugin.enabled:
                p.setCheckState(QtCore.Qt.Checked)
            else:
                p.setCheckState(QtCore.Qt.Unchecked)
                 
            p.setData(QtCore.Qt.UserRole, plugin)
            self.ui.lwPlugins.addItem(p)
             
        self.ui.leName.setFocus()
                     
    def saveLanguage(self):
        self.language.name = self.ui.leName.text()
        #self.language.termRegex = self.ui.leTermRegex.text()
        self.language.isArchived = self.ui.cbIsArchived.isChecked()
        self.language.direction = LanguageDirection.LeftToRight if self.ui.rbLTR.isChecked() else LanguageDirection.RightToLeft
        self.language.languageCode = self.ui.cbLanguageCodes.itemData(self.ui.cbLanguageCodes.currentIndex())
        self.language.theme = self.ui.leTheme.text()
         
        plugins = []
         
        for index in range(0, self.ui.lwPlugins.count()):
            item = self.ui.lwPlugins.item(index)
             
            if item.checkState()==QtCore.Qt.Checked:
                data = item.data(QtCore.Qt.UserRole)
                plugins.append(data.pluginId)
                 
        self.language = self.languageService.save(self.language, plugins)
        self.setLanguage(self.language.languageId)
        self.hasSaved = True

    def resetLanguage(self):
        self.setLanguage(self.language.languageId)
        self.bindLanguage()