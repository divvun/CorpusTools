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
from __future__ import unicode_literals

import doctest
from lxml import doctestcompare
from lxml import etree
import os
import tempfile
import unittest

from corpustools import generate_anchor_list
from corpustools import parallelize
from corpustools import text_cat


here = os.path.dirname(__file__)


def PrintFrame(input = "empty"):
    """
    Print debug output
    """
    callerframerecord = inspect.stack()[1]    # 0 represents this line
                                                # 1 represents line at caller
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)

    print(info.lineno, info.function, input)

class TestParallelPicker(unittest.TestCase):
    def setUp(self):
        self.language1ConvertedDir = os.path.join(os.environ['GTHOME'], 'gt/script/langTools/fakecorpus/converted/sme')

        self.pp = ParallelPicker(self.language1ConvertedDir, 'nob', '73', '110')

    def testCalculateLanguage1(self):
        self.pp.calculateLanguage1(self.language1ConvertedDir)
        self.assertEqual(self.pp.getLanguage1(), 'sme')

    def testGetParallelLanguage(self):
        self.assertEqual(self.pp.getParallelLanguage(), 'nob')

    def testHasOrig(self):
        fileWithOrig1 = parallelize.CorpusXMLFile(os.path.join(self.language1ConvertedDir, 'samediggi-article-47.html.xml'), self.pp.getParallelLanguage())
        self.assertEqual(self.pp.hasOrig(fileWithOrig1), True)

        language1PrestableConvertedDir = os.path.join(os.environ['GTHOME'], 'gt/script/langTools/fakecorpus/prestable/converted/sme')
        fileWithOrig2 = parallelize.CorpusXMLFile(os.path.join(language1PrestableConvertedDir, 'samediggi-article-47.html.xml'), self.pp.getParallelLanguage())
        self.assertEqual(self.pp.hasOrig(fileWithOrig2), True)

        fileWithoutOrig1 = parallelize.CorpusXMLFile(os.path.join(self.language1ConvertedDir, 'samediggi-article-1.html.xml'), self.pp.getParallelLanguage())
        self.assertEqual(self.pp.hasOrig(fileWithoutOrig1), False)

        fileWithoutOrig2 = parallelize.CorpusXMLFile(os.path.join(language1PrestableConvertedDir, 'samediggi-article-1.html.xml'), self.pp.getParallelLanguage())
        self.assertEqual(self.pp.hasOrig(fileWithoutOrig2), False)

    def testHasParallel(self):
        fileWithParallel1 = parallelize.CorpusXMLFile(os.path.join(self.language1ConvertedDir, 'samediggi-article-47.html.xml'), self.pp.getParallelLanguage())
        self.assertEqual(self.pp.hasParallel(fileWithParallel1), True)

        language1PrestableConvertedDir = os.path.join(os.environ['GTHOME'], 'gt/script/langTools/fakecorpus/prestable/converted/sme')
        fileWithParallel2 = parallelize.CorpusXMLFile(os.path.join(language1PrestableConvertedDir, 'samediggi-article-47.html.xml'), self.pp.getParallelLanguage())
        self.assertEqual(self.pp.hasParallel(fileWithParallel2), True)

        fileWithoutParallel1 = parallelize.CorpusXMLFile(os.path.join(self.language1ConvertedDir, 'samediggi-article-53.html.xml'), self.pp.getParallelLanguage())
        self.assertEqual(self.pp.hasParallel(fileWithoutParallel1), False)

        fileWithoutParallel2 = parallelize.CorpusXMLFile(os.path.join(language1PrestableConvertedDir, 'samediggi-article-53.html.xml'), self.pp.getParallelLanguage())
        self.assertEqual(self.pp.hasParallel(fileWithoutParallel2), False)
