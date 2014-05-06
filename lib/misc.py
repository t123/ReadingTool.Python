import os
from datetime import datetime
from lib.models.model import User

class Application:
    user = User()
    
    path = os.path.abspath(
                           os.path.join(
                                        os.path.dirname(os.path.realpath(__file__)),
                                        "..",
                                        "data"
                                        )
                           )
    
    pathParsing = os.path.join(path, "parsing")
    pathOutput = os.path.join(path, "output")
    pathDatabase = os.path.join(path, "database")

    connectionString = os.path.join(pathDatabase, "rtwin.sqlite")
    
    apiServer = "http://localhost:8080"
        
class Time:
    @staticmethod
    def toLocal(ts, fmt="%Y-%m-%d %H:%M:%S"):
        return datetime.fromtimestamp(ts).strftime(fmt)
