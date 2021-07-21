# -*- coding: utf-8 -*-

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
#   Copyright © 2012-2020 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
u"""Convert Ávvir-files to the Giella xml format."""

from lxml import etree


def remove_identical_ids(avvir_doc):
    """Remove identical ids.

    Args:
        avvir_doc (etree.Element): the etree that should be manipulated.
    """
    story_ids = set()
    for story in avvir_doc.xpath(".//story[@id]"):
        story_id = story.get("id")
        if story_id not in story_ids:
            story_ids.add(story_id)
        else:
            story.getparent().remove(story)


def insert_element(para, text, position):
    """Insert a new element in p's parent.

    Args:
        p: an lxml element, it is a story/p element
        text: (unicode) string
        position: (integer) the position inside p's parent where the new
                    element is inserted

    Returns:
        position: (integer)
    """
    if text is not None and text.strip() != "":
        new_p = etree.Element("p")
        new_p.text = text
        grandparent = para.getparent()
        grandparent.insert(grandparent.index(para) + position, new_p)
        position += 1

    return position


def convert_sub_p(para):
    """Convert p element found inside story/p elements.

    These elements contain erroneous text that an editor has removed.
    This function removes p.text and saves p.tail

    Args:
        p: an lxml element, it is a story/p element
    """
    for sub_p in para.findall(".//p"):
        previous = sub_p.getprevious()
        if previous is None:
            parent = sub_p.getparent()
            if sub_p.tail is not None:
                if parent.text is not None:
                    parent.text = parent.text + sub_p.tail
                else:
                    parent.text = sub_p.tail
        else:
            if sub_p.tail is not None:
                if previous.tail is not None:
                    previous.tail = previous.tail + sub_p.tail
                else:
                    previous.tail = sub_p.tail
        para.remove(sub_p)


def convert_subelement(para):
    """Convert subelements of story/p elements to p elements.

    Args:
        p: an lxml element, it is a story/p element
    """
    position = 1
    for subelement in para:
        position = insert_element(para, subelement.text, position)

        for subsubelement in subelement:
            for text in [subsubelement.text, subsubelement.tail]:
                position = insert_element(para, text, position)

        position = insert_element(para, subelement.tail, position)

        para.remove(subelement)


def convert_p(avvir_doc):
    """Convert story/p elements to one or more p elements.

    Args:
        avvir_doc (etree.Element): the etree that should be manipulated.
    """
    for para in avvir_doc.findall("./story/p"):
        if para.get("class") is not None:
            del para.attrib["class"]

        convert_sub_p(para)
        convert_subelement(para)

        if para.text is None or para.text.strip() == "":
            story = para.getparent()
            story.remove(para)


def convert_story(avvir_doc):
    """Convert story elements in to giellatekno xml elements.

    Args:
        avvir_doc (etree.Element): the etree that should be manipulated.
    """
    for title in avvir_doc.findall('.//story[@class="Tittel"]'):
        for para in title.findall("./p"):
            para.set("type", "title")

        del title.attrib["class"]
        del title.attrib["id"]

        title.tag = "section"

    for title in avvir_doc.findall('.//story[@class="Undertittel"]'):
        for para in title.findall("./p"):
            para.set("type", "title")

        del title.attrib["class"]
        del title.attrib["id"]

        title.tag = "section"

    for story in avvir_doc.findall("./story"):
        parent = story.getparent()
        for i, para in enumerate(story.findall("./p")):
            parent.insert(parent.index(story) + i + 1, para)

        parent.remove(story)


def convert_article(avvir_doc):
    u"""The root element of an Ávvir doc is article, rename it to body.

    Args:
        avvir_doc (etree.Element): the etree that should be manipulated.

    Returns:
        etree.Element: The document root of the basic Giella xml document.
    """
    avvir_doc.tag = "body"
    document = etree.Element("document")
    document.append(avvir_doc)

    return document


def convert2intermediate(filename):
    u"""Convert Ávvir xml files to the giellatekno xml format.

    The root node in an Ávvir document is article.
    article nodes contains one or more story nodes.
    story nodes contain one or more p nodes.
    p nodes contain span, br and (since 2013) p nodes.
    """
    avvir_doc = etree.parse(filename).getroot()

    remove_identical_ids(avvir_doc)
    convert_p(avvir_doc)
    convert_story(avvir_doc)

    return convert_article(avvir_doc)
