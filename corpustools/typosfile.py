#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#   This file contains classes to handle .typos files in $GTFREE
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
#   Copyright 2012-2014 Børre Gaup <borre.gaup@uit.no>
#


class Typoline:
    """Class to parse a line of a .typos file
    """
    def __init__(self, typoline):
        """Parse a typoline
        A typoline has a number showing frequency of the typo, the typo and
        possibly a correction
        """
        parts = typoline.split('\t')

        self.typo = parts[0]

        if len(parts) == 2:
            self.correction = parts[1]
        else:
            self.correction = None

    def getTypo(self):
        return self.typo

    def setCorrection(self, correction):
        self.correction = correction

    def getCorrection(self):
        return self.correction

    def makeTypoline(self):
        """Make a typoline from the three data parts in this class
        """
        result = self.typo
        if self.correction and self.correction != self.typo:
            result = '{}\t{}'.format(result, self.correction)

        return result


class Typos:
    """A class that reads typos and corrections from a .typos files and
    stores them in a dict
    """
    def __init__(self, typosfile):
        """Read typos from typosfile. If a correction exists, insert the typos
        and corrections into self.typos
        """
        self.typos = {}
        typofile = open(typosfile)

        for strline in typofile:
            line = strline.decode('utf-8')
            if line.strip():
                tl = Typoline(line.rstrip())
                if tl.getCorrection() and tl.getTypo() != tl.getCorrection():
                    self.typos[tl.getTypo()] = tl.getCorrection()
        typofile.close()

    def getTypos(self):
        """Return the typos dict
        """
        return self.typos
