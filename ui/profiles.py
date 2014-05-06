from PyQt4 import QtCore, QtGui, Qt

from lib.misc import Application
from lib.services.service import UserService
from lib.models.model import User
from ui.views.profiles import Ui_Profiles

class ProfilesForm(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Profiles()
        self.ui.setupUi(self)
        
        QtCore.QObject.connect(self.ui.lvUsers, QtCore.SIGNAL("currentItemChanged(QListWidgetItem*,QListWidgetItem*)"), self.populateItem)
        QtCore.QObject.connect(self.ui.pbSave, QtCore.SIGNAL("clicked()"), self.saveUser)
        QtCore.QObject.connect(self.ui.pbAdd, QtCore.SIGNAL("clicked()"), self.addUser)
        QtCore.QObject.connect(self.ui.pbDelete, QtCore.SIGNAL("clicked()"), self.deleteUser)
        
        self.userService = UserService()
        self.updateUsers();
        
    def _currentUser(self):
        if self.ui.lvUsers.currentItem() is None:
            return None
        
        return self.userService.findOne(self.ui.lvUsers.currentItem().data(QtCore.Qt.UserRole).userId)
        
    def populateItem(self, current, previous):
        if current is None:
            return
        
        user = self.userService.findOne(current.data(QtCore.Qt.UserRole).userId)
        self.ui.leUsername.setText(user.username)
        self.ui.leAccessKey.setText(user.accessKey)
        self.ui.leAccessSecret.setText(user.accessSecret)
        self.ui.cbSyncData.setChecked(user.syncData)
        
        if self.ui.lvUsers.currentItem().data(QtCore.Qt.UserRole).userId==Application.user.userId:
            self.ui.pbDelete.setEnabled(False)
            self.ui.pbSwitch.setEnabled(False)
        else:
            self.ui.pbDelete.setEnabled(True)
            self.ui.pbSwitch.setEnabled(True)
        
    def saveUser(self):
        if self.ui.lvUsers.currentItem() is None:
            return
        
        user = self._currentUser()
        user.username = self.ui.leUsername.text()
        user.accessKey = self.ui.leAccessKey.text()
        user.accessSecret = self.ui.leAccessSecret.text()
        user.syncData = self.ui.cbSyncData.isChecked()
        self.userService.save(user)
        self.updateUsers()
        
    def deleteUser(self):
        user = self._currentUser()
        
        if user is None:
            return
        
        self.userService.delete(user.userId)
        self.updateUsers()
        
    def addUser(self):
        counter = 1
        username = "New Profile"
        
        while self.userService.findOneByUsername(username) is not None:
            username = "New Profile %d" % counter
            counter += 1
            
        user = User()
        user.username = username
        self.userService.save(user)
        self.updateUsers()
        
    def updateUsers(self):
        users = self.userService.findAll("username", 100000)
        
        self.ui.lvUsers.clear()
        for user in users:
            item = QtGui.QListWidgetItem(user.username)
            item.setData(QtCore.Qt.UserRole, user)
            self.ui.lvUsers.addItem(item)
        
        if self.ui.lvUsers.currentItem() is None:
            self.ui.lvUsers.setCurrentItem(self.ui.lvUsers.item(0))