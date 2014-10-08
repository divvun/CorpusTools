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


class TestNameChanger(unittest.TestCase):
    def testNoneAsciiLower(self):
        want = 'astndzcaoaoai_'

        name = u'ášŧŋđžčåøæöäï+'
        nc = namechanger.NameChanger(name)

        self.assertEqual(nc.newname, want)

    def testNoneAsciiUpper(self):
        want = 'astndzcaoaoai_'

        name = u'ÁŠŦŊĐŽČÅØÆÖÄÏ+'
        nc = namechanger.NameChanger(name)

        self.assertEqual(nc.newname, want)

    def testNoneAsciiBlabla(self):
        want = 'astndzcaoaoai_'

        name = u'ášŧŋđŽČÅØÆÖÄï+'
        nc = namechanger.NameChanger(name)

        self.assertEqual(nc.newname, want)

    def testOwnNameWithOnlyAscii(self):
        want = 'youllneverwalkalone'

        oldname = 'YoullNeverWalkAlone'
        nc = namechanger.NameChanger(oldname)

        self.assertEqual(nc.newname, want)

    def testOwnNameWithOnlyAsciiAndSpace(self):
        want = 'youll_never_walk_alone'

        oldname = 'Youll Never Walk Alone'
        nc = namechanger.NameChanger(oldname)

        self.assertEqual(nc.newname, want)

    def testOwnNameWithAsciiAndSpaceAndApostrophe(self):
        want = 'you_ll_never_walk_alone'

        oldname = "You'll Never Walk Alone"
        nc = namechanger.NameChanger(oldname)

        self.assertEqual(nc.newname, want)

    def testOwnNameWithNonAscii(self):
        want = 'saddago_beaivi_vai_idja/saddago_beaivi_vai_idja'

        oldname = u'Šaddágo beaivi vai idja/Šaddágo beaivi vai idja'
        klass = oldname
        nc = namechanger.NameChanger(klass)

        self.assertEqual(nc.newname, want)
