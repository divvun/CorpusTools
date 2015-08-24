# -*- coding:utf-8 -*-

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
#   Copyright 2013-2015 Børre Gaup <borre.gaup@uit.no>
#   Copyright 2014-2015 Kevin Brubeck Unhammer <unhammer@fsfe.org>
#

from __future__ import print_function
from __future__ import unicode_literals

import lxml.etree as etree
import os
import sys


import util

here = os.path.dirname(__file__)


class XsltException(Exception):
    pass


class MetadataHandler(object):

    '''Class to handle metadata in .xsl files

    To convert the intermediate xml to a fullfledged  giellatekno document
    a combination of three xsl files + the intermediate files is needed
    This class makes the xsl file
    '''
    lang_key = "{http://www.w3.org/XML/1998/namespace}lang"

    def __init__(self, filename, create=False):
        self.filename = filename

        if not os.path.exists(filename):
            if not create:
                raise util.ArgumentError("{} does not exist!".format(filename))
            self.tree = etree.parse(os.path.join(here,
                                                 'xslt/XSL-template.xsl'))
        else:
            try:
                self.tree = etree.parse(filename)
            except etree.XMLSyntaxError as e:
                raise XsltException('Syntax error in {}:\n{}'.format(
                    self.filename, e))

    def _get_variable_elt(self, key):
        return self.tree.getroot().find(
            "{{http://www.w3.org/1999/XSL/Transform}}"
            "variable[@name='{}']".format(key))

    def set_variable(self, key, value):
        try:
            variable = self._get_variable_elt(key)
            variable.attrib['select'] = "'{}'".format(value)
        except AttributeError as e:
            print('Tried to update {} with value {}\n'
                  'Error was {}'.format(key, value, str(e)).encode('utf-8'),
                  file=sys.stderr)
            raise UserWarning

    def get_variable(self, key):
        variable = self._get_variable_elt(key)
        if variable is not None:
            value = variable.attrib['select']
            if value is not None:
                return value.replace("'", "")
        return None

    def get_parallel_texts(self):
        parallels = self._get_variable_elt("parallels")
        if parallels is None:
            return {}
        else:
            elts = parallels.findall("parallel_text")
            return {p.attrib[self.lang_key]: p.attrib["location"].strip("'")
                    for p in elts
                    if p.attrib["location"].strip("'") != ""}

    def set_parallel_text(self, language, location):
        attrib = {self.lang_key: language,
                  "location": location}
        parallels = self._get_variable_elt("parallels")
        if parallels is None:
            parallels = etree.Element(
                "{http://www.w3.org/1999/XSL/Transform}variable",
                name="parallels")
            parallels.text, parallels.tail = "\n", "\n\n"
            self.tree.getroot().append(parallels)
        elt = parallels.find("parallel_text[@{}='{}']".format(self.lang_key,
                                                              language))
        if elt is not None:
            elt.attrib.update(attrib)
        else:
            elt = etree.Element("parallel_text", attrib=attrib)
            elt.tail = "\n"
            parallels.append(elt)

    def write_file(self):
        try:
            with open(self.filename, 'w') as f:
                f.write(etree.tostring(self.tree,
                                       encoding="utf-8",
                                       xml_declaration=True))
        except IOError as e:
            print('cannot write', self.filename)
            print(e)
            sys.exit(254)
