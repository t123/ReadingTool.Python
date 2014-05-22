from PyQt4 import QtCore, QtGui, Qt

from lib.misc import Application
from lib.models.model import Term, TermState
from lib.services.service import TermService, LanguageService
from ui.views.terms import Ui_Terms
from ui.terminfo import TermInfoForm

class TermsForm(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Terms()
        self.ui.setupUi(self)
        
        self.termService = TermService()
        self.setupTags()
        self.setupContextMenu()
        
        QtCore.QObject.connect(self.ui.leFilter, QtCore.SIGNAL("textChanged(QString)"), self.onTextChanged)
        QtCore.QObject.connect(self.ui.leFilter, QtCore.SIGNAL("returnPressed()"), self.bindTerms)
        QtCore.QObject.connect(self.ui.cbTags, QtCore.SIGNAL("currentIndexChanged(int)"), self.onTagChanged)
        QtCore.QObject.connect(self.ui.actionEdit_term, QtCore.SIGNAL("triggered()"), self.editTerm)
        QtCore.QObject.connect(self.ui.actionDelete_term, QtCore.SIGNAL("triggered()"), self.deleteTerm)
    
    def onTextChanged(self, text):
        if text.strip()!="":
            return
        
        self.bindTerms()
        
    def onTagChanged(self, index):
        item = self.ui.cbTags.itemData(index)
         
        if item is None:
            return
         
        self.ui.leFilter.setText(self.ui.leFilter.text() + " " + item)
        self.bindTerms()
        
    def setupContextMenu(self):
        self.ui.twTerms.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
         
        action = QtGui.QAction("Edit", self.ui.twTerms)
        action.setShortcut("Enter")
        action.setToolTip("Edit this term")
        self.ui.twTerms.addAction(action)
        QtCore.QObject.connect(action, QtCore.SIGNAL("triggered()"), self.ui.actionEdit_term.trigger)
         
        action = QtGui.QAction("Delete", self.ui.twTerms)
        action.setShortcut("Del")
        action.setToolTip("Delete this term")
        self.ui.twTerms.addAction(action)
        QtCore.QObject.connect(action, QtCore.SIGNAL("triggered()"), self.ui.actionDelete_term.trigger)
        
    def setupTags(self):
        self.ui.cbTags.addItem("Choose a tag", "")
        self.ui.cbTags.addItem("Known", "#known")
        self.ui.cbTags.addItem("Not known", "#unknown")
        self.ui.cbTags.addItem("Ignored", "#ignored")
         
        ls = LanguageService()
        for l in ls.findAll(orderBy="archived"):
            self.ui.cbTags.addItem(l.name, '"' + l.name + '"')

    def bindTerms(self):
        self.ui.twTerms.clear()
        headers = ["State", "Language", "Phrase", "Base Phrase", "Sentence"]
        
        self.ui.twTerms.setColumnCount(len(headers))
        self.ui.twTerms.setHorizontalHeaderLabels(headers)
        self.ui.twTerms.setSortingEnabled(True)
         
        index = 0
        terms = self.termService.search(self.ui.leFilter.text())
        self.ui.twTerms.setRowCount(len(terms))
         
        for term in terms:
            i = QtGui.QTableWidgetItem(TermState.ToString(term.state))
            i.setData(QtCore.Qt.UserRole, term)
 
            self.ui.twTerms.setItem(index, 0, i)
            self.ui.twTerms.setItem(index, 1, QtGui.QTableWidgetItem(term.language))
            self.ui.twTerms.setItem(index, 2, QtGui.QTableWidgetItem(term.phrase))
            self.ui.twTerms.setItem(index, 3, QtGui.QTableWidgetItem(term.basePhrase))
            self.ui.twTerms.setItem(index, 4, QtGui.QTableWidgetItem(term.sentence))
             
            index +=1
         
        self.ui.twTerms.resizeColumnsToContents()
        self.ui.twTerms.horizontalHeader().setStretchLastSection(True)
    
    def editTerm(self):
        term = self.ui.twTerms.item(self.ui.twTerms.currentRow(), 0)
        termId = term.data(QtCore.Qt.UserRole).termId
         
        self.dialog = TermInfoForm()
        self.dialog.setTerm(termId)
        self.dialog.bindTerm()
        self.dialog.exec_()
        
        if self.dialog.hasSaved:
            term = self.dialog.term
            i = QtGui.QTableWidgetItem(TermState.ToString(term.state))
            i.setData(QtCore.Qt.UserRole, term)
            
            index = self.ui.twTerms.currentRow()
            
            self.ui.twTerms.setItem(index, 0, i)
            self.ui.twTerms.setItem(index, 1, QtGui.QTableWidgetItem(term.language))
            self.ui.twTerms.setItem(index, 2, QtGui.QTableWidgetItem(term.phrase))
            self.ui.twTerms.setItem(index, 3, QtGui.QTableWidgetItem(term.basePhrase))
            self.ui.twTerms.setItem(index, 4, QtGui.QTableWidgetItem(term.sentence))
            
    def deleteTerm(self):
        term = self.ui.twTerms.item(self.ui.twTerms.currentRow(), 0)
        termId = term.data(QtCore.Qt.UserRole).termId
        self.termService.delete(termId)
        self.ui.twTerms.removeRow(self.ui.twTerms.currentRow())
        
    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Escape:
            self.ui.leFilter.setText("")
            event.ignore()