import re, time, datetime

class StringUtil:
    @staticmethod
    def isEmpty(x):
        if x is None:
            return True
        
        x = x.strip()
        
        if len(x)==0:
            return True
        
        return False
    
    @staticmethod
    def isTrue(x):
        if x is None:
            return False
        
        if isinstance(x, bool) and x==True:
            return True
        
        x = str(x).lower().strip()
        
        if x=="1" or x=="true" or x=="yes":
            return True
        
        return False
    
class FilterParser():
    def __init__(self, languageNames=[]):
        self.languageNames = [item.lower() for item in languageNames]

        self.tags = []
        self.normal = []
        self.special = []
        self.languages = []
        self.source = []

        self.current = ""
        self.isTag = False
        self.inQuote = False
        
        self.limit = 0
        self.createdSign = ""
        self.modifiedSign = ""
        self.created = None
        self.modified = None
    
    def parseSource(self, string):
        string = string.replace("source:", "")
        self.source.append(string)

    def parseTime(self, string):
        string = string.lower()
        string = string.replace("created:", "")
        string = string.replace("modified:", "")
        
        sign1 = string[0:1]
        sign2 = string[0:2]
        
        if sign2==">=" or sign2=="<=":
            date = string[2:]
            sign = sign2
        elif sign1==">" or sign1=="<" or sign1=="=":            
            date = string[1:]
            sign = sign1
        else:
            date = string[0:]
            sign = "="
        try:
            if date=="today":
                now = datetime.datetime.now()
                date = now.strftime("%Y-%m-%d")
            elif date=="yesterday":
                yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
                date = yesterday.strftime("%Y-%m-%d")
             
            date = time.strptime(date, "%Y-%m-%d")
            created = date
            
            if sign.startswith("<"):
                created = date + 60*60*24
                
            return (sign, time.mktime(created))
        except:
            pass
        
        return None
        
    def append(self):
        if not StringUtil.isEmpty(self.current):
            if self.isTag:
                self.tags.append(self.current.lower())
                self.current = ""
                self.isTag = False
                self.inQuote = False
            else:
                if self.current.lower() in self.languageNames:
                    self.languages.append(self.current)
                else:
                    if self.current.lower().startswith("limit:"):
                        try:
                            self.limit = int(self.current[6:])
                        except:
                            self.limit = 0
                    elif self.current.lower().startswith("created:"):
                        result = self.parseTime(self.current)
                        
                        if result is not None:
                            self.createdSign = result[0]
                            self.created = result[1]
                            
                    elif self.current.lower().startswith("modified:"):
                        result = self.parseTime(self.current)
                        
                        if result is not None:
                            self.modifiedSign = result[0]
                            self.modified = result[1]
                    elif self.current.lower().startswith("source:"):
                        self.source.append(self.current[7:])
                    else:
                        self.normal.append(self.current)
                    
                self.current = ""
                self.isTag = False
                self.inQuote = False
                
    def filter(self, text):
        if StringUtil.isEmpty(text):
            return
        
        text = text.strip()
        
        for char in text:
            if char=="#":
                self.isTag = True
                continue
            
            if char=="\"":
                if self.inQuote:
                    self.append()
                    self.inQuote = False
                else:
                    self.inQuote = True
                    
                continue
                    
            if char==" ":
                if self.inQuote:
                    self.current += char
                    continue
                
                self.append()
                continue
                        
            self.current += char

        self.append()
