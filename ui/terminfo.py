from PyQt4 import QtCore, QtGui, Qt

from lib.misc import Application, Time
from lib.models.model import Term, TermState, TermType
from lib.services.service import TermService, LanguageService
from ui.views.terminfo import Ui_TermInfo

class TermInfoForm(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_TermInfo()
        self.ui.setupUi(self)
        
        self.termService = TermService()
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.Popup)
        
        self.ui.cbState.addItem("Known", TermState.Known)
        self.ui.cbState.addItem("Unknown", TermState.Unknown)
        self.ui.cbState.addItem("Ignored", TermState.Ignored)
        
        QtCore.QObject.connect(self.ui.pbSave, QtCore.SIGNAL("clicked()"), self.saveTerm)
        QtCore.QObject.connect(self.ui.pbDelete, QtCore.SIGNAL("clicked()"), self.deleteTerm)
        
    def saveTerm(self):
        term = self.termService.findOne(self.termId)
        
        term.basePhrase = self.ui.leBasePhrase.text()
        term.definition = self.ui.pteDefinition.toPlainText()
        term.sentence = self.ui.leSentence.text()
        term.state = self.ui.cbState.itemData(self.ui.cbState.currentIndex())
        
        self.termService.save(term)
        self.setTerm(self.termId)
        
    def deleteTerm(self):
        self.termService.delete(self.termId)
        self.close()
        
    def setTerm(self, termId):
        self.termId = termId
        term = self.termService.findOne(termId)
        
        if term is None:
            return
        
        self.ui.lblCreated.setText(Time.toLocal(term.created))        
        self.ui.lblModified.setText(Time.toLocal(term.modified))
        self.ui.lePhrase.setText(term.phrase)        
        self.ui.leBasePhrase.setText(term.basePhrase)
        self.ui.leSentence.setText(term.sentence)
        self.ui.pteDefinition.setPlainText(term.definition)
        self.ui.leLanguage.setText(term.language)
        self.ui.leItemSource.setText(term.itemSource)
        
        self.ui.cbState.setCurrentIndex(self.ui.cbState.findData(term.state))
        
        history = self.termService.findHistory(termId)
        self.ui.twHistory.clear()
        headers = ["Date", "State", "Type"]
        self.ui.twHistory.setColumnCount(len(headers))
        self.ui.twHistory.setHorizontalHeaderLabels(headers)
        self.ui.twHistory.setSortingEnabled(True)
        self.ui.twHistory.setRowCount(len(history))
        
        index = 0
        for item in history:
            self.ui.twHistory.setItem(index, 0, QtGui.QTableWidgetItem(Time.toLocal(item.entryDate)))
            self.ui.twHistory.setItem(index, 1, QtGui.QTableWidgetItem(TermState.ToString(item.state)))
            self.ui.twHistory.setItem(index, 2, QtGui.QTableWidgetItem(TermType.ToString(item.type)))
            
            index += 1
            
        self.ui.twHistory.horizontalHeader().setResizeMode(Qt.QHeaderView.Stretch)