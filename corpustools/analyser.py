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
#   Copyright © 2013-2023 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Classes and functions to do syntactic analysis on giellatekno xml docs."""


import argparse
import multiprocessing
import os
import sys
from functools import partial

import lxml.etree as etree

from corpustools import argparse_version, ccat, corpuspath, modes, util
from corpustools.common_arg_ncpus import NCpus


def get_modename(path):
    """Get the modename depending on the CorpusPath"""
    if path.lang == "mhr":
        year = path.metadata.get_variable("year")
        if year:
            if 1909 < int(year) < 1939:
                return "hfst_thirties"
    if path.lang == "mrj":
        year = path.metadata.get_variable("year")
        if year:
            if 1909 < int(year) < 1939:
                return "hfst_thirties"
            if 1939 < int(year) < 1995:
                return "hfst_eighties"

    if path.lang in ["nob", "fin", "fao"]:
        return "hfst_no_korp"

    return "hfst"


def ccatter(path):
    """Turn an xml formatted file into clean text."""
    xml_printer = ccat.XMLPrinter(lang=path.lang, all_paragraphs=True)
    xml_printer.parse_file(path.converted)
    text = xml_printer.process_file().getvalue()
    if text:
        # Gruesome hack for mhr
        # When https://github.com/giellalt/lang-mhr/issues/3
        # is resolved, remove this
        if path.lang == "mhr":
            return " - ".join(part.strip() for part in text.split("-"))
        # end of hack
        return text

    raise UserWarning(f"Empty file {path.converted}")


def do_dependency_analysis(text, modename, lang):
    """Insert disambiguation and dependency analysis into the body."""
    pipeline = modes.Pipeline(modename, lang)
    pipeline.sanity_check()

    return pipeline.run(text.encode("utf8"))


def dependency_analysis(path, modename):
    """Insert disambiguation and dependency analysis into the body."""
    xml_file = etree.parse(path.converted)
    oldbody = xml_file.find(".//body")
    parent = oldbody.getparent()
    parent.remove(oldbody)

    body = etree.SubElement(parent, "body")
    dependency = etree.SubElement(body, "dependency")
    dependency.text = etree.CDATA(
        do_dependency_analysis(
            ccatter(path),
            modename=modename if modename is not None else get_modename(path),
            lang=path.lang,
        )
    )
    with util.ignored(OSError):
        os.makedirs(os.path.dirname(path.analysed))
    with open(path.analysed, "wb") as analysed_stream:
        analysed_stream.write(
            etree.tostring(
                xml_file, xml_declaration=True, encoding="utf8", pretty_print=True
            )
        )


def analyse(xml_file, modename):
    """Analyse a file if it is not ocr'ed."""
    try:
        path = corpuspath.make_corpus_path(xml_file)

        if not path.metadata.get_variable("ocr"):
            dependency_analysis(path, modename)
        else:
            print(xml_file, "is an OCR file and will not be analysed", file=sys.stderr)
    except (etree.XMLSyntaxError, UserWarning) as error:
        print("Can not parse", xml_file, file=sys.stderr)
        print("The error was:", str(error), file=sys.stderr)


def analyse_in_parallel(file_list, modename, pool_size):
    """Analyse file in parallel."""
    pool = multiprocessing.Pool(processes=pool_size)
    pool.map(partial(analyse, modename=modename), file_list)
    pool.close()  # no more tasks
    pool.join()  # wrap up current tasks


def analyse_serially(file_list, modename):
    """Analyse files one by one."""
    xml_files = list(file_list)
    print(f"Starting the analysis of {len(xml_files)} files")

    fileno = 0
    for xml_file in xml_files:
        fileno += 1
        # print some ugly banner cos i want to see progress on local
        # batch job
        util.print_frame("*" * 79)
        util.print_frame(f"Analysing {xml_file} [{fileno} of {len(xml_files)}]")
        util.print_frame("*" * 79)
        analyse(xml_file, modename)


def parse_options():
    """Parse the given options."""
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser], description="Analyse files in parallel."
    )

    parser.add_argument("--ncpus", action=NCpus, default=multiprocessing.cpu_count() * 2)
    parser.add_argument(
        "--serial",
        action="store_true",
        help="When this argument is used files will be analysed one by one."
             "Using --serial takes priority over --ncpus",
    )
    parser.add_argument(
        "-k",
        "--modename",
        choices=modes.list_modes(),
        help="You can set the analyser pipeline explicitely if you want.",
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

    try:
        if args.serial:
            analyse_serially(
                corpuspath.collect_files(args.converted_entities, suffix=".xml"),
                args.modename,
            )
        else:
            analyse_in_parallel(
                corpuspath.collect_files(args.converted_entities, suffix=".xml"),
                args.modename,
                args.ncpus,
            )
    except util.ArgumentError as error:
        print(f"Cannot do analysis\n{str(error)}", file=sys.stderr)
        raise SystemExit(1)
