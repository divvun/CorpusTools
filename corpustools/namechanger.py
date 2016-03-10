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
#   Copyright © 2013-2016 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
from __future__ import print_function

import os

from collections import namedtuple
import hashlib
import unidecode
import urllib

from corpustools import util
from corpustools import versioncontrol
from corpustools import xslsetter


class NamechangerException(Exception):
    pass


PathPair = namedtuple('PathPair', 'oldpath newpath')


class MovepairComputer(object):
    '''Compute oldname, newname pairs'''
    def __init__(self):
        '''filepairs will be a list of PathPairs'''
        self.filepairs = []

    def compute_movepairs(self, oldpath, newpath, nochange=False):
        '''Add the oldpath and the new goalpath to filepairs

        Args:
            oldpath (unicode): the old path to an original file
            newpath (unicode): the new path of an original file
        '''
        normalisedpath = os.path.join(
            os.path.dirname(newpath),
            normalise_filename(os.path.basename(newpath)))

        if normalisedpath == newpath and nochange:
            non_dupe_path = newpath
        else:
            non_dupe_path = compute_new_basename(oldpath, normalisedpath)

        self.filepairs.append(PathPair(oldpath, non_dupe_path))

    def compute_parallel_movepairs(self, oldpath, newpath):
        '''Add the parallel files of oldpath to filepairs

        Args:
            oldpath (unicode): the old path
            newpath (unicode): the new path
        '''
        old_components = util.split_path(oldpath)

        if newpath == u'':
            newpath = oldpath

        new_components = util.split_path(newpath)

        metadatafile = xslsetter.MetadataHandler(oldpath + '.xsl')
        for lang, parallel in metadatafile.get_parallel_texts().iteritems():
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
            no_mv_needed = (old_components.genre == new_components.genre and
                            old_components.subdirs == new_components.subdirs)
            self.compute_movepairs(oldparellelpath, newparallelpath, no_mv_needed)

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

    def _move(self, oldpath, newpath):
        if os.path.exists(oldpath):
            newdir = os.path.dirname(newpath)
            with util.ignored(OSError):
                os.makedirs(newdir)
            self.vcs.move(oldpath.encode('utf8'), newpath.encode('utf8'))

    def move_orig(self):
        '''Move the original file'''
        self._move(
            u'/'.join(self.old_components),
            u'/'.join(self.new_components))

    def move_xsl(self):
        '''Move the metadata file'''
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
        '''Move the prestable/converted file'''
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
        '''Move the prestable toktmx and tmx files'''
        for tmx in [u'tmx', u'toktmx']:
            tmxdir = u'/'.join((u'prestable', tmx))
            metadataname = u'/'.join((self.new_components.root,
                                      self.new_components.module,
                                      self.new_components.lang,
                                      self.new_components.genre,
                                      self.new_components.subdirs,
                                      self.new_components.basename + '.xsl'))
            if os.path.isfile(metadataname):
                metadatafile = xslsetter.MetadataHandler(metadataname)
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


class CorpusFileRemover(object):
    '''Remove an original file and all its derived files'''
    def __init__(self, oldpath):
        '''Class to remove corpus files

        Args:
            oldpath (unicode): the old path
        '''
        self.old_components = util.split_path(oldpath)
        self.vcs = versioncontrol.VersionControlFactory().vcs(
            self.old_components.root)

    def remove_files(self):
        self.remove_prestable_tmx()
        self.remove_prestable_converted()
        self.remove_xsl()
        self.remove_orig()

    def _remove(self, oldpath):
        if os.path.exists(oldpath):
            self.vcs.remove(oldpath.encode('utf8'))

    def remove_orig(self):
        '''Remove the original file'''
        self._remove(u'/'.join(self.old_components))

    def remove_xsl(self):
        '''Remove the metadata file'''
        self._remove(
            u'/'.join((self.old_components.root,
                       self.old_components.module,
                       self.old_components.lang,
                       self.old_components.genre,
                       self.old_components.subdirs,
                       self.old_components.basename + '.xsl')))

    def remove_prestable_converted(self):
        '''Remove the prestable/converted file'''
        self._remove(
            u'/'.join((self.old_components.root,
                       u'prestable/converted',
                       self.old_components.lang,
                       self.old_components.genre,
                       self.old_components.subdirs,
                       self.old_components.basename + '.xml')))

    def remove_prestable_tmx(self):
        '''Remove the prestable toktmx and tmx files'''
        for tmx in [u'tmx', u'toktmx']:
            tmxdir = u'/'.join((u'prestable', tmx))
            metadataname = u'/'.join((self.old_components.root,
                                      self.old_components.module,
                                      self.old_components.lang,
                                      self.old_components.genre,
                                      self.old_components.subdirs,
                                      self.old_components.basename + '.xsl'))
            if os.path.isfile(metadataname):
                metadatafile = xslsetter.MetadataHandler(metadataname)
                translated_from = metadatafile.get_variable('translated_from')
                if translated_from is None or translated_from == u'':
                    for lang in metadatafile.get_parallel_texts().keys():
                        self._remove(
                            u'/'.join((self.old_components.root, tmxdir,
                                       self.old_components.lang + u'2' + lang,
                                       self.old_components.genre,
                                       self.old_components.subdirs,
                                       self.old_components.basename + u'.' +
                                       tmx)))


class CorpusFilesetMoverAndUpdater(object):
    '''Move or remove a file within a repository

    When moving a file inside the same directory:
    * move the original file
    * move the metadata file
    * move the prestable/converted file
    * move the prestable/toktmx file
    * move the prestable/tmx file
    * change the metadata in the metadata file, if needed
    * change the reference to the file name in the parallel files' metadata, if needed
    * if the parallel files need name normalisation, move them the same way the
      original file is handled

    Removal is signaled by an empty string for the newpath argument.
    When removing a file. :
    * remove the original file
    * remove the metadata file
    * remove the prestable/converted file
    * remove the prestable/toktmx file
    * remove the prestable/tmx file
    * change the reference to the file name in the parallel files' metadata
    * if the parallel files need name normalisation, move them the same way the
      original file is handled

    When moving a file from one subdirectory to another:
    * move the original file
    * move the metadata file
    * move the prestable/converted file
    * move the prestable/toktmx file
    * move the prestable/tmx file
    * change the metadata in the metadata file, if needed
    * change the reference to the file name in the parallel files' metadata, if needed
    * change the reference to the file name in the parallel files' metadata if needed
    * move the parallel files the same way the original file has been moved.

    When moving a file to a new genre:
    * the subdirectory move operations +
    * change the genre reference in the metadata files

    When moving a file to a new language:
    * move the original file
    * move the metadata file
    * move the prestable/converted file
    * move the prestable/toktmx file
    * move the prestable/tmx file
    * change the language of the file in the parallel files' metadata
    * if the parallel files need name normalisation, move them the same way the
      original file is handled

    Normalise a file name: Replace non-ascii char with ascii ones and remove
    unwanted characters.

    When doing these operations, detect name clashes for the original files.

    If a name clash is found, check if the files are duplicates. If they are
    duplicates, raise an exception, otherwise suggest a new name.
    '''

    def __init__(self, oldpath, newpath):
        self.mc = MovepairComputer()
        self.mc.compute_all_movepairs(oldpath, newpath)
        self.old_components = util.split_path(oldpath)
        self.vcs = versioncontrol.VersionControlFactory().vcs(
            self.old_components.root)

    def move_files(self):
        for filepair in self.mc.filepairs:
            if len(filepair.newpath) == 0:
                cfr = CorpusFileRemover(filepair.oldpath)
                cfr.remove_files()
            elif filepair.oldpath != filepair.newpath:
                cfm = CorpusFileMover(filepair.oldpath, filepair.newpath)
                cfm.move_files()

    def update_own_metadata(self):
        '''Update metadata'''
        for filepair in self.mc.filepairs:
            if len(filepair.newpath) > 0:
                old_components = util.split_path(filepair.oldpath)
                new_components = util.split_path(filepair.newpath)

                metadataname = filepair.newpath + '.xsl'
                if os.path.isfile(metadataname):
                    metadatafile = xslsetter.MetadataHandler(metadataname)
                    if (old_components.genre != new_components.genre):
                        metadatafile.set_variable('genre', new_components.genre)
                    if (old_components.lang != new_components.lang):
                        metadatafile.set_variable('mainlang', new_components.lang)
                    metadatafile.write_file()
                    self.vcs.add(metadataname)

    def update_parallel_files_metadata(self):
        '''Update the info in the parallel files'''
        for filepair in self.mc.filepairs:
            parallel_filepairs = list(self.mc.filepairs)
            parallel_filepairs.remove(filepair)

            old_components = util.split_path(filepair.oldpath)
            if len(filepair.newpath) > 0:
                new_components = util.split_path(filepair.newpath)

                for parallel_filepair in parallel_filepairs:
                    parallel_name = parallel_filepair.newpath + '.xsl'
                    if os.path.isfile(parallel_name):
                        parallel_metadatafile = xslsetter.MetadataHandler(
                            parallel_name)
                        if old_components.lang != new_components.lang:
                            parallel_metadatafile.set_parallel_text(
                                old_components.lang, '')
                            parallel_metadatafile.set_parallel_text(
                                new_components.lang, new_components.basename)
                        elif old_components.basename != new_components.basename:
                            parallel_metadatafile.set_parallel_text(
                                new_components.lang, new_components.basename)
                        parallel_metadatafile.write_file()
                        self.vcs.add(parallel_name)

            else:
                for parallel_filepair in parallel_filepairs:
                    parallel_name = parallel_filepair.newpath + '.xsl'
                    if os.path.isfile(parallel_name):
                        parallel_metadatafile = xslsetter.MetadataHandler(
                            parallel_name)
                        parallel_metadatafile.set_parallel_text(
                                old_components.lang, u'')
                        parallel_metadatafile.write_file()
                        self.vcs.add(parallel_name)


def compute_hexdigest(path, blocksize=65536):
    '''Compute the hexdigest of the file in path

    Args:
        path: the file to compute the hexdigest of

    Returns:
        a hexdigest of the file
    '''
    with open(path, 'rb') as afile:
        hasher = hashlib.md5()
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)

        return hasher.hexdigest()


def normalise_filename(filename):
    '''Normalise filename to ascii only

    Downcase filename, replace non-ascii characters with ascii ones and
    remove or replace unwanted characters.

    Args:
        filename: is a unicode string

    Returns:
        a downcased string containing only ascii chars
    '''
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

    newname = util.replace_all(unwanted_chars.iteritems(), newname)

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
    return (os.path.isfile(oldpath) and os.path.isfile(newpath) and
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
            raise UserWarning(u'{} and {} are duplicates. '.format(oldpath,
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
