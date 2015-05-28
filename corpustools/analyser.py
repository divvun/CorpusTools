# -*- coding: utf-8 -*-

#
#   This file contains a class to analyse text in giellatekno xml format
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
#   Copyright 2013 Børre Gaup <borre.gaup@uit.no>
#

from __future__ import unicode_literals

'''This class makes a dependency analysis of sma, sme and smj files

The pipeline is:
ccat <file> | preprocess (with optionally abbr file) |
lookup <lang dependent files> | lookup2cg |
vislcg3 <disambiguation files> | vislcg3 <function files |
vislcg3 <dependency files>
'''
import os
import sys
import subprocess
import multiprocessing
import lxml.etree as etree
import argparse

import ccat
import parallelize
import argparse_version
import util


class Analyser(object):
    '''A class which can analyse giellatekno xml formatted documents
    using preprocess, lookup, lookup2cg and vislcg3
    '''
    def __init__(self, lang,
                 fstkit,
                 fst_file,
                 disambiguation_analysis_file,
                 function_analysis_file,
                 dependency_analysis_file):
        '''Set the files needed by preprocess, lookup and vislcg3
        '''
        self.lang = lang
        self.xml_printer = ccat.XMLPrinter(lang=lang, all_paragraphs=True)
        self.fstkit = fstkit

        self.raise_unless_exists(fst_file)
        self.raise_unless_exists(disambiguation_analysis_file)
        self.raise_unless_exists(function_analysis_file)
        self.raise_unless_exists(dependency_analysis_file)

        self.fst_file = fst_file
        self.disambiguation_analysis_file = disambiguation_analysis_file
        self.function_analysis_file = function_analysis_file
        self.dependency_analysis_file = dependency_analysis_file

    def raise_unless_exists(self, filename):
        '''Raise an ArgumentError if filename does not exist
        '''
        if not os.path.exists(filename):
            raise(util.ArgumentError('ERROR: {} does not exist'.format(filename)))

    def collect_files(self, converted_dirs):
        '''converted_dirs is a list of directories containing converted
        xml files
        '''
        self.xml_files = []
        for cdir in converted_dirs:
            if os.path.isfile(cdir):
                self.append_file(cdir)
            else:
                for root, dirs, files in os.walk(cdir):
                    for xml_file in files:
                        if self.lang in root and xml_file.endswith('.xml'):
                            self.append_file(os.path.join(root, xml_file))

    def append_file(self, xml_file):
        '''Append xml_file to the xml_files list'''
        try:
            self.xml_files.append(
                unicode(xml_file, sys.getfilesystemencoding()))
        except UnicodeDecodeError:
                print >>sys.stderr, (
                    'Could not handle the file name {}'.format(xml_file))

    @staticmethod
    def makedirs(filename):
        """Make the analysed directory
        """
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError:
            pass

    def ccat(self):
        """Turn an xml formatted file into clean text
        """
        self.xml_printer.parse_file(self.xml_file.get_name())
        text = self.xml_printer.process_file().getvalue()
        if len(text) > 0:
            return text

    def run_external_command(self, command, input):
        '''Run the command with input using subprocess
        '''
        runner = util.ExternalCommandRunner()
        runner.run(command, to_stdin=input)
        self.check_error(command, runner.stderr)

        return runner.stdout

    def preprocess(self):
        """Runs preprocess on the ccat output.
        Returns the output of preprocess
        """
        pre_process_command = util.get_preprocess_command(self.lang)

        text = self.ccat()
        if text is not None:
            return self.run_external_command(pre_process_command, text)

    def lookup(self):
        """Runs lookup on the preprocess output
        Returns the output of preprocess
        """
        lookup_command = ['lookup', '-q', '-flags', 'mbTT', self.fst_file]

        preprocess = self.preprocess()
        if preprocess is not None:
            return self.run_external_command(lookup_command, preprocess)

    def lookup2cg(self):
        """Runs lookup2cg on the lookup output
        Returns the output of lookup2cg
        """
        if self.fstkit == 'hfst':
            text = self.ccat()
            lookup = self.run_external_command('apertium-deshtml', text)
            lookup2cg_command = ['hfst-proc', '--cg', self.fst_file]
        else:
            lookup2cg_command = ['lookup2cg']
            lookup = self.lookup()

        if lookup is not None:
            return self.run_external_command(lookup2cg_command, lookup)

    def disambiguation_analysis(self):
        """Runs vislcg3 on the lookup2cg output

        Produces a disambiguation analysis
        """
        dis_analysis_command = \
            ['vislcg3', '-g', self.disambiguation_analysis_file]

        lookup2cg = self.lookup2cg()
        if lookup2cg is not None:
            self.disambiguation = \
                self.run_external_command(dis_analysis_command, lookup2cg)
        else:
            self.disambiguation = None

    def function_analysis(self):
        """Runs vislcg3 on the disambiguation analysis

        Return the output of this process
        """
        self.disambiguation_analysis()

        function_analysis_command = \
            ['vislcg3', '-g', self.function_analysis_file]

        if self.get_disambiguation() is not None:
            return self.run_external_command(function_analysis_command,
                                             self.get_disambiguation())

    def dependency_analysis(self):
        """Runs vislcg3 on the functions analysis output

        Produces a dependency analysis
        """
        function_analysis = self.function_analysis()

        if function_analysis is not None:
            dep_analysis_command = \
                ['vislcg3', '-g', self.dependency_analysis_file]

            self.dependency = \
                self.run_external_command(dep_analysis_command,
                                          self.function_analysis())

    def get_disambiguation(self):
        '''Get the disambiguation analysis
        '''
        return self.disambiguation

    def get_dependency(self):
        '''Get the dependency analysis
        '''
        return self.dependency

    def get_analysis_xml(self):
        '''Replace the body of the converted document with disambiguation
        and dependency analysis
        '''
        body = etree.Element('body')

        disambiguation = etree.Element('disambiguation')
        disambiguation.text = \
            etree.CDATA(self.get_disambiguation().decode('utf8'))
        body.append(disambiguation)

        dependency = etree.Element('dependency')
        dependency.text = etree.CDATA(self.get_dependency().decode('utf8'))
        body.append(dependency)

        self.xml_file.set_body(body)

    def check_error(self, command, error):
        '''Print errors
        '''
        if error is not None and len(error) > 0:
            print >>sys.stderr, self.xml_file.get_name()
            print >>sys.stderr, command
            print >>sys.stderr, error

    def analyse(self, xml_file):
        '''Analyse a file if it is not ocr'ed
        '''
        self.xml_file = parallelize.CorpusXMLFile(xml_file)
        analysis_xml_name = self.xml_file.get_name().replace('converted/',
                                                             'analysed/')

        if self.xml_file.get_ocr() is None:
            self.dependency_analysis()
            if self.get_disambiguation() is not None:
                self.makedirs(analysis_xml_name)
                self.get_analysis_xml()
                self.xml_file.write(analysis_xml_name)
        else:
            print >>sys.stderr, xml_file, 'is an OCR file and will not be \
            analysed'

    def analyse_in_parallel(self):
        '''Analyse file in parallel
        '''
        pool_size = multiprocessing.cpu_count() * 2
        pool = multiprocessing.Pool(processes=pool_size,)
        pool.map(
            unwrap_self_analyse,
            zip([self]*len(self.xml_files), self.xml_files))
        pool.close()  # no more tasks
        pool.join()   # wrap up current tasks

    def analyse_serially(self):
        '''Analyse files one by one
        '''
        for xml_file in self.xml_files:
            print >>sys.stderr, 'Analysing', xml_file
            self.analyse(xml_file)


def unwrap_self_analyse(arg, **kwarg):
    return Analyser.analyse(*arg, **kwarg)


def parse_options():
    '''Parse the given options
    '''
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Analyse files found in the given directories \
        for the given language using multiple parallel processes.')

    parser.add_argument('lang',
                        help="lang which should be analysed")
    parser.add_argument('--serial',
                        action="store_true",
                        help="When this argument is used files will \
                        be analysed one by one.")
    parser.add_argument('converted_dirs', nargs='+',
                        help="director(y|ies) where the converted files \
                        exist")
    parser.add_argument('-k', '--fstkit',
                        dest='fstkit',
                        choices=['hfst', 'xfst'],
                        default='xfst',
                        help="Finite State Toolkit. Either hfst or xfst (the default).")

    args = parser.parse_args()
    return args


def main():
    '''Analyse files in the given directories
    '''
    args = parse_options()
    util.sanity_check(['preprocess', 'lookup2cg', 'lookup', 'vislcg3'])

    if args.fstkit == 'hfst':
        fst_file = 'src/analyser-disamb-gt-desc.hfstol'
    elif args.fstkit == 'xfst':
        fst_file = 'src/analyser-disamb-gt-desc.xfst'

    try:
        ana = Analyser(args.lang,
                       args.fstkit,
                       fst_file=os.path.join(
                           os.getenv('GTHOME'), 'langs',
                           args.lang, fst_file),
                       disambiguation_analysis_file=os.path.join(
                           os.getenv('GTHOME'), 'langs',
                           args.lang, 'src/syntax/disambiguation.cg3'),
                       function_analysis_file=os.path.join(
                           os.getenv('GTHOME'),
                           'gtcore/gtdshared/smi/src/syntax/korp.cg3'),
                       dependency_analysis_file=os.path.join(
                           os.getenv('GTHOME'),
                           'gtcore/gtdshared/smi/src/syntax/dependency.cg3')
        )
    except util.ArgumentError as a:
        print >>sys.stderr, a.message
        sys.exit(4)

    ana.collect_files(args.converted_dirs)
    if len(ana.xml_files) > 0:
        if args.serial:
            ana.analyse_serially()
        else:
            ana.analyse_in_parallel()
    else:
        print >>sys.stderr, "Did not find any files in", args.converted_dirs
