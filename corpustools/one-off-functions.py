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
#   Copyright © 2016-2017 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

"""One off funtions to set metadata.

Might be useful in other contexts.
"""


from __future__ import absolute_import, print_function

from lxml import etree, html
from dateutil.parser import parse
import os
import sys

from corpustools import converter


def html_files(path):
    """Find all html files in path."""
    for directory in path:
        for root, _, files in os.walk(directory):
            for f in files:
                if f.endswith('.html'):
                    yield(os.path.join(root, f))


def regjeringen_no(path):
    """Set metadata for regjeringen.no html files."""
    for html_file in html_files(path):
        conv = converter.HTMLConverter(html_file)
        c = html.document_fromstring(conv.content)

        w = False
        author = c.find('.//meta[@name="AUTHOR"]')
        if author is not None:
            w = True
            conv.md.set_variable('author1_ln', author.get('content'))

        cd = c.find('.//meta[@name="creation_date"]')
        if cd is not None:
            w = True
            conv.md.set_variable('year', parse(cd.get('content')).year)

        pub = c.find('.//meta[@name="DC.Publisher"]')
        if pub is not None:
            w = True
            conv.md.set_variable('publisher', pub.get('content'))

        if w:
            conv.md.write_file()


def to_free(path):
    """Set the lisence type."""
    cm = converter.ConverterManager(False, False)
    cm.collect_files([path])

    for f in cm.FILES:
        c = cm.converter(f)
        c.md.set_variable('license_type', 'free')
        c.md.write_file()


def skuvla_historja(path):
    """Find skuvlahistorja directories in path, set year."""
    years = {
        '1': '2005',
        '2': '2007',
        '3': '2009',
        '4': '2010',
        '5': '2011',
        '6': '2013',
    }

    for root, _, files in os.walk(path):
        if 'skuvlahistorja' in root:
            print(root)
            for f in files:
                if f.endswith('.html'):
                    print(f)
                    conv = converter.HTMLConverter(os.path.join(root, f))
                    conv.md.set_variable('year', years[root[-1]])
                    conv.md.write_file()


if __name__ == "__main__":
    skuvla_historja(sys.argv[1])
