from PyQt4 import QtCore, QtGui, Qt

from lib.misc import Application
from lib.models.model import Term, TermState
from lib.services.service import TermService
from ui.views.terms import Ui_Terms

class TermsForm(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Terms()
        self.ui.setupUi(self)
        
        self.termService = TermService()
        self.updateTerms();        
        
    def updateTerms(self):
        self.ui.tTerms.clear()
        headers = ["State", "Language", "Phrase", "Base Phrase", "Sentence"]
        self.ui.tTerms.setColumnCount(len(headers))
        self.ui.tTerms.setHorizontalHeaderLabels(headers)
        self.ui.tTerms.setSortingEnabled(False)
        
        index = 0
        terms = self.termService.findAll()
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
