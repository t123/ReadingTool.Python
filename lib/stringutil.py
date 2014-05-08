class StringUtil:
    @staticmethod
    def isEmpty(x):
        if x is None:
            return True
        
        x = x.strip()
        
        if len(x)==0:
            return True
        
        return False