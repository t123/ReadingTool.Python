import time, uuid, re
from lib.models.model import User, Language, LanguageCode, Term, TermLog, Item, TermType, Plugin, LanguagePlugin
from lib.db import Db
from lib.misc import Application

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
            self.db.execute("UPDATE user SET username=:username, accessKey=:accessKey, accessSecret=:accessSecret, syncData=:syncData WHERE userId=:userId",
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
    
    def findAll(self, orderBy="lastLogin", maxResults=10):
        if orderBy=="lastLogin":
            return self.db.many(User, "SELECT * FROM user ORDER BY lastLogin LIMIT :limit", limit=maxResults)
        elif orderBy=="username":
            return self.db.many(User, "SELECT * FROM user ORDER BY username LIMIT :limit", limit=maxResults)
        else:
            return self.db.many(User, "SELECT * FROM user ORDER BY username LIMIT :limit", limit=maxResults)
    
    def loginUser(self, userId):
        self.db.execute("UPDATE user SET lastLogin=:lastLogin WHERE userId=:userId", lastLogin=time.time(), userId=userId)
            
    def delete(self, userId):
        languageService = LanguageService()
        
        for language in languageService.findAll():
            languageService.delete(language.languageId)
            
        self.db.execute("DELETE FROM user WHERE userId=:userId", userId)

class LanguageService:
    def __init__(self):
        self.db = Db(Application.connectionString)
        
    def save(self, language, plugins=None):
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
            self.db.execute("UPDATE language SET name=:name, modified=:modified, isArchived=:isArchived, languageCode=:languageCode, sentenceRegex=:sentenceRegex, termRegex=:termRegex, direction=:direction WHERE languageId=:languageId",
                            languageId= language.languageId,
                            name = language.name,
                            modified = time.time(),
                            isArchived = language.isArchived,
                            languageCode = language.languageCode,
                            sentenceRegex = language.sentenceRegex,
                            termRegex = language.termRegex,
                            direction = language.direction
                            )
            
        if plugins is not None:
            self.db.execute("DELETE FROM language_plugin WHERE languageId=:languageId", language.languageId)
            
            for pluginId in plugins:
                self.db.execute("INSERT INTO language_plugin ( languageId, pluginId ) VALUES ( :languageId, :pluginId )", language.languageId, pluginId)
                
        return self.findOne(language.languageId)
        
    def findAllPlugins(self, languageId, active=True):
        return self.db.many(LanguagePlugin, """SELECT a.PluginId, a.Name, a.Description, b.PluginId as enabled 
                                                FROM Plugin a 
                                                LEFT OUTER JOIN language_plugin b ON a.pluginid=b.pluginid AND b.languageid=:languageId 
                                                ORDER BY a.Name COLLATE NOCASE
                                                """,
                                                languageId=languageId
                                                )
        
    def findOne(self, languageId):
        return self.db.one(Language, "SELECT * FROM language WHERE languageId=:languageId AND userId=:userId", 
                           languageId=languageId, userId=Application.user.userId)
        
    def findOneByName(self, name):
        return self.db.one(Language, "SELECT * FROM language WHERE name=:name AND userId=:userId", 
                           name=name, userId=Application.user.userId)
    
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
        return self.db.many(LanguageCode, "SELECT * FROM LanguageCode ORDER BY name COLLATE NOCASE")
    
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
        
    def findAll(self):
        return self.db.many(Term, """SELECT term.*, b.name as language, c.collectionNo || ' - ' || c.CollectionName || ' ' || c.L1Title as itemSource
                                        FROM term term
                                        LEFT JOIN language b on term.languageId=b.LanguageId
                                        LEFT JOIN item c on term.itemSourceId=c.itemId
                                        WHERE term.userId=:userId
                                        ORDER BY term.lowerPhrase
                                        """, 
                                        userId=Application.user.userId
                            )
        
    def findOne(self, termId):
        return self.db.one(Term, """SELECT term.*, b.name as language, c.collectionNo || ' - ' || c.CollectionName || ' ' || c.L1Title as itemSource
                                        FROM term term
                                        LEFT JOIN language b on term.languageId=b.LanguageId
                                        LEFT JOIN item c on term.itemSourceId=c.itemId
                                        WHERE term.userId=:userId AND term.termId=:termId
                                        ORDER BY term.lowerPhrase
                                        """, 
                                        userId=Application.user.userId,
                                        termId=termId
                            )
    
    def fineOneByPhraseAndLanguage(self, phrase, languageId):
        lowerPhrase = (phrase or "").lower()
        return self.db.one(Term, """SELECT term.*, b.name as language, c.collectionNo || ' - ' || c.CollectionName || ' ' || c.L1Title as itemSource
                                        FROM term term
                                        LEFT JOIN language b on term.languageId=b.LanguageId
                                        LEFT JOIN item c on term.itemSourceId=c.itemId
                                        WHERE term.lowerPhrase=:lowerPhrase AND term.languageId=:languageId AND term.userId=:userId
                                        ORDER BY term.lowerPhrase
                                        """, 
                                        lowerPhrase=lowerPhrase, languageId=languageId, userId=Application.user.userId
                            )
    
    def findAllByLanguage(self, languageId):
        return self.db.many(Term, """SELECT term.*, b.name as language, c.collectionNo || ' - ' || c.CollectionName || ' ' || c.L1Title as itemSource
                                        FROM term term
                                        LEFT JOIN language b on term.languageId=b.LanguageId
                                        LEFT JOIN item c on term.itemSourceId=c.itemId
                                        WHERE term.languageId=:languageId AND term.userId=:userId
                                        ORDER BY term.lowerPhrase
                                        """, 
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
            self.db.execute("UPDATE item SET modified=:modified, itemType=:itemType, collectionName=:collectionName, collectionNo=:collectionNo, mediaUri=:mediaUri, lastRead=:lastRead, l1Title=:l1Title, l2Title=:l2Title, l1LanguageId=:l1LanguageId, l2LanguageId=:l2LanguageId, l1Content=:l1Content, l2Content=:l2Content, readTimes=:readTimes, listenedTimes=:listenedTimes WHERE itemId=:itemId",
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
                           SELECT item.itemId, item.created, item.modified, item.itemType, item.userId, item.collectionName, item.collectionNo, 
                           item.mediaUri, item.lastRead, item.l1Title, item.l2Title, item.l1LanguageId, item.l2LanguageId, '' as l1Content,
                           CASE WHEN length(item.l2Content) > 0 THEN substr(item.l2Content,0,20) ELSE '' END AS l2Content, 
                           item.readTimes, item.listenedTimes, B.Name as l1Language, C.Name as l2Language FROM item item
                           LEFT JOIN language B on item.l1LanguageId=B.LanguageId
                           LEFT JOIN language C on item.l2LanguageId=C.LanguageId
                           WHERE item.userId=:userId
                           ORDER BY l1Language, item.collectionName, item.collectionNo, item.l1Title
                           """, 
                           userId=Application.user.userId)
        
    def findRecentlyRead(self, maxItems=5):
        return self.db.many(Item, 
                            """
                           SELECT item.itemId, item.created, item.modified, item.itemType, item.userId, item.collectionName, item.collectionNo, 
                           item.mediaUri, item.lastRead, item.l1Title, item.l2Title, item.l1LanguageId, item.l2LanguageId, '' as l1Content, '' as l2Content, 
                           item.readTimes, item.listenedTimes, B.Name as l1Language, C.Name as l2Language FROM item item
                           LEFT JOIN language B on item.l1LanguageId=B.LanguageId
                           LEFT JOIN language C on item.l2LanguageId=C.LanguageId
                           WHERE item.userId=:userId
                           ORDER BY item.lastRead DESC
                           LIMIT :maxItems
                           """, 
                           userId=Application.user.userId, maxItems=maxItems)
        
    def findRecentlyCreated(self, maxItems=5):
        return self.db.many(Item, 
                            """
                           SELECT item.itemId, item.created, item.modified, item.itemType, item.userId, item.collectionName, item.collectionNo, 
                           item.mediaUri, item.lastRead, item.l1Title, item.l2Title, item.l1LanguageId, item.l2LanguageId, '' as l1Content, '' as l2Content, 
                           item.readTimes, item.listenedTimes, B.Name as l1Language, C.Name as l2Language FROM item item
                           LEFT JOIN language B on item.l1LanguageId=B.LanguageId
                           LEFT JOIN language C on item.l2LanguageId=C.LanguageId
                           WHERE item.userId=:userId
                           ORDER BY item.created DESC
                           LIMIT :maxItems
                           """, 
                           userId=Application.user.userId, maxItems=maxItems)
        
    def findPrevious(self, item, itemId=0, limit=1):
        if item is None:
            item = self.findOne(itemId)
        
        if item is None:
            return []
        
        return self.db.many(Item, 
                            """
                           SELECT item.itemId, item.created, item.modified, item.itemType, item.userId, item.collectionName, item.collectionNo, 
                           item.mediaUri, item.lastRead, item.l1Title, item.l2Title, item.l1LanguageId, item.l2LanguageId, '' as l1Content, '' as l2Content, 
                           item.readTimes, item.listenedTimes, B.Name as l1Language, C.Name as l2Language FROM item item
                           LEFT JOIN language B on item.l1LanguageId=B.LanguageId
                           LEFT JOIN language C on item.l2LanguageId=C.LanguageId
                           WHERE item.userId=:userId AND item.l1LanguageId=:l1LanguageId AND item.collectionName=:collectionName AND item.collectionNo<:collectionNo
                           ORDER BY item.collectionNo DESC
                           LIMIT :limit 
                           """, 
                           userId=Application.user.userId, l1LanguageId=item.l1LanguageId, collectionName=item.collectionName, collectionNo=item.collectionNo, limit=limit
                           )
        
    def findNext(self, item, itemId=0, limit=1):
        if item is None:
            item = self.findOne(itemId)
            
        if item is None:
            return []
        
        return self.db.many(Item, 
                            """
                           SELECT item.itemId, item.created, item.modified, item.itemType, item.userId, item.collectionName, item.collectionNo, 
                           item.mediaUri, item.lastRead, item.l1Title, item.l2Title, item.l1LanguageId, item.l2LanguageId, '' as l1Content, '' as l2Content, 
                           item.readTimes, item.listenedTimes, B.Name as l1Language, C.Name as l2Language FROM item item
                           LEFT JOIN language B on item.l1LanguageId=B.LanguageId
                           LEFT JOIN language C on item.l2LanguageId=C.LanguageId
                           WHERE item.userId=:userId AND item.l1LanguageId=:l1LanguageId AND item.collectionName=:collectionName AND item.collectionNo>:collectionNo
                           ORDER BY item.collectionNo
                           LIMIT :limit 
                           """, 
                           userId=Application.user.userId, l1LanguageId=item.l1LanguageId, collectionName=item.collectionName, collectionNo=item.collectionNo, limit=limit
                           )
    
    def copyItem(self, itemId):
        item = self.findOne(itemId)
        
        if item is None:
            return None
        
        copy = Item()
        copy.collectionName = item.collectionName
        copy.collectionNo = item.collectionNo
        copy.itemType = item.itemType
        copy.l1Content = item.l1Content
        copy.l2Content = item.l2Content
        copy.l1LanguageId = item.l1LanguageId
        copy.l2LanguageId = item.l2LanguageId
        copy.l1Title = item.l1Title + " (copy)"
        copy.l2Title = item.l2Title
        copy.mediaUri = item.mediaUri
        
        return copy
    
    def splitItem(self, itemId):
        item = self.findOne(itemId)
        
        if item is None:
            return
        
        l1Split = re.split("===", item.l1Content)
        l2Split = re.split("===", item.l2Content)
        
        for i in range(0, len(l1Split)):
            copy = self.copyItem(item.itemId)
            copy.l1Content = l1Split[i].strip()
            copy.l2Content = l2Split[i].strip() if i<len(l2Split) else ""
            
            if item.collectionNo is not None:
                copy.collectionNo = item.collectionNo+i
            else:
                copy.collectionNo = None
                
            self.save(copy)
     
class PluginService:
    def __init__(self):
        self.db = Db(Application.connectionString)
        
    def save(self, plugin):
        if(plugin.pluginId==0):
            plugin.pluginId= self.db.execute("INSERT INTO plugin ( pluginId, name, description, content, uuid) VALUES ( :pluginId, :name, :description, :content, :uuid)",
                            pluginId = None,
                            name = plugin.name,
                            description = plugin.description,
                            content = plugin.content,
                            uuid = str(uuid.uuid1())
                            )
        else:        
            self.db.execute("UPDATE plugin SET name=:name, description=:description, content=:content WHERE pluginId=:pluginId",
                            pluginId = plugin.pluginId,
                            name = plugin.name,
                            content = plugin.content,
                            description = plugin.description
                            )
            
        return self.findOne(plugin.pluginId)
        
    def findOne(self, pluginId):
        return self.db.one(Plugin, "SELECT * FROM Plugin WHERE pluginId=:pluginId", pluginId=pluginId)
        
    def findOneByName(self, name):
        return self.db.one(Plugin, "SELECT * FROM Plugin WHERE name=:name", name=name)
    
    def findAll(self):
        return self.db.many(Plugin, "SELECT * FROM Plugin ORDER BY name     COLLATE NOCASE")
    
    def delete(self, pluginId):
        self.db.execute("DELETE FROM Plugin WHERE pluginId=:pluginId", pluginId=pluginId)
        self.db.execute("DELETE FROM Language_Plugin WHERE pluginId=:pluginId", pluginId=pluginId)