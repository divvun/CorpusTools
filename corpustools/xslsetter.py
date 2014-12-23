# -*- coding:utf-8 -*-
import os
import sys

import lxml.etree as etree
from pkg_resources import resource_filename


class MetadataHandler(object):
    '''Class to handle metadata in .xsl files
    '''

    def __init__(self, filename):
        self.filename = filename

        if not os.path.exists(filename):
            preprocessXsl = etree.parse(
                resource_filename(__name__, 'xslt/preprocxsl.xsl'))
            preprocessXslTransformer = etree.XSLT(preprocessXsl)
            filexsl = etree.parse(
                resource_filename(__name__, 'xslt/XSL-template.xsl'))
            self.tree = preprocessXslTransformer(
                filexsl,
                commonxsl=etree.XSLT.strparam(
                    'file://' + resource_filename(__name__,
                                                  'xslt/common.xsl')))
        else:
            self.tree = etree.parse(filename)

    def set_variable(self, key, value):
        try:
            self.tree.getroot().find(
                "{http://www.w3.org/1999/XSL/Transform}variable[@name='" +
                key + "']").attrib['select'] = "'" + value + "'"
        except AttributeError as e:
            print >>sys.stderr, 'tried to update', key, 'with value', value
            raise UserWarning

    def get_variable(self, key):
        return self.tree.getroot().find(
            "{http://www.w3.org/1999/XSL/Transform}variable[@name='" +
            key + "']").attrib['select'].replace("'", "")

    def write_file(self):
        try:
            self.tree.write(self.filename, encoding="utf-8",
                            xml_declaration=True)
        except IOError:
            print 'cannot write', self.filename
            sys.exit(254)
