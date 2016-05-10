# -*- coding:utf-8 -*-

#
#   Normalise the files in the given directory
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

from __future__ import absolute_import
from __future__ import print_function
import argparse
import os

from corpustools import argparse_version
from corpustools import namechanger


def normaliser():
    '''Normalise the filenames in the corpuses'''
    for corpus in [os.getenv('GTFREE'), os.getenv('GTBOUND')]:
        print(('Normalising names in {}'.format(corpus)))
        for root, dirs, files in os.walk(os.path.join(corpus, 'orig')):
            print(('\t' + root.replace(corpus, '')))
            for f in files:
                if not f.endswith('.xsl'):
                    try:
                        cfmu = namechanger.CorpusFilesetMoverAndUpdater(
                            os.path.join(root, f).decode('utf8'),
                            os.path.join(root, f).decode('utf8'))
                        filepair = cfmu.mc.filepairs[0]
                        print(('\t\tmove {} -> {}'.format(
                            filepair.oldpath, filepair.newpath)))
                        cfmu.move_files()
                        cfmu.update_own_metadata()
                        cfmu.update_parallel_files_metadata()
                    except UserWarning:
                        pass


def normalise_parse_args():
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Program to automatically normalise names in '
        '$GTFREE and $GTBOUND. The filenames are downcases, non ascii '
        'characters are replaced by ascii ones and some unwanted characters '
        'are removed')

    parser.parse_args()


def main():
    normalise_parse_args()
    normaliser()
