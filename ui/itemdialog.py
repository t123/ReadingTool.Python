import os, logging, uuid
from PyQt4 import QtCore, QtGui, Qt
from PyQt4.Qsci import QsciScintilla

from lib.stringutil import StringUtil
from lib.misc import Application, Validations, Time
from lib.models.model import Item, ItemType
from lib.services.service import ItemService, LanguageService, StorageService
from ui.views.itemdialog import Ui_ItemDialog
from lib.services.web import WebService

class ItemDialogForm(QtGui.QDialog):
    def __init__(self, parent=None, itemId=None):
        self.itemService = ItemService()
        self.languageService = LanguageService()
        
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_ItemDialog()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setupContent()
        self.updateLanguages()
        
        self.ui.leCollectionNo.setValidator(QtGui.QIntValidator())

        QtCore.QObject.connect(self.ui.pbPrevious, QtCore.SIGNAL("clicked()"), self.previousItem)
        QtCore.QObject.connect(self.ui.pbNext, QtCore.SIGNAL("clicked()"), self.nextItem)
        QtCore.QObject.connect(self.ui.pbSave, QtCore.SIGNAL("clicked()"), self.saveItem)
        QtCore.QObject.connect(self.ui.pbCopy, QtCore.SIGNAL("clicked()"), self.copyItem)
        QtCore.QObject.connect(self.ui.pbSplit, QtCore.SIGNAL("clicked()"), self.splitItem)
        QtCore.QObject.connect(self.ui.pbChoose, QtCore.SIGNAL("clicked()"), self.chooseFile)
        QtCore.QObject.connect(self.ui.pbSegment, QtCore.SIGNAL("clicked()"), self.segmentText)
        QtCore.QObject.connect(self.ui.cbL1Language, QtCore.SIGNAL("currentIndexChanged(int)"), self.checkLanguageCode)
        
        QtCore.QObject.connect(self.ui.leL1Title, QtCore.SIGNAL("textChanged(QString)"), self.onTitleChanged)
        
        self.setItem(itemId)
        self.hasChange = False
        self.onTitleChanged(self.item.l1Title if self.item else "")
        
        if not self.languageService.any():
            self.ui.pbCopy.setEnabled(False)
            self.ui.pbSplit.setEnabled(False)
            self.ui.pbSave.setEnabled(False)
            
        logging.debug("Item Id: {0}".format(itemId))
        logging.debug("Language Id: {0}".format(self.item.l1LanguageId if self.item is not None else "New"))
        
    def onTitleChanged(self, title):
        p = Qt.QPalette()
        
        if len(title.strip())>0:
            p.setColor(QtGui.QPalette.Base, QtGui.QColor(Validations.Ok))
            self.ui.pbCopy.setEnabled(True)
            self.ui.pbSplit.setEnabled(True)
            self.ui.pbSave.setEnabled(True)
        else:
            p.setColor(QtGui.QPalette.Base, QtGui.QColor(Validations.Failed))
            self.ui.pbCopy.setEnabled(False)
            self.ui.pbSplit.setEnabled(False)
            self.ui.pbSave.setEnabled(False)
            
        self.ui.leL1Title.setPalette(p)
            
    def closeEvent(self, event):
        if self.hasChange:
            Application.myApp.bindItems()
            
        event.accept()
        
    def segmentText(self):
        webService = WebService()
        content = webService.segmentText(self.language.languageCode, self.ui.teL1Content.text())
        
        if content is not None:
            self.ui.teL1Content.setText(content)
        
    def chooseFile(self):
        storageService = StorageService()
        mediaDirectory = storageService.find("last_media_directory", uuid=str(Application.user.userId))
        
        if StringUtil.isEmpty(mediaDirectory):
            filename = QtGui.QFileDialog.getOpenFileName(caption="Choose a media file", filter="Media files (*.mp3 *.mp4)")
        else:
            filename = QtGui.QFileDialog.getOpenFileName(caption="Choose a media file", filter="Media files (*.mp3 *.mp4)", directory=mediaDirectory)
                    
        if not StringUtil.isEmpty(filename):
            path, file = os.path.split(filename)
            storageService.save("last_media_directory", path, str(Application.user.userId))
            self.ui.leMediaURI.setText(filename)
        
    def splitItem(self):
        if self.item is None:
            return
        
        self.itemService.splitItem(self.item.itemId)
        self.hasChange = True
        
    def copyItem(self):
        if self.item is None:
            return
        
        copy = self.itemService.copyItem(self.item.itemId)
        copy = self.itemService.save(copy)
        self.setItem(copy.itemId)
        self.hasChange = True
        
    def saveItem(self):
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
        
        if item.l2LanguageId is None and item.isParallel():
            item.l2LanguageId = item.l1LanguageId
            
        item = self.itemService.save(item)
        self.setItem(item.itemId)
        self.hasChange = True
        
    def nextItem(self):
        next = self.itemService.findNext(self.item)

        if len(next)==0:
            return

        self.hasChange = False
        self.setItem(next[0].itemId)

    def previousItem(self):
        previous = self.itemService.findPrevious(self.item)

        if len(previous)==0:
            return

        self.hasChange = False
        self.setItem(previous[0].itemId)

    def setItem(self, itemId):
        if itemId is None:
            self.ui.lblDate.setText("Unsaved item")
            self.ui.pbCopy.setEnabled(False)
            self.ui.pbSplit.setEnabled(False)
            self.ui.rbText.setChecked(True)
            self.ui.rbVideo.setChecked(False)
            self.setWindowTitle("New item")
            self.checkLanguageCode(-1)
            self.item = None
            self.setNextPrevious(self.item)
            return
        
        self.item = self.itemService.findOne(itemId)
        self.ui.lblDate.setText("{1} (Created on {0})".format(Time.toLocal(self.item.created), Time.toLocal(self.item.modified)))
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
        
        index1 = self.findIndex(self.ui.cbL1Language, self.item.l1LanguageId)
        index2 = self.findIndex(self.ui.cbL2Language, self.item.l2LanguageId)
        
        self.ui.cbL1Language.setCurrentIndex(index1)
        self.ui.cbL2Language.setCurrentIndex(index2)
        
        self.checkLanguageCode(index1)
        self.setNextPrevious(self.item)

    def setNextPrevious(self, item):
        if item is None:
            self.ui.pbPrevious.setEnabled(False)
            self.ui.pbNext.setEnabled(False)
            return

        previous = self.itemService.findPrevious(self.item)
        next = self.itemService.findNext(self.item)

        if len(previous)==0:
            self.ui.pbPrevious.setEnabled(False)
        else:
            self.ui.pbPrevious.setEnabled(True)

        if len(next)==0:
            self.ui.pbNext.setEnabled(False)
        else:
            self.ui.pbNext.setEnabled(True)

    def findIndex(self, cb, data):
        if cb is None or not isinstance(cb, QtGui.QComboBox):
            return -1
        
        if data is None:
            return -1
        
        for index in range(0, cb.count()):
            cbData = cb.itemData(index)
            
            if cbData==data:
                return index
            
        return -1
    
    def checkLanguageCode(self, index):
        if not Application.user.hasCredentials():
            self.ui.pbSegment.hide()
            return
            
        l1LanguageId = self.ui.cbL1Language.itemData(self.ui.cbL1Language.currentIndex())
        self.language = self.languageService.findOne(l1LanguageId)
        
        if self.language is None:
            return
        
        if self.language.languageCode=="ja":
            self.ui.pbSegment.setToolTip("Segment with Mecab")
            self.ui.pbSegment.show()
        else:
            self.ui.pbSegment.hide()
            
    def updateLanguages(self):
        languages = self.languageService.findAll()
        self.ui.cbL1Language.clear()
        self.ui.cbL2Language.clear()
        
        for language in languages:
            self.ui.cbL1Language.addItem(language.name, language.languageId)
            self.ui.cbL2Language.addItem(language.name, language.languageId)
            
    def setupContent(self):
        font = QtGui.QFont()
        font.setFamily("Arial Unicode MS")
        font.setFixedPitch(True)
        font.setPointSize(10)

        self.ui.teL1Content.setUtf8(True)
        self.ui.teL2Content.setUtf8(True)

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