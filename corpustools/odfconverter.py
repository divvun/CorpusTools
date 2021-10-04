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
#   Copyright © 2012-2020 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Convert odf files to the Giella xml format."""

from lxml import html
from odf.odf2xhtml import ODF2XHTML

from corpustools import util


def to_html_elt(filename):
    """Convert the content of an odf file to xhtml.

    Returns:
        A string contaning the xhtml version of the odf file.
    """
    generatecss = False
    embedable = True
    odhandler = ODF2XHTML(generatecss, embedable)
    try:
        return html.document_fromstring(odhandler.odf2xhtml(filename))
    except TypeError as error:
        raise util.ConversionError(f"Error: {error}")
