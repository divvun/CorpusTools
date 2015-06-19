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
#   Copyright 2013-2015 Børre Gaup <borre.gaup@uit.no>
#

from __future__ import print_function

import argparse
import os
import subprocess
import sys

import unidecode
import urllib

import corpustools.argparse_version as argparse_version
import corpustools.util as util
import corpustools.xslsetter as xslsetter


class NameChangerBase(object):
    """Class to change names of corpus files.

    Will also take care of changing info in meta data of parallel files.
    """

    def __init__(self, oldname):
        """Find the directory the oldname is in.

        self.oldname is the basename of oldname.
        self.newname is the basename of oldname, in lowercase and
        with some characters replaced.
        """
        self.old_filename = os.path.basename(oldname)
        self.old_dirname = os.path.dirname(oldname)

        self.new_filename = self.change_to_ascii()

    def change_to_ascii(self):
        """Downcase all chars in self.oldname, replace some chars"""
        unwanted_chars = {
            u'+': '_', u' ': u'_', u'(': u'_', u')': u'_', u"'": u'_',
            u'–': u'-', u'?': u'_', u',': u'_', u'!': u'_', u',': u'_',
            u'<': u'_', u'>': u'_', u'"': u'_', u'&': u'_', u';': u'_',
            u'&': u'_', u'#': u'_', u'=': u'-', u'\\': u'_', u'|': u'_',
            u'$': u'_',
        }

        # unidecode.unidecode makes ascii only
        newname = unicode(
            unidecode.unidecode(
                urllib.unquote(
                    self.old_filename
                ))).lower()

        newname = util.replace_all(unwanted_chars.items(), newname)

        while '__' in newname:
            newname = newname.replace('__', '_')

        return newname


class CorpusNameFixer(NameChangerBase):
    def __init__(self, oldname):
        super(CorpusNameFixer, self).__init__(oldname)

    def change_name(self):
        """Change the name of the original file and it's metadata file

        Update the name in parallel files
        Also move the other files that's connected to the original file
        """
        if self.old_filename != self.new_filename:
            fullname = os.path.join(self.old_dirname, self.new_filename)
            if not os.path.exists(fullname):
                self.move_origfile()
                self.move_xslfile()
                self.update_name_in_parallel_files()
                self.move_prestable_converted()
                self.move_prestable_toktmx()
                self.move_prestable_tmx()
            else:
                print('\nError renaming {}'
                    '\n{} exists\n'.format(
                        os.path.join(self.old_dirname, self.old_filename),
                        fullname), file=sys.stderr)

    def move_file(self, oldname, newname):
        """Change name of file from fromname to toname"""
        if not os.path.exists(os.path.dirname(newname)):
            os.makedirs(os.path.dirname(newname))
        if newname != oldname:
            subprocess.call(['git', 'mv', oldname, newname])

    def move_origfile(self):
        """Change the name of the original file."""
        fromname = os.path.join(self.old_dirname, self.old_filename)
        toname = os.path.join(self.old_dirname, self.new_filename)

        self.move_file(fromname, toname)

    def move_xslfile(self):
        """Change the name of the metadata file."""
        fromname = os.path.join(
            self.old_dirname,
            u'{}.xsl'.format(self.old_filename))
        toname = os.path.join(self.old_dirname,
                              '{}.xsl'.format(self.new_filename))

        if os.path.exists(fromname):
            self.move_file(fromname, toname)

    def set_para_backreference(self, mainlang, paralang, paraname):
        """Replace oldname with newname in parallell file reference."""
        paradir = self.old_dirname.replace("/"+mainlang+"/",
                                           "/"+paralang+"/")
        parafile = os.path.join(paradir, u'{}.xsl'.format(paraname))
        if os.path.exists(parafile):
            paradata = xslsetter.MetadataHandler(parafile)
            paradata.set_parallel_text(mainlang, self.new_filename)
            paradata.write_file()

    def update_name_in_parallel_files(self):
        """Open the .xsl file belonging to the file we are changing names of.

        Look for parallel files.
        Open the xsl files of these parallel files and change the name of this
        parallel from the old to the new one
        """
        xslfile = os.path.join(self.old_dirname,
                               '{}.xsl'.format(self.new_filename))
        if os.path.exists(xslfile):
            metadata = xslsetter.MetadataHandler(xslfile)
            xslroot = metadata.tree.getroot()

            mainlang = xslroot.find(".//*[@name='mainlang']").get(
                'select').strip("'")

            if mainlang != "":
                parallels = metadata.get_parallel_texts()
                for paralang, paraname in parallels.iteritems():
                    self.set_para_backreference(mainlang, paralang, paraname)

    def move_prestable_converted(self):
        """Move the file in prestable/converted from the old to the new name"""
        dirname = self.old_dirname.replace('/orig/', '/prestable/converted/')
        fromname = os.path.join(dirname, u'{}.xml'.format(self.old_filename))
        toname = os.path.join(dirname, '{}.xml'.format(self.new_filename))

        if os.path.exists(fromname):
            self.move_file(fromname, toname)

    def move_prestable_toktmx(self):
        """Move the file in prestable/toktmx from the old to the new name"""
        for suggestion in ['/prestable/toktmx/sme2nob/',
                           '/prestable/toktmx/nob2sme/']:
            dirname = self.old_dirname.replace('/orig/', suggestion)
            fromname = os.path.join(dirname, u'{}.toktmx'.format(
                self.old_filename))
            if os.path.exists(fromname):
                toname = os.path.join(dirname, '{}.toktmx'.format(
                    self.new_filename))
                self.move_file(fromname, toname)

    def move_prestable_tmx(self):
        """Move the file in prestable/tmx from the old to the new name"""
        for suggestion in ['/prestable/tmx/sme2nob/',
                           '/prestable/tmx/nob2sme/']:
            dirname = self.old_dirname.replace('/orig/', suggestion)
            fromname = os.path.join(dirname, u'{}.tmx'.format(
                self.old_filename))
            if os.path.exists(fromname):
                toname = os.path.join(dirname, '{}.tmx'.format(
                    self.new_filename))
                self.move_file(fromname, toname)


def parse_args():
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Program to automatically rename corpus files in the \
        given directory. It downcases the filenames and removes unwanted \
        characters.')

    parser.add_argument('directory',
                        help='The directory where filenames should be \
                        renamed')

    return parser.parse_args()


def main():
    args = parse_args()

    for root, dirs, files in os.walk(args.directory):
        for file_ in files:
            if not file_.endswith('.xsl'):
                nc = CorpusNameFixer(
                    util.name_to_unicode(os.path.join(root, file_)))
                nc.change_name()
