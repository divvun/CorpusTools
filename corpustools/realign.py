# -*- coding: utf-8 -*-

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
#   Copyright © 2017 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Sentence align a given file anew."""

from __future__ import absolute_import, print_function

import argparse
import os
import shutil

from corpustools import (argparse_version, convertermanager, corpuspath,
                         parallelize)


def print_filename(corpus_path):
    """Print interesting filenames for doing sentence alignment.

    Arguments:
        corpus_path (corpuspath.CorpusPath): filenames
    """
    print('\toriginal: {}\n\tmetatada: {}\n\tconverted: {}'.format(
        corpus_path.orig, corpus_path.xsl, corpus_path.converted))


def print_filenames(corpus_path1, corpus_path2):
    """Print interesting filenames for doing sentence alignment.

    Arguments:
        corpus_path1 (corpuspath.CorpusPath): filenames for the lang1 file.
        corpus_path2 (corpuspath.CorpusPath): filenames for the lang2 file.
    """
    print('\nLanguage 1 filenames:')
    print_filename(corpus_path1)
    print('\nLanguage 2 filenames:')
    print_filename(corpus_path2)


def calculate_paths(tmxhtml):
    """Calculate paths, given a file from the command line.

    Arguments:
        tmxhtml (str): path to a .tmx or a .tmx.html file

    Returns:
        tuple of corpuspath.CorpusPath
    """
    path = tmxhtml[:-5] if tmxhtml.endswith('.tmx.html') else \
        tmxhtml
    corpus_path1 = corpuspath.CorpusPath(path)
    lang2 = corpus_path1.split_on_module(path)[2].split('/')[0].split('2')[1]
    corpus_path2 = corpuspath.CorpusPath(corpus_path1.parallel(lang2))

    return corpus_path1, corpus_path2


def convert_and_copy(corpus_path1, corpus_path2):
    """Reconvert and copy files to prestable/converted.

    Arguments:
        corpus_path1 (corpuspath.CorpusPath): A CorpusPath representing the
            lang1 file that should be reconverted.
        corpus_path2 (corpuspath.CorpusPath): A CorpusPath representing the
            lang2 file that should be reconverted.
    """
    for corpus_path in [corpus_path1, corpus_path2]:
        if os.path.exists(corpus_path.converted):
            os.remove(corpus_path.converted)
        if os.path.exists(corpus_path.prestable_converted):
            os.remove(corpus_path.prestable_converted)

    convertermanager.sanity_check()
    converter_manager = convertermanager.ConverterManager(
        write_intermediate=False, goldstandard=False)
    converter_manager.collect_files([corpus_path1.orig, corpus_path2.orig])
    converter_manager.convert_serially()

    for corpus_path in [corpus_path1, corpus_path2]:
        shutil.copy(corpus_path.converted, corpus_path.prestable_converted)


def parse_options():
    """Parse the commandline options.

    Returns:
        a list of arguments as parsed by argparse.Argumentparser.
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Sentence align a given file anew.')
    parser.add_argument(
        u'--files',
        action=u'store_true',
        help=u'Show the interesting filenames '
        'that are needed for improving sentence '
        'alignment.')
    parser.add_argument(
        u'--convert',
        action=u'store_true',
        help=u'Only convert the original files '
        'that are the source of the .tmx.html file. '
        'This is useful when improving the output of '
        'the converted files.')
    parser.add_argument('tmxhtml', help="The tmx.html file to realign.")

    args = parser.parse_args()
    return args


def main():
    """Sentence align a given file anew."""
    args = parse_options()

    corpus_path1, corpus_path2 = calculate_paths(args.tmxhtml)

    if args.files:
        print_filenames(corpus_path1, corpus_path2)
        raise SystemExit()

    try:
        if args.convert:
            convert_and_copy(corpus_path1, corpus_path2)
            print_filenames(corpus_path1, corpus_path2)
            raise SystemExit()
    except Exception:
        raise SystemExit(1)

    parallelize.parallelise_file(
        corpus_path1.prestable_converted,
        corpus_path2.metadata.get_variable('mainlang'),
        dictionary=None,
        quiet=True,
        aligner='tca2',
        stdout=False,
        force=True)
    print_filenames(corpus_path1, corpus_path2)
