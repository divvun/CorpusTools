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
#   Copyright © 2018-2020 The University of Tromsø &
#                    the Norwegian Sámi Parliament
#   http://divvun.no & http://giellatekno.uit.no
#
"""Classes and functions to make corpus training files."""

from __future__ import absolute_import, print_function, unicode_literals

import argparse
import io
import os
import sys
from shutil import copy

import regex

from corpustools import argparse_version, ccat, util


class TrainingCorpusMaker(object):
    """Turn analysed giella xml files into training corpus.

    Filter out all sentences containing words unknown to the
    giella fst analysers.

    Attributes:
        only_words: regex catching word made up of letters.
        xml_printer (ccat.XMLPrinter): extracts the dependency analysis
            from the giella xml files.
        lang (str): the language of the training corpus.
    """

    only_words = regex.compile(r'\p{L}+')
    xml_printer = ccat.XMLPrinter(dependency=True)

    def __init__(self, lang):
        """Initialise the TrainingCorpusMaker class."""
        self.lang = lang

    def parse_dependency(self, text):
        """Parse the dependency element found in a giella xml file.

        Args:
            text (str): contains the dependency element of a giella xml file.

        Yields:
            str: a sentence containing only words known to the giella fst
                analysers, that contain at least a word as identified by
                the only_words regex.
        """
        sentence_buffer = []
        uff_buffer = []
        for line in io.StringIO(text):
            line = line.rstrip()
            if line == ':' or line == ':\\n':
                sentence_buffer.append(' ')
            elif line.startswith(':'):
                uff_buffer.append(line)
            elif line.startswith('"'):
                sentence_buffer.append(line[2:-2])
            elif 'CLB' in line:
                if not ('".' not in line and '"¶"' not in line
                        and '"?"' not in line and '"!"' not in line
                        and '"…"' not in line):
                    if uff_buffer:
                        for uff in uff_buffer:
                            util.print_frame(uff)
                    else:
                        sentence_line = ''.join(sentence_buffer).replace(
                            '¶', '').strip()
                        if self.only_words.search(sentence_line):
                            yield sentence_line
                    uff_buffer[:] = []
                    sentence_buffer[:] = []
            elif '" ?' in line:
                uff_buffer.append(line)

    def file_to_sentences(self, filename):
        """Turn a giella xml into a list of sentences.

        Args:
            filename (str): name of the giella xml file containing a
                dependency element.

        Returns:
            list of str
        """
        self.xml_printer.parse_file(filename)
        text = self.xml_printer.process_file().getvalue()
        if text.strip():
            return [
                sentence for sentence in self.parse_dependency(text)
                if sentence
            ]
        else:
            return []

    def analysed_files(self):
        """Find analysed files.

        Yields:
            str: filename of an analysed file.
        """
        for corpus in [
                os.path.join(os.getenv('GTFREE'), 'analysed', self.lang),
                os.path.join(os.getenv('GTBOUND'), 'analysed', self.lang)
        ]:
            for root, _, files in os.walk(corpus):
                for file_ in files:
                    yield os.path.join(root, file_)

    def make_corpus_files(self):
        """Make .txt files from .xml files.

        The .txt files contain only sentences with words known to the
        giella fsts.
        """
        for analysed_file in self.analysed_files():
            if analysed_file.endswith('.xml'):
                with open(analysed_file.replace('.xml', '.txt'),
                          'w') as txt_stream:
                    txt_stream.write('\n'.join(
                        self.file_to_sentences(analysed_file)))
                    txt_stream.write('\n')

    def pytextcat_corpus(self):
        """Turn the free and bound corpus into a pytextcat training corpus."""
        corpus_dir = os.path.join('pytextcat', self.lang)
        with util.ignored(OSError):
            os.makedirs(corpus_dir)

        with open('{}.txt'.format(os.path.join(corpus_dir, self.lang)),
                  'w') as corpusfile:
            for analysed_file in self.analysed_files():
                if analysed_file.endswith('.txt'):
                    with open(analysed_file) as analysed:
                        corpusfile.write(analysed.read())

    def langid_corpus(self):
        """Turn the free and bound corpus into a langid training corpus."""
        for analysed_file in self.analysed_files():
            if analysed_file.endswith('.txt'):
                langid_dir = 'langid/{}/{}'.format(
                    util.split_path(analysed_file).genre, self.lang)
                with util.ignored(OSError):
                    os.makedirs(langid_dir)
                copy(analysed_file, langid_dir)


def parse_options():
    """Parse the options given to the program."""
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Make training corpus from analysed giella xml files.\n'
        'Sentences with words unknown for the giella fsts are not included.')
    parser.add_argument(
        'langs',
        nargs='+',
        help='The languages to make a training corpus for.')

    return parser.parse_args()


def main():
    """Turn the corpus into a pytextcat training corpus."""
    args = parse_options()

    for lang in args.langs:
        sentence_maker = TrainingCorpusMaker(lang)
        sentence_maker.make_corpus_files()
        sentence_maker.pytextcat_corpus()
        sentence_maker.langid_corpus()

    print('Now you will find training corpus for pytextcat and langid '
          'in the pytextcat and langid directories in the current directory.')
