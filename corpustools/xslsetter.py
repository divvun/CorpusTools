# -*- coding:utf-8 -*-
import os

import lxml.etree as etree
from pkg_resources import resource_string, resource_filename
import ccat

class MetadataHandler(object):
    '''Class to handle metadata in .xsl files
    '''

    def __init__(self, filename):
        if not os.path.exists(filename):
            self.tree = etree.parse(
                resource_filename(__name__, 'xslt/XSL-template.xsl'))
        else:
            self.tree = etree.parse(filename)
        self.filename = filename

    def set_variable(self, key, value):
        self.tree.getroot().find(
            "{http://www.w3.org/1999/XSL/Transform}variable[@name='" \
                + key + "']").attrib['select'] = "'" + value + "'"

    def get_variable(self, key):
        return self.tree.getroot().find(
            "{http://www.w3.org/1999/XSL/Transform}variable[@name='" \
                + key + "']").attrib['select'].replace("'", "")

    def write_file(self):
        try:
            self.tree.write(self.filename, encoding="utf-8", xml_declaration=True)
        except IOError:
            print 'cannot write', xsl_filename
            sys.exit(254)
