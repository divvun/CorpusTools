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
#   Copyright 2011-2015 Børre Gaup <borre.gaup@uit.no>
#   Copyright 2014-2015 Kevin Brubeck Unhammer <unhammer@fsfe.org>
#

import lxml.etree as etree
import os
import unittest

from corpustools import compare_tmx_goldstandard
from corpustools import parallelize


here = os.path.dirname(__file__)


class TestTmxComparator(unittest.TestCase):

    """A test class for the TmxComparator class"""

    def test_equal_tmxes(self):
        comp = compare_tmx_goldstandard.TmxComparator(
            parallelize.Tmx(etree.parse(
                os.path.join(
                    here,
                    'parallelize_data/aarseth2-n.htm.toktmx'))),
            parallelize.Tmx(etree.parse(
                os.path.join(
                    here,
                    'parallelize_data/aarseth2-n.htm.toktmx'))))

        self.assertEqual(comp.get_number_of_differing_lines(), -1)
        self.assertEqual(comp.get_lines_in_wantedfile(), 274)
        self.assertEqual(len(comp.get_diff_as_text()), 0)
