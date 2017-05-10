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

u"""Convert rtf files to the Giella xml format."""


import io

import six
from pyth.plugins.rtf15.reader import Rtf15Reader
from pyth.plugins.xhtml.writer import XHTMLWriter

from corpustools.htmlconverter import HTMLConverter


class RTFError(Exception):
    """Use this when errors occur in this module."""

    pass


class RTFConverter(HTMLConverter):
    """Convert rtf documents to the Giella xml format."""

    @property
    def content(self):
        """Convert the content of an rtf file to xhtml.

        Returns:
            A string containing the xhtml version of the rtf file.
        """
        with open(self.orig, "rb") as rtf_document:
            content = rtf_document.read()
            try:
                pyth_doc = Rtf15Reader.read(
                    io.BytesIO(content.replace(b'fcharset256',
                                               b'fcharset255')))
                return six.text_type(XHTMLWriter.write(
                    pyth_doc, pretty=True).read(), encoding='utf8')
            except UnicodeDecodeError:
                raise RTFError('Unicode problems in {}'.format(
                    self.orig))
