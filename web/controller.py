import cherrypy
import routes
from web.internal import InternalController
from web.resources import ResourceController
from web.apiv1 import ApiV1Controller

class Controller():
    def start(self):
        ic = InternalController()
        rc = ResourceController()

        d = cherrypy.dispatch.RoutesDispatcher()
        #d.mapper.minimization = True 
        #d.mapper.explicit = False
        
        d.connect(name="i1", route='/internal/v1/term/', controller=InternalController(), action="index", conditions=dict(method=["GET"]))
        d.connect(name="i2", route='/internal/v1/term/:termId', controller=InternalController(), action="getTermById", conditions=dict(method=["GET"]))
        d.connect(name="i3", route='/internal/v1/term/:phrase/:languageId', controller=InternalController(), action="getTermByPhraseAndLanguage", conditions=dict(method=["GET"]))
        d.connect(name="i4", route='/internal/v1/encode/:phrase', controller=InternalController(), action="encodePhrase", conditions=dict(method=["GET"]))
        d.connect(name="i5", route='/internal/v1/term', controller=InternalController(), action="deleteTerm", conditions=dict(method=["DELETE"]))
        d.connect(name="i6", route='/internal/v1/term', controller=InternalController(), action="saveTerm", conditions=dict(method=["POST"]))
        d.connect(name="i7", route='/internal/v1/markallknown', controller=InternalController(), action="markAllAsKnown", conditions=dict(method=["POST"]))
         
        d.connect(name="r1", route='/resource/v1/', controller=ResourceController(), action="index", conditions=dict(method=["GET"]))
        d.connect(name="r2", route='/resource/v1/plugins/:id', controller=ResourceController(), action="getPlugins", conditions=dict(method=["GET"]))
        d.connect(name="r3", route='/resource/v1/media/:id', controller=ResourceController(), action="getMedia", conditions=dict(method=["GET"]))
        d.connect(name="r4", route='/resource/v1/item/:id', controller=ResourceController(), action="getItem", conditions=dict(method=["GET"]))
        d.connect(name="r5", route='/resource/v1/local/:name', controller=ResourceController(), action="getLocalResource", conditions=dict(method=["GET"]))
            
        conf = {'/': {'request.dispatch': d}}
        #cherrypy.config.update({'environment': 'embedded'})
        cherrypy.tree.mount(root=None, config=conf)
        cherrypy.engine.start()
        cherrypy.engine.block()
        
    def stop(self):
        cherrypy.engine.exit()