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
import io
import os
import re

from lxml import etree, html

from corpustools.htmlcontentconverter import HTMLContentConverter

HERE = os.path.dirname(__file__)


class HTMLError(Exception):
    """Raise this error in this module."""

    pass


def remove_declared_encoding(content):
    """Remove declared decoding.

    lxml explodes if we send a decoded Unicode string with an
    xml-declared encoding
    http://lxml.de/parsing.html#python-unicode-strings

    Arguments:
        content (str): the contents of a html document

    Returns:
        str: content sans the declared decoding
    """
    xml_encoding_declaration_re = re.compile(
        r"^<\?xml [^>]*encoding=[\"']([^\"']+)[^>]*\?>[ \r\n]*", re.IGNORECASE)

    return re.sub(xml_encoding_declaration_re, "", content)


def webpage_to_unicodehtml(filename):
    """Return the content of the html doc as a string.

    Arguments:
        filename (str): path to the webpage

    Returns:
        etree.Element: the content of the webpage sent through the
            lxml.html5parser.
    """
    for encoding in ['utf-8', 'windows-1252', 'latin1']:
        try:
            with codecs.open(filename, encoding=encoding) as file_:
                return html.document_fromstring(
                    remove_declared_encoding(file_.read()))
        except UnicodeDecodeError:
            pass

    raise HTMLError('{}: encoding trouble'.format(filename))


def convert2xhtml(content_xml):
    """Convert html document to a cleaned up xhtml document.

    Arguments:
        content (etree.Element): html document

    Returns:
        a cleaned up xhtml document as an etree element
    """
    for elt in content_xml.iter('script'):
        elt.getparent().remove(elt)

    converter = HTMLContentConverter()
    return converter.convert2xhtml(
        etree.tostring(content_xml, encoding='unicode'))


def replace_bare_text(body):
    """Replace bare text in body with a p element.

    Arguments:
        body (etree.Element): the body element of the html document
    """
    if body.text is not None and body.text.strip() != '':
        new_p = etree.Element('p')
        new_p.text = body.text
        body.text = None
        body.insert(0, new_p)


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


def xhtml2intermediate(xhtml):
    """Convert xhtml to Giella xml.

    Arguments:
        xhtml (etree.Element): the result of convert2xhtml

    Returns:
        etree.Element: the root element of the Giella xml document
    """
    converter_xsl = os.path.join(HERE, 'xslt/xhtml2corpus.xsl')

    html_xslt_root = etree.parse(converter_xsl)
    transform = etree.XSLT(html_xslt_root)

    intermediate = transform(xhtml)

    replace_bare_text(intermediate.find('.//body'))
    add_p_instead_of_tail(intermediate)

    return intermediate.getroot()


def convert2intermediate(filename):
    """Convert a webpage to Giella xml.

    Arguments:
        filename (str): name of the file

    Returns:
        etree.Element: the root element of the Giella xml document
    """
    return xhtml2intermediate(convert2xhtml(webpage_to_unicodehtml(filename)))
