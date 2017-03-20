# -*- coding: utf-8 -*-

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
#   Copyright © 2012-2017 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

"""This file contains classes to convert files to the giellatekno xml format."""


from __future__ import absolute_import, print_function

import argparse
import codecs
import collections
import distutils.dep_util
import distutils.spawn
import io
import logging
import multiprocessing
import os
import re
import sys
from copy import deepcopy

import epub
import six
from lxml import etree, html
from lxml.html import clean, html5parser
from odf.odf2xhtml import ODF2XHTML
from pydocx.export import PyDocXHTMLExporter
from pyth.plugins.rtf15.reader import Rtf15Reader
from pyth.plugins.xhtml.writer import XHTMLWriter

from corpustools import (argparse_version, ccat, corpuspath, decode,
                         errormarkup, text_cat, util, xslsetter)

here = os.path.dirname(__file__)


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class ConversionError(Exception):
    """Raise this exception when an error occurs in the converter module."""

    pass


class Converter(object):
    """Take care of data common to all Converter classes."""

    def __init__(self, filename, write_intermediate=False):
        """Initialise the Converter class.

        Arguments:
            filename: string containing the path to the file that should
            be converted
            write_intermediate: boolean which decides whether intermediate
            versions of the converted document should be written (used for
            debugging purposes).
        """
        codecs.register_error('mixed', self.mixed_decoder)
        self.names = corpuspath.CorpusPath(filename)
        self.write_intermediate = write_intermediate
        try:
            self.md = xslsetter.MetadataHandler(self.names.xsl, create=True)
        except xslsetter.XsltError as e:
            raise ConversionError(e)

        self.md.set_lang_genre_xsl()
        with util.ignored(OSError):
            os.makedirs(self.tmpdir)

    @property
    def dependencies(self):
        """Return files that converted files depend on."""
        return [self.names.orig, self.names.xsl]

    @property
    def standard(self):
        """Return a boolean indicating if the file is convertable."""
        return self.md.get_variable('conversion_status') == 'standard'

    @property
    def goldstandard(self):
        """Return a boolean indicating if the file is a gold standard doc."""
        return self.md.get_variable('conversion_status') == 'correct'

    def convert2intermediate(self):
        """Convert from original format to an intermediate corpus file."""
        raise NotImplementedError(
            'You have to subclass and override convert2intermediate')

    @staticmethod
    def get_dtd_location():
        """Return the path to the corpus dtd file."""
        return os.path.join(here, 'dtd/corpus.dtd')

    def validate_complete(self, complete):
        """Validate the complete document."""
        dtd = etree.DTD(Converter.get_dtd_location())

        if not dtd.validate(complete):
            with codecs.open(self.names.log, 'w', encoding='utf8') as logfile:
                logfile.write('Error at: {}'.format(
                    six.text_type(util.lineno())))
                for entry in dtd.error_log:
                    logfile.write('\n')
                    logfile.write(six.text_type(entry))
                    logfile.write('\n')
                util.print_element(complete, 0, 4, logfile)

            raise ConversionError(
                '{}: Not valid XML. More info in the log file: '
                '{}'.format(type(self).__name__, self.names.log))

    def maybe_write_intermediate(self, intermediate):
        """Write intermediate file.

        Used for debugging purposes.
        """
        if not self.write_intermediate:
            return
        im_name = self.names.orig + '.im.xml'
        with open(im_name, 'w') as im_file:
            im_file.write(etree.tostring(intermediate,
                                         encoding='utf8',
                                         pretty_print='True'))

    def transform_to_complete(self):
        """Combine the intermediate xml document with its medatata."""
        intermediate = self.convert2intermediate()
        self.fix_document(intermediate)
        self.maybe_write_intermediate(intermediate)
        try:
            xm = XslMaker(self.md.tree)
            complete = xm.transformer(intermediate)

            return complete.getroot()
        except etree.XSLTApplyError as e:
            with open(self.names.log, 'w') as logfile:
                logfile.write('Error at: {}'.format(
                    six.text_type(util.lineno())))
                for entry in e.error_log:
                    logfile.write(six.text_type(entry))
                    logfile.write('\n')

            raise ConversionError("Check the syntax in: {}".format(
                self.names.xsl))
        except etree.XSLTParseError as e:
            with open(self.names.log, 'w') as logfile:
                logfile.write('Error at: {}'.format(
                    six.text_type(util.lineno())))
                for entry in e.error_log:
                    logfile.write(six.text_type(entry))
                    logfile.write('\n')

            raise ConversionError("XSLTParseError in: {}\nError {}".format(
                self.names.xsl, str(e)))

    def convert_errormarkup(self, complete):
        """Convert error markup to xml."""
        if self.goldstandard:
            try:
                em = errormarkup.ErrorMarkup(self.names.orig)

                for element in complete.find('body'):
                    em.add_error_markup(element)
            except IndexError as e:
                with open(self.names.log, 'w') as logfile:
                    logfile.write('Error at: {}'.format(
                        six.text_type(util.lineno())))
                    logfile.write("There is a markup error\n")
                    logfile.write("The error message: ")
                    logfile.write(six.text_type(e))
                    logfile.write("\n\n")
                    logfile.write("This is the xml tree:\n")
                    logfile.write(etree.tostring(complete,
                                                 encoding='utf8',
                                                 pretty_print=True))
                    logfile.write('\n')

                raise ConversionError(
                    u"Markup error. More info in the log file: {}".format(
                        self.names.log))

    def fix_document(self, complete):
        """Fix a misc. issues found in converted document."""
        fixer = DocumentFixer(complete)

        fixer.fix_newstags()
        fixer.soft_hyphen_to_hyph_tag()
        self.md.set_variable('wordcount', fixer.calculate_wordcount())

        if not self.goldstandard:
            fixer.detect_quotes()

        # The above line adds text to hyph, fix that
        for hyph in complete.iter('hyph'):
            hyph.text = None

        if (self.md.get_variable('mainlang') in
                ['sma', 'sme', 'smj', 'smn', 'sms', 'nob', 'fin', 'swe',
                 'nno', 'dan', 'fkv', 'sju', 'sje', 'mhr']):
            try:
                fixer.fix_body_encoding(self.md.get_variable('mainlang'))
            except UserWarning as error:
                util.print_frame(error)
                util.print_frame(self.names.orig)

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
        """Convert text to unicode."""
        badstring = decode_error.object[decode_error.start:decode_error.end]
        badhex = badstring.encode('hex')
        repl = self.mixed_to_unicode.get(badhex, u'\ufffd')
        if repl == u'\ufffd':   # � unicode REPLACEMENT CHARACTER
            logger.warn("Skipped bad byte \\x{}, seen in {}".format(
                badhex, self.names.orig))
        return repl, (decode_error.start + len(repl))

    def make_complete(self, languageGuesser):
        """Make a complete giellatekno xml file.

        Combine the intermediate giellatekno xml file and the metadata into
        a complete giellatekno xml file.
        Fix the character encoding
        Detect the languages in the xml file
        """
        complete = self.transform_to_complete()
        self.validate_complete(complete)
        self.convert_errormarkup(complete)
        ld = LanguageDetector(complete, languageGuesser)
        ld.detect_language()

        return complete

    @staticmethod
    def has_content(complete):
        """Find out if the xml document has any content.

        Arguments:
            complete: a etree element containing the converted document.

        Returns:
            The length of the content in complete.
        """
        xml_printer = ccat.XMLPrinter(all_paragraphs=True,
                                      hyph_replacement=None)
        xml_printer.etree = etree.ElementTree(complete)

        return len(xml_printer.process_file().getvalue())

    def write_complete(self, languageguesser):
        """Write the complete converted document to disk.

        Arguments:
            languageguesser: a text.Classifier
        """
        if distutils.dep_util.newer_group(
                self.dependencies, self.names.converted):
            with util.ignored(OSError):
                os.makedirs(os.path.dirname(self.names.converted))

            if self.standard or self.goldstandard:
                complete = self.make_complete(languageguesser)

                if self.has_content(complete):
                    with open(self.names.converted, 'wb') as converted:
                        converted.write(etree.tostring(complete,
                                                       encoding='utf8',
                                                       pretty_print='True'))
                else:
                    logger.error("{} has no text".format(self.names.orig))

    @property
    def tmpdir(self):
        """Return the directory where temporary files should be placed."""
        return os.path.join(self.names.pathcomponents.root, 'tmp')

    @property
    def corpusdir(self):
        """Return the directory where the corpus directory is."""
        return self.names.pathcomponents.root

    def extract_text(self, command):
        """Extract the text from a document.

        :command: a list containing the command and the arguments sent to
        ExternalCommandRunner.
        :returns: byte string containing the output of the program
        """
        runner = util.ExternalCommandRunner()
        runner.run(command, cwd=self.tmpdir)

        if runner.returncode != 0:
            with open(self.names.log, 'w') as logfile:
                print('stdout\n{}\n'.format(runner.stdout), file=logfile)
                print('stderr\n{}\n'.format(runner.stderr), file=logfile)
                raise ConversionError(
                    '{} failed. More info in the log file: {}'.format(
                        command[0], self.names.log))

        return runner.stdout

    def handle_syntaxerror(self, e, lineno, invalid_input):
        """Handle an xml syntax error.

        Arguments:
            e: an exception
            lineno: the line number in this module where the error happened.
            invalid_input: a string containing the invalid input.
        """
        with open(self.names.log, 'w') as logfile:
            logfile.write('Error at: {}'.format(lineno))
            for entry in e.error_log:
                logfile.write('\n{}: {} '.format(
                    six.text_type(entry.line), six.text_type(entry.column)))
                try:
                    logfile.write(entry.message)
                except ValueError:
                    logfile.write(entry.message.encode('latin1'))

                logfile.write('\n')

            if six.PY3:
                logfile.write(invalid_input)
            else:
                logfile.write(invalid_input.encode('utf8'))

        raise ConversionError(
            "{}: log is found in {}".format(type(self).__name__, self.names.log))


class AvvirConverter(Converter):
    u"""Convert Ávvir xml files to the giellatekno xml format.

    The root node in an Ávvir document is article.
    article nodes contains one or more story nodes.
    story nodes contain one or more p nodes.
    p nodes contain span, br and (since 2013) p nodes.
    """

    def convert2intermediate(self):
        u"""Convert an Ávvir xml to an intermediate xml document."""
        self.intermediate = etree.parse(self.names.orig).getroot()
        self.remove_identical_ids()
        self.convert_p()
        self.convert_story()
        self.convert_article()

        return self.intermediate

    def remove_identical_ids(self):
        story_ids = set()
        for story in self.intermediate.xpath('.//story[@id]'):
            story_id = story.get('id')
            if story_id not in story_ids:
                story_ids.add(story_id)
            else:
                story.getparent().remove(story)

    @staticmethod
    def insert_element(p, text, position):
        """Insert a new element in p's parent.

        Arguments:
            p: an lxml element, it is a story/p element
            text: (unicode) string
            position: (integer) the position inside p's parent where the new
                      element is inserted

        Returns:
            position: (integer)
        """
        if text is not None and text.strip() != '':
            new_p = etree.Element('p')
            new_p.text = text
            grandparent = p.getparent()
            grandparent.insert(grandparent.index(p) + position, new_p)
            position += 1

        return position

    @staticmethod
    def convert_sub_p(p):
        """Convert p element found inside story/p elements.

        These elements contain erroneous text that an editor has removed.
        This function removes p.text and saves p.tail

        Arguments:
            p: an lxml element, it is a story/p element
        """
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
        """Convert subelements of story/p elements to p elements.

        Arguments:
            p: an lxml element, it is a story/p element
        """
        position = 1
        for subelement in p:
            position = self.insert_element(p, subelement.text, position)

            for subsubelement in subelement:
                for text in [subsubelement.text, subsubelement.tail]:
                    position = self.insert_element(p, text, position)

            position = self.insert_element(p, subelement.tail, position)

            p.remove(subelement)

    def convert_p(self):
        """Convert story/p elements to one or more p elements."""
        for p in self.intermediate.findall('./story/p'):
            if p.get("class") is not None:
                del p.attrib["class"]

            self.convert_sub_p(p)
            self.convert_subelement(p)

            if p.text is None or p.text.strip() == '':
                story = p.getparent()
                story.remove(p)

    def convert_story(self):
        """Convert story elements in to giellatekno xml elements."""
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
            for i, p in enumerate(story.findall('./p')):
                parent.insert(parent.index(story) + i + 1, p)

            parent.remove(story)

    def convert_article(self):
        u"""The root element of an Ávvir doc is article, rename it to body."""
        self.intermediate.tag = 'body'
        document = etree.Element('document')
        document.append(self.intermediate)
        self.intermediate = document


class SVGConverter(Converter):
    """Convert SVG files to the giellatekno xml format."""

    def convert2intermediate(self):
        """Transform svg to an intermediate xml document."""
        svgXsltRoot = etree.parse(os.path.join(here, 'xslt/svg2corpus.xsl'))
        transform = etree.XSLT(svgXsltRoot)
        doc = etree.parse(self.names.orig)
        intermediate = transform(doc)

        return intermediate.getroot()


class PlaintextConverter(Converter):
    """Convert plain text files to the giellatekno xml format."""

    def to_unicode(self):
        """Read a file into a unicode string.

        If the content of the file is not utf-8, pretend the encoding is
        latin1. The real encoding (for sma, sme and smj) will be detected
        later.

        :returns: a unicode string
        """
        try:
            content = codecs.open(self.names.orig, encoding='utf8').read()
        except ValueError:
            content = codecs.open(self.names.orig, encoding='latin1').read()

        content = self.strip_chars(content)

        return content

    def strip_chars(self, content, extra=u''):
        """Remove the characters found in plaintext_oddities from content.

        Arguments:
            content: a string containing the content of a document.
            extra: a string containg even more characters to remove
            from content.

        Returns:
            A string containing the content sans unwanted characters.
        """
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
        """Make an xml element.

        :param eName: Name of the xml element
        :param text: The text the xml should contain
        :param attributes: The attributes the element should have

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
        """Transform plaintext to an intermediate xml document.

        Returns:
            An etree element.
        """
        return self.content2xml(io.StringIO(self.to_unicode()))

    def content2xml(self, content):
        """Transform plaintext to an intermediate xml document.

        Arguments:
            content: a string containing the content of the plaintext
            document.

        Returns:
            An etree element.
        """
        document = etree.Element('document')
        header = etree.Element('header')
        body = etree.Element('body')

        ptext = ''

        for line_no, line in enumerate(content, start=1):
            if line_no not in self.md.skip_lines:
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


PDFFontspec = collections.namedtuple('PDFFontspec', ['size', 'family', 'color'])


class PDFFontspecs(object):
    """Add font specs found in a pdf page to this class.

    Attributes:
        pdffontspecs (dict{PDFFontspec:int}): map fontspecs to fontspec ids.
        duplicates (dict{str:str}): map ids of duplicate fontspecs to the
            id of the first instance of this fontspec.
    """

    def __init__(self):
        """Initialise the PDFFontspecs class."""
        self.pdffontspecs = {}
        self.duplicates = {}

    def add_fontspec(self, xmlfontspec):
        """Add a pdf2xml fontspec to this class.

        xmlfontspec (etree.Element): a PDF2XML fontspec element found in a PDF2XML page
        element.
        """
        this_id = xmlfontspec.get('id')
        this_fontspec = PDFFontspec(size=xmlfontspec.get('size'),
                                    family=xmlfontspec.get('family'),
                                    color=xmlfontspec.get('color'))

        for fontspec in self.pdffontspecs.keys():
            if fontspec == this_fontspec:
                self.duplicates[this_id] = self.pdffontspecs[fontspec]
                break
        else:
            self.pdffontspecs[this_fontspec] = this_id

    def corrected_id(self, id):
        """Return a corrected id of a fontspec.

        Some xmlfontspecs have different id's for an identical font.
        This function makes sure identical fonts have identical id's.

        Arguments:
            id: an integer that is the id of the fontspec.

        Returns:
            an integer that is the corrected id of the fontspec.
        """
        if id in self.duplicates:
            return self.duplicates[id]
        else:
            return id


class BoundingBox(object):
    """Define an area that a box covers.

    Used in PDF conversion classes
    """

    def __init__(self):
        """Initialise the BoundingBox class."""
        self.top = sys.maxsize
        self.left = sys.maxsize
        self.bottom = 0
        self.right = 0

    @property
    def width(self):
        """Return the width of a bounding box."""
        return self.right - self.left

    @property
    def height(self):
        """Return the height of a bounding box."""
        return self.bottom - self.top

    def is_below(self, other_box):
        """True if this element is below other_box."""
        return self.top >= other_box.bottom

    def is_above(self, other_box):
        """True if this element is above other_box."""
        return other_box.top >= self.bottom

    def is_right_of(self, other_box):
        """True if this element is right of other_box."""
        return self.left >= other_box.right

    def is_left_of(self, other_box):
        """True if this element is left of other_box."""
        return self.right <= other_box.left

    def is_covered(self, other_box):
        """Check if self is sideways (partly) covered by other_box."""
        return self.left <= other_box.right and self.right >= other_box.left

    def increase_box(self, other_box):
        """Increase area of the boundingbox."""
        if self.top > other_box.top:
            self.top = other_box.top
        if self.left > other_box.left:
            self.left = other_box.left
        if self.bottom < other_box.bottom:
            self.bottom = other_box.bottom
        if self.right < other_box.right:
            self.right = other_box.right

    def __unicode__(self):
        """Turn the data in this class into a string."""
        info = []
        for key, value in six.iteritems(self.__dict__):
            info.append(six.text_type(key) + u' ' + six.text_type(value))
        info.append(u'height ' + six.text_type(self.height))
        info.append(u'width ' + six.text_type(self.width))

        return u'\n'.join(info)


class PDFTextElement(BoundingBox):
    """pdf2xml text elements are enclosed in this class."""

    def __init__(self, t):
        """Initialise the PDFTextElement class.

        Arguments:
            t: a pdf2xml text element
        """
        self.t = t

    @property
    def top(self):
        """Return the top of the text element."""
        return int(self.t.get('top'))

    @property
    def left(self):
        """Return the left point of the text element."""
        return int(self.t.get('left'))

    @property
    def height(self):
        """Return the height of the text element."""
        return int(self.t.get('height'))

    @property
    def width(self):
        """Return the width of the text element."""
        return int(self.t.get('width'))

    @property
    def bottom(self):
        """Return the bottom of the text element."""
        return self.top + self.height

    @property
    def right(self):
        """Return the right point of the text element."""
        return self.left + self.width

    @property
    def font(self):
        """Return the font id of the text element."""
        return self.t.get('font')

    @property
    def plain_text(self):
        """Return the plain text of the text element."""
        return self.t.xpath("string()")

    def is_text_on_same_line(self, other_box):
        """Check if this text element is on the same line as other_box."""
        return not self.is_below(other_box) and not self.is_above(other_box)

    def remove_superscript(self):
        """Remove text from text elements that seem to be superscripts."""
        with util.ignored(ValueError):
            int(self.t.xpath("string()").strip())
            child = self.t
            while len(child):
                child = child[0]
            child.text = re.sub('\d+', '', child.text)

    def merge_text_elements(self, other_box):
        """Merge the contents of other_box into self."""
        prev_t = self.t
        t = other_box.t
        if not len(prev_t):
            if t.text is not None:
                if prev_t.text is None:
                    prev_t.text = t.text
                else:
                    prev_t.text += t.text
        else:
            last = prev_t[-1]
            if t.text is not None:
                if last.tail is None:
                    last.tail = t.text
                else:
                    last.tail += t.text
        for child in t:
            prev_t.append(child)

        prev_t.set('width', six.text_type(self.width + other_box.width))
        if self.height < other_box.height:
            prev_t.set('height', six.text_type(other_box.height))

    def __unicode__(self):
        """Turn the data in this class into a string."""
        info = []
        info.append(u'text ' + self.plain_text)
        info.append(u'top ' + six.text_type(self.top))
        info.append(u'left ' + six.text_type(self.left))
        info.append(u'bottom ' + six.text_type(self.bottom))
        info.append(u'right ' + six.text_type(self.right))
        info.append(u'height ' + six.text_type(self.height))
        info.append(u'width ' + six.text_type(self.width))

        return '\n'.join(info)


class PDFParagraph(object):
    """Mimic a paragraph.

    textelements is a list of PDFTextElements

    boundingboxes is a list of BoundingBoxes.
    Since a paragraph can span several columns, there will be made a
    boundingbox for each column.

    in_list is a boolean to indicate whether the paragraph contains a
    list
    """

    LIST_CHARS = [
        u'•',  # U+2022: BULLET
        u'–',  # U+2013: EN DASH
        u'\-',  # U+00AD: HYPHEN-MINUS
        six.unichr(61623),  # U+F0B7
        six.unichr(61553),  # U+F071
        u'■',  # U+25A0: BLACK SQUARE
    ]
    LIST_RE = re.compile(u'^[{}].'.format(u''.join(LIST_CHARS)))

    def __init__(self, linespacing):
        """Initialise the PDFParagraph class."""
        self.textelements = []
        self.boundingboxes = [BoundingBox()]
        self.is_listitem = False
        self.linespacing = linespacing

    def append_textelement(self, textelement):
        """Append a PDFTextElement to this paragraph.

        Arguments:
            textelement: a PDFTextElement
        """
        if (textelement.plain_text and
                self.LIST_RE.search(textelement.plain_text)):
            self.is_listitem = True
        if self.textelements and textelement.is_right_of(self.textelements[-1]):
            self.boundingboxes.append(BoundingBox())
        self.boundingboxes[-1].increase_box(textelement)
        self.textelements.append(textelement)

    def is_within_line_distance(self, textelement):
        """Check if a textelement is in the same paragraph.

        Arguments:
            textelement: a PDFTextElement.

        Returns:
            A boolean indicating whether textelement belongs to this
            paragraph.
        """
        ratio = self.linespacing
        delta = textelement.top - self.textelements[-1].top

        return delta < ratio * self.textelements[-1].height

    def is_same_paragraph(self, textelement):
        """Decide whether textelement belongs to this paragraph."""
        if self.LIST_RE.search(textelement.plain_text):
            return False
        elif self.is_listitem:
            if (self.textelements[-1].is_above(textelement) and
                    (
                        (self.textelements[0].left < textelement.left and
                         re.search('^\S', textelement.plain_text)) or
                        (self.textelements[0].left == textelement.left and
                         re.search('^\s', textelement.plain_text))
            ) and
                    not textelement.is_left_of(self.textelements[-1]) and
                    self.is_within_line_distance(textelement) and
                    self.textelements[-1].font == textelement.font):
                return True
            elif (self.textelements[-1].is_left_of(textelement) and
                  self.textelements[-1].is_below(textelement) and
                  self.textelements[-1].font == textelement.font and
                  (
                      (not re.search(u'[.?!]\s*$', self.textelements[-1].plain_text) and
                       textelement.plain_text[0] == textelement.plain_text[0].lower()) or
                      (re.search(u'[.?!]\s*$', self.textelements[-1].plain_text) and
                       textelement.plain_text[0] == textelement.plain_text[0].upper())
            )):
                return True
            else:
                return False
        elif not self.is_listitem:
            if (self.textelements[-1].is_above(textelement) and
                    self.textelements[-1].font == textelement.font and
                    self.is_within_line_distance(textelement)):
                return True
            elif (self.textelements[-1].is_left_of(textelement) and
                  self.textelements[-1].is_below(textelement) and
                  self.textelements[-1].font == textelement.font and
                  not re.match('\d', self.textelements[-1].plain_text[0]) and
                  self.textelements[-1].plain_text[0] ==
                  self.textelements[-1].plain_text[0].lower()):
                return True
            else:
                return False
        else:
            return False

    def __unicode__(self):
        """Turn the data in this class into a string."""
        return u'\n'.join([t.plain_text for t in self.textelements])


class PDFSection(BoundingBox):
    """A PDFSection contains paragraphs that belong together.

    A PDFSection conceptually covers the page width.

    paragraphs is a list of PDFParagraphs
    """

    def __init__(self):
        """Initialise the PDFSection class."""
        super(PDFSection, self).__init__()
        self.paragraphs = []
        self.column_width = 0

    def append_paragraph(self, paragraph):
        """Append a paragraph and increase the area of the section.

        paragraph is PDFParagraph
        """
        for box in paragraph.boundingboxes:
            self.increase_box(box)
            if box.width > self.column_width:
                self.column_width = box.width

        self.paragraphs.append(paragraph)

    def is_same_section(self, paragraph):
        """Define whether a paragraph belongs to this section.

        Use the left and width properties to define this.

        paragraph is PDFParagraph
        """
        if not self.paragraphs:
            return True
        else:
            prev_box = self.paragraphs[-1].boundingboxes[-1]
            new_box = paragraph.boundingboxes[0]

            # If the ending of the last paragraph and the start of the new
            # paragraph are in the same column, this check is done
            if prev_box.is_above(new_box):
                if (paragraph.is_listitem or
                    (prev_box.left == new_box.left and
                     self.column_width * 1.1 > new_box.width)):
                    return True
                else:
                    return False
            # If the ending of the last paragraph and the start of the new
            # paragraph are in different columns, this check is done
            elif (prev_box.is_left_of(new_box) and
                  new_box.bottom > self.top and
                  self.column_width * 1.1 > new_box.width):
                return True
            else:
                return False

    def __unicode__(self):
        """Turn the data in this class into a string."""
        info = [six.text_type(paragraph)
                for paragraph in self.paragraphs]

        info.append(super(PDFSection, self).__unicode__())

        return u'\n'.join(info)


class OrderedPDFSections(object):
    """Place the PDFSections in the order they are placed on the page.

    sections is a list of PDFSections

    pdftohtml mostly renders the content of a pdf in the
    reading order. In that case a PDFSection covers the
    whole page.

    In other cases, separate sections of a page are rendered
    in the reading order, but the sections are mixed up.

    One example, where the main heading that belongs almost at
    the top of the page, but appears as the last element of a
    page element, is illustrated in TestPDFSection2.

    Another example, where a page contains multicolumn text
    intersperced with tables, is illustrated in TestPDFSection1.
    """

    def __init__(self):
        """Initialise the OrderedPDFSections class."""
        self.sections = []

    def find_position(self, new_section):
        """Find the position of the new section in self.sections.

        Arguments:
            new_section: a PDFSection

        Returns:
            An integer indicating where it was should be placed in
            self.section.
        """
        for i, section in enumerate(self.sections):
            if new_section.is_above(section):
                return i
        else:
            return len(self.sections)

    def insert_section(self, new_section):
        """new_section is a PDFSection."""
        i = self.find_position(new_section)
        if not self.sections or i == len(self.sections):
            self.sections.append(new_section)
        else:
            if i < len(self.sections) and self.sections[i].is_below(new_section):
                self.sections.insert(i, new_section)
            else:
                if i < 0:
                    util.print_frame(debug=six.text_type(self.sections[i - 1]))
                util.print_frame(debug=six.text_type(new_section))
                util.print_frame(debug=six.text_type(self.sections[i]))
                assert self.sections[i].is_below(new_section), \
                    'new_section does not fit between sections'

    @property
    def paragraphs(self):
        """Return the paragraphs in all sections."""
        return [p
                for section in self.sections
                for p in section.paragraphs]


class PDFTextExtractor(object):
    """Extract text from a list of PDFParagraphs.

    Attributes:
        body (etree.Element): Contains the text of all pdf pages.
    """

    def __init__(self):
        """Initialise the PDFTextExtractor class."""
        self.body = etree.Element('body')
        etree.SubElement(self.body, 'p')

    @property
    def p(self):
        """Return the last paragraph in self.body."""
        return self.body[-1]

    def append_to_body(self):
        """Append an empty p element to self.body."""
        etree.SubElement(self.body, 'p')

    def append_text_to_p(self, text):
        """Append text to self.p.

        Args:
            text (str): content of a text element.
        """
        if not len(self.p) and not self.p.text:
            self.p.text = text
        elif not len(self.p) and self.p.text:
            self.p.text += text
        if len(self.p):
            last = self.p[-1]
            if not last.tail:
                last.tail = text
            else:
                last.tail += text

    def extract_textelement(self, textelement):
        """Convert one <text> element to an array of text and etree Elements.

        A <text> element can contain <i> and <b> elements.

        <i> elements can contain <b> and <a> elements.
        <b> elements can contain <i> and <a> elements.

        The text and tail parts of the elements contained in the <i> and <b>
        elements become the text parts of <i> and <b> elements.
        """
        # print(util.lineno(), etree.tostring(textelement), file=sys.stderr)
        if textelement.text:
            self.append_text_to_p(textelement.text)

        for child in textelement:
            em = etree.Element('em')

            if child.text:
                em.text = child.text
            else:
                em.text = ''

            if len(child):
                for grandchild in child:
                    if grandchild.text:
                        em.text += grandchild.text
                    if grandchild.tail:
                        em.text += grandchild.tail

            if child.tag == 'i':
                em.set('type', 'italic')
            elif child.tag == 'b':
                em.set('type', 'bold')

            em.tail = child.tail

            if len(self.p):
                last = self.p[-1]
                if last.tail is None and last.tag == em.tag and last.attrib == em.attrib:
                    if last.text:
                        last.text += em.text
                    else:
                        last.text = em.text
                    last.tail = em.tail
                else:
                    self.p.append(em)
            else:
                self.p.append(em)

    @property
    def last_string(self):
        """Get the plain text of the last paragraph of body."""
        return self.p.xpath("string()")

    def handle_line_ending(self):
        r"""Add a soft hyphen or a space at the end of self.p.

        If - is followed by a space, do not replace it by a soft hyphen
        Sometimes this should be replaced by a soft hyphen, other times not.
        Examples of when not to replace it:
        katt- \n
        og hundehold
        giella- \n
        ja guovlodepartemeanta

        Examples of when to replace it:
        katte-\n
        hår
        gussa-\n
        seaibi

        The tech to be able to replace it is not accessible at this stage.
        """
        if re.search('\S-$', self.last_string):
            if not len(self.p):
                self.p.text = self.p.text[:-1] + u'\xAD'
            else:
                last = self.p[-1]
                if last.tail is None:
                    last.text = last.text[:-1] + u'\xAD'
                else:
                    last.tail = last.tail[:-1] + u'\xAD'
        elif self.last_string and not re.search(u'[\s\xAD]$',
                                                      self.last_string):
            self.extract_textelement(etree.fromstring('<text> </text>'))

    def is_first_page(self):
        """Find out if we are at the first page.

        Returns:
            A boolean indicating if this is the first page.
        """
        return len(self.body) == 1 and not self.last_string

    def is_last_paragraph_end_of_page(self):
        """Find out if the last paragraph is at the end of the page.

        Returns:
            A boolean indicating if this is the last paragraph of the page.
        """
        return (self.last_string and
                re.search(u'[.?!]\s*$', self.last_string))

    def is_new_page(self, paragraph):
        """Check if the paragraph is the start of a new page.

        Args:
            paragraph (PDFParagraph)

        Returns:
            bool
        """
        firstletter = paragraph.textelements[-1].plain_text[0]
        return firstletter == firstletter.upper()

    def extract_text_from_paragraph(self, paragraph):
        """Append text from a paragraph to the xml document.

        Args:
            paragraph (PDFParagraph)
        """
        for textelement in paragraph.textelements:
            self.extract_textelement(textelement.t)
            self.handle_line_ending()
        self.append_to_body()

    def extract_text_from_page(self, paragraphs):
        """Append text from a page to the xml document.

        Args:
            paragraphs (list of PDFParagraph): contains the text of one pdf
                page.
        """
        if (not self.is_first_page() and
            (self.is_new_page(paragraphs[0]) or
             self.is_last_paragraph_end_of_page())):
            self.append_to_body()

        for paragraph in paragraphs:
            if paragraph.is_listitem:
                self.p.set('type', 'listitem')
            self.extract_text_from_paragraph(paragraph)

        if not self.last_string:
            self.body.remove(self.p)


class PDFEmptyPageError(Exception):
    """Raise this exception if a pdf page is empty."""

    pass


class PDFPageMetadata(object):
    """Read pdf metadata from the metadata file into this class.

    Compute metadata needed by the conversion from the data contained in
    this class.
    """

    def __init__(self, page_number=0, page_height=0, page_width=0,
                 metadata_margins={}, metadata_inner_margins={}):
        """Initialise the PDFPageMetadata class.

        Arguments:
            page_number: integer
            page_height: integer
            page_width: integer
            metadata_margins: a dict containing margins read from the metadata
            file.
            metadata_inner_margins: a dict containing inner_margins read from
            the metadata file.
        """
        self.page_number = page_number
        self.page_height = page_height
        self.page_width = page_width
        self.metadata_margins = metadata_margins
        self.metadata_inner_margins = metadata_inner_margins

    def compute_margins(self):
        """Compute the margins of a page in pixels.

        :returns: a dict containing the four margins in pixels
        """
        margins = {margin: self.compute_margin(margin)
                   for margin in ['right_margin', 'left_margin', 'top_margin',
                                  'bottom_margin']}

        return margins

    def compute_margin(self, margin):
        """Compute a margin in pixels.

        :param margin: the name of the  margin

        :return: an int telling where the margin is on the page.
        """
        coefficient = self.get_coefficient(margin)

        if margin == 'left_margin':
            return int(coefficient * self.page_width / 100.0)
        if margin == 'right_margin':
            return int(self.page_width - coefficient * self.page_width / 100.0)
        if margin == 'top_margin':
            return int(coefficient * self.page_height / 100.0)
        if margin == 'bottom_margin':
            return int(self.page_height - coefficient * self.page_height / 100.0)

    def get_coefficient(self, margin):
        """Get the width of the margin in percent."""
        coefficient = 7
        if margin in list(self.metadata_margins.keys()):
            m = self.metadata_margins[margin]
            if m.get(six.text_type(self.page_number)) is not None:
                coefficient = m[six.text_type(self.page_number)]
            elif m.get('all') is not None:
                coefficient = m['all']
            elif self.page_number % 2 == 0 and m.get('even') is not None:
                coefficient = m['even']
            elif self.page_number % 2 == 1 and m.get('odd') is not None:
                coefficient = m['odd']

        return coefficient

    def compute_inner_margins(self):
        """Compute inner margins of the document.

        Returns:
            A dict where the key is the name of the margin and the value
            is an integer indicating where the margin is on the page.
        """
        margins = {margin: self.compute_inner_margin(margin)
                   for margin in ['inner_right_margin', 'inner_left_margin',
                                  'inner_top_margin', 'inner_bottom_margin']}

        if (margins['inner_bottom_margin'] == self.page_height and
                margins['inner_top_margin'] == 0 and
                margins['inner_left_margin'] == 0 and
                margins['inner_right_margin'] == self.page_width):
            margins = {}

        return margins

    def compute_inner_margin(self, margin):
        """Compute a margin in pixels.

        :param margin: the name of the margin

        :return: an int telling where the margin is on the page.
        """
        coefficient = self.get_inner_coefficient(margin)

        if margin == 'inner_left_margin':
            return int(coefficient * self.page_width / 100.0)
        if margin == 'inner_right_margin':
            return int(self.page_width - coefficient * self.page_width / 100.0)
        if margin == 'inner_top_margin':
            return int(coefficient * self.page_height / 100.0)
        if margin == 'inner_bottom_margin':
            return int(self.page_height - coefficient * self.page_height / 100.0)

    def get_inner_coefficient(self, margin):
        """Get the width of the margin in percent."""
        coefficient = 0
        if margin in list(self.metadata_inner_margins.keys()):
            m = self.metadata_inner_margins[margin]
            if m.get(six.text_type(self.page_number)) is not None:
                coefficient = m[six.text_type(self.page_number)]
            elif m.get('all') is not None:
                coefficient = m['all']
            elif self.page_number % 2 == 0 and m.get('even') is not None:
                coefficient = m['even']
            elif self.page_number % 2 == 1 and m.get('odd') is not None:
                coefficient = m['odd']

        return coefficient


class PDFPage(object):
    """Reads a page element.

    Attributes:
        textelements (list of PDFTextElements): contains the text of the page
        pdf_pagemetadata (PDFPageMetadata): contains the metadata of the page

    The textelements are manipulated in several ways,
    then ordered in the way they appear on the page and
    finally sent to PDFTextExtractor
    """

    def __init__(self, page_element, metadata_margins={}, metadata_inner_margins={},
                 linespacing={}):
        """Initialise the PDFPage class.

        Arguments:
            page_element: an etree element representing a pdf page
            metadata_margins: a dict containing margins read from the metadata
            file.
            metadata_inner_margins: a dict containing inner_margins read from
            the metadata file.
        """
        self.textelements = [PDFTextElement(t)
                             for t in page_element.iter('text')]
        self.pdf_pagemetadata = PDFPageMetadata(
            page_number=int(page_element.get('number')),
            page_height=int(page_element.get('height')),
            page_width=int(page_element.get('width')),
            metadata_margins=metadata_margins,
            metadata_inner_margins=metadata_inner_margins)
        self.linespacing_dict = linespacing

    def is_skip_page(self, skip_pages):
        """Found out if this page should be skipped.

        Arguments:
            skip_pages (list of mixed): list of the pages that should be
                skipped.

        Returns:
            boolean: True if this page should be skipped, otherwise false.
        """
        return (('odd' in skip_pages and
                 (self.pdf_pagemetadata.page_number % 2) == 1) or
                ('even' in skip_pages and
                 (self.pdf_pagemetadata.page_number % 2) == 0) or
                self.pdf_pagemetadata.page_number in skip_pages)

    @property
    def linespacing(self):
        if self.linespacing_dict.get('all'):
            return self.linespacing_dict['all']
        elif self.linespacing_dict.get('even') and (\
                (self.pdf_pagemetadata.page_number % 2) == 0):
            return self.linespacing_dict['even']
        elif self.linespacing_dict.get('odd') and (\
                (self.pdf_pagemetadata.page_number % 2) == 1):
            return self.linespacing_dict['odd']
        elif self.linespacing_dict.get(self.pdf_pagemetadata.page_number):
            return self.linespacing_dict[self.pdf_pagemetadata.page_number]
        else:
            return 1.5

    def fix_font_id(self, pdffontspecs):
        """Fix font id in text elements.

        Sometimes the same font has different ID's. Correct that ID
        if necessary.

        Arguments:
            pdffontspecs (PDFFontspecs): a PDFFontspecs instance.
        """
        for textelement in self.textelements:
            correct = pdffontspecs.corrected_id(textelement.font)
            textelement.t.set('font', correct)

    def adjust_line_heights(self):
        """Adjust the height if there is a 1 pixel overlap between elements."""
        for i in six.moves.range(1, len(self.textelements)):
            prev_textelement = self.textelements[i - 1]
            textelement = self.textelements[i]
            if prev_textelement.bottom == textelement.top + 1:
                prev_textelement.t.set(
                    'height', six.text_type(prev_textelement.height - 1))

    def remove_footnotes_superscript(self):
        """Remove numbers from elements found by find_footnotes_superscript."""
        for textelement in self.textelements[1:]:
            textelement.remove_superscript()

    def remove_elements_not_within_margin(self):
        """Remove PDFTextElements from textelements if needed."""
        margins = self.pdf_pagemetadata.compute_margins()
        inner_margins = self.pdf_pagemetadata.compute_inner_margins()

        self.textelements[:] = [t for t in self.textelements
                                if self.is_inside_margins(t, margins)]
        if inner_margins:
            self.textelements[:] = [
                t for t in self.textelements
                if not self.is_inside_inner_margins(t, inner_margins)]

    def merge_elements_on_same_line(self):
        """Merge PDFTextElements that are on the same line."""
        same_line_indexes = [i for i in six.moves.range(1,
                                                        len(self.textelements))
                             if self.textelements[i - 1].is_text_on_same_line(
                                 self.textelements[i])]
        for i in reversed(same_line_indexes):
            self.textelements[i - 1].merge_text_elements(
                self.textelements[i])
            del self.textelements[i]

    def remove_invalid_elements(self):
        """Remove elements with empty strings or where the width is zero or negative."""
        self.textelements[:] = [t for t in self.textelements
                                if not (not t.t.xpath("string()").strip() or
                                        t.width < 1)]

    def is_inside_margins(self, t, margins):
        """Check if t is inside the given margins.

        t is a text element
        """
        return (t.top > margins['top_margin'] and
                t.top < margins['bottom_margin'] and
                t.left > margins['left_margin'] and
                t.left < margins['right_margin'])

    def is_inside_inner_margins(self, t, margins):
        """Check if t is inside the given margins.

        Arguments:
            t (etree.Element): a text element
            margins (dict): contains the page margins as pixels

        Returns:
            boolean: True if t is inside the margings, False otherwise
        """
        return (t.top > margins['inner_top_margin'] and
                t.top < margins['inner_bottom_margin'] and
                t.left > margins['inner_left_margin'] and
                t.left < margins['inner_right_margin'])

    def make_unordered_paragraphs(self):
        """Make paragraphs from the text elements found in a pdf page."""
        paragraphs = [PDFParagraph(self.linespacing)]
        textelement = self.textelements[0]
        paragraphs[-1].append_textelement(textelement)

        for textelement in self.textelements[1:]:
            if not paragraphs[-1].is_same_paragraph(textelement):
                paragraphs.append(PDFParagraph(self.linespacing))
            paragraphs[-1].append_textelement(textelement)

        return paragraphs

    def make_ordered_sections(self):
        """Order the text elements the order they appear on the page.

        The text elements are placed into PDFParagraphs,
        the PDFParagraphs are placed into PDFSections and finally
        the PDFSections are placed into an OrderedPDFSections

        Returns a list of PDFParagraphs
        """
        paragraphs = self.make_unordered_paragraphs()
        section = PDFSection()
        section.append_paragraph(paragraphs[0])

        ordered_sections = OrderedPDFSections()

        for paragraph in paragraphs[1:]:
            if not section.is_same_section(paragraph):
                ordered_sections.insert_section(section)
                section = PDFSection()
            section.append_paragraph(paragraph)

        ordered_sections.insert_section(section)

        return ordered_sections

    def pick_valid_text_elements(self):
        """Pick the wanted text elements from a page.

        This is the main function of this class
        """
        self.adjust_line_heights()
        self.remove_elements_not_within_margin()
        self.remove_footnotes_superscript()
        self.merge_elements_on_same_line()
        self.remove_invalid_elements()

        if not self.textelements:
            raise PDFEmptyPageError()
        else:
            ordered_sections = self.make_ordered_sections()
            return ordered_sections.paragraphs


class PDF2XMLConverter(Converter):
    """Class to convert the xml output of pdftohtml to giellatekno xml.

    Attributes:
        extractor (PDFTextExtractor): class to extract text from the xml that
            pdftohtml produces.
        pdffontspecs (PDFFontspecs): class to store fontspecs found in the xml
            pages.
    """

    def __init__(self, filename, write_intermediate=False):
        """Initialise the PDF2XMLConverte class.

        Arguments:
            filename (str): the path to the pdf file.
            write_intermediate (boolean): indicate whether intermediate
                versions of the converter document should be written to disk.
        """
        super(PDF2XMLConverter, self).__init__(filename,
                                               write_intermediate)
        self.extractor = PDFTextExtractor()
        self.pdffontspecs = PDFFontspecs()

    def strip_chars(self, content, extra=u''):
        """Strip unwanted chars from the document.

        Arguments:
            content (str): the xml document that pdftohtml produces
            extra (str): more character that should be removed

        Returns:
            str containing the modified version of the document.
        """
        remove_re = re.compile(u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F{}]'.format(
            extra))
        content, count = remove_re.subn('', content)

        # Microsoft Word PDF's have Latin-1 file names in links; we
        # don't actually need any link attributes:
        content = re.sub(u'<a [^>]+>', '<a>', content)

        return content

    def replace_ligatures(self, content):
        """Replace unwanted strings with correct replacements.

        Arguments:
            content (str): content of an xml document.

        Returns:
            String containing the new content of the xml document.
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
            u" ]": u"",
            u"Ď": u"đ",  # cough
            u"ď": u"đ",  # cough
            u"ﬁ": u"fi",
            u"ﬂ": u"fl",
            u"ﬀ": u"ff",
            u"ﬃ": u"ffi",
            u"ﬄ": u"ffl",
            u"ﬅ": u"ft",
        }

        for key, value in six.iteritems(replacements):
            content = content.replace(key + u' ', value)
            content = content.replace(key, value)

        return content

    def convert2intermediate(self):
        """Convert from pdf to a corpus xml file.

        Returns:
            A corpus xml etree with the content of the pdf file, but without
            most of the metadata.
        """
        document = etree.Element('document')
        etree.SubElement(document, 'header')
        document.append(self.extractor.body)

        command = (
            'pdftohtml -hidden -enc UTF-8 -stdout -nodrm -i -xml {}'.format(
                self.names.orig))
        pdftohtmloutput = self.extract_text(command.split())
        pdf_content = self.replace_ligatures(self.strip_chars(
            pdftohtmloutput.decode('utf8', 'ignore')))

        try:
            root_element = etree.fromstring(pdf_content.encode('utf8'))
        except etree.XMLSyntaxError as e:
            self.handle_syntaxerror(e, util.lineno(),
                                    pdf_content)

        self.parse_pages(root_element)

        return document

    def parse_page(self, page):
        """Parse the page element.

        Arguments:
            page: a pdf xml page element.
        """
        try:
            pdfpage = PDFPage(page, metadata_margins=self.md.margins,
                            metadata_inner_margins=self.md.inner_margins,
                            linespacing=self.md.linespacing)
            if not pdfpage.is_skip_page(self.md.skip_pages):
                pdfpage.fix_font_id(self.pdffontspecs)
                with util.ignored(PDFEmptyPageError):
                    self.extractor.extract_text_from_page(
                        pdfpage.pick_valid_text_elements())
        except xslsetter.XsltError as e:
            raise ConversionError(str(e))

    def parse_pages(self, root_element):
        """Parse the pages of the pdf xml document.

        Arguments:
            root_element: the root element of the pdf2xml document.
        """
        for page in root_element.iter('page'):
            self.add_fontspecs(page)
            self.parse_page(page)

    def add_fontspecs(self, page):
        """Extract font specs found in a pdf2xml page element.

        Arguments:
            page (etree.Element): a pdf page
        """
        for xmlfontspec in page.iter('fontspec'):
            self.pdffontspecs.add_fontspec(xmlfontspec)


class BiblexmlConverter(Converter):
    """Convert bible xml files to the giellatekno xml format."""

    def convert2intermediate(self):
        """Convert the bible xml to intermediate giellatekno xml format."""
        document = etree.Element('document')
        document.append(self.process_bible())

        return document

    def process_verse(self, verse_element):
        """Process the verse element found in bible xml documents.

        Arguments:
            verse_element: an etree element containing the verse element found
            in a bible xml document.

        Returns:
            A string containing the text of the verse element.
        """
        if verse_element.tag != 'verse':
            raise UserWarning(
                '{}: Unexpected element in verse: {}'.format(
                    self.names.orig, verse_element.tag))

        return verse_element.text

    def process_section(self, section_element):
        """Process the section element found in the bible xml documents.

        Arguments:
            section_element: an etree element containing the section element
            found in a bible xml document.

        Returns:
            section: an etree element containing a corpus xml section.
        """
        section = etree.Element('section')

        title = etree.Element('p')
        title.set('type', 'title')
        title.text = section_element.get('title')

        section.append(title)

        verses = []
        for element in section_element:
            if element.tag == 'p':
                if verses:
                    section.append(self.make_p(verses))
                    verses = []
                section.append(self.process_p(element))
            elif element.tag == 'verse':
                text = self.process_verse(element)
                if text:
                    verses.append(text)
            else:
                raise UserWarning(
                    '{}: Unexpected element in section: {}'.format(
                        self.names.orig, element.tag))

        section.append(self.make_p(verses))

        return section

    def process_p(self, p):
        """Convert bible xml verse elements to p elements.

        Arguments:
            p is a bible xml p element.
        Returns:
            a giellatekno xml p element
        """
        verses = []
        for child in p:
            text = self.process_verse(child)
            if text:
                verses.append(text)

        p = etree.Element('p')
        p.text = '\n'.join(verses)

        return p

    @staticmethod
    def make_p(verses):
        """Convert verse strings to p element.

        Arguments:
            verses: a list of strings
        Returns:
            a giellatekno xml p element
        """
        p = etree.Element('p')
        p.text = '\n'.join(verses)

        return p

    def process_chapter(self, chapter_element):
        """Convert a bible xml chapter to a giellatekno xml section one.

        Arguments:
            chapter_element: a bible xml chapter element

        Returns:
            a giellatekno xml section element.
        """
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
                        self.names.orig, child.tag))

        return section

    def process_book(self, book_element):
        """Convert a bible xml book to a giellatekno xml section one.

        Arguments:
            book_element: a bible xml book element

        Returns:
            a giellatekno xml section element.
        """
        section = etree.Element('section')

        title = etree.Element('p')
        title.set('type', 'title')
        title.text = book_element.get('title')

        section.append(title)

        for chapter_element in book_element:
            if chapter_element.tag != 'chapter':
                raise UserWarning(
                    '{}: Unexpected element in book: {}'.format(
                        self.names.orig, chapter_element.tag))
            section.append(self.process_chapter(chapter_element))

        return section

    def process_bible(self):
        """Convert a bible xml document to a giellatekno xml document.

        Returns:
            a giellatekno xml body element.
        """
        bible = etree.parse(self.names.orig)

        body = etree.Element('body')

        for book in bible.xpath('.//book'):
            body.append(self.process_book(book))

        return body


class HTMLContentConverter(object):
    """Convert html documents to the giellatekno xml format."""

    def superclean(self, content):
        """Remove unwanted elements from an html document.

        Arguments:
            content is a string containing an html document.

        Returns:
            a string containing the cleaned up html document.
        """
        cleaner = clean.Cleaner(
            page_structure=False,
            scripts=True,
            javascript=True,
            comments=True,
            style=True,
            processing_instructions=True,
            remove_unknown_tags=True,
            embedded=True,
            kill_tags=[
                'img',
                'area',
                'address',
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
                'colgroup',
            ])

        try:
            return cleaner.clean_html(content)
        except etree.ParserError as e:
            raise ConversionError(six.text_type(e))

    def remove_cruft(self, content):
        """Remove cruft from svenskakyrkan.se documents.

        Args:
            content (str): the content of a document.

        Returns:
            str: The content of the document without the cruft.
        """
        replacements = [
            (u'//<script', u'<script'),
            (u'&nbsp;', u' '),
            (u' ', u' '),
        ]
        return util.replace_all(replacements, content)

    def simplify_tags(self):
        u"""Turn tags to divs.

        We don't care about the difference between <fieldsets>, <legend>
        etc. – treat them all as <div>'s for xhtml2corpus
        """
        superfluously_named_tags = self.soup.xpath(
            "//fieldset | //legend | //article | //hgroup "
            "| //section | //dl | //dd | //dt"
            "| //menu",
            )
        for elt in superfluously_named_tags:
            elt.tag = 'div'

    def fix_spans_as_divs(self):
        """Turn div like elements into div.

        XHTML doesn't allow (and xhtml2corpus doesn't handle) span-like
        elements with div-like elements inside them; fix this and
        similar issues by turning them into divs.
        """
        spans_as_divs = self.soup.xpath(
            "//*[( descendant::div or descendant::p"
            "      or descendant::h1 or descendant::h2"
            "      or descendant::h3 or descendant::h4"
            "      or descendant::h5 or descendant::h6 ) "
            "and ( self::span or self::b or self::i"
            "      or self::em or self::strong "
            "      or self::a )"
            "    ]",
            )
        for elt in spans_as_divs:
            elt.tag = 'div'

        ps_as_divs = self.soup.xpath(
            "//p[descendant::div]",
            )
        for elt in ps_as_divs:
            elt.tag = 'div'

        lists_as_divs = self.soup.xpath(
            "//*[( child::ul or child::ol ) "
            "and ( self::ul or self::ol )"
            "    ]",
            )
        for elt in lists_as_divs:
            elt.tag = 'div'

    def remove_empty_p(self):
        """Remove empty p elements."""
        ps = self.soup.xpath(
            '//p',
            )

        for elt in ps:
            if elt.text is None and elt.tail is None and not len(elt):
                elt.getparent().remove(elt)

    def remove_empty_class(self):
        """Delete empty class attributes."""
        for element in self.soup.xpath('.//*[@class=""]'):
            del element.attrib['class']

    def remove_elements(self):
        """Remove unwanted tags from a html document.

        The point with this exercise is to remove all but the main content of
        the document.
        """
        unwanted_classes_ids = {
            'div': {
                'class': [
                    'AddThis',  # lansstyrelsen.se
                    'InnholdForfatter',  # unginordland
                    'NavigationLeft',  # lansstyrelsen.se
                    'QuickNav',
                    'ad',
                    'andrenyheter',  # tysfjord.kommune.no
                    'art-layout-cell art-sidebar2',  # gaaltije.se
                    'art-postheadericons art-metadata-icons',  # gaaltije.se
                    'article-ad',
                    'article-bottom-element',
                    'article-column',
                    ('article-dateline article-dateline-footer '
                     'meta-widget-content'),  # nrk.no
                    ('article-dateline article-footer '
                     'container-widget-content cf'),  # nrk.no
                    'article-heading-wrapper',  # 1177.se
                    'article-info',  # regjeringen.no
                    'article-related',
                    'article-toolbar__tool',  # umo.se
                    'article-universe-teaser container-widget-content',
                    'articleImageRig',
                    'articlegooglemap',  # tysfjord.kommune.no
                    'articleTags',  # nord-salten.no
                    'attribute-related_object',  # samediggi.no
                    'authors',
                    'authors ui-helper-clearfix',  # nord-salten.no
                    'back_button',
                    'banner-element',
                    'breadcrumbs ',
                    'breadcrumbs',
                    'breadcrums span-12',
                    'btm_menu',
                    'byline',  # arran.no
                    'c1',  # jll.se
                    'art-bar art-nav',  # gaaltije.se
                    'art-layout-cell art-sidebar1',  # gaaltije.se
                    'clearfix breadcrumbsAndSocial noindex',  # udir.no
                    'complexDocumentBottom',  # regjeringen.no
                    'container-widget-content',  # nrk.no
                    'container_full',
                    'documentInfoEm',
                    'documentPaging',
                    'documentPaging PagingBtm',  # regjeringen.no
                    'documentTop',  # regjeringen.no
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
                    'historic-info',  # regjeringen.no
                    'historic-label',  # regjeringen.no
                    'imagecontainer',
                    'innholdsfortegenlse-child',
                    'latestnews_uutisarkisto',
                    'ld-navbar',
                    'meta',
                    'meta ui-helper-clearfix',  # nord-salten.no
                    'authors ui-helper-clearfix',  # nord-salten.no
                    'menu',  # visitstetind.no
                    'metaWrapper',
                    'moduletable_oikopolut',
                    'moduletable_etulinkki',  # www.samediggi.fi
                    'naviHlp',  # visitstetind.no
                    'noindex',  # ntfk
                    'nrk-globalfooter',  # nrk.no
                    'nrk-globalfooter-dk lp_globalfooter',  # nrk.no
                    'nrk-globalnavigation',  # nrk.no
                    'nrkno-share bulletin-share',  # nrk.no
                    'outer-column',
                    'plug-teaser',  # nrk.no
                    'post-footer',
                    'printbutton-wrapper',  # 1177.se
                    'printContact',
                    'right',  # ntfk
                    'rightverticalgradient',  # udir.no
                    'sharebutton-wrapper',  # 1177.se
                    'sharing',
                    'sidebar',
                    'spalte300',  # osko.no
                    'subfooter',  # visitstetind.no
                    'tabbedmenu',
                    'tipformcontainer',  # tysfjord.kommune.no
                    'tipsarad mt6 selfClear',
                    'titlepage',
                    'toc-placeholder',  # 1177.se
                    'toc',
                    'tools',  # arran.no
                ],
                'id': [
                    'print-logo-wrapper',  # 1177.se
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
                    'PageLanguageInfo',   # regjeringen.no
                    'PrintDocHead',
                    'SamiDisclaimer',
                    'ShareArticle',
                    'WIPSELEMENT_CALENDAR',  # learoevierhtieh.no
                    'WIPSELEMENT_HEADING',  # learoevierhtieh.no
                    'WIPSELEMENT_MENU',  # learoevierhtieh.no
                    'WIPSELEMENT_MENURIGHT',  # learoevierhtieh.no
                    'WIPSELEMENT_NEWS',  # learoevierhtieh.no
                    'WebPartZone1',  # lansstyrelsen.se
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
                    'ctl00_AccesskeyShortcuts',  # lansstyrelsen.se
                    'ctl00_ctl00_ArticleFormContentRegion_'
                    'ArticleBodyContentRegion_ctl00_'
                    'PageToolWrapper',  # 1177.se
                    'ctl00_ctl00_ArticleFormContentRegion_'
                    'ArticleBodyContentRegion_ctl03_'
                    'PageToolWrapper',  # 1177.se
                    'ctl00_Cookies',  # lansstyrelsen.se
                    'ctl00_FullRegion_CenterAndRightRegion_HitsControl_'
                    'ctl00_FullRegion_CenterAndRightRegion_Sorting_sortByDiv',
                    'ctl00_LSTPlaceHolderFeedback_'
                    'editmodepanel31',  # lansstyrelsen.se
                    'ctl00_LSTPlaceHolderSearch_'
                    'SearchBoxControl',  # lansstyrelsen.se
                    'ctl00_MidtSone_ucArtikkel_ctl00_ctl00_ctl01_divRessurser',
                    'ctl00_MidtSone_ucArtikkel_ctl00_divNavigasjon',
                    'ctl00_PlaceHolderMain_EditModePanel1',  # lansstyrelsen.se
                    'ctl00_PlaceHolderTitleBreadcrumb_'
                    'DefaultBreadcrumb',  # lansstyrelsen.se
                    'ctl00_TopLinks',  # lansstyrelsen.se
                    'deleModal',
                    'document-header',
                    'errorMessageContainer',  # nord-salten.no
                    'final-footer-wrapper',  # 1177.se
                    'flu-vaccination',  # 1177.se
                    'footer',  # forrest, too, tysfjord.kommune.no
                    'footer-wrapper',
                    'frontgallery',  # visitstetind.no
                    'header',
                    'headerBar',
                    'headWrapper',  # osko.no
                    'hoyre',  # unginordland
                    'innholdsfortegnelse',  # regjeringen.no
                    'leftMenu',
                    'leftPanel',
                    'leftbar',  # forrest (divvun and giellatekno sites)
                    'leftcol',  # new samediggi.no
                    'leftmenu',
                    'main_navi_main',           # www.samediggi.fi
                    'mainContentBookmark',  # udir.no
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
                    'phone-bar',  # 1177.se
                    'publishinfo',  # 1177.se
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
                    'svid10_49531bad1412ceb82564aea',  # ostersund.se
                    'svid10_6ba9fa711d2575a2a7800024318',  # jll.se
                    'svid10_6c1eb18a13ec7d9b5b82ee7',  # ostersund.se
                    'svid10_b0dabad141b6aeaf101229',  # ostersund.se
                    'svid10_49531bad1412ceb82564af3',  # ostersund.se
                    'svid10_6ba9fa711d2575a2a7800032145',  # jll.se
                    'svid10_6ba9fa711d2575a2a7800032151',  # jll.se
                    'svid10_6ba9fa711d2575a2a7800024344',  # jll.se
                    'svid10_6ba9fa711d2575a2a7800032135',  # jll.se
                    'svid10_6c1eb18a13ec7d9b5b82ee3',  # ostersund.se
                    'svid10_6c1eb18a13ec7d9b5b82edf',  # ostersund.se
                    'svid10_6c1eb18a13ec7d9b5b82edd',  # ostersund.se
                    'svid10_6c1eb18a13ec7d9b5b82eda',  # ostersund.se
                    'svid10_6c1eb18a13ec7d9b5b82ed5',  # ostersund.se
                    'svid12_6ba9fa711d2575a2a7800032140',  # jll.se
                    'theme-area-label-wrapper',  # 1177.se
                    'tipafriend',
                    'tools',  # arran.no
                    'topHeader',  # nord-salten.no
                    'topMenu',
                    'topUserMenu',
                    'top',  # arran.no
                    'topnav',  # tysfjord.kommune.no
                    'toppsone',  # unginordland
                    'vedleggogregistre',  # regjeringen.no
                    'venstre',  # unginordland
                ],
            },
            'p': {
                'class': [
                    'WebPartReadMoreParagraph',
                    'breadcrumbs',
                    'langs',  # oahpa.no
                    'art-page-footer',  # gaaltije.se
                ],
            },
            'ul': {
                'id': [
                    'AreaTopLanguageNav',
                    'AreaTopPrintMeny',
                    'skiplinks',  # umo.se
                ],
                'class': [
                    'QuickNav',
                    'article-tools',
                    'article-universe-list',  # nrk.no
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
                    'breadcrumbs pathway',  # gaaltije.se
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
                    'skip-link',  # 1177.se
                    'toggle-link expanded',  # 1177.se
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
                    'pageHeader ',  # regjeringen.no
                ],
            },
            'section': {
                'class': [
                    'section-theme-sub-nav',  # 1177.se
                    'span3',  # samernas.se
                    'tree-menu current',  # umo.se
                    'tree-menu',  # umo.se
                ],
            },
        }

        ns = {'html': 'http://www.w3.org/1999/xhtml'}
        for tag, attribs in six.iteritems(unwanted_classes_ids):
            for key, values in six.iteritems(attribs):
                for value in values:
                    search = ('.//{}[@{}="{}"]'.format(tag, key, value))
                    for unwanted in self.soup.xpath(search, namespaces=ns):
                        unwanted.getparent().remove(unwanted)

    def add_p_around_text(self):
        """Add p around text after an hX element."""
        stop_tags = [
            'p',
            'h3',
            'h2',
            'div',
            'table']
        for h in self.soup.xpath(
                './/body/*',
                ):
            if h.tail is not None and h.tail.strip() != '':
                p = etree.Element('p')
                p.text = h.tail
                h.tail = None
                for next_element in iter(h.getnext, None):
                    if next_element.tag in stop_tags:
                        break
                    p.append(next_element)

                h_parent = h.getparent()
                h_parent.insert(h_parent.index(h) + 1, p)

        # br's are not allowed right under body in XHTML:
        for elt in self.soup.xpath(
                './/body/br',
                ):
            elt.tag = 'p'
            elt.text = ' '

    def center2div(self):
        """Convert center to div in tidy style."""
        for center in self.soup.xpath(
                './/center',
                ):
            center.tag = 'div'
            center.set('class', 'c1')

    def body_i(self):
        """Wrap bare elements inside a p element."""
        for tag in ['a', 'i', 'em', 'u', 'strong', 'span']:
            for bi in self.soup.xpath(
                    './/body/{}'.format(tag),
                    ):
                p = etree.Element('p')
                bi_parent = bi.getparent()
                bi_parent.insert(bi_parent.index(bi), p)
                p.append(bi)

    @staticmethod
    def handle_font_text(font_elt):
        """Incorporate font.text into correct element.

        Args:
            font_elt (etree.Element): a font element.
        """
        font_parent = font_elt.getparent()
        font_index = font_parent.index(font_elt)

        if font_elt.text is not None:
            if font_index > 0:
                previous_element = font_parent[font_index - 1]
                if previous_element.tail is not None:
                    previous_element.tail += font_elt.text
                else:
                    previous_element.tail = font_elt.text
            else:
                if font_elt.text is not None:
                    if font_parent.text is not None:
                        font_parent.text += font_elt.text
                    else:
                        font_parent.text = font_elt.text

    @staticmethod
    def handle_font_children(font_elt):
        """Incorporate font children into correct element.

        Args:
            font_elt (etree.Element): a font element.
        """
        font_parent = font_elt.getparent()
        font_index = font_parent.index(font_elt)

        for position, font_child in enumerate(font_elt, start=font_index):
            if font_elt.tail is not None:
                if font_elt[-1].tail is not None:
                    font_elt[-1].tail += font_elt.tail
                else:
                    font_elt[-1].tail = font_elt.tail
            font_parent.insert(position, font_child)

    @staticmethod
    def handle_font_tail(font_elt):
        """Incorporate font.tail into correct element.

        Args:
            font_elt (etree.Element): a font element.
        """
        font_parent = font_elt.getparent()
        font_index = font_parent.index(font_elt)
        previous_element = font_parent[font_index - 1]

        if font_elt.tail is not None:
            if font_index > 0:
                if previous_element.tail is not None:
                    previous_element.tail += font_elt.tail
                else:
                    previous_element.tail = font_elt.tail
            else:
                if font_parent.text is not None:
                    font_parent.text += font_elt.tail
                else:
                    font_parent.text = font_elt.tail

    def remove_font(self):
        """Remove font elements, incorporate content into it's parent."""
        for font_elt in reversed(list(self.soup.iter('{*}font'))):
            self.handle_font_text(font_elt)

            if len(font_elt) > 0:
                self.handle_font_children(font_elt)
            else:
                self.handle_font_tail(font_elt)

            font_elt.getparent().remove(font_elt)

    def body_text(self):
        """Wrap bare text inside a p element."""
        body = self.soup.find(
            './/body')

        if body.text is not None:
            p = etree.Element('p')
            p.text = body.text
            body.text = None
            body.insert(0, p)

    def convert2xhtml(self, content):
        """Clean up the html document.

        Destructively modifies self.soup, trying
        to create strict xhtml for xhtml2corpus.xsl
        """
        c_content = self.remove_cruft(content)

        c_clean = self.superclean(c_content)
        self.soup = html.document_fromstring(c_clean)
        self.remove_empty_class()
        self.remove_empty_p()
        self.remove_elements()
        self.remove_font()
        self.add_p_around_text()
        self.center2div()
        self.body_i()
        self.body_text()
        self.simplify_tags()
        self.fix_spans_as_divs()

        return self.soup


class HTMLConverter(Converter):
    """Convert html pages to giellatekno xml documents."""

    @property
    def content(self):
        """Return the content of the html doc as a string.

        Returns:
            a string containing the html document.
        """
        for encoding in ['utf-8', 'windows-1252', 'latin1']:
            try:
                with codecs.open(self.names.orig, encoding=encoding) as f:
                    return etree.tostring(
                        html.document_fromstring(
                            self.remove_declared_encoding(f.read())
                        ),
                        encoding='unicode'
                    )
            except UnicodeDecodeError:
                pass

        raise ConversionError('HTML error'.format(self.names.orig))

    def remove_declared_encoding(self, content):
        """Remove declared decoding.

        lxml explodes if we send a decoded Unicode string with an
        xml-declared encoding
        http://lxml.de/parsing.html#python-unicode-strings

        Arguments:
            content: a string containing the html document.

        Returns:
            a string where the declared decoding is removed.
        """
        xml_encoding_declaration_re = re.compile(
            r"^<\?xml [^>]*encoding=[\"']([^\"']+)[^>]*\?>[ \r\n]*",
            re.IGNORECASE)

        return re.sub(xml_encoding_declaration_re, "", content)

    def convert2xhtml(self):
        """Convert html document to a cleaned up xhtml document.

        Returns:
            a cleaned up xhtml document as an etree element.
        """
        converter = HTMLContentConverter()

        return converter.convert2xhtml(self.content)

    @staticmethod
    def replace_bare_text_in_body_with_p(body):
        """Replace bare text in body with a p elemnt."""
        if body.text is not None and body.text.strip() != '':
            new_p = etree.Element('p')
            new_p.text = body.text
            body.text = None
            body.insert(0, new_p)

    @staticmethod
    def add_p_instead_of_tail(intermediate):
        """Convert tail in list and p to a p element."""
        for element in ['list', 'p']:
            for found_element in intermediate.findall('.//' + element):
                if found_element.tail is not None and found_element.tail.strip() != '':
                    new_p = etree.Element('p')
                    new_p.text = found_element.tail
                    found_element.tail = None
                    found_element.addnext(new_p)

    def convert2intermediate(self):
        """Convert the original document to the giellatekno xml format.

        The resulting xml is stored in intermediate
        """
        converter_xsl = os.path.join(here, 'xslt/xhtml2corpus.xsl')

        html_xslt_root = etree.parse(converter_xsl)
        transform = etree.XSLT(html_xslt_root)

        intermediate = transform(self.convert2xhtml())

        self.replace_bare_text_in_body_with_p(intermediate.find('.//body'))
        self.add_p_instead_of_tail(intermediate)

        return intermediate.getroot()


class RTFConverter(HTMLConverter):
    """Convert rtf documents to the giellatekno xml format."""

    @property
    def content(self):
        """Convert the content of an rtf file to xhtml.

        Returns:
            A string containing the xhtml version of the rtf file.
        """
        with open(self.names.orig, "rb") as rtf_document:
            content = rtf_document.read()
            try:
                pyth_doc = Rtf15Reader.read(
                    io.BytesIO(content.replace(b'fcharset256', b'fcharset255')))
                return six.text_type(XHTMLWriter.write(
                    pyth_doc, pretty=True).read(), encoding='utf8')
            except UnicodeDecodeError:
                raise ConversionError('Unicode problems in {}'.format(
                    self.names.orig))


class OdfConverter(HTMLConverter):
    """Convert odf documents to the giellatekno xml format."""

    @property
    def content(self):
        """Convert the content of an odf file to xhtml.

        Returns:
            A string contaning the xhtml version of the odf file.
        """
        generatecss = False
        embedable = True
        odhandler = ODF2XHTML(generatecss, embedable)
        try:
            return odhandler.odf2xhtml(six.text_type(self.names.orig))
        except TypeError as e:
            raise ConversionError('Error: {}'.format(e))


class DocxConverter(HTMLConverter):
    """Convert docx documents to the giellatekno xml format."""

    @property
    def content(self):
        """Convert the content of a docx file to xhtml.

        Returns:
            A string contaning the xhtml version of the docx file.
        """
        return PyDocXHTMLExporter(self.names.orig).export()

    def remove_elements(self):
        """Remove some docx specific html elements."""
        super(DocxConverter, self).remove_elements()

        unwanted_classes_ids = {
            'a': {
                'name': [
                    'footnote-ref',  # footnotes in running text
                ],
            }
        }
        ns = {'html': 'http://www.w3.org/1999/xhtml'}
        for tag, attribs in six.iteritems(unwanted_classes_ids):
            for key, values in six.iteritems(attribs):
                for value in values:
                    search = ('.//html:{}[starts-with(@{}, "{}")]'.format(
                        tag, key, value))
                    for unwanted in self.soup.xpath(search, namespaces=ns):
                        unwanted.getparent().remove(unwanted)


class EpubConverter(HTMLConverter):
    """Convert epub documents to the giellatekno xml format.

    Epub files are zip files that contain text in xhtml files. This class reads
    all xhtml files found in this archive. The body element of these files are
    converted to div elements, and appended inside a new body element.

    It is possible to filter away ranges of elements from this new xhtml file.
    These ranges consist pairs of xpath paths, specified inside the metadata
    file that belongs to this epub file.
    """

    @staticmethod
    def read_chapter(chapter):
        """Read the contents of a epub_file chapter.

        Args:
            chapter (epub.BookChapter): the chapter of an epub file

        Returns:
            str: The contents of a chapter

        Raises:
            ConversionException
        """
        try:
            return etree.fromstring(chapter.read())
        except KeyError as e:
            raise ConversionError(e)

    def chapters(self):
        """Get the all linear chapters of the epub book.

        Yields:
            etree._Element: The body of an xhtml file found in the epub file.
        """
        book = epub.Book(epub.open_epub(self.names.orig))

        for chapter in book.chapters:
            chapterbody = self.read_chapter(chapter).find(
                '{http://www.w3.org/1999/xhtml}body')
            chapterbody.tag = '{http://www.w3.org/1999/xhtml}div'
            yield chapterbody

    @property
    def content(self):
        """Append all chapter bodies as divs to an html file.

        Returns:
            a string containing the content of all xhtml files
            found in the epub file.
        """
        mainbody = etree.Element('{http://www.w3.org/1999/xhtml}body')

        for chapterbody in self.chapters():
            mainbody.append(chapterbody)

        html = etree.Element('{http://www.w3.org/1999/xhtml}html')
        html.append(etree.Element('{http://www.w3.org/1999/xhtml}head'))
        html.append(mainbody)

        if self.md.skip_elements:
            for pairs in self.md.skip_elements:
                self.remove_range(pairs[0], pairs[1], html)

        return etree.tostring(html, encoding='unicode')

    @staticmethod
    def remove_siblings_shorten_path(parts, content, preceding=False):
        """Remove all siblings before or after an element.

        Args:
            parts (list of str): a xpath path split on /
            content (etree._Element): an xhtml document
            preceding (bool): When True, iterate through the preceding siblings
                of the found element, otherwise iterate throughe the following
                siblings.

        Returns:
            list of str: the path to the parent of parts.
        """
        path = '/'.join(parts)
        found = content.find(
            path, namespaces={'html': 'http://www.w3.org/1999/xhtml'})
        parent = found.getparent()
        for sibling in found.itersiblings(preceding=preceding):
            parent.remove(sibling)

        return parts[:-1]

    def shorten_longest_path(self, path1, path2, content):
        """Remove elements from the longest path.

        If starts is longer than ends, remove the siblings following starts,
        shorten starts with one step (going to the parent). If starts still is
        longer than ends, remove the siblings following the parent. This is
        done untill starts and ends are of equal length.

        If on the other hand ends is longer than starts, remove the siblings
        preceding ends, then shorten ends (going to its parent).

        Args:
            path1 (str): path to first element
            path2 (str): path to second element
            content (etree._Element): xhtml document, where elements are
                removed.

        Returns:
            tuple of list of str: paths to the new start and end element, now
                with the same length.
        """
        starts, ends = path1.split('/'), path2.split('/')

        while len(starts) > len(ends):
            starts = self.remove_siblings_shorten_path(starts, content)

        while len(ends) > len(starts):
            ends = self.remove_siblings_shorten_path(
                ends, content, preceding=True)

        return starts, ends

    def remove_trees_with_unequal_parents(self, path1, path2, content):
        """Remove tree nodes that do not have the same parents.

        While the parents in starts and ends are unequal (that means that
        starts and ends belong in different trees), remove elements
        following starts and preceding ends. Shorten the path to the parents
        of starts and ends and remove more elements if needed. starts and
        ends are of equal length.

        Args:
            path1 (str): path to first element
            path2 (str): path to second element
            content (etree._Element): xhtml document, where elements are
                removed.

        Returns:
            tuple of list of str: paths to the new start and end element.
        """
        starts, ends = self.shorten_longest_path(path1, path2, content)

        while starts[:-1] != ends[:-1]:
            starts = self.remove_siblings_shorten_path(starts, content)
            ends = self.remove_siblings_shorten_path(
                ends, content, preceding=True)

        return starts, ends

    def remove_trees_with_equal_parents(self, starts, ends, content):
        """Remove tree nodes that have the same parents.

        Now that the parents of starts and ends are equal, remove the last
        trees of nodes between starts and ends (if necessary).

        Args:
            starts (list of str): path to first element
            ends (list of str): path to second element
            content (etree._Element): xhtml document, where elements are
                removed.
        """
        deepest_start = content.find(
            '/'.join(starts), namespaces={'html': 'http://www.w3.org/1999/xhtml'})
        deepest_end = content.find(
            '/'.join(ends), namespaces={'html': 'http://www.w3.org/1999/xhtml'})
        parent = deepest_start.getparent()
        for sibling in deepest_start.itersiblings():
            if sibling == deepest_end:
                break
            else:
                parent.remove(sibling)

    @staticmethod
    def remove_first_element(path1, content):
        """Remove the first element in the range.

        Args:
            path1 (str): path to the first element to remove.
            content (etree._Element): the xhtml document that should
                be altered.
        """
        first_start = content.find(
            path1, namespaces={'html': 'http://www.w3.org/1999/xhtml'})
        first_start.getparent().remove(first_start)

    def remove_range(self, path1, path2, content):
        """Remove a range of elements from an xhtml document.

        Args:
            path1 (str): path to first element
            path2 (str): path to second element
            content (etree._Element): xhtml document
        """
        starts, ends = self.remove_trees_with_unequal_parents(path1, path2,
                                                              content)
        self.remove_trees_with_equal_parents(starts, ends, content)
        self.remove_first_element(path1, content)


class DocConverter(HTMLConverter):
    """Convert Microsoft Word documents to the giellatekno xml format."""

    @property
    def content(self):
        """Convert a doc file to xhtml.

        Returns:
            A string containing the xhtml version of the doc file.
        """
        command = ['wvHtml',
                   os.path.realpath(self.names.orig),
                   '-']
        try:
            return self.extract_text(command).decode('utf8')
        except:
            return self.extract_text(command).decode('windows-1252')

    def fix_wv_output(self):
        u"""Fix headers in the docx xhtml output.

        Examples of headings:

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

        """
        pass


class DocumentFixer(object):
    """Fix the content of a giellatekno xml document.

    Receive a stringified etree from one of the raw converters,
    replace ligatures, fix the encoding and return an etree with correct
    characters
    """

    def __init__(self, document):
        """Initialise the DocumentFixer class."""
        self.root = document

    def get_etree(self):
        """Get the root of the xml document."""
        return self.root

    def compact_ems(self):
        """Compact consecutive em elements into a single em if possible."""
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
        """Replace soft hyphen chars with hyphen tags."""
        for element in self.root.iter('p'):
            self.replace_shy(element)

    def replace_shy(self, element):
        """Replace shy with a hyph element.

        Arguments:
            element: an etree element
        """
        for child in element:
            self.replace_shy(child)

        text = element.text
        if text is not None:
            parts = text.split(u'­')
            if len(parts) > 1:
                element.text = parts[0]
                for x, part in enumerate(parts[1:]):
                    hyph = etree.Element('hyph')
                    hyph.tail = part
                    element.insert(x, hyph)

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
        """Insert space after semicolon where needed."""
        irritating_words_regex = re.compile(u'(govv(a|en|ejeaddji):)([^ ])',
                                            re.UNICODE | re.IGNORECASE)
        for child in self.root.find('.//body'):
            self.insert_space_after_semicolon(child, irritating_words_regex)

    def insert_space_after_semicolon(self, element, irritating_words_regex):
        """Insert space after words needing it.

        Arguments:
            element: an etree element
            irritating_words_regex: regex
        """
        if element.text is not None:
            element.text = irritating_words_regex.sub(r'\1 \3', element.text)
        for child in element:
            self.insert_space_after_semicolon(child, irritating_words_regex)
        if element.tail is not None:
            element.tail = irritating_words_regex.sub(r'\1 \3', element.tail)

    def replace_ligatures(self):
        """Replace unwanted chars."""
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
            u" ]": u"",
            u"Ď": u"đ",  # cough
            u"ď": u"đ",  # cough
            "\x03": u"",
            "\x04": u"",
            "\x07": u"",
            "\x08": u"",
            "\x0F": u"",
            "\x10": u"",
            "\x11": u"",
            "\x13": u"",
            "\x14": u"",
            "\x15": u"",
            "\x17": u"",
            "\x18": u"",
            "\x1A": u"",
            "\x1B": u"",
            "\x1C": u"",
            "\x1D": u"",
            "\x1E": u"",
            u"ﬁ": "fi",
            u"ﬂ": "fl",
            u"ﬀ": "ff",
            u"ﬃ": "ffi",
            u"ﬄ": "ffl",
            u"ﬅ": "ft",
        }

        for element in self.root.iter('p'):
            if element.text:
                for key, value in six.iteritems(replacements):
                    element.text = element.text.replace(key + ' ', value)
                    element.text = element.text.replace(key, value)

    def replace_bad_unicode(self):
        """Replace some chars in an otherwise 'valid utf-8' document.

        These chars e.g. 'valid utf-8' (don't give UnicodeDecodeErrors), but
        we still want to replace them to what they most likely were
        meant to be.

        :param content: a unicode string
        :returns: a cleaned up unicode string
        """
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
        """Replace invalid accents with valid ones for the sms language."""
        replacement_pairs = [
            (u'\u2019', u'\u02BC'),
            (u'\u0027', u'\u02BC'),
            (u'\u2032', u'\u02B9'),
            (u'\u00B4', u'\u02B9'),
        ]

        for replacement_pair in replacement_pairs:
            if element.text:
                element.text = element.text.replace(replacement_pair[0],
                                                    replacement_pair[1])
            if element.tail:
                element.tail = element.tail.replace(replacement_pair[0],
                                                    replacement_pair[1])
        for child in element:
            self.fix_sms(child)

    def fix_body_encoding(self, mainlang):
        """Replace wrongly encoded saami chars with proper ones.

        Send a stringified version of the body into the EncodingGuesser class.
        It returns the same version, but with fixed characters.
        Parse the returned string, insert it into the document
        """
        self.replace_ligatures()

        body = self.root.find('body')
        bodyString = etree.tostring(body, encoding='unicode')
        body.getparent().remove(body)

        eg = decode.EncodingGuesser()
        encoding = eg.guess_body_encoding(bodyString)

        try:
            body = etree.fromstring(eg.decode_para(encoding, bodyString))
        except UnicodeEncodeError as error:
            util.print_frame('Detected encoding: {}'.format(encoding))
            util.print_frame(bodyString[:error.start], '\n')
            util.print_frame(bodyString[error.start:error.end],
                             ord(bodyString[error.start:error.start + 1]),
                             hex(ord(bodyString[error.start:error.start + 1])), '\n')
            util.print_frame(bodyString, '\n')
            raise UserWarning(str(error))
        self.root.append(body)

        if mainlang == 'sms':
            self.fix_sms(self.root.find('body'))

    def fix_title_person(self, encoding):
        """Fix encoding problems."""
        eg = decode.EncodingGuesser()

        title = self.root.find('.//title')
        if title is not None and title.text is not None:
            text = title.text

            text = text
            util.print_frame(encoding)
            title.text = eg.decode_para(encoding, text)

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
                        lastname))

                firstname = person.get('firstname')

                if encoding == 'mac-sami_to_latin1':
                    firstname = firstname.replace(u'‡', u'á')
                    firstname = firstname.replace(u'Œ', u'å')

                person.set(
                    'firstname',
                    eg.decode_para(
                        encoding,
                        firstname))

    @staticmethod
    def get_quote_list(text):
        """Get list of quotes from the given text.

        Arguments:
            text: string

        Returns:
            A list of span tuples containing indexes to quotes found in text.
        """
        unwanted = '[^:,!?.\s]'
        quote_regexes = [re.compile('"{0}.+?{0}"'.format(unwanted)),
                         re.compile(u'«.+?»'),
                         re.compile(u'“.+?”'),
                         re.compile(u'”{0}.+?{0}”'.format(unwanted)), ]
        quote_list = [m.span()
                      for quote_regex in quote_regexes
                      for m in quote_regex.finditer(text)]
        quote_list.sort()

        return quote_list

    @staticmethod
    def append_quotes(element, text, quote_list):
        """Append quotes to an element.

        Arguments:
            text: a string that contains the plain text of the element.
            quote_list: A list of span tuples containing indexes to quotes
            found in text.
        """
        for x in six.moves.range(0, len(quote_list)):
            span = etree.Element('span')
            span.set('type', 'quote')
            span.text = text[quote_list[x][0]:quote_list[x][1]]
            if x + 1 < len(quote_list):
                span.tail = text[quote_list[x][1]:quote_list[x + 1][0]]
            else:
                span.tail = text[quote_list[x][1]:]
            element.append(span)

    def detect_quote(self, element):
        """Insert span elements around quotes.

        Arguments:
            element: an etree element.
        """
        newelement = deepcopy(element)

        element.text = ''
        for child in element:
            child.getparent().remove(child)

        text = newelement.text
        if text:
            quote_list = self.get_quote_list(text)
            if quote_list:
                element.text = text[0:quote_list[0][0]]
                self.append_quotes(element, text, quote_list)
            else:
                element.text = text

        for child in newelement:
            if (child.tag == 'span' and child.get('type') == 'quote'):
                element.append(child)
            else:
                element.append(self.detect_quote(child))

            if child.tail:
                text = child.tail
                quote_list = self.get_quote_list(text)
                if quote_list:
                    child.tail = text[0:quote_list[0][0]]
                    self.append_quotes(element, text, quote_list)

        return element

    def detect_quotes(self):
        """Detect quotes in all paragraphs."""
        for paragraph in self.root.iter('p'):
            paragraph = self.detect_quote(paragraph)

    def calculate_wordcount(self):
        """Count the words in the file."""
        plist = [etree.tostring(paragraph, method='text', encoding='unicode')
                 for paragraph in self.root.iter('p')]

        return six.text_type(len(re.findall(u'\S+', ' '.join(plist))))

    def make_element(self, eName, text, attributes={}):
        """Make an xml element.

        :param eName: the name of the element
        :param text: the content of the element
        :param attributes: the elements attributes

        :returns: lxml.etree.Element
        """
        el = etree.Element(eName)
        for key in attributes:
            el.set(key, attributes[key])

        el.text = text

        return el

    def fix_newstags(self):
        """Convert newstags found in text to xml elements."""
        newstags = re.compile(
            u'(@*logo:|[\s+\']*@*\s*ingres+[\.:]*|.*@*.*bilde\s*\d*:|\W*(@|'
            u'LED|bilde)*tekst:|@*foto:|@fotobyline:|@*bildetitt:|'
            u'<pstyle:bilde>|<pstyle:ingress>|<pstyle:tekst>|'
            u'@*Samleingress:*|tekst/ingress:|billedtekst:|.@tekst:)', re.IGNORECASE)
        titletags = re.compile(
            u'\s*@m.titt[\.:]|\s*@*stikk:|Mellomtittel:|@*(stikk\.*|'
            u'under)titt(el)*:|@ttt:|\s*@*[utm]*[:\.]*tit+:|<pstyle:m.titt>|'
            u'undertittel:', re.IGNORECASE)
        headertitletags = re.compile(
            u'(\s*@*(led)*tittel:|\s*@*titt(\s\d)*:|@LEDtitt:|'
            u'<pstyle:tittel>|@*(hoved|over)titt(el)*:)', re.IGNORECASE)
        bylinetags = re.compile('(<pstyle:|\s*@*)[Bb]yline[:>]*\s*(\S+:)*',
                                re.UNICODE | re.IGNORECASE)
        boldtags = re.compile(u'@bold\s*:')

        header = self.root.find('.//header')
        unknown = self.root.find('.//unknown')

        for em in self.root.iter('em'):
            paragraph = em.getparent()
            if not len(em) and em.text:
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
            if not len(paragraph) and paragraph.text:
                index = paragraph.getparent().index(paragraph)
                lines = []

                for line in paragraph.text.split('\n'):
                    if newstags.match(line):
                        if lines:
                            index += 1
                            paragraph.getparent().insert(
                                index,
                                self.make_element('p',
                                                  ' '.join(lines).strip(),
                                                  attributes=paragraph.attrib))
                        lines = []

                        lines.append(newstags.sub('', line))
                    elif bylinetags.match(line):
                        if lines:
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
                        if lines:
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
                        if lines:
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
                        if lines:
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
                        if title is not None and title.text is None:
                            title.text = line.strip()
                        paragraph.getparent().insert(
                            index,
                            self.make_element('p', line.strip(),
                                              {'type': 'title'}))
                    elif titletags.match(line):
                        if lines:
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
                    elif line == '' and lines:
                        index += 1
                        paragraph.getparent().insert(
                            index,
                            self.make_element('p',
                                              ' '.join(lines).strip(),
                                              attributes=paragraph.attrib))
                        lines = []
                    else:
                        lines.append(line)

                if lines:
                    index += 1
                    paragraph.getparent().insert(
                        index, self.make_element('p',
                                                 ' '.join(lines).strip(),
                                                 attributes=paragraph.attrib))

                paragraph.getparent().remove(paragraph)


class XslMaker(object):
    """Make an xsl file to combine with the intermediate xml file.

    To convert the intermediate xml to a fullfledged  giellatekno document
    a combination of three xsl files + the intermediate xml file is needed.
    """

    def __init__(self, xslfile):
        """Initialise the XslMaker class.

        Arguments:
            xslfile: a string containing the path to the xsl file.
        """
        self.filexsl = xslfile

    @property
    def logfile(self):
        """Return the name of the logfile."""
        return self.filename + '.log'

    @property
    def xsl(self):
        """Return an etree of the xsl file.

        Raises:
            In case of an xml syntax error, raise ConversionException.
        """
        preprocessXsl = etree.parse(
            os.path.join(here, 'xslt/preprocxsl.xsl'))
        preprocessXslTransformer = etree.XSLT(preprocessXsl)

        common_xsl_path = os.path.join(
            here, 'xslt/common.xsl').replace(' ', '%20')

        return preprocessXslTransformer(
            self.filexsl,
            commonxsl=etree.XSLT.strparam('file://{}'.format(common_xsl_path)))

    @property
    def transformer(self):
        """Make an etree.XSLT transformer.

        Raises:
            raise a ConversionException in case of invalid XML in the xsl file.
        Returns:
            an etree.XSLT transformer
        """
        return etree.XSLT(self.xsl)


class LanguageDetector(object):
    """Detect and set the languages of a document."""

    def __init__(self, document, languageGuesser):
        """Initialise the LanguageDetector class.

        Arguments:
            document: an etree element.
            languageGuesser: a text_cat.Classifier.
        """
        self.document = document
        self.languageGuesser = languageGuesser

    @property
    def inlangs(self):
        """Return the predifined possible languages of the document."""
        inlangs = [language.get('{http://www.w3.org/XML/1998/namespace}'
                                'lang')
                   for language in self.document.findall(
            'header/multilingual/language')]
        if inlangs:
            inlangs.append(self.mainlang)

        return inlangs

    @property
    def mainlang(self):
        """Get the mainlang of the file."""
        return self.document.\
            attrib['{http://www.w3.org/XML/1998/namespace}lang']

    def set_paragraph_language(self, paragraph):
        """Set xml:lang of paragraph.

        Extract the text outside the quotes, use this text to set
        language of the paragraph.
        Set the language of the quotes in the paragraph.
        """
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
        """Set xml:lang of span element."""
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
        """Extract all text except the one inside <span type='quote'>."""
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
        """Detect language in all the paragraphs in self.document."""
        if self.document.find('header/multilingual') is not None:
            for paragraph in self.document.iter('p'):
                self.set_paragraph_language(paragraph)


class ConverterManager(object):
    """Manage the conversion of original files to corpus xml."""

    LANGUAGEGUESSER = text_cat.Classifier(None)


    def __init__(self, write_intermediate, goldstandard):
        """Initialise the ConverterManager class.

        Arguments:
            write_intermediate: boolean indicating whether intermediate versions
            of the converted document should be written to disk.
            goldstandard: boolean indicating whether goldstandard documents
            should be converted.
        """
        self.write_intermediate = write_intermediate
        self.goldstandard = goldstandard
        self.FILES = []

    def convert(self, orig_file):
        """Convert file to corpus xml format.

        Arguments:
            orig_file: string containg the path to the original file.
        """
        try:
            conv = self.converter(orig_file)
            conv.write_complete(self.LANGUAGEGUESSER)
        except (ConversionError, ValueError) as error:
            logger.warn('Could not convert {}\n{}'.format(
                orig_file,
                six.text_type(error)))

    def converter(self, orig_file):
        """Return correct converter class based on the orig file name.

        Arguments:
            orig_file: path to the original file.
        Returns:
            A class inherited from the Converter class.
        """
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

        elif '.htm' in orig_file or '.php' in orig_file or '.xhtm' in orig_file:
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

        elif orig_file.endswith('.epub'):
            return EpubConverter(
                orig_file, write_intermediate=self.write_intermediate)

        elif '.rtf' in orig_file:
            return RTFConverter(
                orig_file, write_intermediate=self.write_intermediate)

        elif orig_file.endswith('.bible.xml'):
            return BiblexmlConverter(
                orig_file, write_intermediate=self.write_intermediate)

        else:
            raise ConversionError(
                "Unknown file extension, not able to convert {} "
                "\nHint: you may just have to rename the file".format(
                    orig_file))

    def convert_in_parallel(self):
        """Convert files using the multiprocessing module."""
        logger.info('Starting the conversion of {} files'.format(len(self.FILES)))

        pool_size = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(processes=pool_size,)
        pool.map(unwrap_self_convert,
                 list(six.moves.zip([self] * len(self.FILES), self.FILES)))
        pool.close()
        pool.join()

    def convert_serially(self):
        """Convert the files in one process."""
        logger.info('Starting the conversion of {} files'.format(len(self.FILES)))

        for orig_file in self.FILES:
            logger.debug('converting {}'.format(orig_file))
            self.convert(orig_file)

    def add_file(self, xsl_file):
        """Add file for conversion."""
        if os.path.isfile(xsl_file) and os.path.isfile(xsl_file[:-4]):
            md = xslsetter.MetadataHandler(xsl_file)
            if (
                (md.get_variable('conversion_status') == 'standard' and
                 not self.goldstandard) or (
                     md.get_variable('conversion_status') == 'correct' and
                     self.goldstandard)):
                self.FILES.append(xsl_file[:-4])
        else:
            logger.warn('{} does not exist'.format(xsl_file[:-4]))

    @staticmethod
    def make_xsl_file(source):
        """Write an xsl file if it does not exist."""
        xsl_file = source if source.endswith('.xsl') else source + '.xsl'
        if not os.path.isfile(xsl_file):
            metadata = xslsetter.MetadataHandler(xsl_file, create=True)
            metadata.set_lang_genre_xsl()
            metadata.write_file()

        return xsl_file

    def add_directory(self, directory):
        """Add all files in a directory for conversion."""
        for root, dirs, files in os.walk(directory):
            for f in files:
                if f.endswith('.xsl'):
                    self.add_file(os.path.join(root, f))

    def collect_files(self, sources):
        """Find all convertible files in sources.

        Arguments:
            sources: a list of files or directories where convertable
            files are found.
        """
        logger.info('Collecting files to convert')

        for source in sources:
            if os.path.isfile(source):
                xsl_file = self.make_xsl_file(source)
                self.add_file(xsl_file)
            elif os.path.isdir(source):
                self.add_directory(source)
            else:
                logger.error(
                    'Can not process {}\n'
                    'This is neither a file nor a directory.'.format(source))


def unwrap_self_convert(arg, **kwarg):
    """Unpack self from the arguments and call convert again.

    This is due to how multiprocess works:
    http://www.rueckstiess.net/research/snippets/show/ca1d7d90
    """
    return ConverterManager.convert(*arg, **kwarg)


def parse_options():
    """Parse the commandline options.

    Returns:
        a list of arguments as parsed by argparse.Argumentparser.
    """
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
    parser.add_argument(u'--goldstandard',
                        action=u"store_true",
                        help=u'Convert goldstandard and .correct files')
    parser.add_argument('sources',
                        nargs='+',
                        help="The original file(s) or \
                        directory/ies where the original files exist")

    args = parser.parse_args()

    return args


def sanity_check():
    """Check that needed programs and environment variables are set."""
    util.sanity_check([u'wvHtml', u'pdftotext'])
    if not os.path.isfile(Converter.get_dtd_location()):
        raise util.SetupError(
            "Couldn't find {}\n"
            "Check that GTHOME points at the right directory "
            "(currently: {}).".format(Converter.get_dtd_location(),
                                      os.environ['GTHOME']))


def main():
    """Convert documents to giellatekno xml format."""
    sanity_check()
    args = parse_options()

    cm = ConverterManager(args.write_intermediate, args.goldstandard)
    cm.collect_files(args.sources)

    if args.serial:
        cm.convert_serially()
    else:
        cm.convert_in_parallel()
