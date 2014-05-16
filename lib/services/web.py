import requests, uuid, base64, json, hashlib, hmac, time
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
        
    def createJsonSignatureHeaders(self, dictionary, contentType="application/json"):
        data = json.dumps(dictionary, sort_keys=True)
        message = data.encode('utf-8')
        secret = Application.user.accessSecret.encode('utf-8')
        signature = base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest())
        
        return (data, signature, {
                   "Content-Type": contentType,
                   "X-Signature": signature,
                   "X-AccessKey": Application.user.accessKey
                   })
        
    def checkForNewVersion(self):
        uri = Application.remoteServer + "/api/v1/latestversion"
        r = requests.get(uri)
        
        if r.status_code!=200:
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
                
        except requests.exceptions.RequestException:
            pass
        
        return None