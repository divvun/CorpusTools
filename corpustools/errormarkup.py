# -*- coding: utf-8 -*-

#
#   This file contains routines to convert errormarkup to xml
#   as specified in the giellatekno xml format.
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
#   Copyright 2013 Børre Gaup <borre.gaup@uit.no>
#

import re
from lxml import etree


class ErrorMarkup:
    '''This is a class to convert errormarkuped text to xml
    '''
    def __init__(self, filename):
        self._filename = filename
        self.types = {u"$": u"errorort",
                      u"¢": "errorortreal",
                      u"€": "errorlex",
                      u"£": "errormorphsyn",
                      u"¥": "errorsyn",
                      u"§": "error",
                      u"∞": "errorlang"}
        self.error_regex = re.compile(u'(?P<error>\([^\(]*\)$|\w+$|\w+[-\':\]]\w+$|\w+[-\'\]\./]$|\d+’\w+$|\d+%:\w+$|”\w+”$)', re.UNICODE)
        self.correction_regex = re.compile(u'(?P<correction>[$€£¥§¢∞]\([^\)]*\)|[$€£¥§¢∞]\S+)(?P<tail>.*)', re.UNICODE)

    def add_error_markup(self, element):
        self.really_add_error_markup(element)
        for elt in element:
            self.add_error_markup(elt)

    def really_add_error_markup(self, element):
        '''
        Search for errormarkup in the text and tail of an etree.Element
        If found, replace errormarkuped text with xml

        To see examples of what new_content consists of, have a look at the
        test_error_parser* methods

        '''
        self.fix_text(element)
        self.fix_tail(element)

    def fix_text(self, element):
        '''Replace the text of an element with errormarkup if possible
        '''
        new_content = self.error_parser(element.text)

        if new_content:
            element.text = None

            if isinstance(new_content[0], basestring):
                element.text = new_content[0]
                new_content = new_content[1:]

            new_pos = 0
            for part in new_content:
                element.insert(new_pos, part)
                new_pos += 1

    def fix_tail(self, element):
        '''Replace the tail of an element with errormarkup if possible
        '''
        new_content = self.error_parser(element.tail)

        if new_content:
            element.tail = None

            if isinstance(new_content[0], basestring):
                element.tail = new_content[0]
                new_content = new_content[1:]

            new_pos = element.getparent().index(element) + 1
            for part in new_content:
                element.getparent().insert(new_pos, part)
                new_pos += 1

    def error_parser(self, text):
        '''
        Parse errormarkup found in text. If any markup is found, return
        a list of elements in elements

        result -- contains a list of non-correction/correction parts

        The algorithm for parsing the error is:
        Find a correction in the result list.

        If the preceding element in result contains a simple error and is not a
        correction make an error_element, append it to elements

        If the preceding element in result is not a simple error, it is part of
        nested markup.

        '''

        if text:
            text = text.replace('\n', ' ')
            result = self.process_text(text)

            if len(result) > 1:
                #print text
                #print result
                elements = []
                # This means that we are inside an error markup
                # Start with the two first elements
                # The first contains an error, the second one is a correction

                for index in range(0, len(result)):
                    if self.is_correction(result[index]):
                        if (not self.is_correction(result[index-1]) and
                                self.is_error(result[index-1])):
                            self.add_simple_error(elements,
                                                  result[index-1],
                                                  result[index])

                        else:

                            self.add_nested_error(elements,
                                                  result[index-1],
                                                  result[index])

                if not self.is_correction(result[-1]):
                    elements[-1].tail = result[-1]

                return elements

    def add_simple_error(self, elements, errorstring, correctionstring):
        '''Make an error element, append it to elements

        elements -- a list of error_elements
        errorstring -- a string containing a text part and an errormarkup
        error
        correctionstring -- a string containing an errormarkup correction

        '''
        (head, error) = self.process_head(errorstring)
        if len(elements) == 0:
            if head != '':
                elements.append(head)
        else:
            elements[-1].tail = head

        error_element = self.get_error(error, correctionstring)

        elements.append(error_element)

    def add_nested_error(self, elements, errorstring, correctionstring):
        '''Make error_element, append it to elements

        elements -- a list of error_elements
        errorstring -- contains either a correction or string ending with
        a right parenthesis )
        correctionstring -- a string containing an errormarkup correction

        The algorithm:
        At least the last element in elements will be engulfed in error_element
        and replaced by error_element in elements

        Remove the last element, use it as the inner_element when making
        error_element

        If the errorstring is not a correction, then it ends in a ).

        Extract the string from the last element of elements.
        If a ( is found, set the part before ( to be the tail of the last
        element of elements. Set the part after ( to be the text of
        error_element, append error_element to elements.

        If a ( is not found, insert the last element of elements as first child
        of error_element, continue searching

        '''
        #print u'«' + errorstring + u'»', u'«' + correctionstring + u'»'
        try:
            inner_element = elements[-1]
        except IndexError:
            print '\n', self._filename
            print "Cannot handle:\n"
            print errorstring + correctionstring
            print "This is either an error in the markup or an error in the \
            errormarkup conversion code"
            print "If the markup is correct, send a report about this error \
            to borre.gaup@uit.no"

        elements.remove(elements[-1])
        if not self.is_correction(errorstring):
            inner_element.tail = errorstring[:-1]
        error_element = self.get_error(inner_element, correctionstring)

        if self.is_correction(errorstring):
            elements.append(error_element)
        else:
            parenthesis_found = False

            while not parenthesis_found:
                text = self.get_text(elements[-1])

                index = text.rfind('(')
                if index > -1:
                    parenthesis_found = True

                    error_element.text = text[index+1:]
                    if isinstance(elements[-1], etree._Element):
                        elements[-1].tail = text[:index]
                    else:
                        elements[-1] = text[:index]
                    elements.append(error_element)

                else:
                    inner_element = elements[-1]
                    elements.remove(elements[-1])
                    try:
                        error_element.insert(0, inner_element)
                    except TypeError as e:
                        print '\n', self._filename
                        print str(e)
                        print u"The program expected an error element, but \
                        found a string:\n«" + inner_element + u"»"
                        print u"There is either an error in errormarkup close \
                        to this sentence"
                        print u"or the program cannot evaluate a correct \
                        errormarkup."
                        print u"If the errormarkup is correct, please report \
                        about the error to borre.gaup@uit.no"

    def get_text(self, element):
        text = None
        if isinstance(element, etree._Element):
            text = element.tail
        else:
            text = element

        return text

    def is_correction(self, expression):
        return self.correction_regex.search(expression)

    def process_text(self, text):
        '''Divide the text in to a list consisting of alternate
        non-correctionstring/correctionstrings
        '''
        result = []

        matches = self.correction_regex.search(text)
        while matches:
            head = self.correction_regex.sub('', text)
            if not (head != '' and head[-1] == " "):
                if head != '':
                    result.append(head)
                result.append(matches.group('correction'))
            text = matches.group('tail')
            matches = self.correction_regex.search(text)

        if text != '':
            result.append(text)

        return result

    def process_head(self, text):
        '''Divide text into text/error parts
        '''
        matches = self.error_regex.search(text)
        text = self.error_regex.sub('', text)

        return (text, matches.group('error'))

    def is_error(self, text):
        return self.error_regex.search(text)

    def get_error(self, error, correction):
        '''Make an error_element

        error -- is either a string or an etree.Element
        correction -- is a correctionstring

        '''
        (fixed_correction, ext_att, att_list) = \
            self.look_for_extended_attributes(
                correction[1:].replace('(', '').replace(')', ''))

        element_name = self.get_element_name(correction[0])

        error_element = self.make_error_element(error,
                                                fixed_correction,
                                                element_name,
                                                att_list)

        return error_element

    def look_for_extended_attributes(self, correction):
        '''Extract attributes and correction from a correctionstring
        '''
        ext_att = False
        att_list = None
        if '|' in correction:
            ext_att = True
            try:
                (att_list, correction) = correction.split('|')
            except ValueError as e:
                print '\n', self._filename
                print str(e)
                print u"too many | characters inside the correction. «" +\
                    correction + u"»"
                print u"Have you remembered to encase the error inside \
                parenthesis, e.g. (vowlat,a-á|servodatvuogádat)?"
                print u"If the errormarkup is correct, send a report about \
                this error to borre.gaup@uit.no"

        return (correction, ext_att, att_list)

    def get_element_name(self, separator):
        return self.types[separator]

    def make_error_element(self,
                           error,
                           fixed_correction,
                           element_name,
                           att_list):
        error_element = etree.Element(element_name)
        if isinstance(error, etree._Element):
            error_element.append(error)
        else:
            error_element.text = error.replace('(', '').replace(')', '')

        error_element.set('correct', fixed_correction)

        if att_list is not None:
            error_element.set('errorinfo', att_list)

        return error_element
