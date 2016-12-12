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
#   Copyright © 2014-2016 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

"""Test the naming scheme of corpus files."""

from __future__ import absolute_import

import os

import six
from nose_parameterized import parameterized

from corpustools import corpuspath

here = os.path.dirname(__file__)

def name(module, lang, extension):
    return os.path.join(here, module, lang,
                        'subdir/subsubdir/filename.html' + extension)

@parameterized([
    ('orig_to_orig', name('orig', 'sme', '')),
    ('xsl_to_orig', name('orig', 'sme', '.xsl')),
    ('log_to_orig', name('orig', 'sme', '.log')),
    ('converted_to_orig', name('converted', 'sme', '.xml')),
    ('prestable_converted_to_orig', name('prestable/converted', 'sme', '.xml')),
    ('analysed_to_orig', name('converted', 'sme', '.xml')),
    ('toktmx_to_orig', name('toktmx/', 'sme2nob', '.toktmx')),
    ('prestable_toktmx_to_orig', name('prestable/toktmx/', 'sme2nob', '.toktmx')),
    ('tmx_to_orig', name('tmx', 'sme2nob', '.tmx')),
    ('prestable_tmx_to_orig', name('prestable/tmx/', 'sme2nob', '.tmx')),
])
def test_path_to_corpuspath(testname, orig):
    """Check that the corpus file naming scheme works as it should.

    Args:
        testname (str): name of the test
        testcontent (dict): mapping from given name to the wanted name

    Raises:
        AssertionError: is raised if the result is not what is expected
    """
    cp = corpuspath.CorpusPath(orig)

    if cp.orig != name('orig', 'sme', ''):
        raise AssertionError('{}:\nexpected {}\ngot {}'.format(
            testname, name('orig', 'sme', ''), cp.orig))
