import time
from lib.misc import Application
from lib.models.model import User, Language, LanguageCode, Term, TermLog, Item, TermType
from lib.db import Db

class UserService:
    def __init__(self):
        self.db = Db(Application.connectionString)
        
    def save(self, user):
        if(user.userId==0):
            user.userId = self.db.execute("INSERT INTO user ( userId, username, lastLogin, accessKey, accessSecret, syncData ) VALUES ( :userId, :username, :lastLogin, :accessKey, :accessSecret, :syncData )",
                            userId=None,
                            username=user.username,
                            lastLogin=None,
                            accessKey=user.accessKey,
                            accessSecret=user.accessSecret,
                            syncData=user.syncData
                            )
        else:        
            self.db.execute("UPDATE user SET userId=:userId, username=:username, syncData=:syncData WHERE userId=:userId",
                            userId=user.userId,
                            username=user.username,
                            accessKey=user.accessKey,
                            accessSecret=user.accessSecret,
                            syncData=user.syncData
                            )

        return self.findOne(user.userId)   

    def findOne(self, userId):
        return self.db.one(User, "SELECT * FROM user WHERE userId=:userId", userId=userId)
    
    def findOneByUsername(self, username):
        return self.db.one(User, "SELECT * FROM user WHERE username=:username", username=username)
    
    def loginUser(self, userId):
        user = self.findOne(userId)
        
        if user:
            user.lastLogin = time.time()
            self.save(user)
            
    def delete(self, userId):
        languageService = LanguageService()
        
        for language in languageService.findAll():
            languageService.delete(language.languageId)
            
        self.db.execute("DELETE FROM user WHERE userId=:userId", userId)

class LanguageService:
    def __init__(self):
        self.db = Db(Application.connectionString)
        
    def save(self, language):
        if(language.languageId==0):
            language.languageId = self.db.execute("INSERT INTO language ( languageId, name, created, modified, isArchived, languageCode, userId, sentenceRegex, termRegex, direction) VALUES ( :languageId, :name, :created, :modified, :isArchived, :languageCode, :userId, :sentenceRegex, :termRegex, :direction )",
                            languageId = None,
                            name = language.name,
                            created = time.time(),
                            modified = time.time(),
                            isArchived = language.isArchived,
                            languageCode = language.languageCode,
                            userId = Application.user.userId,
                            sentenceRegex = language.sentenceRegex,
                            termRegex = language.termRegex,
                            direction = language.direction
                            )
        else:        
            self.db.execute("UPDATE language SET name=:name, modified=:modified, isArchived=:isArchived, languageCode=:languageCode, sentenceRegex=:sentenceRegex, termRegex=:termRegex WHERE languageId=:languageId",
                            languageId= language.languageId,
                            name = language.name,
                            modified = time.time(),
                            isArchived = language.isArchived,
                            languageCode = language.languageCode,
                            sentenceRegex = language.sentenceRegex,
                            termRegex = language.termRegex,
                            direction = language.direction
                            )
            
        return self.findOne(language.languageId)
        
    def findOne(self, languageId):
        return self.db.one(Language, "SELECT * FROM language WHERE languageId=:languageId AND userId=:userId", 
                           languageId=languageId, userId=Application.user.userId)
    
    def findAll(self):
        return self.db.many(Language, "SELECT * FROM language WHERE userId=:userId ORDER BY Name COLLATE NOCASE", Application.user.userId)
    
    def delete(self, languageId):
        self.db.execute("DELETE FROM term WHERE languageId=:languageId AND userId=:userId", languageId=languageId, userId=Application.user.userId)
        self.db.execute("DELETE FROM item WHERE l1LanguageId=:languageId AND userId=:userId", languageId=languageId, userId=Application.user.userId)
        self.db.execute("DELETE FROM termLog WHERE languageId=:languageId AND userId=:userId", languageId=languageId, userId=Application.user.userId)
        self.db.execute("DELETE FROM language WHERE languageId=:languageId AND userId=:userId", languageId=languageId, userId=Application.user.userId)
    
class LanguageCodeService:
    def __init__(self):
        self.db = Db(Application.connectionString)
        
    def save(self, lc):
        temp = self.findOne(lc.code)
        
        if temp is None:
            self.db.execute("INSERT INTO languagecode ( code, name ) VALUES ( :code, :name )", lc.code, lc.name)
        else:
            self.db.execute("UPDATE languagecode SET name=:name WHERE code=:code", lc.code, lc.name )
            
        return self.findOne(lc.code)
    
    def findOne(self, code):
        return self.db.one(LanguageCode, "SELECT * FROM languagecode WHERE code=:code", code=code)
    
    def findAll(self):
        return self.db.many(LanguageCode, "SELECT * FROM LanguageCode ORDER BY name")
    
class TermService:
    def __init__(self):
        self.db = Db(Application.connectionString)
        
    def save(self, term):
        isNew = True
        if(term.termId==0):
            term.termId = self.db.execute("INSERT INTO term ( termId, created, modified, phrase, lowerPhrase, basePhrase, definition, sentence, languageId, state, userId, itemSourceId) VALUES ( :termId, :created, :modified, :phrase, :lowerPhrase, :basePhrase, :definition, :sentence, :languageId, :state, :userId, :itemSourceId)",
                            termId = None,
                            created = time.time(),
                            modified = time.time(),
                            phrase = term.phrase,
                            lowerPhrase = term.lowerPhrase,
                            basePhrase = term.basePhrase,
                            definition = term.definition,
                            sentence = term.sentence,
                            languageId = term.languageId,
                            state = term.state,
                            userId = Application.user.userId,
                            itemSourceId = term.itemSourceId
                            )
        else:        
            isNew = False
            self.db.execute("UPDATE term SET modified=:modified, lowerPhrase=:lowerPhrase, basePhrase=:basePhrase, definition=:definition, state=:state, itemSourceId=:itemSourceId WHERE termId=:termId",
                            termId= term.termId,
                            modified = time.time(),
                            lowerPhrase = term.lowerPhrase,
                            basePhrase = term.basePhrase,
                            definition = term.definition,
                            sentence = term.sentence,
                            state = term.state,
                            itemSourceId = term.itemSourceId
                            )
            
        self.db.execute("INSERT INTO termlog ( entryDate, languageId, termId, state, userId, type ) VALUES (:entryDate, :languageId, :termId, :state, :userId, :type)",
                        entryDate = time.time(),
                        languageId = term.languageId,
                        termId = term.termId,
                        state = term.state,
                        userId = Application.user.userId,
                        type = TermType.Create if isNew else TermType.Modify
                        )
            
        term = self.findOne(term.termId)
            
        return term
        
    def findOne(self, termId):
        return self.db.one(Term, "SELECT * FROM term WHERE termId=:termId", termId=termId)
    
    def fineOneByPhraseAndLanguage(self, phrase, languageId):
        lowerPhrase = (phrase or "").lower()
        return self.db.one(Term, "SELECT * FROM term WHERE lowerPhrase=:lowerPhrase AND languageId=:languageId AND userId=:userId", 
                           lowerPhrase=lowerPhrase, languageId=languageId, userId=Application.user.userId)
    
    def findAllByLanguage(self, languageId):
        return self.db.many(Term, "SELECT * FROM term WHERE languageId=:languageId AND userId=:userId",
                            languageId=languageId, userId=Application.user.userId
                            )
        
    def delete(self, termId):
        term = self.findOne(termId)
        
        if term is None:
            return
        
        self.db.execute("INSERT INTO termlog ( entryDate, languageId, termId, state, userId, type ) VALUES (:entryDate, :languageId, :termId, :state, :userId, :type)",
                        entryDate = time.time(),
                        languageId = term.languageId,
                        termId = term.termId,
                        state = term.state,
                        userId = Application.user.userId,
                        type = TermType.Delete
                        )
        
        self.db.execute("DELETE FROM term WHERE termId=:termId and userId=:userId", termId=termId, userId=Application.user.userId)
        
class ItemService:
    def __init__(self):
        self.db = Db(Application.connectionString)
        
    def save(self, item):
        if(item.itemId==0):
            item.itemId = self.db.execute("INSERT INTO item ( itemId, created, modified, itemType, userId, collectionName, collectionNo, mediaUri, lastRead, l1Title, l2Title, l1LanguageId, l2LanguageId, l1Content, l2Content, readTimes, listenedTimes) VALUES ( :itemId, :created, :modified, :itemType, :userId, :collectionName, :collectionNo, :mediaUri, :lastRead, :l1Title, :l2Title, :l1LanguageId, :l2LanguageId, :l1Content, :l2Content, :readTimes, :listenedTimes )",
                            itemId = None,
                            created = time.time(),
                            modified = time.time(),
                            itemType = item.itemType, 
                            userId = Application.user.userId, 
                            collectionName = item.collectionName, 
                            collectionNo = item.collectionNo, 
                            mediaUri = item.mediaUri, 
                            lastRead = item.lastRead, 
                            l1Title = item.l1Title, 
                            l2Title = item.l2Title, 
                            l1LanguageId = item.l1LanguageId, 
                            l2LanguageId = item.l2LanguageId, 
                            l1Content = item.l1Content, 
                            l2Content = item.l2Content, 
                            readTimes = item.readTimes, 
                            listenedTimes = item.listenedTimes
                            )
        else:        
            item.itemId = self.db.execute("UPDATE INTO item SET modified=:modified, itemType=:itemType, collectionName=:collectionName, collectionNo:=collectionNo, mediaUri:=mediaUri, lastRead:=lastRead, l1Title:=l1Title, l2Title:=l2Title, l1LanguageId:=l1LanguageId, l2LanguageId:=l2LanguageId, l1Content:=l1Content, l2Content:=l2Content, readTimes:=readTimes, listenedTimes:=listenedTimes WHERE itemId=:itemId",
                            itemId = item.itemId,
                            modified = time.time(),
                            itemType = item.itemType, 
                            collectionName = item.collectionName, 
                            collectionNo = item.collectionNo, 
                            mediaUri = item.mediaUri, 
                            lastRead = item.lastRead, 
                            l1Title = item.l1Title, 
                            l2Title = item.l2Title, 
                            l1LanguageId = item.l1LanguageId, 
                            l2LanguageId = item.l2LanguageId, 
                            l1Content = item.l1Content, 
                            l2Content = item.l2Content, 
                            readTimes = item.readTimes, 
                            listenedTimes = item.listenedTimes
                            )
        
        return self.findOne(item.itemId)
        
    def findOne(self, itemId):
        return self.db.one(Item,
                           """
                           SELECT item.*, B.Name as l1Language, C.Name as l2Language FROM item item
                           LEFT JOIN language B on item.l1LanguageId=B.LanguageId
                           LEFT JOIN language C on item.l2LanguageId=C.LanguageId
                           WHERE item.itemId=:itemId AND item.userId=:userId
                           """, 
                           itemId=itemId, userId=Application.user.userId)
    
    def delete(self, itemId):
        self.db.execute("DELETE FROM item WHERE itemId=:itemId and userId=:userId", itemId=itemId, userId=Application.user.userId)
        
    def findAll(self):
        return self.db.many(Item, 
                            """
                           SELECT item.*, B.Name as l1Language, C.Name as l2Language FROM item item
                           LEFT JOIN language B on item.l1LanguageId=B.LanguageId
                           LEFT JOIN language C on item.l2LanguageId=C.LanguageId
                           WHERE item.userId=:userId
                           """, 
                           userId=Application.user.userId)