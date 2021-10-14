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
#   Copyright © 2011-2021 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Class to test the class CorpusXMLFile."""


import doctest
import os
import unittest

from lxml import doctestcompare, etree

from corpustools import corpusxmlfile, corpuspath

HERE = os.path.dirname(__file__)


class TestCorpusXMLFile(unittest.TestCase):
    """A test class for the CorpusXMLFile class."""

    def setUp(self):
        self.pfile = corpusxmlfile.CorpusXMLFile(
            os.path.join(
                HERE,
                "parallelize_data",
                "converted/sme/facta/skuvlahistorja2/",
                "aarseth2-s.html.xml",
            )
        )

    @staticmethod
    def assertXmlEqual(got, want):
        """Check if two stringified xml snippets are equal."""
        string_got = etree.tostring(got, encoding="unicode")
        string_want = etree.tostring(want, encoding="unicode")

        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(string_want, string_got, 0):
            message = checker.output_difference(
                doctest.Example("", string_want), string_got, 0
            )
            raise AssertionError(message)

    def test_get_translated_from(self):
        self.assertEqual(self.pfile.translated_from, "nob")

    def test_get_word_count(self):
        corpusfile = corpusxmlfile.CorpusXMLFile(
            os.path.join(
                HERE,
                "parallelize_data",
                "converted/sme/facta/skuvlahistorja2/",
                "aarseth2-s.html.xml",
            )
        )
        self.assertEqual(corpusfile.word_count, "3229")

    def test_remove_version(self):
        file_with_version = corpusxmlfile.CorpusXMLFile(
            os.path.join(
                HERE,
                "parallelize_data",
                "converted/sme/facta/skuvlahistorja2/",
                "aarseth2-s.html.xml",
            )
        )
        file_with_version.remove_version()

        self.assertIsNone(file_with_version.root.find(".//version"))

    def test_remove_skip(self):
        file_with_skip = corpusxmlfile.CorpusXMLFile(
            os.path.join(
                HERE,
                "parallelize_data",
                "converted/sme/facta/skuvlahistorja2/",
                "aarseth2-s-with-skip.html.xml",
            )
        )
        file_with_skip.remove_skip()
        self.assertListEqual(file_with_skip.root.xpath(".//skip"), [])

    def test_move_later(self):
        file_with_later = corpusxmlfile.CorpusXMLFile(
            os.path.join(
                HERE,
                "parallelize_data",
                "converted/sme/facta/skuvlahistorja2/",
                "aarseth2-s-with-later.html.xml",
            )
        )

        before = [
            later.getparent().index(later)
            for later in file_with_later.root.xpath(".//later")
        ]
        file_with_later.move_later()
        after = [
            later.getparent().index(later)
            for later in file_with_later.root.xpath(".//later")
        ]

        self.assertNotEqual(before, after)
