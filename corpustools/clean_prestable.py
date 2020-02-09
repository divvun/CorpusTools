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
#   Copyright © 2016-2020 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Classes and functions to clean the prestable directories."""

from __future__ import absolute_import, print_function, unicode_literals

import argparse
import os
from collections import defaultdict

import git

from corpustools import argparse_version, corpuspath, util, versioncontrol


def parse_options():
    """Parse the commandline options.

    Returns:
        a list of arguments as parsed by argparse.Argumentparser.
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Remove files in prestable that have no original files.')

    parser.add_argument('corpusdirs', nargs='+', help='Corpus directories')

    args = parser.parse_args()
    return args


def find_prestable_files(corpusdir):
    """Find interesting files in prestable.

    Args:
        corpusdir (src): path to a corpus directory

    Yields:
        str: path to an interesting prestable file
    """
    for subdir in ['converted', 'tmx']:
        prestable_root = os.path.join(corpusdir, 'prestable', subdir)
        if os.path.exists(prestable_root):
            for root, _, files in os.walk(prestable_root):
                if 'pre_run' not in root:
                    for presteable_file in files:
                        yield os.path.join(root, presteable_file)


def main():
    """Remove files in prestable that don't have original files."""
    args = parse_options()

    counter = defaultdict(int)
    for corpusdir in args.corpusdirs:
        vcsfactory = versioncontrol.VersionControlFactory()
        vcs = vcsfactory.vcs(corpusdir)
        for prestable_path in find_prestable_files(corpusdir):
            corpus_file = corpuspath.CorpusPath(prestable_path)
            if not os.path.exists(corpus_file.orig):
                counter['prestable'] += 1
                print('Removing {}'.format(prestable_path))
                print('Orig was {}'.format(corpus_file.orig))
                try:
                    vcs.remove(prestable_path)
                except git.exc.GitCommandError:
                    util.note('\nError when trying to remove {}'.format(
                        corpus_file.prestable_converted))
                    util.note('Orig was {}\n'.format(prestable_path))

    for key in counter.keys():
        print('Removed {} files from prestable'.format(counter[key]))
