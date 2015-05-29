#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#   Generate an anchor file needed by the java aligner
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
#   Copyright 2015 Børre Gaup <borre.gaup@uit.no>
#

from __future__ import unicode_literals

import os
import sys
import argparse

import argparse_version

def note(msg):
    print >>sys.stderr, msg.encode('utf-8')

class GenerateAnchorList(object):
    def __init__(self, lang1, lang2, languages, anchor_file):
        self.lang1 = lang1
        self.lang2 = lang2
        self.lang1_index = languages.index(lang1)
        self.lang2_index = languages.index(lang2)
        self.languages = languages
        self.anchor_file = anchor_file

    def words_of_line(self, lineno, line):
        """Either a word-pair or None, if no word-pair on that line."""
        line = line.strip()
        if (not line.startswith('#') or not
                line.startswith('&')):
            words = line.split('/')
            if len(words) == len(self.languages):
                word1 = words[self.lang1_index].strip()
                word2 = words[self.lang2_index].strip()
                if len(word1) > 0 and len(word2) > 0:
                    return word1, word2
            else:
                print >>sys.stderr, (
                    'Invalid line at {} in {}'.format(lineno, self.anchor_file))

    def read_anchors(self, quiet=False):
        """List of word-pairs in infiles, empty/bad lines skipped."""
        out = []
        with open(self.anchor_file) as f:
            if not quiet:
                note('Reading {}'.format(self.anchor_file))
            out += [self.words_of_line(i, l.decode('utf-8'))
                    for i,l in enumerate(f.readlines())]
        return filter(None, out)

    def generate_file(self, outpath, quiet=False):
        '''infiles is a list of file paths
        '''
        anchors = self.read_anchors(quiet)

        with open(outpath, 'wb') as outfile:
            if not quiet:
                note('Generating anchor word list to {}'.format(outpath))
            out = "\n".join("{} / {}".format(w1, w2)
                            for w1,w2 in anchors)
            print >>outfile, out.encode('utf-8')


def parse_options():
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description=(
            'Generate paired anchor lisit for languages lg1 and lg2. '
            'Output line format e.g. njukčamán* / mars. '
            'Source file is given on the command line, the format is tailored '
            'for the file gt/common/src/anchor.txt.'))

    parser.add_argument('--lang1', help='First languages in the word list')
    parser.add_argument('--lang2', help='Second languages in the word list')
    parser.add_argument('--outdir', help='The output directory')
    parser.add_argument('input_file', nargs='+', help="The input file(s)")

    args = parser.parse_args()
    return args


def main():
    args = parse_options()

    gal = GenerateAnchorList(args.lang1, args.lang2, args.outdir)
    gal.generate_file(args.input_file)
