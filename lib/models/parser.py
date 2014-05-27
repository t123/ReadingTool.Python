import os, uuid
from lib.misc import Application

class ParserInput:
    def __init__(self):
        self._terms = None
        self._multiTerms = None
        #self.html = ""
        self.item = None
        self.language1 = None
        self.language2 = None
        self.asParallel = False
        self.lookup = {}
        self.fragments = {}
        
    @property
    def terms(self):
        return self._terms
    
    @terms.setter
    def terms(self, value):
        self._terms = value
        self.lookup = dict((el.lowerPhrase, el) for el in value)
        
    @property
    def multiTerms(self):
        return self._multiTerms
    
    @multiTerms.setter
    def multiTerms(self, value):
        self._multiTerms = value
        self.fragments = dict((el.lowerPhrase, el) for el in value)
        
class ParserOutput:
    def __init__(self):
        self.item = None
        self.xml = ""
        self.html = ""
        self.stats = ParseStats()
        self.l1Srt = None
        self.l2Srt = None
        
    def save(self):
        if self.item is None:
            return
        
        itemId = str(self.item.itemId)
        xmlPath = os.path.join(Application.pathOutput, itemId + ".xml")
        htmlPath = os.path.join(Application.pathOutput, itemId + ".html")
        
        with open(xmlPath, 'wb') as f:
            f.write(self.xml)

        with open(htmlPath, 'wt', encoding="utf8") as f:
            f.write(self.html)        
        
class ParseStats:
    def __init__(self):
        self.known = 0
        self.unknown = 0
        self.ignored = 0
        self.notseen = 0
        self.totalTerms = 0
        self.uniqueTerms = 0
        self.uniqueKnown = 0
        self.uniqueUnknown = 0
        self.uniqueIgnored = 0
        self.uniqueNotSeen = 0
        
class SRT:
    def __init__(self):
        self.lineNo = None
        self.content = ""
        self.start = 0.0
        self.end = 0.0