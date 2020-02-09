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
#   Copyright © 2014-2020 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

from __future__ import absolute_import

import doctest
import os

import lxml.doctestcompare
import lxml.etree
import six
import testfixtures
from parameterized import parameterized


def assertXmlEqual(got, want):
    """Check if two xml snippets are equal"""
    got = lxml.etree.tostring(got, encoding='unicode')
    want = lxml.etree.tostring(want, encoding='unicode')
    checker = lxml.doctestcompare.LXMLOutputChecker()
    if not checker.check_output(want, got, 0):
        message = checker.output_difference(doctest.Example("", want), got, 0)
        raise AssertionError(message)
