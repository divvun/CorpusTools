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
#   Copyright © 2012-2016 The University of Tromsø &
#                        the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

"""Test the ParallelPicker class."""

from __future__ import absolute_import, print_function

import os
import unittest

import git
import testfixtures

from corpustools import corpusxmlfile, pick_parallel_docs

HERE = os.path.dirname(__file__)


article47_sme = u'''<?xml version="1.0" encoding="UTF-8"?>
<document id="no_id" xml:lang="sme">
  <header>
    <translated_from xml:lang="nob"/>
    <wordcount>209</wordcount>
    <parallel_text location="article-47.html" xml:lang="nob"/>
  </header>
</document>
'''

article47_nob = u'''<?xml version="1.0" encoding="UTF-8"?>
<document id="no_id" xml:lang="nob">
  <header>
    <wordcount>209</wordcount>
    <parallel_text location="article-47.html" xml:lang="sme"/>
  </header>
</document>
'''


class TestParallelPicker(unittest.TestCase):

    def setUp(self):
        self.tempdir = testfixtures.TempDirectory(ignore=['.git'])
        r = git.Repo.init(self.tempdir.path)
        self.tempdir.makedir('converted/sme/admin')
        self.tempdir.makedir('converted/nob/admin')

        self.language1_converted_dir = os.path.join(
            self.tempdir.path, 'converted/sme/admin')

        self.tempdir.write('converted/sme/admin/article-47.html.xml',
                           article47_sme.encode('utf8'))
        self.tempdir.write('converted/nob/admin/article-47.html.xml',
                           article47_nob.encode('utf8'))
        self.picker = pick_parallel_docs.ParallelPicker(
            self.language1_converted_dir, 'nob', '73', '110')

    def tearDown(self):
        self.tempdir.cleanup()

    def test_calculate_language1(self):
        self.picker.calculate_language1('converted/sme/admin')
        self.assertEqual(self.picker.language1, 'sme')

    def test_get_parallel_language(self):
        self.assertEqual(self.picker.parallel_language, 'nob')

    def test_has_parallel1(self):
        """Parallel exists, parallel_text points to correct place."""
        file_with_parallel1 = corpusxmlfile.CorpusXMLFile(os.path.join(
            self.language1_converted_dir,
            'article-47.html.xml'))
        self.assertEqual(self.picker.has_parallel(file_with_parallel1),
                         True)

    def test_has_parallel2(self):
        """parallel_text points to wrong language."""
        file_with_parallel1 = corpusxmlfile.CorpusXMLFile(os.path.join(
            self.language1_converted_dir,
            'article-47.html.xml'))
        file_with_parallel1.etree.find('//parallel_text').set(
            '{http://www.w3.org/XML/1998/namespace}lang', 'sma')
        self.assertEqual(self.picker.has_parallel(file_with_parallel1),
                         False)

    def test_has_parallel3(self):
        """parallel_text points to wrong file."""
        file_with_parallel1 = corpusxmlfile.CorpusXMLFile(os.path.join(
            self.language1_converted_dir,
            'article-47.html.xml'))
        file_with_parallel1.etree.find('//parallel_text').set(
            'location', 'article-48.html')
        self.assertEqual(self.picker.has_parallel(file_with_parallel1),
                         False)
