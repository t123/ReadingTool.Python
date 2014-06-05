import os
from PyQt4 import QtCore, QtGui, Qt

from lib.misc import Time, Application
from lib.stringutil import StringUtil
from lib.models.model import Term, TermState
from lib.services.service import TermService, StorageService
from ui.views.terms import Ui_Terms
from ui.terminfo import TermInfoForm

class TermsForm(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Terms()
        self.ui.setupUi(self)
        
        self.languages = []
        self.filters = []
        self.termCount = 0
        
        self.termService = TermService()
        self.setupContextMenu()
        
        QtCore.QObject.connect(self.ui.leFilter, QtCore.SIGNAL("textChanged(QString)"), self.onTextChanged)
        QtCore.QObject.connect(self.ui.leFilter, QtCore.SIGNAL("returnPressed()"), self.bindTerms)
        QtCore.QObject.connect(self.ui.actionEdit_term, QtCore.SIGNAL("triggered()"), self.editTerm)
        QtCore.QObject.connect(self.ui.actionDelete_term, QtCore.SIGNAL("triggered()"), self.deleteTerm)
        QtCore.QObject.connect(self.ui.actionExport, QtCore.SIGNAL("triggered()"), self.export)

        self.ui.leFilter.setText("limit:1000 ")
    
    def onTextChanged(self, text):
        if text.strip()!="":
            return
        
        self.bindTerms()
        
    def getCount(self):
        return self.termCount
    
    def setFilters(self, languages=[], filters=[]):
        self.languages = languages
        self.filters = filters
        
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
        
    def bindTerms(self):
        self.ui.twTerms.clear()
        headers = ["State", "Language", "Phrase", "Base Phrase", "Sentence"]
        
        self.ui.twTerms.setColumnCount(len(headers))
        self.ui.twTerms.setHorizontalHeaderLabels(headers)
        self.ui.twTerms.setSortingEnabled(True)
         
        filterText = self.ui.leFilter.text() + " " + \
                     " ".join(['"' + i + '"' for i in self.languages]) + " " \
                     " ".join(self.filters)
                     
        index = 0
        terms = self.termService.search(filterText)
        self.ui.twTerms.setRowCount(len(terms))
         
        for term in terms:
            i = QtGui.QTableWidgetItem(TermState.ToString(term.state))
            i.setData(QtCore.Qt.UserRole, term)
            
            if term.state==TermState.Known:
                i.setBackgroundColor(Qt.QColor("#dae5eb"))
            elif term.state==TermState.Unknown:
                i.setBackgroundColor(Qt.QColor("#f5b8a9"))
            elif term.state==TermState.Ignored:
                i.setBackgroundColor(Qt.QColor("#ffe97f"))
 
            self.ui.twTerms.setItem(index, 0, i)
            self.ui.twTerms.setItem(index, 1, QtGui.QTableWidgetItem(term.language))
            self.ui.twTerms.setItem(index, 2, QtGui.QTableWidgetItem(term.phrase))
            self.ui.twTerms.setItem(index, 3, QtGui.QTableWidgetItem(term.basePhrase))
            self.ui.twTerms.setItem(index, 4, QtGui.QTableWidgetItem(term.sentence))
             
            index +=1
         
        self.ui.twTerms.resizeColumnsToContents()
        self.ui.twTerms.horizontalHeader().setStretchLastSection(True)
        self.termCount = len(terms)
        
    def editTerm(self):
        term = self.ui.twTerms.item(self.ui.twTerms.currentRow(), 0)
        
        if term is None:
            return
        
        data = term.data(QtCore.Qt.UserRole) 
        
        if data is None:
            return
        
        termId = data.termId
         
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
        
    def export(self):
        items = []

        for index in range(0, self.ui.twTerms.rowCount()):
            data = self.ui.twTerms.item(index, 0).data(QtCore.Qt.UserRole)

            if data is None:
                continue

            row = []

            row.append(str(data.termId))
            row.append(Time.toLocal(data.created))
            row.append(Time.toLocal(data.modified))
            row.append(data.phrase)
            row.append(data.basePhrase)
            row.append(data.sentence)
            row.append(data.definition.replace("\n", "<br/>"))
            row.append(TermState.ToString(data.state))
            row.append(str(data.languageId))
            row.append(data.language)
            row.append(str(data.itemSourceId))
            row.append(data.itemSource if data.itemSource is not None else "")
            row.append(data.sourceCode)

            try:
                items.append("\t".join(row))
            except Exception as e:
                print(str(e))
                print(row)

        tsv = "\n".join(items)

        directory = StorageService.sfind("last_tsv_directory", uuid=str(Application.user.userId))

        if StringUtil.isEmpty(directory):
            filename = QtGui.QFileDialog.getSaveFileName(parent=self, caption="Save your terms", filter="*.tsv")
        else:
            filename = QtGui.QFileDialog.getSaveFileName(parent=self, caption="Save your terms", filter="*.tsv", directory=directory)

        if filename:
            #path, file = os.path.split(filename)
            StorageService.ssave("last_tsv_directory", filename, str(Application.user.userId))

            with open(filename, "w", encoding="utf-8") as file:
                file.write(tsv)

    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Escape:
            self.ui.leFilter.setText("")
            event.ignore()