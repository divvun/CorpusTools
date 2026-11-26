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
#   Copyright © 2012-2026 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""This file contains functions to convert files to the Giella xml format."""

import codecs
import logging
import unicodedata
from functools import partial
from pathlib import Path
from typing import Callable

from lxml import etree

from corpustools import (
    avvirconverter,
    avvirdigital,
    biblesfmconverter,
    biblexmlconverter,
    ccat,
    documentfixer,
    error_annotated_converter,
    htmlcontentconverter,
    languagedetector,
    plaintextconverter,
    svgconverter,
    text_cat,
    usxconverter,
    util,
    xslmaker,
    xslsetter,
)
from corpustools.corpuspath import CorpusPath

HERE = Path(__file__).parent

logging.basicConfig(level=logging.WARNING)
LOGGER = logging.getLogger(__name__)

MIXED_TO_UNICODE = {
    "e4": "ä",
    "85": "…",  # u'\u2026' ... character.
    "96": "–",  # u'\u2013' en-dash
    "97": "—",  # u'\u2014' em-dash
    "91": "‘",  # u'\u2018' left single quote
    "92": "’",  # u'\u2019' right single quote
    "93": "“",  # u'\u201C' left double quote
    "94": "”",  # u'\u201D' right double quote
    "95": "•",  # u'\u2022' bullet
}

GOLDSTANDARD_STATUSES = ["goldstandard", "correct"]


def newer_group(sources: list[Path], target: Path) -> bool:
    if not target.exists():
        # Target does not exist, so we say that "sources are newer"
        return True

    target_mtime = target.stat().st_mtime

    return any(src.stat().st_mtime > target_mtime for src in sources)


def dependencies(names: CorpusPath) -> list[Path]:
    """Return files that converted files depend on."""
    return [names.orig, names.xsl]


def is_standard(names: CorpusPath) -> bool:
    """Return a boolean indicating if the file is convertable."""
    return names.metadata.get_variable("conversion_status") == "standard"


def is_goldstandard(names: CorpusPath) -> bool:
    """Return a boolean indicating if the file is a gold standard doc."""
    return names.metadata.get_variable("conversion_status") in GOLDSTANDARD_STATUSES


def get_tmpdir(names: CorpusPath) -> Path:
    """Return the directory where temporary files should be placed."""
    return names.converted_corpus_dir / "tmp"


def get_dtd_location() -> Path:
    """Return the path to the corpus dtd file."""
    return HERE / "dtd" / "corpus.dtd"


def validate_complete(complete: etree.Element, names: CorpusPath) -> None:
    """Validate the complete document."""
    dtd = etree.DTD(str(get_dtd_location()))

    if not dtd.validate(complete):
        names.log.write_text(
            f"Error at: {str(util.lineno())}"
            + "\n".join(str(entry) for entry in dtd.error_log)
            + "\n".join(util.print_element(complete, 0, 4))
        )

        raise util.ConversionError(
            f"Converter: Not valid XML. More info in the log file: {names.log}"
        )


def to_giella(path: Path) -> etree.ElementTree:
    """Convert a document to the giella xml format.

    Args:
        path: path to the document

    Returns:
        The converted document as an lxml ElementTree.
    """
    chooser: dict[str, Callable[[Path], etree.ElementTree]] = {
        ".doc": htmlcontentconverter.convert2intermediate,
        ".docx": htmlcontentconverter.convert2intermediate,
        ".epub": htmlcontentconverter.convert2intermediate,
        ".html": htmlcontentconverter.convert2intermediate,
        ".odt": htmlcontentconverter.convert2intermediate,
        ".pdf": htmlcontentconverter.convert2intermediate,
        ".rtf": htmlcontentconverter.convert2intermediate,
        ".sfm": biblesfmconverter.convert2intermediate,
        ".svg": svgconverter.convert2intermediate,
        ".txt": plaintextconverter.convert2intermediate,
        ".tex": htmlcontentconverter.convert2intermediate,
        ".writenow": htmlcontentconverter.convert2intermediate,
        ".usx": usxconverter.convert2intermediate,
        ".correct.txt": error_annotated_converter.convert2intermediate,
    }

    str_path = path.absolute().as_posix()
    if "avvir_xml" in str_path and path.suffix == ".xml":
        return avvirconverter.convert2intermediate(path)
    if "avvir_xml" in str_path and path.suffix == ".digital":
        return avvirdigital.convert2intermediate(path)
    elif str_path.endswith("bible.xml"):
        return biblexmlconverter.convert2intermediate(path)
    elif "udhr_" in str_path and path.suffix == ".xml":
        return htmlcontentconverter.convert2intermediate(path)
    elif path.name.endswith(".correct.txt"):
        return error_annotated_converter.convert2intermediate(path)
    else:
        return chooser[path.suffix](path)


def transform_to_complete(names: CorpusPath) -> etree.Element:
    """Combine the intermediate xml document with its medatata."""
    try:
        intermediate = to_giella(names.orig)
    except KeyError as error:
        raise util.ConversionError(
            f"{names.orig} can not convert files of this format {str(error)}:"
        ) from error
    try:
        fix_document(intermediate.getroot(), names)
    except etree.XMLSyntaxError as error:
        with open(names.log, "w") as logfile:
            logfile.write(f"Error at: {str(util.lineno())}")

        raise util.ConversionError(
            f"Syntax error in: {names}\nError {str(error)}"
        ) from error

    try:
        xsl_maker = xslmaker.XslMaker(names.metadata.tree)
        complete = xsl_maker.transformer(intermediate)

        return complete.getroot()
    except etree.XSLTApplyError:
        with open(names.log, "w") as logfile:
            logfile.write(f"Error at: {str(util.lineno())}")

        raise util.ConversionError(f"Check the syntax in: {names.xsl}") from None
    except etree.XSLTParseError as error:
        with open(names.log, "w") as logfile:
            logfile.write(f"Error at: {str(util.lineno())}")

        raise util.ConversionError(
            f"XSLTParseError in: {names.xsl}\nError {str(error)}"
        ) from error


def fix_document(complete: etree.Element, names: CorpusPath) -> None:
    """Fix a misc. issues found in converted document."""
    fixer = documentfixer.DocumentFixer(complete)

    fixer.fix_newstags()
    fixer.soft_hyphen_to_hyph_tag()
    names.metadata.set_variable("wordcount", fixer.calculate_wordcount())

    if not is_goldstandard(names):
        fixer.detect_quotes()

    # The above line adds text to hyph, fix that
    for hyph in complete.iter("hyph"):
        hyph.text = None

    if names.metadata.get_variable("mainlang") in [
        "sma",
        "sme",
        "smj",
        "smn",
        "sms",
        "nob",
        "fin",
        "swe",
        "nno",
        "dan",
        "fkv",
        "sju",
        "sje",
        "mhr",
        "mrj",
        "mns",
    ]:
        try:
            mainlang = names.metadata.get_variable("mainlang")
            if mainlang is not None:
                fixer.fix_body_encoding(mainlang)
        except UserWarning as error:
            util.print_frame(str(error))
            util.print_frame(str(names.orig))


def mixed_decoder(orig: Path, decode_error: UnicodeDecodeError) -> tuple[str, int]:
    """Convert text to unicode."""
    badstring = decode_error.object[decode_error.start : decode_error.end]
    badhex = badstring.hex()
    repl = MIXED_TO_UNICODE.get(badhex, "\ufffd")
    if repl == "\ufffd":  # � unicode REPLACEMENT CHARACTER
        LOGGER.warning("Skipped bad byte \\x%s, seen in %s", badhex, orig)
    return repl, decode_error.end


def fix_parallels(complete: etree.Element) -> None:
    for parallel in complete.xpath(".//parallel_text"):
        if not parallel.get("location"):
            parallel.getparent().remove(parallel)


def make_complete(
    names: CorpusPath, language_guesser: text_cat.Classifier | None
) -> etree.Element:
    """Make a complete Giella xml file.

    Combine the intermediate Giella xml file and the metadata into
    a complete Giella xml file.
    Fix the character encoding
    Detect the languages in the xml file
    """
    complete = transform_to_complete(names)
    validate_complete(complete, names)
    fix_parallels(complete)
    lang_detector = languagedetector.LanguageDetector(complete, language_guesser)
    lang_detector.detect_language()

    # Add whitespace to separate header, body and paragraphs
    # and make it easier to see where the diffs are
    header = complete.find("header")
    if header is not None:
        header.tail = "\n"
    body = complete.find("body")
    if body is not None:
        body.text = "\n"
    for para in complete.iter("p"):
        para.tail = "\n"

    return complete


def has_content(complete: etree.Element) -> int:
    """Find out if the xml document has any content.

    Args:
        complete (lxml.etree.Element): a etree element containing
            the converted document.

    Returns:
        (int): The length of the content in complete.
    """
    options = ccat.make_options(all_paragraphs=True, hyph_replacement="")
    return len(ccat.process_file(options, etree.ElementTree(complete)).getvalue())


def write_complete(
    names: CorpusPath,
    languageguesser: text_cat.Classifier | None,
    lazy_conversion: bool = False,
) -> None:
    """Write the complete converted document to disk.

    Args:
        names: the path to the file that should be converted
        languageguesser: a text.Classifier
        lazy_conversion: only convert if the dependencies are newer than the
            converted file.
    """
    codecs.register_error("mixed", partial(mixed_decoder, names.orig))
    try:
        names.metadata.set_lang_genre_xsl()
    except xslsetter.XsltError as error:
        raise util.ConversionError(error) from error

    with util.ignored(OSError):
        get_tmpdir(names).mkdir(parents=True, exist_ok=True)

    if lazy_conversion and not newer_group(dependencies(names), names.converted):
        return

    with util.ignored(OSError):
        names.converted.parent.mkdir(parents=True, exist_ok=True)

    if is_standard(names) or is_goldstandard(names):
        complete = make_complete(names, languageguesser)

        if has_content(complete):
            with open(names.converted, "w") as converted:
                print(
                    unicodedata.normalize(
                        "NFC", etree.tostring(complete, encoding="unicode")
                    ),
                    file=converted,
                )
        else:
            LOGGER.error("%s has no text", names.orig)
