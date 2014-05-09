import bz2
from lib.stringutil import StringUtil

class TermState:
    Invalid, Known, Unknown, Ignored, NotSeen = range(5)
    
    @staticmethod
    def ToString(state):
        if state==0:
            return "Invalid"
        elif state==1:
            return "Known"
        elif state==2:
            return "Unknown"
        elif state==3:
            return "Ignored"
        elif state==4:
            return "NotSeen"
        
        raise Exception("Unknown int state")
    
    @staticmethod
    def ToEnum(state):
        state = state.lower()
        
        if state=="invalid":
            return 0
        elif state=="known":
            return 1
        elif state=="unknown":
            return 2
        elif state=="ignored":
            return 3
        elif state=="notseen":
            return 4
        
        raise Exception("Unknown string state")
    
class ItemType:
    Unknown, Text, Video = range(3)
    
    @staticmethod
    def ToString(itemType):
        if itemType==0:
            return "Invalid"
        elif itemType==1:
            return "Text"
        elif itemType==2:
            return "Video"
        
        raise Exception("Unknown int itemType")
    
class TermType:
    Unknown, Create, Modify, Delete = range(4)
    
class LanguageDirection:
    Unknown, LeftToRight, RightToLeft = range(3)
    
class User():
    def __init__(self):
        self.userId = 0
        self.username = ""
        self.lastLogin = None
        self.accessKey = ""
        self.accessSecret = ""
        self.syncData = False
        
class Language():
    TERM_REGEX = "([a-zA-ZÀ-ÖØ-öø-ÿĀ-ſƀ-ɏ\\'-]+)"
    SENTENCE_REGEX = "[^\\.!\\?]+[\\.!\\?\\n]+"
    
    def __init__(self):
        self.languageId = 0
        self.name = ""
        self.created = None
        self.modified = None
        self.isArchived = False
        self.languageCode = "--"
        self.userId = None
        self.sentenceRegex = Language.SENTENCE_REGEX
        self.termRegex = Language.TERM_REGEX
        self.direction = LanguageDirection.LeftToRight
    
class LanguageCode():
    def __init__(self):
        self.code = ""
        self.name = ""

class LanguagePlugin():
    def __init__(self):
        self.pluginId = 0
        self.name = ""
        self.description = ""
        self.enabled = False
        self.content = ""
        self.uuid = None
            
class Term():
    def __init__(self):
        self.termId = 0
        self.created = None
        self.modified = None
        
        self._phrase = ""
        self.lowerPhrase = ""
        self.basePhrase = ""
        self.definition = ""
        self.sentence = ""
        self.languageId = None
        self.state = TermState.Unknown
        self.userId = None
        self.itemSourceId = None
        self.language = ""
        self.itemSource = ""
        
    def fullDefinition(self):
        fullDef = ""
        
        if not StringUtil.isEmpty(self.basePhrase):
            fullDef += self.basePhrase + "<br/>" 
            
        if not StringUtil.isEmpty(self.definition):
            fullDef += self.definition
         
        return fullDef
        
    @property
    def phrase(self):
        return self._phrase;
    
    @phrase.setter
    def phrase(self, value):
        self._phrase = value;
        self.lowerPhrase = (value or "").lower()
        
class TermLog():
    def __init__(self):
        self.entryDate = None
        self.termId = None
        self.state = None
        self.type = TermType.Unknown
        self.languageId = None
        self.userId = None
        
class Item():
    def __init__(self):
        self.itemId = 0
        self.created = None
        self.modified = None
        self.itemType = ItemType.Text
        self.userId = None
        self.collectionName = ""
        self.collectionNo = None
        self.mediaUri = ""
        self.lastRead = None
        self.l1Title = ""
        self.l2Title = ""
        self.l1LanguageId = None
        self.l2LanguageId = None
        self.readTimes = 0
        self.listenedTimes = 0
        self.l1Language = None
        self.l2Language = None
        self.l1Content = None
        self.l2Content = None
        
    def getL1Content(self):
        if self.l1Content is None or StringUtil.isEmpty(self.l1Content):
            return ""
        
        return bz2.decompress(self.l1Content).decode()
    
    def setL1Content(self, value):
        if value is None or StringUtil.isEmpty(value):
            self.l1Content = None
            return
            
        self.l1Content = bz2.compress(value.encode())
        
    def getL2Content(self):
        if self.l2Content is None or StringUtil.isEmpty(self.l2Content):
            return ""
        
        return bz2.decompress(self.l2Content).decode()
    
    def setL2Content(self, value):
        if value is None or StringUtil.isEmpty(value):
            self.l2Content = None
            return
            
        self.l2Content = bz2.compress(value.encode())
        
    def hasMedia(self):
        return not StringUtil.isEmpty(self.mediaUri)
    
    def isParallel(self):
        return not StringUtil.isEmpty(self.l2Content)
    
    def name(self):
        name = ""
        if self.collectionNo:
            name += str(self.collectionNo) + ". "
            
        if not StringUtil.isEmpty(self.collectionName):
            name += self.collectionName + "  - "
            
        name += self.l1Title
        
        return name
    
class Plugin():
    def __init__(self):
        self.pluginId = 0
        self.description = ""
        self.name = ""
        self.content = ""
        self.uuid = ""
    