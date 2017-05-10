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
#   Copyright © 2012-2017 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

"""This file contains classes to convert files to the Giella xml format."""


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
from corpustools import (argparse_version, ccat, corpuspath, decode,
                         errormarkup, text_cat, util, xslsetter)

HERE = os.path.dirname(__file__)


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
        return os.path.join(HERE, 'dtd/corpus.dtd')

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
        """Make a complete Giella xml file.

        Combine the intermediate Giella xml file and the metadata into
        a complete Giella xml file.
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


class OdfConverter(HTMLConverter):
    """Convert odf documents to the Giella xml format."""

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
    """Convert docx documents to the Giella xml format."""

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
    """Convert epub documents to the Giella xml format.

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
    """Convert Microsoft Word documents to the Giella xml format."""

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
    """Fix the content of a Giella xml document.

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
            (u'\u0301', u'\u02B9'),
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
            os.path.join(HERE, 'xslt/preprocxsl.xsl'))
        preprocessXslTransformer = etree.XSLT(preprocessXsl)

        common_xsl_path = os.path.join(
            HERE, 'xslt/common.xsl').replace(' ', '%20')

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
