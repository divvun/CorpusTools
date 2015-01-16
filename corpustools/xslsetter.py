# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import os
import sys

import lxml.etree as etree


here = os.path.dirname(__file__)


class MetadataHandler(object):
    '''Class to handle metadata in .xsl files
    '''

    lang_key = "{http://www.w3.org/XML/1998/namespace}lang"

    def __init__(self, filename):
        self.filename = filename

        if not os.path.exists(filename):
            preprocessXsl = etree.parse(os.path.join(here,
                                                     'xslt/preprocxsl.xsl'))
            preprocessXslTransformer = etree.XSLT(preprocessXsl)
            filexsl = etree.parse(os.path.join(here, 'xslt/XSL-template.xsl'))
            self.tree = preprocessXslTransformer(
                filexsl,
                commonxsl=etree.XSLT.strparam(
                    'file://' + os.path.join(here, 'xslt/common.xsl')))
        else:
            self.tree = etree.parse(filename)

    def _get_variable_elt(self, key):
        return self.tree.getroot().find(
            "{http://www.w3.org/1999/XSL/Transform}"
            "variable[@name='{}']".format(key))

    def set_variable(self, key, value):
        try:
            variable = self._get_variable_elt(key)
            variable.attrib['select'] = "'{}'".format(value)
        except AttributeError as e:
            print >>sys.stderr, (
                'Tried to update {} with value {}\n'
                'Error was {}'.format(key, value, str(e))).encode('utf-8')
            raise UserWarning

    def get_variable(self, key):
        variable = self._get_variable_elt(key)
        return variable.attrib['select'].replace("'", "")


    def get_parallel_texts(self):
        parallels = self._get_variable_elt("parallels")
        elts = parallels.findall("parallel_rtext")
        return { p.attrib[self.lang_key]: p.attrib["location"].strip("'")
                 for p in elts }

    def set_parallel_text(self, language, location):
        attrib = { self.lang_key: language,
                   "location" : location }
        parallels = self._get_variable_elt("parallels")
        elt = parallels.find("parallel_text[@{}='{}']".format(
            self.lang_key, language))
        if elt is not None:
            elt.attrib = attrib
        else:
            parallels.append( etree.Element("parallel_text", attrib=attrib) )


    def write_file(self):
        try:
            self.tree.write(self.filename, encoding="utf-8",
                            xml_declaration=True)
        except IOError:
            print 'cannot write', self.filename
            sys.exit(254)
