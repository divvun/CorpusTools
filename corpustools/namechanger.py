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


'''Change the names of files within a repository

Normalise a file name: Replace non-ascii char with ascii ones and remove
unwanted characters.

When normalising a file name containing unwanted characters or renaming it
for other reasons:
* change the name of original file
* change the name of metadata file
* change the name of prestable/converted file
* change the name of prestable/toktmx file
* change the name of prestable/tmx file
* change the reference to the file name in the parallel files' metadata

When moving a file from one subdirectory to another:
* move the original file
* move the metadata file
* move the prestable/converted file
* move the prestable/toktmx file
* move the prestable/tmx file
* move the parallel files the same way the original file has been moved.

When moving a file to a new genre:
* the subdirectory move operations +
* change the genre reference in the metadata files

When moving a file to a new language:
* change the language of the file in the parallel files' metadata

When doing these operations, detect name clashes for the original files.

If a name clash is found, check if the files are duplicates. If they are
duplicates, raise an exception, otherwise suggest a new name.
'''
from __future__ import print_function

import argparse
import os

from collections import namedtuple
import hashlib
import unidecode
import urllib

from corpustools import argparse_version
from corpustools import util
from corpustools import versioncontrol
from corpustools import xslsetter


class NamechangerException(Exception):
    pass


def compute_hexdigest(path, blocksize=65536):
    '''Compute the hexdigest of the file in path'''
    with open(path, 'rb') as afile:
        hasher = hashlib.md5()
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)

        return hasher.hexdigest()


def normalise_filename(filename):
    """Normalise filename to ascii only

    Downcase filename, replace non-ascii characters with ascii ones and
    remove or replace unwanted characters.

    Args:
        filename: is a unicode string

    Returns:
        a downcased string containing only ascii chars
    """
    if type(filename) is not unicode:
        raise NamechangerException('{} is not a unicode string'.format(
            filename))

    if os.sep in filename:
        raise NamechangerException(
            'Invalid filename {}.\n'
            'Filename is not allowed to contain {}'.format(filename,
                                                           os.sep))

    unwanted_chars = {
        u'+': '_', u' ': u'_', u'(': u'_', u')': u'_', u"'": u'_',
        u'–': u'-', u'?': u'_', u',': u'_', u'!': u'_', u',': u'_',
        u'<': u'_', u'>': u'_', u'"': u'_', u'&': u'_', u';': u'_',
        u'&': u'_', u'#': u'_', u'\\': u'_', u'|': u'_', u'$': u'_',
    }

    # unidecode.unidecode makes ascii only
    # urllib.unquote replaces %xx escapes by their single-character equivalent.
    newname = unicode(
        unidecode.unidecode(
            urllib.unquote(
                filename
            ))).lower()

    newname = util.replace_all(unwanted_chars.items(), newname)

    while u'__' in newname:
        newname = newname.replace(u'__', u'_')

    return newname


def are_duplicates(oldpath, newpath):
    '''Check if oldpath and newpath are duplicates of each other.

    Args:
        oldpath (unicode): old path of the file
        newpath (unicode): the wanted, new path of the file

    Returns:
        a boolean indicating if the two files are duplicates
    '''
    return (os.path.isfile(newpath) and
            compute_hexdigest(oldpath) == compute_hexdigest(
                newpath))


def compute_new_basename(oldpath, wanted_path):
    '''Compute the new path

    Args:
        oldpath (unicode): path to the old file
        wanted_path (unicode): the path that one wants to move the file to

    Returns:
        a unicode string pointing to the new path
    '''
    wanted_basename = os.path.basename(wanted_path)
    new_basename = os.path.basename(wanted_path)
    newpath = os.path.join(os.path.dirname(wanted_path), new_basename)
    n = 1

    while os.path.exists(newpath):
        if are_duplicates(oldpath, newpath):
            raise UserWarning('{} and {} are duplicates. '
                              'Please remove one of them'.format(oldpath,
                                                                 newpath))
        else:
            if u'.' in wanted_basename:
                dot = wanted_basename.rfind('.')
                extension = wanted_basename[dot:]
                pre_extension = wanted_basename[:dot]
                new_basename = pre_extension + u'_' + unicode(n) + extension
            else:
                new_basename = wanted_basename + unicode(n)
            newpath = os.path.join(os.path.dirname(wanted_path), new_basename)
            n += 1

    return newpath


PathPair = namedtuple('PathPair', 'oldpath newpath')


def normaliser():
    '''Normalise the filenames in the corpuses'''
    for corpus in [os.getenv('GTFREE'), os.getenv('GTBOUND')]:
        for root, dirs, files in os.walk(os.path.join(corpus, 'orig')):
            for f in files:
                if not f.endswith('.xsl'):
                    cfmu = CorpusFilesetMoverAndUpdater(
                        os.path.join(root, f).decode('utf8'),
                        os.path.join(root, f).decode('utf8'))
                    filepair = cfmu.mc.filepairs[0]
                    if filepair.oldpath != filepair.newpath:
                        cfmu.move_files()
                        cfmu.update_own_metadata()
                        cfmu.update_parallel_files_metadata()

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
    normaliser()
    #args = parse_args()

    #for root, dirs, files in os.walk(args.directory):
        #for file_ in files:
            #if not file_.endswith('.xsl'):
                #nc = CorpusNameFixer(
                    #util.name_to_unicode(os.path.join(root, file_)))
                #nc.change_name()


class MovepairComputer(object):
    def __init__(self):
        self.filepairs = []

    def compute_movepairs(self, oldpath, newpath):
        normalisedpath = os.path.join(
            os.path.dirname(newpath),
            normalise_filename(os.path.basename(newpath)))

        non_dupe_path = compute_new_basename(oldpath, normalisedpath)

        self.filepairs.append(PathPair(oldpath, non_dupe_path))

    def compute_parallel_movepairs(self, oldpath, newpath):
        old_components = util.split_path(oldpath)
        new_components = util.split_path(newpath)

        if (old_components.genre != new_components.genre or
                old_components.subdirs != new_components.subdirs):
            metadatafile = xslsetter.MetadataHandler(oldpath + '.xsl')
            for lang, parallel in metadatafile.get_parallel_texts().items():
                oldparellelpath = u'/'.join((
                    old_components.root,
                    old_components.module,
                    lang, old_components.genre,
                    old_components.subdirs, parallel))
                newparallelpath = u'/'.join((
                    new_components.root,
                    new_components.module,
                    lang, new_components.genre,
                    new_components.subdirs,
                    parallel))

                self.compute_movepairs(oldparellelpath, newparallelpath)

    def compute_all_movepairs(self, oldpath, newpath):
        self.compute_movepairs(oldpath, newpath)
        self.compute_parallel_movepairs(oldpath, newpath)


class CorpusFileMover(object):
    '''Move an original file and all its derived files.'''
    def __init__(self, oldpath, newpath):
        '''Class to move corpus files

        Args:
            oldpath (unicode): the old path
            newpath (unicode): the new path
        '''
        self.old_components = util.split_path(oldpath)
        self.new_components = util.split_path(newpath)
        self.vcs = versioncontrol.VersionControlFactory().vcs(
            self.old_components.root)

    def move_files(self):
        self.move_orig()
        self.move_xsl()
        self.move_prestable_converted()
        self.move_prestable_tmx()

    def update_metadata(self):
        '''Update metadata'''
        metadatafile = xslsetter.MetadataHandler(self.xsl_pair.oldpath)
        if (self.old_components.genre != self.new_components.genre):
            metadatafile.set_variable('genre', self.new_components.genre)
        if (self.old_components.lang != self.new_components.lang):
            metadatafile.set_variable('mainlang', self.new_components.lang)
        metadatafile.write_file()

    def update_parallel_files_metadata(self):
        '''Update the info in the parallel files'''
        metadatafile = xslsetter.MetadataHandler(self.xsl_pair.oldpath)
        parallel_files = metadatafile.get_parallel_texts()

        for lang, parallel_file in parallel_files.items():
            parallel_metadatafile = xslsetter.MetadataHandler(
                '/'.join(
                    (self.old_components.root,
                     self.old_components.module,
                     lang, self.old_components.genre,
                     self.old_components.subdirs,
                     parallel_file + '.xsl')))

            if self.old_components.basename != self.new_components.basename:
                parallel_metadatafile.set_parallel_text(
                    self.new_components.lang, self.new_components.basename)
            parallel_metadatafile.write_file()

    def _move(self, oldpath, newpath):
        if os.path.exists(oldpath):
            newdir = os.path.dirname(newpath)
            if not os.path.exists(newdir):
                os.makedirs(newdir)
            self.vcs.move(oldpath.encode('utf8'), newpath.encode('utf8'))

    def move_orig(self):
        '''Move the original file'''
        self._move(
            u'/'.join(self.old_components),
            u'/'.join(self.new_components))

    def move_xsl(self):
        """Move the metadata file"""
        self._move(
            u'/'.join((self.old_components.root,
                       self.old_components.module,
                       self.old_components.lang,
                       self.old_components.genre,
                       self.old_components.subdirs,
                       self.old_components.basename + '.xsl')),
            u'/'.join((self.new_components.root,
                       self.new_components.module,
                       self.new_components.lang,
                       self.new_components.genre,
                       self.new_components.subdirs,
                       self.new_components.basename + '.xsl')))

    def move_prestable_converted(self):
        """Move the prestable/converted file"""
        self._move(
            u'/'.join((self.old_components.root,
                       u'prestable/converted',
                       self.old_components.lang,
                       self.old_components.genre,
                       self.old_components.subdirs,
                       self.old_components.basename + '.xml')),
            u'/'.join((self.new_components.root,
                       u'prestable/converted',
                       self.new_components.lang,
                       self.new_components.genre,
                       self.new_components.subdirs,
                       self.new_components.basename + '.xml')))

    def move_prestable_tmx(self):
        """Move the prestable toktmx and tmx files"""
        for tmx in [u'tmx', u'toktmx']:
            tmxdir = u'/'.join((u'prestable', tmx))
            metadatafile = xslsetter.MetadataHandler(
                u'/'.join((self.new_components.root,
                           self.new_components.module,
                           self.new_components.lang,
                           self.new_components.genre,
                           self.new_components.subdirs,
                           self.new_components.basename + '.xsl')))
            translated_from = metadatafile.get_variable('translated_from')
            if translated_from is None or translated_from == u'':
                for lang in metadatafile.get_parallel_texts().keys():
                    self._move(
                        u'/'.join((self.old_components.root, tmxdir,
                                   self.old_components.lang + u'2' + lang,
                                   self.old_components.genre,
                                   self.old_components.subdirs,
                                   self.old_components.basename + u'.' +
                                   tmx)),
                        u'/'.join((self.new_components.root, tmxdir,
                                   self.new_components.lang + u'2' + lang,
                                   self.new_components.genre,
                                   self.new_components.subdirs,
                                   self.new_components.basename + u'.' +
                                   tmx)))


class CorpusFilesetMoverAndUpdater(object):
    '''Move an original, its parallel files and all their derived files'''
    def __init__(self, oldpath, newpath):
        self.mc = MovepairComputer()
        self.mc.compute_all_movepairs(oldpath, newpath)

    def move_files(self):
        for filepair in self.mc.filepairs:
            cfm = CorpusFileMover(filepair.oldpath, filepair.newpath)
            cfm.move_files()

    def update_own_metadata(self):
        '''Update metadata'''
        for filepair in self.mc.filepairs:
            old_components = util.split_path(filepair.oldpath)
            new_components = util.split_path(filepair.newpath)

            metadatafile = xslsetter.MetadataHandler(filepair.newpath + '.xsl')
            if (old_components.genre != new_components.genre):
                metadatafile.set_variable('genre', new_components.genre)
            if (old_components.lang != new_components.lang):
                metadatafile.set_variable('mainlang', new_components.lang)
            metadatafile.write_file()

    def update_parallel_files_metadata(self):
        '''Update the info in the parallel files'''
        for filepair in self.mc.filepairs:
            parallel_filepairs = list(self.mc.filepairs)
            parallel_filepairs.remove(filepair)

            old_components = util.split_path(filepair.oldpath)
            new_components = util.split_path(filepair.newpath)

            for parallel_filepair in parallel_filepairs:
                parallel_metadatafile = xslsetter.MetadataHandler(
                        parallel_filepair.newpath + '.xsl')
                if old_components.lang != new_components.lang:
                    parallel_metadatafile.set_parallel_text(
                        old_components.lang, '')
                    parallel_metadatafile.set_parallel_text(
                        new_components.lang, new_components.basename)
                elif old_components.basename != new_components.basename:
                    parallel_metadatafile.set_parallel_text(
                        new_components.lang, new_components.basename)
                parallel_metadatafile.write_file()
