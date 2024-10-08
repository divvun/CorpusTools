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
import re
from copy import deepcopy

from lxml import etree

from corpustools import decode, util

HERE = os.path.dirname(__file__)


class DocumentFixer:
    """Fix the content of a Giella xml document.

    Receive a stringified etree from one of the raw converters,
    replace ligatures, fix the encoding and return an etree with correct
    characters
    """

    newstags = re.compile(
        r"(@*logo:|[\s+\']*@*\s*ingres+[\.:]*|.*@*.*bilde\s*\d*:|\W*(@|"
        r"LED|bilde)*tekst:|@*foto:|@fotobyline:|@*bildetitt:|"
        r"<pstyle:bilde>|<pstyle:ingress>|<pstyle:tekst>|"
        r"@*Samleingress:*|tekst/ingress:|billedtekst:|.@tekst:)",
        re.IGNORECASE,
    )
    titletags = re.compile(
        r"\s*@m.titt[\.:]|\s*@*stikk:|Mellomtittel:|@*(stikk\.*|"
        r"under)titt(el)*:|@ttt:|\s*@*[utm]*[:\.]*tit+:|<pstyle:m.titt>|"
        r"undertittel:",
        re.IGNORECASE,
    )
    headertitletags = re.compile(
        r"(\s*@*(led)*tittel:|\s*@*titt(\s\d)*:|@LEDtitt:|"
        r"<pstyle:tittel>|@*(hoved|over)titt(el)*:)",
        re.IGNORECASE,
    )
    bylinetags = re.compile(
        r"(<pstyle:|\s*@*)[Bb]yline[:>]*\s*(\S+:)*", re.UNICODE | re.IGNORECASE
    )
    boldtags = re.compile(r"@bold\s*:")

    def __init__(self, document):
        """Initialise the DocumentFixer class."""
        self.root = document

    def get_etree(self):
        """Get the root of the xml document."""
        return self.root

    def compact_ems(self):
        """Compact consecutive em elements into a single em if possible."""
        word = re.compile(r"\w+", re.UNICODE)
        for element in self.root.iter("p"):
            if len(element.xpath(".//em")) > 1:
                lines = []
                for emphasis in element.iter("em"):
                    next_elt = emphasis.getnext()
                    if (
                        next_elt is not None
                        and next_elt.tag == "em"
                        and (emphasis.tail is None or not word.search(emphasis.tail))
                    ):
                        if emphasis.text is not None:
                            lines.append(emphasis.text.strip())
                        emphasis.getparent().remove(emphasis)
                    else:
                        if emphasis.text is not None:
                            lines.append(emphasis.text.strip())
                        emphasis.text = " ".join(lines)
                        if emphasis.tail is not None:
                            emphasis.tail = f" {emphasis.tail}"
                        del lines[:]

    def soft_hyphen_to_hyph_tag(self):
        """Replace soft hyphen chars with hyphen tags."""
        for element in self.root.iter("p"):
            self.replace_shy(element)

    def replace_shy(self, element):
        """Replace shy with a hyph element.

        Args:
            element (etree.Element): an etree element
        """
        for child in element:
            self.replace_shy(child)

        text = element.text
        if text is not None:
            parts = text.split("­")
            if len(parts) > 1:
                element.text = parts[0]
                for index, part in enumerate(parts[1:]):
                    hyph = etree.Element("hyph")
                    hyph.tail = part
                    element.insert(index, hyph)

        text = element.tail
        if text is not None:
            parts = text.split("­")
            if len(parts) > 1:
                element.tail = parts[0]
                for part in parts[1:]:
                    hyph = etree.Element("hyph")
                    hyph.tail = part
                    element.getparent().append(hyph)

    def insert_spaces_after_semicolon(self):
        """Insert space after semicolon where needed."""
        irritating_words_regex = re.compile(
            "(govv(a|en|ejeaddji):)([^ ])", re.UNICODE | re.IGNORECASE
        )
        for child in self.root.find(".//body"):
            self.insert_space_after_semicolon(child, irritating_words_regex)

    def insert_space_after_semicolon(self, element, irritating_words_regex):
        """Insert space after words needing it.

        Args:
            element (etree.Element): an etree element
            irritating_words_regex (re.Pattern): regex
        """
        if element.text is not None:
            element.text = irritating_words_regex.sub(r"\1 \3", element.text)
        for child in element:
            self.insert_space_after_semicolon(child, irritating_words_regex)
        if element.tail is not None:
            element.tail = irritating_words_regex.sub(r"\1 \3", element.tail)

    def replace_ligatures(self):
        """Replace unwanted chars."""
        replacements = {
            "[dstrok]": "đ",
            "[Dstrok]": "Đ",
            "[tstrok]": "ŧ",
            "[Tstrok]": "Ŧ",
            "[scaron]": "š",
            "[Scaron]": "Š",
            "[zcaron]": "ž",
            "[Zcaron]": "Ž",
            "[ccaron]": "č",
            "[Ccaron]": "Č",
            "[eng": "ŋ",
            " ]": "",
            "Ď": "đ",  # cough
            "ď": "đ",  # cough
            "\x03": "",
            "\x04": "",
            "\x07": "",
            "\x08": "",
            "\x0F": "",
            "\x10": "",
            "\x11": "",
            "\x13": "",
            "\x14": "",
            "\x15": "",
            "\x17": "",
            "\x18": "",
            "\x1A": "",
            "\x1B": "",
            "\x1C": "",
            "\x1D": "",
            "\x1E": "",
            "ﬁ": "fi",
            "ﬂ": "fl",
            "ﬀ": "ff",
            "ﬃ": "ffi",
            "ﬄ": "ffl",
            "ﬅ": "ft",
        }

        for element in self.root.iter("p"):
            if element.text:
                for key, value in replacements.items():
                    element.text = element.text.replace(key + " ", value)
                    element.text = element.text.replace(key, value)

    def replace_bad_unicode(self):
        """Replace some chars in an otherwise 'valid utf-8' document.

        These chars e.g. 'valid utf-8' (don't give UnicodeDecodeErrors), but
        we still want to replace them to what they most likely were
        meant to be.

        :param content: a unicode string
        :returns: a cleaned up unicode string
        """
        # u'š'.encode('windows-1252') gives '\x9a', which sometimes
        # appears in otherwise utf-8-encoded documents with the
        # meaning 'š'
        replacements = [
            ("\x9a", "š"),
            ("\x8a", "Š"),
            ("\x9e", "ž"),
            ("\x8e", "Ž"),
        ]
        for element in self.root.iter("p"):
            if element.text:
                element.text = util.replace_all(replacements, element.text)

    def fix_lang(self, element, lang):
        """Replace invalid accents with valid ones for the sms language."""

        sms_space = re.compile(
            r"(?P<unwanted_space>\s+)"
            r"(?P<sms_modifiers>[ʼʹ])",  # MODIFIER LETTER APOSTROPHE,
            # MODIFIER LETTER PRIME
            re.UNICODE,
        )

        replacement_pairs = {
            "sms": [
                ("\u2019", "\u02BC"),  # RIGHT SINGLE QUOTATION MARK,
                # MODIFIER LETTER APOSTROPHE
                ("\u0027", "\u02BC"),  # apostrophe,
                # MODIFIER LETTER APOSTROPHE
                ("\u2032", "\u02B9"),  # PRIME, MODIFIER LETTER PRIME
                ("\u00B4", "\u02B9"),  # ACUTE ACCENT,
                # MODIFIER LETTER PRIME
                ("\u0301", "\u02BC"),  # COMBINING ACUTE ACCENT,
                # MODIFIER LETTER PRIME
            ],
            "mns": [
                ("\uf50e", "А̄"),  # CYRILLIC VOWELS WITH LENGTH MARK
                ("\uf50f", "а̄"),
                ("\uf510", "Е̄"),
                ("\uf511", "е̄"),
                ("\uf512", "Ё̄"),  #
                ("\uf513", "ё̄"),
                ("\uf517", "О̄"),  # 17? Just guessing
                ("\uf518", "О̄"),  # CYRILLIC LONG CAPITAL O
                ("\uf519", "о̄"),  # CYRILLIC LONG SMALL O
                ("\uf520", "Ы̄"),  #
                ("\uf521", "ы̄"),  #
                ("\uf522", "Э̄"),
                ("\uf523", "э̄"),
                ("\uf52c", "Ю̄"),  #
                ("\uf52d", "ю̄"),
                ("\uf528", "Я̄"),
                ("\uf529", "я̄"),
            ],
        }

        if element.text:
            element.text = util.replace_all(replacement_pairs[lang], element.text)
            if lang == "sms":
                element.text = sms_space.sub(r"\g<sms_modifiers>", element.text)
        if element.tail:
            element.tail = util.replace_all(replacement_pairs[lang], element.tail)
            if lang == "sms":
                element.tail = sms_space.sub(r"\g<sms_modifiers>", element.tail)
        for child in element:
            self.fix_lang(child, lang)

    def fix_body_encoding(self, mainlang):
        """Replace wrongly encoded saami chars with proper ones.

        Send a stringified version of the body into the EncodingGuesser class.
        It returns the same version, but with fixed characters.
        Parse the returned string, insert it into the document
        """
        self.replace_ligatures()

        body = self.root.find("body")
        # Weird bug(?) in MacOS, the end tag of document lingers …
        body_string = etree.tostring(body, encoding="unicode").replace(
            "</document>", ""
        )
        body.getparent().remove(body)

        encoding = decode.guess_body_encoding(body_string, mainlang)

        try:
            body = etree.fromstring(decode.decode_para(encoding, body_string))
        except UnicodeEncodeError as error:
            raise UserWarning(str(error)) from error
        self.root.append(body)

        if mainlang in ["sms", "mns"]:
            for paragraph in body.iter("p"):
                self.fix_lang(paragraph, lang=mainlang)

    def fix_title_person(self, encoding):
        """Fix encoding problems."""
        title = self.root.find(".//title")
        if title is not None and title.text is not None:
            text = title.text

            util.print_frame(encoding)
            title.text = decode.decode_para(encoding, text)

        persons = self.root.findall(".//person")
        for person in persons:
            if person is not None:
                lastname = person.get("lastname")

                if encoding == "mac-sami_to_latin1":
                    lastname = lastname.replace("‡", "á")
                    lastname = lastname.replace("Œ", "å")

                person.set("lastname", decode.decode_para(encoding, lastname))

                firstname = person.get("firstname")

                if encoding == "mac-sami_to_latin1":
                    firstname = firstname.replace("‡", "á")
                    firstname = firstname.replace("Œ", "å")

                person.set("firstname", decode.decode_para(encoding, firstname))

    @staticmethod
    def get_quote_list(text):
        """Get list of quotes from the given text.

        Args:
            text (str): string

        Returns:
            (list[tuple[int, int]]): A list of span tuples containing
                indexes to quotes found in text.
        """
        unwanted = r"[^:,!?.\s]"
        quote_regexes = [
            re.compile('"{0}.+?{0}"'.format(unwanted)),
            re.compile("«.+?»"),
            re.compile("“.+?”"),
            re.compile("”{0}.+?{0}”".format(unwanted)),
        ]
        quote_list = [
            m.span()
            for quote_regex in quote_regexes
            for m in quote_regex.finditer(text)
        ]
        quote_list.sort()

        return quote_list

    @staticmethod
    def append_quotes(element, text, quote_list):
        """Append quotes to an element.

        Args:
            text (str): the plain text of the element.
            quote_list (list of tuple of int): A list of span tuples containing
                indexes to quotes found in text.
        """
        for index in range(0, len(quote_list)):
            span = etree.Element("span")
            span.set("type", "quote")
            span.text = text[quote_list[index][0] : quote_list[index][1]]
            if index + 1 < len(quote_list):
                span.tail = text[quote_list[index][1] : quote_list[index + 1][0]]
            else:
                span.tail = text[quote_list[index][1] :]
            element.append(span)

    def _detect_quote(self, element):
        """Insert span elements around quotes.

        Args:
            element (etree.Element): an etree element.
        """
        newelement = deepcopy(element)

        element.text = ""
        for child in element:
            child.getparent().remove(child)

        text = newelement.text
        if text:
            quote_list = self.get_quote_list(text)
            if quote_list:
                element.text = text[0 : quote_list[0][0]]
                self.append_quotes(element, text, quote_list)
            else:
                element.text = text

        for child in newelement:
            if child.tag == "span" and child.get("type") == "quote":
                element.append(child)
            else:
                element.append(self._detect_quote(child))

            if child.tail:
                text = child.tail
                quote_list = self.get_quote_list(text)
                if quote_list:
                    child.tail = text[0 : quote_list[0][0]]
                    self.append_quotes(element, text, quote_list)

        return element

    def detect_quotes(self):
        """Detect quotes in all paragraphs."""
        for paragraph in self.root.iter("p"):
            paragraph = self._detect_quote(paragraph)

    def calculate_wordcount(self):
        """Count the words in the file."""
        plist = [
            etree.tostring(paragraph, method="text", encoding="unicode")
            for paragraph in self.root.iter("p")
        ]

        return str(len(re.findall(r"\S+", " ".join(plist))))

    @staticmethod
    def _make_element(name, text, attributes=None):
        """Make an xml element.

        :param name: the name of the element
        :param text: the content of the element
        :param attributes: the elements attributes

        :returns: lxml.etree.Element
        """
        attributes = attributes or {}
        element = etree.Element(name)
        for key in attributes:
            element.set(key, attributes[key])

        element.text = text

        return element

    def _fix_emphasises(self):
        for emphasis in self.root.iter("em"):
            paragraph = emphasis.getparent()
            if not len(emphasis) and emphasis.text:
                if self.bylinetags.match(emphasis.text):
                    line = self.bylinetags.sub("", emphasis.text).strip()
                    unknown = self.root.find(".//unknown")
                    if unknown is not None:
                        person = etree.Element("person")
                        person.set("lastname", line)
                        person.set("firstname", "")
                        unknown.getparent().replace(unknown, person)
                        paragraph.getparent().remove(paragraph)
                elif self.titletags.match(emphasis.text):
                    emphasis.text = self.titletags.sub("", emphasis.text).strip()
                    paragraph.set("type", "title")
                elif self.newstags.match(emphasis.text):
                    emphasis.text = self.newstags.sub("", emphasis.text).strip()

    def _add_paragraph(self, line, index, paragraph, attributes):
        if line:
            index += 1
            paragraph.getparent().insert(
                index, self._make_element("p", line, attributes=attributes)
            )

        return index

    def _add_emphasis(self, index, line, attributes, paragraph):
        index += 1
        element = etree.Element("p")
        element.append(self._make_element("em", line, attributes))

        paragraph.getparent().insert(index, element)

        return index

    def _handle_line(self, line, index, lines, paragraph):
        if self.newstags.match(line):
            index = self._add_paragraph(
                " ".join(lines).strip(), index, paragraph, paragraph.attrib
            )
            del lines[:]

            lines.append(self.newstags.sub("", line))

        elif self.bylinetags.match(line):
            index = self._add_paragraph(
                " ".join(lines).strip(), index, paragraph, paragraph.attrib
            )
            del lines[:]

            unknown = self.root.find(".//unknown")
            if unknown is not None:
                person = etree.Element("person")
                person.set("lastname", self.bylinetags.sub("", line).strip())
                person.set("firstname", "")

                unknown.getparent().replace(unknown, person)

        elif self.boldtags.match(line):
            index = self._add_paragraph(
                " ".join(lines).strip(), index, paragraph, paragraph.attrib
            )
            index = self._add_emphasis(
                index, self.boldtags.sub("", line).strip(), {"type": "bold"}, paragraph
            )
            del lines[:]

        elif line.startswith("@kursiv:"):
            index = self._add_paragraph(
                " ".join(lines).strip(), index, paragraph, paragraph.attrib
            )
            index = self._add_emphasis(
                index,
                line.replace("@kursiv:", "").strip(),
                {"type": "italic"},
                paragraph,
            )
            del lines[:]

        elif self.headertitletags.match(line):
            index = self._add_paragraph(
                " ".join(lines).strip(), index, paragraph, paragraph.attrib
            )
            del lines[:]

            header = self.root.find(".//header")
            title = header.find("./title")
            if title is not None and title.text is None:
                title.text = self.headertitletags.sub("", line).strip()

            index = self._add_paragraph(
                self.headertitletags.sub("", line).strip(),
                index,
                paragraph,
                {"type": "title"},
            )
        elif self.titletags.match(line):
            index = self._add_paragraph(
                " ".join(lines).strip(), index, paragraph, paragraph.attrib
            )
            del lines[:]

            index += 1
            paragraph.getparent().insert(
                index,
                self._make_element(
                    "p", self.titletags.sub("", line).strip(), {"type": "title"}
                ),
            )
        elif line == "" and lines:
            index = self._add_paragraph(
                " ".join(lines).strip(), index, paragraph, paragraph.attrib
            )
            del lines[:]

        else:
            lines.append(line)

        return index

    def _fix_paragraphs(self):
        for paragraph in self.root.iter("p"):
            if not len(paragraph) and paragraph.text:
                index = paragraph.getparent().index(paragraph)
                lines = []

                for line in paragraph.text.split("\n"):
                    index = self._handle_line(line, index, lines, paragraph)

                index = self._add_paragraph(
                    " ".join(lines).strip(), index, paragraph, paragraph.attrib
                )

                paragraph.getparent().remove(paragraph)

    def fix_newstags(self):
        """Convert newstags found in text to xml elements."""
        self._fix_emphasises()
        self._fix_paragraphs()
