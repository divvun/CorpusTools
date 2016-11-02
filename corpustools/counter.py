# -*- coding: utf-8 -*-

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
#   Copyright © 2012-2016 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

"""This file contains classes to convert files to the giellatekno xml format."""


from __future__ import absolute_import, print_function

import argparse
import logging
import os

from corpustools import argparse_version, converter, util


logging.basicConfig(level=logging.CRITICAL)


def count_files(path):
    """Count files in the given language."""
    cm = converter.ConverterManager(False, False)
    cm.collect_files([path])

    con = 0
    ana = 0
    for f in cm.FILES:
        c = cm.converter(f)
        if os.path.exists(c.names.converted):
            con += 1
        if os.path.exists(c.names.analysed):
            ana += 1

    return(len(cm.FILES), con, ana)


def main():

    for corpus in [os.getenv('GTFREE'), os.getenv('GTBOUND')]:
        print(corpus)
        for language in ['fkv', 'sma', 'sme', 'smj', 'smn', 'sms']:
            print(language,
                  count_files(os.path.join(corpus, 'orig', language)),
                  corpus
            )
