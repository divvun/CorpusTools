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
#   Copyright © 2015-2016 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

"""Classes to find and handle duplicate files in the repository.

The classes work on converted files.
"""


from __future__ import absolute_import, print_function

import argparse
import collections
import difflib
import os
import sys

import lxml.etree as etree
import six

from corpustools import argparse_version, ccat, move_files, util, xslsetter


class DupeFinder(object):
    """Handle duplicates in the corpus."""

    def __init__(self, directory):
        self.files = self._get_files(directory)
        self.dupe_files = set()

    @staticmethod
    def _get_files(directory):
        files = {}
        xmlprinter = ccat.XMLPrinter(all_paragraphs=True)
        for f in os.listdir(directory):
            if f.endswith('.xml'):
                filename = os.path.join(directory, f)
                xmlprinter.parse_file(filename)
                files[filename] = xmlprinter.process_file().getvalue()

        return files

    @staticmethod
    def get_parallel_texts(filename1):
        return etree.parse(filename1).xpath('.//parallel_text')

    def remove_dupe_file(self, filename1, filename2):
        result = list(difflib.unified_diff(
            self.files[filename1].splitlines(1),
            self.files[filename2].splitlines(1)))
        if not result:
            print('\nParallels:', filename1, filename2)
            to_remove = filename1
            if self.get_parallel_texts(filename1) > self.get_parallel_texts(filename2):
                to_remove = filename2

            self.dupe_files.add(to_remove)
            origname = to_remove.replace(
                'converted/', 'orig/').replace('.xml', '').decode('utf8')
            if os.path.exists(origname):
                move_files.mover(origname, u'')

    @staticmethod
    def get_wc(filename):
        tree = etree.parse(filename)
        w = tree.find('.//wordcount').text

        return float(w)

    def good_word_ratio(self, filename1, filename2):
        w1 = self.get_wc(filename1)
        w2 = self.get_wc(filename2)

        ratio = min(w1, w2) / max(w1, w2)

        return ratio > 0.9

    def compare_files(self, filename1, filename2):
        sm = difflib.SequenceMatcher(a=self.files[filename1],
                                     b=self.files[filename2])
        ratio = sm.ratio()
        if ratio > 0.90:
            self.dupe_files.add((filename1, filename2))
            print()
            print(round(ratio, 2), filename1, filename2)

            result = difflib.unified_diff(
                self.files[filename1].splitlines(1),
                self.files[filename2].splitlines(1),
                fromfile=os.path.basename(filename1),
                tofile=os.path.basename(filename2))
            sys.stdout.writelines(result)

    def iterate_all_files(self, remove=False):
        wrong_ratio = 0
        good_ratio = 0
        checked_files = collections.defaultdict(set)
        for filename1 in six.iterkeys(self.files):
            for filename2 in six.iterkeys(self.files):
                if filename1 != filename2 and filename1 not in checked_files[filename2]:
                    if self.good_word_ratio(filename1, filename2):
                        good_ratio += 1
                        if remove:
                            self.remove_dupe_file(filename1, filename2)
                        else:
                            self.compare_files(filename1, filename2)

                    checked_files[filename1].add(filename2)
                    checked_files[filename2].add(filename1)
                else:
                    wrong_ratio += 1

        util.print_frame(debug=good_ratio)
        util.print_frame(debug=wrong_ratio)
        print('Almost dupes', len(self.dupe_files))


def parse_remover_options():
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Remove duplicate files from the given directory')

    parser.add_argument('dir',
                        help="The directory where the converted files exist")

    args = parser.parse_args()

    return args


def main():
    args = parse_remover_options()

    df = DupeFinder(args.dir)
    df.iterate_all_files(remove=True)


def parse_finder_options():
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Find files with more than 90% similarity in the given directory')

    parser.add_argument('dir',
                        help="The directory where the converted files exist")

    args = parser.parse_args()

    return args


def find():
    args = parse_finder_options()

    df = DupeFinder(args.dir)
    df.iterate_all_files()
