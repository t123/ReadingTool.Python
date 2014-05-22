from PyQt4 import QtCore, QtGui, Qt

from lib.misc import Application, Time
from lib.stringutil import StringUtil
from lib.models.model import Item, ItemType
from lib.services.service import ItemService, LanguageService
from lib.services.web import WebService
from ui.views.items import Ui_Items
from ui.itemdialog import ItemDialogForm
from ui.reader import ReaderWindow
from PyQt4.Qt import QAction

class ItemsForm(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Items()
        self.ui.setupUi(self)
        
        self.languages = []
        self.collectionNames = []
        self.filters = []
        
        self.itemService = ItemService()
        self.setupContextMenu()
        
        QtCore.QObject.connect(self.ui.leFilter, QtCore.SIGNAL("textChanged(QString)"), self.onTextChanged)
        QtCore.QObject.connect(self.ui.leFilter, QtCore.SIGNAL("returnPressed()"), self.bindItems)
        
        QtCore.QObject.connect(self.ui.actionEdit_item, QtCore.SIGNAL("triggered()"), self.editItem)
        QtCore.QObject.connect(self.ui.actionDelete_item, QtCore.SIGNAL("triggered()"), self.deleteItem)
        QtCore.QObject.connect(self.ui.actionCopy_item, QtCore.SIGNAL("triggered()"), self.copyItem)
        QtCore.QObject.connect(self.ui.actionRead_item, QtCore.SIGNAL("triggered()"), lambda: self.readItem(False))
        QtCore.QObject.connect(self.ui.actionRead_in_parallel, QtCore.SIGNAL("triggered()"), lambda: self.readItem(True))
        QtCore.QObject.connect(self.ui.actionCreate_PDF, QtCore.SIGNAL("triggered()"), self.createPdf)

    def onTextChanged(self, text):
        if text.strip()!="":
            return
        
        self.bindItems()
        
    def setFilters(self, languages=[], collectionNames=[], filters=[]):
        self.languages = languages
        self.collectionNames = collectionNames
        self.filters = filters
        
    def bindItems(self):
        self.ui.twItems.clear()
        headers = ["Language", "Collection Name", "No", "Title", "Read", "Listened", "Last Read", "Media?", "Parallel"]
        
        self.ui.twItems.setColumnCount(len(headers))
        self.ui.twItems.setHorizontalHeaderLabels(headers)
        self.ui.twItems.setSortingEnabled(True)
         
        filterText = self.ui.leFilter.text() + " " + \
                     " ".join(['"' + i + '"' for i in self.languages]) + " " \
                     " ".join(['"' + i + '"' for i in self.collectionNames]) + " " \
                     " ".join(self.filters)
                     
        index = 0
        items = self.itemService.search(filterText)
        self.ui.twItems.setRowCount(len(items))
         
        for item in items:
            i = QtGui.QTableWidgetItem(item.l1Language)
            i.setData(QtCore.Qt.UserRole, item)
             
            self.ui.twItems.setItem(index, 0, i)
            self.ui.twItems.setItem(index, 1, QtGui.QTableWidgetItem(item.collectionName))
            self.ui.twItems.setItem(index, 2, QtGui.QTableWidgetItem(str(item.collectionNo) if item.collectionNo is not None else ""))
            self.ui.twItems.setItem(index, 3, QtGui.QTableWidgetItem(item.l1Title))
            self.ui.twItems.setItem(index, 4, QtGui.QTableWidgetItem(str(item.readTimes)))
            self.ui.twItems.setItem(index, 5, QtGui.QTableWidgetItem(str(item.listenedTimes)))
            self.ui.twItems.setItem(index, 6, QtGui.QTableWidgetItem(Time.toHuman(item.lastRead)))
            self.ui.twItems.setItem(index, 7, QtGui.QTableWidgetItem("Yes" if item.hasMedia() else "No"))
            self.ui.twItems.setItem(index, 8, QtGui.QTableWidgetItem("Yes" if item.isParallel() else "No"))
             
            if item.itemType==ItemType.Video:
                colour = Qt.QColor("#FFE97F")
                 
                for j in range(0, self.ui.twItems.columnCount()):
                    it = self.ui.twItems.item(index, j)
                    it.setBackgroundColor(colour)
             
            index +=1
        
        self.ui.twItems.resizeColumnsToContents()
        self.ui.twItems.horizontalHeader().setStretchLastSection(True)

    def setupContextMenu(self):
        self.ui.twItems.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
         
        self.ui.twItems.addAction(self.ui.actionEdit_item)
        self.ui.twItems.addAction(self.ui.actionCopy_item)
        self.ui.twItems.addAction(self.ui.actionRead_item)
        self.ui.twItems.addAction(self.ui.actionRead_in_parallel)
        self.ui.twItems.addAction(self.ui.actionCreate_PDF)
        self.ui.twItems.addAction(self.ui.actionDelete_item)
         
    def createPdf(self):
        item = self.ui.twItems.item(self.ui.twItems.currentRow(), 0)
         
        if item is None:
            return
         
        data = item.data(QtCore.Qt.UserRole)
         
        if data.itemType==ItemType.Video:
            QtGui.QMessageBox.information(self, "Cannot create PDF", "PDFs can only be created for text items.")
            return
         
        webService = WebService()
        content = webService.createPdf(data.itemId)
         
        if content is None:
            QtGui.QMessageBox.warning(self, "Create PDF failed", "Unfortunately your PDF could not be created.")
        else:
            filename = QtGui.QFileDialog.getSaveFileName(parent=self, caption="Save your PDF", filter="*.pdf")
             
            if filename:
                with open(filename, "wb") as file:
                    file.write(content)

    def editItem(self):
        item = self.ui.twItems.item(self.ui.twItems.currentRow(), 0)
         
        if item is None:
            return
         
        self.dialog = ItemDialogForm(self)
        self.dialog.setItem(item.data(QtCore.Qt.UserRole).itemId)
        self.dialog.show()
        #TODO refresh items
         
    def copyItem(self):
        item = self.ui.twItems.item(self.ui.twItems.currentRow(), 0)
         
        if item is None:
            return
         
        copy = self.itemService.copyItem(item.data(QtCore.Qt.UserRole).itemId)
        self.itemService.save(copy)
        self.bindItems()
         
    def deleteItem(self):
        item = self.ui.twItems.item(self.ui.twItems.currentRow(), 0)
         
        if item is None:
            return
         
        self.itemService.delete(item.data(QtCore.Qt.UserRole).itemId)
        self.bindItems()
         
    def readItem(self, asParallel=None):
        item = self.ui.twItems.item(self.ui.twItems.currentRow(), 0)
         
        if item is None:
            return
         
        self.dialog = ReaderWindow()
        self.dialog.readItem(item.data(QtCore.Qt.UserRole).itemId, asParallel)
        self.dialog.show()
         
    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Escape:
            self.ui.leFilter.setText("")
            event.ignore()