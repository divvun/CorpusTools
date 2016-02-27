# -*- coding:utf-8 -*-

#
#   This file contains routines to add files to a corpus directory
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

import argparse
import os
import requests
import shutil
import sys

from corpustools import argparse_version
from corpustools import namechanger
from corpustools import util
from corpustools import versioncontrol
from corpustools import xslsetter


class AdderException(Exception):
    pass


class UrlDownloader(object):
    def __init__(self, url, download_dir):
        self.download_dir = download_dir
        self.url = url

    @staticmethod
    def add_url_extension(filename, content_type):
        content_type_extension = {
            'text/html': '.html',
            'application/msword': '.doc',
            'application/pdf': '.pdf',
            'text/plain': '.txt',
        }

        for ct, extension in content_type_extension.items():
            if (ct in content_type and not filename.endswith(extension)):
                filename += extension

        return filename

    def download(self):
        '''Download a url to a temporary file

        Return the request object and the name of the temporary file
        '''
        try:
            r = requests.get(self.url)
            if r.status_code == requests.codes.ok:
                tmpname = self.add_url_extension(
                    os.path.join(self.download_dir,
                                 os.path.basename(r.url)),
                    r.headers['content-type'])
                with open(tmpname, 'wb') as tmpfile:
                    tmpfile.write(r.content)

                return (r, tmpname)
            else:
                raise AdderException('ERROR:', url, 'does not exist')
        except requests.exceptions.MissingSchema as e:
            raise AdderException(str(e))
        except requests.exceptions.ConnectionError as e:
            raise AdderException(str(e))


class AddToCorpus(object):

    def __init__(self, corpusdir, mainlang, path):
        '''Class to adding files, urls and dirs to the corpus

        Args:
            corpusdir: (unicode) the directory where the corpus is
            mainlang: (unicode) three character long lang id (iso-639)
            path: (unicode) path below the language directory where the files
            should be added
        '''
        if type(corpusdir) is not unicode:
            raise AdderException(u'corpusdir is not unicode: {}.'.format(
                corpusdir))

        if type(mainlang) is not unicode:
            raise AdderException(u'mainlang is not unicode: {}.'.format(
                mainlang))

        if type(path) is not unicode:
            raise AdderException(u'path is not unicode: {}.'.format(
                path))

        if not os.path.isdir(corpusdir):
            raise AdderException(u'The given corpus directory, {}, '
                                 u'does not exist.'.format(corpusdir))

        if (len(mainlang) != 3 or mainlang != mainlang.lower() or
                mainlang != namechanger.normalise_filename(mainlang)):
            raise AdderException(
                u'Invalid mainlang: {}. '
                u'It must consist of three lowercase ascii '
                u'letters'.format(mainlang))

        self.corpusdir = corpusdir
        vcsfactory = versioncontrol.VersionControlFactory()
        self.vcs = vcsfactory.vcs(self.corpusdir)
        self.goaldir = os.path.join(corpusdir, u'orig', mainlang,
                                    self.__normalise_path(path))
        if not os.path.exists(self.goaldir):
            os.makedirs(self.goaldir)
        self.additions = []

    @staticmethod
    def __normalise_path(path):
        '''All paths in the corpus should consist of lowercase ascii letters'''
        return u'/'.join([namechanger.normalise_filename(part)
                          for part in path.split('/')])

    def copy_url_to_corpus(self, url, parallelpath=''):
        '''Add a URL to the corpus

        Copy a downloaded url to the corpus
        '''
        try:
            downloader = UrlDownloader(url, os.path.join(self.corpusdir, 'tmp'))
            (r, tmpname) = downloader.download()

            return self.copy_file_to_corpus(tmpname, r.url, parallelpath)
        except UserWarning as e:
            print(u'Skipping: {}'.format(e))

    def copy_file_to_corpus(self, origpath, metadata_filename, parallelpath=''):
        '''Add a file to the corpus

        * normalise the basename, copy the the file to the given directory
        * make a metadata file belonging to it
        ** set the original basename as the filename
        ** set the mainlang
        ** set the genre
        ** if a parallel file is given, set the parallel info in all the
        parellel files
        '''
        try:
            none_dupe_path = self.none_dupe_path(origpath)
            shutil.copy(origpath, none_dupe_path)
            self.additions.append(none_dupe_path)

            self.add_metadata_to_corpus(none_dupe_path,
                                        metadata_filename)
            self.update_parallel_data(util.split_path(none_dupe_path),
                                      parallelpath)
            return none_dupe_path
        except UserWarning as e:
            print(u'Skipping: {}'.format(e))

    def add_metadata_to_corpus(self, none_dupe_path, meta_filename):
        none_dupe_components = util.split_path(none_dupe_path)
        new_metadata = xslsetter.MetadataHandler(none_dupe_path + '.xsl',
                                                 create=True)
        new_metadata.set_variable('filename', meta_filename)
        new_metadata.set_variable('mainlang', none_dupe_components.lang)
        new_metadata.set_variable('genre', none_dupe_components.genre)
        new_metadata.write_file()
        self.additions.append(none_dupe_path + '.xsl')

    @staticmethod
    def update_parallel_data(none_dupe_components, parallelpath):
        '''Update metadata in the parallel files

        Arguments:
            new_components: (util.PathComponents) of none_dupe_path
            parallelpath: (string) path of the parallel file
        '''
        if len(parallelpath) > 0:
            if not os.path.exists(parallelpath):
                raise AdderException('{} does not exist'.format(
                    parallelpath))

            parallel_metadata = xslsetter.MetadataHandler(
                parallelpath + '.xsl')
            parallels = parallel_metadata.get_parallel_texts()
            parallels[none_dupe_components.lang] = none_dupe_components.basename

            parall_components = util.split_path(parallelpath)
            parallels[parall_components.lang] = parall_components.basename

            for lang, parallel in parallels.items():
                metadata = xslsetter.MetadataHandler(
                    '/'.join((
                        none_dupe_components.root,
                        none_dupe_components.module,
                        lang,
                        none_dupe_components.genre,
                        none_dupe_components.subdirs,
                        parallel + '.xsl')))

                for lang1, parallel1 in parallels.items():
                    if lang1 != lang:
                        metadata.set_parallel_text(lang1, parallel1)
                metadata.write_file()

    def none_dupe_path(self, path):
        '''Compute the none duplicate path of the file to be added

        Arguments:
            path: (string) path of the file as given as input
            This string may contain unwanted chars and
        '''
        return namechanger.compute_new_basename(
            path, os.path.join(self.goaldir,
                               namechanger.normalise_filename(
                                   os.path.basename(path))))

    def copy_files_in_dir_to_corpus(self, origpath):
        '''Add a directory to the corpus

        * Recursively walks through the given original directory
        ** First checks for duplicates, raises an error printing a list of
        duplicate files if duplicates are found
        ** For each file, do the "add file to the corpus" operations (minus the
        parallel info).
        '''
        self.find_duplicates(origpath)
        for root, dirs, files in os.walk(origpath):
            for f in files:
                orig_f = os.path.join(root, f).decode('utf8')
                self.copy_file_to_corpus(orig_f, os.path.basename(orig_f))

    @staticmethod
    def find_duplicates(origpath):
        duplicates = {}
        for root, dirs, files in os.walk(origpath):
            for f in files:
                path = os.path.join(root, f).decode('utf8')
                file_hash = namechanger.compute_hexdigest(path)
                if file_hash in duplicates:
                    duplicates[file_hash].append(path)
                else:
                    duplicates[file_hash] = [path]

        results = list(filter(lambda x: len(x) > 1, duplicates.values()))
        if len(results) > 0:
            print(u'Duplicates Found:')
            print(u'___')
            for result in results:
                for subresult in result:
                    print(u'\t{}'.format(subresult))
                print(u'___')

            raise AdderException(u'Found duplicates')

    def add_files_to_working_copy(self):
        self.vcs.add(self.additions)


def parse_args():
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Add file(s) to a corpus directory. The filenames are '
        'converted to ascii only names. Metadata files containing the '
        'original name, the main language, the genre and possibly parallel '
        'files are also made. The files are added to the working copy.')

    parser.add_argument('-p', '--parallel',
                        dest='parallel_file',
                        help='An existing file in the corpus that is '
                        'parallel to the orig that is about to be added')
    parser.add_argument('corpusdir',
                        help='The corpus dir (freecorpus or boundcorpus)')
    parser.add_argument('mainlang',
                        help='The language of the files that will be added '
                        '(sma, sme, ...)')
    parser.add_argument('path',
                        help='The genre directory where the files will be '
                        'added. This may also be a path, e.g. '
                        'admin/facta/skuvlahistorja1')
    parser.add_argument('origs',
                        nargs='+',
                        help='The original files, urls or directories where '
                        'the original files reside (not in svn)')

    return parser.parse_args()


def main():
    args = parse_args()
    adder = AddToCorpus(args.corpusdir.decode('utf8'),
                        args.mainlang.decode('utf8'),
                        args.path.decode('utf8'))

    if args.parallel_file is not None:
        if not os.path.exists(args.parallel_file):
            print('The given parallel file\n\t{}\n'
                  'does not exist'.format(args.parallel_file), file=sys.stderr)
            sys.exit(1)
        if len(args.origs) > 1:
            print('When the -p option is given, it only makes '
                  'sense to add one file at a time.', file=sys.stderr)
            sys.exit(2)
        if len(args.origs) == 1 and os.path.isdir(args.origs[-1]):
            print('It is not possible to add a directory '
                  'when the -p option is given.', file=sys.stderr)
            sys.exit(3)
        orig = args.origs[0]
        if os.path.isfile(orig):
            adder.copy_file_to_corpus(orig.decode('utf8'),
                                      args.parallel_file.decode('utf8'))
        elif orig.startswith('http'):
            adder.copy_url_to_corpus(orig.decode('utf8'),
                                     args.parallel_file.decode('utf8'))
    else:
        for orig in args.origs:
            if os.path.isfile(orig):
                adder.copy_file_to_corpus(orig.decode('utf8'),
                                          os.path.basename(orig.decode('utf8')))
            elif orig.startswith('http'):
                adder.copy_url_to_corpus(orig.decode('utf8'))
            elif os.path.isdir(orig):
                adder.copy_files_in_dir_to_corpus(orig)
            else:
                print(u'Cannot handle {}'.format(orig), file=sys.stderr)

    adder.add_files_to_working_copy()
