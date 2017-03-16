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
#   Copyright © 2012-2016 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

"""Pick out parallel files to prestable/converted inside a corpus directory."""


from __future__ import absolute_import, print_function

import argparse
import os
import shutil
from collections import defaultdict

from corpustools import (argparse_version, corpusxmlfile, parallelize, util,
                         versioncontrol)


class ParallelPicker(object):
    """Pick valid parallel files from converted xml files.

    Attributes:
        vcs (versioncontrol.vcs): version control client for the corpus
            directory
        language1_dir (str): the directory where converted files of language1
            are found
        parallel_language (str): three character long language code
        minratio (float): the lowest diff in percent between wordcount in the
            language1 and parallel document that is accepted
        maxratio (float): the highest diff in percent between wordcount in the
            language1 and parallel document that is accepted
        poor_ratio (list of tuple): each tuple contains a pair of filename
            paths and the word count ratio of this pair.
        counter (defaultdict(int)): count various things.
    """

    def __init__(self, language1_dir, parallel_language, minratio, maxratio):
        """Initialise the ParallelPicker class.

        Args:
            language1_dir (str): the directory where the lang1 files exist.
            parallel_language (str): the parallel language where the lang2
                files exist.
            minratio (int): the minimum acceptable ratio of sentences
                between two parallel documents
            maxratio (int): the maximum acceptable ratio of sentences
                between two parallel documents
        """
        self.vcs = versioncontrol.vcs(language1_dir[
            :language1_dir.find('converted/')])
        self.language1_dir = language1_dir
        self.calculate_language1(language1_dir)
        self.parallel_language = parallel_language
        self.minratio = float(minratio)
        self.maxratio = float(maxratio)
        self.poor_ratio = []
        self.counter = defaultdict(int)

    def calculate_language1(self, language1_dir):
        """The language is the part after 'converted/'."""
        converted_pos = language1_dir.find('converted/')
        part_after_converted = language1_dir[
            converted_pos + len('converted/'):]

        if part_after_converted.find('/') == -1:
            self.language1 = part_after_converted
        else:
            self.language1 = part_after_converted[
                :part_after_converted.find('/')]

    def find_lang1_files(self):
        """Find the language1 files.

        Yields:
            corpusxmlfile.CorpusXMLFile
        """
        for root, _, files in os.walk(self.language1_dir):
            for lang1_file in files:
                if lang1_file.endswith('.xml'):
                    yield corpusxmlfile.CorpusXMLFile(
                        os.path.join(root, lang1_file))

    def has_parallel(self, language1_file):
        """Check if the given file has a parallel file.

        Arguments:
            language1_file (corpusxmlfile.CorpusXMLFile): The first file of a
                parallel pair.

        Returns:
            boolean
        """
        parallel_name = language1_file.get_parallel_filename(
            self.parallel_language)
        return parallel_name is not None and os.path.isfile(parallel_name)

    @staticmethod
    def has_sufficient_words(file1, file2):
        """Check if the given file contains more words than the threshold.

        Arguments:
            file1 (corpusxmlfile.CorpusXMLFile): The first file of a parallel
                pair.
            file2 (corpusxmlfile.CorpusXMLFile): The second file of a parallel
                pair.

        Returns:
            boolean
        """
        threshold = 30
        return (file1.word_count is not None and
                int(file1.word_count) > threshold and
                file2.word_count is not None and
                int(file2.word_count) > threshold)

    def has_sufficient_ratio(self, file1, file2):
        """See if the ratio of words is good enough.

        Arguments:
            file1 (corpusxmlfile.CorpusXMLFile): The first file of a parallel
                pair.
            file2 (corpusxmlfile.CorpusXMLFile): The second file of a parallel
                pair.

        Returns:
            boolean
        """
        ratio = float(file1.word_count) / \
            float(file2.word_count) * 100
        if self.minratio < ratio < self.maxratio:
            return True
        else:
            self.poor_ratio.append(
                (file1.name,
                 file1.word_count,
                 file2.name,
                 file2.word_count,
                 ratio))

    def copy_file(self, xml_file):
        """Copy xml_file to prestable/converted.

        Arguments:
            xml_file (corpusxmlfile.CorpusXMLFile): the file that should be
                copied to prestable/converted.
        """
        prestable_dir = xml_file.dirname.replace(
            'converted', 'prestable/converted')

        if not os.path.isdir(prestable_dir):
            with util.ignored(OSError):
                os.makedirs(prestable_dir)

        prestable_name = os.path.join(prestable_dir, xml_file.basename)
        shutil.copy(xml_file.name, prestable_dir)
        self.vcs.add(prestable_name)

        return prestable_name

    def is_valid_pair(self, file1, file2):
        """Check if file1 and file2 is a valid parallel pair.

        Arguments:
            file1 (corpusxmlfile.CorpusXMLFile): The first file of a parallel
                pair.
            file2 (corpusxmlfile.CorpusXMLFile): The second file of a parallel
                pair.

        Returns:
            bool
        """
        return (
            self.has_sufficient_words(
                file1, file2) and
            self.has_sufficient_ratio(
                file1, file2))

    def valid_parallels(self):
        """Pick valid parallel file pairs.

        Yields:
            tuple of corpusxmlfile.CorpusXMLFile
        """
        for language1_file in self.find_lang1_files():
            if self.has_parallel(language1_file):
                self.counter['has_parallel'] += 1
                parallel_file = corpusxmlfile.CorpusXMLFile(
                    language1_file.get_parallel_filename(
                        self.parallel_language))
                if self.is_valid_pair(language1_file, parallel_file):
                    self.counter['good_parallel'] += 1
                    yield (language1_file, parallel_file)

    def copy_valid_parallels(self):
        """Copy valid parallel files from converted to prestable/converted."""
        for file1, file2 in self.valid_parallels():
            prestable_name = self.copy_file(file1)
            self.copy_file(file2)
            self.parallelise(
                prestable_name,
                file2.lang)

    def print_report(self):
        for poor_ratio in self.poor_ratio:
            print('{0}: {1}\n{2}: {3}\nratio: {4}\n'.format(*poor_ratio))

        for key, value in self.counter.items():
            print(key, value)

    def parallelise(self, prestable_name, parallel_lang):
        """Sentence align files.

        Arguments:
            prestable_name (str): path to the converted file in the
                prestable directory
            parallel_lang (str): three character language code of the
                parellel file
        """
        parallelizer = parallelize.ParallelizeTCA2(
            prestable_name,
            parallel_lang,
            quiet=True)
        try:
            tmx = parallelizer.parallelize_files()
        except UserWarning as error:
            print(str(error))
        else:
            tmx.clean_toktmx()
            outfile_existed = os.path.exists(
                parallelizer.outfile_name)
            print('Making {}'.format(
                parallelizer.outfile_name))
            tmx.write_tmx_file(parallelizer.outfile_name)

            self.vcs.add(parallelizer.outfile_name)


def parse_options():
    """Parse the commandline options.

    Returns:
        a list of arguments as parsed by argparse.Argumentparser.
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Pick out parallel files from converted to '
        'prestable/converted.')

    parser.add_argument(
        'language1_dir', help='directory where the files of language1 exist')
    parser.add_argument('-p', '--parallel_language', dest='parallel_language',
                        help='The language where we would like to find '
                        'parallel documents', required=True)
    parser.add_argument('--minratio', dest='minratio',
                        help='The minimum ratio', required=True)
    parser.add_argument('--maxratio', dest='maxratio',
                        help='The maximum ratio', required=True)

    args = parser.parse_args()
    return args


def main():
    """Copy valid parallel pairs from converted to prestable/converted."""
    args = parse_options()

    picker = ParallelPicker(args.language1_dir, args.parallel_language,
                            args.minratio, args.maxratio)
    picker.copy_valid_parallels()
    picker.print_report()
