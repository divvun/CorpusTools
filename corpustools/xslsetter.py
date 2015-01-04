# -*- coding:utf-8 -*-
import os
import sys

import lxml.etree as etree


here = os.path.dirname(__file__)


class MetadataHandler(object):
    '''Class to handle metadata in .xsl files
    '''

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

    def set_variable(self, key, value):
        try:
            self.tree.getroot().find(
                "{http://www.w3.org/1999/XSL/Transform}variable[@name='%s']" %
                key).attrib['select'] = "'%s'" % value
        except AttributeError as e:
            print >>sys.stderr, ('Tried to update %s with value %s\n'
                                 'Error was %s' %
                                 (key, value, str(e)))
            raise UserWarning

    def get_variable(self, key):
        return self.tree.getroot().find(
            "{http://www.w3.org/1999/XSL/Transform}variable[@name='%s']" %
            key).attrib['select'].replace("'", "")

    def write_file(self):
        try:
            self.tree.write(self.filename, encoding="utf-8",
                            xml_declaration=True)
        except IOError:
            print 'cannot write', self.filename
            sys.exit(254)
