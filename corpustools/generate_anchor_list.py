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

import os
import sys
import argparse

import argparse_version


class GenerateAnchorList(object):
    LANGUAGES = ['eng', 'nob', 'sme', 'fin', 'smj', 'sma']

    def __init__(self, lang1, lang2, outdir):
        self.lang1 = lang1
        self.lang2 = lang2
        self.outfile = os.path.join(outdir,
                                    'anchor-{}{}.txt'.format(lang1, lang2))

    def get_outfile(self):
        return self.outfile

    def generate_file(self, infiles):
        '''infiles is a list of files
        '''
        lang1_index = self.LANGUAGES.index(self.lang1)
        lang2_index = self.LANGUAGES.index(self.lang2)

        with open(self.outfile, 'wb') as outfile:
            print 'Generating anchor word list to {}'.format(self.outfile)

            for infile in infiles:
                with open(infile) as instream:
                    print 'Reading {}'.format(infile)
                    lineno = 0
                    for line in instream.readlines():
                        lineno += 1
                        line = line.strip()
                        if (not line.startswith('#') or not
                                line.startswith('&')):
                            words = line.split('/')
                            if len(words) == len(self.LANGUAGES):
                                word1 = words[lang1_index].strip()
                                word2 = words[lang2_index].strip()
                                if len(word1) > 0 and len(word2) > 0:
                                    print >>outfile, '{} / {}'.format(word1,
                                                                      word2)
                            else:
                                print >>sys.stderr, (
                                    'Invalid line at {} in {}'.format(lineno,
                                                                      infile))


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
