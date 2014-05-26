import logging, time
from PyQt4 import QtCore, QtGui, Qt

from lib.misc import Application
from lib.services.service import StorageService, LanguageService, TermService, SharedTermService
from lib.services.web import WebService
from ui.views.syncmodal import Ui_SyncModal

class SyncModalForm(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        
        self.ui = Ui_SyncModal()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFixedSize(self.size())
        self.ui.pbClose.setEnabled(False)
        self.ui.progressBar.setMinimum(0)
        self.ui.progressBar.setMaximum(100)
        
        QtCore.QObject.connect(self.ui.pbClose, QtCore.SIGNAL("clicked()"), self.close)
        
        self.isDone = False
        
    def closeEvent(self, event):
        if self.isDone:
            event.accept()
        else:
            event.ignore()
        
    def exec_(self):
        self.start()
        QtGui.QDialog.exec_(self)
        
    def setMessage(self, percent, message):
        self.ui.progressBar.setValue(percent)
        self.ui.pteMessage.appendPlainText(message)
        
    def finished(self):
        self.setMessage(100, "Sync complete")
        self.syncThread.wait()
        self.syncThread.deleteLater()
        self.ui.pbClose.setEnabled(True)
        self.isDone = True
        
    def start(self):
        self.isDone = False
        
        thread = SyncThread(self)
        thread.trigger.connect(self.setMessage)
        thread.finished.connect(self.finished)
        thread.start()
        
        self.syncThread = thread
        
class SyncThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(int, str)

    def __init__(self, parent=None):
        super(SyncThread, self).__init__(parent)
        logging.debug("Syncing __init__")
        
    def run(self):
        logging.debug("Syncing __run__")
        
        self.termService = TermService()
        self.sharedTermService = SharedTermService()
        self.languageService = LanguageService()
        self.webService = WebService()
        
        self.trigger.emit(0, "Sync is starting")

        lastSync = float(StorageService.sfind(StorageService.SHARE_TERMS_LAST_SYNC, 0, Application.user.userId))
        syncTime = time.time()
        
        changedTerms = self.termService.findAlteredPastModifed(lastSync)
        deletedTerms = self.termService.findDeletedPastModifed(lastSync)
            
        merged = { }
        
        self.trigger.emit(10, "Collecting local terms")
        
        for term in changedTerms:
            merged[term.termId] =  {
                                    "id": term.termId,
                                    "code": term.language,
                                    "source": term.sourceCode,
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
        
        self.trigger.emit(20, "Getting language codes")
        
        codes = [l.languageCode for l in self.languageService.findAll() if l.languageCode!="--"]
        acceptable = [l.sourceCode for l in self.languageService.findAll() if l.languageCode!="--"]
        
        self.trigger.emit(30, "Sending {0} terms to server".format(len(merged)))
        self.trigger.emit(30, "Asking for languages: " + ",".join(codes))
        self.trigger.emit(30, "with definitions in: " + ",".join(acceptable))
        
        newTerms = self.webService.syncTerms(merged, lastSync, codes, acceptable)
        
        if newTerms is None:
            logging.debug("Error receiving terms")
            QtGui.QMessageBox.warning(self, "Unable to sync", "There was an error while attempting to sync your words.")
            self.finished.emit()
            return
        
        self.trigger.emit(50, "Received {0} terms from server".format(len(newTerms)))
        logging.debug("Received {0} terms".format(len(newTerms)))
        self.sharedTermService.update(newTerms)
        
        self.trigger.emit(99, "Finishing...")
        StorageService.ssave(StorageService.SHARE_TERMS_LAST_SYNC, syncTime, Application.user.userId)
        logging.debug("Sync complete")
        
        