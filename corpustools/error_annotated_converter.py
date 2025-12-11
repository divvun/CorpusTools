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
#   Copyright © 2025 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
from pathlib import Path

from lxml import etree

from corpustools.error_annotated_sentence import parse_markup_to_sentence


def convert2intermediate(filename: Path) -> etree.Element:
    """Convert files containing error-annotated sentences to the GiellaLT xml format."""
    document = etree.Element("document")
    etree.SubElement(document, "header")
    body = etree.SubElement(document, "body")

    for line in filename.read_text(encoding="utf-8").splitlines():
        error_annotated = parse_markup_to_sentence(line)
        body.append(error_annotated.to_errormarkupxml())

    return document