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
#   Copyright © 2014-2021 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Implement the XslMaker class."""


import os

from lxml import etree

HERE = os.path.dirname(__file__)


class XslMaker:
    """Make an xsl file to combine with the intermediate xml file.

    To convert the intermediate xml to a fullfledged  giellatekno document
    a combination of three xsl files + the intermediate xml file is needed.
    """

    def __init__(self, xslfile):
        """Initialise the XslMaker class.

        Args:
            xslfile: a string containing the path to the xsl file.
        """
        self.filename = xslfile

    @property
    def logfile(self):
        """Return the name of the logfile."""
        return self.filename + ".log"

    @property
    def xsl(self):
        """Return an etree of the xsl file.

        Raises:
            In case of an xml syntax error, raise ConversionException.
        """
        xsl = etree.parse(os.path.join(HERE, "xslt/preprocxsl.xsl"))
        transformer = etree.XSLT(xsl)

        common_xsl_path = os.path.join(HERE, "xslt/common.xsl").replace(" ", "%20")

        return transformer(
            self.filename,
            commonxsl=etree.XSLT.strparam(f"file://{common_xsl_path}"),
        )

    @property
    def transformer(self):
        """Make an etree.XSLT transformer.

        Raises:
            raise a ConversionException in case of invalid XML in the xsl file.
        Returns:
            an etree.XSLT transformer
        """
        return etree.XSLT(self.xsl)
