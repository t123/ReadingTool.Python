import os, re, datetime, math
from lxml import etree
from lib.services.service import UserService, ItemService, LanguageService, TermService
from lib.models.model import User, Item, Language, LanguageDirection, TermState, ItemType
from lib.models.parser import ParserInput, ParserOutput, SRT
from lib.misc import Time, Application
from lib.stringutil import StringUtil
        
class BaseParser:
    def __init__(self):
        self.pi = None
        self.po = ParserOutput()
        self.frequency = {}
        self.xsltFile = None
        self.htmlFile = None
    
    def splitIntoTerms(self, sentence, regex):
        matches = regex.split(sentence)
            
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
                                webApi=Application.apiServer, 
                                isParallel=str(self.pi.asParallel), 
                                collectionName=self.pi.item.collectionName or "",
                                collectionNo=str(self.pi.item.collectionNo) if self.pi.item.collectionNo else "",
                                dateCreated=Time.toLocal(self.pi.item.created),
                                dateModified=Time.toLocal(self.pi.item.modified),
                                lastRead=Time.toLocal(self.pi.item.lastRead) if self.pi.item.lastRead else "",
                                l1Title=self.pi.item.l1Title,
                                l2Title=self.pi.item.l2Title,
                                mediaUri=self.pi.item.mediaUri,
                                l1Id=str(self.pi.language1.languageId),
                                l2Id=str(self.pi.language2.languageId) if self.pi.language2 else "",
                                itemType=ItemType.ToString(self.pi.item.itemType).lower(),
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
                termNode.attrib["isWhitespace"] = "True"
                
        return termNode
    
    def addFrequencyData(self, document):
        totalTerms = sum(self.frequency.values())
        common = {}
        notseenState = TermState.ToString(TermState.NotSeen).lower()
        
        t = []
        for el in document.iter("term"):
            if el.attrib["isTerm"]=="True":
                el.attrib["occurrences"] = str(self.frequency[el.text.lower()])
                el.attrib["frequency"] = str(round(self.frequency[el.text.lower()]/totalTerms*100, 2))
                
                if el.attrib["state"]==notseenState:
                    t.append([el, el.attrib["phrase"], el.attrib["frequency"]])
                    common[el.text.lower()] = self.frequency[el.text.lower()]
                    
        t = sorted(t, key=lambda tup: tup[2], reverse=True)
        u = []
        counter = 0
        
        for i in t:
            if counter>60:
                break
            
            if i[1] in u:
                continue
            
            for el in document.iter("term"):
                if el.attrib["isTerm"]=="True" and el.attrib["phrase"]==i[1]:
                    if counter<20:
                        el.attrib["commonness"] = "high"
                    elif counter<40:
                        el.attrib["commonness"] = "medium"
                    else:
                        el.attrib["commonness"] = "low"
                        
            u.append(i[1])
            counter += 1
        
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
        self.po.item = parserInput.item
        
        l1Paragraphs = self.splitIntoParagraphs(self.pi.item.getL1Content())
        l2Paragraphs = self.splitIntoParagraphs(self.pi.item.getL2Content())
        
        l1SentenceRegex = re.compile(self.pi.language1.sentenceRegex)
        l1TermRegex = re.compile(self.pi.language1.termRegex)
        
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
                    if term=="":
                        continue
                    
                    sentenceNode.append(self.createTermNode(term, l1TermRegex))
                    
                l1ParagraphNode.append(sentenceNode)
                
            joinNode.append(l1ParagraphNode) 
            joinNode.append(l2ParagraphNode)
            contentNode.append(joinNode)
        
        root.append(contentNode)
        self.addFrequencyData(root)
        self.calculateUniqueTerms(root)
                
        self.po.xml = etree.tostring(root, pretty_print=True, encoding="utf8") 
        
        htmlContent = None
        
        with open (os.path.join(Application.pathParsing, self.htmlFile), "r") as htmlFile:
            htmlContent = htmlFile.read()
            
        self.po.html = htmlContent.replace("<!-- table -->", str(self.applyTransform(root))).replace('<!-- plugins -->', "<script src=\"<!-- webapi -->/resource/v1/plugins/" + str(self.pi.language1.languageId) + "\"></script>").replace("<!-- webapi -->", Application.apiServer)
        
        return self.po

class VideoParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.xsltFile = "video.xslt"
        self.htmlFile = "watching.html"
        
    def parseSrt(self, content):
        srtList = []
        
        lines = content.splitlines()
        
        srt = None
        
        for line in lines:
            if StringUtil.isEmpty(line):
                continue
            
            if line.isdigit():
                if srt is not None:
                    srtList.append(srt)
                    
                srt = SRT()
                srt.lineNo = int(line)
            elif "-->" in line:
                times = line.split(" --> ")
                start = datetime.datetime.strptime(times[0], "%H:%M:%S,%f")
                end = datetime.datetime.strptime(times[1], "%H:%M:%S,%f")
                srt.start = start.hour*60*60 + start.minute*60 + start.second + start.microsecond/1000000
                srt.end = end.hour*60*60 + end.minute*60 + end.second + end.microsecond/1000000
            else:
                if srt is None:
                    continue
                
                if StringUtil.isEmpty(srt.content):
                    srt.content = line
                else:
                    srt.content += " " + line

        return srtList
    
    def parse(self, parserInput):
        self.pi = parserInput
        self.po.item = parserInput.item
        self.po.l1Srt = self.parseSrt(self.po.item.getL1Content())
        self.po.l2Srt = self.parseSrt(self.po.item.getL2Content()) if self.pi.asParallel else []
        
        l1SentenceRegex = re.compile(self.pi.language1.sentenceRegex)
        l1TermRegex = re.compile(self.pi.language1.termRegex)
        
        root = etree.Element("root")
        contentNode = self.createContentNode()
        
        for i in range(0,len(self.po.l1Srt)):
            l1Paragraph = self.po.l1Srt[i]
            l2Paragraph = self.po.l2Srt[i] if self.po.l2Srt is not None and i<len(self.po.l2Srt) and self.pi.asParallel else None
             
            joinNode = etree.Element("join")
            joinNode.attrib["line"] = str(l1Paragraph.lineNo)
            
            l1ParagraphNode = etree.Element("paragraph")
            l2ParagraphNode = etree.Element("translation")
            
            l1ParagraphNode.attrib["start"] = str(l1Paragraph.start)
            l1ParagraphNode.attrib["end"] = str(l1Paragraph.end)
            
            l2ParagraphNode.text = l2Paragraph.content if l2Paragraph is not None else ""
            l1ParagraphNode.attrib["direction"] = "ltr" if self.pi.language1.direction==LanguageDirection.LeftToRight else "rtl"            
            l2ParagraphNode.attrib["direction"] = "ltr" if self.pi.language2 and self.pi.language2.direction==LanguageDirection.LeftToRight else "rtl"
            
            sentences = self.splitIntoSentences(l1Paragraph.content, l1SentenceRegex)
            
            for sentence in sentences:
                sentenceNode = etree.Element("sentence")
                terms = self.splitIntoTerms(sentence, l1TermRegex)
                
                for term in terms:
                    if term=="":
                        continue
                    
                    sentenceNode.append(self.createTermNode(term, l1TermRegex))
                    
                l1ParagraphNode.append(sentenceNode)
                
            joinNode.append(l1ParagraphNode) 
            joinNode.append(l2ParagraphNode)
            contentNode.append(joinNode)
        
        root.append(contentNode)
        self.addFrequencyData(root)
        self.calculateUniqueTerms(root)
                
        self.po.xml = etree.tostring(root, pretty_print=True, encoding="utf8") 
        
        htmlContent = None
        
        with open (os.path.join(Application.pathParsing, self.htmlFile), "r") as htmlFile:
            htmlContent = htmlFile.read()
            
        self.po.html = htmlContent.replace("<!-- table -->", str(self.applyTransform(root))).replace('<!-- plugins -->', "<script src=\"<!-- webapi -->/resource/v1/plugins/" + str(self.pi.language1.languageId) + "\"></script>").replace("<!-- webapi -->", Application.apiServer)
        
        return self.po