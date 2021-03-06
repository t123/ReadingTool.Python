import bz2, re
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
        state = str(state).lower()
        
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
    
    @staticmethod
    def ToString(termType):
        if termType==0:
            return "Unknown"
        elif termType==1:
            return "Create"
        elif termType==2:
            return "Modify"
        elif termType==3:
            return "Delete"
        
        raise Exception("Unknown int termType")
    
class LanguageDirection:
    Unknown, LeftToRight, RightToLeft = range(3)
    
class User():
    def __init__(self):
        self.userId = None
        self.username = ""
        self.lastLogin = None
        self.accessKey = ""
        self.accessSecret = ""
        self.syncData = False
        
    def hasCredentials(self):
        if not self.accessKey or not self.accessSecret:
            return False
        
        if len(self.accessKey)!=20 or len(self.accessSecret)!=50:
            return False
        
        return True
        
class Language():
    TERM_REGEX = "([a-zA-ZÀ-ÖØ-öø-ÿĀ-ſƀ-ɏ\’\'-]+)|(\s+)|(\d+)|(__\d+__)|(<\/?[a-z][A-Z0-9]*[^>]*>)|(.)"
    
    def __init__(self):
        self.languageId = None
        self.name = ""
        self.created = None
        self.modified = None
        self.isArchived = False
        self.languageCode = "--"
        self.userId = None
        self.termRegex = Language.TERM_REGEX
        self.direction = LanguageDirection.LeftToRight
        self.theme = None
        self.sourceCode = "--"
        
    def toDict(self):
        d = {}
        
        d["languageId"] = str(self.languageId)
        d["name"] = self.name
        d["created"] = self.created
        d["modified"] = self.modified
        d["isArchived"] = self.isArchived
        d["languageCode"] = self.languageCode
        d["userId"] = str(self.userId)
        d["termRegex"] = self.termRegex
        d["direction"] = self.direction
        d["theme"] = self.theme
        d["sourceCode"] = self.sourceCode
        
        return d
    
class LanguageCode():
    def __init__(self):
        self.code = ""
        self.name = ""

class LanguagePlugin():
    def __init__(self):
        self.pluginId = None
        self.name = ""
        self.description = ""
        self.enabled = False
        self.content = ""
        self.uuid = None
            
class SharedTerm():
    def __init__(self):
        self._phrase = ""
        
        self.id = None
        self.code = ""
        self.lowerPhrase = ""
        self.basePhrase = ""
        self.sentence = ""
        self.definition = ""
        self.language = ""
        self.source = ""
        
    @property
    def phrase(self):
        return self._phrase
    
    @phrase.setter
    def phrase(self, value):
        self._phrase = value
        self.lowerPhrase = (value or "").lower()
        
class Term():
    def __init__(self):
        self.termId = None
        self.created = None
        self.modified = None
        
        self._phrase = ""
        self._isFragment = False
        
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
        self.sourceCode = ""

        self.itemSourceCollection = "" #only for search
        self.itemSourceTitle  = "" #only for search
        
    def fullDefinition(self, joinString="<br/>"):
        fullDef = ""
        
        if joinString=="<br/>":
            if not StringUtil.isEmpty(self.basePhrase):
                fullDef += self.basePhrase + joinString 
            
            if not StringUtil.isEmpty(self.definition):
                fullDef += self.definition
                
            return re.sub(r"\n", "<br/>", fullDef)
         
        if joinString=="\n":
            if not StringUtil.isEmpty(self.basePhrase):
                fullDef += self.basePhrase + joinString 
            
            if not StringUtil.isEmpty(self.definition):
                fullDef += self.definition
                
            return fullDef
        
        if joinString==" ; ":
            if not StringUtil.isEmpty(self.basePhrase):
                fullDef += self.basePhrase + joinString 
            
            if not StringUtil.isEmpty(self.definition):
                fullDef += self.definition
                
            return re.sub(r"\n", " ; ", fullDef)
        
    @property
    def phrase(self):
        return self._phrase
    
    @phrase.setter
    def phrase(self, value):
        self._phrase = value
        self.lowerPhrase = (value or "").lower()
        
        if " " in value:
            self._isFragment = True
        
    @property
    def isFragment(self):
        return self._isFragment
    
    @isFragment.setter
    def isFragment(self, value):
        self._isFragment = value;
    
    def toDict(self):
        d = {}
        d["termId"] = str(self.termId)
        d["created"] = self.created
        d["modified"] = self.modified
        d["phrase"] = self.phrase
        d["lowerPhrase"] = self.lowerPhrase
        d["basePhrase"] = self.basePhrase
        d["definition"] = self.definition
        d["sentence"] = self.sentence
        d["languageId"] = str(self.languageId)
        d["state"] = TermState.ToString(self.state).lower() #historical
        d["userId"] = str(self.userId)
        d["itemSourceId"] = str(self.itemSourceId)
        d["language"] = self.language
        d["itemSource"] = self.itemSource
        d["isFragment"] = self.isFragment
        
        return d
        
class TermLog():
    def __init__(self):
        self.entryDate = None
        self.termId = None
        self.state = None
        self.type = TermType.Unknown
        self.languageId = None
        self.userId = None
        
    def toDict(self):
        d = {}
        d["entryDate"] = self.entryDate
        d["termId"] = str(self.termId)
        d["state"] = TermState.ToString(self.state)
        d["type"] = TermType.ToString(self.type)
        d["languageId"] = str(self.languageId)
        d["userId"] = str(self.userId)
        
        return d
    
class Item():
    def __init__(self):
        self.itemId = None
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
    
    def toDict(self):
        d = {}
        d["itemId"] = str(self.itemId)
        d["created"] = self.created
        d["modified"] = self.modified
        d["itemType"] = self.itemType
        d["userId"] = str(self.userId)
        d["collectionName"] = self.collectionName
        d["collectionNo"] = self.collectionNo
        d["mediaUri"] = self.mediaUri
        d["lastRead"] = self.lastRead
        d["l1Title"] = self.l1Title
        d["l2Title"] = self.l2Title
        d["l1LanguageId"] = str(self.l1LanguageId)
        d["l2LanguageId"] = str(self.l2LanguageId)
        d["readTimes"] = self.readTimes
        d["listenedTimes"] = self.listenedTimes
        d["l1Language"] = self.l1Language
        d["l2Language"] = self.l2Language
        d["isParallel"] = self.isParallel()
        d["hasMedia"] = self.hasMedia()
        
        if self.l1Content is not None:
            d["l1Content"] = self.getL1Content()
        else:
            d["l1Content"] = ""
            
        if self.l2Content is not None:
            try:
                d["l2Content"] = self.getL2Content()
            except ValueError: #Find all only returns 1st 20 bytes
                d["l2Content"] = ""
        else:
            d["l2Content"] = ""
            
        return d
    
class Plugin():
    def __init__(self):
        self.pluginId = None
        self.description = ""
        self.name = ""
        self.content = ""
        self.uuid = ""
        self.version = 0
        self.local = False
        
    def toDict(self):
        d = {}
        d["pluginId"] = str(self.pluginId)
        d["description"] = self.description
        d["name"] = self.name
        d["content"] = self.content
        d["uuid"] = self.uuid
        d["version"] = self.version
        d["local"] = self.local
        
        return d

class Storage():
    def __init__(self):
        self.uuid = ""
        self.key = ""
        self.value = ""
        
    def toDict(self):
        d = {}
        d["uuid"] = str(self.uuid)
        d["key"] = self.key
        d["value"] = self.value
        
        return d