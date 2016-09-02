# -*- coding:utf-8 -*-

#
#   Check the consistency of the parallel entries in the metadata files
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

from __future__ import absolute_import, print_function

import argparse
import os

import six

from corpustools import argparse_version, namechanger, util, xslsetter


def parse_args():
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Check the if the files in the parallel_text entries '
        'found in the metadata files exist')

    parser.add_argument('orig_dir',
                        help='The directory where the original corpus '
                        'files are')

    return parser.parse_args()


def main():
    total = 0
    para_fail = 0
    no_orig_xsl = 0
    args = parse_args()

    for root, dirs, files in os.walk(args.orig_dir):
        for f in files:
            if not f.endswith('.xsl'):
                total += 1
                orig = os.path.join(root, f)
                orig_components = util.split_path(orig)
                xsl_name = orig + '.xsl'
                if os.path.exists(xsl_name):
                    xsl = xslsetter.MetadataHandler(xsl_name)

                    para_files = set()
                    for lang, parallel in six.iteritems(xsl.get_parallel_texts()):
                        parallelpath = u'/'.join((
                            orig_components.root,
                            orig_components.module,
                            lang, orig_components.genre,
                            orig_components.subdirs, parallel))
                        if not os.path.isfile(parallelpath.encode('utf8')):
                            none_dupe_path = os.path.join(os.path.join(
                                os.path.dirname(parallelpath),
                                namechanger.normalise_filename(
                                    os.path.basename(parallelpath))))

                            if not os.path.isfile(none_dupe_path):
                                para_fail += 1
                                para_files.add(none_dupe_path)

                    if para_files:
                        print(orig, 'points to non-existing file')
                        for p in para_files:
                            print('\t', p)
                        print()
                else:
                    no_orig_xsl += 1

    print('Total {}, fails {}, {} files with no xsl'.format(total, para_fail,
                                                            no_orig_xsl))
