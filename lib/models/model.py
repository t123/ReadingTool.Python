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
    TERM_REGEX = "([a-zA-ZÀ-ÖØ-öø-ȳ\\'-]+)"
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
        
        if not self.basePhrase.isspace():
            fullDef += self.basePhrase + "<br/>" 
            
        if not self.definition.isspace():
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
        self.l1Content = ""
        self.l2Content = ""
        self.readTimes = 0
        self.listenedTimes = 0
        self.l1Language = None
        self.l2Language = None
        
    def hasMedia(self):
        if self.mediaUri is None:
            return False
        
        test = self.mediaUri.strip()
        
        if test.isspace() or len(test)==0:
            return False
        
        return True
    
    def isParallel(self):
        if self.l2Content is None:
            return False
        
        test = self.l2Content.strip()
        
        if test.isspace() or len(test)==0:
            return False
        
        return True
    
    def name(self):
        name = ""
        if self.collectionNo:
            name += str(self.collectionNo) + ". "
            
        if not self.collectionName.isspace():
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
    