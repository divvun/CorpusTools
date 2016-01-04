# -*- coding: utf-8 -*-

#
#   This program compares prestable tmx files to files produced by the
#   parallelizer pipeline
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
#   along with program. If not, see <http://www.gnu.org/licenses/>.
#
#   Copyright © 2011-2016 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

from __future__ import print_function

import argparse
import datetime
import difflib
import lxml.etree as etree
import os
import subprocess
import sys
import time

from corpustools import parallelize
from corpustools import util


class TmxComparator(object):

    """A class to compare two tmx-files"""

    def __init__(self, want_tmx, got_tmx):
        self.want_tmx = want_tmx
        self.got_tmx = got_tmx

    def get_lines_in_wantedfile(self):
        """Return the number of lines in the reference doc"""
        return len(self.want_tmx.tmx_to_stringlist())

    def get_number_of_differing_lines(self):
        """Find how many lines differ between to tmx documents.

        Given a unified_diff, find out how many lines in the reference doc
        differs from the doc to be tested. A return value of -1 means that
        the docs are equal
        """
        # Start at -1 because a unified diff always starts with a --- line
        num_diff_lines = -1
        for line in difflib.unified_diff(
                self.want_tmx.tmx_to_stringlist(),
                self.got_tmx.tmx_to_stringlist(), n=0):
            if line[:1] == '-':
                num_diff_lines += 1

        return num_diff_lines

    def get_diff_as_text(self):
        """Return a stringlist containing the diff lines"""
        diff = []
        for line in difflib.unified_diff(
                self.want_tmx.tmx_to_stringlist(),
                self.got_tmx.tmx_to_stringlist(), n=0):
            diff.append(line)

        return diff

    def get_lang_diff_as_text(self, lang):
        """Return a stringlist containing the diff lines"""
        diff = []
        for line in difflib.unified_diff(
                self.want_tmx.lang_to_stringlist(lang),
                self.got_tmx.lang_to_stringlist(lang), n=0):
            diff.append(line + '\n')

        return diff


class TmxGoldstandardTester(object):

    """A class to test the alignment pipeline against the tmx goldstandard"""

    def __init__(self, testresult_filename, dateformat_addition=None):
        """Set the name where the testresults should be written

        Find all goldstandard tmx files
        """
        self.number_of_diff_lines = 0
        self.testresult_writer = TmxTestDataWriter(
            testresult_filename)
        if dateformat_addition is None:
            self.date = self.dateformat()
        else:
            self.date = self.dateformat() + dateformat_addition

    def set_number_of_diff_lines(self, diff_lines):
        """Increase the total number of difflines in this test run"""
        self.number_of_diff_lines += diff_lines

    def get_number_of_diff_lines(self):
        return self.number_of_diff_lines

    def dateformat(self):
        """Get the date and time, 20111209-1234. Used in a testrun element"""
        d = datetime.datetime.fromtimestamp(time.time())

        return d.strftime("%Y%m%d-%H%M")

    def run_test(self):
        # Make a testrun element, which will contain the result of the test
        testrun = self.testresult_writer.make_testrun_element(self.date)

        paralang = ""
        # Go through each tmx goldstandard file
        for want_tmx_file in self.find_goldstandard_tmx_files():
            print("testing {} …".format(want_tmx_file))

            # Calculate the parallel lang, to be used in parallelization
            if want_tmx_file.find('nob2sme') > -1:
                paralang = 'sme'
            else:
                paralang = 'nob'

            # Align files
            self.align_files(testrun, want_tmx_file, paralang, aligner="tca2")

        # All files have been tested, insert this run at the top of the
        # paragstest element
        self.testresult_writer.insert_testrun_element(testrun)
        # Write data to file
        self.testresult_writer.write_paragstesting_data()

    def align_files(self, testrun, want_tmx_file, paralang, aligner):
        """Align files

        Compare the tmx's of the result of this parallellization and
        the tmx of the goldstandard file
        Write the result to a file
        Write the diffs of these to tmx's to a separate file
        """

        # Compute the name of the main file to parallelize
        xml_file = self.compute_xmlfilename(want_tmx_file)

        parallelizer = parallelize.Parallelize(xml_file, paralang)
        got_tmx = parallelizer.parallelize_files()

        # This is the tmx element fetched from the goldstandard file
        want_tmx = parallelize.Tmx(etree.parse(want_tmx_file))

        # Instantiate a comparator with the two tmxes
        comparator = TmxComparator(want_tmx, got_tmx)

        # Make a file_element for our results file
        file_element = self.testresult_writer.make_file_element(
            filelist[0].get_basename(),
            str(comparator.get_lines_in_wantedfile()),
            str(comparator.get_number_of_differing_lines()))

        self.set_number_of_diff_lines(
            comparator.get_number_of_differing_lines())

        # Append the result for this file to the testrun element
        testrun.append(file_element)

        self.write_diff_files(comparator, parallelizer,
                              filelist[0].get_basename())

    def compute_xmlfilename(self, want_tmx_file):
        """Compute the name of the xmlfile which should be aligned"""
        xml_file = want_tmx_file.replace('tmx/goldstandard/', 'converted/')
        xml_file = xml_file.replace('nob2sme', 'nob')
        xml_file = xml_file.replace('sme2nob', 'sme')
        xml_file = xml_file.replace('.toktmx', '.xml')

        return xml_file

    def write_diff_files(self, comparator, parallelizer, filename):
        """Write diffs to a jspwiki file"""
        print("write_diff_files {}".format(filename))
        filename = '{}_{}.jspwiki'.format(filename, self.date)
        dirname = os.path.join(
            os.path.dirname(self.testresult_writer.get_filename()),
            'tca2testing')

        with open(os.path.join(dirname, filename), "w") as diff_file:
            diff_file.write('!!!{}\n'.format(filename))
            diff_file.write("!!TMX diff\n{{{\n")
            diff_file.writelines(comparator.get_diff_as_text())
            diff_file.write("\n}}}\n!! diff\n{{{\n".format(
                parallelizer.get_lang1()))
            diff_file.writelines(comparator.get_lang_diff_as_text(
                parallelizer.get_lang1()))
            diff_file.write("\n}}}\n!!{} diff\n{{{\n".format(
                parallelizer.get_lang2()))
            diff_file.writelines(comparator.get_lang_diff_as_text(
                parallelizer.get_lang2()))
            diff_file.write("\n}}}\n")

    def find_goldstandard_tmx_files(self):
        """Find the goldstandard tmx files, return them as a list"""
        file_list = []
        for root, dirs, files in os.walk(os.path.join(
                os.environ['GTFREE'], 'prestable/toktmx')):
            for f in files:
                if f.endswith('.toktmx'):
                    print(util.lineno(), f)
                    file_list.append(os.path.join(root, f))

        return file_list


class TmxTestDataWriter(object):

    """A class that writes tmx test data to a file"""

    def __init__(self, filename):
        self.filename = filename

        try:
            tree = etree.parse(filename)
            self.set_parags_testing_element(tree.getroot())
        except IOError as error:
            util.note("I/O error({0}): {1}".format(error.errno,
                                                   error.strerror))
            sys.exit(1)

    def get_filename(self):
        return self.filename

    def make_file_element(self, name, gspairs, diffpairs):
        """Make the element file, set the attributes"""
        file_element = etree.Element("file")
        file_element.attrib["name"] = name
        file_element.attrib["gspairs"] = gspairs
        file_element.attrib["diffpairs"] = diffpairs

        return file_element

    def set_parags_testing_element(self, paragstesting):
        self.paragstesting = paragstesting

    def make_testrun_element(self, datetime):
        """Make the testrun element, set the attribute"""
        testrun_element = etree.Element("testrun")
        testrun_element.attrib["datetime"] = datetime

        return testrun_element

    def make_paragstesting_element(self):
        """Make the paragstesting element"""
        paragstesting_element = etree.Element("paragstesting")

        return paragstesting_element

    def insert_testrun_element(self, testrun):
        self.paragstesting.insert(0, testrun)

    def write_paragstesting_data(self):
        """Write the paragstesting data to a file"""
        with open(self.filename, "w") as paragstesting:
            et = etree.ElementTree(self.paragstesting)
            et.write(paragstesting, pretty_print=True, encoding="utf-8",
                     xml_declaration=True)


def parse_options():
    """Parse the command line.

    Expected input is one or more tmx goldstandard files.
    """
    parser = argparse.ArgumentParser(description='Compare goldstandard tmx '
                                     'files to files produced by the '
                                     'parallelizer pipeline.')

    parser.parse_args()


def main():
    parse_options()

    # Set the name of the file to write the test to
    paragstestfile = os.path.join(
        os.environ['GTHOME'], 'techdoc/ling/testruns.paragstesting.xml')

    # Initialize an instance of a tmx test data writer
    tester = TmxGoldstandardTester(paragstestfile)
    tester.run_test()
