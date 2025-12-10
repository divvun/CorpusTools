"""Tests for error_annotated_sentence module, ported from Rust tests."""

from corpustools.error_annotated_sentence import ErrorAnnotatedSentence
from corpustools.error_markup import ErrorMarkup
from corpustools.error_types import ErrorType


def test_sentence_no_errors():
    """Test creating a sentence with no errors."""
    sentence = ErrorAnnotatedSentence(text="Muittán doložiid")

    assert sentence.text == "Muittán doložiid"
    assert sentence.error_count() == 0


def test_sentence_with_errors():
    """Test adding errors to a sentence."""
    error = ErrorMarkup(
        form="čohke",
        start=0,
        end=6,
        errortype=ErrorType.ERRORORTREAL,
        suggestions=["čohkke"],
    )

    sentence = ErrorAnnotatedSentence(text="čohke is wrong")
    sentence.errors.append(error)

    assert sentence.error_count() == 1


def test_add_error():
    """Test the add_error method."""
    sentence = ErrorAnnotatedSentence(text="some text")
    assert sentence.error_count() == 0

    sentence.errors.append(ErrorMarkup(
        form="error",
        start=0,
        end=5,
        errortype=ErrorType.ERROR,
    ))

    assert sentence.error_count() == 1


def test_multiple_errors():
    """Test adding multiple errors to a sentence."""
    sentence = ErrorAnnotatedSentence(text="text with errors")
    
    error1 = ErrorMarkup("error1", 0, 6, ErrorType.ERRORORT)
    error2 = ErrorMarkup("error2", 7, 13, ErrorType.ERRORSYN)
    
    sentence.errors.append(error1)
    sentence.errors.append(error2)
    
    assert sentence.error_count() == 2
    assert sentence.errors[0].form == "error1"
    assert sentence.errors[1].form == "error2"


def test_sentence_with_two_simple_errors():
    """Test sentence with two simple errors.
    
    Input: gitta {Nordkjosbotn'ii}${Nordkjosbotnii} (mii lea ge 
    {nordkjosbotn}${Nordkjosbotn} sámegillii? Muhtin, veahket mu!) gos
    """
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


def test_paragraph_character():
    """Test that § character is not confused with error markup.
    
    Input: Vuodoláhkaj §110a
    """
    sentence = ErrorAnnotatedSentence("Vuodoláhkaj §110a")

    assert sentence.error_count() == 0
    assert sentence.text == "Vuodoláhkaj §110a"


def test_sentence_with_multiple_errors_different_types():
    """Test sentence with multiple errors of different types.
    
    Input: ( {nissonin}¢{noun,suf|nissoniin} dušše {0.6 %:s}£{0.6 %} )
    """
    error1 = ErrorMarkup(
        form="nissonin",
        start=2,
        end=2 + len("nissonin"),
        errortype=ErrorType.ERRORORTREAL,
        suggestions=["nissoniin"],
        errorinfo="noun,suf",
    )

    error2 = ErrorMarkup(
        form="0.6 %:s",
        start=2 + len("nissonin") + 7,
        end=2 + len("nissonin") + 7 + len("0.6 %:s"),
        errortype=ErrorType.ERRORMORPHSYN,
        suggestions=["0.6 %"],
    )

    sentence = ErrorAnnotatedSentence("( nissonin dušše 0.6 %:s )")
    sentence.errors.append(error1)
    sentence.errors.append(error2)

    assert sentence.error_count() == 2
    assert sentence.errors[0].errortype == ErrorType.ERRORORTREAL
    assert sentence.errors[1].errortype == ErrorType.ERRORMORPHSYN


def test_multiple_errors_in_sentence():
    """Test sentence with 3 errors."""
    error1 = ErrorMarkup(
        form="njiŋŋalas",
        start=15,
        end=15 + len("njiŋŋalas"),
        errortype=ErrorType.ERRORORT,
        suggestions=["njiŋŋálas"],
        errorinfo="noun,á",
    )
    
    error2 = ErrorMarkup(
        form="ságahuvvon",
        start=25,
        end=25 + len("ságahuvvon"),
        errortype=ErrorType.ERRORORT,
        suggestions=["sagahuvvon"],
        errorinfo="verb,a",
    )
    
    error3 = ErrorMarkup(
        form="guovža-klána",
        start=40,
        end=40 + len("guovža-klána"),
        errortype=ErrorType.ERRORORT,
        suggestions=["guovžaklána"],
        errorinfo="noun,cmp",
    )

    sentence = ErrorAnnotatedSentence(
        "(haploida) ja njiŋŋalas ságahuvvon manneseallas guovža-klána"
    )
    sentence.errors.append(error1)
    sentence.errors.append(error2)
    sentence.errors.append(error3)

    assert sentence.error_count() == 3
    assert sentence.errors[0].errorinfo == "noun,á"
    assert sentence.errors[1].errorinfo == "verb,a"
    assert sentence.errors[2].errorinfo == "noun,cmp"
