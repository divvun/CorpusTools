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

import os
import unittest

import git
import testfixtures

from corpustools import namechanger
from corpustools import xslsetter

here = os.path.dirname(__file__)


class TestFilenameToAscii(unittest.TestCase):
    '''Test the normalise_filename function'''
    def test_none_ascii_lower(self):
        oldname = u'ášŧŋđžčåøæöäï+'
        want = u'astngdzcaoaeoai_'

        self.assertEqual(namechanger.normalise_filename(oldname), want)

    def test_none_ascii_upper(self):
        oldname = u'ÁŠŦŊĐŽČÅØÆÖÄÏ+'
        want = u'astngdzcaoaeoai_'

        self.assertEqual(namechanger.normalise_filename(oldname), want)

    def test_none_ascii_blabla(self):
        oldname = u'ášŧŋđŽČÅØÆÖÄï+'
        want = u'astngdzcaoaeoai_'

        self.assertEqual(namechanger.normalise_filename(oldname), want)

    def test_own_name_with_only_ascii(self):
        oldname = u'YoullNeverWalkAlone'
        want = u'youllneverwalkalone'

        self.assertEqual(namechanger.normalise_filename(oldname), want)

    def test_own_name_with_only_ascii_and_space(self):
        oldname = u'Youll Never Walk Alone'
        want = u'youll_never_walk_alone'

        self.assertEqual(namechanger.normalise_filename(oldname), want)

    def test_own_name_with_ascii_and_space_and_apostrophe(self):
        oldname = u"You'll Never Walk Alone"
        want = u'you_ll_never_walk_alone'

        self.assertEqual(namechanger.normalise_filename(oldname), want)

    def test_own_name_with_non_ascii(self):
        oldname = u'Šaddágo beaivi vai idja'
        want = u'saddago_beaivi_vai_idja'

        self.assertEqual(namechanger.normalise_filename(oldname), want)

    def test_own_name_with_quote(self):
        oldname = u'aba".txt'
        want = u'aba_.txt'

        self.assertEqual(namechanger.normalise_filename(oldname), want)

    def test_own_name_with_lt(self):
        oldname = u'aba<.txt'
        want = u'aba_.txt'

        self.assertEqual(namechanger.normalise_filename(oldname), want)

    def test_own_name_with_gt(self):
        oldname = u'aba>.txt'
        want = u'aba_.txt'

        self.assertEqual(namechanger.normalise_filename(oldname), want)

    def test_own_name_with_complete_path(self):
        oldname = u'j/a/b/c/aba>.txt'

        self.assertRaises(namechanger.NamechangerException,
                          namechanger.normalise_filename, oldname)


class TestAreDuplicates(unittest.TestCase):
    '''Test the are_duplicates function'''
    def test_are_duplicate_nonexisting_file(self):
        self.assertFalse(namechanger.are_duplicates('old.txt', 'new.txt'))

    def test_are_duplicate_equal_files(self):
        self.assertTrue(namechanger.are_duplicates(
            os.path.join(here, 'name_changer_data/orig/sme/admin/other_files',
                         'old_dupe.txt'),
            os.path.join(here, 'name_changer_data/orig/sme/admin/other_files',
                         'new_dupe.txt')))

    def test_are_duplicate_unequal_files(self):
        self.assertFalse(namechanger.are_duplicates(
            os.path.join(here, 'name_changer_data/orig/sme/admin/other_files',
                         'old_dupe.txt'),
            os.path.join(here, 'name_changer_data/orig/sme/admin/other_files',
                         'new_none_dupe.txt')))


class TestComputeNewBasename(unittest.TestCase):
    def test_compute_new_basename_duplicates(self):
        '''What happens when the wanted name is taken, and a duplicate'''
        with self.assertRaises(UserWarning):
            namechanger.compute_new_basename(
                os.path.join(here,
                             'name_changer_data/orig/sme/admin/other_files',
                             'old_dupe.txt'),
                os.path.join(here,
                             'name_changer_data/orig/sme/admin/other_files',
                             'new_dupe.txt'))

    def test_compute_new_basename_same_name(self):
        '''What happens when the wanted name is taken, but not duplicate'''
        self.assertEqual(
            namechanger.compute_new_basename(
                os.path.join(here,
                             'name_changer_data/orig/sme/admin/other_files',
                             'new_none_düpe.txt'),
                os.path.join(here,
                             'name_changer_data/orig/sme/admin/other_files',
                             'new_none_dupe.txt')),
            os.path.join(here, 'name_changer_data', 'orig', 'sme', 'admin',
                         'other_files', 'new_none_dupe_1.txt')
            )


class TestComputeMovepairs(unittest.TestCase):
    def setUp(self):
        self.tempdir = testfixtures.TempDirectory()
        self.tempdir.makedir('orig/sme/ficti/sub')
        self.tempdir.makedir('orig/smj/ficti/sub')
        self.tempdir.makedir('orig/sma/ficti/sub')

    def tearDown(self):
        self.tempdir.cleanup()

    def test_compute_movepairs_1(self):
        '''newpath does not exist, no parallels'''
        mc = namechanger.MovepairComputer()
        mc.compute_all_movepairs(
            os.path.join(self.tempdir.path,
                         'orig/sme/ficti/sub/a.txt').decode('utf8'),
            os.path.join(self.tempdir.path,
                         'orig/sme/ficti/sub/b.txt').decode('utf8'))

        testfixtures.compare(mc.filepairs, [
            namechanger.PathPair(
                os.path.join(self.tempdir.path,
                             'orig/sme/ficti/sub/a.txt').decode('utf8'),
                os.path.join(self.tempdir.path,
                             'orig/sme/ficti/sub/b.txt').decode('utf8'))])

    def test_compute_movepairs_2(self):
        '''newpath does not exist, needs normalisation, no parallels'''
        mc = namechanger.MovepairComputer()
        mc.compute_all_movepairs(
            os.path.join(self.tempdir.path,
                         'orig/sme/ficti/sub/æ.txt').decode('utf8'),
            os.path.join(self.tempdir.path,
                         'orig/sme/ficti/sub/æ.txt').decode('utf8'))

        testfixtures.compare(mc.filepairs, [
            namechanger.PathPair(
                os.path.join(self.tempdir.path,
                             'orig/sme/ficti/sub/æ.txt').decode('utf8'),
                os.path.join(self.tempdir.path,
                             'orig/sme/ficti/sub/ae.txt').decode('utf8'))])

    def test_compute_movepairs_3(self):
        '''newpath exists, not duplicate, no parallels'''
        self.tempdir.write('orig/sme/ficti/sub/c.txt', 'c content')
        self.tempdir.write('orig/sme/ficti/sub/d.txt', 'd content')

        mc = namechanger.MovepairComputer()
        mc.compute_all_movepairs(
            os.path.join(self.tempdir.path,
                         'orig/sme/ficti/sub/c.txt').decode('utf8'),
            os.path.join(self.tempdir.path,
                         'orig/sme/ficti/sub/d.txt').decode('utf8'))

        testfixtures.compare(mc.filepairs, [
            namechanger.PathPair(
                os.path.join(self.tempdir.path,
                             'orig/sme/ficti/sub/c.txt').decode('utf8'),
                os.path.join(self.tempdir.path,
                             'orig/sme/ficti/sub/d_1.txt').decode('utf8'))])

    def test_compute_movepairs_4(self):
        '''newpath exists, duplicate, no parallels'''
        self.tempdir.write('orig/sme/ficti/sub/c.txt', 'c content')
        self.tempdir.write('orig/sme/ficti/sub/e.txt', 'c content')

        with self.assertRaises(UserWarning):
            mc = namechanger.MovepairComputer()
            mc.compute_all_movepairs(
                os.path.join(self.tempdir.path,
                             'orig/sme/ficti/sub/c.txt').decode('utf8'),
                os.path.join(self.tempdir.path,
                             'orig/sme/ficti/sub/e.txt').decode('utf8'))

    def test_compute_movepairs_5(self):
        '''move to same directory, with parallels'''
        sme_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/sme/ficti/sub/f.txt.xsl'),
            create=True)
        sme_metadata.set_variable('mainlang', 'sme')
        sme_metadata.set_parallel_text('smj', 'f.txt')
        sme_metadata.set_parallel_text('sma', 'f.txt')
        sme_metadata.write_file()

        smj_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/smj/ficti/sub/f.txt.xsl'),
            create=True)
        smj_metadata.set_variable('mainlang', 'smj')
        smj_metadata.set_parallel_text('sme', 'f.txt')
        smj_metadata.set_parallel_text('sma', 'f.txt')
        smj_metadata.write_file()

        sma_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/sma/ficti/sub/f.txt.xsl'),
            create=True)
        sma_metadata.set_variable('mainlang', 'sma')
        sma_metadata.set_parallel_text('sme', 'f.txt')
        sma_metadata.set_parallel_text('smj', 'f.txt')
        sma_metadata.write_file()

        mc = namechanger.MovepairComputer()
        mc.compute_all_movepairs(
            os.path.join(self.tempdir.path,
                         'orig/sme/ficti/sub/f.txt').decode('utf8'),
            os.path.join(self.tempdir.path,
                         'orig/sme/ficti/sub/g.txt').decode('utf8'))

        testfixtures.compare(mc.filepairs, [
            namechanger.PathPair(
                os.path.join(self.tempdir.path,
                             'orig/sme/ficti/sub/f.txt').decode('utf8'),
                os.path.join(self.tempdir.path,
                             'orig/sme/ficti/sub/g.txt').decode('utf8'))])

    def test_compute_movepairs_6(self):
        '''move to different subdir, with parallels'''
        sme_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/sme/ficti/sub/f.txt.xsl'),
            create=True)
        sme_metadata.set_variable('mainlang', 'sme')
        sme_metadata.set_parallel_text('smj', 'f.txt')
        sme_metadata.set_parallel_text('sma', 'f.txt')
        sme_metadata.write_file()

        smj_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/smj/ficti/sub/f.txt.xsl'),
            create=True)
        smj_metadata.set_variable('mainlang', 'smj')
        smj_metadata.set_parallel_text('sme', 'f.txt')
        smj_metadata.set_parallel_text('sma', 'f.txt')
        smj_metadata.write_file()

        sma_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/sma/ficti/sub/f.txt.xsl'),
            create=True)
        sma_metadata.set_variable('mainlang', 'sma')
        sma_metadata.set_parallel_text('sme', 'f.txt')
        sma_metadata.set_parallel_text('smj', 'f.txt')
        sma_metadata.write_file()

        mc = namechanger.MovepairComputer()
        mc.compute_all_movepairs(
            os.path.join(self.tempdir.path,
                         'orig/sme/ficti/sub/f.txt').decode('utf8'),
            os.path.join(self.tempdir.path,
                         'orig/sme/ficti/bub/g.txt').decode('utf8'))

        testfixtures.compare(mc.filepairs, [
            namechanger.PathPair(
                os.path.join(self.tempdir.path,
                             'orig/sme/ficti/sub/f.txt').decode('utf8'),
                os.path.join(self.tempdir.path,
                             'orig/sme/ficti/bub/g.txt').decode('utf8')),
            namechanger.PathPair(
                os.path.join(self.tempdir.path,
                             'orig/smj/ficti/sub/f.txt').decode('utf8'),
                os.path.join(self.tempdir.path,
                             'orig/smj/ficti/bub/f.txt').decode('utf8')),
            namechanger.PathPair(
                os.path.join(self.tempdir.path,
                             'orig/sma/ficti/sub/f.txt').decode('utf8'),
                os.path.join(self.tempdir.path,
                             'orig/sma/ficti/bub/f.txt').decode('utf8'))])

    def test_compute_movepairs_7(self):
        '''move to different genre, with parallels'''
        sme_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/sme/ficti/sub/f.txt.xsl'),
            create=True)
        sme_metadata.set_variable('mainlang', 'sme')
        sme_metadata.set_parallel_text('smj', 'f.txt')
        sme_metadata.set_parallel_text('sma', 'f.txt')
        sme_metadata.write_file()

        smj_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/smj/ficti/sub/f.txt.xsl'),
            create=True)
        smj_metadata.set_variable('mainlang', 'smj')
        smj_metadata.set_parallel_text('sme', 'f.txt')
        smj_metadata.set_parallel_text('sma', 'f.txt')
        smj_metadata.write_file()

        sma_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/sma/ficti/sub/f.txt.xsl'),
            create=True)
        sma_metadata.set_variable('mainlang', 'sma')
        sma_metadata.set_parallel_text('sme', 'f.txt')
        sma_metadata.set_parallel_text('smj', 'f.txt')
        sma_metadata.write_file()

        mc = namechanger.MovepairComputer()
        mc.compute_all_movepairs(
            os.path.join(self.tempdir.path,
                         'orig/sme/ficti/sub/f.txt').decode('utf8'),
            os.path.join(self.tempdir.path,
                         'orig/sme/facta/sub/g.txt').decode('utf8'))

        testfixtures.compare(mc.filepairs, [
            namechanger.PathPair(
                os.path.join(self.tempdir.path,
                             'orig/sme/ficti/sub/f.txt').decode('utf8'),
                os.path.join(self.tempdir.path,
                             'orig/sme/facta/sub/g.txt').decode('utf8')),
            namechanger.PathPair(
                os.path.join(self.tempdir.path,
                             'orig/smj/ficti/sub/f.txt').decode('utf8'),
                os.path.join(self.tempdir.path,
                             'orig/smj/facta/sub/f.txt').decode('utf8')),
            namechanger.PathPair(
                os.path.join(self.tempdir.path,
                             'orig/sma/ficti/sub/f.txt').decode('utf8'),
                os.path.join(self.tempdir.path,
                             'orig/sma/facta/sub/f.txt').decode('utf8'))])

    def test_compute_movepairs_8(self):
        '''move to different genre, one parallel needs normalisation'''
        sme_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/sme/ficti/sub/f.txt.xsl'),
            create=True)
        sme_metadata.set_variable('mainlang', 'sme')
        sme_metadata.set_parallel_text('smj', u'ø.txt')
        sme_metadata.set_parallel_text('sma', 'f.txt')
        sme_metadata.write_file()

        smj_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/smj/ficti/sub/ø.txt.xsl'),
            create=True)
        smj_metadata.set_variable('mainlang', 'smj')
        smj_metadata.set_parallel_text('sme', 'f.txt')
        smj_metadata.set_parallel_text('sma', 'f.txt')
        smj_metadata.write_file()

        sma_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/sma/ficti/sub/f.txt.xsl'),
            create=True)
        sma_metadata.set_variable('mainlang', 'sma')
        sma_metadata.set_parallel_text('sme', 'f.txt')
        sma_metadata.set_parallel_text('smj', u'ø.txt')
        sma_metadata.write_file()

        mc = namechanger.MovepairComputer()
        mc.compute_all_movepairs(
            os.path.join(self.tempdir.path,
                         'orig/sme/ficti/sub/f.txt').decode('utf8'),
            os.path.join(self.tempdir.path,
                         'orig/sme/facta/sub/g.txt').decode('utf8'))

        testfixtures.compare(mc.filepairs, [
            namechanger.PathPair(
                os.path.join(self.tempdir.path,
                             'orig/sme/ficti/sub/f.txt').decode('utf8'),
                os.path.join(self.tempdir.path,
                             'orig/sme/facta/sub/g.txt').decode('utf8')),
            namechanger.PathPair(
                os.path.join(self.tempdir.path,
                             'orig/smj/ficti/sub/ø.txt').decode('utf8'),
                os.path.join(self.tempdir.path,
                             'orig/smj/facta/sub/o.txt').decode('utf8')),
            namechanger.PathPair(
                os.path.join(self.tempdir.path,
                             'orig/sma/ficti/sub/f.txt').decode('utf8'),
                os.path.join(self.tempdir.path,
                             'orig/sma/facta/sub/f.txt').decode('utf8'))])


class TestCorpusFileMover(unittest.TestCase):
    def setUp(self):
        self.tempdir = testfixtures.TempDirectory(ignore=['.git'])

        self.tempdir.makedir('orig/sme/ficti/sub')
        self.tempdir.write('orig/sme/ficti/sub/f.txt', 'content of f')
        sme_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/sme/ficti/sub/f.txt.xsl'),
            create=True)
        sme_metadata.set_variable('mainlang', 'sme')
        sme_metadata.set_parallel_text('smj', u'ø.txt')
        sme_metadata.set_parallel_text('sma', 'f.txt')
        sme_metadata.write_file()
        self.tempdir.makedir('prestable/converted/sme/ficti/sub')
        self.tempdir.write('prestable/converted/sme/ficti/sub/f.txt.xml',
                           'converted content of f')
        self.tempdir.makedir('prestable/tmx/sme2smj/ficti/sub')
        self.tempdir.write('prestable/tmx/sme2smj/ficti/sub/f.txt.tmx',
                           'parallelised content of f')
        self.tempdir.makedir('prestable/tmx/sme2sma/ficti/sub')
        self.tempdir.write('prestable/tmx/sme2sma/ficti/sub/f.txt.tmx',
                           'parallelised content of f')

        r = git.Repo.init(self.tempdir.path)
        r.index.add(['orig', 'prestable'])
        r.index.commit('Added orig and prestable')

    def tearDown(self):
        self.tempdir.cleanup()

    def test_move_orig(self):
        cfm = namechanger.CorpusFileMover(
            os.path.join(self.tempdir.path, 'orig/sme/ficti/sub/f.txt'),
            os.path.join(self.tempdir.path, 'orig/sme/facta/bub/g.txt'))
        cfm.move_files()
        self.tempdir.check_all(
            '',
            'orig/',
            'orig/sme/',
            'orig/sme/facta/',
            'orig/sme/facta/bub/',
            'orig/sme/facta/bub/g.txt',
            'orig/sme/facta/bub/g.txt.xsl',
            'orig/sme/ficti/',
            'orig/sme/ficti/sub/',
            'prestable/',
            'prestable/converted/',
            'prestable/converted/sme/',
            'prestable/converted/sme/facta/',
            'prestable/converted/sme/facta/bub/',
            'prestable/converted/sme/facta/bub/g.txt.xml',
            'prestable/converted/sme/ficti/',
            'prestable/converted/sme/ficti/sub/',
            'prestable/tmx/',
            'prestable/tmx/sme2sma/',
            'prestable/tmx/sme2sma/facta/',
            'prestable/tmx/sme2sma/facta/bub/',
            'prestable/tmx/sme2sma/facta/bub/g.txt.tmx',
            'prestable/tmx/sme2sma/ficti/',
            'prestable/tmx/sme2sma/ficti/sub/',
            'prestable/tmx/sme2smj/',
            'prestable/tmx/sme2smj/facta/',
            'prestable/tmx/sme2smj/facta/bub/',
            'prestable/tmx/sme2smj/facta/bub/g.txt.tmx',
            'prestable/tmx/sme2smj/ficti/',
            'prestable/tmx/sme2smj/ficti/sub/')


class TestCorpusFilesetMetadataUpdater1(unittest.TestCase):
    def setUp(self):
        self.tempdir = testfixtures.TempDirectory(ignore=['.git'])

        self.tempdir.makedir('orig/sme/ficti/sub')
        self.tempdir.write('orig/sme/ficti/sub/f.txt', 'content of f')
        sme_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/sme/ficti/sub/f.txt.xsl'),
            create=True)
        sme_metadata.set_variable('mainlang', 'sme')
        sme_metadata.set_parallel_text('smj', u'ø.txt')
        sme_metadata.set_parallel_text('sma', 'f.txt')
        sme_metadata.write_file()
        self.tempdir.makedir('prestable/converted/sme/ficti/sub')
        self.tempdir.write('prestable/converted/sme/ficti/sub/f.txt.xml',
                           'converted content of f')
        self.tempdir.makedir('prestable/tmx/sme2smj/ficti/sub')
        self.tempdir.write('prestable/tmx/sme2smj/ficti/sub/f.txt.tmx',
                           'parallelised content of f')
        self.tempdir.makedir('prestable/tmx/sme2sma/ficti/sub')
        self.tempdir.write('prestable/tmx/sme2sma/ficti/sub/f.txt.tmx',
                           'parallelised content of f')
        self.tempdir.makedir('prestable/toktmx/sme2smj/ficti/sub')
        self.tempdir.write('prestable/toktmx/sme2smj/ficti/sub/f.txt.toktmx',
                           'parallelised content of f')
        self.tempdir.makedir('prestable/toktmx/sme2sma/ficti/sub')
        self.tempdir.write('prestable/toktmx/sme2sma/ficti/sub/f.txt.toktmx',
                           'parallelised content of f')

        self.tempdir.makedir('orig/smj/ficti/sub')
        self.tempdir.write('orig/smj/ficti/sub/ø.txt', 'content of ø')
        smj_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/smj/ficti/sub/ø.txt.xsl'),
            create=True)
        smj_metadata.set_variable('mainlang', 'smj')
        smj_metadata.set_variable('translated_from', 'sme')
        smj_metadata.set_parallel_text('sme', 'f.txt')
        smj_metadata.set_parallel_text('sma', 'f.txt')
        smj_metadata.write_file()
        self.tempdir.makedir('prestable/converted/smj/ficti/sub')
        self.tempdir.write('prestable/converted/smj/ficti/sub/ø.txt.xml',
                           'converted content of ø')

        self.tempdir.makedir('orig/sma/ficti/sub')
        self.tempdir.write('orig/sma/ficti/sub/f.txt', 'content of f')
        sma_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/sma/ficti/sub/f.txt.xsl'),
            create=True)
        sma_metadata.set_variable('mainlang', 'sma')
        sma_metadata.set_variable('translated_from', 'sme')
        sma_metadata.set_parallel_text('sme', 'f.txt')
        sma_metadata.set_parallel_text('smj', u'ø.txt')
        sma_metadata.write_file()
        self.tempdir.makedir('prestable/converted/sma/ficti/sub')
        self.tempdir.write('prestable/converted/sma/ficti/sub/f.txt.xml',
                           'converted content of f')

        r = git.Repo.init(self.tempdir.path)
        r.index.add(['orig', 'prestable'])
        r.index.commit('Added orig and prestable')

        oldpath = os.path.join(self.tempdir.path,
                               'orig/sme/ficti/sub/f.txt').decode('utf8')
        newpath = os.path.join(self.tempdir.path,
                               'orig/sme/facta/bub/g.txt').decode('utf8')
        cfm = namechanger.CorpusFilesetMoverAndUpdater(oldpath, newpath)
        cfm.move_files()
        cfm.update_own_metadata()
        cfm.update_parallel_files_metadata()

    def tearDown(self):
        self.tempdir.cleanup()

    def test_move_fileset(self):
        self.tempdir.check_all(
            '',
            'orig/',
            'orig/sma/',
            'orig/sma/facta/',
            'orig/sma/facta/bub/',
            'orig/sma/facta/bub/f.txt',
            'orig/sma/facta/bub/f.txt.xsl',
            'orig/sma/ficti/',
            'orig/sma/ficti/sub/',
            'orig/sme/',
            'orig/sme/facta/',
            'orig/sme/facta/bub/',
            'orig/sme/facta/bub/g.txt',
            'orig/sme/facta/bub/g.txt.xsl',
            'orig/sme/ficti/',
            'orig/sme/ficti/sub/',
            'orig/smj/',
            'orig/smj/facta/',
            'orig/smj/facta/bub/',
            'orig/smj/facta/bub/o.txt',
            'orig/smj/facta/bub/o.txt.xsl',
            'orig/smj/ficti/',
            'orig/smj/ficti/sub/',
            'prestable/',
            'prestable/converted/',
            'prestable/converted/sma/',
            'prestable/converted/sma/facta/',
            'prestable/converted/sma/facta/bub/',
            'prestable/converted/sma/facta/bub/f.txt.xml',
            'prestable/converted/sma/ficti/',
            'prestable/converted/sma/ficti/sub/',
            'prestable/converted/sme/',
            'prestable/converted/sme/facta/',
            'prestable/converted/sme/facta/bub/',
            'prestable/converted/sme/facta/bub/g.txt.xml',
            'prestable/converted/sme/ficti/',
            'prestable/converted/sme/ficti/sub/',
            'prestable/converted/smj/',
            'prestable/converted/smj/facta/',
            'prestable/converted/smj/facta/bub/',
            'prestable/converted/smj/facta/bub/o.txt.xml',
            'prestable/converted/smj/ficti/',
            'prestable/converted/smj/ficti/sub/',
            'prestable/tmx/',
            'prestable/tmx/sme2sma/',
            'prestable/tmx/sme2sma/facta/',
            'prestable/tmx/sme2sma/facta/bub/',
            'prestable/tmx/sme2sma/facta/bub/g.txt.tmx',
            'prestable/tmx/sme2sma/ficti/',
            'prestable/tmx/sme2sma/ficti/sub/',
            'prestable/tmx/sme2smj/',
            'prestable/tmx/sme2smj/facta/',
            'prestable/tmx/sme2smj/facta/bub/',
            'prestable/tmx/sme2smj/facta/bub/g.txt.tmx',
            'prestable/tmx/sme2smj/ficti/',
            'prestable/tmx/sme2smj/ficti/sub/',
            'prestable/toktmx/',
            'prestable/toktmx/sme2sma/',
            'prestable/toktmx/sme2sma/facta/',
            'prestable/toktmx/sme2sma/facta/bub/',
            'prestable/toktmx/sme2sma/facta/bub/g.txt.toktmx',
            'prestable/toktmx/sme2sma/ficti/',
            'prestable/toktmx/sme2sma/ficti/sub/',
            'prestable/toktmx/sme2smj/',
            'prestable/toktmx/sme2smj/facta/',
            'prestable/toktmx/sme2smj/facta/bub/',
            'prestable/toktmx/sme2smj/facta/bub/g.txt.toktmx',
            'prestable/toktmx/sme2smj/ficti/',
            'prestable/toktmx/sme2smj/ficti/sub/')

    def test_update_metadata(self):
        sme_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/sme/facta/bub/g.txt.xsl'))
        self.assertEqual(sme_metadata.get_variable('genre'), 'facta')
        self.assertEqual(sme_metadata.get_variable('mainlang'), 'sme')
        sme_parallels = sme_metadata.get_parallel_texts()
        self.assertEqual(sme_parallels['smj'], 'o.txt')
        self.assertEqual(sme_parallels['sma'], 'f.txt')

        sma_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/sma/facta/bub/f.txt.xsl'))
        self.assertEqual(sma_metadata.get_variable('genre'), 'facta')
        sma_parallels = sma_metadata.get_parallel_texts()
        self.assertEqual(sma_parallels['smj'], 'o.txt')
        self.assertEqual(sma_parallels['sme'], 'g.txt')

        smj_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/smj/facta/bub/o.txt.xsl'))
        self.assertEqual(smj_metadata.get_variable('genre'), 'facta')
        smj_parallels = smj_metadata.get_parallel_texts()
        self.assertEqual(smj_parallels['sme'], 'g.txt')
        self.assertEqual(smj_parallels['sma'], 'f.txt')


class TestCorpusFilesetMetadataUpdater2(unittest.TestCase):
    def setUp(self):
        self.tempdir = testfixtures.TempDirectory(ignore=['.git'])

        self.tempdir.makedir('orig/sme/ficti/sub')
        self.tempdir.write('orig/sme/ficti/sub/f.txt', 'content of f')
        sme_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/sme/ficti/sub/f.txt.xsl'),
            create=True)
        sme_metadata.set_variable('mainlang', 'sme')
        sme_metadata.set_parallel_text('smj', u'ø.txt')
        sme_metadata.set_parallel_text('sma', 'f.txt')
        sme_metadata.write_file()
        self.tempdir.makedir('prestable/converted/sme/ficti/sub')
        self.tempdir.write('prestable/converted/sme/ficti/sub/f.txt.xml',
                           'converted content of f')
        self.tempdir.makedir('prestable/tmx/sme2smj/ficti/sub')
        self.tempdir.write('prestable/tmx/sme2smj/ficti/sub/f.txt.tmx',
                           'parallelised content of f')
        self.tempdir.makedir('prestable/tmx/sme2sma/ficti/sub')
        self.tempdir.write('prestable/tmx/sme2sma/ficti/sub/f.txt.tmx',
                           'parallelised content of f')
        self.tempdir.makedir('prestable/toktmx/sme2smj/ficti/sub')
        self.tempdir.write('prestable/toktmx/sme2smj/ficti/sub/f.txt.toktmx',
                           'parallelised content of f')
        self.tempdir.makedir('prestable/toktmx/sme2sma/ficti/sub')
        self.tempdir.write('prestable/toktmx/sme2sma/ficti/sub/f.txt.toktmx',
                           'parallelised content of f')

        self.tempdir.makedir('orig/smj/ficti/sub')
        self.tempdir.write('orig/smj/ficti/sub/ø.txt', 'content of ø')
        smj_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/smj/ficti/sub/ø.txt.xsl'),
            create=True)
        smj_metadata.set_variable('mainlang', 'smj')
        smj_metadata.set_variable('translated_from', 'sme')
        smj_metadata.set_parallel_text('sme', 'f.txt')
        smj_metadata.set_parallel_text('sma', 'f.txt')
        smj_metadata.write_file()
        self.tempdir.makedir('prestable/converted/smj/ficti/sub')
        self.tempdir.write('prestable/converted/smj/ficti/sub/ø.txt.xml',
                           'converted content of ø')

        self.tempdir.makedir('orig/sma/ficti/sub')
        self.tempdir.write('orig/sma/ficti/sub/f.txt', 'content of f')
        sma_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/sma/ficti/sub/f.txt.xsl'),
            create=True)
        sma_metadata.set_variable('mainlang', 'sma')
        sma_metadata.set_variable('translated_from', 'sme')
        sma_metadata.set_parallel_text('sme', 'f.txt')
        sma_metadata.set_parallel_text('smj', u'ø.txt')
        sma_metadata.write_file()
        self.tempdir.makedir('prestable/converted/sma/ficti/sub')
        self.tempdir.write('prestable/converted/sma/ficti/sub/f.txt.xml',
                           'converted content of f')

        r = git.Repo.init(self.tempdir.path)
        r.index.add(['orig', 'prestable'])
        r.index.commit('Added orig and prestable')

        oldpath = os.path.join(self.tempdir.path,
                               'orig/sme/ficti/sub/f.txt').decode('utf8')
        newpath = os.path.join(self.tempdir.path,
                               'orig/smn/facta/bub/g.txt').decode('utf8')
        cfm = namechanger.CorpusFilesetMoverAndUpdater(oldpath, newpath)
        cfm.move_files()
        cfm.update_own_metadata()
        cfm.update_parallel_files_metadata()

    def tearDown(self):
        self.tempdir.cleanup()

    def test_move_fileset(self):
        self.tempdir.check_all(
            '',
            'orig/',
            'orig/sma/',
            'orig/sma/facta/',
            'orig/sma/facta/bub/',
            'orig/sma/facta/bub/f.txt',
            'orig/sma/facta/bub/f.txt.xsl',
            'orig/sma/ficti/',
            'orig/sma/ficti/sub/',
            'orig/sme/',
            'orig/sme/ficti/',
            'orig/sme/ficti/sub/',
            'orig/smj/',
            'orig/smj/facta/',
            'orig/smj/facta/bub/',
            'orig/smj/facta/bub/o.txt',
            'orig/smj/facta/bub/o.txt.xsl',
            'orig/smj/ficti/',
            'orig/smj/ficti/sub/',
            'orig/smn/',
            'orig/smn/facta/',
            'orig/smn/facta/bub/',
            'orig/smn/facta/bub/g.txt',
            'orig/smn/facta/bub/g.txt.xsl',
            'prestable/',
            'prestable/converted/',
            'prestable/converted/sma/',
            'prestable/converted/sma/facta/',
            'prestable/converted/sma/facta/bub/',
            'prestable/converted/sma/facta/bub/f.txt.xml',
            'prestable/converted/sma/ficti/',
            'prestable/converted/sma/ficti/sub/',
            'prestable/converted/sme/',
            'prestable/converted/sme/ficti/',
            'prestable/converted/sme/ficti/sub/',
            'prestable/converted/smj/',
            'prestable/converted/smj/facta/',
            'prestable/converted/smj/facta/bub/',
            'prestable/converted/smj/facta/bub/o.txt.xml',
            'prestable/converted/smj/ficti/',
            'prestable/converted/smj/ficti/sub/',
            'prestable/converted/smn/',
            'prestable/converted/smn/facta/',
            'prestable/converted/smn/facta/bub/',
            'prestable/converted/smn/facta/bub/g.txt.xml',
            'prestable/tmx/',
            'prestable/tmx/sme2sma/',
            'prestable/tmx/sme2sma/ficti/',
            'prestable/tmx/sme2sma/ficti/sub/',
            'prestable/tmx/sme2smj/',
            'prestable/tmx/sme2smj/ficti/',
            'prestable/tmx/sme2smj/ficti/sub/',
            'prestable/tmx/smn2sma/',
            'prestable/tmx/smn2sma/facta/',
            'prestable/tmx/smn2sma/facta/bub/',
            'prestable/tmx/smn2sma/facta/bub/g.txt.tmx',
            'prestable/tmx/smn2smj/',
            'prestable/tmx/smn2smj/facta/',
            'prestable/tmx/smn2smj/facta/bub/',
            'prestable/tmx/smn2smj/facta/bub/g.txt.tmx',
            'prestable/toktmx/',
            'prestable/toktmx/sme2sma/',
            'prestable/toktmx/sme2sma/ficti/',
            'prestable/toktmx/sme2sma/ficti/sub/',
            'prestable/toktmx/sme2smj/',
            'prestable/toktmx/sme2smj/ficti/',
            'prestable/toktmx/sme2smj/ficti/sub/',
            'prestable/toktmx/smn2sma/',
            'prestable/toktmx/smn2sma/facta/',
            'prestable/toktmx/smn2sma/facta/bub/',
            'prestable/toktmx/smn2sma/facta/bub/g.txt.toktmx',
            'prestable/toktmx/smn2smj/',
            'prestable/toktmx/smn2smj/facta/',
            'prestable/toktmx/smn2smj/facta/bub/',
            'prestable/toktmx/smn2smj/facta/bub/g.txt.toktmx')

    def test_update_metadata(self):
        smn_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/smn/facta/bub/g.txt.xsl'))
        self.assertEqual(smn_metadata.get_variable('genre'), 'facta')
        self.assertEqual(smn_metadata.get_variable('mainlang'), 'smn')
        smn_parallels = smn_metadata.get_parallel_texts()
        self.assertEqual(smn_parallels['smj'], 'o.txt')
        self.assertEqual(smn_parallels['sma'], 'f.txt')

        sma_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/sma/facta/bub/f.txt.xsl'))
        self.assertEqual(sma_metadata.get_variable('genre'), 'facta')
        sma_parallels = sma_metadata.get_parallel_texts()
        self.assertEqual(sma_parallels['smj'], 'o.txt')
        self.assertEqual(sma_parallels['smn'], 'g.txt')
        with self.assertRaises(KeyError):
            sma_parallels['sme']

        smj_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/smj/facta/bub/o.txt.xsl'))
        self.assertEqual(smj_metadata.get_variable('genre'), 'facta')
        smj_parallels = smj_metadata.get_parallel_texts()
        self.assertEqual(smj_parallels['smn'], 'g.txt')
        self.assertEqual(smj_parallels['sma'], 'f.txt')
        with self.assertRaises(KeyError):
            smj_parallels['sme']
