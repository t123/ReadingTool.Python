from PyQt4 import QtCore, QtGui, Qt

from lib.misc import Application
from lib.services.service import UserService
from lib.services.web import WebService
from lib.models.model import User
from ui.views.profiles import Ui_Profiles
from ui.editprofile import ChangeProfileForm
from lib.stringutil import StringUtil

class ProfilesForm(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_Profiles()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        QtCore.QObject.connect(self.ui.lwProfiles, QtCore.SIGNAL("currentItemChanged(QListWidgetItem*,QListWidgetItem*)"), self.updateUi)
        QtCore.QObject.connect(self.ui.pbSwitch, QtCore.SIGNAL("clicked()"), self.switchUser)
        QtCore.QObject.connect(self.ui.pbAdd, QtCore.SIGNAL("clicked()"), self.addUser)
        QtCore.QObject.connect(self.ui.pbEdit, QtCore.SIGNAL("clicked()"), self.editUser)
        QtCore.QObject.connect(self.ui.pbDelete, QtCore.SIGNAL("clicked()"), self.deleteUser)
        
        self.userService = UserService()
        self.bindProfiles();
        
        self.switchProfile = None
        
    def updateUi(self, item, previous):
        if item is None or item.data(QtCore.Qt.UserRole) is None:
            return
        
        userId = item.data(QtCore.Qt.UserRole).userId
        
        if userId==Application.user.userId:
            self.ui.pbDelete.setEnabled(False)
            self.ui.pbSwitch.setEnabled(False)
        else:
            self.ui.pbDelete.setEnabled(True)
            self.ui.pbSwitch.setEnabled(True)
            
    def bindProfiles(self):
        users = self.userService.findAll("username", 100000)
         
        self.ui.lwProfiles.clear()
        
        for user in users:
            item = QtGui.QListWidgetItem(user.username)
            item.setData(QtCore.Qt.UserRole, user)
            self.ui.lwProfiles.addItem(item)
            
        self.ui.lwProfiles.setCurrentRow(0)
                
    def addUser(self):
        self.dialog = ChangeProfileForm()
        self.dialog.setProfile(None)
        self.dialog.bindProfile()
        self.dialog.exec_()
        
        if self.dialog.hasSaved:
            self.bindProfiles()
    
    def editUser(self):
        self.dialog = ChangeProfileForm()
        self.dialog.setProfile(self.ui.lwProfiles.currentItem().data(QtCore.Qt.UserRole).userId)
        self.dialog.bindProfile()
        self.dialog.exec_()
        
        if self.dialog.hasSaved:
            self.bindProfiles()
    
    def deleteUser(self):
        user = self.userService.findOne(self.ui.lwProfiles.currentItem().data(QtCore.Qt.UserRole).userId)
        
        result = QtGui.QMessageBox.question(self, "Delete Profile", "Are you sure you want to delete <b>{0}</b>?".format(user.username), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        
        if result==QtGui.QMessageBox.Yes:
            self.userService.delete(user.userId)
            self.bindProfiles()
    
    def switchUser(self):
        self.switchProfile = self.userService.findOne(self.ui.lwProfiles.currentItem().data(QtCore.Qt.UserRole).userId)
        self.close()