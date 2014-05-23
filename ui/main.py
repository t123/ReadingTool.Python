import logging
from PyQt4 import Qt, QtGui, QtCore
from lib.misc import Application
from lib.services.service import UserService, ItemService, StorageService, LanguageService
from lib.services.web import WebService

from ui.views.main import Ui_MainWindow
from ui.reader import ReaderWindow
from ui.profiles import ProfilesForm
from ui.languages import LanguagesForm
from ui.plugins import PluginsForm
from ui.items import ItemsForm
from ui.terms import TermsForm
from ui.settings import SettingsForm
from ui.about import AboutForm
from ui.itemdialog import ItemDialogForm
from lib.stringutil import StringUtil

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.userService = UserService()
        self.itemService = ItemService()
        self.languageService = LanguageService()
         
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.setupUserLayout()
        
        self.ui.verticalSplitter.setStretchFactor(0,0)
        self.ui.verticalSplitter.setStretchFactor(1,1)
        self.showMaximized()

        QtCore.QObject.connect(self.ui.lwLanguages, QtCore.SIGNAL("itemSelectionChanged()"), self.bindCollectionNames)
        QtCore.QObject.connect(self.ui.lwLanguages, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"), self.editLanguage)
        QtCore.QObject.connect(self.ui.lwLanguages, QtCore.SIGNAL("customContextMenuRequested(QPoint)"), self.onLanguageContextMenu)
        QtCore.QObject.connect(self.ui.lwCollections, QtCore.SIGNAL("itemSelectionChanged()"), self.bindData)
        QtCore.QObject.connect(self.ui.lwFilters, QtCore.SIGNAL("itemSelectionChanged()"), self.bindData)
        QtCore.QObject.connect(self.ui.tabWidget, QtCore.SIGNAL("currentChanged(int)"), self.onTabChanged)

        QtCore.QObject.connect(self.ui.action_New_item, QtCore.SIGNAL("triggered(bool)"), self.addItem)
        QtCore.QObject.connect(self.ui.actionNew_Language, QtCore.SIGNAL("triggered(bool)"), self.addLanguage)
        QtCore.QObject.connect(self.ui.actionQuit, QtCore.SIGNAL("triggered(bool)"), self.close)
        QtCore.QObject.connect(self.ui.actionCheck_for_updates, QtCore.SIGNAL("triggered(bool)"), self.checkForUpdates)
        QtCore.QObject.connect(self.ui.actionDelete_language, QtCore.SIGNAL("triggered(bool)"), self.deleteLanguage)
        QtCore.QObject.connect(self.ui.actionSettings, QtCore.SIGNAL("triggered(bool)"), self.manageSettings)
        QtCore.QObject.connect(self.ui.actionManage_Plugins, QtCore.SIGNAL("triggered(bool)"), self.managePlugins)
        QtCore.QObject.connect(self.ui.actionAbout_ReadingTool, QtCore.SIGNAL("triggered(bool)"), self.showAbout)
        
        self.ui.lwLanguages.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        
    def setupUserLayout(self):
        self.setWindowTitle(self.tr("ReadingTool - {0}").format(Application.user.username))
        self.setupSplitters()
        
        self.setupMenus()
        
        self.ui.lwLanguages.clear()
        self.ui.lwFilters.clear()
        
        self.bindLanguages()
        self.bindCollectionNames()
        self.bindFilters()
        
    def setupMenus(self):
        readItems = self.itemService.findRecentlyRead()
        newItems = self.itemService.findRecentlyCreated()
         
        self.ui.menuRecently_Seen_Items.clear()
        self.ui.menuRecently_Created_Items.clear()
        
        if len(readItems)==0:
            self.ui.menuRecently_Seen_Items.setEnabled(False)
        else:
            self.ui.menuRecently_Seen_Items.setEnabled(True)
            
            for item in readItems:
                action = QtGui.QAction(self.ui.menuRecently_Seen_Items)
                action.setText(item.name())
                action.setData(item)
                action.connect(action, QtCore.SIGNAL("triggered()"), lambda item=action.data(): self.readItem(item))
                self.ui.menuRecently_Seen_Items.addAction(action)
              
        if len(readItems)==0:
            self.ui.menuRecently_Created_Items.setEnabled(False)
        else:
            self.ui.menuRecently_Created_Items.setEnabled(True)
            
            for item in newItems:
                action = QtGui.QAction(self.ui.menuRecently_Created_Items)
                action.setText(item.name())
                action.setData(item)
                action.connect(action, QtCore.SIGNAL("triggered()"), lambda item=action.data(): self.readItem(item))
                self.ui.menuRecently_Created_Items.addAction(action)
            
        users = self.userService.findAll(orderBy="username")
        
        self.ui.menuProfiles.clear()
        action = QtGui.QAction(self.ui.menuProfiles)
        action.setText("Manage profiles")
        action.connect(action, QtCore.SIGNAL("triggered()"), self.manageProfiles)
                       
        self.ui.menuProfiles.addAction(action)
                
        if len(users)>0:
            self.ui.menuProfiles.addSeparator()
            
            for user in users:
                action = QtGui.QAction(self.ui.menuProfiles)
                action.setText(user.username)
                action.setData(user)
                action.connect(action, QtCore.SIGNAL("triggered()"), lambda user=action.data(): self.changeProfile(user))
                action.setToolTip("Switch to profile {0}".format(user.username))
                self.ui.menuProfiles.addAction(action)
         
    def setupSplitters(self):
        self.ui.splitter.setHandleWidth(7)
        self.addHandleToSplitter(self.ui.splitter.handle(1), self.ui.splitter.orientation())
        self.addHandleToSplitter(self.ui.splitter.handle(2), self.ui.splitter.orientation())
        
        self.ui.verticalSplitter.setHandleWidth(7)
        self.addHandleToSplitter(self.ui.verticalSplitter.handle(1), self.ui.verticalSplitter.orientation())
    
    def addHandleToSplitter(self, handle, orientation):
        if orientation==QtCore.Qt.Horizontal:
            layout = QtGui.QHBoxLayout(handle)
            layout.setSpacing(0)
            layout.setMargin(0)
            
            line = QtGui.QFrame(handle)
            line.setFrameShape(QtGui.QFrame.VLine)
            line.setFrameShadow(QtGui.QFrame.Sunken)
            layout.addWidget(line)
        else:
            layout = QtGui.QVBoxLayout(handle)
            layout.setSpacing(0)
            layout.setMargin(0)
            
            line = QtGui.QFrame(handle)
            line.setFrameShape(QtGui.QFrame.HLine)
            line.setFrameShadow(QtGui.QFrame.Sunken)
            layout.addWidget(line)
         
    def onLanguageContextMenu(self, point):
        item = self.ui.lwLanguages.itemAt(point)
        
        if item is None:
            return
        
        menu = QtGui.QMenu(self.ui.lwLanguages)
        
        action = QtGui.QAction(menu)
        action.setText("Edit language")
        action.connect(action, QtCore.SIGNAL("triggered()"), lambda: self.editLanguage(item))        
        menu.addAction(action)
          
        menu.addAction(self.ui.actionDelete_language)
        
        menu.exec_(QtGui.QCursor.pos())
        
    def bindLanguages(self):
        self.ui.lwLanguages.clear()
        languages = self.languageService.findAll()
        
        for language in languages:
            item = QtGui.QListWidgetItem(language.name)
            item.setData(QtCore.Qt.UserRole, language)
            self.ui.lwLanguages.addItem(item)
        
    def bindCollectionNames(self):
        self.ui.lwCollections.clear()
        languageIds = [str(item.data(QtCore.Qt.UserRole).languageId) for item in self.ui.lwLanguages.selectedItems()]
        collections = self.itemService.collectionsByLanguages(languageIds)
        
        for collection in collections:
            item = QtGui.QListWidgetItem(collection)
            item.setData(QtCore.Qt.UserRole, collection)
            self.ui.lwCollections.addItem(item)
            
        self.bindData()

    def bindFilters(self):
        self.ui.lwFilters.clear()
        
        if self.ui.tabWidget.currentIndex()==0:
            item = QtGui.QListWidgetItem("Text Items")
            item.setData(QtCore.Qt.UserRole, "#text")
            self.ui.lwFilters.addItem(item)
            
            item = QtGui.QListWidgetItem("Video Items")
            item.setData(QtCore.Qt.UserRole, "#video")
            self.ui.lwFilters.addItem(item)
            
            item = QtGui.QListWidgetItem("Single Items")
            item.setData(QtCore.Qt.UserRole, "#single")
            self.ui.lwFilters.addItem(item)
            
            item = QtGui.QListWidgetItem("Parallel Items")
            item.setData(QtCore.Qt.UserRole, "#parallel")
            self.ui.lwFilters.addItem(item)
                
            item = QtGui.QListWidgetItem("Media Items")
            item.setData(QtCore.Qt.UserRole, "#media")
            self.ui.lwFilters.addItem(item)
        elif self.ui.tabWidget.currentIndex()==1:
            item = QtGui.QListWidgetItem("Known")
            item.setData(QtCore.Qt.UserRole, "#known")
            self.ui.lwFilters.addItem(item)
            
            item = QtGui.QListWidgetItem("Unknown")
            item.setData(QtCore.Qt.UserRole, "#unknown")
            self.ui.lwFilters.addItem(item)
            
            item = QtGui.QListWidgetItem("Ignored")
            item.setData(QtCore.Qt.UserRole, "#ignored")
            self.ui.lwFilters.addItem(item)
        
    def onTabChanged(self, tabIndex):
        self.bindFilters()
        self.bindData()
        
    def bindData(self):
        if self.ui.tabWidget.currentIndex()==0:
            self.ui.lwCollections.show()
            self.bindItems()
        elif self.ui.tabWidget.currentIndex()==1:
            self.ui.lwCollections.hide()
            self.bindTerms()
        
    def bindItems(self):
        if len(self.ui.tabItems.children())==0:
            self.itemsForm = ItemsForm()
            self.itemsForm.setParent(self)
            
            verticalLayout = QtGui.QVBoxLayout()
            verticalLayout.addWidget(self.itemsForm)
            
            self.ui.tabItems.setLayout(verticalLayout)
            
        languages = [item.data(QtCore.Qt.UserRole).name for item in self.ui.lwLanguages.selectedItems()]
        collectionNames = [item.data(QtCore.Qt.UserRole) for item in self.ui.lwCollections.selectedItems()]
        filters = [item.data(QtCore.Qt.UserRole) for item in self.ui.lwFilters.selectedItems()]
        
        self.itemsForm.setFilters(languages, collectionNames, filters)
        self.itemsForm.bindItems()
        
        self.ui.tabWidget.setTabText(0, "Items ({0})".format(self.itemsForm.getCount()))
        self.ui.tabWidget.setTabToolTip(0, "Found {0} items in the search".format(self.itemsForm.getCount()))
        self.ui.tabWidget.setTabText(1, "Terms")
        self.ui.tabWidget.setTabToolTip(1, "")
        
    def bindTerms(self):
        if len(self.ui.tabTerms.children())==0:
            self.termsForm = TermsForm()
            self.termsForm.setParent(self)
            
            verticalLayout = QtGui.QVBoxLayout()
            verticalLayout.addWidget(self.termsForm)
            
            self.ui.tabTerms.setLayout(verticalLayout)
            
        languages = [item.data(QtCore.Qt.UserRole).name for item in self.ui.lwLanguages.selectedItems()]
        filters = [item.data(QtCore.Qt.UserRole) for item in self.ui.lwFilters.selectedItems()]
        
        self.termsForm.setFilters(languages, filters)
        self.termsForm.bindTerms()
        
        self.ui.tabWidget.setTabText(0, "Items")
        self.ui.tabWidget.setTabToolTip(0, "")
        self.ui.tabWidget.setTabText(1, "Terms ({0})".format(self.termsForm.getCount()))
        self.ui.tabWidget.setTabToolTip(1, "Found {0} terms in the search".format(self.itemsForm.getCount()))
        
    def addItem(self):
        self.dialog = ItemDialogForm()
        self.dialog.setItem(0)
        self.dialog.show()
        #TODO refresh items
        
    def readItem(self, item):
        self.reader = ReaderWindow()
        self.reader.readItem(item.itemId)
        self.reader.show()
        
    def addLanguage(self):
        self.dialog = LanguagesForm()
        self.dialog.setLanguage()
        self.dialog.bindLanguage()
        self.dialog.exec_()
        
        if self.dialog.hasSaved:
            self.bindLanguages()
        
    def editLanguage(self, item):
        languageId = item.data(QtCore.Qt.UserRole).languageId
        self.dialog = LanguagesForm()
        self.dialog.setLanguage(languageId)
        self.dialog.bindLanguage()
        self.dialog.exec_()
        
        if self.dialog.hasSaved:
            self.bindLanguages()            
        
    def deleteLanguage(self, item):
        languages = self.ui.lwLanguages.selectedItems()
        names = "\n".join([x.data(QtCore.Qt.UserRole).name for x in languages])
        result = QtGui.QMessageBox.question(self, "Delete Language", "Are you sure you want to delete:\n{0}".format(names), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        
        if result==QtGui.QMessageBox.Yes:
            for languageId in [x.data(QtCore.Qt.UserRole).languageId for x in languages]:
                self.languageService.delete(languageId)
                
            self.bindLanguages()
            self.bindCollectionNames()
        else:
            print("skipped")
            
    def checkForUpdates(self):
        try:
            storageService = StorageService()
            checkForUpdate = storageService.find(StorageService.SOFTWARE_CHECK_UPDATES, "true")
             
            if not StringUtil.isTrue(checkForUpdate):
                return
         
            softwareVersion = storageService.find(StorageService.SOFTWARE_VERSION, "0.0")
            webService = WebService()
             
            result = webService.checkForNewVersion()
             
            if not result:
                Qt.QMessageBox.information(self, "Unable to check", "Could not connect to server or invalid response. Please try again later.", Qt.QMessageBox.Ok)
                return
             
            if float(result["version"])>float(softwareVersion):
                Qt.QMessageBox.information(self, result["title"], result["message"], Qt.QMessageBox.Ok)
            else:
                Qt.QMessageBox.information(self, "No new version", "You are using the lastest version.", Qt.QMessageBox.Ok)
        except Exception as e:
            logging.error(str(e))        
    
    def manageProfiles(self):
        self.dialog = ProfilesForm()
        self.dialog.exec_()
        self.setupMenus()
        
        if self.dialog.switchProfile is not None:
            self.changeProfile(self.dialog.switchProfile)
        
    def changeProfile(self, user):
        Application.user = user
        userService = UserService()
        userService.loginUser(user.userId)
        self.setupUserLayout()

    def manageSettings(self):
        self.dialog = SettingsForm()
        self.dialog.bindSettings()
        self.dialog.exec_()
        
    def managePlugins(self):
        self.dialog = PluginsForm()
        self.dialog.bindAll()
        self.dialog.exec_()
        
    def showAbout(self):
        self.dialog = AboutForm()
        self.dialog.exec_()