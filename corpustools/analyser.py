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
"""Classes and functions to do syntactic analysis on GiellaLT xml docs."""


import argparse
import os
import sys
from functools import lru_cache
from pathlib import Path

from lxml import etree

from corpustools import argparse_version, corpuspath, util
from corpustools.ccat import ccatter
from corpustools.common_arg_ncpus import NCpus
from corpustools.util import lang_resource_dirs, run_external_command


def get_modename(path: corpuspath.CorpusPath) -> str:
    """Get the modename depending on the CorpusPath"""

    o_nine = 1909
    thirtynine = 1939
    ninetyfive = 1995
    if path.lang == "mhr":
        year = path.metadata.get_variable("year")
        if year:
            if o_nine < int(year) < thirtynine:
                return "korp-analyser-thirties"
    if path.lang == "mrj":
        year = path.metadata.get_variable("year")
        if year:
            if o_nine < int(year) < thirtynine:
                return "korp-analyser-thirties"
            if thirtynine < int(year) < ninetyfive:
                return "korp-analyser-eighties"

    return "korp-analyser"


def dependency_analysis(path: corpuspath.CorpusPath, analysed_text: str) -> None:
    """Insert dependency analysis into the body."""
    xml_file = etree.parse(path.converted)
    oldbody = xml_file.find(".//body")

    if oldbody is None:
        raise UserWarning(f"No body found in {path.converted}")

    parent = oldbody.getparent()

    if parent is None:
        raise UserWarning(f"No parent found for body in { path.converted}")

    parent.remove(oldbody)

    body = etree.SubElement(parent, "body")
    dependency = etree.SubElement(body, "dependency")
    dependency.text = etree.CDATA(analysed_text)

    with util.ignored(OSError):
        os.makedirs(os.path.dirname(path.analysed))
    with open(path.analysed, "wb") as analysed_stream:
        analysed_stream.write(
            etree.tostring(
                xml_file, xml_declaration=True, encoding="utf8", pretty_print=True
            )
        )


LANGUAGES = {
    "eng": "en",
    "fin": "fi",
    "sme": "se",
    "swe": "sv",
    "nob": "nb",
    "nno": "nn",
}


@lru_cache(maxsize=None)
def valid_path(lang: str) -> Path:
    """Check if resources needed by modes exists.

    Args:
        lang: the language that modes is asked to serve.

    Returns:
        A path to the zpipe file.

    Raises:
        utils.ArgumentError: if no resources are found.
    """
    archive_name = f"{LANGUAGES.get(lang, lang)}.zpipe"
    for lang_dir in lang_resource_dirs(lang):
        full_path = lang_dir / archive_name
        if full_path.exists():
            return full_path

    raise (util.ArgumentError(f"ERROR: found no resources for {lang}"))


def analyse(xml_path: corpuspath.CorpusPath) -> None:
    """Analyse a file."""
    zpipe_path = valid_path(xml_path.lang)
    variant_name = get_modename(xml_path)

    try:
        dependency_analysis(
            xml_path,
            analysed_text=run_external_command(
                command=f"divvun-checker -a {zpipe_path} -n {variant_name}".split(),
                instring=ccatter(xml_path),
            ),
        )
    except (etree.XMLSyntaxError, UserWarning) as error:
        print("Can not parse", xml_path, file=sys.stderr)
        print("The error was:", str(error), file=sys.stderr)


def analyse_in_parallel(file_list: list[corpuspath.CorpusPath], pool_size: int):
    """Analyse file in parallel."""
    print(f"Parallel analysis of {len(file_list)} files with {pool_size} workers")
    # Here we know that we are looking at the .converted file,
    file_list = [(file, os.path.getsize(file.converted)) for file in file_list]

    # sort the file list by size, smallest first
    file_list.sort(key=lambda entry: entry[1])

    # and turn the list of 2-tuples [[a, b, c, d], [1, 2, 3, 4]] back to
    # two lists: [a, b, c, d] and [1, 2, 3, 4]
    file_list, file_sizes = zip(*file_list)

    util.run_in_parallel(
        function=analyse,
        max_workers=pool_size,
        file_list=file_list,
        file_sizes=file_sizes,
    )


def analyse_serially(file_list: list[corpuspath.CorpusPath]):
    """Analyse files one by one."""
    print(f"Starting the analysis of {len(file_list)} files")

    fileno = 0
    for xml_file in file_list:
        fileno += 1
        # print some ugly banner cos i want to see progress on local
        # batch job
        util.print_frame("*" * 79)
        util.print_frame(f"Analysing {xml_file} [{fileno} of {len(file_list)}]")
        util.print_frame("*" * 79)
        analyse(xml_file)


def parse_options():
    """Parse the given options."""
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser], description="Analyse files in parallel."
    )

    parser.add_argument("--ncpus", action=NCpus)
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip analysis of files that already are analysed (== already "
        "exist in the analysed/ folder)",
    )
    parser.add_argument(
        "--serial",
        action="store_true",
        help="When this argument is used files will be analysed one by one. "
        "Using --serial takes priority over --ncpus",
    )
    parser.add_argument(
        "converted_entities",
        nargs="+",
        help="converted files or director(y|ies) where the converted files exist",
    )

    return parser.parse_args()


def main():
    """Analyse files in the given directories."""
    args = parse_options()

    corpuspath_paths = (
        corpuspath.make_corpus_path(xml_file.as_posix())
        for xml_file in corpuspath.collect_files(args.converted_entities, suffix=".xml")
    )
    analysable_paths = [
        path for path in corpuspath_paths if not path.metadata.get_variable("ocr")
    ]

    if args.skip_existing:
        non_skipped_files = [
            analysable_path
            for analysable_path in analysable_paths
            if not analysable_path.analysed.exists()
        ]
        n_skipped_files = len(analysable_paths) - len(non_skipped_files)
        print(
            f"--skip-existing given. Skipping {n_skipped_files} "
            "files that are already analysed"
        )
        if n_skipped_files == len(analysable_paths):
            print("nothing to do, exiting")
            raise SystemExit(0)
        analysable_paths = non_skipped_files

    try:
        if args.serial:
            analyse_serially(analysable_paths)
        else:
            analyse_in_parallel(analysable_paths, args.ncpus)
    except util.ArgumentError as error:
        print(f"Cannot do analysis\n{str(error)}", file=sys.stderr)
        raise SystemExit(1) from error
