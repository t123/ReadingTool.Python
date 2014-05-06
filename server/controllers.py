import cherrypy, json, urllib, os
from lib.models.model import TermState, Term, Item
from lib.services.service import TermService, ItemService
from lib.misc import Application

class InternalController(object):
    def __isValidId(self, id):
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
        if not phrase or not self.__isValidId(languageId):
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
        if not phrase or not self.__isValidId(languageId):
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
        if not self.__isValidId(languageId) or not self.__isValidId(itemId):
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
        
            
    def markAllAsKnown(self):
        cherrypy.response.status = "501 - not implemented"
        cherrypy.response.headers["Content-Type"] = "text/plain"
        
class ResourceController(object):
    def __isValidId(self, id):
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
        if not self.__isValidId(id):
            raise cherrypy.HTTPError(404)
        
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "text/plain"
        return "TODO" + id
        
    def getMedia(self, id):
        if not self.__isValidId(id):
            raise cherrypy.HTTPError(404)
        
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "text/plain"
        return "TODO" + id
        
    def getItem(self, id):
        if not self.__isValidId(id):
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
    def __init__(self):
        pass
    
    def encodePhrase(self, phrase, encoding="utf-8"):
        encoded = urllib.parse.quote(phrase.encode(encoding))
         
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "text/plain"
        return encoded