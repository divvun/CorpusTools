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
#   Copyright © 2013-2020 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Classes and functions to convert errormarkup to xml."""

import re
import sys

from lxml import etree

ERROR_REGEX = re.compile('(?P<error>{[^{]*}$)', re.UNICODE)
ERROR_TYPES = {
    '$': 'errorort',
    '¢': 'errorortreal',
    '€': 'errorlex',
    '£': 'errormorphsyn',
    '¥': 'errorsyn',
    '§': 'error',
    '∞': 'errorlang',
    '‰': 'errorformat'
}
CORRECTION_REGEX = re.compile('(?P<correction>[$€£¥§¢∞‰]{[^\}]*})(?P<tail>.*)',
                              re.UNICODE)


def is_error(text):
    """Check if the test contains an error markup.

    Args:
        text (str): the text to search for error markup.

    Returns:
        A re.match() if error markup is found, else None
    """
    return ERROR_REGEX.search(text)


def is_correction(expression):
    return CORRECTION_REGEX.search(expression)


def process_text(text):
    """Divide the text in to a list.

    The list will consist of alternate
    non-correctionstring/correctionstrings
    """
    result = []

    matches = CORRECTION_REGEX.search(text)
    while matches:
        head = CORRECTION_REGEX.sub('', text)
        if not (head and head[-1] == ' '):
            if head:
                result.append(head)
            result.append(matches.group('correction'))
        text = matches.group('tail')
        matches = CORRECTION_REGEX.search(text)

    if text:
        result.append(text)

    return result


def process_head(text):
    """Divide text into text/error parts."""
    matches = ERROR_REGEX.search(text)
    text = ERROR_REGEX.sub('', text)

    return (text, matches.group('error'))


def get_element_name(separator):
    return ERROR_TYPES[separator]


def make_error_element(error, fixed_correction, element_name, att_list):
    """Make an error xml element.

    Args:
        error (str or etree._Element):
        fixed_correction (str):
        element_name (str):
        att_list (str):

    Returns:
        An etree._Element representing the error markup.
    """
    error_element = etree.Element(element_name)
    if isinstance(error, etree._Element):
        error_element.append(error)
    else:
        error_element.text = error.replace('{', '').replace('}', '')

    error_element.set('correct', fixed_correction)

    if att_list is not None:
        error_element.set('errorinfo', att_list)

    return error_element


def get_text(element):
    """Get the text an element.

    Args:
        element(etree._Element or str):

    Returns:
        If text is found, str. Otherwise return None.
    """
    return element.tail if isinstance(element, etree._Element) else element


def look_for_extended_attributes(correction):
    """Extract attributes and correction from a correctionstring."""
    ext_att = False
    att_list = None
    if '|' in correction:
        ext_att = True
        try:
            (att_list, correction) = correction.split('|')
        except ValueError as e:
            raise ErrorMarkupError(
                f'\n{str(e)}\n'
                'Too many | characters inside the correction: '
                f'«{correction}»\n'
                'Have you remembered to encase the error inside '
                'parenthesis, e.g. (vowlat,a-á|servodatvuogádat)?'
                'If the errormarkup is correct, send a report about '
                'this error to borre.gaup@uit.no')

    return (correction, ext_att, att_list)


def get_error(error, correction):
    """Make an error_element.

    error - - is either a string or an etree.Element
    correction - - is a correctionstring
    """
    (fixed_correction, ext_att, att_list) = \
        look_for_extended_attributes(
            correction[1:].replace('{', '').replace('}', ''))

    element_name = get_element_name(correction[0])

    error_element = make_error_element(error, fixed_correction, element_name,
                                       att_list)

    return error_element


def add_nested_error(elements, errorstring, correctionstring):
    """Make error_element, append it to elements.

    Args:
        elements:           a list of error_elements
        errorstring:        contains either a correction or string ending
                            with a right parenthesis }
        correctionstring:   a string containing an errormarkup correction

    The algorithm:
    At least the last element in elements will be engulfed in error_element
    and replaced by error_element in elements

    Remove the last element, use it as the inner_element when making
    error_element

    If the errorstring is not a correction, then it ends in a ).

    Extract the string from the last element of elements.
    If a ( is found, set the part before ( to be the tail of the last
    element of elements. Set the part after ( to be the text of
    error_element, append error_element to elements.

    If a ( is not found, insert the last element of elements as first child
    of error_element, continue searching
    """
    try:
        inner_element = elements[-1]
    except IndexError:
        raise ErrorMarkupError(
            f'Cannot handle:\n{errorstring} {correctionstring}\n'
            'This is either an error in the markup or an error in the '
            'errormarkup conversion code.\n'
            'If the markup is correct, send a report about this error to '
            'borre.gaup@uit.no')

    elements.remove(elements[-1])
    if not is_correction(errorstring):
        inner_element.tail = errorstring[:-1]
    error_element = get_error(inner_element, correctionstring)

    if is_correction(errorstring):
        elements.append(error_element)
    else:
        while True:
            text = get_text(elements[-1])

            index = text.rfind('{')
            if index > -1:
                error_element.text = text[index + 1:]
                if isinstance(elements[-1], etree._Element):
                    elements[-1].tail = text[:index]
                else:
                    elements[-1] = text[:index]
                elements.append(error_element)
                break

            else:
                inner_element = elements[-1]
                elements.remove(elements[-1])
                try:
                    error_element.insert(0, inner_element)
                except TypeError as e:
                    raise ErrorMarkupError(
                        f'{e}\n'
                        'The program expected an error element, but '
                        f'found a string:\n«{inner_element}»\n'
                        'There is either an error in the errormarkup '
                        'close to this sentence or the program cannot '
                        'evaluate a correct errormarkup.\n'
                        'If the errormarkup is correct, please report '
                        'about the error to borre.gaup@uit.no')


def add_simple_error(elements, errorstring, correctionstring):
    """Make an error element, append it to elements.

    elements -- a list of error_elements
    errorstring -- a string containing a text part and an errormarkup
    error
    correctionstring -- a string containing an errormarkup correction

    """
    (head, error) = process_head(errorstring)

    if elements:
        elements[-1].tail = head

    if not elements and head:
        elements.append(head)

    elements.append(get_error(error, correctionstring))


def error_parser(text):
    """Parse errormarkup found in text.

    If any markup is found, return
    a list of elements in elements

    result -- contains a list of non-correction/correction parts

    The algorithm for parsing the error is:
    Find a correction in the result list.

    If the preceding element in result contains a simple error and is not a
    correction make an error_element, append it to elements

    If the preceding element in result is not a simple error, it is part of
    nested markup.
    """
    elements = []
    result = process_text(text.replace('\n', ' '))

    for index in range(0, len(result)):
        if is_correction(result[index]):
            if (not is_correction(result[index - 1])
                    and is_error(result[index - 1])):
                add_simple_error(elements, result[index - 1], result[index])

            else:

                add_nested_error(elements, result[index - 1], result[index])

    try:
        if not is_correction(result[-1]):
            elements[-1].tail = result[-1]
    except IndexError:
        pass

    return elements


def fix_tail(element):
    """Replace the tail of an element with errormarkup if possible."""
    new_content = error_parser(element.tail if element.tail else '')

    if new_content:
        element.tail = None

        if isinstance(new_content[0], str):
            element.tail = new_content[0]
            new_content = new_content[1:]

        new_pos = element.getparent().index(element) + 1
        for pos, part in enumerate(new_content):
            element.getparent().insert(new_pos + pos, part)


def fix_text(element):
    """Replace the text of an element with errormarkup if possible."""
    new_content = error_parser(element.text if element.text else '')

    if new_content:
        element.text = None

        if isinstance(new_content[0], str):
            element.text = new_content[0]
            new_content = new_content[1:]

        for pos, part in enumerate(new_content):
            element.insert(pos, part)


def really_add_error_markup(element):
    """Search for errormarkup.

    If found, replace errormarkuped text with xml

    To see examples of what new_content consists of, have a look at the
    test_error_parser* methods
    """
    fix_text(element)
    fix_tail(element)


def add_error_markup(element):
    """Convert error markup to xml in this element and its children.

    This is the starting point for doing markup.

    Args:
        element (etree._Element): The element where error markup should
            be converted to xml.
    """
    really_add_error_markup(element)
    for elt in element:
        add_error_markup(elt)


class ErrorMarkupError(Exception):
    """This is raised for errors in this module."""
    pass
