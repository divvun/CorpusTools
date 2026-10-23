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
"""Check the consistency of the parallel entries in the metadata files."""


import argparse
import os

from corpustools import argparse_version, corpuspath


def parse_args():
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Check the if the files in the parallel_text entries "
        "found in the metadata files exist",
    )

    parser.add_argument(
        "orig_dir", help="The directory where the original corpus " "files are"
    )

    return parser.parse_args()


def get_files(orig_dir):
    return [
        os.path.join(root, f)
        for root, _, files in os.walk(orig_dir)
        if ".git" not in root
        for f in files
        if not f.endswith(".xsl")
    ]


def main():
    total = 0
    para_fail = 0
    no_orig_xsl = 0
    args = parse_args()

    for orig in get_files(args.orig_dir):
        total += 1
        try:
            orig_path = corpuspath.make_corpus_path(orig)
        except ValueError as error:
            no_orig_xsl += 1
            print("***")
            print(error)
            print("***")
        else:
            xsl_path = orig_path.xsl
            if xsl_path.exists():
                nonexisting_parallels = [
                    parallel.as_posix()
                    for parallel in orig_path.parallels()
                    if not parallel.exists()
                ]

                if nonexisting_parallels:
                    para_fail += len(nonexisting_parallels)
                    print(f"{orig_path.xsl} points to non-existing file")
                    print("\n".join({f"\t{p}" for p in nonexisting_parallels}))
                    print()
            else:
                no_orig_xsl += 1

    print(f"Total {total}, fails {para_fail}, {no_orig_xsl} files with no xsl")
