# -*- coding: utf-8 -*-

#
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
#   Copyright © 2014-2017 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Test conversion of doc files."""

import os

from lxml import etree

from corpustools import htmlcontentconverter
from corpustools.test.xmltester import XMLTester

HERE = os.path.dirname(__file__)


class TestDocConverter(XMLTester):
    """Test docx conversion."""

    def test_convert2intermediate(self):
        """Test conversion of a doc file."""
        got = htmlcontentconverter.convert2intermediate(
            os.path.join(
                HERE, 'converter_data/fakecorpus/orig/sme/riddu/doc-test.doc'))
        want = etree.parse(os.path.join(HERE, 'converter_data/doc-test.xml'))

        self.assertXmlEqual(got, want)
