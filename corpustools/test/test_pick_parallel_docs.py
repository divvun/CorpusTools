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

import glob
import os
import unittest

import git
import testfixtures

from corpustools import corpusxmlfile, pick_parallel_docs

HERE = os.path.dirname(__file__)


ARTICLE47_SME = u'''<?xml version="1.0" encoding="UTF-8"?>
<document id="no_id" xml:lang="sme">
  <header>
    <translated_from xml:lang="nob"/>
    <wordcount>209</wordcount>
    <parallel_text location="article-47.html" xml:lang="nob"/>
    <parallel_text location="article-47.html" xml:lang="smj"/>
  </header>
  <body>
    <p>hallo</p>
  </body>
</document>
'''

ARTICLE47_NOB = u'''<?xml version="1.0" encoding="UTF-8"?>
<document id="no_id" xml:lang="nob">
  <header>
    <wordcount>209</wordcount>
    <parallel_text location="article-47.html" xml:lang="sme"/>
    <parallel_text location="article-47.html" xml:lang="smj"/>
  </header>
  <body>
    <p>hallo</p>
  </body>
</document>
'''

ARTICLE47_SMJ = u'''<?xml version="1.0" encoding="UTF-8"?>
<document id="no_id" xml:lang="smj">
  <header>
    <wordcount>209</wordcount>
    <parallel_text location="article-47.html" xml:lang="sme"/>
    <parallel_text location="article-47.html" xml:lang="nob"/>
  </header>
  <body>
    <p>hallo</p>
  </body>
</document>
'''


class TestParallelPicker(unittest.TestCase):
    """Test the ParallelPicker class."""

    def make_tempdir(self):
        """Make tempdir where ParallelPicker will do its magic."""
        tempdir = testfixtures.TempDirectory(ignore=['.git'])
        tempdir.makedir('converted/sme/admin')
        tempdir.makedir('converted/nob/admin')
        tempdir.makedir('converted/smj/admin')
        tempdir.write('converted/sme/admin/article-47.html.xml',
                      ARTICLE47_SME.encode('utf8'))
        tempdir.write('converted/nob/admin/article-47.html.xml',
                      ARTICLE47_NOB.encode('utf8'))
        tempdir.write('converted/smj/admin/article-47.html.xml',
                      ARTICLE47_SMJ.encode('utf8'))

        return tempdir

    def setUp(self):
        """Make the ParallelPicker work on tempdir."""
        self.tempdir = self.make_tempdir()
        git.Repo.init(self.tempdir.path)
        self.language1_converted_dir = os.path.join(
            self.tempdir.path, 'converted/sme/admin')
        self.picker = pick_parallel_docs.ParallelPicker(
            self.language1_converted_dir, 'nob', '73', '110')

    def tearDown(self):
        """Cleanup after tests are done."""
        self.tempdir.cleanup()

    def test_calculate_language1(self):
        """Check that the correct language is found."""
        self.picker.calculate_language1('converted/sme/admin')
        self.assertEqual(self.picker.language1, 'sme')

    def test_get_parallel_language(self):
        """Check that the correct parallel language is set."""
        self.assertEqual(self.picker.parallel_language, 'nob')

    def test_has_parallel1(self):
        """Parallel exists, parallel_text points to correct place."""
        file_with_parallel1 = corpusxmlfile.CorpusXMLFile(os.path.join(
            self.language1_converted_dir,
            'article-47.html.xml'))
        self.assertTrue(self.picker.has_parallel(file_with_parallel1))

    def test_has_parallel2(self):
        """parallel_text points to wrong language."""
        file_with_parallel1 = corpusxmlfile.CorpusXMLFile(os.path.join(
            self.language1_converted_dir,
            'article-47.html.xml'))
        file_with_parallel1.etree.find('//parallel_text').set(
            '{http://www.w3.org/XML/1998/namespace}lang', 'sma')
        self.assertFalse(self.picker.has_parallel(file_with_parallel1))

    def test_has_parallel3(self):
        """parallel_text points to wrong file."""
        file_with_parallel1 = corpusxmlfile.CorpusXMLFile(os.path.join(
            self.language1_converted_dir,
            'article-47.html.xml'))
        file_with_parallel1.etree.find('//parallel_text').set(
            'location', 'article-48.html')
        self.assertFalse(self.picker.has_parallel(file_with_parallel1))

    def test_find_lang1_files(self):
        """Check that lang1 files are found."""
        self.assertListEqual(
            glob.glob(self.language1_converted_dir + '/*.xml'),
            [corpus_file.name
             for corpus_file in self.picker.find_lang1_files()])

    def test_copy_valid_parallels(self):
        """Only copy in the nob-sme pair, and align them."""
        self.picker.copy_valid_parallels()
        self.tempdir.check_all(
            'prestable',
            'converted/',
            'converted/nob/',
            'converted/nob/admin/',
            'converted/nob/admin/article-47.html.xml',
            'converted/sme/',
            'converted/sme/admin/',
            'converted/sme/admin/article-47.html.xml',
            'tmx/',
            'tmx/nob2sme/',
            'tmx/nob2sme/admin/',
            'tmx/nob2sme/admin/article-47.html.tmx',
            'tmx/nob2sme/admin/article-47.html.tmx.html')
