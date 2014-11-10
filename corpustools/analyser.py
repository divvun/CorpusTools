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

from corpustools import ccat


here = os.path.dirname(__file__)
version = os.path.join(here, '_version.py')
scope = {}
exec(open(version).read(), scope)
version = scope['VERSION']


class Analyser(object):
    '''A class which can analyse giellatekno xml formatted documents
    using preprocess, lookup, lookup2cg and vislcg3
    '''
    def __init__(self, lang):
        self.lang = lang
        self.xml_printer = ccat.XMLPrinter(lang=lang, all_paragraphs=True)

    def exit_on_error(self, filename):
        '''Exit the process if filename does not exist
        '''
        error = False

        if filename is None:
            print >>sys.stderr, filename, 'is not defined'
            error = True
        elif not os.path.exists(filename):
            print >>sys.stderr, filename, 'does not exist'
            error = True

        if error:
            sys.exit(4)

    def set_analysis_files(self,
                           abbr_file=None,
                           fst_file=None,
                           disambiguation_analysis_file=None,
                           function_analysis_file=None,
                           dependency_analysis_file=None):
        '''Set the files needed by preprocess, lookup and vislcg3
        '''
        if self.lang in ['sma', 'sme', 'smj']:
            self.exit_on_error(abbr_file)
        self.exit_on_error(fst_file)
        self.exit_on_error(disambiguation_analysis_file)
        self.exit_on_error(function_analysis_file)
        self.exit_on_error(dependency_analysis_file)

        self.abbr_file = abbr_file
        self.fst_file = fst_file
        self.disambiguation_analysis_file = disambiguation_analysis_file
        self.function_analysis_file = function_analysis_file
        self.dependency_analysis_file = dependency_analysis_file

    def set_corr_file(self, corr_file):
        '''Set the correct file used by preprocess
        '''
        self.exit_on_error(corr_file)
        self.corr_file = corr_file

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
                print >>sys.stderr, 'Could not handle the file name', xml_file

    def makedirs(self):
        u"""Make the analysed directory
        """
        try:
            os.makedirs(os.path.dirname(self.analysis_xml_file))
        except OSError:
            pass

    def get_lang(self):
        u"""
        @brief Get the mainlang from the xml file

        :returns: the language as set in the xml file
        """
        lang = u'{http://www.w3.org/XML/1998/namespace}lang'
        if self.etree.getroot().attrib[lang] is not None:
            return self.etree.getroot().\
                attrib[lang]
        else:
            return u'none'

    def get_genre(self):
        u"""
        @brief Get the genre from the xml file

        :returns: the genre as set in the xml file
        """
        if self.etree.getroot().find(u".//genre") is not None:
            return self.etree.getroot().find(u".//genre").attrib[u"code"]
        else:
            return u'none'

    def get_ocr(self):
        u"""
        @brief Check if the ocr element exists

        :returns: the ocr element or None
        """
        return self.etree.getroot().find(u".//ocr")

    def get_translatedfrom(self):
        u"""
        @brief Get the translated_from value from the xml file

        :returns: the value of translated_from as set in the xml file
        """
        if self.etree.getroot().find(u".//translated_from") is not None:
            return self.etree.getroot().find(u".//translated_from").\
                attrib[u"{http://www.w3.org/XML/1998/namespace}lang"]
        else:
            return u'none'

    def calculate_filenames(self, xml_file):
        u"""Set the names of the analysis files
        """
        self.dependency_analysis_name = xml_file.replace(u'/converted/',
                                                         u'/analysed')

    def ccat(self):
        u"""Turn an xml formatted file into clean text
        """
        self.xml_printer.parse_file(self.xml_file)
        text = self.xml_printer.process_file().getvalue()
        if len(text) > 0:
            return text

    def run_external_command(self, command, input):
        '''Run the command with input using subprocess
        '''
        subp = subprocess.Popen(command,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        (output, error) = subp.communicate(input)
        self.check_error(command, error)

        return output

    def preprocess(self):
        u"""Runs preprocess on the ccat output.
        Returns the output of preprocess
        """
        pre_process_command = [u'preprocess']

        if self.abbr_file is not None:
            pre_process_command.append(u'--abbr=' + self.abbr_file)

        text = self.ccat()
        if text is not None:
            return self.run_external_command(pre_process_command, text)

    def lookup(self):
        u"""Runs lookup on the preprocess output
        Returns the output of preprocess
        """
        lookup_command = [u'lookup', u'-q', u'-flags', u'mbTT', self.fst_file]

        preprocess = self.preprocess()
        if preprocess is not None:
            return self.run_external_command(lookup_command, preprocess)

    def lookup2cg(self):
        u"""Runs lookup2cg on the lookup output
        Returns the output of lookup2cg
        """
        lookup2cg_command = [u'lookup2cg']

        lookup = self.lookup()
        if lookup is not None:
            return self.run_external_command(lookup2cg_command, lookup)

    def disambiguation_analysis(self):
        u"""Runs vislcg3 on the lookup2cg output

        Produces a disambiguation analysis
        """
        dis_analysis_command = \
            [u'vislcg3', u'-g', self.disambiguation_analysis_file]

        lookup2cg = self.lookup2cg()
        if lookup2cg is not None:
            self.disambiguation = \
                self.run_external_command(dis_analysis_command, lookup2cg)
        else:
            self.disambiguation = None

    def function_analysis(self):
        u"""Runs vislcg3 on the disambiguation analysis

        Return the output of this process
        """
        self.disambiguation_analysis()

        function_analysis_command = \
            [u'vislcg3', u'-g', self.function_analysis_file]

        if self.get_disambiguation() is not None:
            return self.run_external_command(function_analysis_command,
                                             self.get_disambiguation())

    def dependency_analysis(self):
        u"""Runs vislcg3 on the functions analysis output

        Produces a dependency analysis
        """
        function_analysis = self.function_analysis()

        if function_analysis is not None:
            dep_analysis_command = \
                [u'vislcg3', u'-g', self.dependency_analysis_file]

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
        body = etree.Element(u'body')

        disambiguation = etree.Element(u'disambiguation')
        disambiguation.text = self.get_disambiguation().decode(u'utf8')
        body.append(disambiguation)

        dependency = etree.Element(u'dependency')
        dependency.text = self.get_dependency().decode(u'utf8')
        body.append(dependency)

        oldbody = self.etree.find(u'.//body')
        oldbody.getparent().replace(oldbody, body)

        return self.etree

    def check_error(self, command, error):
        '''Print errors
        '''
        if error is not None and len(error) > 0:
            print >>sys.stderr, self.xml_file
            print >>sys.stderr, command
            print >>sys.stderr, error

    def analyse(self, xml_file):
        u'''Analyse a file if it is not ocr'ed
        '''
        self.xml_file = xml_file
        self.analysis_xml_file = self.xml_file.replace(u'converted/',
                                                       u'analysed/')
        self.etree = etree.parse(xml_file)
        self.calculate_filenames(xml_file)

        if self.get_ocr() is None:
            self.dependency_analysis()
            if self.get_disambiguation() is not None:
                self.makedirs()
                self.get_analysis_xml().write(
                    self.analysis_xml_file,
                    encoding=u'utf8',
                    xml_declaration=True)
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
            print >>sys.stderr, u'Analysing', xml_file
            self.analyse(xml_file)


def unwrap_self_analyse(arg, **kwarg):
    return Analyser.analyse(*arg, **kwarg)


def sanity_check(program_list):
    u"""Look for programs and files that are needed to do the analysis.
    If they don't exist, quit the program
    """
    for program in program_list:
        if which(program) is False:
            sys.stderr.write(program)
            sys.stderr.write(u" isn't found in path\n")
            sys.stderr.write(u'You must install it.\n')
            sys.exit(2)


def which(name):
    u"""Get the output of the unix command which.
    Return false if empty, true if non-empty
    """
    try:
        subprocess.check_output([u'which', name])
        return True
    except subprocess.CalledProcessError:
        return False


def parse_options():
    '''Parse the given options
    '''
    parser = argparse.ArgumentParser(
        description=u'Analyse files found in the given directories \
        for the given language using multiple parallel processes.',
        version=version)
    parser.add_argument(u'lang',
                        help=u"lang which should be analysed")
    parser.add_argument(u'--serial',
                        action=u"store_true",
                        help=u"When this argument is used files will \
                        be analysed one by one.")
    parser.add_argument(u'converted_dirs', nargs=u'+',
                        help=u"director(y|ies) where the converted files \
                        exist")

    args = parser.parse_args()
    return args


def main():
    '''Analyse files in the given directories
    '''
    args = parse_options()
    sanity_check([u'preprocess', u'lookup2cg', u'lookup', u'vislcg3'])

    ana = Analyser(args.lang)
    ana.set_analysis_files(
        abbr_file=os.path.join(
            os.getenv(u'GTHOME'), u'langs',
            args.lang, 'tools/preprocess/abbr.txt'),
        fst_file=os.path.join(
            os.getenv(u'GTHOME'), u'langs',
            args.lang, u'src/analyser-disamb-gt-desc.xfst'),
        disambiguation_analysis_file=os.path.join(
            os.getenv(u'GTHOME'), u'langs',
            args.lang, u'src/syntax/disambiguation.cg3'),
        function_analysis_file=os.path.join(
            os.getenv(u'GTHOME'),
            u'gtcore/gtdshared/smi/src/syntax/korp.cg3'),
        dependency_analysis_file=os.path.join(
            os.getenv(u'GTHOME'),
            u'gtcore/gtdshared/smi/src/syntax/dependency.cg3')
        )

    ana.collect_files(args.converted_dirs)
    if args.serial:
        ana.analyse_serially()
    else:
        ana.analyse_in_parallel()

if __name__ == u'__main__':
    main()
