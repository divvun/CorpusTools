#
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
#   Copyright © 2026 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Helper functions for converting goldstandard files to .correct.txt files."""

import argparse
import logging

from git import GitCommandError
from lxml import etree

from corpustools import argparse_version, versioncontrol
from corpustools.ccat import make_options, process_file
from corpustools.converter import Converter
from corpustools.convertermanager import collect_files, convert, sanity_check
from corpustools.corpuspath import CorpusPath, make_corpus_path
from corpustools.move_files import mover

LOGGER = logging.getLogger(__name__)


def parse_options():
    """Parse the commandline options.

    Returns:
        (argparse.Namespace): the parsed commandline arguments
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Convert goldstandard go .correct.txt files.",
    )

    parser.add_argument(
        "sources",
        nargs="+",
        help="The original file(s) or \
                        directory/ies where the original files exist",
    )

    args = parser.parse_args()

    return args


def move_orig_to_correct(orig_file: CorpusPath, text: str):
    """Move the original file to a .correct.txt file.

    Args:
        orig_file: The original goldstandard file.
        text: The text to write to the .correct.txt file.
    """
    correct_path = make_corpus_path(
        orig_file.orig.with_suffix(".correct.txt").as_posix()
    )
    mover(
        orig_file,
        correct_path,
    )
    correct_file = orig_file.orig.with_suffix(".correct.txt")
    correct_file.write_text(text, encoding="utf-8")
    metadata = make_corpus_path(correct_file.as_posix()).metadata
    metadata.set_variable("conversion_status", "correct")
    metadata.write_file()


def orig_to_text(orig_file: CorpusPath) -> str:
    """Extract the text from a file.

    Args:
        orig_file: The original goldstandard file.

    Returns:
        The content of the file as a string.
    """
    orig_converter = Converter(orig_file)
    tree = orig_converter.to_giella(orig_file.orig)
    options = make_options(all_paragraphs=True)
    return process_file(options, etree.ElementTree(tree)).getvalue().replace(" ¶", "\n")


def main():
    """Convert goldstandard files to .correct.txt files."""
    args = parse_options()

    sanity_check()

    logging.getLogger().setLevel(logging.INFO)
    gold_files = [
        orig_file
        for orig_file in collect_files(args.sources, goldstandard=True)
        if not orig_file.orig.name.endswith("correct.txt")
    ]
    if gold_files:
        print(f"Found {len(gold_files)} goldstandard files to convert")

    for orig_file in gold_files:
        orig_vcs = versioncontrol.vcs(orig_file.orig_corpus_dir)
        try:
            convert(orig_file)
        except (AttributeError, NameError) as error:
            print(f"Conversion failed for {orig_file.orig}: {error}")
            continue

        if not orig_file.converted.exists():
            print(f"\nCould not convert {orig_file}")
            continue

        text = orig_to_text(orig_file)
        test_text = "".join(line.strip() for line in text.splitlines())

        if not test_text:
            print(
                f"\nFile {orig_file.orig} is empty after conversion, "
                "not writing .correct.txt file"
            )
            continue

        try:
            move_orig_to_correct(orig_file, text)

        except GitCommandError as error:
            if "destination exists" in str(error):
                orig_vcs = versioncontrol.vcs(orig_file.orig_corpus_dir)
                orig_vcs.remove(orig_file.orig)
                orig_vcs.remove(orig_file.xsl)
                if orig_file.converted.exists():
                    conv_vcs = versioncontrol.vcs(orig_file.converted_corpus_dir)
                    conv_vcs.remove(orig_file.converted)
            else:
                raise
