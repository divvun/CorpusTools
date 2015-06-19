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

import testfixtures
import git

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


class TestMoveFileBasenameChanged(unittest.TestCase):
    '''Test what happens when only basename is changed'''
    def setUp(self):
        self.tempdir = testfixtures.TempDirectory()
        self.tempdir.makedir('orig/sme/ficti/sub')
        self.tempdir.makedir('orig/smj/ficti/sub')
        self.tempdir.makedir('orig/sma/ficti/sub')
        self.cfm = namechanger.CorpusFileMover(
            os.path.join(self.tempdir.path, 'orig/sme/ficti/sub/a.txt'),
            os.path.join(self.tempdir.path, 'orig/sme/ficti/sub/b.txt'))

    def tearDown(self):
        self.tempdir.cleanup()

    def test_init_corpus_file_mover(self):
        self.assertEqual(self.cfm.old_components, (
            self.tempdir.path, u'orig', u'sme', u'ficti', u'sub', u'a.txt'))
        self.assertEqual(self.cfm.new_components, (
            self.tempdir.path, u'orig', u'sme', u'ficti', u'sub', u'b.txt'))

    def test_corpus_file_mover_orig_pair(self):
        self.assertEqual(self.cfm.orig_pair, (
            os.path.join(self.tempdir.path, u'orig/sme/ficti/sub/a.txt'),
            os.path.join(self.tempdir.path, u'orig/sme/ficti/sub/b.txt')))

    def test_corpus_file_mover_xsl_pair(self):
        self.assertEqual(self.cfm.xsl_pair, (
            os.path.join(self.tempdir.path, u'orig/sme/ficti/sub/a.txt.xsl'),
            os.path.join(self.tempdir.path, u'orig/sme/ficti/sub/b.txt.xsl')))

    def test_corpus_file_mover_prestable_converted_pair(self):
        self.assertEqual(self.cfm.prestable_converted_pair, (
            os.path.join(self.tempdir.path,
                         u'prestable/converted/sme/ficti/sub/a.txt.xml'),
            os.path.join(self.tempdir.path,
                         u'prestable/converted/sme/ficti/sub/b.txt.xml')))

    def test_corpus_file_mover_prestable_tmx_pairs1(self):
        '''If a file has parallels'''
        mdh = xslsetter.MetadataHandler(os.path.join(
            self.tempdir.path, 'orig/sme/ficti/sub/a.txt.xsl'), create=True)
        mdh.set_variable('mainlang', 'sme')
        mdh.set_parallel_text('smj', 'c.txt')
        mdh.set_parallel_text('sma', 'd.txt')
        mdh.write_file()

        result = self.cfm.prestable_tmx_pairs
        testfixtures.compare(
            result[0],
            namechanger.PathPair(
                os.path.join(self.tempdir.path,
                             u'prestable/tmx/sme2smj/ficti/sub/a.txt.tmx'),
                os.path.join(self.tempdir.path,
                             u'prestable/tmx/sme2smj/ficti/sub/b.txt.tmx')))
        testfixtures.compare(
            result[1],
            namechanger.PathPair(
                os.path.join(self.tempdir.path,
                             u'prestable/tmx/sme2sma/ficti/sub/a.txt.tmx'),
                os.path.join(self.tempdir.path,
                             u'prestable/tmx/sme2sma/ficti/sub/b.txt.tmx')))
        testfixtures.compare(
            result[2],
            namechanger.PathPair(
                os.path.join(self.tempdir.path,
                             u'prestable/toktmx/sme2smj/ficti/sub',
                             u'a.txt.toktmx'),
                os.path.join(self.tempdir.path,
                             u'prestable/toktmx/sme2smj/ficti/sub',
                             u'b.txt.toktmx')))
        testfixtures.compare(
            result[3],
            namechanger.PathPair(
                os.path.join(self.tempdir.path,
                             u'prestable/toktmx/sme2sma/ficti/sub',
                             u'a.txt.toktmx'),
                os.path.join(self.tempdir.path,
                             u'prestable/toktmx/sme2sma/ficti/sub',
                             u'b.txt.toktmx')))

    def test_corpus_file_mover_prestable_tmx_pairs2(self):
        '''If a file has not parallels'''
        mdh = xslsetter.MetadataHandler(os.path.join(
            self.tempdir.path, 'orig/sme/ficti/sub/a.txt.xsl'), create=True)
        mdh.set_variable('mainlang', 'sme')
        mdh.write_file()

        result = self.cfm.prestable_tmx_pairs
        testfixtures.compare(result, [])

    def test_corpus_file_mover_prestable_tmx_pairs3(self):
        '''If a file has set translated_from'''
        mdh = xslsetter.MetadataHandler(os.path.join(
            self.tempdir.path, 'orig/sme/ficti/sub/a.txt.xsl'), create=True)
        mdh.set_variable('mainlang', 'sme')
        mdh.set_variable('translated_from', 'nob')
        mdh.set_parallel_text('smj', 'c.txt')
        mdh.set_parallel_text('sma', 'd.txt')
        mdh.write_file()

        result = self.cfm.prestable_tmx_pairs
        testfixtures.compare(result, [])

    #def test_corpus_file_mover_update_parallel_metadata(self):
        #mdh = xslsetter.MetadataHandler(os.path.join(
            #self.tempdir.path, 'orig/sme/ficti/sub/a.txt.xsl'), create=True)
        #mdh.set_variable('mainlang', 'sme')
        #mdh.set_variable('translated_from', 'nob')
        #mdh.set_parallel_text('smj', 'c.txt')
        #mdh.set_parallel_text('sma', 'd.txt')
        #mdh.write_file()

        #smj_mdh = xslsetter.MetadataHandler(os.path.join(
            #self.tempdir.path, 'orig/smj/ficti/sub/c.txt.xsl'), create=True)
        #smj_mdh.set_parallel_text('sme', 'a.txt')
        #smj_mdh.write_file()

        #sma_mdh = xslsetter.MetadataHandler(os.path.join(
            #self.tempdir.path, 'orig/sma/ficti/sub/d.txt.xsl'), create=True)
        #sma_mdh.set_parallel_text('sme', 'a.txt')
        #sma_mdh.write_file()

        #self.cfm.update_parallel_files_metadata()

        #smj_mdh = xslsetter.MetadataHandler(os.path.join(
            #self.tempdir.path, 'orig/smj/ficti/sub/c.txt.xsl'))
        #smj_mdh_parallel_texts = smj_mdh.get_parallel_texts()
        #self.assertEqual(smj_mdh_parallel_texts['sme'], 'b.txt')

        #sma_mdh = xslsetter.MetadataHandler(os.path.join(
            #self.tempdir.path, 'orig/sma/ficti/sub/d.txt.xsl'))
        #sma_mdh_parallel_texts = sma_mdh.get_parallel_texts()
        #self.assertEqual(sma_mdh_parallel_texts['sme'], 'b.txt')


class TestMoveFileGenreChanged(unittest.TestCase):
    '''Test what happens when genre is changed'''
    def setUp(self):
        self.tempdir = testfixtures.TempDirectory()

        self.tempdir.write(('orig', 'sme', 'ficti', 'sub', 'a.txt'), 'a')
        self.tempdir.write(('orig', 'smj', 'ficti', 'sub', 'c.txt'), 'a')
        self.tempdir.write(('orig', 'sma', 'ficti', 'sub', 'd.txt'), 'a')

        sme_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/sme/ficti/sub/a.txt.xsl'),
            create=True)
        sme_metadata.set_variable('mainlang', 'sme')
        sme_metadata.set_parallel_text('smj', 'c.txt')
        sme_metadata.set_parallel_text('sma', 'd.txt')
        sme_metadata.write_file()

        smj_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/smj/ficti/sub/c.txt.xsl'),
            create=True)
        smj_metadata.set_variable('mainlang', 'smj')
        smj_metadata.set_parallel_text('sme', 'a.txt')
        smj_metadata.set_parallel_text('sma', 'd.txt')
        smj_metadata.write_file()

        sma_metadata = xslsetter.MetadataHandler(
            os.path.join(self.tempdir.path, 'orig/sma/ficti/sub/d.txt.xsl'),
            create=True)
        sma_metadata.set_variable('mainlang', 'sma')
        sma_metadata.set_parallel_text('sme', 'a.txt')
        sma_metadata.set_parallel_text('smj', 'c.txt')
        sma_metadata.write_file()

        r = git.Repo.init(self.tempdir.path)
        r.index.add(['orig'])
        r.index.commit('Added orig')


    def tearDown(self):
        self.tempdir.cleanup()

    def test_file_mover(self):
        namechanger.file_mover(
            os.path.join(self.tempdir.path, 'orig/sme/ficti/sub/a.txt'),
            os.path.join(self.tempdir.path, 'orig/sme/facta/sub/b.txt'))

        #testfixtures.compare(self.tempdir.listdir('orig/sme/ficti/sub/'), '')

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
                             'orig/sma/ficti/bub/f.txt').decode('utf8')),])

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
                             'orig/sma/facta/sub/f.txt').decode('utf8')),])

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
                             'orig/sma/facta/sub/f.txt').decode('utf8')),])
