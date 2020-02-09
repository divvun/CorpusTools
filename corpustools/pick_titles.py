#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#   Program to pick out documents to be saved to the corpus from samediggi.se
#
#   This file contains routines to change names of corpus files
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
#   Copyright © 2013-2020 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Program to pick out documents to be saved to the corpus from samediggi.se.

The documents have been fetched using wget.
"""

from __future__ import absolute_import, print_function, unicode_literals

import os
import shutil
import sys
import time
import urllib2

from corpustools import util, xslsetter


class DocumentPicker(object):
    """Pick documents from samediggi.se to be added to the corpus."""

    def __init__(self, source_dir):
        self.freecorpus = os.getenv('GTFREE')
        self.source_dir = source_dir
        self.file_dict = {}
        self.file_dict.setdefault('sma', [])
        self.file_dict.setdefault('sme', [])
        self.file_dict.setdefault('smj', [])
        self.file_dict.setdefault('swe', [])
        self.file_dict.setdefault('none', [])
        self.parallel_dict = {}
        self.total_file = 0

    def classify_files(self):
        """Iterate through all files, classify them according to language"""
        for root, dirs, files in os.walk(self.source_dir):
            for f in files:
                if f.endswith('.xsl'):
                    self.total_file += 1
                    self.classify_file(os.path.join(root, f))

    def classify_file(self, file_):
        """Identify the language of the file"""
        mh = xslsetter.MetadataHandler(file_, create=True)
        url = mh.get_variable('filename')
        if ('regjeringen.no' in url and 'regjeringen.no' not in file_ and
                '.pdf' not in file_):
            try:
                remote = urllib2.urlopen(urllib2.Request(url.encode('utf8')))
                self.copyfile(remote, file_)
            except urllib2.HTTPError:
                print(
                    util.lineno(),
                    'Could not fetch',
                    file_.replace('.xsl', ''),
                    file=sys.stderr)
            except UnicodeEncodeError:
                print(
                    util.lineno(), 'Unicode error in url', url, file=sys.stderr)
            print(util.lineno(), 'sleeping …')
            time.sleep(2)

    def copyfile(self, remote, file_):
        try:
            with open(file_.replace('.xsl', ''), 'wb') as f:
                print(util.lineno(), 'Fetching', file_.replace('.xsl', ''))
                shutil.copyfileobj(remote, f)
        finally:
            remote.close()


def main():
    dp = DocumentPicker(sys.argv[1])
    dp.classify_files()
    #  dp.conclude()
    #  dp.check_consistency()
    #  dp.move_files_set_metadata()


if __name__ == "__main__":
    main()
