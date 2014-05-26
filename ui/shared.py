import logging, time
from PyQt4 import QtCore, QtGui, Qt

from lib.misc import Application
from lib.stringutil import StringUtil
from lib.services.service import StorageService, TermService, LanguageService
from lib.services.web import WebService
from ui.views.shared import Ui_Shared

class SharedForm(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Shared()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.languages = []
        self.termCount = 0
        self.termService = TermService()
        
        QtCore.QObject.connect(self.ui.pbEnable, QtCore.SIGNAL("clicked()"), self.enableSharing)
        QtCore.QObject.connect(self.ui.pbDisable, QtCore.SIGNAL("clicked()"), self.disableSharing)
        QtCore.QObject.connect(self.ui.pbSync, QtCore.SIGNAL("clicked()"), self.sync)
        QtCore.QObject.connect(self.ui.leFilter, QtCore.SIGNAL("textChanged(QString)"), self.onTextChanged)
        QtCore.QObject.connect(self.ui.leFilter, QtCore.SIGNAL("returnPressed()"), self.bindTerms)
        
        self.setButtons()
        
    def setFilters(self, languages=[]):
        self.languages = languages
        self.ui.leFilter.setText("limit:1000 ")

    def onTextChanged(self, text):
        if text.strip()!="":
            return
        
        self.bindTerms()
        
    def getCount(self):
        return self.termCount
    
    def isSyncEnabled(self):
        return StringUtil.isTrue(StorageService.sfind(StorageService.SHARE_TERMS, "false", Application.user.userId))
    
    def setButtons(self):
        if not self.isSyncEnabled():
            self.ui.pbEnable.show()
            self.ui.pbDisable.hide()
            self.ui.pbSync.hide()
        else:
            self.ui.pbEnable.hide()
            self.ui.pbDisable.show()
            self.ui.pbSync.show()
            
    def enableSharing(self):
        StorageService.ssave(StorageService.SHARE_TERMS, "true", Application.user.userId)
        StorageService.sdelete(StorageService.SHARE_TERMS_LAST_SYNC, Application.user.userId)
        self.bindTerms()
        self.setButtons()
        
    def disableSharing(self):
        result = QtGui.QMessageBox.question(self, "Disable Sharing", "If you disable sharing all your shared terms will be deleted.", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        
        if result==QtGui.QMessageBox.No:
            return
        
        StorageService.ssave(StorageService.SHARE_TERMS, "false", Application.user.userId)
        StorageService.sdelete(StorageService.SHARE_TERMS_LAST_SYNC, Application.user.userId)
        self.termService.deleteSharedTerms()
        self.bindTerms()
        self.setButtons()
        
    def bindTerms(self):
        self.ui.twTerms.clear()
        headers = ["Language", "Phrase", "Base Phrase", "Sentence"]
        
        self.ui.twTerms.setColumnCount(len(headers))
        self.ui.twTerms.setHorizontalHeaderLabels(headers)
        self.ui.twTerms.setSortingEnabled(True)
         
        filterText = self.ui.leFilter.text() + " " + \
                     " ".join(['"' + i + '"' for i in self.languages])
                     
        index = 0
        
        if not self.isSyncEnabled():
            terms = []
        else:
            terms = self.termService.searchSharedTerms(filterText)
            
        self.ui.twTerms.setRowCount(len(terms))
         
        for term in terms:
            i = QtGui.QTableWidgetItem(term.language)
            i.setData(QtCore.Qt.UserRole, term)
            
            self.ui.twTerms.setItem(index, 0, i)
            self.ui.twTerms.setItem(index, 1, QtGui.QTableWidgetItem(term.phrase))
            self.ui.twTerms.setItem(index, 2, QtGui.QTableWidgetItem(term.basePhrase))
            self.ui.twTerms.setItem(index, 3, QtGui.QTableWidgetItem(term.sentence))
             
            index +=1
         
        self.ui.twTerms.resizeColumnsToContents()
        self.ui.twTerms.horizontalHeader().setStretchLastSection(True)
        self.termCount = len(terms)
    
    def sync(self):
        if not self.isSyncEnabled():
            return
        
        self.ui.lblMessage.setText("Sync starting")
        logging.debug("Syncing...")
        
        lastSync = float(StorageService.sfind(StorageService.SHARE_TERMS_LAST_SYNC, 0, Application.user.userId))
        
        changedTerms = self.termService.findAlteredPastModifed(lastSync)
        deletedTerms = self.termService.findDeletedPastModifed(lastSync)
        
        lastSync = time.time()
        merged = { }
        
        for term in changedTerms:
            merged[term.termId] =  {
                                    "id": term.termId,
                                    "code": term.language,
                                    "phrase": term.phrase,
                                    "basePhrase": term.basePhrase,
                                    "sentence": term.sentence,
                                    "definition": term.definition,
                                    "modified": term.modified
                                   }             
            
        for term in deletedTerms:
            if term.termId in merged and "modified" in merged[term.termId]:
                if term.entryDate>merged[term.termId]["modified"]:
                    merged[term.termId] = {
                                           "id": term.termId,
                                           "code": "del"
                                           }
            else:
                merged[term.termId] = {
                                           "id": term.termId,
                                           "code": "del"
                                           }
        
        logging.debug("Syncing terms with server....")

        languageService = LanguageService()
        codes = [l.languageCode for l in languageService.findAll() if l.languageCode!="--"]
        
        webService = WebService()
        newTerms = webService.syncTerms(merged, lastSync, codes)
        self.termService.updateSharedTerms(newTerms)
        
        StorageService.ssave(StorageService.SHARE_TERMS_LAST_SYNC, lastSync, Application.user.userId)
        logging.debug("Sync complete")
        
        self.ui.lblMessage.setText("Sync complete")
        
        self.bindTerms()