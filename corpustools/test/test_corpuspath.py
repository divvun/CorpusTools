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
from pathlib import Path

import pytest

from corpustools import corpuspath

HERE = os.path.dirname(__file__)


def name(module, lang, extension, goallang):
    """Produce a path to a corpus file.

    Args:
        module (str): module of the corpus file
        lang (str): language of the corpus file
        extension (str): extension of the corpus file
        goallang (str): goallang of tmx file

    Returns:
        (str): path to the corpus file
    """
    corpusdir = f"corpus-{lang}-orig" if module == "orig" else f"corpus-{lang}"
    return (
        Path(HERE)
        / corpusdir
        / f"{module if module != 'orig' else ''}"
        / f"{goallang if module.endswith('tmx') else ''}"
        / f"subdir/subsubdir/filename.html{extension}"
    )


@pytest.mark.parametrize(
    "path, parent, corpusdir, corpusfile",
    [
        ("/a/corpus-lang-x/b", "/a", "lang-x", "b"),
        ("/a/b/corpus-lang-orig-x-x/c/d/e", "/a/b", "lang-orig-x-x", "c/d/e"),
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
        (name("orig", "sme", "", "")),
        (name("orig", "sme", ".xsl", "")),
        (name("orig", "sme", ".log", "")),
        (name("correct-no-gs/converted", "sme", ".xml", "")),
        (name("goldstandard/converted", "sme", ".xml", "")),
        (name("stable/converted", "sme", ".xml", "")),
        (name("stable/tmx", "sme", ".tmx", "nob")),
        (name("analysed", "sme", ".xml", "")),
        (name("converted", "sme", ".xml", "")),
        (name("korp_mono", "sme", ".xml", "")),
        (name("korp_tmx", "sme", ".tmx", "nob")),
        (name("tmx", "sme", ".tmx", "nob")),
    ],
)
def test_path_to_orig(filename):
    """Check that the corpus file naming scheme works as it should.

    Args:
        filename (str): the filename to check

    Raises:
        AssertionError: is raised if the result is not what is expected
    """
    assert corpuspath.make_corpus_path(filename).orig == name(
        module="orig", lang="sme", extension="", goallang=""
    )


class TestComputeCorpusnames(unittest.TestCase):
    def setUp(self):
        self.corpus_path = corpuspath.make_corpus_path(name("orig", "sme", "", ""))

    def test_compute_orig(self):
        self.assertEqual(self.corpus_path.orig, name("orig", "sme", "", ""))

    def test_compute_xsl(self):
        self.assertEqual(self.corpus_path.xsl, name("orig", "sme", ".xsl", ""))

    def test_compute_log(self):
        self.assertEqual(self.corpus_path.log, name("orig", "sme", ".log", ""))

    def test_compute_converted(self):
        self.assertEqual(
            self.corpus_path.converted, name("converted", "sme", ".xml", "")
        )

    def test_compute_goldstandard_converted(self):
        self.corpus_path.metadata.set_variable("conversion_status", "correct")
        self.assertEqual(
            self.corpus_path.converted,
            name("goldstandard/converted", "sme", ".xml", ""),
        )

    def test_compute_correctnogs_converted(self):
        self.corpus_path.metadata.set_variable("conversion_status", "correct-no-gs")
        self.assertEqual(
            self.corpus_path.converted,
            name("correct-no-gs/converted", "sme", ".xml", ""),
        )

    def test_compute_analysed(self):
        self.assertEqual(
            self.corpus_path.analysed,
            name("analysed", "sme", ".xml", ""),
        )

    def test_compute_korp_mono(self):
        self.assertEqual(
            self.corpus_path.korp_mono,
            name("korp_mono", "sme", ".xml", ""),
        )

    def test_compute_korp_tmx(self):
        self.assertEqual(
            self.corpus_path.korp_tmx("nob"),
            name("korp_tmx", "sme", ".tmx", "nob"),
        )

    def test_compute_tmx(self):
        self.assertEqual(
            self.corpus_path.tmx("nob"),
            name("tmx", "sme", ".tmx", "nob"),
        )

    def test_compute_parallel(self):
        self.corpus_path.metadata.set_parallel_text("nob", "filename.html")
        self.assertEqual(
            self.corpus_path.parallel("nob"),
            name("orig", "nob", "", ""),
        )

    def test_compute_sent_filename(self):
        self.corpus_path.tca2_input == (
            self.corpus_path.root
            / f"corpus-{self.corpus_path.lang}/tmp"
            / f"{self.corpus_path.filepath.name}_"
            / f"{self.corpus_path.lang}.sent"
        )

    def test_compute_orig_corpus_dir(self):
        assert (
            self.corpus_path.orig_corpus_dir
            == self.corpus_path.root / "corpus-sme-orig"
        )

    def test_compute_converted_corpus_dir(self):
        assert (
            self.corpus_path.converted_corpus_dir
            == self.corpus_path.root / "corpus-sme"
        )
