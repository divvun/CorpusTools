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
#   Copyright © 2014-2020 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Test the XslMaker class."""


import os

from lxml import etree

from corpustools import xslmaker
from corpustools.test.xmltester import XMLTester

HERE = os.path.dirname(__file__)


class TestXslMaker(XMLTester):
    """Test the Xslmaker class."""

    def test_get_xsl(self):
        """Test the functionality of the XslMaker class."""
        xsl_maker = xslmaker.XslMaker(
            etree.parse(
                os.path.join(HERE, "converter_data/samediggi-article-48.html.xsl")
            )
        )
        got = xsl_maker.xsl

        # The import href is different for each user testing, so just
        # check that it looks OK:
        import_elt = got.find(
            "/xsl:import", namespaces={"xsl": "http://www.w3.org/1999/XSL/Transform"}
        )
        self.assertTrue(import_elt.attrib["href"].startswith("file:///"))
        self.assertTrue(import_elt.attrib["href"].endswith("common.xsl"))
        with open(import_elt.attrib["href"][7:].replace("%20", " ")) as xsl:
            self.assertGreater(len(xsl.read()), 0)
        # ... and set it to the hardcoded path in test.xsl:
        import_elt.attrib["href"] = (
            "file:///home/boerre/langtech/trunk/tools/CorpusTools/"
            "corpustools/xslt/common.xsl"
        )

        want = etree.parse(os.path.join(HERE, "converter_data/test.xsl"))
        self.assertXmlEqual(got, want)
