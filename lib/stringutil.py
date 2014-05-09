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
    
    def stripQuotes(self, text):
        if text.startswith('"'):
            text = text[1:len(text)]
            
        if text.endswith('"'):
            text = text[0:-1]
            
        return text
    
    def split(self, text):
        return text.split(":", 1)
        
    def filter(self, text):
        if StringUtil.isEmpty(text):
            return
        
        p = re.compile('[\w:]+|\w+|"[\w\s]*"|#\w+|#"[\w\s]*"')
        matches = p.findall(text.lower())
        for match in matches:
            if match.startswith("#"):
                match = match[1:len(match)]
                match = self.stripQuotes(match)
                self.tags.append(match)
            elif ":" in match:
                self.special.append(self.split(match))
            else:
                match = self.stripQuotes(match)
                self.normal.append(match)
