from PyQt4 import QtCore, QtGui, Qt

from lib.misc import Application
from lib.services.service import UserService
from lib.services.web import WebService
from lib.models.model import User
from ui.views.profileedit import Ui_ChangeProfile
from lib.stringutil import StringUtil

class ChangeProfileForm(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_ChangeProfile()
        self.ui.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.userService = UserService()
        
        QtCore.QObject.connect(self.ui.actionSave, QtCore.SIGNAL("triggered(bool)"), self.saveProfile)
        QtCore.QObject.connect(self.ui.actionCancel, QtCore.SIGNAL("triggered(bool)"), self.resetProfile)
        
        self.hasSaved = False
           
    def setProfile(self, id):
        if id==0 or id is None:
            self.profile = User()
            self.setWindowTitle("Add new profile")
        else:
            self.profile = self.userService.findOne(id)
            self.setWindowTitle("Edit profile - {0}".format(self.profile.username))
            
    def bindProfile(self):
        self.ui.leUsername.setText(self.profile.username)
        self.ui.leAccessKey.setText(self.profile.accessKey)
        self.ui.leAccessSecret.setText(self.profile.accessSecret)
        
    def saveProfile(self):
        self.profile.username = self.ui.leUsername.text()
        self.profile.accessKey = self.ui.leAccessKey.text().strip()
        self.profile.accessSecret = self.ui.leAccessSecret.text().strip()
        self.profile.syncData = False
         
        webService = WebService()
         
        if not StringUtil.isEmpty(self.profile.accessKey) and not StringUtil.isEmpty(self.profile.accessSecret): 
            if not webService.validateCredentials(self.profile.accessKey, self.profile.accessSecret):
                Qt.QMessageBox.critical(self, "Could not save", "Either your Access Key or Access Secret is incorrect.")
                return
                
        self.userService.save(self.profile)
        self.setProfile(self.profile.userId)
        
        self.hasSaved = True
        
    def resetProfile(self):
        self.setProfile(self.profile.userId)
        self.bindProfile()
