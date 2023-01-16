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
#   Copyright © 2013-2023 The University of Tromsø &
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

VERBOSE_ERROR = "(?P<error>{[^{}]*})"
CORRECTION = "[" + "".join(ERROR_TYPES.keys()) + "]{[^}]*}"
VERBOSE_CORRECTION = f"(?P<correction>{CORRECTION})"

CORRECTION_REGEX = re.compile(VERBOSE_CORRECTION, re.UNICODE)
SIMPLE_ERROR_REGEX = re.compile(f"{VERBOSE_ERROR}{VERBOSE_CORRECTION}", re.UNICODE)
LAST_CORRECTION_REGEX = re.compile(f"{VERBOSE_CORRECTION}(?!.*{CORRECTION}.*)")


def invalid_corrections(text):
    """Check if all corrections are valid."""
    return [
        correction
        for match in CORRECTION_REGEX.finditer(text)
        for correction in match.group("correction").split("///")
        if not correction.count("|") < 2
    ]


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


def make_error_element(error_text, error_name, correction):
    """Make an error xml element.

    Args:
        error_text: the text of the error element
        error_name: the tag of the error element
        correction: the correction(s) for the error

    Returns:
        An etree._Element
    """
    error_element = etree.Element(error_name)
    error_element.text = error_text

    for correction_element in make_correction_element(correction):
        error_element.append(correction_element)

    return error_element


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


def scan_for_error(text):
    """Scan for error markup in the given text."""
    level = 0
    index = len(text) - 1

    while index > 0:
        if text[index] == "}":
            level += 1
        if text[index] == "{":
            level -= 1
        if level == 0:
            break
        index -= 1

    if index:
        return text[:index], text[index + 1 : -1]

    return "", text[index + 1 : -1]


def fix_text(element):
    """Replace error markup with error xml."""
    if element.text:
        text = element.text
        last_correction = LAST_CORRECTION_REGEX.search(text)
        while last_correction:
            text, error_element = errormarkup_to_xml(text, last_correction)
            element.text = text
            element.insert(0, error_element)
            last_correction = LAST_CORRECTION_REGEX.search(text)


def errormarkup_to_xml(text, last_correction):
    """Turn the errormarkup into error xml."""
    tail = text[last_correction.end() :]
    text, error = scan_for_error(text[: last_correction.start()])
    error_element = make_error_element(
        error,
        ERROR_TYPES[last_correction.group("correction")[0]],
        last_correction.group("correction")[2:-1],
    )
    error_element.tail = tail
    fix_text(error_element)

    return text, error_element


def fix_tail(element):
    """Replace error markup with error xml."""
    parent = element.getparent()
    position = parent.index(element)
    if element.tail:
        text = element.tail
        last_correction = LAST_CORRECTION_REGEX.search(text)
        while last_correction:
            position += 1
            text, error_element = errormarkup_to_xml(text, last_correction)
            element.tail = text
            parent.insert(position, error_element)
            last_correction = LAST_CORRECTION_REGEX.search(text)


def convert_to_errormarkupxml(element):
    """Convert errormarkup found in the element to xml."""
    if element.text:
        fix_text(element)

    if element.tail:
        fix_tail(element)

    for child in element:
        convert_to_errormarkupxml(child)


def validate_markup(element):
    """Check if the markup is valid."""
    for child in element:
        child_as_text = etree.tostring(child, encoding="unicode")
        for invalid_correction in invalid_corrections(child_as_text):
            yield f"Too many «|» in {invalid_correction}"
        invalid_pair = has_not_valid_pairs(child_as_text)
        if invalid_pair:
            yield f"In text starting with\n\t{child_as_text[len(child.tag)+2:50]}"
            yield f"\tError in front of\n\t\t{invalid_pair}"


def add_error_markup(element):
    """Convert error markup to xml in this element and its children.

    This is the starting point for doing markup.

    Args:
        element (etree._Element): The element where error markup should
            be converted to xml.
    """
    errors = [message for message in validate_markup(element)]

    if errors:
        raise ErrorMarkupError("{}".format("\n".join(errors)))

    for child in element:
        convert_to_errormarkupxml(child)


class ErrorMarkupError(Exception):
    """This is raised for errors in this module."""
