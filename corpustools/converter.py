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
import re
import io
import subprocess
import HTMLParser
from copy import deepcopy
import distutils.dep_util, distutils.spawn
import codecs
import multiprocessing
import argparse
import tempfile
from pkg_resources import resource_string, resource_filename

import lxml.etree as etree
import lxml.html.clean as clean
from lxml.html import html5parser
from pyth.plugins.rtf15.reader import Rtf15Reader
from pyth.plugins.xhtml.writer import XHTMLWriter
from pydocx.parsers import Docx2Html

import decode
import ngram
import errormarkup
import ccat
import analyser
import argparse_version
import functools
import util


class ConversionException(Exception):
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


class Converter(object):
    """
    Class to take care of data common to all Converter classes
    """
    def __init__(self, filename, write_intermediate=False, test=False):
        self.orig = os.path.abspath(filename)
        self.set_corpusdir()
        self.set_converted_name()
        self.dependencies = [self.get_orig(), self.get_xsl()]
        self.fix_lang_genre_xsl()
        self._write_intermediate = write_intermediate

    def make_intermediate(self, encoding_from_xsl):
        """Convert the input file from the original format to a basic
        giellatekno xml document
        """
        if 'avvir_xml' in self.orig:
            intermediate = AvvirConverter(self.orig)

        elif self.orig.endswith('.txt'):
            intermediate = PlaintextConverter(self.orig)

        elif self.orig.endswith('.pdf'):
            intermediate = PDFConverter(self.orig)

        elif self.orig.endswith('.svg'):
            intermediate = SVGConverter(self.orig)

        elif '.htm' in self.orig or '.php' in self.orig:
            intermediate = HTMLConverter(self.orig, encoding_from_xsl)

        elif self.orig.endswith('.doc') or self.orig.endswith('.DOC'):
            intermediate = DocConverter(self.orig)

        elif self.orig.endswith('.docx'):
            intermediate = DocxConverter(self.orig)

        elif '.rtf' in self.orig:
            intermediate = RTFConverter(self.orig)

        elif self.orig.endswith('.bible.xml'):
            intermediate = BiblexmlConverter(self.orig)

        else:
            raise ConversionException("Unknown file extension, not able to convert " + self.orig + "\nHint: you may just have to rename the file")

        document = intermediate.convert2intermediate()

        if isinstance(document, etree._XSLTResultTree):
            document = etree.fromstring(etree.tostring(document))

        return document

    @staticmethod
    def get_dtd_location():
        return os.path.join(os.getenv('GTHOME'), 'gt/dtd/corpus.dtd')

    def validate_complete(self, complete):
        """Validate the complete document
        """
        dtd = etree.DTD(Converter.get_dtd_location())

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

    def maybe_write_intermediate(self, intermediate):
        if not self._write_intermediate:
            return
        im_name = self.orig + '.im.xml'
        with open(im_name, 'w') as im_file:
            im_file.write(etree.tostring(intermediate,
                                         encoding='utf8',
                                         pretty_print='True'))

    def encoding_from_xsl(self, xsl):
        encoding_elt = xsl.find('//xsl:variable[@name="text_encoding"]',
                                namespaces={'xsl':'http://www.w3.org/1999/XSL/Transform'})
        if encoding_elt is not None:
            return encoding_elt.attrib.get("select","''").strip("'")
        else:
            return None

    def transform_to_complete(self):
        xm = XslMaker(self.get_xsl())
        intermediate = self.make_intermediate(self.encoding_from_xsl(xm.finalXsl))
        self.maybe_write_intermediate(intermediate)

        try:
            complete = xm.get_transformer()(intermediate)

            return complete
        except etree.XSLTApplyError as (e):
            logfile = open(self.orig + '.log', 'w')

            logfile.write('Error at: ' + str(ccat.lineno()))
            for entry in e.error_log:
                logfile.write(str(entry))
                logfile.write('\n')

            logfile.close()
            raise ConversionException("Check the syntax in: " + self.get_xsl())

    def convert_errormarkup(self, complete):
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

    def fix_document(self, complete):
        fixer = DocumentFixer(etree.fromstring(etree.tostring(complete)))

        fixer.fix_newstags()
        fixer.soft_hyphen_to_hyph_tag()
        fixer.set_word_count()
        fixer.detect_quotes()

        if (complete.getroot().
            attrib['{http://www.w3.org/XML/1998/namespace}lang'] in
                ['sma', 'sme', 'smj', 'nob', 'fin']):
            fixer.fix_body_encoding()

        return fixer.get_etree()

    def make_complete(self):
        """Combine the intermediate giellatekno xml file and the metadata into
        a complete giellatekno xml file.
        Fix the character encoding
        Detect the languages in the xml file
        """
        complete = self.transform_to_complete()
        self.validate_complete(complete)
        self.convert_errormarkup(complete)
        complete = self.fix_document(complete)
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

                xml_printer = ccat.XMLPrinter(all_paragraphs=True,
                                              hyph_replacement=None)
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
                to_write = False
                parts = origname[1:].split('/')

                lang = root.find(transform +
                                 mainlang).attrib['select'].replace("'", "")

                if lang == "":
                    to_write = True
                    lang = parts[1]
                    root.find(transform +
                              mainlang).attrib['select'] = "'" + lang + "'"

                genre = root.find(transform +
                                  xslgenre).attrib['select'].replace("'", "")

                if genre == "" or genre not in ['admin', 'bible', 'facta',
                                                'ficti', 'news']:
                    to_write = True
                    if parts[2] in ['admin', 'bible', 'facta', 'ficti',
                                    'news']:
                        genre = parts[parts.index('orig') + 2]
                        root.find(transform +
                                  xslgenre).attrib['select'] = \
                            "'" + genre + "'"
                if to_write:
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
                logfile.close()
                raise ConversionException(
                    u"XSL syntax error. More info in the log file: " +
                    self.get_orig() + u".log")

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

        for title in self.intermediate.findall(
                './/story[@class="Undertittel"]'):
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

        content = self.strip_chars(content)

        return content

    def strip_chars(self, content, extra=u''):
        content = content.replace(u'ÊÊ', '\n')
        content = content.replace(u'<\!q>', u'')
        content = content.replace(u'<\!h>', u'')
        content = content.replace(u'<*B>', u'')
        content = content.replace(u'<*P>', u'')
        content = content.replace(u'<*I>', u'')
        # Convert CR (carriage return) to LF (line feed)
        content = content.replace('\x0d', '\x0a')
        content = content.replace(u'<ASCII-MAC>', '')
        content = content.replace(u'<vsn:3.000000>', u'')
        # Some plain text files have some chars marked up this way …
        content = content.replace(u'<0x010C>', u'Č')
        content = content.replace(u'<0x010D>', u'č')
        content = content.replace(u'<0x0110>', u'Đ')
        content = content.replace(u'<0x0111>', u'đ')
        content = content.replace(u'<0x014A>', u'Ŋ')
        content = content.replace(u'<0x014B>', u'ŋ')
        content = content.replace(u'<0x0160>', u'Š')
        content = content.replace(u'<0x0161>', u'š')
        content = content.replace(u'<0x0166>', u'Ŧ')
        content = content.replace(u'<0x0167>', u'ŧ')
        content = content.replace(u'<0x017D>', u'Ž')
        content = content.replace(u'<0x017E>', u'ž')
        content = content.replace(u'<0x2003>', u' ')

        remove_re = re.compile(
            u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F%s]' % extra)
        content, count = remove_re.subn('', content)

        return content

    def make_element(self, eName, text):
        """
        @brief Makes an xml element containing the given name, text and
        attributes. Adds a hyph element if necessary.

        :param eName: Name of the xml element
        :type eName: string

        :param text: The text the xml should contain
        :type text: string

        :param attributes: The attributes the element should have
        :type attributes: dict

        :returns: lxml.etree.Element
        """
        el = etree.Element(eName)

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
        return self.content2xml(io.StringIO(self.to_unicode()))

    def content2xml(self, content):
        document = etree.Element('document')
        header = etree.Element('header')
        body = etree.Element('body')

        ptext = ''

        for line in content:
            if line.strip() == '':
                if ptext.strip() != '':
                    body.append(self.make_element('p', ptext))
                ptext = ''
            else:
                ptext = ptext + line

        if ptext != '':
            body.append(self.make_element('p', ptext))

        document.append(header)
        document.append(body)

        return document


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

    def convert2intermediate(self):
        document = etree.Element('document')
        header = etree.Element('header')
        body = etree.Element('body')

        content = io.StringIO(self.extract_text())
        ptext = ''

        for line in content:
            if line.strip() == '':
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


class PDF2XMLConverter(object):
    '''Class to convert pdf2xml
    '''
    def __init__(self):
        self.body = etree.Element('body')
        self.parts = []
        self.skip_pages = []
        self.margins = {}

    def set_margins(self, margin_lines={}):
        '''margins_lines will be fetched from the metadata file belonging to
        the original file. Before it is passed here, the validity of them
        are checked.
        '''
        for key, value in margin_lines.items():
            self.margins[key] = self.set_margin(value)

    def set_margin(self, value):
        '''
        '''
        m = {}
        parts = value.split(';')
        for part in parts:
            page = part.split('=')[0].strip()
            margin = int(part.split('=')[1])
            m[page] = margin

        return m

    def compute_margins(self, page):
        '''page is a page element
        '''
        margins = {}
        page_number = page.get('number')
        page_width = int(page.get('width'))
        page_height = int(page.get('height'))

        for margin in ['rm', 'lm', 'tm', 'bm']:
            if margin in self.margins.keys():
                m = self.margins[margin]
                if m.get(page_number) is not None:
                    margins[margin] = m[page_number.strip()]
                elif m.get('all') is not None:
                    margins[margin] = m['all']
                elif int(page_number) % 2 == 0 and m.get('even') is not None:
                    margins[margin] = m['even']
                elif int(page_number) % 2 == 1 and m.get('odd') is not None:
                    margins[margin] = m['odd']
                else:
                    margins[margin] = self.compute_margin(margin, page_height, page_width)
            else:
                margins[margin] = self.compute_margin(margin, page_height, page_width)

        return margins

    def compute_margin(self, margin, page_height, page_width):
        '''Compute the margins if they are not explicitely set
        '''
        default = 0.07
        if margin == 'rm':
            return int(default * page_width)
        if margin == 'lm':
            return int(page_width - default * page_width)
        if margin == 'tm':
            return int(default * page_height)
        if margin == 'bm':
            return int(page_height - default * page_height)

        return margins

    def append_to_body(self, element):
        self.body.append(element)
        self.parts = []

    def get_body(self):
        return self.body

    def extract_textelement(self, textelement):
        '''Convert one <text> element to an array of text and etree Elements.

        A <text> element can contain <i> and <b> elements.

        <i> elements can contain <b> and <a> elements.
        <b> elements can contain <i> and <a> elements.

        The text and tail parts of the elements contained in the <i> and <b>
        elements become the text parts of <i> and <b> elements.
        '''

        print ccat.lineno(), etree.tostring(textelement)
        if (textelement is not None and int(textelement.get('width')) > 0):
            if textelement.text is not None:
                if len(self.parts) > 0:
                    if isinstance(self.parts[-1], etree._Element):
                        if self.parts[-1].tail is not None:
                            self.parts[-1].tail += ' ' + textelement.text
                        else:
                            self.parts[-1].tail = textelement.text
                    else:
                        self.parts[-1] += ' ' + textelement.text
                else:
                    m = re.search('\w-$', textelement.text, re.UNICODE)
                    if m:
                        self.parts.append(textelement.text[:-1])
                        self.parts.append(etree.Element('hyph'))
                    else:
                        self.parts.append(textelement.text)


            for child in textelement:
                em = etree.Element('em')

                if child.text is not None:
                    m = re.search('\w-$', child.text, re.UNICODE)
                    if m:
                        em.text = child.text[:-1]
                        em.append(etree.Element('hyph'))
                    else:
                        em.text = child.text
                else:
                    em.text = ''

                if len(child) > 0:
                    for grandchild in child:
                        if grandchild.text is not None:
                            m = re.search('\w-$', grandchild.text, re.UNICODE)
                            if m:
                                em.text += grandchild.text[:-1]
                                em.append(etree.Element('hyph'))
                            else:
                                em.text += grandchild.text
                        if grandchild.tail is not None:
                            em.text += grandchild.tail

                if child.tag == 'i':
                    em.set('type', 'italic')
                elif child.tag == 'b':
                    em.set('type', 'bold')

                em.tail = child.tail

                self.parts.append(em)
        print ccat.lineno(), self.parts

    def is_same_paragraph(self, text1, text2):
        '''Define the incoming text elements text1 and text2 to belong to
        the same paragraph if they have the same height and if the difference
        between the top attributes is less than ratio times the height of
        the text elements.
        '''
        result = False

        h1 = float(text1.get('height'))
        h2 = float(text2.get('height'))
        f1 = text1.get('font')
        f2 = text2.get('font')
        delta = float(text2.get('top')) - float(text1.get('top'))
        ratio = 1.5

        if ( f1 == f2 and h1 == h2 and delta < ratio * h1):
            result = True

        return result

    def parse_page(self, page):
        '''Parse a page element
        '''
        margins = self.compute_margins(page)

        prev_t = None
        for t in page.iter('text'):
            if prev_t is not None:
                print ccat.lineno(), etree.tostring(prev_t), etree.tostring(t)
                if not self.is_same_paragraph(prev_t, t):
                    self.append_to_body(self.make_paragraph())
            if self.is_inside_margins(t, margins):
                self.extract_textelement(t)
                print ccat.lineno(), self.parts
                prev_t = t

        self.append_to_body(self.make_paragraph())

    def is_inside_margins(self, t, margins):
        '''Check if t is inside the given margins

        t is a text element
        '''
        return (int(t.get('top')) > margins['tm'] and int(t.get('top')) < margins['bm'] and
                int(t.get('left')) > margins['rm'] and int(t.get('left')) < margins['lm'])

    def parse_pages(self, root_element):
        for page in root_element.iter('page'):
            if page.get('number') not in self.skip_pages:
                self.parse_page(page)

    def make_paragraph(self):
        '''parts is a list of strings and etree.Elements that belong to the
        same paragraph

        The parts list is converted to a p element.
        '''
        if len(self.parts) > 0:
            p = etree.Element('p')
            print ccat.lineno(), self.parts[0], self.parts, type(self.parts[0])
            if (isinstance(self.parts[0], str) or isinstance(self.parts[0], unicode)):
                p.text = self.parts[0]
            else:
                p.append(self.parts[0])

            for part in self.parts[1:]:
                if isinstance(part, etree._Element):
                    if len(p) > 0 and len(p[-1]) > 0 and p[-1][-1].tag == 'hyph':
                        if p[-1].tag == part.tag and p[-1].get('type') == part.get('type'):
                            p[-1][-1].tail = part.text
                            p[-1].tail = part.tail
                        else:
                            p.append(part)
                    else:
                        p.append(part)
                else:
                    if p[-1].tail is None:
                        p[-1].tail = part
                    else:
                        p[-1].tail = ' ' + part

            return p

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
        (tmpfile, tmpname) = tempfile.mkstemp()
        bible2xmlpl = 'bible2xml.pl'
        if distutils.spawn.find_executable(bible2xmlpl) is None:
            raise ConversionException("Could not find %s in $PATH" %(bible2xmlpl,))

        subp = subprocess.Popen(
            [bible2xmlpl, '-out', tmpname, self.orig],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        (output, error) = subp.communicate()

        if subp.returncode != 0:
            logfile = open(self.get_orig() + '.log', 'w')

            logfile.write('Error at: ' + str(ccat.lineno()))
            logfile.write('bible2xml.pl exit status was not 0\n')
            logfile.write('stdout: \n')
            logfile.write(output)
            logfile.write('stderr: \n')
            logfile.write(error)
            logfile.close()
            raise ConversionException('bible2xml.pl returned non zero status. More info in ' + self.orig + '.log')

        return etree.parse(tmpname)


class HTMLContentConverter(object):
    """
    Class to convert html documents to the giellatekno xml format

    content is a string
    """
    def __init__(self, filename, content):
        '''Clean up content, then convert it to xhtml using html5parser
        '''
        self.orig = filename

        cleaner = clean.Cleaner(
            page_structure=False,
            scripts=True,
            javascript=True,
            comments=True,
            style=True,
            processing_instructions=True,
            remove_unknown_tags=True,
            embedded=True,
            remove_tags=['img', 'area', 'hr', 'cite', 'footer', 'figcaption',
                         'aside', 'time', 'figure', 'nav', 'noscript', 'map',])

        charset = 'utf-8'
        cg = content.find('charset=')
        if cg > 0:
            f = cg + content[cg:].find('"')
            charset = content[cg + len('charset='):f]
            print ccat.lineno(), self.orig, cg, f, content[cg + len('charset='):f]

        superclean = cleaner.clean_html(content.decode(charset))

        self.soup = html5parser.document_fromstring(superclean)
        with open('HTMLContentConverter.xml', 'w') as huff:
            huff.write(etree.tostring(self.soup, encoding='utf-8'))

        self.converter_xsl = resource_string(__name__, 'xslt/xhtml2corpus.xsl')

    def remove_empty_class(self):
        """Some documents have empty class attributes.
        Delete these attributes.
        """
        for element in self.soup.xpath('.//*[@class=""]'):
            del element.attrib['class']

    def remove_elements(self):
        '''Remove unwanted tags from a html document

        The point with this exercise is to remove all but the main content of
        the document.
        '''
        unwanted_classes_ids = {
            'div': {
                'class': [
                    'QuickNav', 'tabbedmenu', 'printContact', 'documentPaging',
                    'breadcrumbs', 'post-footer', 'documentInfoEm',
                    'article-column', 'nrk-globalfooter', 'article-related',
                    'outer-column', 'article-ad', 'article-bottom-element',
                    'banner-element', 'nrk-globalnavigation', 'sharing', 'ad',
                    'meta', 'authors', 'articleImageRig',  'btm_menu',
                    'expandable', 'toc', 'titlepage',
                    'container_full', 'moduletable_oikopolut',
                    "latestnews_uutisarkisto", 'back_button'],
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
                    'ctl00_MidtSone_ucArtikkel_ctl00_ctl00_ctl01_divRessurser',
                    'leftPanel',
                    'leftMenu',
                    'topMenu',
                    'article_footer',
                    'rightCol',
                    'PrintDocHead',],
                },
            'p': {
                'class': ['WebPartReadMoreParagraph', 'breadcrumbs'],
                },
            'ul': {
                'id': ['AreaTopPrintMeny', 'AreaTopLanguageNav'],
                'class': ['QuickNav', 'article-tools', 'byline']
                },
            'span': {
                'id': ['skiplinks'],
                'class': ['K-NOTE-FOTNOTE']
                },
            'a': {
                'id': ['leftPanelTab',],
                'class': ['mainlevel'],
                },
            'td': {
                'id': ["paavalikko_linkit", "hakulomake", 'sg_oikea'],
                'class': ["modifydate"],
                },
            'tr': {
                'id': ["sg_ylaosa1", "sg_ylaosa2"]
                },
            }

        ns = {'html': 'http://www.w3.org/1999/xhtml'}
        for tag, attribs in unwanted_classes_ids.items():
            for key, values in attribs.items():
                for value in values:
                    search = './/html:' + tag + '[@' + key + '="' + value + '"]'
                    for unwanted in self.soup.xpath(search, namespaces=ns):
                        unwanted.getparent().remove(unwanted)

    def add_p_around_text(self):
        '''Add p around text after an hX element
        '''
        for h_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            for h in self.soup.xpath('.//html:' + h_tag, namespaces={'html': 'http://www.w3.org/1999/xhtml'}):
                if h.tail is not None and h.tail.strip() != '':
                    p = etree.Element('{http://www.w3.org/1999/xhtml}p')
                    p.text = h.tail
                    h.tail = None
                    n = h.getnext()
                    while n is not None:
                        if (n.tag == '{http://www.w3.org/1999/xhtml}p' or n.tag == '{http://www.w3.org/1999/xhtml}h3' or n.tag == '{http://www.w3.org/1999/xhtml}div'):
                            break
                        p.append(n)
                        n = n.getnext()

                    h_parent = h.getparent()
                    h_parent.insert(h_parent.index(h) + 1, p)

    def tidy(self):
        """
        Clean up the html document
        """
        self.remove_empty_class()
        self.remove_elements()
        self.add_p_around_text()

        return etree.tostring(self.soup)

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
                logfile.write(entry.message.encode('utf8'))
                logfile.write('\n')

            logfile.write(html.encode('utf8'))
            logfile.close()
            raise ConversionException(
                'transformation failed' + self.orig + '.log')

        return intermediate


class HTMLConverter(HTMLContentConverter):
    def __init__(self, filename, encoding_from_xsl=None):
        f = open(filename)
        HTMLContentConverter.__init__(self, filename, f.read(), encoding_from_xsl)
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
        try:
            doc = Rtf15Reader.read(
                io.BytesIO(content.replace('fcharset256', 'fcharset255')))
        except UnicodeDecodeError:
            raise ConversionException('Unicode problems in ' + self.orig)

        html = XHTMLWriter.write(doc, pretty=True).read()
        xml = etree.fromstring(html)
        xml.tag = 'body'
        htmlElement = etree.Element('html')
        htmlElement.append(xml)
        return etree.tostring(htmlElement)


class DocxConverter(HTMLContentConverter):
    '''Class to convert docx documents to the giellatekno xml format
    '''
    def __init__(self, filename):
        self.orig = filename
        HTMLContentConverter.__init__(self, filename, self.docx2html())

    def docx2html(self):
        '''Convert docx to html, return the converted html
        '''
        parser = Docx2Html(path=self.orig)

        return parser.parsed


class DocConverter(HTMLContentConverter):
    """
    Class to convert Microsoft Word documents to the giellatekno xml format
    """
    def __init__(self, filename):
        self.orig = filename
        HTMLContentConverter.__init__(self, filename, self.doc2html())

    def doc2html(self):
        """Convert the doc file using wvHtml.
        Return the output of the wvHtml
        """
        subp = subprocess.Popen(
            ['wvHtml', self.orig, '-'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        (output, error) = subp.communicate()

        if subp.returncode != 0:
            logfile = open(self.orig + '.log', 'w')
            logfile.write('Error at: ' + str(ccat.lineno()) + '\n')
            logfile.write('Could not process' + self.orig + '\n')
            logfile.write('Stdout from wvHtml: ' + output + '\n\n')
            logfile.write('Stderr from wvHtml: ' + error + '\n')
            raise ConversionException("Conversion from .doc to .html failed. More info in " + self.orig + '.log')

        return output


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

    def compact_ems(self):
        """Replace consecutive em elements divided by white space into
        a single element.
        """
        word = re.compile(u'\w+', re.UNICODE)
        for element in self.etree.iter('p'):
            if len(element.xpath('.//em')) > 1:
                lines = []
                for em in element.iter('em'):
                    next = em.getnext()
                    if (next is not None and next.tag == 'em' and
                            (em.tail is None or not word.search(em.tail))):
                        if em.text is not None:
                            lines.append(em.text.strip())
                        em.getparent().remove(em)
                    else:
                        if em.text is not None:
                            lines.append(em.text.strip())
                        em.text = ' '.join(lines)
                        if em.tail is not None:
                            em.tail = ' ' + em.tail
                        lines = []

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

    def insert_spaces_after_semicolon(self):
        """Insert space after semicolon where needed
        """
        irritating_words_regex = re.compile(u'(govv(a|en|ejeaddji):)([^ ])',
                                            re.UNICODE | re.IGNORECASE)
        for child in self.etree.find('.//body'):
            self.insert_space_after_semicolon(child, irritating_words_regex)

    def insert_space_after_semicolon(self, element, irritating_words_regex):
        if element.text is not None:
            element.text = irritating_words_regex.sub(r'\1 \3', element.text)
        for child in element:
            self.insert_space_after_semicolon(child, irritating_words_regex)
        if element.tail is not None:
            element.tail = irritating_words_regex.sub(r'\1 \3', element.tail)

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

    def make_element(self, eName, text, attributes={}):
        """
        @brief Makes an xml element containing the given name, text and
        attributes. Adds a hyph element if necessary.

        :returns: lxml.etree.Element
        """
        el = etree.Element(eName)
        for key in attributes:
            el.set(key, attributes[key])

        el.text = text

        return el

    def fix_newstags(self):
        """Convert newstags found in text to xml elements
        """
        newstags = re.compile(r'(@*logo:|[\s+\']*@*\s*ingres+[\.:]*|.*@*.*bilde\s*\d*:|\W*(@|LED|bilde)*tekst:|@*foto:|@fotobyline:|@*bildetitt:|<pstyle:bilde>|<pstyle:ingress>|<pstyle:tekst>|@*Samleingress:*|tekst/ingress:|billedtekst:)', re.IGNORECASE)
        titletags = re.compile(r'\s*@m.titt[\.:]|\s*@*stikk:|Mellomtittel:|@*(stikk\.*|under)titt(el)*:|@ttt:|\s*@*[utm]*[:\.]*tit+:|<pstyle:m.titt>|undertittel:', re.IGNORECASE)
        headertitletags = re.compile(r'(\s*@*(led)*tittel:|\s*@*titt(\s\d)*:|@LEDtitt:|<pstyle:tittel>|@*(hoved|over)titt(el)*:)', re.IGNORECASE)
        bylinetags = re.compile(u'(<pstyle:|\s*@*)[Bb]yline[:>]*\s*(\S+:)*',
                                re.UNICODE | re.IGNORECASE)
        boldtags = re.compile(u'@bold\s*:')

        header = self.etree.find('.//header')
        unknown = self.etree.find('.//unknown')

        for em in self.etree.iter('em'):
            paragraph = em.getparent()
            if len(em) == 0 and em.text is not None:

                if bylinetags.match(em.text):
                    line = bylinetags.sub('', em.text).strip()
                    if unknown is not None:
                        person = etree.Element('person')
                        person.set('lastname', line)
                        person.set('firstname', '')
                        unknown.getparent().replace(unknown, person)
                        paragraph.getparent().remove(paragraph)
                elif titletags.match(em.text):
                    em.text = titletags.sub('', em.text).strip()
                    paragraph.set('type', 'title')
                elif newstags.match(em.text):
                    em.text = newstags.sub('', em.text).strip()

        for paragraph in self.etree.iter('p'):
            if len(paragraph) == 0 and paragraph.text is not None:
                index = paragraph.getparent().index(paragraph)
                lines = []

                for line in paragraph.text.split('\n'):
                    if newstags.match(line):
                        if len(lines) > 0:
                            index += 1
                            paragraph.getparent().insert(
                                index,
                                self.make_element('p',
                                                  ' '.join(lines).strip()))
                        lines = []

                        lines.append(newstags.sub('', line))
                    elif bylinetags.match(line):
                        if len(lines) > 0:
                            index += 1
                            paragraph.getparent().insert(
                                index,
                                self.make_element('p',
                                                  ' '.join(lines).strip()))
                        line = bylinetags.sub('', line).strip()

                        if unknown is not None:
                            person = etree.Element('person')
                            person.set('lastname', line)
                            person.set('firstname', '')

                            unknown.getparent().replace(unknown, person)
                            unknown = None

                        lines = []
                    elif boldtags.match(line):
                        if len(lines) > 0:
                            index += 1
                            paragraph.getparent().insert(
                                index,
                                self.make_element('p',
                                                  ' '.join(lines).strip()))
                        line = boldtags.sub('', line).strip()
                        lines = []
                        index += 1
                        p = etree.Element('p')
                        p.append(self.make_element('em', line.strip(),
                                                   {'type': 'bold'}))
                        paragraph.getparent().insert(index, p)
                    elif line.startswith('@kursiv:'):
                        if len(lines) > 0:
                            index += 1
                            paragraph.getparent().insert(
                                index,
                                self.make_element('p',
                                                  ' '.join(lines).strip()))
                        line = line.replace('@kursiv:', '')
                        lines = []
                        index += 1
                        p = etree.Element('p')
                        p.append(self.make_element('em', line.strip(),
                                                   {'type': 'italic'}))
                        paragraph.getparent().insert(index, p)
                    elif headertitletags.match(line):
                        if len(lines) > 0:
                            index += 1
                            paragraph.getparent().insert(
                                index,
                                self.make_element('p',
                                                  ' '.join(lines).strip()))
                        line = headertitletags.sub('', line)
                        lines = []
                        index += 1
                        title = header.find('./title')
                        if title.text is None:
                            title.text = line.strip()
                        paragraph.getparent().insert(
                            index,
                            self.make_element('p', line.strip(),
                                              {'type': 'title'}))
                    elif titletags.match(line):
                        if len(lines) > 0:
                            index += 1
                            paragraph.getparent().insert(
                                index,
                                self.make_element('p',
                                                  ' '.join(lines).strip()))
                        line = titletags.sub('', line)
                        lines = []
                        index += 1
                        paragraph.getparent().insert(
                            index,
                            self.make_element(
                                'p', line.strip(), {'type': 'title'}))
                    elif line == '' and len(lines) > 0:
                        if len(lines) > 0:
                            index += 1
                            paragraph.getparent().insert(
                                index,
                                self.make_element('p',
                                                  ' '.join(lines).strip()))
                        lines = []
                    else:
                        lines.append(line)

                if len(lines) > 0:
                    index += 1
                    paragraph.getparent().insert(
                        index, self.make_element('p',
                                                 ' '.join(lines).strip()))

                paragraph.getparent().remove(paragraph)


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

            logfile.write('Error at: ' + str(ccat.lineno()) + '\n')
            for entry in e.error_log:
                logfile.write(str(entry))
                logfile.write('\n')

            logfile.close()
            raise ConversionException("Syntax error in " + self.filename)

        self.finalXsl = preprocessXslTransformer(
            filexsl,
            commonxsl=
            etree.XSLT.strparam('file://' +
                                resource_filename(__name__,
                                                  'xslt/common.xsl')))

    def get_xsl(self):
        return self.finalXsl

    def get_transformer(self):
        xsltRoot = self.get_xsl()
        try:
            transform = etree.XSLT(xsltRoot)
            return transform
        except etree.XSLTParseError as (e):
            logfile = open(self.filename.replace('.xsl', '') + '.log', 'w')

            logfile.write('Error at: ' + str(ccat.lineno()) + '\n')
            logfile.write('Invalid XML in ' + self.filename + '\n')
            for entry in e.error_log:
                logfile.write(str(entry))
                logfile.write('\n')

            logfile.close()
            raise ConversionException("Invalid XML in " + self.filename)


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
                paragraph.set('{http://www.w3.org/XML/1998/namespace}lang',
                              lang)

            for element in paragraph.iter("span"):
                if element.get("type") == "quote":
                    if element.text is not None:
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
                self.set_paragraph_language(paragraph)


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
        return (1.0 * self.get_unknown_wordcount() /
                self.get_mainlang_wordcount())

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
        (output, error) = subp.communicate(
            self.get_preprocessed_mainlang_words())

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
        parents=[argparse_version.parser],
        description='Convert original files to giellatekno xml.')

    parser.add_argument(u'--serial',
                        action=u"store_true",
                        help=u"use this for debugging the conversion \
                        process. When this argument is used files will \
                        be converted one by one.")
    parser.add_argument(u'--write-intermediate',
                        action=u"store_true",
                        help=u"Write the intermediate XML representation \
                        to ORIGFILE.im.xml, for debugging the XSLT.\
                        (Has no effect if the converted file already exists.)")
    parser.add_argument('sources',
                        nargs='+',
                        help="The original file(s) or \
                        directory/ies where the original files exist")

    args = parser.parse_args()
    return args


def worker(args, xsl_file):
    orig_file = xsl_file[:-4]
    if os.path.exists(orig_file) and not orig_file.endswith('.xsl'):
        conv = Converter(orig_file, args.write_intermediate)

        try:
            conv.write_complete()
        except ConversionException as e:
            print >>sys.stderr, 'Could not convert', orig_file
            print >>sys.stderr, e.parameter
    else:
        print >>sys.stderr, orig_file, 'does not exist'


def convert_in_parallel(args, xsl_files):
    pool_size = multiprocessing.cpu_count() * 2
    pool = multiprocessing.Pool(processes=pool_size,)
    pool.map(functools.partial(worker, args),
             xsl_files)
    pool.close()
    pool.join()


def convert_serially(args, xsl_files):
    for xsl_file in xsl_files:
        print 'converting', xsl_file[:-4]
        worker(args, xsl_file)


def collect_files(source_dir):
    xsl_files = []
    for root, dirs, files in os.walk(source_dir):
        for f in files:
            if f.endswith('.xsl'):
                xsl_files.append(os.path.join(root, f))

    return xsl_files


def sanity_check():
    util.sanity_check([u'wvHtml', u'pdftotext'])
    if not os.path.isfile(Converter.get_dtd_location()):
        raise util.SetupException(
            "Couldn't find %s\n"
            "Check that GTHOME points at the right directory (currently: %s)."
            % (Converter.get_dtd_location(),
               os.environ['GTHOME']))


def main():
    sanity_check()
    args = parse_options()

    for source in args.sources:
        if os.path.isfile(source):
            xsl_file = source + '.xsl'
            if os.path.isfile(xsl_file):
                worker(args, xsl_file)
            else:
                xsl_stream = open(xsl_file, 'w')
                xsl_stream.write(
                    resource_string(__name__, 'xslt/XSL-template.xsl'))
                xsl_stream.close()
                print "Fill in meta info in", xsl_file, \
                    ', then run this command again'
                sys.exit(1)
        elif os.path.isdir(source):
            if args.serial:
                convert_serially(args, collect_files(source))
            else:
                convert_in_parallel(args, collect_files(source))
        else:
            print >>sys.stderr, 'Can not process', source
            print >>sys.stderr, 'This is neither a file nor a directory.'
