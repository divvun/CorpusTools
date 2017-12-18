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
#   Copyright © 2012-2017 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Convert epub documents to the Giella xml format.

Epub files are zip files that contain text in xhtml files. This class reads
all xhtml files found in this archive. The body element of these files are
converted to div elements, and appended inside a new body element.

It is possible to filter away ranges of elements from this new xhtml file.
These ranges consist pairs of xpath paths, specified inside the metadata
file that belongs to this epub file.
"""

import sys
from lxml import etree

import epub
from corpustools import epubconverter, util, xslsetter
from prompt_toolkit import prompt


def print_choice(excluded, titles):
    print('\nIncluded chapters:')
    for index in not_chosen(excluded, titles):
        print('[{}]:\t{}'.format(index, titles[index]))

    print('\nExcluded chapters:')
    for index in excluded:
        print('[{}]:\t{}'.format(index, titles[index]))


def include(titles):
    while 1:
        text = prompt('\nWrite the chapter numbers to include, divided by space: ')
        excluded = not_chosen([int(index) for index in text.split()], titles)
        print_choice(excluded, titles)


def not_chosen(chosen, titles):
    return list(set([x for x in range(len(titles))]) - set(chosen))


def exclude(titles):
    while 1:
        text = prompt('\nWrite the chapter numbers to exclude, divided by space: ')
        excluded = [int(index)
                  for index in text.split()]
        print_choice(excluded, titles)


def get_titles(book):
    """Get the all linear chapters of the epub book.

    Arguments:
        book (epub.Book): The epub book element

    Yields:
        etree._Element: The body of an xhtml file found in the epub file.
    """
    return [epubconverter.read_chapter(chapter).find('.//{http://www.w3.org/1999/xhtml}title').text
            for chapter in book.chapters]


def main():
    book = epub.Book(epub.open_epub(sys.argv[1]))
    md = xslsetter.MetadataHandler(sys.argv[1] + '.xsl')
    excluded = md.epub_excluded_chapters
    titles = get_titles(book)
    print_choice(excluded, titles)

    while 1:
        text = prompt('\nWould you like to mainly [i]nclude or [e]xclude chapters?: ')
        if text.strip() == 'i':
            include(titles)
        elif text.strip() == 'e':
            exclude(titles)
        else:
            print('Invalid choice, write either i or e')
        print('You said: %s' % text)
