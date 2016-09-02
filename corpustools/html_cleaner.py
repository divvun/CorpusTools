# -*- coding: utf-8 -*-

#
#   Script to write a nicely indented html doc. Mainly used to debug the
#   input to the converter.HTMLContentConverter
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
#   Copyright © 2013-2016 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

from __future__ import absolute_import

import argparse

from corpustools import argparse_version, converter, util


def parse_args():
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
    args = parse_args()

    with open(args.inhtml) as f:
        c = converter.HTMLContentConverter(args.inhtml, False, content=f.read())
        with open(args.outhtml, 'wb') as outfile:
            util.print_element(c.soup, 0, 4, outfile)
