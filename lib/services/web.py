import requests, uuid, base64, json, hashlib, hmac, time, logging, gzip
from urllib.parse import urlparse

from lib.db import Db
from lib.misc import Application
from lib.models.model import Item
from lib.models.parser import ParserInput
from lib.services.parser import LatexParser
from lib.services.service import ItemService, LanguageService, TermService

class WebService:
    def getStandardDictionary(self, uri, verb="POST", accessKey=None):
        return {
                    "Uri": uri,
                    "Verb": verb,
                    "Time": time.time(),
                    "Nonce": str(uuid.uuid1()),
                    "AccessKey": Application.user.accessKey if accessKey is None else accessKey
                }
        
    def logError(self, response):
        try:
            data = json.loads(response.content.decode("utf8"))
            logging.debug(data["code"])
            logging.debug(data["message"])
        except Exception as e:
            logging.debug(str(e))
            logging.debug(response.content)
             
    def createJsonSignatureHeaders(self, dictionary, contentType="application/json", accessKey=None, accessSecret=None, headers=None):
        data = json.dumps(dictionary, sort_keys=True)
        message = data.encode('utf-8')
        
        if accessSecret is None:
            accessSecret = Application.user.accessSecret.encode('utf-8')
        else:
            accessSecret = accessSecret.encode('utf-8')
             
        signature = base64.b64encode(hmac.new(accessSecret, message, digestmod=hashlib.sha256).digest())
        
        h = {
               "Content-Type": contentType,
               "X-Client": "RT",
               "X-Signature": signature,
               "X-AccessKey": Application.user.accessKey if accessKey is None else accessKey
               }
        
        if headers is not None:
            h.update(headers)
            
        return (data, signature, h)
        
    def segmentText(self, languageCode, content):
        uri = Application.remoteServer + "/api/v1/segment"
        
        data = self.getStandardDictionary(uri)
        data["LanguageCode"] = languageCode
        data["Content"] = content
        content, signature, headers = self.createJsonSignatureHeaders(data)
        
        try:
            r = requests.post(uri, headers=headers, data=content)
            
            if r.status_code==200:
                return r.content.decode('utf8')
                
            self.logError(r)
            
        except requests.exceptions.RequestException:
            pass
        
        return None
    
    def validateCredentials(self, accessKey, accessSecret):
        uri = Application.remoteServer + "/api/v1/validatecredentials"
        data = self.getStandardDictionary(uri, accessKey=accessKey)
        
        content, signature, headers = self.createJsonSignatureHeaders(data, accessKey=accessKey, accessSecret=accessSecret)
        
        try:
            r = requests.post(uri, headers=headers, data=content)
            
            if r.status_code==200:
                return True
            
            self.logError(r)
                
        except requests.exceptions.RequestException:
            pass
              
        return False
    
    def checkForNewVersion(self):
        uri = Application.remoteServer + "/api/v1/latestversion"
        r = requests.get(uri, headers={"X-Client": "RT"})
        
        if r.status_code!=200:
            self.logError(r)
            return None
        
        return json.loads(r.text)
        
    def createPdf(self, itemId):
        itemService = ItemService()
        languageService = LanguageService()
        termService = TermService()
        parser = LatexParser()
        
        item = itemService.findOne(itemId)
        
        pi = ParserInput()
        pi.item = item
        pi.language1 = languageService.findOne(item.l1LanguageId)
        pi.language2 = None
        pi.asParallel = False
        pi.terms, pi.multiTerms = termService.findAllForParsing(item.l1LanguageId)
        
        self.po = parser.parse(pi)
    
        uri = Application.remoteServer + "/api/v1/createpdf"
        
        data = self.getStandardDictionary(uri)
        data["Latex"] = self.po.html
        data["Title"] = item.name()
        
        content, signature, headers = self.createJsonSignatureHeaders(data, headers={ "Content-Encoding": "gzip"})
        data = gzip.compress(content.encode())
        
        try:
            r = requests.post(uri, headers=headers, data=data)
            
            if r.status_code==200:
                return r.content 
            
            self.logError(r)
                
        except requests.exceptions.RequestException:
            pass
        
        return None
    
    def getAvailablePlugins(self):
        uri = Application.remoteServer + "/api/v1/plugins"
        
        data = self.getStandardDictionary(uri)
        content, signature, headers = self.createJsonSignatureHeaders(data)
        
        try:
            r = requests.get(uri, headers=headers)
            
            if r.status_code==200:
                return json.loads(r.content.decode('utf8'))
                
            self.logError(r)
            
        except requests.exceptions.RequestException:
            pass
        
        return None
    
    def getPlugins(self, uuids):
        uri = Application.remoteServer + "/api/v1/plugins"
        
        data = self.getStandardDictionary(uri)
        data["uuids"] = uuids
        content, signature, headers = self.createJsonSignatureHeaders(data)
        
        try:
            r = requests.post(uri, headers=headers, data=content)
            
            if r.status_code==200:
                return json.loads(r.content.decode('utf8'))
                
            self.logError(r)
            
        except requests.exceptions.RequestException:
            pass
        
        return None
    
    def reportException(self):
        import traceback, os
        from lib.stringutil import StringUtil
        from lib.services.service import StorageService
        
        if not StringUtil.isTrue(StorageService.sfind(StorageService.SOFTWARE_REPORT_ERRORS, True)):
            return
                    
        details = traceback.format_exc()
        
        uri = Application.remoteServer + "/api/v1/report"
        
        data =  { }
        data["Stacktrace"] = details
        data["Version"] = StorageService.sfind(StorageService.SOFTWARE_VERSION, "Unknown")
        data["OS"] = os.name
        data["AccessKey"] = Application.user.accessKey
        
        content = json.dumps(data, sort_keys=True)
        
        try:
            r = requests.post(uri, headers={"X-Client": "RT"}, data=content)
        except requests.exceptions.RequestException:
            pass

    def syncTerms(self, terms, lastSync, codes, acceptable):
        uri = Application.remoteServer + "/api/v1/syncterms"
        
        data = self.getStandardDictionary(uri)
        data["Terms"] = terms
        data["LastSync"] = lastSync
        data["Codes"] = codes
        data["Acceptable"] = acceptable
        
        content, signature, headers = self.createJsonSignatureHeaders(data, headers={ "Content-Encoding": "gzip"})
        data = gzip.compress(content.encode())
    
        logging.debug("Content size={0}; Compressed={1}".format(len(content), len(data)))
    
        try:
            r = requests.post(uri, headers=headers, data=data)
            
            if r.status_code==200:
                return json.loads(r.content.decode('utf8'))
                
            self.logError(r)
            
        except requests.exceptions.RequestException:
            pass
        
        return None
    
    #===========================================================================
    # def sync(self, userId):
    #     from lib.models.model import Language, Term, Item
    #     
    #     self.db = Db(Application.connectionString)
    #     uri = Application.remoteServer + "/api/v1/sync-server-changes-1"
    #     
    #     data = self.getStandardDictionary(uri)
    #     data["Language"] = self.db.scalar("SELECT ifnull(sync, 0) ts FROM language ORDER BY ts DESC LIMIT 1")
    #     data["Terms"] = 0 #self.db.scalar("SELECT ifnull(sync, 0) ts FROM term ORDER BY ts DESC LIMIT 1")
    #     data["Items"] = 0 #self.db.scalar("SELECT ifnull(sync, 0) ts FROM item ORDER BY ts DESC LIMIT 1")
    #     
    #     content, signature, headers = self.createJsonSignatureHeaders(data)
    #     r = requests.post(uri, headers=headers, data=content)
    #     
    #     if r.status_code!=200:
    #         self.logError(r)
    #         return None;
    #         
    #     serverData = json.loads(r.content.decode('utf8'))
    #     self.syncLanguage(userId, serverData["Language"])
    #     
    # def syncLanguage(self, userId, data):
    #     from lib.models.model import Language
    #     
    #     timestamp = data["Timestamp"]
    #     print(timestamp)
    #     
    #     for l in data["Languages"]:
    #         pass
    #     
    #     languages = self.db.many(Language, "SELECT * FROM language WHERE isDeleted=0 AND userId=:userId AND modified>:ts", userId=userId, ts=timestamp)
    #     languageReplace = []
    #     
    #     for l in languages:
    #         languageReplace.append(json.dumps(l.toDict()))
    #         
    #     languages = self.db.many(Language, "SELECT * FROM language WHERE isDeleted=1 AND userId=:userId", userId=userId)
    #     languageDelete = []
    #     
    #     for l in languages:
    #         languageDelete.append(json.dumps(l.toDict()))
    #         
    #     uri = Application.remoteServer + "/api/v1/sync-server-changes-languages"
    #     
    #     sendData = self.getStandardDictionary(uri)
    #     sendData["LanguagesReplace"] = languageReplace
    #     sendData["LanguagesDelete"] = languageDelete
    #     
    #     print(languageReplace)
    #     print(languageDelete)
    #     
    #     content, signature, headers = self.createJsonSignatureHeaders(sendData)
    #     r = requests.post(uri, headers=headers, data=content)
    #     
    #     if r.status_code!=200:
    #         self.logError(r)
    #         
    #     response = json.loads(r.content.decode('utf8'))
    #     
    #     syncTime = response["Timestamp"]
    #     self.db.execute("UPDATE language SET sync=:sync WHERE userId=:userId and modified>:ts", sync=syncTime, userId=userId, ts=timestamp)
    #     self.db.execute("DELETE FROM language WHERE isDeleted=1 AND userId=:userId", userId=userId)
    #===========================================================================