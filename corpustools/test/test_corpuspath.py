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

from corpustools import corpuspath

here = os.path.dirname(__file__)


path_to_corpuspath = {
    'orig_to_orig': {
        'in_name': os.path.join(
            here, 'orig/sme/admin/subdir/subsubdir/filename.html'),
        'want_name': os.path.join(
            here, 'orig/sme/admin/subdir/subsubdir/filename.html'),
    },
    'xsl_to_orig': {
        'in_name': os.path.join(
            here, 'orig/sme/admin/subdir/subsubdir/filename.html.xsl'),
        'want_name': os.path.join(
            here, 'orig/sme/admin/subdir/subsubdir/filename.html'),
    },
    'log_to_orig': {
        'in_name': os.path.join(
            here, 'orig/sme/admin/subdir/subsubdir/filename.html.log'),
        'want_name': os.path.join(
            here, 'orig/sme/admin/subdir/subsubdir/filename.html'),
    },
    'converted_to_orig': {
        'in_name': os.path.join(
            here, 'converted/sme/admin/subdir/subsubdir/filename.html.xml'),
        'want_name': os.path.join(
            here, 'orig/sme/admin/subdir/subsubdir/filename.html'),
    },
    'prestable_converted_to_orig': {
        'in_name': os.path.join(
            here, 'prestable/converted/sme/admin/subdir/subsubdir/filename.html.xml'),
        'want_name': os.path.join(
            here, 'orig/sme/admin/subdir/subsubdir/filename.html'),
    },
    'analysed_to_orig': {
        'in_name': os.path.join(
            here, 'converted/sme/admin/subdir/subsubdir/filename.html.xml'),
        'want_name': os.path.join(
            here, 'orig/sme/admin/subdir/subsubdir/filename.html'),
    },
    'toktmx_to_orig': {
        'in_name': os.path.join(
            here, 'toktmx/sme/admin/subdir/subsubdir/filename.html.toktmx'),
        'want_name': os.path.join(
            here, 'orig/sme/admin/subdir/subsubdir/filename.html'),
    },
    'prestable_toktmx_to_orig': {
        'in_name': os.path.join(
            here, 'prestable/toktmx/sme/admin/subdir/subsubdir/filename.html.toktmx'),
        'want_name': os.path.join(
            here, 'orig/sme/admin/subdir/subsubdir/filename.html'),
    },
    'tmx_to_orig': {
        'in_name': os.path.join(
            here, 'tmx/sme/admin/subdir/subsubdir/filename.html.tmx'),
        'want_name': os.path.join(
            here, 'orig/sme/admin/subdir/subsubdir/filename.html'),
    },
    'prestable_tmx_to_orig': {
        'in_name': os.path.join(
            here, 'prestable/tmx/sme/admin/subdir/subsubdir/filename.html.tmx'),
        'want_name': os.path.join(
            here, 'orig/sme/admin/subdir/subsubdir/filename.html'),
    },
}


def test_path_to_corpuspath():
    """Test the naming scheme for corpus paths."""
    for testname, testcontent in six.iteritems(path_to_corpuspath):
        yield check_names_to_corpuspath, testname, testcontent


def check_names_to_corpuspath(testname, testcontent):
    """Check that the corpus file naming scheme works as it should.

    Args:
        testname (str): name of the test
        testcontent (dict): mapping from given name to the wanted name

    Raises:
        AssertionError: is raised if the result is not what is expected
    """
    cp = corpuspath.CorpusPath(testcontent['in_name'])

    if cp.orig != testcontent['want_name']:
        raise AssertionError('{}:\nexpected {}\ngot {}'.format(
            testname, testcontent['want_name'], cp.orig))
