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

u"""Convert html files to the Giella xml format."""

import codecs
import os
import re

from lxml import etree, html

from corpustools.htmlcontentconverter import HTMLContentConverter
from corpustools.basicconverter import BasicConverter

HERE = os.path.dirname(__file__)


class HTMLError(Exception):
    """Raise this error in this module."""

    pass


class HTMLConverter(BasicConverter):
    """Convert html pages to Giella xml documents."""

    @property
    def content(self):
        """Return the content of the html doc as a string.

        Returns:
            a string containing the html document.
        """
        for encoding in ['utf-8', 'windows-1252', 'latin1']:
            try:
                with codecs.open(self.orig, encoding=encoding) as file_:
                    return etree.tostring(
                        html.document_fromstring(
                            self.remove_declared_encoding(file_.read())
                        ),
                        encoding='unicode'
                    )
            except UnicodeDecodeError:
                pass

        raise HTMLError('HTML error {}'.format(self.orig))

    @staticmethod
    def remove_declared_encoding(content):
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
    def replace_bare_text(body):
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
                if (found_element.tail is not None and
                        found_element.tail.strip() != ''):
                    new_p = etree.Element('p')
                    new_p.text = found_element.tail
                    found_element.tail = None
                    found_element.addnext(new_p)

    def convert2intermediate(self):
        """Convert the original document to the Giella xml format.

        The resulting xml is stored in intermediate
        """
        converter_xsl = os.path.join(HERE, 'xslt/xhtml2corpus.xsl')

        html_xslt_root = etree.parse(converter_xsl)
        transform = etree.XSLT(html_xslt_root)

        intermediate = transform(self.convert2xhtml())

        self.replace_bare_text(intermediate.find('.//body'))
        self.add_p_instead_of_tail(intermediate)

        return intermediate.getroot()
