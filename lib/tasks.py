import sys, os, datetime, shutil, time, logging
from lib.stringutil import StringUtil
from lib.misc import Application
from lib.services.service import UserService, DatabaseService, StorageService
from lib.models.model import User

class Startup:
    def __init__(self):
        self.storage = StorageService()
        self.createDb()
        self.setServers()
    
    def createDb(self):
        databaseService = DatabaseService()
        databaseService.createDb()
        
    def setServers(self):
        local = self.storage.find(StorageService.SERVER_LOCAL, "http://localhost:8080") 
        remote = self.storage.find(StorageService.SERVER_REMOTE, "http://api.readingtool.net")
        
        Application.apiServer = local 
        Application.remoteServer = remote
        
        logging.debug("Local server=%s" % Application.apiServer) 
        logging.debug("Remote server=%s" % Application.remoteServer) 
            
    def checkUser(self):
        userService = UserService()
        users = userService.findAll()
    
        if len(users) == 0:
            user = User()
            user.username = "New Profile"
            user = userService.save(user)
            Application.user = user
            userService.loginUser(user.userId)
        else:
            Application.user = users[0]
            userService.loginUser(users[0].userId)
            
    def backupDb(self, stage):
        if not os.path.exists(Application.connectionString):
            return
        
        path = self.storage.find(StorageService.DB_BACKUP_DIRECTORY)
        
        if StringUtil.isEmpty(path) or not os.path.exists(path):
            path = os.path.join(Application.pathDatabase, "backup")
        
        if not os.path.exists(path):
            os.mkdir(path)
            
        logging.info("Backup directory: %s" % path)
        
        counter = 1
        backupFile = "{0}-{1}-{2}.sqlite".format(datetime.datetime.now().strftime("%Y-%m-%d"), stage, counter)
        
        while os.path.exists(os.path.join(path, backupFile)):
            counter += 1
            backupFile = "{0}-{1}-{2}.sqlite".format(datetime.datetime.now().strftime("%Y-%m-%d"), stage, counter)
            
        shutil.copy(Application.connectionString, os.path.join(path, backupFile))
        
        files = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path,file))]
        
        try:
            maxFiles = int(self.storage.find(StorageService.DB_BACKUP_MAXFILES, 30))
        except:
            logging.debug("Invalid db_backup_maxfiles, default to 30")
            maxFiles = 30
            
        if len(files)>maxFiles:
            d = []
            for file in files:
                d.append([file, os.path.getmtime(os.path.join(path,file))])
                
            d = sorted(d, key=lambda tup:tup[1])
            
            difference = len(files)-maxFiles
            
            if difference>0:
                for i in range(0, difference):
                    removePath = os.path.join(path, d[i][0])
                    logging.debug("Removing %s" % removePath)
                    os.remove(removePath)
              
    def compact(self):
        lastVacuum = StorageService.sfind(StorageService.DB_LAST_VACUUM, None)
        
        if lastVacuum is None:
            StorageService.ssave(StorageService.DB_LAST_VACUUM, time.time())
            return
        
        if time.time()-float(lastVacuum)>60*60*24*7:
            logging.debug("compacting database")
            databaseService = DatabaseService()
            databaseService.compact()
            StorageService.ssave(StorageService.DB_LAST_VACUUM, time.time())            
        
    def cleanOldFiles(self):
        path = Application.pathOutput
        files = [file for file in os.listdir(path) if os.path.isfile(os.path.join(path,file))]
        
        for file in files:
            (name, ext) = os.path.splitext(file)
            
            ext = ext.lower()
            
            if not ext in ["html", "xml", "pdf"]:
                continue
            
            now = time.time() 
            created = os.path.getmtime(os.path.join(path,file))
            
            if now-created>60*60*24*7:
                os.remove(os.path.join(path, file))
    
    def checkDbForUpgrade(self):
        databaseService = DatabaseService()
        
        if not databaseService.upgradeRequired():
            return
                    
        self.backupDb("dbupgrade")
        databaseService.upgradeDb()
