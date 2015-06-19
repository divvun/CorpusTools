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
        self.tempdir.makedir('corpus/orig')
        self.tempdir.write('corpus/orig/sme/ae/c/o/b.txt', 'content of b')
        self.realcorpusdir = os.path.join(self.tempdir.path,
                                          'corpus').decode('utf8')
        self.origdirectory = os.path.join(self.tempdir.path,
                                          'origdirectory')

        r = git.Repo.init(self.realcorpusdir)
        r.index.add(['orig'])
        r.index.commit('Added orig')

    def tearDown(self):
        self.tempdir.cleanup()

    def test_add_file_no_normalise_no_parallel(self):
        aftc = adder.AddFileToCorpus(self.realcorpusdir, u'sme', u'æ/č/ö',
                                     os.path.join(self.origdirectory, u'a.txt'))
        aftc.add_file_to_corpus()

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
            'corpus/orig/sme/ae/c/o/b.txt',
            'origdirectory/',
            'origdirectory/a.txt',
            'origdirectory/b.txt',
            'origdirectory/æ.txt')

        metadata = xslsetter.MetadataHandler(
            os.path.join(self.realcorpusdir, 'orig/sme/ae/c/o/a.txt.xsl'))
        self.assertEqual(metadata.get_variable('filename'), 'a.txt')
        self.assertEqual(metadata.get_variable('genre'), 'ae')
        self.assertEqual(metadata.get_variable('mainlang'), 'sme')

    def test_add_file_normalise_no_parallel(self):
        aftc = adder.AddFileToCorpus(self.realcorpusdir, u'sme', u'æ/č/ö',
                                     os.path.join(self.origdirectory, u'æ.txt'))
        aftc.add_file_to_corpus()

        self.tempdir.check_all(
            '',
            'corpus/',
            'corpus/orig/',
            'corpus/orig/sme/',
            'corpus/orig/sme/ae/',
            'corpus/orig/sme/ae/c/',
            'corpus/orig/sme/ae/c/o/',
            'corpus/orig/sme/ae/c/o/ae.txt',
            'corpus/orig/sme/ae/c/o/ae.txt.xsl',
            'corpus/orig/sme/ae/c/o/b.txt',
            'origdirectory/',
            'origdirectory/a.txt',
            'origdirectory/b.txt',
            'origdirectory/æ.txt')

        metadata = xslsetter.MetadataHandler(
            os.path.join(self.realcorpusdir, 'orig/sme/ae/c/o/ae.txt.xsl'))
        self.assertEqual(metadata.get_variable('filename'), u'æ.txt')
        self.assertEqual(metadata.get_variable('genre'), 'ae')
        self.assertEqual(metadata.get_variable('mainlang'), 'sme')

    def test_add_file_duplicate_no_parallel(self):
        with self.assertRaises(UserWarning):
            aftc = adder.AddFileToCorpus(self.realcorpusdir, u'sme', u'æ/č/ö',
                                        os.path.join(self.origdirectory, u'b.txt'))
