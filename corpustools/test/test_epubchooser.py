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
#   Copyright © 2018-2023 The University of Tromsø &
#                    the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Test the functionality in epubchooser."""

import unittest

from corpustools import epubchooser


class TestRangeHandler(unittest.TestCase):
    """Test the MetadataHandler class."""

    def setUp(self):
        self.rangehandler = epubchooser.RangeHandler()
        self.rangehandler.xpaths = [
            ".//body/div",
            ".//body/div/div",
            ".//body/div/div/p",
            ".//body/div/div/p[2]",
            ".//body/div/div[2]",
            ".//body/div[2]",
            ".//body/div[2]/div",
            ".//body/div[2]/div/p",
            ".//body/div[2]/div/p[2]",
        ]

    def test1(self):
        """Check that an exception is raised when first xpath is empty."""
        with self.assertRaises(KeyError):
            self.rangehandler.check_range(("", ""))

    def test2(self):
        """Check that an exception is raised when first xpath is invalid."""
        with self.assertRaises(KeyError):
            self.rangehandler.check_range((".//body/div/div[3]", ""))

    def test3(self):
        """Check that an exception is raised when second xpath is invalid."""
        with self.assertRaises(KeyError):
            self.rangehandler.check_range((".//body/div/div", ".//body/div/div[3]"))

    def test4(self):
        """Valid first part, empty second part is a valid pair."""
        self.assertEqual(
            self.rangehandler.check_range((self.rangehandler.xpaths[0], "")), None
        )

    def test5(self):
        """Valid first part, valid second part is a valid pair."""
        self.assertEqual(
            self.rangehandler.check_range(
                (self.rangehandler.xpaths[0], self.rangehandler.xpaths[1])
            ),
            None,
        )

    def test6(self):
        """First part of new range is within existing ranges."""
        self.rangehandler._ranges.add(
            (
                self.rangehandler.xpaths.index(".//body/div/div/p"),
                self.rangehandler.xpaths.index(".//body/div[2]/div"),
            )
        )

        new_range = ((".//body/div/div/p[2]"), (".//body/div[2]/div"))
        with self.assertRaises(IndexError):
            self.rangehandler.check_overlap(new_range)

    def test7(self):
        """Second part of new range is within existing ranges."""
        self.rangehandler._ranges.add(
            (
                self.rangehandler.xpaths.index(".//body/div/div/p"),
                self.rangehandler.xpaths.index(".//body/div[2]/div"),
            )
        )

        new_range = ((".//body/div[2]/div"), (".//body/div/div/p[2]"))
        with self.assertRaises(IndexError):
            self.rangehandler.check_overlap(new_range)

    def test8(self):
        """First part of new range is equal to first part of existing range."""
        self.rangehandler._ranges.add(
            (
                self.rangehandler.xpaths.index(".//body/div/div/p"),
                self.rangehandler.xpaths.index(".//body/div[2]/div"),
            )
        )

        new_range = ((".//body/div/div/p"), (""))
        with self.assertRaises(IndexError):
            self.rangehandler.check_overlap(new_range)

    def test9(self):
        """Check for valid range.

        Second part of new range is equal to first part of existing range.
        """
        self.rangehandler._ranges.add(
            (
                self.rangehandler.xpaths.index(".//body/div/div/p"),
                self.rangehandler.xpaths.index(".//body/div[2]/div"),
            )
        )
        new_range = ((".//body/div"), (".//body/div/div/p"))
        with self.assertRaises(IndexError):
            self.rangehandler.check_overlap(new_range)

    def test10(self):
        """Check that a range is reversed if needed."""
        self.rangehandler.add_range(
            (self.rangehandler.xpaths[1], self.rangehandler.xpaths[0])
        )
        want = set()
        want.add(
            (
                self.rangehandler.xpaths.index(self.rangehandler.xpaths[0]),
                self.rangehandler.xpaths.index(self.rangehandler.xpaths[1]),
            )
        )
        self.assertEqual(self.rangehandler._ranges, want)

    def test11(self):
        """Check that ranges are returned reversed and as text."""
        self.rangehandler.add_range(
            (self.rangehandler.xpaths[4], self.rangehandler.xpaths[6])
        )
        want = "{};{},{};{}".format(
            self.rangehandler.xpaths[4],
            self.rangehandler.xpaths[6],
            self.rangehandler.xpaths[0],
            self.rangehandler.xpaths[1],
        )
        self.assertEqual(self.rangehandler.ranges, want)

    def test12(self):
        """Check that empty second part of range works as exptected."""
        self.rangehandler.add_range((self.rangehandler.xpaths[7], ""))
        want = "{};,{};{},{};{}".format(
            self.rangehandler.xpaths[7],
            self.rangehandler.xpaths[4],
            self.rangehandler.xpaths[6],
            self.rangehandler.xpaths[0],
            self.rangehandler.xpaths[1],
        )
        self.assertEqual(self.rangehandler.ranges, want)
