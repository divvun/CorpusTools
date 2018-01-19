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
#   Copyright © 2011-2018 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://divvun.no & http://giellatekno.uit.no
#
"""Classes and functions to sentence align two files."""

from __future__ import absolute_import, print_function, unicode_literals

import io
import os
import sys

import regex
from lxml import etree

from corpustools import ccat, modes, util

HERE = os.path.dirname(__file__)


def to_plain_text(lang, filename):
    """Turn an xml formatted file into clean text.

    Arguments:
        lang (str): three character name of main language of document.
        filename (str): name of the xmlfile

    Raises:
        UserWarning: if there is no text, raise a UserWarning

    Returns:
        str: the content of ccat output
    """
    xml_printer = ccat.XMLPrinter(lang=lang, all_paragraphs=True)
    xml_printer.parse_file(filename)
    text = xml_printer.process_file().getvalue()
    if text:
        return text
    else:
        raise UserWarning('Empty file {}'.format(filename))


class SentenceDivider(object):
    """A class to divide plain text output into sentences.

    Uses hfst-tokenise as the motor for this purpose.

    Attributes:
        stops (list of str): tokens that imply where a sentence ends.
        lang (str): three character language code
        relative_path (str): relative path to where files needed by
            modes.xml are found.
        tokeniser (modes.Pipeline): tokeniser pipeline
    """

    stops = [';', '!', '?', '.', '..', '...', '¶', '…']

    def __init__(self,
                 lang,
                 relative_path=os.path.join(os.getenv('GTHOME'), 'langs')):
        """Set the files needed by the tokeniser.

        Arguments:
            lang (str): language the analyser can tokenise
        """
        self.lang = 'nob' if lang in ['nno', 'swe'] else lang
        self.relative_path = relative_path
        self.tokeniser = self.setup_pipeline('tokenise')

    def setup_pipeline(self, pipeline_name):
        """Setup the tokeniser pipeline.

        Returns:
            modes.Pipeline: a tokeniser pipeline that receives plain text
                input and outputs a token per line.
        """
        modefile = etree.parse(
            os.path.join(os.path.dirname(__file__), 'xml/modes.xml'))
        pipeline = modes.Pipeline(
            mode=modefile.find('.//mode[@name="{}"]'.format(pipeline_name)),
            relative_path=os.path.join(self.relative_path, self.lang))
        pipeline.sanity_check()

        return pipeline

    @staticmethod
    def clean_sentence(sentence):
        """Remove cruft from a sentence.

        Arguments:
            sentence (str): a raw sentence, warts and all

        Returns:
            str: a cleaned up sentence, looking the way a sentence should.
        """
        return sentence.replace('\n', '').strip()

    def make_sentences(self, ccat_output):
        """Turn ccat output into cleaned up sentences.

        Arguments:
            ccat_output (str): plain text output of ccat.

        Yields:
            str: a cleaned up sentence
        """
        preprocessed = self.tokeniser.run(ccat_output.encode('utf8'))

        token_buffer = []
        for token in io.StringIO(preprocessed):
            token_buffer.append(token)
            if token.strip() in self.stops:
                yield self.clean_sentence(''.join(token_buffer))
                token_buffer[:] = []

    def make_valid_sentences(self, ccat_output):
        """Turn ccat output into full sentences.

        Arguments:
            ccat_output (str): the plain text output of ccat

        Returns:
            list of str: The ccat output has been turned into a list
                of full sentences.
        """
        sentences = [
            sentence.replace(' ¶', '')
            for sentence in self.make_sentences(ccat_output)
            if sentence not in self.stops
        ]

        invalid_sentence_re = regex.compile(r'^\W+$')
        valid_sentences = []
        for sentence in sentences:
            if invalid_sentence_re.match(sentence) and valid_sentences:
                valid_sentences[-1] = ''.join([valid_sentences[-1] + sentence])
            else:
                valid_sentences.append(sentence)

        return valid_sentences


class TrainingCorpusMaker(object):
    """Turn analysed giella xml files into training corpus.

    Filter out all sentences containing words unknown to the
    giella fst analysers.

    Attributes:
        only_words: regex catching word made up of letters.
        xml_printer (ccat.XMLPrinter): extracts the dependency analysis
            from the giella xml files.
    """

    only_words = regex.compile(r'\p{L}+')
    xml_printer = ccat.XMLPrinter(dependency=True)

    def parse_dependency(self, text):
        """Parse the dependency element found in a giella xml file.

        Arguments:
            text (str): contains the dependency element of a giella xml file.

        Yields:
            str: a sentence containing only words known to the giella fst
                analysers, that contain at least a word as identified by
                the only_words regex.
        """
        sentence_buffer = []
        uff_buffer = []
        for line in io.StringIO(text):
            line = line.rstrip()
            if line == ':' or line == ':\\n':
                sentence_buffer.append(' ')
            elif line.startswith(':'):
                uff_buffer.append(line)
            elif line.startswith('"'):
                sentence_buffer.append(line[2:-2])
            elif 'CLB' in line:
                if not ('".' not in line and '"¶"' not in line
                        and '"?"' not in line and '"!"' not in line
                        and '"…"' not in line):
                    if uff_buffer:
                        for uff in uff_buffer:
                            util.print_frame(uff)
                    else:
                        sentence_line = ''.join(sentence_buffer).replace(
                            '¶', '').strip()
                        if self.only_words.search(sentence_line):
                            yield sentence_line
                    uff_buffer[:] = []
                    sentence_buffer[:] = []
            elif '" ?' in line:
                uff_buffer.append(line)

    def file_to_sentences(self, filename):
        """Turn a giella xml into a list of sentences.

        Arguments:
            filename (str): name of the giella xml file containing a
                dependency element.

        Returns:
            list of str
        """
        self.xml_printer.parse_file(filename)
        text = self.xml_printer.process_file().getvalue()
        if text.strip():
            return [
                sentence for sentence in self.parse_dependency(text)
                if sentence
            ]
        else:
            return []

    def pytextcat_corpus(self):
        """Turn the free and bound corpus into a pytextcat training corpus."""
        with open('{}.txt'.format(sys.argv[1]), 'w') as corpusfile:
            for corpus in [
                    os.path.join(os.getenv('GTFREE'), 'analysed', sys.argv[1]),
                    os.path.join(
                        os.getenv('GTBOUND'), 'analysed', sys.argv[1])
            ]:
                # util.print_frame(corpus)
                for root, _, files in os.walk(corpus):
                    # util.print_frame('\t', root)
                    for file_ in files:
                        util.print_frame('\n\t\t', file_)
                        if file_.endswith('.xml'):
                            corpusfile.write('\n'.join(
                                self.file_to_sentences(
                                    os.path.join(root, file_))))
                            corpusfile.write('\n')


def main():
    """Turn the corpus into a pytextcat training corpus."""
    sentence_maker = TrainingCorpusMaker()
    sentence_maker.pytextcat_corpus()
