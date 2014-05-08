from PyQt4 import QtCore, QtGui, Qt

from lib.misc import Application, Time
from lib.models.model import Item, ItemType
from lib.services.service import ItemService
from ui.views.items import Ui_Items
from ui.itemdialog import ItemDialogForm
from ui.reader import ReaderWindow

class ItemsForm(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Items()
        self.ui.setupUi(self)
        
        self.itemService = ItemService()
        self.updateItems();
        
        QtCore.QObject.connect(self.ui.pbAdd, QtCore.SIGNAL("clicked()"), lambda: self.addItem())
        QtCore.QObject.connect(self.ui.pbEdit, QtCore.SIGNAL("clicked()"), self.editItem)
        QtCore.QObject.connect(self.ui.pbCopy, QtCore.SIGNAL("clicked()"), self.copyItem)
        QtCore.QObject.connect(self.ui.pbDelete, QtCore.SIGNAL("clicked()"), self.deleteItem)
        QtCore.QObject.connect(self.ui.pbRead, QtCore.SIGNAL("clicked()"), lambda asParallel = False: self.readItem(asParallel))        
        QtCore.QObject.connect(self.ui.pbReadParallel, QtCore.SIGNAL("clicked()"), lambda asParallel = True: self.readItem(asParallel))        
        QtCore.QObject.connect(self.ui.tItems, QtCore.SIGNAL("itemDoubleClicked(QTableWidgetItem*)"), lambda: self.readItem(asParallel=None))
        
    def addItem(self):
        self.dialog = ItemDialogForm()
        self.dialog.setItem(0)
        self.dialog.show()
        
    def editItem(self):
        item = self.ui.tItems.item(self.ui.tItems.currentRow(), 0)
        
        if item is None:
            return
        
        self.dialog = ItemDialogForm()
        self.dialog.setItem(item.data(QtCore.Qt.UserRole).itemId)
        self.dialog.show()
        
    def copyItem(self):
        item = self.ui.tItems.item(self.ui.tItems.currentRow(), 0)
        
        if item is None:
            return
        
        copy = self.itemService.copyItem(item.data(QtCore.Qt.UserRole).itemId)
        self.itemService.save(copy)
        self.updateItems()
        
    def deleteItem(self):
        item = self.ui.tItems.item(self.ui.tItems.currentRow(), 0)
        
        if item is None:
            return
        
        self.itemService.delete(item.data(QtCore.Qt.UserRole).itemId)
        self.updateItems()
        
    def readItem(self, asParallel=None):
        item = self.ui.tItems.item(self.ui.tItems.currentRow(), 0)
        
        if item is None:
            return
        
        reader = ReaderWindow()
        reader.readItem(item.data(QtCore.Qt.UserRole).itemId, asParallel)
        reader.show()
        
    def updateItems(self):
        self.ui.tItems.clear()
        headers = ["Language", "Collection Name", "No", "Title", "Read", "Listened", "Last Read", "Media?", "Parallel"]
        self.ui.tItems.setColumnCount(len(headers))
        self.ui.tItems.setHorizontalHeaderLabels(headers)
        self.ui.tItems.setSortingEnabled(False)
        
        index = 0
        items = self.itemService.findAll()
        self.ui.tItems.setRowCount(len(items))
        
        for item in items:
            i = QtGui.QTableWidgetItem(item.l1Language)
            i.setData(QtCore.Qt.UserRole, item)

            self.ui.tItems.setItem(index, 0, i)
            self.ui.tItems.setItem(index, 1, QtGui.QTableWidgetItem(item.collectionName))
            self.ui.tItems.setItem(index, 2, QtGui.QTableWidgetItem(str(item.collectionNo) if item.collectionNo is not None else ""))
            self.ui.tItems.setItem(index, 3, QtGui.QTableWidgetItem(item.l1Title))
            self.ui.tItems.setItem(index, 4, QtGui.QTableWidgetItem(str(item.readTimes)))
            self.ui.tItems.setItem(index, 5, QtGui.QTableWidgetItem(str(item.listenedTimes)))
            self.ui.tItems.setItem(index, 6, QtGui.QTableWidgetItem(Time.toHuman(item.lastRead)))
            self.ui.tItems.setItem(index, 7, QtGui.QTableWidgetItem("Yes" if item.hasMedia() else "No"))
            self.ui.tItems.setItem(index, 8, QtGui.QTableWidgetItem("Yes" if item.isParallel() else "No"))
            
            index +=1
        
        self.ui.tItems.resizeColumnsToContents()
        self.ui.tItems.setSortingEnabled(True)            
