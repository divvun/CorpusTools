# -*- coding: utf-8 -*-

#
#   This file contains routines to convert files to the giellatekno xml
#   format.
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
#   Copyright 2012-2015 Børre Gaup <borre.gaup@uit.no>
#   Copyright 2014-2015 Kevin Brubeck Unhammer <unhammer@fsfe.org>
#

from __future__ import print_function

import argparse
import difflib
import io
import os
import sys

import argparse_version
import ccat



class DupeFinder(object):
    def __init__(self, directory):
        self.files = {}

        xmlprinter = ccat.XMLPrinter(all_paragraphs=True)
        for root, dirs, files in os.walk(directory):
            for f in files:
                if f.endswith('.xml'):
                    filename = os.path.join(root, f)
                    xmlprinter.parse_file(filename)
                    self.files[filename] = xmlprinter.process_file().getvalue()

    def compare_files(self):
        dupe_files = set()
        for filename1 in self.files.iterkeys():
            if filename1 not in dupe_files:
                for filename2 in self.files.iterkeys():
                    if filename1 != filename2 and filename2 not in dupe_files:
                        result = list(difflib.unified_diff(
                            self.files[filename1].splitlines(1),
                            self.files[filename2].splitlines(1)))
                        if len(result) == 0:
                            dupe_files.add(filename2)
                            xsl = filename2.replace('converted/', 'orig/').replace('.xml', '.xsl')
                            orig = xsl.replace('.xsl', '')
                            os.remove(xsl)
                            os.remove(orig)
                            print('Removed:', orig)

        print(len(dupe_files), len(self.files))


def parse_options():
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Convert original files to giellatekno xml.')

    parser.add_argument('dir',
                        help="The original file(s) or \
                        directory/ies where the original files exist")

    args = parser.parse_args()

    return args


def main():
    args = parse_options()

    df = DupeFinder(args.dir)
    df.compare_files()
