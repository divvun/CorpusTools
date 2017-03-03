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

from corpustools import argparse_version, parallelize, util, versioncontrol


class ParallelPicker(object):
    """Pick parallel files from converted xml files.

    Attributes:
        language1_dir (str): the directory where converted files of language1
            are found
        parallel_language (str):
        parellel_files (int): number of parallel files
        copied_files (int): number of copied files
        minratio (float): the lowest diff in percent between wordcount in the
            language1 and parallel document that is accepted
        maxratio (float): the highest diff in percent between wordcount in the
            language1 and parallel document that is accepted
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
        self.vcs =versioncontrol.vcs(language1_dir[
            :language1_dir.find('converted/')])
        self.language1_dir = language1_dir
        self.calculate_language1(language1_dir)
        self.parallel_language = parallel_language
        self.minratio = float(minratio)
        self.maxratio = float(maxratio)
        self.poor_ratio = []

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
            parallelize.CorpusXMLFile
        """
        for root, _, files in os.walk(self.language1_dir):
            for lang1_file in files:
                if lang1_file.endswith('.xml'):
                    yield parallelize.CorpusXMLFile(
                        os.path.join(root, lang1_file))

    def has_parallel(self, language1_file):
        """Check if the given file has a parallel file.

        Arguments:
            language1_file (parallelize.CorpusXMLFile): The first file of a
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
            file1 (parallelize.CorpusXMLFile): The first file of a parallel
                pair.
            file2 (parallelize.CorpusXMLFile): The second file of a parallel
                pair.

        Returns:
            boolean
        """
        if (file1.word_count is not None and
                int(file1.word_count) > 30 and
                file2.word_count is not None and
                int(file2.word_count) > 30):
            return True

    def has_sufficient_ratio(self, file1, file2):
        """See if the ratio of words is good enough.

        Arguments:
            file1 (parallelize.CorpusXMLFile): The first file of a parallel
                pair.
            file2 (parallelize.CorpusXMLFile): The second file of a parallel
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
            xml_file (parallelize.CorpusXMLFile): the file that should be
                copied to prestable/converted.
        """
        prestable_dir = xml_file.dirname.replace(
            'converted', 'prestable/converted')

        if not os.path.isdir(prestable_dir):
            with util.ignored(OSError):
                os.makedirs(prestable_dir)

        prestable_name = os.path.join(prestable_dir, xml_file.basename)
        if not os.path.exists(prestable_name):
            shutil.copy(xml_file.name, prestable_dir)
            self.vcs.add(prestable_name)
        else:
            shutil.copy(xml_file.name, prestable_dir)

        return prestable_name

    def copy_valid_parallels(self):
        """Copy valid parallel files from converted to prestable/converted."""
        counter = defaultdict(int)
        for language1_file in self.find_lang1_files():
            if self.has_parallel(language1_file):
                counter['has_parallel'] += 1
                parallel_file = parallelize.CorpusXMLFile(
                    language1_file.get_parallel_filename(
                        self.parallel_language))

                if self.has_sufficient_words(language1_file, parallel_file):
                    if self.has_sufficient_ratio(language1_file,
                                                 parallel_file):
                        counter['good_parallel'] += 1
                        prestable_name = self.copy_file(language1_file)
                        self.copy_file(parallel_file)
                        parallelizer = parallelize.ParallelizeTCA2(
                            prestable_name,
                            parallel_file.lang,
                            quiet=True)
                        try:
                            tmx = parallelizer.parallelize_files()
                        except UserWarning as error:
                            print(str(error))
                        else:
                            tmx.clean_toktmx()
                            outfile_existed = os.path.exists(parallelizer.outfile_name)
                            print('Making {}'.format(parallelizer.outfile_name))
                            tmx.write_tmx_file(parallelizer.outfile_name)
                            if not outfile_existed:
                                self.vcs.add(parallelizer.outfile_name)

        for poor_ratio in self.poor_ratio:
            print('{0}: {1}\n{2}: {3}\nratio: {4}\n'.format(*poor_ratio))

        for key, value in counter.items():
            print(key, value)


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
