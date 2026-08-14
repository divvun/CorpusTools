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
"""Convert bible sfm (usfm) files to the Giella xml format."""

import re

from lxml import etree

# The marker at the start of a line, e.g. \p, \mt1 or \v
LINE_MARKER_RE = re.compile(r"\s*\\(?P<name>[a-z]+[0-9]*)\s*")

# Footnotes (\f … \f*), cross references (\x … \x*) and published verse
# numbers (\vp … \vp*) are not part of the running text, so everything from
# the opening to the closing marker is thrown away.
NOTE_RE = re.compile(r"\\(f|x|vp)\b.*?\\\1\*", re.DOTALL)

# The verse number following a \v marker
VERSE_NUMBER_RE = re.compile(r"^[0-9]+[-0-9]*\s*")

# Letters written with a combining macron in the 1895 bible, but with a
# caron in modern orthography
MACRON_RE = re.compile("([cCsSʒƷ])̄")
CARON_LETTERS = {"c": "č", "C": "Č", "s": "š", "S": "Š", "ʒ": "ǯ", "Ʒ": "Ǯ"}

# Markers starting a paragraph of running text
TEXT_MARKERS = set(["p", "m"])

# Markers starting a p element containing a title
TITLE_MARKERS = set(["mt1", "mt2", "s1"])

# \s2 holds the summary of a chapter, which is running text of its own
SUMMARY_MARKER = "s2"

# Markers carrying no text of interest: file identification, running header,
# table of contents and published chapter number
IGNORED_MARKERS = set(["id", "ide", "h", "toc1", "toc2", "toc3", "cp"])


def macron_to_caron(text):
    """Replace letters written with a macron with their caron equivalents.

    The 1895 bible writes č, š and ǯ as c, s and ʒ with a combining macron.

    Args:
        text (str): a text string.

    Returns:
        (str): the string with carons instead of macrons.
    """
    return MACRON_RE.sub(lambda match: CARON_LETTERS[match.group(1)], text)


def clean_text(text):
    """Normalise the whitespace and the macron letters of a text string.

    Args:
        text (str): a text string.

    Returns:
        (str): the normalised string.
    """
    return macron_to_caron(" ".join(text.split()))


def parse_line(line):
    """Split an sfm line into its marker and its text.

    Footnotes and cross references are removed from the text.

    Args:
        line (str): a line from an sfm file.

    Returns:
        (tuple[str | None, str]): the name of the marker (None if the line
            does not start with a marker) and the text of the line.
    """
    line = NOTE_RE.sub("", line)
    match = LINE_MARKER_RE.match(line)

    if match is None:
        return None, clean_text(line)

    return match.group("name"), clean_text(line[match.end() :])


def add_text(paragraph, text):
    """Add text to a p element, one verse per line.

    Args:
        paragraph (lxml.etree.Element): a Giella xml p element.
        text (str): the text that should be added.
    """
    if not text:
        return

    paragraph.text = f"{paragraph.text}\n{text}" if paragraph.text else text


def remove_empty(body):
    """Remove p and section elements without text from the body.

    Args:
        body (lxml.etree.Element): a Giella xml body element.
    """
    for paragraph in body.findall(".//p"):
        if paragraph.text is None:
            paragraph.getparent().remove(paragraph)

    for section in body.findall("section"):
        if not len(section):
            body.remove(section)


def parse_sfm(lines):
    """Convert the lines of an sfm file to a Giella xml document.

    Each chapter becomes a section holding one p element, where each verse
    is a line. Titles end the p element, so a chapter with titles in the
    middle of it gets one p element per title.

    Args:
        lines (collections.abc.Iterable[str]): the lines of an sfm file.

    Returns:
        (lxml.etree.Element): a Giella xml document element.
    """
    document = etree.Element("document")
    body = etree.SubElement(document, "body")
    section = etree.SubElement(body, "section")
    paragraph = None

    for line in lines:
        marker, text = parse_line(line)

        if marker in IGNORED_MARKERS:
            continue

        if marker == "c":
            section = etree.SubElement(body, "section")
            paragraph = None
        elif marker in TITLE_MARKERS:
            title = etree.SubElement(section, "p")
            title.set("type", "title")
            add_text(title, text)
            paragraph = None
        elif marker == SUMMARY_MARKER:
            summary = etree.SubElement(section, "p")
            add_text(summary, text)
            paragraph = None
        elif marker in TEXT_MARKERS or marker == "v" or marker is None:
            if marker == "v":
                text = VERSE_NUMBER_RE.sub("", text)
            if paragraph is None:
                paragraph = etree.SubElement(section, "p")
            add_text(paragraph, text)
        else:
            raise UserWarning(f"Unknown sfm marker: \\{marker}")

    remove_empty(body)

    return document


def convert2intermediate(filename):
    """Convert an sfm file to the intermediate Giella xml format."""

    with open(filename, encoding="utf-8") as sfm_file:
        return parse_sfm(sfm_file)
