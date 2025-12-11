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
"""Represents a sentence with zero or more error markups."""

import re
from dataclasses import dataclass, field

from lxml import etree

from corpustools.error_markup import ErrorMarkup, ErrorSegment
from corpustools.error_types import ErrorMarkupError, all_error_symbols

VERBOSE_ERROR = "(?P<error>{[^{}]*})"
CORRECTION = "[" + "".join(all_error_symbols()) + "]{[^}]*}"
VERBOSE_CORRECTION = f"(?P<correction>{CORRECTION})"

CORRECTION_REGEX = re.compile(VERBOSE_CORRECTION, re.UNICODE)
SIMPLE_ERROR_REGEX = re.compile(f"{VERBOSE_ERROR}{VERBOSE_CORRECTION}", re.UNICODE)
LAST_CORRECTION_REGEX = re.compile(f"{VERBOSE_CORRECTION}(?!.*{CORRECTION}.*)")


@dataclass
class ErrorAnnotatedSentence:
    """Represents a sentence with zero or more error markups.

    Attributes:
        text: The original text of the sentence
        errors: List of errors found in the sentence
    """

    text: str
    errors: list[ErrorMarkup] = field(default_factory=lambda: [])

    def error_count(self) -> int:
        """Get the number of errors in the sentence."""
        return len(self.errors)

    def to_errormarkupxml(self) -> etree.Element:
        """Convert the error annotated sentence to XML format.

        This reconstructs the XML representation from the parsed error structures.
        For sentences with no errors, returns a <p> element with the text.
        For sentences with errors, recursively builds the error element tree.

        Returns:
            An lxml Element containing a <p> tag with error markup XML
        """
        # Create the paragraph element
        para = etree.Element("p")

        # If no errors, just set the clean text
        if not self.errors:
            # Remove markup syntax from text to get clean text
            clean_text = self._remove_markup(self.text)
            para.text = clean_text
            return para

        # For sentences with errors, we need to find top-level errors
        # (errors that are not nested inside other errors)
        top_level_errors = self._find_top_level_errors()

        # Add all top-level error elements to the paragraph
        for error in top_level_errors:
            error_elem = self._error_to_xml(error)
            para.append(error_elem)

        return para

    def _find_top_level_errors(self) -> list[ErrorMarkup]:
        """Find errors that are not nested inside other errors."""
        # An error is top-level if no other error contains it
        top_level: list[ErrorMarkup] = []
        for error in self.errors:
            is_nested = False
            for other in self.errors:
                if other != error and self._contains_error(other, error):
                    is_nested = True
                    break
            if not is_nested:
                top_level.append(error)
        return top_level

    def _contains_error(self, parent: ErrorMarkup, child: ErrorMarkup) -> bool:
        """Check if parent error contains child error."""
        if not parent.is_nested:
            return False
        assert isinstance(parent.form, list)
        for segment in parent.form:
            if segment.is_error:
                assert isinstance(segment.content, ErrorMarkup)
                if segment.content == child:
                    return True
                if self._contains_error(segment.content, child):
                    return True
        return False

    def _remove_markup(self, text: str) -> str:
        """Remove error markup syntax from text."""
        # This is a simple implementation - remove patterns like {text}${corr}
        import re

        from corpustools.error_types import all_error_symbols

        symbols = "".join(re.escape(s) for s in all_error_symbols())
        pattern = r"\{[^{}]*\}[" + symbols + r"]\{[^}]*\}"

        # Keep removing markup until none left
        old_text = text
        while True:
            new_text = re.sub(pattern, "", old_text)
            if new_text == old_text:
                break
            old_text = new_text

        return new_text

    def _error_to_xml(self, error: ErrorMarkup) -> etree.Element:
        """Convert an ErrorMarkup to an XML element.

        Args:
            error: The ErrorMarkup to convert

        Returns:
            An lxml Element for the error
        """
        from lxml import etree

        # Create the error element with the appropriate tag (lowercase)
        error_elem = etree.Element(error.errortype.error_name)

        # Handle the form (can be string or list of segments)
        if isinstance(error.form, str):
            # Simple form - just text
            error_elem.text = error.form
        else:
            # Nested form - process segments
            for i, segment in enumerate(error.form):
                if segment.is_text:
                    # Text segment - content is str
                    assert isinstance(segment.content, str)
                    text_content = segment.content
                    if i == 0 and error_elem.text is None:
                        error_elem.text = text_content
                    elif len(error_elem) > 0:
                        tail = error_elem[-1].tail or ""
                        error_elem[-1].tail = tail + text_content
                    else:
                        error_elem.text = (error_elem.text or "") + text_content
                else:
                    # Nested error segment - content is ErrorMarkup
                    assert isinstance(segment.content, ErrorMarkup)
                    nested_elem = self._error_to_xml(segment.content)
                    error_elem.append(nested_elem)

        # Add correction elements
        for suggestion in error.suggestions:
            correct_elem = etree.Element("correct")
            correct_elem.text = suggestion

            # Add errorinfo attribute if present
            if error.errorinfo:
                correct_elem.set("errorinfo", error.errorinfo)

            error_elem.append(correct_elem)

        return error_elem


def parse_markup_to_sentence(text: str) -> ErrorAnnotatedSentence:
    """Parse marked up text into an ErrorAnnotatedSentence.

    Args:
        text: Text with error markup notation

    Returns:
        Sentence with parsed errors

    Raises:
        ErrorMarkupError: If markup is invalid
    """
    from corpustools.error_annotated_sentence import ErrorAnnotatedSentence

    # Validate markup first
    errors_list = list(invalid_corrections(text))
    if errors_list:
        raise ErrorMarkupError(f"Invalid corrections: {', '.join(errors_list)}")

    invalid_pair = has_not_valid_pairs(text)
    if invalid_pair:
        raise ErrorMarkupError(f"Invalid pair: {invalid_pair}")

    errors: list[ErrorMarkup] = []
    _parse_text_recursive(text, 0, errors)

    return ErrorAnnotatedSentence(text=text, errors=errors)


def scan_for_error(text: str) -> tuple[str, str]:
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


def look_for_extended_attributes(correction: str) -> tuple[str, str | None]:
    """Extract attributes and correction from a correctionstring."""
    details = correction.split("|")

    if len(details) == 1:
        return (details[0], None)

    return (details[1], details[0])


def _parse_text_recursive(
    text: str, base_offset: int, errors: list["ErrorMarkup"]
) -> None:
    """Recursively parse error markup and collect errors.

    Args:
        text: Text to parse
        base_offset: Base byte offset for this text segment
        errors: List to collect ErrorMarkup objects
    """
    from corpustools.error_markup import ErrorMarkup
    from corpustools.error_types import error_type_from_symbol

    last_correction = LAST_CORRECTION_REGEX.search(text)
    while last_correction:
        # Extract the correction info
        correction_symbol = last_correction.group("correction")[0]
        correction_content = last_correction.group("correction")[2:-1]

        # Scan backwards to find the error text
        prefix, error_text = scan_for_error(text[: last_correction.start()])

        # Calculate position
        error_start = base_offset + len(prefix)
        error_end = error_start + len(error_text)

        # Parse correction content (may have errorinfo)
        corrections: list[str] = []
        errorinfo = ""

        for correction in correction_content.split("///"):
            correction_text, att_list = look_for_extended_attributes(correction)
            corrections.append(correction_text)
            if att_list and not errorinfo:
                errorinfo = att_list

        # Get error type
        error_type = error_type_from_symbol(correction_symbol)
        if not error_type:
            raise ErrorMarkupError(f"Unknown error symbol: {correction_symbol}")

        # Check if error contains nested errors
        nested_errors: list[ErrorMarkup] = []
        form = _parse_error_form(error_text, error_start, nested_errors)

        # Add nested errors to the main errors list
        errors.extend(nested_errors)

        # Create the error markup
        error = ErrorMarkup(
            form=form,
            start=error_start,
            end=error_end,
            errortype=error_type,
            errorinfo=errorinfo,
            suggestions=corrections,
        )
        errors.append(error)

        # Continue with the remaining text (prefix)
        text = prefix
        last_correction = LAST_CORRECTION_REGEX.search(text)


def _parse_error_form(
    error_text: str, base_offset: int, nested_errors: list["ErrorMarkup"]
) -> str | list["ErrorSegment"]:
    """Parse error form which may contain nested errors.

    Args:
        error_text: The error text to parse
        base_offset: Base offset for this error
        nested_errors: List to collect nested errors

        Returns:
        Simple string or list of segments
    """
    from corpustools.error_markup import ErrorMarkup, ErrorSegment
    from corpustools.error_types import error_type_from_symbol

    # Check if there are nested corrections in the error text
    if not LAST_CORRECTION_REGEX.search(error_text):
        # No nested errors, return simple string
        return error_text

    # Has nested errors - build segment list
    segments: list[ErrorSegment] = []
    current_text = error_text

    last_correction = LAST_CORRECTION_REGEX.search(current_text)
    while last_correction:
        # The tail is everything after the correction
        tail = current_text[last_correction.end() :]

        # Get the text before this correction (prefix and error text)
        prefix, nested_error_text = scan_for_error(
            current_text[: last_correction.start()]
        )

        # Add tail as text segment first (we're building backwards)
        if tail:
            segments.insert(0, ErrorSegment(content=tail))

        # Parse the nested error
        correction_symbol = last_correction.group("correction")[0]
        correction_content = last_correction.group("correction")[2:-1]

        nested_start = base_offset + len(prefix)
        nested_end = nested_start + len(nested_error_text)

        # Parse correction
        corrections: list[str] = []
        errorinfo = ""
        for correction in correction_content.split("///"):
            correction_text, att_list = look_for_extended_attributes(correction)
            corrections.append(correction_text)
            if att_list and not errorinfo:
                errorinfo = att_list

        # Get error type
        error_type = error_type_from_symbol(correction_symbol)
        if not error_type:
            raise ErrorMarkupError(f"Unknown error symbol: {correction_symbol}")

        # Recursively parse nested error form
        nested_form = _parse_error_form(nested_error_text, nested_start, nested_errors)

        # Create nested error
        nested_error = ErrorMarkup(
            form=nested_form,
            start=nested_start,
            end=nested_end,
            errortype=error_type,
            errorinfo=errorinfo,
            suggestions=corrections,
        )

        # Add to nested_errors list and as segment (at beginning)
        nested_errors.append(nested_error)
        segments.insert(0, ErrorSegment(content=nested_error))

        # Continue with prefix
        current_text = prefix
        last_correction = LAST_CORRECTION_REGEX.search(current_text)

    # Add any remaining text at the beginning
    if current_text:
        segments.insert(0, ErrorSegment(content=current_text))

    return segments


def invalid_corrections(text: str) -> list[str]:
    """Check if all corrections are valid."""
    min_length = 2  # At least symbol and {}
    return [
        correction
        for match in CORRECTION_REGEX.finditer(text)
        for correction in match.group("correction").split("///")
        if not correction.count("|") < min_length
    ]


def has_not_valid_pairs(text: str) -> str:
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


def remove_simple_errors(text: str) -> str:
    """Remove non nested errors from the text."""
    result: list[str] = []
    previous = 0
    for match in SIMPLE_ERROR_REGEX.finditer(text):
        result.append(text[previous : match.start()])
        previous = match.end()

    if previous < len(text):
        result.append(text[previous:])

    return "".join(result)
