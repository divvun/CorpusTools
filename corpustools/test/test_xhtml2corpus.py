# -*- coding: utf-8 -*-
import unittest
import lxml.doctestcompare
import lxml.etree
import os
import doctest

from corpustools import converter


here = os.path.join(os.path.dirname(__file__), 'xhtml2corpus')


class TestConversion(unittest.TestCase):
    """Class to test html to divvun-corpus format conversion
    """
    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal
        """
        got = lxml.etree.tostring(got)
        want = lxml.etree.tostring(want)
        checker = lxml.doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(
                doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)

    def test_list_within_list(self):

        got = converter.HTMLConverter(
            os.path.join(here, "ol-within-ol.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "ol-within-ol.xml"))

        self.assertXmlEqual(got, want)

    def test_h1_6(self):
        got = converter.HTMLConverter(
            os.path.join(here, "h1-6.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "h1-6.xml"))

        self.assertXmlEqual(got, want)

    def test_a_within_list(self):
        got = converter.HTMLConverter(
            os.path.join(here, "a-within-li.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "a-within-li.xml"))

        self.assertXmlEqual(got, want)

    def test_span_within_list(self):
        got = converter.HTMLConverter(
            os.path.join(here, "span-within-li.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "span-within-li.xml"))

        self.assertXmlEqual(got, want)

    def test_span(self):
        got = converter.HTMLConverter(
            os.path.join(here, "span.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "span.xml"))

        self.assertXmlEqual(got, want)

    def test_blockquote(self):
        got = converter.HTMLConverter(
            os.path.join(here, "blockquote.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "blockquote.xml"))

        self.assertXmlEqual(got, want)

    def test_td_font_span_strong(self):
        got = converter.HTMLConverter(
            os.path.join(here,
                         "td-font-span-strong.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "td-font-span-strong.xml"))

        self.assertXmlEqual(got, want)

    def test_td_font_span(self):
        got = converter.HTMLConverter(
            os.path.join(here, "td-font-span.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "td-font-span.xml"))

        self.assertXmlEqual(got, want)

    def test_td_span(self):
        got = converter.HTMLConverter(
            os.path.join(here, "td-span.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "td-span.xml"))

        self.assertXmlEqual(got, want)

    def test_td_font_span_span_span(self):
        got = converter.HTMLConverter(
            os.path.join(here,
                         "td-font-span-span-span.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here,
                                             "td-font-span-span-span.xml"))

        self.assertXmlEqual(got, want)

    def test_td_a(self):
        got = converter.HTMLConverter(
            os.path.join(here, "td-a.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "td-a.xml"))

        self.assertXmlEqual(got, want)

    def test_td_font(self):
        got = converter.HTMLConverter(
            os.path.join(here, "td-font.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "td-font.xml"))

        self.assertXmlEqual(got, want)

    def test_td_table_tr_td(self):
        got = converter.HTMLConverter(
            os.path.join(here, "td-table-tr-td.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "td-table-tr-td.xml"))

        self.assertXmlEqual(got, want)

    def test_td_div(self):
        got = converter.HTMLConverter(
            os.path.join(here, "td-div.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "td-div.xml"))

        self.assertXmlEqual(got, want)

    def test_div_div_a_span(self):
        got = converter.HTMLConverter(
            os.path.join(here, "div-div-a-span.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "div-div-a-span.xml"))

        self.assertXmlEqual(got, want)

    def test_div_hx(self):
        got = converter.HTMLConverter(
            os.path.join(here, "div-hx.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "div-hx.xml"))

        self.assertXmlEqual(got, want)

    def test_div_text(self):
        got = converter.HTMLConverter(
            os.path.join(here, "div-text.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "div-text.xml"))

        self.assertXmlEqual(got, want)

    def test_div(self):
        got = converter.HTMLConverter(
            os.path.join(here, "div.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "div.xml"))

        self.assertXmlEqual(got, want)

    def test_div_table(self):
        got = converter.HTMLConverter(
            os.path.join(here, "div-table.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "div-table.xml"))

        self.assertXmlEqual(got, want)

    def test_li_div(self):
        got = converter.HTMLConverter(
            os.path.join(here, "li-div.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "li-div.xml"))

        self.assertXmlEqual(got, want)

    def test_div_ul(self):
        got = converter.HTMLConverter(
            os.path.join(here, "div-ul.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "div-ul.xml"))

        self.assertXmlEqual(got, want)

    def test_div_div_a(self):
        got = converter.HTMLConverter(
            os.path.join(here, "div-div-a.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "div-div-a.xml"))

        self.assertXmlEqual(got, want)

    def test_div_p_and_text(self):
        got = converter.HTMLConverter(
            os.path.join(here, "div-p-and-text.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "div-p-and-text.xml"))

        self.assertXmlEqual(got, want)

    def test_td_p(self):
        got = converter.HTMLConverter(
            os.path.join(here, "td-p.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "td-p.xml"))

        self.assertXmlEqual(got, want)

    def test_td_h3(self):
        got = converter.HTMLConverter(
            os.path.join(here, "td-h3.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "td-h3.xml"))

        self.assertXmlEqual(got, want)

    def test_div_span(self):
        got = converter.HTMLConverter(
            os.path.join(here, "div-span.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "div-span.xml"))

        self.assertXmlEqual(got, want)

    def test_td_b(self):
        got = converter.HTMLConverter(
            os.path.join(here, "td-b.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "td-b.xml"))

        self.assertXmlEqual(got, want)

    def test_td_span_font(self):
        got = converter.HTMLConverter(
            os.path.join(here, "td-span-font.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "td-span-font.xml"))

        self.assertXmlEqual(got, want)

    def test_td_b_and_text(self):
        got = converter.HTMLConverter(
            os.path.join(here, "td-b-and-text.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "td-b-and-text.xml"))

        self.assertXmlEqual(got, want)

    def test_td_span_and_b_and_p(self):
        got = converter.HTMLConverter(
            os.path.join(here,
                         "td-span-and-b-and-p.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "td-span-and-b-and-p.xml"))

        self.assertXmlEqual(got, want)

    def test_p_b_span(self):
        got = converter.HTMLConverter(
            os.path.join(here, "p-b-span.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "p-b-span.xml"))

        self.assertXmlEqual(got, want)

    def test_th_div(self):
        got = converter.HTMLConverter(
            os.path.join(here, "th-div.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "th-div.xml"))

        self.assertXmlEqual(got, want)

    def test_thead(self):
        got = converter.HTMLConverter(
            os.path.join(here, "thead.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "thead.xml"))

        self.assertXmlEqual(got, want)

    def test_p_font_font_b_span(self):
        got = converter.HTMLConverter(
            os.path.join(here,
                         "p-font-font-b-span.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "p-font-font-b-span.xml"))

        self.assertXmlEqual(got, want)

    def test_p_span_b(self):
        got = converter.HTMLConverter(
            os.path.join(here, "p-span-b.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "p-span-b.xml"))

        self.assertXmlEqual(got, want)

    def test_td_h2_text_p(self):
        got = converter.HTMLConverter(
            os.path.join(here,
                         "td-h2-and-text-and-p.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "td-h2-and-text-and-p.xml"))

        self.assertXmlEqual(got, want)

    def test_td_p_b(self):
        got = converter.HTMLConverter(
            os.path.join(here, "td-p-and-b.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "td-p-and-b.xml"))

        self.assertXmlEqual(got, want)

    def test_td_text_i_p(self):
        got = converter.HTMLConverter(
            os.path.join(here,
                         "td-text-and-i-and-p.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "td-text-and-i-and-p.xml"))

        self.assertXmlEqual(got, want)

    def test_div_b_text(self):
        got = converter.HTMLConverter(
            os.path.join(here, "div-b-and-text.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "div-b-and-text.xml"))

        self.assertXmlEqual(got, want)

    def test_div_text_and_div(self):
        got = converter.HTMLConverter(
            os.path.join(here, "div-text-and-div.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "div-text-and-div.xml"))

        self.assertXmlEqual(got, want)

    def test_ul_li_div_p(self):
        got = converter.HTMLConverter(
            os.path.join(here, "ul-li-div-p.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "ul-li-div-p.xml"))

        self.assertXmlEqual(got, want)

    def test_font_span_font_sub(self):
        got = converter.HTMLConverter(
            os.path.join(here,
                         "font-span-font-sub.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "font-span-font-sub.xml"))

        self.assertXmlEqual(got, want)

    def test_li_a_b_font(self):
        got = converter.HTMLConverter(
            os.path.join(here, "li-a-b-font.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "li-a-b-font.xml"))

        self.assertXmlEqual(got, want)

    def test_div_h1_and_a(self):
        got = converter.HTMLConverter(
            os.path.join(here, "div-h1-and-a.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "div-h1-and-a.xml"))

        self.assertXmlEqual(got, want)

    def test_div_h1_and_text(self):
        got = converter.HTMLConverter(
            os.path.join(here, "div-h1-and-text.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "div-h1-and-text.xml"))

        self.assertXmlEqual(got, want)

    def test_div_p_and_font(self):
        got = converter.HTMLConverter(
            os.path.join(here, "div-p-and-font.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "div-p-and-font.xml"))

        self.assertXmlEqual(got, want)

    def test_div_text_and_span(self):
        got = converter.HTMLConverter(
            os.path.join(here,
                         "div-text-and-span.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "div-text-and-span.xml"))

        self.assertXmlEqual(got, want)

    def test_div_font_and_i(self):
        got = converter.HTMLConverter(
            os.path.join(here, "div-font-and-i.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "div-font-and-i.xml"))

        self.assertXmlEqual(got, want)

    def test_ul_li_p_i(self):
        got = converter.HTMLConverter(
            os.path.join(here, "ul-li-p-i.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "ul-li-p-i.xml"))

        self.assertXmlEqual(got, want)

    def test_p_a_b(self):
        got = converter.HTMLConverter(
            os.path.join(here, "p-a-b.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "p-a-b.xml"))

        self.assertXmlEqual(got, want)

    def test_td_a_b(self):
        got = converter.HTMLConverter(
            os.path.join(here, "td-a-b.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "td-a-b.xml"))

        self.assertXmlEqual(got, want)

    def test_blockquote_p_and_text(self):
        got = converter.HTMLConverter(
            os.path.join(here,
                         "blockquote-p-and-text.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here,
                                             "blockquote-p-and-text.xml"))

        self.assertXmlEqual(got, want)

    def test_tr_td_em(self):
        got = converter.HTMLConverter(
            os.path.join(here, "tr-td-em.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "tr-td-em.xml"))

        self.assertXmlEqual(got, want)

    def test_td_u(self):
        got = converter.HTMLConverter(
            os.path.join(here, "td-u.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "td-u.xml"))

        self.assertXmlEqual(got, want)

    def test_td_strong(self):
        got = converter.HTMLConverter(
            os.path.join(here, "td-strong.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "td-strong.xml"))

        self.assertXmlEqual(got, want)

    def test_th_p(self):
        got = converter.HTMLConverter(
            os.path.join(here, "th-p.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "th-p.xml"))

        self.assertXmlEqual(got, want)

    def test_h1_b(self):
        got = converter.HTMLConverter(
            os.path.join(here, "h1-b.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "h1-b.xml"))

        self.assertXmlEqual(got, want)

    def test_th_b(self):
        got = converter.HTMLConverter(
            os.path.join(here, "th-b.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "th-b.xml"))

        self.assertXmlEqual(got, want)

    def test_address(self):
        got = converter.HTMLConverter(
            os.path.join(here, "address.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "address.xml"))

        self.assertXmlEqual(got, want)

    def test_p_to_p_listitem(self):
        got = converter.HTMLConverter(
            os.path.join(here, "p-to-p-listitem.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "p-to-p-listitem.xml"))

        self.assertXmlEqual(got, want)

    def test_note_within_p(self):
        got = converter.HTMLConverter(
            os.path.join(here, "note-within-p.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "note-within-p.xml"))

        self.assertXmlEqual(got, want)

    def test_i_within_note(self):
        got = converter.HTMLConverter(
            os.path.join(here, "i-within-note.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "i-within-note.xml"))

        self.assertXmlEqual(got, want)

    def test_pb(self):
        got = converter.HTMLConverter(
            os.path.join(here, "pb.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "pb.xml"))

        self.assertXmlEqual(got, want)

    def test_nobr(self):
        got = converter.HTMLConverter(
            os.path.join(here, "nobr.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "nobr.xml"))

        self.assertXmlEqual(got, want)

    def test_nrk_wbr(self):
        got = converter.HTMLConverter(
            os.path.join(here, "nrk-wbr.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "nrk-wbr.xml"))

        self.assertXmlEqual(got, want)

    def test_sup(self):
        got = converter.HTMLConverter(
            os.path.join(here, "sup.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "sup.xml"))

        self.assertXmlEqual(got, want)

    def test_td_a_div(self):
        got = converter.HTMLConverter(
            os.path.join(here, "td-a-div.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "td-a-div.xml"))

        self.assertXmlEqual(got, want)

    def test_ol_i_li(self):
        got = converter.HTMLConverter(
            os.path.join(here, "ol-i-li.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "ol-i-li.xml"))

        self.assertXmlEqual(got, want)

    def test_td_a_p(self):
        got = converter.HTMLConverter(
            os.path.join(here, "td-a-p.html")).convert2intermediate()
        want = lxml.etree.parse(os.path.join(here, "td-a-p.xml"))

        self.assertXmlEqual(got, want)
