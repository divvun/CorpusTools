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
#   Copyright © 2014-2023 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Test the naming scheme of corpus files."""


import os
import unittest
import pytest

from parameterized import parameterized

from corpustools import corpuspath

HERE = os.path.dirname(__file__)


def name(module, lang, extension):
    """Produce a path to a corpus file.

    Args:
        module (str): module of the corpus file
        lang (str): language of the corpus file
        extension (str): extension of the corpus file

    Returns:
        str: path to the corpus file
    """
    corpusdir = f"corpus-{lang}-orig" if module == "orig" else f"corpus-{lang}"
    return os.path.join(
        HERE,
        corpusdir,
        f"{module + '/' if module != 'orig' else ''}subdir/subsubdir/filename.html"
        + extension,
    )


@pytest.mark.parametrize(
    "path, parent, corpusdir, corpusfile",
    [
        ("/a/corpus-x/b", "/a/", "corpus-x", "/b"),
        ("/a/b/corpus-orig-x-x/c/d/e", "/a/b/", "corpus-orig-x-x", "/c/d/e"),
    ],
)
def test_corpuspath_re(path, parent, corpusdir, corpusfile):
    assert corpuspath.CORPUS_DIR_RE.search(path).groups() == (
        parent,
        corpusdir,
        corpusfile,
    )


@pytest.mark.parametrize(
    "filename",
    [
        (name("orig", "sme", "")),
        (name("orig", "sme", ".xsl")),
        (name("orig", "sme", ".log")),
        (name("converted", "sme", ".xml")),
        (name("prestable/converted", "sme", ".xml")),
        (name("converted", "sme", ".xml")),
        (name("toktmx/nob", "sme", ".toktmx")),
        (name("prestable/toktmx/nob", "sme", ".toktmx")),
        (name("tmx/nob", "sme", ".tmx")),
        (name("prestable/tmx/nob", "sme", ".tmx")),
    ],
)
def test_path_to_orig(filename):
    """Check that the corpus file naming scheme works as it should.

    Args:
        testname (str): name of the test
        testcontent (dict): mapping from given name to the wanted name

    Raises:
        AssertionError: is raised if the result is not what is expected
    """

class TestComputeCorpusnames(unittest.TestCase):
    @staticmethod
    def name(module):
        return os.path.join(HERE, module, "sme/admin/subdir/subsubdir/filename.html")

    def setUp(self):
        self.corpus_path = corpuspath.CorpusPath(self.name("orig"))

    def test_compute_orig(self):
        self.assertEqual(self.corpus_path.orig, self.name("orig"))

    def test_compute_xsl(self):
        self.assertEqual(self.corpus_path.xsl, self.name("orig") + ".xsl")

    def test_compute_log(self):
        self.assertEqual(self.corpus_path.log, self.name("orig") + ".log")

    def test_compute_converted(self):
        self.assertEqual(self.corpus_path.converted, self.name("converted") + ".xml")

    def test_compute_prestable_converted(self):
        self.assertEqual(
            self.corpus_path.prestable_converted,
            self.name("prestable/converted") + ".xml",
        )

    def test_compute_goldstandard_converted(self):
        self.corpus_path.metadata.set_variable("conversion_status", "correct")
        self.assertEqual(
            self.corpus_path.converted, self.name("goldstandard/converted") + ".xml"
        )

    def test_compute_prestable_goldstandard_converted(self):
        self.corpus_path.metadata.set_variable("conversion_status", "correct")
        self.assertEqual(
            self.corpus_path.prestable_converted,
            self.name("prestable/goldstandard/converted") + ".xml",
        )

    def test_compute_analysed(self):
        self.assertEqual(self.corpus_path.analysed, self.name("analysed") + ".xml")

    def test_compute_sent_filename(self):
        self.assertEqual(
            self.corpus_path.sent_filename,
            f"{self.corpus_path.pathcomponents.root}/tmp/"
            f"{self.corpus_path.pathcomponents.basename}_"
            f"{self.corpus_path.pathcomponents.lang}.sent",
        )
