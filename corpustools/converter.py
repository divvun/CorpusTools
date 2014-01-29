# -*- coding: utf-8 -*-

#
#   This file contains routines to convert files to the giellatekno xml
#   format.
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this file. If not, see <http://www.gnu.org/licenses/>.
#
#   Copyright 2012-2014 Børre Gaup <borre.gaup@uit.no>
#

import os
import sys
import lxml.etree as etree
import re
import io
import subprocess
import bs4
import HTMLParser
from pyth.plugins.rtf15.reader import Rtf15Reader
from pyth.plugins.xhtml.writer import XHTMLWriter
from copy import deepcopy
import distutils.dep_util
import tidylib
import codecs
import multiprocessing
import argparse
import shutil

import decode
import ngram
import errormarkup


class ConversionException(Exception):
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


class Converter:
    """
    Class to take care of data common to all Converter classes
    """
    def __init__(self, filename, test=False):
        self.orig = os.path.abspath(filename)
        self.setCorpusdir()
        self.setConvertedName()
        self.dependencies = [self.getOrig(), self.getXsl()]
        self.test = test
        self.fixLangGenreXsl()

    def makeIntermediate(self):
        """Convert the input file from the original format to a basic
        giellatekno xml document
        """
        if 'Avvir' in self.orig:
            intermediate = AvvirConverter(self.orig)

        elif self.orig.endswith('.txt'):
            intermediate = PlaintextConverter(self.orig)

        elif self.orig.endswith('.pdf'):
            intermediate = PDFConverter(self.orig)

        elif self.orig.endswith('.svg'):
            intermediate = SVGConverter(self.orig)

        elif '.htm' in self.orig or '.php' in self.orig:
            intermediate = HTMLConverter(self.orig)

        elif '.doc' in self.orig or '.DOC' in self.orig:
            intermediate = DocConverter(self.orig)

        elif '.rtf' in self.orig:
            intermediate = RTFConverter(self.orig)

        elif self.orig.endswith('.bible.xml'):
            intermediate = BiblexmlConverter(self.orig)

        else:
            raise ConversionException("Not able to convert " + self.orig)

        document = intermediate.convert2intermediate()

        if isinstance(document, etree._XSLTResultTree):
            document = etree.fromstring(etree.tostring(document))

        return document

    def makeComplete(self):
        """Combine the intermediate giellatekno xml file and the metadata into
        a complete giellatekno xml file.
        Fix the character encoding
        Detect the languages in the xml file
        """
        xm = XslMaker(self.getXsl())
        xsltRoot = xm.getXsl()
        try:
            transform = etree.XSLT(xsltRoot)
        except etree.XSLTParseError as (e):
            logfile = open(self.orig + '.log', 'w')

            for entry in e.error_log:
                logfile.write(str(entry))
                logfile.write('\n')

            logfile.close()
            raise ConversionException("Invalid XML in " + self.getXsl())

        intermediate = self.makeIntermediate()

        try:
            complete = transform(intermediate)
        except etree.XSLTApplyError as (e):
            logfile = open(self.orig + '.log', 'w')

            for entry in e.error_log:
                logfile.write(str(entry))
                logfile.write('\n')

            logfile.close()
            raise ConversionException("Check the syntax in: " + self.getXsl())

        dtd = etree.DTD(os.path.join(os.getenv('GTHOME'), 'gt/dtd/corpus.dtd'))

        if not dtd.validate(complete):
            #print etree.tostring(complete)
            logfile = open(self.getOrig() + '.log', 'w')

            for entry in dtd.error_log:
                logfile.write('\n')
                logfile.write(str(entry))
                logfile.write('\n')

            logfile.write(etree.tostring(complete,
                                         encoding='utf8',
                                         pretty_print=True))
            logfile.close()

            raise ConversionException(
                "Not valid XML. More info in the log file: " +
                self.getOrig() + u".log")

        if 'correct.' in self.orig:
            try:
                em = errormarkup.ErrorMarkup(self.getOrig())

                for element in complete.find('body'):
                    em.addErrorMarkup(element)
            except IndexError as e:
                logfile = open(self.getOrig() + '.log', 'w')
                logfile.write("There is a markup error\n")
                logfile.write("The error message: ")
                logfile.write(str(e))
                logfile.write("\n\n")
                logfile.write("This is the xml tree:\n")
                logfile.write(etree.tostring(complete,
                                             encoding='utf8',
                                             pretty_print=True))
                logfile.write('\n')
                logfile.close()
                raise ConversionException(
                    u"Markup error. More info in the log file: " +
                    self.getOrig() + u".log")

        if (complete.getroot().
            attrib['{http://www.w3.org/XML/1998/namespace}lang'] in
                ['sma', 'sme']):
            ef = DocumentFixer(etree.fromstring(etree.tostring(complete)))
            complete = ef.fixBodyEncoding()

        ld = LanguageDetector(complete)
        ld.detectLanguage()

        return complete

    def writeComplete(self):
        if distutils.dep_util.newer_group(
                self.dependencies, self.getConvertedName()):
            self.makedirs()

            if (('goldstandard' in self.orig and '.correct.' in self.orig) or
                    'goldstandard' not in self.orig):
                complete = self.makeComplete()

                converted = open(self.getConvertedName(), 'w')
                converted.write(etree.tostring(complete,
                                               encoding='utf8',
                                               pretty_print='True'))
                converted.close()

    def makedirs(self):
        """Make the converted directory
        """
        try:
            os.makedirs(os.path.dirname(self.getConvertedName()))
        except OSError:
            pass

    def getOrig(self):
        return self.orig

    def getXsl(self):
        return self.orig + '.xsl'

    def getTest(self):
        return self.test

    def getTmpdir(self):
        return os.path.join(self.getCorpusdir(), 'tmp')

    def getCorpusdir(self):
        return self.corpusdir

    def setCorpusdir(self):
        origPos = self.orig.find('orig/')
        if origPos != -1:
            self.corpusdir = os.path.dirname(self.orig[:origPos])
        else:
            self.corpusdir = os.getcwd()

    def fixLangGenreXsl(self):
        """Set the mainlang and genre variables in the xsl file, if possible
        """
        try:
            transform = u'{http://www.w3.org/1999/XSL/Transform}'
            mainlang = u'variable[@name="mainlang"]'
            xslgenre = 'variable[@name="genre"]'
            xsltree = etree.parse(self.getXsl())

            root = xsltree.getroot()
            origname = self.getOrig().replace(self.getCorpusdir(), '')
            if origname.startswith('/orig'):
                parts = origname[1:].split('/')

                lang = root.find(transform +
                                 mainlang).attrib['select'].replace("'", "")

                if lang == "":
                    lang = parts[1]
                    root.find(transform +
                              mainlang).attrib['select'] = "'" + lang + "'"

                genre = root.find(transform +
                                  xslgenre).attrib['select'].replace("'", "")

                if genre == "" or genre not in ['admin', 'bible', 'facta',
                                                'ficti', 'news']:
                    if parts[2] in ['admin', 'bible', 'facta', 'ficti',
                                    'news']:
                        genre = parts[parts.index('orig') + 2]
                        root.find(transform +
                                  xslgenre).attrib['select'] = "'" + genre + "'"

                xsltree.write(
                    self.getXsl(), encoding="utf-8", xml_declaration=True)
        except etree.XMLSyntaxError as e:
            logfile = open(self.orig + '.log', 'w')

            for entry in e.error_log:
                logfile.write('\n')
                logfile.write(str(entry.line))
                logfile.write(':')
                logfile.write(str(entry.column))
                logfile.write(" ")

                try:
                    logfile.write(entry.message)
                except ValueError:
                    logfile.write(entry.message.encode('latin1'))

                logfile.write('\n')

    def setConvertedName(self):
        """Set the name of the converted file
        """
        convertedBasename = os.path.join(self.getCorpusdir(), 'converted')
        origname = self.getOrig().replace(self.getCorpusdir(), '')
        if origname.startswith('/'):
            origname = origname[1:]
        if origname.startswith('orig/'):
            origname = origname.replace('orig/', '')
        else:
            origname = os.path.basename(origname)

        self._convertedName = os.path.join(convertedBasename,
                                           origname) + '.xml'

    def getConvertedName(self):
        return self._convertedName


class AvvirConverter:
    """
    Class to convert Ávvir xml files to the giellatekno xml format
    """

    def __init__(self, filename):
        self.orig = filename
        self.converterXsl = os.path.join(
            os.getenv('GTHOME'), 'gt/script/corpus/avvir2corpus.xsl')

    def convert2intermediate(self):
        """
        Convert the original document to the giellatekno xml format, with no
        metadata
        The resulting xml is stored in intermediate
        """
        avvirXsltRoot = etree.parse(self.converterXsl)
        transform = etree.XSLT(avvirXsltRoot)
        doc = etree.parse(self.orig)
        intermediate = transform(doc)

        return intermediate


class SVGConverter:
    """
    Class to convert SVG files to the giellatekno xml format
    """

    def __init__(self, filename):
        self.orig = filename
        self.converterXsl = os.path.join(
            os.getenv('GTHOME'), 'gt/script/corpus/svg2corpus.xsl')

    def convert2intermediate(self):
        """
        Convert the original document to the giellatekno xml format, with no
        metadata
        The resulting xml is stored in intermediate
        """
        svgXsltRoot = etree.parse(self.converterXsl)
        transform = etree.XSLT(svgXsltRoot)
        doc = etree.parse(self.orig)
        intermediate = transform(doc)

        return intermediate


class PlaintextConverter:
    """
    A class to convert plain text files containing "news" tags to the
    giellatekno xml format
    """

    def __init__(self, filename):
        self.orig = filename

    def toUnicode(self):
        """
        Read a file into a unicode string.
        If the content of the file is not utf-8, pretend the encoding is
        latin1. The real encoding (for sma, sme and smj) will be detected
        later.

        Return a unicode string
        """
        try:
            content = codecs.open(self.orig, encoding='utf8').read()
        except:
            content = codecs.open(self.orig, encoding='latin1').read()

        content = content.replace(u'ÊÊ', '\n\n')
        content = content.replace(u'<\!q>', u' ')
        content = content.replace('\x0d', '\x0a')
        content = content.replace('<*B>', '')
        content = content.replace('<*P>', '')
        content = content.replace('<*I>', '')
        content = self.strip_chars(content)

        return content

    def strip_chars(self, content, extra=u''):
        remove_re = re.compile(
            u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F%s]' % extra)
        content, count = remove_re.subn('', content)

        return content

    def makeElement(self, eName, text, attributes={}):
        """
        @brief Makes an xml element containing the given name, text and
        attributes. Adds a hyph element if necessary.

        :param eName: Name of the xml element
        :type el: string

        :param text: The text the xml should contain
        :type text: string

        :param attributes: The attributes the element should have
        :type attributes: dict

        :returns: lxml.etree.Element
        """
        el = etree.Element(eName)
        for key in attributes:
            el.set(key, attributes[key])

        hyphParts = text.split('<hyph/>')
        if len(hyphParts) > 1:
            el.text = hyphParts[0]
            for hyphPart in hyphParts[1:]:
                h = etree.Element('hyph')
                h.tail = hyphPart
                el.append(h)
        else:
            el.text = text

        return el

    def convert2intermediate(self):
        document = etree.Element('document')

        content = io.StringIO(self.toUnicode())
        header = etree.Element('header')
        body = etree.Element('body')
        ptext = ''

        newstags = re.compile(r'(@*logo:|@*ingres+:|.*@*bilde(\s\d)*:|(@|LED)*tekst:|@*stikk:|@foto:|@fotobyline:|@bildetitt:)', re.IGNORECASE)
        titletags = re.compile(r'@m.titt:@ingress:|Mellomtittel:|@*(stikk|under)titt:|@ttt:|@*[utm]*[:\.]*tit+:', re.IGNORECASE)
        headertitletags = re.compile(r'@tittel:|@titt:|TITT:|Tittel:|@LEDtitt:')

        for line in content:
            if newstags.match(line):
                line = newstags.sub('', line).strip()
                body.append(self.makeElement('p', line))
                ptext = ''
            elif line.startswith('@bold:'):
                line = line.replace('@bold:', '').strip()
                p = etree.Element('p')
                p.append(self.makeElement('em', line, {'type': 'bold'}))
                body.append(p)
                ptext = ''
            elif line.startswith('@kursiv:'):
                line = line.replace('@kursiv:', '').strip()
                p = etree.Element('p')
                p.append(self.makeElement('em', line, {'type': 'italic'}))
                body.append(p)
                ptext = ''
            elif line.startswith(u'  '):
                body.append(self.makeElement('p', line.strip()))
                ptext = ''
            elif headertitletags.match(line):
                line = headertitletags.sub('', line).strip()
                if header.find("title") is None:
                    header.append(self.makeElement('title', line))
                else:
                    body.append(self.makeElement('p', line, {'type': 'title'}))
                ptext = ''
            elif titletags.match(line):
                line = titletags.sub('', line).strip()
                body.append(self.makeElement('p', line, {'type': 'title'}))
                ptext = ''
            elif line.startswith('@byline:') or line.startswith('Byline:'):
                person = etree.Element('person')

                line = line.replace('@byline:', '').strip()
                line = line.replace('Byline:', '').strip()
                names = line.strip().split(' ')
                person.set('lastname', names[-1])
                person.set('firstname', ' '.join(names[:-1]))

                author = etree.Element('author')
                author.append(person)
                header.append(author)
                ptext = ''
            elif line == '\n' and ptext != '':
                if ptext.strip() != '':
                    try:
                        body.append(self.makeElement('p', ptext.strip()))
                        ptext = ''
                    except ValueError:
                        raise ConversionException(
                            "Invalid utf8 «" +
                            ptext.strip().encode('utf-8') + "»")

                ptext = ''
            else:
                ptext = ptext + line.replace('\n', ' ')

        if ptext != '':
            body.append(self.makeElement('p', ptext.strip()))

        document.append(header)
        document.append(body)

        return document

#from pdfminer.pdfparser import PDFDocument, PDFParser
#from pdfminer.pdfinterp import PDFResourceManager, \
    #PDFPageInterpreter, process_pdf
#from pdfminer.pdfdevice import PDFDevice, TagExtractor
#from pdfminer.converter import TextConverter
#from pdfminer.cmapdb import CMapDB
#from pdfminer.layout import LAParams


class PDFConverter:
    def __init__(self, filename):
        self.orig = filename

    def replaceLigatures(self):
        """
        document is a stringified xml document
        """
        replacements = {
            u"[dstrok]": u"đ",
            u"[Dstrok]": u"Đ",
            u"[tstrok]": u"ŧ",
            u"[Tstrok]": u"Ŧ",
            u"[scaron]": u"š",
            u"[Scaron]": u"Š",
            u"[zcaron]": u"ž",
            u"[Zcaron]": u"Ž",
            u"[ccaron]": u"č",
            u"[Ccaron]": u"Č",
            u"[eng": u"ŋ",
            " ]": "",
            u"Ď": u"đ",  # cough
            u"ď": u"đ",  # cough
            u"ﬁ": "fi",
            u"ﬂ": "fl",
            u"ﬀ": "ff",
            u"ﬃ": "ffi",
            u"ﬄ": "ffl",
            u"ﬅ": "ft",
        }

        for key, value in replacements.items():
            #print '583', key, value
            self.text = self.text.replace(key + ' ', value)
            self.text = self.text.replace(key, value)

    def extractText(self):
        """
        Extract the text from the pdf file using pdftotext
        output contains string from the program and is a utf-8 string
        """
        subp = subprocess.Popen(
            ['pdftotext', '-enc', 'UTF-8', '-nopgbrk', '-eol',
             'unix', self.orig, '-'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        (output, error) = subp.communicate()

        if subp.returncode != 0:
            logfile = open(self.orig + '.log', 'w')
            logfile.write('stdout\n')
            logfile.write(output)
            logfile.write('\n')
            logfile.write('stderr\n')
            logfile.write(error)
            logfile.write('\n')
            logfile.close()
            raise ConversionException("Could not extract text from pdf. \
                More info in the log file: " + self.orig + u".log")

        self.text = unicode(output, encoding='utf8')
        self.replaceLigatures()
        return self.strip_chars(self.text)

    def strip_chars(self, content, extra=u''):
        remove_re = re.compile(u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F%s]' % extra)
        content, count = remove_re.subn('', content)

        return content

    #def extractText1(self):
        ## debug option
        #debug = 0
        ## input option
        #pagenos = set()
        #maxpages = 0
        ## output option
        #codec = 'utf-8'
        #caching = True
        #laparams = LAParams()

        #PDFDocument.debug = debug
        #PDFParser.debug = debug
        #CMapDB.debug = debug
        #PDFResourceManager.debug = debug
        #PDFPageInterpreter.debug = debug
        #PDFDevice.debug = debug
        ##
        #rsrcmgr = PDFResourceManager(caching=caching)

        #outfp = cStringIO.StringIO()

        #device = TextConverter(rsrcmgr, outfp, codec=codec, laparams=laparams)

        #fp = file(self.orig, 'rb')
        #process_pdf(rsrcmgr, device, fp, pagenos, maxpages=maxpages,
                    #caching=caching, check_extractable=True)
        #fp.close()

        #device.close()
        #self.text = unicode(outfp.getvalue(), encoding='utf8')
        #self.replaceLigatures()
        #outfp.close()

        #return self.text

    def convert2intermediate(self):
        document = etree.Element('document')
        header = etree.Element('header')
        body = etree.Element('body')

        content = io.StringIO(self.extractText())
        ptext = ''

        for line in content:
            if line == '\n':
                p = etree.Element('p')
                p.text = ptext
                body.append(p)
                ptext = ''
            else:
                ptext = ptext + line

        if ptext != '':
            p = etree.Element('p')
            p.text = ptext.replace('\x0c', '')
            body.append(p)

        document.append(header)
        document.append(body)

        return document


class DocConverter:
    """
    Class to convert Microsoft Word documents to the giellatekno xml format
    """
    def __init__(self, filename):
        self.orig = filename
        self.converterXsl = os.path.join(
            os.getenv('GTHOME'), 'gt/script/corpus/docbook2corpus2.xsl')

    def extractText(self):
        """Extract the text from the doc file using antiword
        output contains the docbook xml output by antiword,
        and is a utf-8 string
        """
        subp = subprocess.Popen(
            ['antiword', '-x', 'db', self.orig],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        (output, error) = subp.communicate()

        if subp.returncode != 0:
            print >>sys.stderr, 'Could not process', self.orig
            print >>sys.stderr, output
            print >>sys.stderr, error
            return subp.returncode

        return output

    def convert2intermediate(self):
        """Convert the original document to the giellatekno xml format,
        with no metadata
        The resulting xml is stored in intermediate
        """
        docbookXsltRoot = etree.parse(self.converterXsl)
        transform = etree.XSLT(docbookXsltRoot)
        doc = etree.fromstring(self.extractText())
        intermediate = transform(doc)

        return intermediate


class BiblexmlConverter:
    """
    Class to convert bible xml files to the giellatekno xml format
    """
    def __init__(self, filename):
        self.orig = filename

    def convert2intermediate(self):
        """
        Convert the bible xml to giellatekno xml format using bible2xml.pl
        """
        subp = subprocess.Popen(
            ['bible2xml.pl', '-out', 'kluff.xml', self.orig],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        (output, error) = subp.communicate()

        if subp.returncode != 0:
            print >>sys.stderr, 'Could not process', self.orig
            print >>sys.stderr, output
            print >>sys.stderr, error
            return subp.returncode

        return etree.parse('kluff.xml')


class HTMLContentConverter:
    """
    Class to convert html documents to the giellatekno xml format
    """
    def __init__(self, filename, content):
        self.orig = filename
        self.content = content

        self.converterXsl = os.path.join(
            os.getenv('GTHOME'), 'gt/script/corpus/xhtml2corpus.xsl')

    def tidy(self):
        """
        Run html through tidy
        """
        try:
            soup = bs4.BeautifulSoup(self.content)
        except HTMLParser.HTMLParseError:
            raise ConversionException("BeautifulSoup couldn't parse the html")

        comments = soup.findAll(
            text=lambda text: isinstance(text, bs4.Comment))
        [comment.extract() for comment in comments]

        [item.extract() for item in soup.findAll(
            text=lambda text: isinstance(text, bs4.ProcessingInstruction))]
        [item.extract() for item in soup.findAll(
            text=lambda text: isinstance(text, bs4.Declaration))]

        remove_tags = ['script', 'style', 'o:p', 'st1:country-region',
                       'v:shapetype', 'v:shape', 'st1:metricconverter',
                       'area', 'object', 'meta', 'fb:like', 'fb:comments',
                       'g:plusone']

        for remove_tag in remove_tags:
            removes = soup.findAll(remove_tag)
            for remove in removes:
                remove.extract()

        if not ("xmlns", "http://www.w3.org/1999/xhtml") in soup.html.attrs:
            soup.html["xmlns"] = "http://www.w3.org/1999/xhtml"

        soup = soup.prettify()
        replacements = {'&shy;': u'­',
                        '&nbsp;': ' ',
                        '&aelig;': u'æ',
                        '&eacute;': u'é'}
        for key, value in replacements.iteritems():
            soup = soup.replace(key, value)

        tidyOption = {"indent": "auto",
                      "indent-spaces": 2,
                      "wrap": 72,
                      "markup": "yes",
                      "output-xml": "yes",
                      "add-xml-decl": "yes",
                      "input-xml": "no",
                      "show-warnings": "no",
                      "numeric-entities": "yes",
                      "quote-marks": "yes",
                      "quote-nbsp": "yes",
                      "quote-ampersand": "yes",
                      "break-before-br": "no",
                      "uppercase-tags": "no",
                      "uppercase-attributes": "no",
                      "char-encoding": "utf8",
                      "enclose-block-text": "yes",
                      "new-empty-tags": "ms,mb,nf,mu",
                      "new-inline-tags": "dato,note,idiv,o:p,pb,v:shapetype,\
                          v:stroke,v:formulas,v:f,v:path,v:shape,v:imagedata,\
                          o:lock,st1:country-region,st1:place,\
                          st1:metricconverter,g:plusone,fb:like,fb:comments",
                      "new-blocklevel-tags": "label,nav,article,header,\
                          figcaption,time,aside,figure,footer",
                      "clean": "true",
                      "drop-proprietary-attributes": "true",
                      "drop-empty-paras": "true"
                      }

        tidiedHtml, errors = tidylib.tidy_document(soup, tidyOption)

        #sys.stderr.write(str(lineno()) + ' ' +  soup.prettify())
        return tidiedHtml

    def convert2intermediate(self):
        """
        Convert the original document to the giellatekno xml format, with no
        metadata
        The resulting xml is stored in intermediate
        """
        #print docbook
        htmlXsltRoot = etree.parse(self.converterXsl)
        transform = etree.XSLT(htmlXsltRoot)

        intermediate = ''

        html = self.tidy()
        try:
            doc = etree.fromstring(html)
            intermediate = transform(doc)
        except etree.XMLSyntaxError as e:
            logfile = open(self.orig + '.log', 'w')

            for entry in e.error_log:
                logfile.write('\n')
                logfile.write(str(entry.line))
                logfile.write(':')
                logfile.write(str(entry.column))
                logfile.write(" ")

                try:
                    logfile.write(entry.message)
                except ValueError:
                    logfile.write(entry.message.encode('latin1'))

                logfile.write('\n')

            # html is unicode, encode it as utf8 before writing it
            logfile.write(html.encode('utf8'))
            logfile.close()
            raise ConversionException(
                "Invalid html, log is found in " + self.orig + '.log')

        if len(transform.error_log) > 0:

            logfile = open(self.orig + '.log', 'w')

            for entry in transform.error_log:
                logfile.write('\n')
                logfile.write(str(entry.line))
                logfile.write(':')
                logfile.write(str(entry.column))
                logfile.write(" ")

                try:
                    logfile.write(entry.message)
                except ValueError:
                    logfile.write(entry.message.encode('latin1'))

                logfile.write('\n')

            logfile.write(html.encode('utf8'))
            logfile.close()
            raise ConversionException(
                'transformation failed' + self.orig + '.log')

        return intermediate


class HTMLConverter(HTMLContentConverter):
    def __init__(self, filename):
        f = open(filename)
        HTMLContentConverter.__init__(self, filename, f.read())
        f.close()


class RTFConverter(HTMLContentConverter):
    """
    Class to convert html documents to the giellatekno xml format
    """
    def __init__(self, filename):
        self.orig = filename
        HTMLContentConverter.__init__(self, filename, self.rtf2html())

    def rtf2html(self):
        """Open the rtf document
        Turn it into an html snippet (which starts with a div)
        Change the div tag to body
        Append the body to an html element
        """
        doc = open(self.orig, "rb")
        content = doc.read()
        doc = Rtf15Reader.read(
            io.BytesIO(content.replace('fcharset256', 'fcharset255')))
        html = XHTMLWriter.write(doc, pretty=True).read()
        xml = etree.fromstring(html)
        xml.tag = 'body'
        htmlElement = etree.Element('html')
        htmlElement.append(xml)
        return etree.tostring(htmlElement)


class DocumentFixer:
    """
    Receive a stringified etree from one of the raw converters,
    replace ligatures, fix the encoding and return an etree with correct
    characters
    """
    def __init__(self, document):
        self.etree = document

    def replaceLigatures(self):
        """
        document is a stringified xml document
        """
        replacements = {
            u"[dstrok]": u"đ",
            u"[Dstrok]": u"Đ",
            u"[tstrok]": u"ŧ",
            u"[Tstrok]": u"Ŧ",
            u"[scaron]": u"š",
            u"[Scaron]": u"Š",
            u"[zcaron]": u"ž",
            u"[Zcaron]": u"Ž",
            u"[ccaron]": u"č",
            u"[Ccaron]": u"Č",
            u"[eng": u"ŋ",
            " ]": "",
            u"Ď": u"đ",  # cough
            u"ď": u"đ",  # cough
            "\x03": "",
            "\x04": "",
            "\x07": "",
            "\x08": "",
            "\x0F": "",
            "\x10": "",
            "\x11": "",
            "\x13": "",
            "\x14": "",
            "\x15": "",
            "\x17": "",
            "\x18": "",
            "\x1A": "",
            "\x1B": "",
            "\x1C": "",
            "\x1D": "",
            "\x1E": "",
            u"ﬁ": "fi",
            u"ﬂ": "fl",
            u"ﬀ": "ff",
            u"ﬃ": "ffi",
            u"ﬄ": "ffl",
            u"ﬅ": "ft",
        }

        for element in self.etree.iter('p'):
            if element.text:
                for key, value in replacements.items():
                    element.text = element.text.replace(key + ' ', value)
                    element.text = element.text.replace(key, value)

    def fixBodyEncoding(self):
        """
        Send a stringified version of the body into the EncodingGuesser class.
        It returns the same version, but with fixed characters.
        Parse the returned string, insert it into the document
        """
        self.replaceLigatures()

        if isinstance(self.etree, etree._XSLTResultTree):
            sys.stderr.write("xslt!\n")

        body = self.etree.find('body')
        bodyString = etree.tostring(body, encoding='utf-8')
        body.getparent().remove(body)

        eg = decode.EncodingGuesser()
        encoding = eg.guess_body_encoding(bodyString)

        body = etree.fromstring(eg.decode_para(encoding, bodyString))
        self.etree.append(body)

        self.detectQuotes()

        return etree.parse(io.BytesIO(etree.tostring(self.etree)))

    def detectQuote(self, element):
        """Detect quotes in an etree element.
        """
        newelement = deepcopy(element)

        element.text = ''
        for child in element:
            child.getparent().remove(child)

        quoteList = []
        quoteRegexes = [re.compile('".+?"'),
                        re.compile(u'«.+?»'),
                        re.compile(u'“.+?”')]

        text = newelement.text
        if text:
            for quoteRegex in quoteRegexes:
                for m in quoteRegex.finditer(text):
                    quoteList.append(m.span())

            if len(quoteList) > 0:
                quoteList.sort()
                element.text = text[0:quoteList[0][0]]

                for x in range(0, len(quoteList)):
                    span = etree.Element('span')
                    span.set('type', 'quote')
                    span.text = text[quoteList[x][0]:quoteList[x][1]]
                    if x + 1 < len(quoteList):
                        span.tail = text[quoteList[x][1]:quoteList[x + 1][0]]
                    else:
                        span.tail = text[quoteList[x][1]:]
                    element.append(span)
            else:
                element.text = text

        for child in newelement:
            element.append(self.detectQuote(child))

            if child.tail:
                quoteList = []
                text = child.tail

                for quoteRegex in quoteRegexes:
                    for m in quoteRegex.finditer(text):
                        quoteList.append(m.span())

                if len(quoteList) > 0:
                    quoteList.sort()
                    child.tail = text[0:quoteList[0][0]]

                for x in range(0, len(quoteList)):
                    span = etree.Element('span')
                    span.set('type', 'quote')
                    span.text = text[quoteList[x][0]:quoteList[x][1]]
                    if x + 1 < len(quoteList):
                        span.tail = text[quoteList[x][1]:quoteList[x + 1][0]]
                    else:
                        span.tail = text[quoteList[x][1]:]
                    element.append(span)

        return element

    def detectQuotes(self):
        """Detect quotes in all paragraphs
        """
        for paragraph in self.etree.iter('p'):
            paragraph = self.detectQuote(paragraph)

    def setWordCount(self):
        """Count the words in the file
        """
        plist = []
        for paragraph in self.etree.iter('p'):
            plist.append(etree.tostring(paragraph,
                                        method='text',
                                        encoding='utf8'))

        words = len(re.findall(r'\S+', ' '.join(plist)))

        wordcount = self.etree.find('header/wordcount')
        if wordcount is None:
            tags = ['collection', 'publChannel', 'place', 'year',
                    'translated_from', 'translator', 'author']
            for tag in tags:
                found = self.etree.find('header/' + tag)
                if found is not None:
                    wordcount = etree.Element('wordcount')
                    header = found.getparent()
                    header.insert(header.index(found) + 1, wordcount)
                    break

        wordcount.text = str(words)


class XslMaker:
    """
    To convert the intermediate xml to a fullfledged  giellatekno document
    a combination of three xsl files + the intermediate files is needed
    This class makes the xsl file
    """

    def __init__(self, xslfile):
        preprocessXsl = etree.parse(
            os.path.join(os.getenv('GTHOME'),
                         'gt/script/corpus/preprocxsl.xsl'))
        preprocessXslTransformer = etree.XSLT(preprocessXsl)

        self.filename = xslfile
        try:
            filexsl = etree.parse(xslfile)
        except etree.XMLSyntaxError as e:
            logfile = open(self.filename + '.log', 'w')

            for entry in e.error_log:
                logfile.write(str(entry))
                logfile.write('\n')

            logfile.close()
            raise ConversionException("Syntax error in " + self.filename)

        self.finalXsl = preprocessXslTransformer(
            filexsl,
            commonxsl=
            etree.XSLT.strparam('file://' +
                                os.path.join(os.getenv('GTHOME'),
                                             'gt/script/corpus/common.xsl')))

    def getXsl(self):
        return self.finalXsl


class LanguageDetector:
    """
    Receive an etree.
    Detect the languages of quotes.
    Detect the languages of the paragraphs.
    """
    def __init__(self, document):
        self.document = document
        self.mainlang = self.document.getroot().\
            attrib['{http://www.w3.org/XML/1998/namespace}lang']

        inlangs = []
        for language in self.document.findall('header/multilingual/language'):
            inlangs.append(
                language.get('{http://www.w3.org/XML/1998/namespace}lang'))
        if len(inlangs) != 0:
            if self.mainlang != '':
                inlangs.append(self.mainlang)
            else:
                raise ConversionException('mainlang not set')

        self.languageGuesser = ngram.NGram(
            os.path.join(os.getenv('GTHOME'), 'tools/lang-guesser/LM/'),
            langs=inlangs)

    def getDocument(self):
        return self.document

    def getMainlang(self):
        """
        Get the mainlang of the file
        """
        return self.mainlang

    def setParagraphLanguage(self, paragraph):
        """Extract the text outside the quotes, use this text to set
        language of the paragraph.
        Set the language of the quotes in the paragraph
        """
        paragraphText = self.removeQuote(paragraph)
        lang = self.languageGuesser.classify(
            paragraphText.encode("ascii", "ignore"))
        if lang != self.getMainlang():
            paragraph.set('{http://www.w3.org/XML/1998/namespace}lang', lang)

        for element in paragraph.iter("span"):
            if element.get("type") == "quote":
                lang = self.languageGuesser.classify(
                    element.text.encode("ascii", "ignore"))
                if lang != self.getMainlang():
                    element.set(
                        '{http://www.w3.org/XML/1998/namespace}lang', lang)

        return paragraph

    def removeQuote(self, paragraph):
        """Extract all text except the one inside <span type='quote'>"""
        text = ''
        for element in paragraph.iter():
            if (element.tag == 'span' and
                    element.get('type') == 'quote' and
                    element.tail is not None):
                text = text + element.tail
            else:
                if element.text is not None:
                    text = text + element.text
                if element.tail is not None:
                    text = text + element.tail

        return text

    def detectLanguage(self):
        """Detect language in all the paragraphs in self.document
        """
        if self.document.find('header/multilingual') is not None:
            for paragraph in self.document.iter('p'):
                paragraph = self.setParagraphLanguage(paragraph)


class DocumentTester:
    def __init__(self, document):
        self.document = document
        self.mainlang = self.document.getroot().\
            attrib['{http://www.w3.org/XML/1998/namespace}lang']
        self.removeForeignLanguage()

    def getMainlang(self):
        """
        Get the mainlang of the file
        """
        return self.mainlang

    def getMainlangWordcount(self):
        return len(re.findall(r'\S+', self.getMainlangWords()))

    def getUnknownWordsRatio(self):
        return 1.0 * self.getUnknownWordcount() / self.getMainlangWordcount()

    def getMainlangRatio(self):
        return 1.0 * self.getMainlangWordcount() / float(
            self.document.find('header/wordcount').text)

    def removeForeignLanguage(self):
        """Remove text mark as not belonging to mainlang
        First remove foreign language in quotes
        Then look for paragraphs with foreign language
        If they contain quotes in the original language, set that as the text
        of the paragraph and remove the xml:lang attribute
        If it contains only foreign text, remove the whole paragraph
        """

        for span in self.document.xpath('//span[@xml:lang]'):
            span.text = ''

        hit = False

        for paragraph in self.document.xpath('//p[@xml:lang]'):
            paragraph.text = ''
            for span in paragraph.xpath('//span[@type="quote"]'):
                if span.get('xml:lang') is None:
                    hit = True
                    paragraph.text = paragraph.text + span.text
                span.getparent().remove(span)

            if not hit:
                paragraph.getparent().remove(paragraph)
            else:
                del paragraph.\
                    attrib['{http://www.w3.org/XML/1998/namespace}lang']

    def getUnknownWordcount(self):
        lookupCommand = ['lookup', '-flags', 'mbTT']
        if self.getMainlang() == 'sme':
            lookupCommand.append(os.getenv('GTHOME') +
                                 '/gt/' +
                                 self.getMainlang() +
                                 '/bin/' +
                                 self.getMainlang() +
                                 '.fst')
        else:
            lookupCommand.append(
                os.getenv('GTHOME') +
                '/langs/' +
                self.getMainlang() +
                '/src/analyser-gt-desc.xfst')

        subp = subprocess.Popen(lookupCommand,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        (output, error) = subp.communicate(self.getPreprocessedMainlangWords())

        if subp.returncode != 0:
            print >>sys.stderr, 'Could not lookup text'
            print >>sys.stderr, output
            raise ConversionException(error)
        else:
            count = 0
            for line in output.split():
                if '+?' in line:
                    count += 1

            return count

    def getPreprocessedMainlangWords(self):
        """Send the text into preprocess, return the result.
        If the process fails, exit the program
        """
        preprocessCommand = []
        if self.getMainlang() == 'sme':
            abbrFile = os.path.join(
                os.environ['GTHOME'], 'gt/sme/bin/abbr.txt')
            corrFile = os.path.join(
                os.environ['GTHOME'], 'gt/sme/bin/corr.txt')
            preprocessCommand = ['preprocess',
                                 '--abbr=' + abbrFile, '--corr=' + corrFile]
        else:
            preprocessCommand = ['preprocess']

        subp = subprocess.Popen(preprocessCommand,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        (output, error) = subp.communicate(
            self.getMainlangWords().replace('\n', ' '))

        if subp.returncode != 0:
            print >>sys.stderr, output
            print >>sys.stderr, error
            raise ConversionException('Could not preprocess text')
        else:
            return output

    def getMainlangWords(self):
        plist = []
        for paragraph in self.document.iter('p'):
            plist.append(
                etree.tostring(paragraph, method='text', encoding='utf8'))

        return ' '.join(plist)


def parse_options():
    parser = argparse.ArgumentParser(
        description='Convert original files to giellatekno xml, using \
        dependency checking.')
    parser.add_argument(u'--debug',
                        action=u"store_true",
                        help=u"use this for debugging the conversion \
                        process. When this argument is used files will \
                        be converted one by one.")
    parser.add_argument('orig_dir',
                        help="directory where the original files exist")

    args = parser.parse_args()
    return args


def worker(xsl_file):
    conv = Converter(xsl_file[:-4])

    # The clause below made because of this bug in python 2.7
    # http://www.gossamer-threads.com/lists/python/bugs/1025933
    try:
        conv.writeComplete()
    except Exception as e:
        raise RuntimeError

def convert_in_parallel(xsl_files):
    pool_size = multiprocessing.cpu_count() * 2
    pool = multiprocessing.Pool(processes=pool_size,)
    pool.map(worker, xsl_files)
    pool.close()
    pool.join()

def convert_serially(xsl_files):
    for xsl_file in xsl_files:
        conv = Converter(xsl_file[:-4])
        try:
            conv.writeComplete()
        except ConversionException:
            print >>sys.stderr, 'Could not convert', xsl_file[:-4]

def main():
    args = parse_options()
    xsl_files = []

    if os.path.isfile(args.orig_dir):
        xsl_file = args.orig_dir + '.xsl'
        if os.path.isfile(xsl_file):
            worker(xsl_file)
        else:
            shutil.copy(
                os.path.join(os.getenv('GTHOME'),
                             'gt/script/corpus/XSL-template.xsl'),
                xsl_file)
            print "Fill in meta info in", xsl_file, \
                ', then run this command again'
            sys.exit(1)
    elif os.path.isdir(args.orig_dir):
        for root, dirs, files in os.walk(args.orig_dir):
            for f in files:
                if f.endswith('.xsl'):
                    xsl_files.append(os.path.join(root, f))

        if args.debug:
            convert_serially(xsl_files)
        else:
            try:
                convert_in_parallel(xsl_files)
            except RuntimeError as e:
                pass
