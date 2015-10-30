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
#   Copyright © 2013-2015 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

import unittest

from corpustools import util


class TestSplitPath(unittest.TestCase):

    def test_split_converted(self):
        self.assertEqual(
            util.split_path("/home/me/src/freecorpus-git/converted/sma/admin/"
                            "depts/other_files/tips.html.xml"),
            ('/home/me/src/freecorpus-git',
             'converted',
             'sma',
             'admin',
             'depts/other_files',
             'tips.html.xml'))

    def test_split_orig(self):
        self.assertEqual(
            util.split_path(
                "/home/me/freecorpus/orig/nob/bible/osko/omoss.html"),
            ('/home/me/freecorpus',
             'orig',
             'nob',
             'bible',
             'osko',
             'omoss.html'))
