# -*- coding: utf-8 -*-

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
#   Copyright 2015 Børre Gaup <borre.gaup@uit.no>
#

import git
import os
import testfixtures
import unittest

from corpustools import adder
from corpustools import versioncontrol
from corpustools import xslsetter


class TestAddToCorpus(unittest.TestCase):
    def setUp(self):
        self.tempdir = testfixtures.TempDirectory(ignore=['.git'])
        self.tempdir.makedir('tull')
        self.tempdir.makedir('corpus/orig')
        self.realcorpusdir = os.path.join(self.tempdir.path,
                                          'corpus').decode('utf8')

        r = git.Repo.init(self.realcorpusdir)
        r.index.add(['orig'])
        r.index.commit('Added orig')

    def tearDown(self):
        self.tempdir.cleanup()

    def test_init_with_non_unicode_corpusdir(self):
        corpusdir = 'there'
        lang = u'sme'
        path = u'a/b/c'

        with self.assertRaises(adder.AdderException):
            adder.AddToCorpus(corpusdir, lang, path)

    def test_init_with_non_unicode_lang(self):
        corpusdir = u'there'
        lang = 'sme'
        path = u'a/b/c'

        with self.assertRaises(adder.AdderException):
            adder.AddToCorpus(corpusdir, lang, path)

    def test_init_with_non_unicode_path(self):
        corpusdir = u'there'
        lang = u'sme'
        path = 'a/b/c'

        with self.assertRaises(adder.AdderException):
            adder.AddToCorpus(corpusdir, lang, path)

    def test_init_with_non_existing_corpusdir(self):
        corpusdir = u'there'
        lang = u'sme'
        path = u'a/b/c'

        with self.assertRaises(adder.AdderException):
            adder.AddToCorpus(corpusdir, lang, path)

    def test_init_with_existing_corpusdir_but_not_vcs(self):
        lang = u'sme'
        path = u'a/b/c'

        with self.assertRaises(versioncontrol.VersionControlException):
            adder.AddToCorpus(
                os.path.join(self.tempdir.path, 'tull').decode('utf8'),
                lang, path)

    def test_init_with_vcs_corpusdir(self):
        lang = u'sme'
        path = u'a/b/c'

        atc = adder.AddToCorpus(
            self.realcorpusdir,
            lang, path)
        self.assertEqual(atc.goaldir, os.path.join(self.tempdir.path, 'corpus',
                                                   'orig', lang, path))
        self.tempdir.check_dir('corpus/orig/sme/a/b/c')

    def test_init_with_too_long_mainlang(self):
        lang = u'smei'
        path = u'a/b/c'

        with self.assertRaises(adder.AdderException):
            adder.AddToCorpus(self.realcorpusdir, lang, path)

    def test_init_with_uppercase_mainlang(self):
        lang = u'SME'
        path = u'a/b/c'

        with self.assertRaises(adder.AdderException):
            adder.AddToCorpus(self.realcorpusdir, lang, path)

    def test_init_with_non_ascii_mainlang(self):
        lang = u'øåæ'
        path = u'a/b/c'

        with self.assertRaises(adder.AdderException):
            adder.AddToCorpus(self.realcorpusdir, lang, path)

    def test_init_with_path_that_must_be_normalised(self):
        lang = u'sme'
        path = u'æ/č/ö'

        atc = adder.AddToCorpus(self.realcorpusdir, lang, path)
        self.assertEqual(atc.goaldir, os.path.join(self.tempdir.path, 'corpus',
                                                   'orig', lang, 'ae/c/o'))


class TestAddFileToCorpus(unittest.TestCase):
    def setUp(self):
        self.tempdir = testfixtures.TempDirectory(ignore=['.git'])
        self.tempdir.write('origdirectory/a.txt', 'content of a')
        self.tempdir.write('origdirectory/æ.txt', 'content of æ')
        self.tempdir.write('origdirectory/b.txt', 'content of b')
        self.tempdir.write('origdirectory/c.txt', 'original content of c')
        self.tempdir.write('origdirectory/d.txt', 'content of d')

        self.tempdir.makedir('corpus/orig')
        self.tempdir.write('corpus/orig/sme/ae/c/o/b.txt', 'content of b')
        self.tempdir.write('corpus/orig/sme/ae/c/o/c.txt',
                           'corpusfile content of c')
        self.tempdir.write('corpus/orig/smj/ae/c/o/f.txt', 'smj content of f')
        self.tempdir.write('corpus/orig/sma/ae/c/o/f.txt', 'sma content of f')

        self.realcorpusdir = os.path.join(self.tempdir.path,
                                          'corpus').decode('utf8')
        self.origdirectory = os.path.join(self.tempdir.path,
                                          'origdirectory')

        smj_metadata = xslsetter.MetadataHandler(
            os.path.join(self.realcorpusdir, 'orig/smj/ae/c/o/f.txt.xsl'),
            create=True)
        smj_metadata.set_variable('mainlang', 'smj')
        smj_metadata.set_parallel_text('sma', 'f.txt')
        smj_metadata.write_file()

        sma_metadata = xslsetter.MetadataHandler(
            os.path.join(self.realcorpusdir, 'orig/sma/ae/c/o/f.txt.xsl'),
            create=True)
        sma_metadata.set_variable('mainlang', 'sma')
        sma_metadata.set_variable('translated_from', 'smj')
        sma_metadata.set_parallel_text('smj', u'f.txt')
        sma_metadata.write_file()

        r = git.Repo.init(self.realcorpusdir)
        r.index.add(['orig'])
        r.index.commit('Added orig')

    def tearDown(self):
        self.tempdir.cleanup()

    def test_add_file_no_normalise_no_parallel(self):
        atc = adder.AddToCorpus(self.realcorpusdir, u'sme', u'æ/č/ö')

        atc.copy_file_to_corpus(os.path.join(self.origdirectory,
                                              u'a.txt'))
        atc.add_files_to_working_copy()

        self.tempdir.check_all(
            '',
            'corpus/',
            'corpus/orig/',
            'corpus/orig/sma/',
            'corpus/orig/sma/ae/',
            'corpus/orig/sma/ae/c/',
            'corpus/orig/sma/ae/c/o/',
            'corpus/orig/sma/ae/c/o/f.txt',
            'corpus/orig/sma/ae/c/o/f.txt.xsl',
            'corpus/orig/sme/',
            'corpus/orig/sme/ae/',
            'corpus/orig/sme/ae/c/',
            'corpus/orig/sme/ae/c/o/',
            'corpus/orig/sme/ae/c/o/a.txt',
            'corpus/orig/sme/ae/c/o/a.txt.xsl',
            'corpus/orig/sme/ae/c/o/b.txt',
            'corpus/orig/sme/ae/c/o/c.txt',
            'corpus/orig/smj/',
            'corpus/orig/smj/ae/',
            'corpus/orig/smj/ae/c/',
            'corpus/orig/smj/ae/c/o/',
            'corpus/orig/smj/ae/c/o/f.txt',
            'corpus/orig/smj/ae/c/o/f.txt.xsl',
            'origdirectory/',
            'origdirectory/a.txt',
            'origdirectory/b.txt',
            'origdirectory/c.txt',
            'origdirectory/d.txt',
            'origdirectory/æ.txt')

        metadata = xslsetter.MetadataHandler(
            os.path.join(self.realcorpusdir, 'orig/sme/ae/c/o/a.txt.xsl'))
        self.assertEqual(metadata.get_variable('filename'), 'a.txt')
        self.assertEqual(metadata.get_variable('genre'), 'ae')
        self.assertEqual(metadata.get_variable('mainlang'), 'sme')

    def test_add_file_normalise_no_parallel(self):
        atc = adder.AddToCorpus(self.realcorpusdir, u'sme', u'æ/č/ö')
        atc.copy_file_to_corpus(os.path.join(self.origdirectory, u'æ.txt'))
        atc.add_files_to_working_copy()

        self.tempdir.check_all(
            '',
            'corpus/',
            'corpus/orig/',
            'corpus/orig/sma/',
            'corpus/orig/sma/ae/',
            'corpus/orig/sma/ae/c/',
            'corpus/orig/sma/ae/c/o/',
            'corpus/orig/sma/ae/c/o/f.txt',
            'corpus/orig/sma/ae/c/o/f.txt.xsl',
            'corpus/orig/sme/',
            'corpus/orig/sme/ae/',
            'corpus/orig/sme/ae/c/',
            'corpus/orig/sme/ae/c/o/',
            'corpus/orig/sme/ae/c/o/ae.txt',
            'corpus/orig/sme/ae/c/o/ae.txt.xsl',
            'corpus/orig/sme/ae/c/o/b.txt',
            'corpus/orig/sme/ae/c/o/c.txt',
            'corpus/orig/smj/',
            'corpus/orig/smj/ae/',
            'corpus/orig/smj/ae/c/',
            'corpus/orig/smj/ae/c/o/',
            'corpus/orig/smj/ae/c/o/f.txt',
            'corpus/orig/smj/ae/c/o/f.txt.xsl',
            'origdirectory/',
            'origdirectory/a.txt',
            'origdirectory/b.txt',
            'origdirectory/c.txt',
            'origdirectory/d.txt',
            'origdirectory/æ.txt')

        metadata = xslsetter.MetadataHandler(
            os.path.join(self.realcorpusdir, 'orig/sme/ae/c/o/ae.txt.xsl'))
        self.assertEqual(metadata.get_variable('filename'), u'æ.txt')
        self.assertEqual(metadata.get_variable('genre'), 'ae')
        self.assertEqual(metadata.get_variable('mainlang'), 'sme')

    def test_add_file_identical_name_no_parallel(self):
        atc = adder.AddToCorpus(self.realcorpusdir, u'sme', u'æ/č/ö')
        atc.copy_file_to_corpus(os.path.join(self.origdirectory, u'c.txt'))
        atc.add_files_to_working_copy()

        self.tempdir.check_all(
            '',
            'corpus/',
            'corpus/orig/',
            'corpus/orig/sma/',
            'corpus/orig/sma/ae/',
            'corpus/orig/sma/ae/c/',
            'corpus/orig/sma/ae/c/o/',
            'corpus/orig/sma/ae/c/o/f.txt',
            'corpus/orig/sma/ae/c/o/f.txt.xsl',
            'corpus/orig/sme/',
            'corpus/orig/sme/ae/',
            'corpus/orig/sme/ae/c/',
            'corpus/orig/sme/ae/c/o/',
            'corpus/orig/sme/ae/c/o/b.txt',
            'corpus/orig/sme/ae/c/o/c.txt',
            'corpus/orig/sme/ae/c/o/c_1.txt',
            'corpus/orig/sme/ae/c/o/c_1.txt.xsl',
            'corpus/orig/smj/',
            'corpus/orig/smj/ae/',
            'corpus/orig/smj/ae/c/',
            'corpus/orig/smj/ae/c/o/',
            'corpus/orig/smj/ae/c/o/f.txt',
            'corpus/orig/smj/ae/c/o/f.txt.xsl',
            'origdirectory/',
            'origdirectory/a.txt',
            'origdirectory/b.txt',
            'origdirectory/c.txt',
            'origdirectory/d.txt',
            'origdirectory/æ.txt')

        metadata = xslsetter.MetadataHandler(
            os.path.join(self.realcorpusdir, 'orig/sme/ae/c/o/c_1.txt.xsl'))
        self.assertEqual(metadata.get_variable('filename'), u'c.txt')
        self.assertEqual(metadata.get_variable('genre'), 'ae')
        self.assertEqual(metadata.get_variable('mainlang'), 'sme')

    def test_add_file_with_non_existing_parallel(self):
        atc = adder.AddToCorpus(self.realcorpusdir, u'sme', u'æ/č/ö')
        with self.assertRaises(adder.AdderException):
            atc.copy_file_to_corpus(
                os.path.join(self.origdirectory, u'd.txt'),
                parallelpath=os.path.join(self.realcorpusdir,
                                           'orig/smi/ae/c/o/f.txt'))

    def test_add_file_with_parallel(self):
        atc = adder.AddToCorpus(self.realcorpusdir, u'sme', u'æ/č/ö')
        atc.copy_file_to_corpus(os.path.join(self.origdirectory, u'd.txt'),
                                parallelpath=os.path.join(
                                    self.realcorpusdir,
                                    'orig/smj/ae/c/o/f.txt'))
        atc.add_files_to_working_copy()

        self.tempdir.check_all(
            '',
            'corpus/',
            'corpus/orig/',
            'corpus/orig/sma/',
            'corpus/orig/sma/ae/',
            'corpus/orig/sma/ae/c/',
            'corpus/orig/sma/ae/c/o/',
            'corpus/orig/sma/ae/c/o/f.txt',
            'corpus/orig/sma/ae/c/o/f.txt.xsl',
            'corpus/orig/sme/',
            'corpus/orig/sme/ae/',
            'corpus/orig/sme/ae/c/',
            'corpus/orig/sme/ae/c/o/',
            'corpus/orig/sme/ae/c/o/b.txt',
            'corpus/orig/sme/ae/c/o/c.txt',
            'corpus/orig/sme/ae/c/o/d.txt',
            'corpus/orig/sme/ae/c/o/d.txt.xsl',
            'corpus/orig/smj/',
            'corpus/orig/smj/ae/',
            'corpus/orig/smj/ae/c/',
            'corpus/orig/smj/ae/c/o/',
            'corpus/orig/smj/ae/c/o/f.txt',
            'corpus/orig/smj/ae/c/o/f.txt.xsl',
            'origdirectory/',
            'origdirectory/a.txt',
            'origdirectory/b.txt',
            'origdirectory/c.txt',
            'origdirectory/d.txt',
            'origdirectory/æ.txt')

        sme_metadata = xslsetter.MetadataHandler(
            os.path.join(self.realcorpusdir, 'orig/sme/ae/c/o/d.txt.xsl'))
        sme_parallels = sme_metadata.get_parallel_texts()
        self.assertEqual(sme_parallels['sma'], 'f.txt')
        self.assertEqual(sme_parallels['smj'], 'f.txt')

        smj_metadata = xslsetter.MetadataHandler(
            os.path.join(self.realcorpusdir, 'orig/smj/ae/c/o/f.txt.xsl'))
        smj_parallels = smj_metadata.get_parallel_texts()
        self.assertEqual(smj_parallels['sma'], 'f.txt')
        self.assertEqual(smj_parallels['sme'], 'd.txt')

        sma_metadata = xslsetter.MetadataHandler(
            os.path.join(self.realcorpusdir, 'orig/sma/ae/c/o/f.txt.xsl'))
        sma_parallels = sma_metadata.get_parallel_texts()
        self.assertEqual(sma_parallels['sme'], 'd.txt')
        self.assertEqual(sma_parallels['smj'], 'f.txt')


class TestDirectoryToCorpusWithDuplicates(unittest.TestCase):
    def setUp(self):
        self.tempdir = testfixtures.TempDirectory(ignore=['.git'])
        self.tempdir.write('origdirectory/a.txt', 'content of a')
        self.tempdir.write('origdirectory/æ.txt', 'content of b')
        self.tempdir.write('origdirectory/b.txt', 'content of b')
        self.tempdir.write('origdirectory/sub/c.txt', 'content of a')
        self.tempdir.write('origdirectory/sub/d.txt', 'content of d')
        self.tempdir.makedir('corpus/orig')
        self.origdirectory = os.path.join(self.tempdir.path,
                                          'origdirectory')
        self.realcorpusdir = os.path.join(self.tempdir.path,
                                          'corpus').decode('utf8')
        r = git.Repo.init(self.realcorpusdir)
        r.index.add(['orig'])
        r.index.commit('Added orig')

    def tearDown(self):
        self.tempdir.cleanup()

    def test_add_directory_with_duplicate(self):
        atc = adder.AddToCorpus(self.realcorpusdir, u'sme', u'æ/č/ö')
        with self.assertRaises(adder.AdderException):
            atc.copy_files_in_dir_to_corpus(self.origdirectory)


class TestDirectoryToCorpusWithoutDuplicates(unittest.TestCase):
    def setUp(self):
        self.tempdir = testfixtures.TempDirectory(ignore=['.git'])
        self.tempdir.write('origdirectory/a.txt', 'content of a')
        self.tempdir.write('origdirectory/æ.txt', 'content of æ')
        self.tempdir.write('origdirectory/b.txt', 'content of b')
        self.tempdir.write('origdirectory/sub/a.txt', 'content of sub/a')
        self.tempdir.write('origdirectory/sub/c.txt', 'content of c')
        self.tempdir.write('origdirectory/sub/d.txt', 'content of d')
        self.tempdir.makedir('corpus/orig')
        self.origdirectory = os.path.join(self.tempdir.path,
                                          'origdirectory')
        self.realcorpusdir = os.path.join(self.tempdir.path,
                                          'corpus').decode('utf8')
        r = git.Repo.init(self.realcorpusdir)
        r.index.add(['orig'])
        r.index.commit('Added orig')

    def tearDown(self):
        self.tempdir.cleanup()

    def test_add_directory_without_duplicate(self):
        atc = adder.AddToCorpus(self.realcorpusdir, u'sme', u'æ/č/ö')
        atc.copy_files_in_dir_to_corpus(self.origdirectory)
        atc.add_files_to_working_copy()

        self.tempdir.check_all(
            '',
            'corpus/',
            'corpus/orig/',
            'corpus/orig/sme/',
            'corpus/orig/sme/ae/',
            'corpus/orig/sme/ae/c/',
            'corpus/orig/sme/ae/c/o/',
            'corpus/orig/sme/ae/c/o/a.txt',
            'corpus/orig/sme/ae/c/o/a.txt.xsl',
            'corpus/orig/sme/ae/c/o/a_1.txt',
            'corpus/orig/sme/ae/c/o/a_1.txt.xsl',
            'corpus/orig/sme/ae/c/o/ae.txt',
            'corpus/orig/sme/ae/c/o/ae.txt.xsl',
            'corpus/orig/sme/ae/c/o/b.txt',
            'corpus/orig/sme/ae/c/o/b.txt.xsl',
            'corpus/orig/sme/ae/c/o/c.txt',
            'corpus/orig/sme/ae/c/o/c.txt.xsl',
            'corpus/orig/sme/ae/c/o/d.txt',
            'corpus/orig/sme/ae/c/o/d.txt.xsl',
            'origdirectory/',
            'origdirectory/a.txt',
            'origdirectory/b.txt',
            'origdirectory/sub/',
            'origdirectory/sub/a.txt',
            'origdirectory/sub/c.txt',
            'origdirectory/sub/d.txt',
            'origdirectory/æ.txt')
