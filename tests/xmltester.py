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
#   Copyright © 2014-2023 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Class to test xml snippets."""

import doctest
import unittest

from lxml import doctestcompare, etree


class XMLTester(unittest.TestCase):
    """Test xml equality."""

    @staticmethod
    def assertXmlEqual(got, want):
        """Check if two stringified xml snippets are equal.

        Args:
            got (etree.Element): the xml part given by the tester
            want (etree.Element): the wanted xml

        Raises:
            AssertionError: If they are not equal
        """
        got = etree.tostring(got, encoding="unicode")
        want = etree.tostring(want, encoding="unicode")

        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(doctest.Example("", want), got, 0)
            raise AssertionError(message)
