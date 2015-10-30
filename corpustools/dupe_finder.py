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
#   Copyright © 2015 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

from __future__ import print_function

import argparse
import difflib
import io
import os
import sys

import argparse_version
import ccat
import versioncontrol
import xslsetter



class DupeFinder(object):
    def __init__(self, directory):
        self.files = self._get_files(directory)
        self.dupe_files = set()
        absdir = os.path.abspath(directory)
        corpusdir = absdir[:absdir.find('/converted/')]
        self.vcs = versioncontrol.VersionControlFactory().vcs(corpusdir)

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

    def remove_dupe_files(self):
        for filename1 in self.files.iterkeys():
            if filename1 not in self.dupe_files:
                for filename2 in self.files.iterkeys():
                    if filename1 != filename2 and filename2 not in self.dupe_files:
                        self.remove_dupe_file(filename1, filename2)

    def remove_dupe_file(self, filename1, filename2):
        result = list(difflib.unified_diff(
            self.files[filename1].splitlines(1),
            self.files[filename2].splitlines(1)))
        if len(result) == 0:
            self.dupe_files.add(filename2)
            os.remove(filename2)
            xsl = filename2.replace('converted/', 'orig/').replace('.xml', '.xsl')
            orig = xsl.replace('.xsl', '')
            self.remove_from_parallel_files(xsl)
            self.vcs.remove(xsl)
            self.vcs.remove(orig)
            print('Removed:', orig)

    def remove_from_parallel_files(self, orig_xslname):
        orig_xsl = xslsetter.MetadataHandler(orig_xslname)
        parallel_files = orig_xsl.get_parallel_texts()

        for lang, filename in parallel_files.iteritems():
            orig_lang = orig_xsl.get_variable('mainlang')
            new_xslname = orig_xslname.replace(orig_lang + '/', lang + '/')
            new_xslname = new_xslname.replace(os.path.basename(orig_xslname), filename + '.xsl')
            new_xsl = xslsetter.MetadataHandler(new_xslname)
            new_xsl.set_parallel_text(orig_lang, '')
            new_xsl.write_file()

    def find_almost_dupes(self):
        for filename1 in self.files.iterkeys():
            if filename1 not in self.dupe_files:
                for filename2 in self.files.iterkeys():
                    if filename1 != filename2 and filename2 not in self.dupe_files:
                        sm = difflib.SequenceMatcher(a=self.files[filename1],
                                                    b=self.files[filename2])
                        ratio = sm.ratio()
                        if ratio > 0.90:
                            self.dupe_files.add(filename2)
                            print()
                            print(round(ratio, 2), len(self.files[filename1]))

                            result = difflib.unified_diff(
                                self.files[filename1].splitlines(1),
                                self.files[filename2].splitlines(1),
                                fromfile=os.path.basename(filename1),
                                tofile=os.path.basename(filename2))
                            sys.stdout.writelines(result)

        print('Almost dupes', len(self.dupe_files))



def parse_options():
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Remove duplicate files.')

    parser.add_argument('dir',
                        help="The directory the converted files exist")

    args = parser.parse_args()

    return args


def main():
    args = parse_options()

    df = DupeFinder(args.dir)
    df.remove_dupe_files()

def find():
    args = parse_options()

    df = DupeFinder(args.dir)
    df.find_almost_dupes()
