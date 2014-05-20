import os, re, datetime, math, logging, time
from lxml import etree
from copy import deepcopy
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
        self.joinString = "<br/>"
    
    def splitIntoTerms(self, sentence):
        matches = self.l1TermRegex.findall(sentence)
        return matches
    
    def splitIntoSentences(self, paragraph):
        if not paragraph.endswith('\n'):
            paragraph += '\n'
            
        matches = self.l1SentenceRegex.findall(paragraph)
      
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
    
    def createTermNode(self, term, fragments):
        if term[0]!="": #term
            termNode = etree.Element("term")
            termLower = term[0].lower()
            termNode.text = term[0]
            self.po.stats.totalTerms += 1
            termNode.attrib["phrase"] = termLower
            termNode.attrib["phraseClass"] = termLower.replace("'", "_").replace("\"", "_")
            
            if self.frequency.__contains__(termLower):
                self.frequency[termLower] += 1
            else:
                self.frequency[termLower] = 1
                
            if self.pi.lookup.__contains__(termLower):
                existing = self.pi.lookup[termLower]
                termNode.attrib["state"] = TermState.ToString(existing.state).lower()
                
                definition = existing.fullDefinition(self.joinString)
                
                if not StringUtil.isEmpty(definition):
                    termNode.attrib["definition"] = definition
                
                if existing.state==TermState.Known:
                    self.po.stats.known += 1
                elif existing.state==TermState.Unknown:
                    self.po.stats.unknown += 1
                elif existing.state==TermState.Ignored:
                    self.po.stats.ignored += 1
            else:
                self.po.stats.notseen += 1
                termNode.attrib["state"] = TermState.ToString(TermState.NotSeen).lower()
                
            return termNode
        
        if term[1]!="": #whitespace
            termNode = etree.Element("whitespace")
            termNode.text = term[1]
            return termNode
        
        if term[2]!="": #number
            termNode = etree.Element("number")
            termNode.text = term[2]
            return termNode
        
        if term[3]!="": #fragment
            if fragments is not None and term[3] in fragments:
                return deepcopy(fragments[term[3]])
            
            logging.debug("missing fragment: %s" % term[3])
            return None
        
        if term[4]!="": #tag
            termNode = etree.Element("tag")
            termNode.text = term[4]
            return termNode
            
        if term[5]!="": #punctuation
            termNode = etree.Element("punctuation")
            termNode.text = term[5]
            return termNode
        
        return None
    
    def addFrequencyData(self, document):
        time1 = time.time()
        totalTerms = sum(self.frequency.values())
        common = {}
        notseenState = TermState.ToString(TermState.NotSeen).lower()
        
        t = []
        for el in document.iter("term"):
            el.attrib["occurrences"] = str(self.frequency[el.text.lower()])
            el.attrib["frequency"] = str(round(self.frequency[el.text.lower()]/totalTerms*100, 2))
            
            if el.attrib["state"]==notseenState:
                t.append([el, el.attrib["phrase"], el.attrib["frequency"]])
                common[el.text.lower()] = self.frequency[el.text.lower()]
                    
        t = sorted(t, key=lambda tup: tup[2], reverse=True)
        time2 = time.time()
        
        u = []
        counter = 0
        
        for i in t:
            if counter>60:
                break
            
            if i[1] in u:
                continue
            
            for el in document.iter("term"):
                if el.attrib["phrase"]==i[1]:
                    if counter<20:
                        el.attrib["commonness"] = "high"
                    elif counter<40:
                        el.attrib["commonness"] = "medium"
                    else:
                        el.attrib["commonness"] = "low"
                        
            u.append(i[1])
            counter += 1
            
        logging.debug("\taddFrequencyData 1={}".format(time2-time1))
        logging.debug("\taddFrequencyData 2={}".format(time.time()-time2))
        logging.debug("addFrequencyData total={}".format(time.time()-time1))
        
    def calculateUniqueTerms(self, document):
        time1 = time.time()
        terms = {}
        
        for el in document.iter("term"):
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
                
        logging.debug("calculateUniqueTerms={}".format(time.time()-time1))
        
    def applyTransform(self, document=None):
        time1 = time.time()
        xsltContent = None
        
        with open (os.path.join(Application.pathParsing, self.xsltFile), "r") as xsltFile:
            xsltContent = xsltFile.read()

        xslt = etree.XML(xsltContent)
        transform = etree.XSLT(xslt)
        
        if document is None:
            result = transform(etree.fromstring(self.po.xml))
        else:
            result = transform(document)
        
        logging.debug("applyTransform={}".format(time.time()-time1))
        
        return result
        
    def parseFragments(self, content):
        time1 = time.time()
        
        mdict = { }
        rdict = { }
        counter = 0
        
        for lower, t in self.pi.fragments.items():
            matches = re.findall(lower, content, re.IGNORECASE) 
             
            if len(matches)==0:
                continue
             
            for match in matches:
                if not match in mdict:
                    root = etree.Element("fragment")
                    root.attrib["termId"] = str(t.termId)
                    root.attrib["lower"] = lower
                    root.attrib["phrase"] = match
                    root.attrib["state"] = TermState.ToString(t.state).lower()
                     
                    definition = t.fullDefinition(self.joinString)
                     
                    if not StringUtil.isEmpty(definition):
                        root.attrib["definition"] = definition
                     
                    terms = self.splitIntoTerms(match)
                         
                    for term in terms:
                        root.append(self.createTermNode(term, None))
         
                    #xml = etree.tostring(root, pretty_print=False, encoding="utf8")
                    mdict[match] = root
                    rdict["__" + str(counter) + "__"]  = root
                    content = content.replace(match, "__" + str(counter) + "__")
                    counter += 1
            
        logging.debug("parseFragments={}".format(time.time()-time1))
        return (content, rdict)

class TextParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.xsltFile = "text.xslt"
        self.htmlFile = "reading.html"
        
    def parse(self, parserInput):
        self.pi = parserInput
        self.po.item = parserInput.item
        self.l1TermRegex = re.compile(self.pi.language1.termRegex)
        
        time1 = time.time()        
        
        l1Content = self.pi.item.getL1Content()
        l1Content, fragments = self.parseFragments(l1Content)
        
        l1Paragraphs = self.splitIntoParagraphs(l1Content)
        l2Paragraphs = self.splitIntoParagraphs(self.pi.item.getL2Content())
        
        root = etree.Element("root")
        contentNode = self.createContentNode()
        
        time2 = time.time()
        logging.debug("\tparse (root)={}".format(time2-time1))
        
        for i in range(0, len(l1Paragraphs)):
            l1Paragraph = l1Paragraphs[i]
            
            if l1Paragraph is None:
                continue
            
            l2Paragraph = l2Paragraphs[i] if l2Paragraphs and self.pi.asParallel and i<len(l2Paragraphs) else ''
            
            joinNode = etree.Element("join")
            l1ParagraphNode = etree.Element("paragraph")
            l1ParagraphNode.attrib["direction"] = "ltr" if self.pi.language1.direction==LanguageDirection.LeftToRight else "rtl"
            
            l2ParagraphNode = etree.Element("translation")
            l2ParagraphNode.text = l2Paragraph
            l2ParagraphNode.attrib["direction"] = "ltr" if self.pi.language2 and self.pi.language2.direction==LanguageDirection.LeftToRight else "rtl"
            
            terms = self.splitIntoTerms(l1Paragraph)
            for term in terms:
                termNode = self.createTermNode(term, fragments)
                
                if termNode is not None:
                    l1ParagraphNode.append(termNode)
                    #l1ParagraphNode.append(sentenceNode)
                
            joinNode.append(l1ParagraphNode) 
            joinNode.append(l2ParagraphNode)
            contentNode.append(joinNode)
        
        root.append(contentNode)
        
        time3 = time.time()
        logging.debug("\tparse (xml)={}".format(time3-time2))
        
        self.addFrequencyData(root)
        self.calculateUniqueTerms(root)
                
        time4 = time.time()
        logging.debug("\t parse (frequency)={}".format(time4-time3))
        
        self.po.xml = etree.tostring(root, pretty_print=True, encoding="utf8")
        htmlContent = None
        
        with open (os.path.join(Application.pathParsing, self.htmlFile), "r") as htmlFile:
            htmlContent = htmlFile.read()
            
        #WTF?? Newlines in XSLT transform cause extra spaces around punctuation. If anyone wants to try fix that... 
        transform = re.sub("span>\s+<span", "span><span", str(self.applyTransform(root)))
        
        theme = ""
        if not StringUtil.isEmpty(self.pi.language1.theme):
            theme = self.pi.language1.theme + "_reading.css"
                
        joined = os.path.join(Application.path, os.path.join("resources", theme))
        if StringUtil.isEmpty(theme) or not os.path.exists(joined):
                theme = "reading.css"
                    
        logging.debug("Using css: %s" % theme)
        
        self.po.html = htmlContent.replace("<!-- table -->", transform) \
                .replace('<!-- plugins -->', "<script src=\"<!-- webapi -->/resource/v1/plugins/" + str(self.pi.language1.languageId) + "\"></script>") \
                .replace('<!-- theme -->', theme) \
                .replace("<!-- webapi -->", Application.apiServer)
                
        time5 = time.time()
        logging.debug("\tparse (html+xslt)={}".format(time5-time4))
        logging.debug("parse total={}".format(time5-time1))
        
        return self.po
    
class LatexParser(BaseParser):
    def __init__(self):
        super().__init__()
        self.xsltFile = "latex.xslt"
        self.htmlFile = ""
        self.joinString = " ; "
        
    def createContentNode(self):
        content = etree.Element("content",
                                author=Application.user.username,
                                title=self.pi.item.l1Title
                                )
        
        return content;
    
    def parse(self, parserInput):
        self.pi = parserInput
        self.po.item = parserInput.item
        self.l1TermRegex = re.compile(self.pi.language1.termRegex)
        
        l1Content = self.pi.item.getL1Content()
        l1Content, fragments = self.parseFragments(l1Content)
        
        l1Paragraphs = self.splitIntoParagraphs(l1Content)
        
        root = etree.Element("root")
        contentNode = self.createContentNode()
        
        for i in range(0, len(l1Paragraphs)):
            l1Paragraph = l1Paragraphs[i]
            
            if l1Paragraph is None:
                continue;
            
            joinNode = etree.Element("join")
            l1ParagraphNode = etree.Element("paragraph")
            l1ParagraphNode.attrib["direction"] = "ltr" if self.pi.language1.direction==LanguageDirection.LeftToRight else "rtl"
            
            l2ParagraphNode = etree.Element("translation")
            l2ParagraphNode.text = ''
            l2ParagraphNode.attrib["direction"] = "ltr"
            
            terms = self.splitIntoTerms(l1Paragraph)
            
            for term in terms:
                termNode = self.createTermNode(term, fragments)
                
                if termNode is not None:
                    l1ParagraphNode.append(termNode)
                    
            joinNode.append(l1ParagraphNode) 
            joinNode.append(l2ParagraphNode)
            contentNode.append(joinNode)
        
        root.append(contentNode)
                
        self.po.xml = etree.tostring(root, pretty_print=True, encoding="utf8")
        latex = str(self.applyTransform())
        self.po.html = re.sub("/\*(.)*?\*/", lambda m: re.sub("\s+", " ", m.group(0).rstrip('\n').replace("/*", "").replace("*/", "")), latex, flags=re.DOTALL)
        self.po.html = re.sub("\s+([”“,\-:\"/«»…\?!\.]\s+)", r"\1", self.po.html)
        #self.po.html = ' '.join(latex.split())
                
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
        self.l1TermRegex = re.compile(self.pi.language1.termRegex)
        
        l1Content = self.pi.item.getL1Content()
        l1Content, fragments = self.parseFragments(l1Content)
        
        self.po.l1Srt = self.parseSrt(l1Content)
        self.po.l2Srt = self.parseSrt(self.po.item.getL2Content()) if self.pi.asParallel else []
        
        root = etree.Element("root")
        contentNode = self.createContentNode()
        
        for i in range(0,len(self.po.l1Srt)):
            l1Paragraph = self.po.l1Srt[i]
            
            if l1Paragraph is None:
                continue
            
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
            
            terms = self.splitIntoTerms(l1Paragraph.content)
                
            for term in terms:
                termNode = self.createTermNode(term, fragments)
                
                if termNode is not None:
                    l1ParagraphNode.append(termNode)
                
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
            
        theme = ""
        if not StringUtil.isEmpty(self.pi.language1.theme):
            theme = self.pi.language1.theme + "_watching.css"
                
        joined = os.path.join(Application.path, os.path.join("resources", theme))
        if StringUtil.isEmpty(theme) or not os.path.exists(joined):
                theme = "watching.css"
                    
        logging.debug("Using css: %s" % theme)
        
        self.po.html = htmlContent \
                        .replace("<!-- table -->", str(self.applyTransform(root))) \
                        .replace('<!-- theme -->', theme) \
                        .replace('<!-- plugins -->', "<script src=\"<!-- webapi -->/resource/v1/plugins/" + str(self.pi.language1.languageId) + "\"></script>") \
                        .replace("<!-- webapi -->", Application.apiServer)
                        
        self.po.html = re.sub("span>\s+<span", "span><span", self.po.html)
        
        return self.po