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

import os
import sys
import subprocess
import multiprocessing
import datetime
import lxml.etree as etree
from io import open
import StringIO
from corpustools import ccat
import argparse

def unwrap_self_analyse(arg, **kwarg):
    return Analyser.analyse(*arg, **kwarg)

class Analyser(object):
    def __init__(self, lang, old=False):
        self.lang = lang
        self.old = old
        self.xp = ccat.XMLPrinter(lang=lang, all_paragraphs=True)
        self.xp.set_outfile(StringIO.StringIO())

    def exit_on_error(self, filename):
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
        self.exit_on_error(corr_file)
        self.corr_file = corr_file

    def collect_files(self, converted_dirs):
        '''converted_dirs is a list of directories containing converted xml files
        '''
        self.xml_files = []
        for cdir in converted_dirs:
            for root, dirs, files in os.walk(cdir): # Walk directory tree
                for f in files:
                    if self.lang in root and f.endswith(u'.xml'):
                        self.xml_files.append(os.path.join(root, f))

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
        if self.etree.getroot().attrib[u'{http://www.w3.org/XML/1998/namespace}lang'] is not None:
            return self.etree.getroot().attrib[u'{http://www.w3.org/XML/1998/namespace}lang']
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
            return self.etree.getroot().find(u".//translated_from").attrib[u"{http://www.w3.org/XML/1998/namespace}lang"]
        else:
            return u'none'

    def calculate_filenames(self, xml_file):
        u"""Set the names of the analysis files
        """
        self.dependency_analysis_name = xml_file.replace(u'/converted/', u'/analysed')

    def ccat(self):
        u"""Runs ccat on the input file
        Returns the output of ccat
        """
        self.xp.process_file(self.xml_file)

        return self.xp.outfile.getvalue()

    def run_external_command(self, command, input):
        '''Run the command with input using subprocess
        '''
        subp = subprocess.Popen(command,
                                stdin = subprocess.PIPE,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE)
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

        if self.lang == 'sme' and self.corr_file is not None:
            pre_process_command.append(u'--corr=' + self.corr_file)

        return self.run_external_command(pre_process_command, self.ccat())

    def lookup(self):
        u"""Runs lookup on the preprocess output
        Returns the output of preprocess
        """
        lookup_command = [u'lookup', u'-q', u'-flags', u'mbTT', self.fst_file]

        return self.run_external_command(lookup_command, self.preprocess())


    def lookup2cg(self):
        u"""Runs the lookup on the lookup output
        Returns the output of lookup2cg
        """
        lookup2cg_command = [u'lookup2cg']

        return self.run_external_command(lookup2cg_command, self.lookup())

    def disambiguation_analysis(self):
        u"""Runs vislcg3 on the lookup2cg output, which produces a disambiguation
        analysis
        The output is stored in a .dis file
        """
        dis_analysis_command = \
            [u'vislcg3', u'-g', self.disambiguation_analysis_file]

        self.disambiguation = \
            self.run_external_command(dis_analysis_command, self.lookup2cg())

    def function_analysis(self):
        u"""Runs vislcg3 on the dis file
        Return the output of this process
        """
        self.disambiguation_analysis()

        function_analysis_command = \
            [u'vislcg3', u'-g', self.function_analysis_file]

        return self.run_external_command(function_analysis_command, self.get_disambiguation())

    def dependency_analysis(self):
        u"""Runs vislcg3 on the .dis file.
        Produces output in a .dep file
        """
        dep_analysis_command = \
            [u'vislcg3', u'-g', self.dependency_analysis_file]

        self.dependency = \
            self.run_external_command(dep_analysis_command, self.function_analysis())

    def get_disambiguation(self):
        return self.disambiguation

    def get_disambiguation_xml(self):
        disambiguation = etree.Element(u'disambiguation')
        disambiguation.text = self.disambiguation_analysis().decode(u'utf8')
        body = etree.Element(u'body')
        body.append(disambiguation)

        oldbody = self.etree.find(u'.//body')
        oldbody.getparent().replace(oldbody, body)

        return self.etree

    def get_dependency(self):
        return self.dependency

    def get_analysis_xml(self):
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
        if error is not None and len(error) > 0:
            print >>sys.stderr, self.xml_file
            print >>sys.stderr, command
            print >>sys.stderr, error

    def analyse(self, xml_file):
        u'''Analyse a file if it is not ocr'ed
        '''
        self.xml_file = xml_file
        self.analysis_xml_file = self.xml_file.replace(u'converted/', u'analysed/')
        self.etree = etree.parse(xml_file)
        self.calculate_filenames(xml_file)

        if self.get_ocr() is None:
            self.dependency_analysis()
            self.makedirs()
            self.get_analysis_xml().write(
                self.analysis_xml_file,
                encoding=u'utf8',
                xml_declaration=True)

    def analyse_in_parallel(self):
        pool_size = multiprocessing.cpu_count() * 2
        pool = multiprocessing.Pool(processes=pool_size,)
        pool_outputs = pool.map(
            unwrap_self_analyse,
            zip([self]*len(self.xml_files), self.xml_files))
        pool.close() # no more tasks
        pool.join()  # wrap up current tasks

    def analyse_serially(self):
        for xml_file in self.xml_files:
            print >>sys.stderr, u'Analysing', xml_file
            self.analyse(xml_file)


class AnalysisConcatenator(object):
    def __init__(self, goal_dir, xml_files, old=False):
        u"""
        @brief Receives a list of filenames that has been analysed
        """
        self.basenames = xml_files
        self.old = old
        if old:
            self.disold_files = {}
            self.depold_files = {}
        self.dis_files = {}
        self.dep_files = {}
        self.goal_dir = os.path.join(goal_dir, datetime.date.today().isoformat())
        try:
            os.makedirs(self.goal_dir)
        except OSError:
            pass

    def concatenate_analysed_files(self):
        u"""
        @brief Concatenates analysed files according to origlang, translated_from_lang and genre
        """
        for xml_file in self.basenames:
            self.concatenate_analysed_file(xml_file[1].replace(u".xml", u".dis"))
            self.concatenate_analysed_file(xml_file[1].replace(u".xml", u".dep"))
            if self.old:
                self.concatenate_analysed_file(xml_file[1].replace(u".xml", u".disold"))
                self.concatenate_analysed_file(xml_file[1].replace(u".xml", u".depold"))


    def concatenate_analysed_file(self, filename):
        u"""
        @brief Adds the content of the given file to file it belongs to

        :returns: ...
        """
        if os.path.isfile(filename):
            from_file = open(filename)
            self.get_to_file(from_file.readline(), filename).write(from_file.read())
            from_file.close()
            os.unlink(filename)

    def get_to_file(self, prefix, filename):
        u"""
        @brief Gets the prefix of the filename. Opens a file object with the files prefix.

        :returns: File object belonging to the prefix of the filename
        """

        prefix = os.path.join(self.goal_dir, prefix.strip())
        if filename[-4:] == u".dis":
            try:
                self.dis_files[prefix]
            except KeyError:
                self.dis_files[prefix] = open(prefix + u".dis", u"w")

            return self.dis_files[prefix]

        elif filename[-4:] == u".dep":
            try:
                self.dep_files[prefix]
            except KeyError:
                self.dep_files[prefix] = open(prefix + u".dep", u"w")

            return self.dep_files[prefix]

        if filename[-7:] == u".disold":
            try:
                self.disold_files[prefix]
            except KeyError:
                self.disold_files[prefix] = open(prefix + u".disold", u"w")

            return self.disold_files[prefix]

        elif filename[-7:] == u".depold":
            try:
                self.depold_files[prefix]
            except KeyError:
                self.depold_files[prefix] = open(prefix + u".depold", u"w")

            return self.depold_files[prefix]

def sanity_check():
    u"""Look for programs and files that are needed to do the analysis.
    If they don't exist, quit the program
    """
    for program in [u'preprocess', u'lookup2cg', u'lookup', u'vislcg3']:
        if which(program) is False:
            sys.stderr.write(program, u" isn't found in path\n")
            sys.exit(2)

def which(name):
        u"""Get the output of the unix command which.
        Return false if empty, true if non-empty
        """
        if subprocess.check_output([u'which', name]) == u'':
            return False
        else:
            return True

def parse_options():
    parser = argparse.ArgumentParser(description = u'Analyse files found in the given directories for the given language using multiple parallel processes.')
    parser.add_argument(u'-l', u'--lang', help = u"lang which should be analysed")
    #parser.add_argument('-a', '--analysisdir', help='directory where the analysed files are placed')
    parser.add_argument(u'-o', u'--old', help=u'When using this sme texts are analysed using the old disambiguation grammars', action=u"store_true")
    parser.add_argument(u'--debug', help=u"use this for debugging the analysis process. When this argument is used files will be analysed one by one.", action=u"store_true")
    parser.add_argument(u'converted_dirs', nargs=u'+', help = u"director(y|ies) where the converted files exist")

    args = parser.parse_args()
    return args

def main():
    args = parse_options()
    sanity_check()

    ana = Analyser(args.lang, args.old)
    ana.set_analysis_files(
        abbr_file=\
            os.path.join(os.getenv(u'GTHOME'),
                          u'langs/' +
                          args.lang +
                          '/src/syntax/abbr.txt'),
        fst_file=\
            os.path.join(os.getenv(u'GTHOME'),
                         u'langs/' +
                         args.lang +
                         u'/src/analyser-gt-desc.xfst'),
        disambiguation_analysis_file=\
            os.path.join(os.getenv(u'GTHOME'),
                         u'langs/' +
                         args.lang +
                         u'/src/syntax/disambiguation.cg3'),
        function_analysis_file=\
            os.path.join(os.getenv(u'GTHOME'),
                         u'gtcore/gtdshared/smi/src/syntax/functions.cg3'),
        dependency_analysis_file=\
            os.path.join(
                os.getenv(u'GTHOME'),
                u'gtcore/gtdshared/smi/src/syntax/dependency.cg3'))

    if args.lang == u'sme':
        ana.set_corr_file(os.path.join(os.getenv(u'GTHOME'),
                                     u'langs/' +
                                     args.lang +
                                     '/src/syntax/corr.txt'))

    ana.collect_files(args.converted_dirs)
    if args.debug is False:
        ana.analyse_in_parallel()
    else:
        ana.analyse_serially()

if __name__ == u'__main__':
    main()
