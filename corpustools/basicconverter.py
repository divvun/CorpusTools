# -*- coding: utf-8 -*-

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
#   Copyright © 2012-2018 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Base class for converters."""

from corpustools import xslsetter


class BasicConverter(object):
    """Take care of data common to all BasicConverter classes."""

    def __init__(self, filename):
        """Initialise the BasicConverter class.

        Args:
            filename: string containing the path to the file that should
            be converted
            write_intermediate: boolean which decides whether intermediate
            versions of the converted document should be written (used for
            debugging purposes).
        """
        self.orig = filename
        self.metadata = xslsetter.MetadataHandler(
            filename + '.xsl', create=True)
