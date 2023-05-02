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
#   Copyright © 2012-2023 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""This file contains classes fix converted documents."""

import os

HERE = os.path.dirname(__file__)


class LanguageDetector:
    """Detect and set the languages of a document."""

    def __init__(self, document, language_guesser):
        """Initialise the LanguageDetector class.

        Args:
            document (etree.Element): an etree element.
            language_guesser: a text_cat.Classifier.
        """
        self.document = document
        self.language_guesser = language_guesser

    @property
    def inlangs(self):
        """Return the predifined possible languages of the document."""
        inlangs = [
            language.get("{http://www.w3.org/XML/1998/namespace}" "lang")
            for language in self.document.findall("header/multilingual/language")
        ]
        if inlangs:
            inlangs.append(self.mainlang)

        return inlangs

    @property
    def mainlang(self):
        """Get the mainlang of the file."""
        return self.document.attrib["{http://www.w3.org/XML/1998/namespace}lang"]

    def set_paragraph_language(self, paragraph):
        """Set xml:lang of paragraph.

        Extract the text outside the quotes, use this text to set
        language of the paragraph.
        Set the language of the quotes in the paragraph.
        """
        if paragraph.get("{http://www.w3.org/XML/1998/namespace}lang") is None:
            paragraph_text = self.remove_quote(paragraph)
            if self.language_guesser is not None and self.language_guesser.get_langs(
                self.inlangs
            ):
                lang = self.language_guesser.classify(
                    paragraph_text, langs=self.inlangs
                )
                if lang != self.mainlang:
                    paragraph.set("{http://www.w3.org/XML/1998/namespace}lang", lang)

                self.set_span_language(paragraph)

        return paragraph

    def set_span_language(self, paragraph):
        """Set xml:lang of span element."""
        for element in paragraph.iter("span"):
            if element.get("type") == "quote":
                if element.text is not None:
                    lang = self.language_guesser.classify(
                        element.text, langs=self.inlangs
                    )
                    if lang != self.mainlang:
                        element.set("{http://www.w3.org/XML/1998/namespace}lang", lang)

    @staticmethod
    def remove_quote(paragraph):
        """Extract all text except the one inside <span type='quote'>."""
        text = ""
        for element in paragraph.iter():
            if (
                element.tag == "span"
                and element.get("type") == "quote"
                and element.tail is not None
            ):
                text = text + element.tail
            else:
                if element.text is not None:
                    text = text + element.text
                if element.tail is not None:
                    text = text + element.tail

        return text

    def detect_language(self):
        """Detect language in all the paragraphs in self.document."""
        if self.document.find("header/multilingual") is not None:
            for paragraph in self.document.iter("p"):
                self.set_paragraph_language(paragraph)
