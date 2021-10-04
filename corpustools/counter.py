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
#   Copyright © 2012-2020 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""This file contains classes to convert files to the giellatekno xml format."""


import argparse
import logging
import os
from collections import defaultdict
from datetime import date

from corpustools import argparse_version, converter, convertermanager, util

logging.basicConfig(level=logging.CRITICAL)


def parse_options():
    """Parse the commandline options.

    Returns:
        a list of arguments as parsed by argparse.Argumentparser.
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Count corpus files. List them if called for.",
    )

    parser.add_argument(
        "--listfiles",
        action="store_true",
        help="List lacking converted and analysed files.",
    )

    args = parser.parse_args()

    return args


def count_files(path):
    """Count files in the given language."""
    today = date.today()

    cm = convertermanager.ConverterManager(False, False)
    cm.collect_files([path])
    counter = defaultdict(int)
    lacking_files = defaultdict(set)
    for f in cm.files:
        c = converter.Converter(f)
        if os.path.exists(c.names.converted):
            counter["con"] += 1
        else:
            lacking_files["con"].add(c.names.orig)

        for fst in ["xfst", "hfst"]:
            todays_analysed = f"/analysed.{today}/{fst}/"
            if os.path.exists(c.names.analysed.replace("/analysed/", todays_analysed)):
                counter[fst] += 1
        else:
            if os.path.exists(c.names.converted):
                lacking_files["ana"].add(c.names.converted)
    return (
        len(cm.files),
        counter["con"],
        counter["xfst"],
        counter["hfst"],
        lacking_files,
    )


def main():

    args = parse_options()

    lacking_files = defaultdict(set)
    print("\t".join(["language", "original", "converted", "xfst", "hfst"]))
    for corpus in [os.getenv("GTFREE"), os.getenv("GTBOUND")]:
        print(corpus)
        for language in ["fkv", "sma", "sme", "smj", "smn", "sms"]:
            result = count_files(os.path.join(corpus, "orig", language))
            print(
                "{}\t{}\t{}\t{}\t{}".format(
                    language, result[0], result[1], result[2], result[3]
                )
            )
            for key, value in result[-1].items():
                lacking_files[key].update(value)

    if args.listfiles:
        for key, value in lacking_files.items():
            print(key)
            for f in value:
                print("\t", f)
        print()
