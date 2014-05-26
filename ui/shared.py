import logging, time
from PyQt4 import QtCore, QtGui, Qt

from lib.misc import Application
from lib.stringutil import StringUtil
from lib.services.service import StorageService, TermService, LanguageService, SharedTermService
from lib.services.web import WebService
from ui.views.shared import Ui_Shared
from ui.definition import DefinitionForm

class SharedForm(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Shared()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.languages = []
        self.termCount = 0
        self.termService = TermService()
        self.sharedTermService = SharedTermService()
        
        QtCore.QObject.connect(self.ui.pbEnable, QtCore.SIGNAL("clicked()"), self.enableSharing)
        QtCore.QObject.connect(self.ui.pbDisable, QtCore.SIGNAL("clicked()"), self.disableSharing)
        QtCore.QObject.connect(self.ui.pbSync, QtCore.SIGNAL("clicked()"), self.sync)
        QtCore.QObject.connect(self.ui.leFilter, QtCore.SIGNAL("textChanged(QString)"), self.onTextChanged)
        QtCore.QObject.connect(self.ui.leFilter, QtCore.SIGNAL("returnPressed()"), self.bindTerms)
        
        QtCore.QObject.connect(self.ui.twTerms, QtCore.SIGNAL("itemClicked(QTableWidgetItem*)"), self.showDefinition)
        
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
            self.ui.lblMessage.setText("")
            self.ui.pbEnable.show()
            self.ui.pbDisable.hide()
            self.ui.pbSync.hide()
        else:
            self.ui.lblMessage.setText("")
            self.ui.pbEnable.hide()
            self.ui.pbDisable.show()
            self.ui.pbSync.show()
            
    def enableSharing(self):
        StorageService.ssave(StorageService.SHARE_TERMS, "true", Application.user.userId)
        StorageService.sdelete(StorageService.SHARE_TERMS_LAST_SYNC, Application.user.userId)
        self.bindTerms()
        
    def disableSharing(self):
        StorageService.ssave(StorageService.SHARE_TERMS, "false", Application.user.userId)
        StorageService.sdelete(StorageService.SHARE_TERMS_LAST_SYNC, Application.user.userId)
        self.bindTerms()
        
    def showDefinition(self, item):
        i = self.ui.twTerms.item(self.ui.twTerms.currentRow(), 0)
        data = i.data(QtCore.Qt.UserRole)
        
        self.definition = DefinitionForm(data.definition, self.ui.twTerms)
        point = QtGui.QCursor.pos()
        self.definition.move(point.x()+20, point.y());
        self.definition.show()
        
    def bindTerms(self):
        self.setButtons()
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
            terms = self.sharedTermService.search(filterText)
            
        self.ui.twTerms.setRowCount(len(terms))
         
        for term in terms:
            i = QtGui.QTableWidgetItem(term.language)
            i.setData(QtCore.Qt.UserRole, term)
            i.setToolTip(term.definition)
            self.ui.twTerms.setItem(index, 0, i)
            
            i = QtGui.QTableWidgetItem(term.phrase)
            i.setToolTip(term.definition)
            self.ui.twTerms.setItem(index, 1, i)
            
            i = QtGui.QTableWidgetItem(term.basePhrase)
            i.setToolTip(term.definition)
            self.ui.twTerms.setItem(index, 2, i)
            
            i = QtGui.QTableWidgetItem(term.sentence)
            i.setToolTip(term.definition)
            self.ui.twTerms.setItem(index, 3, i)
             
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
        syncTime = time.time()
        
        changedTerms = self.termService.findAlteredPastModifed(lastSync)
        deletedTerms = self.termService.findDeletedPastModifed(lastSync)
        
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
        
        logging.debug("Merged {0} terms".format(len(merged)))
        logging.debug("Syncing terms with server....")

        languageService = LanguageService()
        codes = [l.languageCode for l in languageService.findAll() if l.languageCode!="--"]
        
        webService = WebService()
        newTerms = webService.syncTerms(merged, lastSync, codes)
        
        if newTerms is None:
            logging.debug("Error receiving terms")
            QtGui.QMessageBox.warning(self, "Unable to sync", "There was an error while attempting to sync your words.")
            return
        
        logging.debug("Received {0} terms".format(len(newTerms)))
        self.sharedTermService.update(newTerms)
        
        StorageService.ssave(StorageService.SHARE_TERMS_LAST_SYNC, syncTime, Application.user.userId)
        logging.debug("Sync complete")
        
        self.ui.lblMessage.setText("Sync complete")
        
        self.bindTerms()
        
    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Escape:
            self.ui.leFilter.setText("")
            event.ignore()