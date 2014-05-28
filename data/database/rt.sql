CREATE TABLE "item" (
	"itemId" GUID PRIMARY KEY NOT NULL
	,"itemType" INTEGER NOT NULL
	,"collectionName" VARCHAR NOT NULL
	,"collectionNo" INTEGER
	,"l1Title" VARCHAR NOT NULL
	,"l1Content" BINARY DEFAULT(NULL)
	,"l1LanguageId" GUID NOT NULL
	,"l2Title" VARCHAR NOT NULL
	,"l2Content" BINARY DEFAULT(NULL)
	,"l2LanguageId" GUID
	,"created" FLOAT NOT NULL
	,"modified" FLOAT NOT NULL
	,"lastRead" FLOAT
	,"mediaUri" VARCHAR
	,"userId" GUID NOT NULL
	,"readTimes" INTEGER NOT NULL DEFAULT(0)
	,"listenedTimes" INTEGER NOT NULL DEFAULT(0)
	);

CREATE TABLE "language" (
	"languageId" GUID PRIMARY KEY
	,"name" VARCHAR NOT NULL
	,"created" FLOAT NOT NULL
	,"modified" FLOAT
	,"isArchived" INTEGER
	,"languageCode" VARCHAR NOT NULL
	,"userId" GUID NOT NULL
	,"direction" INTEGER NOT NULL
	,"termRegex" VARCHAR NOT NULL
	,"theme" VARCHAR
	,"sourceCode" VARCHAR NOT NULL DEFAULT '--'
	);

CREATE TABLE "language_plugin" (
	"languageId" GUID NOT NULL
	,"pluginId" GUID NOT NULL
	,PRIMARY KEY (
		"languageId"
		,"pluginId"
		)
	);

CREATE TABLE "languagecode" (
	"name" VARCHAR NOT NULL
	,"code" VARCHAR UNIQUE NOT NULL
	);

CREATE TABLE "plugin" (
	"pluginId" GUID PRIMARY KEY NOT NULL
	,"name" VARCHAR NOT NULL
	,"description" VARCHAR
	,"content" TEXT
	,"uuid" VARCHAR NOT NULL
	,"version" INTEGER NOT NULL DEFAULT(0)
	,"local" BOOLEAN NOT NULL DEFAULT 0
	);

CREATE TABLE "shared_term" (
	"id" INTEGER PRIMARY KEY NOT NULL
	,"code" VARCHAR NOT NULL
	,"phrase" VARCHAR NOT NULL
	,"lowerPhrase" VARCHAR NOT NULL
	,"basePhrase" VARCHAR NOT NULL
	,"sentence" VARCHAR NOT NULL
	,"definition" VARCHAR NOT NULL
	,"source" VARCHAR NOT NULL DEFAULT '--'
	);

CREATE TABLE "storage" (
	"uuid" GUID
	,"k" VARCHAR NOT NULL
	,"v" TEXT NOT NULL
	);

CREATE TABLE "term" (
	"termId" GUID PRIMARY KEY
	,"created" FLOAT NOT NULL
	,"modified" FLOAT
	,"phrase" VARCHAR NOT NULL
	,"basePhrase" VARCHAR
	,"lowerPhrase" VARCHAR NOT NULL
	,"definition" VARCHAR
	,"sentence" VARCHAR
	,"state" INTEGER NOT NULL
	,"languageId" GUID NOT NULL
	,"itemSourceId" GUID
	,"userId" GUID NOT NULL
	,"isFragment" BOOL NOT NULL DEFAULT 0
	);

CREATE TABLE "termlog" (
	"entryDate" FLOAT NOT NULL
	,"termId" GUID NOT NULL
	,"state" INTEGER NOT NULL
	,"type" INTEGER NOT NULL DEFAULT(0)
	,"languageId" GUID NOT NULL
	,"userId" GUID NOT NULL
	);

CREATE TABLE "user" (
	"userId" GUID PRIMARY KEY NOT NULL
	,"username" VARCHAR UNIQUE NOT NULL
	,"lastLogin" FLOAT
	,"accessKey" VARCHAR
	,"accessSecret" VARCHAR
	,"syncData" BOOL
	);

CREATE TRIGGER "TRIGGER_Term_Create"
AFTER INSERT ON "term"
FOR EACH ROW

BEGIN
	INSERT INTO termlog (
		entryDate
		,languageId
		,termId
		,STATE
		,userId
		,type
		)
	VALUES (
		new.created
		,new.languageId
		,new.termId
		,new.STATE
		,new.userId
		,1
		);
END;

CREATE TRIGGER "TRIGGER_Term_Delete" BEFORE

DELETE ON "term"
FOR EACH ROW

BEGIN
	INSERT INTO termlog (
		entryDate
		,languageId
		,termId
		,STATE
		,userId
		,type
		)
	VALUES (
		strftime('%s', 'now')
		,old.languageId
		,old.termId
		,old.STATE
		,old.userId
		,3
		);
END;

CREATE TRIGGER "TRIGGER_Term_Modify"
AFTER UPDATE ON "term"
FOR EACH ROW

BEGIN
	INSERT INTO termlog (
		entryDate
		,languageId
		,termId
		,STATE
		,userId
		,type
		)
	VALUES (
		new.modified
		,new.languageId
		,new.termId
		,new.STATE
		,new.userId
		,2
		);
END;

CREATE INDEX "IDX_item_l1Id" ON "item" ("l1LanguageId" ASC);

CREATE INDEX "IDX_item_l2Id" ON "item" ("l2LanguageId" ASC);

CREATE INDEX "IDX_term_languageId" ON "term" ("languageId" ASC);

CREATE UNIQUE INDEX "IDX_term_unique" ON "term" (
	"lowerPhrase" ASC
	,"languageId" ASC
	,"userId" ASC
	);

CREATE UNIQUE INDEX "IDX_unique_storage_key" ON "storage" (
	"uuid" ASC
	,"k" ASC
	);

