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
#   Copyright © 2017-2023 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Sentence align a given file anew."""


import argparse
import logging
from pathlib import Path

from corpustools import (
    argparse_version,
    convertermanager,
    corpuspath,
    parallelize,
    tmx,
    util,
)

LOGGER = logging.getLogger(__name__)


def print_filename(corpus_path):
    """Print interesting filenames for doing sentence alignment.

    Args:
        corpus_path (corpuspath.make_corpus_path): filenames
    """
    print(
        "\toriginal: {}\n\tmetatada: {}\n\tconverted: {}".format(
            corpus_path.orig, corpus_path.xsl, corpus_path.converted
        )
    )


def print_filenames(corpus_path1, corpus_path2):
    """Print interesting filenames for doing sentence alignment.

    Args:
        corpus_path1 (corpuspath.make_corpus_path): filenames for the lang1 file.
        corpus_path2 (corpuspath.make_corpus_path): filenames for the lang2 file.
    """
    print("\nLanguage 1 filenames:")
    print_filename(corpus_path1)
    print("\nLanguage 2 filenames:")
    print_filename(corpus_path2)


def convert_and_copy(corpus_path1, corpus_path2):
    """Reconvert and copy files to prestable/converted.

    Args:
        corpus_path1 (corpuspath.make_corpus_path): A CorpusPath representing the
            lang1 file that should be reconverted.
        corpus_path2 (corpuspath.make_corpus_path): A CorpusPath representing the
            lang2 file that should be reconverted.
    """
    for corpus_path in [corpus_path1, corpus_path2]:
        corpus_path.converted.unlink(missing_ok=True)

    convertermanager.sanity_check()
    converter_manager = convertermanager.ConverterManager()
    converter_manager.collect_files(
        [corpus_path1.orig.as_posix(), corpus_path2.orig.as_posix()]
    )
    converter_manager.convert_serially()


def parse_options():
    """Parse the commandline options.

    Returns:
        (argparse.Namespace): the parsed commandline arguments
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Sentence align a given file anew.\n"
        "Files are converted before being parallelised.\n"
        "This is mainly thought of as a debugging program "
        "when trying to solve issues in parallelised files.",
    )
    parser.add_argument(
        "--files",
        action="store_true",
        help="Only show the interesting filenames "
        "that are needed for improving sentence "
        "alignment.",
    )
    parser.add_argument(
        "--convert",
        action="store_true",
        help="Only convert the original files "
        "that are the source of the .tmx.html file. "
        "This is useful when improving the content of "
        "the converted files.",
    )
    parser.add_argument("tmxhtml", help="The tmx.html file to realign.")

    args = parser.parse_args()
    return args


def main():
    """Sentence align a given file anew."""
    convertermanager.LOGGER.setLevel(logging.DEBUG)
    args = parse_options()

    tmxhtml = Path(args.tmxhtml).resolve()
    path = tmxhtml.with_suffix("") if tmxhtml.suffix == ".html" else tmxhtml
    source_path = corpuspath.make_corpus_path(path)

    if not source_path.orig.exists():
        raise SystemExit(
            f"\nERROR: You should delete\n«{args.tmxhtml}»\n"
            f"The source of it does not exist."
        )

    lang2 = Path(path.as_posix().split("/tmx/")[1]).parts[0]
    parallel = source_path.parallel(lang2)
    if parallel is None:
        raise SystemExit(f"Could not find parallel file of {source_path.orig}")

    para_path = corpuspath.make_corpus_path(parallel)

    print_filenames(source_path, para_path)

    if args.files:
        raise SystemExit("Only printing file names")

    try:
        convert_and_copy(source_path, para_path)
    except Exception as error:
        raise SystemExit from error

    if args.convert:
        raise SystemExit("Only converting")

    try:
        parallelize.parallelise_file(
            source_path,
            para_path,
            anchor_file=parallelize.get_dictionary(para_path.lang, source_path.lang),
        )
        tmx.tmx2html(source_path.tmx(para_path.lang))
    except util.ArgumentError as error:
        raise SystemExit(
            f"\n{error}\n"
            f"Run «make install» in lang-{source_path.lang} "
            f"and/or lang-{para_path.lang} first."
        ) from error
