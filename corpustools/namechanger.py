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

Normalize a file name: Replace non-ascii char with ascii ones and remove
unwanted characters.

When normalizing a file name containing unwanted characters or renaming it
for other reasons:
* change the name of original file
* change the name of metadata file
* change the name of prestable/converted file
* change the name of prestable/toktmx file
* change the name of prestable/tmx file
* change the reference to the file name in the parallel files' metadata

Moving a file to another directory:
* Move a file to another genre
* Move a file to another language
* Move a file to a new subdirectory, without changing language or genre

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

    while '__' in newname:
        newname = newname.replace('__', '_')

    return newname


def are_duplicates(oldpath, newpath):
    '''Check if oldpath and newpath are duplicates of each other.

    Returns:
        a boolean indicating if the two files are duplicates
    '''
    return (os.path.isfile(newpath) and
            compute_hexdigest(oldpath) == compute_hexdigest(
                newpath))


def compute_new_basename(oldpath, wanted_path):
    '''Compute the new path

    Args:
        oldpath: path to the old file
        wanted_path: the path to move the file to

    Returns:
        a util.PathComponents namedtuple pointing to the new path
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
            if '.' in wanted_basename:
                dot = wanted_basename.rfind('.')
                extension = wanted_basename[dot:]
                pre_extension = wanted_basename[:dot]
                new_basename = pre_extension + '_' + str(n) + extension
            else:
                new_basename = wanted_basename + str(n)
            newpath = os.path.join(os.path.dirname(wanted_path), new_basename)
            n += 1

    return util.split_path(newpath)


PathPair = namedtuple('PathPair', ['oldpath', 'newpath'])
PathComponentsPair = namedtuple('PathComponentsPair', ['oldcomponent',
                                                       'newcomponent'])


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


class CorpusFileMover(object):
    '''Move an original file and all its associated files.'''
    def __init__(self, path_components_pair):
        '''

        Args:
            path_components_pair: a PathComponentsPair namedtuple
        '''
        self.path_components_pair = path_components_pair

    def move_files(self):
        for filepair in self.__compute_filepairs():
            if os.path.isfile(filepair[0]):
                subprocess.call(['git', 'mv', filepair[0], filepair[1]])
        self.__update_parallel_files()

    def __update_parallel_files(self):
        '''Update the info in the parallel files'''
        oldcomponent = self.path_components_pair.oldcomponent
        newcomponent = self.path_components_pair.newcomponent
        metadatafile = xslsetter.MetadataHandler('/'.join(
            self.path_components_pair.newcomponent) + '.xsl')

        parallels = metadatafile.get_parallel_texts()
        if (oldcomponent.basename != newcomponent.basename and
                oldcomponent.lang != newcomponent.lang):
            metadatafile.set_parallel_text(newcomponent.lang,
                                        newcomponent.basename)
        if (oldcomponent.lang != newcomponent.lang):
            metadatafile.set_parallel_text(newcomponent.lang,
                                           newcomponent.basename)
            metadatafile.set_parallel_text(oldcomponent.lang, '')
        if (oldcomponent.genre != newcomponent.genre):
            metadatafile.set_variable('genre', newcomponent.genre)
        metadatafile.write_file()

    def __compute_filepairs(self):
        filepairs = [('/'.join(self.path_components_pair.oldcomponent),
                      '/'.join(self.path_components_pair.newcomponent))]
        self.__get_xsl_pair(filepairs)
        self.__get_prestable_converted_pair(filepairs)
        self.__get_prestable_tmx_pairs(filepairs)

        return filepairs

    def __get_xsl_pair(self, filepairs):
        """Compute the new names of the metadata files.

        The new pair is appended to filepairs
        """
        oldpath = self.path_components_pair.oldcomponent
        newpath = self.path_components_pair.newcomponent

        oldname = os.path.join(oldpath.root, oldpath.module, oldpath.lang,
                               oldpath.genre, oldpath.subdirs,
                               oldpath.basename + '.xsl')
        newname = os.path.join(newpath.root, newpath.module, newpath.lang,
                               newpath.genre, newpath.subdirs,
                               newpath.basename + '.xsl')

        filepairs.append(PathPair(oldname, newname))

    def __get_prestable_converted_pair(self, filepairs):
        """Compute the new files of the prestabe/converted files.

        The new pair is appended to filepairs
        """
        oldpath = self.path_components_pair.oldcomponent
        newpath = self.path_components_pair.newcomponent

        oldname = os.path.join(oldpath.root, 'prestable/converted',
                               oldpath.lang, oldpath.genre, oldpath.subdirs,
                               oldpath.basename + '.xml')
        newname = os.path.join(newpath.root, 'prestable/converted',
                               newpath.lang, newpath.genre, newpath.subdirs,
                               newpath.basename + '.xml')

        filepairs.append(PathPair(oldname, newname))

    def __get_prestable_tmx_pairs(self, filepairs):
        """Compute the new names of the tmx files in prestable

        The new pairs are appended to filepairs
        """
        oldpath = self.path_components_pair.oldcomponent
        newpath = self.path_components_pair.newcomponent

        for tmx in ['tmx', 'toktmx']:
            tmxdir = os.path.join('prestable', tmx)
            for langsubdir in glob.glob(os.path.join(oldpath.root, tmxdir) + '/*'):
                oldname = os.path.join(oldpath.root, tmxdir,
                                       os.path.basename(langsubdir), oldpath.genre,
                                       oldpath.subdirs,
                                       oldpath.basename + '.' + tmx)
                newname = os.path.join(newpath.root, tmxdir,
                                       os.path.basename(langsubdir), newpath.genre,
                                       newpath.subdirs,
                                       newpath.basename + '.' + tmx)

                filepairs.append(PathPair(oldname, newname))


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
