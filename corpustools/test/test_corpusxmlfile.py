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
#   Copyright © 2011-2020 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Class to test the class CorpusXMLFile."""

from __future__ import absolute_import, print_function, unicode_literals

import doctest
import os
import unittest

from lxml import doctestcompare, etree

from corpustools import corpusxmlfile

HERE = os.path.dirname(__file__)


class TestCorpusXMLFile(unittest.TestCase):
    """A test class for the CorpusXMLFile class."""

    def setUp(self):
        self.pfile = corpusxmlfile.CorpusXMLFile(
            os.path.join(HERE, "parallelize_data",
                         "prestable/converted/sme/facta/skuvlahistorja2/"
                         "aarseth2-s.htm.xml"))

    @staticmethod
    def assertXmlEqual(got, want):
        """Check if two stringified xml snippets are equal."""
        string_got = etree.tostring(got, encoding='unicode')
        string_want = etree.tostring(want, encoding='unicode')

        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(string_want, string_got, 0):
            message = checker.output_difference(
                doctest.Example("", string_want), string_got, 0)
            raise AssertionError(message)

    def test_basename(self):
        self.assertEqual(self.pfile.basename, "aarseth2-s.htm.xml")

    def test_dirname(self):
        self.assertEqual(
            self.pfile.dirname,
            os.path.join(HERE, "parallelize_data",
                         "prestable/converted/sme/facta/skuvlahistorja2"))

    def test_name(self):
        self.assertEqual(
            self.pfile.name,
            os.path.join(HERE, "parallelize_data",
                         "prestable/converted/sme/facta/skuvlahistorja2/"
                         "aarseth2-s.htm.xml"))

    def test_lang(self):
        self.assertEqual(self.pfile.lang, "sme")

    def test_get_parallel_basename(self):
        self.assertEqual(
            self.pfile.get_parallel_basename('nob'), "aarseth2-n.htm")

    def test_get_parallel_filename(self):
        self.assertEqual(
            self.pfile.get_parallel_filename('nob'),
            os.path.join(HERE, "parallelize_data",
                         "prestable/converted/nob/facta/skuvlahistorja2/"
                         "aarseth2-n.htm.xml"))

    def test_get_original_filename(self):
        self.assertEqual(
            self.pfile.original_filename,
            os.path.join(HERE, "parallelize_data",
                         "orig/sme/facta/skuvlahistorja2/aarseth2-s.htm"))

    def test_get_translated_from(self):
        self.assertEqual(self.pfile.translated_from, "nob")

    def test_get_word_count(self):
        corpusfile = corpusxmlfile.CorpusXMLFile(
            os.path.join(HERE,
                         'parallelize_data/aarseth2-n-with-version.htm.xml'))
        self.assertEqual(corpusfile.word_count, "4009")

    def test_remove_version(self):
        file_with_version = corpusxmlfile.CorpusXMLFile(
            os.path.join(HERE,
                         'parallelize_data/aarseth2-n-with-version.htm.xml'))
        file_without_version = corpusxmlfile.CorpusXMLFile(
            os.path.join(HERE,
                         'parallelize_data/aarseth2-n-without-version.htm.xml'))

        file_with_version.remove_version()

        got = file_without_version.etree
        want = file_with_version.etree

        self.assertXmlEqual(got, want)

    def test_remove_skip(self):
        file_with_skip = corpusxmlfile.CorpusXMLFile(
            os.path.join(HERE, 'parallelize_data/aarseth2-s-with-skip.htm.xml'))
        file_without_skip = corpusxmlfile.CorpusXMLFile(
            os.path.join(HERE,
                         'parallelize_data/aarseth2-s-without-skip.htm.xml'))

        file_with_skip.remove_skip()

        got = file_without_skip.etree
        want = file_with_skip.etree

        self.assertXmlEqual(got, want)

    def test_move_later(self):
        file_with_later = corpusxmlfile.CorpusXMLFile(
            os.path.join(HERE,
                         'parallelize_data/aarseth2-s-with-later.htm.xml'))
        file_with_moved_later = corpusxmlfile.CorpusXMLFile(
            os.path.join(
                HERE, 'parallelize_data/aarseth2-s-with-moved-later.htm.xml'))

        file_with_later.move_later()
        got = file_with_moved_later.etree
        want = file_with_later.etree
        self.assertXmlEqual(got, want)
