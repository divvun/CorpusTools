# -*- coding: utf-8 -*-

#
#   This is a program to pick out parallel files to prestable/converted
#   inside a corpus directory
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
#   Copyright © 2012-2015 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

from __future__ import print_function
import os
import argparse
import parallelize
from lxml import etree
from lxml import doctestcompare
import shutil


class ParallelPicker:
    def __init__(self, language1_dir, parallel_language, minratio, maxratio):
        self.language1_dir = language1_dir
        self.calculate_language1(language1_dir)
        self.parallel_language = parallel_language
        self.minratio = minratio
        self.maxratio = maxratio
        self.old_files = []
        self.no_orig = []
        self.no_parallel = []
        self.poor_ratio = []
        self.too_few_words = []
        self.changed_files = []
        self.no_files_translations = []

    def calculate_language1(self, language1_dir):
        """
        The language is the part after 'converted/'
        """
        converted_pos = language1_dir.find('converted/')
        part_after_converted = language1_dir[converted_pos + len('converted/'):]

        if part_after_converted.find('/') == -1:
            self.language1 = part_after_converted
        else:
            self.language1 = part_after_converted[:part_after_converted.find('/')]

    def get_language1(self):
        return self.language1

    def get_parallel_language(self):
        return self.parallel_language

    def add_oldfiles(self, filename):
        """
        Add a filename to the list of files that were in prestable before
        new files were added
        """
        self.old_files.append(filename)

    def add_no_orig(self, filename):
        """
        Add a filename to the list of files in prestable that had no original
        file before new files were added
        """
        self.no_orig.append(filename)

    def add_no_parallel(self, filename):
        """
        Add a filename to the list of files in prestable that had no parallel
        file before new files were added
        """
        self.no_parallel.append(filename)

    def add_no_files_translations(self, language1_file, parallel_file):
        self.no_files_translations.append(language1_file.get_name() + ' ,' + parallel_file.get_name())

    def remove_file(self, filename):
        """
        Remove the given file
        """
        os.remove(filename)

    def check_prestable_file(self, corpus_file):
        """
        Remove a file and its parallel file from prestable if it has no orig file
        Remove a file from prestable if it has no parallel
        If not, add the file name to the list of old files
        """
        # PrintFrame()
        if not self.has_orig(corpus_file):
            self.add_no_orig(corpus_file.get_name())
            self.remove_file(corpus_file.get_name())

            if self.has_parallel(corpus_file):
                self.add_no_orig(corpus_file.get_parallel_filename())
                self.remove_file(corpus_file.get_parallel_filename())

        elif not self.has_parallel(corpus_file):
            self.add_no_parallel(corpus_file.get_name())
            self.remove_file(corpus_file.get_name())

        else:
            self.add_oldfiles(corpus_file.get_name())

    def get_old_file_names(self):
        """
        Get all the filenames in prestable for the language pair that is given to the program
        """

        prestable_dir = self.language1_dir.replace('converted/', 'prestable/converted/')
        # PrintFrame(prestable_dir)

        for root, dirs, files in os.walk(prestable_dir):  # Walk directory tree
            for f in files:
                if f.endswith('.xml'):
                    # PrintFrame(os.path.join(root, f))
                    corpus_file = parallelize.CorpusXMLFile(os.path.join(root, f), self.get_parallel_language())
                    self.check_prestable_file(corpus_file)

        l2prestable_dir = prestable_dir.replace('/' + self.get_language1(), '/' + self.get_parallel_language())

        for root, dirs, files in os.walk(l2prestable_dir):  # Walk directory tree
            for f in files:
                if f.endswith('.xml'):
                    # PrintFrame(os.path.join(root, f))
                    corpus_file = parallelize.CorpusXMLFile(os.path.join(root, f), self.get_language1())
                    self.check_prestable_file(corpus_file)

    def find_lang1_files(self):
        """
        Find the language1 files
        """
        language1_files = []
        for root, dirs, files in os.walk(self.language1_dir):  # Walk directory tree
            for f in files:
                if f.endswith('.xml'):
                    language1_files.append(parallelize.CorpusXMLFile(root + '/' + f, self.parallel_language))

        return language1_files

    def has_parallel(self, language1_file):
        """
        Check if the given file has a parallel file
        """

        return language1_file.get_parallel_filename(self.parallel_language) is not None and os.path.isfile(language1_file.get_parallel_filename(self.parallel_language))

    def has_orig(self, language1_file):
        """
        Check if the given file has an original file
        """

        return language1_file.get_original_filename() is not None and os.path.isfile(language1_file.get_original_filename())

    def has_sufficient_words(self, language1_file, parallel_file):
        """
        Check if the given file contains more words than the threshold
        """

        if (language1_file.get_word_count() is not None and
                float(language1_file.get_word_count()) > 30 and
                parallel_file.get_word_count() is not None and
                float(parallel_file.get_word_count()) > 30):
            return True
        else:
            # PrintFrame(u'Too few words ' + language1_file.get_name() + ' ' + language1_file.get_word_count() + ' ' + parallel_file.get_name() + ' ' + parallel_file.get_word_count())
            self.add_too_few_words(language1_file.get_name(), parallel_file.get_name())
            return False

    def add_too_few_words(self, name1, name2):
        """
        Add the file names of the files with to few words
        """
        self.too_few_words.append(name1 + ' ' + name2)

    def has_sufficient_ratio(self, file1, file2):
        """
        See if the ratio of words is good enough
        """

        ratio = float(file1.get_word_count())/float(file2.get_word_count())*100

        if ratio > float(self.minratio) and ratio < float(self.maxratio):
            return True
        else:
            self.add_poor_ratio(file1.get_name(), file2.get_name(), ratio)
            return False

    def add_poor_ratio(self, name1, name2, ratio):
        """
        Add filenames to the poor_ratio list
        """
        self.poor_ratio.append(name1 + ',' + name2 + ',' + repr(ratio))

    def add_changed_file(self, corpus_file):
        self.changed_files.append(corpus_file.get_name())
        prestable_filename = corpus_file.get_name().replace('converted/', 'prestable/converted/')
        print(prestable_filename)

        if prestable_filename in self.old_files:
            self.old_files.remove(prestable_filename)

    def both_files_translated_from(self, parallel_file, language1_file):

        if (parallel_file.get_translated_from() == language1_file.get_lang() and
                language1_file.get_translated_from() == self.parallel_language):
            # print ("Both files claim to be translations of the other")
            self.add_both_files_translated(language1_file, parallel_file)
            return True
        else:
            return False

    def one_file_translated_from(self, language1_file, parallel_file):
        if (language1_file.get_translated_from() == self.parallel_language or
                parallel_file.get_translated_from() == language1_file.get_lang()):
            if self.valid_diff(language1_file, parallel_file.get_lang()):
                self.add_changed_file(language1_file)
                self.copy_file(language1_file)

            if self.valid_diff(parallel_file, language1_file.get_lang()):
                self.add_changed_file(parallel_file)
                self.copy_file(parallel_file)

        else:
            # print ("None of the files are translations of the other", language1_file.get_name(), parallel_file.get_name())
            self.add_no_files_translations(language1_file, parallel_file)

    def traverse_files(self):
        """
        Go through all files
        """
        for language1_file in self.find_lang1_files():
            # print('.', end='')

            if self.has_parallel(language1_file):

                parallel_file = parallelize.CorpusXMLFile(language1_file.get_parallel_filename(), language1_file.get_lang())

                # PrintFrame(language1_file.get_name() + ' ' + language1_file.get_word_count())
                # PrintFrame(parallel_file.get_name() + ' ' + parallel_file.get_word_count())

                if (self.has_sufficient_words(language1_file, parallel_file) and
                        self.has_sufficient_ratio(language1_file, parallel_file)):
                    if not self.both_files_translated_from(parallel_file, language1_file):
                        self.one_file_translated_from(language1_file, parallel_file)

    def valid_diff(self, converted_file, parallel_language):
        """
        Check if there are differences between the files in
        converted and prestable/converted
        """

        is_valid_diff = True

        prestable_filename = converted_file.get_name().replace('converted/', 'prestable/converted/')

        if os.path.isfile(prestable_filename):
            prestable_file = parallelize.CorpusXMLFile(prestable_filename, parallel_language)

            prestable_file.remove_version()
            converted_file.remove_version()

            # check_diff sets is_valid_diff either True or False
            # PrintFrame(converted_file.get_name())
            # PrintFrame(prestable_file.get_name())
            is_valid_diff = self.check_diff(converted_file.get_etree(), prestable_file.get_etree())

        return is_valid_diff

    def check_diff(self, etree1, etree2):
        """
            Return true if there is a difference between the
            content of etree1 and etree2
        """
        doc1 = etree.tostring(etree1)
        doc2 = etree.tostring(etree2)

        checker = doctestcompare.LXMLOutputChecker()

        if not checker.check_output(doc1, doc2, 0):
            return True
        else:
            return False

    def copy_file(self, xml_file):
        """
        Copy xml_file to prestable/converted
        """
        prestable_dir = xml_file.getDirname().replace('converted/', 'prestable/converted/')

        if not os.path.isdir(prestable_dir):
            try:
                os.makedirs(prestable_dir)
            except os.error:
                pass
                # print ("couldn't make", prestable_dir)

        shutil.copy(xml_file.get_name(), prestable_dir)

    def treat_lists(self):
        for old_file in self.old_files:
            self.remove_file(old_file)

        print(len(self.old_files), 'of the original prestable files were deleted')
        print(len(self.no_orig), 'of the original prestable files had no original file')
        print(len(self.no_parallel), 'of the original prestable files had no original file')
        print(len(self.poor_ratio), 'pairs of the candidate files had too bad ratio')
        print(len(self.too_few_words), 'pairs of the candidate files had too few words')
        print(len(self.changed_files), 'of the candidate files were copied into prestable')
        print(len(self.no_files_translations), 'pairs of the candidate files had no translated_from entry')

    def write_log(self):
        log_file = open('pick.log', 'w')

        log_file.write('old_files' + '\n')
        for old_file in self.old_files:
            log_file.write(old_file + '\n')
        log_file.write('\n')

        log_file.close()


def parse_options():
    parser = argparse.ArgumentParser(description='Pick out parallel files from converted to prestable/converted.')

    parser.add_argument('language1_dir', help="directory where the files of language1 exist")
    parser.add_argument('-p', '--parallel_language', dest='parallel_language', help="The language where we would like to find parallel documents", required=True)
    parser.add_argument('--minratio', dest='minratio', help="The minimum ratio", required=True)
    parser.add_argument('--maxratio', dest='maxratio', help="The maximum ratio", required=True)

    args = parser.parse_args()
    return args


def main():
    args = parse_options()

    language1_dir = args.language1_dir
    parallel_language = args.parallel_language
    minratio = args.minratio
    maxratio = args.maxratio

    pp = ParallelPicker(language1_dir, parallel_language, minratio, maxratio)
    pp.get_old_file_names()
    pp.traverse_files()
    pp.treat_lists()
    pp.write_log()
