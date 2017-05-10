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

"""Test conversion of svg files."""

import os

import lxml.etree as etree

from corpustools import svgconverter
from corpustools.test import xmltester

HERE = os.path.dirname(__file__)


class TestSVGConverter(xmltester.XMLTester):
    """Test conversion of svg files."""

    def test_convert2intermediate(self):
        """Test conversion of svg files."""
        svg_file = os.path.join(HERE,
                                'converter_data/fakecorpus/orig/sme/riddu/'
                                'Riddu_Riddu_avis_TXT.200923.svg')

        got = svgconverter.convert2intermediate(svg_file)
        want = etree.parse(
            os.path.join(HERE,
                         'converter_data/Riddu_Riddu_avis_TXT.200923.svg.xml'))

        self.assertXmlEqual(got, want)
