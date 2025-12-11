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
"""Tests for error_markup module, ported from Rust tests."""

from corpustools.error_annotated_sentence import ErrorAnnotatedSentence
from corpustools.error_markup import (
    ErrorMarkup,
    ErrorSegment,
)
from corpustools.error_types import ErrorType


def test_create_error_markup():
    """Test creating a simple error markup."""
    markup = ErrorMarkup(
        form="čohke",
        start=0,
        end=6,
        errortype=ErrorType.ERRORORTREAL,
    )
    
    assert markup.form == "čohke"
    assert markup.start == 0
    assert markup.end == 6
    assert markup.errortype == ErrorType.ERRORORTREAL
    assert markup.errorinfo == ""
    assert len(markup.suggestions) == 0


def test_with_suggestions():
    """Test creating error markup with suggestions."""
    markup = ErrorMarkup(
        form="čohke",
        start=0,
        end=6,
        errortype=ErrorType.ERRORORTREAL,
        suggestions=["čohkke"],
    )
    
    assert markup.suggestions == ["čohkke"]


def test_nested_error_markup():
    """Test creating nested error markup.
    
    Example: {{epoxi}${noun,cons|epoksy} lim}¢{noun,mix|epoksylim}
    Inner error: {epoxi}${noun,cons|epoksy}
    """
    # Inner error: {epoxi}${noun,cons|epoksy}
    inner_error = ErrorMarkup(
        form="epoxi",
        start=0,
        end=5,
        errortype=ErrorType.ERRORORT,
        suggestions=["epoksy"],
        errorinfo="noun,cons",
    )
    
    # Outer error contains the inner error and " lim"
    outer_markup = ErrorMarkup(
        form=[
            ErrorSegment(content=inner_error),
            ErrorSegment(content=" lim"),
        ],
        start=0,
        end=10,
        errortype=ErrorType.ERRORORTREAL,
    )
    outer_markup.errorinfo = "noun,mix"
    outer_markup.suggestions = ["epoksylim"]
    
    # Verify structure
    assert outer_markup.is_nested
    assert isinstance(outer_markup.form, list)
    assert len(outer_markup.form) == 2
    
    # Check first segment (nested error)
    first_segment = outer_markup.form[0]
    assert first_segment.is_error
    inner = first_segment.content
    assert isinstance(inner, ErrorMarkup)
    assert inner.form == "epoxi"
    assert inner.errortype == ErrorType.ERRORORT
    assert inner.errorinfo == "noun,cons"
    assert inner.suggestions == ["epoksy"]
    
    # Check second segment (text)
    second_segment = outer_markup.form[1]
    assert second_segment.is_text
    assert second_segment.content == " lim"
    
    # Check outer error attributes
    assert outer_markup.errorinfo == "noun,mix"
    assert outer_markup.suggestions == ["epoksylim"]


def test_form_as_string():
    """Test extracting text from simple and nested structures."""
    # Simple form
    simple = ErrorMarkup("čohke", 0, 6, ErrorType.ERRORORTREAL)
    assert simple.form_as_string() == "čohke"
    
    # Nested form
    inner = ErrorMarkup(form="epoxi", start=0, end=5, errortype=ErrorType.ERRORORT)
    nested = ErrorMarkup(
        form=[
            ErrorSegment(content=inner),
            ErrorSegment(content=" lim"),
        ],
        start=0,
        end=10,
        errortype=ErrorType.ERRORORTREAL,
    )
    assert nested.form_as_string() == "epoxi lim"


def test_add_suggestion():
    """Test adding suggestions to an error."""
    markup = ErrorMarkup(form="čohke", start=0, end=6, errortype=ErrorType.ERRORORTREAL)
    assert len(markup.suggestions) == 0
    
    markup.suggestions.append("čohkke")
    assert markup.suggestions == ["čohkke"]
    
    markup.suggestions.append("čohkka")
    assert markup.suggestions == ["čohkke", "čohkka"]


def test_error_segment_properties():
    """Test ErrorSegment helper properties."""
    # Text segment
    text_seg = ErrorSegment(content="hello")
    assert text_seg.is_text
    assert not text_seg.is_error
    assert text_seg.as_text() == "hello"
    
    # Error segment
    error = ErrorMarkup(form="test", start=0, end=4, errortype=ErrorType.ERRORORT)
    error_seg = ErrorSegment(content=error)
    assert error_seg.is_error
    assert not error_seg.is_text
    assert error_seg.as_text() == "test"


def test_sentence_with_two_simple_errors():
    """Test sentence with two simple errors."""
    # Input: gitta {Nordkjosbotn'ii}${Nordkjosbotnii} (mii lea ge 
    # {nordkjosbotn}${Nordkjosbotn} sámegillii? Muhtin, veahket mu!) gos
    
    text = "gitta Nordkjosbotn'ii (mii lea ge nordkjosbotn sámegillii? Muhtin, veahket mu!) gos"
    
    error1 = ErrorMarkup(
        form="Nordkjosbotn'ii",
        start=6,
        end=6 + len("Nordkjosbotn'ii"),
        errortype=ErrorType.ERRORORT,
        suggestions=["Nordkjosbotnii"],
    )

    error2 = ErrorMarkup(
        form="nordkjosbotn",
        start=35,
        end=35 + len("nordkjosbotn"),
        errortype=ErrorType.ERRORORT,
        suggestions=["Nordkjosbotn"],
    )

    sentence = ErrorAnnotatedSentence(text)
    sentence.errors.append(error1)
    sentence.errors.append(error2)

    assert sentence.error_count() == 2
    assert sentence.errors[0].suggestions == ["Nordkjosbotnii"]
    assert sentence.errors[1].suggestions == ["Nordkjosbotn"]


def test_only_text_no_errors():
    """Test sentence with only text and no errors."""
    # Input: Muittán doložiid
    sentence = ErrorAnnotatedSentence("Muittán doložiid")

    assert sentence.error_count() == 0
    assert sentence.text == "Muittán doložiid"


def test_paragraph_character():
    """Test that § character is not confused with error markup."""
    # Input: Vuodoláhkaj §110a
    sentence = ErrorAnnotatedSentence("Vuodoláhkaj §110a")

    assert sentence.error_count() == 0
    assert sentence.text == "Vuodoláhkaj §110a"


def test_errorlang_infinity():
    """Test errorlang with infinity symbol.
    
    Input: {molekylærbiologimi}∞{kal,bio}
    """
    error = ErrorMarkup(
        form="molekylærbiologimi",
        start=0,
        end=len("molekylærbiologimi"),
        errortype=ErrorType.ERRORLANG,
        suggestions=["kal,bio"],
    )

    assert error.errortype == ErrorType.ERRORLANG
    assert error.suggestions == ["kal,bio"]


def test_quote_char():
    """Test error with quote characters.
    
    Input: {"sjievnnijis"}${conc,vnn-vnnj|sjievnnjis}
    """
    error = ErrorMarkup(
        form='"sjievnnijis"',
        start=0,
        end=len('"sjievnnijis"'),
        errortype=ErrorType.ERRORORT,
        suggestions=["sjievnnjis"],
        errorinfo="conc,vnn-vnnj",
    )

    assert error.errortype == ErrorType.ERRORORT
    assert error.errorinfo == "conc,vnn-vnnj"
    assert error.suggestions == ["sjievnnjis"]


def test_errorort1():
    """Test orthographic error with abbreviation.
    
    Input: {jne.}${adv,typo|jna.}
    """
    error = ErrorMarkup(
        form="jne.",
        start=0,
        end=len("jne."),
        errortype=ErrorType.ERRORORT,
        suggestions=["jna."],
        errorinfo="adv,typo",
    )

    assert error.errortype == ErrorType.ERRORORT
    assert error.errorinfo == "adv,typo"
    assert error.suggestions == ["jna."]


def test_error_morphsyn1():
    """Test morphosyntactic error.
    
    Input: {Nieiddat leat nuorra}£{a,spred,nompl,nomsg,agr|Nieiddat leat nuorat}
    """
    error = ErrorMarkup(
        form="Nieiddat leat nuorra",
        start=0,
        end=len("Nieiddat leat nuorra"),
        errortype=ErrorType.ERRORMORPHSYN,
        suggestions=["Nieiddat leat nuorat"],
        errorinfo="a,spred,nompl,nomsg,agr",
    )

    assert error.errortype == ErrorType.ERRORMORPHSYN
    assert error.errorinfo == "a,spred,nompl,nomsg,agr"
    assert error.suggestions == ["Nieiddat leat nuorat"]


def test_errorort_with_slash():
    """Test orthographic error with slash.
    
    Input: {magistter/}${loan,vowlat,e-a|magisttar}
    """
    error = ErrorMarkup(
        form="magistter/",
        start=0,
        end=len("magistter/"),
        errortype=ErrorType.ERRORORT,
        suggestions=["magisttar"],
        errorinfo="loan,vowlat,e-a",
    )

    assert error.errorinfo == "loan,vowlat,e-a"
    assert error.suggestions == ["magisttar"]


def test_error_correct_generic():
    """Test generic error.
    
    Input: {1]}§{Ij}
    """
    error = ErrorMarkup(
        form="1]",
        start=0,
        end=len("1]"),
        errortype=ErrorType.ERROR,
        suggestions=["Ij"],
    )

    assert error.errortype == ErrorType.ERROR
    assert error.suggestions == ["Ij"]


def test_error_lex1():
    """Test lexical error.
    
    Input: {dábálaš}€{adv,adj,der|dábálaččat}
    """
    error = ErrorMarkup(
        form="dábálaš",
        start=0,
        end=len("dábálaš"),
        errortype=ErrorType.ERRORLEX,
        suggestions=["dábálaččat"],
        errorinfo="adv,adj,der",
    )

    assert error.errortype == ErrorType.ERRORLEX
    assert error.errorinfo == "adv,adj,der"
    assert error.suggestions == ["dábálaččat"]


def test_error_ortreal1():
    """Test real orthographic error.
    
    Input: {ráhččamušaid}¢{noun,mix|rahčamušaid}
    """
    error = ErrorMarkup(
        form="ráhččamušaid",
        start=0,
        end=len("ráhččamušaid"),
        errortype=ErrorType.ERRORORTREAL,
        suggestions=["rahčamušaid"],
        errorinfo="noun,mix",
    )

    assert error.errortype == ErrorType.ERRORORTREAL
    assert error.errorinfo == "noun,mix"
    assert error.suggestions == ["rahčamušaid"]


def test_error_syn1():
    """Test syntactic error.
    
    Input: {riŋgen nieidda lusa}¥{x,pph|riŋgen niidii}
    """
    error = ErrorMarkup(
        form="riŋgen nieidda lusa",
        start=0,
        end=len("riŋgen nieidda lusa"),
        errortype=ErrorType.ERRORSYN,
        suggestions=["riŋgen niidii"],
        errorinfo="x,pph",
    )

    assert error.errortype == ErrorType.ERRORSYN
    assert error.errorinfo == "x,pph"
    assert error.suggestions == ["riŋgen niidii"]


def test_error_syn_with_empty_correction():
    """Test syntactic error with empty correction.
    
    Input: {ovtta}¥{num,redun| }
    """
    error = ErrorMarkup(
        form="ovtta",
        start=0,
        end=len("ovtta"),
        errortype=ErrorType.ERRORSYN,
        suggestions=[""],
        errorinfo="num,redun",
    )

    assert error.errorinfo == "num,redun"
    assert error.suggestions == [""]


def test_nested_error_format():
    """Test nested error markup.
    
    Input: {{A  B}‰{notspace|A B}  C}‰{notspace|A B C}
    """
    inner_error = ErrorMarkup(
        form="A  B",
        start=0,
        end=4,
        errortype=ErrorType.ERRORFORMAT,
        suggestions=["A B"],
        errorinfo="notspace",
    )

    outer_error = ErrorMarkup(
        form=[
            ErrorSegment(content=inner_error),
            ErrorSegment(content="  C"),
        ],
        start=0,
        end=8,
        errortype=ErrorType.ERRORFORMAT,
        suggestions=["A B C"],
        errorinfo="notspace",
    )

    # Verify nested structure
    assert outer_error.is_nested
    assert isinstance(outer_error.form, list)
    assert len(outer_error.form) == 2
    
    # Check first segment (nested error)
    first_segment = outer_error.form[0]
    assert first_segment.is_error
    assert isinstance(first_segment.content, ErrorMarkup)
    assert first_segment.content.errortype == ErrorType.ERRORFORMAT
    assert first_segment.content.errorinfo == "notspace"
    
    # Check second segment (text)
    second_segment = outer_error.form[1]
    assert second_segment.is_text
    assert second_segment.content == "  C"


def test_inline_multiple_corrections():
    """Test error with multiple suggestions.
    
    Input: {leimme}£{leimmet///leat}
    """
    error = ErrorMarkup(
        form="leimme",
        start=0,
        end=len("leimme"),
        errortype=ErrorType.ERRORMORPHSYN,
        suggestions=["leimmet", "leat"],
    )

    assert error.errortype == ErrorType.ERRORMORPHSYN
    assert len(error.suggestions) == 2
    assert error.suggestions == ["leimmet", "leat"]
