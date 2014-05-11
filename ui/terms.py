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
        self.updateCombo()
        self.ui.leFilter.setText("#unknown")
        self.updateTerms()        
        
        QtCore.QObject.connect(self.ui.leFilter, QtCore.SIGNAL("textChanged(QString)"), self.updateTerms)
        QtCore.QObject.connect(self.ui.leFilter, QtCore.SIGNAL("editingFinished()"), self.updateTerms)
        QtCore.QObject.connect(self.ui.cbCollections, QtCore.SIGNAL("currentIndexChanged(int)"), self.onComboItem)
        QtCore.QObject.connect(self.ui.tTerms, QtCore.SIGNAL("itemDoubleClicked(QTableWidgetItem*)"), self.showInfo)
        
    def showInfo(self, data):
        term = self.ui.tTerms.item(self.ui.tTerms.currentRow(), 0)
        termId = term.data(QtCore.Qt.UserRole).termId
        
        self.popup = TermInfoForm()
        self.popup.setTerm(termId)
        self.popup.show() 
        
    def onComboItem(self, index):
        item = self.ui.cbCollections.itemData(index)
        
        if item is None:
            return
        
        self.ui.leFilter.setText(self.ui.leFilter.text() + " " + item)
        self.updateTerms()
            
    def updateCombo(self):
        self.ui.cbCollections.addItem("Known", "#known")
        self.ui.cbCollections.addItem("Not known", "#unknown")
        self.ui.cbCollections.addItem("Ignored", "#ignored")
        
        ls = LanguageService()
        for l in ls.findAll(orderBy="archived"):
            self.ui.cbCollections.addItem(l.name, '"' + l.name + '"')
                
    def updateTerms(self, filter=None):
        if filter is not None and filter!="":
            return
        
        self.ui.tTerms.clear()
        headers = ["State", "Language", "Phrase", "Base Phrase", "Sentence"]
        self.ui.tTerms.setColumnCount(len(headers))
        self.ui.tTerms.setHorizontalHeaderLabels(headers)
        self.ui.tTerms.setSortingEnabled(False)
        
        index = 0
        terms = self.termService.search(self.ui.leFilter.text())
        self.ui.tTerms.setRowCount(len(terms))
        
        for term in terms:
            i = QtGui.QTableWidgetItem(TermState.ToString(term.state))
            i.setData(QtCore.Qt.UserRole, term)

            self.ui.tTerms.setItem(index, 0, i)
            self.ui.tTerms.setItem(index, 1, QtGui.QTableWidgetItem(term.language))
            self.ui.tTerms.setItem(index, 2, QtGui.QTableWidgetItem(term.phrase))
            self.ui.tTerms.setItem(index, 3, QtGui.QTableWidgetItem(term.basePhrase))
            self.ui.tTerms.setItem(index, 4, QtGui.QTableWidgetItem(term.sentence))
            
            index +=1
        
        self.ui.tTerms.resizeColumnsToContents()
        self.ui.tTerms.setSortingEnabled(True)            
