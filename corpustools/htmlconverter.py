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
#   Copyright © 2012-2018 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
u"""Convert html files to the Giella xml format."""

import codecs
import re

from lxml import html


class HTMLError(Exception):
    """Raise this error in this module."""

    pass


def remove_declared_encoding(content):
    """Remove declared decoding.

    lxml explodes if we send a decoded Unicode string with an
    xml-declared encoding
    http://lxml.de/parsing.html#python-unicode-strings

    Args:
        content (str): the contents of a html document

    Returns:
        str: content sans the declared decoding
    """
    xml_encoding_declaration_re = re.compile(
        r"^<\?xml [^>]*encoding=[\"']([^\"']+)[^>]*\?>[ \r\n]*", re.IGNORECASE)

    return re.sub(xml_encoding_declaration_re, "", content)


def to_html_elt(filename):
    """Return the content of the html doc as a string.

    Args:
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
