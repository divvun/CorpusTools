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
#   Copyright © 2020 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Convert bible usx xml files to giella xml format."""

from lxml import etree


def char_to_span(document):
    for char in document.iter("char"):
        for key in char.attrib:
            del char.attrib[key]
        char.tag = "span"
        char.set("type", "quote")


def remove_unwanted(document):
    for unwanted in ["note", "verse", "book", "table"]:
        etree.strip_elements(document, unwanted, with_tail=False)


def usx_to_document(usx_document):
    document = etree.Element("document")
    body = etree.SubElement(document, "body")
    body.text = "\n"

    for child in usx_document:
        if child.tag == "chapter":
            section = etree.SubElement(body, "section")
            section.text = "\n"
            section.tail = "\n"
        elif child.tag == "para":
            if child.get("style") in ["s", "p", "nb", "mt", "mt1", "ms", "sp", "ip"]:
                try:
                    paragraph = etree.SubElement(section, "p")
                except UnboundLocalError:
                    section = etree.SubElement(body, "section")
                    section.text = "\n"
                    section.tail = "\n"
                    paragraph = etree.SubElement(section, "p")

                if child.get("style") in ["s", "mt", "ms", "mt1"]:
                    paragraph.set("type", "title")
                if child.text:
                    paragraph.text = " ".join(child.text.split())
                for grandchild in child:
                    paragraph.append(grandchild)
            elif child.get("style") in ["m", "q", "q1", "q2", "pi"]:
                try:
                    if paragraph.get("type") == "title":
                        paragraph = etree.SubElement(section, "p")
                except UnboundLocalError:
                    paragraph = etree.SubElement(section, "p")
                if len(paragraph):
                    if not paragraph[-1].tail:
                        paragraph[-1].tail = " ".join(child.text.split())
                    else:
                        paragraph[-1].tail = (
                            f"{paragraph[-1].tail} " f'{" ".join(child.text.split())}'
                        )
                else:
                    if not paragraph.text:
                        try:
                            paragraph.text = " ".join(child.text.split())
                        except AttributeError:
                            pass
                    else:
                        try:
                            paragraph.text = (
                                f"{paragraph.text} " f'{" ".join(child.text.split())}'
                            )
                        except AttributeError:
                            pass
            elif child.get("style") in ["li", "li1", "li2"]:
                paragraph = etree.SubElement(section, "p")
                paragraph.set("type", "listitem")
                if child.text:
                    paragraph.text = " ".join(child.text.split())
                for grandchild in child:
                    paragraph.append(grandchild)

            elif child.get("style") in ["b", "qa", "mr", "qc", "ide", "pc", "periph"]:
                pass
            elif child.get("style") in ["rem", "toc1", "toc2", "toc3", "h"]:
                # Should possibly handled further
                pass
            else:
                print(etree.tostring(child, encoding="unicode"))
        else:
            print(etree.tostring(child, encoding="unicode"))

    return document


def convert2intermediate(filename):
    """Convert usx xml files to the giellatekno xml format."""
    usx_doc = etree.parse(filename).getroot()
    remove_unwanted(usx_doc)
    char_to_span(usx_doc)

    return usx_to_document(usx_doc)
