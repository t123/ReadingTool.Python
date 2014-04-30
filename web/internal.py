import cherrypy, json, urllib
from lib.models.model import TermState, Term
from lib.services.service import TermService

class InternalController(object):
    def __isValidId(self, id):
        if not id:
            return False
        
        if not id.isdigit():
            return False
        
        if int(id)<=0:
            return False
        
        return True
    
    def getTermById(self, termId):
        termService = TermService()
        term = termService.findOne(termId)
        
        if term is None:
            return self.__notFound()
        
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
            return self.__notFound()
         
        termService = TermService()
        term = termService.fineOneByPhraseAndLanguage(phrase, languageId)
         
        if term is None:
            return self.__notFound()
         
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
     
    def encodePhrase(self, phrase, encoding="utf-8"):
        encoded = urllib.parse.quote(phrase.encode(encoding))
         
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "text/plain"
        return encoded
     
    def deleteTerm(self, phrase, languageId):
        if not phrase or not self.__isValidId(languageId):
            return self.__notFound()
         
        termService = TermService()
        term = termService.fineOneByPhraseAndLanguage(phrase, languageId)
         
        if term is None:
            return self.__notFound()
         
        termService.deleteOne(term.termId)
         
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
            cherrypy.response.headers["Content-Type"] = "text/plain"
            return ""
        else:
            term.basePhrase = (basePhrase or "").strip()
            term.definition = (definition or "").strip()
            term.state = TermState.ToEnum(state)
            
            if term.sentence.isspace():
                term.sentence = sentence
                term.itemSourceId = itemId
            elif term.sentence.lower()!=sentence.lower():
                term.sentence = sentence
                term.itemSourceId = itemId
            
            termService.save(term)
            
            cherrypy.response.status = 200
            cherrypy.response.headers["Content-Type"] = "text/plain"
            
    def __notFound(self):
        cherrypy.response.status = 404
        cherrypy.response.headers["Content-Type"] = "text/plain"
        return