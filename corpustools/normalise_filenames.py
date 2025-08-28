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
#   Copyright © 2015-2023 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Normalise the files in the given directory."""

import argparse
from pathlib import Path

from corpustools import argparse_version
from corpustools.corpuspath import make_corpus_path
from corpustools.namechanger import normalise_filename


def normalise(target_dir: Path):
    """Normalise the filenames in the corpuses.

    Args:
        target_dir (str): directory where filenames should be normalised
    """
    print(f"Normalising names in {target_dir}")
    files = (
        root / file_
        for root, _, filenames in target_dir.walk()
        for file_ in filenames
        if ".git" not in str(root) and not file_.endswith(".xsl")
    )

    normalised_paths = (
        (
            make_corpus_path(str(file_.with_name(normalise_filename(file_.name)))),
            make_corpus_path(str(file_)),
        )
        for file_ in files
        if normalise_filename(file_.name) != file_.name
    )

    for normalised_path, orig_corpus_path in normalised_paths:
        print(f"\t\tmove {orig_corpus_path.orig} -> {normalised_path.orig}")
        orig_corpus_path.orig.rename(normalised_path.orig)
        if orig_corpus_path.xsl.exists():
            orig_corpus_path.xsl.rename(normalised_path.xsl)
        if orig_corpus_path.converted.exists():
            orig_corpus_path.converted.rename(normalised_path.converted)

        for parallel_path in orig_corpus_path.parallels():
            if parallel_path is not None and parallel_path.exists():
                parallel_corpuspath = make_corpus_path(str(parallel_path))
                parallel_corpuspath.metadata.set_parallel_text(
                    normalised_path.lang, normalised_path.orig.name
                )
                parallel_corpuspath.metadata.write_file()

                if orig_corpus_path.tmx(parallel_corpuspath.lang).exists():
                    orig_corpus_path.tmx(parallel_corpuspath.lang).rename(
                        normalised_path.tmx(parallel_corpuspath.lang)
                    )


def normalise_parse_args():
    """Parse the commandline options.

    Returns:
        (argparse.Namespace): the parsed commandline arguments
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Program to normalise names in given directories. "
        "The filenames are downcased, non ascii characters are replaced "
        "by ascii ones and some unwanted characters are removed.",
    )
    parser.add_argument(
        "target_dirs",
        nargs="+",
        help="The directory/ies where filenames should be normalised.",
    )

    args = parser.parse_args()

    return args


def main():
    """Normalise filenames."""
    for target_dir in normalise_parse_args().target_dirs:
        normalise(Path(target_dir))
