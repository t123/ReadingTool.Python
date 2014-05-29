import os, math
from datetime import datetime
from lib.models.model import User

class Application:
    debug = False
    version = 1
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

    connectionString = os.path.join(pathDatabase, "rt.sqlite")
    
    apiServer = None
    remoteServer = None
    
    myApp = None
        
class Time:
    @staticmethod
    def toLocal(ts, fmt="%Y-%m-%d %H:%M:%S"):
        if ts is None:
            return "NA"
        
        return datetime.fromtimestamp(ts).strftime(fmt)
    
    @staticmethod
    def toHuman(ts, nullValue="NA", append=" ago"):
        if ts is None or ts<0:
            return nullValue
        
        diff = datetime.now()-datetime.fromtimestamp(ts)
        
        if diff.days>365:
            years = math.floor(diff.days/365)
            return "1 year" + append if years==1 else str(years) + " years" + append

        if diff.days>30:
            months = math.floor(diff.days/30)
            return "1 month" + append if months==1 else str(months) + " months" + append
        
        if diff.days==1:
            return "1 day" + append
        
        if diff.days>1:
            return str(math.floor(diff.days)) + " days" + append
        
        if diff.seconds==60*60:
            return "1 hour"
        
        if diff.seconds>60*60:
            return str(math.floor(diff.seconds/60/60)) + " hours" + append
        
        if diff.seconds>60*5:
            return str(math.floor(diff.seconds/60)) + " minutes" + append
        
        if diff.seconds>60:
            return "minutes" + append
        
        return "seconds" + append
    
class Validations:
    Ok = "#96D899"
    Failed = "#FBE3E4"
    
    Empty = r"^$|\s+"
    NotEmpty = r"^[^$|\s]+"
