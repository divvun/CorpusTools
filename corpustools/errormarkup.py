# -*- coding: utf-8 -*-

#
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
#   Copyright © 2013-2021 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Classes and functions to convert errormarkup to xml."""

import re

from lxml import etree

ERROR_TYPES = {
    "$": "errorort",
    "¢": "errorortreal",
    "€": "errorlex",
    "£": "errormorphsyn",
    "¥": "errorsyn",
    "§": "error",
    "∞": "errorlang",
    "‰": "errorformat",
}

ERROR_STRING = "(?P<error>{[^{}]*})"
CORRECTION_STRING = "(?P<correction>[" + "".join(ERROR_TYPES.keys()) + "]{[^}]*})"

CORRECTION_REGEX = re.compile(CORRECTION_STRING, re.UNICODE)
SIMPLE_ERROR_REGEX = re.compile(f"{ERROR_STRING}{CORRECTION_STRING}", re.UNICODE)


def are_corrections_valid(text):
    """Check if all corrections are valid."""
    return all(
        correction.count("|") < 2
        for match in CORRECTION_REGEX.finditer(text)
        for correction in match.group("correction").split("///")
    )


def remove_simple_errors(text):
    """Remove non nested errors from the text."""
    result = []
    previous = 0
    for match in SIMPLE_ERROR_REGEX.finditer(text):
        result.append(text[previous : match.start()])
        previous = match.end()

    if previous < len(text):
        result.append(text[previous:])

    return "".join(result)


def has_not_valid_pairs(text):
    """Check if the text has valid pairs."""
    old = text
    correction = CORRECTION_REGEX.search(old)
    while correction:
        no_simple = remove_simple_errors(old)
        correction = CORRECTION_REGEX.search(no_simple)

        if old == no_simple and correction:
            return correction.group("correction")

        old = no_simple

    return ""


def convert_to_xml(text):
    """Convert text into errormarkup xml.

    Args:
        text: Stringified xml that may contain errormarkup

    Returns:
        Errormarkup xml.
    """
    correction = CORRECTION_REGEX.search(text)
    converted = text
    while correction:
        converted = make_simple_errors(converted)
        correction = CORRECTION_REGEX.search(converted)
        if not correction:
            break

    for orig, replacement in [("&lt;", "<"), ("&gt;", ">")]:
        converted = converted.replace(orig, replacement)

    return etree.fromstring(converted)


def make_simple_errors(text):
    """Divide the text in to a list.

    The list will consist of alternate
    non-correctionstring/correctionstrings
    """
    result = []
    previous = 0
    for match in SIMPLE_ERROR_REGEX.finditer(text):
        if previous < match.start():
            result.append(text[previous : match.start()])
        result.append(make_error_element_as_text(match))
        previous = match.end()

    if previous < len(text):
        result.append(text[previous:])

    converted = "".join(result)
    for orig, replacement in [("&lt;", "<"), ("&gt;", ">")]:
        converted = converted.replace(orig, replacement)
    return converted


def make_error_element_as_text(match):
    """Make an error xml element.

    Args:
        match: a SIMPLE_ERROR_MATCH

    Returns:
        An etree._Element as a string
    """
    error_element = etree.Element(ERROR_TYPES[match.group("correction")[0]])
    error_element.text = match.group("error")[1:-1]

    for correction_element in make_correction_element(match.group("correction")[2:-1]):
        error_element.append(correction_element)

    return etree.tostring(error_element, encoding="unicode")


def make_correction_element(correction_content):
    """Make correction elements.

    Args:
        correction_content: string containing the correction(s)

    Yields:
        A correction element for each correction
    """
    for correction in correction_content.split("///"):
        correction_text, att_list = look_for_extended_attributes(correction)

        correct_element = etree.Element("correct")
        correct_element.text = correction_text

        if att_list is not None:
            correct_element.set("errorinfo", att_list)

        yield correct_element


def look_for_extended_attributes(correction):
    """Extract attributes and correction from a correctionstring."""
    details = correction.split("|")

    if len(details) == 1:
        return (details[0], None)

    return (details[1], details[0])


def add_error_markup(element):
    """Convert error markup to xml in this element and its children.

    This is the starting point for doing markup.

    Args:
        element (etree._Element): The element where error markup should
            be converted to xml.
    """
    return convert_to_xml(etree.tostring(element, encoding="unicode"))


class ErrorMarkupError(Exception):
    """This is raised for errors in this module."""
