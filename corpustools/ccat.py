# -*- coding:utf-8 -*-

import inspect
def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

import io
import cStringIO

from lxml import etree
import os
import sys

class XMLPrinter:
    def __init__(self,
                 lang=None,
                 allP=False,
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
                 printFilename=False,
                 oneWordPerLine=False):

        self.p = True
        self.allP = allP

        if title or listitem or table:
            self.p = False

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
            self.errorFiltering = True
        else:
            self.errorFiltering = False

        self.typos = typos
        self.printFilename = printFilename
        if self.typos:
            self.oneWordPerLine = True
        else:
            self.oneWordPerLine = oneWordPerLine

        self.lang = lang
        self.outfile = sys.stdout

    def getLang(self):
        """
        Get the lang of the file
        """
        return self.eTree.getroot().attrib['{http://www.w3.org/XML/1998/namespace}lang']

    def getElementLanguage(self, element, parentlang):
        if element.get('{http://www.w3.org/XML/1998/namespace}lang') is None:
            return parentlang
        else:
            return element.get('{http://www.w3.org/XML/1998/namespace}lang')

    def collectNotInlineErrors(self, element, textlist):
        '''Add the formatted errors as strings to the textlist list
        '''
        errorString = self.errorNotInline(element)
        if errorString != '':
            textlist.append(errorString)

        for child in element:
            if self.visitErrorNotInline(child):
                self.collectNotInlineErrors(child, textlist)

        if not self.typos:
            if element.tail != None and element.tail.strip() != '':
                if not self.oneWordPerLine:
                    textlist.append(element.tail.strip())
                else:
                    textlist.append('\n'.join(element.tail.strip().split()))

    def errorNotInline(self, element):
        '''Collect and format element.text, element.tail and
        the attributes into the string text

        Also scan the children if there is no error filtering or
        if the element is filtered
        '''
        text = ''
        if not self.noforeign:
            if element.text is not None and element.text.strip() != '':
                text = element.text.strip()

            if not self.errorFiltering or self.includeThisError(element):
                for child in element:
                    if text != '':
                        text += ' '
                    text += child.get('correct')
                    if  child.tail is not None and child.tail.strip() != '':
                        text += ' ' + child.tail.strip()

            text += self.getErrorAttributes(dict(element.attrib))

        return text

    def getErrorAttributes(self, attributes):
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

            if self.printFilename:
                text += ', file: ' + os.path.basename(self.filename)

        elif self.printFilename:
            text += '\t#file: ' + os.path.basename(self.filename)

        return text

    def collectInlineErrors(self, element, textlist, parentlang):
        '''Add the "correct" element to the list textlist
        '''
        if element.get('correct') != None and not self.noforeign:
            textlist.append(element.get('correct'))

        self.getTail(element, textlist, parentlang)

    def collectPlainP(self, element, parentlang):
        textlist = []

        self.plainP(element, textlist, parentlang)

        if len(textlist) > 0:
            if not self.oneWordPerLine:
                self.outfile.write(' '.join(textlist).encode('utf8'))
                self.outfile.write(' ¶\n')
            else:
                self.outfile.write('\n'.join(textlist).encode('utf8'))
                self.outfile.write('\n')

    def getText(self, element, textlist, parentlang):
        '''Get the text part of an lxml element
        '''
        if element.text != None and element.text.strip() != '' and (self.lang == None or self.getElementLanguage(element, parentlang) == self.lang):
            if not self.oneWordPerLine:
                textlist.append(element.text.strip())
            else:
                textlist.append('\n'.join(element.text.strip().split()))

    def getTail(self, element, textlist, parentlang):
        '''Get the tail part of an lxml element
        '''
        if element.tail != None and element.tail.strip() != '' and (self.lang == None or parentlang == self.lang):
            if not self.oneWordPerLine:
                textlist.append(element.tail.strip())
            else:
                textlist.append('\n'.join(element.tail.strip().split()))

    def visitChildren(self, element, textlist, parentlang):
        for child in element:
            if self.visitErrorInline(child):
                self.collectInlineErrors(child, textlist, self.getElementLanguage(child, parentlang))
            elif self.visitErrorNotInline(child):
                self.collectNotInlineErrors(child, textlist)
            else:
                self.plainP(child, textlist, self.getElementLanguage(element, parentlang))

    def plainP(self, element, textlist, parentlang):
        if not self.typos:
            self.getText(element, textlist, parentlang)
        self.visitChildren(element, textlist, parentlang)
        if not self.typos:
            self.getTail(element, textlist, parentlang)

    def visitThisNode(self, element):
        '''Return True if the element should be visited
        '''
        return (
            self.allP or
            (
                self.p is True and (element.get('type') is None or element.get('type') == 'text')
            ) or (
                self.title is True and element.get('type') == 'title'
            ) or (
                self.listitem is True and element.get('type') == 'listitem'
            ) or (
                self.table is True and element.get('type') == 'tablecell'
            )
        )

    def visitErrorNotInline(self, element):
        return (
            element.tag.startswith('error') and self.oneWordPerLine and not self.errorFiltering or
            self.includeThisError(element)
            )

    def visitErrorInline(self, element):
        return (
                element.tag.startswith('error') and not self.oneWordPerLine and
                (self.correction or self.includeThisError(element))
            )

    def includeThisError(self, element):
        return self.errorFiltering and (
                (element.tag == 'error' and self.error) or \
                (element.tag == 'errorort' and self.errorort) or \
                (element.tag == 'errorortreal' and self.errorortreal) or \
                (element.tag == 'errormorphsyn' and self.errormorphsyn) or \
                (element.tag == 'errorsyn' and self.errorsyn) or \
                (element.tag == 'errorlex' and self.errorlex) or \
                (element.tag == 'errorlang' and self.errorlang) or \
                (element.tag == 'errorlang' and self.noforeign)
            )

    def setOutfile(self, outfile):
        '''outfile must either be a string containing the path to the file
        where the result should be written, or an object that supports the
        write method
        '''
        if type(outfile) != file:
            if isinstance(outfile, (str, unicode)):
                self.outfile = open(outfile, 'w')
            else:
                self.outfile = outfile

    def processFile(self, filename):
        if os.path.exists(filename):
            self.eTree = etree.parse(filename)
        self.filename = filename

        for p in self.eTree.findall('.//p'):
            if self.visitThisNode(p):
                self.collectPlainP(p, self.getLang())
