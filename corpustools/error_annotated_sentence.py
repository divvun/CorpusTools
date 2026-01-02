from dataclasses import dataclass
from typing import Iterator

from lxml import etree

from corpustools.error_types import ErrorType, error_type_from_symbol


@dataclass
class CorrectionSegment:
    error_info: str | None
    suggestions: list[str]

    def to_xml(self) -> etree.Element:
        """Convert the correction segment to its XML representation.

        Returns:
            An lxml Element representing the correction segment in XML format.
        """
        correct_elem = etree.Element("correct")
        if self.error_info:
            correct_elem.set("errorinfo", self.error_info)
        correct_elem.text = "///".join(self.suggestions)
        return correct_elem


def parse_markup_to_correction_segment(markup: Iterator[str]) -> CorrectionSegment:
    """Parse correction segment from markup iterator.
    Args:
        markup: An iterator over strings representing the markup.
    Returns:
        A CorrectionSegment representing the parsed content.
    """
    next(markup)  # Skip initial '{'
    contents: list[str] = []
    for char in markup:
        if char == "}":
            break
        contents.append(char)

    correction_str = "".join(contents)
    if "|" in correction_str:
        error_info, suggestions_str = correction_str.split("|", 1)
        suggestions = suggestions_str.split("///")
    else:
        error_info = ""
        suggestions = correction_str.split("///")

    return CorrectionSegment(
        error_info=error_info if error_info else None,
        suggestions=suggestions,
    )


@dataclass
class ErrorMarkup:
    """Represents a marked up error in a sentence.

    Attributes:
        error: "ErrorAnnotatedSentence" representing the erroneous segment
        errortype: Type of error
        correction: CorrectionSegment
    """

    error: "ErrorAnnotatedSentence"
    errortype: ErrorType
    correction: CorrectionSegment

    def uncorrected_text(self) -> str:
        """Get the uncorrected text of the error markup."""
        return self.error.uncorrected_text()

    def to_xml(self) -> etree.Element:
        """Convert the error markup to its XML representation.

        Returns:
            An lxml Element representing the error markup in XML format.
        """

        error_elem = etree.Element(self.errortype.name.lower())
        self.error.to_xml(parent=error_elem)
        error_elem.append(self.correction.to_xml())

        return error_elem


@dataclass
class ErrorMarkupSegment:
    error_markup: ErrorMarkup
    tail: str

    def uncorrected_text(self) -> str:
        """Get the uncorrected text of the error markup segment."""
        return self.error_markup.uncorrected_text() + self.tail

    def to_xml(self) -> etree.Element:
        """Convert the error markup segment to its XML representation.
        Returns:
            An lxml Element representing the error markup segment in XML format.
        """
        error_elem = self.error_markup.to_xml()
        error_elem.tail = self.tail

        return error_elem


@dataclass
class ErrorAnnotatedSentence:
    """Represents a sentence with zero or more error markups."""

    head: str
    errors: list[ErrorMarkupSegment]

    def uncorrected_text(self) -> str:
        """Get the uncorrected text of the sentence."""
        parts: list[str] = [self.head]

        for error in self.errors:
            parts.append(error.uncorrected_text())

        return "".join(parts)

    def to_xml(self, parent: etree.Element | None = None) -> etree.Element:
        """Convert the error annotated sentence to its XML representation.

        Args:
            parent: The parent XML element to which the sentence will be appended.

        Returns:
            An lxml Element representing the error annotated sentence in XML format.
        """
        if parent is None:
            parent = etree.Element("p")
        parent.text = self.head
        for error_segment in self.errors:
            parent.append(error_segment.to_xml())

        return parent


def parse_markup_to_sentence(markup: Iterator[str]) -> ErrorAnnotatedSentence:
    """Parse error annotated sentence from markup iterator.

    Args:
        markup: An iterator over strings representing the markup.
    Returns:
        An ErrorAnnotatedSentence representing the parsed content.
    """
    chars: list[str] = []
    errors: list[ErrorMarkupSegment] = []
    try:
        while char := next(markup):
            if char == "{":  # start of error markup
                break
            if char == "}":  # end of current error markup
                return ErrorAnnotatedSentence(
                    head="".join(chars),
                    errors=errors,
                )
            chars.append(char)
    except StopIteration:
        return ErrorAnnotatedSentence(
            head="".join(chars),
            errors=errors,
        )

    while True:
        try:
            error_segment, delimiter = parse_markup_to_error_markup_segment(markup)
            errors.append(error_segment)
            if delimiter == "}":
                # End of nested error content
                break
            elif delimiter == "{":
                # Start of another error markup segment, continue
                continue
            else:
                # End of markup (delimiter is None)
                break
        except StopIteration:
            break

    return ErrorAnnotatedSentence(
        head="".join(chars),
        errors=errors,
    )


def parse_markup_to_error_markup_segment(
    markup: Iterator[str],
) -> tuple[ErrorMarkupSegment, str | None]:
    """Parse ErrorMarkupSegment from markup iterator.
    Args:
        markup: An iterator over strings representing the markup.
    Returns:
        An ErrorMarkupSegment representing the parsed content.
    """
    error = parse_markup_to_sentence(markup)
    symbol = next(markup)
    errortype = error_type_from_symbol(symbol)
    if errortype is None:
        raise ValueError(f"Unknown error symbol: «{symbol}»")
    correction = parse_markup_to_correction_segment(markup)
    tail, delimiter = parse_tail(markup)
    return ErrorMarkupSegment(
        error_markup=ErrorMarkup(
            error=error, errortype=errortype, correction=correction
        ),
        tail=tail,
    ), delimiter


def parse_tail(markup: Iterator[str]) -> tuple[str, str | None]:
    """Parse tail from markup iterator.

    Args:
        markup: An iterator over strings representing the markup.
    Returns:
        A tuple of (tail string, next delimiter character or None).
        The delimiter is either '{', '}', or None if end of markup.
    """
    tail_chars: list[str] = []
    delimiter = None
    for char in markup:
        if char in "{}":
            # Start or end of next error markup segment
            delimiter = char
            break
        tail_chars.append(char)

    return "".join(tail_chars), delimiter
