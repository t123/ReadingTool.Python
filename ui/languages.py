import re
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
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.languageService = LanguageService()
        self.languageCodeService = LanguageCodeService()
        
        self.hasSaved = False
        self.setLanguageCodes()
        self.setTermExpressions()

        QtCore.QObject.connect(self.ui.actionSave, QtCore.SIGNAL("triggered(bool)"), self.saveLanguage)
        QtCore.QObject.connect(self.ui.actionCancel, QtCore.SIGNAL("triggered(bool)"), self.resetLanguage)
        QtCore.QObject.connect(self.ui.cbTermRegex, QtCore.SIGNAL("currentIndexChanged(int)"), self.onTermRegexChanged)
        
        QtCore.QObject.connect(self.ui.cbTermRegex, QtCore.SIGNAL("editTextChanged(QString)"), self.testRegex)
        
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
            
    def setTermExpressions(self):
        self.ui.cbTermRegex.addItem("Latin Script - apostrophes and hyphens are one word", r"([a-zA-ZÀ-ÖØ-öø-ÿĀ-ſƀ-ɏ\’\'-]+)|(\s+)|(\d+)|(__\d+__)|(<\/?[a-z][A-Z0-9]*[^>]*>)|(.)")
        self.ui.cbTermRegex.addItem("Latin Script - apostrophes and hyphens are separate words", r"([a-zA-ZÀ-ÖØ-öø-ÿĀ-ſƀ-ɏ]+)|(\s+)|(\d+)|(__\d+__)|(<\/?[a-z][A-Z0-9]*[^>]*>)|(.)")
        self.ui.cbTermRegex.addItem("Chinese Script", r"([一-龥]+)|(\s+)|(\d+)|(__\d+__)|(<\/?[a-z][A-Z0-9]*[^>]*>)|(.)")
        self.ui.cbTermRegex.addItem("Cyrillic Script", r"([a-zA-ZÀ-ÖØ-öø-ÿĀ-ſƀ-ɏЀ-ӹ\’'-]+)|(\s+)|(\d+)|(__\d+__)|(<\/?[a-z][A-Z0-9]*[^>]*>)|(.)")
        self.ui.cbTermRegex.addItem("Greek Script", r"([\u0370-\u03FF\u1F00-\u1FFF]+)|(\s+)|(\d+)|(__\d+__)|(<\/?[a-z][A-Z0-9]*[^>]*>)|(.)")
        self.ui.cbTermRegex.addItem("Greek Script", r"([\u0590-\u05FF]+)|(\s+)|(\d+)|(__\d+__)|(<\/?[a-z][A-Z0-9]*[^>]*>)|(.)")
        self.ui.cbTermRegex.addItem("Japanese Script", r"([一-龥ぁ-ヾ]+)|(\s+)|(\d+)|(__\d+__)|(<\/?[a-z][A-Z0-9]*[^>]*>)|(.)")
        self.ui.cbTermRegex.addItem("Korean Script", r"([가-힣ᄀ-ᇂ]+)|(\s+)|(\d+)|(__\d+__)|(<\/?[a-z][A-Z0-9]*[^>]*>)|(.)")
        self.ui.cbTermRegex.addItem("Thai Script", r"([ก-๛]+)|(\s+)|(\d+)|(__\d+__)|(<\/?[a-z][A-Z0-9]*[^>]*>)|(.)")

    def onTermRegexChanged(self, index):
        data = self.ui.cbTermRegex.itemData(index)
        self.ui.cbTermRegex.setEditText(data)
        
    def testRegex(self, regex):
        p = Qt.QPalette()

        try:
            re.compile(regex)
            p.setColor(QtGui.QPalette.Base, QtGui.QColor("#96D899"))
            self.ui.actionSave.setEnabled(True)
            self.ui.pbSave.setEnabled(True)
        except:
            p.setColor(QtGui.QPalette.Base, QtGui.QColor("#FBE3E4"))
            self.ui.actionSave.setEnabled(False)
            self.ui.pbSave.setEnabled(False)
        
        self.ui.cbTermRegex.lineEdit().setPalette(p)
        
    def bindLanguage(self):
        self.ui.leName.setText(self.language.name)
        
        if self.language.languageId==0:
            self.ui.cbTermRegex.setEditText("Pick a script below or enter your own regular expression")
        else:
            self.ui.cbTermRegex.setEditText(self.language.termRegex)
            
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
        self.language.termRegex = self.ui.cbTermRegex.lineEdit().text()
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