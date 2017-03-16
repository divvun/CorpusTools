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
#   Copyright © 2016-2017 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

"""One off funtions to set metadata.

Might be useful in other contexts.
"""


from __future__ import absolute_import, print_function

import collections
import os
import sys

from dateutil.parser import parse
from lxml import html

from corpustools import converter, corpuspath, util, xslsetter


def find_endings(directories, suffix):
    """Find all files in with suffix within directories.

    Arguments:
        directories (list of str): list of directories to walk
        suffix (str): files suffixes to be searched for

    Yields:
        str: path to file with suffix
    """
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file_ in files:
                if file_.endswith(suffix):
                    yield os.path.join(root, file_)


def regjeringen_no(directories):
    """Set metadata for regjeringen.no html files.

    Arguments:
        directories (list of str): list of directories to walk
    """
    for html_file in find_endings(directories, '.html'):
        conv = converter.HTMLConverter(html_file)
        content = html.document_fromstring(conv.content)

        should_write = False
        author = content.find('.//meta[@name="AUTHOR"]')
        if author is not None:
            should_write = True
            conv.md.set_variable('author1_ln', author.get('content'))

        creation_date = content.find('.//meta[@name="creation_date"]')
        if creation_date is not None:
            should_write = True
            conv.md.set_variable('year',
                                 parse(creation_date.get('content')).year)

        publisher = content.find('.//meta[@name="DC.Publisher"]')
        if publisher is not None:
            should_write = True
            conv.md.set_variable('publisher', publisher.get('content'))

        if should_write:
            conv.md.write_file()


def to_free(path):
    """Set the lisence type."""
    conv_manager = converter.ConverterManager(False, False)
    conv_manager.collect_files([path])

    for file_ in conv_manager.FILES:
        conv = conv_manager.converter(file_)
        conv.md.set_variable('license_type', 'free')
        conv.md.write_file()


def skuvla_historja(directories):
    """Find skuvlahistorja directories in paths, set year.

    Arguments:
        directories (list of str): list of directories to walk
    """
    years = {
        'skuvlahistorja1': '2005',
        'skuvlahistorja2': '2007',
        'skuvlahistorja3': '2009',
        'skuvlahistorja4': '2010',
        'skuvlahistorja5': '2011',
        'skuvlahistorja6': '2013',
    }

    for file_ in find_endings(directories, '.xsl'):
        if 'skuvlahistorja' in file_:
            print(file_)
            metadata = xslsetter.MetadataHandler(file_)
            metadata.set_variable('year', years[file_.split('/')[-1]])
            metadata.write_file()


def fin_admin(directories):
    """Set all docs from samediggi.fi to be translated from fin.

    Arguments:
        directories (list of str): list of directories to walk
    """
    counter = collections.defaultdict(int)
    for file_ in find_endings(directories, '.xsl'):
        corpus_path = corpuspath.CorpusPath(file_)
        if ('samediggi.fi' in corpus_path.metadata.get_variable(
                'filename') and
                corpus_path.metadata.get_variable(
                    'mainlang') == 'fin'):
            counter['fin'] += 1
            for parallel in corpus_path.parallels():
                counter['parallels'] += 1
                try:
                    metadata = xslsetter.MetadataHandler(parallel + '.xsl')
                except util.ArgumentError as error:
                    util.note(error)
                    util.note('Referenced from {}'.format(file_))
                finally:
                    metadata.set_variable('translated_from', 'fin')
                    metadata.write_file()

    print(counter)


if __name__ == "__main__":
    fin_admin(sys.argv[1:])
