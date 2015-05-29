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

from __future__ import unicode_literals

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
import text_cat
import argparse_version
import util
import generate_anchor_list
import tempfile


here = os.path.dirname(__file__)

def note(msg):
    print >>sys.stderr, msg.encode('utf-8')


class CorpusXMLFile:
    """
    A class that contains the info on a file to be parallellized, name
    and language
    """

    def __init__(self, name):
        self.name = name
        self.etree = etree.parse(name)
        self.root = self.etree.getroot()
        self.sanity_check()

    def sanity_check(self):
        if self.root.tag != "document":
            raise util.ArgumentError(
                "Expected Corpus XML file (output of convert2xml) with "
                "<document> as the root tag, got {} -- did you pass the "
                "wrong file?".format(
                    self.root.tag,))

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

    def get_basename_noext(self):
        """
        Return the basename of the file without the final .xml
        """
        root, _ = os.path.splitext(self.get_basename())
        return root

    def get_lang(self):
        """
        Get the lang of the file
        """
        return self.root.attrib[
            '{http://www.w3.org/XML/1998/namespace}lang']

    def get_word_count(self):
        word_count = self.root.find(".//wordcount")
        if word_count is not None:
            return word_count.text

    def get_genre(self):
        """
        @brief Get the genre from the xml file

        :returns: the genre as set in the xml file
        """
        if self.root.find(".//genre") is not None:
            return self.root.find(".//genre").attrib["code"]

    def get_ocr(self):
        """
        @brief Check if the ocr element exists

        :returns: the ocr element or None
        """
        return self.root.find(".//ocr")

    def get_parallel_basename(self, paralang):
        """
        Get the basename of the parallel file
        Input is the lang of the parallel file
        """
        parallel_files = self.root.findall(".//parallel_text")
        for p in parallel_files:
            if (p.attrib['{http://www.w3.org/XML/1998/namespace}lang'] ==
                    paralang):
                return p.attrib['location']

    def get_parallel_filename(self, paralang):
        """
        Infer the absolute path of the parallel file
        """
        if self.get_parallel_basename(paralang) is None:
            return None
        root, module, lang, genre, subdirs, _ = util.split_path(self.get_name())
        parallel_basename = '{}.xml'.format(
            self.get_parallel_basename(paralang))
        return apply(
            os.path.join,
            [root, module, paralang, genre, subdirs,
             parallel_basename]
        )


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
        translated_from = self.root.find(".//translated_from")

        if translated_from is not None:
            return translated_from.attrib[
                '{http://www.w3.org/XML/1998/namespace}lang']

    def remove_version(self):
        """
        Remove the version element
        This is often the only difference between the otherwise
        identical files in converted and prestable/converted
        """
        version_element = self.root.find(".//version")
        version_element.getparent().remove(version_element)

    def remove_skip(self):
        """
        Remove the skip element
        This contains text that is not wanted in e.g. sentence alignment
        """
        skip_list = self.root.findall(".//skip")

        for skip_element in skip_list:
            skip_element.getparent().remove(skip_element)

    def move_later(self):
        """
        Move the later elements to the end of the body element.
        """
        body = self.root.xpath("/document/body")[0]

        later_list = self.root.xpath(".//later")

        for later_element in later_list:
            body.append(later_element)

    def set_body(self, new_body):
        '''Replace the body element with new_body element
        '''
        if new_body.tag == 'body':
            oldbody = self.etree.find('.//body')
            oldbody.getparent().replace(oldbody, new_body)

    def write(self, file_name=None):
        '''Write self.etree
        '''
        if file_name is None:
            file_name = self.get_name()

        self.etree.write(file_name,
                         encoding='utf8',
                         pretty_print=True,
                         xml_declaration=True)


class SentenceDivider:
    """A class that takes a giellatekno xml document as input.
    It spits out an xml document that has divided the text inside the p tags
    into sentences, but otherwise is unchanged.
    Each sentence is encased in an s tag, and has an id number
    """
    def __init__(self, input_xmlfile):
        """Parse the input_xmlfile, set doc_lang to lang and read typos from
        the corresponding .typos file if it exists
        """
        self.set_up_input_file(input_xmlfile)
        self.sentence_counter = 0
        self.typos = {}
        self.document = None

        typosname = input_xmlfile.replace('.xml', '.typos')
        if os.path.isfile(typosname):
            t = typosfile.Typos(input_xmlfile.replace('.xml', '.typos'))
            self.typos.update(t.get_typos())

    def set_up_input_file(self, input_xmlfile):
        """
        Initialize the inputfile, skip those parts that are meant to be
        skipped, move <later> elements.
        """
        in_file = CorpusXMLFile(input_xmlfile)
        self.doc_lang = in_file.get_lang()

        in_file.move_later()
        in_file.remove_skip()
        self.input_etree = in_file.get_etree()

    def in_main_lang(self, elt):
        return self.doc_lang == elt.attrib.get(
            '{http://www.w3.org/XML/1998/namespace}lang',
            self.doc_lang)

    def process_all_paragraphs(self):
        """Go through all paragraphs in the etree and process them one by one.
        """
        if self.document is None:
            self.document = etree.Element('document')
            body = etree.Element('body')
            self.document.append(body)

            elts_doc_lang = filter(self.in_main_lang,
                                self.input_etree.findall('//p'))
            processed = self.process_elts(elts_doc_lang)
            body.extend(processed)
        return self.document

    def process_elts(self, elts):
        para_texts = ("".join(elt.xpath('.//text()'))
                      for elt in elts)
        preprocessed = self.preprocess_para_texts(para_texts)
        return map(self.process_one_para_text,
                   preprocessed)

    def write_result(self, outfile):
        """Write self.document to the given outfile name
        """
        o_path, o_file = os.path.split(outfile)
        o_rel_path = o_path.replace(os.getcwd()+'/', '', 1)
        try:
            if o_rel_path != '':
                os.makedirs(o_rel_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        with open(outfile, 'w') as sentence_file:
            et = etree.ElementTree(self.document)
            et.write(sentence_file,
                    pretty_print=True,
                    encoding="utf-8",
                    xml_declaration=True)

    def preprocess_para_texts(self, para_texts):
        """Run a list of paragraphs through preprocess.
        """
        # Temporarily intersperse an XML tag <SKIP/> between
        # paragraphs so that we can use just one call to preprocess,
        # but still have them split at the right points.
        replacements = [("<", "&lt;"),
                        (">", "&gt;"),
                        ('\n', ' '),]
        sanitized = (util.replace_all(replacements, p)
                     for p in para_texts)
        return self.ext_preprocess("\n<SKIP/>".join(sanitized)).split("<SKIP/>")

    def ext_preprocess(self, preprocess_input):
        """Send the text in preprocess_input into preprocess, return the
        result.
        If the process fails, exit the program
        """
        preprocess_command = util.get_preprocess_command(self.doc_lang)

        subp = subprocess.Popen(preprocess_command,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        (output, error) = subp.communicate(
            preprocess_input.encode('utf-8'))

        if subp.returncode != 0:
            note('ERROR: Could not divide into sentences')
            print >>sys.stderr, output
            print >>sys.stderr, error
            sys.exit()
        else:
            return output.decode('utf-8')

    pseudosent_re = re.compile(r"^[\W|\s]*$")

    def process_one_para_text(self, para_text):
        """Make sentences from the output of preprocess.
        Return a new paragraph containing the marked up sentences.
        """
        new_paragraph = etree.Element("p")

        sentence = []
        incomplete_sentences = ['.', '?', '!', ')', ']', '...', '…',
                                '"', '»', '”', '°', '', ':']
        words = para_text.split('\n')
        i = 0
        while i < len(words):
            word = words[i].strip()

            # If word exists in typos, replace it with the correction
            if word in self.typos:
                word = self.typos[word]

            sentence.append(word)
            if word in ['.', '?', '!']:
                while (i + 1 < len(words) and
                       words[i + 1].strip() in incomplete_sentences):
                    if words[i + 1] != '':
                        sentence.append(words[i + 1].strip())
                    i = i + 1

                # exclude pseudo-sentences, i.e. sentences that
                # don't contain any alphanumeric characters
                if not self.pseudosent_re.match(' '.join(sentence)):
                    new_paragraph.append(self.make_sentence(sentence))
                sentence = []

            i = i + 1

        # exclude pseudo-sentences, i.e. sentences that don't contain
        # any alphanumeric characters
        if (len(sentence) > 1
            and not self.pseudosent_re.match(' '.join(sentence))):
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

class Parallelize(object):
    """
    A class to parallelize two files
    Input is the xml file that should be parallellized and the language that it
    should be parallellized with.
    The language of the input file is found in the metadata of the input file.
    The other file is found via the metadata in the input file
    """

    def __init__(self, origfile1, lang2, anchor_file=None, quiet=False):
        """
        Set the original file name, the lang of the original file and the
        language that it should parallellized with.
        Parse the original file to get the access to metadata
        """
        self.quiet = quiet
        self.origfiles = []

        self.origfiles.append(CorpusXMLFile(
            os.path.abspath(origfile1)))

        para_file = self.origfiles[0].get_parallel_filename(lang2)
        if para_file is not None:
            self.origfiles.append(CorpusXMLFile(para_file))
        else:
            raise IOError("{} doesn't have a parallel file in {}".format(
                origfile1, lang2))

        self.consistency_check(self.origfiles[1], self.origfiles[0])

        # As stated in --help, we assume user-specified anchor file
        # has columns based on input files, where --parallel_file is
        # column two regardless of what file was translated from what,
        # therefore we set this before reshuffling:
        anchor_cols = [self.get_lang1(), self.get_lang2()]
        if self.is_translated_from_lang2():
            self.reshuffle_files()

        self.gal = self.setup_anchors(anchor_file, anchor_cols)

    def setup_anchors(self, path, cols):
        if path is None:
            path = os.path.join(os.environ['GTHOME'], 'gt/common/src/anchor.txt')
            cols = ['eng', 'nob', 'sme', 'fin', 'smj', 'sma']
            for l in {self.get_lang1(), self.get_lang2()} - set(cols):
                note("WARNING: {} not supported by default anchor list!".format(l))
        elif not self.quiet:
            assert len(cols)==2
            note("Assuming {} has the order {} / {}".format(path, cols[0], cols[1]))
        # The lang-codes are looked up in cols after reshuffling, so
        # returned pairs should have first part as lang1, second as lang2:
        return generate_anchor_list.GenerateAnchorList(
            self.get_lang1(), self.get_lang2(),
            cols, path)

    def consistency_check(self, f0, f1):
        """
        Warn if parallel_text of f0 is not f1
        """
        lang1 = f1.get_lang()
        para0 = f0.get_parallel_basename(lang1)
        base1 = f1.get_basename_noext()
        if para0 != base1:
            if para0 is None:
                note("WARNING: {} missing from {} parallel_texts in {}!".format(
                    base1, lang1, f0.get_name()))
            else:
                note("WARNING: {}, not {}, in {} parallel_texts of {}!".format(
                    para0, base1, lang1, f0.get_name()))

    def reshuffle_files(self):
        """
        Change the order of the files (so that the translated text is last)
        """
        tmp = self.origfiles[0]
        self.origfiles[0] = self.origfiles[1]
        self.origfiles[1] = tmp

    def get_outfile_name(self):
        """
        Compute the name of the final tmx file
        """

        orig_path_part = '/converted/{}/'.format(self.origfiles[0].get_lang())
        # First compute the part that shall replace /orig/ in the path
        replace_path_part = '/toktmx/{}2{}/'.format(
            self.origfiles[0].get_lang(),
            self.origfiles[1].get_lang())
        # Then set the outdir
        out_dirname = self.origfiles[0].get_dirname().replace(
            orig_path_part, replace_path_part)
        # Replace xml with tmx in the filename
        out_filename = self.origfiles[0].get_basename_noext() + '.toktmx'

        return os.path.join(out_dirname, out_filename)

    def get_origfiles(self):
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
        translated_from = self.origfiles[0].get_translated_from()

        if translated_from is not None:
            return translated_from == self.get_lang2()
        else:
            return False

    def parallelize_files(self):
        """
        Parallelize two files
        """
        if not self.quiet:
            note("Aligning files …")
        return self.align()

    def run_command(self, command):
        """
        Run a parallelize command and return its output
        """
        if not self.quiet:
            note("Running {}".format(" ".join(command)))
        subp = subprocess.Popen(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        (output, error) = subp.communicate()

        if subp.returncode != 0:
            raise Exception(
                'Could not parallelize {} and {} into sentences\n{}\n\n{}\n'.format(
                    self.get_origfiles()[0], self.get_origfiles()[1],
                    output, error))

        return output, error

    def align(self):
        raise NotImplementedError('You have to subclass and override align')


class ParallelizeHunalign(Parallelize):
    split_anchors_on = re.compile(r' *, *')
    def anchor_to_dict(self, words_pairs):
        # turn [("foo, bar", "fie")] into [("foo", "fie"), ("bar", "fie")]:
        expanded_pairs= [ (w1,w2)
                          for w1s, w2s in words_pairs
                          for w1 in re.split(self.split_anchors_on, w1s)
                          for w2 in re.split(self.split_anchors_on, w2s)
                          if w1 and w2]
        return expanded_pairs

    def make_dict(self):
        assert self.gal.lang1 == self.get_lang1()
        assert self.gal.lang2 == self.get_lang2()
        words_pairs = self.gal.read_anchors(quiet=self.quiet)
        expanded_pairs = self.anchor_to_dict(words_pairs)
        cleaned_pairs = [(w1.replace('*', ''), w2.replace('*', ''))
                         for w1,w2 in expanded_pairs]
        # Hunalign expects the _reverse_ format for the dictionary!
        # See Dictionary under http://mokk.bme.hu/resources/hunalign/
        return "\n".join(["{} @ {}".format(w2, w1)
                          for w1, w2 in cleaned_pairs])+"\n"

    def to_sents(self, origfile):
        divider = SentenceDivider(origfile.get_name())
        doc = divider.process_all_paragraphs()
        paragraphs = etree.ElementTree(doc).xpath('//p')
        sents = [["<p>"]+p.xpath('./s/text()') for p in paragraphs]
        return "\n".join(sum(sents, []))

    def align(self):
        """
        Parallelize two files using hunalign
        """
        def tmp():
            return tempfile.NamedTemporaryFile('w')
        with tmp() as dict_f, tmp() as sent0_f, tmp() as sent1_f:
            dict_f.write(self.make_dict().encode('utf-8'))
            sent0_f.write(self.to_sents(self.get_origfiles()[0]).encode('utf-8'))
            sent1_f.write(self.to_sents(self.get_origfiles()[1]).encode('utf-8'))
            dict_f.flush()
            sent0_f.flush()
            sent1_f.flush()

            command = ['hunalign',
                       '-utf',
                       '-realign',
                       '-text',
                       dict_f.name,
                       sent0_f.name, sent1_f.name,
            ]
            output, error = self.run_command(command)

        tmx = HunalignToTmx(self.get_origfiles(), output.decode('utf-8'))
        return tmx

class ParallelizeTCA2(Parallelize):
    def generate_anchor_file(self, outpath):
        """
        Generate an anchor file with lang1 and lang2.
        """
        assert self.gal.lang1 == self.get_lang1()
        assert self.gal.lang2 == self.get_lang2()
        self.gal.generate_file(outpath, quiet=self.quiet)

    def divide_p_into_sentences(self):
        """
        Tokenize the text in the given file and reassemble it again
        """
        for pfile in self.origfiles:
            infile = os.path.join(pfile.get_name())
            outfile = self.get_sent_filename(pfile)
            divider = SentenceDivider(infile)
            divider.process_all_paragraphs()
            divider.write_result(outfile)

    def get_sentfiles(self):
        return map(self.get_sent_filename, self.get_origfiles())

    def get_sent_filename(self, pfile):
        """
        Compute a name for the corpus-analyze output and tca2 input file
        Input is a CorpusXMLFile
        """
        origfilename = pfile.get_basename_noext()
        # Ensure we have 20 bytes of leeway to let TCA2 append
        # lang_sent_new.txt without going over the 255 byte limit:
        origfilename = self.crop_to_bytes(origfilename, (255 - 20))
        return os.path.join(os.environ['GTFREE'], 'tmp',
                            '{}{}_sent.xml'.format(
                                origfilename, pfile.get_lang()))

    def crop_to_bytes(name, max_bytes):
        """
        Ensure `name` is less than `max_bytes` bytes, without splitting in the
        middle of a wide byte.
        """
        while len(name.encode('utf-8')) > max_bytes:
            name = name[:-1]
        return name

    def align(self):
        """
        Parallelize two files using tca2
        """
        if not self.quiet:
            note("Adding sentence structure for the aligner …")
        self.divide_p_into_sentences()

        tca2_jar = os.path.join(here, 'tca2/dist/lib/alignment.jar')
        # util.sanity_check([tca2_jar])

        with tempfile.NamedTemporaryFile('w') as anchor_file:
            self.generate_anchor_file(anchor_file.name)
            anchor_file.flush()
            command = ['java',
                       '-Xms512m', '-Xmx1024m',
                       '-jar',
                       tca2_jar,
                       '-cli-plain',
                       '-anchor={}'.format(anchor_file.name),
                       '-in1={}'.format(self.get_sent_filename(self.get_origfiles()[0])),
                       '-in2={}'.format(self.get_sent_filename(self.get_origfiles()[1]))]
            output, error = self.run_command(command)
            # Ignore output, Tca2ToTmx guesses name of output-files from sentfiles
            # TODO: Use a tempfile.mkdtemp instead of hardcoded
            # GTFREE/tmp? Can't use tmpfiles for in1/in2, since output
            # file name is guessed based on them.

        tmx = Tca2ToTmx(self.get_origfiles(), self.get_sentfiles())
        return tmx


class Tmx(object):
    """
    A class that reads a tmx file, and implements a bare minimum of
    functionality to be able to compare two tmx's.
    It also contains functions to manipulate the tmx in several ways.
    """

    def __init__(self, tmx):
        """Input is a tmx element
        """
        self.tmx = tmx

        # TODO: not actually used apart from in tests, remove?
        # self.language_guesser = text_cat.Classifier(None)

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
        return string

    def tuv_to_string(self, tuv):
        """
        Extract the string from the tuv element
        """
        string = ""
        try:
            string = tuv[0].text.strip()
        except(AttributeError):
            pass

        return string

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
        space_punctuation = re.compile(
            "(?P<space>\s)(?P<punctuation>[\)\]\.»:;,])")
        # for every match in the result string, replace the match
        # (space+punctuation) with the punctuation part
        result = space_punctuation.sub(lambda match: match.group(
            'punctuation'), result)

        # regex to find punctuation followed by space
        punctuation_space = re.compile(
            "(?P<punctuation>[\[\(«])(?P<space>\s)+")
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
        out_dir = os.path.dirname(out_filename)
        if out_dir != '' and not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        with open(out_filename, "w") as tmx_file:
            string = etree.tostring(self.get_tmx(),
                                    pretty_print=True,
                                    encoding="utf-8",
                                    xml_declaration=True)
            tmx_file.write(string)

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

    def check_language(self, tu, lang):
        """Get the text of the tuv element with the given lang
        Run the text through the language guesser, return the result
        of this test
        """
        for tuv in tu:
            if tuv.get('{http://www.w3.org/XML/1998/namespace}lang') == lang:
                text = tuv[0].text
                test_lang = self.language_guesser.classify(text)
                if test_lang != lang:
                    return False

        return True


class AlignmentToTmx(Tmx):
    """
    A class to make tmx files based on the output of an aligner

    This just implements some common methods for the TCA2 and hunalign
    subclasses.
    """
    def __init__(self, origfiles):
        """
        Input is a list of CorpusXMLFile objects
        """
        self.origfiles = origfiles
        super(AlignmentToTmx, self).__init__(self.make_tmx())

    def make_tu(self, line1, line2):
        """
        Make a tmx tu element based on line1 and line2 as input
        """
        tu = etree.Element("tu")

        tu.append(self.make_tuv(line1, self.origfiles[0].get_lang()))
        tu.append(self.make_tuv(line2, self.origfiles[1].get_lang()))

        return tu

    def make_tuv(self, line, lang):
        """
        Make a tuv element given an input line and a lang variable
        """
        tuv = etree.Element("tuv")
        tuv.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = lang
        seg = etree.Element("seg")
        seg.text = line.strip()
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

    def make_tmx(self):
        """
        Make tmx file based on the output of the aligner
        """
        tmx = etree.Element("tmx")
        header = self.make_tmx_header(self.origfiles[0].get_lang())
        tmx.append(header)

        pfile1_data, pfile2_data = self.parse_alignment_results()

        body = etree.SubElement(tmx, "body")
        for line1, line2 in zip(pfile1_data, pfile2_data):
            tu = self.make_tu(line1, line2)
            body.append(tu)

        return tmx

    def parse_alignment_results(self):
        raise NotImplementedError(
            'You have to subclass and override parse_alignment_results')


class HunalignToTmx(AlignmentToTmx):
    """
    A class to make tmx files based on the output from hunalign
    """
    def __init__(self, origfiles, output):
        """
        Input is a list of CorpusXMLFile objects
        """
        self.output = output
        self.threshold = 0.0 # TODO: user-settable?
        super(HunalignToTmx, self).__init__(origfiles)

    def parse_alignment_results(self):
        """
        Return parsed output files of tca2
        """
        pairs = [line.split("\t")
                 for line in self.output.split("\n")
                 if line]
        pairs = filter(self.is_good_line,
                       pairs)

        src_lines = [self.clean_line(l[0])
                     for l in pairs]
        trg_lines = [self.clean_line(l[1])
                     for l in pairs]
        return src_lines, trg_lines

    def is_good_line(self, l):
        return (len(l) == 3 and
                l[0] != "<p>" and
                l[1] != "<p>" and
                l[2] > self.threshold)

    multi_sep = re.compile(r' *~~~ *')
    def clean_line(self, line):
        """
        Remove the ~~~ occuring in multi-sentence alignments
        """
        return self.multi_sep.sub(' ', line)

class Tca2ToTmx(AlignmentToTmx):
    """
    A class to make tmx files based on the output from tca2
    """
    def __init__(self, origfiles, sentfiles):
        """
        Input is a list of CorpusXMLFile objects
        """
        self.sentfiles = sentfiles
        super(Tca2ToTmx, self).__init__(origfiles)

    def parse_alignment_results(self):
        """
        Return parsed output files of tca2
        """
        pfile1_data = self.read_tca2_output(self.sentfiles[0])
        pfile2_data = self.read_tca2_output(self.sentfiles[1])
        return pfile1_data, pfile2_data

    def read_tca2_output(self, sentfile):
        """
        Read the output of tca2
        Input is a CorpusXMLFile
        """
        sentfile_name = sentfile.replace('.xml', '_new.txt')

        with open(sentfile_name, "r") as tca2_output:
            return map(self.remove_s_tag,
                       tca2_output.read().decode('utf-8').split('\n'))

    sregex = re.compile('<s id="[^ ]*">')
    def remove_s_tag(self, line):
        """
        Remove the s tags that tca2 has added
        """
        line = line.replace('</s>', '')
        line = self.sregex.sub('', line)
        return line


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
            note("I/O error({0}): {1}".format(error.errno, error.strerror))
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
        with open(self.filename, "w") as paragstesting:
            et = etree.ElementTree(self.paragstesting)
            et.write(paragstesting, pretty_print=True, encoding="utf-8",
                     xml_declaration=True)


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
            print "testing {} …".format(want_tmx_file)

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
        got_tmx = parallelizer.parallelize_files()

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
        print "write_diff_files {}".format(filename)
        filename = '{}_{}.jspwiki'.format(filename, self.date)
        dirname = os.path.join(
            os.path.dirname(self.testresult_writer.get_filename()),
            'tca2testing')

        with open(os.path.join(dirname, filename), "w") as diff_file:
            diff_file.write('!!!{}\n'.format(filename))
            diff_file.write("!!TMX diff\n{{{\n")
            diff_file.writelines(comparator.get_diff_as_text())
            diff_file.write("\n}}}\n!! diff\n{{{\n".format(parallelizer.get_lang1()))
            diff_file.writelines(comparator.get_lang_diff_as_text(
                parallelizer.get_lang1()))
            diff_file.write("\n}}}\n!!{} diff\n{{{\n".format(parallelizer.get_lang2()))
            diff_file.writelines(comparator.get_lang_diff_as_text(
                parallelizer.get_lang2()))
            diff_file.write("\n}}}\n")

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
            note('ERROR: When searching for goldstandard docs:')
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
            note('ERROR: When searching for toktmx docs:')
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

    parser.add_argument('input_file',
                        help="The input filename")
    parser.add_argument('output_file',
                        help="Optionally an output filename. Defaults to "
                        "toktmx/{LANGA}2{LANGB}/{GENRE}/.../{BASENAME}.toktmx",
                        default=None,
                        nargs='?')
    parser.add_argument('-f', '--force',
                        help="Overwrite output file if it already exists."
                        "The default is to skip parallelizing existing files.",
                        action="store_true")
    parser.add_argument('-q', '--quiet',
                        help="Don't mention anything out of the ordinary.",
                        action="store_true")
    parser.add_argument('-a', '--aligner',
                        choices=['hunalign', 'tca2'],
                        default='tca2',
                        help="Either hunalign or tca2 (the default).")
    parser.add_argument('-d', '--dict',
                        default=None,
                        help="Use a different bilingual seed dictionary. Must have "
                        "two columns, with input_file language first, and "
                        "--parallel_language second, separated by `/'. By default, "
                        "$GTHOME/gt/common/src/anchor.txt is used, but this file "
                        "only supports pairings between sme/sma/smj/fin/eng/nob. ")
    parser.add_argument('-p', '--parallel_language',
                        help="The language to parallelize the input "
                        "document with",
                        required=True)

    args = parser.parse_args()
    return args


def main():
    args = parse_options()

    try:
        if args.aligner == "hunalign":
            parallelizer = ParallelizeHunalign(origfile1 = args.input_file,
                                               lang2 = args.parallel_language,
                                               anchor_file = args.dict,
                                               quiet = args.quiet)
        elif args.aligner == "tca2":
            parallelizer = ParallelizeTCA2(origfile1 = args.input_file,
                                           lang2 = args.parallel_language,
                                           anchor_file = args.dict,
                                           quiet = args.quiet)

    except IOError as e:
        print e.message
        sys.exit(1)

    if args.output_file is None:
        outfile = parallelizer.get_outfile_name()
    elif args.output_file == "-":
        outfile = "/dev/stdout"
    else:
        outfile = args.output_file
    if outfile != "/dev/stdout" and os.path.exists(outfile):
        if args.force:
            note("{} already exists, overwriting!".format(outfile))
        else:
            note("{} already exists, skipping ...".format(outfile))
            sys.exit(1)

    if not args.quiet:
        note("Aligning {} and its parallel file".format(args.input_file))
    tmx = parallelizer.parallelize_files()

    if not args.quiet:
        note("Generating the tmx file {}".format(outfile))
    tmx.write_tmx_file(outfile)
    if not args.quiet:
        note("Wrote {}".format(outfile))
