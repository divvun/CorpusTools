#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#   This file contains routines to sentence align two files
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
#   Copyright 2011-2014 Børre Gaup <borre.gaup@uit.no>
#

import os
import errno
import re
import sys
import subprocess
import difflib
from lxml import etree
import datetime
import time
import argparse

import typosfile
import ngram
import argparse_version
import util

class ArgumentError(Exception):
    pass

class CorpusXMLFile:
    """
    A class that contains the info on a file to be parallellized, name
    and language
    """

    def __init__(self, name, paralang):
        self.name = name
        self.paralang = paralang
        self.etree = etree.parse(name)
        self.sanity_check()

    def sanity_check(self):
        if self.etree.getroot().tag != u"document":
            raise ArgumentError(
                "Expected Corpus XML file (output of convert2xml) with <document> as "
                "the root tag, got %s -- did you pass the wrong file?" % (
                    self.etree.getroot().tag,))

    def get_etree(self):
        return self.etree

    def get_name(self):
        """
        Return the absolute path of the file
        """
        return self.name

    def get_dirname(self):
        """
        Return the dirname of the file
        """
        return os.path.dirname(self.name)

    def get_basename(self):
        """
        Return the basename of the file
        """
        return os.path.basename(self.name)

    def get_lang(self):
        """
        Get the lang of the file
        """
        return self.etree.getroot().attrib[
            '{http://www.w3.org/XML/1998/namespace}lang']

    def get_word_count(self):
        root = self.etree.getroot()
        word_count = root.find(".//wordcount")
        if word_count is not None:
            return word_count.text

    def get_parallel_basename(self):
        """
        Get the basename of the parallel file
        Input is the lang of the parallel file
        """
        root = self.etree.getroot()
        parallel_files = root.findall(".//parallel_text")
        for p in parallel_files:
            if (p.attrib['{http://www.w3.org/XML/1998/namespace}lang'] ==
                    self.paralang):
                return p.attrib['location']

    def get_parallel_filename(self):
        """
        Infer the absolute path of the parallel file
        """
        parallel_dirname = self.get_dirname().replace(
            self.get_lang(), self.paralang)
        if self.get_parallel_basename() is not None:
            parallel_basename = self.get_parallel_basename() + '.xml'

            return os.path.join(parallel_dirname, parallel_basename)

    def get_original_filename(self):
        """
        Infer the path of the original file
        """
        return self.get_name().replace('prestable/', '').replace(
            'converted/', 'orig/').replace('.xml', '')

    def get_translated_from(self):
        """
        Get the translated_from element from the orig doc
        """
        root = self.etree.getroot()
        translated_from = root.find(".//translated_from")

        if translated_from is not None:
            return translated_from.attrib[
                '{http://www.w3.org/XML/1998/namespace}lang']

    def remove_version(self):
        """
        Remove the version element
        This is often the only difference between the otherwise
        identical files in converted and prestable/converted
        """
        root = self.etree.getroot()
        version_element = root.find(".//version")
        version_element.getparent().remove(version_element)

    def remove_skip(self):
        """
        Remove the skip element
        This contains text that is not wanted in e.g. sentence alignment
        """
        root = self.etree.getroot()
        skip_list = root.findall(".//skip")

        for skip_element in skip_list:
            skip_element.getparent().remove(skip_element)

    def move_later(self):
        """
        Move the later elements to the end of the body element.
        """
        root = self.etree.getroot()
        body = root.xpath("/document/body")[0]

        later_list = root.xpath(".//later")

        for later_element in later_list:
            body.append(later_element)


class SentenceDivider:
    """A class that takes a giellatekno xml document as input.
    It spits out an xml document that has divided the text inside the p tags
    into sentences, but otherwise is unchanged.
    Each sentence is encased in an s tag, and has an id number
    """
    def __init__(self, input_xmlfile, parallel_lang):
        """Parse the input_xmlfile, set doc_lang to lang and read typos from
        the corresponding .typos file if it exists
        """
        self.set_up_input_file(input_xmlfile, parallel_lang)
        self.sentence_counter = 0
        self.typos = {}

        typosname = input_xmlfile.replace('.xml', '.typos')
        if os.path.isfile(typosname):
            t = typosfile.Typos(input_xmlfile.replace('.xml', '.typos'))
            self.typos.update(t.get_typos())

    def set_up_input_file(self, input_xmlfile, parallel_lang):
        """
        Initialize the inputfile, skip those parts that are meant to be
        skipped, move <later> elements.
        """
        in_file = CorpusXMLFile(input_xmlfile, parallel_lang)
        self.doc_lang = in_file.get_lang()

        in_file.move_later()
        in_file.remove_skip()
        self.input_etree = in_file.get_etree()

    def process_all_paragraphs(self):
        """Go through all paragraphs in the etree and process them one by one.
        """
        self.document = etree.Element('document')
        body = etree.Element('body')
        self.document.append(body)

        for paragraph in self.input_etree.findall('//p'):
            body.append(self.process_one_paragraph(paragraph))

    def write_result(self, outfile):
        """Write self.document to the given outfile name
        """
        o_path, o_file = os.path.split(outfile)
        o_rel_path = o_path.replace(os.getcwd()+'/', '', 1)
        try:
            os.makedirs(o_rel_path)
        except OSError, e:
            if e.errno != errno.EEXIST:
                raise
        f = open(outfile, 'w')
        et = etree.ElementTree(self.document)
        et.write(f,
                 pretty_print=True,
                 encoding="utf-8",
                 xml_declaration=True)
        f.close()

    def get_preprocess_output(self, preprocess_input):
        """Send the text in preprocess_input into preprocess, return the
        result.
        If the process fails, exit the program
        """
        preprocess_script = os.path.join(os.environ['GTHOME'],
                                         'gt/script/preprocess')
        util.sanity_check([preprocess_script])

        preprocess_command = []
        if (self.doc_lang == 'nob'):
            abbr_file = os.path.join(
                os.environ['GTHOME'], 'st/nob/bin/abbr.txt')
            preprocess_command = [preprocess_script, '--abbr=' + abbr_file]
        else:
            abbr_file = os.path.join(os.environ['GTHOME'],
                                     'gt/sme/bin/abbr.txt')
            corr_file = os.path.join(os.environ['GTHOME'],
                                     'gt/sme/bin/corr.txt')
            preprocess_command = [preprocess_script,
                                  '--abbr=' + abbr_file,
                                  '--corr=' + corr_file]

        subp = subprocess.Popen(preprocess_command,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        (output, error) = subp.communicate(
            preprocess_input.encode('utf-8').replace('\n', ' '))

        if subp.returncode != 0:
            print >>sys.stderr, 'Could not divide into sentences'
            print >>sys.stderr, output
            print >>sys.stderr, error
            sys.exit()
        else:
            return output

    def process_one_paragraph(self, orig_paragraph):
        """Run the content of the orig_paragraph through preprocess,
        make sentences
        Return a new paragraph containing the marked up sentences
        """
        new_paragraph = etree.Element("p")

        all_text = orig_paragraph.xpath('.//text()')
        preprocess_input = "".join(all_text)

        # Check if there is any text from preprocess
        if (preprocess_input):
            output = self.get_preprocess_output(preprocess_input)
            sentence = []
            incomplete_sentences = ['.', '?', '!', ')', ']', '...', '…', '"',
                                    '»', '”', '°', '', ':']
            words = output.split('\n')
            i = 0
            while i < len(words):
                word = words[i].strip()

                # If word exists in typos, replace it with the correction
                if word in self.typos:
                    word = self.typos[word]

                sentence.append(word.decode('utf-8'))
                if (word == '.' or word == '?' or word == '!'):
                    while (i + 1 < len(words) and
                           words[i + 1].strip() in incomplete_sentences):
                        if words[i + 1] != '':
                            sentence.append(
                                words[i + 1].decode('utf-8').strip())
                        i = i + 1

                    # exclude pseudo-sentences, i.e. sentences that
                    # don't contain any alphanumeric characters
                    if not re.compile(
                            r"^[\W|\s]*$").match(' '.join(sentence)):
                        new_paragraph.append(self.make_sentence(sentence))
                    sentence = []

                i = i + 1

            # exclude pseudo-sentences, i.e. sentences that don't contain
            # any alphanumeric characters
            if (len(sentence) > 1 and not
                    re.compile(r"^[\W|\s]*$").match(' '.join(sentence))):
                new_paragraph.append(self.make_sentence(sentence))

        return new_paragraph

    def make_sentence(self, sentence):
        """Make an s element, set the id and set the text to be the content of
        the list sentence
        """

        # make regex for two or more space characters
        spaces = re.compile(' +')

        s = etree.Element("s")
        s.attrib["id"] = str(self.sentence_counter)

        # substitute two or more spaces with one space
        s.text = spaces.sub(' ', ' '.join(sentence)).strip()

        self.sentence_counter += 1

        return s


class Parallelize:
    """
    A class to parallelize two files
    Input is the xml file that should be parallellized and the language that it
    should be parallellized with.
    The language of the input file is found in the metadata of the input file.
    The other file is found via the metadata in the input file
    """

    def __init__(self, origfile1, lang2):
        """
        Set the original file name, the lang of the original file and the
        language that it should parallellized with.
        Parse the original file to get the access to metadata
        """
        self.origfiles = []

        tmpfile = CorpusXMLFile(os.path.abspath(origfile1), lang2)
        self.origfiles.append(tmpfile)

        if self.origfiles[0].get_parallel_filename() is not None:
            tmpfile = CorpusXMLFile(
                self.origfiles[0].get_parallel_filename(),
                self.origfiles[0].get_lang())
            self.origfiles.append(tmpfile)
        else:
            raise IOError(origfile1 + " doesn't have a parallel file in " +
                          lang2)

        if self.is_translated_from_lang2():
            self.reshuffle_files()

    def reshuffle_files(self):
        """
        Change the order of the files (so that the translated text is last)
        """
        tmp = self.origfiles[0]
        self.origfiles[0] = self.origfiles[1]
        self.origfiles[1] = tmp

    def get_filelist(self):
        """
        Return the list of (the two) files that are aligned
        """
        return self.origfiles

    def get_lang1(self):
        return self.origfiles[0].get_lang()

    def get_lang2(self):
        return self.origfiles[1].get_lang()

    def get_origfile1(self):
        return self.origfiles[0].get_name()

    def get_origfile2(self):
        return self.origfiles[1].get_name()

    def is_translated_from_lang2(self):
        """
        Find out if the given doc is translated from lang2
        """
        result = False
        origfile1Tree = etree.parse(self.get_origfile1())
        root = origfile1Tree.getroot()
        translated_from = root.find(".//translated_from")
        if translated_from is not None:
            if (translated_from.attrib[
                    '{http://www.w3.org/XML/1998/namespace}lang'] ==
                    self.get_lang2()):
                result = True

        return result

    def generate_anchor_file(self):
        """
        Generate an anchor file with lang1 and lang2. Return the path
        to the anchor file
        """
        generate_script = os.path.join(os.environ['GTHOME'],
                                       'gt/script/corpus/generate-anchor-list.pl')
        util.sanity_check([generate_script])

        infile1 = os.path.join(os.environ['GTHOME'],
                               'gt/common/src/anchor.txt')
        infile2 = os.path.join(os.environ['GTHOME'],
                               'gt/common/src/anchor-admin.txt')

        subp = subprocess.Popen([generate_script,
                                 '--lang1=' + self.get_lang1(),
                                 '--lang2' + self.get_lang2(),
                                 '--outdir=' + os.environ['GTFREE'],
                                 infile1, infile2],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        (output, error) = subp.communicate()
        out_filename = 'anchor-' + self.get_lang1() + self.get_lang2() + '.txt'

        if subp.returncode != 0:
            print >>sys.stderr, out_filename
            print >>sys.stderr, output
            print >>sys.stderr, error
            return subp.returncode

        # Return the absolute path of the resulting file
        return os.path.join(os.environ['GTFREE'], out_filename)

    def divide_p_into_sentences(self):
        """
        Tokenize the text in the given file and reassemble it again
        """
        for pfile in self.origfiles:
            infile = os.path.join(pfile.get_name())
            if os.path.exists(infile):
                outfile = self.get_sent_filename(pfile)
                divider = SentenceDivider(infile, pfile.get_lang())
                divider.process_all_paragraphs()
                divider.write_result(outfile)
            else:
                print >>sys.stderr, infile, "doesn't exist"
                return 2

        return 0

    def get_sent_filename(self, pfile):
        """
        Compute a name for the corpus-analyze output and tca2 input file
        Input is a CorpusXMLFile
        """
        origfilename = pfile.get_basename().replace('.xml', '')
        return os.environ['GTFREE'] + '/tmp/' + origfilename + \
            pfile.get_lang() + '_sent.xml'

    def parallelize_files(self):
        """
        Parallelize two files using tca2
        """
        tca2_script = os.path.join(os.environ['GTHOME'],
                                   'gt/script/corpus/tca2.sh')
        util.sanity_check([tca2_script])

        anchor_name = self.generate_anchor_file()

        subp = subprocess.Popen([tca2_script,
                                 anchor_name,
                                 self.get_sent_filename(
                                     self.get_filelist()[0]),
                                 self.get_sent_filename(
                                     self.get_filelist()[1])],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        (output, error) = subp.communicate()

        if subp.returncode != 0:
            print >>sys.stderr, 'Could not parallelize', \
                self.get_sent_filename(self.get_filelist()[0]), 'and', \
                self.get_sent_filename(self.get_filelist()[1]), \
                ' into sentences'
            print >>sys.stderr, output
            print >>sys.stderr, error

        return subp.returncode


class Tmx:
    """
    A class that reads a tmx file, and implements a bare minimum of
    functionality to be able to compare two tmx's.
    It also contains functions to manipulate the tmx in several ways.
    """

    def __init__(self, tmx):
        """Input is a tmx element
        """
        self.tmx = tmx

        gthome = os.getenv('GTHOME')
        self.language_guesser = ngram.NGram(gthome + '/tools/lang-guesser/LM/')

    def get_src_lang(self):
        """
        Get the srclang from the header element
        """
        return self.tmx.find(".//header").attrib['srclang'][:3]

    def get_tmx(self):
        """
        Get the tmx xml element
        """
        return self.tmx

    def tu_to_string(self, tu):
        """
        Extract the two strings of a tu element
        """
        string = ""
        try:
            string = string + tu[0][0].text.strip()
        except(AttributeError):
            pass

        string += '\t'

        try:
            string = string + tu[1][0].text.strip()
        except(AttributeError):
            pass

        string += '\n'
        return string.encode('utf-8')

    def tuv_to_string(self, tuv):
        """
        Extract the string from the tuv element
        """
        string = ""
        try:
            string = tuv[0].text.strip()
        except(AttributeError):
            pass

        return string.encode('utf-8')

    def lang_to_stringlist(self, lang):
        """
        Get all the strings in the tmx in language lang, insert them
        into the list strings
        """
        all_tuv = self.get_tmx().\
            xpath('.//tuv[@xml:lang="' + lang + '"]',
                  namespaces={'xml': 'http://www.w3.org/XML/1998/namespace'})

        strings = []
        for tuv in all_tuv:
            strings.append(self.tuv_to_string(tuv))

        return strings

    def tmx_to_stringlist(self):
        """
        Extract all string pairs in a tmx to a list of strings
        """
        all_tu = self.get_tmx().findall('.//tu')
        strings = []
        for tu in all_tu:
            strings.append(self.tu_to_string(tu))

        return strings

    def prettify_segs(self, tu):
        """Strip white space from start and end of the strings in the
        seg elements
        Input is a tu element
        Output is a tu element with white space stripped strings
        """
        try:
            string = tu[0][0].text.strip()
            tu[0][0].text = string
        except(AttributeError):
            pass

        try:
            string = tu[1][0].text.strip()
            tu[1][0].text = string
        except(AttributeError):
            pass

        return tu

    # to debug here
    def reverse_langs(self):
        """
        Reverse the langs in a tmx
        Return the reverted tmx
        """
        all_tu = self.get_tmx().findall('.//tu')
        body = etree.Element('body')
        for tu in all_tu:
            tmp = etree.Element('tu')
            tmp.append(tu[1])
            tmp.append(tu[0])
            tmp = self.prettify_segs(tmp)
            body.append(tmp)

        tmx = etree.Element('tmx')
        tmx.append(body)

        self.tmx = tmx

    def remove_unwanted_space(self):
        """The SentenceDivider adds spaces before and after punctuation,
        quotemarks, parentheses and so on.
        Remove those spaces so that the tmxes are more appropriate for real
        world™ use cases.
        """

        root = self.get_tmx().getroot()
        for tu in root.iter("tu"):
            tu = self.remove_unwanted_space_from_segs(tu)

    def remove_unwanted_space_from_segs(self, tu):
        """Remove spaces before and after punctuation,
        quotemarks, parentheses and so on as appropriate in the seg elements
        in the tu elements.
        Input is a tu element
        Output is a tu element with modified seg elements
        """
        try:
            string = tu[0][0].text.strip()
            string = self.remove_unwanted_space_from_string(string)
            tu[0][0].text = string
        except AttributeError:
            pass

        try:
            string = tu[1][0].text.strip()
            string = self.remove_unwanted_space_from_string(string)
            tu[1][0].text = string
        except AttributeError:
            pass

        return tu

    def remove_unwanted_space_from_string(self, input_string):
        """Remove spaces before and after punctuation,
        quotemarks, parentheses and so on as appropriate
        """
        result = input_string

        # regex to find space followed by punctuation
        space_punctuation = re.compile("(?P<space>\s)(?P<punctuation>[\)\]\.»:;,])")
        # for every match in the result string, replace the match
        # (space+punctuation) with the punctuation part
        result = space_punctuation.sub(lambda match: match.group(
            'punctuation'), result)

        # regex to find punctuation followed by space
        punctuation_space = re.compile("(?P<punctuation>[\[\(«])(?P<space>\s)+")
        result = punctuation_space.sub(lambda match: match.group(
            'punctuation'), result)

        # regex which matches multiple spaces
        multiple_space = re.compile("\s+")
        result = multiple_space.sub(lambda match: ' ', result)

        return result

    def write_tmx_file(self, out_filename):
        """
        Write a tmx file given a tmx etree element and a filename
        """
        #try:
        try:
            os.makedirs(os.path.dirname(out_filename))
        except OSError:
            pass

        f = open(out_filename, "w")

        string = etree.tostring(self.get_tmx(),
                                pretty_print=True,
                                encoding="utf-8",
                                xml_declaration=True)
        f.write(string)
        f.close()
        print "Wrote", out_filename

    def remove_tu_with_empty_seg(self):
        """Remove tu elements that contain empty seg element
        """
        root = self.get_tmx().getroot()
        for tu in root.iter("tu"):
            try:
                self.check_if_emtpy_seg(tu)
            except AttributeError:
                tu.getparent().remove(tu)

    def check_if_emtpy_seg(self, tu):
        """Check if a tu element contains empty strings
        If there are any empty elements an AttributeError is raised
        """
        string = tu[0][0].text.strip()
        string = tu[1][0].text.strip()

    # Commented out this code because language detection doesn't work well
    # enough
    #def remove_tu_with_wrong_lang(self, lang):
        #"""Remove tu elements that have the wrong lang according to the
        #language guesser
        #"""
        #root = self.get_tmx().getroot()
        #for tu in root.iter("tu"):
            #if self.check_language(tu, lang) == False:
                #tu.getparent().remove(tu)

    def check_language(self, tu, lang):
        """Get the text of the tuv element with the given lang
        Run the text through the language guesser, return the result
        of this test
        """
        for tuv in tu:
            if tuv.get('{http://www.w3.org/XML/1998/namespace}lang') == lang:
                text = tuv[0].text.encode("ascii", "ignore")
                test_lang = self.language_guesser.classify(text)
                if test_lang != lang:
                    return False

        return True


class Tca2ToTmx(Tmx):
    """
    A class to make tmx files based on the output from tca2
    """
    def __init__(self, filelist):
        """
        Input is a list of CorpusXMLFile objects
        """
        self.filelist = filelist
        Tmx.__init__(self, self.set_tmx())

    def make_tu(self, line1, line2):
        """
        Make a tmx tu element based on line1 and line2 as input
        """
        tu = etree.Element("tu")

        tu.append(self.make_tuv(line1, self.filelist[0].get_lang()))
        tu.append(self.make_tuv(line2, self.filelist[1].get_lang()))

        return tu

    def make_tuv(self, line, lang):
        """
        Make a tuv element given an input line and a lang variable
        """
        tuv = etree.Element("tuv")
        tuv.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = lang
        seg = etree.Element("seg")
        seg.text = self.remove_s_tag(line).strip().decode("utf-8")
        tuv.append(seg)

        return tuv

    def make_tmx_header(self, lang):
        """
        Make a tmx header based on the lang variable
        """
        header = etree.Element("header")

        # Set various attributes
        header.attrib["segtype"] = "sentence"
        header.attrib["o-tmf"] = "OmegaT TMX"
        header.attrib["adminlang"] = "en-US"
        header.attrib["srclang"] = lang
        header.attrib["datatype"] = "plaintext"

        return header

    def remove_s_tag(self, line):
        """
        Remove the s tags that tca2 has added
        """
        line = line.replace('</s>', '')
        sregex = re.compile('<s id="[^ ]*">')
        line = sregex.sub('', line)

        return line

    def get_outfile_name(self):
        """
        Compute the name of the tmx file
        """

        orig_path_part = '/converted/' + self.filelist[0].get_lang() + '/'
        # First compute the part that shall replace /orig/ in the path
        replace_path_part = '/toktmx/' + self.filelist[0].get_lang() + '2' \
            + self.filelist[1].get_lang() + '/'
        # Then set the outdir
        out_dirname = self.filelist[0].get_dirname().replace(
            orig_path_part, replace_path_part)
        # Replace xml with tmx in the filename
        out_filename = self.filelist[0].get_basename().replace('.xml',
                                                               '.toktmx')

        return os.path.join(out_dirname, out_filename)

    def set_tmx(self):
        """
        Make tmx file based on the two output files of tca2
        """
        tmx = etree.Element("tmx")
        header = self.make_tmx_header(self.filelist[0].get_lang())
        tmx.append(header)

        pfile1_data = self.read_tca2_output(self.filelist[0])
        pfile2_data = self.read_tca2_output(self.filelist[1])

        body = etree.SubElement(tmx, "body")
        for line1, line2 in map(None, pfile1_data, pfile2_data):
            tu = self.make_tu(line1, line2)
            body.append(tu)

        return tmx

    def read_tca2_output(self, pfile):
        """
        Read the output of tca2
        Input is a CorpusXMLFile
        """
        text = ""
        pfile_name = self.get_sent_filename(pfile).replace('.xml', '_new.txt')
        try:
            f = open(pfile_name, "r")
            text = f.readlines()
            f.close()
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
            sys.exit(1)

        return text

    def get_sent_filename(self, pfile):
        """
        Compute a name for the corpus-analyze output and tca2 input file
        Input is a CorpusXMLFile
        """
        origfilename = pfile.get_basename().replace('.xml', '')
        return (os.environ['GTFREE'] + '/tmp/' + origfilename +
                pfile.get_lang() + '_sent.xml')


class TmxComparator:
    """
    A class to compare two tmx-files
    """
    def __init__(self, want_tmx, got_tmx):
        self.want_tmx = want_tmx
        self.got_tmx = got_tmx

    def get_lines_in_wantedfile(self):
        """
        Return the number of lines in the reference doc
        """
        return len(self.want_tmx.tmx_to_stringlist())

    def get_number_of_differing_lines(self):
        """
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
        """
        Return a stringlist containing the diff lines
        """
        diff = []
        for line in difflib.unified_diff(
                self.want_tmx.tmx_to_stringlist(),
                self.got_tmx.tmx_to_stringlist(), n=0):
            diff.append(line)

        return diff

    def get_lang_diff_as_text(self, lang):
        """
        Return a stringlist containing the diff lines
        """
        diff = []
        for line in difflib.unified_diff(
                self.want_tmx.lang_to_stringlist(lang),
                self.got_tmx.lang_to_stringlist(lang), n=0):
            diff.append(line + '\n')

        return diff


class TmxTestDataWriter():
    """
    A class that writes tmx test data to a file
    """
    def __init__(self, filename):
        self.filename = filename

        try:
            tree = etree.parse(filename)
            self.set_parags_testing_element(tree.getroot())
        except IOError, error:
            print "I/O error({0}): {1}".format(error.errno, error.strerror)
            sys.exit(1)

    def get_filename(self):
        return self.filename

    def make_file_element(self, name, gspairs, diffpairs):
        """
        Make the element file, set the attributes
        """
        file_element = etree.Element("file")
        file_element.attrib["name"] = name
        file_element.attrib["gspairs"] = gspairs
        file_element.attrib["diffpairs"] = diffpairs

        return file_element

    def set_parags_testing_element(self, paragstesting):
        self.paragstesting = paragstesting

    def make_testrun_element(self, datetime):
        """
        Make the testrun element, set the attribute
        """
        testrun_element = etree.Element("testrun")
        testrun_element.attrib["datetime"] = datetime

        return testrun_element

    def make_paragstesting_element(self):
        """
        Make the paragstesting element
        """
        paragstesting_element = etree.Element("paragstesting")

        return paragstesting_element

    def insert_testrun_element(self, testrun):
        self.paragstesting.insert(0, testrun)

    def write_paragstesting_data(self):
        """
        Write the paragstesting data to a file
        """
        try:
            f = open(self.filename, "w")

            et = etree.ElementTree(self.paragstesting)
            et.write(f, pretty_print=True, encoding="utf-8",
                     xml_declaration=True)
            f.close()
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
            sys.exit(1)


class TmxGoldstandardTester:
    """
    A class to test the alignment pipeline against the tmx goldstandard
    """
    def __init__(self, testresult_filename, dateformat_addition=None):
        """
        Set the name where the testresults should be written
        Find all goldstandard tmx files
        """
        self.number_of_diff_lines = 0
        self.testresult_writer = TmxTestDataWriter(testresult_filename)
        if dateformat_addition is None:
            self.date = self.dateformat()
        else:
            self.date = self.dateformat() + dateformat_addition

    def set_number_of_diff_lines(self, diff_lines):
        """
        Increase the total number of difflines in this test run
        """
        self.number_of_diff_lines += diff_lines

    def get_number_of_diff_lines(self):
        return self.number_of_diff_lines

    def dateformat(self):
        """
        Get the date and time, 20111209-1234. Used in a testrun element
        """
        d = datetime.datetime.fromtimestamp(time.time())

        return d.strftime("%Y%m%d-%H%M")

    def run_test(self):
        # Make a testrun element, which will contain the result of the test
        testrun = self.testresult_writer.make_testrun_element(self.date)

        paralang = ""
        # Go through each tmx goldstandard file
        for want_tmx_file in self.find_goldstandard_tmx_files():
            print "testing", want_tmx_file, "..."

            # Calculate the parallel lang, to be used in parallelization
            if want_tmx_file.find('nob2sme') > -1:
                paralang = 'sme'
            else:
                paralang = 'nob'

            # Align files
            self.align_files(testrun, want_tmx_file, paralang)

        # All files have been tested, insert this run at the top of the
        # paragstest element
        self.testresult_writer.insert_testrun_element(testrun)
        # Write data to file
        self.testresult_writer.write_paragstesting_data()

    def align_files(self, testrun, want_tmx_file, paralang):
        """
        Align files
        Compare the tmx's of the result of this parallellization and
        the tmx of the goldstandard file
        Write the result to a file
        Write the diffs of these to tmx's to a separate file
        """

        # Compute the name of the main file to parallelize
        xml_file = self.compute_xmlfilename(want_tmx_file)

        parallelizer = Parallelize(xml_file, paralang)
        if parallelizer.divide_p_into_sentences() == 0:
            if parallelizer.parallelize_files() == 0:

                # The result of the alignment is a tmx element
                filelist = parallelizer.get_filelist()
                got_tmx = Tca2ToTmx(filelist)

                # This is the tmx element fetched from the goldstandard file
                want_tmx = Tmx(etree.parse(want_tmx_file))

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
        """
        Compute the name of the xmlfile which should be aligned
        """
        xml_file = want_tmx_file.replace('tmx/goldstandard/', 'converted/')
        xml_file = xml_file.replace('nob2sme', 'nob')
        xml_file = xml_file.replace('sme2nob', 'sme')
        xml_file = xml_file.replace('.toktmx', '.xml')

        return xml_file

    def write_diff_files(self, comparator, parallelizer, filename):
        """
        Write diffs to a jspwiki file
        """
        print "write_diff_files", filename
        filename = filename + '_' + self.date + '.jspwiki'
        dirname = os.path.join(
            os.path.dirname(self.testresult_writer.get_filename()),
            'tca2testing')

        try:
            f = open(os.path.join(dirname, filename), "w")
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
            sys.exit(1)

        f.write('!!!' + filename + '\n')
        f.write("!!TMX diff\n{{{\n")
        f.writelines(comparator.get_diff_as_text())
        f.write("\n}}}\n!!" + parallelizer.get_lang1() + " diff\n{{{\n")
        f.writelines(comparator.get_lang_diff_as_text(
            parallelizer.get_lang1()))
        f.write("\n}}}\n!!" + parallelizer.get_lang2() + " diff\n{{{\n")
        f.writelines(comparator.get_lang_diff_as_text(
            parallelizer.get_lang2()))
        f.write("\n}}}\n")
        f.close()

    def find_goldstandard_tmx_files(self):
        """
        Find the goldstandard tmx files, return them as a list
        """
        subp = subprocess.Popen(
            ['find', os.path.join(os.environ['GTFREE'],
                                  'prestable/toktmx/goldstandard'),
                '-name', '*.toktmx', '-print'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        (output, error) = subp.communicate()

        if subp.returncode != 0:
            print >>sys.stderr, 'Error when searching for goldstandard docs'
            print >>sys.stderr, error
            sys.exit(1)
        else:
            files = output.split('\n')
            return files[:-1]


class TmxFixer:
    """
    A class to reverse the langs and change the name of a tmx file if needed
    Possible errors of a tmx file:
    * the languages can be in the wrong order
    * the name is wrong
    * the file is placed in the wrong lang directory
    """

    def __init__(self, filetofix):
        """
        Input is the tmx file we should consider to fix
        """
        pass


class Toktmx2Tmx:
    """A class to make a tidied up version of toktmx files.
    Removes unwanted spaces around punctuation, parentheses and so on.
    """
    def read_toktmx_file(self, toktmx_file):
        """Reads a toktmx file, parses it, sets the tmx file name
        """
        self.tmxfile_name = toktmx_file.replace('toktmx', 'tmx')
        self.tmx = Tmx(etree.parse(toktmx_file))
        self.add_filename_iD()

    def add_filename_iD(self):
        """Add the tmx filename as an prop element in the header
        """
        prop = etree.Element('prop')
        prop.attrib['type'] = 'x-filename'
        prop.text = os.path.basename(self.tmxfile_name).decode('utf-8')

        root = self.tmx.get_tmx().getroot()

        for header in root.iter('header'):
            header.append(prop)

    def write_cleanedup_tmx(self):
        """Write the cleanup tmx
        """
        self.tmx.write_tmx_file(self.tmxfile_name)

    def clean_toktmx(self):
        """Do the cleanup of the toktmx file
        """
        self.tmx.remove_unwanted_space()
        self.tmx.remove_tu_with_empty_seg()

    def find_toktmx_files(self, dirname):
        """
        Find the toktmx files in dirname, return them as a list
        """
        subp = subprocess.Popen(
            ['find', dirname,
                '-name', '*.toktmx', '-print'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (output, error) = subp.communicate()

        if subp.returncode != 0:
            print >>sys.stderr, 'Error when searching for toktmx docs'
            print >>sys.stderr, error
            sys.exit(1)
        else:
            files = output.split('\n')
            return files[:-1]


def parse_options():
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Sentence align two files. Input is the document \
        containing the main language, and language to parallelize it with.')

    parser.add_argument('input_file', help="The input file")
    parser.add_argument('-p', '--parallel_language',
                        dest='parallel_language',
                        help="The language to parallelize the input \
                        document with",
                        required=True)

    args = parser.parse_args()
    return args


def main():
    args = parse_options()

    try:
        parallelizer = Parallelize(args.input_file, args.parallel_language)
    except IOError as e:
        print e.message
        sys.exit(1)

    print "Aligning", args.input_file, "and its parallel file"
    print "Adding sentence structure that tca2 needs ..."
    if parallelizer.divide_p_into_sentences() == 0:
        print "Aligning files ..."
        if parallelizer.parallelize_files() == 0:
            tmx = Tca2ToTmx(parallelizer.get_filelist())

            o_path, o_file = os.path.split(tmx.get_outfile_name())
            o_rel_path = o_path.replace(os.getcwd()+'/', '', 1)
            try:
                os.makedirs(o_rel_path)
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise
            print "Generating the tmx file", tmx.get_outfile_name()
            tmx.write_tmx_file(tmx.get_outfile_name())
