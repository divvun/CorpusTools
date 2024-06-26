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
import os

from corpustools import argparse_version, namechanger


def normalise(target_dir):
    """Normalise the filenames in the corpuses.

    Args:
        target_dir (str): directory where filenames should be normalised
    """
    print(f"Normalising names in {target_dir}")
    for root, dirs, files in os.walk(os.path.join(target_dir)):
        for f in files:
            if not f.endswith(".xsl"):
                try:
                    orig_path = os.path.join(root, f)

                    cfmu = namechanger.CorpusFilesetMoverAndUpdater(
                        orig_path, orig_path
                    )
                    filepair = cfmu.move_computer.filepairs[0]
                    print(f"\t\tmove {filepair.oldpath} -> {filepair.newpath}")
                    cfmu.move_files()
                    cfmu.update_own_metadata()
                    cfmu.update_parallel_files_metadata()
                except UserWarning:
                    pass


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
        normalise(target_dir)
