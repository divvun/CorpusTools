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

u"""Convert pdf files to the Giella xml format."""

from __future__ import absolute_import, print_function

import collections
import re
import sys

import lxml.etree as etree
import six

from corpustools import basicconverter, util, xslsetter

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
        six.unichr(61623),  # U+F0B7: <private use>
        six.unichr(61553),  # U+F071: <private use>
        u'■',  # U+25A0: BLACK SQUARE
        six.unichr(61692),  # U+F0FC: <private use>
    ]
    LIST_RE = re.compile(u'^(\s*[{}])(.+)'.format(u''.join(LIST_CHARS)))

    def __init__(self, linespacing):
        """Initialise the PDFParagraph class."""
        self.textelements = []
        self.boundingboxes = [BoundingBox()]
        self.is_listitem = False
        self.linespacing = linespacing

    def add_space_in_list(self, textelt):
        """Add space after list character.

        Arguments:
            textelement (etree): a pdf text element
        """
        if textelt.text is not None:
            hits2 = self.LIST_RE.search(textelt.text)
            if hits2:
                textelt.text = ' '.join([hits2.group(1), hits2.group(2)])
            else:
                self.add_space_in_list(textelt[0])
        else:
            self.add_space_in_list(textelt[0])

    def append_textelement(self, textelement):
        """Append a PDFTextElement to this paragraph.

        Arguments:
            textelement: a PDFTextElement
        """
        hits = self.LIST_RE.search(textelement.plain_text)
        if hits:
            if re.match(u'^\S', hits.group(2)):
                self.add_space_in_list(textelement.t)
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

        Arguments:
            filename (str): the path to the pdf file.
            write_intermediate (boolean): indicate whether intermediate
                versions of the converter document should be written to disk.
        """
        super(PDF2XMLConverter, self).__init__(filename)
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
                self.orig))
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
            pdfpage = PDFPage(page, metadata_margins=self.metadata.margins,
                            metadata_inner_margins=self.metadata.inner_margins,
                            linespacing=self.metadata.linespacing)
            if not pdfpage.is_skip_page(self.metadata.skip_pages):
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

    def extract_text(self, command):
        """Extract the text from a document.

        :command: a list containing the command and the arguments sent to
        ExternalCommandRunner.
        :returns: byte string containing the output of the program
        """
        runner = util.ExternalCommandRunner()
        runner.run(command, cwd='/tmp')

        if runner.returncode != 0:
            with open(self.names.log, 'w') as logfile:
                print('stdout\n{}\n'.format(runner.stdout), file=logfile)
                print('stderr\n{}\n'.format(runner.stderr), file=logfile)
                raise ConversionError(
                    '{} failed. More info in the log file: {}'.format(
                        command[0], self.names.log))

        return runner.stdout
