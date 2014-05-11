import cherrypy, json, urllib, os, time
from lib.models.model import TermState, Term, Item, TermType
from lib.services.service import TermService, ItemService, PluginService, LanguageService
from lib.misc import Application, Time
from lib.stringutil import StringUtil

class InternalController(object):
    def isValidId(self, id):
        if not id:
            return False
        
        if not id.isdigit():
            return False
        
        if int(id)<=0:
            return False
        
        return True
    
    def index(self):
        return "OK"
    
    def getTermById(self, termId):
        termService = TermService()
        term = termService.findOne(termId)
        
        if term is None:
            raise cherrypy.HTTPError(404)
        
        data = {
            'id': term.termId,
            'phrase': term.phrase,
            'basePhrase': term.basePhrase,
            'definition': term.definition,
            'state': TermState.ToString(term.state).lower(),
            'sentence': term.sentence
        }
     
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps(data).encode()
     
    def getTermByPhraseAndLanguage(self, phrase, languageId):
        if not phrase or not self.isValidId(languageId):
            raise cherrypy.HTTPError(404)
        
        termService = TermService()
        term = termService.fineOneByPhraseAndLanguage(phrase, languageId)
         
        if term is None:
            raise cherrypy.HTTPError(404)
         
        data = {
            'id': term.termId,
            'phrase': term.phrase,
            'basePhrase': term.basePhrase,
            'definition': term.definition,
            'state': TermState.ToString(term.state).lower(),
            'sentence': term.sentence
        }
      
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps(data).encode()
     
    def deleteTerm(self, phrase, languageId):
        if not phrase or not self.isValidId(languageId):
            raise cherrypy.HTTPError(404)
         
        termService = TermService()
        term = termService.fineOneByPhraseAndLanguage(phrase, languageId)
         
        if term is None:
            raise cherrypy.HTTPError(404)
         
        termService.delete(term.termId)
         
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "text/plain"
        return ""

    def saveTerm(self, phrase, basePhrase, sentence, definition, languageId, itemId, state):
        if not self.isValidId(languageId) or not self.isValidId(itemId):
            pass

        termService = TermService()
        term = termService.fineOneByPhraseAndLanguage(phrase, languageId)
    
        basePhrase = (basePhrase or "").strip()
        phrase = (phrase or "").strip()
        sentence = (sentence or "").strip()
        definition = (definition or "").strip()
        
        if term is None:
            term = Term()
            term.basePhrase = basePhrase
            term.phrase = phrase
            term.sentence = sentence
            term.definition = definition
            term.languageId = languageId
            term.itemSourceId = itemId
            term.state = TermState.ToEnum(state)
            
            termService.save(term)
            cherrypy.response.status = 201
        else:
            term.basePhrase = basePhrase
            term.definition = definition
            term.state = TermState.ToEnum(state)
            
            if term.sentence.isspace():
                term.sentence = sentence
                term.itemSourceId = itemId
            elif term.sentence.lower()!=sentence.lower():
                term.sentence = sentence
                term.itemSourceId = itemId
            
            termService.save(term)
            cherrypy.response.status = 200
        
            
    def markAllAsKnownOptions(self):
        cherrypy.response.status = "200"
    
    def markAllAsKnown(self):
        cherrypy.response.status = "200"
        cherrypy.response.headers["Content-Type"] = "text/plain"
        
        length = cherrypy.request.headers['Content-Length']
        raw = cherrypy.request.body.read(int(length)).decode()
        data = json.loads(raw)
        termService = TermService()
        counter = 0
        
        languageId = data["languageId"]
        itemSourceId = data["itemId"]
        
        for item in data["phrases"]:
            try:
                term = Term()
                term.state = TermState.Known
                term.phrase = item
                term.languageId = languageId
                term.itemSourceId = itemSourceId
                
                termService.save(term)
                
                counter += 1
                
            except:
                continue
        
        return str(counter)
        
class ResourceController(object):
    def isValidId(self, id):
        if not id:
            return False
        
        if not id.isdigit():
            return False
        
        if int(id)<=0:
            return False
        
        return True
    
    def index(self):
        return "OK"
    
    def getPlugins(self, id):
        if not self.isValidId(id):
            raise cherrypy.HTTPError(404)
        
        languageService = LanguageService()
        plugins = languageService.findAllPlugins(id, True)
        output = "//Generated at " + Time.toLocal(time.time()) + "\n"
        
        if len(plugins)>0:
            output += "$(document).on('pluginReady', function() {\n"
            
            for plugin in plugins:
                output += "\n"
                output += "/*\n"
                output += "* " + plugin.name + "\n"
                output += "* " + plugin.uuid + "\n"
                output += "* " + plugin.description + "\n"
                output += "*/"
                output += plugin.content
                output += "\n"
                
            output += "$(document).trigger('pluginInit');\n"
            output += "});"
            
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "application/javascript"
        return output.encode()
        
    def getMedia(self, id):
        if not self.isValidId(id):
            raise cherrypy.HTTPError(404)
        
        itemService = ItemService()
        item = itemService.findOne(id)
        
        if item is None:
            raise cherrypy.HTTPError(404)
        
        if not os.path.isfile(item.mediaUri):
            raise cherrypy.HTTPError(404)
        
        fileName, fileExtension = os.path.splitext(item.mediaUri)
        content = ""
        size = os.path.getsize(item.mediaUri)
        
        file = open (item.mediaUri, "rb")
                
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Length"] = size
             
        if fileExtension.lower()==".mp3":
            cherrypy.response.headers["Content-Type"] = "audio/mpeg3"
        elif fileExtension.lower()==".mp4":
            cherrypy.response.headers["Content-Type"] = "video/mp4"
        else:
            raise cherrypy.HTTPError(404)
        
        def stream():
            data = file.read(65000)
            
            while len(data)>0:
                yield data
                data = file.read(65000)
                
        return stream()
        
    def getItem(self, id):
        if not self.isValidId(id):
            raise cherrypy.HTTPError(404)
        
        itemService = ItemService()
        item = itemService.findOne(id)
        
        if item is None:
            raise cherrypy.HTTPError(404)
        
        htmlContent = ""
        with open (os.path.join(Application.pathOutput, str(item.itemId) + ".html"), "r", encoding="utf8") as htmlFile:
            htmlContent = htmlFile.read()
        
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "text/html"
        
        return htmlContent.encode()
        
    def getLocalResource(self, name):
        file = os.path.join(Application.pathOutput, "resources", name)
        
        if not os.path.isfile(file):
            raise cherrypy.HTTPError(404)
        
        fileName, fileExtension = os.path.splitext(file)
        content = None
        
        with open (file, "rb") as file:
            content = file.read()
            
        if fileExtension.lower()==".js":
            cherrypy.response.headers["Content-Type"] = "application/javascript"
        elif fileExtension.lower()==".css":
            cherrypy.response.headers["Content-Type"] = "text/css"
        elif fileExtension.lower()==".swf":
            cherrypy.response.headers["Content-Type"] = "application/x-shockwave-flash"
        elif fileExtension.lower()==".jpg":
            cherrypy.response.headers["Content-Type"] = "image/jpeg"
        elif fileExtension.lower()==".png":
            cherrypy.response.headers["Content-Type"] = "image/png"
        else:        
            cherrypy.response.headers["Content-Type"] = "text/html"
        
        cherrypy.response.status = 200
        
        return content
   
class ApiV1Controller(object):
    def isValidId(self, id):
        if not id:
            return False
        
        if not id.isdigit():
            return False
        
        if int(id)<=0:
            return False
        
        return True
    
    def encodePhrase(self, phrase, encoding="utf-8"):
        encoded = urllib.parse.quote(phrase.encode(encoding))
         
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "text/plain"
        return encoded
    
    def _languageToDict(self, language):
        if language is None:
            return None
        
        d = {}
        d["languageId"] = language.languageId
        d["name"] = language.name
        d["created"] = language.created
        d["modified"] = language.modified
        d["isArchived"] = language.isArchived
        d["languageCode"] = language.languageCode
        d["userId"] = language.userId
        d["sentenceRegex"] = language.sentenceRegex
        d["termRegex"] = language.termRegex
        d["direction"] = language.direction
        
        return d
        
    def getLanguages(self):
        languageService = LanguageService()
        languages = languageService.findAll()
        
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "application/json"
        
        l = []
        
        for language in languages:
            l.append(self._languageToDict(language))
            
        return json.dumps(l).encode()
    
    def getLanguage(self, id):
        if not self.isValidId(id):
            raise cherrypy.HTTPError(404)
        
        languageService = LanguageService()
        language = languageService.findOne(id)
        
        if language is None:
            raise cherrypy.HTTPError(404)
        
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "application/json"
        
        return json.dumps(self._languageToDict(language)).encode()
    
    def _itemToDict(self, item, individual=False):
        if item is None:
            return None
        
        d = {}
        d["itemId"] = item.itemId
        d["created"] = item.created
        d["modified"] = item.modified
        d["itemType"] = item.itemType
        d["userId"] = item.userId
        d["collectionName"] = item.collectionName
        d["collectionNo"] = item.collectionNo
        d["mediaUri"] = item.mediaUri
        d["lastRead"] = item.lastRead
        d["l1Title"] = item.l1Title
        d["l2Title"] = item.l2Title
        d["l1LanguageId"] = item.l1LanguageId
        d["l2LanguageId"] = item.l2LanguageId
        d["readTimes"] = item.readTimes
        d["listenedTimes"] = item.listenedTimes
        d["l1Language"] = item.l1Language
        d["l2Language"] = item.l2Language
        d["isParallel"] = item.isParallel()
        d["hasMedia"] = item.hasMedia()
        
        if individual:
            d["l1Content"] = item.getL1Content()
            d["l2Content"] = item.getL2Content()
        else:
            d["l1Content"] = ""
            d["l2Content"] = ""
            
        return d
        
    def getItems(self):
        itemService = ItemService()
        items = itemService.findAll()
        
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "application/json"
        
        i = []
        
        for item in items:
            i.append(self._itemToDict(item))
            
        return json.dumps(i).encode()
    
    def getItem(self, id):
        if not self.isValidId(id):
            raise cherrypy.HTTPError(404)
        
        itemService = ItemService()
        item = itemService.findOne(id)
        
        if item is None:
            raise cherrypy.HTTPError(404)
        
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "application/json"
        
        return json.dumps(self._itemToDict(item, True)).encode()
    
    def _termToDict(self, term, history=None):
        if term is None:
            return None
        
        d = {}
        d["termId"] = term.termId
        d["created"] = term.created
        d["modified"] = term.modified
        d["phrase"] = term.phrase
        d["lowerPhrase"] = term.lowerPhrase
        d["basePhrase"] = term.basePhrase
        d["definition"] = term.definition
        d["sentence"] = term.sentence
        d["languageId"] = term.languageId
        d["state"] = TermState.ToString(term.state)
        d["userId"] = term.userId
        d["itemSourceId"] = term.itemSourceId
        d["language"] = term.language
        d["itemSource"] = term.itemSource

        if history is not None:
            l = []
            
            for h in history:
                hd = {}
                hd["entryDate"] = h.entryDate
                hd["termId"] = h.termId
                hd["state"] = TermState.ToString(h.state)
                hd["type"] = TermType.ToString(h.type)
                hd["languageId"] = h.languageId
                hd["userId"] = h.userId
                
                l.append(hd)
                
            d["history"] = l
            
        return d
        
    def getTerms(self):
        termService = TermService()
        terms = termService.findAll()
        
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "application/json"
        
        t = []
        
        for term in terms:
            t.append(self._termToDict(term))
            
        return json.dumps(t).encode()
    
    def getTerm(self, id):
        if not self.isValidId(id):
            raise cherrypy.HTTPError(404)
        
        termService = TermService()
        term = termService.findOne(id)
        
        if term is None:
            raise cherrypy.HTTPError(404)
        
        history = termService.findHistory(id)
        
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "application/json"
        
        return json.dumps(self._termToDict(term, history)).encode()