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

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lxml import etree


@dataclass
class AvvirAuthor:
    """A class representing an Ávvir author."""

    forname: str
    surname: str


@dataclass
class AvvirTaggedText:
    """A class representing an Ávvir tagged text."""

    text: str
    tag: str


def convert_article(avvir_doc: Path) -> etree.Element:
    """Convert an Ávvir article to the giellatekno xml format.

    Args:
        avvir_doc: the etree that should be manipulated.

    Returns:
        The resulting etree.Element after the conversion.
    """
    tree = etree.Element("document")
    body = etree.SubElement(tree, "body")  # noqa: F841

    return tree


def convert2intermediate(filename: Path) -> etree.Element:
    """Convert Ávvir xml files to the giellatekno xml format.

    The root node in an Ávvir document is article.
    article nodes contains one or more story nodes.
    story nodes contain one or more p nodes.
    p nodes contain span, br and (since 2013) p nodes.
    """

    return convert_article(filename)


def convert_author(author_dict: dict[str, Any]) -> AvvirAuthor | None:
    """Convert an Ávvir author to AvvirAuthor.

    Args:
        fullname: the full name of the Ávvir author.

    Returns:
        The resulting AvvirAuthor object after the conversion.
    """
    fullname = author_dict.get("content", {}).get("name", [{}])[0].get("insert", "")
    if not fullname:
        return None

    name_parts = fullname.split(" ")
    return AvvirAuthor(forname=" ".join(name_parts[:-1]), surname=name_parts[-1])


def convert_tagged_text(faktatittel_dict: dict[str, Any]) -> AvvirTaggedText:
    """Convert an Ávvir faktatittel to AvvirTaggedText.

    Args:
        faktatittel_dict: the faktatittel of the Ávvir document.

    Returns:
        The resulting AvvirTaggedText object after the conversion.
    """
    texts = (
        text_part.get("insert", "")
        for text_part in faktatittel_dict.get("content", {}).get("text", [{}])
    )
    return AvvirTaggedText(text="".join(texts), tag=faktatittel_dict["identifier"])


def convert_image(image_dict: dict[str, Any]) -> AvvirTaggedText:
    """Convert an Ávvir image to AvvirTaggedText.

    Args:
        image_dict: the image of the Ávvir document.

    Returns:
        The resulting AvvirTaggedText object after the conversion.
    """
    texts = (
        text_part.get("insert", "")
        for text_part in image_dict.get("content", {}).get("caption", [{}])
    )
    return AvvirTaggedText(text="".join(texts), tag=image_dict["identifier"])


def convert_slideshow(slideshow_dict: dict[str, Any]) -> AvvirTaggedText:
    """Convert an Ávvir slideshow to AvvirTaggedText.

    Avoid duplicate text by using a dictionary comprehension to extract unique text
    parts from the slideshow's containers.

    Args:
        slideshow_dict: the slideshow of the Ávvir document.

    Returns:
        The resulting AvvirTaggedText object after the conversion.
    """
    texts = {
        text_part.get("insert", ""): None
        for images in slideshow_dict.get("containers", {}).get("slideshow", [{}])
        for text_part in images.get("content", {}).get("caption", [{}])
    }
    return AvvirTaggedText(
        text=" ".join(texts.keys()), tag=slideshow_dict["identifier"]
    )
