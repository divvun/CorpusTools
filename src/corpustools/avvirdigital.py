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
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from lxml import etree

type SerializedXml = etree.Element | Sequence[SerializedXml]

# Control characters that are not allowed in XML 1.0 (tab, LF and CR are kept)
CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")


def remove_control_chars(text: str) -> str:
    """Remove control characters that can not be part of an XML document."""
    return CONTROL_CHAR_RE.sub("", text)


@dataclass
class AvvirAuthor:
    """A class representing an Ávvir author."""

    forname: str
    surname: str


@dataclass
class AvvirTaggedText:
    """A class representing an Ávvir tagged text."""

    quote_tags: ClassVar[tuple[str, ...]] = ("quote",)
    title_tags: ClassVar[tuple[str, ...]] = (
        "faktatittel",
        "mellom",
        "title",
        "subtitle",
        "crosshead",
    )
    text: str
    tag: str

    def to_xml(self) -> etree.Element:
        """Convert the AvvirTaggedText to an XML element."""
        element = etree.Element("p")

        if self.tag in self.quote_tags:
            quote_element = etree.SubElement(element, "span")
            quote_element.text = self.text
            quote_element.set("type", "quote")
            return element

        if self.tag in self.title_tags:
            element.set("type", "title")

        element.text = self.text
        return element


@dataclass
class AvvirContainer:
    """A class representing an Ávvir container."""

    main_content: list[AvvirTaggedText]
    captions: list[AvvirTaggedText]
    slideshows: list[AvvirTaggedText]
    containers: list["AvvirContainer"]

    """A class representing an Ávvir container."""

    def serialize(self) -> list[etree.Element]:
        """Serialize the AvvirContainer to a list of lists of XML elements."""
        return flatten(
            [
                [content.to_xml() for content in self.main_content],
                [caption.to_xml() for caption in self.captions],
                [slideshow.to_xml() for slideshow in self.slideshows],
                flatten([container.serialize() for container in self.containers]),
            ]
        )


@dataclass
class AvvirDocument:
    """A class representing an Ávvir document."""

    authors: list[AvvirAuthor] | None
    title: str
    main_content: list[AvvirTaggedText]
    captions: list[AvvirTaggedText]
    slideshows: list[AvvirTaggedText]
    containers: list[AvvirContainer]

    @classmethod
    def from_json(cls, avvir_json: dict[str, Any]) -> "AvvirDocument":
        """Create an AvvirDocument from a JSON dictionary."""

        return cls(
            authors=extract_authors(avvir_json),
            title=extract_title(avvir_json),
            main_content=extract_main_content(avvir_json),
            captions=extract_captions(avvir_json),
            slideshows=extract_slideshows(avvir_json),
            containers=extract_containers(avvir_json),
        )

    def serialize(self) -> list[etree.Element]:
        """Serialize the AvvirDocument to a list of XML elements."""
        return flatten(
            [
                [content.to_xml() for content in self.main_content],
                [caption.to_xml() for caption in self.captions],
                [slideshow.to_xml() for slideshow in self.slideshows],
                flatten([container.serialize() for container in self.containers]),
            ]
        )


def extract_title(avvir_json: dict[str, Any]) -> str:
    """Extract the title from an Ávvir JSON dictionary.

    Args:
        avvir_json: the JSON dictionary representing the Ávvir document.

    Returns:
        The title of the Ávvir document.
    """
    for content in avvir_json["data"]["content"]:
        if content["identifier"] in ["title", "crosshead"]:
            if "content" in content and "text" in content["content"]:
                return remove_control_chars(
                    "".join(
                        [
                            text.get("insert", "")
                            for text in content.get("content").get("text", [{}])
                        ]
                    )
                )
    return ""


def extract_authors(avvir_json: dict[str, Any]) -> list[AvvirAuthor]:
    """Extract the authors from an Ávvir JSON dictionary."""
    return [
        convert_author(content)
        for content in avvir_json["data"]["content"]
        if content["identifier"] == "author"
    ]


def extract_main_content(avvir_json: dict[str, Any]) -> list[AvvirTaggedText]:
    """Extract the main content from an Ávvir JSON dictionary."""
    return [
        convert_tagged_text(content)
        for content in avvir_json["data"]["content"]
        if content["identifier"]
        in [
            "faktatittel",
            "faktatekst",
            "mellom",
            "title",
            "subtitle",
            "quote",
            "crosshead",
            "body",
            "intro",
        ]
    ]


def extract_captions(avvir_json: dict[str, Any]) -> list[AvvirTaggedText]:
    """Extract the captions from an Ávvir JSON dictionary."""
    return [
        convert_image(content)
        for content in avvir_json["data"]["content"]
        if content["identifier"] == "image"
    ]


def extract_slideshows(avvir_json: dict[str, Any]) -> list[AvvirTaggedText]:
    """Extract the slideshows from an Ávvir JSON dictionary."""
    return [
        convert_slideshow(content)
        for content in avvir_json["data"]["content"]
        if content["identifier"] == "slideshow"
    ]


def extract_containers(avvir_json: dict[str, Any]) -> list[AvvirContainer]:
    """Extract the containers from an Ávvir JSON dictionary."""
    return [
        convert_container(content)
        for content in avvir_json["data"]["content"]
        if content["identifier"] == "container"
    ]


def convert2intermediate(filepath: Path) -> etree.Element:
    """Convert Ávvir json files to the giellatekno xml format."""
    avvir_doc = AvvirDocument.from_json(
        json.loads(filepath.read_text(encoding="utf-8"))
    )
    tree = etree.Element("document")
    header = etree.SubElement(tree, "header")
    title = etree.SubElement(header, "title")
    title.text = avvir_doc.title

    for author in avvir_doc.authors or []:
        if not (author.forname or author.surname):
            continue
        author_element = etree.SubElement(header, "author")
        etree.SubElement(
            author_element,
            "person",
            firstname=author.forname,
            lastname=author.surname,
        )

    body = etree.SubElement(tree, "body")

    for element in avvir_doc.serialize():
        if "".join(element.itertext()).strip():
            body.append(element)
    return tree


def convert_author(author_dict: dict[str, Any]) -> AvvirAuthor:
    """Convert an Ávvir author to AvvirAuthor.

    Args:
        fullname: the full name of the Ávvir author.

    Returns:
        The resulting AvvirAuthor object after the conversion.
    """
    fullname = remove_control_chars(
        author_dict.get("content", {}).get("name", [{}])[0].get("insert", "")
    )

    name_parts = fullname.split(" ")
    return AvvirAuthor(forname=" ".join(name_parts[:-1]), surname=name_parts[-1])


def convert_tagged_text(content_dict: dict[str, Any]) -> AvvirTaggedText:
    """Convert an Ávvir faktatittel to AvvirTaggedText.

    Args:
        content_dict: the content of the Ávvir document.

    Returns:
        The resulting AvvirTaggedText object after the conversion.
    """
    texts = (
        text_part.get("insert", "")
        for text_part in content_dict.get("content", {}).get("text", [{}])
    )
    return AvvirTaggedText(
        text=remove_control_chars("".join(texts)), tag=content_dict["identifier"]
    )


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
    return AvvirTaggedText(
        text=remove_control_chars("".join(texts)), tag=image_dict["identifier"]
    )


def convert_slideshow(slideshow_dict: dict[str, Any]) -> AvvirTaggedText:
    """Convert an Ávvir slideshow to AvvirTaggedText.

    Avoid duplicate text by using dict.fromkeys to extract unique, non-empty text
    parts, in order, from the slideshow's containers.

    Args:
        slideshow_dict: the slideshow of the Ávvir document.

    Returns:
        The resulting AvvirTaggedText object after the conversion.
    """
    texts = dict.fromkeys(
        text_part.get("insert", "")
        for images in slideshow_dict.get("containers", {}).get("slideshow", [{}])
        for text_part in images.get("content", {}).get("caption", [{}])
        if text_part.get("insert", "")
    )
    return AvvirTaggedText(
        text=remove_control_chars(" ".join(texts)), tag=slideshow_dict["identifier"]
    )


def convert_container(container_dict: dict[str, Any]) -> AvvirContainer:
    """Convert an Ávvir container to AvvirContainer.

    Args:
        container_dict: the container of the Ávvir document.

    Returns:
        The resulting AvvirContainer object after the conversion.
    """
    container_content_ids = {
        "body",
        "faktatekst",
        "faktatittel",
        "footer",
        "intro",
        "mellom",
        "title",
    }

    known_keys = {"containers", "identifier", "content", "styles", "id"}
    if set(container_dict.keys()) != known_keys:
        raise ValueError(
            "Unknown container structure. "
            f"Got: {[key for key in container_dict.keys() if key not in known_keys]}"
        )

    return AvvirContainer(
        main_content=[
            convert_tagged_text(content)
            for content in container_dict.get("content", [])
            if content["identifier"] in container_content_ids
        ],
        captions=extract_captions(container_dict),
        slideshows=extract_slideshows(container_dict),
        containers=extract_containers(container_dict),
    )


def flatten(items: Iterable[SerializedXml]) -> list[etree.Element]:
    """Flatten a nested structure of XML elements and sequences."""
    result: list[etree.Element] = []

    for item in items:
        if etree.iselement(item):
            result.append(item)
        else:
            result.extend(flatten(item))

    return result
