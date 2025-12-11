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
"""Error markup representation for grammar checking.

Represents marked up errors in sentences with support for nested errors.

Example simple markup: {čohke}¢{čohkke}
This indicates an error "čohke" with correction "čohkke" of type "errorortreal" (¢)

Example nested markup: {{epoxi}${noun,cons|epoksy} lim}¢{noun,mix|epoksylim}
This indicates a nested error where "epoxi" has its own correction within a larger error.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from corpustools.error_types import ErrorType


@dataclass
class ErrorSegment:
    """A segment within an error, either plain text or a nested error."""
    
    content: str | ErrorMarkup
    
    @property
    def is_text(self) -> bool:
        """Check if this segment is plain text."""
        return isinstance(self.content, str)
    
    @property
    def is_error(self) -> bool:
        """Check if this segment is a nested error."""
        return isinstance(self.content, ErrorMarkup)
    
    def as_text(self) -> str:
        """Get the text content, extracting from nested errors if needed."""
        if isinstance(self.content, str):
            return self.content
        return self.content.form_as_string()


@dataclass
class ErrorMarkup:
    """Represents a marked up error in a sentence.
    
    Attributes:
        form: The error form/text (can be string or list of ErrorSegments for nested)
        start: Start position in the sentence (byte offset)
        end: End position in the sentence (byte offset)
        errortype: Type of error
        errorinfo: Optional info about the error (e.g. "noun,cons")
        suggestions: List of suggested corrections
    """
    
    form: str | list[ErrorSegment]
    start: int
    end: int
    errortype: ErrorType
    errorinfo: str = ""
    suggestions: list[str] = field(default_factory=lambda: [])
    
    def form_as_string(self) -> str:
        """Get the form as a string (extracts text from nested structures)."""
        if isinstance(self.form, str):
            return self.form
        
        # Nested structure - concatenate all segments
        return "".join(segment.as_text() for segment in self.form)
    
    @property
    def is_nested(self) -> bool:
        """Check if this error has nested structure."""
        return isinstance(self.form, list)
