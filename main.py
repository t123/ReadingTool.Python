import sys, os, datetime, shutil, time
from PyQt4 import QtGui
from ui.main import MainWindow
from lib.misc import Application
from lib.services.service import UserService
from lib.models.model import User
from server.server import Server

def checkUser():
    userService = UserService()
    users = userService.findAll(1)

    if len(users) == 0:
        user = User()
        user.username = "New Profile"
        user = userService.save(user)
        Application.user = user
        userService.loginUser(user.userId)
    else:
        Application.user = users[0]
        userService.loginUser(users[0].userId)
        
def backupDb(stage):
    if not os.path.exists(Application.connectionString):
        return
    
    path = os.path.join(Application.pathDatabase, "backup")
    
    if not os.path.exists(path):
        os.mkdir(path)
        
    counter = 1
    backupFile = "{0}-{1}-{2}.sqlite".format(datetime.datetime.now().strftime("%Y-%m-%d"), stage, counter)
    
    while os.path.exists(os.path.join(path, backupFile)):
        counter += 1
        backupFile = "{0}-{1}-{2}.sqlite".format(datetime.datetime.now().strftime("%Y-%m-%d"), stage, counter)
        
    shutil.copy(Application.connectionString, os.path.join(path, backupFile))
    
    files = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path,file))]
    
    if len(files)>15:
        d = []
        for file in files:
            d.append([file, os.path.getmtime(os.path.join(path,file))])
            
        d = sorted(d, key=lambda tup:tup[1])
        
        difference = len(files)-15
        
        if difference>0:
            for i in range(0, difference):
                os.remove(os.path.join(path, d[i][0]))
          
def cleanOldFiles():
    path = Application.pathOutput
    files = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path,file))]
    
    for file in files:
        (name, ext) = os.path.splitext(file)
        
        if not ext.lower()==".html" and not ext.lower()==".xml":
            continue
        
        now = time.time() 
        created = os.path.getmtime(os.path.join(path,file))
        
        if now-created>60*60*24*7:
            os.remove(os.path.join(path, file))
        
if __name__=="__main__":
    cleanOldFiles()
    checkUser()
    backupDb("start")
    
    Application.server = Server(embed=True)
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
    Application.server.start()
    ret = app.exec_()
    Application.server.stop()
    backupDb("stop")
    sys.exit(ret)
