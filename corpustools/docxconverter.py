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

from corpustools.htmlconverter import HTMLConverter


class DocxConverter(HTMLConverter):
    """Convert docx documents to the Giella xml format."""

    @property
    def content(self):
        """Convert the content of a docx file to xhtml.

        Returns:
            A string contaning the xhtml version of the docx file.
        """
        return PyDocXHTMLExporter(self.orig).export()
