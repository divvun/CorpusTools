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

from corpustools import argparse_version, versioncontrol
from corpustools.ccat import XMLPrinter
from corpustools.convertermanager import ConverterManager, sanity_check
from corpustools.corpuspath import make_corpus_path
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


def main():
    """Convert goldstandard files to .correct.txt files."""
    args = parse_options()

    sanity_check()

    logging.getLogger().setLevel(logging.INFO)
    converter_manager = ConverterManager(
        goldstandard=True,
    )

    converter_manager.collect_files(args.sources)
    gold_files = [
        orig_file
        for orig_file in converter_manager.files
        if not orig_file.orig.name.endswith("correct.txt")
    ]
    if gold_files:
        print(f"Found {len(gold_files)} goldstandard files to convert")

    for orig_file in gold_files:
        try:
            metadata = orig_file.metadata
            metadata.set_variable("monolingual", "1")  # turn off language detection
            metadata.write_file()
            converter_manager.convert(orig_file)
        except (AttributeError, NameError) as error:
            print(f"Conversion failed for {orig_file.orig}: {error}")
            continue

        if not orig_file.converted.exists():
            print(f"\nCould not convert {orig_file}")
            continue

        xml_printer = XMLPrinter(lang=orig_file.lang, all_paragraphs=True)
        xml_printer.parse_file(orig_file.converted.absolute().as_posix())
        text = xml_printer.process_file().getvalue().replace(" ¶", "\n")

        test_text = "".join(line.strip() for line in text.splitlines())
        if not test_text:
            print(
                f"\nFile {orig_file.orig} is empty after conversion, "
                "not writing .correct.txt file"
            )
            continue

        try:
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

        except GitCommandError as error:
            if "destination exists" in str(error):
                orig_vcs = versioncontrol.vcs(orig_file.orig_corpus_dir)
                orig_vcs.remove(orig_file.orig)
                orig_vcs.remove(orig_file.xsl)
            else:
                raise
