import threading, datetime, time, os

from PyQt4 import QtCore, QtGui, Qt

from lib.misc import Application
from lib.models.model import Item, ItemType
from lib.models.parser import ParserInput
from lib.services.parser import TextParser, VideoParser
from lib.services.service import ItemService, LanguageService, TermService
from ui.views.reader import Ui_ReadingWindow

class Javascript(QtCore.QObject):
    def __init__(self, po=None):
        super().__init__()
        self.po = po
        
    @QtCore.pyqtSlot(str)
    def copyToClipboard(self, message):
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(message)
        
    @QtCore.pyqtSlot(float, result=int)
    def getSrtL1(self, message):
        if self.po is None or self.po.l1Srt is None:
            return -1
        
        srt = [srt for srt in self.po.l1Srt if srt.start<message and srt.end>message]
        
        if srt is None or len(srt)==0:
            return -1
        
        first = srt[0]
        return first.lineNo
    
    @QtCore.pyqtSlot(float, result=int)
    def getSrtL2(self, message, result=int):
        if self.po is None or self.po.l2Srt is None:
            return -1
        
        srt = [srt for srt in self.po.l2Srt if srt.start<message and srt.end>message]
        
        if srt is None or len(srt)==0:
            return -1
        
        first = srt[0]
        return first.lineNo
        
class CustomWebPage(Qt.QWebPage):
    def __init__(self, parent = None):
        Qt.QWebPage.__init__(self, parent)
    
    def acceptNavigationRequest(self, frame, request, navigationType):
        if request.url().toString().startswith("http://localhost") or request.url().toString().startswith("about:blank"):
            return True
        else:
            Qt.QDesktopServices.openUrl(request.url())
            return False
    
    def createWindow(self, windowType):
        self.newPage = CustomWebPage()
        return self.newPage
    
class CustomWebView(Qt.QWebView):
    def __init__(self, parent = None):
        Qt.QWebView.__init__(self, parent)
        self.setPage(CustomWebPage())
        self.page().setLinkDelegationPolicy(Qt.QWebPage.DelegateAllLinks)
        
    def createWindow(self, webWindowType):
        return super(CustomWebView, self).createWindow(webWindowType)
    
class ReaderWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        self.itemService = ItemService()
        self.languageService = LanguageService()
        self.termService = TermService()
        
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_ReadingWindow()
        self.ui.setupUi(self)
        
        self.webView = CustomWebView(self)
        self.webView.setUrl(QtCore.QUrl("about:blank"))
        self.webView.setRenderHints(QtGui.QPainter.Antialiasing|QtGui.QPainter.HighQualityAntialiasing|QtGui.QPainter.SmoothPixmapTransform|QtGui.QPainter.TextAntialiasing)
        self.webView.setObjectName("webView")
        self.ui.verticalLayout.addWidget(self.webView)
        
        self.__openTime = datetime.datetime.now()
        self.setWindowFlags(QtCore.Qt.Window)
        self.showMaximized()
        
        QtCore.QObject.connect(self.ui.btnMarkKnown, QtCore.SIGNAL("clicked()"), self.markKnown)
        QtCore.QObject.connect(self.webView, QtCore.SIGNAL("loadFinished(bool)"), self.onLoadComplete)
        QtCore.QObject.connect(self.webView, QtCore.SIGNAL("javaScriptWindowObjectCleared()"), self.onJsCleared)
        QtCore.QObject.connect(self.webView, QtCore.SIGNAL("linkClicked(QUrl)"), self.onLinkClicked)
        QtCore.QObject.connect(self.ui.spListening, QtCore.SIGNAL("valueChanged(int)"), self.onListeningChanged)
        QtCore.QObject.connect(self.ui.spReading, QtCore.SIGNAL("valueChanged(int)"), self.onReadingChanged)
        
        Qt.QWebSettings.globalSettings().setAttribute(Qt.QWebSettings.DeveloperExtrasEnabled, True)
        Qt.QWebSettings.globalSettings().setAttribute(Qt.QWebSettings.PluginsEnabled, True)
        Qt.QWebSettings.globalSettings().setAttribute(Qt.QWebSettings.JavascriptEnabled, True)
        Qt.QWebSettings.globalSettings().setAttribute(Qt.QWebSettings.JavascriptCanOpenWindows, True)
        Qt.QWebSettings.globalSettings().setAttribute(Qt.QWebSettings.JavascriptCanCloseWindows, True)
        Qt.QWebSettings.globalSettings().setAttribute(Qt.QWebSettings.JavascriptCanAccessClipboard, True)
        Qt.QWebSettings.globalSettings().setAttribute(Qt.QWebSettings.LocalStorageDatabaseEnabled, True)
        Qt.QWebSettings.globalSettings().setAttribute(Qt.QWebSettings.WebGLEnabled, True)
        Qt.QWebSettings.globalSettings().setAttribute(Qt.QWebSettings.LocalStorageDatabaseEnabled, True)
        Qt.QWebSettings.globalSettings().setAttribute(Qt.QWebSettings.LocalContentCanAccessFileUrls, True)
        Qt.QWebSettings.globalSettings().setAttribute(Qt.QWebSettings.LocalContentCanAccessRemoteUrls, True)
        
    def markKnown(self):
        frame = self.webView.page().mainFrame()
        frame.evaluateJavaScript("window.reading.markRemainingAsKnown();")
    
    def readItem(self, itemId, asParallel=None):
        self.item = self.itemService.findOne(itemId)

        if self.item.itemType==ItemType.Video:
            self.ui.label_2.setText("Watched")
            
        self.ui.spListening.setValue(self.item.listenedTimes)
        self.ui.spReading.setValue(self.item.readTimes)
        self.ui.lblMessage.setText("")
        
        if ((asParallel is None and self.item.isParallel()) or asParallel==True) and self.item.l2LanguageId is not None:
            asParallel = True
        else:
            asParallel = False
            
        if self.item.itemType==ItemType.Text:
            parser = TextParser()
        else:
            parser = VideoParser()
            
        pi = ParserInput()
        pi.item = self.item
        pi.language1 = self.languageService.findOne(self.item.l1LanguageId)
        pi.language2 = self.languageService.findOne(self.item.l2LanguageId) if asParallel else None
        pi.asParallel = asParallel
        pi.terms = self.termService.findAllByLanguage(self.item.l1LanguageId)
        
        self.po = parser.parse(pi)
        self.po.save()
        
        self.webView.setUrl(QtCore.QUrl(Application.apiServer + "/resource/v1/item/" + str(self.po.item.itemId)))
        self.setWindowTitle(self.item.name())
        self.__readTime = datetime.datetime.now()
        self.__updateTitle()
        self._updateNextPreviousMenu()
        
        self.item.lastRead = time.time()
        self.itemService.save(self.item)
        
    def onLoadComplete(self, result):
        self.loadJs()
    
    def onJsCleared(self):
        self.loadJs()
        
    def onListeningChanged(self, value):
        self.itemService.changeState(self.item.itemId, "listen", value)
        self.setStatMessage(value, "listen")
        
    def onReadingChanged(self, value):
        self.itemService.changeState(self.item.itemId, "read", value)
        self.setStatMessage(value, "read")
        
    def setStatMessage(self, value, type):
        if type=="listen":
            if self.item.itemType==ItemType.Text:
                msg = "listened to"
            else:
                msg = "watched"
        else:
            msg = "read"
            
        if value==0:
            self.ui.lblMessage.setText("Item never %s." % msg)
            return
            
        if value==1:
            self.ui.lblMessage.setText("Item %s once." % msg)
            return
        
        if value==2:
            self.ui.lblMessage.setText("Item %s twice." % msg)
            return
            
        self.ui.lblMessage.setText("Item %s %d times." % (msg, value))
        
    def loadJs(self):
        self.js = Javascript(self.po)
        frame = self.webView.page().mainFrame()
        frame.addToJavaScriptWindowObject("rtjscript", self.js)
        
    def onLinkClicked(self, url):
        Qt.QDesktopServices.openUrl(url)
        
    def _updateNextPreviousMenu(self):
        prev = self.itemService.findPrevious(self.item, limit=5)
        next = self.itemService.findNext(self.item, limit=5)
        
        nextItem = next[0] if next is not None and len(next)>0 else None
        
        if nextItem is None:
            nextItem = prev[-1] if prev is not None and len(prev)>0 else None         
         
        if nextItem is None:
            self.ui.tbItems.setText('No items')
            self.ui.tbItems.hide()
            return
            
        self.ui.tbItems.show()
        action = QtGui.QAction(self)
        action.setText(nextItem.name())
        action.setData(nextItem.itemId)
        action.connect(action, QtCore.SIGNAL("triggered()"), lambda item=action.data(): self.readItem(item))
        
        self.ui.tbItems.enabled = True
        self.ui.tbItems.setDefaultAction(action)
            
        menu = QtGui.QMenu()
        for item in reversed(prev):
            action = QtGui.QAction(menu)
            action.setText(item.name())
            action.setData(item.itemId)
            action.connect(action, QtCore.SIGNAL("triggered()"), lambda item=action.data(): self.readItem(item))
            menu.addAction(action)
            
        for item in next:
            action = QtGui.QAction(menu)
            action.setText(item.name())
            action.setData(item.itemId)
            action.connect(action, QtCore.SIGNAL("triggered()"), lambda item=action.data(): self.readItem(item))
            menu.addAction(action)
            
        self.ui.tbItems.setMenu(menu)
        
    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_F11:
            if self.windowState()==QtCore.Qt.WindowFullScreen:
                if self.previousState==QtCore.Qt.WindowMaximized:
                    self.showMaximized()
                else:
                    self.showNormal()
                    self.setGeometry(self.previousGeometry)
            else:
                self.previousState = self.windowState()
                self.previousGeometry = self.geometry()
                self.showNormal()
                self.showFullScreen()
            
            return
        
        if event.key()==QtCore.Qt.Key_Escape:
            return
        
        return QtGui.QDialog.keyPressEvent(self, event)
        
    def __updateTitle(self):
        delta = (datetime.datetime.now()-self.__openTime)
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        title = "%s [window %s] [item %s] [total %02d:%02d]" % \
            (self.item.name(), self.__openTime.strftime("%H:%M"), self.__readTime.strftime("%H:%M"), hours, minutes)
             
        self.setWindowTitle(title)
        threading.Timer(5, self.__updateTitle).start()