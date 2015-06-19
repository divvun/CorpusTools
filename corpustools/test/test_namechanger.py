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
#   Copyright 2013-2014 Børre Gaup <borre.gaup@uit.no>
#

import os
import unittest

from corpustools import namechanger
from corpustools import util

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
            util.PathComponents(os.path.join(here, 'name_changer_data'),
                                'orig', 'sme', 'admin', 'other_files',
                                'new_none_dupe_1.txt')
            )
