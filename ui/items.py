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
        
        QtCore.QObject.connect(self.ui.twItems, QtCore.SIGNAL("itemDoubleClicked(QTableWidgetItem*)"), lambda: self.readItem(asParallel=None))
        QtCore.QObject.connect(self.ui.leFilter, QtCore.SIGNAL("textChanged(QString)"), self.onTextChanged)
        QtCore.QObject.connect(self.ui.leFilter, QtCore.SIGNAL("returnPressed()"), self.bindItems)

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
         
        action = QAction("Edit", self.ui.twItems)
        self.ui.twItems.addAction(action)
        QtCore.QObject.connect(action, QtCore.SIGNAL("triggered()"), self.editItem)
         
        action = QAction("Delete", self.ui.twItems)
        self.ui.twItems.addAction(action)
        QtCore.QObject.connect(action, QtCore.SIGNAL("triggered()"), self.deleteItem)
         
        action = QAction("Copy", self.ui.twItems)
        self.ui.twItems.addAction(action)
        QtCore.QObject.connect(action, QtCore.SIGNAL("triggered()"), self.copyItem)
         
        action = QAction("Read", self.ui.twItems)
        self.ui.twItems.addAction(action)
        QtCore.QObject.connect(action, QtCore.SIGNAL("triggered()"), lambda: self.readItem(asParallel=False))
         
        action = QAction("Read Parallel", self.ui.twItems)
        self.ui.twItems.addAction(action)
        QtCore.QObject.connect(action, QtCore.SIGNAL("triggered()"), lambda: self.readItem(asParallel=True))
         
        action = QAction("Create PDF", self.ui.twItems)
        self.ui.twItems.addAction(action)
        QtCore.QObject.connect(action, QtCore.SIGNAL("triggered()"), self.createPdf)
         
    def createPdf(self):
        item = self.ui.twItems.item(self.ui.twItems.currentRow(), 0)
         
        if item is None:
            return
         
        data = item.data(QtCore.Qt.UserRole)
         
        if data.itemType==ItemType.Video:
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
         
    def copyItem(self):
        item = self.ui.twItems.item(self.ui.twItems.currentRow(), 0)
         
        if item is None:
            return
         
        copy = self.itemService.copyItem(item.data(QtCore.Qt.UserRole).itemId)
        self.itemService.save(copy)
        self.updateItems()
         
    def deleteItem(self):
        item = self.ui.twItems.item(self.ui.twItems.currentRow(), 0)
         
        if item is None:
            return
         
        self.itemService.delete(item.data(QtCore.Qt.UserRole).itemId)
        self.updateItems()
         
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
            
#     def keyPressEvent(self, event):
#         if event.key()==QtCore.Qt.Key_Escape:
#             return
#             
#         if self.ui.twItems.hasFocus():
#             if not event.modifiers() & QtCore.Qt.ControlModifier and (event.key()==QtCore.Qt.Key_Return or event.key()==QtCore.Qt.Key_Enter):
#                 self.readItem(None)
#                 return
#             
#             if event.key()==QtCore.Qt.Key_Delete:
#                 self.deleteItem()
#                 return
#                 
#             if event.modifiers() & QtCore.Qt.ControlModifier:
#                 if event.key()==QtCore.Qt.Key_Return or event.key()==QtCore.Qt.Key_Enter:
#                     self.readItem(False)
#                     return
#                     
#                 if event.key()==QtCore.Qt.Key_E:
#                     self.editItem()
#                     return
#                 
#                 if event.key()==QtCore.Qt.Key_D:    
#                     self.addItem()
#                     return
#                     
#                 if event.key()==QtCore.Qt.Key_C:    
#                     self.copyItem()
#                     return
#                 
#                 if event.key()==QtCore.Qt.Key_L or event.key()==QtCore.Qt.Key_F:    
#                     self.ui.leFilter.setFocus()
#                     return
#             
#         return QtGui.QDialog.keyPressEvent(self, event)
#===============================================================================