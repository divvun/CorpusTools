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
"""Convert bible xml files to the Giella xml format."""

from lxml import etree


def process_verse(verse_element):
    """Process the verse element found in bible xml documents.

    Args:
        verse_element (lxml.etree.Element): an etree element containing
            the verse element found in a bible xml document.

    Returns:
        (str): A string containing the text of the verse element.
    """
    if verse_element.tag != "verse":
        raise UserWarning(f"Unexpected element in verse: {verse_element.tag}")

    return verse_element.text


def process_section(section_element):
    """Process the section element found in the bible xml documents.

    Args:
        section_element (lxml.etree.Element): an etree element containing the
             section element found in a bible xml document.

    Returns:
        section (lxml.etree.Element): an etree element containing a
            corpus xml section.
    """
    section = etree.Element("section")

    title = etree.Element("p")
    title.set("type", "title")
    title.text = section_element.get("title")

    section.append(title)

    verses = []
    for element in section_element:
        if element.tag == "p":
            if verses:
                section.append(make_p(verses))
                verses = []
            section.append(process_p(element))
        elif element.tag == "verse":
            text = process_verse(element)
            if text:
                verses.append(text)
        else:
            raise UserWarning(f"Unexpected element in section: {element.tag}")

    section.append(make_p(verses))

    return section


def process_p(paragraph):
    """Convert bible xml verse elements to p elements.

    Args:
        paragraph (lxml.etree.Element): is a bible xml p element.

    Returns:
        (lxml.etree.Element): a Giella xml p element
    """
    verses = []
    for child in paragraph:
        text = process_verse(child)
        if text:
            verses.append(text)

    paragraph = etree.Element("p")
    paragraph.text = "\n".join(verses)

    return paragraph


def make_p(verses):
    """Convert verse strings to p element.

    Args:
        verses (list[str]): a list of strings

    Returns:
        (lxml.etree.Element): a Giella xml p element
    """
    paragraph = etree.Element("p")
    paragraph.text = "\n".join(verses)

    return paragraph


def process_chapter(chapter_element):
    """Convert a bible xml chapter to a Giella xml section one.

    Args:
        chapter_element (lxml.etree.Element): a bible xml chapter element

    Returns:
        (lxml.etree.Element): a Giella xml section element.
    """
    section = etree.Element("section")

    text_parts = []
    if chapter_element.get("number") is not None:
        text_parts.append(chapter_element.get("number"))
    if chapter_element.get("title") is not None:
        text_parts.append(chapter_element.get("title"))

    title = etree.Element("p")
    title.set("type", "title")
    title.text = " ".join(text_parts)

    section.append(title)

    for child in chapter_element:
        if child.tag == "section":
            section.append(process_section(child))
        elif child.tag == "verse":
            paragraph = etree.Element("p")
            paragraph.text = child.text
            section.append(paragraph)
        else:
            raise UserWarning(f"Unexpected element in chapter: {child.tag}")

    return section


def process_book(book_element):
    """Convert a bible xml book to a Giella xml section one.

    Args:
        book_element (lxml.etree.Element): a bible xml book element

    Returns:
        (lxml.etree.Element): a Giella xml section element.
    """
    section = etree.Element("section")

    title = etree.Element("p")
    title.set("type", "title")
    title.text = book_element.get("title")

    section.append(title)

    for chapter_element in book_element:
        if chapter_element.tag != "chapter":
            raise UserWarning(f"Unexpected element in book: {chapter_element.tag}")

        section.append(process_chapter(chapter_element))

    return section


def process_bible(bible_doc):
    """Convert a bible xml document to a Giella xml document.

    Args:
        bible_doc (etree.Element): the bible xml tree

    Returns:
        (lxml.etree.Element): a Giella xml body element.
    """
    body = etree.Element("body")

    for book in bible_doc.xpath(".//book"):
        body.append(process_book(book))

    return body


def convert2intermediate(filename):
    """Convert the bible xml to intermediate Giella xml format."""

    document = etree.Element("document")
    document.append(process_bible(etree.parse(filename)))

    return document
