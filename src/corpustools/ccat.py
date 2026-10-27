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
from dataclasses import dataclass, replace
from io import StringIO
from pathlib import Path
from typing import Iterable

from lxml import etree

from corpustools import argparse_version
from corpustools.corpuspath import CorpusPath
from corpustools.orthographies import is_orthography_of, orthographies


@dataclass(frozen=True)
class PrintOptions:
    """The settings that govern how giellatekno xml is turned into text.

    Create it with make_options, which computes the derived fields.
    """

    lang: str | None
    invert_lang: bool
    all_paragraphs: bool
    paragraph: bool
    title: bool
    listitem: bool
    table: bool
    correction: bool
    error: bool
    errorort: bool
    errorortreal: bool
    errormorphsyn: bool
    errorsyn: bool
    errorlex: bool
    errorlang: bool
    noforeign: bool
    foreign: bool
    errorformat: bool
    error_filtering: bool
    typos: bool
    print_filename: bool
    one_word_per_line: bool
    disambiguation: bool
    dependency: bool
    hyph_replacement: str
    orthography: str | None
    filename: str = ""


def make_options(  # noqa: PLR0913
    lang: str | None = None,
    all_paragraphs: bool = False,
    title: bool = False,
    listitem: bool = False,
    table: bool = False,
    correction: bool = False,
    error: bool = False,
    errorort: bool = False,
    errorortreal: bool = False,
    errormorphsyn: bool = False,
    errorsyn: bool = False,
    errorlex: bool = False,
    errorlang: bool = False,
    foreign: bool = False,
    errorformat: bool = False,
    noforeign: bool = False,
    withforeign: bool = False,
    typos: bool = False,
    print_filename: bool = False,
    one_word_per_line: bool = False,
    disambiguation: bool = False,
    dependency: bool = False,
    hyph_replacement: str = "",
    orthography: str | None = None,
) -> PrintOptions:
    """Set up all the options.

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
    error_filtering = (
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
        correction = False
        error = True
        errorort = True
        errorortreal = True
        errormorphsyn = True
        errorsyn = True
        errorlex = True
        errorformat = True
        errorlang = False
        noforeign = False
        error_filtering = True

    invert_lang = bool(lang and lang.startswith("!"))
    if lang and invert_lang:
        lang = lang[1:]

    return PrintOptions(
        lang=lang,
        invert_lang=invert_lang,
        all_paragraphs=all_paragraphs,
        paragraph=not (title or listitem or table),
        title=title,
        listitem=listitem,
        table=table,
        correction=correction,
        error=error,
        errorort=errorort,
        errorortreal=errorortreal,
        errormorphsyn=errormorphsyn,
        errorsyn=errorsyn,
        errorlex=errorlex,
        errorlang=errorlang,
        noforeign=noforeign,
        foreign=foreign,
        errorformat=errorformat,
        error_filtering=error_filtering,
        typos=typos,
        print_filename=print_filename,
        one_word_per_line=typos or one_word_per_line,
        disambiguation=disambiguation,
        dependency=dependency,
        hyph_replacement="<hyph/>" if hyph_replacement == "xml" else hyph_replacement,
        orthography=orthography,
    )


def get_lang(tree: etree.ElementTree) -> str:
    """Get the lang of the file."""
    return tree.getroot().attrib["{http://www.w3.org/XML/1998/namespace}lang"]


def get_element_language(element: etree.Element, parentlang: str | None) -> str | None:
    """Get the language of element.

    Elements inherit the parents language if not explicitely set
    """
    if element.get("{http://www.w3.org/XML/1998/namespace}lang") is None:
        return parentlang

    return element.get("{http://www.w3.org/XML/1998/namespace}lang")


def collect_not_inline_errors(
    options: PrintOptions, element: etree.Element, textlist: list[str]
) -> None:
    """Add the formatted errors as strings to the textlist list."""
    error_string = error_not_inline(options, element)
    if error_string != "":
        textlist.append(error_string)

    for child in element:
        if visit_error_not_inline(options, child):
            collect_not_inline_errors(options, child, textlist)

    if not options.typos:
        if element.tail is not None and element.tail.strip() != "":
            if not options.one_word_per_line:
                textlist.append(element.tail)
            else:
                textlist.extend(element.tail.strip().split())


def corrected_texts(error_element: etree.Element) -> Iterable[str]:
    """Yield corrected versions of the error element."""
    for correct in error_element.xpath("./correct"):
        correct_text = "" if correct.text is None else correct.text
        tail_text = "" if error_element.tail is None else error_element.tail
        yield f"{correct_text}{tail_text}"


def error_not_inline(options: PrintOptions, element: etree.Element) -> str:
    """Collect and format parts of the element.

    Also scan the children if there is no error filtering or
    if the element is filtered
    """
    text: list[str] = []
    if element.text is not None and element.text.strip() != "":
        text.append(element.text)

    if not options.error_filtering or include_this_error(options, element):
        for child in element:
            if child.tag != "correct":
                text.extend(corrected for corrected in corrected_texts(child))

    return "\n".join(
        f"{''.join(text)}{get_error_attributes(options, correct)}"
        for correct in element.xpath("./correct")
    )


def get_error_attributes(options: PrintOptions, correct_element: etree.Element) -> str:
    """Collect and format the attributes + the filename."""
    text = ["\t"]
    text.append("" if correct_element.text is None else correct_element.text)

    attributes = correct_element.attrib
    attr = [key + "=" + str(attributes[key]) for key in sorted(attributes)]

    if attr:
        text.append("\t#")
        text.append(",".join(attr))

        if options.print_filename:
            text.append(f", file: {os.path.basename(options.filename)}")

    elif options.print_filename:
        text.append(f"\t#file: {os.path.basename(options.filename)}")

    return "".join(text)


def collect_inline_errors(
    options: PrintOptions,
    element: etree.Element,
    textlist: list[str],
    parentlang: str | None,
) -> None:
    """Add the "correct" element to the list textlist."""
    correct = element.find("./correct")
    if correct is not None and not options.noforeign:
        textlist.append("" if correct.text is None else correct.text)

    get_contents(options, element.tail, textlist, parentlang)


def collect_text(
    options: PrintOptions, element: etree.Element, parentlang: str, buffer: StringIO
) -> None:
    """Collect text from element, and write the contents to buffer."""
    textlist: list[str] = []

    visit_nonerror_element(options, element, textlist, parentlang)

    if textlist:
        if not options.one_word_per_line:
            textlist[-1] = textlist[-1].rstrip()
            buffer.write("".join(textlist))
            buffer.write(" ¶\n")
        else:
            buffer.write("\n".join(textlist))
            buffer.write("\n")


def is_correct_lang(options: PrintOptions, elt_lang: str | None) -> bool:
    """Check if elt_lang is a wanted language."""
    return (
        options.lang is None
        or (not options.invert_lang and elt_lang == options.lang)
        or (options.invert_lang and elt_lang != options.lang)
    )


def get_contents(
    options: PrintOptions,
    elt_contents: str | None,
    textlist: list[str],
    elt_lang: str | None,
) -> None:
    """Get the contents of a xml document."""
    if elt_contents is not None:
        text = elt_contents
        if is_correct_lang(options, elt_lang):
            if not options.one_word_per_line:
                textlist.append(text)
            else:
                textlist.extend(text.split())


def visit_children(
    options: PrintOptions,
    element: etree.Element,
    textlist: list[str],
    parentlang: str | None,
) -> None:
    """Visit the children of element, adding their content to textlist."""
    for child in element:
        if child.tag != "correct":
            if child.tag == "errorlang" and options.noforeign and options.typos:
                pass
            elif child.tag == "errorlang" and options.noforeign:
                get_contents(options, child.tail, textlist, parentlang)
            elif visit_error_inline(options, child):
                collect_inline_errors(
                    options, child, textlist, get_element_language(child, parentlang)
                )
            elif visit_error_not_inline(options, child):
                collect_not_inline_errors(options, child, textlist)
            else:
                visit_nonerror_element(options, child, textlist, parentlang)
        elif not (isinstance(element.tag, str) and element.tag.startswith("error")):
            visit_nonerror_element(
                options, child, textlist, get_element_language(element, parentlang)
            )


def visit_nonerror_element(
    options: PrintOptions,
    element: etree.Element,
    textlist: list[str],
    parentlang: str | None,
) -> None:
    """Visit and extract text from non error element."""
    if not options.typos:
        get_contents(
            options, element.text, textlist, get_element_language(element, parentlang)
        )
    visit_children(options, element, textlist, parentlang)
    if not options.typos:
        get_contents(options, element.tail, textlist, parentlang)


def visit_this_node(options: PrintOptions, element: etree.Element) -> bool:
    """Return True if the element should be visited."""
    return (
        options.all_paragraphs
        or (
            options.paragraph is True
            and (element.get("type") is None or element.get("type") == "text")
        )
        or (options.title is True and element.get("type") == "title")
        or (options.listitem is True and element.get("type") == "listitem")
        or (options.table is True and element.get("type") == "tablecell")
    )


def visit_error_not_inline(options: PrintOptions, element: etree.Element) -> bool:
    """Determine whether element should be visited."""
    return (
        isinstance(element.tag, str)
        and element.tag.startswith("error")
        and options.one_word_per_line
        and not options.error_filtering
        or include_this_error(options, element)
    )


def visit_error_inline(options: PrintOptions, element: etree.Element) -> bool:
    """Determine whether element should be visited."""
    return (
        isinstance(element.tag, str)
        and element.tag.startswith("error")
        and not options.one_word_per_line
        and (options.correction or include_this_error(options, element))
    )


def include_this_error(options: PrintOptions, element: etree.Element) -> bool:
    """Determine whether element should be visited."""
    return options.error_filtering and (
        (element.tag == "error" and options.error)
        or (element.tag == "errorort" and options.errorort)
        or (element.tag == "errorortreal" and options.errorortreal)
        or (element.tag == "errormorphsyn" and options.errormorphsyn)
        or (element.tag == "errorsyn" and options.errorsyn)
        or (element.tag == "errorlex" and options.errorlex)
        or (element.tag == "errorformat" and options.errorformat)
        or (element.tag == "errorlang" and options.errorlang)
        or (element.tag == "errorlang" and options.noforeign)
    )


def parse_file(filename: Path) -> etree.ElementTree:
    """Parse the xml document."""
    return etree.parse(filename, etree.XMLParser(huge_tree=True))


def process_file(options: PrintOptions, tree: etree.ElementTree) -> StringIO:
    """Process the given xml tree, adding the text into a buffer.

    The tree is modified, the hyph elements are replaced.

    Returns the buffer
    """
    buffer = StringIO()

    handle_hyph(options, tree)
    if options.dependency and (dependency := tree.find(".//dependency")) is not None:
        print_element(dependency, buffer)
    elif (
        options.disambiguation
        and (disambiguation := tree.find(".//disambiguation")) is not None
    ):
        print_element(disambiguation, buffer)
    else:
        for paragraph in tree.findall(".//p"):
            if is_correct_lang(
                options, get_element_language(paragraph, get_lang(tree))
            ) and visit_this_node(options, paragraph):
                collect_text(options, paragraph, get_lang(tree), buffer)

    return buffer


def handle_hyph(options: PrintOptions, tree: etree.ElementTree) -> None:
    """Replace hyph tags."""
    hyph_tails: list[str] = []
    for hyph in tree.findall(".//hyph"):
        if hyph.tail is not None:
            hyph_tails.append(hyph.tail)

        hyph_parent = hyph.getparent()

        if hyph_parent is not None:
            if hyph.getnext() is None:
                if hyph_parent.text is not None:
                    hyph_tails.insert(0, hyph_parent.text)
                hyph_parent.text = options.hyph_replacement.join(hyph_tails)
                hyph_tails[:] = []

            hyph_parent.remove(hyph)


def print_element(element: etree.Element, buffer: StringIO) -> None:
    """Write the text of the element to the buffer."""
    if element.text is not None:
        buffer.write(element.text)


def print_file(options: PrintOptions, filename: Path) -> bool:
    """Print a xml file to stdout. Returns True if something was printed,
    False otherwise."""
    tree = parse_file(filename)
    text_orthography = tree.find(".//header/orthography")
    wanted_orthography = options.orthography

    if text_orthography is None or not text_orthography.text:
        # text has standard orthography, show text if no --orthography
        # was given
        show_text = wanted_orthography is None
    else:
        # text has specific orthoraphy! show only if wanted orthoraphy
        # is same as this text has!
        show_text = text_orthography.text == wanted_orthography

    if show_text:
        sys.stdout.write(
            process_file(replace(options, filename=filename.name), tree).getvalue()
        )
        return True

    return False


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


def find_files(targets: list[str], extension: str) -> Iterable[Path]:
    """Search for files with extension in targets.

    Args:
        targets (list of str): files or directories
        extension (str): interesting files has this extension.

    Yields:
        (Path): path to the interesting file, in sorted order within a directory
    """
    for target in targets:
        target_path = Path(target)
        if target_path.is_file():
            if target.endswith(extension):
                yield target_path
        elif target_path.is_dir():
            for root, dirs, files in os.walk(target_path):
                dirs.sort()
                for xml_file in sorted(files):
                    if xml_file.endswith(extension):
                        yield Path(root) / xml_file
        else:
            print(f"{target} does not exist", file=sys.stderr)


def _main() -> None:
    """Set up the print options from the command line options.

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
        print(
            "ccat: error: the following arguments are required: targets",
            file=sys.stderr,
        )
        sys.exit(2)

    # error if given --orthography is not an orthography of the given lang -l
    if args.orthography is not None and args.lang is not None:
        if not is_orthography_of(args.orthography, args.lang):
            print(
                f"ccat: error: orthography '{args.orthography}' is not an "
                f"orthography of language '{args.lang}'",
                file=sys.stderr,
            )
            sys.exit(2)

    options = make_options(
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
            if print_file(options, filename):
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


def main() -> int:
    try:
        _main()
    except SystemExit:
        try:
            sys.stdout.flush()
        except BrokenPipeError:
            return _handle_broken_pipe()
        raise
    except BrokenPipeError:
        return _handle_broken_pipe()

    try:
        sys.stdout.flush()
    except BrokenPipeError:
        return _handle_broken_pipe()

    return 0


def _handle_broken_pipe() -> int:
    devnull = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(devnull, sys.stdout.fileno())
    finally:
        os.close(devnull)
    return 1


def ccatter(path: CorpusPath) -> str:
    """Turn an xml formatted file into clean text.

    Args:
        path: The path to the file

    Raises:
        UserWarning: if there is no text, raise a UserWarning

    Returns:
        The content of ccat output
    """
    options = make_options(lang=path.lang, all_paragraphs=True)
    text = process_file(
        replace(options, filename=str(path.converted)), parse_file(path.converted)
    ).getvalue()
    if text:
        return text

    raise UserWarning(f"Empty file {path.converted}")


if __name__ == "__main__":
    sys.exit(main())
