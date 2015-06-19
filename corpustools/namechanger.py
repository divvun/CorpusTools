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
import glob
import os
import subprocess

from collections import namedtuple
import hashlib
import unidecode
import urllib

import corpustools.argparse_version as argparse_version
import corpustools.util as util
import corpustools.xslsetter as xslsetter


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


class PathComponentsPair(namedtuple('PathComponentsPair',
                                    'oldcomponent newcomponent')):
    pass


def normaliser():
    '''Normalise the filenames in the corpuses'''
    for corpus in [os.getenv('GTFREE'), os.getenv('GTBOUND')]:
        os.chdir(corpus)
        for root, dirs, files in os.walk(os.path.join(corpus, 'orig')):
            for f in files:
                if not f.endswith('.xsl'):
                    old_path = os.path.join(root, f).decode('utf8')
                    wanted_path = os.path.join(root, normalise_filename(
                        f.decode('utf8')))
                    if old_path != wanted_path:
                        mover = CorpusFileMover(
                            PathComponentsPair(util.split_path(old_path),
                                               compute_new_basename(
                                                   old_path, wanted_path)))
                        mover.move_files()


def file_mover(oldpath, newpath):
    origmover = CorpusFileMover(oldpath, newpath)
    origmover.move_files()
    origmover.update_parallel_files()

    if (origmover.old_components.subdirs != origmover.new_components.subdirs or
            origmover.old_components.genre != origmover.new_components.genre):
        metadatafile = xslsetter.MetadataHandler(origmover.xsl_pair.oldpath)
        for lang, parallel_file in metadatafile.get_parallel_texts():
            oldparellelpath = u'/'.join(
                origmover.old_components.root,
                origmover.old_components.module,
                lang, origmover.old_components.genre,
                origmover.old_components.subdirs, parallel_file)
            newparallelpath = u'/'.join(
                origmover.new_components.root,
                origmover.new_components.module,
                lang, origmover.new_components.genre,
                origmover.new_components.subdirs, parallel_file)
            parallelmover = CorpusFileMover(oldparellelpath, newparallelpath)
            parallelmover.move_files()
            parallelmover.update_parallel_files()



class CorpusFileMover(object):
    '''Move an original file and all its associated files.'''
    def __init__(self, oldpath, newpath):
        '''

        Args:
            oldpath (unicode): the old path
            newpath (unicode): the new path
        '''
        self.old_components = util.split_path(oldpath)
        self.new_components = util.split_path(newpath)

    def move_files(self):
        for filepair in self.file_pairs():
            if os.path.isfile(filepair.old_path):
                subprocess.call(['git', 'mv', filepair[0], filepair[1]])

    def update_parallel_files(self):
        '''Update the info in the parallel files'''
        metadatafile = xslsetter.MetadataHandler(self.xsl_pair.oldpath)
        parallels = metadatafile.get_parallel_texts()
        if (self.old_components.basename != self.new_components.basename and
                self.old_components.lang != self.new_components.lang):
            metadatafile.set_parallel_text(self.new_components.lang,
                                           self.new_components.basename)
        if (self.old_components.lang != self.new_components.lang):
            metadatafile.set_parallel_text(self.new_components.lang,
                                           self.new_components.basename)
            metadatafile.set_parallel_text(self.old_components.lang, '')
        if (self.old_components.genre != self.new_components.genre):
            metadatafile.set_variable('genre', self.new_components.genre)
        metadatafile.write_file()

    @property
    def file_pairs(self):
        return ([self.orig_pair, self.xsl_pair, self.prestable_converted_pair] +
                self.prestable_tmx_pairs)

    @property
    def orig_pair(self):
        '''Make an orig PathPair'''
        return PathPair(u'/'.join(self.old_components),
                        u'/'.join(self.new_components))

    @property
    def xsl_pair(self):
        """Compute the new names of the metadata files.

        The new pair is appended to filepairs
        """
        return PathPair(u'/'.join(self.old_components.root,
                                  self.old_components.module,
                                  self.old_components.lang,
                                  self.old_components.genre,
                                  self.old_components.subdirs,
                                  self.old_components.basename + '.xsl'),
                        u'/'.join(self.new_components.root,
                                  self.new_components.module,
                                  self.new_components.lang,
                                  self.new_components.genre,
                                  self.new_components.subdirs,
                                  self.new_components.basename + '.xsl'))

    @property
    def prestable_converted_pair(self):
        """Compute the new files of the prestabe/converted files.

        The new pair is appended to filepairs
        """
        return PathPair(u'/'.join(self.old_components.root,
                                  u'prestable/converted',
                                  self.old_components.lang,
                                  self.old_components.genre,
                                  self.old_components.subdirs,
                                  self.old_components.basename + '.xml'),
                        u'/'.join(self.new_components.root,
                                  u'prestable/converted',
                                  self.new_components.lang,
                                  self.new_components.genre,
                                  self.new_components.subdirs,
                                  self.new_components.basename + '.xsl'))

    @property
    def prestable_tmx_pairs(self):
        """Compute the new names of the tmx files in prestable

        The new pairs are appended to filepairs
        """
        filepairs = []
        for tmx in [u'tmx', u'toktmx']:
            tmxdir = u'/'.join(u'prestable', tmx)
            metadatafile = xslsetter.MetadataHandler(self.xsl_pair.oldpath)
            translated_from = metadatafile.get_variable('translated_from')
            if translated_from is None or translated_from == u'':
                for lang in metadatafile.get_parallel_texts().keys():
                    orig_lang = metadatafile.get_variable('mainlang')
                    filepairs.append(
                        PathPair(
                            u'/'.join(self.old_components.root, tmxdir,
                                      orig_lang + u'2' + lang,
                                      self.old_components.genre,
                                      self.old_components.subdirs,
                                      self.old_components.basename + u'.' +
                                      tmx),
                            u'/'.join(self.new_components.root, tmxdir,
                                      orig_lang + u'2' + lang,
                                      self.new_components.genre,
                                      self.new_components.subdirs,
                                      self.new_components.basename + u'.' +
                                      tmx)))

        return filepairs

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
