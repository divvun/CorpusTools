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
"""Move a corpus file from oldpath to newpath."""


import argparse
import os
import sys

from corpustools import argparse_version, namechanger


def mover(oldpath, newpath):
    """Move a file from oldpath to newpath."""
    if os.path.isfile(oldpath):
        if oldpath.endswith(".xsl"):
            oldpath = oldpath[:-4]
    else:
        raise UserWarning(f"{oldpath} is not a file")

    if newpath.endswith(".xsl"):
        newpath = newpath[:-4]
    elif os.path.isdir(newpath):
        newpath = os.path.join(newpath, os.path.basename(oldpath))

    cfmu = namechanger.CorpusFilesetMoverAndUpdater(oldpath, newpath)
    filepair = cfmu.move_computer.filepairs[0]
    if filepair.newpath:
        print(f"\tmoving {filepair.oldpath} -> {filepair.newpath}")
    else:
        print(f"\tremoving {filepair.oldpath}")
    cfmu.move_files()
    cfmu.update_own_metadata()
    cfmu.update_parallel_files_metadata()


def mover_parse_args():
    """Parse the commandline options.

    Returns:
        a list of arguments as parsed by argparse.Argumentparser.
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Program to move or rename a file inside the corpus.",
    )

    parser.add_argument("oldpath", help="The path of the old file.")
    parser.add_argument(
        "newpath",
        help="The place to move the file to. newpath can "
        "be either a filename or a directory",
    )

    return parser.parse_args()


def main():
    """Move a file."""
    args = mover_parse_args()
    if args.oldpath == args.newpath:
        print(
            f"{args.oldpath} and {args.newpath} are the same file",
            file=sys.stderr,
        )
    else:
        oldpath = args.oldpath
        newpath = args.newpath
        try:
            mover(os.path.abspath(oldpath), os.path.abspath(newpath))
        except UserWarning as e:
            print("Can not move file:", str(e), file=sys.stderr)


def remover_parse_args():
    """Parse the commandline options.

    Returns:
        a list of arguments as parsed by argparse.Argumentparser.
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Program to remove a file from the corpus.",
    )

    parser.add_argument("oldpath", help="The path of the old file.")

    return parser.parse_args()


def remove_main():
    """Remove a file."""
    args = remover_parse_args()
    try:
        mover(os.path.abspath(args.oldpath), "")
    except UserWarning as e:
        print("Can not remove file:", str(e), file=sys.stderr)
