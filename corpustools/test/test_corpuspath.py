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
#   Copyright © 2014-2017 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Test the naming scheme of corpus files."""

from __future__ import absolute_import

import os
import unittest

from parameterized import parameterized

from corpustools import corpuspath

HERE = os.path.dirname(__file__)


def name(module, lang, extension):
    """Produce a path to a corpus file.

    Arguments:
        module (str): module of the corpus file
        lang (str): language of the corpus file
        extension (str): extension of the corpus file

    Returns:
        str: path to the corpus file
    """
    return os.path.join(HERE, module, lang,
                        'subdir/subsubdir/filename.html' + extension)


@parameterized([
    ('orig_to_orig', name('orig', 'sme', '')),
    ('xsl_to_orig', name('orig', 'sme', '.xsl')),
    ('log_to_orig', name('orig', 'sme', '.log')),
    ('converted_to_orig', name('converted', 'sme', '.xml')),
    ('prestable_converted_to_orig', name('prestable/converted', 'sme', '.xml')),
    ('analysed_to_orig', name('converted', 'sme', '.xml')),
    ('toktmx_to_orig', name('toktmx/', 'sme2nob', '.toktmx')),
    ('prestable_toktmx_to_orig', name('prestable/toktmx/', 'sme2nob',
                                      '.toktmx')),
    ('tmx_to_orig', name('tmx', 'sme2nob', '.tmx')),
    ('prestable_tmx_to_orig', name('prestable/tmx/', 'sme2nob', '.tmx')),
])
def test_path_to_orig(testname, orig):
    """Check that the corpus file naming scheme works as it should.

    Args:
        testname (str): name of the test
        testcontent (dict): mapping from given name to the wanted name

    Raises:
        AssertionError: is raised if the result is not what is expected
    """
    corpus_path = corpuspath.CorpusPath(orig)
    orig_name = name(module='orig', lang='sme', extension='')
    if corpus_path.orig != orig_name:
        raise AssertionError('{}:\nexpected {}\ngot {}'.format(
            testname, orig_name, corpus_path.orig))


class TestComputeCorpusnames(unittest.TestCase):

    @staticmethod
    def name(module):
        return os.path.join(HERE, module,
                            'sme/admin/subdir/subsubdir/filename.html')

    def setUp(self):
        self.corpus_path = corpuspath.CorpusPath(self.name('orig'))

    def test_compute_orig(self):
        self.assertEqual(self.corpus_path.orig, self.name('orig'))

    def test_compute_xsl(self):
        self.assertEqual(self.corpus_path.xsl, self.name('orig') + '.xsl')

    def test_compute_log(self):
        self.assertEqual(self.corpus_path.log, self.name('orig') + '.log')

    def test_compute_converted(self):
        self.assertEqual(self.corpus_path.converted,
                         self.name('converted') + '.xml')

    def test_compute_prestable_converted(self):
        self.assertEqual(self.corpus_path.prestable_converted,
                         self.name('prestable/converted') + '.xml')

    def test_compute_goldstandard_converted(self):
        self.corpus_path.metadata.set_variable('conversion_status', 'correct')
        self.assertEqual(self.corpus_path.converted,
                         self.name('goldstandard/converted') + '.xml')

    def test_compute_prestable_goldstandard_converted(self):
        self.corpus_path.metadata.set_variable('conversion_status', 'correct')
        self.assertEqual(self.corpus_path.prestable_converted,
                         self.name('prestable/goldstandard/converted') + '.xml')

    def test_compute_analysed(self):
        self.assertEqual(self.corpus_path.analysed,
                         self.name('analysed') + '.xml')
