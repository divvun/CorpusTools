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
#   Copyright © 2014-2017 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

"""Test conversion of epub files."""

import os

from lxml import etree
from lxml.html import html5parser
from corpustools.epubconverter import EpubConverter
from corpustools.test.xmltester import XMLTester
from corpustools.test.test_htmlcontentconverter import clean_namespaces

HERE = os.path.dirname(__file__)


class TestEpubConverter(XMLTester):
    """Test the epub converter."""

    def setUp(self):
        """Setup epub content."""
        self.testdoc = EpubConverter(
            os.path.join(
                HERE, 'converter_data/fakecorpus/orig/sme/riddu/test.epub'))

    def test_remove_range(self):
        """Test the remove_range function."""
        content = etree.fromstring(self.testdoc.content)

        path1 = './/html:body/html:div[1]/html:h2[1]'
        path2 = './/html:body/html:div[3]/html:div[1]/html:h3[1]'

        self.testdoc.remove_range(path1, path2, content)
        got = content
        want = html5parser.document_fromstring(u"""
            <html>
                <head/>
                <body>
                    <div">
                        <div>
                            <h1>1 Bajilčála</h1>
                            <p>1asdf</p>
                        </div>
                    </div>
                    <div">
                        <div>
                            <h3 id="sigil_toc_id_5">3.1.1 Bajilčála</h3>
                            <div>8asdf</div>
                        </div>
                    </div>
                </body>
            </html>
        """)

        clean_namespaces([got, want])
        self.assertXmlEqual(got, want)

    def test_convert2intermediate_1(self):
        """Test without skip_elements."""
        got = self.testdoc.convert2intermediate()
        want = ("""
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
        """)

        self.assertXmlEqual(got, etree.fromstring(want))

    def test_convert2intermediate_2(self):
        """Test with skip_elements."""
        self.testdoc.metadata.set_variable(
            'skip_elements',
            './/html:body/html:div[1]/html:h2[1];'
            './/html:body/html:div[3]/html:div[1]/html:h3[1]')

        got = self.testdoc.convert2intermediate()
        want = ("""
            <document>
                <body>
                    <p type="title">1 Bajilčála</p>
                    <p>1asdf</p>
                    <p type="title">3.1.1 Bajilčála</p>
                    <p>8asdf</p>
                </body>
            </document>
        """)

        self.assertXmlEqual(got, etree.fromstring(want))


class TestEpubConverter1(XMLTester):
    """Test the epub converter."""

    def setUp(self):
        """Setup epub content."""
        self.testdoc = EpubConverter(
            os.path.join(
                HERE, 'converter_data/fakecorpus/orig/sme/riddu/test2.epub'))

    def test_convert2intermediate(self):
        """Range of same depth with the same name in the next to last level."""
        self.testdoc.metadata.set_variable(
            'skip_elements',
            './/body/div[1]/div[1]/p[1];.//body/div[2]/div[1]/p[4]')

        got = self.testdoc.convert2intermediate()
        want = ("""
            <document>
                <body>
                    <p>igjen går hesten</p>
                    <p>baklengs inni framtida</p>
                </body>
            </document>
        """)

        self.assertXmlEqual(got, etree.fromstring(want))

    def test_convert2intermediate1(self):
        """Range with same parents."""
        self.testdoc.metadata.set_variable(
            'skip_elements',
            './/body/div[2]/div[1]/p[1];.//body/div[2]/div[1]/p[4]')

        got = self.testdoc.convert2intermediate()
        want = ("""
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
        """)

        self.assertXmlEqual(got, etree.fromstring(want))
