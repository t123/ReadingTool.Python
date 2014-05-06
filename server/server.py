import cherrypy, routes
from server.controllers import InternalController, ResourceController, ApiV1Controller 

def CORS():
        if "Origin" in cherrypy.request.headers:
            origin = cherrypy.request.headers["Origin"].lower()
            
            # TODO -> replace localhost
            if  origin=="null" or origin.startswith("http://localhost"):
                cherrypy.response.headers["Access-Control-Allow-Origin"] = cherrypy.request.headers["Origin"]
                
            #===================================================================
            # if "Access-Control-Request-Method" in cherrypy.request.headers:
            #     cherrypy.response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,HEAD,OPTIONS"
            #     
            # if "Access-Control-Request-Headers" in cherrypy.request.headers:
            #     cherrypy.response.headers["Access-Control-Allow-Headers"] = cherrypy.request.headers["Access-Control-Request-Headers"]
            #===================================================================
        
class Server():
    def __init__(self, embed=True):
        cherrypy.tools.CORS = cherrypy.Tool('before_handler', CORS) 
        
        ic = InternalController()
        rc = ResourceController()
        ac = ApiV1Controller()

        d = cherrypy.dispatch.RoutesDispatcher()
        #d.mapper.minimization = True 
        #d.mapper.explicit = False
        
        #d.connect(name="i1", route='/internal/v1/term/', controller=ic, action="index", conditions=dict(method=["GET"]))
        d.connect(name="i2", route='/internal/v1/term/:termId', controller=ic, action="getTermById", conditions=dict(method=["GET"]))
        d.connect(name="i3", route='/internal/v1/term', controller=ic, action="getTermByPhraseAndLanguage", conditions=dict(method=["GET"]))
        
        #some CORS weirdness with DELETE
        d.connect(name="i5", route='/internal/v1/deleteterm', controller=ic, action="deleteTerm", conditions=dict(method=["POST"]))
        d.connect(name="i6", route='/internal/v1/term', controller=ic, action="saveTerm", conditions=dict(method=["POST"]))
        d.connect(name="i7", route='/internal/v1/markallknown', controller=ic, action="markAllAsKnown", conditions=dict(method=["POST"]))
         
        d.connect(name="r1", route='/resource/v1/', controller=rc, action="index", conditions=dict(method=["GET"]))
        d.connect(name="r2", route='/resource/v1/plugins/:id', controller=rc, action="getPlugins", conditions=dict(method=["GET"]))
        d.connect(name="r3", route='/resource/v1/media/:id', controller=rc, action="getMedia", conditions=dict(method=["GET"]))
        d.connect(name="r4", route='/resource/v1/item/:id', controller=rc, action="getItem", conditions=dict(method=["GET"]))
        d.connect(name="r5", route='/resource/v1/local/:name', controller=rc, action="getLocalResource", conditions=dict(method=["GET"]))
        
        d.connect(name="a1", route='/api/v1/encode/:phrase', controller=ac, action="encodePhrase", conditions=dict(method=["GET"]))
            
        conf = {'/': {
                      'request.dispatch': d, 
                      'tools.CORS.on': True
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