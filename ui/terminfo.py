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
        
        self.ui.cbState.addItem("Known", TermState.Known)
        self.ui.cbState.addItem("Unknown", TermState.Unknown)
        self.ui.cbState.addItem("Ignored", TermState.Ignored)
        
        QtCore.QObject.connect(self.ui.actionSave, QtCore.SIGNAL("triggered()"), self.saveTerm)
        QtCore.QObject.connect(self.ui.actionCancel, QtCore.SIGNAL("triggered()"), self.resetTerm)
        
        self.ui.leBasePhrase.setFocus()
        self.hasSaved = False
        
    def setTerm(self, termId=None):
        if termId is None or termId==0:
            self.term = Term()
            self.setWindowTitle("Add a new term")
        else:
            self.term = self.termService.findOne(termId)
            self.setWindowTitle("Edit term - {0}".format(self.term.phrase))
        
    def bindTerm(self):
        self.ui.lblCreated.setText(Time.toLocal(self.term.created))
        self.ui.lblCreated.setToolTip(Time.toHuman(self.term.created))        
        self.ui.lblModified.setText(Time.toLocal(self.term.modified))
        self.ui.lblModified.setToolTip(Time.toHuman(self.term.modified))
        self.ui.lePhrase.setText(self.term.phrase)        
        self.ui.leBasePhrase.setText(self.term.basePhrase)
        self.ui.leSentence.setText(self.term.sentence)
        self.ui.pteDefinition.setPlainText(self.term.definition)
        self.ui.leLanguage.setText(self.term.language)
        self.ui.leItemSource.setText(self.term.itemSource)
        
        self.ui.cbState.setCurrentIndex(self.ui.cbState.findData(self.term.state))
        
        history = self.termService.findHistory(self.term.termId)
        self.ui.twHistory.clear()
        
        headers = ["Date", "When", "State", "Type"]
        self.ui.twHistory.setColumnCount(len(headers))
        self.ui.twHistory.setHorizontalHeaderLabels(headers)
        self.ui.twHistory.setSortingEnabled(True)
        self.ui.twHistory.setRowCount(len(history))
        
        index = 0
        for item in history:
            self.ui.twHistory.setItem(index, 0, QtGui.QTableWidgetItem(Time.toLocal(item.entryDate)))
            self.ui.twHistory.setItem(index, 1, QtGui.QTableWidgetItem(Time.toHuman(item.entryDate)))
            self.ui.twHistory.setItem(index, 2, QtGui.QTableWidgetItem(TermState.ToString(item.state)))
            self.ui.twHistory.setItem(index, 3, QtGui.QTableWidgetItem(TermType.ToString(item.type)))
            
            index += 1
            
        self.ui.twHistory.resizeColumnsToContents()
        self.ui.twHistory.horizontalHeader().setStretchLastSection(True)
        
    def saveTerm(self):
        self.term.basePhrase = self.ui.leBasePhrase.text()
        self.term.definition = self.ui.pteDefinition.toPlainText()
        self.term.sentence = self.ui.leSentence.text()
        self.term.state = self.ui.cbState.itemData(self.ui.cbState.currentIndex())
        
        self.term = self.termService.save(self.term)
        self.setTerm(self.term.termId)
        self.bindTerm()
        
        self.hasSaved = True
        
    def resetTerm(self):
        self.setTerm(self.term.termId)
        self.bindTerm()
        
    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Escape:
            self.close()