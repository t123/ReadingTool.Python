import cherrypy

class ApiV1Controller(object):
    @cherrypy.expose
    def index(self):
        return "apiv1"