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
#   Copyright © 2014-2020 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
u"""Test conversion of pdf files."""

import collections
import os
import unittest

import lxml.etree as etree

from corpustools import pdfconverter, xslsetter
from corpustools.test import xmltester

HERE = os.path.dirname(__file__)


class TestPDFFontspecs(unittest.TestCase):

    def test_add_fontspec(self):
        f1 = etree.fromstring(
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>')
        f2 = etree.fromstring(
            '<fontspec id="5" size="19" family="Times" color="#231f20"/>')
        f3 = etree.fromstring(
            '<fontspec id="6" size="13" family="Times" color="#231f20"/>')

        pdffontspecs = pdfconverter.PDFFontspecs()
        pdffontspecs.add_fontspec(f1)
        pdffontspecs.add_fontspec(f2)
        pdffontspecs.add_fontspec(f3)

        self.assertListEqual(
            sorted([id for p, id in pdffontspecs.pdffontspecs.items()]),
            ["1", "5"])
        self.assertDictEqual(pdffontspecs.duplicates, {"6": "1"})

    def test_corrected_id(self):
        page = etree.fromstring('''
            <page number="3" position="absolute" top="0" left="0" height="1325" width="955">
                <fontspec id="1" size="13" family="Times" color="#231f20"/>
                <fontspec id="5" size="19" family="Times" color="#231f20"/>
                <fontspec id="6" size="13" family="Times" color="#231f20"/>
                <text top="634" left="104" width="178" height="26" font="5"><i><b>Politihkalaš vuođđu </b></i></text>
                <text top="666" left="104" width="312" height="18" font="1">Ráđđehusbellodagaid politihkalaš vuođđu – <i>Soria </i></text>
                <text top="687" left="104" width="318" height="18" font="6"><i>Moria-julggaštus</i> – almmuha ulbmilin dakkár sáme-</text>
            </page>
        ''')  # nopep8
        pfs = pdfconverter.PDFFontspecs()
        for xmlfontspec in page.iter('fontspec'):
            pfs.add_fontspec(xmlfontspec)
        ppage = pdfconverter.PDFPage(page)
        ppage.fix_font_id(pfs)

        self.assertListEqual(
            [pdftextelement.font for pdftextelement in ppage.textelements],
            ["5", "1", "1"])


class TestPDFPageMetaData(unittest.TestCase):

    def test_compute_default_margins(self):
        """Test if the default margins are set."""
        page1 = pdfconverter.PDFPageMetadata(
            page_number=1, page_height=1263, page_width=862)

        self.assertEqual(
            page1.compute_margins(), {
                'left_margin': 60,
                'right_margin': 801,
                'top_margin': 88,
                'bottom_margin': 1174
            })

    def test_compute_margins1(self):
        """Test parse_margin_lines."""
        metadata = xslsetter.MetadataHandler('test.pdf.xsl', create=True)
        metadata.set_variable('left_margin', '7=5')
        metadata.set_variable('right_margin', 'odd=10,even=15,3=5')
        metadata.set_variable('top_margin', '8=8')
        metadata.set_variable('bottom_margin', '9=20')

        page1 = pdfconverter.PDFPageMetadata(
            page_number=1,
            page_height=1263,
            page_width=862,
            metadata_margins=metadata.margins)

        self.assertEqual(
            page1.compute_margins(), {
                'left_margin': 60,
                'right_margin': 775,
                'top_margin': 88,
                'bottom_margin': 1174
            })
        page2 = pdfconverter.PDFPageMetadata(
            page_number=2,
            page_height=1263,
            page_width=862,
            metadata_margins=metadata.margins)
        self.assertEqual(
            page2.compute_margins(), {
                'left_margin': 60,
                'right_margin': 732,
                'top_margin': 88,
                'bottom_margin': 1174
            })
        page3 = pdfconverter.PDFPageMetadata(
            page_number=3,
            page_height=1263,
            page_width=862,
            metadata_margins=metadata.margins)
        self.assertEqual(
            page3.compute_margins(), {
                'left_margin': 60,
                'right_margin': 818,
                'top_margin': 88,
                'bottom_margin': 1174
            })
        page7 = pdfconverter.PDFPageMetadata(
            page_number=7,
            page_height=1263,
            page_width=862,
            metadata_margins=metadata.margins)
        self.assertEqual(
            page7.compute_margins(), {
                'left_margin': 43,
                'right_margin': 775,
                'top_margin': 88,
                'bottom_margin': 1174
            })
        page8 = pdfconverter.PDFPageMetadata(
            page_number=8,
            page_height=1263,
            page_width=862,
            metadata_margins=metadata.margins)
        self.assertEqual(
            page8.compute_margins(), {
                'left_margin': 60,
                'right_margin': 732,
                'top_margin': 101,
                'bottom_margin': 1174
            })
        page9 = pdfconverter.PDFPageMetadata(
            page_number=9,
            page_height=1263,
            page_width=862,
            metadata_margins=metadata.margins)
        self.assertEqual(
            page9.compute_margins(), {
                'left_margin': 60,
                'right_margin': 775,
                'top_margin': 88,
                'bottom_margin': 1010
            })

    def test_compute_inner_margins_1(self):
        """Test if inner margins is set for the specified page."""
        metadata = xslsetter.MetadataHandler('test.pdf.xsl', create=True)
        metadata.set_variable('inner_top_margin', '1=40')
        metadata.set_variable('inner_bottom_margin', '1=40')

        page1 = pdfconverter.PDFPageMetadata(
            page_number=1,
            page_height=1263,
            page_width=862,
            metadata_inner_margins=metadata.inner_margins)

        self.assertEqual(
            page1.compute_inner_margins(), {
                'inner_top_margin': 505,
                'inner_bottom_margin': 757,
                'inner_left_margin': 0,
                'inner_right_margin': 862
            })

    def test_compute_inner_margins_2(self):
        """Test that inner margins is empty for the specified page."""
        metadata = xslsetter.MetadataHandler('test.pdf.xsl', create=True)
        metadata.set_variable('inner_top_margin', '1=40')
        metadata.set_variable('inner_bottom_margin', '1=40')

        page1 = pdfconverter.PDFPageMetadata(
            page_number=2,
            page_height=1263,
            page_width=862,
            metadata_inner_margins=metadata.inner_margins)

        self.assertEqual(page1.compute_inner_margins(), {})

    def test_width(self):
        page = pdfconverter.PDFPageMetadata(
            page_number=1, page_height=1263, page_width=862)

        self.assertEqual(page.page_number, 1)
        self.assertEqual(page.page_height, 1263)
        self.assertEqual(page.page_width, 862)


class TestPDFPage(xmltester.XMLTester):

    def test_is_inside_margins1(self):
        """top and left inside margins."""
        t = pdfconverter.PDFTextElement(
            etree.fromstring('<text top="109" left="135"/>'))
        margins = {}
        margins['left_margin'] = 62
        margins['right_margin'] = 802
        margins['top_margin'] = 88
        margins['bottom_margin'] = 1174

        p2x = pdfconverter.PDFPage(
            etree.fromstring('<page number="2" height="1263" width="862"/>'))

        self.assertTrue(p2x.is_inside_margins(t, margins))

    def test_is_inside_margins2(self):
        """top above top margin and left inside margins."""
        t = pdfconverter.PDFTextElement(
            etree.fromstring('<text top="85" left="135"/>'))
        margins = {}
        margins['left_margin'] = 62
        margins['right_margin'] = 802
        margins['top_margin'] = 88
        margins['bottom_margin'] = 1174

        p2x = pdfconverter.PDFPage(
            etree.fromstring('<page number="2" height="1263" width="862"/>'))

        self.assertFalse(p2x.is_inside_margins(t, margins))

    def test_is_inside_margins3(self):
        """top below bottom margin and left inside margins."""
        t = pdfconverter.PDFTextElement(
            etree.fromstring('<text top="1178" left="135"/>'))
        margins = {}
        margins['left_margin'] = 62
        margins['right_margin'] = 802
        margins['top_margin'] = 88
        margins['bottom_margin'] = 1174

        p2x = pdfconverter.PDFPage(
            etree.fromstring('<page number="2" height="1263" width="862"/>'))

        self.assertFalse(p2x.is_inside_margins(t, margins))

    def test_is_inside_margins4(self):
        """top inside margins and left outside right margin."""
        t = pdfconverter.PDFTextElement(
            etree.fromstring('<text top="1000" left="50"/>'))
        margins = {}
        margins['left_margin'] = 62
        margins['right_margin'] = 802
        margins['top_margin'] = 88
        margins['bottom_margin'] = 1174

        p2x = pdfconverter.PDFPage(
            etree.fromstring('<page number="2" height="1263" width="862"/>'))

        self.assertFalse(p2x.is_inside_margins(t, margins))

    def test_is_inside_margins5(self):
        """top inside margins and left outside left margin."""
        t = pdfconverter.PDFTextElement(
            etree.fromstring('<text top="1000" left="805"/>'))
        margins = {}
        margins['left_margin'] = 62
        margins['right_margin'] = 802
        margins['top_margin'] = 88
        margins['bottom_margin'] = 1174

        p2x = pdfconverter.PDFPage(
            etree.fromstring('<page number="2" height="1263" width="862"/>'))

        self.assertFalse(p2x.is_inside_margins(t, margins))

    def test_is_skip_page_1(self):
        """Odd page should be skipped when odd is in skip_pages."""
        p2x = pdfconverter.PDFPage(
            etree.fromstring('<page number="1" height="1263" width="862"/>'))

        self.assertTrue(p2x.is_skip_page(['odd']))

    def test_is_skip_page_2(self):
        """Even page should be skipped when even is in skip_pages."""
        p2x = pdfconverter.PDFPage(
            etree.fromstring('<page number="2" height="1263" width="862"/>'))

        self.assertTrue(p2x.is_skip_page(['even']))

    def test_is_skip_page_3(self):
        """Even page should not be skipped when odd is in skip_pages."""
        p2x = pdfconverter.PDFPage(
            etree.fromstring('<page number="2" height="1263" width="862"/>'))

        self.assertFalse(p2x.is_skip_page(['odd']))

    def test_is_skip_page_4(self):
        """Odd page should not be skipped when even is in skip_pages."""
        p2x = pdfconverter.PDFPage(
            etree.fromstring('<page number="1" height="1263" width="862"/>'))

        self.assertFalse(p2x.is_skip_page(['even']))

    def test_is_skip_page_5(self):
        """Page should not be skipped when not in skip_range."""
        p2x = pdfconverter.PDFPage(
            etree.fromstring('<page number="1" height="1263" width="862"/>'))

        self.assertFalse(p2x.is_skip_page(['even', 3]))

    def test_is_skip_page_6(self):
        """Page should be skipped when in skip_range."""
        p2x = pdfconverter.PDFPage(
            etree.fromstring('<page number="3" height="1263" width="862"/>'))

        self.assertTrue(p2x.is_skip_page(['even', 3]))


class TestPDF2XMLConverter(xmltester.XMLTester):
    """Test the class that converts from pdf2xml to giellatekno/divvun xml."""

    def test_pdf_converter(self):
        pdfdocument = pdfconverter.PDF2XMLConverter(
            os.path.join(
                HERE, 'converter_data/fakecorpus/orig/sme/riddu/pdf-test.pdf'))
        got = pdfdocument.convert2intermediate()
        want = etree.parse(
            os.path.join(HERE, 'converter_data/pdf-xml2pdf-test.xml'))

        self.assertXmlEqual(got, want)

    def test_parse_page_1(self):
        """Page with one paragraph, three <text> elements."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="106" left="100" width="100" height="19" font="1">a </text>'
            '<text top="126" left="100" width="100" height="19" font="1">b </text>'
            '<text top="145" left="100" width="100" height="19" font="1">c.</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(p2x.extractor.body,
                            etree.fromstring('<body><p>a b c.</p></body>'))

    def test_parse_page_2(self):
        """Page with two paragraphs, four <text> elements."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="106" left="100" width="100" height="19" font="1">a </text>'
            '<text top="126" left="100" width="100" height="19" font="1">b.</text>'
            '<text top="166" left="100" width="100" height="19" font="1">c </text>'
            '<text top="186" left="100" width="100" height="19" font="1">d.</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            p2x.extractor.body,
            etree.fromstring('<body><p>a b.</p><p>c d.</p></body>'))

    def test_parse_page_3(self):
        """Page with one paragraph, one <text> elements."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="145" left="100" width="100" height="19" font="1">3.</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(p2x.extractor.body,
                            etree.fromstring('<body><p>3.</p></body>'))

    def test_parse_page_4(self):
        """One text element with a ascii letter, the other one with a non-ascii

        This makes two parts lists. The first list contains one element that is
        of type str, the second list contains one element that is unicode.
        """
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="215" left="100" width="51" height="14" font="1">R</text>'
            '<text top="245" left="100" width="39" height="14" font="1">Ø</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(p2x.extractor.body,
                            etree.fromstring('<body><p>R</p><p>Ø</p></body>'))

    def test_parse_page_5(self):
        """Test parse pages

        One text element containing a <b>, the other one with a
        non-ascii string. Both belong to the same paragraph.
        """
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="215" left="100" width="51" height="14" font="1"><b>R</b></text>'
            '<text top="235" left="100" width="39" height="14" font="1">Ø</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            p2x.extractor.body,
            etree.fromstring('<body><p><em type="bold">R</em>Ø</p></body>'))

    def test_parse_page_6(self):
        """One text element ending with a hyphen."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="215" left="100" width="51" height="14" font="1">R-</text>'
            '<text top="235" left="100" width="39" height="14" font="1">Ø</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(p2x.extractor.body,
                            etree.fromstring(u'<body><p>R\xADØ</p></body>'))

    def test_parse_page_7(self):
        """One text element ending with a hyphen."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="215" left="100" width="51" height="14" font="1">R -</text>'
            '<text top="235" left="100" width="39" height="14" font="1">Ø</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(p2x.extractor.body,
                            etree.fromstring('<body><p>R - Ø</p></body>'))

    def test_parse_page_8(self):
        """One text element ending with a hyphen."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="15" size="13" family="Times" color="#231f20"/>'
            '<text top="196" left="142" width="69" height="21" font="15">'
            '<b>JULE-</b></text>'
            '<text top="223" left="118" width="123" height="21" font="15">'
            '<b>HANDEL</b></text></page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            p2x.extractor.body,
            etree.fromstring(
                u'<body><p><em type="bold">JULE\xADHANDEL</em></p></body>'))

    def test_parse_page_9(self):
        """Two <text> elements. One is above the top margin."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="70" left="100" width="100" height="19" font="1">Page 1</text>'
            '<text top="145" left="100" width="100" height="19" font="1">3.</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(p2x.extractor.body,
                            etree.fromstring('<body><p>3.</p></body>'))

    def test_parse_page_10(self):
        """Two <text> elements. One is below the bottom margin."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="1200" left="100" width="100" height="19" font="1">Page 1</text>'
            '<text top="145" left="100" width="100" height="19" font="1">3.</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(p2x.extractor.body,
                            etree.fromstring('<body><p>3.</p></body>'))

    def test_parse_page_11(self):
        """Two <text> elements. One is to the left of the right margin."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="500" left="50" width="100" height="19" font="1">Page 1</text>'
            '<text top="145" left="100" width="100" height="19" font="1">3.</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(p2x.extractor.body,
                            etree.fromstring('<body><p>3.</p></body>'))

    def test_parse_page_12(self):
        """Two <text> elements. One is to the right of the left margin."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="500" left="850" width="100" height="19" font="1">Page 1</text>'
            '<text top="145" left="100" width="100" height="19" font="1">3.</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(p2x.extractor.body,
                            etree.fromstring('<body><p>3.</p></body>'))

    def test_parse_page_13(self):
        """Test list detection with • character."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<text top="195" left="104" width="260" height="18" font="1">'
            'vuosttaš dábálaš linnjá</text>'
            '<text top="237" left="104" width="311" height="18" font="1">'
            '• Vuosttaš listolinnjá </text>'
            '<text top="258" left="121" width="296" height="18" font="1">'
            'vuosttaš listolinnjá joaktta</text>'
            '<text top="279" left="104" width="189" height="18" font="1">'
            '• Nubbi listo-</text>'
            '<text top="300" left="121" width="324" height="18" font="1">'
            'linnjá</text>'
            '<text top="321" left="104" width="40" height="18" font="1">'
            'Nubbi dábáláš linnjá</text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.maxDiff = None
        self.assertXmlEqual(
            p2x.extractor.body,
            etree.fromstring(u'<body>'
                             u'<p>vuosttaš dábálaš linnjá</p>'
                             u'<p type="listitem">• Vuosttaš listolinnjá  '
                             u'vuosttaš listolinnjá joaktta</p>'
                             u'<p type="listitem">• Nubbi listo\xADlinnjá</p>'
                             u'<p>Nubbi dábáláš linnjá</p>'
                             u'</body>'))

    def test_parse_page_14(self):
        """Test that elements outside margin is not added."""
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<text top="1104" left="135" width="45" height="16" font="2">'
            '1751, </text>'
            '<text top="1184" left="135" width="4" height="15" font="0"> '
            '</text>'
            '<text top="1184" left="437" width="37" height="15" font="0">'
            '– 1 – </text>'
            '</page>')

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(p2x.extractor.body,
                            etree.fromstring('<body>'
                                             '<p>1751, </p>'
                                             '</body>'))

    def test_parse_page_soria_moria(self):
        """The last element was not added to the p element."""
        page_element = etree.fromstring('''
            <page number="1" height="1263" width="862">
                <text top="666" left="104" width="312" height="18" font="1">A – <i>b </i></text>
                <text top="687" left="104" width="318" height="18" font="1"><i>c-d</i> – e-</text>
                <text top="708" left="104" width="328" height="18" font="1">f </text>
            </page>
        ''')  # nopep8

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(p2x.extractor.body,
                            etree.fromstring(
                                u'<body><p>A – <em type="italic">b c-d</em> – '
                                u'e\xADf </p></body>'))

    def test_parse_pdf2xmldoc1(self):
        """Test how a parsing a simplistic pdf2xml document works."""
        pdf2xml = etree.fromstring('''
            <pdf2xml>
                <page number="1" height="1263" width="862">
                    <fontspec id="1" size="13" family="Times" color="#231f20"/>
                    <text top="145" left="100" width="100" height="19" font="1">1.</text>
                </page>
                <page number="2" height="1263" width="862">
                    <text top="145" left="100" width="100" height="19" font="1">2.</text>
                </page>
                <page number="3" height="1263" width="862">
                    <text top="145" left="100" width="100" height="19" font="1">3.</text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'<body><p>1.</p><p>2.</p><p>3.</p></body>'

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_parse_pdf2xmldoc2(self):
        """Test if pages really are skipped."""
        pdf2xml = etree.fromstring('''
            <pdf2xml>
                <page number="1" height="1263" width="862">
                    <fontspec id="1" size="13" family="Times" color="#231f20"/>
                    <text top="145" left="100" width="100" height="19" font="1">1.</text>
                </page>
                <page number="2" height="1263" width="862">
                    <text top="145" left="100" width="100" height="19" font="1">2.</text>
                </page>
                <page number="3" height="1263" width="862">
                    <text top="145" left="100" width="100" height="19" font="1">3.</text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'<body><p>2.</p><p>3.</p></body>'

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.metadata.set_variable('skip_pages', '1')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_parse_pdf2xmldoc3(self):
        """Check if paragraph is continued from page to page

        Paragraph should continue if the first character on next page is a
        lower case character
        """
        pdf2xml = etree.fromstring('''
            <pdf2xml>
                <page number="1" position="absolute" top="0" left="0" height="1020" width="723">
                    <text top="898" left="80" width="512" height="19" font="0">Dán </text>
                </page>
                <page number="2" position="absolute" top="0" left="0" height="1020" width="723">
                    <text top="43" left="233" width="415" height="16" font="7">Top text </text>
                    <text top="958" left="174" width="921" height="19" font="0">15 </text>
                    <text top="93" left="131" width="512" height="19" font="0">barggus.</text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'<body><p>Dán barggus.</p></body>'

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_parse_pdf2xmldoc4(self):
        """Check if paragraph is continued from page to page.

        Paragraph should continue if the first character on next page is a
        lower case character
        """
        pdf2xml = etree.fromstring('''
            <pdf2xml>
                <page number="1" position="absolute" top="0" left="0" height="1020" width="723">
                    <text top="898" left="80" width="512" height="19" font="0">Dán ovddidan-</text>
                </page>
                <page number="2" position="absolute" top="0" left="0" height="1020" width="723">
                    <text top="43" left="233" width="415" height="16" font="7">Top text </text>
                    <text top="958" left="174" width="921" height="19" font="0">15 </text>
                    <text top="93" left="131" width="512" height="19" font="0">barggus.</text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'<body><p>Dán ovddidan\xADbarggus.</p></body>'

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_text_disappears(self):
        """Bug 2115, Store deler av teksten blir borte."""
        pdf2xml = etree.fromstring('''
            <pdf2xml>
                <page number="40" position="absolute" top="0" left="0" height="1263" width="892">
                    <text top="1061" left="106" width="680" height="20" font="7"><i>vuođđooahpa-</i></text>
                    <text top="1085" left="106" width="653" height="20" font="7"><i>hussi. </i></text>
                    <text top="1110" left="106" width="5" height="20" font="7"><i> </i></text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'''<body><p><em type="italic">vuođđooahpa\xADhussi. </em></p></body>'''

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_text_unwanted_line_shift(self):
        """Bug 2107, Linjeskift hvor det ikke skal være."""
        pdf2xml = etree.fromstring('''
            <pdf2xml>
                <page number="40" position="absolute" top="0" left="0" height="1263" width="892">
                    <text top="354" left="119" width="205" height="22" font="2">1.1.   RIEKTEJOAVKKU</text>
                    <text top="352" left="325" width="8" height="15" font="7">1</text>
                    <text top="354" left="332" width="6" height="22" font="2"> </text>
                    <text top="350" left="339" width="4" height="16" font="7"> </text>
                    <text top="354" left="343" width="104" height="22" font="2">MANDÁHTA</text>
                    <text top="352" left="447" width="12" height="15" font="7">2 </text>
                    <text top="354" left="460" width="143" height="22" font="2">JA ČOAHKÁDUS</text>
                    <text top="352" left="603" width="12" height="15" font="7">3 </text>
                    <text top="354" left="615" width="13" height="22" font="2">  </text>
                    <text top="376" left="119" width="6" height="22" font="2"> </text>
                    <text top="398" left="119" width="389" height="22" font="2">1.1.1 Riektejoavkku nammadeami duogáš </text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'''
            <body>
                <p>1.1. RIEKTEJOAVKKU MANDÁHTA JA ČOAHKÁDUS</p>
                <p>1.1.1 Riektejoavkku nammadeami duogáš</p>
            </body>
        '''

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_parse_pdf2xmldoc_ends_with_dot(self):
        """If last string on a page ends with ., do not continue paragraph to next page."""
        pdf2xml = etree.fromstring('''
            <pdf2xml>
                <page number="1" height="1263" width="862">
                    <fontspec id="1" size="13" family="Times" color="#231f20"/>
                    <text top="145" left="100" width="100" height="19" font="1">1.</text>
                </page>
                <page number="2" height="1263" width="862">
                    <text top="145" left="100" width="100" height="19" font="1">2.</text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'<body><p>1.</p><p>2.</p></body>'

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_parse_pdf2xmldoc_ends_with_exclam(self):
        """If last string on a page ends with !, do not continue paragraph to next page."""
        pdf2xml = etree.fromstring('''
            <pdf2xml>
                <page number="1" height="1263" width="862">
                    <fontspec id="1" size="13" family="Times" color="#231f20"/>
                    <text top="145" left="100" width="100" height="19" font="1">1!</text>
                </page>
                <page number="2" height="1263" width="862">
                    <text top="145" left="100" width="100" height="19" font="1">2.</text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'<body><p>1!</p><p>2.</p></body>'

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_parse_pdf2xmldoc_ends_with_question(self):
        """If last string on a page ends with ?, do not continue paragraph to next page."""
        pdf2xml = etree.fromstring(
            '<pdf2xml>'
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="145" left="100" width="100" height="19" font="1">1?</text>'
            '</page>'
            '<page number="2" height="1263" width="862">'
            '<text top="145" left="100" width="100" height="19" font="1">2.</text>'
            '</page>'
            '</pdf2xml>')
        want = u'<body><p>1?</p><p>2.</p></body>'

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_parse_pdf2xmldoc_not_end_of_sentence(self):
        """If last string on a page is not ended, continue paragraph."""
        pdf2xml = etree.fromstring(
            '<pdf2xml>'
            '<page number="1" height="1263" width="862">'
            '<fontspec id="1" size="13" family="Times" color="#231f20"/>'
            '<text top="145" left="100" width="100" height="19" font="1">a </text>'
            '</page>'
            '<page number="2" height="1263" width="862">'
            '<text top="145" left="100" width="100" height="19" font="1">b.</text>'
            '</page>'
            '</pdf2xml>')
        want = u'<body><p>a b.</p></body>'

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_parse_pdf2xmldoc_text_on_same_line_different_font(self):
        """Test of bug2101."""
        pdf2xml = etree.fromstring('''
            <pdf2xml>
                <page number="1" height="1263" width="862"><fontspec/>
                    <text top="187" left="64" width="85" height="14" font="20">bajás</text>
                    <text top="187" left="149" width="6" height="14" font="8">š</text>
                    <text top="187" left="155" width="280" height="14" font="20">addandili</text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'<body><p>bajásšaddandili</p></body>'

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_parse_pdf2xmldoc_pp_tjenesten(self):
        """Test of bug2101."""
        pdf2xml = etree.fromstring(u'''
            <pdf2xml>
                <page number="4" position="absolute" top="0" left="0" height="1262" width="892">
                    <text top="942" left="133" width="640" height="23" font="4"> ahte buoridit unnitlogugielagiid oahpahusfálaldaga dási ja buoridit barggu, man olis </text>
                    <text top="965" left="160" width="617" height="22" font="4">ovddidit fátmmasteaddji, máŋggakultuvrralaš oahppansearvevuođaid mánáidgárdái </text>
                    <text top="986" left="160" width="165" height="22" font="4">ja vuođđooahpahussii.</text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'''
            <body>
                <p type="listitem"> ahte buoridit unnitlogugielagiid oahpahusfálaldaga dási ja buoridit barggu, man olis ovddidit fátmmasteaddji, máŋggakultuvrralaš oahppansearvevuođaid mánáidgárdái ja vuođđooahpahussii.</p>
            </body>'''  # nopep8

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))

    def test_parse_pdf2xmldoc_em_at_end_of_page_and_start_of_next_page(self):
        pdf2xml = etree.fromstring(u'''
            <pdf2xml>
                <page number="1" position="absolute" top="0" left="0" height="1263" width="892">
                    <fontspec id="0" size="18" family="Times" color="#000000"/>
                    <text top="899" left="98" width="719" height="23" font="0">Tabeallas 2.1 oaidnit lohku bissu dássedin mánáidgárddiin main lea </text>
                    <text top="926" left="98" width="703" height="23" font="0">sámegielfálaldat. Lohku mánáidgárddiin maid Sámediggi gohčoda  <i>sámi</i> </text>
                    <text top="954" left="98" width="717" height="23" font="0">mánáidgárdin, gal lea njiedjan maŋemus vihtta jagi ollislaččat, muhto </text>
                    <text top="982" left="98" width="697" height="23" font="0">mánáidgárdefálaldagat gohčoduvvon  <i>sámegielat fálaldat dárogielat mánáid-</i></text>
                </page>
                <page number="1" position="absolute" top="0" left="0" height="1263" width="892">
                    <fontspec id="2" size="18" family="Times" color="#000000"/>
                    <text top="116" left="98" width="710" height="23" font="2"><i>gárddiin</i> leat lassánan, nu ahte fálaldagaid ollislaš lohku lea goitge bisson </text>
                </page>
            </pdf2xml>
        ''')  # nopep8
        want = u'''
            <body>
                <p>
                    Tabeallas 2.1 oaidnit lohku bissu dássedin mánáidgárddiin main lea
                    sámegielfálaldat. Lohku mánáidgárddiin maid Sámediggi gohčoda
                    <em type="italic">sámi</em>mánáidgárdin, gal lea njiedjan maŋemus
                    vihtta jagi ollislaččat, muhto mánáidgárdefálaldagat gohčoduvvon
                    <em type="italic">sámegielat fálaldat dárogielat mánáid\xADgárddiin</em>leat
                    lassánan, nu ahte fálaldagaid ollislaš lohku lea goitge bisson
                </p>
            </body>
        '''  # nopep8

        p2x = pdfconverter.PDF2XMLConverter('orig/sme/riddu/bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(p2x.extractor.body, etree.fromstring(want))
