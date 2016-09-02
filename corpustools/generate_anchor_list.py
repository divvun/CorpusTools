#!/usr/bin/env python
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

"""Generate an anchor file needed by the java aligner."""


from __future__ import absolute_import, print_function, unicode_literals

import argparse
import codecs
import sys

from corpustools import argparse_version, util


class GenerateAnchorList(object):
    """Generate anchor list used by tca2."""

    def __init__(self, lang1, lang2, columns, path):
        self.lang1 = lang1
        self.lang2 = lang2
        self.lang1_index = columns.index(lang1)
        self.lang2_index = columns.index(lang2)
        self.columns = columns
        self.path = path

    def words_of_line(self, lineno, line):
        """Either a word-pair or None, if no word-pair on that line."""
        line = line.strip()
        if (not line.startswith('#') or not
                line.startswith('&')):
            words = line.split('/')
            if len(words) == len(self.columns):
                word1 = words[self.lang1_index].strip()
                word2 = words[self.lang2_index].strip()
                if word1 and word2:
                    return word1, word2
            else:
                print('Invalid line at {} in {}'.format(lineno, self.path),
                      file=sys.stderr)

    def read_anchors(self, quiet=False):
        """List of word-pairs in infiles, empty/bad lines skipped."""
        with codecs.open(self.path, encoding='utf8') as f:
            out = [self.words_of_line(i, l)
                   for i, l in enumerate(f.readlines())]
            out = [_f for _f in out if _f]
            if not quiet:
                util.note("Read {} anchors from {}".format(len(out),
                                                           self.path))
            return out

    def generate_file(self, outpath, quiet=False):
        '''infiles is a list of file paths'''
        anchors = self.read_anchors(quiet)

        with codecs.open(outpath, 'w', encoding='utf8') as outfile:
            if not quiet:
                util.note('Generating anchor word list to {}'.format(outpath))
            out = u"\n".join(u"{} / {}".format(w1, w2)
                             for w1, w2 in anchors)
            outfile.write(out)
            outfile.write('\n')


def parse_options():
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description=(
            "Generate paired anchor list for languages lang1 and lang2. "
            "Output line format e.g. njukčamán* / mars. "
            "Source file is given on the command line, the format is "
            "hardcoded for the languages used in "
            "$GTHOME/gt/common/src/anchor.txt."))

    parser.add_argument("--lang1", help="First languages in the word list")
    parser.add_argument("--lang2", help="Second languages in the word list")
    parser.add_argument("--outdir", help="The output directory")
    parser.add_argument("input_file", nargs='+', help="The input file(s)")

    args = parser.parse_args()
    return args


def main():
    args = parse_options()

    gal = GenerateAnchorList(args.lang1, args.lang2,
                             ['eng', 'nob', 'sme', 'fin',
                                 'smj', 'sma', 'smn', 'sms'],
                             args.input_file)
    gal.generate_file("{}/anchor-{}{}.txt".format(args.outdir,
                                                  args.lang1,
                                                  args.lang2))
