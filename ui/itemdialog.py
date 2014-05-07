from PyQt4 import QtCore, QtGui, Qt
from PyQt4.Qsci import QsciScintilla

from lib.misc import Application
from lib.models.model import Item, ItemType
from lib.services.service import ItemService
from ui.views.itemdialog import Ui_ItemDialog

class ItemDialogForm(QtGui.QDialog):
    def __init__(self, parent=None):
        self.itemService = ItemService()
        
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_ItemDialog()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window)
        self._setupContent()
        
        #=======================================================================
        # QtCore.QObject.connect(self.ui.lvPlugins, QtCore.SIGNAL("currentItemChanged(QListWidgetItem*,QListWidgetItem*)"), self.populateItem)
        # QtCore.QObject.connect(self.ui.pbSave, QtCore.SIGNAL("clicked()"), self.savePlugin)
        # QtCore.QObject.connect(self.ui.pbAdd, QtCore.SIGNAL("clicked()"), self.addPlugin)
        # QtCore.QObject.connect(self.ui.pbDelete, QtCore.SIGNAL("clicked()"), self.deletePlugin)
        # 
        # self.pluginService = PluginService()
        # self.updatePlugins();
        #=======================================================================
        
    def setItem(self, itemId):
        self.item = self.itemService.findOne(itemId)
        
        if self.item is None:
            return
        
        self.ui.leCollectionName.setText(self.item.collectionName)
        
    def _setupContent(self):
        font = QtGui.QFont()
        font.setFamily('Courier')
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