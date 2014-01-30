# -*- coding: utf-8 -*-

#
#   This file contains classes to handle .typos files in $GTFREE
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
#   Copyright 2012-2014 Børre Gaup <borre.gaup@uit.no>
#

import unittest

from corpustools import typosfile


class TestTypoline(unittest.TestCase):
    """Class to test the typos synchroniser
    """
    def setUp(self):
        pass

    def testGetTypo(self):
        tl = typosfile.Typoline('deatalaš\tdeaŧalaš')
        self.assertEqual(tl.getTypo(), 'deatalaš')

        tl = typosfile.Typoline('deatalaš\tdeaŧalaš')
        self.assertEqual(tl.getTypo(), 'deatalaš')

    def testGetCorrection(self):
        tl = typosfile.Typoline('deatalaš\tdeaŧalaš')
        self.assertEqual(tl.getCorrection(), 'deaŧalaš')

        tl = typosfile.Typoline('deatalaš')
        self.assertEqual(tl.getCorrection(), None)

    def testMakeTypoline(self):
        tl = typosfile.Typoline('deatalaš\tdeaŧalaš')
        self.assertEqual(tl.makeTypoline(), 'deatalaš\tdeaŧalaš')

        tl = typosfile.Typoline('deatalaš\tdeatalaš')
        self.assertEqual(tl.makeTypoline(), 'deatalaš')

    def testSetCorrection(self):
        tl = typosfile.Typoline('deatalaš\tdeaŧalaš')
        tl.setCorrection('ditalaš')
        self.assertEqual(tl.getCorrection(), 'ditalaš')
