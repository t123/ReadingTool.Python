from PyQt4 import QtCore, QtGui, Qt
from PyQt4.Qsci import QsciScintilla

from lib.misc import Application
from lib.models.model import Item, ItemType
from lib.services.service import ItemService, LanguageService
from ui.views.itemdialog import Ui_ItemDialog

class ItemDialogForm(QtGui.QDialog):
    def __init__(self, parent=None):
        self.itemService = ItemService()
        self.languageService = LanguageService()
        
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_ItemDialog()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window)
        self._setupContent()
        self._updateLanguages()
        
        self.ui.leCollectionNo.setValidator(QtGui.QIntValidator())
        
        QtCore.QObject.connect(self.ui.pbSave, QtCore.SIGNAL("clicked()"), self.saveItem)
        QtCore.QObject.connect(self.ui.pbCopy, QtCore.SIGNAL("clicked()"), self.copyItem)
        QtCore.QObject.connect(self.ui.pbSplit, QtCore.SIGNAL("clicked()"), self.splitItem)
         
    def splitItem(self):
        if self.item is None:
            return
        
        self.itemService.splitItem(self.item.itemId)
        
    def copyItem(self):
        if self.item is None:
            return
        
        copy = self.itemService.copyItem(self.item.itemId)
        copy = self.itemService.save(copy)
        self.setItem(copy.itemId)
        
    def saveItem(self):
        item = None
        
        if self.item is None:
            item = Item()
        else:
            item = self.itemService.findOne(self.item.itemId)
            
        item.itemType = ItemType.Text if self.ui.rbText.isChecked() else ItemType.Video
        item.collectionName = self.ui.leCollectionName.text()
        item.collectionNo = None if self.ui.leCollectionNo.text().isspace() or len(self.ui.leCollectionNo.text())==0 else int(self.ui.leCollectionNo.text())  
        item.mediaUri = self.ui.leMediaURI.text()
        item.l1Title = self.ui.leL1Title.text()
        item.l2Title = self.ui.leL2Title.text()
        item.setL1Content(self.ui.teL1Content.text())
        item.setL2Content(self.ui.teL2Content.text())
        item.l1LanguageId = self.ui.cbL1Language.itemData(self.ui.cbL1Language.currentIndex())
        item.l2LanguageId = self.ui.cbL2Language.itemData(self.ui.cbL2Language.currentIndex())
        
        item = self.itemService.save(item)
        self.setItem(item.itemId)
        
    def setItem(self, itemId):
        self.item = self.itemService.findOne(itemId)
        
        if self.item is None:
            self.ui.pbCopy.setEnabled(False)
            self.ui.pbSplit.setEnabled(False)
            self.ui.rbText.setChecked(True)
            self.ui.rbVideo.setChecked(False)
            self.setWindowTitle("New item")
            return
        
        self.ui.pbCopy.setEnabled(True)
        self.ui.pbSplit.setEnabled(True)
        
        self.setWindowTitle("Edit " + self.item.name())
        self.ui.leCollectionName.setText(self.item.collectionName)
        self.ui.leCollectionNo.setText(str(self.item.collectionNo) if self.item.collectionNo is not None else "")
        self.ui.leL1Title.setText(self.item.l1Title)
        self.ui.leL2Title.setText(self.item.l2Title)
        self.ui.leMediaURI.setText(self.item.mediaUri)
        
        if self.item.itemType==ItemType.Text:
            self.ui.rbText.setChecked(True)
            self.ui.rbVideo.setChecked(False)
        else:
            self.ui.rbText.setChecked(False)
            self.ui.rbVideo.setChecked(True)
            
        self.ui.teL1Content.setUtf8(True)
        self.ui.teL2Content.setUtf8(True)
        self.ui.teL1Content.setText(self.item.getL1Content())
        self.ui.teL2Content.setText(self.item.getL2Content())
        
        index1 = self.ui.cbL1Language.findData(self.item.l1LanguageId)
        index2= self.ui.cbL1Language.findData(self.item.l2LanguageId)
        
        self.ui.cbL1Language.setCurrentIndex(index1)
        self.ui.cbL2Language.setCurrentIndex(index2)
        
    def _updateLanguages(self):
        languages = self.languageService.findAll()
        self.ui.cbL1Language.clear()
        self.ui.cbL2Language.clear()
        
        for language in languages:
            self.ui.cbL1Language.addItem(language.name, language.languageId)
            self.ui.cbL2Language.addItem(language.name, language.languageId)
            
    def _setupContent(self):
        font = QtGui.QFont()
        font.setFamily("Arial Unicode MS")
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.ui.teL1Content.setFont(font)
        self.ui.teL1Content.setMarginsFont(font)
        self.ui.teL2Content.setFont(font)
        self.ui.teL2Content.setMarginsFont(font)
        
        fontmetrics = QtGui.QFontMetrics(font)
        self.ui.teL1Content.setMarginsFont(font)
        self.ui.teL1Content.setMarginWidth(0, fontmetrics.width("00000"))
        self.ui.teL1Content.setMarginLineNumbers(0, True)
        self.ui.teL1Content.setMarginsBackgroundColor(QtGui.QColor("#cccccc"))
        self.ui.teL2Content.setMarginsFont(font)
        self.ui.teL2Content.setMarginWidth(0, fontmetrics.width("00000"))
        self.ui.teL2Content.setMarginLineNumbers(0, True)
        self.ui.teL2Content.setMarginsBackgroundColor(QtGui.QColor("#cccccc"))
        
        self.ui.teL1Content.setCaretLineVisible(True)
        self.ui.teL1Content.setCaretLineBackgroundColor(QtGui.QColor("#ffe4e4"))
        self.ui.teL2Content.setCaretLineVisible(True)
        self.ui.teL2Content.setCaretLineBackgroundColor(QtGui.QColor("#ffe4e4"))