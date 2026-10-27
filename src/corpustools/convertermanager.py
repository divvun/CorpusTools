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
"""This file manages conversion of files to the Giella xml format."""

import argparse
import logging
import os
from concurrent.futures import Future, ProcessPoolExecutor, as_completed
from functools import cache
from pathlib import Path
from typing import Iterator

from corpustools import argparse_version, converter, text_cat, util
from corpustools.common_arg_ncpus import NCpus
from corpustools.corpuspath import CorpusPath, make_corpus_path

LOGGER = logging.getLogger(__name__)


@cache
def languageguesser() -> text_cat.Classifier:
    """Return the language guesser.

    It takes a while to initialise, so it is created on first use,
    once per process.
    """
    return text_cat.Classifier(None)


def convert(orig_file: CorpusPath, lazy_conversion: bool = False) -> None:
    """Convert file to corpus xml format.

    Args:
        orig_file: the path to the original file.
        lazy_conversion: only convert if metadata have changed since last
            conversion.
    """
    try:
        conv = converter.Converter(orig_file, lazy_conversion=lazy_conversion)
        conv.write_complete(languageguesser())
    except (
        util.ConversionError,
        ValueError,
        IndexError,
    ) as error:
        LOGGER.warning("Could not convert %s\n%s", orig_file.orig, error)
        raise


def convert_in_parallel(
    files: list[CorpusPath], pool_size: int, lazy_conversion: bool = False
) -> None:
    """Convert files using a pool of worker processes."""
    nfiles = len(files)
    futures: dict[Future[None], CorpusPath] = {}  # Future -> filename
    print(f"Starting parallel conversion with {pool_size} workers")
    failed: list[CorpusPath] = []
    with ProcessPoolExecutor(max_workers=pool_size) as pool:
        for file in files:
            fut = pool.submit(convert, file, lazy_conversion)
            futures[fut] = file

        for i, future in enumerate(as_completed(futures), start=1):
            exc = future.exception()
            filename = futures[future]
            if exc is not None:
                failed.append(filename)
                print(f"[{i}/{nfiles} FAILED: {filename.orig}")
                print(exc)
            else:
                print(f"[{i}/{nfiles}] done: {filename.converted}")

    n_ok = nfiles - len(failed)
    print(f"all done converting. {n_ok} files converted ok, {len(failed)} failed")
    if failed:
        print("the files that failed to convert are:")
        for filename in failed:
            print(filename.orig)


def convert_serially(files: list[CorpusPath], lazy_conversion: bool = False) -> None:
    """Convert the files in one process."""
    LOGGER.info("Starting the conversion of %d files", len(files))

    for orig_file in files:
        LOGGER.debug("converting %s", orig_file.orig)
        try:
            convert(orig_file, lazy_conversion)
        except util.ConversionError as error:
            LOGGER.warning("Could not convert %s\n%s", orig_file.orig, error)


def corpus_paths(sources: list[str]) -> Iterator[CorpusPath]:
    """Yield all convertible files in sources.

    Args:
        sources (list of str): a list of files or directories where
            convertable files are found.
    Yields:
        Convertible files found in sources.
    """
    LOGGER.info("Collecting files to convert")

    paths = (Path(source) for source in sources)
    for path in paths:
        if path.is_file():
            yield make_corpus_path(path.as_posix())
        elif path.is_dir():
            for xsl_file in path.rglob("*.xsl"):
                yield make_corpus_path(xsl_file.as_posix())
        else:
            LOGGER.error(
                "Can not process %s\nThis is neither a file nor a directory.",
                path,
            )


def collect_files(sources: list[str], goldstandard: bool = False) -> list[CorpusPath]:
    """Find all convertible files in sources.

    Args:
        sources (list of str): a list of files or directories where
            convertable files are found.
        goldstandard: also include goldstandard documents.
    """
    LOGGER.info("Collecting files to convert")

    return [
        c_path
        for c_path in corpus_paths(sources)
        if c_path.is_convertable(goldstandard)
    ]


def parse_options():
    """Parse the commandline options.

    Returns:
        (argparse.Namespace): the parsed commandline arguments
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Convert original files to giellatekno xml.",
    )

    parser.add_argument("--ncpus", action=NCpus)
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="skip converting files that are already converted (that already "
        "exist in the converted/ folder",
    )
    parser.add_argument(
        "--serial",
        action="store_true",
        help="use this for debugging the conversion \
                        process. When this argument is used files will \
                        be converted one by one.",
    )
    parser.add_argument(
        "--lazy-conversion",
        action="store_true",
        help="Reconvert only if metadata have changed.",
    )
    parser.add_argument(
        "--goldstandard",
        action="store_true",
        help="Convert goldstandard and .correct files",
    )
    parser.add_argument(
        "sources",
        nargs="+",
        help="The original file(s) or \
                        directory/ies where the original files exist",
    )

    args = parser.parse_args()

    return args


def sanity_check():
    """Check that needed programs and environment variables are set."""
    util.sanity_check(["pdftotext", "latex2html", "pandoc"])
    if not os.path.isfile(converter.Converter.get_dtd_location()):
        raise util.SetupError(
            "Couldn't find {}\n"
            "Check that GTHOME points at the right directory "
            "(currently: {}).".format(
                converter.Converter.get_dtd_location(), os.environ["GTHOME"]
            )
        )


def main():
    """Convert documents to giellatekno xml format."""
    LOGGER.setLevel(logging.WARNING)
    try:
        sanity_check()
    except (util.SetupError, util.ExecutableMissingError) as error:
        raise SystemExit(str(error)) from error

    args = parse_options()

    files = collect_files(args.sources, args.goldstandard)

    try:
        if args.serial:
            LOGGER.setLevel(logging.DEBUG)
            convert_serially(files, args.lazy_conversion)
        else:
            convert_in_parallel(files, args.ncpus, args.lazy_conversion)
    except util.ExecutableMissingError as error:
        raise SystemExit(str(error)) from error
