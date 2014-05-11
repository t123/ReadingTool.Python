from PyQt4 import Qt, QtGui, QtCore
from lib.misc import Application
from lib.services.service import UserService, ItemService

from ui.views.main import Ui_MainWindow
from ui.reader import ReaderWindow
from ui.profiles import ProfilesForm
from ui.languages import LanguagesForm
from ui.plugins import PluginsForm
from ui.items import ItemsForm
from ui.terms import TermsForm
from ui.itemdialog import ItemDialogForm

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.userService = UserService()
        self.itemService = ItemService()
        
        self.mainWindow = Ui_MainWindow()
        self.mainWindow.setupUi(self)
        self.mainWindow.verticalLayout.setStretch(2, 1)
        self.changeView("items")
        
        QtCore.QObject.connect(self.mainWindow.pbLanguages, QtCore.SIGNAL("clicked()"), lambda view = "languages": self.changeView(view))
        QtCore.QObject.connect(self.mainWindow.tbProfiles, QtCore.SIGNAL("clicked()"), lambda view = "profiles": self.changeView(view))
        QtCore.QObject.connect(self.mainWindow.pbPlugins, QtCore.SIGNAL("clicked()"), lambda view = "plugins": self.changeView(view))
        QtCore.QObject.connect(self.mainWindow.tbItems, QtCore.SIGNAL("clicked()"), lambda view = "items": self.changeView(view))
        QtCore.QObject.connect(self.mainWindow.pbTerms, QtCore.SIGNAL("clicked()"), lambda view = "terms": self.changeView(view))
        
        self.showMaximized()

    def updateItems(self):
        readItems = self.itemService.findRecentlyRead()
        newItems = self.itemService.findRecentlyCreated()
        
        menu = QtGui.QMenu()
        
        action = QtGui.QAction(self)
        action.setText("Add item")
        action.connect(action, QtCore.SIGNAL("triggered()"), self.addItem)
        menu.addAction(action)
            
        readMenu = QtGui.QMenu("Recently Read", self)
        newMenu = QtGui.QMenu("Recently Created", self)
        
        for item in readItems:
            action = QtGui.QAction(self)
            action.setText(item.name())
            action.setData(item)
            action.connect(action, QtCore.SIGNAL("triggered()"), lambda item=action.data(): self.readItem(item))
            readMenu.addAction(action)
             
        for item in newItems:
            action = QtGui.QAction(self)
            action.setText(item.name())
            action.setData(item)
            action.connect(action, QtCore.SIGNAL("triggered()"), lambda item=action.data(): self.readItem(item))
            newMenu.addAction(action)
        
        menu.addMenu(readMenu)
        menu.addMenu(newMenu)
        self.mainWindow.tbItems.setMenu(menu)
        
    def addItem(self):
        self.dialog = ItemDialogForm()
        self.dialog.setItem(0)
        self.dialog.show()
        
    def readItem(self, item):
        reader = ReaderWindow()
        reader.readItem(item.itemId)
        reader.show()
    
    def updateProfiles(self):
        users = self.userService.findAll(orderBy="username")
         
        menu = QtGui.QMenu()
        
        for user in users:
            action = QtGui.QAction(menu)
            action.setText(user.username)
            action.setData(user)
            action.connect(action, QtCore.SIGNAL("triggered()"), lambda user=action.data(): self.changeProfile(user))
            menu.addAction(action)
        
        self.mainWindow.tbProfiles.setMenu(menu)
        
    def changeProfile(self, user):
        Application.user = user
        self.changeView(self.currentView)
    
    def _removeChild(self):
        count = self.mainWindow.verticalLayout.count()
        
        if count>2:
            layout = self.mainWindow.verticalLayout.takeAt(count-1)
            
            if layout is not None:
                widget = layout.widget()
                if widget is not None:
                    widget.deleteLater()
                    
    def changeView(self, viewName):
        self.currentView = viewName
        viewName = viewName.lower()
        
        if viewName=="profiles":
            self._removeChild()
            profilesForm = ProfilesForm()
            self.mainWindow.verticalLayout.addWidget(profilesForm)
            
        elif viewName=="languages":
            self._removeChild()
            languagesForm = LanguagesForm()
            self.mainWindow.verticalLayout.addWidget(languagesForm)
            
        elif viewName=="plugins":
            self._removeChild()
            pluginsForm = PluginsForm()
            self.mainWindow.verticalLayout.addWidget(pluginsForm)
            
        elif viewName=="items":
            self._removeChild()
            itemsForm = ItemsForm()
            self.mainWindow.verticalLayout.addWidget(itemsForm)
            
        elif viewName=="terms":
            self._removeChild()
            termsForm = TermsForm()
            self.mainWindow.verticalLayout.addWidget(termsForm)
            
        self.updateItems()
        self.updateProfiles()
        self.setWindowTitle("ReadingTool - %s" % Application.user.username)
