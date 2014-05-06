import sys
import PyQt4.QtGui
from PyQt4 import QtGui
from ui.main import MainWindow
from ui.reader import ReaderWindow
from lib.misc import Application
from lib.services.service import UserService
from lib.models.model import User
from server.server import Server

def checkUser():
    userService = UserService()
    users = userService.findAll(1)
    
    if len(users)==0:
        user = User()
        user.username = "New Profile"
        user = userService.save(user)
        Application.user = user
        userService.loginUser(user.userId)
    else:
        Application.user = users[0]
        userService.loginUser(users[0].userId)
    
if __name__=="__main__":
    checkUser()
    
    Application.server = Server(embed=False)
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    Application.server.start()    
    ret = app.exec_()
    Application.server.stop()
    sys.exit(ret)