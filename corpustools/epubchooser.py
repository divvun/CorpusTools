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
#   Copyright © 2017 The University of Tromsø &
#                    the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Set which parts of an epub should be omitted.

It is possible to filter away chapters and ranges of elements from an epub
file. This is a helper program for that purpose.
"""
import argparse
import sys

import six
from prompt_toolkit import prompt

import epub
from corpustools import argparse_version, epubconverter, xslsetter


class EpubPresenter(object):
    """Class to present metadata and content.

    Attributes:
        path (str): path to the epub document
        book (epub.Book): the epub document to handle.
        metadata (xslsetter.MetadataHandler): the corpus metadata
            attached to the book.
    """

    def __init__(self, path):
        """Initialise the EpubPresenter class.

        Arguments:
            path (str): path to the epub document
        """
        self.path = path
        self.book = epub.Book(epub.open_epub(sys.argv[1]))
        self.metadata = xslsetter.MetadataHandler(sys.argv[1] + '.xsl')

    @property
    def book_titles(self):
        """Get the all linear chapters of the epub book.

        Arguments:
            book (epub.Book): The epub book element

        Yields:
            etree._Element: The body of an xhtml file found in the epub file.
        """
        return [
            epubconverter.read_chapter(chapter).find(
                './/{http://www.w3.org/1999/xhtml}title').text
            for chapter in self.book.chapters
        ]

    @property
    def excluded_chapters(self):
        """Show the excluded chapters."""
        return self.metadata.epub_excluded_chapters

    @excluded_chapters.setter
    def excluded_chapters(self, new_excluded):
        """Set the exluded chapters in the metadata file.

        Arguments:
            new_excluded (list of int): the chapters to exclude.
        """
        self.metadata.set_variable('epub_excluded_chapters', ', '.join(
            [str(index) for index in new_excluded]))

    def print_choice(self):
        """Present omitted and present chapters."""
        print('\nIncluded chapters:')
        for index in self.not_chosen:
            print('[{}]:\t{}'.format(index, self.book_titles[index]))

        print('\nExcluded chapters:')
        for index in self.excluded_chapters:
            print('[{}]:\t{}'.format(index, self.book_titles[index]))

    @property
    def not_chosen(self):
        """The chapter that are not excluded."""
        return list(
            set([x for x in range(len(self.book_titles))]) -
            set(self.excluded_chapters))

    def save(self):
        """Save metadata."""
        self.metadata.write_file()

    @property
    def skip_elements(self):
        """Return a string representing the html elements that is omitted."""
        if self.metadata.skip_elements:
            return ', '.join(
                [';'.join(pair) for pair in self.metadata.skip_elements])
        else:
            return ''

    @skip_elements.setter
    def skip_elements(self, elements):
        """Set the md set_variable skip_elements.

        Arguments:
            elements (str): the elements that should be skip
        """
        self.metadata.set_variable('skip_elements', elements)

    def present_html(self):
        """Print the html that is left after omitting chapters."""
        print_xpath(
            epubconverter.extract_content(self.path, self.metadata), 0, 4,
            sys.stdout)


class EpubChooser(object):
    """Class to determine which parts of an epub should be omitted.

    Attributes:
        presenter (EpubPresenter): the presenter of the metadata and content
            of the epub file.
    """

    def __init__(self, path):
        """Initialise the EpubChooser class.

        Arguments:
            path (str): path to the document
        """
        self.presenter = EpubPresenter(path)

    def exclude_chapters(self):
        """Choose which chapters should be omitted from the epub file."""
        while 1:
            self.presenter.print_choice()
            text = prompt('\nWould you like to \n'
                          '* [c]lear and edit empty range\n'
                          '* s[a]ve this and go to next step\n'
                          '* [s]ave and quit\n* [q]uit without saving\n'
                          '[c/a/s/q]: ')
            if text == 'c':
                edits = prompt('Make new range: ')
                new_excluded = [int(index) for index in edits.split()]
                self.presenter.excluded_chapters = new_excluded
            elif text == 'a':
                break
            elif text == 's':
                self.presenter.save()
                raise SystemExit('Saved your choises')
            elif text == 'q':
                raise SystemExit('Did not save anything')
            else:
                print('Invalid choice, trying again.')

    def exclude_tags(self):
        """Choose which html tags should be removed from epub file."""
        while 1:
            self.presenter.present_html()
            existing_range = self.presenter.skip_elements
            text = prompt('Choose html ranges that should be removed\n'
                          'Existing ranges are: "{}"\n'
                          '* [c]lear and make new range\n'
                          '* [a]add range\n'
                          '* [s]ave and quit\n'
                          '* [q]uit without saving\n'
                          '[c/a/s/q]: '.format(existing_range))
            if text == 'c':
                start = prompt('First xpath: ')
                end = prompt('Second xpath: ')
                self.presenter.skip_elements = ';'.join([start, end])
            elif text == 'a':
                start = prompt(
                    'Cut and paste xpath expressions found in the text above\n'
                    'First xpath: ')
                end = prompt('Second xpath: ')
                self.presenter.skip_elements = '{}, {};{}'.format(
                    self.presenter.skip_elements, start, end)
            elif text == 's':
                self.presenter.save()
                raise SystemExit('Saved your choises')
            elif text == 'q':
                raise SystemExit('Did not save anything')
            else:
                print('Invalid choice, trying again.')


def print_xpath(element, level, indent, out, xpath='', element_no=1):
    """Format an html document and write xpaths at tags openings.

    This function formats html documents for readability and prints
    xpaths to at tag openings, to see the structure of the given document
    and make it possible to choose xpaths. It ruins white space in
    text parts.

    Args:
        element (etree._Element): the element to format.
        level (int): indicate at what level this element is.
        indent (int): indicate how many spaces this element should be indented
        out (stream): a buffer where the formatted element is written.
        xpath (string): The xpath of the parent of this element.
        tag_no (int): the position of the element tag
    """
    counter = {}
    tag = element.tag.replace('{http://www.w3.org/1999/xhtml}', '')

    out.write(' ' * (level * indent))
    out.write('<{}'.format(tag))

    for att_tag, att_value in six.iteritems(element.attrib):
        out.write(' ')
        out.write(att_tag)
        out.write('="')
        out.write(att_value)
        out.write('"')

    out.write('>')
    if xpath and '/body' in xpath:
        out.write('\t')
        out.write(xpath.replace('/html/', './/'))
        out.write('/')
        out.write(tag)
        if element_no > 1:
            out.write('[')
            out.write(str(element_no))
            out.write(']')
    out.write('\n')

    if element.text is not None and element.text.strip() != '':
        out.write(' ' * ((level + 1) * indent))
        out.write(element.text.strip())
        out.write('\n')

    for child in element:
        if not counter.get(child.tag):
            counter[child.tag] = 0
        counter[child.tag] += 1
        if element_no > 1:
            new_xpath = xpath + '/' + tag + '[' + str(element_no) + ']'
        else:
            new_xpath = xpath + '/' + tag
        print_xpath(
            child,
            level + 1,
            indent,
            out,
            xpath=new_xpath,
            element_no=counter[child.tag])

    out.write(' ' * (level * indent))
    out.write('</{}>\n'.format(tag))

    if level > 0 and element.tail is not None and element.tail.strip() != '':
        for _ in range(0, (level - 1) * indent):
            out.write(' ')
        out.write(element.tail.strip())
        out.write('\n')


def parse_options():
    """Parse the commandline options.

    Returns:
        a list of arguments as parsed by argparse.Argumentparser.
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description=
        'Choose which chapters and html ranges should be omitted from '
        'an epub file.')

    parser.add_argument('epubfile', help='Path to an epub file')

    args = parser.parse_args()

    return args


def main():
    """Set which parts of an epub should be omitted."""
    args = parse_options()

    chooser = EpubChooser(args.epubfile)
    chooser.exclude_chapters()
    chooser.exclude_tags()
