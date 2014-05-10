import re
class StringUtil:
    @staticmethod
    def isEmpty(x):
        if x is None:
            return True
        
        x = x.strip()
        
        if len(x)==0:
            return True
        
        return False
    
class FilterParser():
    def __init__(self):
        self.tags = []
        self.normal = []
        self.special = []
        
        self.current = ""
        self.isTag = False
        self.inQuote = False
    
    def append(self):
        if not StringUtil.isEmpty(self.current):
            if self.isTag:
                self.tags.append(self.current)
                self.current = ""
                self.isTag = False
                self.inQuote = False
            else:
                self.normal.append(self.current)
                self.current = ""
                self.isTag = False
                self.inQuote = False
                
    def filter(self, text):
        if StringUtil.isEmpty(text):
            return
        
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
