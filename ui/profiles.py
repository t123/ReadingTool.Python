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
        QtCore.QObject.connect(self.ui.pbCancel, QtCore.SIGNAL("clicked()"), self.cancel)
        QtCore.QObject.connect(self.ui.leUsername, QtCore.SIGNAL("textChanged(QString)"), self.changed)
        QtCore.QObject.connect(self.ui.leAccessKey, QtCore.SIGNAL("textChanged(QString)"), self.changed)
        QtCore.QObject.connect(self.ui.leAccessSecret, QtCore.SIGNAL("textChanged(QString)"), self.changed)
        QtCore.QObject.connect(self.ui.cbSyncData, QtCore.SIGNAL("stateChanged(int)"), self.changed)
        
        self.userService = UserService()
        self.updateUsers();
        
        self.ui.splitter.setStretchFactor(0,0)
        self.ui.splitter.setStretchFactor(1,1)
        self.ui.pbSwitch.hide()
        
    def _currentUser(self):
        if self.ui.lvUsers.currentItem() is None:
            return None
        
        return self.userService.findOne(self.ui.lvUsers.currentItem().data(QtCore.Qt.UserRole).userId)
        
    def changed(self):
        self.ui.pbCancel.setEnabled(True)
        self.ui.pbSave.setEnabled(True)
        self.ui.lvUsers.setEnabled(False)
        self.ui.pbAdd.setEnabled(False)
        self.ui.pbDelete.setEnabled(False)
        self.ui.pbSwitch.setEnabled(False)
        self.changed = True
        
    def resetForm(self):
        self.ui.pbCancel.setEnabled(False)
        self.ui.pbSave.setEnabled(False)
        self.ui.lvUsers.setEnabled(True)
        self.ui.pbAdd.setEnabled(True)
        self.ui.pbDelete.setEnabled(True)
        self.ui.pbSwitch.setEnabled(True)
        self.changed = False
        
    def cancel(self):
        currentRow = self.ui.lvUsers.currentRow()
        self.ui.lvUsers.setCurrentRow(-1)
        self.ui.lvUsers.setCurrentRow(currentRow)
        self.resetForm()
        
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
            
        self.resetForm()
        
    def saveUser(self):
        user = None
        
        if self.ui.lvUsers.currentItem() is None:
            user = User()
        else:
            user = self._currentUser()
                    
        currentRow = self.ui.lvUsers.currentRow()
        
        user.username = self.ui.leUsername.text()
        user.accessKey = self.ui.leAccessKey.text()
        user.accessSecret = self.ui.leAccessSecret.text()
        user.syncData = self.ui.cbSyncData.isChecked()
        
        self.userService.save(user)
        self.updateUsers()
        self.ui.lvUsers.setCurrentRow(currentRow)
        
        self.resetForm()
        
        Application.user = user
        
    def deleteUser(self):
        user = self._currentUser()
        
        if user is None or self.changed or user.userId==Application.user.userId:
            return
        
        currentRow = self.ui.lvUsers.currentRow()
        self.userService.delete(user.userId)
        self.updateUsers()
        
        if currentRow>=self.ui.lvUsers.count():
            self.ui.lvUsers.setCurrentRow(self.ui.lvUsers.count()-1)
        else:
            self.ui.lvUsers.setCurrentRow(currentRow)
            
        self.resetForm()
        
    def addUser(self):
        counter = 1
        username = "New Profile"
        
        while self.userService.findOneByUsername(username) is not None:
            username = "New Profile %d" % counter
            counter += 1
            
        user = User()
        user.username = username
        user = self.userService.save(user)
        self.updateUsers(user.userId)
        
        self.resetForm()
        
    def updateUsers(self, selectedId=None):
        users = self.userService.findAll("username", 100000)
        
        self.ui.lvUsers.clear()
        for user in users:
            item = QtGui.QListWidgetItem(user.username)
            item.setData(QtCore.Qt.UserRole, user)
            self.ui.lvUsers.addItem(item)
            
            if selectedId is not None and user.userId==selectedId:
                self.ui.lvUsers.setCurrentItem(item)
        
        if self.ui.lvUsers.currentItem() is None and self.ui.lvUsers.count()>0:
            self.ui.lvUsers.setCurrentItem(self.ui.lvUsers.item(0))
            
    def keyPressEvent(self, event):
        if(self._currentUser() is None):
            return
        
        if event.key()==QtCore.Qt.Key_Delete:
            self.deleteUser()
            return
        
        if event.key()==QtCore.Qt.Key_Escape:
            self.cancel()
            return
            
        if event.modifiers() & QtCore.Qt.ControlModifier:
            if event.key()==QtCore.Qt.Key_S:
                self.saveUser()
                return
            
        return QtGui.QDialog.keyPressEvent(self, event)