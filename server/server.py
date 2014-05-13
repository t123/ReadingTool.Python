import cherrypy, routes
from server.controllers import InternalController, ResourceController, ApiV1Controller 

def CORS():
        if "Origin" in cherrypy.request.headers:
            origin = cherrypy.request.headers["Origin"].lower()
            
            #TODO fix localhost
            if  origin=="null" or origin.startswith("http://localhost"):
                cherrypy.response.headers["Access-Control-Allow-Origin"] = cherrypy.request.headers["Origin"]
                
                for header in cherrypy.request.headers.keys():
                    if header.lower()=="access-control-request-headers":
                        cherrypy.response.headers["Access-Control-Allow-Headers"] = cherrypy.request.headers["Access-Control-Request-Headers"]
                    
                    if header.lower()=="access-control-request-method":
                        cherrypy.response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,HEAD,OPTIONS"
                         
class Server():
    def __init__(self, embed=True):
        cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS) 
        
        ic = InternalController()
        rc = ResourceController()
        ac = ApiV1Controller()

        d = cherrypy.dispatch.RoutesDispatcher()
        #d.mapper.minimization = True 
        #d.mapper.explicit = False
        
        d.connect(name="i2", route='/internal/v1/term/:termId', controller=ic, action="getTermById", conditions=dict(method=["GET"]))
        d.connect(name="i3", route='/internal/v1/term', controller=ic, action="getTermByPhraseAndLanguage", conditions=dict(method=["GET"]))
        d.connect(name="i4", route='/internal/v1/term', controller=ic, action="saveTerm", conditions=dict(method=["POST"]))
        d.connect(name="i5", route='/internal/v1/delete', controller=ic, action="deleteTerm", conditions=dict(method=["OPTIONS", "POST"]))
        d.connect(name="i7", route='/internal/v1/markallknown', controller=ic, action="markAllAsKnown", conditions=dict(method=["POST", "OPTIONS"]))
        
        d.connect(name="r2", route='/resource/v1/plugins/:id', controller=rc, action="getPlugins", conditions=dict(method=["GET"]))
        d.connect(name="r3", route='/resource/v1/media/:id', controller=rc, action="getMedia", conditions=dict(method=["GET"]))
        d.connect(name="r4", route='/resource/v1/item/:id', controller=rc, action="getItem", conditions=dict(method=["GET"]))
        d.connect(name="r5", route='/resource/v1/local/:name', controller=rc, action="getLocalResource", conditions=dict(method=["GET"]))
         
        d.connect(name="a1", route='/api/v1/encode', controller=ac, action="encodePhrase", conditions=dict(method=["GET"]))
        d.connect(name="a2", route='/api/v1/languages', controller=ac, action="getLanguages", conditions=dict(method=["GET"]))
        d.connect(name="a2.1", route='/api/v1/languages/:id', controller=ac, action="getLanguage", conditions=dict(method=["GET"]))
        d.connect(name="a3", route='/api/v1/items', controller=ac, action="getItems", conditions=dict(method=["GET"]))
        d.connect(name="a3.1", route='/api/v1/items/:id', controller=ac, action="getItem", conditions=dict(method=["GET"]))
        d.connect(name="a4", route='/api/v1/terms', controller=ac, action="getTerms", conditions=dict(method=["GET"]))
        d.connect(name="a4.1", route='/api/v1/terms/:id', controller=ac, action="getTerm", conditions=dict(method=["GET"]))
        d.connect(name="a5", route='/api/v1/terms/delete/:id', controller=ac, action="deleteTerm", conditions=dict(method=["OPTIONS", "DELETE"]))
        d.connect(name="a6", route='/api/v1/terms/save', controller=ac, action="saveTerms", conditions=dict(method=["OPTIONS", "POST"]))
         
        d.connect(name="s7.1", route='/api/v1/storage/:uuid/:key', controller=ac, action="getStorage", conditions=dict(method=["GET"]))
        d.connect(name="s7.2", route='/api/v1/storage/:uuid/:key', controller=ac, action="saveStorage", conditions=dict(method=["POST"]))
        d.connect(name="s7.3", route='/api/v1/storage/:uuid', controller=ac, action="allStorage", conditions=dict(method=["GET"]))

        conf = {'/': {
                      'request.dispatch': d, 
                      'tools.CORS.on': True,
                      'request.stream': True
                      }
                }
        
        if embed:
            cherrypy.config.update({'environment': 'embedded'})
            
        cherrypy.tree.mount(root=None, config=conf)
        
    def start(self, block=False):
        cherrypy.engine.start()
        
        if block:
            cherrypy.engine.block()
        
    def stop(self):
        cherrypy.engine.exit()