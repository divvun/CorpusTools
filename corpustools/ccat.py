#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this file. If not, see <http://www.gnu.org/licenses/>.
#
#   Copyright © 2013-2025 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Classes and functions to convert giellatekno xml formatted files to text."""

import argparse
import os
import sys
from functools import wraps
from io import StringIO
from traceback import print_exc

from lxml import etree

from corpustools import argparse_version
from corpustools.corpuspath import CorpusPath
from corpustools.orthographies import is_orthography_of, orthographies


def suppress_broken_pipe_msg(function):
    """Suppress message after a broken pipe error.

    This code is fetched from:
    http://stackoverflow.com/questions/14207708/ioerror-errno-32-broken-pipe-python

    Args:
        function (function): the function that should be wrapped by this function.
    """

    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except SystemExit:
            raise
        except:
            print_exc()
            sys.exit(1)
        finally:
            try:
                sys.stdout.flush()
            finally:
                try:
                    sys.stdout.close()
                finally:
                    try:
                        sys.stderr.flush()
                    finally:
                        sys.stderr.close()

    return wrapper


class XMLPrinter:
    """Convert giellatekno xml formatted files to plain text."""

    def __init__(  # noqa: PLR0913, PLR0915
        self,
        lang=None,
        all_paragraphs=False,
        title=False,
        listitem=False,
        table=False,
        correction=False,
        error=False,
        errorort=False,
        errorortreal=False,
        errormorphsyn=False,
        errorsyn=False,
        errorlex=False,
        errorlang=False,
        foreign=False,
        errorformat=False,
        noforeign=False,
        withforeign=False,
        typos=False,
        print_filename=False,
        one_word_per_line=False,
        disambiguation=False,
        dependency=False,
        hyph_replacement="",
        orthography=None,
    ):
        """Setup all the options.

        The handling of error* elements are governed by the error*,
        noforeign, correction, typos and one_word_per_line arguments.

        If one_word_per_line and typos are False and correction is True, the
        content of the correct attribute should be printed instead of the
        .text part of the error element.

        If one_word_per_line or typos are True, the .text part, the correct
        attribute and the other attributes of the error* element should be
        printed out on one line.

        If typos is True and some of the error* options are True, only the
        elements that are True should be output

        If one_word_per_line is True and some of the error* options are True,
        only the elements that are True should get the error treatment, the
        other ones get treated as plain elements.

        If noforeign is True, neither the errorlang.text part nor the correct
        attribute should be printed.
        """
        self.paragraph = True
        self.all_paragraphs = all_paragraphs

        if title or listitem or table:
            self.paragraph = False

        self.title = title
        self.listitem = listitem
        self.table = table

        self.correction = correction
        self.error = error
        self.errorort = errorort
        self.errorortreal = errorortreal
        self.errormorphsyn = errormorphsyn
        self.errorsyn = errorsyn
        self.errorlex = errorlex
        self.errorlang = errorlang
        self.noforeign = noforeign
        self.foreign = foreign
        self.errorformat = errorformat

        self.error_filtering = (
            error
            or errorort
            or errorortreal
            or errormorphsyn
            or errorsyn
            or errorlex
            or errorlang
            or errorformat
        )

        if withforeign:
            self.correction = False
            self.error = True
            self.errorort = True
            self.errorortreal = True
            self.errormorphsyn = True
            self.errorsyn = True
            self.errorlex = True
            self.errorformat = True
            self.errorlang = False
            self.noforeign = False
            self.error_filtering = True

        self.typos = typos
        self.print_filename = print_filename
        if self.typos:
            self.one_word_per_line = True
        else:
            self.one_word_per_line = one_word_per_line

        if lang and lang.startswith("!"):
            self.lang = lang[1:]
            self.invert_lang = True
        else:
            self.lang = lang
            self.invert_lang = False

        self.disambiguation = disambiguation
        self.dependency = dependency

        if hyph_replacement == "xml":
            self.hyph_replacement = "<hyph/>"
        else:
            self.hyph_replacement = hyph_replacement

        self.orthography = orthography

    def get_lang(self):
        """Get the lang of the file."""
        return self.etree.getroot().attrib["{http://www.w3.org/XML/1998/namespace}lang"]

    @staticmethod
    def get_element_language(element, parentlang):
        """Get the language of element.

        Elements inherit the parents language if not explicitely set
        """
        if element.get("{http://www.w3.org/XML/1998/namespace}lang") is None:
            return parentlang
        else:
            return element.get("{http://www.w3.org/XML/1998/namespace}lang")

    def collect_not_inline_errors(self, element, textlist):
        """Add the formatted errors as strings to the textlist list."""
        error_string = self.error_not_inline(element)
        if error_string != "":
            textlist.append(error_string)

        for child in element:
            if self.visit_error_not_inline(child):
                self.collect_not_inline_errors(child, textlist)

        if not self.typos:
            if element.tail is not None and element.tail.strip() != "":
                if not self.one_word_per_line:
                    textlist.append(element.tail)
                else:
                    textlist.extend(element.tail.strip().split())

    @staticmethod
    def corrected_texts(error_element):
        """Yield corrected versions of the error element."""
        for correct in error_element.xpath("./correct"):
            correct_text = "" if correct.text is None else correct.text
            tail_text = "" if error_element.tail is None else error_element.tail
            yield f"{correct_text}{tail_text}"

    def error_not_inline(self, element):
        """Collect and format parts of the element.

        Also scan the children if there is no error filtering or
        if the element is filtered
        """
        text = []
        if element.text is not None and element.text.strip() != "":
            text.append(element.text)

        if not self.error_filtering or self.include_this_error(element):
            for child in element:
                if child.tag != "correct":
                    text.extend(corrected for corrected in self.corrected_texts(child))

        text.extend(
            self.get_error_attributes(correct) for correct in element.xpath("./correct")
        )
        return "".join(text)

    @staticmethod
    def combine(text, text_list):
        """Combine a text with a parto f the text_list."""
        return [f"{text}{part}" for part in text_list]

    def get_error_attributes(self, correct_element):
        """Collect and format the attributes + the filename."""
        text = ["\t"]
        text.append("" if correct_element.text is None else correct_element.text)

        attributes = correct_element.attrib
        attr = [key + "=" + str(attributes[key]) for key in sorted(attributes)]

        if attr:
            text.append("\t#")
            text.append(",".join(attr))

            if self.print_filename:
                text.append(f", file: {os.path.basename(self.filename)}")

        elif self.print_filename:
            text.append(f"\t#file: {os.path.basename(self.filename)}")

        return "".join(text)

    def collect_inline_errors(self, element, textlist, parentlang):
        """Add the "correct" element to the list textlist."""
        correct = element.find("./correct")
        if correct is not None and not self.noforeign:
            textlist.append("" if correct.text is None else correct.text)

        self.get_contents(element.tail, textlist, parentlang)

    def collect_text(self, element, parentlang, buffer):
        """Collect text from element, and write the contents to buffer."""
        textlist = []

        self.visit_nonerror_element(element, textlist, parentlang)

        if textlist:
            if not self.one_word_per_line:
                textlist[-1] = textlist[-1].rstrip()
                buffer.write("".join(textlist))
                buffer.write(" ¶\n")
            else:
                buffer.write("\n".join(textlist))
                buffer.write("\n")

    def is_correct_lang(self, elt_lang):
        """Check if elt_lang is a wanted language.

        Args:
            elt_lang (str): a three character language.

        Returns:
            (bool): boolean
        """
        return (
            self.lang is None
            or (not self.invert_lang and elt_lang == self.lang)
            or (self.invert_lang and elt_lang != self.lang)
        )

    def get_contents(self, elt_contents, textlist, elt_lang):
        """Get the contents of a xml document.

        Args:
            elt_contents (str): the text of an etree element.
            textlist (list of str): text will be added this list.
            elt_lang (str): language of the element.
        """
        if elt_contents is not None:
            text = elt_contents
            if self.is_correct_lang(elt_lang):
                if not self.one_word_per_line:
                    textlist.append(text)
                else:
                    textlist.extend(text.split())

    def visit_children(self, element, textlist, parentlang):
        """Visit the children of element, adding their content to textlist."""
        for child in element:
            if child.tag != "correct":
                if child.tag == "errorlang" and self.noforeign and self.typos:
                    pass
                elif child.tag == "errorlang" and self.noforeign:
                    self.get_contents(child.tail, textlist, parentlang)
                elif self.visit_error_inline(child):
                    self.collect_inline_errors(
                        child, textlist, self.get_element_language(child, parentlang)
                    )
                elif self.visit_error_not_inline(child):
                    self.collect_not_inline_errors(child, textlist)
                else:
                    self.visit_nonerror_element(
                        child, textlist, self.get_element_language(element, parentlang)
                    )

    def visit_nonerror_element(self, element, textlist, parentlang):
        """Visit and extract text from non error element."""
        if not self.typos:
            self.get_contents(
                element.text, textlist, self.get_element_language(element, parentlang)
            )
        self.visit_children(element, textlist, parentlang)
        if not self.typos:
            self.get_contents(element.tail, textlist, parentlang)

    def visit_this_node(self, element):
        """Return True if the element should be visited."""
        return (
            self.all_paragraphs
            or (
                self.paragraph is True
                and (element.get("type") is None or element.get("type") == "text")
            )
            or (self.title is True and element.get("type") == "title")
            or (self.listitem is True and element.get("type") == "listitem")
            or (self.table is True and element.get("type") == "tablecell")
        )

    def visit_error_not_inline(self, element):
        """Determine whether element should be visited."""
        return (
            element.tag.startswith("error")
            and self.one_word_per_line
            and not self.error_filtering
            or self.include_this_error(element)
        )

    def visit_error_inline(self, element):
        """Determine whether element should be visited."""
        return (
            element.tag.startswith("error")
            and not self.one_word_per_line
            and (self.correction or self.include_this_error(element))
        )

    def include_this_error(self, element):
        """Determine whether element should be visited."""
        return self.error_filtering and (
            (element.tag == "error" and self.error)
            or (element.tag == "errorort" and self.errorort)
            or (element.tag == "errorortreal" and self.errorortreal)
            or (element.tag == "errormorphsyn" and self.errormorphsyn)
            or (element.tag == "errorsyn" and self.errorsyn)
            or (element.tag == "errorlex" and self.errorlex)
            or (element.tag == "errorformat" and self.errorformat)
            or (element.tag == "errorlang" and self.errorlang)
            or (element.tag == "errorlang" and self.noforeign)
        )

    def parse_file(self, filename):
        """Parse the xml document.

        Args:
            filename (str): path to the filename.
        """
        self.filename = filename
        p = etree.XMLParser(huge_tree=True)
        self.etree = etree.parse(filename, p)

    def process_file(self):
        """Process the given file, adding the text into buffer.

        Returns the buffer
        """
        buffer = StringIO()

        self.handle_hyph()
        if self.dependency:
            self.print_element(self.etree.find(".//dependency"), buffer)
        elif self.disambiguation:
            self.print_element(self.etree.find(".//disambiguation"), buffer)
        else:
            for paragraph in self.etree.findall(".//p"):
                if self.is_correct_lang(
                    self.get_element_language(paragraph, self.get_lang())
                ) and self.visit_this_node(paragraph):
                    self.collect_text(paragraph, self.get_lang(), buffer)

        return buffer

    def handle_hyph(self):
        """Replace hyph tags."""
        hyph_tails = []
        for hyph in self.etree.findall(".//hyph"):
            if hyph.tail is not None:
                hyph_tails.append(hyph.tail)

            if hyph.getnext() is None:
                if hyph.getparent().text is not None:
                    hyph_tails.insert(0, hyph.getparent().text)
                hyph.getparent().text = self.hyph_replacement.join(hyph_tails)
                hyph_tails[:] = []

            hyph.getparent().remove(hyph)

    def print_element(self, element, buffer):
        """Write the text of the element to the buffer.

        Args:
            element (etree._Element):
            buffer ():
        """
        if element is not None and element.text is not None:
            buffer.write(element.text)

    def print_file(self, file_):
        """Print a xml file to stdout. Returns True if something was printed,
        False otherwise."""
        if not file_.endswith(".xml"):
            return False

        self.parse_file(file_)
        text_orthography = self.etree.find(".//header/orthography")
        wanted_orthography = self.orthography

        if text_orthography is None or text_orthography.text == "":
            # text has standard orthography, show text if no --orthography
            # was given
            show_text = wanted_orthography is None
        else:
            # text has specific orthoraphy! show only if wanted orthoraphy
            # is same as this text has!
            show_text = text_orthography.text == wanted_orthography

        if show_text:
            try:
                sys.stdout.write(self.process_file().getvalue())
                return True
            except BrokenPipeError:
                pass


def parse_options():
    """Parse the options given to the program."""
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Print the contents of a corpus in XML format\n\
        The default is to print paragraphs with no type (=text type).",
    )

    parser.add_argument(
        "-l",
        dest="lang",
        help="Print only elements in language LANG. Default \
                        is all langs.",
    )
    parser.add_argument(
        "-T", dest="title", action="store_true", help="Print paragraphs with title type"
    )
    parser.add_argument(
        "-L", dest="list", action="store_true", help="Print paragraphs with list type"
    )
    parser.add_argument(
        "-t", dest="table", action="store_true", help="Print paragraphs with table type"
    )
    parser.add_argument(
        "-a", dest="all_paragraphs", action="store_true", help="Print all text elements"
    )

    parser.add_argument(
        "-c",
        dest="corrections",
        action="store_true",
        help="Print corrected text instead of the original \
                        typos & errors",
    )
    parser.add_argument(
        "-C",
        dest="error",
        action="store_true",
        help="Only print unclassified (§/<error..>) \
                        corrections",
    )
    parser.add_argument(
        "-ort",
        dest="errorort",
        action="store_true",
        help="Only print ortoghraphic, non-word \
                        ($/<errorort..>) corrections",
    )
    parser.add_argument(
        "-ortreal",
        dest="errorortreal",
        action="store_true",
        help="Only print ortoghraphic, real-word \
                        (¢/<errorortreal..>) corrections",
    )
    parser.add_argument(
        "-morphsyn",
        dest="errormorphsyn",
        action="store_true",
        help="Only print morphosyntactic \
                        (£/<errormorphsyn..>) corrections",
    )
    parser.add_argument(
        "-syn",
        dest="errorsyn",
        action="store_true",
        help="Only print syntactic (¥/<errorsyn..>) \
                        corrections",
    )
    parser.add_argument(
        "-lex",
        dest="errorlex",
        action="store_true",
        help="Only print lexical (€/<errorlex..>) \
                        corrections",
    )
    parser.add_argument(
        "-format",
        dest="errorformat",
        action="store_true",
        help="Only print format (‰/<errorformat..>) \
                        corrections",
    )
    parser.add_argument(
        "-foreign",
        dest="errorlang",
        action="store_true",
        help="Only print foreign (∞/<errorlang..>) \
                        corrections",
    )
    parser.add_argument(
        "-noforeign",
        dest="noforeign",
        action="store_true",
        help="Do not print anything from foreign \
                        (∞/<errorlang..>) corrections",
    )
    parser.add_argument(
        "-withforeign",
        dest="withforeign",
        action="store_true",
        help="When printing corrections: include foreign text instead of nothing",
    )
    parser.add_argument(
        "-typos",
        dest="typos",
        action="store_true",
        help="Print only the errors/typos in the text, with \
                        corrections tab-separated",
    )
    parser.add_argument(
        "-f",
        dest="print_filename",
        action="store_true",
        help="Add the source filename as a comment after each \
                        error word.",
    )
    parser.add_argument(
        "-S",
        dest="one_word_per_line",
        action="store_true",
        help="Print the whole text one word per line; \
                        typos have tab separated corrections",
    )
    parser.add_argument(
        "-dis",
        dest="disambiguation",
        action="store_true",
        help="Print the disambiguation element",
    )
    parser.add_argument(
        "-dep",
        dest="dependency",
        action="store_true",
        help="Print the dependency element",
    )
    parser.add_argument(
        "-hyph",
        dest="hyph_replacement",
        default="",
        help="Replace hyph tags with the given argument",
    )
    parser.add_argument(
        "--orthography",
        help=("Print only texts written in the specified orthography."),
        choices=[*orthographies()],
    )
    parser.add_argument(
        "--list-orthographies",
        help=(
            "List all orthographies known. Useful together with -l to limit "
            "the list to only orthographies known for that language. If -l is "
            "not given, all known orthographies are listed."
        ),
        action="store_true",
    )
    parser.add_argument(
        "targets",
        nargs="*",
        help="Name of the files or directories to process. \
                        If a directory is given, all files in this directory \
                        and its subdirectories will be listed.",
    )

    args = parser.parse_args()
    return args


def find_files(targets, extension):
    """Search for files with extension in targets.

    Args:
        targets (list of str): files or directories
        extension (str): interesting files has this extension.

    Yields:
        (str): path to the interesting file
    """
    for target in targets:
        if os.path.exists(target):
            if os.path.isfile(target) and target.endswith(extension):
                yield target
            elif os.path.isdir(target):
                for root, _, files in os.walk(target):
                    for xml_file in files:
                        if xml_file.endswith(extension):
                            yield os.path.join(root, xml_file)
        else:
            print(f"{target} does not exist", file=sys.stderr)


@suppress_broken_pipe_msg
def main():
    """Set up the XMLPrinter class with the given command line options.

    Process the given files and directories
    Print the output to stdout
    """
    args = parse_options()

    if args.list_orthographies:
        for orthography in orthographies(args.lang):
            print(orthography)
        return

    # the targets argument is required when --list-orthographies is not given
    if not args.targets:
        print("ccat: error: the following arguments are required: targets")
        return

    # error if given --orthography is not an orthography of the given lang -l
    if args.orthography is not None and args.lang is not None:
        if not is_orthography_of(args.orthography, args.lang):
            print(
                f"ccat: error: orthography '{args.orthography}' is not an "
                f"orthography of language '{args.lang}'"
            )
            return

    xml_printer = XMLPrinter(
        lang=args.lang,
        all_paragraphs=args.all_paragraphs,
        title=args.title,
        listitem=args.list,
        table=args.table,
        correction=args.corrections,
        error=args.error,
        errorort=args.errorort,
        errorortreal=args.errorortreal,
        errormorphsyn=args.errormorphsyn,
        errorsyn=args.errorsyn,
        errorlex=args.errorlex,
        errorlang=args.errorlang,
        noforeign=args.noforeign,
        withforeign=args.withforeign,
        errorformat=args.errorformat,
        typos=args.typos,
        print_filename=args.print_filename,
        one_word_per_line=args.one_word_per_line,
        dependency=args.dependency,
        disambiguation=args.disambiguation,
        hyph_replacement=args.hyph_replacement,
        orthography=args.orthography,
    )

    did_print = False
    try:
        for filename in find_files(args.targets, ".xml"):
            if xml_printer.print_file(filename):
                did_print = True
    except KeyboardInterrupt:
        print()

    if not did_print and args.orthography is not None and args.lang is None:
        # idea (anders): try to "guess" which language we're in by reading
        # the path to (any of the) target file(s), and looking for "corpus-xxx"
        # -- and if we can guess the language, then we can tell the user that
        # this and this orthography is not a part of the guessed language, so
        # that may be the reason for no output... ?
        print(
            "ccat: notice: no output. it could be that the orthography "
            "requested is not an orthography of that language\n"
            "hint: use -l to specify the language explicitly. if you do, the "
            "script will error out if any of the given --orthography's are "
            "invalid for that language",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()


def ccatter(path: CorpusPath) -> str:
    """Turn an xml formatted file into clean text.

    Args:
        path: The path to the file

    Raises:
        UserWarning: if there is no text, raise a UserWarning

    Returns:
        The content of ccat output
    """
    xml_printer = XMLPrinter(lang=path.lang, all_paragraphs=True)
    xml_printer.parse_file(path.converted)
    text = xml_printer.process_file().getvalue()
    if text:
        return text

    raise UserWarning(f"Empty file {path.converted}")
