#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Program to pick out documents to be saved to the corpus from samediggi.se
'''


import os
import sys
import inspect
import shutil
import time
import urllib2

import xslsetter


def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno


class DocumentPicker(object):
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
        '''Iterate through all files, classify them according to language
        '''
        for root, dirs, files in os.walk(self.source_dir):
            for f in files:
                if f.endswith('.xsl'):
                    self.total_file += 1
                    self.classify_file(os.path.join(root, f))

    def classify_file(self, file_):
        '''Identify the language of the file
        '''
        mh = xslsetter.MetadataHandler(file_, create=True)
        url = mh.get_variable('filename')
        if ('regjeringen.no' in url and 'regjeringen.no' not in file_ and
                '.pdf' not in file_):
            try:
                remote = urllib2.urlopen(urllib2.Request(url.encode('utf8')))
                self.copyfile(remote, file_)
            except urllib2.HTTPError:
                print >>sys.stderr, lineno(), ('Could not fetch',
                                               file_.replace('.xsl', ''))
            except UnicodeEncodeError:
                print >>sys.stderr, lineno(), 'Unicode error in url', url
            print lineno(), 'sleeping …'
            time.sleep(2)

    def copyfile(self, remote, file_):
        try:
            with open(file_.replace('.xsl', ''), 'wb') as f:
                print lineno(), 'Fetching', file_.replace('.xsl', '')
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
