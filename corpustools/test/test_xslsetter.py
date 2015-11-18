# -*- coding: utf-8 -*-

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
#   Copyright © 2014-2015 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

import unittest

from corpustools import xslsetter


class TestMetadataHandler(unittest.TestCase):
    def test_set_skip_pages1(self):
        '''Test a valid skip_pages line'''
        md = xslsetter.MetadataHandler('bogus.pdf', create=True)
        md.set_variable('skip_pages', '1, 4-5, 7')
        got = md.skip_pages
        want = [1, 4, 5, 7]

        self.assertEqual(got, want)

    def test_set_skip_pages2(self):
        '''Test an invalid skip_pages line'''
        md = xslsetter.MetadataHandler('bogus.xml', create=True)
        md.set_variable('skip_pages', '1, 4 5, 7')

        with self.assertRaises(xslsetter.XsltException):
            md.skip_pages

    def test_set_skip_pages3(self):
        '''Test an empty skip_pages line'''
        md = xslsetter.MetadataHandler('bogus.xml', create=True)
        md.set_variable('skip_pages', ' ')
        got = md.skip_pages
        want = []

        self.assertEqual(got, want)

    def test_set_skip_pages4(self):
        '''Test with odd as a page range'''
        md = xslsetter.MetadataHandler('bogus.xml', create=True)
        md.set_variable('skip_pages', 'odd, 2')
        got = md.skip_pages
        want = ['odd', 2]

        self.assertEqual(got, want)

    def test_set_skip_pages5(self):
        '''Test with even as a page range'''
        md = xslsetter.MetadataHandler('bogus.xml', create=True)
        md.set_variable('skip_pages', 'even, 1')
        got = md.skip_pages
        want = ['even', 1]

        self.assertEqual(got, want)

    def test_set_skip_pages6(self):
        '''Raise an exception if both odd and even are used'''
        md = xslsetter.MetadataHandler('bogus.xml', create=True)
        md.set_variable('skip_pages', 'odd, even')

        with self.assertRaises(xslsetter.XsltException):
            md.skip_pages



