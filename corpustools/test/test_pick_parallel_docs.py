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
#   Copyright © 2012-2015 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

from __future__ import print_function

import os
import unittest

from corpustools import parallelize
from corpustools import pick_parallel_docs


here = os.path.dirname(__file__)


class TestParallelPicker(unittest.TestCase):
    def setUp(self):
        self.language1_converted_dir = os.path.join(os.environ['GTHOME'], 'gt/script/langTools/fakecorpus/converted/sme')

        self.pp = pick_parallel_docs.ParallelPicker(self.language1_converted_dir, 'nob', '73', '110')

    def test_calculate_language1(self):
        self.pp.calculate_language1(self.language1_converted_dir)
        self.assertEqual(self.pp.get_language1(), 'sme')

    def test_get_parallel_language(self):
        self.assertEqual(self.pp.get_parallel_language(), 'nob')

    def test_has_orig(self):
        file_with_orig1 = parallelize.CorpusXMLFile(os.path.join(self.language1_converted_dir, 'samediggi-article-47.html.xml'))
        self.assertEqual(self.pp.has_orig(file_with_orig1), True)

        language1_prestable_converted_dir = os.path.join(os.environ['GTHOME'], 'gt/script/langTools/fakecorpus/prestable/converted/sme')
        file_with_orig2 = parallelize.CorpusXMLFile(os.path.join(language1_prestable_converted_dir, 'samediggi-article-47.html.xml'))
        self.assertEqual(self.pp.has_orig(file_with_orig2), True)

        file_without_orig1 = parallelize.CorpusXMLFile(os.path.join(self.language1_converted_dir, 'samediggi-article-1.html.xml'))
        self.assertEqual(self.pp.has_orig(file_without_orig1), False)

        file_without_orig2 = parallelize.CorpusXMLFile(os.path.join(language1_prestable_converted_dir, 'samediggi-article-1.html.xml'))
        self.assertEqual(self.pp.has_orig(file_without_orig2), False)

    def test_has_parallel(self):
        file_with_parallel1 = parallelize.CorpusXMLFile(os.path.join(self.language1_converted_dir, 'samediggi-article-47.html.xml'))
        self.assertEqual(self.pp.has_parallel(file_with_parallel1), True)

        language1_prestable_converted_dir = os.path.join(os.environ['GTHOME'], 'gt/script/langTools/fakecorpus/prestable/converted/sme')
        file_with_parallel2 = parallelize.CorpusXMLFile(os.path.join(language1_prestable_converted_dir, 'samediggi-article-47.html.xml'))
        self.assertEqual(self.pp.has_parallel(file_with_parallel2), True)

        file_without_parallel1 = parallelize.CorpusXMLFile(os.path.join(self.language1_converted_dir, 'samediggi-article-53.html.xml'))
        self.assertEqual(self.pp.has_parallel(file_without_parallel1), False)

        file_without_parallel2 = parallelize.CorpusXMLFile(os.path.join(language1_prestable_converted_dir, 'samediggi-article-53.html.xml'))
        self.assertEqual(self.pp.has_parallel(file_without_parallel2), False)
