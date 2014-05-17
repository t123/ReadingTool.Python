import requests, uuid, base64, json, hashlib, hmac, time, logging
from urllib.parse import urlparse

from lib.misc import Application
from lib.models.model import Item
from lib.models.parser import ParserInput
from lib.services.parser import LatexParser
from lib.services.service import ItemService, LanguageService, TermService

class WebService:
    def getStandardDictionary(self, uri, verb="POST"):
        return {
                    "Uri": uri,
                    "Verb": verb,
                    "Time": time.time(),
                    "Nonce": str(uuid.uuid1()),
                    "AccessKey": Application.user.accessKey
                }
        
    def logError(self, response):
        try:
            data = json.loads(response.content.decode("utf8"))
            logging.debug(data["code"])
            logging.debug(data["message"])
        except Exception as e:
            logging.debug(str(e))
             
    def createJsonSignatureHeaders(self, dictionary, contentType="application/json", secret=None):
        data = json.dumps(dictionary, sort_keys=True)
        message = data.encode('utf-8')
        
        if secret is None:
            secret = Application.user.accessSecret.encode('utf-8')
        else:
            secret = secret.encode('utf-8')
             
        signature = base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest())
        
        return (data, signature, {
                   "Content-Type": contentType,
                   "X-Signature": signature,
                   "X-AccessKey": Application.user.accessKey
                   })
        
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
        data = self.getStandardDictionary(uri)
        data["AccessKey"] = accessKey
        
        content, signature, headers = self.createJsonSignatureHeaders(data, secret=accessSecret)
        
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
        r = requests.get(uri)
        
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
        #self.po.save()
        
        uri = Application.remoteServer + "/api/v1/createpdf"
        
        data = self.getStandardDictionary(uri)
        data["Latex"] = self.po.html
        data["Title"] = item.name()
        content, signature, headers = self.createJsonSignatureHeaders(data)
        
        try:
            r = requests.post(uri, headers=headers, data=content)
            
            if r.status_code==200:
                return r.content 
            
            self.logError(r)
                
        except requests.exceptions.RequestException:
            pass
        
        return None