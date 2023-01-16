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
#   Copyright © 2012-2023 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""This file contains classes to convert files to the Giella xml format."""


import codecs
import distutils.dep_util
import distutils.spawn
import logging
import os
import unicodedata

from lxml import etree

from corpustools import (
    avvirconverter,
    biblexmlconverter,
    ccat,
    corpuspath,
    documentfixer,
    errormarkup,
    htmlcontentconverter,
    languagedetector,
    plaintextconverter,
    svgconverter,
    usxconverter,
    util,
    xslmaker,
    xslsetter,
)

HERE = os.path.dirname(__file__)

logging.basicConfig(level=logging.WARNING)
LOGGER = logging.getLogger(__name__)


def to_giella(path):
    """Convert a document to the giella xml format.

    Args:
        path (str): path to the document

    Returns:
        etree.Element: root of the resulting xml document
    """
    chooser = {
        ".doc": htmlcontentconverter.convert2intermediate,
        ".docx": htmlcontentconverter.convert2intermediate,
        ".epub": htmlcontentconverter.convert2intermediate,
        ".html": htmlcontentconverter.convert2intermediate,
        ".odt": htmlcontentconverter.convert2intermediate,
        ".pdf": htmlcontentconverter.convert2intermediate,
        ".rtf": htmlcontentconverter.convert2intermediate,
        ".svg": svgconverter.convert2intermediate,
        ".txt": plaintextconverter.convert2intermediate,
        ".tex": htmlcontentconverter.convert2intermediate,
        ".usx": usxconverter.convert2intermediate,
    }

    if "avvir_xml" in path:
        return avvirconverter.convert2intermediate(path)
    elif path.endswith("bible.xml"):
        return biblexmlconverter.convert2intermediate(path)
    elif "udhr_" in path and path.endswith(".xml"):
        return htmlcontentconverter.convert2intermediate(path)
    else:
        return chooser[os.path.splitext(path)[1]](path)


class Converter:
    """Take care of data common to all Converter classes."""

    def __init__(self, filename, lazy_conversion=False, write_intermediate=False):
        """Initialise the Converter class.

        Args:
            filename: string containing the path to the file that should
            be converted
            write_intermediate: boolean which decides whether intermediate
            versions of the converted document should be written (used for
            debugging purposes).
        """
        codecs.register_error("mixed", self.mixed_decoder)
        self.names = corpuspath.CorpusPath(filename)
        self.lazy_conversion = lazy_conversion
        self.write_intermediate = write_intermediate
        try:
            self.metadata = xslsetter.MetadataHandler(self.names.xsl, create=True)
        except xslsetter.XsltError as error:
            raise util.ConversionError(error)

        self.metadata.set_lang_genre_xsl()
        with util.ignored(OSError):
            os.makedirs(self.tmpdir)

    @property
    def dependencies(self):
        """Return files that converted files depend on."""
        return [self.names.orig, self.names.xsl]

    @property
    def standard(self):
        """Return a boolean indicating if the file is convertable."""
        return self.metadata.get_variable("conversion_status") == "standard"

    @property
    def goldstandard(self):
        """Return a boolean indicating if the file is a gold standard doc."""
        return self.metadata.get_variable("conversion_status").startswith("correct")

    @staticmethod
    def get_dtd_location():
        """Return the path to the corpus dtd file."""
        return os.path.join(HERE, "dtd/corpus.dtd")

    def validate_complete(self, complete):
        """Validate the complete document."""
        dtd = etree.DTD(Converter.get_dtd_location())

        if not dtd.validate(complete):
            with codecs.open(self.names.log, "w", encoding="utf8") as logfile:
                logfile.write(f"Error at: {str(util.lineno())}")
                for entry in dtd.error_log:
                    logfile.write("\n")
                    logfile.write(str(entry))
                    logfile.write("\n")
                util.print_element(complete, 0, 4, logfile)

            raise util.ConversionError(
                "{}: Not valid XML. More info in the log file: "
                "{}".format(type(self).__name__, self.names.log)
            )

    def transform_to_complete(self):
        """Combine the intermediate xml document with its medatata."""
        try:
            intermediate = to_giella(self.names.orig)
        except KeyError as error:
            raise util.ConversionError(
                "{} can not convert files of this format {}:".format(
                    self.names.orig, str(error)
                )
            )
        try:
            self.fix_document(intermediate)
        except etree.XMLSyntaxError as error:
            with open(self.names.log, "w") as logfile:
                logfile.write(f"Error at: {str(util.lineno())}")

            raise util.ConversionError(
                f"Syntax error in: {self.names}\nError {str(error)}"
            )

        try:
            xsl_maker = xslmaker.XslMaker(self.metadata.tree)
            complete = xsl_maker.transformer(intermediate)

            return complete.getroot()
        except etree.XSLTApplyError as error:
            with open(self.names.log, "w") as logfile:
                logfile.write(f"Error at: {str(util.lineno())}")

            raise util.ConversionError(f"Check the syntax in: {self.names.xsl}")
        except etree.XSLTParseError as error:
            with open(self.names.log, "w") as logfile:
                logfile.write(f"Error at: {str(util.lineno())}")

            raise util.ConversionError(
                f"XSLTParseError in: {self.names.xsl}\nError {str(error)}"
            )

    def convert_errormarkup(self, complete):
        """Convert error markup to xml."""
        if self.goldstandard:
            try:
                errormarkup.add_error_markup(complete.find("body"))
            except errormarkup.ErrorMarkupError as error:
                with open(self.names.log, "w") as logfile:
                    print(str(error), file=logfile)

                raise util.ConversionError(
                    "Markup error. More info in the log file: " f"{self.names.log}"
                )

    def fix_document(self, complete):
        """Fix a misc. issues found in converted document."""
        fixer = documentfixer.DocumentFixer(complete)

        fixer.fix_newstags()
        fixer.soft_hyphen_to_hyph_tag()
        self.metadata.set_variable("wordcount", fixer.calculate_wordcount())

        if not self.goldstandard:
            fixer.detect_quotes()

        # The above line adds text to hyph, fix that
        for hyph in complete.iter("hyph"):
            hyph.text = None

        if self.metadata.get_variable("mainlang") in [
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
                fixer.fix_body_encoding(self.metadata.get_variable("mainlang"))
            except UserWarning as error:
                util.print_frame(error)
                util.print_frame(self.names.orig)

    mixed_to_unicode = {
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

    def mixed_decoder(self, decode_error):
        """Convert text to unicode."""
        badstring = decode_error.object[decode_error.start : decode_error.end]
        badhex = badstring.encode("hex")
        repl = self.mixed_to_unicode.get(badhex, "\ufffd")
        if repl == "\ufffd":  # � unicode REPLACEMENT CHARACTER
            LOGGER.warn("Skipped bad byte \\x%s, seen in %s", badhex, self.names.orig)
        return repl, (decode_error.start + len(repl))

    def fix_parallels(self, complete):
        for parallel in complete.xpath(".//parallel_text"):
            if not parallel.get("location"):
                parallel.getparent().remove(parallel)

    def make_complete(self, language_guesser):
        """Make a complete Giella xml file.

        Combine the intermediate Giella xml file and the metadata into
        a complete Giella xml file.
        Fix the character encoding
        Detect the languages in the xml file
        """
        complete = self.transform_to_complete()
        self.validate_complete(complete)
        self.fix_parallels(complete)
        self.convert_errormarkup(complete)
        lang_detector = languagedetector.LanguageDetector(complete, language_guesser)
        lang_detector.detect_language()

        for para in complete.iter("p"):
            para.tail = "\n"

        return complete

    @staticmethod
    def has_content(complete):
        """Find out if the xml document has any content.

        Args:
            complete: a etree element containing the converted document.

        Returns:
            The length of the content in complete.
        """
        xml_printer = ccat.XMLPrinter(all_paragraphs=True, hyph_replacement=None)
        xml_printer.etree = etree.ElementTree(complete)

        return len(xml_printer.process_file().getvalue())

    def write_complete(self, languageguesser):
        """Write the complete converted document to disk.

        Args:
            languageguesser: a text.Classifier
        """
        if not self.lazy_conversion or (
            self.lazy_conversion
            and distutils.dep_util.newer_group(self.dependencies, self.names.converted)
        ):
            with util.ignored(OSError):
                os.makedirs(os.path.dirname(self.names.converted))

            if self.standard or self.goldstandard:
                complete = self.make_complete(languageguesser)

                if self.has_content(complete):
                    with open(self.names.converted, "w") as converted:
                        print(
                            unicodedata.normalize(
                                "NFC", etree.tostring(complete, encoding="unicode")
                            ),
                            file=converted,
                        )
                else:
                    LOGGER.error("%s has no text", self.names.orig)

    @property
    def tmpdir(self):
        """Return the directory where temporary files should be placed."""
        return os.path.join(self.names.pathcomponents.root, "tmp")

    @property
    def corpusdir(self):
        """Return the directory where the corpus directory is."""
        return self.names.pathcomponents.root
