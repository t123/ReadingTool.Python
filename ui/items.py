from PyQt4 import QtCore, QtGui, Qt

from lib.misc import Application, Time
from lib.stringutil import StringUtil
from lib.models.model import Item, ItemType
from lib.services.service import ItemService, LanguageService
from ui.views.items import Ui_Items
from ui.itemdialog import ItemDialogForm
from ui.reader import ReaderWindow
from PyQt4.Qt import QAction

class ItemsForm(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Items()
        self.ui.setupUi(self)
        
        self.itemService = ItemService()
        self.updateItems()
        self.updateTree()
        
        QtCore.QObject.connect(self.ui.pbAdd, QtCore.SIGNAL("clicked()"), lambda: self.addItem())
        QtCore.QObject.connect(self.ui.pbEdit, QtCore.SIGNAL("clicked()"), self.editItem)
        QtCore.QObject.connect(self.ui.pbCopy, QtCore.SIGNAL("clicked()"), self.copyItem)
        QtCore.QObject.connect(self.ui.pbDelete, QtCore.SIGNAL("clicked()"), self.deleteItem)
        QtCore.QObject.connect(self.ui.pbClear, QtCore.SIGNAL("clicked()"), self.clear)
        QtCore.QObject.connect(self.ui.pbRead, QtCore.SIGNAL("clicked()"), lambda asParallel = False: self.readItem(asParallel))        
        QtCore.QObject.connect(self.ui.pbReadParallel, QtCore.SIGNAL("clicked()"), lambda asParallel = True: self.readItem(asParallel))        
        QtCore.QObject.connect(self.ui.tItems, QtCore.SIGNAL("itemDoubleClicked(QTableWidgetItem*)"), lambda: self.readItem(asParallel=None))
        QtCore.QObject.connect(self.ui.leFilter, QtCore.SIGNAL("textChanged(QString)"), self.updateItems)
        QtCore.QObject.connect(self.ui.leFilter, QtCore.SIGNAL("returnPressed()"), self.updateItems)
        QtCore.QObject.connect(self.ui.tvFilter, QtCore.SIGNAL("itemDoubleClicked(QTreeWidgetItem*,int)"), self.onItemClicked)
        
        self.ui.splitter.setStretchFactor(0,0)
        self.ui.splitter.setStretchFactor(1,1)
        
        self.contextMenu()
        
    def clear(self):
        self.ui.leFilter.setText("")
        self.updateItems()
                
    def contextMenu(self):
        self.ui.tItems.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        
        action = QAction("Edit", self.ui.tItems)
        self.ui.tItems.addAction(action)
        QtCore.QObject.connect(action, QtCore.SIGNAL("triggered()"), self.editItem)
        
        action = QAction("Delete", self.ui.tItems)
        self.ui.tItems.addAction(action)
        QtCore.QObject.connect(action, QtCore.SIGNAL("triggered()"), self.deleteItem)
        
        action = QAction("Copy", self.ui.tItems)
        self.ui.tItems.addAction(action)
        QtCore.QObject.connect(action, QtCore.SIGNAL("triggered()"), self.copyItem)
        
        action = QAction("Read", self.ui.tItems)
        self.ui.tItems.addAction(action)
        QtCore.QObject.connect(action, QtCore.SIGNAL("triggered()"), lambda: self.readItem(asParallel=False))
        
        action = QAction("Read Parallel", self.ui.tItems)
        self.ui.tItems.addAction(action)
        QtCore.QObject.connect(action, QtCore.SIGNAL("triggered()"), lambda: self.readItem(asParallel=True))
        
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
        
    def updateTree(self):
        self.ui.tvFilter.header().hide()
        self.ui.tvFilter.clear()
        self.ui.tvFilter.setColumnCount(1)
        
        i = QtGui.QTreeWidgetItem(self.ui.tvFilter, ["Clear filter"])
        i.setData(0, QtCore.Qt.UserRole, "")
        self.ui.tvFilter.addTopLevelItem(i)
        
        i = QtGui.QTreeWidgetItem(self.ui.tvFilter, ["Parallel items"])
        i.setData(0, QtCore.Qt.UserRole, "#parallel")
        self.ui.tvFilter.addTopLevelItem(i)
        
        i = QtGui.QTreeWidgetItem(self.ui.tvFilter, ["Text items"])
        i.setData(0, QtCore.Qt.UserRole, "#text")
        self.ui.tvFilter.addTopLevelItem(i)
        
        i = QtGui.QTreeWidgetItem(self.ui.tvFilter, ["Video items"])
        i.setData(0, QtCore.Qt.UserRole, "#video")
        self.ui.tvFilter.addTopLevelItem(i)
        
        i = QtGui.QTreeWidgetItem(self.ui.tvFilter, ["Items with media"])
        i.setData(0, QtCore.Qt.UserRole, "#media")
        self.ui.tvFilter.addTopLevelItem(i)
        
        ls = LanguageService()
        
        for l in ls.findAll("archived"):
            collections = self.itemService.collectionsByLanguage(l.languageId)
            
            i = QtGui.QTreeWidgetItem(self.ui.tvFilter, [l.name])
            i.setData(0, QtCore.Qt.UserRole, '"' + l.name + '"')
            
            if not l.isArchived:
                i.setExpanded(True)
                
            for collectionName in collections:
                si = QtGui.QTreeWidgetItem(i, [collectionName])
                si.setData(0, QtCore.Qt.UserRole, '"' + l.name + '" ' + '"' + collectionName + '"') 
                
            self.ui.tvFilter.addTopLevelItem(i)

        
    def onItemClicked(self, item, column):
        data = item.data(0, QtCore.Qt.UserRole)
        self.ui.leFilter.setText(data)
        #=======================================================================
        # if StringUtil.isEmpty(data):
        #     self.ui.leFilter.setText("")
        # else:
        #     self.ui.leFilter.setText(self.ui.leFilter.text() + " " + data)
        #=======================================================================
            
        self.updateItems()
        
    def updateItems(self, filter = None):
        if filter is not None and filter!="":
            return
        
        self.ui.tItems.clear()
        headers = ["Language", "Collection Name", "No", "Title", "Read", "Listened", "Last Read", "Media?", "Parallel"]
        self.ui.tItems.setColumnCount(len(headers))
        self.ui.tItems.setHorizontalHeaderLabels(headers)
        self.ui.tItems.setSortingEnabled(True)
        
        index = 0
        items = self.itemService.search(self.ui.leFilter.text())
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
        
    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Escape:
            return
            
        if self.ui.tItems.hasFocus():
            if not event.modifiers() & QtCore.Qt.ControlModifier and (event.key()==QtCore.Qt.Key_Return or event.key()==QtCore.Qt.Key_Enter):
                self.readItem(None)
                return
            
            if event.key()==QtCore.Qt.Key_Delete:
                self.deleteItem()
                return
                
            if event.modifiers() & QtCore.Qt.ControlModifier:
                if event.key()==QtCore.Qt.Key_Return or event.key()==QtCore.Qt.Key_Enter:
                    self.readItem(False)
                    return
                    
                if event.key()==QtCore.Qt.Key_E:
                    self.editItem()
                    return
                
                if event.key()==QtCore.Qt.Key_D:    
                    self.addItem()
                    return
                    
                if event.key()==QtCore.Qt.Key_C:    
                    self.copyItem()
                    return
                
                if event.key()==QtCore.Qt.Key_L or event.key()==QtCore.Qt.Key_F:    
                    self.ui.leFilter.setFocus()
                    return
            
        return QtGui.QDialog.keyPressEvent(self, event)