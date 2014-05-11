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
        
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps(term.toDict()).encode()
     
    def getTermByPhraseAndLanguage(self, phrase, languageId):
        if not phrase or not self.isValidId(languageId):
            raise cherrypy.HTTPError(404)
        
        termService = TermService()
        term = termService.fineOneByPhraseAndLanguage(phrase, languageId)
         
        if term is None:
            raise cherrypy.HTTPError(404)
         
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps(term.toDict()).encode()
     
    def deleteTerm(self, phrase=None, languageId=None):
        if cherrypy.request.method=="OPTIONS":
            cherrypy.response.status = 200
            return
                    
        if not phrase or not self.isValidId(languageId):
            raise cherrypy.HTTPError(404)
          
        termService = TermService()
        term = termService.fineOneByPhraseAndLanguage(phrase, languageId)
          
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "application/json"
                
        if term is None:
            return json.dumps({}).encode() 
          
        termService.delete(term.termId)
        return json.dumps(term.toDict()).encode()

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
        
        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps(term.toDict()).encode()
            
    def markAllAsKnown(self):
        if cherrypy.request.method=="OPTIONS":
            cherrypy.response.status = 200
            return
        
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
    
    def getLanguages(self):
        languageService = LanguageService()
        languages = languageService.findAll()
        
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "application/json"
        
        l = []
        
        for language in languages:
            l.append(language.toDict())
            
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
        
        return json.dumps(language.toDict()).encode()
    
    def getItems(self):
        itemService = ItemService()
        items = itemService.findAll()
        
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "application/json"
        
        i = []
        
        for item in items:
            i.append(item.toDict())
            
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
        
        return json.dumps(item.toDict()).encode()
        
    def getTerms(self):
        termService = TermService()
        terms = termService.findAll()
        
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "application/json"
        
        t = []
        
        for term in terms:
            t.append(term.toDict())
            
        return json.dumps(t).encode()
    
    def getTerm(self, id):
        if not self.isValidId(id):
            raise cherrypy.HTTPError(404)
        
        termService = TermService()
        term = termService.findOne(id)
        
        if term is None:
            raise cherrypy.HTTPError(404)
        
        t = term.toDict()
        history = termService.findHistory(id)
        if history is not None:
            l = []
            
            for h in history:
                l.append(h.toDict())
                
            t["history"] = l
        
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "application/json"
        
        return json.dumps(t).encode()