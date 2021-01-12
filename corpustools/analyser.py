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
#   Copyright © 2013-2020 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Classes and functions to do syntactic analysis on giellatekno xml docs."""

from __future__ import absolute_import, print_function, unicode_literals

import argparse
import multiprocessing
import os
import sys

import lxml.etree as etree

from corpustools import argparse_version, ccat, corpusxmlfile, modes, util


class Analyser(object):
    """This class makes a dependency analysis of giella xml files.

    Attributes:
        lang (str): the language of the input.
        modename (str): the pipeline that should be used to analyse the
            files. The pipeline definitions are found in the file
            xml/modes.xml.
        giella_prefix: Set this variable if the installed giella files
            are not found in the standard places.
    """

    def __init__(self, lang, modename, giella_prefix=None):
        """Set the files needed by preprocess, lookup and vislcg3.

        Args:
            lang (str): language the analyser can analyse
            pipeline_name (str): the name of the pipeline which will be used to
                analyse files
        """
        self.lang = lang
        self.xml_printer = ccat.XMLPrinter(lang=lang, all_paragraphs=True)
        self.modename = modename
        self.giella_prefix = giella_prefix

    def collect_files(self, converted_dirs):
        """Collect converted files."""
        self.xml_files = []
        for cdir in converted_dirs:
            if os.path.isfile(cdir):
                self.append_file(cdir)
            else:
                for root, _, files in os.walk(cdir):
                    for xml_file in files:
                        if self.lang in root and xml_file.endswith('.xml'):
                            self.append_file(os.path.join(root, xml_file))

    def append_file(self, xml_file):
        """Append xml_file to the xml_files list."""
        self.xml_files.append(xml_file)

    def ccat(self):
        """Turn an xml formatted file into clean text."""
        self.xml_printer.parse_file(self.xml_file.name)
        text = self.xml_printer.process_file().getvalue()
        if text:
            return text
        else:
            raise UserWarning('Empty file {}'.format(self.xml_file.name))

    def dependency_analysis(self):
        """Insert disambiguation and dependency analysis into the body."""
        pipeline = modes.Pipeline(self.modename, self.lang, self.giella_prefix)
        pipeline.sanity_check()

        body = etree.Element('body')

        dependency = etree.Element('dependency')
        dependency.text = etree.CDATA(pipeline.run(self.ccat().encode('utf8')))
        body.append(dependency)

        self.xml_file.set_body(body)

    def analyse(self, xml_file):
        """Analyse a file if it is not ocr'ed."""
        try:
            self.xml_file = corpusxmlfile.CorpusXMLFile(xml_file)
            analysis_xml_name = self.xml_file.name.replace(
                'converted/', 'analysed/{}/'.format(self.modename))

            if self.xml_file.ocr is None:
                self.dependency_analysis()
                with util.ignored(OSError):
                    os.makedirs(os.path.dirname(analysis_xml_name))
                self.xml_file.write(analysis_xml_name)
            else:
                print(
                    xml_file,
                    'is an OCR file and will not be analysed',
                    file=sys.stderr)
        except (etree.XMLSyntaxError, UserWarning) as error:
            print('Can not parse', xml_file, file=sys.stderr)
            print('The error was:', str(error), file=sys.stderr)

    def analyse_in_parallel(self):
        """Analyse file in parallel."""
        pool_size = multiprocessing.cpu_count() * 2
        pool = multiprocessing.Pool(processes=pool_size, )
        pool.map(unwrap_self_analyse,
                 list(zip([self] * len(self.xml_files), self.xml_files)))
        pool.close()  # no more tasks
        pool.join()  # wrap up current tasks

    def analyse_serially(self):
        """Analyse files one by one."""
        print('Starting the analysis of {} files'.format(len(self.xml_files)))

        fileno = 0
        for xml_file in self.xml_files:
            fileno += 1
            # print some ugly banner cos i want to see progress on local
            # batch job
            print('*' * 79, file=sys.stderr)
            print('Analysing {} [{} of {}]'.format(xml_file, fileno,
                                                   len(self.xml_files),
                  file=sys.stderr))
            print('*' * 79, file=sys.stderr)
            self.analyse(xml_file)


def unwrap_self_analyse(arg, **kwarg):
    """Unpack self from the arguments and call convert again.

    This is due to how multiprocess works:
    http://www.rueckstiess.net/research/snippets/show/ca1d7d90
    """
    return Analyser.analyse(*arg, **kwarg)


def parse_options():
    """Parse the given options."""
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Analyse files found in the given directories \
        for the given language using multiple parallel processes.')

    parser.add_argument('lang', help="lang which should be analysed")
    parser.add_argument(
        '--serial',
        action="store_true",
        help="When this argument is used files will \
                        be analysed one by one.")
    parser.add_argument(
        'converted_dirs',
        nargs='+',
        help="director(y|ies) where the converted files \
                        exist")
    parser.add_argument(
        '-k',
        '--fstkit',
        choices=['hfst', 'xfst', 'trace-smegram', 'trace-smegram-dev',
                 'hfst_thirties', 'hfst_eighties'],
        default='xfst',
        help='Finite State Toolkit. '
        'Either hfst or xfst (the default).')

    args = parser.parse_args()
    return args


def main():
    """Analyse files in the given directories."""
    args = parse_options()

    ana = Analyser(args.lang, args.fstkit)

    ana.collect_files(args.converted_dirs)

    if ana.xml_files:
        try:
            if args.serial:
                ana.analyse_serially()
            else:
                ana.analyse_in_parallel()
        except util.ArgumentError as error:
            print(
                'Cannot do analysis for {}\n{}'.format(args.lang, str(error)),
                file=sys.stderr)
            sys.exit(1)
    else:
        print(
            "Did not find any files in", args.converted_dirs, file=sys.stderr)
