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
#   Copyright © 2012-2026 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Convert ocr text files to the Giella xml format.

These files have the .ocr suffix. They are plain text files where
* lines starting with # are headings
* empty lines separate paragraphs
* words are often split over two lines, and must be joined again
"""

import codecs
import io
import re
from pathlib import Path
from typing import Iterable

from lxml import etree

from corpustools import basicconverter
from corpustools.pdfconverter import is_probably_hyphenated

HEADING_RE = re.compile(r"\s*#+\s*(?P<title>.*)")


def join_lines(lines: list[str]) -> str:
    """Join the lines of a paragraph into one string.

    Words split over two lines are joined again, and the hyphen that split
    them is removed.

    Args:
        lines: the lines belonging to one paragraph.

    Returns:
        The lines as one string.
    """
    paragraph = ""

    for line in lines:
        if not paragraph:
            paragraph = line
        elif is_probably_hyphenated(paragraph, line):
            # A word split over two lines, remove the hyphen
            paragraph = f"{paragraph[:-1]}{line}"
        elif paragraph.endswith("-"):
            # A real hyphen, e.g. in a compound, keep it
            paragraph = f"{paragraph}{line}"
        else:
            paragraph = f"{paragraph} {line}"

    return paragraph


class OcrContentConverter(basicconverter.BasicConverter):
    """Convert ocr text files to the Giella xml format."""

    def to_unicode(self) -> str:
        """Read a file into a unicode string.

        If the content of the file is not utf-8, pretend the encoding is
        latin1. The real encoding will be detected later.

        Returns:
            The decoded string.
        """
        try:
            content = codecs.open(self.orig.as_posix(), encoding="utf8").read()
        except ValueError:
            content = codecs.open(self.orig.as_posix(), encoding="latin1").read()

        return content.replace("\r\n", "\n")

    @staticmethod
    def make_element(text: str, is_heading: bool = False) -> etree._Element:
        """Make a p element.

        Args:
            text: the text the element should contain.
            is_heading: whether the text is a heading.

        Returns:
            An etree element.
        """
        element = etree.Element("p")
        if is_heading:
            element.set("type", "title")
        element.text = text

        return element

    def lines2xml(self, content: io.StringIO) -> Iterable[etree._Element]:
        """Turn headings and paragraphs into etree elements.

        Args:
            content: the content of the ocr_corrected document.

        Yields:
            An etree element.
        """
        valid_lines = (
            line.strip()
            for line_no, line in enumerate(content, start=1)
            if line_no not in self.metadata.skip_lines
        )

        buffer: list[str] = []
        for line in valid_lines:
            heading = HEADING_RE.fullmatch(line)

            if (not line or heading) and buffer:
                yield self.make_element(join_lines(buffer))
                buffer.clear()

            if heading:
                title = heading.group("title").strip()
                if title:
                    yield self.make_element(title, is_heading=True)
            elif line:
                buffer.append(line)

        if buffer:
            yield self.make_element(join_lines(buffer))

    def content2xml(self, content: io.StringIO) -> etree._Element:
        """Transform the ocr text to an intermediate xml document.

        Args:
            content: the content of the ocr_corrected document.

        Returns:
            An etree element.
        """
        document = etree.Element("document")
        etree.SubElement(document, "header")
        body = etree.SubElement(document, "body")

        for para in self.lines2xml(content):
            body.append(para)

        return document


def convert2intermediate(filename: Path) -> etree._Element:
    """Transform an .ocr file to an intermediate xml document.

    Args:
        filename: path of the file that should be converted.

    Returns:
        An etree element.
    """
    converter = OcrContentConverter(filename)

    return converter.content2xml(io.StringIO(converter.to_unicode()))
