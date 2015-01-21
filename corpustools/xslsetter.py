# -*- coding:utf-8 -*-

from __future__ import unicode_literals

import os
import sys

import lxml.etree as etree

import util
import ccat

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
            filexsl = etree.parse(os.path.join(here, 'xslt/XSL-template.xsl'))
        else:
            filexsl = etree.parse(filename)

        self.tree = self.make_tree(filexsl)

    def make_tree(self, filexsl):
        preprocessXsl = etree.parse(os.path.join(here,
                                                 'xslt/preprocxsl.xsl'))
        common_xsl_path = os.path.join(
            here, 'xslt/common.xsl').replace(' ', '%20')
        preprocessXslTransformer = etree.XSLT(preprocessXsl)

        return preprocessXslTransformer(
            filexsl,
            commonxsl=etree.XSLT.strparam(
                'file://{}'.format(common_xsl_path)))

    def _get_variable_elt(self, key):
        return self.tree.getroot().find(
            "{{http://www.w3.org/1999/XSL/Transform}}"
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
            return { p.attrib[self.lang_key]: p.attrib["location"].strip("'")
                     for p in elts
                     if p.attrib["location"].strip("'") != "" }

    def set_parallel_text(self, language, location):
        attrib = { self.lang_key: language,
                   "location" : location }
        parallels = self._get_variable_elt("parallels")
        if parallels is None:
            parallels = etree.Element("{http://www.w3.org/1999/XSL/Transform}variable",
                                      name="parallels")
            parallels.text, parallels.tail = "\n", "\n\n"
            self.tree.getroot().append(parallels)
        elt = parallels.find("parallel_text[@{}='{}']".format(self.lang_key, language))
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
            print 'cannot write', self.filename
            print e
            sys.exit(254)

    def get_xsl(self):
        return self.tree

    def get_transformer(self):
        try:
            transform = etree.XSLT(self.tree)
            return transform
        except etree.XSLTParseError as (e):
            logfile = open(self.filename.replace('.xsl', '') + '.log', 'w')

            logfile.write('Error at: {}\n'.format(str(ccat.lineno())))
            logfile.write('Invalid XSLT in {}\n'.format(self.filename))
            for entry in e.error_log:
                logfile.write('{}\n'.format(str(entry)))

            logfile.close()
            raise XsltException("Invalid XML in {}".format(
                self.filename))

