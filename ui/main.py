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
        QtCore.QObject.connect(self.ui.lwCollections, QtCore.SIGNAL("itemSelectionChanged()"), self.bindData)
        QtCore.QObject.connect(self.ui.lwFilters, QtCore.SIGNAL("itemSelectionChanged()"), self.bindData)
        QtCore.QObject.connect(self.ui.tabWidget, QtCore.SIGNAL("currentChanged(int)"), self.bindData)

        #=======================================================================
        # self.mainWindow.verticalLayout.setStretch(2, 1)
        # self.changeView("items")
        #  
        # QtCore.QObject.connect(self.mainWindow.pbLanguages, QtCore.SIGNAL("clicked()"), lambda view = "languages": self.changeView(view))
        # QtCore.QObject.connect(self.mainWindow.tbProfiles, QtCore.SIGNAL("clicked()"), lambda view = "profiles": self.changeView(view))
        # QtCore.QObject.connect(self.mainWindow.pbPlugins, QtCore.SIGNAL("clicked()"), lambda view = "plugins": self.changeView(view))
        # QtCore.QObject.connect(self.mainWindow.tbItems, QtCore.SIGNAL("clicked()"), lambda view = "items": self.changeView(view))
        # QtCore.QObject.connect(self.mainWindow.pbTerms, QtCore.SIGNAL("clicked()"), lambda view = "terms": self.changeView(view))
        #  
        # self.showMaximized()
        # self.checkVersion()
        #=======================================================================
        
    def setupUserLayout(self):
        self.ui.lwLanguages.clear()
        self.ui.lwFilters.clear()
        
        self.bindLanguages()
        self.bindCollectionNames()
        self.bindFilters()
        
    def bindLanguages(self):
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
        
    def bindData(self):
        if self.ui.tabWidget.currentIndex()==0:
            self.bindItems()
        elif  self.ui.tabWidget.currentIndex()==1:
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
        
    def bindTerms(self):
        if len(self.ui.tabTerms.children())==0:
            self.termsForm = TermsForm()
            self.termsForm.setParent(self)
            
            verticalLayout = QtGui.QVBoxLayout()
            verticalLayout.addWidget(self.termsForm)
            
            self.ui.tabTerms.setLayout(verticalLayout)
            
        self.termsForm.bindTerms()
    
    #===========================================================================
    # def checkVersion(self):
    #     try:
    #         storageService = StorageService()
    #         checkForUpdate = storageService.find(StorageService.SOFTWARE_CHECK_UPDATES, "true")
    #         
    #         if not StringUtil.isTrue(checkForUpdate):
    #             return
    #     
    #         softwareVersion = storageService.find(StorageService.SOFTWARE_VERSION, "0.0")
    #         webService = WebService()
    #         
    #         result = webService.checkForNewVersion()
    #         
    #         if not result:
    #             return
    #         
    #         if float(result["version"])>float(softwareVersion):
    #             Qt.QMessageBox.information(self, result["title"], result["message"], Qt.QMessageBox.Ok)
    #     except Exception as e:
    #         logging.error(str(e))
    #             
    # def updateItems(self):
    #     readItems = self.itemService.findRecentlyRead()
    #     newItems = self.itemService.findRecentlyCreated()
    #     
    #     menu = QtGui.QMenu()
    #     
    #     action = QtGui.QAction(self)
    #     action.setText("Add item")
    #     action.connect(action, QtCore.SIGNAL("triggered()"), self.addItem)
    #     menu.addAction(action)
    #         
    #     readMenu = QtGui.QMenu("Recently Read", self)
    #     newMenu = QtGui.QMenu("Recently Created", self)
    #     
    #     for item in readItems:
    #         action = QtGui.QAction(self)
    #         action.setText(item.name())
    #         action.setData(item)
    #         action.connect(action, QtCore.SIGNAL("triggered()"), lambda item=action.data(): self.readItem(item))
    #         readMenu.addAction(action)
    #          
    #     for item in newItems:
    #         action = QtGui.QAction(self)
    #         action.setText(item.name())
    #         action.setData(item)
    #         action.connect(action, QtCore.SIGNAL("triggered()"), lambda item=action.data(): self.readItem(item))
    #         newMenu.addAction(action)
    #     
    #     menu.addMenu(readMenu)
    #     menu.addMenu(newMenu)
    #     self.mainWindow.tbItems.setMenu(menu)
    #     
    # def addItem(self):
    #     self.dialog = ItemDialogForm()
    #     self.dialog.setItem(0)
    #     self.dialog.show()
    #     
    # def readItem(self, item):
    #     reader = ReaderWindow()
    #     reader.readItem(item.itemId)
    #     reader.show()
    # 
    # def updateProfiles(self):
    #     users = self.userService.findAll(orderBy="username")
    #      
    #     menu = QtGui.QMenu()
    #     
    #     for user in users:
    #         action = QtGui.QAction(menu)
    #         action.setText(user.username)
    #         action.setData(user)
    #         action.connect(action, QtCore.SIGNAL("triggered()"), lambda user=action.data(): self.changeProfile(user))
    #         menu.addAction(action)
    #     
    #     self.mainWindow.tbProfiles.setMenu(menu)
    #     
    # def changeProfile(self, user):
    #     Application.user = user
    #     self.changeView(self.currentView)
    # 
    # def _removeChild(self):
    #     count = self.mainWindow.verticalLayout.count()
    #     
    #     if count>2:
    #         layout = self.mainWindow.verticalLayout.takeAt(count-1)
    #         
    #         if layout is not None:
    #             widget = layout.widget()
    #             if widget is not None:
    #                 widget.deleteLater()
    #                 
    # def changeView(self, viewName):
    #     self.currentView = viewName
    #     viewName = viewName.lower()
    #     
    #     if viewName=="profiles":
    #         self._removeChild()
    #         profilesForm = ProfilesForm()
    #         self.mainWindow.verticalLayout.addWidget(profilesForm)
    #         
    #     elif viewName=="languages":
    #         self._removeChild()
    #         languagesForm = LanguagesForm()
    #         self.mainWindow.verticalLayout.addWidget(languagesForm)
    #         
    #     elif viewName=="plugins":
    #         self._removeChild()
    #         pluginsForm = PluginsForm()
    #         self.mainWindow.verticalLayout.addWidget(pluginsForm)
    #         
    #     elif viewName=="items":
    #         self._removeChild()
    #         itemsForm = ItemsForm()
    #         self.mainWindow.verticalLayout.addWidget(itemsForm)
    #         
    #     elif viewName=="terms":
    #         self._removeChild()
    #         termsForm = TermsForm()
    #         self.mainWindow.verticalLayout.addWidget(termsForm)
    #         
    #     self.updateItems()
    #     self.updateProfiles()
    #     self.setWindowTitle("ReadingTool - %s" % Application.user.username)
    #===========================================================================
