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
u"""Test conversion of rtf files."""
import os

from lxml import etree

from corpustools import htmlcontentconverter
from corpustools.test.xmltester import XMLTester

HERE = os.path.dirname(__file__)


class TestRTFConverter(XMLTester):
    """Test the RTFConverter class."""

    def test_convert2intermediate(self):
        """Test rtf conversion to Giella xml."""
        got = htmlcontentconverter.convert2intermediate(
            os.path.join(HERE, 'converter_data/fakecorpus/orig/sme/riddu/'
                         'folkemote.rtf'))
        want = etree.parse(os.path.join(HERE, 'converter_data/folkemote.xml'))

        self.assertXmlEqual(got, want)
