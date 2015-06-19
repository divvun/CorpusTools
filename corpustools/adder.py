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
#   Copyright 2013-2014 Børre Gaup <borre.gaup@uit.no>
#

from __future__ import print_function

import argparse
import os
import shutil
import sys

import requests

import corpustools.argparse_version as argparse_version
import corpustools.namechanger as namechanger
import corpustools.util as util
import corpustools.versioncontrol as versioncontrol
import corpustools.xslsetter as xslsetter


class AddFileToCorpus(namechanger.NameChangerBase):
    '''Add a given file to a given corpus'''
    def __init__(self, oldname, corpusdir, mainlang, path, parallel_file):
        super(AddFileToCorpus, self).__init__(oldname)
        self.corpusdir = corpusdir
        self.mainlang = mainlang
        self.path = path
        self.new_dirname = os.path.join(corpusdir, 'orig', mainlang, path)
        vcsfactory = versioncontrol.VersionControlFactory()
        self.vcs = vcsfactory.vcs(corpusdir)
        self.parallel_file = parallel_file
        self.parallels = self._get_parallels()

    def makedirs(self):
        try:
            os.makedirs(self.new_dirname)
            self.vcs.add_directory(self.new_dirname)
        except OSError:
            pass

    def add_url_extension(self, content_type):
        content_type_extension = {
            'text/html': '.html',
            'application/msword': '.doc',
            'application/pdf': '.pdf',
            'text/plain': '.txt',
        }

        for ct, extension in content_type_extension.items():
            if (ct in content_type and not
                    self.new_filename.endswith(extension)):
                self.new_filename += extension

    def toname(self):
        return os.path.join(self.new_dirname, self.new_filename)

    def copy_orig_to_corpus(self):
        '''Copy the original file to the correct place in the given corpus'''
        fromname = os.path.join(self.old_dirname, self.old_filename)
        self.makedirs()

        if fromname.startswith('http'):
            try:
                r = requests.get(fromname)
                if r.status_code == requests.codes.ok:
                    self.add_url_extension(r.headers['content-type'])
                    if not os.path.exists(self.toname()):
                        with open(self.toname(), 'wb') as new_corpus_file:
                            new_corpus_file.write(r.content)
                        print('Added {}'.format(self.toname()))
                        self.vcs.add(self.toname())
                    else:
                        print('{} already exists'.format(self.toname()),
                              file=sys.stderr)
                else:
                    print('ERROR: {} does not exist'.format(fromname),
                          file=sys.stderr)
                    raise UserWarning
            except requests.exceptions.MissingSchema:
                print('Error: wrong schema', file=sys.stderr)
                raise UserWarning
            except requests.exceptions.ConnectionError as e:
                print('Could not connect', file=sys.stderr)
                print(str(e), file=sys.stderr)
                raise UserWarning
        else:
            shutil.copy(fromname, self.toname())
            print('Added', self.toname())
            self.vcs.add(self.toname())

    def _get_parallels(self):
        '''Set all the parallels of the orig file'''
        parallels = {}

        if self.parallel_file is not None:
            parallel_metadata = xslsetter.MetadataHandler(
                self.parallel_file + '.xsl')
            parallels[self.mainlang] = self.new_filename
            parallels[parallel_metadata.get_variable(
                'mainlang')] = os.path.basename(self.parallel_file)
            parallels.update(parallel_metadata.get_parallel_texts())

        return parallels

    def make_metadata_file(self, extra_values):
        '''Make a metadata file

        :param: extra_values is a dict that contains data for the metadata file
        that is not possible to infer from the data given in the constructor.
        '''
        metafile_name = self.toname() + '.xsl'
        if not os.path.exists(metafile_name):
            metadata_file = xslsetter.MetadataHandler(metafile_name,
                                                      create=True)
            if self.old_dirname.startswith('http'):
                metadata_file.set_variable('filename', os.path.join(
                    self.old_dirname, self.old_filename))
            else:
                metadata_file.set_variable('filename', self.old_filename)
            metadata_file.set_variable('genre', self.path.split('/')[0])
            metadata_file.set_variable('mainlang', self.mainlang)
            if isinstance(self.vcs.user_name(), str):
                metadata_file.set_variable(
                    'sub_name', self.vcs.user_name().decode('utf-8'))
            else:
                metadata_file.set_variable(
                    'sub_name', self.vcs.user_name())
            metadata_file.set_variable('sub_email', self.vcs.user_email())

            for key, value in extra_values.items():
                metadata_file.set_variable(key, value)
            metadata_file.write_file()

            self.update_parallel_files()

            print('Added', metadata_file.filename)
            self.vcs.add(metadata_file.filename)
        else:
            print(metafile_name, 'already exists', file=sys.stderr)

    def update_parallel_files(self):
        for lang1, location1 in self.parallels.items():
            for lang2, location2 in self.parallels.items():
                if lang2 != lang1:
                    parallel_metadata = xslsetter.MetadataHandler(
                        os.path.join(self.corpusdir, 'orig', lang1, self.path,
                                     location1 + '.xsl'))
                    parallel_metadata.set_parallel_text(lang2, location2)
                    parallel_metadata.write_file()


def gather_files(origs):
    file_list = []

    for orig in origs:
        if os.path.isdir(orig):
            for root, dirs, files in os.walk(orig):
                for f in files:
                    file_list.append(
                        util.name_to_unicode(os.path.join(root, f)))
        elif os.path.isfile(orig):
            file_list.append(util.name_to_unicode(orig))
        elif orig.startswith('http'):
            file_list.append(util.name_to_unicode(orig))
        else:
            print(
                'ERROR: {} is neither a directory, nor a file nor a '
                'http-url\n'.format(orig), file=sys.stderr)
            raise UserWarning

    return file_list


def add_files(args):
    for orig in gather_files(args.origs):
        adder = AddFileToCorpus(
            orig,
            args.corpusdir,
            args.mainlang,
            args.path,
            args.parallel_file)
        adder.copy_orig_to_corpus()
        adder.make_metadata_file({})


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

    if os.path.isdir(args.corpusdir):
        try:
            add_files(args)
        except UserWarning:
            pass
    else:
        print('ERROR', file=sys.stderr)
        print('The given corpus directory, {}, '
              'does not exist.'.format(args.corpusdir))
