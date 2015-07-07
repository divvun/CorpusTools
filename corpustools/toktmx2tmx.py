# -*- coding: utf-8 -*-

#
#   This program converts toktmx files to tmx files useful for e.g.
#   Autshumato ITE
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
#   along with program. If not, see <http://www.gnu.org/licenses/>.
#
#   Copyright 2011-2015 Børre Gaup <borre.gaup@uit.no>
#

import os
import sys
import argparse
import lxml.etree
import subprocess

from corpustools import parallelize
from corpustools import util


class Toktmx2Tmx(object):
    """A class to make a tidied up version of toktmx files.
    Removes unwanted spaces around punctuation, parentheses and so on.
    """
    def read_toktmx_file(self, toktmx_file):
        """Reads a toktmx file, parses it, sets the tmx file name
        """
        self.tmxfile_name = toktmx_file.replace('toktmx', 'tmx')
        self.tmx = parallelize.Tmx(etree.parse(toktmx_file))
        self.add_filename_iD()

    def add_filename_iD(self):
        """Add the tmx filename as an prop element in the header
        """
        prop = etree.Element('prop')
        prop.attrib['type'] = 'x-filename'
        prop.text = os.path.basename(self.tmxfile_name).decode('utf-8')

        root = self.tmx.get_tmx().getroot()

        for header in root.iter('header'):
            header.append(prop)

    def write_cleanedup_tmx(self):
        """Write the cleanup tmx
        """
        self.tmx.write_tmx_file(self.tmxfile_name)

    def clean_toktmx(self):
        """Do the cleanup of the toktmx file
        """
        self.tmx.remove_unwanted_space()
        self.tmx.remove_tu_with_empty_seg()

    def find_toktmx_files(self, dirname):
        """
        Find the toktmx files in dirname, return them as a list
        """
        subp = subprocess.Popen(
            ['find', dirname,
                '-name', '*.toktmx', '-print'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (output, error) = subp.communicate()

        if subp.returncode != 0:
            util.note('ERROR: When searching for toktmx docs:')
            util.note(error)
            sys.exit(1)
        else:
            files = output.split('\n')
            return files[:-1]


def parse_options():
    """
    Parse the command line. No arguments expected.
    """
    parser = argparse.ArgumentParser(description = 'Run this script to generate tmx files for use in e.g. Autshumato ITE. It depends on toktmx files to exist in $GTFREE/prestable/toktmx.')
    parser.add_argument('dirname',
                        help="Directory where the toktmx files exist")
    args = parser.parse_args()
    return args


def main():
    args = parse_options()

    toktmx2tmx = Toktmx2Tmx()
    for filename in toktmx2tmx.find_toktmx_files(args.dirname):
        toktmx2tmx.read_toktmx_file(filename)
        toktmx2tmx.clean_toktmx()
        toktmx2tmx.write_cleanedup_tmx()
