import cherrypy, json, urllib
from lib.models.model import TermState, Term
from lib.services.service import TermService

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
            cherrypy.response.status = 404
            cherrypy.response.headers["Content-Type"] = "text/plain"
            return
        
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "text/plain"
        return "TODO" + id
        
    def getMedia(self, id):
        if not self.__isValidId(id):
            cherrypy.response.status = 404
            cherrypy.response.headers["Content-Type"] = "text/plain"
            return
        
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "text/plain"
        return "TODO" + id
        
    def getItem(self, id):
        if not self.__isValidId(id):
            cherrypy.response.status = 404
            cherrypy.response.headers["Content-Type"] = "text/plain"
            return
        
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "text/plain"
        return "TODO" + id
        
    def getLocalResource(self, name):
        cherrypy.response.status = 200
        cherrypy.response.headers["Content-Type"] = "text/plain"
        return "TODO" + name
