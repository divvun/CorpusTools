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
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lxml import etree

type SerializedXml = etree.Element | Sequence[SerializedXml]


@dataclass
class AvvirAuthor:
    """A class representing an Ávvir author."""

    forname: str
    surname: str


@dataclass
class AvvirTaggedText:
    """A class representing an Ávvir tagged text."""

    quote_tags = ["quote"]
    title_tags = ["faktatittel", "mellom", "title", "subtitle", "crosshead"]
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

    def serialize(self) -> list[list[etree.Element]]:
        """Serialize the AvvirContainer to a dictionary."""
        return [
            [content.to_xml() for content in self.main_content],
            [caption.to_xml() for caption in self.captions],
            [slideshow.to_xml() for slideshow in self.slideshows],
            flatten([container.serialize() for container in self.containers]),
        ]


@dataclass
class AvvirDocument:
    """A class representing an Ávvir document."""

    authors: list[AvvirAuthor] | None
    title: AvvirTaggedText
    main_content: list[AvvirTaggedText]
    captions: list[AvvirTaggedText]
    slideshows: list[AvvirTaggedText]
    containers: list[AvvirContainer]

    @classmethod
    def from_json(cls, avvir_json: dict) -> "AvvirDocument":  # type: ignore
        """Create an AvvirDocument from a JSON dictionary."""

        return cls(
            authors=extract_authors(avvir_json),  # type: ignore
            title=extract_title(avvir_json),  # type: ignore
            main_content=extract_main_content(avvir_json),  # type: ignore
            captions=extract_captions(avvir_json),  # type: ignore
            slideshows=extract_slideshows(avvir_json),  # type: ignore
            containers=extract_containers(avvir_json),  # type: ignore
        )

    def serialize(self) -> list[list[etree.Element]]:
        """Serialize the AvvirDocument to a dictionary."""
        return [
            [content.to_xml() for content in self.main_content],
            [caption.to_xml() for caption in self.captions],
            [slideshow.to_xml() for slideshow in self.slideshows],
            flatten([container.serialize() for container in self.containers]),
        ]


def extract_title(avvir_json: dict[str, Any]) -> str:
    """Extract the title from an Ávvir JSON dictionary.

    Args:
        avvir_json: the JSON dictionary representing the Ávvir document.

    Returns:
        The title of the Ávvir document.
    """
    for content in avvir_json["data"]["content"]:  # type: ignore
        if content["identifier"] in ["title", "crosshead"]:
            if "content" in content and "text" in content["content"]:
                return "".join(
                    [
                        text.get("insert", "")
                        for text in content.get("content").get("text", [{}])
                    ]
                )
    return ""


def extract_authors(avvir_json: dict[str, Any]) -> list[AvvirAuthor]:
    """Extract the authors from an Ávvir JSON dictionary."""
    authors = [
        convert_author(content)  # type: ignore
        for content in avvir_json["data"]["content"]  # type: ignore
        if content["identifier"] == "author"
    ]
    return authors if authors else []


def extract_main_content(avvir_json: dict[str, Any]) -> list[AvvirTaggedText]:
    """Extract the main content from an Ávvir JSON dictionary."""
    main_content = [
        convert_tagged_text(content)  # type: ignore
        for content in avvir_json["data"]["content"]  # type: ignore
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
    return main_content if main_content else []


def extract_captions(avvir_json: dict[str, Any]) -> list[AvvirTaggedText]:
    """Extract the captions from an Ávvir JSON dictionary."""
    captions = [
        convert_image(content)  # type: ignore
        for content in avvir_json["data"]["content"]  # type: ignore
        if content["identifier"] == "image"
    ]
    return captions if captions else []


def extract_slideshows(avvir_json: dict[str, Any]) -> list[AvvirTaggedText]:
    """Extract the slideshows from an Ávvir JSON dictionary."""
    slideshows = [
        convert_slideshow(content)  # type: ignore
        for content in avvir_json["data"]["content"]  # type: ignore
        if content["identifier"] == "slideshow"
    ]
    return slideshows if slideshows else []


def extract_containers(avvir_json: dict[str, Any]) -> list[AvvirContainer]:
    """Extract the containers from an Ávvir JSON dictionary."""
    containers = [
        convert_container(content)  # type: ignore
        for content in avvir_json["data"]["content"]  # type: ignore
        if content["identifier"] == "container"
    ]
    return containers if containers else []


def convert2intermediate(avvir_doc: Path) -> etree.Element:
    """Convert Ávvir json files to the giellatekno xml format."""
    avvir_doc = AvvirDocument.from_json( # type: ignore
        json.loads(avvir_doc.read_text(encoding="utf-8"))
    )  # type: ignore
    tree = etree.Element("document")
    body = etree.SubElement(tree, "body")

    for element in flatten(avvir_doc.serialize()):  # type: ignore
        body.append(element)
    return tree


def convert_author(author_dict: dict[str, Any]) -> AvvirAuthor:
    """Convert an Ávvir author to AvvirAuthor.

    Args:
        fullname: the full name of the Ávvir author.

    Returns:
        The resulting AvvirAuthor object after the conversion.
    """
    fullname = author_dict.get("content", {}).get("name", [{}])[0].get("insert", "")

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
    return AvvirTaggedText(text="".join(texts), tag=content_dict["identifier"])


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


def convert_container(container_dict: dict[str, Any]) -> AvvirContainer:
    """Convert an Ávvir container to AvvirContainer.

    Args:
        container_dict: the container of the Ávvir document.

    Returns:
        The resulting AvvirContainer object after the conversion.
    """
    not_wanted_ids = {"embed"}
    container_content_ids = {
        "body",
        "faktatekst",
        "faktatittel",
        "footer",
        "image",
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
            convert_tagged_text(content)  # type: ignore
            for content in container_dict.get("content", [])  # type: ignore
            if content["identifier"] in container_content_ids
        ],
        captions=[
            convert_image(content)  # type: ignore
            for content in container_dict.get("content", [])  # type: ignore
            if content["identifier"] == "image"
        ],
        slideshows=[
            convert_slideshow(content)  # type: ignore
            for content in container_dict.get("content", [])  # type: ignore
            if content["identifier"] == "slideshow"
        ],
        containers=[
            convert_container(content)  # type: ignore
            for content in container_dict.get("content", [])  # type: ignore
            if content["identifier"] == "container"
        ],
    )


def flatten(items: Iterable[SerializedXml]) -> list[etree.Element]:
    result: list[etree.Element] = []

    for item in items:
        if etree.iselement(item):
            result.append(item)
        else:
            result.extend(flatten(item))

    return result
