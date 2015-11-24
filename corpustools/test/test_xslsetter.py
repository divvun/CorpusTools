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

    def test_set_margin(self):
        '''Test if the margin is set correctly'''
        md = xslsetter.MetadataHandler('bogus.pdf', create=True)

        self.assertEqual(
            md.parse_margin_line('odd=230, even = 540 , 8 = 340'),
            {'odd': 230, 'even': 540, '8': 340})

    def test_parse_margin_lines1(self):
        '''Test parse_margin_lines'''
        md = xslsetter.MetadataHandler('bogus.pdf', create=True)
        md.set_variable('left_margin', '7=7')
        md.set_variable('right_margin', 'odd=4,even=8,3=6')
        md.set_variable('top_margin', '8=8')
        md.set_variable('bottom_margin', '9=2')

        self.assertEqual(md.margins, {
            'left_margin': {'7': 7},
            'right_margin': {'odd': 4, 'even': 8, '3': 6},
            'top_margin': {'8': 8},
            'bottom_margin': {'9': 2}})

    def test_parse_margin_lines2(self):
        '''all and even in margin line should raise ConversionException'''
        md = xslsetter.MetadataHandler('bogus.pdf', create=True)
        md.set_variable('right_margin', 'all=40,even=80')

        with self.assertRaises(xslsetter.XsltException):
                md.margins

    def test_parse_margin_lines3(self):
        '''all and odd in margin line should raise ConversionException'''
        md = xslsetter.MetadataHandler('bogus.pdf', create=True)
        md.set_variable('right_margin', 'all=40,odd=80')

        with self.assertRaises(xslsetter.XsltException):
            md.margins

    def test_parse_margin_lines4(self):
        '''text after = should raise ConversionException'''
        md = xslsetter.MetadataHandler('bogus.pdf', create=True)
        md.set_variable('right_margin', 'all=tullball')

        with self.assertRaises(xslsetter.XsltException):
            md.margins

    def test_parse_margin_lines5(self):
        '''no = should raise ConversionException'''
        md = xslsetter.MetadataHandler('bogus.pdf', create=True)
        md.set_variable('right_margin', 'all 50')

        with self.assertRaises(xslsetter.XsltException):
            md.margins

    def test_parse_margin_lines6(self):
        '''line with no comma between values should raise an exception'''
        md = xslsetter.MetadataHandler('bogus.pdf', create=True)
        md.set_variable('right_margin', 'all=50 3')

        with self.assertRaises(xslsetter.XsltException):
            md.margins

    def test_parse_margin_lines7(self):
        '''multiple pages with the same margin are separated by semicolon'''
        md = xslsetter.MetadataHandler('bogus.pdf', create=True)
        md.set_variable('right_margin', '1;3=50, 2=30')

        self.assertEqual(md.margins, {
            'right_margin': {'1': 50, '2': 30, '3': 50}})

    def test_inner_margin1(self):
        '''Raise exception if inner_right is set and not inner_left'''
        for p in ['top', 'bottom', 'right', 'left']:
            md = xslsetter.MetadataHandler('bogus.pdf', create=True)
            md.set_variable('inner_' + p + '_margin', '5=30')

            with self.assertRaises(xslsetter.XsltException):
                md.inner_margins

    def test_inner_margin2(self):
        '''Raise exception if not the same pages are set'''
        md = xslsetter.MetadataHandler('bogus.pdf', create=True)
        md.set_variable('inner_top_margin', '5=30')
        md.set_variable('inner_bottom_margin', '6=30')
        with self.assertRaises(xslsetter.XsltException):
            md.inner_margins

        md = xslsetter.MetadataHandler('bogus.pdf', create=True)
        md.set_variable('inner_left_margin', '5=30')
        md.set_variable('inner_right_margin', '6=30')
        with self.assertRaises(xslsetter.XsltException):
            md.inner_margins

    def test_inner_margin3(self):
        '''Test whether a correctly set inner margin gives the wanted result'''
        md = xslsetter.MetadataHandler('bogus.pdf', create=True)
        md.set_variable('inner_top_margin', '6=20, 5=20')
        md.set_variable('inner_bottom_margin', '5=30, 6=50')

        self.assertEqual(md.inner_margins,
                         {u'inner_bottom_margin': {u'5': 30, u'6': 50},
                          u'inner_top_margin': {u'5': 20, u'6': 20}})

    def test_inner_margin4(self):
        '''Test whether a correctly set inner margin gives the wanted result'''
        md = xslsetter.MetadataHandler('bogus.pdf', create=True)
        md.set_variable('inner_left_margin', '6=20, 5=20')
        md.set_variable('inner_right_margin', '5=30, 6=50')

        self.assertEqual(md.inner_margins,
                         {u'inner_right_margin': {u'5': 30, u'6': 50},
                          u'inner_left_margin': {u'5': 20, u'6': 20}})
