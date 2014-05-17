import sys, logging
from PyQt4 import QtGui
from ui.main import MainWindow
from lib.misc import Application
from server.server import Server
from lib.tasks import Startup

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

if __name__=="__main__":
    start = Startup()
    start.cleanOldFiles()
    start.checkUser()
    start.backupDb("start")
    start.checkDbForUpgrade()
         
    Application.server = Server(embed=True)
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    myapp.show()
       
    Application.server.start()
    ret = app.exec_()
    Application.server.stop()
    start.backupDb("stop")
    sys.exit(ret)
