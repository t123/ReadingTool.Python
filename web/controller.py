import cherrypy
import routes
from web.internal import InternalController
from web.apiv1 import ApiV1Controller

class Controller():
    def start(self):
        ic = InternalController()

        d = cherrypy.dispatch.RoutesDispatcher()
        d.mapper.minimization = True 
        d.mapper.explicit = False
         
        d.connect(name=None, route='/internal/v1/term/:termId', controller=ic, action="getTermById", conditions=dict(method=["GET"]))
        d.connect(name=None, route='/internal/v1/term/:phrase/:languageId', controller=ic, action="getTermByPhraseAndLanguage", conditions=dict(method=["GET"]))
        d.connect(name=None, route='/internal/v1/encode/:phrase', controller=ic, action="encodePhrase", conditions=dict(method=["GET"]))
        d.connect(name=None, route='/internal/v1/term', controller=ic, action="deleteTerm", conditions=dict(method=["DELETE"]))
        d.connect(name=None, route='/internal/v1/term', controller=ic, action="saveTerm", conditions=dict(method=["POST"]))
            
        print(d.mapper)
        conf = {'/': {'request.dispatch': d}}
        
        #cherrypy.config.update({'environment': 'embedded'})
        cherrypy.tree.mount(root=None, config=conf)
         
        cherrypy.engine.start()
        cherrypy.engine.block()
        
    def stop(self):
        cherrypy.engine.exit()
