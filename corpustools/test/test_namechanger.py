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

import unittest

from corpustools import namechanger


class TestNameChangerBase(unittest.TestCase):
    def test_none_ascii_lower(self):
        name = u'ášŧŋđžčåøæöäï+'
        nc = namechanger.NameChangerBase(name)
        want = u'astngdzcaoaeoai_'

        self.assertEqual(nc.new_filename, want)

    def test_none_ascii_upper(self):
        name = u'ÁŠŦŊĐŽČÅØÆÖÄÏ+'
        nc = namechanger.NameChangerBase(name)
        want = u'astngdzcaoaeoai_'

        self.assertEqual(nc.new_filename, want)

    def test_none_ascii_blabla(self):
        name = u'ášŧŋđŽČÅØÆÖÄï+'
        nc = namechanger.NameChangerBase(name)
        want = u'astngdzcaoaeoai_'

        self.assertEqual(nc.new_filename, want)

    def test_own_name_with_only_ascii(self):
        oldname = u'YoullNeverWalkAlone'
        nc = namechanger.NameChangerBase(oldname)
        want = u'youllneverwalkalone'

        self.assertEqual(nc.new_filename, want)

    def test_own_name_with_only_ascii_and_space(self):
        oldname = u'Youll Never Walk Alone'
        nc = namechanger.NameChangerBase(oldname)
        want = u'youll_never_walk_alone'

        self.assertEqual(nc.new_filename, want)

    def test_own_name_with_ascii_and_space_and_apostrophe(self):
        oldname = u"You'll Never Walk Alone"
        nc = namechanger.NameChangerBase(oldname)
        want = u'you_ll_never_walk_alone'

        self.assertEqual(nc.new_filename, want)

    def test_own_name_with_non_ascii(self):
        oldname = u'Šaddágo beaivi vai idja/Šaddágo beaivi vai idja'
        nc = namechanger.NameChangerBase(oldname)
        want = u'saddago_beaivi_vai_idja'

        self.assertEqual(nc.new_filename, want)

    def test_own_name_with_quote(self):
        oldname = u'aba".txt'
        nc = namechanger.NameChangerBase(oldname)
        want = u'aba_.txt'

        self.assertEqual(nc.new_filename, want)

    def test_own_name_with_lt(self):
        oldname = u'aba<.txt'
        nc = namechanger.NameChangerBase(oldname)
        want = u'aba_.txt'

        self.assertEqual(nc.new_filename, want)

    def test_own_name_with_gt(self):
        oldname = u'aba>.txt'
        nc = namechanger.NameChangerBase(oldname)
        want = u'aba_.txt'

        self.assertEqual(nc.new_filename, want)

    def test_own_name_with_complete_path(self):
        oldname = u'j/a/b/c/aba>.txt'
        nc = namechanger.NameChangerBase(oldname)
        want = u'aba_.txt'

        self.assertEqual(nc.new_filename, want)

    def test_own_name_with_url(self):
        oldname = u'http://j/a/b/c/aba>.txt'
        nc = namechanger.NameChangerBase(oldname)
        want = u'aba_.txt'

        self.assertEqual(nc.new_filename, want)
