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

"""Convert docx files to the Giella xml format."""

from pydocx.export import PyDocXHTMLExporter

from corpustools.htmlconverter import xhtml2intermediate, convert2xhtml


def convert2intermediate(filename):
    """Convert a Microsoft Word document to the Giella xml format.

    Arguments:
        filename (str): path to the document

    Returns:
        etree.Element: the root element of the Giella xml document
    """
    return xhtml2intermediate(
        convert2xhtml(PyDocXHTMLExporter(filename).export()))
