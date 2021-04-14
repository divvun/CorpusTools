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
#   Copyright © 2012-2021 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Convert pdf files to the Giella xml format."""

import collections
import re
import sys
from copy import deepcopy

import lxml.etree as etree

from corpustools import basicconverter, util, xslsetter

LETTER_AT_START = re.compile(r'[^\W\d_].*', re.UNICODE)
LETTER_HYPHEN_AT_END = re.compile(r'.*[^\W\d_]-$', re.UNICODE)


def styles(page_style):
    """Turn inline css styles into a dict."""
    styles = {}
    for style_pair in page_style.split(';'):
        if style_pair:
            values = style_pair.split(':')
            styles[values[0]] = values[1].replace('px', '')

    return styles


def merge(first, second):
    """Merge two paragraph elements into one."""
    if len(first):
        if second.text:
            if first[-1].tail:
                first[-1].tail = f'{first[-1].tail}{second.text}'
            else:
                first[-1].tail = second.text
    else:
        if second.text:
            if first.text:
                first.text = f'{first.text}{second.text}'
            else:
                first.text = second.text

    for child in second:
        first.append(child)

    return first


def is_probably_hyphenated(previous, current):
    """Find out if previous is part of a hyphenated word.

    Args:
        previous: the previous string in front of a particular br tag
        current:  the current string following a particular br tag

    Returns:
        True if previous is part of a hyphenated word, False otherwise
    """
    previous1 = previous[-2:]
    current1 = current[:2]

    return (LETTER_HYPHEN_AT_END.match(previous1)
            and LETTER_AT_START.match(current1)
            and current[0] == current[0].lower())


def handle_br(previous, current):
    """Handle br tags in p elements.

    Args:
        previous: the previous string in front of a particular br tag
        current:  the current string following a particular br tag

    Returns:
        A possibly modified version of previous
    """
    # Remove hyphen
    if is_probably_hyphenated(previous, current):
        return previous[:-1]

    # Preserve hyphen
    if previous and previous[-1] == '-':
        return previous

    # Turn br tag into space
    return f'{previous} '


PDFFontspec = collections.namedtuple('PDFFontspec',
                                     ['size', 'family', 'color'])


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

        Args:
            xmlfontspec (etree.Element): a PDF2XML fontspec element found in a
                PDF2XML page element.
        """
        this_id = xmlfontspec.get('id')
        this_fontspec = PDFFontspec(size=xmlfontspec.get('size'),
                                    family=xmlfontspec.get('family'),
                                    color=xmlfontspec.get('color'))

        for fontspec in list(self.pdffontspecs.keys()):
            if fontspec == this_fontspec:
                self.duplicates[this_id] = self.pdffontspecs[fontspec]
                break
        else:
            self.pdffontspecs[this_fontspec] = this_id

    def corrected_id(self, font_id):
        """Return a corrected id of a fontspec.

        Some xmlfontspecs have different id's for an identical font.
        This function makes sure identical fonts have identical id's.

        Args:
            font_id: an integer that is the id of the fontspec.

        Returns:
            an integer that is the corrected id of the fontspec.
        """
        if font_id in self.duplicates:
            return self.duplicates[font_id]
        else:
            return font_id


class PDFEmptyPageError(Exception):
    """Raise this exception if a pdf page is empty."""

    pass


class PDFPageMetadata(object):
    """Read pdf metadata from the metadata file into this class.

    Compute metadata needed by the conversion from the data contained in
    this class.
    """
    def __init__(self,
                 page_id,
                 page_style,
                 metadata_margins=None,
                 metadata_inner_margins=None):
        """Initialise the PDFPageMetadata class.

        Args:
            page_number: integer
            page_height: integer
            page_width: integer
            metadata_margins: a dict containing margins read from the metadata
            file.
            metadata_inner_margins: a dict containing inner_margins read from
            the metadata file.
        """
        self.page_number = int(page_id.replace('page', '').replace('-div', ''))
        style = styles(page_style)
        self.page_height = int(style.get('height'))
        self.page_width = int(style.get('width'))
        self.metadata_margins = metadata_margins or {}
        self.metadata_inner_margins = metadata_inner_margins or {}

    def compute_margins(self):
        """Compute the margins of a page in pixels.

        :returns: a dict containing the four margins in pixels
        """
        margins = {
            margin: self.compute_margin(margin)
            for margin in
            ['right_margin', 'left_margin', 'top_margin', 'bottom_margin']
        }

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
            return int(self.page_height -
                       coefficient * self.page_height / 100.0)

    def get_coefficient(self, margin):
        """Get the width of the margin in percent."""
        coefficient = 7
        if margin in list(self.metadata_margins.keys()):
            margin_data = self.metadata_margins[margin]
            if margin_data.get(str(self.page_number)) is not None:
                coefficient = margin_data[str(self.page_number)]
            elif margin_data.get('all') is not None:
                coefficient = margin_data['all']
            elif self.page_number % 2 == 0 and margin_data.get(
                    'even') is not None:
                coefficient = margin_data['even']
            elif self.page_number % 2 == 1 and margin_data.get(
                    'odd') is not None:
                coefficient = margin_data['odd']

        return coefficient

    def compute_inner_margins(self):
        """Compute inner margins of the document.

        Returns:
            A dict where the key is the name of the margin and the value
            is an integer indicating where the margin is on the page.
        """
        margins = {
            margin.replace('inner_', ''): self.compute_inner_margin(margin)
            for margin in [
                'inner_right_margin', 'inner_left_margin', 'inner_top_margin',
                'inner_bottom_margin'
            ]
        }

        if (margins['bottom_margin'] == self.page_height
                and margins['top_margin'] == 0 and margins['left_margin'] == 0
                and margins['right_margin'] == self.page_width):
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
            return int(self.page_height -
                       coefficient * self.page_height / 100.0)

    def get_inner_coefficient(self, margin):
        """Get the width of the margin in percent."""
        coefficient = 0
        if margin in list(self.metadata_inner_margins.keys()):
            margin_data = self.metadata_inner_margins[margin]
            if margin_data.get(str(self.page_number)) is not None:
                coefficient = margin_data[str(self.page_number)]
            elif margin_data.get('all') is not None:
                coefficient = margin_data['all']
            elif self.page_number % 2 == 0 and margin_data.get(
                    'even') is not None:
                coefficient = margin_data['even']
            elif self.page_number % 2 == 1 and margin_data.get(
                    'odd') is not None:
                coefficient = margin_data['odd']

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
    def __init__(self,
                 page_element,
                 metadata_margins=None,
                 metadata_inner_margins=None,
                 linespacing=None):
        """Initialise the PDFPage class.

        Args:
            page_element: an etree element representing a pdf page
            metadata_margins: a dict containing margins read from the metadata
            file.
            metadata_inner_margins: a dict containing inner_margins read from
            the metadata file.
        """
        self.page_element = page_element
        self.pdf_pagemetadata = PDFPageMetadata(
            page_id=page_element.get('id'),
            page_style=page_element.get('style'),
            metadata_margins=metadata_margins,
            metadata_inner_margins=metadata_inner_margins)

    def is_skip_page(self, skip_pages):
        """Found out if this page should be skipped.

        Args:
            skip_pages (list of mixed): list of the pages that should be
                skipped.

        Returns:
            boolean: True if this page should be skipped, otherwise false.
        """
        return (('odd' in skip_pages and
                 (self.pdf_pagemetadata.page_number % 2) == 1)
                or ('even' in skip_pages and
                    (self.pdf_pagemetadata.page_number % 2) == 0)
                or self.pdf_pagemetadata.page_number in skip_pages)

    @property
    def linespacing(self):
        """Return linespacing."""
        if self.linespacing_dict.get('all'):
            return self.linespacing_dict['all']
        elif self.linespacing_dict.get('even') and (
            (self.pdf_pagemetadata.page_number % 2) == 0):
            return self.linespacing_dict['even']
        elif self.linespacing_dict.get('odd') and (
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

        Args:
            pdffontspecs (PDFFontspecs): a PDFFontspecs instance.
        """
        for textelement in self.textelements:
            correct = pdffontspecs.corrected_id(textelement.font)
            textelement.text_elt.set('font', correct)

    def remove_elements_outside_margin(self):
        """Remove PDFTextElements from textelements if needed."""
        margins = self.pdf_pagemetadata.compute_margins()
        inner_margins = self.pdf_pagemetadata.compute_inner_margins()

        self.textelements[:] = [
            t for t in self.textelements if self.is_inside_margins(t, margins)
        ]
        if inner_margins:
            self.textelements[:] = [
                t for t in self.textelements
                if not self.is_inside_inner_margins(t, inner_margins)
            ]

    @staticmethod
    def is_inside_margins(text, margins):
        """Check if t is inside the given margins.

        t is a text element
        """
        if not margins:
            return False

        style = styles(text.get('style'))
        top = int(style.get('top'))
        left = int(style.get('left'))

        return (top > margins['top_margin'] and top < margins['bottom_margin']
                and left > margins['left_margin']
                and left < margins['right_margin'])

    def pick_valid_text_elements(self):
        """Pick the wanted text elements from a page.

        This is the main function of this class
        """
        margins = self.pdf_pagemetadata.compute_margins()
        inner_margins = self.pdf_pagemetadata.compute_inner_margins()
        for paragraph in self.page_element.iter('p'):
            if self.is_inside_margins(paragraph,
                                      margins) and not self.is_inside_margins(
                                          paragraph, inner_margins):
                yield deepcopy(paragraph)


class PDF2XMLConverter(basicconverter.BasicConverter):
    """Class to convert the xml output of pdftohtml to Giella xml.

    Attributes:
        extractor (PDFTextExtractor): class to extract text from the xml that
            pdftohtml produces.
        pdffontspecs (PDFFontspecs): class to store fontspecs found in the xml
            pages.
    """
    def __init__(self, filename):
        """Initialise the PDF2XMLConverte class.

        Args:
            filename (str): the path to the pdf file.
            write_intermediate (boolean): indicate whether intermediate
                versions of the converter document should be written to disk.
        """
        super(PDF2XMLConverter, self).__init__(filename)
        self.pdffontspecs = PDFFontspecs()

    @staticmethod
    def strip_chars(content, extra=''):
        """Strip unwanted chars from the document.

        Args:
            content (str): the xml document that pdftohtml produces
            extra (str): more character that should be removed

        Returns:
            str containing the modified version of the document.
        """
        remove_re = re.compile(
            '[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F{}]'.format(extra))
        content, _ = remove_re.subn('', content)

        # Microsoft Word PDF's have Latin-1 file names in links; we
        # don't actually need any link attributes:
        content = re.sub('<a [^>]+>', '<a>', content)

        return content

    @staticmethod
    def replace_ligatures(content):
        """Replace unwanted strings with correct replacements.

        Args:
            content (str): content of an xml document.

        Returns:
            String containing the new content of the xml document.
        """
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
            "ﬅ": "ft"
        }

        for key, value in replacements.items():
            content = content.replace(key + ' ', value)
            content = content.replace(key, value)

        return content

    def convert2intermediate(self):
        """Convert from pdf to a corpus xml file.

        Returns:
            A corpus xml etree with the content of the pdf file, but without
            most of the metadata.
        """
        command = (
            f'pdftohtml -hidden -enc UTF-8 -stdout -nodrm -i -s {self.orig}')
        pdftohtmloutput = self.extract_text(command.split())
        return self.pdftohtml2intermediate(pdftohtmloutput)

    @staticmethod
    def possibly_add_to_body(body, this_p):
        if this_p.text or len(this_p):
            body.append(this_p)

    def pdftohtml2intermediate(self, pdftohtmloutput):
        """Convert output of pdftohtml to a corpus xml file.

        Returns:
            A corpus xml etree with the content of the pdf file, but without
            most of the metadata.
        """
        pdf_content = self.split_by_br(
            self.replace_ligatures(self.strip_chars(pdftohtmloutput)))

        document = etree.Element('html')
        body = etree.SubElement(document, 'body')

        try:
            parser = etree.HTMLParser()
            root_element = etree.fromstring(pdf_content.encode('utf8'),
                                            parser=parser)
        except etree.XMLSyntaxError as error:
            self.handle_syntaxerror(error, util.lineno(), pdf_content)

        this_p = etree.Element('p')
        for paragraph in self.parse_pages(root_element):
            text = paragraph.xpath('string()').strip()
            if text:
                if text[0] != text[0].lower():
                    self.possibly_add_to_body(body, this_p)
                    this_p = etree.Element('p')
                this_p = merge(this_p, paragraph)

        self.possibly_add_to_body(body, this_p)

        return document

    def pdftohtml2html(self, pdftohtmloutput):
        """Convert output of pdftohtml to html (applying our regular fixes)

        Returns:
            An html file as string with the content of the pdf file, but without
            most of the metadata.
        """
        doc = self.pdftohtml2intermediate(pdftohtmloutput)
        meta = etree.Element('meta')
        meta.attrib['charset'] = "utf-8"
        doc.insert(0, meta)
        list(map(doc.remove, doc.findall('header')))
        doc.tag = 'html'
        lang = self.metadata.get_variable('mainlang')
        if lang is None or lang == "":
            lang = 'se'
        doc.attrib['lang'] = lang
        return etree.tostring(doc,
                              encoding='utf8',
                              method='html',
                              pretty_print=True)

    def parse_page(self, page):
        """Parse the page element.

        Args:
            page: a pdf xml page element.
        """
        try:
            pdfpage = PDFPage(
                page,
                metadata_margins=self.metadata.margins,
                metadata_inner_margins=self.metadata.inner_margins,
                linespacing=self.metadata.linespacing)
            if not pdfpage.is_skip_page(self.metadata.skip_pages):
                #pdfpage.fix_font_id(self.pdffontspecs)
                for paragraph in pdfpage.pick_valid_text_elements():
                    yield paragraph
        except xslsetter.XsltError as error:
            raise util.ConversionError(str(error))

    def parse_pages(self, root_element):
        """Parse the pages of the pdf xml document.

        Args:
            root_element: the root element of the pdf2xml document.
        """
        return (
            paragraph
            for page in root_element.xpath('//div[starts-with(@id, "page")]')
            for paragraph in self.parse_page(page))

    def add_fontspecs(self, page):
        """Extract font specs found in a pdf2xml page element.

        Args:
            page (etree.Element): a pdf page
        """
        for xmlfontspec in page.iter('fontspec'):
            self.pdffontspecs.add_fontspec(xmlfontspec)

    def split_by_br(self, text):
        brs = text.replace('&#160;', ' ').split('<br/>')

        if len(brs) == 1:
            return text

        strings = [
            handle_br(brs[index], current)
            for index, current in enumerate(brs[1:])
        ]
        strings.append(brs[-1])

        return ''.join(strings)

    def extract_text(self, command):
        """Extract the text from a document.

        :command: a list containing the command and the arguments sent to
        ExternalCommandRunner.
        :returns: byte string containing the output of the program
        """
        runner = util.ExternalCommandRunner()
        runner.run(command, cwd='/tmp')

        if runner.returncode != 0:
            with open(self.orig + '.log', 'w') as logfile:
                print('stdout\n{}\n'.format(runner.stdout), file=logfile)
                print('stderr\n{}\n'.format(runner.stderr), file=logfile)
                raise util.ConversionError(
                    '{} failed. More info in the log file: {}'.format(
                        command[0], self.orig + '.log'))

        return runner.stdout.decode('utf8')

    def handle_syntaxerror(self, error, lineno, invalid_input):
        """Handle an xml syntax error.

        Args:
            error: an exception
            lineno: the line number in this module where the error happened.
            invalid_input: a string containing the invalid input.
        """
        with open(self.orig + '.log', 'w') as logfile:
            logfile.write('Error at: {}'.format(lineno))
            for entry in error.error_log:
                logfile.write('\n{}: {} '.format(str(entry.line),
                                                 str(entry.column)))
                try:
                    logfile.write(entry.message)
                except ValueError:
                    logfile.write(entry.message.encode('latin1'))

                logfile.write('\n')

            logfile.write(invalid_input)

        raise util.ConversionError("{}: log is found in {}".format(
            type(self).__name__, self.orig + '.log'))


def to_html_elt(path):
    """Convert a pdf document to the Giella xml format.

    Args:
        filename (str): path to the document

    Returns:
        etree.Element: the root element of the Giella xml document
    """
    converter = PDF2XMLConverter(path)
    return converter.convert2intermediate()
