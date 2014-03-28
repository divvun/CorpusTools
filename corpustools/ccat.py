# -*- coding:utf-8 -*-

#
#   This file contains a class and main function to convert giellatekno xml
#   formatted files to pure text
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
#   Copyright 2013-2014 Børre Gaup <borre.gaup@uit.no>
#

import inspect
from lxml import etree
import StringIO
import os
import sys
import argparse


def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno


class XMLPrinter:
    """This is a class to convert giellatekno xml formatted files to plain text
    """
    def __init__(self,
                 lang=None,
                 all_paragraphs=False,
                 title=False,
                 listitem=False,
                 table=False,
                 correction=False,
                 error=False,
                 errorort=False,
                 errorortreal=False,
                 errormorphsyn=False,
                 errorsyn=False,
                 errorlex=False,
                 errorlang=False,
                 noforeign=False,
                 typos=False,
                 print_filename=False,
                 one_word_per_line=False,
                 disambiguation=False,
                 dependency=False,
                 hyph_replacement=''):

        self.paragraph = True
        self.all_paragraphs = all_paragraphs

        if title or listitem or table:
            self.paragraph = False

        self.title = title
        self.listitem = listitem
        self.table = table

        self.correction = correction
        self.error = error
        self.errorort = errorort
        self.errorortreal = errorortreal
        self.errormorphsyn = errormorphsyn
        self.errorsyn = errorsyn
        self.errorlex = errorlex
        self.errorlang = errorlang
        self.noforeign = noforeign

        if (error or
                errorort or
                errorortreal or
                errormorphsyn or
                errorsyn or
                errorlex or
                errorlang or
                noforeign):
            self.error_filtering = True
        else:
            self.error_filtering = False

        self.typos = typos
        self.print_filename = print_filename
        if self.typos:
            self.one_word_per_line = True
        else:
            self.one_word_per_line = one_word_per_line

        self.lang = lang

        self.disambiguation = disambiguation
        self.dependency = dependency

        if hyph_replacement == 'xml':
            self.hyph_replacement = '<hyph/>'
        else:
            self.hyph_replacement = hyph_replacement

    def get_lang(self):
        """
        Get the lang of the file
        """
        return self.etree.getroot().\
            attrib['{http://www.w3.org/XML/1998/namespace}lang']

    def get_genre(self):
        u"""
        @brief Get the genre from the xml file

        :returns: the genre as set in the xml file
        """
        if self.etree.getroot().find(u".//genre") is not None:
            return self.etree.getroot().find(u".//genre").attrib[u"code"]
        else:
            return u'none'

    def get_translatedfrom(self):
        u"""
        @brief Get the translated_from value from the xml file

        :returns: the value of translated_from as set in the xml file
        """
        if self.etree.getroot().find(u".//translated_from") is not None:
            return self.etree.getroot().find(u".//translated_from").\
                attrib[u"{http://www.w3.org/XML/1998/namespace}lang"]
        else:
            return u'none'

    def get_element_language(self, element, parentlang):
        """Get the language of element.

        Elements inherit the parents language if not explicitely set
        """
        if element.get('{http://www.w3.org/XML/1998/namespace}lang') is None:
            return parentlang
        else:
            return element.get('{http://www.w3.org/XML/1998/namespace}lang')

    def collect_not_inline_errors(self, element, textlist):
        '''Add the formatted errors as strings to the textlist list
        '''
        error_string = self.error_not_inline(element)
        if error_string != '':
            textlist.append(error_string)

        for child in element:
            if self.visit_error_not_inline(child):
                self.collect_not_inline_errors(child, textlist)

        if not self.typos:
            if element.tail is not None and element.tail.strip() != '':
                if not self.one_word_per_line:
                    textlist.append(element.tail.strip())
                else:
                    textlist.append('\n'.join(element.tail.strip().split()))

    def error_not_inline(self, element):
        '''Collect and format element.text, element.tail and
        the attributes into the string text

        Also scan the children if there is no error filtering or
        if the element is filtered
        '''
        text = ''
        if not self.noforeign:
            if element.text is not None and element.text.strip() != '':
                text = element.text.strip()

            if not self.error_filtering or self.include_this_error(element):
                for child in element:
                    if text != '':
                        text += ' '
                    text += child.get('correct')
                    if child.tail is not None and child.tail.strip() != '':
                        text += ' ' + child.tail.strip()

            text += self.get_error_attributes(dict(element.attrib))

        return text

    def get_error_attributes(self, attributes):
        '''Collect and format the attributes + the filename
        into the string text.
        '''
        text = '\t'
        text += attributes.get('correct')
        del attributes['correct']

        attr = []
        for key in sorted(attributes):
            attr.append(key + '=' + attributes[key])

        if len(attr) > 0:
            text += '\t#'
            text += ','.join(attr)

            if self.print_filename:
                text += ', file: ' + os.path.basename(self.filename)

        elif self.print_filename:
            text += '\t#file: ' + os.path.basename(self.filename)

        return text

    def collect_inline_errors(self, element, textlist, parentlang):
        '''Add the "correct" element to the list textlist
        '''
        if element.get('correct') is not None and not self.noforeign:
            textlist.append(element.get('correct'))

        self.get_tail(element, textlist, parentlang)

    def collect_text(self, element, parentlang, buffer):
        """Collect text from element, and write the contents to buffer
        """
        textlist = []

        self.visit_nonerror_element(element, textlist, parentlang)

        if len(textlist) > 0:
            if not self.one_word_per_line:
                buffer.write(' '.join(textlist).encode('utf8'))
                buffer.write(' ¶\n')
            else:
                buffer.write('\n'.join(textlist).encode('utf8'))
                buffer.write('\n')

    def get_text(self, element, textlist, parentlang):
        '''Get the text part of an lxml element
        '''
        if (element.text is not None and element.text.strip() != '' and
            (self.lang is None or
             self.get_element_language(element, parentlang) == self.lang)):
            if not self.one_word_per_line:
                textlist.append(element.text.strip())
            else:
                textlist.append('\n'.join(element.text.strip().split()))

    def get_tail(self, element, textlist, parentlang):
        '''Get the tail part of an lxml element
        '''
        if (element.tail is not None and element.tail.strip() != '' and
                (self.lang is None or parentlang == self.lang)):
            if not self.one_word_per_line:
                textlist.append(element.tail.strip())
            else:
                textlist.append('\n'.join(element.tail.strip().split()))

    def visit_children(self, element, textlist, parentlang):
        """Visit the children of element, adding their content to textlist
        """
        for child in element:
            if self.visit_error_inline(child):
                self.collect_inline_errors(
                    child,
                    textlist,
                    self.get_element_language(child, parentlang))
            elif self.visit_error_not_inline(child):
                self.collect_not_inline_errors(child, textlist)
            else:
                self.visit_nonerror_element(
                    child,
                    textlist,
                    self.get_element_language(element, parentlang))

    def visit_nonerror_element(self, element, textlist, parentlang):
        """Visit and extract text from non error element
        """
        if not self.typos:
            self.get_text(element, textlist, parentlang)
        self.visit_children(element, textlist, parentlang)
        if not self.typos:
            self.get_tail(element, textlist, parentlang)

    def visit_this_node(self, element):
        '''Return True if the element should be visited
        '''
        return (
            self.all_paragraphs or
            (
                self.paragraph is True and (element.get('type') is None or
                                            element.get('type') == 'text')
            ) or (
                self.title is True and element.get('type') == 'title'
            ) or (
                self.listitem is True and element.get('type') == 'listitem'
            ) or (
                self.table is True and element.get('type') == 'tablecell'
            )
        )

    def visit_error_not_inline(self, element):
        """Determine whether element should be visited
        """
        return (
            element.tag.startswith('error') and self.one_word_per_line and not
            self.error_filtering or
            self.include_this_error(element)
            )

    def visit_error_inline(self, element):
        """Determine whether element should be visited
        """
        return (element.tag.startswith('error') and not
                self.one_word_per_line and
                (self.correction or self.include_this_error(element))
                )

    def include_this_error(self, element):
        """Determine whether element should be visited
        """
        return self.error_filtering and (
            (element.tag == 'error' and self.error) or
            (element.tag == 'errorort' and self.errorort) or
            (element.tag == 'errorortreal' and self.errorortreal) or
            (element.tag == 'errormorphsyn' and self.errormorphsyn) or
            (element.tag == 'errorsyn' and self.errorsyn) or
            (element.tag == 'errorlex' and self.errorlex) or
            (element.tag == 'errorlang' and self.errorlang) or
            (element.tag == 'errorlang' and self.noforeign)
            )

    def parse_file(self, filename):
        self.filename = filename
        p = etree.XMLParser(huge_tree=True)
        self.etree = etree.parse(filename, p)

    def process_file(self):
        """Process the given file, adding the text into buffer

        Returns the buffer
        """
        buffer = StringIO.StringIO()

        self.handle_hyph()
        if self.dependency:
            self.print_element(self.etree.find('.//dependency'), buffer)
        elif self.disambiguation:
            self.print_element(self.etree.find('.//disambiguation'), buffer)
        else:
            for paragraph in self.etree.findall('.//p'):
                if self.visit_this_node(paragraph):
                    self.collect_text(paragraph, self.get_lang(), buffer)

        return buffer

    def handle_hyph(self):
        """Replace hyph tags
        """
        hyph_tails = []
        for hyph in self.etree.findall('.//hyph'):
            hyph_tails.append(hyph.tail)

            if hyph.getnext() is None:
                if hyph.getparent().text is not None:
                    hyph_tails.insert(0, hyph.getparent().text)
                hyph.getparent().text = self.hyph_replacement.join(hyph_tails)
                hyph_tails[:] = []

            hyph.getparent().remove(hyph)


    def print_element(self, element, buffer):
        if element is not None and element.text is not None:
            buffer.write(element.text.encode('utf8'))

    def print_file(self, file_):
        '''Print a xml file to stdout'''
        self.parse_file(file_)
        sys.stdout.write(self.process_file().getvalue())


def parse_options():
    """Parse the options given to the program
    """
    parser = argparse.ArgumentParser(
        description='Print the contents of a corpus in XML format\n\
        The default is to print paragraphs with no type (=text type).')

    parser.add_argument('-l',
                        dest='lang',
                        help='Print only elements in language LANG. Default \
                        is all langs.')
    parser.add_argument('-T',
                        dest='title',
                        action='store_true',
                        help='Print paragraphs with title type', )
    parser.add_argument('-L',
                        dest='list',
                        action='store_true',
                        help='Print paragraphs with list type')
    parser.add_argument('-t',
                        dest='table',
                        action='store_true',
                        help='Print paragraphs with table type')
    parser.add_argument('-a',
                        dest='all_paragraphs',
                        action='store_true',
                        help='Print all text elements')

    parser.add_argument('-c',
                        dest='corrections',
                        action='store_true',
                        help='Print corrected text instead of the original \
                        typos & errors')
    parser.add_argument('-C',
                        dest='error',
                        action='store_true',
                        help='Only print unclassified (§/<error..>) \
                        corrections')
    parser.add_argument('-ort',
                        dest='errorort',
                        action='store_true',
                        help='Only print ortoghraphic, non-word \
                        ($/<errorort..>) corrections')
    parser.add_argument('-ortreal',
                        dest='errorortreal',
                        action='store_true',
                        help='Only print ortoghraphic, real-word \
                        (¢/<errorortreal..>) corrections')
    parser.add_argument('-morphsyn',
                        dest='errormorphsyn',
                        action='store_true',
                        help='Only print morphosyntactic \
                        (£/<errormorphsyn..>) corrections')
    parser.add_argument('-syn',
                        dest='errorsyn',
                        action='store_true',
                        help='Only print syntactic (¥/<errorsyn..>) \
                        corrections')
    parser.add_argument('-lex',
                        dest='errorlex',
                        action='store_true',
                        help='Only print lexical (€/<errorlex..>) \
                        corrections')
    parser.add_argument('-foreign',
                        dest='errorlang',
                        action='store_true',
                        help='Only print foreign (∞/<errorlang..>) \
                        corrections')
    parser.add_argument('-noforeign',
                        dest='noforeign',
                        action='store_true',
                        help='Do not print anything from foreign \
                        (∞/<errorlang..>) corrections')
    parser.add_argument('-typos',
                        dest='typos',
                        action='store_true',
                        help='Print only the errors/typos in the text, with \
                        corrections tab-separated')
    parser.add_argument('-f',
                        dest='print_filename',
                        action='store_true',
                        help='Add the source filename as a comment after each \
                        error word.')
    parser.add_argument('-S',
                        dest='one_word_per_line',
                        action='store_true',
                        help='Print the whole text one word per line; \
                        typos have tab separated corrections')
    parser.add_argument('-dis',
                        dest='disambiguation',
                        action='store_true',
                        help='Print the disambiguation element')
    parser.add_argument('-dep',
                        dest='dependency',
                        action='store_true',
                        help='Print the dependency element')
    parser.add_argument('-hyph',
                        dest='hyph_replacement',
                        default='',
                        help='Replace hyph tags with the given argument')

    parser.add_argument('-r',
                        dest='recursive',
                        action='store_true',
                        help='Recursively process directory and \
                        subdirs encountered')
    parser.add_argument('targets',
                        nargs='+',
                        help='Name of the files or directories to process')

    args = parser.parse_args()
    return args


def main():
    """Set up the XMLPrinter class with the given command line options and
    process the given files and directories
    Print the output to stdout
    """
    args = parse_options()

    xml_printer = XMLPrinter(lang=args.lang,
                             all_paragraphs=args.all_paragraphs,
                             title=args.title,
                             listitem=args.list,
                             table=args.table,
                             correction=args.corrections,
                             error=args.error,
                             errorort=args.errorort,
                             errorortreal=args.errorortreal,
                             errormorphsyn=args.errormorphsyn,
                             errorsyn=args.errorsyn,
                             errorlex=args.errorlex,
                             errorlang=args.errorlang,
                             noforeign=args.noforeign,
                             typos=args.typos,
                             print_filename=args.print_filename,
                             one_word_per_line=args.one_word_per_line,
                             dependency=args.dependency,
                             disambiguation=args.disambiguation,
                             hyph_replacement=args.hyph_replacement)

    for target in args.targets:
        if os.path.isfile(target):
            xml_printer.print_file(target)
        elif os.path.isdir(target):
            for root, dirs, files in os.walk(target):
                for xml_file in files:
                    xml_printer.print_file(os.path.join(root, xml_file))

if __name__ == '__main__':
    main()
