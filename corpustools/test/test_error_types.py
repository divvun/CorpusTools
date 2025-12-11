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
"""Tests for error_types module, ported from Rust tests."""


from corpustools.error_types import (
    ErrorType,
    all_error_symbols,
    error_type_from_symbol,
)


def test_symbol_roundtrip():
    """Test that all error types can be converted to/from symbols."""
    for error_type in ErrorType:
        symbol = error_type.symbol
        assert error_type_from_symbol(symbol) == error_type


def test_invalid_symbol():
    """Test that invalid symbols return None."""
    assert error_type_from_symbol("x") is None
    assert error_type_from_symbol("@") is None


def test_name():
    """Test that error type names are correct."""
    assert ErrorType.ERRORORT.name == "ERRORORT"
    assert ErrorType.ERRORMORPHSYN.name == "ERRORMORPHSYN"


def test_all_symbols():
    """Test that all_symbols returns the expected list."""
    symbols = all_error_symbols()
    expected = ["$", "¢", "€", "£", "¥", "§", "∞", "‰"]
    assert symbols == expected


def test_str_representation():
    """Test string representation."""
    assert str(ErrorType.ERRORORT) == "errorort"
    assert str(ErrorType.ERRORSYN) == "errorsyn"


def test_specific_symbols():
    """Test specific symbol mappings."""
    assert ErrorType.ERRORORT.symbol == "$"
    assert ErrorType.ERRORORTREAL.symbol == "¢"
    assert ErrorType.ERRORLEX.symbol == "€"
    assert ErrorType.ERRORMORPHSYN.symbol == "£"
    assert ErrorType.ERRORSYN.symbol == "¥"
    assert ErrorType.ERROR.symbol == "§"
    assert ErrorType.ERRORLANG.symbol == "∞"
    assert ErrorType.ERRORFORMAT.symbol == "‰"
