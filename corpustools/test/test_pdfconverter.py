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
"""Test conversion of pdf files."""

import os
import unittest
from pathlib import Path

from lxml import etree
from parameterized import parameterized

from corpustools import pdfconverter, xslsetter
from corpustools.test import xmltester

HERE = os.path.dirname(__file__)


@parameterized(
    [
        ("a-", "b", "a"),
        ("a-", "B", "a-"),
        ("a", "b", "a "),
        ("A", "B", "A "),
        ("a-", "0", "a-"),
    ]
)
def test_handle_br(previous, current, wanted):
    assert pdfconverter.handle_br(previous, current) == wanted


class TestPDFFontspecs(unittest.TestCase):
    def test_add_fontspec(self):
        f1 = etree.fromstring(
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
        )
        f2 = etree.fromstring(
            '<fontspec id="5" size="19" family="Times" color="#231f20"/>'
        )
        f3 = etree.fromstring(
            '<fontspec id="6" size="13" family="Times" color="#231f20"/>'
        )

        pdffontspecs = pdfconverter.PDFFontspecs()
        pdffontspecs.add_fontspec(f1)
        pdffontspecs.add_fontspec(f2)
        pdffontspecs.add_fontspec(f3)

        assert sorted(id_ for p, id_ in pdffontspecs.pdffontspecs.items()) == ["1", "5"]
        assert pdffontspecs.duplicates == {"6": "1"}


class TestPDFPageMetaData(unittest.TestCase):
    def test_compute_default_margins(self):
        """Test that original margins are kept by default."""
        page1 = pdfconverter.PDFPageMetadata(
            page_id="page1-div", page_style="height:1263px;width:862px;"
        )

        assert page1.compute_margins() == {
            "left_margin": 0,
            "right_margin": 862,
            "top_margin": 0,
            "bottom_margin": 1263,
        }

    def test_compute_margins1(self):
        """Test parse_margin_lines."""
        metadata = xslsetter.MetadataHandler("test.pdf.xsl", create=True)
        metadata.set_variable("left_margin", "7=5")
        metadata.set_variable("right_margin", "odd=10,even=15,3=5")
        metadata.set_variable("top_margin", "8=8")
        metadata.set_variable("bottom_margin", "9=20")

        page1 = pdfconverter.PDFPageMetadata(
            page_id="page1-div",
            page_style="height:1263px;width:862px;",
            metadata_margins=metadata.margins,
        )

        assert page1.compute_margins() == {
            "left_margin": 0,
            "right_margin": 775,
            "top_margin": 0,
            "bottom_margin": 1263,
        }

        page2 = pdfconverter.PDFPageMetadata(
            page_id="page2-div",
            page_style="height:1263px;width:862px;",
            metadata_margins=metadata.margins,
        )
        assert page2.compute_margins() == {
            "left_margin": 00,
            "right_margin": 732,
            "top_margin": 0,
            "bottom_margin": 1263,
        }
        page3 = pdfconverter.PDFPageMetadata(
            page_id="page3-div",
            page_style="height:1263px;width:862px;",
            metadata_margins=metadata.margins,
        )
        assert page3.compute_margins() == {
            "left_margin": 0,
            "right_margin": 818,
            "top_margin": 0,
            "bottom_margin": 1263,
        }
        page7 = pdfconverter.PDFPageMetadata(
            page_id="page7-div",
            page_style="height:1263px;width:862px;",
            metadata_margins=metadata.margins,
        )
        assert page7.compute_margins() == {
            "left_margin": 43,
            "right_margin": 775,
            "top_margin": 0,
            "bottom_margin": 1263,
        }
        page8 = pdfconverter.PDFPageMetadata(
            page_id="page8-div",
            page_style="height:1263px;width:862px;",
            metadata_margins=metadata.margins,
        )
        assert page8.compute_margins() == {
            "left_margin": 0,
            "right_margin": 732,
            "top_margin": 101,
            "bottom_margin": 1263,
        }
        page9 = pdfconverter.PDFPageMetadata(
            page_id="page9-div",
            page_style="height:1263px;width:862px;",
            metadata_margins=metadata.margins,
        )
        assert page9.compute_margins() == {
            "left_margin": 0,
            "right_margin": 775,
            "top_margin": 0,
            "bottom_margin": 1010,
        }

    def test_compute_inner_margins_1(self):
        """Test if inner margins is set for the specified page."""
        metadata = xslsetter.MetadataHandler("test.pdf.xsl", create=True)
        metadata.set_variable("inner_top_margin", "1=40")
        metadata.set_variable("inner_bottom_margin", "1=40")

        page1 = pdfconverter.PDFPageMetadata(
            page_id="page1-div",
            page_style="height:1263px;width:862px;",
            metadata_inner_margins=metadata.inner_margins,
        )

        assert page1.compute_inner_margins() == {
            "top_margin": 505,
            "bottom_margin": 757,
            "left_margin": 0,
            "right_margin": 862,
        }

    def test_compute_inner_margins_2(self):
        """Test that inner margins is empty for the specified page."""
        metadata = xslsetter.MetadataHandler("test.pdf.xsl", create=True)
        metadata.set_variable("inner_top_margin", "1=40")
        metadata.set_variable("inner_bottom_margin", "1=40")

        page1 = pdfconverter.PDFPageMetadata(
            page_id="page2-div",
            page_style="height:1263px;width:862px;",
            metadata_inner_margins=metadata.inner_margins,
        )

        assert page1.compute_inner_margins() == {}

    def test_width(self):
        page = pdfconverter.PDFPageMetadata(
            page_id="page1-div", page_style="height:1263px;width:862px;"
        )

        assert page.page_number == 1
        assert page.page_height == 1263
        assert page.page_width == 862


class TestPDFPage(xmltester.XMLTester):
    def test_is_inside_margins1(self):
        """top and left inside margins."""
        t = etree.fromstring('<p style="top:109px;left:135px"/>')
        margins = {}
        margins["left_margin"] = 62
        margins["right_margin"] = 802
        margins["top_margin"] = 88
        margins["bottom_margin"] = 1174

        p2x = pdfconverter.PDFPage(
            etree.fromstring('<div id="page2-div" style="width:862px;height:1263px"/>')
        )

        assert p2x.is_inside_margins(t, margins)

    def test_is_inside_margins2(self):
        """top above top margin and left inside margins."""
        t = etree.fromstring('<p style="top:85px;left:135px"/>')
        margins = {}
        margins["left_margin"] = 62
        margins["right_margin"] = 802
        margins["top_margin"] = 88
        margins["bottom_margin"] = 1174

        p2x = pdfconverter.PDFPage(
            etree.fromstring('<div id="page2-div" style="width:862px;height:1263px"/>')
        )

        assert not p2x.is_inside_margins(t, margins)

    def test_is_inside_margins3(self):
        """top below bottom margin and left inside margins."""
        t = etree.fromstring('<p style="top:1178px;left:135px"/>')
        margins = {}
        margins["left_margin"] = 62
        margins["right_margin"] = 802
        margins["top_margin"] = 88
        margins["bottom_margin"] = 1174

        p2x = pdfconverter.PDFPage(
            etree.fromstring('<div id="page2-div" style="width:862px;height:1263px"/>')
        )

        assert not p2x.is_inside_margins(t, margins)

    def test_is_inside_margins4(self):
        """top inside margins and left outside right margin."""
        t = etree.fromstring('<p style="top:1000px;left:50px"/>')
        margins = {}
        margins["left_margin"] = 62
        margins["right_margin"] = 802
        margins["top_margin"] = 88
        margins["bottom_margin"] = 1174

        p2x = pdfconverter.PDFPage(
            etree.fromstring('<div id="page2-div" style="width:862px;height:1263px"/>')
        )

        assert not p2x.is_inside_margins(t, margins)

    def test_is_inside_margins5(self):
        """top inside margins and left outside left margin."""
        t = etree.fromstring('<p style="top:1000px;left:805px"/>')
        margins = {}
        margins["left_margin"] = 62
        margins["right_margin"] = 802
        margins["top_margin"] = 88
        margins["bottom_margin"] = 1174

        p2x = pdfconverter.PDFPage(
            etree.fromstring('<div id="page2-div" style="width:862px;height:1263px"/>')
        )

        assert not p2x.is_inside_margins(t, margins)

    def test_is_skip_page_1(self):
        """Odd page should be skipped when odd is in skip_pages."""
        p2x = pdfconverter.PDFPage(
            etree.fromstring('<div id="page1-div" style="width:862px;height:1263px"/>')
        )

        p2x.is_skip_page(["odd"])

    def test_is_skip_page_2(self):
        """Even page should be skipped when even is in skip_pages."""
        p2x = pdfconverter.PDFPage(
            etree.fromstring('<div id="page2-div" style="width:862px;height:1263px"/>')
        )

        assert p2x.is_skip_page(["even"])

    def test_is_skip_page_3(self):
        """Even page should not be skipped when odd is in skip_pages."""
        p2x = pdfconverter.PDFPage(
            etree.fromstring('<div id="page2-div" style="width:862px;height:1263px"/>')
        )

        assert not p2x.is_skip_page(["odd"])

    def test_is_skip_page_4(self):
        """Odd page should not be skipped when even is in skip_pages."""
        p2x = pdfconverter.PDFPage(
            etree.fromstring('<div id="page1-div" style="width:862px;height:1263px"/>')
        )

        assert not p2x.is_skip_page(["even"])

    def test_is_skip_page_5(self):
        """Page should not be skipped when not in skip_range."""
        p2x = pdfconverter.PDFPage(
            etree.fromstring('<div id="page1-div" style="width:862px;height:1263px"/>')
        )

        assert not p2x.is_skip_page(["even", 3])

    def test_is_skip_page_6(self):
        """Page should be skipped when in skip_range."""
        p2x = pdfconverter.PDFPage(
            etree.fromstring('<div id="page3-div" style="width:862px;height:1263px"/>')
        )

        assert p2x.is_skip_page(["even", 3])


class TestPDF2XMLConverter(xmltester.XMLTester):
    """Test the class that converts from pdf2xml to giellatekno/divvun xml."""

    def test_pdf_converter(self):
        pdfdocument = pdfconverter.PDF2XMLConverter(
            Path(HERE) / "converter_data/fakecorpus/orig/sme/riddu/pdf-test.pdf"
        )
        got = pdfdocument.convert2intermediate()
        want = etree.parse(os.path.join(HERE, "converter_data/pdf-xml2pdf-test.xml"))

        self.assertXmlEqual(got, want)
