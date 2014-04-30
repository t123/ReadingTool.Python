import os, re
from lxml import etree
from lib.services.service import UserService, ItemService, LanguageService, TermService
from lib.models.model import User, Item, Language, LanguageDirection, TermState, ItemType
from lib.models.parser import ParserInput, ParserOutput
from lib.misc import Time, Application
        
class BaseParser:
    def __init__(self):
        self.pi = None
        self.po = ParserOutput()
        self.frequency = {}
        self.xsltFile = None
        self.htmlFile = None
    
    def splitIntoTerms(self, sentence, regex):
        matches = regex.findall(sentence)
        return matches
    
    def splitIntoSentences(self, paragraph, regex):
        paragraph = paragraph or ""
        
        if not paragraph.endswith('\n'):
            paragraph += '\n'
            
        matches = regex.findall(paragraph)
        
        if len(matches)==0:
            return [paragraph.strip()]
        
        return matches
        
    def splitIntoParagraphs(self, content):
        if not content:
            return []
        
        return content.splitlines()
    
    def createContentNode(self):
        content = etree.Element("content", 
                                isParallel=str(self.pi.asParallel), 
                                collectionName=self.pi.item.collectionName or "",
                                collectionNo=str(self.pi.item.collectionNo) if self.pi.item.collectionNo else "",
                                dateCreated=Time.toLocal(self.pi.item.created),
                                dateModified=Time.toLocal(self.pi.item.modified),
                                lastRead=Time.toLocal(self.pi.item.lastRead) if self.pi.item.lastRead else "",
                                l1Title=self.pi.item.l1Title,
                                l2Title=self.pi.item.l2Title,
                                l1Id=str(self.pi.language1.languageId),
                                l2Id=str(self.pi.language2.languageId) if self.pi.language2 else "",
                                itemType=str(self.pi.item.itemType),
                                itemId=str(self.pi.item.itemId),
                                l1Direction=str(self.pi.language1.direction),
                                l2Direction=str(self.pi.language2.direction) if self.pi.language2 else "",
                                l1Code=self.pi.language1.languageCode,
                                l2Code=self.pi.language2.languageCode if self.pi.language2 else ""
                                )
        
        return content;
    
    def createTermNode(self, term, l1TermRegex):
        termLower = term.lower()
        termNode = etree.Element("term",
                                 phrase = termLower,
                                 phraseClass = termLower.replace("'", "_").replace("\"", "_")
                                 )
        termNode.text = term
        
        if l1TermRegex.match(term):
            self.po.stats.totalTerms += 1
            termNode.attrib["isTerm"] = "True"
            
            if self.frequency.__contains__(termLower):
                self.frequency[termLower] += 1
            else:
                self.frequency[termLower] = 1
                
            if self.pi.lookup.__contains__(termLower):
                existing = self.pi.lookup[termLower]
                termNode.attrib["state"] = TermState.ToString(existing.state).lower()
                termNode.attrib["definition"] = existing.fullDefinition()
                
                if existing.state==TermState.Known:
                    self.po.stats.known += 1
                elif existing.state==TermState.Unknown:
                    self.po.stats.unknown += 1
                elif existing.state==TermState.Ignored:
                    self.po.stats.ignored += 1
            else:
                self.po.stats.notseen += 1
                termNode.attrib["state"] = TermState.ToString(TermState.NotSeen).lower()
                
        else:
            termNode.attrib["isTerm"] = "False"
            
            if term.isspace():
                termNode.attr["isWhitespace"] = "True"
                
        return termNode
    
    def addFrequencyData(self, document):
        totalTerms = sum(self.frequency.values())
        common = {}
        notseenState = TermState.ToString(TermState.NotSeen).lower()
        
        for el in document.iter("term"):
            if el.attrib["isTerm"]=="True":
                el.attrib["occurences"] = str(self.frequency[el.text.lower()])
                el.attrib["frequency"] = str(self.frequency[el.text.lower()]/totalTerms*100)
                
                if el.attrib["state"]==notseenState:
                    common[el.text.lower()] = self.frequency[el.text.lower()]

        # TODO
        #nodes = sorted(common, key=common.get, reverse=True)
        #inv_map = {v:k for k, v in common.items()}
        
    def calculateUniqueTerms(self, document):
        terms = {}
        
        for el in document.iter("term"):
            if el.attrib["isTerm"]=="True":
                terms[el.text.lower()] = el.attrib["state"]
                
        self.po.stats.uniqueTerms = len(terms)
        
        for state in terms.values():
            if state==TermState.ToString(TermState.Known).lower():
                self.po.stats.uniqueKnown += 1
            elif state==TermState.ToString(TermState.Unknown).lower():
                self.po.stats.uniqueUnknown += 1
            elif state==TermState.ToString(TermState.Ignored).lower():
                self.po.stats.uniqueIgnored += 1
            elif state==TermState.ToString(TermState.NotSeen).lower():
                self.po.stats.uniqueNotSeen += 1
        
    def applyTransform(self, document):
        xsltContent = None
        
        with open (os.path.join(Application.pathParsing, self.xsltFile), "r") as xsltFile:
            xsltContent = xsltFile.read()

        xslt = etree.XML(xsltContent)
        transform = etree.XSLT(xslt)
        return transform(document)
        
class TextParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.xsltFile = "text.xslt"
        self.htmlFile = "reading.html"
        
    def parse(self, parserInput):
        self.pi = parserInput
        l1Paragraphs = self.splitIntoParagraphs(self.pi.item.l1Content)
        l2Paragraphs = self.splitIntoParagraphs(self.pi.item.l2Content)
        
        l1SentenceRegex = re.compile(self.pi.language1.sentenceRegex)
        l1TermRegex = re.compile(self.pi.language2.termRegex)
        
        root = etree.Element("root")
        contentNode = self.createContentNode()

        for i in range(0, len(l1Paragraphs)):
            l1Paragraph = l1Paragraphs[i]
            l2Paragraph = l2Paragraphs[i] if l2Paragraphs and self.pi.asParallel and i<len(l2Paragraphs) else ''
            
            joinNode = etree.Element("join")
            l1ParagraphNode = etree.Element("paragraph")
            l1ParagraphNode.attrib["direction"] = "ltr" if self.pi.language1.direction==LanguageDirection.LeftToRight else "rtl"
            
            l2ParagraphNode = etree.Element("translation")
            l2ParagraphNode.text = l2Paragraph
            l2ParagraphNode.attrib["direction"] = "ltr" if self.pi.language2 and self.pi.language2.direction==LanguageDirection.LeftToRight else "rtl"
            
            sentences = self.splitIntoSentences(l1Paragraph, l1SentenceRegex)
            
            for sentence in sentences:
                sentenceNode = etree.Element("sentence")
                terms = self.splitIntoTerms(sentence, l1TermRegex)
                
                for term in terms:
                    sentenceNode.append(self.createTermNode(term, l1TermRegex))
                    
                l1ParagraphNode.append(sentenceNode)
                
            joinNode.append(l1ParagraphNode) 
            joinNode.append(l2ParagraphNode)
            contentNode.append(joinNode)
        
        root.append(contentNode)
        self.addFrequencyData(root)
        self.calculateUniqueTerms(root)
                
        self.po.xml = etree.tostring(root, pretty_print=False) 
        
        htmlContent = None
        
        with open (os.path.join(Application.pathParsing, self.htmlFile), "r") as htmlFile:
            htmlContent = htmlFile.read()
            
        self.po.html = htmlContent.replace("<!-- table -->", str(self.applyTransform(root)))
