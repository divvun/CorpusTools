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
"""Test conversion of epub files."""

import os
from shutil import copyfile

from lxml import etree
from testfixtures import TempDirectory

from corpustools import htmlcontentconverter, xslsetter, util
from corpustools.test.xmltester import XMLTester

HERE = os.path.dirname(__file__)


def set_data(directory, testdoc, skip_elements):
    """Set needed testdata.

    Args:
        directory (testfixtures.TempDirectory): path to the directory
        testdoc (str): path to the test document
        skip_elements (str): the range of elements to skip

    Returns:
        str: path to the test document in the temporary test directory
    """
    temp_epub = os.path.join(directory.path, os.path.basename(testdoc))
    copyfile(testdoc, temp_epub)
    metadata = xslsetter.MetadataHandler(temp_epub + ".xsl", create=True)
    metadata.set_variable("skip_elements", skip_elements)
    metadata.write_file()

    return temp_epub


class TestEpubConverter(XMLTester):
    """Test the epub converter."""

    def setUp(self):
        """Setup epub content."""
        self.testdoc = os.path.join(
            HERE, "converter_data/fakecorpus/orig/sme/riddu/test.epub"
        )

    def test_convert2intermediate_1(self):
        """Test without skip_elements."""
        got = htmlcontentconverter.convert2intermediate(self.testdoc)
        want = """
            <document>
                <body>
                    <p type="title">1 Bajilčála</p>
                    <p>1asdf</p>
                    <p type="title">1.1 Bajilčála</p>
                    <p>2asdf</p>
                    <p type="title">1.1.1 Bajilčála</p>
                    <p>3asdf</p>
                    <p type="title">2 Bajilčála</p>
                    <p>4asdf</p>
                    <p type="title">2.1 Bajilčála</p>
                    <p>5asdf</p>
                    <p type="title">2.1.1 Bajilčála</p>
                    <p>6asdf</p>
                    <p type="title">3.1 Bajilčála</p>
                    <p>7asdf</p>
                    <p type="title">3.1.1 Bajilčála</p>
                    <p>8asdf</p>
                </body>
            </document>
        """

        self.assertXmlEqual(got, etree.fromstring(want))

    def test_convert2intermediate_2(self):
        """Test with skip_elements."""
        with TempDirectory() as directory:
            temp_epub = set_data(
                directory,
                self.testdoc,
                ".//html:body/html:div[1]/html:h2[1];"
                ".//html:body/html:div[3]/html:div[1]/html:h3[1]",
            )
            got = htmlcontentconverter.convert2intermediate(temp_epub)
            want = """
                <document>
                    <body>
                        <p type="title">1 Bajilčála</p>
                        <p>1asdf</p>
                        <p type="title">3.1.1 Bajilčála</p>
                        <p>8asdf</p>
                    </body>
                </document>
            """

            self.assertXmlEqual(got, etree.fromstring(want))

    def test_convert2intermediate_3(self):
        """Test with skip_elements that only has first path defined."""
        with TempDirectory() as directory:
            temp_epub = set_data(
                directory, self.testdoc, ".//html:body/html:div[1]/html:h2[1];"
            )
            got = htmlcontentconverter.convert2intermediate(temp_epub)
            want = """
                <document>
                    <body>
                        <p type="title">1 Bajilčála</p>
                        <p>1asdf</p>
                        <p>2asdf</p>
                        <p type="title">1.1.1 Bajilčála</p>
                        <p>3asdf</p>
                        <p type="title">2 Bajilčála</p>
                        <p>4asdf</p>
                        <p type="title">2.1 Bajilčála</p>
                        <p>5asdf</p>
                        <p type="title">2.1.1 Bajilčála</p>
                        <p>6asdf</p>
                        <p type="title">3.1 Bajilčála</p>
                        <p>7asdf</p>
                        <p type="title">3.1.1 Bajilčála</p>
                        <p>8asdf</p>
                    </body>
                </document>
            """

            self.assertXmlEqual(got, etree.fromstring(want))


class TestEpubConverter1(XMLTester):
    """Test the epub converter."""

    def setUp(self):
        """Setup epub content."""
        self.testdoc = os.path.join(
            HERE, "converter_data/fakecorpus/orig/sme/riddu/test2.epub"
        )

    def test_convert2intermediate(self):
        """Range of same depth with the same name in the next to last level."""
        with TempDirectory() as directory:
            temp_epub = set_data(
                directory,
                self.testdoc,
                ".//body/div[1]/div[1]/p[1];.//body/div[2]/div[1]/p[4]",
            )
            got = htmlcontentconverter.convert2intermediate(temp_epub)
            want = """
                <document>
                    <body>
                        <p>igjen går hesten</p>
                        <p>baklengs inni framtida</p>
                    </body>
                </document>
            """

            self.assertXmlEqual(got, etree.fromstring(want))

    def test_convert2intermediate1(self):
        """Range with same parents."""
        with TempDirectory() as directory:
            temp_epub = set_data(
                directory,
                self.testdoc,
                ".//body/div[2]/div[1]/p[1];.//body/div[2]/div[1]/p[4]",
            )
            got = htmlcontentconverter.convert2intermediate(temp_epub)
            want = """
                <document>
                    <body>
                        <p>alle gir gass</p>
                        <p>men ikke</p>
                        <p>alle</p>
                        <p>har tass</p>
                        <p>igjen går hesten</p>
                        <p>baklengs inni framtida</p>
                    </body>
                </document>
            """

            self.assertXmlEqual(got, etree.fromstring(want))

    def test_convert2intermediate_invalid_skipelements(self):
        """Range of same depth with the same name in the next to last level."""
        with TempDirectory() as directory:
            temp_epub = set_data(
                directory,
                self.testdoc,
                ".//body/div[1]/div[1]/p[1];.//body/div[2]/div[15]/p[4]",
            )

            self.assertRaises(
                util.ConversionError,
                htmlcontentconverter.convert2intermediate,
                temp_epub,
            )
