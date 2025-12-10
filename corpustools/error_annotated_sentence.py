"""Represents a sentence with zero or more error markups.

Ported from divvun-runtime/cli/src/command/yaml_test/sentence.rs
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from corpustools.error_markup import ErrorMarkup, ErrorSegment
from corpustools.error_types import ErrorMarkupError

if TYPE_CHECKING:
    from corpustools.error_types import (
        all_error_symbols,
    )

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
        raise ErrorMarkupError(
            f"Invalid corrections: {', '.join(errors_list)}"
        )
    
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
            raise ErrorMarkupError(
                f"Unknown error symbol: {correction_symbol}"
            )
        
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
            raise ErrorMarkupError(
                f"Unknown error symbol: {correction_symbol}"
            )
        
        # Recursively parse nested error form
        nested_form = _parse_error_form(
            nested_error_text, nested_start, nested_errors
        )
        
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


def invalid_corrections(text:str) -> list[str]:
    """Check if all corrections are valid."""
    return [
        correction
        for match in CORRECTION_REGEX.finditer(text)
        for correction in match.group("correction").split("///")
        if not correction.count("|") < 2
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
