# -*- coding: utf-8 -*-

#
#   Add tmx files to a zipfile.
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
#   Copyright 2012-2015 Børre Gaup <borre.gaup@uit.no>
#

import os
import sys
import argparse
import zipfile
import subprocess
import time
import zlib


class PackageTmx:
    """A class to package tmx files into a zip file
    """
    def __init__(self, dirname):
        """Set the counter on which filenames are based
        """
        self.fileId = 1
        self.date = time.strftime('%Y-%m-%d', time.localtime())
        self.dirname = dirname
        self.zipname = self.dirname + '-' + self.date + '.zip'
        self.zipfile = zipfile.ZipFile(self.zipname, mode='w')

    def __del__(self):
        """Close the zipfile"""
        print "All tmx files are in", self.zipname
        self.zipfile.close()

    def findTmxFiles(self):
        """
        Find the tmx files in dirname, return them as a list
        """
        subp = subprocess.Popen(['find', os.path.join(os.environ['GTFREE'], 'prestable/tmx/' + self.dirname), '-name', '*.tmx', '-print' ], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        (output, error) = subp.communicate()

        if subp.returncode != 0:
            print >>sys.stderr, 'Error when searching for tmx docs'
            print >>sys.stderr, error
            sys.exit(1)
        else:
            files = output.split('\n')
            return files[:-1]

    def generateFilename(self):
        """Generate a new file name. Return the new filename
        """
        name = self.dirname + '-' + self.date + '-{0:06d}'.format(self.fileId) + '.tmx'
        self.fileId += 1

        return name

    def writeNewFile(self, tmxFile):
        """Write the file to the zipfile with a new filename
        """
        #print "Writing", self.tmxFile, 'as', self.generateFilename()
        self.zipfile.write(tmxFile, arcname=self.generateFilename(), compress_type = zipfile.ZIP_DEFLATED)

def parse_options():
    """
    Parse the command line. No arguments expected.
    """
    parser = argparse.ArgumentParser(description = 'Run this to add tmx files to a zip archive. It depends on tmx files to exist in $GTFREE/prestable/tmx.')

    args = parser.parse_args()
    return args

def main():
    args = parse_options()


    for dirname in ['nob2sme']:
        packagetmx = PackageTmx(dirname)
        for filename in packagetmx.findTmxFiles():
            packagetmx.writeNewFile(filename)
