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
        (argparse.Namespace): the parsed commandline arguments
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
