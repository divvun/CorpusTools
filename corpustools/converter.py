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
#   Copyright © 2012-2015 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

from __future__ import print_function

import argparse
import codecs
from copy import deepcopy
import distutils.dep_util
import distutils.spawn
import io
import multiprocessing
import os
import re
import sys

from lxml import etree
from lxml.html import clean
from lxml.html import html5parser
from odf.odf2xhtml import ODF2XHTML
from pyth.plugins.rtf15.reader import Rtf15Reader
from pyth.plugins.xhtml.writer import XHTMLWriter
from pydocx.export import PyDocXHTMLExporter

import argparse_version
import ccat
import decode
import errormarkup
import text_cat
import util
import xslsetter


here = os.path.dirname(__file__)


class ConversionException(Exception):
    pass


class Converter(object):

    '''Take care of data common to all Converter classes'''

    def __init__(self, filename, write_intermediate=False):
        codecs.register_error('mixed', self.mixed_decoder)
        self.orig = os.path.abspath(filename)
        self.write_intermediate = write_intermediate
        try:
            self.md = xslsetter.MetadataHandler(self.xsl, create=True)
        except xslsetter.XsltException as e:
            raise ConversionException(e)

        self.fix_lang_genre_xsl()
        if not os.path.exists(self.tmpdir):
            os.mkdir(self.tmpdir)

    @property
    def dependencies(self):
        return [self.orig, self.xsl]

    @property
    def logfile(self):
        '''The name of the logfile'''
        return self.orig + '.log'

    @property
    def orig(self):

        return self.__orig

    @orig.setter
    def orig(self, orig):
        self.__orig = orig

    @property
    def write_intermediate(self):
        return self.__write_intermediate

    @write_intermediate.setter
    def write_intermediate(self, write_intermediate):
        self.__write_intermediate = write_intermediate

    def convert2intermediate(self):
        raise NotImplementedError(
            'You have to subclass and override convert2intermediate')

    @staticmethod
    def get_dtd_location():
        return os.path.join(here, 'dtd/corpus.dtd')

    def validate_complete(self, complete):
        '''Validate the complete document'''
        dtd = etree.DTD(Converter.get_dtd_location())

        if not dtd.validate(complete):
            with open(self.logfile, 'w') as logfile:
                logfile.write('Error at: {}'.format(str(util.lineno())))
                for entry in dtd.error_log:
                    logfile.write('\n')
                    logfile.write(str(entry))
                    logfile.write('\n')
                util.print_element(complete, 0, 4, logfile)

            raise ConversionException(
                '{}: Not valid XML. More info in the log file: '
                '{}'.format(type(self).__name__, self.logfile))

    def maybe_write_intermediate(self, intermediate):
        if not self.write_intermediate:
            return
        im_name = self.orig + '.im.xml'
        with open(im_name, 'w') as im_file:
            im_file.write(etree.tostring(intermediate,
                                         encoding='utf8',
                                         pretty_print='True'))

    def transform_to_complete(self):
        '''Combine the intermediate xml document with its medatata.'''
        intermediate = self.convert2intermediate()

        self.maybe_write_intermediate(intermediate)

        try:
            xm = XslMaker(self.xsl)
            complete = xm.transformer(intermediate)

            return complete.getroot()
        except etree.XSLTApplyError as e:
            with open(self.logfile, 'w') as logfile:
                logfile.write('Error at: {}'.format(str(util.lineno())))
                for entry in e.error_log:
                    logfile.write(str(entry))
                    logfile.write('\n')

            raise ConversionException("Check the syntax in: {}".format(
                self.xsl))

    def convert_errormarkup(self, complete):
        if 'correct.' in self.orig:
            try:
                em = errormarkup.ErrorMarkup(self.orig)

                for element in complete.find('body'):
                    em.add_error_markup(element)
            except IndexError as e:
                with open(self.logfile, 'w') as logfile:
                    logfile.write('Error at: {}'.format(str(util.lineno())))
                    logfile.write("There is a markup error\n")
                    logfile.write("The error message: ")
                    logfile.write(str(e))
                    logfile.write("\n\n")
                    logfile.write("This is the xml tree:\n")
                    logfile.write(etree.tostring(complete,
                                                 encoding='utf8',
                                                 pretty_print=True))
                    logfile.write('\n')

                raise ConversionException(
                    u"Markup error. More info in the log file: {}".format(
                        self.logfile))

    def fix_document(self, complete):
        fixer = DocumentFixer(complete)

        fixer.fix_newstags()
        fixer.soft_hyphen_to_hyph_tag()
        fixer.set_word_count()
        fixer.detect_quotes()

        if (complete.
            attrib['{http://www.w3.org/XML/1998/namespace}lang'] in
                ['sma', 'sme', 'smj', 'smn', 'sms', 'nob', 'fin', 'swe',
                 'nno', 'dan', 'fkv', 'sju', 'sje']):
            fixer.fix_body_encoding()

    mixed_to_unicode = {
        'e4': u'ä',
        '85': u'…',            # u'\u2026' ... character.
        '96': u'–',            # u'\u2013' en-dash
        '97': u'—',            # u'\u2014' em-dash
        '91': u"‘",            # u'\u2018' left single quote
        '92': u"’",            # u'\u2019' right single quote
        '93': u'“',            # u'\u201C' left double quote
        '94': u'”',            # u'\u201D' right double quote
        '95': u"•"             # u'\u2022' bullet
    }

    def mixed_decoder(self, decode_error):
        badstring = decode_error.object[decode_error.start:decode_error.end]
        badhex = badstring.encode('hex')
        repl = self.mixed_to_unicode.get(badhex, u'\ufffd')
        if repl == u'\ufffd':   # � unicode REPLACEMENT CHARACTER
            print("Skipped bad byte \\x{}, seen in {}".format(
                badhex, self.orig))
        return repl, (decode_error.start + len(repl))

    def make_complete(self, languageGuesser):
        '''Make a complete giellatekno xml file

        Combine the intermediate giellatekno xml file and the metadata into
        a complete giellatekno xml file.
        Fix the character encoding
        Detect the languages in the xml file
        '''
        complete = self.transform_to_complete()
        self.validate_complete(complete)
        self.convert_errormarkup(complete)
        self.fix_document(complete)
        ld = LanguageDetector(complete, languageGuesser)
        ld.detect_language()

        return complete

    def write_complete(self, languageguesser):
        if distutils.dep_util.newer_group(
                self.dependencies, self.converted_name):
            self.makedirs()

            if (('goldstandard' in self.orig and '.correct.' in self.orig) or
                    'goldstandard' not in self.orig):
                complete = self.make_complete(languageguesser)

                xml_printer = ccat.XMLPrinter(all_paragraphs=True,
                                              hyph_replacement=None)
                xml_printer.etree = etree.ElementTree(complete)
                text = xml_printer.process_file().getvalue()

                if len(text) > 0:
                    with open(self.converted_name, 'w') as converted:
                        converted.write(etree.tostring(complete,
                                                       encoding='utf8',
                                                       pretty_print='True'))
                else:
                    print(self.orig, "has no text", file=sys.stderr)

    def makedirs(self):
        '''Make the converted directory.'''
        try:
            os.makedirs(os.path.dirname(self.converted_name))
        except OSError:
            pass

    @property
    def xsl(self):
        return self.orig + '.xsl'

    @property
    def tmpdir(self):
        if self.corpusdir == os.path.dirname(self.orig):
            return self.corpusdir
        else:
            return os.path.join(self.corpusdir, 'tmp')

    @property
    def corpusdir(self):
        orig_pos = self.orig.find('orig/')
        if orig_pos != -1:
            return os.path.dirname(self.orig[:orig_pos])
        else:
            return os.path.dirname(self.orig)

    def fix_lang_genre_xsl(self):
        '''Set the mainlang and genre variables in the xsl file, if possible'''
        origname = self.orig.replace(self.corpusdir, '')
        if origname.startswith('/orig'):
            to_write = False
            parts = origname[1:].split('/')

            lang = self.md.get_variable('mainlang')

            if lang == "":
                to_write = True
                lang = parts[1]
                self.md.set_variable('mainlang', lang)

            genre = self.md.get_variable('genre')

            if genre == "" and parts[2] != os.path.basename(self.orig):
                to_write = True
                genre = parts[2]
                self.md.set_variable('genre', genre)
            if to_write:
                self.md.write_file()

    @property
    def converted_name(self):
        '''Get the name of the converted file'''
        orig_pos = self.orig.find('orig/')
        if orig_pos != -1:
            return self.orig.replace(
                '/orig/', '/converted/') + '.xml'
        else:
            return self.orig + '.xml'

    def extract_text(self, command):
        '''Extract the text from a document.

        :command: a list containing the command and the arguments sent to
        ExternalCommandRunner.
        :returns: a utf-8 encoded string containing the content of the document
        '''
        runner = util.ExternalCommandRunner()
        runner.run(command, cwd=self.tmpdir)

        if runner.returncode != 0:
            with open(self.logfile, 'w') as logfile:
                print('stdout\n{}\n'.format(runner.stdout), file=logfile)
                print('stderr\n{}\n'.format(runner.stderr), file=logfile)
                raise ConversionException(
                    '{} failed. More info in the log file: {}'.format(
                        command[0], self.logfile))

        return runner.stdout

    def handle_syntaxerror(self, e, lineno, invalid_input):
        with open(self.logfile, 'w') as logfile:
            logfile.write('Error at: {}'.format(lineno))
            for entry in e.error_log:
                logfile.write('\n{}: {} '.format(
                    str(entry.line), str(entry.column)))
                try:
                    logfile.write(entry.message)
                except ValueError:
                    logfile.write(entry.message.encode('latin1'))

                logfile.write('\n')

            logfile.write(invalid_input.encode('utf8'))

        raise ConversionException(
            "{}: log is found in {}".format(type(self).__name__, self.logfile))


class AvvirConverter(Converter):

    '''Convert Ávvir xml files to the giellatekno xml format.

    The root node in an Ávvir document is article.
    article nodes contains one or more story nodes.
    story nodes contain one or more p nodes.
    p nodes contain span, br and (since 2013) p nodes.
    '''

    def __init__(self, filename, write_intermediate=False):
        super(AvvirConverter, self).__init__(filename,
                                             write_intermediate)

    def convert2intermediate(self):
        '''Convert an Ávvir xml to an intermediate xml document.'''
        self.intermediate = etree.fromstring(open(self.orig).read())
        self.convert_p()
        self.convert_story()
        self.convert_article()

        return self.intermediate

    @staticmethod
    def insert_element(p, text, position):
        '''Insert a new element in p's parent

        Arguments:
            p: an lxml element, it is a story/p element
            text: (unicode) string
            position: (integer) the position inside p's parent where the new
                      element is inserted

        Returns:
            position: (integer)
        '''
        if text is not None and text.strip() != '':
            new_p = etree.Element('p')
            new_p.text = text
            grandparent = p.getparent()
            grandparent.insert(grandparent.index(p) + position, new_p)
            position += 1

        return position

    @staticmethod
    def convert_sub_p(p):
        '''Convert p element found inside story/p elements

        These elements contain erroneous text that an editor has removed.
        This function removes p.text and saves p.tail

        Arguments:
            p: an lxml element, it is a story/p element
        '''
        for sub_p in p.findall('.//p'):
            previous = sub_p.getprevious()
            if previous is None:
                parent = sub_p.getparent()
                if sub_p.tail is not None:
                    if parent.text is not None:
                        parent.text = parent.text + sub_p.tail
                    else:
                        parent.text = sub_p.tail
            else:
                if sub_p.tail is not None:
                    if previous.tail is not None:
                        previous.tail = previous.tail + sub_p.tail
                    else:
                        previous.tail = sub_p.tail
            p.remove(sub_p)

    def convert_subelement(self, p):
        '''Convert subelements of story/p elements to p elements

        Arguments:
            p: an lxml element, it is a story/p element
        '''
        position = 1
        for subelement in p:
            position = self.insert_element(p, subelement.text, position)

            for subsubelement in subelement:
                for text in [subsubelement.text, subsubelement.tail]:
                    position = self.insert_element(p, text, position)

            position = self.insert_element(p, subelement.tail, position)

            p.remove(subelement)

    def convert_p(self):
        '''Convert story/p elements to one or more p elements'''
        for p in self.intermediate.findall('./story/p'):
            if p.get("class") is not None:
                del p.attrib["class"]

            self.convert_sub_p(p)
            self.convert_subelement(p)

            if p.text is None or p.text.strip() == '':
                story = p.getparent()
                story.remove(p)

    def convert_story(self):
        '''Convert story elements in to giellatekno xml elements'''
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
        '''The root element of an Ávvir doc is article, rename it to body'''
        self.intermediate.tag = 'body'
        document = etree.Element('document')
        document.append(self.intermediate)
        self.intermediate = document


class SVGConverter(Converter):

    '''Convert SVG files to the giellatekno xml format.'''

    def __init__(self, filename, write_intermediate=False):
        super(SVGConverter, self).__init__(filename,
                                           write_intermediate)

    def convert2intermediate(self):
        '''Transform svg to an intermediate xml document'''
        svgXsltRoot = etree.parse(os.path.join(here, 'xslt/svg2corpus.xsl'))
        transform = etree.XSLT(svgXsltRoot)
        doc = etree.parse(self.orig)
        intermediate = transform(doc)

        return intermediate.getroot()


class PlaintextConverter(Converter):

    '''Convert plain text files to the giellatekno xml format.'''

    def __init__(self, filename, write_intermediate=False):
        super(PlaintextConverter, self).__init__(filename,
                                                 write_intermediate)

    def to_unicode(self):
        '''Read a file into a unicode string.

        If the content of the file is not utf-8, pretend the encoding is
        latin1. The real encoding (for sma, sme and smj) will be detected
        later.

        :returns: a unicode string
        '''
        try:
            content = codecs.open(self.orig, encoding='utf8').read()
        except ValueError:
            content = codecs.open(self.orig, encoding='latin1').read()

        content = self.strip_chars(content)

        return content

    def strip_chars(self, content, extra=u''):
        plaintext_oddities = [
            (u'ÊÊ', u'\n'),
            (u'<\!q>', u''),
            (u'<\!h>', u''),
            (u'<*B>', u''),
            (u'<*P>', u''),
            (u'<*I>', u''),
            (u'\r', u'\n'),
            (u'<ASCII-MAC>', ''),
            (u'<vsn:3.000000>', u''),
            (u'<0x010C>', u'Č'),
            (u'<0x010D>', u'č'),
            (u'<0x0110>', u'Đ'),
            (u'<0x0111>', u'đ'),
            (u'<0x014A>', u'Ŋ'),
            (u'<0x014B>', u'ŋ'),
            (u'<0x0160>', u'Š'),
            (u'<0x0161>', u'š'),
            (u'<0x0166>', u'Ŧ'),
            (u'<0x0167>', u'ŧ'),
            (u'<0x017D>', u'Ž'),
            (u'<0x017E>', u'ž'),
            (u'<0x2003>', u' '),
        ]
        content = util.replace_all(plaintext_oddities, content)
        remove_re = re.compile(
            u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F{}]'.format(extra))
        content, count = remove_re.subn('', content)

        return content

    def make_element(self, eName, text):
        '''Makes an xml element.

        :param eName: Name of the xml element
        :param text: The text the xml should contain
        :param attributes: The attributes the element should have

        :returns: lxml.etree.Element
        '''
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


class PDFTextExtractor(object):
    LIST_CHARS = [u'•']

    def __init__(self):
        self.body = etree.Element('body')
        self.p = etree.Element('p')

    def replace_list_chars(self):
        if self.get_last_string().startswith(u'•'):
            if self.p.text is None:
                self.p[0].text = re.sub(u'•\s*', '', self.p[0].text)
            else:
                self.p.text = re.sub(u'•\s*', '', self.p.text)

            self.p.set('type', 'listitem')

    def append_to_body(self):
        self.replace_list_chars()
        self.body.append(self.p)
        self.p = etree.Element('p')

    def append_text_to_p(self, text):
        '''text is a string'''
        if len(self.p) == 0 and self.p.text is None:
            self.p.text = text
        elif len(self.p) == 0 and self.p.text is not None:
            self.p.text += text
        if len(self.p) > 0:
            last = self.p[-1]
            if last.tail is None:
                last.tail = text
            else:
                last.tail += text

    def extract_textelement(self, textelement):
        '''Convert one <text> element to an array of text and etree Elements.

        A <text> element can contain <i> and <b> elements.

        <i> elements can contain <b> and <a> elements.
        <b> elements can contain <i> and <a> elements.

        The text and tail parts of the elements contained in the <i> and <b>
        elements become the text parts of <i> and <b> elements.
        '''

        # print(util.lineno(), etree.tostring(textelement), file=sys.stderr)
        if textelement.text is not None:
            self.append_text_to_p(textelement.text)

        for child in textelement:
            em = etree.Element('em')

            if child.text is not None:
                em.text = child.text
            else:
                em.text = ''

            if len(child) > 0:
                for grandchild in child:
                    if grandchild.text is not None:
                        em.text += grandchild.text
                    if grandchild.tail is not None:
                        em.text += grandchild.tail

            if child.tag == 'i':
                em.set('type', 'italic')
            elif child.tag == 'b':
                em.set('type', 'bold')

            em.tail = child.tail

            self.p.append(em)

    def get_last_string(self):
        '''Get the last string of self.parts'''
        return self.p.xpath("string()")

    def handle_line_ending(self):
        '''Add a soft hyphen or a space at the end of self.p'''
        p_content = self.p.xpath("string()")
        if re.search('\S-$', p_content):
            if len(self.p) == 0:
                self.p.text = self.p.text[:-1] + u'\xAD'
            else:
                last = self.p[-1]
                if last.tail is None:
                    last.text = last.text[:-1] + u'\xAD'
                else:
                    last.tail = last.tail[:-1] + u'\xAD'
        elif not re.search(u'[ \xAD]$', p_content):
            self.extract_textelement(etree.fromstring('<text> </text>'))


class PDF2XMLConverter(Converter):
    '''Class to convert the xml output of pdftohtml to giellatekno xml'''
    def __init__(self, filename, write_intermediate=False):
        super(PDF2XMLConverter, self).__init__(filename,
                                               write_intermediate)
        self.extractor = PDFTextExtractor()
        self.in_list = False
        self.prev_t = None

    def strip_chars(self, content, extra=u''):
        remove_re = re.compile(u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F{}]'.format(
            extra))
        content, count = remove_re.subn('', content)

        # Microsoft Word PDF's have Latin-1 file names in links; we
        # don't actually need any link attributes:
        content = re.sub(r'<a [^>]+>', '<a>', content)

        return content

    def replace_ligatures(self, content):
        '''document is a stringified xml document'''
        replacements = {
            "[dstrok]": "đ",
            "[Dstrok]": "Đ",
            "[tstrok]": "ŧ",
            "[Tstrok]": "Ŧ",
            "[scaron]": "š",
            "[Scaron]": "Š",
            "[zcaron]": "ž",
            "[Zcaron]": "Ž",
            "[ccaron]": "č",
            "[Ccaron]": "Č",
            "[eng": "ŋ",
            " ]": "",
            "Ď": "đ",  # cough
            "ď": "đ",  # cough
            "ﬁ": "fi",
            "ﬂ": "fl",
            "ﬀ": "ff",
            "ﬃ": "ffi",
            "ﬄ": "ffl",
            "ﬅ": "ft",
        }

        for key, value in replacements.items():
            content = content.replace(key + ' ', value)
            content = content.replace(key, value)

        return content

    def convert2intermediate(self):
        document = etree.Element('document')
        etree.SubElement(document, 'header')
        document.append(self.extractor.body)

        command = ['pdftohtml', '-hidden', '-enc', 'UTF-8', '-stdout',
                   '-nodrm', '-i', '-xml', self.orig]
        pdf_content = self.replace_ligatures(self.strip_chars(
            self.extract_text(command)))

        try:
            root_element = etree.fromstring(pdf_content)
        except etree.XMLSyntaxError as e:
            self.handle_syntaxerror(e, util.lineno(),
                                    pdf_content.decode('utf-8'))

        self.parse_pages(root_element)

        return document

    def get_coefficient(self, margin, page_number):
        '''Get the width of the margin in percent'''
        coefficient = 7
        if margin in self.md.margins.keys():
            m = self.md.margins[margin]
            if m.get(page_number) is not None:
                coefficient = m[page_number.strip()]
            elif m.get('all') is not None:
                coefficient = m['all']
            elif int(page_number) % 2 == 0 and m.get('even') is not None:
                coefficient = m['even']
            elif int(page_number) % 2 == 1 and m.get('odd') is not None:
                coefficient = m['odd']

        return coefficient

    def get_inner_coefficient(self, margin, page_number):
        '''Get the width of the margin in percent'''
        coefficient = 0
        if margin in self.md.inner_margins.keys():
            m = self.md.inner_margins[margin]
            if m.get(page_number) is not None:
                coefficient = m[page_number.strip()]
            elif m.get('all') is not None:
                coefficient = m['all']
            elif int(page_number) % 2 == 0 and m.get('even') is not None:
                coefficient = m['even']
            elif int(page_number) % 2 == 1 and m.get('odd') is not None:
                coefficient = m['odd']

        return coefficient

    def compute_margins(self, page):
        '''Compute the margins of a page in pixels.

        :param page: a pdf2xml page element

        :returns: a dict containing the four margins in pixels
        '''
        margins = {margin: self.compute_margin(margin, page)
                   for margin in ['right_margin', 'left_margin', 'top_margin',
                                  'bottom_margin']}

        return margins

    def compute_inner_margins(self, page):

        margins = {margin: self.compute_inner_margin(margin, page)
                   for margin in ['inner_right_margin', 'inner_left_margin',
                                  'inner_top_margin', 'inner_bottom_margin']}

        if (margins['inner_bottom_margin'] == int(page.get('height')) and
                margins['inner_top_margin'] == 0 and
                margins['inner_left_margin'] == 0 and
                margins['inner_right_margin'] == int(page.get('width'))):
            margins = {}

        return margins

    def compute_margin(self, margin, page):
        '''Compute a margin in pixels.

        :param margin: the name of the  margin
        :param page: a pdf2xml page element

        :return: an int telling where the margin is on the page.
        '''
        page_width = int(page.get('width'))
        page_height = int(page.get('height'))
        coefficient = self.get_coefficient(margin, page.get('number'))
        # print(util.lineno(), margin, page_height, page_width, coefficient, file=sys.stderr)

        if margin == 'left_margin':
            return int(coefficient * page_width / 100)
        if margin == 'right_margin':
            return int(page_width - coefficient * page_width / 100)
        if margin == 'top_margin':
            return int(coefficient * page_height / 100)
        if margin == 'bottom_margin':
            return int(page_height - coefficient * page_height / 100)

    def compute_inner_margin(self, margin, page):
        '''Compute a margin in pixels.

        :param margin: the name of the margin
        :param page: a pdf2xml page element

        :return: an int telling where the margin is on the page.
        '''
        page_width = int(page.get('width'))
        page_height = int(page.get('height'))
        coefficient = self.get_inner_coefficient(margin, page.get('number'))

        if margin == 'inner_left_margin':
            return int(coefficient * page_width / 100)
        if margin == 'inner_right_margin':
            return int(page_width - coefficient * page_width / 100)
        if margin == 'inner_top_margin':
            return int(coefficient * page_height / 100)
        if margin == 'inner_bottom_margin':
            return int(page_height - coefficient * page_height / 100)

    def is_text_on_same_line(self, text):
        if self.prev_t is None:
            return True

        h1 = float(self.prev_t.get('height'))
        t1 = float(self.prev_t.get('top'))
        t2 = float(text.get('top'))

        return t1 + h1 > t2 and t1 - h1 < t2

    def is_text_in_same_paragraph(self, text):
        h1 = float(self.prev_t.get('height'))
        h2 = float(text.get('height'))

        delta = float(text.get('top')) - float(self.prev_t.get('top'))
        ratio = 1.5

        return h1 == h2 and delta < ratio * h1 and delta > 0

    def is_same_paragraph(self, text):
        '''Find out if text belongs in the same paragraph as self.prev_t.

        Define the incoming text elements text1 and self.prev_t to belong to
        the same paragraph if they have the same height and if the difference
        between the top attributes is less than ratio times the height of
        the text elements.
        '''
        same_paragraph = False

        h1 = float(self.prev_t.get('height'))
        h2 = float(text.get('height'))
        t1 = int(self.prev_t.get('top'))
        t2 = int(text.get('top'))
        # util.print_frame(
        #    debug='{} {} {} {} {} {}'.format(h1, h2, t1, t2, h1 == h2, t1 > t2))
        real_text = etree.tostring(text, method='text', encoding='unicode')

        if self.is_text_in_same_paragraph(text):
            if (real_text[0] in self.extractor.LIST_CHARS):
                self.in_list = True
                # util.print_frame(debug=text.text)
            elif (re.match('\s', real_text[0]) is None and
                  real_text[0] == real_text[0].upper() and self.in_list):
                self.in_list = False
                same_paragraph = False
                # util.print_frame(debug=text.text)
            elif (real_text[0] not in self.extractor.LIST_CHARS):
                # util.print_frame()
                same_paragraph = True
        elif (h1 == h2 and t1 >= t2 and not re.match('\d', real_text[0]) and
              real_text[0] == real_text[0].lower()):
            # util.print_frame()
            same_paragraph = True
        else:
            # util.print_frame()
            self.in_list = False

        return same_paragraph

    def find_footnotes_superscript(self, page):
        '''Search for text elements containing potential footnotes.

        :return superscripts: a list of potential footnotes.
        '''
        superscripts = []
        for t in page.iter('text'):
            try:
                int(t.xpath("string()").strip())
                superscripts.append(t)
            except ValueError:
                pass

        return superscripts

    @staticmethod
    def has_content(element):
        '''True if an element either has text or contains another element'''
        return element.text is not None or len(element) > 0

    def remove_footnotes_superscript(self, page):
        '''Remove numbers from elements found by find_footnotes_superscript.'''
        for superscript in self.find_footnotes_superscript(page):
            previous_element = superscript.getprevious()
            if (previous_element is not None and
                    self.has_content(previous_element) and
                    int(previous_element.get('top')) >=
                    int(superscript.get('top'))):
                if len(superscript) > 0:
                    superscript[-1].text = re.sub('\d+', '', superscript[-1].text)
                else:
                    superscript.text = re.sub('\d+', '', superscript.text)

    def parse_page(self, page):
        '''Parse the page element.'''
        self.remove_elements_not_within_margin(page)
        self.remove_footnotes_superscript(page)
        self.extract_text_from_page(page)

    def remove_elements_not_within_margin(self, page):
        margins = self.compute_margins(page)
        inner_margins = self.compute_inner_margins(page)
        for t in page.iter('text'):
            if not self.is_inside_margins(t, margins):
                t.getparent().remove(t)
            elif (len(inner_margins) > 0 and
                  self.is_inside_inner_margins(t, inner_margins)):
                t.getparent().remove(t)

    def extract_text_from_page(self, page):
        '''Decide which text elements are sent to extract_textelement

        When t elements is on the same line as self.prev_t, allow empty elements or
        elements containing only whitespace

        If t is not on the same line as self.prev_t, do not not use them
        '''
        for t in page.iter('text'):
            if int(t.get('width')) > 0:
                if self.is_text_on_same_line(t):
                    self.extractor.extract_textelement(t)
                    self.prev_t = t
                elif len(t.xpath("string()").strip()) > 0:
                    if (self.prev_t is not None and
                            not self.is_same_paragraph(t) and
                            len(self.extractor.p.xpath("string()")) > 0):
                        self.extractor.append_to_body()
                    else:
                        self.extractor.handle_line_ending()
                    self.extractor.extract_textelement(t)
                    self.prev_t = t

        # If the last string on a page is the end of a sentence,
        # wrap self.parts into a paragraph
        if len(self.extractor.p.xpath("string()")) > 0:
            last_string = self.extractor.get_last_string()
            if re.search(u'[.?!]$', last_string):
                self.extractor.append_to_body()

    def is_inside_margins(self, t, margins):
        '''Check if t is inside the given margins

        t is a text element
        '''
        return (int(t.get('top')) > margins['top_margin'] and
                int(t.get('top')) < margins['bottom_margin'] and
                int(t.get('left')) > margins['left_margin'] and
                int(t.get('left')) < margins['right_margin'])

    def is_inside_inner_margins(self, t, margins):
        '''Check if t is inside the given margins

        t is a text element
        '''
        return (int(t.get('top')) > margins['inner_top_margin'] and
                int(t.get('top')) < margins['inner_bottom_margin'] and
                int(t.get('left')) > margins['inner_left_margin'] and
                int(t.get('left')) < margins['inner_right_margin'])

    @staticmethod
    def is_skip_page(page_number, skip_pages):
        '''True if a page should be skipped, otherwise false'''
        return (('odd' in skip_pages and (page_number % 2) == 1) or
                ('even' in skip_pages and (page_number % 2) == 0) or
                page_number in skip_pages)

    def parse_pages(self, root_element):
        skip_pages = self.md.skip_pages
        for page in root_element.iter('page'):
            if not self.is_skip_page(int(page.get('number')), skip_pages):
                self.parse_page(page)

        if len(self.extractor.get_last_string()) > 0:
            self.extractor.append_to_body()


class BiblexmlConverter(Converter):

    '''Convert bible xml files to the giellatekno xml format'''

    def __init__(self, filename, write_intermediate=False):
        super(BiblexmlConverter, self).__init__(filename,
                                                write_intermediate)

    def convert2intermediate(self):
        '''Convert the bible xml to intermediate giellatekno xml format'''
        document = etree.Element('document')
        document.append(self.process_bible())

        return document

    def process_verse(self, verse_element):
        if verse_element.tag != 'verse':
            raise UserWarning(
                '{}: Unexpected element in verse: {}'.format(
                    self.orig, verse_element.tag))

        return verse_element.text

    def process_section(self, section_element):
        section = etree.Element('section')

        title = etree.Element('p')
        title.set('type', 'title')
        title.text = section_element.get('title')

        section.append(title)

        verses = []
        for element in section_element:
            if element.tag == 'p':
                if len(verses) > 0:
                    section.append(self.make_p(verses))
                    verses = []
                section.append(self.process_p(element))
            elif element.tag == 'verse':
                text = self.process_verse(element)
                if text is not None:
                    verses.append(text)
            else:
                raise UserWarning(
                    '{}: Unexpected element in section: {}'.format(
                        self.orig, element.tag))

        section.append(self.make_p(verses))

        return section

    def process_p(self, p):
        verses = []
        for child in p:
            text = self.process_verse(child)
            if text is not None:
                verses.append(text)

        p = etree.Element('p')
        p.text = '\n'.join(verses)

        return p

    @staticmethod
    def make_p(verses):
        p = etree.Element('p')
        p.text = '\n'.join(verses)

        return p

    def process_chapter(self, chapter_element):
        section = etree.Element('section')

        text_parts = []
        if chapter_element.get('number') is not None:
            text_parts.append(chapter_element.get('number'))
        if chapter_element.get('title') is not None:
            text_parts.append(chapter_element.get('title'))

        title = etree.Element('p')
        title.set('type', 'title')
        title.text = ' '.join(text_parts)

        section.append(title)

        for child in chapter_element:
            if child.tag == 'section':
                section.append(self.process_section(child))
            elif child.tag == 'verse':
                p = etree.Element('p')
                p.text = child.text
                section.append(p)
            else:
                raise UserWarning(
                    '{}: Unexpected element in chapter: {}'.format(
                        self.orig, child.tag))

        return section

    def process_book(self, book_element):
        section = etree.Element('section')

        title = etree.Element('p')
        title.set('type', 'title')
        title.text = book_element.get('title')

        section.append(title)

        for chapter_element in book_element:
            if chapter_element.tag != 'chapter':
                raise UserWarning(
                    '{}: Unexpected element in book: {}'.format(
                        self.orig, chapter_element.tag))
            section.append(self.process_chapter(chapter_element))

        return section

    def process_bible(self):
        bible = etree.parse(self.orig)

        body = etree.Element('body')

        for book in bible.xpath('.//book'):
            body.append(self.process_book(book))

        return body


class HTMLContentConverter(Converter):

    '''Convert html documents to the giellatekno xml format.'''

    def __init__(self, filename, write_intermediate=False, content=None):
        '''Clean up content, then convert it to xhtml using html5parser'''
        super(HTMLContentConverter, self).__init__(filename,
                                                   write_intermediate)
        cleaner = clean.Cleaner(
            page_structure=False,
            scripts=True,
            javascript=True,
            comments=True,
            style=True,
            processing_instructions=True,
            remove_unknown_tags=True,
            embedded=True,
            remove_tags=[
                'img',
                'area',
                'hr',
                'cite',
                'footer',
                'figcaption',
                'aside',
                'time',
                'figure',
                'nav',
                'noscript',
                'map',
                'ins',
                's',
            ])

        decoded = self.to_unicode(content)
        semiclean = self.remove_cruft(decoded)
        superclean = cleaner.clean_html(semiclean)

        self.soup = html5parser.document_fromstring(superclean)
        self.convert2xhtml()
        self.converter_xsl = os.path.join(here, 'xslt/xhtml2corpus.xsl')

    def remove_cruft(self, content):
        '''from svenskakyrkan.se documents'''
        replacements = [
            (u'//<script', u'<script'),
            (u'&nbsp;', u' '),
            (u' ', u' '),
        ]
        return util.replace_all(replacements, content)

    def to_unicode(self, content):
        return self.remove_declared_encoding(
            self.try_decode_encodings(content))

    def try_decode_encodings(self, content):
        if type(content) == unicode:
            return content
        assert type(content) == str
        found = self.get_encoding(content)
        more_guesses = [(c, 'guess')
                        for c in ["utf-8", "windows-1252"]
                        if c != found[0]]
        errors = []
        for encoding, source in [found] + more_guesses:
            try:
                decoded = unicode(content, encoding=encoding)
                return decoded
            except UnicodeDecodeError as e:
                if source == 'xsl':
                    with open('{}.log'.format(self.orig), 'w') as f:
                        print(util.lineno(), str(e), self.orig, file=f)
                    raise ConversionException(
                        'The text_encoding specified in {} lead to decoding '
                        'errors, please fix the XSL'.format(self.md.filename))
                else:
                    errors.append(e)
        if errors != []:
            # If no "clean" encoding worked, we just skip the bad bytes:
            return unicode(content, encoding='utf-8', errors='mixed')
        else:
            raise ConversionException(
                "Strange exception converting {} to unicode".format(self.orig))

    xml_encoding_declaration_re = re.compile(
        r"^<\?xml [^>]*encoding=[\"']([^\"']+)[^>]*\?>[ \r\n]*", re.IGNORECASE)
    html_meta_charset_re = re.compile(
        r"<meta [^>]*[\"; ]charset=[\"']?([^\"' ]+)", re.IGNORECASE)

    def get_encoding_from_content(self, content):
        '''Extract encoding from html header.

        :param content: a utf-8 encoded byte string
        :return: a string containing the encoding
        '''
        # <?xml version="1.0" encoding="ISO-8859-1"?>
        # <meta charset="utf-8">
        # <meta http-equiv="Content-Type" content="charset=utf-8" />
        # <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        # <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
        m = (re.search(self.xml_encoding_declaration_re, content) or
             re.search(self.html_meta_charset_re, content))
        if m is not None:
            return m.group(1).lower()

    def get_normalized_encoding(self, encoding, source):
        '''Interpret some 8-bit encodings as windows-1252.'''
        if encoding not in ['iso-8859-15', 'utf-8']:
            encoding_norm = {
                'iso-8859-1': 'windows-1252',
                'ascii': 'windows-1252',
                'windows-1252': 'windows-1252',
            }
            if encoding in encoding_norm:
                encoding = encoding_norm[encoding]
            else:
                print("Unusual encoding found in {} {}: {}".format(
                    self.orig, source, encoding), file=sys.stderr)

        return encoding

    def get_encoding(self, content):
        encoding = 'utf-8'
        source = 'guess'

        encoding_from_xsl = self.md.get_variable('text_encoding')

        if encoding_from_xsl == '' or encoding_from_xsl is None:
            if self.get_encoding_from_content(content) is not None:
                source = 'content'
                encoding = self.get_encoding_from_content(content)
        else:
            source = 'xsl'
            encoding = encoding_from_xsl.lower()

        encoding = self.get_normalized_encoding(encoding, source)

        return encoding, source

    def remove_declared_encoding(self, content):
        '''Remove declared decoding

        lxml explodes if we send a decoded Unicode string with an
        xml-declared encoding
        http://lxml.de/parsing.html#python-unicode-strings
        '''
        return re.sub(self.xml_encoding_declaration_re, "", content)

    def simplify_tags(self):
        '''Turn tags to divs.

        We don't care about the difference between <fieldsets>, <legend>
        etc. – treat them all as <div>'s for xhtml2corpus
        '''
        superfluously_named_tags = self.soup.xpath(
            "//html:fieldset | //html:legend | //html:article | //html:hgroup "
            "| //html:section | //html:dl | //html:dd | //html:dt"
            "| //html:menu",
            namespaces={'html': 'http://www.w3.org/1999/xhtml'})
        for elt in superfluously_named_tags:
            elt.tag = '{http://www.w3.org/1999/xhtml}div'

    def fix_spans_as_divs(self):
        '''Turn div like elements into div.

        XHTML doesn't allow (and xhtml2corpus doesn't handle) span-like
        elements with div-like elements inside them; fix this and
        similar issues by turning them into divs.
        '''
        spans_as_divs = self.soup.xpath(
            "//*[( descendant::html:div or descendant::html:p"
            "      or descendant::html:h1 or descendant::html:h2"
            "      or descendant::html:h3 or descendant::html:h4"
            "      or descendant::html:h5 or descendant::html:h6 ) "
            "and ( self::html:span or self::html:b or self::html:i"
            "      or self::html:em or self::html:strong "
            "      or self::html:a )"
            "    ]",
            namespaces={'html': 'http://www.w3.org/1999/xhtml'})
        for elt in spans_as_divs:
            elt.tag = '{http://www.w3.org/1999/xhtml}div'

        ps_as_divs = self.soup.xpath(
            "//html:p[descendant::html:div]",
            namespaces={'html': 'http://www.w3.org/1999/xhtml'})
        for elt in ps_as_divs:
            elt.tag = '{http://www.w3.org/1999/xhtml}div'

        lists_as_divs = self.soup.xpath(
            "//*[( child::html:ul or child::html:ol ) "
            "and ( self::html:ul or self::html:ol )"
            "    ]",
            namespaces={'html': 'http://www.w3.org/1999/xhtml'})
        for elt in lists_as_divs:
            elt.tag = '{http://www.w3.org/1999/xhtml}div'

    def remove_empty_p(self):
        ps = self.soup.xpath(
            '//html:p',
            namespaces={'html': 'http://www.w3.org/1999/xhtml'})

        for elt in ps:
            if elt.text is None and elt.tail is None and len(elt) == 0:
                elt.getparent().remove(elt)

    def remove_empty_class(self):
        '''Delete empty class attributes.'''
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
                    "latestnews_uutisarkisto",
                    'InnholdForfatter',  # unginordland
                    'QuickNav',
                    'ad',
                    'andrenyheter',  # tysfjord.kommune.no
                    'article-ad',
                    'article-bottom-element',
                    'article-column',
                    'article-dateline article-dateline-footer meta-widget-content',  # nrk.no
                    'article-related',
                    'articleImageRig',
                    'articlegooglemap',  # tysfjord.kommune.no
                    'articleTags',  # nord-salten.no
                    'authors',
                    'authors ui-helper-clearfix',  # nord-salten.no
                    'back_button',
                    'banner-element',
                    'breadcrumbs ',
                    'breadcrumbs',
                    'breadcrums span-12',
                    'btm_menu',
                    'byline',  # arran.no
                    'c1',  # arran.no
                    'clearfix breadcrumbsAndSocial noindex',  # udir.no
                    'container_full',
                    'documentInfoEm',
                    'documentPaging',
                    'dotList',  # nord-salten.no
                    'dropmenudiv',  # calliidlagadus.org
                    'egavpi',  # calliidlagadus.org
                    'egavpi_fiskes',  # calliidlagadus.org
                    'expandable',
                    'feedbackContainer noindex',  # udir.no
                    'fixed-header',
                    'g100 col fc s18 sg6 sg9 sg12 menu-reference',  # nrk.no
                    'g100 col fc s18 sg6 sg9 sg12 flow-reference',  # nrk.no
                    'g11 col fl s2 sl6 sl9 sl12 sl18',  # nrk.no
                    'g22 col fl s4 sl6 sl9 sl12 sl18 article-header-sidebar',  # nrk.no
                    'g94 col fl s17 sl18 sg6 sg9 sg12 meta-widget',  # nrk.no
                    'globmenu',  # visitstetind.no
                    'grid cf',  # nrk.no
                    'help closed hidden-xs',
                    'imagecontainer',
                    'innholdsfortegenlse-child',
                    'ld-navbar',
                    'meta',
                    'meta ui-helper-clearfix',  # nord-salten.no
                    'authors ui-helper-clearfix'  # nord-salten.no
                    'menu',  # visitstetind.no
                    'metaWrapper',
                    'moduletable_oikopolut',
                    'moduletable_etulinkki',  # www.samediggi.fi
                    'naviHlp',  # visitstetind.no
                    'noindex',  # ntfk
                    'nrk-globalfooter',  # nrk.no
                    'nrk-globalfooter-dk lp_globalfooter',  # nrk.no
                    'nrk-globalnavigation',  # nrk.no
                    'outer-column',
                    'post-footer',
                    'printContact',
                    'right',  # ntfk
                    'rightverticalgradient',  # udir.no
                    'sharing',
                    'sidebar',
                    'spalte300',  # osko.no
                    'tabbedmenu',
                    'tipformcontainer',  # tysfjord.kommune.no
                    'tipsarad mt6 selfClear',
                    'titlepage',
                    'toc',
                    'tools',  # arran.no
                ],
                'id': [
                    'AreaLeft',
                    'AreaLeftNav',
                    'AreaRight',
                    'AreaTopRight',
                    'AreaTopSiteNav',
                    'NAVbreadcrumbContainer',
                    'NAVfooterContainer',
                    'NAVheaderContainer',
                    'NAVrelevantContentContainer',
                    'NAVsubmenuContainer',
                    'PageFooter',
                    'PrintDocHead',
                    'SamiDisclaimer',
                    'ShareArticle',
                    'WIPSELEMENT_CALENDAR',  # learoevierhtieh.no
                    'WIPSELEMENT_HEADING',  # learoevierhtieh.no
                    'WIPSELEMENT_MENU',  # learoevierhtieh.no
                    'WIPSELEMENT_MENURIGHT',  # learoevierhtieh.no
                    'WIPSELEMENT_NEWS',  # learoevierhtieh.no
                    'aa',
                    'andrenyheter',  # tysfjord.kommune.no
                    'article_footer',
                    'attached',  # tysfjord.kommune.no
                    'blog-pager',
                    'breadcrumbs-bottom',
                    'bunninformasjon',  # unginordland
                    'chatBox',
                    'chromemenu',  # calliidlagadus.org
                    'crumbs',  # visitstetind.no
                    'ctl00_FullRegion_CenterAndRightRegion_HitsControl_'
                    'ctl00_FullRegion_CenterAndRightRegion_Sorting_sortByDiv',
                    'ctl00_MidtSone_ucArtikkel_ctl00_ctl00_ctl01_divRessurser',
                    'ctl00_MidtSone_ucArtikkel_ctl00_divNavigasjon',
                    'deleModal',
                    'document-header',
                    'errorMessageContainer',  # nord-salten.no
                    'footer',  # forrest, too, tysfjord.kommune.no
                    'footer-wrapper',
                    'frontgallery',  # visitstetind.no
                    'header',
                    'headerBar',
                    'headWrapper',  # osko.no
                    'hoyre',  # unginordland
                    'leftMenu',
                    'leftPanel',
                    'leftbar',  # forrest (divvun and giellatekno sites)
                    'leftcol',  # new samediggi.no
                    'leftmenu',
                    'main_navi_main',           # www.samediggi.fi
                    'mainsidebar',  # arran.no
                    'menu',
                    'murupolku',                # www.samediggi.fi
                    'navbar',  # tysfjord.kommune.no
                    'ncFooter',  # visitstetind.no
                    'ntfkFooter',  # ntfk
                    'ntfkHeader',  # ntfk
                    'ntfkNavBreadcrumb',  # ntfk
                    'ntfkNavMain',  # ntfk
                    'pageFooter',
                    'path',  # new samediggi.no, tysfjord.kommune.no
                    'readspeaker_button1',
                    'rightAds',
                    'rightCol',
                    'rightside',
                    's4-leftpanel',  # ntfk
                    'searchBox',
                    'searchHitSummary',
                    'sendReminder',
                    'share-article',
                    'sidebar',  # finlex.fi, too
                    'sidebar-wrapper',
                    'sitemap',
                    'skipLinks',  # udir.no
                    'skiplink',  # tysfjord.kommune.no
                    'spraakvelger',  # osko.no
                    'subfoote',  # visitstetind.no
                    'submenu',  # nord-salten.no
                    'tipafriend',
                    'tools',  # arran.no
                    'topHeader',  # nord-salten.no
                    'topMenu',
                    'topUserMenu',
                    'top',  # arran.no
                    'topnav',  # tysfjord.kommune.no
                    'toppsone',  # unginordland
                    'venstre',  # unginordland
                ],
            },
            'p': {
                'class': [
                    'WebPartReadMoreParagraph',
                    'breadcrumbs',
                    'langs'  # oahpa.no
                ],
            },
            'ul': {
                'id': [
                    'AreaTopLanguageNav'
                    'AreaTopPrintMeny',
                    'skiplinks',  # umo.se
                ],
                'class': [
                    'QuickNav',
                    'article-tools',
                    'byline',
                    'chapter-index',  # lovdata.no
                    'footer-nav',  # lovdata.no
                    'hidden',  # unginordland
                ],
            },
            'span': {
                'id': [
                    'skiplinks'
                ],
                'class': [
                    'K-NOTE-FOTNOTE',
                    'graytext',  # svenskakyrkan.se
                ],
            },
            'a': {
                'id': [
                    'ctl00_IdWelcome_ExplicitLogin',  # ntfk
                    'leftPanelTab',
                ],
                'class': [
                    'addthis_button_print',  # ntfk
                    'mainlevel',
                    'share-paragraf',  # lovdata.no
                    'mainlevel_alavalikko',  # www.samediggi.fi
                    'sublevel_alavalikko',  # www.samediggi.fi
                ],
            },
            'td': {
                'id': [
                    "hakulomake",  # www.samediggi.fi
                    "paavalikko_linkit",  # www.samediggi.fi
                    'sg_oikea',  # www.samediggi.fi
                    'sg_vasen',  # www.samediggi.fi
                ],
                'class': [
                    "modifydate",
                ],
            },
            'tr': {
                'id': [
                    "sg_ylaosa1",
                    "sg_ylaosa2",
                ]
            },
            'header': {
                'id': [
                    'header',  # umo.se
                ],
                'class': [
                    'nrk-masthead-content cf',  # nrk.no
                ],
            },
            'section': {
                'class': [
                    'tree-menu current',  # umo.se
                    'tree-menu',  # umo.se
                ],
            },
        }

        ns = {'html': 'http://www.w3.org/1999/xhtml'}
        for tag, attribs in unwanted_classes_ids.items():
            for key, values in attribs.items():
                for value in values:
                    search = ('.//html:{}[@{}="{}"]'.format(tag, key, value))
                    for unwanted in self.soup.xpath(search, namespaces=ns):
                        unwanted.getparent().remove(unwanted)

    def add_p_around_text(self):
        '''Add p around text after an hX element'''
        for h in self.soup.xpath(
                './/html:body/*',
                namespaces={'html': 'http://www.w3.org/1999/xhtml'}):
            if h.tail is not None and h.tail.strip() != '':
                p = etree.Element('{http://www.w3.org/1999/xhtml}p')
                p.text = h.tail
                h.tail = None
                n = h.getnext()
                while n is not None:
                    if (n.tag == '{http://www.w3.org/1999/xhtml}p' or
                            n.tag == '{http://www.w3.org/1999/xhtml}h3' or
                            n.tag == '{http://www.w3.org/1999/xhtml}h2' or
                            n.tag == '{http://www.w3.org/1999/xhtml}div' or
                            n.tag == '{http://www.w3.org/1999/xhtml}table'):
                        break
                    p.append(n)
                    n = n.getnext()

                h_parent = h.getparent()
                h_parent.insert(h_parent.index(h) + 1, p)

        # br's are not allowed right under body in XHTML:
        for elt in self.soup.xpath(
                './/html:body/html:br',
                namespaces={'html': 'http://www.w3.org/1999/xhtml'}):
            elt.tag = '{http://www.w3.org/1999/xhtml}p'
            elt.text = ' '

    def center2div(self):
        '''Convert center to div in tidy style.'''
        for center in self.soup.xpath(
                './/html:center',
                namespaces={'html': 'http://www.w3.org/1999/xhtml'}):
            center.tag = '{http://www.w3.org/1999/xhtml}div'
            center.set('class', 'c1')

    def body_i(self):
        '''Wrap bare elements inside a p element.'''
        for tag in ['a', 'i', 'em', 'font', 'u', 'strong', 'span']:
            for bi in self.soup.xpath(
                    './/html:body/html:{}'.format(tag),
                    namespaces={'html': 'http://www.w3.org/1999/xhtml'}):
                p = etree.Element('{http://www.w3.org/1999/xhtml}p')
                bi_parent = bi.getparent()
                bi_parent.insert(bi_parent.index(bi), p)
                p.append(bi)

    def body_text(self):
        '''Wrap bare text inside a p element.'''
        body = self.soup.find(
            './/html:body',
            namespaces={'html': 'http://www.w3.org/1999/xhtml'})

        if body.text is not None:
            p = etree.Element('{http://www.w3.org/1999/xhtml}p')
            p.text = body.text
            body.text = None
            body.insert(0, p)

    def convert2xhtml(self):
        '''Clean up the html document.

        Destructively modifies self.soup, trying
        to create strict xhtml for xhtml2corpus.xsl
        '''
        self.remove_empty_class()
        self.remove_empty_p()
        self.remove_elements()
        self.add_p_around_text()
        self.center2div()
        self.body_i()
        self.body_text()
        self.simplify_tags()
        self.fix_spans_as_divs()

    def convert2intermediate(self):
        '''Convert the original document to the giellatekno xml format.

        The resulting xml is stored in intermediate
        '''
        html_xslt_root = etree.parse(self.converter_xsl)
        transform = etree.XSLT(html_xslt_root)

        intermediate = ''

        try:
            intermediate = transform(self.soup)
        except etree.XMLSyntaxError as e:
            self.handle_syntaxerror(e, util.lineno(),
                                    etree.tostring(self.soup))

        if len(transform.error_log) > 0:
            with open(self.logfile, 'w') as logfile:
                logfile.write('Error at: {}'.format(str(util.lineno())))
                for entry in transform.error_log:
                    logfile.write('\n{}: {} {}\n'.format(
                        str(entry.line), str(entry.column),
                        entry.message.encode('utf8')))
                util.print_element(self.soup, 0, 4, logfile)

            raise ConversionException(
                'HTMLContentConverter: transformation failed.'
                'More info in {}'.format(self.logfile))

        return intermediate.getroot()


class HTMLConverter(HTMLContentConverter):

    def __init__(self, filename, write_intermediate=False):
        with open(filename) as f:
            super(HTMLConverter, self).__init__(filename,
                                                write_intermediate,
                                                content=f.read())


class RTFConverter(HTMLContentConverter):

    '''Convert html documents to the giellatekno xml format.'''

    def __init__(self, filename, write_intermediate=False):
        with open(filename, "rb") as rtf_document:
            content = rtf_document.read()
            try:
                pyth_doc = Rtf15Reader.read(
                    io.BytesIO(content.replace('fcharset256', 'fcharset255')))
                HTMLContentConverter.__init__(
                    self, filename,
                    content=XHTMLWriter.write(pyth_doc, pretty=True).read())
            except UnicodeDecodeError:
                raise ConversionException('Unicode problems in {}'.format(
                    self.orig))


class OdfConverter(HTMLContentConverter):

    '''Convert odf documents to the giellatekno xml format'''

    def __init__(self, filename, write_intermediate=False):
        generatecss = False
        embedable = True
        odhandler = ODF2XHTML(generatecss, embedable)
        HTMLContentConverter.__init__(self, filename,
                                      content=odhandler.odf2xhtml(unicode(filename)))


class DocxConverter(HTMLContentConverter):

    '''Convert docx documents to the giellatekno xml format'''

    def __init__(self, filename, write_intermediate=False):

        HTMLContentConverter.__init__(self, filename,
                                      content=PyDocXHTMLExporter(filename).export())

    def remove_elements(self):
        '''Remove some docx specific html elements'''
        super(DocxConverter, self).remove_elements()

        unwanted_classes_ids = {
            'a': {
                'name': [
                    'footnote-ref',  # footnotes in running text
                ],
            }
        }
        ns = {'html': 'http://www.w3.org/1999/xhtml'}
        for tag, attribs in unwanted_classes_ids.items():
            for key, values in attribs.items():
                for value in values:
                    search = ('.//html:{}[starts-with(@{}, "{}")]'.format(tag, key, value))
                    for unwanted in self.soup.xpath(search, namespaces=ns):
                        unwanted.getparent().remove(unwanted)


class DocConverter(HTMLContentConverter):

    '''Convert Microsoft Word documents to the giellatekno xml format'''

    def __init__(self, filename, write_intermediate=False):
        Converter.__init__(self, filename, write_intermediate)
        command = ['wvHtml',
                   os.path.realpath(self.orig),
                   '-']
        HTMLContentConverter.__init__(self, filename,
                                      content=self.extract_text(command))

    def fix_wv_output(self):
        '''Examples of headings

        h1:
        <html:ul>
            <html:li value="2">
                <html:p/>
                <html:div align="left" name="Overskrift 1">
                    <html:p>
                        <html:b>
                            <html:span>
                                OVTTASKASOLBMOT
                            </html:span>
                        </html:b>
                    </html:p>
                </html:div>
            </html:li>
        </html:ul>

        h2:
        <html:ol type="1">
            <html:li value="1">
                <html:p/>
                <html:div align="left" name="Overskrift 2">
                    <html:p>
                        <html:b>
                            <html:span>
                                čoahkkáigeassu
                            </html:span>
                        </html:b>
                    </html:p>
                </html:div>
            </html:li>
        </html:ol>

        <html:ol type="1">
            <html:ol type="1">
                <html:li value="2">
                    <html:p/>
                    <html:div align="left" name="Overskrift 2">
                        <html:p>
                            <html:b>
                                <html:span>
                                    Ulbmil ja váldooasit
                                </html:span>
                            </html:b>
                        </html:p>
                    </html:div>
                </html:li>
            </html:ol>
        </html:ol>

        h3:
        <html:ol type="1">
            <html:ol type="1">
                <html:ol type="1">
                    <html:li value="1">
                        <html:p>
                        </html:p>
                        <html:div align="left" name="Overskrift 3">
                            <html:p>
                                <html:b>
                                    <html:span>
                                        Geaográfalaš
                                    </html:span>
                                </html:b>
                                <html:b>
                                    <html:span>
                                        ráddjen
                                    </html:span>
                                </html:b>

                            </html:p>
                        </html:div>
                    </html:li>

                </html:ol>
            </html:ol>
        </html:ol>

        <html:ol type="1">
            <html:ol type="1">
                <html:ol type="1">
                    <html:li value="1">
                        <html:p>
                        </html:p>
                        <html:div align="left" name="Overskrift 3">
                            <html:p>
                                <html:b>
                                <html:span>Iskanjoavku ja sámegielaga
                                definišuvdn</html:span></html:b>
                                <html:b><html:span>a</html:span></html:b>
                            </html:p>
                        </html:div>
                    </html:li>

                </html:ol>
            </html:ol>
        </html:ol>

        h4:
        <html:div align="left" name="Overskrift 4">
            <html:p>
                <html:b>
                    <html:i>
                        <html:span>
                            Mildosat:
                        </html:span>
                    </html:i>
                </html:b>
            </html:p>
        </html:div>

        '''
        pass


class DocumentFixer(object):

    '''Fix the content of a giellatekno xml document.

    Receive a stringified etree from one of the raw converters,
    replace ligatures, fix the encoding and return an etree with correct
    characters
    '''

    def __init__(self, document):
        self.root = document

    def get_etree(self):
        return self.root

    def compact_ems(self):
        '''Compact consecutive em elements into a single em if possible.'''
        word = re.compile(u'\w+', re.UNICODE)
        for element in self.root.iter('p'):
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
                            em.tail = ' {}'.format(em.tail)
                        lines = []

    def soft_hyphen_to_hyph_tag(self):
        '''Replace soft hyphen chars with hyphen tags.'''
        for element in self.root.iter('p'):
            self.replace_shy(element)

    def replace_shy(self, element):
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
        '''Insert space after semicolon where needed.'''
        irritating_words_regex = re.compile(u'(govv(a|en|ejeaddji):)([^ ])',
                                            re.UNICODE | re.IGNORECASE)
        for child in self.root.find('.//body'):
            self.insert_space_after_semicolon(child, irritating_words_regex)

    def insert_space_after_semicolon(self, element, irritating_words_regex):
        if element.text is not None:
            element.text = irritating_words_regex.sub(r'\1 \3', element.text)
        for child in element:
            self.insert_space_after_semicolon(child, irritating_words_regex)
        if element.tail is not None:
            element.tail = irritating_words_regex.sub(r'\1 \3', element.tail)

    def replace_ligatures(self):
        '''Replace unwanted chars.'''
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

        for element in self.root.iter('p'):
            if element.text:
                for key, value in replacements.items():
                    element.text = element.text.replace(key + ' ', value)
                    element.text = element.text.replace(key, value)

    def replace_bad_unicode(self):
        '''Replace some chars in an otherwise 'valid utf-8' document.

        These chars e.g. 'valid utf-8' (don't give UnicodeDecodeErrors), but
        we still want to replace them to what they most likely were
        meant to be.

        :param content: a unicode string
        :returns: a cleaned up unicode string
        '''
        # u'š'.encode('windows-1252') gives '\x9a', which sometimes
        # appears in otherwise utf-8-encoded documents with the
        # meaning 'š'
        replacements = [(u'\x9a', u'š'),
                        (u'\x8a', u'Š'),
                        (u'\x9e', u'ž'),
                        (u'\x8e', u'Ž')]
        for element in self.root.iter('p'):
            if element.text:
                element.text = util.replace_all(replacements, element.text)

    def fix_sms(self, element):

        replacement_pairs = [
            (u'\u2019', u'\u02BC'),
            (u'\u0027', u'\u02BC'),
            (u'\u2032', u'\u02B9'),
            (u'\u00B4', u'\u02B9'),
        ]

        for replacement_pair in replacement_pairs:
            if element.text:
                element.text = element.text.replace(replacement_pair[0], replacement_pair[1])
            if element.tail:
                element.tail = element.tail.replace(replacement_pair[0], replacement_pair[1])
        for child in element:
            self.fix_sms(child)

    def fix_body_encoding(self):
        '''Replace wrongly encoded saami chars with proper ones.

        Send a stringified version of the body into the EncodingGuesser class.
        It returns the same version, but with fixed characters.
        Parse the returned string, insert it into the document
        '''
        self.replace_ligatures()

        body = self.root.find('body')
        bodyString = etree.tostring(body, encoding='utf-8')
        body.getparent().remove(body)

        eg = decode.EncodingGuesser()
        encoding = eg.guess_body_encoding(bodyString)

        body = etree.fromstring(eg.decode_para(encoding, bodyString))
        self.root.append(body)

        self.fix_title_person('double-utf8')
        self.fix_title_person('mac-sami_to_latin1')
        self.replace_bad_unicode()

        try:
            if self.root.attrib['{http://www.w3.org/XML/1998/namespace}lang'] == 'sms':
                self.fix_sms(self.root.find('body'))
        except KeyError:
            pass

    def fix_title_person(self, encoding):
        '''Fix encoding problems'''
        eg = decode.EncodingGuesser()

        title = self.root.find('.//title')
        if title is not None and title.text is not None:
            text = title.text

            if encoding == 'mac-sami_to_latin1':
                text = text.replace(u'‡', u'á')
                text = text.replace(u'Œ', u'å')

            text = text.encode('utf8')
            title.text = eg.decode_para(encoding, text).decode('utf-8')

        persons = self.root.findall('.//person')
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

    @staticmethod
    def get_quote_list(text):
        quote_regexes = [re.compile('".+?"'),
                         re.compile(u'«.+?»'),
                         re.compile(u'“.+?”')]
        quote_list = [m.span()
                      for quote_regex in quote_regexes
                      for m in quote_regex.finditer(text)]
        quote_list.sort()

        return quote_list

    @staticmethod
    def append_quotes(element, text, quote_list):
        for x in range(0, len(quote_list)):
            span = etree.Element('span')
            span.set('type', 'quote')
            span.text = text[quote_list[x][0]:quote_list[x][1]]
            if x + 1 < len(quote_list):
                span.tail = text[quote_list[x][1]:quote_list[x + 1][0]]
            else:
                span.tail = text[quote_list[x][1]:]
            element.append(span)

    def detect_quote(self, element):
        '''Insert span elements around quotes.'''
        newelement = deepcopy(element)

        element.text = ''
        for child in element:
            child.getparent().remove(child)

        text = newelement.text
        if text:
            quote_list = self.get_quote_list(text)
            if len(quote_list) > 0:
                element.text = text[0:quote_list[0][0]]
                self.append_quotes(element, text, quote_list)
            else:
                element.text = text

        for child in newelement:
            element.append(self.detect_quote(child))

            if child.tail:
                text = child.tail
                quote_list = self.get_quote_list(text)
                if len(quote_list) > 0:
                    child.tail = text[0:quote_list[0][0]]
                    self.append_quotes(element, text, quote_list)

        return element

    def detect_quotes(self):
        '''Detect quotes in all paragraphs.'''
        for paragraph in self.root.iter('p'):
            paragraph = self.detect_quote(paragraph)

    def calculate_wordcount(self):
        '''Count the words in the file.'''
        plist = [etree.tostring(paragraph, method='text', encoding='utf8')
                 for paragraph in self.root.iter('p')]

        return str(len(re.findall(r'\S+', ' '.join(plist))))

    def set_word_count(self):
        '''Set the wordcount element'''
        wordcount = self.root.find('header/wordcount')
        if wordcount is None:
            tags = ['collection', 'publChannel', 'place', 'year',
                    'translated_from', 'translator', 'author']
            for tag in tags:
                found = self.root.find('header/' + tag)
                if found is not None:
                    wordcount = etree.Element('wordcount')
                    header = found.getparent()
                    header.insert(header.index(found) + 1, wordcount)
                    break

        wordcount.text = self.calculate_wordcount()

    def make_element(self, eName, text, attributes={}):
        '''Make an xml element.

        :param eName: the name of the element
        :param text: the content of the element
        :param attributes: the elements attributes

        Add hyph elements if necessary.

        :returns: lxml.etree.Element
        '''
        el = etree.Element(eName)
        for key in attributes:
            el.set(key, attributes[key])

        el.text = text

        return el

    def fix_newstags(self):
        '''Convert newstags found in text to xml elements'''
        newstags = re.compile(
            r'(@*logo:|[\s+\']*@*\s*ingres+[\.:]*|.*@*.*bilde\s*\d*:|\W*(@|'
            r'LED|bilde)*tekst:|@*foto:|@fotobyline:|@*bildetitt:|'
            r'<pstyle:bilde>|<pstyle:ingress>|<pstyle:tekst>|'
            r'@*Samleingress:*|tekst/ingress:|billedtekst:)', re.IGNORECASE)
        titletags = re.compile(
            r'\s*@m.titt[\.:]|\s*@*stikk:|Mellomtittel:|@*(stikk\.*|'
            r'under)titt(el)*:|@ttt:|\s*@*[utm]*[:\.]*tit+:|<pstyle:m.titt>|'
            r'undertittel:', re.IGNORECASE)
        headertitletags = re.compile(
            r'(\s*@*(led)*tittel:|\s*@*titt(\s\d)*:|@LEDtitt:|'
            r'<pstyle:tittel>|@*(hoved|over)titt(el)*:)', re.IGNORECASE)
        bylinetags = re.compile(u'(<pstyle:|\s*@*)[Bb]yline[:>]*\s*(\S+:)*',
                                re.UNICODE | re.IGNORECASE)
        boldtags = re.compile(u'@bold\s*:')

        header = self.root.find('.//header')
        unknown = self.root.find('.//unknown')

        for em in self.root.iter('em'):
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

        for paragraph in self.root.iter('p'):
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
                                                  ' '.join(lines).strip(),
                                                  attributes=paragraph.attrib))
                        lines = []

                        lines.append(newstags.sub('', line))
                    elif bylinetags.match(line):
                        if len(lines) > 0:
                            index += 1
                            paragraph.getparent().insert(
                                index,
                                self.make_element('p',
                                                  ' '.join(lines).strip(),
                                                  attributes=paragraph.attrib))
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
                                                  ' '.join(lines).strip(),
                                                  attributes=paragraph.attrib))
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
                                                  ' '.join(lines).strip(),
                                                  attributes=paragraph.attrib))
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
                                                  ' '.join(lines).strip(),
                                                  attributes=paragraph.attrib))
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
                                                  ' '.join(lines).strip(),
                                                  attributes=paragraph.attrib))
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
                                                  ' '.join(lines).strip(),
                                                  attributes=paragraph.attrib))
                        lines = []
                    else:
                        lines.append(line)

                if len(lines) > 0:
                    index += 1
                    paragraph.getparent().insert(
                        index, self.make_element('p',
                                                 ' '.join(lines).strip(),
                                                 attributes=paragraph.attrib))

                paragraph.getparent().remove(paragraph)


class XslMaker(object):

    '''Make an xsl file to combine with the intermediate xml file.

    To convert the intermediate xml to a fullfledged  giellatekno document
    a combination of three xsl files + the intermediate xml file is needed.
    '''

    def __init__(self, xslfile):
        self.filename = xslfile

    @property
    def filename(self):
        return self.__filename

    @filename.setter
    def filename(self, filename):
        self.__filename = filename

    @property
    def logfile(self):
        return self.filename + '.log'

    @property
    def xsl(self):
        try:
            filexsl = etree.parse(self.filename)
        except etree.XMLSyntaxError as e:
            with open(self.logfile, 'w') as logfile:
                logfile.write('Error at: {}'.format(str(util.lineno())))
                for entry in e.error_log:
                    logfile.write('{}\n'.format(str(entry)))

            raise ConversionException(
                '{}: Syntax error. More info in {}'.format(type(self).__name__,
                                                           self.logfile))

        preprocessXsl = etree.parse(
            os.path.join(here, 'xslt/preprocxsl.xsl'))
        preprocessXslTransformer = etree.XSLT(preprocessXsl)

        common_xsl_path = os.path.join(
            here, 'xslt/common.xsl').replace(' ', '%20')

        return preprocessXslTransformer(
            filexsl,
            commonxsl=etree.XSLT.strparam('file://{}'.format(common_xsl_path)))

    @property
    def transformer(self):
        try:
            return etree.XSLT(self.xsl)
        except etree.XSLTParseError as (e):
            with open(self.logfile, 'w') as logfile:
                logfile.write('Error at: {}\n'.format(str(util.lineno())))
                logfile.write('Invalid XML in {}\n'.format(self.filename))
                for entry in e.error_log:
                    logfile.write('{}\n'.format(str(entry)))

            raise ConversionException(
                '{}: Invalid XML in {}. More info in {}'.format(
                    type(self).__name__, self.filename, self.logfile))


class LanguageDetector(object):

    '''Detect and set the languages of a document.'''

    def __init__(self, document, languageGuesser):
        self.document = document
        self.languageGuesser = languageGuesser

    @property
    def inlangs(self):
        inlangs = [language.get('{http://www.w3.org/XML/1998/namespace}'
                                'lang')
                   for language in self.document.findall(
            'header/multilingual/language')]
        if len(inlangs) != 0:
            inlangs.append(self.mainlang)

        return inlangs

    @property
    def mainlang(self):
        '''Get the mainlang of the file'''
        return self.document.\
            attrib['{http://www.w3.org/XML/1998/namespace}lang']

    def set_paragraph_language(self, paragraph):
        '''Set xml:lang of paragraph

        Extract the text outside the quotes, use this text to set
        language of the paragraph.
        Set the language of the quotes in the paragraph.
        '''

        if paragraph.get('{http://www.w3.org/XML/1998/namespace}lang') is None:
            paragraph_text = self.remove_quote(paragraph)
            if self.languageGuesser is not None:
                lang = self.languageGuesser.classify(paragraph_text,
                                                     langs=self.inlangs)
                if lang != self.mainlang:
                    paragraph.set('{http://www.w3.org/XML/1998/namespace}lang',
                                  lang)

                self.set_span_language(paragraph)

        return paragraph

    def set_span_language(self, paragraph):
        '''Set xml:lang of span element'''
        for element in paragraph.iter("span"):
            if element.get("type") == "quote":
                if element.text is not None:
                    lang = self.languageGuesser.classify(element.text,
                                                         langs=self.inlangs)
                    if lang != self.mainlang:
                        element.set(
                            '{http://www.w3.org/XML/1998/namespace}lang',
                            lang)

    def remove_quote(self, paragraph):
        '''Extract all text except the one inside <span type='quote'>'''
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
        '''Detect language in all the paragraphs in self.document'''
        if self.document.find('header/multilingual') is not None:
            for paragraph in self.document.iter('p'):
                self.set_paragraph_language(paragraph)


class ConverterManager(object):

    '''Manage the conversion of original files to corpus xml'''
    LANGUAGEGUESSER = text_cat.Classifier(None)
    FILES = []

    def __init__(self, write_intermediate):
        self.write_intermediate = write_intermediate

    @property
    def write_intermediate(self):
        return self.__write_intermediate

    @write_intermediate.setter
    def write_intermediate(self, write_intermediate):
        self.__write_intermediate = write_intermediate

    def convert(self, xsl_file):
        orig_file = xsl_file[:-4]
        if os.path.exists(orig_file) and not orig_file.endswith('.xsl'):

            try:
                conv = self.converter(orig_file)
                conv.write_complete(self.LANGUAGEGUESSER)
            except ConversionException as e:
                print('Could not convert {}'.format(orig_file),
                      file=sys.stderr)
                print(str(e), file=sys.stderr)
        else:
            print('{} does not exist'.format(orig_file), file=sys.stderr)

    def converter(self, orig_file):
        if 'avvir_xml' in orig_file:
            return AvvirConverter(
                orig_file, write_intermediate=self.write_intermediate)

        elif orig_file.endswith('.txt'):
            return PlaintextConverter(
                orig_file, write_intermediate=self.write_intermediate)

        elif orig_file.endswith('.pdf'):
            return PDF2XMLConverter(
                orig_file, write_intermediate=self.write_intermediate)

        elif orig_file.endswith('.svg'):
            return SVGConverter(
                orig_file, write_intermediate=self.write_intermediate)

        elif '.htm' in orig_file or '.php' in orig_file:
            return HTMLConverter(
                orig_file, write_intermediate=self.write_intermediate)

        elif orig_file.endswith('.doc') or orig_file.endswith('.DOC'):
            return DocConverter(
                orig_file, write_intermediate=self.write_intermediate)

        elif orig_file.endswith('.odt'):
            return OdfConverter(
                orig_file, write_intermediate=self.write_intermediate)

        elif orig_file.endswith('.docx'):
            return DocxConverter(
                orig_file, write_intermediate=self.write_intermediate)

        elif '.rtf' in orig_file:
            return RTFConverter(
                orig_file, write_intermediate=self.write_intermediate)

        elif orig_file.endswith('.bible.xml'):
            return BiblexmlConverter(
                orig_file, write_intermediate=self.write_intermediate)

        else:
            raise ConversionException(
                "Unknown file extension, not able to convert {} "
                "\nHint: you may just have to rename the file".format(
                    orig_file))

    def convert_in_parallel(self):
        print('Starting the conversion of {} files'.format(len(self.FILES)))

        pool_size = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(processes=pool_size,)
        pool.map(unwrap_self_convert,
                 zip([self] * len(self.FILES), self.FILES))
        pool.close()
        pool.join()

    def convert_serially(self):
        print('Starting the conversion of {} files'.format(len(self.FILES)))

        for xsl_file in self.FILES:
            print('converting', xsl_file[:-4], file=sys.stderr)
            self.convert(xsl_file)

    def collect_files(self, sources):
        print('Collecting files to convert')

        for source in sources:
            if os.path.isfile(source):
                xsl_file = '{}.xsl'.format(source)
                if os.path.isfile(xsl_file):
                    self.FILES.append(xsl_file)
                elif source.endswith('.xsl') and os.path.isfile(source[:-4]):
                    self.FILES.append(source)
                else:
                    metadata = xslsetter.MetadataHandler(xsl_file,
                                                         create=True)
                    metadata.write_file()
                    print("Fill in meta info in", xsl_file,
                          ', then run this command again')
                    sys.exit(1)
            elif os.path.isdir(source):
                self.FILES.extend(
                    [os.path.join(root, f)
                     for root, dirs, files in os.walk(source)
                     for f in files if f.endswith('.xsl')])
            else:
                print('Can not process {}'.format(source), file=sys.stderr)
                print('This is neither a file nor a directory.',
                      file=sys.stderr)


def unwrap_self_convert(arg, **kwarg):
    return ConverterManager.convert(*arg, **kwarg)


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


def sanity_check():
    util.sanity_check([u'wvHtml', u'pdftotext'])
    if not os.path.isfile(Converter.get_dtd_location()):
        raise util.SetupException(
            "Couldn't find {}\n"
            "Check that GTHOME points at the right directory "
            "(currently: {}).".format(Converter.get_dtd_location(),
                                      os.environ['GTHOME']))


def main():
    sanity_check()
    args = parse_options()

    cm = ConverterManager(args.write_intermediate)

    cm.collect_files(args.sources)

    if args.serial:
        cm.convert_serially()
    else:
        cm.convert_in_parallel()
