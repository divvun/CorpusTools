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
#   Copyright © 2026 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Convert Ávvir-json-files to the Giella xml format."""

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint

from lxml import etree


@dataclass
class AvvirAuthor:
    """A class representing an Ávvir author."""

    forname: str
    surname: str


def convert_article(avvir_doc: Path) -> etree.Element:
    """Convert an Ávvir article to the giellatekno xml format.

    Args:
        avvir_doc: the etree that should be manipulated.

    Returns:
        The resulting etree.Element after the conversion.
    """
    tree = etree.Element("document")
    body = etree.SubElement(tree, "body")

    return tree


def convert2intermediate(filename: Path) -> etree.Element:
    """Convert Ávvir xml files to the giellatekno xml format.

    The root node in an Ávvir document is article.
    article nodes contains one or more story nodes.
    story nodes contain one or more p nodes.
    p nodes contain span, br and (since 2013) p nodes.
    """

    return convert_article(filename)


def content_list(avvir_json: dict) -> None:
    known_content_identifiers = []

    interesting_content_identifiers = [
        "author",
    ]

    to_handle = [
        "body",
        "faktatekst",
        "faktatittel",
        "intro",
        "mellom",
        "subtitle",
        "title",
        "slideshow",
        "image",
        "container",
        "quote",
    ]
    not_interesting_content_identifiers = [
        "embed",
        "tags",
        "video",
    ]
    hits = 0
    for content in avvir_json["data"]["content"]:
        if hits > 10:
            break
        if content["identifier"] in interesting_content_identifiers:
            print(f"Interesting content identifier: {content['identifier']}")
            pprint(content)
            print()
            hits += 1


def convert_author(fullname: str) -> AvvirAuthor:
    """Convert an Ávvir author to the giellatekno xml format.

    Args:
        fullname: the full name of the Ávvir author.

    Returns:
        The resulting AvvirAuthor object after the conversion.
    """
    name_parts = fullname.split(" ")
    return AvvirAuthor(forname=" ".join(name_parts[:-1]), surname=name_parts[-1])


def main():
    json_dir = Path(sys.argv[1])
    known_versions = ["2.2", "2.3"]

    for json_file in json_dir.glob("*.digital"):
        avvir_json = json.loads(json_file.read_text(encoding="utf-8"))
        if avvir_json["version"] not in known_versions:
            print(f"Unknown version: {avvir_json['version']}")
        content_list(avvir_json)
