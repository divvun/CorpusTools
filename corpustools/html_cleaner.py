# -*- coding: utf-8 -*-

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
#   Copyright © 2013-2017 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

"""Script to write a nicely indented html doc.

Mainly used to debug the input to the converter.HTMLContentConverter.
"""


from __future__ import absolute_import

import argparse

from corpustools import argparse_version, htmlconverter, util


def parse_args():
    """Parse the commandline options.

    Returns:
        a list of arguments as parsed by argparse.Argumentparser.
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Program to print out a nicely indented html document. '
        'This makes it easier to see the structure of it. This eases '
        'debugging the conversion of html documents.')

    parser.add_argument('inhtml',
                        help='The path of the html to indent.')
    parser.add_argument('outhtml',
                        help='The place where the indented html doc is written')

    return parser.parse_args()


def main():
    """Convert an html file, and print the result to outfile."""
    args = parse_args()

    c = htmlconverter.convert2xhtml(
        htmlconverter.webpage_to_unicodehtml(args.inhtml))
    with open(args.outhtml, 'w') as outfile:
        util.print_element(c, 0, 4, outfile)
