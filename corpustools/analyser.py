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
import re
import datetime
import lxml.etree as etree
from io import open
import StringIO
import ccat
import argparse

def unwrap_self_analyse(arg, **kwarg):
    return Analyser.analyse(*arg, **kwarg)

class Analyser(object):
    def __init__(self, lang, old=False):
        self.lang = lang
        self.old = old
        self.xp = ccat.XMLPrinter(lang=lang, all_paragraphs=True)
        self.xp.set_outfile(StringIO.StringIO())

    def exitOnError(self, filename):
        error = False

        if filename is None:
            print >>sys.stderr, filename, 'is not defined'
            error = True
        elif not os.path.exists(filename):
            print >>sys.stderr, filename, 'does not exist'
            error = True

        if error:
            sys.exit(4)

    def setAnalysisFiles(self,
                         abbrFile=None,
                         fstFile=None,
                         disambiguationAnalysisFile=None,
                         functionAnalysisFile=None,
                         dependencyAnalysisFile=None):
        if self.lang in ['sma', 'sme', 'smj']:
            self.exitOnError(abbrFile)
        self.exitOnError(fstFile)
        self.exitOnError(disambiguationAnalysisFile)
        self.exitOnError(functionAnalysisFile)
        self.exitOnError(dependencyAnalysisFile)

        self.abbrFile = abbrFile
        self.fstFile = fstFile
        self.disambiguationAnalysisFile = disambiguationAnalysisFile
        self.functionAnalysisFile = functionAnalysisFile
        self.dependencyAnalysisFile = dependencyAnalysisFile

    def setCorrFile(self, corrFile):
        self.exitOnError(corrFile)
        self.corrFile = corrFile

    def collectFiles(self, convertedDirs):
        '''convertedDirs is a list of directories containing converted xml files
        '''
        self.xmlFiles = []
        for cdir in convertedDirs:
            for root, dirs, files in os.walk(cdir): # Walk directory tree
                for f in files:
                    if self.lang in root and f.endswith(u'.xml'):
                        self.xmlFiles.append(os.path.join(root, f))

    def makedirs(self):
        u"""Make the analysed directory
        """
        try:
            os.makedirs(os.path.dirname(self.analysisXmlFile))
        except OSError:
            pass

    def getLang(self):
        u"""
        @brief Get the mainlang from the xml file

        :returns: the language as set in the xml file
        """
        if self.eTree.getroot().attrib[u'{http://www.w3.org/XML/1998/namespace}lang'] is not None:
            return self.eTree.getroot().attrib[u'{http://www.w3.org/XML/1998/namespace}lang']
        else:
            return u'none'

    def getGenre(self):
        u"""
        @brief Get the genre from the xml file

        :returns: the genre as set in the xml file
        """
        if self.eTree.getroot().find(u".//genre") is not None:
            return self.eTree.getroot().find(u".//genre").attrib[u"code"]
        else:
            return u'none'

    def getOcr(self):
        u"""
        @brief Check if the ocr element exists

        :returns: the ocr element or None
        """
        return self.eTree.getroot().find(u".//ocr")

    def getTranslatedfrom(self):
        u"""
        @brief Get the translated_from value from the xml file

        :returns: the value of translated_from as set in the xml file
        """
        if self.eTree.getroot().find(u".//translated_from") is not None:
            return self.eTree.getroot().find(u".//translated_from").attrib[u"{http://www.w3.org/XML/1998/namespace}lang"]
        else:
            return u'none'

    def calculateFilenames(self, xmlFile):
        u"""Set the names of the analysis files
        """
        self.dependencyAnalysisName = xmlFile.replace(u'/converted/', u'/analysed')

    def ccat(self):
        u"""Runs ccat on the input file
        Returns the output of ccat
        """
        self.xp.process_file(self.xmlFile)

        return self.xp.outfile.getvalue()

    def runExternalCommand(self, command, input):
        '''Run the command with input using subprocess
        '''
        subp = subprocess.Popen(command,
                                stdin = subprocess.PIPE,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE)
        (output, error) = subp.communicate(input)
        self.checkError(command, error)

        return output

    def preprocess(self):
        u"""Runs preprocess on the ccat output.
        Returns the output of preprocess
        """
        preProcessCommand = [u'preprocess']

        if self.abbrFile is not None:
            preProcessCommand.append(u'--abbr=' + self.abbrFile)

        if self.lang == 'sme' and self.corrFile is not None:
            preProcessCommand.append(u'--corr=' + self.corrFile)

        return self.runExternalCommand(preProcessCommand, self.ccat())

    def lookup(self):
        u"""Runs lookup on the preprocess output
        Returns the output of preprocess
        """
        lookupCommand = [u'lookup', u'-q', u'-flags', u'mbTT', self.fstFile]

        return self.runExternalCommand(lookupCommand, self.preprocess())


    def lookup2cg(self):
        u"""Runs the lookup on the lookup output
        Returns the output of lookup2cg
        """
        lookup2cgCommand = [u'lookup2cg']

        return self.runExternalCommand(lookup2cgCommand, self.lookup())

    def disambiguationAnalysis(self):
        u"""Runs vislcg3 on the lookup2cg output, which produces a disambiguation
        analysis
        The output is stored in a .dis file
        """
        disAnalysisCommand = \
            [u'vislcg3', u'-g', self.disambiguationAnalysisFile]

        self.disambiguation = \
            self.runExternalCommand(disAnalysisCommand, self.lookup2cg())

    def functionAnalysis(self):
        u"""Runs vislcg3 on the dis file
        Return the output of this process
        """
        self.disambiguationAnalysis()

        functionAnalysisCommand = \
            [u'vislcg3', u'-g', self.functionAnalysisFile]

        return self.runExternalCommand(functionAnalysisCommand, self.getDisambiguation())

    def dependencyAnalysis(self):
        u"""Runs vislcg3 on the .dis file.
        Produces output in a .dep file
        """
        depAnalysisCommand = \
            [u'vislcg3', u'-g', self.dependencyAnalysisFile]

        self.dependency = \
            self.runExternalCommand(depAnalysisCommand, self.functionAnalysis())

    def getDisambiguation(self):
        return self.disambiguation

    def getDisambiguationXml(self):
        disambiguation = etree.Element(u'disambiguation')
        disambiguation.text = self.disambiguationAnalysis().decode(u'utf8')
        body = etree.Element(u'body')
        body.append(disambiguation)

        oldbody = self.eTree.find(u'.//body')
        oldbody.getparent().replace(oldbody, body)

        return self.eTree

    def getDependency(self):
        return self.dependency

    def getAnalysisXml(self):
        body = etree.Element(u'body')

        disambiguation = etree.Element(u'disambiguation')
        disambiguation.text = self.getDisambiguation().decode(u'utf8')
        body.append(disambiguation)

        dependency = etree.Element(u'dependency')
        dependency.text = self.getDependency().decode(u'utf8')
        body.append(dependency)

        oldbody = self.eTree.find(u'.//body')
        oldbody.getparent().replace(oldbody, body)

        return self.eTree

    def checkError(self, command, error):
        if error is not None and len(error) > 0:
            print >>sys.stderr, self.xmlFile
            print >>sys.stderr, command
            print >>sys.stderr, error

    def analyse(self, xmlFile):
        u'''Analyse a file if it is not ocr'ed
        '''
        self.xmlFile = xmlFile
        self.analysisXmlFile = self.xmlFile.replace(u'converted/', u'analysed/')
        self.eTree = etree.parse(xmlFile)
        self.calculateFilenames(xmlFile)

        if self.getOcr() is None:
            self.dependencyAnalysis()
            self.makedirs()
            self.getAnalysisXml().write(
                self.analysisXmlFile,
                encoding=u'utf8',
                xml_declaration=True)

    def analyseInParallel(self):
        poolSize = multiprocessing.cpu_count() * 2
        pool = multiprocessing.Pool(processes=poolSize,)
        poolOutputs = pool.map(
            unwrap_self_analyse,
            zip([self]*len(self.xmlFiles), self.xmlFiles))
        pool.close() # no more tasks
        pool.join()  # wrap up current tasks

    def analyseSerially(self):
        for xmlFile in self.xmlFiles:
            print >>sys.stderr, u'Analysing', xmlFile
            self.analyse(xmlFile)


class AnalysisConcatenator(object):
    def __init__(self, goalDir, xmlFiles, old=False):
        u"""
        @brief Receives a list of filenames that has been analysed
        """
        self.basenames = xmlFiles
        self.old = old
        if old:
            self.disoldFiles = {}
            self.depoldFiles = {}
        self.disFiles = {}
        self.depFiles = {}
        self.goalDir = os.path.join(goalDir, datetime.date.today().isoformat())
        try:
            os.makedirs(self.goalDir)
        except OSError:
            pass

    def concatenateAnalysedFiles(self):
        u"""
        @brief Concatenates analysed files according to origlang, translated_from_lang and genre
        """
        for xmlFile in self.basenames:
            self.concatenateAnalysedFile(xmlFile[1].replace(u".xml", u".dis"))
            self.concatenateAnalysedFile(xmlFile[1].replace(u".xml", u".dep"))
            if self.old:
                self.concatenateAnalysedFile(xmlFile[1].replace(u".xml", u".disold"))
                self.concatenateAnalysedFile(xmlFile[1].replace(u".xml", u".depold"))


    def concatenateAnalysedFile(self, filename):
        u"""
        @brief Adds the content of the given file to file it belongs to

        :returns: ...
        """
        if os.path.isfile(filename):
            fromFile = open(filename)
            self.getToFile(fromFile.readline(), filename).write(fromFile.read())
            fromFile.close()
            os.unlink(filename)

    def getToFile(self, prefix, filename):
        u"""
        @brief Gets the prefix of the filename. Opens a file object with the files prefix.

        :returns: File object belonging to the prefix of the filename
        """

        prefix = os.path.join(self.goalDir, prefix.strip())
        if filename[-4:] == u".dis":
            try:
                self.disFiles[prefix]
            except KeyError:
                self.disFiles[prefix] = open(prefix + u".dis", u"w")

            return self.disFiles[prefix]

        elif filename[-4:] == u".dep":
            try:
                self.depFiles[prefix]
            except KeyError:
                self.depFiles[prefix] = open(prefix + u".dep", u"w")

            return self.depFiles[prefix]

        if filename[-7:] == u".disold":
            try:
                self.disoldFiles[prefix]
            except KeyError:
                self.disoldFiles[prefix] = open(prefix + u".disold", u"w")

            return self.disoldFiles[prefix]

        elif filename[-7:] == u".depold":
            try:
                self.depoldFiles[prefix]
            except KeyError:
                self.depoldFiles[prefix] = open(prefix + u".depold", u"w")

            return self.depoldFiles[prefix]

def sanityCheck():
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
    sanityCheck()

    ana = Analyser(args.lang, args.old)
    ana.setAnalysisFiles(
        abbrFile=\
            os.path.join(os.getenv(u'GTHOME'),
                          u'langs/' +
                          args.lang +
                          '/src/syntax/abbr.txt'),
        fstFile=\
            os.path.join(os.getenv(u'GTHOME'),
                         u'langs/' +
                         args.lang +
                         u'/src/analyser-gt-desc.xfst'),
        disambiguationAnalysisFile=\
            os.path.join(os.getenv(u'GTHOME'),
                         u'langs/' +
                         args.lang +
                         u'/src/syntax/disambiguation.cg3'),
        functionAnalysisFile=\
            os.path.join(os.getenv(u'GTHOME'),
                         u'gtcore/gtdshared/smi/src/syntax/functions.cg3'),
        dependencyAnalysisFile=\
            os.path.join(
                os.getenv(u'GTHOME'),
                u'gtcore/gtdshared/smi/src/syntax/dependency.cg3'))

    if args.lang == u'sme':
        ana.setCorrFile(os.path.join(os.getenv(u'GTHOME'),
                                     u'langs/' +
                                     args.lang +
                                     '/src/syntax/corr.txt'))

    ana.collectFiles(args.converted_dirs)
    if args.debug is False:
        ana.analyseInParallel()
    else:
        ana.analyseSerially()

if __name__ == u'__main__':
    main()
