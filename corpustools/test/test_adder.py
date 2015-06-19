# -*- coding: utf-8 -*-

#
#   This file contains routines to add files to a corpus directory
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
#   Copyright 2015 Børre Gaup <borre.gaup@uit.no>
#

import os
import unittest

from corpustools import adder


here = os.path.dirname(__file__)


class TestAddToCorpus(unittest.TestCase):
    def test_init_with_valid_corpusdir(self):
        lang = 'sme'
        path = 'a/b/c'
        atc = adder.AddToCorpus(here, lang, path)

        self.assertEqual((atc.corpusdir, atc.mainlang, atc.goaldir),
                         (here, lang, '/'.join([here, 'orig', lang, path])))

    def test_init_with_invalid_corpusdir(self):
        lang = 'sme'
        path = 'a/b/c'

        self.assertRaises(adder.AdderException, adder.AddToCorpus, 'there', lang, path)
