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
#   Copyright 2013-2015 Børre Gaup <borre.gaup@uit.no>
#

from __future__ import print_function

import argparse
import os
import shutil
import sys

import requests

from corpustools import argparse_version
from corpustools import namechanger
from corpustools import util
from corpustools import versioncontrol
from corpustools import xslsetter


'''Adding files, directories and URL's to a corpus directory


Add a URL to the corpus
* normalise the basename, copy the the file to the given directory
* make a metadata file belonging to it
** set the url as the filename
** set the mainlang
** set the genre
** if a parallel file is given, set the parallel info in all the parellel files
** add both the newly copied file and the metadata file to the working copy

Add a directory to the corpus
* Recursively walks through the given original directory
** First checks for duplicates, raises an error printing a list of duplicate
   files if duplicates are found
** For each file, do the "add file to the corpus" operations (minus the
   parallel info).
'''


class AdderException(Exception):
    pass


class AddToCorpus(object):
    def __init__(self, corpusdir, mainlang, path):
        '''Baseclass for adding something to the corpus

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
                u'It must consist of three lowercase non ascii '
                u'letters'.format(mainlang))

        vcsfactory = versioncontrol.VersionControlFactory()
        self.vcs = vcsfactory.vcs(corpusdir)

        self.corpusdir = corpusdir
        self.mainlang = mainlang
        self.goaldir = os.path.join(corpusdir, u'orig', mainlang,
                                    self.__normalise_path(path))
        if not os.path.exists(self.goaldir):
            os.makedirs(self.goaldir)

    @staticmethod
    def __normalise_path(path):
        new_parts = []
        for part in path.split('/'):
            if part != '':
                new_parts.append(namechanger.normalise_filename(part))

        return u'/'.join(new_parts)


class AddFileToCorpus(AddToCorpus):
    '''Add a file to the corpus

    * normalise the basename, copy the the file to the given directory
    * make a metadata file belonging to it
    ** set the original basename as the filename
    ** set the mainlang
    ** set the genre
    ** if a parallel file is given, set the parallel info in all the parellel
    files
    ** add both the newly copied file and the metadata file to the working copy
'''
    def __init__(self, corpusdir, mainlang, path, origpath,
                 parallel_file=None):
        super(AddFileToCorpus, self).__init__(corpusdir, mainlang, path)

        self.mc = namechanger.MovepairComputer()
        self.mc.compute_movepairs(origpath, os.path.join(
            self.goaldir, os.path.basename(origpath)))

        self.parallel_file = parallel_file
        if parallel_file is not None and not os.path.exists(parallel_file):
            raise AdderException(
                'The given parallel file, {}, does not exist'.format(
                    parallel_file))

    def add_file_to_corpus(self):
        for filepair in self.mc.filepairs:
            shutil.copy(filepair.oldpath, filepair.newpath)
            new_components = util.split_path(filepair.newpath)
            new_metadata = xslsetter.MetadataHandler(filepair.newpath + '.xsl',
                                                     create=True)
            new_metadata.set_variable('filename', os.path.basename(
                filepair.oldpath))
            new_metadata.set_variable('mainlang', new_components.lang)
            new_metadata.set_variable('genre', new_components.genre)
            new_metadata.write_file()
            self.vcs.add([filepair.newpath, filepair.newpath + '.xsl'])

            if self.parallel_file is not None:
                parallel_metadata = xslsetter.MetadataHandler(
                    self.parallel_file + '.xsl')
                parallels = parallel_metadata.get_parallel_texts()
                parallels[new_components.lang] = new_components.basename

                parall_components = util.split_path(self.parallel_file)
                parallels[parall_components.lang] = parall_components.basename

                for lang, parallel in parallels.items():
                    metadata = xslsetter.MetadataHandler(
                        '/'.join((
                            new_components.root,
                            new_components.module,
                            lang,
                            new_components.genre,
                            new_components.subdirs,
                            parallel + '.xsl')))

                    for lang1, parallel1 in parallels.items():
                        if lang1 != lang:
                            metadata.set_parallel_text(lang1, parallel1)
                    metadata.write_file()


    #def add_url_extension(self, content_type):
        #content_type_extension = {
            #'text/html': '.html',
            #'application/msword': '.doc',
            #'application/pdf': '.pdf',
            #'text/plain': '.txt',
        #}

        #for ct, extension in content_type_extension.items():
            #if (ct in content_type and not
                    #self.new_filename.endswith(extension)):
                #self.new_filename += extension

    #def toname(self):
        #return os.path.join(self.new_dirname, self.new_filename)

    #def copy_orig_to_corpus(self):
        #'''Copy the original file to the correct place in the given corpus'''
        #fromname = os.path.join(self.old_dirname, self.old_filename)
        #self.makedirs()

        #if fromname.startswith('http'):
            #try:
                #r = requests.get(fromname)
                #if r.status_code == requests.codes.ok:
                    #self.add_url_extension(r.headers['content-type'])
                    #if not os.path.exists(self.toname()):
                        #with open(self.toname(), 'wb') as new_corpus_file:
                            #new_corpus_file.write(r.content)
                        #print('Added {}'.format(self.toname()))
                        #self.vcs.add(self.toname())
                    #else:
                        #print('{} already exists'.format(self.toname()),
                              #file=sys.stderr)
                #else:
                    #print('ERROR: {} does not exist'.format(fromname),
                          #file=sys.stderr)
                    #raise UserWarning
            #except requests.exceptions.MissingSchema:
                #print('Error: wrong schema', file=sys.stderr)
                #raise UserWarning
            #except requests.exceptions.ConnectionError as e:
                #print('Could not connect', file=sys.stderr)
                #print(str(e), file=sys.stderr)
                #raise UserWarning
        #else:
            #shutil.copy(fromname, self.toname())
            #print('Added', self.toname())
            #self.vcs.add(self.toname())

    #def make_metadata_file(self, extra_values):
        #'''Make a metadata file

        #:param: extra_values is a dict that contains data for the metadata file
        #that is not possible to infer from the data given in the constructor.
        #'''
        #metafile_name = self.toname() + '.xsl'
        #if not os.path.exists(metafile_name):
            #metadata_file = xslsetter.MetadataHandler(metafile_name,
                                                      #create=True)
            #if self.old_dirname.startswith('http'):
                #metadata_file.set_variable('filename', os.path.join(
                    #self.old_dirname, self.old_filename))
            #else:
                #metadata_file.set_variable('filename', self.old_filename)
            #metadata_file.set_variable('genre', self.path.split('/')[0])
            #metadata_file.set_variable('mainlang', self.mainlang)
            #if isinstance(self.vcs.user_name(), str):
                #metadata_file.set_variable(
                    #'sub_name', self.vcs.user_name().decode('utf-8'))
            #else:
                #metadata_file.set_variable(
                    #'sub_name', self.vcs.user_name())
            #metadata_file.set_variable('sub_email', self.vcs.user_email())

            #for key, value in extra_values.items():
                #metadata_file.set_variable(key, value)
            #metadata_file.write_file()

            #self.update_parallel_files()

            #print('Added', metadata_file.filename)
            #self.vcs.add(metadata_file.filename)
        #else:
            #print(metafile_name, 'already exists', file=sys.stderr)

    #def update_parallel_files(self):
        #for lang1, location1 in self.parallels.items():
            #for lang2, location2 in self.parallels.items():
                #if lang2 != lang1:
                    #parallel_metadata = xslsetter.MetadataHandler(
                        #os.path.join(self.corpusdir, 'orig', lang1, self.path,
                                     #location1 + '.xsl'))
                    #parallel_metadata.set_parallel_text(lang2, location2)
                    #parallel_metadata.write_file()


#class AddDirToCorpus(AddToCorpus):
    #def __init__(self, origdir, corpusdir, mainlang, path):
        #super(AddDirToCorpus, self).__init(corpusdir, mainlang, path)
        #if not os.path.isdir(origdir):
            #raise AdderException('{} '
                                 #'is not a directory.'.format(origdir))
        #self.origdir = origdir

    #def add(self):
        #'''Add the files contained in self.origdir to self.goaldir'''
        #additions = []
        #if not os.path.isdir(self.goaldir):
            #os.makedirs(self.goaldir)
            #for root, dirs, files in os.walk(self.origdir):
                #for f in files:
                    #self.copy_to_corpusdirectory(root, f)
                    #additions.append(os.path.join(root, f))

        #self.vcs.add(additions)


#def gather_files(origs):
    #file_list = []

    #for orig in origs:
        #if os.path.isdir(orig):
            #for root, dirs, files in os.walk(orig):
                #for f in files:
                    #file_list.append(
                        #util.name_to_unicode(os.path.join(root, f)))
        #elif os.path.isfile(orig):
            #file_list.append(util.name_to_unicode(orig))
        #elif orig.startswith('http'):
            #file_list.append(util.name_to_unicode(orig))
        #else:
            #print(
                #'ERROR: {} is neither a directory, nor a file nor a '
                #'http-url\n'.format(orig), file=sys.stderr)
            #raise UserWarning

    #return file_list


#def add_files(args):
    #for orig in gather_files(args.origs):
        #adder = AddFileToCorpus(
            #orig,
            #args.corpusdir,
            #args.mainlang,
            #args.path,
            #args.parallel_file)
        #adder.copy_orig_to_corpus()
        #adder.make_metadata_file({})


#def parse_args():
    #parser = argparse.ArgumentParser(
        #parents=[argparse_version.parser],
        #description='Add file(s) to a corpus directory. The filenames are '
        #'converted to ascii only names. Metadata files containing the '
        #'original name, the main language, the genre and possibly parallel '
        #'files are also made. The files are added to the working copy.')

    #parser.add_argument('-p', '--parallel',
                        #dest='parallel_file',
                        #help='An existing file in the corpus that is '
                        #'parallel to the orig that is about to be added')
    #parser.add_argument('corpusdir',
                        #help='The corpus dir (freecorpus or boundcorpus)')
    #parser.add_argument('mainlang',
                        #help='The language of the files that will be added '
                        #'(sma, sme, ...)')
    #parser.add_argument('path',
                        #help='The genre directory where the files will be '
                        #'added. This may also be a path, e.g. '
                        #'admin/facta/skuvlahistorja1')
    #parser.add_argument('origs',
                        #nargs='+',
                        #help='The original files, urls or directories where '
                        #'the original files reside (not in svn)')

    #return parser.parse_args()


#def main():
    #args = parse_args()

    #if args.parallel_file is not None:
        #if not os.path.exists(args.parallel_file):
            #print('The given parallel file\n\t{}\n'
                  #'does not exist'.format(args.parallel_file), file=sys.stderr)
            #sys.exit(1)
        #if len(args.origs) > 1:
            #print('When the -p option is given, it only makes '
                  #'sense to add one file at a time.', file=sys.stderr)
            #sys.exit(2)
        #if len(args.origs) == 1 and os.path.isdir(args.origs[-1]):
            #print('It is not possible to add a directory '
                  #'when the -p option is given.', file=sys.stderr)
            #sys.exit(3)

    #if os.path.isdir(args.corpusdir):
        #try:
            #add_files(args)
        #except UserWarning:
            #pass
    #else:
        #print('ERROR', file=sys.stderr)
