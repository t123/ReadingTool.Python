import sys, logging
from PyQt4 import QtGui
from ui.main import MainWindow
from lib.misc import Application
from server.server import Server
from lib.tasks import Startup

try:
    from lib.services.service import StorageService
    from lib.stringutil import StringUtil
    
    if StringUtil.isTrue(StorageService.sfind(StorageService.SOFTWARE_DEBUG, "false")):
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
        Application.debug = True
    else:
        logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
        
    logging.info("Debug is: {}".format(Application.debug))
except Exception as e:
    print(str(e))
    logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.info("Debug failed: {}".format(str(e)))
    
if __name__=="__main__":
    try:
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
    except Exception as e:
        try:
            logging.error(e)
            
            from lib.services.web import WebService
            webService = WebService()
            webService.reportException()
        except Exception as inner:
            logging.error(inner)
