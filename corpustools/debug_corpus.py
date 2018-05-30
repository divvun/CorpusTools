# -*- coding: utf-8 -*-

#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this file. If not, see <http://www.gnu.org/licenses/>.
#
#   Copyright © 2015-2018 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Find out why conversion or analysis stops when ran in multiprocess mode."""

from __future__ import absolute_import, print_function, unicode_literals

import argparse
import os

from corpustools import analyser, argparse_version, converter


def parse_args():
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Run this script on some directory in freecorpus or '
        'boundcorpus to find out why files are not converted or analysed')
    parser.add_argument('lang', help="The language that you would like to test")
    parser.add_argument(
        'dirs', nargs='+', help="A directory containing original corpus files")

    return parser.parse_args()


def main():
    args = parse_args()

    cm = converter.ConverterManager(False)

    fst_file = 'src/analyser-disamb-gt-desc.xfst'
    ana = analyser.Analyser(
        'sme',
        'xfst',
        fst_file=os.path.join(
            os.getenv('GTHOME'), 'langs', args.lang, fst_file),
        disambiguation_analysis_file=os.path.join(
            os.getenv('GTHOME'), 'langs', args.lang,
            'src/syntax/disambiguation.cg3'),
        function_analysis_file=os.path.join(
            os.getenv('GTHOME'), 'giella-shared/smi/src/syntax/korp.cg3'),
        dependency_analysis_file=os.path.join(
            os.getenv('GTHOME'), 'giella-shared/smi/src/syntax/dependency.cg3'))

    ana.xml_files = []
    for directory in args.dirs:
        orig = 0
        converted = 0
        analysed = 0
        for root, dirs, files in os.walk(directory):
            for f in files:
                if f.endswith('.xsl'):
                    orig += 1

                    orig_f = os.path.abspath(os.path.join(root, f[:-4]))
                    converted_f = orig_f.replace('orig/', 'converted/') + '.xml'
                    analysed_f = converted_f.replace('converted/', 'analysed/')

                    if not os.path.exists(converted_f):
                        cm.FILES.append(orig_f + '.xsl')
                        print(orig_f)
                        print('\t' + converted_f)
                        print('\t' + analysed_f)
                        print()
                    elif not os.path.exists(analysed_f):
                        converted += 1
                        ana.xml_files.append(converted_f)
                        print(orig_f)
                        print('\t' + analysed_f)
                        print()
                    else:
                        converted += 1
                        analysed += 1

        print(directory, orig, converted, analysed)
        print(orig - converted, converted - analysed)

    cm.convert_serially()
    ana.analyse_serially()
