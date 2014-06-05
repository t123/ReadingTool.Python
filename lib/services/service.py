import time, uuid, re, logging, datetime
from lib.models.model import User, Language, LanguageCode, Term, TermLog, Item, ItemType, TermType, Plugin, LanguagePlugin, TermState, Storage, SharedTerm
from lib.db import Db
from lib.misc import Application
from lib.stringutil import StringUtil, FilterParser

def newId():
    return uuid.uuid1()

def emptyId(id):
    return id is None

def toUuid(input):
    if isinstance(input, str):
        return uuid.UUID(input)
    
    return input
        
class UserService:
    def __init__(self):
        self.db = Db(Application.connectionString)
        
    def __del__(self):
        if self.db:
            self.db.close()
            
    def save(self, user, refresh=True):
        if emptyId(user.userId):
            user.userId = newId() 
            
            self.db.execute("INSERT INTO user ( userId, username, lastLogin, accessKey, accessSecret, syncData ) VALUES ( :userId, :username, :lastLogin, :accessKey, :accessSecret, :syncData )",
                            userId=user.userId,
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

        if refresh:
            return self.findOne(user.userId)
        else:
            return user

    def findOne(self, userId):
        userId = toUuid(userId)
        
        return self.db.one(User, "SELECT * FROM user WHERE userId=:userId", userId=userId)
    
    def findOneByUsername(self, username):
        return self.db.one(User, "SELECT * FROM user WHERE username=:username", username=username)
    
    def findAll(self, orderBy="lastLogin", maxResults=10):
        if orderBy == "lastLogin":
            return self.db.many(User, "SELECT * FROM user ORDER BY lastLogin DESC LIMIT :limit", limit=maxResults)
        elif orderBy == "username":
            return self.db.many(User, "SELECT * FROM user ORDER BY username COLLATE NOCASE LIMIT :limit", limit=maxResults)
        else:
            return self.db.many(User, "SELECT * FROM user ORDER BY username COLLATE NOCASE LIMIT :limit", limit=maxResults)
    
    def loginUser(self, userId):
        userId = toUuid(userId)
        
        self.db.execute("UPDATE user SET lastLogin=:lastLogin WHERE userId=:userId", lastLogin=time.time(), userId=userId)
            
    def delete(self, userId):
        userId = toUuid(userId)
        
        languages = self.db.many(Language, "SELECT * FROM language WHERE userId=:userId ORDER BY Name COLLATE NOCASE", userId=userId)
        languageService = LanguageService()
        
        for language in languages:
            languageService.delete(language.languageId)
            
        self.db.execute("DELETE FROM user WHERE userId=:userId", userId)
            
class LanguageService:
    def __init__(self):
        self.db = Db(Application.connectionString)
        
    def __del__(self):
        if self.db:
            self.db.close()
            
    def save(self, language, plugins=None, refresh=True):
        if emptyId(language.languageId):
            language.languageId = newId() 
            
            self.db.execute("INSERT INTO language ( languageId, name, created, modified, isArchived, languageCode, userId, termRegex, direction, theme, sourceCode) VALUES ( :languageId, :name, :created, :modified, :isArchived, :languageCode, :userId, :termRegex, :direction, :theme, :sourceCode)",
                            languageId=language.languageId,
                            name=language.name,
                            created=time.time(),
                            modified=time.time(),
                            isArchived=language.isArchived,
                            languageCode=language.languageCode,
                            userId=Application.user.userId,
                            termRegex=language.termRegex,
                            direction=language.direction,
                            theme=language.theme,
                            sourceCode=language.sourceCode
                            )
        else:        
            self.db.execute("UPDATE language SET name=:name, modified=:modified, isArchived=:isArchived, languageCode=:languageCode, termRegex=:termRegex, direction=:direction, theme=:theme, sourceCode=:sourceCode WHERE languageId=:languageId",
                            languageId=language.languageId,
                            name=language.name,
                            modified=time.time(),
                            isArchived=language.isArchived,
                            languageCode=language.languageCode,
                            termRegex=language.termRegex,
                            direction=language.direction,
                            theme=language.theme,
                            sourceCode=language.sourceCode
                            )
            
        if plugins is not None:
            self.db.execute("DELETE FROM language_plugin WHERE languageId=:languageId", language.languageId)
            
            for pluginId in plugins:
                self.db.execute("INSERT INTO language_plugin ( languageId, pluginId ) VALUES ( :languageId, :pluginId )", language.languageId, pluginId)
                
        if refresh:
            return self.findOne(language.languageId)
        else:
            return language
        
    def findAllPlugins(self, languageId, active=None):
        languageId = toUuid(languageId)
        
        if active:
            return self.db.many(LanguagePlugin, """SELECT a.PluginId, a.Name, a.Description, b.PluginId as enabled, a.content, a.uuid 
                                                FROM Plugin a 
                                                LEFT OUTER JOIN language_plugin b ON a.pluginid=b.pluginid AND b.languageid=:languageId
                                                WHERE b.PluginId IS NOT NULL 
                                                ORDER BY a.Name COLLATE NOCASE
                                                """,
                                                languageId=languageId
                                                )
        else:
            return self.db.many(LanguagePlugin, """SELECT a.PluginId, a.Name, a.Description, b.PluginId as enabled, a.content, a.uuid
                                                FROM Plugin a 
                                                LEFT OUTER JOIN language_plugin b ON a.pluginid=b.pluginid AND b.languageid=:languageId 
                                                ORDER BY a.Name COLLATE NOCASE
                                                """,
                                                languageId=languageId
                                                )
        
    def findOne(self, languageId):
        languageId = toUuid(languageId)
        
        return self.db.one(Language, "SELECT * FROM language WHERE languageId=:languageId AND userId=:userId",
                           languageId=languageId, userId=Application.user.userId)
        
    def findOneByName(self, name):
        return self.db.one(Language, "SELECT * FROM language WHERE name=:name AND userId=:userId",
                           name=name, userId=Application.user.userId)
    
    def findAll(self, orderBy="name"):
        if orderBy == "archived":
            return self.db.many(Language, "SELECT * FROM language WHERE userId=:userId ORDER BY isArchived, Name COLLATE NOCASE", userId=Application.user.userId)
        
        return self.db.many(Language, "SELECT * FROM language WHERE userId=:userId ORDER BY Name COLLATE NOCASE", userId=Application.user.userId)
    
    def delete(self, languageId):
        languageId = toUuid(languageId)
        
        self.db.execute("DELETE FROM term WHERE languageId=:languageId", languageId=languageId)
        self.db.execute("DELETE FROM item WHERE l1LanguageId=:languageId", languageId=languageId)
        self.db.execute("DELETE FROM termLog WHERE languageId=:languageId", languageId=languageId)
        self.db.execute("DELETE FROM language WHERE languageId=:languageId", languageId=languageId)
        
    def any(self):
        return self.db.scalar("SELECT COUNT(languageId) FROM language WHERE userId=:userId", userId=Application.user.userId)>0
    
class LanguageCodeService:
    def __init__(self):
        self.db = Db(Application.connectionString)
        
    def __del__(self):
        if self.db:
            self.db.close()
            
    def save(self, lc):
        temp = self.findOne(lc.code)
        
        if temp is None:
            self.db.execute("INSERT INTO languagecode ( code, name ) VALUES ( :code, :name )", lc.code, lc.name)
        else:
            self.db.execute("UPDATE languagecode SET name=:name WHERE code=:code", lc.code, lc.name)
            
        return self.findOne(lc.code)
    
    def findOne(self, code):
        return self.db.one(LanguageCode, "SELECT * FROM languagecode WHERE code=:code", code=code)
    
    def findAll(self):
        return self.db.many(LanguageCode, "SELECT * FROM LanguageCode ORDER BY name COLLATE NOCASE")
    
    def reset(self):
        self.db.execute("DELETE FROM LanguageCode")
        
        codes = {}
        codes["Not Set"] = "--"
        codes["Afrikaans"] = "af"
        codes["Albanian"] = "sq"
        codes["Arabic"] = "ar"
        codes["Azerbaijani"] = "az"
        codes["Basque"] = "eu"
        codes["Bengali"] = "bn"
        codes["Belarusian"] = "be"
        codes["Bulgarian"] = "bg"
        codes["Catalan"] = "ca"
        codes["Chinese Simplified"] = "zh-CN"
        codes["Chinese Traditional"] = "zh-TW"
        codes["Croatian"] = "hr"
        codes["Czech"] = "cs"
        codes["Danish"] = "da"
        codes["Dutch"] = "nl"
        codes["English"] = "en"
        codes["Esperanto"] = "eo"
        codes["Estonian"] = "et"
        codes["Filipino"] = "tl"
        codes["Finnish"] = "fi"
        codes["French"] = "fr"
        codes["Galician"] = "gl"
        codes["Georgian"] = "ka"
        codes["German"] = "de"
        codes["Greek"] = "el"
        codes["Gujarati"] = "gu"
        codes["Haitian Creole"] = "ht"
        codes["Hebrew"] = "iw"
        codes["Hindi"] = "hi"
        codes["Hungarian"] = "hu"
        codes["Icelandic"] = "is"
        codes["Indonesian"] = "id"
        codes["Irish"] = "ga"
        codes["Italian"] = "it"
        codes["Japanese"] = "ja"
        codes["Kannada"] = "kn"
        codes["Korean"] = "ko"
        codes["Latin"] = "la"
        codes["Latvian"] = "lv"
        codes["Lithuanian"] = "lt"
        codes["Macedonian"] = "mk"
        codes["Malay"] = "ms"
        codes["Maltese"] = "mt"
        codes["Norwegian"] = "no"
        codes["Persian"] = "fa"
        codes["Polish"] = "pl"
        codes["Portuguese"] = "pt"
        codes["Romanian"] = "ro"
        codes["Russian"] = "ru"
        codes["Serbian"] = "sr"
        codes["Slovak"] = "sk"
        codes["Slovenian"] = "sl"
        codes["Spanish"] = "es"
        codes["Swahili"] = "sw"
        codes["Swedish"] = "sv"
        codes["Tamil"] = "ta"
        codes["Telugu"] = "te"
        codes["Thai"] = "th"
        codes["Turkish"] = "tr"
        codes["Ukrainian"] = "uk"
        codes["Urdu"] = "ur"
        codes["Vietnamese"] = "vi"
        codes["Welsh"] = "cy"
        codes["Yiddish"] = "yi"
        
        for name, code in codes.items():
            self.db.execute("INSERT INTO languagecode ( code, name ) VALUES ( :code, :name )", code, name)

class TermService:
    def __init__(self):
        self.db = Db(Application.connectionString)
        self.insertStatement = "INSERT INTO term ( termId, created, modified, phrase, lowerPhrase, basePhrase, definition, sentence, languageId, state, userId, itemSourceId, isFragment) VALUES ( :termId, :created, :modified, :phrase, :lowerPhrase, :basePhrase, :definition, :sentence, :languageId, :state, :userId, :itemSourceId, :isFragment)"
        self.updateStatement = "UPDATE term SET modified=:modified, lowerPhrase=:lowerPhrase, basePhrase=:basePhrase, definition=:definition, state=:state, itemSourceId=:itemSourceId, sentence=:sentence WHERE termId=:termId"
        
    def __del__(self):
        if self.db:
            self.db.close()
            
    def bulkSave(self, terms):
        db = Db(Application.connectionString, isolationLevel="IMMEDIATE")
        
        try:
            for term in terms:
                if emptyId(term.termId):
                    term.termId = newId()
                    
                    db.execute(self.insertStatement,
                                    termId=term.termId,
                                    created=time.time(),
                                    modified=time.time(),
                                    phrase=term.phrase.strip(),
                                    lowerPhrase=term.lowerPhrase.strip(),
                                    basePhrase=term.basePhrase.strip(),
                                    definition=term.definition.strip(),
                                    sentence=term.sentence.strip(),
                                    languageId=toUuid(term.languageId),
                                    state=term.state,
                                    userId=Application.user.userId,
                                    itemSourceId=toUuid(term.itemSourceId),
                                    isFragment=term.isFragment
                                    )
                    
                else:        
                    db.execute(self.updateStatement,
                                    termId=term.termId,
                                    modified=time.time(),
                                    lowerPhrase=term.lowerPhrase.strip(),
                                    basePhrase=term.basePhrase.strip(),
                                    definition=term.definition.strip(),
                                    sentence=term.sentence.strip(),
                                    state=term.state,
                                    itemSourceId=toUuid(term.itemSourceId)
                                    )
            db.commit()
        except:
            db.rollback()
            return False
        
        db.close()
        return True
        
    def save(self, term, refresh=True):
        if emptyId(term.termId):
            term.termId = newId()
            
            self.db.execute(self.insertStatement,
                            termId=term.termId,
                            created=time.time(),
                            modified=time.time(),
                            phrase=term.phrase.strip(),
                            lowerPhrase=term.lowerPhrase.strip(),
                            basePhrase=term.basePhrase.strip(),
                            definition=term.definition.strip(),
                            sentence=term.sentence.strip(),
                            languageId=toUuid(term.languageId),
                            state=term.state,
                            userId=Application.user.userId,
                            itemSourceId=toUuid(term.itemSourceId),
                            isFragment=term.isFragment
                            )
        else:        
            self.db.execute(self.updateStatement,
                            termId=term.termId,
                            modified=time.time(),
                            lowerPhrase=term.lowerPhrase.strip(),
                            basePhrase=term.basePhrase.strip(),
                            definition=term.definition.strip(),
                            sentence=term.sentence.strip(),
                            state=term.state,
                            itemSourceId=toUuid(term.itemSourceId)
                            )
            
        if refresh:
            return self.findOne(term.termId)
        else:
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
        termId = toUuid(termId)
        
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
        languageId = toUuid(languageId)
        
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
        languageId = toUuid(languageId)
        
        return self.db.many(Term, """SELECT term.*, b.name as language, c.collectionNo || ' - ' || c.CollectionName || ' ' || c.L1Title as itemSource
                                        FROM term term
                                        LEFT JOIN language b on term.languageId=b.LanguageId
                                        LEFT JOIN item c on term.itemSourceId=c.itemId
                                        WHERE term.languageId=:languageId AND term.userId=:userId
                                        ORDER BY term.lowerPhrase
                                        """,
                                        languageId=languageId, userId=Application.user.userId
                            )
        
    def findAllForParsing(self, languageId):
        languageId = toUuid(languageId)
        
        terms = self.db.many(Term, "SELECT term.* FROM term term WHERE term.languageId=:languageId AND term.isFragment=0 AND term.userId=:userId", languageId=languageId, userId=Application.user.userId)
        fragments = self.db.many(Term, "SELECT term.* FROM term term WHERE term.languageId=:languageId AND term.isFragment=1 AND term.State=2 AND term.userId=:userId", languageId=languageId, userId=Application.user.userId)
        
        return terms, fragments
        
    def delete(self, termId):
        term = self.findOne(termId)
        
        if term is None:
            return
        
        self.db.execute("DELETE FROM term WHERE termId=:termId and userId=:userId", termId=term.termId, userId=Application.user.userId)
        
    def search(self, filter):
        query = """SELECT term.*, b.name as language, c.collectionNo || ' - ' || c.CollectionName || ' ' || c.L1Title as itemSource
                    FROM term term
                    LEFT JOIN language b on term.languageId=b.LanguageId
                    LEFT JOIN item c on term.itemSourceId=c.itemId
                    WHERE term.userId=:userId
                """
                                        
        args = {"userId": Application.user.userId}
        
        languageService = LanguageService()
        fp = FilterParser([language.name for language in languageService.findAll()])
        fp.filter(filter)
        
        if len(fp.tags)>0:
            tagList = []

            for exp in fp.tags:
                if exp == "know" or exp=="known":
                    tagList.append("term.state=" + str(TermState.Known))
                elif exp == "unknown" or exp == "notknown":
                    tagList.append("term.state=" + str(TermState.Unknown))
                elif exp == "ignore" or exp == "ignored":
                    tagList.append("term.state=" + str(TermState.Ignored))

            if len(tagList)>0:
                query += " AND ( " + " OR ".join(tagList) + " )"

        if len(fp.tags)>0:
            tagList = []

            for exp in fp.tags:
                if exp == "word":
                    tagList.append("term.isFragment=0")
                elif exp == "phrase":
                    tagList.append("term.isFragment=1")

            if len(tagList)>0:
                query += " AND ( " + " OR ".join(tagList) + " )"
            
        if len(fp.languages)>0:
            t = []
            counter = 0
            
            for exp in fp.languages:
                t.append("language LIKE :l{0}".format(counter))
                args["l%d" % counter] = exp
                counter += 1
                
            query += " AND ( " + " OR ".join(t) + " )"
            
        if len(fp.normal)>0:
            t = []
            counter = 0
            
            for exp in fp.normal:
                t.append("(term.phrase LIKE :e{0} OR term.basePhrase LIKE :e{0}) ".format(counter))
                args["e%d" % counter] = exp + "%"
                counter += 1
                
            query += " AND ( " + " OR ".join(t) + " )"
                
        if fp.created is not None:
            if fp.createdSign=="=":
                query += " AND term.created>=:created1 and term.created<=:created2"
                args["created1"] = fp.created
                args["created2"] = fp.created + (60*60*24)
            else:
                query += " AND term.created" + fp.createdSign + ":created"
                args["created"] = fp.created
            
        if fp.modified is not None:
            if fp.modifiedSign=="=":
                query += " AND term.modified>=:modified1 and term.modified<=:modified2"
                args["modified1"] = fp.modified
                args["modified2"] = fp.modified + (60*60*24)
            else:
                query += " AND term.modified" + fp.modifiedSign + ":modified"
                args["modified"] = fp.modified
            
        query += " ORDER BY b.isArchived, language, term.lowerPhrase"
        
        if fp.limit>0:
            query += " LIMIT :limit"
            args["limit"] = fp.limit
        
        return self.db.many(Term, query, **args)

    def findHistory(self, termId):
        termId = toUuid(termId)
        return self.db.many(TermLog, "SELECT entryDate, termId, state, type, languageId, userId FROM termlog WHERE termId=:termId ORDER BY entryDate DESC", termId=termId)
       
    def findAlteredPastModifed(self, timestamp):
        return self.db.many(Term, """SELECT term.*, b.languageCode as language, b.sourceCode as sourceCode
                                        FROM term term
                                        LEFT JOIN language b on term.languageId=b.LanguageId
                                        WHERE 
                                            term.userId=:userId AND 
                                            term.modified>:timestamp AND 
                                            length(term.definition)>0 AND 
                                            language<>'--'
                                        ORDER BY term.lowerPhrase
                                        """,
                                        userId=Application.user.userId,
                                        timestamp=timestamp
                            )

    def findDeletedPastModifed(self, timestamp):
        return self.db.many(TermLog, "SELECT * FROM TermLog WHERE userId=:userId AND type=:type AND entryDate>:timestamp", userId=Application.user.userId, type=TermType.Delete, timestamp=timestamp)
            
class SharedTermService():
    def __init__(self):
        self.db = Db(Application.connectionString)
        
    def __del__(self):
        if self.db:
            self.db.close()
            
    def search(self, filter):
        query = """SELECT term.*, b.name as language
                    FROM shared_term term
                    LEFT JOIN language b on term.code=b.languageCode
                    WHERE b.userId=:userId
                """
                                        
        args = {"userId": Application.user.userId}
        
        languageService = LanguageService()
        fp = FilterParser([language.name for language in languageService.findAll()])
        fp.filter(filter)
        
        if len(fp.languages)>0:
            t = []
            counter = 0
            
            for exp in fp.languages:
                t.append("language LIKE :l{0}".format(counter))
                args["l%d" % counter] = exp
                counter += 1
                
            query += " AND ( " + " OR ".join(t) + " )"
            
        if len(fp.normal)>0:
            t = []
            counter = 0
            
            for exp in fp.normal:
                t.append("(term.phrase LIKE :e{0} OR term.basePhrase LIKE :e{0}) ".format(counter))
                args["e%d" % counter] = exp + "%"
                counter += 1
                
            query += " AND ( " + " OR ".join(t) + " )"
                
        query += " ORDER BY b.isArchived, language, term.lowerPhrase"
        
        if fp.limit>0:
            query += " LIMIT :limit"
            args["limit"] = fp.limit
        
        return self.db.many(SharedTerm, query, **args)
    
    def findAll(self):
        return self.db.many(SharedTerm, """SELECT term.*, b.name as language
                                        FROM shared_term term
                                        LEFT JOIN language b on term.code=b.languageCode
                                        ORDER BY term.lowerPhrase
                                        """,
                                        userId=Application.user.userId
                            )
        
    def update(self, terms):
        db = Db(Application.connectionString, isolationLevel="IMMEDIATE")
        
        for term in terms:
            t = db.one(SharedTerm, "SELECT * FROM shared_term WHERE id=:id", term["id"])
            
            try:
                if t is None:
                    db.execute("INSERT INTO shared_term ( id, phrase, lowerPhrase, basePhrase, definition, sentence, code, source) VALUES ( :id, :phrase, :lowerPhrase, :basePhrase, :definition, :sentence, :code, :source)",
                                id=term["id"],
                                phrase=term["phrase"].strip(),
                                lowerPhrase=term["phrase"].lower().strip(),
                                basePhrase=term["basePhrase"].strip(),
                                definition=term["definition"].strip(),
                                sentence=term["sentence"].strip(),
                                code=term["code"].strip(),
                                source=term["source"].strip()
                                )
                else:        
                    db.execute("UPDATE shared_term SET phrase=:phrase, lowerPhrase=:lowerPhrase, basePhrase=:basePhrase, definition=:definition, sentence=:sentence, code=:code, source=:source WHERE id=:id",
                                    id=term["id"],
                                    phrase=term["phrase"].strip(),
                                    lowerPhrase=term["phrase"].lower().strip(),
                                    basePhrase=term["basePhrase"].strip(),
                                    definition=term["definition"].strip(),
                                    sentence=term["sentence"].strip(),
                                    code=term["code"].strip(),
                                    source=term["source"].strip()
                                    )
            
            except: #just skip invalid terms
                pass
        
        db.commit()
                
    def deleteAll(self):
        self.db.execute("DELETE FROM shared_term")
            
class ItemService:
    def __init__(self):
        self.db = Db(Application.connectionString)
        self.insertStatement = "INSERT INTO item ( itemId, created, modified, itemType, userId, collectionName, collectionNo, mediaUri, lastRead, l1Title, l2Title, l1LanguageId, l2LanguageId, l1Content, l2Content, readTimes, listenedTimes) VALUES ( :itemId, :created, :modified, :itemType, :userId, :collectionName, :collectionNo, :mediaUri, :lastRead, :l1Title, :l2Title, :l1LanguageId, :l2LanguageId, :l1Content, :l2Content, :readTimes, :listenedTimes )"
        self.updateStatement = "UPDATE item SET modified=:modified, itemType=:itemType, collectionName=:collectionName, collectionNo=:collectionNo, mediaUri=:mediaUri, lastRead=:lastRead, l1Title=:l1Title, l2Title=:l2Title, l1LanguageId=:l1LanguageId, l2LanguageId=:l2LanguageId, l1Content=:l1Content, l2Content=:l2Content, readTimes=:readTimes, listenedTimes=:listenedTimes WHERE itemId=:itemId"
    
    def __del__(self):
        if self.db:
            self.db.close()
                  
    def bulkSave(self, items):
        db = Db(Application.connectionString, isolationLevel="IMMEDIATE")
        
        try:
            for item in items:
                if emptyId(item.itemId):
                    item.itemId = newId()
                    
                    self.db.execute(self.insertStatement,
                                    itemId=item.itemId,
                                    created=time.time(),
                                    modified=time.time(),
                                    itemType=item.itemType,
                                    userId=Application.user.userId,
                                    collectionName=item.collectionName,
                                    collectionNo=item.collectionNo,
                                    mediaUri=item.mediaUri,
                                    lastRead=item.lastRead,
                                    l1Title=item.l1Title,
                                    l2Title=item.l2Title,
                                    l1LanguageId=item.l1LanguageId,
                                    l2LanguageId=item.l2LanguageId,
                                    l1Content=item.l1Content,
                                    l2Content=item.l2Content,
                                    readTimes=item.readTimes,
                                    listenedTimes=item.listenedTimes
                                    )
                else:        
                    self.db.execute(self.updateStatement,
                                    itemId=item.itemId,
                                    modified=time.time(),
                                    itemType=item.itemType,
                                    collectionName=item.collectionName,
                                    collectionNo=item.collectionNo,
                                    mediaUri=item.mediaUri,
                                    lastRead=item.lastRead,
                                    l1Title=item.l1Title,
                                    l2Title=item.l2Title,
                                    l1LanguageId=item.l1LanguageId,
                                    l2LanguageId=item.l2LanguageId,
                                    l1Content=item.l1Content,
                                    l2Content=item.l2Content,
                                    readTimes=item.readTimes,
                                    listenedTimes=item.listenedTimes
                                    )
            
            db.commit()
        except:
            db.rollback()
            return False
        
        db.close()
        return True
        
    def save(self, item, refresh=True):
        if emptyId(item.itemId):
            item.itemId = newId()
            
            self.db.execute(self.insertStatement,
                            itemId=item.itemId,
                            created=time.time(),
                            modified=time.time(),
                            itemType=item.itemType,
                            userId=Application.user.userId,
                            collectionName=item.collectionName,
                            collectionNo=item.collectionNo,
                            mediaUri=item.mediaUri,
                            lastRead=item.lastRead,
                            l1Title=item.l1Title,
                            l2Title=item.l2Title,
                            l1LanguageId=item.l1LanguageId,
                            l2LanguageId=item.l2LanguageId,
                            l1Content=item.l1Content,
                            l2Content=item.l2Content,
                            readTimes=item.readTimes,
                            listenedTimes=item.listenedTimes
                            )
        else:        
            self.db.execute(self.updateStatement,
                            itemId=item.itemId,
                            modified=time.time(),
                            itemType=item.itemType,
                            collectionName=item.collectionName,
                            collectionNo=item.collectionNo,
                            mediaUri=item.mediaUri,
                            lastRead=item.lastRead,
                            l1Title=item.l1Title,
                            l2Title=item.l2Title,
                            l1LanguageId=item.l1LanguageId,
                            l2LanguageId=item.l2LanguageId,
                            l1Content=item.l1Content,
                            l2Content=item.l2Content,
                            readTimes=item.readTimes,
                            listenedTimes=item.listenedTimes
                            )
        
        if refresh:
            return self.findOne(item.itemId)
        else:
            return item
        
    def findOne(self, itemId):
        itemId = toUuid(itemId)
        
        return self.db.one(Item,
                           """
                           SELECT item.*, B.Name as l1Language, C.Name as l2Language FROM item item
                           LEFT JOIN language B on item.l1LanguageId=B.LanguageId
                           LEFT JOIN language C on item.l2LanguageId=C.LanguageId
                           WHERE item.itemId=:itemId AND item.userId=:userId
                           """,
                           itemId=itemId, userId=Application.user.userId)
    
    def delete(self, itemId):
        itemId = toUuid(itemId)
        
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
        
    def findPrevious(self, item, itemId=None, limit=1):
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
        
    def findNext(self, item, itemId=None, limit=1):
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
            copy.l2Content = l2Split[i].strip() if i < len(l2Split) else ""
            
            if item.collectionNo is not None:
                copy.collectionNo = item.collectionNo + i
            else:
                copy.collectionNo = None
                
            self.save(copy)
            
    def collectionsByLanguage(self, languageId):
        languageId = toUuid(languageId)
        
        return self.db.list("SELECT DISTINCT(CollectionName) as X FROM item WHERE X<>'' AND userId=:userId AND l1LanguageId=:languageId ORDER BY x COLLATE NOCASE", userId=Application.user.userId, languageId=languageId)
    
    def collectionsByLanguages(self, languageIds=[]):
        if languageIds is None or languageIds==[]:
            return self.db.list("SELECT DISTINCT(CollectionName) as X FROM item WHERE X<>'' AND userId=:userId ORDER BY x COLLATE NOCASE", userId=Application.user.userId)
            
        ids = [toUuid(id) for id in languageIds]
        
        stmt = """SELECT DISTINCT(item.collectionName) as X  
FROM item item, language language
WHERE X<>'' AND item.userId=:userId AND item.l1LanguageId=language.languageId AND item.l1LanguageId IN (%s)
ORDER BY language.name COLLATE NOCASE, X COLLATE NOCASE""" % ("?," * len(languageIds))[:-1]
        
        return self.db.list(stmt, Application.user.userId, *ids)
        
    def changeState(self, itemId, type, value):
        if value<0:
            return
        
        if(type=="listen"):
            self.db.execute("UPDATE item SET listenedTimes=:value WHERE itemId=:itemId", value, itemId)
            
        if(type=="read"):
            self.db.execute("UPDATE item SET readTimes=:value WHERE itemId=:itemId", value, itemId)
            
    def search(self, filter):
        query = """
                           SELECT item.itemId, item.created, item.modified, item.itemType, item.userId, item.collectionName, item.collectionNo, 
                           item.mediaUri, item.lastRead, item.l1Title, item.l2Title, item.l1LanguageId, item.l2LanguageId, '' as l1Content,
                           CASE WHEN length(item.l2Content) > 0 THEN substr(item.l2Content,0,20) ELSE '' END AS l2Content, 
                           item.readTimes, item.listenedTimes, B.Name as l1Language, C.Name as l2Language FROM item item
                           LEFT JOIN language B on item.l1LanguageId=B.LanguageId
                           LEFT JOIN language C on item.l2LanguageId=C.LanguageId
                           WHERE item.userId=:userId 
                           """
        
        languageService = LanguageService()
        fp = FilterParser([language.name for language in languageService.findAll()])
        fp.filter(filter)
                           
        args = {
                "userId": Application.user.userId
                }
        
        if len(fp.tags)>0:
            tagList = []
            
            for exp in fp.tags:
                if exp == "parallel":
                    tagList.append("(item.L2Content IS NOT NULL AND item.L2Content<>'')")
                if exp == "single":
                    tagList.append("(item.L2Content IS NULL OR item.L2Content='')")
                elif exp == "media":
                    tagList.append("(item.mediaUri IS NOT NULL AND item.mediaUri<>'')")
                elif exp == "text":
                    tagList.append("item.itemType={0}".format(ItemType.Text))
                elif exp == "video":
                    tagList.append("item.itemType={0}".format(ItemType.Video))
                    
            query += " AND ( " + " OR ".join(tagList) + " )"
        
        if len(fp.languages)>0:
            t = []
            counter = 0
            
            for exp in fp.languages:
                t.append("l1Language LIKE :l{0}".format(counter))
                args["l%d" % counter] = exp
                counter += 1
                
            query += " AND ( " + " OR ".join(t) + " )"
                
        
        if len(fp.normal) > 0:
            t = []
            counter = 0
            
            for exp in fp.normal:
                t.append("item.collectionName LIKE :e{0} OR item.l1Title LIKE :e{0}".format(counter))
                args["e%d" % counter] = exp + "%"
                counter += 1
                
            query += " AND ( " + " OR ".join(t) + " )"
        
        if fp.created is not None:
            if fp.createdSign=="=":
                query += " AND item.created>=:created1 and item.created<=:created2"
                args["created1"] = fp.created
                args["created2"] = fp.created + (60*60*24)
            else:
                query += " AND item.created" + fp.createdSign + ":created"
                args["created"] = fp.created
            
        if fp.modified is not None:
            if fp.modifiedSign=="=":
                query += " AND item.modified>=:modified1 and item.modified<=:modified2"
                args["modified1"] = fp.modified
                args["modified2"] = fp.modified + (60*60*24)
            else:
                query += " AND item.modified" + fp.modifiedSign + ":modified"
                args["modified"] = fp.modified
                
        query += " ORDER BY B.isArchived, l1Language, item.collectionName, item.collectionNo, item.l1Title"

        if fp.limit>0:
            query += " LIMIT :limit"
            args["limit"] = fp.limit
            
        return self.db.many(Item, query, **args)

class PluginService:
    def __init__(self):
        self.db = Db(Application.connectionString)
        
    def __del__(self):
        if self.db:
            self.db.close()
            
    def save(self, plugin, refresh=True):
        if emptyId(plugin.pluginId):
            plugin.pluginId = self.db.execute("INSERT INTO plugin ( pluginId, name, description, content, uuid, version, local) VALUES ( :pluginId, :name, :description, :content, :uuid, :version, :local)",
                            pluginId=newId(),
                            name=plugin.name,
                            description=plugin.description,
                            content=plugin.content,
                            uuid=plugin.uuid,
                            version=plugin.version,
                            local=plugin.local
                            )
        else:        
            self.db.execute("UPDATE plugin SET name=:name, description=:description, content=:content, version=:version WHERE pluginId=:pluginId",
                            pluginId=plugin.pluginId,
                            name=plugin.name,
                            content=plugin.content,
                            description=plugin.description,
                            version=plugin.version,
                            local=plugin.local
                            )
            
        if refresh:
            return self.findOne(plugin.pluginId)
        else:
            return plugin
        
    def findOne(self, pluginId):
        pluginId = toUuid(pluginId)
        
        return self.db.one(Plugin, "SELECT * FROM Plugin WHERE pluginId=:pluginId", pluginId=pluginId)
        
    def findOneByName(self, name):
        return self.db.one(Plugin, "SELECT * FROM Plugin WHERE name=:name", name=name)
    
    def findOneByUuid(self, uuid):
        return self.db.one(Plugin, "SELECT * FROM Plugin WHERE uuid=:uuid", uuid=uuid)
    
    def findAll(self):
        return self.db.many(Plugin, "SELECT * FROM Plugin ORDER BY name COLLATE NOCASE")
    
    def findLocal(self):
        return self.db.many(Plugin, "SELECT * FROM Plugin WHERE local=1 ORDER BY name COLLATE NOCASE")
    
    def delete(self, pluginId):
        self.db.execute("DELETE FROM Plugin WHERE pluginId=:pluginId", pluginId=pluginId)
        self.db.execute("DELETE FROM Language_Plugin WHERE pluginId=:pluginId", pluginId=pluginId)

class StorageService:
    SERVER_LOCAL = "server_local"
    SERVER_REMOTE = "server_remote"
    
    DB_BACKUP_DIRECTORY = "db_backup_directory"
    DB_BACKUP_MAXFILES = "db_backup_maxfiles"
    DB_VERSION = "db_version"
    DB_LAST_VACUUM = "db_last_vacuum"
    
    SOFTWARE_VERSION = "software_version"
    SOFTWARE_CHECK_UPDATES = "software_check_updates"
    SOFTWARE_DEBUG = "software_debug"
    SOFTWARE_REPORT_ERRORS = "software_report_errors"
    
    MEDIA_PLUGIN = "media_plugin"
    
    PLUGIN_LAST_CHECK = "plugin_last_check"
    PLUGIN_CACHE = "plugin_cache"
    
    SHARE_TERMS = "share_terms"
    SHARE_TERMS_LAST_SYNC = "share_terms_last_sync"
    
    def __init__(self):
        self.db = Db(Application.connectionString)
        
    def __del__(self):
        if self.db:
            self.db.close()
            
    def delete(self, key, uuid=None):
        """Deletes key"""
        uuid = toUuid(uuid)
        
        if uuid is None:
            self.db.execute("DELETE FROM storage WHERE k=:key AND uuid is null", key=key)
        else:
            self.db.execute("DELETE FROM storage WHERE k=:key AND uuid=:uuid", uuid=uuid, key=key)
        
    def save(self, key, value, uuid=None):
        """Inserts a new value or replaces an existing if the key already exists"""
        s = self.findOne(key, uuid)
        
        uuid = toUuid(uuid)
            
        if s is None:
            self.db.execute("INSERT INTO storage (uuid, k, v) VALUES (:uuid, :key, :value)", uuid=uuid, key=key, value=value)
        else:
            if uuid is None:
                self.db.execute("UPDATE storage SET v=:value WHERE k=:key AND uuid is null", key=key, value=value)
            else:
                self.db.execute("UPDATE storage SET v=:value WHERE k=:key AND uuid=:uuid", uuid=uuid, key=key, value=value)
    
    def findOne(self, key, uuid=None):
        """Returns the storage object for a given key and UUID"""
        uuid = toUuid(uuid)
        
        if uuid is None:
            return self.db.one(Storage, "SELECT uuid, k as key, v as value FROM storage WHERE k=:key AND uuid is null", key=key)
        else:
            return self.db.one(Storage, "SELECT uuid, k as key, v as value FROM storage WHERE k=:key AND uuid=:uuid", key=key, uuid=uuid)
    
    def findAll(self, uuid=None):
        """Returns all the storage objects for a given UUID"""
        uuid = toUuid(uuid)
        
        if uuid is None:
            return self.db.many(Storage, "SELECT uuid, k as key, v as value FROM storage WHERE uuid is null")
        else:
            return self.db.many(Storage, "SELECT uuid, k as key, v as value FROM storage WHERE uuid=:uuid", uuid=uuid)
    
    def find(self, key, default=None, uuid=None):
        """Returns the storage value for a given key and UUID"""
        uuid = toUuid(uuid)
        
        if uuid is None:
            result = self.db.scalar("SELECT v as value FROM storage WHERE k=:key AND uuid is null", key=key)
        else:
            result = self.db.scalar("SELECT v as value FROM storage WHERE k=:key AND uuid=:uuid", key=key, uuid=uuid)
        
        if result is None:
            return default
        
        return result
    
    @staticmethod
    def sdelete(key, uuid=None):
        """Deletes key"""
        db = Db(Application.connectionString)
        uuid = toUuid(uuid)
        
        if uuid is None:
            db.execute("DELETE FROM storage WHERE k=:key AND uuid is null", key=key)
        else:
            db.execute("DELETE FROM storage WHERE k=:key AND uuid=:uuid", uuid=uuid, key=key)
            
        db.close()
        
    @staticmethod
    def sfind(key, default=None, uuid=None):
        """Returns the storage value for a given key and UUID"""
        db = Db(Application.connectionString)
        uuid = toUuid(uuid)
        
        result = None
        
        if uuid is None:
            result = db.scalar("SELECT v as value FROM storage WHERE k=:key AND uuid is null", key=key)
        else:
            result = db.scalar("SELECT v as value FROM storage WHERE k=:key AND uuid=:uuid", key=key, uuid=uuid)

        if result is None:
            return default
        
        db.close()
        return result
    
    @staticmethod
    def ssave(key, value, uuid=None):
        """Inserts a new value or replaces an existing if the key already exists"""
        db = Db(Application.connectionString)
        uuid = toUuid(uuid)
        s = None
        
        if uuid is None:
            s = db.one(Storage, "SELECT uuid, k as key, v as value FROM storage WHERE k=:key AND uuid is null", key=key)
        else:
            s = db.one(Storage, "SELECT uuid, k as key, v as value FROM storage WHERE k=:key AND uuid=:uuid", key=key, uuid=uuid)
            
        if s is None:
            db.execute("INSERT INTO storage (uuid, k, v) VALUES (:uuid, :key, :value)", uuid=uuid, key=key, value=value)
        else:
            if uuid is None:
                db.execute("UPDATE storage SET v=:value WHERE k=:key AND uuid is null", key=key, value=value)
            else:
                db.execute("UPDATE storage SET v=:value WHERE k=:key AND uuid=:uuid", uuid=uuid, key=key, value=value)
            
        db.close()
    
class DatabaseService:
    def __init__(self):
        self.db = Db(Application.connectionString)
        self.storageService = StorageService()
        
    def __del__(self):
        if self.db:
            self.db.close()
            
    def tableExists(self, name):
        return self.db.scalar("SELECT COUNT(name) FROM sqlite_master WHERE type='table' AND name=:name", name=name)
    
    def indexExist(self, name):
        return self.db.scalar("SELECT COUNT(name) FROM sqlite_master WHERE type='index' AND name=:name", name=name)
    
    def compact(self):
        self.db.execute("VACUUM;")
        
    def upgradeRequired(self):
        if not self.tableExists("storage"):
            logging.debug("missing required table")
            return True
        
        version = self.storageService.findOne(StorageService.DB_VERSION)
        
        if version==None or version<Application.version:
            logging.debug("Required dbversion: %d, your version: %d" % (Application.version, version or 0))
            return True
        
        return False
    
    def createDb(self):
        if self.tableExists("storage"):
            return
        
        import os
        
        logging.debug("creating db")
        sql = ""
        
        with open (os.path.join(Application.pathDatabase, "rt.sql"), "r") as file:
            sql = file.read()
                  
        self.db.script(sql)
        
        storageService = StorageService()
        languageCodeService = LanguageCodeService()
        
        storageService.save(StorageService.SOFTWARE_VERSION, Application.version)
        languageCodeService.reset()
    
    def upgradeDb(self):
        version = self.storageService.findOne(StorageService.DB_VERSION)
        
        if version==None:
            version = 0
            
        if version<=1:
            pass
            
        if version<=2:
            pass
