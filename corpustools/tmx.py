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
#   Copyright © 2011-2023 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Classes and functions to make and handle Translation Memory eXchange files."""


import argparse
import os

from lxml import etree

from corpustools import argparse_version, corpuspath

HERE = os.path.dirname(__file__)


def make_tu(line1, file1_lang, line2, file2_lang):
    """Make a tmx tu element based on line1 and line2 as input."""
    transl_unit = etree.Element("tu")

    transl_unit.append(make_tuv(line1, file1_lang))
    transl_unit.append(make_tuv(line2, file2_lang))

    return transl_unit


def add_filename_id(filename):
    """Add the tmx filename as an prop element in the header."""
    prop = etree.Element("prop")
    prop.attrib["type"] = "x-filename"
    prop.text = filename

    return prop


def make_tmx_header(filename, lang):
    """Make a tmx header based on the lang variable."""
    header = etree.Element("header")

    # Set various attributes
    header.attrib["segtype"] = "sentence"
    header.attrib["o-tmf"] = "OmegaT TMX"
    header.attrib["adminlang"] = "en-US"
    header.attrib["srclang"] = lang
    header.attrib["datatype"] = "plaintext"

    header.append(add_filename_id(filename))

    return header


def make_tmx(file1_name, file1_lang, file2_lang, sentence_pairs):
    """Make tmx file based on the output of the aligner."""
    tmx = etree.Element("tmx")
    header = make_tmx_header(
        file1_name,
        file1_lang,
    )
    tmx.append(header)

    body = etree.SubElement(tmx, "body")
    for line1, line2 in zip(*sentence_pairs):
        transl_unit = make_tu(line1, file1_lang, line2, file2_lang)
        body.append(transl_unit)

    return tmx


def make_tuv(line, lang):
    """Make a tuv element given an input line and a lang variable."""
    tuv = etree.Element("tuv")
    tuv.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = lang
    seg = etree.Element("seg")
    seg.text = line.strip()
    tuv.append(seg)

    return tuv


def tmx2html(filename):
    """Turn a tmx file into an html file.

    Args:
        filename (str): name of a tmx file
    """
    tmx = etree.parse(filename)
    html2tmx_transformer = etree.XSLT(
        etree.parse(os.path.join(HERE, "xslt/tmx2html.xsl"))
    )

    html_name = filename.with_name(filename.name + ".html")
    html_name.write_bytes(
        etree.tostring(
            html2tmx_transformer(tmx),
            pretty_print=True,
            encoding="utf-8",
            xml_declaration=True,
        )
    )
    print(f"Wrote {html_name}")


def parse_options():
    """Parse the commandline options.

    Returns:
        a list of arguments as parsed by argparse.Argumentparser.
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser], description="Convert tmx files to html"
    )

    parser.add_argument(
        "sources", nargs="+", help="Files or directories to search for tmx files"
    )

    args = parser.parse_args()
    return args


def main():
    """Parallelise files."""
    args = parse_options()

    for source in corpuspath.collect_files(args.sources, suffix=".tmx"):
        tmx2html(source)
