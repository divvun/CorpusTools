# -*- coding:utf-8 -*-

#
#   This file contains routines to change names of corpus files
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
#   Copyright 2013-2014 Børre Gaup <borre.gaup@uit.no>
#

import os
import sys
import unidecode
import subprocess
import platform

import lxml.etree as etree


class NameChanger:
    """Class to change names of corpus files.
    Will also take care of changing info in meta data of parallel files.
    """

    def __init__(self, oldname):
        """Find the directory the oldname is in.
        self.oldname is the basename of oldname.
        self.newname is the basename of oldname, in lowercase and
        with some characters replaced.
        """
        self.oldname = oldname

        self.newname = self.change_to_ascii(self.oldname)

    def change_to_ascii(self, oldname):
        """Downcase all chars in oldname, replace some chars
        oldname is a unicode string
        """
        chars = {u'+':'_', u' ': u'_', u'(': u'_', u')': u'_', u"'": u'_', u'–': u'-', u'?': u'_', u',': u'_', u'!': u'_'}

        newname = unicode(unidecode.unidecode(oldname)).lower()

        for key, value in chars.items():
            if key in newname:
                newname = newname.replace(key, value)
        while '__' in newname:
            newname = newname.replace('__', '_')

        return newname

    def move_file(self, fromname, toname):
        """Change name of file from fromname to toname"""
        if not os.path.exists(os.path.dirname(nc.newname)):
            os.makedirs(os.path.dirname(nc.newname))
        if nc.newname != nc.oldname:
            subprocess.call(['git', 'mv', nc.oldname, nc.newname])

    def change_name(self):
        """Change the name of the original file and it's metadata file
        Update the name in parallel files
        Also move the other files that's connected to the original file
        """
        if self.oldname != self.newname:
            self.move_origfile()
            self.move_xslfile()
            self.update_name_in_parallel_files()
            self.move_prestable_converted()
            self.move_prestable_toktmx()
            self.move_prestable_tmx()

        pass

    def move_origfile(self):
        """Change the name of the original file
        using the routines of a given repository tool
        """
        fromname = os.path.join(self.dirname, self.oldname)
        toname = os.path.join(self.dirname, self.newname)

        self.move_file(fromname, toname)

        pass

    def move_xslfile(self):
        """Change the name of an xsl file using the
        routines of a given repository tool
        """
        fromname = os.path.join(self.dirname, self.oldname + '.xsl')
        toname = os.path.join(self.dirname, self.newname + '.xsl')

        self.move_file(fromname, toname)

        pass

    def open_xslfile(self, xslfile):
        """Open xslfile, return the tree"""
        try:
            tree = etree.parse(xslfile)
        except Exception, inst:
            print "Unexpected error opening %s: %s" % (xslfile, inst)
            sys.exit(254)

        return tree

    def set_newname(self, mainlang, paralang, paraname):
        """
        """
        paradir = self.dirname.replace(mainlang, paralang)
        parafile = os.path.join(paradir, paraname + '.xsl')
        if os.path.exists(parafile):
            paratree = self.open_xslfile()
            pararoot = paratree.getroot()

            pararoot.find(".//*[@name='para_" + mainlang + "']").set('select', "'" + self.newname + "'")

            paratree.write(parafile, encoding = 'utf8', xml_declaration = True)

        pass

    def update_name_in_parallel_files(self):
        """Open the .xsl file belonging to the file we are changing names of. Look for parallel files.
        Open the xsl files of these parallel files and change the name of this
        parallel from the old to the new one
        """
        xslfile = os.path.join(self.dirname, self.newname + '.xsl')
        if os.path.exists(xslfile):
            xsltree = self.open_xslfile(xslfile)
            xslroot = xsltree.getroot()

            mainlang = xslroot.find(".//*[@name='mainlang']").get('select').replace("'", "")

            if mainlang != "":
                for element in xslroot.iter():
                    if element.attrib.get('name') and \
                    'para_' in element.attrib.get('name') and \
                    element.attrib.get('select') != "''":
                        paralang = element.attrib.get('name').replace('para_', '')
                        paraname = element.attrib.get('select').replace("'", "")
                        self.set_newname(mainlang, paralang, paraname)

    def move_prestable_converted(self):
        """Move the file in prestable/converted from the old to the new name
        """
        dirname = self.dirname.replace('/orig/', '/prestable/converted/')
        fromname = os.path.join(dirname, self.oldname + '.xml')
        toname = os.path.join(dirname, self.newname + '.xml')

        self.move_file(fromname, toname)

    def move_prestable_toktmx(self):
        """Move the file in prestable/toktmx from the old to the new name
        """
        for suggestion in ['/prestable/toktmx/sme2nob/', '/prestable/toktmx/nob2sme/']:
            dirname = self.dirname.replace('/orig/', suggestion)
            fromname = os.path.join(dirname, self.oldname + '.toktmx')
            if os.path.exists(fromname):
                toname = os.path.join(dirname, self.newname + '.toktmx')
                self.move_file(fromname, toname)

    def move_prestable_tmx(self):
        """Move the file in prestable/tmx from the old to the new name
        """
        for suggestion in ['/prestable/tmx/sme2nob/', '/prestable/tmx/nob2sme/']:
            dirname = self.dirname.replace('/orig/', suggestion)
            fromname = os.path.join(dirname, self.oldname + '.tmx')
            if os.path.exists(fromname):
                toname = os.path.join(dirname, self.newname + '.tmx')
                self.move_file(fromname, toname)

def main():
    for root, dirs, files in os.walk(sys.argv[1]):
        for file_ in files:
            if platform.system != 'Windows':
                nc = NameChanger(os.path.join(root, file_))
            else:
                nc = NameChanger(os.path.join(root, file_).decode('utf-8'))

            nc.move_file(nc.oldname, nc.newname)
