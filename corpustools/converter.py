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

import codecs
import distutils.dep_util
import distutils.spawn
import logging
import os
import re
from copy import deepcopy

from lxml import etree
import six

from corpustools import (avvirconverter, biblexmlconverter,
                         ccat, corpuspath, decode, docconverter, docxconverter,
                         epubconverter, errormarkup, htmlconverter,
                         odfconverter, pdfconverter, plaintextconverter,
                         rtfconverter, svgconverter, util, xslsetter)

HERE = os.path.dirname(__file__)


logging.basicConfig(level=logging.WARNING)
LOGGER = logging.getLogger(__name__)


class ConversionError(Exception):
    """Raise this exception when an error occurs in the converter module."""

    pass


def to_giella(path):
    """Convert a document to the giella xml format.

    Arguments:
        path (str): path to the document

    Returns:
        etree.Element: root of the resulting xml document
    """
    chooser = {
        '.doc': docconverter.convert2intermediate,
        '.docx': docxconverter.convert2intermediate,
        '.epub': epubconverter.convert2intermediate,
        '.html': htmlconverter.convert2intermediate,
        '.odf': odfconverter.convert2intermediate,
        '.pdf': pdfconverter.convert2intermediate,
        '.rtf': rtfconverter.convert2intermediate,
        '.svg': svgconverter.convert2intermediate,
        '.txt': plaintextconverter.convert2intermediate,
    }

    if 'avvir_xml' in path:
        return avvirconverter.convert2intermediate(path)
    elif path.endswith('bible.xml'):
        return biblexmlconverter.convert2intermediate(path)
    else:
        return chooser[os.path.splitext(path)[1]](path)


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
            self.metadata = xslsetter.MetadataHandler(
                self.names.xsl, create=True)
        except xslsetter.XsltError as error:
            raise ConversionError(error)

        self.metadata.set_lang_genre_xsl()
        with util.ignored(OSError):
            os.makedirs(self.tmpdir)

    @property
    def dependencies(self):
        """Return files that converted files depend on."""
        return [self.names.orig, self.names.xsl]

    @property
    def standard(self):
        """Return a boolean indicating if the file is convertable."""
        return self.metadata.get_variable('conversion_status') == 'standard'

    @property
    def goldstandard(self):
        """Return a boolean indicating if the file is a gold standard doc."""
        return self.metadata.get_variable('conversion_status') == 'correct'

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
        intermediate = to_giella(self.names.orig)
        self.fix_document(intermediate)
        self.maybe_write_intermediate(intermediate)
        try:
            xsl_maker = XslMaker(self.metadata.tree)
            complete = xsl_maker.transformer(intermediate)

            return complete.getroot()
        except etree.XSLTApplyError as error:
            with open(self.names.log, 'w') as logfile:
                logfile.write('Error at: {}'.format(
                    six.text_type(util.lineno())))
                for entry in complete.error_log:
                    logfile.write(six.text_type(entry))
                    logfile.write('\n')

            raise ConversionError("Check the syntax in: {}".format(
                self.names.xsl))
        except etree.XSLTParseError as error:
            with open(self.names.log, 'w') as logfile:
                logfile.write('Error at: {}'.format(
                    six.text_type(util.lineno())))
                for entry in complete.error_log:
                    logfile.write(six.text_type(entry))
                    logfile.write('\n')

            raise ConversionError("XSLTParseError in: {}\nError {}".format(
                self.names.xsl, str(error)))

    def convert_errormarkup(self, complete):
        """Convert error markup to xml."""
        if self.goldstandard:
            try:
                error_markup = errormarkup.ErrorMarkup(self.names.orig)

                for element in complete.find('body'):
                    error_markup.add_error_markup(element)
            except IndexError as error:
                with open(self.names.log, 'w') as logfile:
                    logfile.write('Error at: {}'.format(
                        six.text_type(util.lineno())))
                    logfile.write("There is a markup error\n")
                    logfile.write("The error message: ")
                    logfile.write(six.text_type(error))
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
        self.metadata.set_variable('wordcount', fixer.calculate_wordcount())

        if not self.goldstandard:
            fixer.detect_quotes()

        # The above line adds text to hyph, fix that
        for hyph in complete.iter('hyph'):
            hyph.text = None

        if (self.metadata.get_variable('mainlang') in
                ['sma', 'sme', 'smj', 'smn', 'sms', 'nob', 'fin', 'swe',
                 'nno', 'dan', 'fkv', 'sju', 'sje', 'mhr']):
            try:
                fixer.fix_body_encoding(self.metadata.get_variable('mainlang'))
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
            LOGGER.warn("Skipped bad byte \\x%s, seen in %s",
                        badhex, self.names.orig)
        return repl, (decode_error.start + len(repl))

    def make_complete(self, language_guesser):
        """Make a complete Giella xml file.

        Combine the intermediate Giella xml file and the metadata into
        a complete Giella xml file.
        Fix the character encoding
        Detect the languages in the xml file
        """
        complete = self.transform_to_complete()
        self.validate_complete(complete)
        self.convert_errormarkup(complete)
        lang_detector = LanguageDetector(complete, language_guesser)
        lang_detector.detect_language()

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
                    LOGGER.error("%s has no text", self.names.orig)

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

    def handle_syntaxerror(self, error, lineno, invalid_input):
        """Handle an xml syntax error.

        Arguments:
            e: an exception
            lineno: the line number in this module where the error happened.
            invalid_input: a string containing the invalid input.
        """
        with open(self.names.log, 'w') as logfile:
            logfile.write('Error at: {}'.format(lineno))
            for entry in error.error_log:
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


class DocumentFixer(object):
    """Fix the content of a Giella xml document.

    Receive a stringified etree from one of the raw converters,
    replace ligatures, fix the encoding and return an etree with correct
    characters
    """
    newstags = re.compile(
        r'(@*logo:|[\s+\']*@*\s*ingres+[\.:]*|.*@*.*bilde\s*\d*:|\W*(@|'
        r'LED|bilde)*tekst:|@*foto:|@fotobyline:|@*bildetitt:|'
        r'<pstyle:bilde>|<pstyle:ingress>|<pstyle:tekst>|'
        r'@*Samleingress:*|tekst/ingress:|billedtekst:|.@tekst:)',
        re.IGNORECASE)
    titletags = re.compile(
        r'\s*@m.titt[\.:]|\s*@*stikk:|Mellomtittel:|@*(stikk\.*|'
        r'under)titt(el)*:|@ttt:|\s*@*[utm]*[:\.]*tit+:|<pstyle:m.titt>|'
        r'undertittel:', re.IGNORECASE)
    headertitletags = re.compile(
        r'(\s*@*(led)*tittel:|\s*@*titt(\s\d)*:|@LEDtitt:|'
        r'<pstyle:tittel>|@*(hoved|over)titt(el)*:)', re.IGNORECASE)
    bylinetags = re.compile(r'(<pstyle:|\s*@*)[Bb]yline[:>]*\s*(\S+:)*',
                            re.UNICODE | re.IGNORECASE)
    boldtags = re.compile(r'@bold\s*:')

    def __init__(self, document):
        """Initialise the DocumentFixer class."""
        self.root = document

    def get_etree(self):
        """Get the root of the xml document."""
        return self.root

    def compact_ems(self):
        """Compact consecutive em elements into a single em if possible."""
        word = re.compile(r'\w+', re.UNICODE)
        for element in self.root.iter('p'):
            if len(element.xpath('.//em')) > 1:
                lines = []
                for emphasis in element.iter('em'):
                    next_elt = emphasis.getnext()
                    if (next_elt is not None and next_elt.tag == 'em' and
                            (emphasis.tail is None or not word.search(emphasis.tail))):
                        if emphasis.text is not None:
                            lines.append(emphasis.text.strip())
                        emphasis.getparent().remove(emphasis)
                    else:
                        if emphasis.text is not None:
                            lines.append(emphasis.text.strip())
                        emphasis.text = ' '.join(lines)
                        if emphasis.tail is not None:
                            emphasis.tail = ' {}'.format(emphasis.tail)
                        del lines[:]

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
                for index, part in enumerate(parts[1:]):
                    hyph = etree.Element('hyph')
                    hyph.tail = part
                    element.insert(index, hyph)

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
        body_string = etree.tostring(body, encoding='unicode')
        body.getparent().remove(body)

        guesser = decode.EncodingGuesser()
        encoding = guesser.guess_body_encoding(body_string)

        try:
            body = etree.fromstring(guesser.decode_para(encoding, body_string))
        except UnicodeEncodeError as error:
            raise UserWarning(str(error))
        self.root.append(body)

        if mainlang == 'sms':
            self.fix_sms(self.root.find('body'))

    def fix_title_person(self, encoding):
        """Fix encoding problems."""
        guesser = decode.EncodingGuesser()

        title = self.root.find('.//title')
        if title is not None and title.text is not None:
            text = title.text

            text = text
            util.print_frame(encoding)
            title.text = guesser.decode_para(encoding, text)

        persons = self.root.findall('.//person')
        for person in persons:
            if person is not None:
                lastname = person.get('lastname')

                if encoding == 'mac-sami_to_latin1':
                    lastname = lastname.replace(u'‡', u'á')
                    lastname = lastname.replace(u'Œ', u'å')

                person.set(
                    'lastname',
                    guesser.decode_para(
                        encoding,
                        lastname))

                firstname = person.get('firstname')

                if encoding == 'mac-sami_to_latin1':
                    firstname = firstname.replace(u'‡', u'á')
                    firstname = firstname.replace(u'Œ', u'å')

                person.set(
                    'firstname',
                    guesser.decode_para(
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
        unwanted = r'[^:,!?.\s]'
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
        for index in six.moves.range(0, len(quote_list)):
            span = etree.Element('span')
            span.set('type', 'quote')
            span.text = text[quote_list[index][0]:quote_list[index][1]]
            if index + 1 < len(quote_list):
                span.tail = text[quote_list[index][1]:quote_list[index + 1][0]]
            else:
                span.tail = text[quote_list[index][1]:]
            element.append(span)

    def _detect_quote(self, element):
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
            if child.tag == 'span' and child.get('type') == 'quote':
                element.append(child)
            else:
                element.append(self._detect_quote(child))

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
            paragraph = self._detect_quote(paragraph)

    def calculate_wordcount(self):
        """Count the words in the file."""
        plist = [etree.tostring(paragraph, method='text', encoding='unicode')
                 for paragraph in self.root.iter('p')]

        return six.text_type(len(re.findall(r'\S+', ' '.join(plist))))

    @staticmethod
    def _make_element(name, text, attributes=None):
        """Make an xml element.

        :param name: the name of the element
        :param text: the content of the element
        :param attributes: the elements attributes

        :returns: lxml.etree.Element
        """
        attributes = attributes or {}
        element = etree.Element(name)
        for key in attributes:
            element.set(key, attributes[key])

        element.text = text

        return element

    def _fix_emphasises(self):
        for emphasis in self.root.iter('em'):
            paragraph = emphasis.getparent()
            if not len(emphasis) and emphasis.text:
                if self.bylinetags.match(emphasis.text):
                    line = self.bylinetags.sub('', emphasis.text).strip()
                    unknown = self.root.find('.//unknown')
                    if unknown is not None:
                        person = etree.Element('person')
                        person.set('lastname', line)
                        person.set('firstname', '')
                        unknown.getparent().replace(unknown, person)
                        paragraph.getparent().remove(paragraph)
                elif self.titletags.match(emphasis.text):
                    emphasis.text = self.titletags.sub(
                        '', emphasis.text).strip()
                    paragraph.set('type', 'title')
                elif self.newstags.match(emphasis.text):
                    emphasis.text = self.newstags.sub(
                        '', emphasis.text).strip()

    def _add_paragraph(self, line, index, paragraph, attributes):
        if line:
            index += 1
            paragraph.getparent().insert(
                index,
                self._make_element('p',
                                   line,
                                   attributes=attributes))

        return index

    def _add_emphasis(self, index, line, attributes, paragraph):
        index += 1
        element = etree.Element('p')
        element.append(self._make_element('em', line, attributes))

        paragraph.getparent().insert(index, element)

        return index

    def _handle_line(self, line, index, lines, paragraph):
        if self.newstags.match(line):
            index = self._add_paragraph(' '.join(lines).strip(), index,
                                        paragraph, paragraph.attrib)
            del lines[:]

            lines.append(self.newstags.sub('', line))

        elif self.bylinetags.match(line):
            index = self._add_paragraph(' '.join(lines).strip(), index,
                                        paragraph, paragraph.attrib)
            del lines[:]

            unknown = self.root.find('.//unknown')
            if unknown is not None:
                person = etree.Element('person')
                person.set('lastname',
                           self.bylinetags.sub('', line).strip())
                person.set('firstname', '')

                unknown.getparent().replace(unknown, person)

        elif self.boldtags.match(line):
            index = self._add_paragraph(' '.join(lines).strip(), index,
                                        paragraph, paragraph.attrib)
            index = self._add_emphasis(index,
                                       self.boldtags.sub('', line).strip(),
                                       {'type': 'bold'}, paragraph)
            del lines[:]

        elif line.startswith('@kursiv:'):
            index = self._add_paragraph(
                ' '.join(lines).strip(), index, paragraph, paragraph.attrib)
            index = self._add_emphasis(index,
                                       line.replace('@kursiv:', '').strip(),
                                       {'type': 'italic'}, paragraph)
            del lines[:]

        elif self.headertitletags.match(line):
            index = self._add_paragraph(
                ' '.join(lines).strip(), index, paragraph, paragraph.attrib)
            del lines[:]

            header = self.root.find('.//header')
            title = header.find('./title')
            if title is not None and title.text is None:
                title.text = self.headertitletags.sub('', line).strip()

            index = self._add_paragraph(self.headertitletags.sub(
                '', line).strip(), index, paragraph, {'type': 'title'})
        elif self.titletags.match(line):
            index = self._add_paragraph(' '.join(lines).strip(), index,
                                        paragraph, paragraph.attrib)
            del lines[:]

            index += 1
            paragraph.getparent().insert(
                index,
                self._make_element(
                    'p', self.titletags.sub('', line).strip(), {'type': 'title'}))
        elif line == '' and lines:
            index = self._add_paragraph(
                ' '.join(lines).strip(), index, paragraph, paragraph.attrib)
            del lines[:]

        else:
            lines.append(line)

        return index

    def _fix_paragraphs(self):
        for paragraph in self.root.iter('p'):
            if not len(paragraph) and paragraph.text:
                index = paragraph.getparent().index(paragraph)
                lines = []

                for line in paragraph.text.split('\n'):
                    index = self._handle_line(line, index, lines, paragraph)

                index = self._add_paragraph(' '.join(lines).strip(), index,
                                            paragraph, paragraph.attrib)

                paragraph.getparent().remove(paragraph)

    def fix_newstags(self):
        """Convert newstags found in text to xml elements."""
        self._fix_emphasises()
        self._fix_paragraphs()


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
        self.filename = xslfile

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
        xsl = etree.parse(
            os.path.join(HERE, 'xslt/preprocxsl.xsl'))
        transformer = etree.XSLT(xsl)

        common_xsl_path = os.path.join(
            HERE, 'xslt/common.xsl').replace(' ', '%20')

        return transformer(
            self.filename,
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

    def __init__(self, document, language_guesser):
        """Initialise the LanguageDetector class.

        Arguments:
            document: an etree element.
            languageGuesser: a text_cat.Classifier.
        """
        self.document = document
        self.language_guesser = language_guesser

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
            if self.language_guesser is not None:
                lang = self.language_guesser.classify(paragraph_text,
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
                    lang = self.language_guesser.classify(element.text,
                                                          langs=self.inlangs)
                    if lang != self.mainlang:
                        element.set(
                            '{http://www.w3.org/XML/1998/namespace}lang',
                            lang)

    @staticmethod
    def remove_quote(paragraph):
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
