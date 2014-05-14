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
from pkg_resources import resource_string, resource_filename

import decode
import ngram
import errormarkup
from corpustools import ccat


class ConversionException(Exception):
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


class Converter(object):
    """
    Class to take care of data common to all Converter classes
    """
    def __init__(self, filename, test=False):
        self.orig = os.path.abspath(filename)
        self.set_corpusdir()
        self.set_converted_name()
        self.dependencies = [self.get_orig(), self.get_xsl()]
        self.test = test
        self.fix_lang_genre_xsl()

    def make_intermediate(self):
        """Convert the input file from the original format to a basic
        giellatekno xml document
        """
        if 'Avvir_xml' in self.orig:
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

    def make_complete(self):
        """Combine the intermediate giellatekno xml file and the metadata into
        a complete giellatekno xml file.
        Fix the character encoding
        Detect the languages in the xml file
        """
        xm = XslMaker(self.get_xsl())
        xsltRoot = xm.get_xsl()
        try:
            transform = etree.XSLT(xsltRoot)
        except etree.XSLTParseError as (e):
            logfile = open(self.orig + '.log', 'w')

            logfile.write('Error at: ' + str(ccat.lineno()))
            for entry in e.error_log:
                logfile.write(str(entry))
                logfile.write('\n')

            logfile.close()
            raise ConversionException("Invalid XML in " + self.get_xsl())

        intermediate = self.make_intermediate()

        try:
            complete = transform(intermediate)
        except etree.XSLTApplyError as (e):
            logfile = open(self.orig + '.log', 'w')

            logfile.write('Error at: ' + str(ccat.lineno()))
            for entry in e.error_log:
                logfile.write(str(entry))
                logfile.write('\n')

            logfile.close()
            raise ConversionException("Check the syntax in: " + self.get_xsl())

        dtd = etree.DTD(os.path.join(os.getenv('GTHOME'), 'gt/dtd/corpus.dtd'))

        if not dtd.validate(complete):
            #print etree.tostring(complete)
            logfile = open(self.get_orig() + '.log', 'w')

            logfile.write('Error at: ' + str(ccat.lineno()))
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
                self.get_orig() + u".log")

        if 'correct.' in self.orig:
            try:
                em = errormarkup.ErrorMarkup(self.get_orig())

                for element in complete.find('body'):
                    em.add_error_markup(element)
            except IndexError as e:
                logfile = open(self.get_orig() + '.log', 'w')
                logfile.write('Error at: ' + str(ccat.lineno()))
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
                    self.get_orig() + u".log")

        fixer = DocumentFixer(etree.fromstring(etree.tostring(complete)))

        if (complete.getroot().
            attrib['{http://www.w3.org/XML/1998/namespace}lang'] in
                ['sma', 'sme', 'smj', 'nob', 'fin']):
            fixer.fix_body_encoding()

        fixer.soft_hyphen_to_hyph_tag()
        fixer.set_word_count()

        complete = fixer.get_etree()

        ld = LanguageDetector(complete)
        ld.detect_language()

        return complete

    def write_complete(self):
        if distutils.dep_util.newer_group(
                self.dependencies, self.get_converted_name()):
            self.makedirs()

            if (('goldstandard' in self.orig and '.correct.' in self.orig) or
                    'goldstandard' not in self.orig):
                complete = self.make_complete()

                xml_printer = ccat.XMLPrinter(all_paragraphs=True, hyph_replacement=None)
                xml_printer.etree = complete
                text = xml_printer.process_file().getvalue()

                if len(text) > 0:
                    converted = open(self.get_converted_name(), 'w')
                    converted.write(etree.tostring(complete,
                                                encoding='utf8',
                                                pretty_print='True'))
                    converted.close()
                else:
                    print >>sys.stderr, self.orig, "has no text"

    def makedirs(self):
        """Make the converted directory
        """
        try:
            os.makedirs(os.path.dirname(self.get_converted_name()))
        except OSError:
            pass

    def get_orig(self):
        return self.orig

    def get_xsl(self):
        return self.orig + '.xsl'

    def get_test(self):
        return self.test

    def get_tmpdir(self):
        return os.path.join(self.get_corpusdir(), 'tmp')

    def get_corpusdir(self):
        return self.corpusdir

    def set_corpusdir(self):
        orig_pos = self.orig.find('orig/')
        if orig_pos != -1:
            self.corpusdir = os.path.dirname(self.orig[:orig_pos])
        else:
            self.corpusdir = os.getcwd()

    def fix_lang_genre_xsl(self):
        """Set the mainlang and genre variables in the xsl file, if possible
        """
        try:
            transform = u'{http://www.w3.org/1999/XSL/Transform}'
            mainlang = u'variable[@name="mainlang"]'
            xslgenre = 'variable[@name="genre"]'
            xsltree = etree.parse(self.get_xsl())

            root = xsltree.getroot()
            origname = self.get_orig().replace(self.get_corpusdir(), '')
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
                                  xslgenre).attrib['select'] = \
                            "'" + genre + "'"

                xsltree.write(
                    self.get_xsl(), encoding="utf-8", xml_declaration=True)

        except etree.XMLSyntaxError as e:
            logfile = open(self.orig + '.log', 'w')

            logfile.write('Error at: ' + str(ccat.lineno()))
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

    def set_converted_name(self):
        """Set the name of the converted file
        """
        converted_basename = os.path.join(self.get_corpusdir(), 'converted')
        origname = self.get_orig().replace(self.get_corpusdir(), '')
        if origname.startswith('/'):
            origname = origname[1:]
        if origname.startswith('orig/'):
            origname = origname.replace('orig/', '')
        else:
            origname = os.path.basename(origname)

        self._convertedName = os.path.join(converted_basename,
                                           origname) + '.xml'

    def get_converted_name(self):
        return self._convertedName


class AvvirConverter(object):
    """
    Class to convert Ávvir xml files to the giellatekno xml format
    """

    def __init__(self, filename):
        self.orig = filename

    def convert2intermediate(self):
        """
        Convert the original document to the giellatekno xml format, with no
        metadata
        The resulting xml is stored in intermediate
        """
        self.intermediate = etree.fromstring(open(self.orig).read())
        self.convert_p()
        self.convert_story()
        self.convert_article()

        return self.intermediate.getroottree()

    def insert_element(self, p, text, i):
        if text is not None:
            new_p = etree.Element('p')
            new_p.text = text
            grandparent = p.getparent()
            grandparent.insert(grandparent.index(p) + i, new_p)
            i += 1

        return i

    def convert_subelement(self, p):
        i = 1
        for subelement in p:
            i = self.insert_element(p, subelement.text, i)

            for subsubelement in subelement:
                for text in [subsubelement.text, subsubelement.tail]:
                    i = self.insert_element(p, text, i)

            i = self.insert_element(p, subelement.tail, i)

            p.remove(subelement)

    def convert_p(self):
        for p in self.intermediate.findall('.//p'):
            if p.get("class") is not None:
                del p.attrib["class"]

            self.convert_subelement(p)

    def convert_story(self):
        for title in self.intermediate.findall('.//story[@class="Tittel"]'):
            for p in title.findall('./p'):
                p.set('type', 'title')

            del title.attrib['class']
            del title.attrib['id']

            title.tag = 'section'

        for title in self.intermediate.findall('.//story[@class="Undertittel"]'):
            for p in title.findall('./p'):
                p.set('type', 'title')

            del title.attrib['class']
            del title.attrib['id']

            title.tag = 'section'

        for story in self.intermediate.findall('./story'):
            parent = story.getparent()
            i = 1
            for p in story.findall('./p'):
                parent.insert(parent.index(story) + i, p)
                i += 1

            parent.remove(story)

    def convert_article(self):
        self.intermediate.tag = 'body'
        document = etree.Element('document')
        document.append(self.intermediate)
        self.intermediate = document


class SVGConverter(object):
    """
    Class to convert SVG files to the giellatekno xml format
    """

    def __init__(self, filename):
        self.orig = filename
        self.converter_xsl = resource_string(__name__, 'xslt/svg2corpus.xsl')

    def convert2intermediate(self):
        """
        Convert the original document to the giellatekno xml format, with no
        metadata
        The resulting xml is stored in intermediate
        """
        svgXsltRoot = etree.fromstring(self.converter_xsl)
        transform = etree.XSLT(svgXsltRoot)
        doc = etree.parse(self.orig)
        intermediate = transform(doc)

        return intermediate


class PlaintextConverter(object):
    """
    A class to convert plain text files containing "news" tags to the
    giellatekno xml format
    """

    def __init__(self, filename):
        self.orig = filename

    def to_unicode(self):
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

    def make_element(self, eName, text, attributes={}):
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

        hyph_parts = text.split('<hyph/>')
        if len(hyph_parts) > 1:
            el.text = hyph_parts[0]
            for hyph_part in hyph_parts[1:]:
                h = etree.Element('hyph')
                h.tail = hyph_part
                el.append(h)
        else:
            el.text = text

        return el

    def convert2intermediate(self):
        document = etree.Element('document')

        content = io.StringIO(self.to_unicode())
        header = etree.Element('header')
        body = etree.Element('body')
        ptext = ''

        newstags = re.compile(r'(@*logo:|@*ingres+:|.*@*bilde(\s\d)*:|(@|LED)*tekst:|@*stikk:|@foto:|@fotobyline:|@bildetitt:)', re.IGNORECASE)
        titletags = re.compile(r'@m.titt:@ingress:|Mellomtittel:|@*(stikk|under)titt:|@ttt:|@*[utm]*[:\.]*tit+:', re.IGNORECASE)
        headertitletags = re.compile(r'@tittel:|@titt:|TITT:|Tittel:|@LEDtitt:')

        for line in content:
            if newstags.match(line):
                line = newstags.sub('', line).strip()
                body.append(self.make_element('p', line))
                ptext = ''
            elif line.startswith('@bold:'):
                line = line.replace('@bold:', '').strip()
                p = etree.Element('p')
                p.append(self.make_element('em', line, {'type': 'bold'}))
                body.append(p)
                ptext = ''
            elif line.startswith('@kursiv:'):
                line = line.replace('@kursiv:', '').strip()
                p = etree.Element('p')
                p.append(self.make_element('em', line, {'type': 'italic'}))
                body.append(p)
                ptext = ''
            elif line.startswith(u'  '):
                body.append(self.make_element('p', line.strip()))
                ptext = ''
            elif headertitletags.match(line):
                line = headertitletags.sub('', line).strip()
                if header.find("title") is None:
                    header.append(self.make_element('title', line))
                else:
                    body.append(self.make_element('p', line, {'type': 'title'}))
                ptext = ''
            elif titletags.match(line):
                line = titletags.sub('', line).strip()
                body.append(self.make_element('p', line, {'type': 'title'}))
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
                        body.append(self.make_element('p', ptext.strip()))
                        ptext = ''
                    except ValueError:
                        raise ConversionException(
                            "Invalid utf8 «" +
                            ptext.strip().encode('utf-8') + "»")

                ptext = ''
            else:
                ptext = ptext + line.replace('\n', ' ')

        if ptext != '':
            body.append(self.make_element('p', ptext.strip()))

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


class PDFConverter(object):
    def __init__(self, filename):
        self.orig = filename

    def replace_ligatures(self):
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

    def extract_text(self):
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
            logfile.write('Error at: ' + str(ccat.lineno()))
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
        self.replace_ligatures()
        return self.strip_chars(self.text)

    def strip_chars(self, content, extra=u''):
        remove_re = re.compile(u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F%s]' % extra)
        content, count = remove_re.subn('', content)

        return content

    #def extract_text1(self):
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
        #self.replace_ligatures()
        #outfp.close()

        #return self.text

    def convert2intermediate(self):
        document = etree.Element('document')
        header = etree.Element('header')
        body = etree.Element('body')

        content = io.StringIO(self.extract_text())
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


class BiblexmlConverter(object):
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


class HTMLContentConverter(object):
    """
    Class to convert html documents to the giellatekno xml format

    content is a string
    """
    def __init__(self, filename, content):
        self.orig = filename

        try:
            self.soup = bs4.BeautifulSoup(content, 'lxml')
        except HTMLParser.HTMLParseError:
            raise ConversionException("BeautifulSoup couldn't parse the html")

        self.converter_xsl = resource_string(__name__, 'xslt/xhtml2corpus.xsl')

    def remove_empty_class(self):
        """Some documents have empty class attributes.
        Delete these attributes.
        """
        for tag in self.soup.find_all(True):
            if tag.has_attr('class') and tag['class'] == ['']:
                del tag['class']

    def remove_elements(self):
        '''Remove unwanted tags from a html document

        The point with this exercise is to remove all but the main content of
        the document.
        '''
        for instance in [
                bs4.Comment, bs4.ProcessingInstruction, bs4.Declaration]:
            [unwanted.extract() for unwanted in self.soup.find_all(
                text=lambda text: isinstance(text, instance))]

        remove_tags = [
            'script', 'style', 'o:p', 'st1:country-region', 'v:shapetype',
            'v:shape', 'st1:metricconverter', 'area', 'object', 'meta',
            'fb:like', 'fb:comments', 'g:plusone', 'hr', 'nf', 'mb', 'ms',
            'img', 'cite', 'embed', 'footer', 'figcaption', 'aside', 'time',
            'figure', 'nav', 'select', 'noscript', 'iframe', 'map', 'img',
            'colgroup']

        for remove_tag in remove_tags:
            [remove.decompose() for remove in self.soup.find_all(remove_tag)]

        unwanted_classes_ids = {
            'div': {
                'class': [
                    'QuickNav', 'tabbedmenu', 'printContact', 'documentPaging',
                    'breadcrumbs', 'post-footer', 'documentInfoEm',
                    'article-column', 'nrk-globalfooter', 'article-related',
                    'outer-column', 'article-ad', 'article-bottom-element',
                    'banner-element', 'nrk-globalnavigation', 'sharing', 'ad',
                    'meta', 'authors', 'articleImageRig',  'btm_menu',
                    'expandable', 'toc', 'titlepage'],
                'id': [
                    'searchBox',
                    'ctl00_FullRegion_CenterAndRightRegion_Sorting_sortByDiv',
                    'ctl00_FullRegion_CenterAndRightRegion_HitsControl_searchHitSummary',
                    'AreaTopSiteNav', 'SamiDisclaimer', 'AreaTopRight',
                    'AreaLeft', 'AreaRight', 'ShareArticle', 'tipafriend',
                    'AreaLeftNav', 'PageFooter', 'blog-pager',
                    'NAVheaderContainer', 'NAVbreadcrumbContainer',
                    'NAVsubmenuContainer', 'NAVrelevantContentContainer',
                    'NAVfooterContainer', 'sidebar-wrapper', 'footer-wrapper',
                    'share-article', 'topUserMenu', 'rightAds', 'menu', 'aa',
                    'sidebar', 'footer', 'chatBox', 'sendReminder',
                    'ctl00_MidtSone_ucArtikkel_ctl00_divNavigasjon',
                    'ctl00_MidtSone_ucArtikkel_ctl00_ctl00_ctl01_divRessurser'],
                },
            'p': {
                'class': ['WebPartReadMoreParagraph', 'breadcrumbs'],
                },
            'ul': {
                'id': ['AreaTopPrintMeny', 'AreaTopLanguageNav',],
                'class': ['QuickNav', 'article-tools', 'byline']
                },
            'span': {
                'id': ['skiplinks'],
                'class': ['K-NOTE-FOTNOTE']
                },
            }

        for tag, attribs in unwanted_classes_ids.items():
            for key, values in attribs.items():
                for value in values:
                    [remove.decompose() for remove in self.soup.find_all(tag, {key: value})]

    def tidy(self):
        """
        Run html through tidy
        """
        self.remove_empty_class()
        self.remove_elements()

        if not ("xmlns", "http://www.w3.org/1999/xhtml") in self.soup.html.attrs:
            self.soup.html["xmlns"] = "http://www.w3.org/1999/xhtml"

        self.soup = self.soup.prettify()
        replacements = {'&shy;': u'­',
                        '&nbsp;': ' ',
                        '&aelig;': u'æ',
                        '&eacute;': u'é'}
        for key, value in replacements.iteritems():
            self.soup = self.soup.replace(key, value)

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

        tidiedHtml, errors = tidylib.tidy_document(self.soup, tidyOption)

        #sys.stderr.write(str(lineno()) + ' ' +  soup.prettify())
        return tidiedHtml

    def convert2intermediate(self):
        """
        Convert the original document to the giellatekno xml format, with no
        metadata
        The resulting xml is stored in intermediate
        """
        html_xslt_root = etree.fromstring(self.converter_xsl)
        transform = etree.XSLT(html_xslt_root)

        intermediate = ''

        html = self.tidy()
        try:
            doc = etree.fromstring(html)
            intermediate = transform(doc)
        except etree.XMLSyntaxError as e:
            logfile = open(self.orig + '.log', 'w')

            logfile.write('Error at: ' + str(ccat.lineno()))
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

            logfile.write('Error at: ' + str(ccat.lineno()))
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


class DocConverter(HTMLContentConverter):
    """
    Class to convert Microsoft Word documents to the giellatekno xml format
    """
    def __init__(self, filename):
        self.orig = filename
        HTMLContentConverter.__init__(self, filename, self.docbook2html())

    def doc2docbook(self):
        """Convert the doc file using antiword to a docbook xml file
        Return the output as an etree
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

        return etree.fromstring(output)

    def docbook2html(self):
        """Convert the docbook output to html using docbook-xsl
        Return the html as a string
        """
        docbook_transformer = etree.XSLT(etree.parse('http://docbook.sourceforge.net/release/xsl/current/xhtml/docbook.xsl'))
        try:
            html = docbook_transformer(self.doc2docbook())
        except etree.XSLTApplyError as (e):
            logfile = open(self.orig + '.log', 'w')

            logfile.write('Error at: ' + str(ccat.lineno()))
            for entry in e.error_log:
                logfile.write(str(entry))
                logfile.write('\n')

            logfile.close()
            raise ConversionException('Could not convert docbook ' + self.orig)

        return etree.tostring(html)


class DocumentFixer(object):
    """
    Receive a stringified etree from one of the raw converters,
    replace ligatures, fix the encoding and return an etree with correct
    characters
    """
    def __init__(self, document):
        self.etree = document

    def get_etree(self):
        return etree.parse(io.BytesIO(etree.tostring(self.etree)))

    def soft_hyphen_to_hyph_tag(self):
        """Replace soft hyphens in text by the hyph tag
        """
        for element in self.etree.iter('p'):
            self.replace_shy(element)

    def replace_shy(self, element):
        """Split text and tail on shy. Insert hyph tags
        between the parts.
        """
        for child in element:
            self.replace_shy(child)

        text = element.text
        if text is not None:
            parts = text.split(u'­')
            if len(parts) > 1:
                element.text = parts[0]
                x = 0
                for part in parts[1:]:
                    hyph = etree.Element('hyph')
                    hyph.tail = part
                    element.insert(x, hyph)
                    x += 1

        text = element.tail
        if text is not None:
            parts = text.split(u'­')
            if len(parts) > 1:
                element.tail = parts[0]
                for part in parts[1:]:
                    hyph = etree.Element('hyph')
                    hyph.tail = part
                    element.getparent().append(hyph)

    def replace_ligatures(self):
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

    def fix_body_encoding(self):
        """
        Send a stringified version of the body into the EncodingGuesser class.
        It returns the same version, but with fixed characters.
        Parse the returned string, insert it into the document
        """
        self.replace_ligatures()

        if isinstance(self.etree, etree._XSLTResultTree):
            sys.stderr.write("xslt!\n")

        body = self.etree.find('body')
        bodyString = etree.tostring(body, encoding='utf-8')
        body.getparent().remove(body)

        eg = decode.EncodingGuesser()
        encoding = eg.guess_body_encoding(bodyString)

        body = etree.fromstring(eg.decode_para(encoding, bodyString))
        self.etree.append(body)

        self.fix_title_person('double-utf8')
        self.fix_title_person('mac-sami_to_latin1')

        self.detect_quotes()

    def fix_title_person(self, encoding):
        eg = decode.EncodingGuesser()

        title = self.etree.find('.//title')
        if title is not None and title.text is not None:
            text = title.text

            if encoding == 'mac-sami_to_latin1':
                text = text.replace(u'‡', u'á')
                text = text.replace(u'Œ', u'å')

            text = text.encode('utf8')
            title.text = eg.decode_para(encoding, text).decode('utf-8')

        persons = self.etree.findall('.//person')
        for person in persons:
            if person is not None:
                lastname = person.get('lastname')

                if encoding == 'mac-sami_to_latin1':
                    lastname = lastname.replace(u'‡', u'á')
                    lastname = lastname.replace(u'Œ', u'å')

                person.set(
                    'lastname',
                    eg.decode_para(
                        encoding,
                        lastname.encode('utf-8')).decode('utf-8'))

                firstname = person.get('firstname')

                if encoding == 'mac-sami_to_latin1':
                    firstname = firstname.replace(u'‡', u'á')
                    firstname = firstname.replace(u'Œ', u'å')

                person.set(
                    'firstname',
                    eg.decode_para(
                        encoding,
                        firstname.encode('utf-8')).decode('utf-8'))

    def detect_quote(self, element):
        """Detect quotes in an etree element.
        """
        newelement = deepcopy(element)

        element.text = ''
        for child in element:
            child.getparent().remove(child)

        quote_list = []
        quote_regexes = [re.compile('".+?"'),
                        re.compile(u'«.+?»'),
                        re.compile(u'“.+?”')]

        text = newelement.text
        if text:
            for quote_regex in quote_regexes:
                for m in quote_regex.finditer(text):
                    quote_list.append(m.span())

            if len(quote_list) > 0:
                quote_list.sort()
                element.text = text[0:quote_list[0][0]]

                for x in range(0, len(quote_list)):
                    span = etree.Element('span')
                    span.set('type', 'quote')
                    span.text = text[quote_list[x][0]:quote_list[x][1]]
                    if x + 1 < len(quote_list):
                        span.tail = text[quote_list[x][1]:quote_list[x + 1][0]]
                    else:
                        span.tail = text[quote_list[x][1]:]
                    element.append(span)
            else:
                element.text = text

        for child in newelement:
            element.append(self.detect_quote(child))

            if child.tail:
                quote_list = []
                text = child.tail

                for quote_regex in quote_regexes:
                    for m in quote_regex.finditer(text):
                        quote_list.append(m.span())

                if len(quote_list) > 0:
                    quote_list.sort()
                    child.tail = text[0:quote_list[0][0]]

                for x in range(0, len(quote_list)):
                    span = etree.Element('span')
                    span.set('type', 'quote')
                    span.text = text[quote_list[x][0]:quote_list[x][1]]
                    if x + 1 < len(quote_list):
                        span.tail = text[quote_list[x][1]:quote_list[x + 1][0]]
                    else:
                        span.tail = text[quote_list[x][1]:]
                    element.append(span)

        return element

    def detect_quotes(self):
        """Detect quotes in all paragraphs
        """
        for paragraph in self.etree.iter('p'):
            paragraph = self.detect_quote(paragraph)

    def set_word_count(self):
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


class XslMaker(object):
    """
    To convert the intermediate xml to a fullfledged  giellatekno document
    a combination of three xsl files + the intermediate files is needed
    This class makes the xsl file
    """

    def __init__(self, xslfile):
        preprocessXsl = etree.fromstring(
            resource_string(__name__, 'xslt/preprocxsl.xsl'))
        preprocessXslTransformer = etree.XSLT(preprocessXsl)

        self.filename = xslfile
        try:
            filexsl = etree.parse(xslfile)
        except etree.XMLSyntaxError as e:
            logfile = open(self.filename + '.log', 'w')

            logfile.write('Error at: ' + str(ccat.lineno()))
            for entry in e.error_log:
                logfile.write(str(entry))
                logfile.write('\n')

            logfile.close()
            raise ConversionException("Syntax error in " + self.filename)

        self.finalXsl = preprocessXslTransformer(
            filexsl,
            commonxsl=
            etree.XSLT.strparam('file://' +
                                resource_filename(__name__, 'xslt/common.xsl')))

    def get_xsl(self):
        return self.finalXsl


class LanguageDetector(object):
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

    def get_document(self):
        return self.document

    def get_mainlang(self):
        """
        Get the mainlang of the file
        """
        return self.mainlang

    def set_paragraph_language(self, paragraph):
        """Extract the text outside the quotes, use this text to set
        language of the paragraph.
        Set the language of the quotes in the paragraph
        """

        if paragraph.get('{http://www.w3.org/XML/1998/namespace}lang') is None:
            paragraph_text = self.remove_quote(paragraph)
            lang = self.languageGuesser.classify(
                paragraph_text.encode("ascii", "ignore"))
            if lang != self.get_mainlang():
                paragraph.set('{http://www.w3.org/XML/1998/namespace}lang', lang)

            for element in paragraph.iter("span"):
                if element.get("type") == "quote":
                    lang = self.languageGuesser.classify(
                        element.text.encode("ascii", "ignore"))
                    if lang != self.get_mainlang():
                        element.set(
                            '{http://www.w3.org/XML/1998/namespace}lang', lang)

        return paragraph

    def remove_quote(self, paragraph):
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

    def detect_language(self):
        """Detect language in all the paragraphs in self.document
        """
        if self.document.find('header/multilingual') is not None:
            for paragraph in self.document.iter('p'):
                paragraph = self.set_paragraph_language(paragraph)


class DocumentTester(object):
    def __init__(self, document):
        self.document = document
        self.mainlang = self.document.getroot().\
            attrib['{http://www.w3.org/XML/1998/namespace}lang']
        self.remove_foreign_language()

    def get_mainlang(self):
        """
        Get the mainlang of the file
        """
        return self.mainlang

    def get_mainlang_wordcount(self):
        return len(re.findall(r'\S+', self.get_mainlang_words()))

    def get_unknown_words_ratio(self):
        return 1.0 * self.get_unknown_wordcount() / self.get_mainlang_wordcount()

    def get_mainlang_ratio(self):
        return 1.0 * self.get_mainlang_wordcount() / float(
            self.document.find('header/wordcount').text)

    def remove_foreign_language(self):
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

    def get_unknown_wordcount(self):
        lookup_command = ['lookup', '-flags', 'mbTT']
        if self.get_mainlang() == 'sme':
            lookup_command.append(os.getenv('GTHOME') +
                                 '/gt/' +
                                 self.get_mainlang() +
                                 '/bin/' +
                                 self.get_mainlang() +
                                 '.fst')
        else:
            lookup_command.append(
                os.getenv('GTHOME') +
                '/langs/' +
                self.get_mainlang() +
                '/src/analyser-gt-desc.xfst')

        subp = subprocess.Popen(lookup_command,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        (output, error) = subp.communicate(self.get_preprocessed_mainlang_words())

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

    def get_preprocessed_mainlang_words(self):
        """Send the text into preprocess, return the result.
        If the process fails, exit the program
        """
        preprocess_command = []
        if self.get_mainlang() == 'sme':
            abbrFile = os.path.join(
                os.environ['GTHOME'], 'gt/sme/bin/abbr.txt')
            corrFile = os.path.join(
                os.environ['GTHOME'], 'gt/sme/bin/corr.txt')
            preprocess_command = ['preprocess',
                                 '--abbr=' + abbrFile, '--corr=' + corrFile]
        else:
            preprocess_command = ['preprocess']

        subp = subprocess.Popen(preprocess_command,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        (output, error) = subp.communicate(
            self.get_mainlang_words().replace('\n', ' '))

        if subp.returncode != 0:
            print >>sys.stderr, output
            print >>sys.stderr, error
            raise ConversionException('Could not preprocess text')
        else:
            return output

    def get_mainlang_words(self):
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
    parser.add_argument('source',
                        help="directory where the original files exist")

    args = parser.parse_args()
    return args


def worker(xsl_file):
    conv = Converter(xsl_file[:-4])

    try:
        conv.write_complete()
    except ConversionException:
        print >>sys.stderr, 'Could not convert', xsl_file[:-4]


def convert_in_parallel(xsl_files):
    pool_size = multiprocessing.cpu_count() * 2
    pool = multiprocessing.Pool(processes=pool_size,)
    pool.map(worker, xsl_files)
    pool.close()
    pool.join()


def convert_serially(xsl_files):
    for xsl_file in xsl_files:
        worker(xsl_file)


def collect_files(source_dir):
    xsl_files = []
    for root, dirs, files in os.walk(source_dir):
        for f in files:
            if f.endswith('.xsl'):
                xsl_files.append(os.path.join(root, f))

    return xsl_files


def setup_xml_catalog():
    """Setup xml catalog to try to access docbook xsl stylesheets
    without hitting the network
    """
    if os.path.exists('/etc/xml/catalog'):
        os.environ['XML_CATALOG_FILES'] = '/etc/xml/catalog'
    elif os.path.exists('/opt/local/etc/xml/catalog'):
        os.environ['XML_CATALOG_FILES'] = '/opt/local/etc/xml/catalog'


def main():
    setup_xml_catalog()
    args = parse_options()

    if os.path.isfile(args.source):
        xsl_file = args.source + '.xsl'
        if os.path.isfile(xsl_file):
            worker(xsl_file)
        else:
            xsl_stream = open(xsl_file, 'w')
            xsl_stream.write(
                resource_string(__name__, 'xslt/XSL-template.xsl'))
            xsl_stream.close()
            print "Fill in meta info in", xsl_file, \
                ', then run this command again'
            sys.exit(1)
    elif os.path.isdir(args.source):
        if args.debug:
            convert_serially(collect_files(args.source))
        else:
            convert_in_parallel(collect_files(args.source))
