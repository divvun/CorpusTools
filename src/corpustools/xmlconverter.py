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
#   Copyright © 2020-2023 The University of Tromsø &
#                    the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Convert udhr files to the Giella xml format."""
import os
from pathlib import Path

from lxml import etree

HERE = os.path.dirname(__file__)


def to_html_elt(filename: Path) -> etree.Element:
    """Turn a udhr xml file to giella xml."""
    udhr_tree = etree.parse(filename)
    udhr_transformer = etree.XSLT(etree.parse(os.path.join(HERE, "xslt/udhr2html.xsl")))

    return udhr_transformer(udhr_tree).getroot()
