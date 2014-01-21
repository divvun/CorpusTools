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
        self.types = { u"$": u"errorort", u"¢": "errorortreal", u"€": "errorlex", u"£": "errormorphsyn", u"¥": "errorsyn", u"§": "error", u"∞": "errorlang"}
        self.errorRegex = re.compile(u'(?P<error>\([^\(]*\)$|\w+$|\w+[-\':\]]\w+$|\w+[-\'\]\./]$|\d+’\w+$|\d+%:\w+$|”\w+”$)',re.UNICODE)
        self.correctionRegex = re.compile(u'(?P<correction>[$€£¥§¢∞]\([^\)]*\)|[$€£¥§¢∞]\S+)(?P<tail>.*)',re.UNICODE)
        pass

    def addErrorMarkup(self, element):
        self.reallyAddErrorMarkup(element)
        for elt in element:
            self.addErrorMarkup(elt)

    def reallyAddErrorMarkup(self, element):
        '''
        Search for errormarkup in the text and tail of an etree.Element
        If found, replace errormarkuped text with xml

        To see examples of what newContent consists of, have a look at the
        testErrorParser* methods

        '''
        self.fixText(element)
        self.fixTail(element)

        pass

    def fixText(self, element):
        '''Replace the text of an element with errormarkup if possible
        '''
        newContent = self.errorParser(element.text)

        if newContent:
            element.text = None

            if isinstance(newContent[0], basestring):
                element.text = newContent[0]
                newContent = newContent[1:]

            newPos = 0
            for part in newContent:
                element.insert(newPos, part)
                newPos += 1

    def fixTail(self, element):
        '''Replace the tail of an element with errormarkup if possible
        '''
        newContent = self.errorParser(element.tail)

        if newContent:
            element.tail = None

            if isinstance(newContent[0], basestring):
                element.tail = newContent[0]
                newContent = newContent[1:]

            newPos = element.getparent().index(element) + 1
            for part in newContent:
                element.getparent().insert(newPos, part)
                newPos += 1

    def errorParser(self, text):
        '''
        Parse errormarkup found in text. If any markup is found, return a list of elements in elements

        result -- contains a list of non-correction/correction parts

        The algorithm for parsing the error is:
        Find a correction in the result list.

        If the preceding element in result contains a simple error and is not a correction
        make an errorElement, append it to elements

        If the preceding element in result is not a simple error, it is part of
        nested markup.

        '''

        if text:
            text = text.replace('\n', ' ')
            result = self.processText(text)

            if len(result) > 1:
                #print text
                #print result
                elements = []
                # This means that we are inside an error markup
                # Start with the two first elements
                # The first contains an error, the second one is a correction

                for x in range(0, len(result)):
                    if self.isCorrection(result[x]):
                        if not self.isCorrection(result[x-1]) and self.isError(result[x-1]):

                            self.addSimpleError(elements, result[x-1], result[x])

                        else:

                            self.addNestedError(elements, result[x-1], result[x])

                if not self.isCorrection(result[-1]):
                    elements[-1].tail = result[-1]

                return elements

        pass

    def addSimpleError(self, elements, errorstring, correctionstring):
        '''Make an error element, append it to elements

        elements -- a list of errorElements
        errorstring -- a string containing a text part and an errormarkup
        error
        correctionstring -- a string containing an errormarkup correction

        '''
        (head, error) = self.processHead(errorstring)
        if len(elements) == 0:
            if head != '':
                elements.append(head)
        else:
            elements[-1].tail = head

        errorElement = self.getError(error, correctionstring)

        elements.append(errorElement)

    def addNestedError(self, elements, errorstring, correctionstring):
        '''Make errorElement, append it to elements

        elements -- a list of errorElements
        errorstring -- contains either a correction or string ending with
        a right parenthesis )
        correctionstring -- a string containing an errormarkup correction

        The algorithm:
        At least the last element in elements will be engulfed in errorElement
        and replaced by errorElement in elements

        Remove the last element, use it as the innerElement when making
        errorElement

        If the errorstring is not a correction, then it ends in a ).

        Extract the string from the last element of elements.
        If a ( is found, set the part before ( to be the tail of the last
        element of elements. Set the part after ( to be the text of errorElement,
        append errorElement to elements.

        If a ( is not found, insert the last element of elements as first child
        of errorElement, continue searching

        '''
        #print u'«' + errorstring + u'»', u'«' + correctionstring + u'»'
        try:
            innerElement = elements[-1]
        except IndexError:
            print '\n', self._filename
            print "Cannot handle:\n"
            print errorstring + correctionstring
            print "This is either an error in the markup or an error in the errormarkup conversion code"
            print "If the markup is correct, send a report about this error to borre.gaup@uit.no"

        elements.remove(elements[-1])
        if not self.isCorrection(errorstring):
            innerElement.tail = errorstring[:-1]
        errorElement = self.getError(innerElement, correctionstring)


        if self.isCorrection(errorstring):
            elements.append(errorElement)
        else:
            parenthesisFound = False

            while not parenthesisFound:
                text = self.getText(elements[-1])

                x = text.rfind('(')
                if x > -1:
                    parenthesisFound = True

                    errorElement.text = text[x+1:]
                    if isinstance(elements[-1], etree._Element):
                        elements[-1].tail = text[:x]
                    else:
                        elements[-1] = text[:x]
                    elements.append(errorElement)

                else:
                    innerElement = elements[-1]
                    elements.remove(elements[-1])
                    try:
                        errorElement.insert(0, innerElement)
                    except TypeError as e:
                        print '\n', self._filename
                        print str(e)
                        print u"The program expected an error element, but found a string:\n«" + innerElement + u"»"
                        print u"There is either an error in errormarkup close to this sentence"
                        print u"or the program cannot evaluate a correct errormarkup."
                        print u"If the errormarkup is correct, please report about the error to borre.gaup@uit.no"


    def getText(self, element):
        text = None
        if isinstance(element, etree._Element):
            text = element.tail
        else:
            text = element

        return text

    def isCorrection(self, expression):
        return self.correctionRegex.search(expression)

    def processText(self, text):
        '''Divide the text in to a list consisting of alternate
        non-correctionstring/correctionstrings
        '''
        result = []

        m = self.correctionRegex.search(text)
        while m:
            head = self.correctionRegex.sub('', text)
            if not (head != '' and head[-1] == " "):
                if head != '':
                    result.append(head)
                result.append(m.group('correction'))
            text = m.group('tail')
            m = self.correctionRegex.search(text)

        if text != '':
            result.append(text)

        return result

    def processHead(self, text):
        '''Divide text into text/error parts
        '''
        m = self.errorRegex.search(text)
        text = self.errorRegex.sub('', text)

        return (text, m.group('error'))

    def isError(self, text):
        return self.errorRegex.search(text)

    def getError(self, error, correction):
        '''Make an errorElement

        error -- is either a string or an etree.Element
        correction -- is a correctionstring

        '''
        (fixedCorrection, extAtt, attList) = self.lookForExtendedAttributes(correction[1:].replace('(', '').replace(')', ''))

        elementName = self.getElementName(correction[0])

        errorElement = self.makeErrorElement(error, fixedCorrection, elementName, attList)

        return errorElement

    def lookForExtendedAttributes(self, correction):
        '''Extract attributes and correction from a correctionstring
        '''
        extAtt = False
        attList = None
        if '|' in correction:
            extAtt = True
            try:
                (attList, correction) = correction.split('|')
            except ValueError as e:
                print '\n', self._filename
                print str(e)
                print u"too many | characters inside the correction. «" + correction + u"»"
                print u"Have you remembered to encase the error inside parenthesis, e.g. (vowlat,a-á|servodatvuogádat)?"
                print u"If the errormarkup is correct, send a report about this error to borre.gaup@uit.no"

        return (correction, extAtt, attList)

    def getElementName(self, separator):
        return self.types[separator]

    def makeErrorElement(self, error, fixedCorrection, elementName, attList):
        errorElement = etree.Element(elementName)
        if isinstance(error, etree._Element):
            errorElement.append(error)
        else:
            errorElement.text = error.replace('(', '').replace(')', '')

        errorElement.set('correct', fixedCorrection)

        if attList != None:
            errorElement.set('errorinfo', attList)

        return errorElement
