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
#   Copyright © 2011-2020 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://divvun.no & http://giellatekno.uit.no
#
"""Classes and functions to sentence align two files."""

from __future__ import absolute_import, print_function, unicode_literals

import io
import os

import regex
from lxml import etree

from corpustools import ccat, modes


def to_plain_text(lang, filename):
    """Turn an xml formatted file into clean text.

    Args:
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
        raise UserWarning("Empty file {}".format(filename))


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

    stops = [";", "!", "?", ".", "..", "...", "¶", "…"]

    def __init__(self, lang, giella_prefix=None):
        """Set the files needed by the tokeniser.

        Args:
            lang (str): language the analyser can tokenise
        """
        self.tokeniser = modes.Pipeline("tokenise", lang, giella_prefix)

    @staticmethod
    def clean_sentence(sentence):
        """Remove cruft from a sentence.

        Args:
            sentence (str): a raw sentence, warts and all

        Returns:
            str: a cleaned up sentence, looking the way a sentence should.
        """
        return sentence.replace("\n", "").strip()

    def make_sentences(self, ccat_output):
        """Turn ccat output into cleaned up sentences.

        Args:
            ccat_output (str): plain text output of ccat.

        Yields:
            str: a cleaned up sentence
        """
        preprocessed = self.tokeniser.run(ccat_output.encode("utf8"))

        token_buffer = []
        for token in io.StringIO(preprocessed):
            token_buffer.append(token)
            if token.strip() in self.stops:
                yield self.clean_sentence("".join(token_buffer))
                token_buffer[:] = []

    def make_valid_sentences(self, ccat_output):
        """Turn ccat output into full sentences.

        Args:
            ccat_output (str): the plain text output of ccat

        Returns:
            list of str: The ccat output has been turned into a list
                of full sentences.
        """
        sentences = [
            sentence.replace(" ¶", "")
            for sentence in self.make_sentences(ccat_output)
            if sentence not in self.stops
        ]

        invalid_sentence_re = regex.compile(r"^\W+$")
        valid_sentences = []
        for sentence in sentences:
            if invalid_sentence_re.match(sentence) and valid_sentences:
                valid_sentences[-1] = "".join([valid_sentences[-1] + sentence])
            else:
                valid_sentences.append(sentence)

        return valid_sentences
