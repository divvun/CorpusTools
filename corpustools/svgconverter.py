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
#   Copyright © 2012-2020 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""This file contains classes to convert svg files to the Giella xml format."""

import os

import lxml.etree as etree

HERE = os.path.dirname(__file__)


def convert2intermediate(filename):
    """Transform svg to an intermediate xml document.

    Args:
        filename (str): name of the file that should be converted
    """
    svg_xslt_root = etree.parse(os.path.join(HERE, 'xslt/svg2corpus.xsl'))
    transform = etree.XSLT(svg_xslt_root)
    doc = etree.parse(filename)
    intermediate = transform(doc)

    return intermediate.getroot()
