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
"""Error type symbols and their corresponding error categories.

These symbols are used in the markup syntax to indicate different types of errors:
- Basic syntax: {error}${correction}
- Nested syntax: {{error1}${correction_of_error1}}£{correction_of_correction1}
"""

from enum import Enum


class ErrorType(Enum):
    """Error type enumeration with associated symbols.

    Each error type has:
    - An enum name (built-in .name attribute)
    - A symbol character used in markup
    - A string representation for serialization
    """

    # Orthographic error (spelling)
    ERRORORT = ("errorort", "$")

    # Real orthographic error
    ERRORORTREAL = ("errorortreal", "¢")

    # Lexical error
    ERRORLEX = ("errorlex", "€")

    # Morphosyntactic error
    ERRORMORPHSYN = ("errormorphsyn", "£")

    # Syntactic error
    ERRORSYN = ("errorsyn", "¥")

    # Generic error
    ERROR = ("error", "§")

    # Language error
    ERRORLANG = ("errorlang", "∞")

    # Format error
    ERRORFORMAT = ("errorformat", "‰")

    @property
    def symbol(self) -> str:
        """Get the symbol character for this error type."""
        return self.value[1]

    @property
    def error_name(self) -> str:
        """Get the error type name as a string (e.g., 'errorort')."""
        return self.value[0]

    def __str__(self) -> str:
        """String representation returns the error name (e.g., 'errorort')."""
        return self.error_name


# Module-level convenience functions


def error_type_from_symbol(symbol: str) -> ErrorType | None:
    """Parse an error type from a symbol character.

    Args:
        symbol: The symbol character to look up

    Returns:
        The corresponding ErrorType, or None if symbol is invalid

    Example:
        >>> error_type_from_symbol("$")
        <ErrorType.ERRORORT: ('errorort', '$')>
    """
    for error_type in ErrorType:
        if error_type.symbol == symbol:
            return error_type
    return None


def all_error_symbols() -> list[str]:
    """Get all valid error type symbols.

    Returns:
        List of all symbol characters

    Example:
        >>> all_error_symbols()
        ['$', '¢', '€', '£', '¥', '§', '∞', '‰']
    """
    return [error_type.symbol for error_type in ErrorType]


class ErrorMarkupError(Exception):
    """This is raised for errors in this module."""

    pass
