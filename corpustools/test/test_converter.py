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
#   Copyright © 2014-2016 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

import codecs
import collections
import doctest
import io
import lxml.doctestcompare as doctestcompare
import lxml.etree as etree
from lxml.html import html5parser
import os
import unittest

from corpustools import converter
from corpustools import text_cat
from corpustools import xslsetter


here = os.path.dirname(__file__)
LANGUAGEGUESSER = text_cat.Classifier(None)


class TestConverter(unittest.TestCase):
    def setUp(self):
        self.converter_inside_orig = converter.Converter(
            os.path.join(here,
                         'converter_data/fakecorpus/orig/nob/samediggi-'
                         'article-16.html'),
            True)

        self.converter_outside_orig = converter.Converter(
            os.path.join(here,
                         'converter_data/samediggi-article-48.html'), False)

        self.converter_inside_freecorpus = converter.Converter(
            os.path.join(
                os.getenv('GTFREE'),
                'orig/sme/admin/sd/samediggi.no/samediggi-article-48.html'),
            False)

    def test_get_orig(self):
        self.assertEqual(
            self.converter_inside_orig.orig,
            os.path.join(
                here,
                'converter_data/fakecorpus/orig/nob/samediggi-article-'
                '16.html'))

        self.assertEqual(
            self.converter_outside_orig.orig,
            os.path.join(
                here,
                'converter_data/samediggi-article-48.html'))

        self.assertEqual(
            self.converter_inside_freecorpus.orig,
            os.path.join(
                os.getenv('GTFREE'),
                'orig/sme/admin/sd/samediggi.no/samediggi-article-48.html'))

    def test_get_xsl(self):
        self.assertEqual(
            self.converter_inside_orig.xsl,
            os.path.join(
                here,
                'converter_data/fakecorpus/orig/nob/samediggi-'
                'article-16.html.xsl'))

        self.assertEqual(
            self.converter_outside_orig.xsl,
            os.path.join(
                here,
                'converter_data/samediggi-article-48.html.xsl'))

        self.assertEqual(
            self.converter_inside_freecorpus.xsl,
            os.path.join(
                os.getenv('GTFREE'),
                'orig/sme/admin/sd/samediggi.no/samediggi-article-'
                '48.html.xsl'))

    def test_get_tmpdir(self):
        self.assertEqual(
            self.converter_inside_orig.tmpdir,
            os.path.join(
                here,
                'converter_data/fakecorpus/tmp'))

        self.assertEqual(
            self.converter_outside_orig.tmpdir,
            os.path.join(
                here, 'converter_data'))

        self.assertEqual(
            self.converter_inside_freecorpus.tmpdir,
            os.path.join(os.getenv('GTFREE'), 'tmp'))

    def test_get_corpusdir(self):
        self.assertEqual(
            self.converter_inside_orig.corpusdir.rstrip(os.path.sep),
            os.path.join(
                here,
                'converter_data/fakecorpus'))

        self.assertEqual(
            self.converter_outside_orig.corpusdir.rstrip(os.path.sep),
            os.path.join(here, 'converter_data'))

        self.assertEqual(
            self.converter_inside_freecorpus.corpusdir.rstrip(
                os.path.sep),
            os.getenv('GTFREE').rstrip(os.path.sep))

    def test_get_converted_name_inside_orig(self):
        self.assertEqual(
            self.converter_inside_orig.converted_name,
            os.path.join(
                here,
                'converter_data/fakecorpus/converted/nob/samediggi-'
                'article-16.html.xml'))

    def test_get_converted_name_outside_orig(self):
        self.assertEqual(
            self.converter_outside_orig.converted_name,
            os.path.join(
                here,
                'converter_data/samediggi-article-48.html.xml'))

    def test_get_converted_inside_freecorpus(self):
        self.assertEqual(
            self.converter_inside_freecorpus.converted_name,
            os.path.join(
                os.getenv('GTFREE'),
                'converted/sme/admin/sd/samediggi.no/samediggi-'
                'article-48.html.xml'))

    def test_validate_complete(self):
        '''Check that an exception is raised if a document is invalid'''
        complete = etree.fromstring('<document/>')

        self.assertRaises(converter.ConversionException,
                          self.converter_inside_orig.validate_complete,
                          complete)


class XMLTester(unittest.TestCase):

    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal"""
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(
                doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)


class TestAvvirConverter(XMLTester):

    def setUp(self):
        self.avvir = converter.AvvirConverter('fakename')
        self.avvir.intermediate = etree.fromstring(
            '<article>'
            '    <story id="a" class="Tittel">'
            '        <p>a</p>'
            '    </story>'
            '    <story id="b" class="Undertittel">'
            '        <p>b</p>'
            '    </story>'
            '    <story id="c" class="ingress">'
            '        <p>c</p>'
            '    </story>'
            '    <story id="d" class="body">'
            '        <p class="tekst">d<br/>e<br/></p>'
            '        <p>f</p>'
            '    </story>'
            '    <story id="g" class="body">'
            '        <p class="tekst">h<span>i</span>j</p>'
            '    </story>'
            '    <story id="k" class="body">'
            '        <p>l'
            '            <span>'
            '                m'
            '                <br/>'
            '                n'
            '            </span>'
            '            o'
            '        </p>'
            '    </story>'
            '</article>')

    def test_convert_p_1(self):
        '''p does not contain p'''
        want = etree.fromstring(
            '<article>'
            '    <story class="Tittel" id="a">'
            '        <p>a</p>'
            '    </story>'
            '    <story class="Undertittel" id="b">'
            '        <p>b</p>'
            '    </story>'
            '    <story class="ingress" id="c">'
            '        <p>c</p>'
            '    </story>'
            '    <story class="body" id="d">'
            '        <p>d</p>'
            '        <p>e</p>'
            '        <p>f</p>'
            '    </story>'
            '    <story class="body" id="g">'
            '        <p>h</p>'
            '        <p>i</p>'
            '        <p>j</p>'
            '    </story>'
            '    <story class="body" id="k">'
            '        <p>l</p>'
            '        <p>m</p>'
            '        <p>n</p>'
            '        <p>o</p>'
            '    </story>'
            '</article>')

        self.avvir.convert_p()
        self.assertXmlEqual(
            etree.tostring(self.avvir.intermediate), etree.tostring(want))

    def test_convert_p_2(self):
        '''p contains only p'''
        avvir = converter.AvvirConverter('fakename')
        avvir.intermediate = etree.fromstring(
            '<article>'
            '   <story class="body">'
            '       <p>corrected text <p>text with typo</p>with tail</p>'
            '   </story>'
            '</article>')

        want = etree.fromstring(
            '<article>'
            '   <story class="body">'
            '       <p>corrected text with tail</p>'
            '   </story>'
            '</article>')

        avvir.convert_p()
        self.assertXmlEqual(etree.tostring(avvir.intermediate),
                            etree.tostring(want))

    def test_convert_p_3(self):
        '''p contains span and p'''
        avvir = converter.AvvirConverter('fakename')
        avvir.intermediate = etree.fromstring(
            '<article>'
            '   <story class="body">'
            '       <p>'
            '           <span>bla bla</span>'
            '           corrected text <p>text with typo</p>with tail'
            '       </p>'
            '   </story>'
            '</article>')

        want = etree.fromstring(
            '<article>'
            '   <story class="body">'
            '       <p>bla bla</p>'
            '       <p>corrected text with tail</p>'
            '   </story>'
            '</article>')

        avvir.convert_p()
        self.assertXmlEqual(etree.tostring(avvir.intermediate),
                            etree.tostring(want))

    def test_convert_p_4(self):
        '''p.text is None'''
        avvir = converter.AvvirConverter('fakename')
        avvir.intermediate = etree.fromstring(
            '<article>'
            '   <story class="body">'
            '       <p><p> </p>with tail'
            '       </p>'
            '   </story>'
            '</article>')

        want = etree.fromstring(
            '<article>'
            '   <story class="body">'
            '       <p> with tail</p>'
            '   </story>'
            '</article>')

        avvir.convert_p()
        self.assertXmlEqual(etree.tostring(avvir.intermediate),
                            etree.tostring(want))

    def test_convert_p_5(self):
        '''sub_p.tail is None'''
        avvir = converter.AvvirConverter('fakename')
        avvir.intermediate = etree.fromstring(
            '<article>'
            '   <story class="body">'
            '       <p>láigovistti <p class="NormalParagraphStyle">85</p>'
            '       </p>'
            '   </story>'
            '</article>')

        want = etree.fromstring(
            '<article>'
            '   <story class="body">'
            '       <p>láigovistti </p>'
            '   </story>'
            '</article>')

        avvir.convert_p()
        self.assertXmlEqual(etree.tostring(avvir.intermediate),
                            etree.tostring(want))

    def test_convert_p_6(self):
        '''previous.text not None, sub_p.tail is None'''
        avvir = converter.AvvirConverter('fakename')
        avvir.intermediate = etree.fromstring(
            '<article>'
            '   <story class="body">'
            '       <p class="Privat ann tittel">Stohpu<br/>vuovdemassi'
            '<p class="NormalParagraphStyle">85</p><br/></p>'
            '   </story>'
            '</article>')

        want = etree.fromstring(
            '<article>'
            '   <story class="body">'
            '       <p>Stohpu</p>'
            '       <p>vuovdemassi</p>'
            '   </story>'
            '</article>')

        avvir.convert_p()
        self.assertXmlEqual(etree.tostring(avvir.intermediate),
                            etree.tostring(want))

    def test_convert_p_7(self):
        '''previous.tail is None, sub_p.tail not None'''
        avvir = converter.AvvirConverter('fakename')
        avvir.intermediate = etree.fromstring(
            '<article>'
            '   <story class="body">'
            '       <p class="Privat ann tittel">'
            '<br/><p class="NormalParagraphStyle">157</p>Ozan visttáža <br/>'
            '       </p>'
            '   </story>'
            '</article>')

        want = etree.fromstring(
            '<article>'
            '   <story class="body">'
            '       <p>Ozan visttáža</p>'
            '   </story>'
            '</article>')

        avvir.convert_p()
        self.assertXmlEqual(etree.tostring(avvir.intermediate),
                            etree.tostring(want))

    def test_convert_story(self):
        want = etree.fromstring(
            '<article>'
            '    <section>'
            '        <p type="title">a</p>'
            '    </section>'
            '    <section>'
            '        <p type="title">b</p>'
            '    </section>'
            '    <p>c</p>'
            '    <p>d</p>'
            '    <p>e</p>'
            '    <p>f</p>'
            '    <p>h</p>'
            '    <p>i</p>'
            '    <p>j</p>'
            '    <p>l</p>'
            '    <p>m</p>'
            '    <p>n</p>'
            '    <p>o</p>'
            '</article>')

        self.avvir.convert_p()
        self.avvir.convert_story()
        self.assertXmlEqual(
            etree.tostring(self.avvir.intermediate), etree.tostring(want))

    def test_convert_article(self):
        want = etree.fromstring(
            '<document>'
            '    <body>'
            '        <section>'
            '            <p type="title">a</p>'
            '        </section>'
            '        <section>'
            '            <p type="title">b</p>'
            '        </section>'
            '        <p>c</p>'
            '        <p>d</p>'
            '        <p>e</p>'
            '        <p>f</p>'
            '        <p>h</p>'
            '        <p>i</p>'
            '        <p>j</p>'
            '        <p>l</p>'
            '        <p>m</p>'
            '        <p>n</p>'
            '        <p>o</p>'
            '    </body>'
            '</document>')

        self.avvir.convert_p()
        self.avvir.convert_story()
        self.avvir.convert_article()
        self.assertXmlEqual(
            etree.tostring(self.avvir.intermediate), etree.tostring(want))


class TestSVGConverter(XMLTester):

    def setUp(self):
        self.svg = converter.SVGConverter(
            os.path.join(here,
                         'converter_data/Riddu_Riddu_avis_TXT.200923.svg'))

    def test_convert2intermediate(self):
        got = self.svg.convert2intermediate()
        want = etree.parse(
            os.path.join(here,
                         'converter_data/Riddu_Riddu_avis_TXT.200923.svg.xml'))

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))


class TestPlaintextConverter(XMLTester):

    def test_to_unicode(self):
        plaintext = converter.PlaintextConverter(
            os.path.join(here,
                         'converter_data/winsami2-test-ws2.txt'))
        got = plaintext.to_unicode()

        # Ensure that the data in want is unicode
        file_ = codecs.open(
            os.path.join(here,
                         'converter_data/winsami2-test-utf8.txt'),
            encoding='utf8')
        want = file_.read()
        file_.close()

        self.assertEqual(got, want)

    def test_strip_chars1(self):
        plaintext = converter.PlaintextConverter(
            'tullball.txt')
        got = plaintext.strip_chars(
            u'\x0d\n'
            u'<ASCII-MAC>\n'
            u'<vsn:3.000000>\n'
            u'<\!q>\n'
            u'<\!h>\n')
        want = u'''\n\n\n\n\n\n'''

        self.assertEqual(got, want)

    def test_strip_chars2(self):
        plaintext = converter.PlaintextConverter(
            'tullball.txt')
        got = plaintext.strip_chars(
            u'<0x010C><0x010D><0x0110><0x0111><0x014A><0x014B><0x0160><0x0161>'
            u'<0x0166><0x0167><0x017D><0x017E><0x2003>')
        want = u'''ČčĐđŊŋŠšŦŧŽž '''

        self.assertEqual(got, want)

    def test_plaintext(self):
        plaintext = converter.PlaintextConverter(
            'tullball.txt')
        got = plaintext.content2xml(io.StringIO(u'''Sámegiella.

Buot leat.'''))

        want = etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>
            Sámegiella.
        </p>
        <p>
           Buot leat.
       </p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_two_lines(self):
        newstext = converter.PlaintextConverter('tullball.txt')
        got = newstext.content2xml(io.StringIO(u'''Guovssahasa nieida.
Filbma lea.
'''))
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>Guovssahasa nieida.
Filbma lea.</p>
    </body>
</document>
''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_hyph(self):
        newstext = converter.PlaintextConverter('tullball.txt')
        got = newstext.content2xml(io.StringIO(u'''Guovssa<hyph/>hasa
'''))
        want = etree.fromstring(u'''
            <document>
            <header/>
            <body>
                <p>Guovssa<hyph/>hasa</p>
            </body>
            </document> ''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))


class TestDocConverter(XMLTester):

    def setUp(self):
        self.testdoc = converter.DocConverter(
            os.path.join(here,
                         'converter_data/doc-test.doc'), 'bogus')

    def test_convert2intermediate(self):
        got = self.testdoc.convert2intermediate()
        want = etree.parse(
            os.path.join(here,
                         'converter_data/doc-test.xml'))

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))


class TestDocxConverter(XMLTester):

    def setUp(self):
        self.testdoc = converter.DocxConverter(
            os.path.join(here,
                         'converter_data/doc-test.docx'), 'bogus')

    def test_convert2intermediate(self):
        got = self.testdoc.convert2intermediate()
        want = (
            '<document>'
            '    <header>'
            '        <title/>'
            '    </header>'
            '    <body>'
            '        <p>–Mun lean njeallje jagi boaris.</p>'
            '        <p>Nu beaivvádat.</p>'
            '        <p>oahppat guovttejuvlla nalde sykkelastit.</p>'
            '        <p>njeallje suorpma boaris.</p>'
            '        <p>Olggobealde Áššu</p>'
            '        <p>Lea go dus meahccebiila ?</p>'
            '        <p>–Mii lea suohttaseamos geassebargu dus ?</p>'
            '        <p>Suohkana bearašásodagaid juohkin</p>'
            '        <p>Sámi kulturfestivála 1998</p>'
            '    </body>'
            '</document>')

        self.assertXmlEqual(etree.tostring(got), want)


class TestHTMLContentConverter(XMLTester):

    def test_remove_empty_p_1(self):
        '''Remove an empty p'''
        got = converter.HTMLContentConverter(
            'with-o:p.html',
            content='<html><body><p/></html>').soup

        want = html5parser.document_fromstring(
            '<html><head/><body></body></html>')

        self.assertEqual(etree.tostring(got), etree.tostring(want))

    def test_remove_empty_p_2(self):
        '''Do not remove a p with content'''
        got = converter.HTMLContentConverter(
            'with-o:p.html',
            content='<html><body><p><span>spanny</span></p></html>').soup

        want = html5parser.document_fromstring(
            '<html><head/><body><p><span>spanny</span></p></body></html>')

        self.assertEqual(etree.tostring(got), etree.tostring(want))

    def test_remove_empty_class(self):
        got = converter.HTMLContentConverter(
            'with-o:p.html',
            content='<html><body><div class="">a</div><div class="a">'
            '<span class="">b</span></div></html>').soup

        want = html5parser.document_fromstring(
            '<html><head/><body><div>a</div><div class="a">'
            '<span>b</span></div></body></html>')

        self.assertEqual(etree.tostring(got), etree.tostring(want))

    def test_remove_unwanted_classes_and_ids(self):
        unwanted_classes_ids = {
            'div': {
                'class': [
                    'QuickNav', 'tabbedmenu', 'printContact', 'documentPaging',
                    'breadcrumbs',
                    'breadcrumbs ',
                    'post-footer', 'documentInfoEm',
                    'article-column', 'nrk-globalfooter', 'article-related',
                    'outer-column', 'article-ad', 'article-bottom-element',
                    'banner-element', 'nrk-globalnavigation', 'sharing', 'ad',
                    'meta', 'authors', 'articleImageRig',  'btm_menu',
                    'expandable', 'moduletable_etulinkki'],
                'id': [
                    'searchBox',
                    'murupolku',
                    'ctl00_FullRegion_CenterAndRightRegion_Sorting_sortByDiv',
                    'ctl00_FullRegion_CenterAndRightRegion_HitsControl_'
                    'searchHitSummary',
                    'AreaTopSiteNav', 'SamiDisclaimer', 'AreaTopRight',
                    'AreaLeft', 'AreaRight', 'ShareArticle', 'tipafriend',
                    'AreaLeftNav', 'PageFooter', 'blog-pager',
                    'NAVheaderContainer', 'NAVbreadcrumbContainer',
                    'NAVsubmenuContainer', 'NAVrelevantContentContainer',
                    'NAVfooterContainer', 'sidebar-wrapper', 'footer-wrapper',
                    'share-article', 'topUserMenu', 'rightAds', 'menu', 'aa',
                    'sidebar', 'footer', 'chatBox', 'sendReminder',
                    'ctl00_MidtSone_ucArtikkel_ctl00_divNavigasjon',
                    (
                        'ctl00_MidtSone_ucArtikkel_ctl00_'
                        'ctl00_ctl01_divRessurser')],
            },
            'p': {
                'class': ['WebPartReadMoreParagraph', 'breadcrumbs'],
            },
            'ul': {
                'id': ['AreaTopPrintMeny', 'AreaTopLanguageNav'],
                'class': ['QuickNav', 'article-tools', 'byline']
            },
            'span': {
                'id': ['skiplinks'],
                'class': ['K-NOTE-FOTNOTE']
            },
            'a': {
                'class': ['mainlevel_alavalikko',
                          'sublevel_alavalikko'],
            },
            'td': {
                'id': ['sg_vasen'],
            },
        }

        for tag, attribs in unwanted_classes_ids.items():
            for key, values in attribs.items():
                for value in values:
                    hc = converter.HTMLContentConverter(
                        '.html'.format(tag, key, value),
                        content='<html><body><{0} {1}="{2}">'
                        'content:{0}{1}{2}</{0}>'
                        '<div class="ada"/></body>'
                        '</html>'.format(tag, key, value))

                    want = html5parser.document_fromstring(
                        '<html><body><div class="ada"/></body></html>')

                    self.assertEqual(
                        etree.tostring(hc.soup), etree.tostring(want))

    def test_remove_unwanted_tags(self):
        unwanted_tags = [
            'script', 'style', 'area', 'object', 'meta',
            'hr', 'nf', 'mb', 'ms',
            'img', 'cite', 'embed', 'footer', 'figcaption', 'aside', 'time',
            'figure', 'nav', 'select', 'noscript', 'iframe', 'map',
            'colgroup', 'st1:country-region', 'v:shapetype', 'v:shape',
            'st1:metricconverter', 'fb:comments', 'g:plusone', 'fb:like',
        ]

        for unwanted_tag in unwanted_tags:
            got = converter.HTMLContentConverter(
                unwanted_tag + '.html',
                content='<html><body><p>p1</p><%s/><p>p2</p2></body>'
                '</html>' % unwanted_tag).soup
            want = (
                '<html:html xmlns:html="http://www.w3.org/1999/xhtml">'
                '<html:head/><html:body><html:p>p1</html:p><html:p>p2'
                '</html:p></html:body></html:html>')

            self.assertEqual(etree.tostring(got), want)

    def test_remove_comment(self):
        got = converter.HTMLContentConverter(
            'with-o:p.html',
            content='<html><body><b><!--Hey, buddy. --></b></body>'
            '</html>').soup

        want = (
            '<html:html xmlns:html="http://www.w3.org/1999/xhtml"><html:head/>'
            '<html:body><html:b/></html:body></html:html>')

        self.assertEqual(etree.tostring(got), want)

    def test_remove_processinginstruction(self):
        got = converter.HTMLContentConverter(
            'with-o:p.html',
            content='<html><body><b><?ProcessingInstruction?></b></body>'
            '</html>').soup

        want = (
            '<html:html xmlns:html="http://www.w3.org/1999/xhtml">'
            '<html:head/><html:body><html:b/></html:body></html:html>')

        self.assertEqual(etree.tostring(got), want)

    def test_add_p_around_text1(self):
        '''Only text before next significant element'''
        hcc = converter.HTMLContentConverter(
            'withoutp.html',
            content='<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN">'
            '<html><head><meta http-equiv="Content-type" content="text/html; '
            'charset=utf-8"><title>– Den utdøende stammes frykt</title>'
            '</head><body><h3>VI</h3>... Finnerne<p>Der</body></html>')

        want = (
            '<?xml version="1.0"?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML '
            '1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1'
            '-strict.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><head>'
            '<title>– Den utdøende stammes frykt</title></head><body>'
            '<h3>VI</h3>  <p>... Finnerne</p><p>Der</p></body></html>')

        self.assertXmlEqual(etree.tostring(hcc.soup), want)

    def test_add_p_around_text2(self):
        '''Text and i element before next significant element'''
        hcc = converter.HTMLContentConverter(
            'withoutp.html',
            content='<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN">'
            '<html><head><meta http-equiv="Content-type" content="text/html; '
            'charset=utf-8"><title>– Den utdøende stammes frykt</title>'
            '</head><body><h3>VI</h3>... Finnerne<i>Der</body></html>')

        want = (
            '<?xml version="1.0"?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML '
            '1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-'
            'strict.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><head>'
            '<title>– Den utdøende stammes frykt</title></head><body>'
            '<h3>VI</h3>  <p>... Finnerne<i>Der</i></p></body></html>')

        self.assertXmlEqual(etree.tostring(hcc.soup), want)

    def test_add_p_around_text3(self):
        '''h2 as a stop element'''
        hcc = converter.HTMLContentConverter(
            'withoutp.html',
            content='<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN">'
            '<html>'
            '<head><meta http-equiv="Content-type" content="text/html; '
            'charset=utf-8"><title>– Den utdøende stammes frykt</title>'
            '</head><body><h3>VI</h3>... Finnerne<a/>'
            '<h2>Der</h2></body></html>')

        want = (
            '<?xml version="1.0"?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML '
            '1.0 Strict//EN" '
            '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
            '<html xmlns="http://www.w3.org/1999/xhtml"><head><title>– Den '
            'utdøende stammes frykt</title>  </head><body>  <h3>VI</h3>  '
            '<p>... Finnerne<a/></p><h2>Der</h2></body></html>')

        self.assertXmlEqual(etree.tostring(hcc.soup), want)

    def test_set_charset_1(self):
        '''encoding_from_xsl = None, no charset in html header'''
        content = (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN"><html>'
            '<body></body></html>')
        hcc = converter.HTMLContentConverter(
            'ugga.html',
            content=content)

        got = hcc.get_encoding(content)

        self.assertEqual(got, ('utf-8', 'guess'))

    def test_set_charset_2(self):
        '''encoding_from_xsl = '', no charset in html header'''
        content = (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN"><html>'
            '<body></body></html>')
        hcc = converter.HTMLContentConverter(
            'ugga.html',
            content=content)

        got = hcc.get_encoding(content)

        self.assertEqual(got, ('utf-8', 'guess'))

    def test_get_encoding_3(self):
        '''encoding_from_xsl = 'iso-8859-1', no charset in html header'''
        content = (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN"><html>'
            '<body></body></html>')

        hcc = converter.HTMLContentConverter(
            'ugga.html',
            content=content)
        hcc.md.set_variable('text_encoding', 'iso-8859-1')

        got = hcc.get_encoding(content)

        self.assertEqual(got, ('windows-1252', 'xsl'))

    def test_get_encoding_4(self):
        '''Check that encoding_from_xsl overrides meta charset

        encoding_from_xsl = 'iso-8859-1', charset in html header = utf-8
        '''
        content = (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN"><html>'
            '<head><meta http-equiv="Content-type" content="text/html; '
            'charset=utf-8"></head><body></body></html>')

        hcc = converter.HTMLContentConverter(
            'ugga.html',
            content=content)
        hcc.md.set_variable('text_encoding', 'iso-8859-1')

        got = hcc.get_encoding(content)

        self.assertEqual(got, ('windows-1252', 'xsl'))

    def test_get_encoding_5(self):
        '''encoding_from_xsl = None, charset in html header = iso-8859-1'''
        content = (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN"><html>'
            '<head><meta http-equiv="Content-type" content="text/html; '
            'charset=iso-8859-1"></head><body></body></html>')

        hcc = converter.HTMLContentConverter(
            'ugga.html',
            content=content)

        got = hcc.get_encoding(content)

        self.assertEqual(got, ('windows-1252', 'content'))

    def test_get_encoding_6(self):
        '''encoding_from_xsl = '', charset in html header = iso-8859-1'''
        content = (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN"><html>'
            '<head><meta http-equiv="Content-type" content="text/html; '
            'charset=iso-8859-1"></head><body></body></html>')

        hcc = converter.HTMLContentConverter(
            'ugga.html',
            content=content)

        got = hcc.get_encoding(content)

        self.assertEqual(got, ('windows-1252', 'content'))

    def test_set_charset_7(self):
        '''' as quote mark around charset

        encoding_from_xsl = '', charset in html header = iso-8859-1
        '''
        content = (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN"><html>'
            '<head><meta http-equiv="Content-type" content=\'text/html; '
            'charset=iso-8859-1\'></head><body></body></html>')

        hcc = converter.HTMLContentConverter(
            'ugga.html',
            content=content)

        got = hcc.get_encoding(content)

        self.assertEqual(got, ('windows-1252', 'content'))

    def test_set_charset_8(self):
        '''' is quote mark around charset when

        " is found later
        encoding_from_xsl = '', charset in html header = iso-8859-1
        '''
        content = (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN"><html>'
            '<head><meta http-equiv="Content-type" content=\'text/html; '
            'charset=iso-8859-1\'><link rel="index.html"></head><body>'
            '</body></html>')

        hcc = converter.HTMLContentConverter(
            'ugga.html',
            content=content)

        got = hcc.get_encoding(content)

        self.assertEqual(got, ('windows-1252', 'content'))

    def test_set_charset_9(self):
        '''" is quote mark around charset

        ' is found later
        encoding_from_xsl = '', charset in html header = iso-8859-1
        '''
        content = (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN"><html>'
            '<head><meta http-equiv="Content-type" content="text/html; '
            'charset=iso-8859-1"><link rel=\'index.html\'></head><body>'
            '</body></html>')

        hcc = converter.HTMLContentConverter(
            'ugga.html',
            content=content)

        got = hcc.get_encoding(content)

        self.assertEqual(got, ('windows-1252', 'content'))

    def test_set_charset_10(self):
        '''Test uppercase iso-8859-15'''
        content = (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" '
            '"http://www.w3.org/TR/REC-html40/loose.dtd">'
            '<html>'
            '<head>'
            '<META HTTP-EQUIV="Content-Type" CONTENT="text/html;'
            'charset=iso-8859-15">')

        hcc = converter.HTMLContentConverter(
            'ugga.html',
            content=content)

        got = hcc.get_encoding(content)

        self.assertEqual(got, ('iso-8859-15', 'content'))

    def test_center2div(self):
        got = converter.HTMLContentConverter(
            'center.html',
            content='<html><body><center><span class="">b</span>'
            '</center></html>').soup

        want = html5parser.document_fromstring(
            '<html><head/><body><div class="c1"><span>b</span></div></body>'
            '</html>')

        self.assertEqual(etree.tostring(got), etree.tostring(want))

    def test_body_i(self):
        got = converter.HTMLContentConverter(
            'i.html', LANGUAGEGUESSER,
            content='<html><body><i>b</i></body></html>').soup

        want = html5parser.document_fromstring(
            '<html><head/><body><p><i>b</i></p></body></html>')

        self.assertEqual(etree.tostring(got), etree.tostring(want))

    def test_body_a(self):
        got = converter.HTMLContentConverter(
            'a.html', LANGUAGEGUESSER,
            content='<html><body><a>b</a></body></html>').soup

        want = html5parser.document_fromstring(
            '<html><head/><body><p><a>b</a></p></body></html>')

        self.assertEqual(etree.tostring(got), etree.tostring(want))

    def test_body_em(self):
        got = converter.HTMLContentConverter(
            'em.html', LANGUAGEGUESSER,
            content='<html><body><em>b</em></body></html>').soup

        want = html5parser.document_fromstring(
            '<html><head/><body><p><em>b</em></p></body></html>')

        self.assertEqual(etree.tostring(got), etree.tostring(want))

    def test_body_font(self):
        got = converter.HTMLContentConverter(
            'font.html', LANGUAGEGUESSER,
            content='<html><body><font>b</font></body></html>').soup

        want = html5parser.document_fromstring(
            '<html><head/><body><p><font>b</font></p></body></html>')

        self.assertEqual(etree.tostring(got), etree.tostring(want))

    def test_body_u(self):
        got = converter.HTMLContentConverter(
            'u.html', LANGUAGEGUESSER,
            content='<html><body><u>b</u></body></html>').soup

        want = html5parser.document_fromstring(
            '<html><head/><body><p><u>b</u></p></body></html>')

        self.assertEqual(etree.tostring(got), etree.tostring(want))

    def test_body_strong(self):
        got = converter.HTMLContentConverter(
            'strong.html', LANGUAGEGUESSER,
            content='<html><body><strong>b</strong></body></html>').soup

        want = html5parser.document_fromstring(
            '<html><head/><body><p><strong>b</strong></p></body></html>')

        self.assertEqual(etree.tostring(got), etree.tostring(want))

    def test_body_span(self):
        got = converter.HTMLContentConverter(
            'span.html', LANGUAGEGUESSER,
            content='<html><body><span>b</span></body></html>').soup

        want = html5parser.document_fromstring(
            '<html><head/><body><p><span>b</span></p></body></html>')

        self.assertEqual(etree.tostring(got), etree.tostring(want))

    def test_body_text(self):
        got = converter.HTMLContentConverter(
            'text.html', LANGUAGEGUESSER,
            content='<html><body>b</body></html>').soup

        want = html5parser.document_fromstring(
            '<html><head/><body><p>b</p></body></html>')

        self.assertEqual(etree.tostring(got), etree.tostring(want))


class TestRTFConverter(XMLTester):

    def setUp(self):
        self.testrtf = converter.RTFConverter(
            os.path.join(here, 'converter_data/folkemote.rtf'))

    def test_convert2intermediate(self):
        got = self.testrtf.convert2intermediate()
        want = etree.parse(
            os.path.join(here, 'converter_data/folkemote.xml'))

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))


class TestDocumentFixer(XMLTester):

    def test_insert_spaces_after_semicolon(self):
        a = {u'Govven:Á': u'Govven: Á',
             u'govven:á': u'govven: á',
             u'GOVVEN:Á': u'GOVVEN: Á',
             u'Govva:Á': u'Govva: Á',
             u'govva:á': u'govva: á',
             u'GOVVA:Á': u'GOVVA: Á',
             u'GOVVEJEADDJI:Á': u'GOVVEJEADDJI: Á',
             u'Govva:': u'Govva:',
             u'<em>Govven:Á</em>': u'<em>Govven: Á</em>',
             }
        for key, value in a.items():
            document_fixer = converter.DocumentFixer(etree.fromstring(u'''<document>
        <header/>
        <body>
            <p>''' + key + u'''</p>
        </body>
    </document>'''))
            document_fixer.insert_spaces_after_semicolon()
            got = document_fixer.get_etree()
            want = etree.fromstring(u'''<document>
        <header/>
        <body>
            <p>''' + value + u'''</p>
        </body>
    </document>''')

            self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_fix_newstags_bold_1(self):
        '''Test conversion of the @bold: newstag'''
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@bold:buoidi
seaggi</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p><em type="bold">buoidi</em></p>
        <p>seaggi</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_fix_newstags_bold_2(self):
        '''Test conversion of the @bold: newstag'''
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@bold:buoidi
@tekst:seaggi</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p><em type="bold">buoidi</em></p>
        <p>seaggi</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_fix_newstags_bold_3(self):
        '''Test conversion of the @bold: newstag'''
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@bold :DON</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p><em type="bold">DON</em></p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_byline1(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <author>
            <unknown/>
        </author>
    </header>
    <body>
        <p>@byline: Kárášjohka: Elle Merete Utsi</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(u'''<document>
    <header>
        <author>
            <person firstname="" lastname="Elle Merete Utsi"/>
        </author>
    </header>
    <body/>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_byline2(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <author>
            <unknown/>
        </author>
    </header>
    <body>
        <p>&lt;pstyle:byline&gt;NORGA: Åse Pulk</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(u'''<document>
    <header>
        <author>
            <person firstname="" lastname="Åse Pulk"/>
        </author>
    </header>
    <body/>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_byline3(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <author>
            <unknown/>
        </author>
    </header>
    <body>
        <p>@byline:KçRç´JOHKA:Elle Merete Utsi</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(u'''<document>
    <header>
        <author>
            <person firstname="" lastname="Elle Merete Utsi"/>
        </author>
    </header>
    <body/>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_byline4(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <author>
            <unknown/>
        </author>
    </header>
    <body>
        <p>@byline:Elle Merete Utsi</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(u'''<document>
    <header>
        <author>
            <person firstname="" lastname="Elle Merete Utsi"/>
        </author>
    </header>
    <body/>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_byline5(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <author>
            <unknown/>
        </author>
    </header>
    <body>
        <p> @byline:Elle Merete Utsi</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(u'''<document>
    <header>
        <author>
            <person firstname="" lastname="Elle Merete Utsi"/>
        </author>
    </header>
    <body/>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_byline6(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <author>
            <person firstname="" lastname="Juvven"/>
        </author>
    </header>
    <body>
        <p> @byline:Elle Merete Utsi</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(u'''<document>
    <header>
        <author>
            <person firstname="" lastname="Juvven"/>
        </author>
    </header>
    <body/>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_byline7(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <author>
            <unknown/>
        </author>
    </header>
    <body>
        <p> @BYLINE:Elle Merete Utsi</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(u'''<document>
    <header>
        <author>
            <person firstname="" lastname="Elle Merete Utsi"/>
        </author>
    </header>
    <body/>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_byline8(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <author>
            <unknown/>
        </author>
    </header>
    <body>
        <p><em>@BYLINE:Elle Merete Utsi </em> </p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(u'''<document>
    <header>
        <author>
            <person firstname="" lastname="Elle Merete Utsi"/>
        </author>
    </header>
    <body/>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_kursiv(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@kursiv:(Gáldu)</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(r'''<document>
    <header/>
    <body>
        <p><em type="italic">(Gáldu)</em></p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_ledtekst(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@LEDtekst:Dat mearkkaša</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>Dat mearkkaša</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_bildetekst(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>Bildetekst:Dat mearkkaša</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>Dat mearkkaša</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_logo(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@logo:Finnmark jordskifterett</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>Finnmark jordskifterett</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_fotobyline(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@fotobyline:Finnmark jordskifterett</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>Finnmark jordskifterett</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_foto(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@foto: govva1</p>
        <p><em>foto: govva2</em></p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>govva1</p>
        <p><em>govva2</em></p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_bildetitt(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@bildetitt:Finnmark jordskifterett</p>
        <p>Bildetitt:Finnmark jordskifterett</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>Finnmark jordskifterett</p>
        <p>Finnmark jordskifterett</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_bilde(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@bilde:NSR PRESIDEANTAEVTTOHAS? Berit Ranveig Nilssen
B 13  @bilde:DEANU-LEAGIS: Nils Porsanger.
B8  @bilde:SOHPPARIS: Bajit-Sohpparis Nils Andersen.
@bilde :E
BILDE 3:oahppat
&lt;pstyle:bilde&gt;Ii
Billedtekst: 3</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>NSR PRESIDEANTAEVTTOHAS? Berit Ranveig Nilssen</p>
        <p>DEANU-LEAGIS: Nils Porsanger.</p>
        <p>SOHPPARIS: Bajit-Sohpparis Nils Andersen.</p>
        <p>E</p>
        <p>oahppat</p>
        <p>Ii</p>
        <p>3</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_ingress_1(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@ingress:Ragnhild Nystad, Aili Keskitalo.
@ingres:Guovdageainnu lagasradio
 @ingress: Eallu
@ingress. duottar
'@ingress:Golbma
@ingress Odne
Samleingress 1
Samleingress: 2
@Samleingress: 3
&lt;pstyle:ingress&gt;Buot
TEKST/INGRESS: 5
@ Ingress: 6</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>Ragnhild Nystad, Aili Keskitalo.</p>
        <p>Guovdageainnu lagasradio</p>
        <p>Eallu</p>
        <p>duottar</p>
        <p>Golbma</p>
        <p>Odne</p>
        <p>1</p>
        <p>2</p>
        <p>3</p>
        <p>Buot</p>
        <p>5</p>
        <p>6</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_ingress_2(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p><em>@ingress: Gos?</em></p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p><em>Gos?</em></p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_mtitt1(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@m.titt:Juovllat
m.titt:Guolli
@mtitt:Juovllat
M:TITT:Lea go dus meahccebiila?
@m.titt. Maŋemus gártemat
&lt;pstyle:m.titt&gt;Divvot
 @m.titt:Eai</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p type="title">Juovllat</p>
        <p type="title">Guolli</p>
        <p type="title">Juovllat</p>
        <p type="title">Lea go dus meahccebiila?</p>
        <p type="title">Maŋemus gártemat</p>
        <p type="title">Divvot</p>
        <p type="title">Eai</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_mtitt2(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p><em>@m.titt: Maid?</em></p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p type="title"><em>Maid?</em></p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_tekst_1(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>@tekst:veadjá šaddat.
tekst:NSR ii áiggo.
TEKST:ÐMii lea suohttaseamos geassebargu dus?
&lt;pstyle:tekst&gt;Sámi</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>veadjá šaddat.</p>
        <p>NSR ii áiggo.</p>
        <p>ÐMii lea suohttaseamos geassebargu dus?</p>
        <p>Sámi</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_tekst_2(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>@tekst:veadjá šaddat.
NSR ii áiggo.</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>veadjá šaddat. NSR ii áiggo.</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_tekst_3(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>@tekst:veadjá šaddat.
@tekst:NSR ii áiggo.</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>veadjá šaddat.</p>
        <p>NSR ii áiggo.</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_tekst_4(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>NSR <em>ii áiggo.</em></p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>NSR <em>ii áiggo.</em></p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_tekst_5(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>  @tekst:ii</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>ii</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_tekst_6(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>Ê@tekst:ii</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>ii</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_stikktitt(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@stikktitt:Dološ sámegiel máinnas Várjjagis</p>
        <p>@stikk.titt:Dološ sámegiel máinnas Várjjagis</p>
        <p>@stikktittel:Dološ sámegiel máinnas Várjjagis</p>
        <p> @stikk:Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_utitt1(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@utitt:Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_utitt2(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p> @utitt:Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_udot_titt(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@u.titt:Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_undertitt(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@undertitt:Dološ sámegiel máinnas Várjjagis
undertitt:Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_undertittel(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>Undertittel: Ja</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p type="title">Ja</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_ttitt(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@ttitt:Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_headertitletags_1(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <title/>
    </header>
    <body>
        <p>@tittel:Eanebuidda</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_headertitletags_2(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <title/>
    </header>
    <body>
        <p> @tittel:Eanebuidda</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_headertitletags_3(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <title/>
    </header>
    <body>
        <p>@titt:Eanebuidda</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_headertitletags_4(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <title/>
    </header>
    <body>
        <p> @titt:Eanebuidda</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_headertitletags_5(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <title/>
    </header>
    <body>
        <p>TITT:Eanebuidda</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_headertitletags_6(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <title/>
    </header>
    <body>
        <p>Tittel:Eanebuidda</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_headertitletags_7(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <title/>
    </header>
    <body>
        <p>@LEDtitt:Eanebuidda</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_headertitletags_8(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <title/>
    </header>
    <body>
        <p>&lt;pstyle:tittel&gt;Eanebuidda</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_headertitletags_9(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <title/>
    </header>
    <body>
        <p>HOVEDTITTEL:Eanebuidda</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_headertitletags_10(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <title/>
    </header>
    <body>
        <p>TITTEL:Eanebuidda</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_headertitletags_11(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <title/>
    </header>
    <body>
        <p>@Titt:Guolli
titt:Ruovttusuodjaleaddjit
 @titt:Eanebuidda</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header>
        <title>Guolli</title>
    </header>
    <body>
        <p type="title">Guolli</p>
        <p type="title">Ruovttusuodjaleaddjit</p>
        <p type="title">Eanebuidda</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_headertitletags_12(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <title/>
    </header>
    <body>
        <p>Hovedtitt:Eanebuidda</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_headertitletags_13(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <title/>
    </header>
    <body>
        <p>@hovedtitt:Eanebuidda</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_headertitletags_14(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <title/>
    </header>
    <body>
        <p>@titt 2:Eanebuidda</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_headertitletags_15(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <title/>
    </header>
    <body>
        <p>OVERTITTEL:Eanebuidda</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_headertitletags_16(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <title/>
    </header>
    <body>
        <p>@tittel:Gii boahtá Nystø maŋis?
@LEDtitt:Gii boahtá Keskitalo maŋis?
@tittel:Gii boahtá Olli maŋis?
TITT:njeallje suorpma boaris.
&lt;pstyle:tittel&gt;Ii
 @tittel: 1
HOVEDTITTEL: 2
TITTEL: 3</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(u'''<document>
    <header>
        <title>Gii boahtá Nystø maŋis?</title>
    </header>
    <body>
        <p type="title">Gii boahtá Nystø maŋis?</p>
        <p type="title">Gii boahtá Keskitalo maŋis?</p>
        <p type="title">Gii boahtá Olli maŋis?</p>
        <p type="title">njeallje suorpma boaris.</p>
        <p type="title">Ii</p>
        <p type="title">1</p>
        <p type="title">2</p>
        <p type="title">3</p>
    </body>
</document>
''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_ttt(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@ttt:Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_newstags_tit(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@tit:Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_newstags_text_before_titletags(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@tekst: text
@m.titt: title</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>text</p>
        <p type="title">title</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_newstags_text_before_headtitletags(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <title/>
    </header>
    <body>
        <p>@tekst: text
@tittel: title</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header>
        <title>title</title>
    </header>
    <body>
        <p>text</p>
        <p type="title">title</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_newstags_text_before_bylinetags(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header>
        <author>
            <unknown/>
        </author>
    </header>
    <body>
        <p>@tekst: text
@byline: title</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header>
        <author>
            <person firstname="" lastname="title"></person>
        </author>
    </header>
    <body>
        <p>text</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_newstags_text_before_boldtags(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@tekst: text
@bold: title</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>text</p>
        <p><em type="bold">title</em></p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_newstags_text_before_kursiv(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>@tekst: text
@kursiv: title</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>text</p>
        <p><em type="italic">title</em></p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_fix_newstags_4(self):
        '''Check that p attributes are kept'''
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p type="title">title</p>
    </body>
</document>'''))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p type="title">title</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_fix__body_encoding(self):
        newstext = converter.PlaintextConverter(
            'tullball.txt', LANGUAGEGUESSER)
        text = newstext.content2xml(io.StringIO(u'''ÐMun lean njeallje jagi boaris.

Nu beaivvdat.

TITT:njeallje suorpma boaris.

TEKST:Olggobealde ç»»u

M:TITT:Lea go dus meahccebiila ?

TEKST:ÐMii lea suohttaseamos geassebargu dus ?

@bold:Suohkana beara»sodagaid juohkin

LOGO: Smi kulturfestivala 1998
'''))

        document_fixer = converter.DocumentFixer(text)
        document_fixer.fix_body_encoding()
        got = document_fixer.get_etree()

        want = etree.fromstring(u'''<document>
    <header></header>
        <body>
            <p>–Mun lean njeallje jagi boaris.</p>
            <p>Nu beaivvádat.</p>
            <p>TITT:njeallje suorpma boaris.</p>
            <p>TEKST:Olggobealde Áššu</p>
            <p>M:TITT:Lea go dus meahccebiila ?</p>
            <p>TEKST:–Mii lea suohttaseamos geassebargu dus ?</p>
            <p>@bold:Suohkana bearašásodagaid juohkin</p>
            <p>LOGO: Sámi kulturfestivala 1998</p>
        </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_replace_ligatures(self):
        svgtext = converter.SVGConverter(
            os.path.join(here,
                         'converter_data/Riddu_Riddu_avis_TXT.200923.svg'),
            LANGUAGEGUESSER)
        document_fixer = converter.DocumentFixer(
            etree.fromstring(etree.tostring(svgtext.convert2intermediate())))
        document_fixer.fix_body_encoding()
        got = document_fixer.get_etree()

        want = etree.parse(
            os.path.join(here,
                         'converter_data/Riddu_Riddu_avis_TXT.200923.xml'))

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_simple_detect_quote1(self):
        orig_paragraph = '<p>bla bla "bla bla" bla bla </p>'
        expected_paragraph = (
            '<p>bla bla <span type="quote">"bla bla"</span> bla bla</p>')

        document_fixer = converter.DocumentFixer(
            etree.parse(
                os.path.join(here,
                             'converter_data/samediggi-article-48s-before-'
                             'lang-detection-with-multilingual-tag.xml')))
        got_paragraph = document_fixer.detect_quote(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_simple_detect_quote2(self):
        orig_paragraph = '<p>bla bla “bla bla” bla bla</p>'
        expected_paragraph = (
            '<p>bla bla <span type="quote">“bla bla”</span> bla bla</p>')

        document_fixer = converter.DocumentFixer(
            etree.parse(
                os.path.join(here,
                             'converter_data/samediggi-article-48s-before-'
                             'lang-detection-with-multilingual-tag.xml')))
        got_paragraph = document_fixer.detect_quote(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_simple_detect_quote3(self):
        orig_paragraph = '<p>bla bla «bla bla» bla bla</p>'
        expected_paragraph = (
            '<p>bla bla <span type="quote">«bla bla»</span> bla bla</p>')

        document_fixer = converter.DocumentFixer(
            etree.parse(
                os.path.join(here,
                             'converter_data/samediggi-article-48s-before-'
                             'lang-detection-with-multilingual-tag.xml')))
        got_paragraph = document_fixer.detect_quote(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_simple_detect_quote4(self):
        orig_paragraph = (
            '<p type="title">Sámegiel čálamearkkat Windows XP várás.</p>')
        expected_paragraph = (
            '<p type="title">Sámegiel čálamearkkat Windows XP várás.</p>')

        document_fixer = converter.DocumentFixer(
            etree.parse(
                os.path.join(here,
                             'converter_data/samediggi-article-48s-before-'
                             'lang-detection-with-multilingual-tag.xml')))
        got_paragraph = document_fixer.detect_quote(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_simple_detect_quote2_quotes(self):
        orig_paragraph = '<p>bla bla «bla bla» bla bla «bla bla» bla bla</p>'
        expected_paragraph = (
            '<p>bla bla <span type="quote">«bla bla»</span> bla bla '
            '<span type="quote">«bla bla»</span> bla bla</p>')

        document_fixer = converter.DocumentFixer(
            etree.parse(
                os.path.join(here,
                             'converter_data/samediggi-article-48s-before-'
                             'lang-detection-with-multilingual-tag.xml')))
        got_paragraph = document_fixer.detect_quote(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_detect_quote_with_following_tag(self):
        orig_paragraph = '<p>bla bla «bla bla» <em>bla bla</em></p>'
        expected_paragraph = (
            '<p>bla bla <span type="quote">«bla bla»</span> <em>'
            'bla bla</em></p>')

        document_fixer = converter.DocumentFixer(
            etree.parse(
                os.path.join(here,
                             'converter_data/samediggi-article-48s-before-'
                             'lang-detection-with-multilingual-tag.xml')))
        got_paragraph = document_fixer.detect_quote(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_detect_quote_with_tag_infront(self):
        orig_paragraph = '<p>bla bla <em>bla bla</em> «bla bla»</p>'
        expected_paragraph = (
            '<p>bla bla <em>bla bla</em> <span type="quote">'
            '«bla bla»</span></p>')

        document_fixer = converter.DocumentFixer(
            etree.parse(
                os.path.join(here,
                             'converter_data/samediggi-article-48s-before-'
                             'lang-detection-with-multilingual-tag.xml')))
        got_paragraph = document_fixer.detect_quote(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_detect_quote_within_tag(self):
        orig_paragraph = '<p>bla bla <em>bla bla «bla bla»</em></p>'
        expected_paragraph = (
            '<p>bla bla <em>bla bla <span type="quote">'
            '«bla bla»</span></em></p>')

        document_fixer = converter.DocumentFixer(
            etree.parse(
                os.path.join(here,
                             'converter_data/samediggi-article-48s-before-'
                             'lang-detection-with-multilingual-tag.xml')))
        got_paragraph = document_fixer.detect_quote(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph),
                            expected_paragraph)

    def test_word_count(self):
        orig_doc = etree.parse(
            io.BytesIO(
                '<document xml:lang="sma" id="no_id"><header><title/><genre/>'
                '<author><unknown/></author><availability><free/>'
                '</availability><multilingual/></header><body><p>Bïevnesh '
                'naasjovnalen pryövoej bïjre</p><p>2008</p><p>Bïevnesh '
                'eejhtegidie, tjidtjieh aehtjieh bielide naasjovnalen '
                'pryövoej bïjre giej leah maanah 5. jïh 8. '
                'tsiehkine</p></body></document>'))

        expected_doc = (
            '<document xml:lang="sma" id="no_id"><header><title/><genre/>'
            '<author><unknown/></author><wordcount>20</wordcount>'
            '<availability><free/></availability><multilingual/></header>'
            '<body><p>Bïevnesh naasjovnalen pryövoej bïjre</p>'
            '<p>2008</p><p>Bïevnesh eejhtegidie, tjidtjieh aehtjieh bielide '
            'naasjovnalen pryövoej bïjre giej leah maanah 5. jïh 8. '
            'tsiehkine</p></body></document>')

        document_fixer = converter.DocumentFixer(orig_doc)
        document_fixer.set_word_count()

        self.assertXmlEqual(etree.tostring(document_fixer.root), expected_doc)

    def test_replace_shy1(self):
        orig_doc = etree.parse(
            io.BytesIO(
                '<document xml:lang="sma" id="no_id"><header><title/><genre/>'
                '<author><unknown/></author><availability><free/>'
                '</availability><multilingual/></header><body><p>a­b­c'
                '<span>d­e</span>f­g</p></body></document>'))

        expected_doc = (
            '<document xml:lang="sma" id="no_id"><header><title/><genre/>'
            '<author><unknown/></author><availability><free/></availability>'
            '<multilingual/></header><body><p>a<hyph/>b<hyph/>c<span>d<hyph/>'
            'e</span>f<hyph/>g</p></body></document>')

        document_fixer = converter.DocumentFixer(orig_doc)
        document_fixer.soft_hyphen_to_hyph_tag()

        self.assertXmlEqual(etree.tostring(document_fixer.root), expected_doc)

    def test_replace_shy2(self):
        orig_doc = etree.parse(
            io.BytesIO(
                '<document xml:lang="sma" id="no_id">'
                '<header><title/><genre/><author><unknown/></author>'
                '<availability><free/></availability><multilingual/></header>'
                '<body><p>a­b­c<span>d­e</span></p></body></document>'))

        expected_doc = (
            '<document xml:lang="sma" id="no_id"><header><title/><genre/>'
            '<author><unknown/></author><availability><free/></availability>'
            '<multilingual/></header><body><p>a<hyph/>b<hyph/>c<span>d'
            '<hyph/>e</span></p></body></document>')

        document_fixer = converter.DocumentFixer(orig_doc)
        document_fixer.soft_hyphen_to_hyph_tag()

        self.assertXmlEqual(etree.tostring(document_fixer.root), expected_doc)

    def test_compact_em1(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p><em>1</em> <em>2</em></p>
    </body>
</document>'''))
        document_fixer.compact_ems()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p><em>1 2</em></p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_compact_em2(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p><em>1</em> <em>2</em> 3</p>
    </body>
</document>'''))
        document_fixer.compact_ems()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p><em>1 2</em> 3</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_compact_em3(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p><em>1</em> <em>2</em> <span/> <em>3</em> <em>4</em></p>
    </body>
</document>'''))
        document_fixer.compact_ems()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p><em>1 2</em> <span/> <em>3 4</em></p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_compact_em4(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p><em>1</em> <em>2</em> 5<span/> <em>3</em> <em>4</em> 6</p>
    </body>
</document>'''))
        document_fixer.compact_ems()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p><em>1 2</em> 5<span/> <em>3 4</em> 6</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_compact_em5(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(r'''<document>
    <header/>
    <body>
        <p><em></em> <em>2</em> 5<span/> <em>3</em> <em></em> 6</p>
    </body>
</document>'''))
        document_fixer.compact_ems()
        got = document_fixer.get_etree()
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p><em>2</em> 5<span/> <em>3</em> 6</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_fix_sms1(self):
        '''\u2019 (’) should be replaced by \u02BC (ʼ)'''
        document_fixer = converter.DocumentFixer(etree.fromstring(
            u'<document xml:lang="sms">'
            u'  <header/>'
            u'  <body>'
            u'     <p>'
            u'       Mätt’temaaunâstuâjj '
            u'     </p>'
            u'  </body>'
            u'</document>'))
        document_fixer.fix_body_encoding()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            u'<document xml:lang="sms">'
            u'  <header/>'
            u'  <body>'
            u'     <p>'
            u'       Mättʼtemaaunâstuâjj '
            u'     </p>'
            u'  </body>'
            u'</document>')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_fix_sms2(self):
        '''\u0027 (')  should be replaced by \u02BC (ʼ)'''
        document_fixer = converter.DocumentFixer(etree.fromstring(
            u'<document xml:lang="sms">'
            u'  <header/>'
            u'  <body>'
            u'     <p>'
            u"       ǩiõll'laž da kulttuursaž vuõiggâdvuõđi"
            u'     </p>'
            u'  </body>'
            u'</document>'))
        document_fixer.fix_body_encoding()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            u'<document xml:lang="sms">'
            u'  <header/>'
            u'  <body>'
            u'     <p>'
            u'       ǩiõllʼlaž da kulttuursaž vuõiggâdvuõđi'
            u'     </p>'
            u'  </body>'
            u'</document>')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_fix_sms3(self):
        '''\u2032 (′)  should be replaced by \u02B9 (ʹ)'''
        document_fixer = converter.DocumentFixer(etree.fromstring(
            u'<document xml:lang="sms">'
            u'  <header/>'
            u'  <body>'
            u'     <p>'
            u'       Mon tõzz še njui′ǩǩeem tõ′st dõõzze.'
            u'     </p>'
            u'  </body>'
            u'</document>'))
        document_fixer.fix_body_encoding()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            u'<document xml:lang="sms">'
            u'  <header/>'
            u'  <body>'
            u'     <p>'
            u'       Mon tõzz še njuiʹǩǩeem tõʹst dõõzze.'
            u'     </p>'
            u'  </body>'
            u'</document>')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_fix_sms4(self):
        '''\u00B4 (´)  should be replaced by \u02B9 (ʹ)'''
        document_fixer = converter.DocumentFixer(etree.fromstring(
            u'<document xml:lang="sms">'
            u'  <header/>'
            u'  <body>'
            u'     <p>'
            u'       Materialbaaŋk čuä´jtumuš'
            u'     </p>'
            u'  </body>'
            u'</document>'))
        document_fixer.fix_body_encoding()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            u'<document xml:lang="sms">'
            u'  <header/>'
            u'  <body>'
            u'     <p>'
            u'       Materialbaaŋk čuäʹjtumuš'
            u'     </p>'
            u'  </body>'
            u'</document>')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))


class TestXslMaker(XMLTester):

    def test_get_xsl(self):
        xslmaker = converter.XslMaker(
            os.path.join(here,
                         'converter_data/samediggi-article-48.html.xsl'))
        got = xslmaker.xsl

        # The import href is different for each user testing, so just
        # check that it looks OK:
        import_elt = got.find(
            '/xsl:import',
            namespaces={'xsl': 'http://www.w3.org/1999/XSL/Transform'})
        self.assertTrue(import_elt.attrib["href"].startswith("file:///"))
        self.assertTrue(import_elt.attrib["href"].endswith("common.xsl"))
        self.assertGreater(len(open(
            import_elt.attrib["href"][7:].replace('%20', ' '), 'r').read()), 0)
        # ... and set it to the hardcoded path in test.xsl:
        import_elt.attrib["href"] = (
            'file:///home/boerre/langtech/trunk/tools/CorpusTools/'
            'corpustools/xslt/common.xsl')

        want = etree.parse(os.path.join(here, 'converter_data/test.xsl'))
        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))


class TestPDFTextElement(XMLTester):
    def test_is_text_on_same_line_1(self):
        '''When top is the same, two text elements are on the same line'''
        prev_t = converter.PDFTextElement(etree.fromstring(
            '<text top="354" left="119" width="205" height="22" font="2">'
            '1.1.   RIEKTEJOAVKKU</text>'))
        t1 = converter.PDFTextElement(etree.fromstring(
            '<text top="354" left="332" width="6" height="22" font="2"> </text>'))

        self.assertTrue(t1.is_text_on_same_line(prev_t))

    def test_is_text_on_same_line_2(self):
        ''''''
        prev_t = converter.PDFTextElement(etree.fromstring(
            '<text top="354" left="332" width="6" height="22" font="2"> </text>'))
        t1 = converter.PDFTextElement(etree.fromstring(
            '<text top="350" left="339" width="4" height="16" font="7"> </text>'))

        self.assertTrue(t1.is_text_on_same_line(prev_t))

    def test_is_text_on_same_line_3(self):
        ''''''
        prev_t = converter.PDFTextElement(etree.fromstring(
            '<text top="350" left="339" width="4" height="16" font="7"> </text>'))
        t1 = converter.PDFTextElement(etree.fromstring(
            '<text top="354" left="343" width="104" height="22" font="2">MANDÁHTA</text>'))

        self.assertTrue(t1.is_text_on_same_line(prev_t))

    def test_is_text_on_same_line_4(self):
        ''''''
        prev_t = converter.PDFTextElement(etree.fromstring(
            '<text top="354" left="615" width="13" height="22" font="2">  </text>'))
        t1 = converter.PDFTextElement(etree.fromstring(
            '<text top="376" left="119" width="6" height="22" font="2"> </text>'))

        self.assertFalse(t1.is_text_on_same_line(prev_t))

    def test_merge_text_elements(self):
        '''Merge two text elements'''
        prev_t = converter.PDFTextElement(etree.fromstring(
            '<text top="354" left="119" width="205" height="22" font="2">'
            '1.1. RIEKTEJOAVKKU</text>'))
        t1 = converter.PDFTextElement(etree.fromstring(
            '<text top="354" left="332" width="6" height="22" font="2"> </text>'))

        prev_t.merge_text_elements(t1)
        self.assertXmlEqual(
            etree.tostring(prev_t.t),
            '<text top="354" left="119" width="211" height="22" font="2">'
            '1.1. RIEKTEJOAVKKU </text>')


class TestPDFParagraph(XMLTester):
    def setUp(self):
        self.textelements = [
            converter.PDFTextElement(etree.fromstring(
                u'<text top="1078" left="86" width="347" height="15" font="4">guoh-</text>')),
            converter.PDFTextElement(etree.fromstring(
                u'<text top="1095" left="85" width="349" height="15" font="4">tuma </text>')),
            converter.PDFTextElement(etree.fromstring(
                u'<text top="112" left="464" width="347" height="15" font="4">main</text>'))
        ]

    def test_append_first_textelement(self):
        pp = converter.PDFParagraph()
        pp.append_textelement(self.textelements[0])

        self.assertListEqual(pp.textelements, self.textelements[:-2])
        self.assertEqual(pp.boundingboxes[-1].top, self.textelements[0].top)
        self.assertEqual(pp.boundingboxes[-1].left, self.textelements[0].left)
        self.assertEqual(pp.boundingboxes[-1].bottom, self.textelements[0].bottom)
        self.assertEqual(pp.boundingboxes[-1].right, self.textelements[0].right)
        self.assertEqual(len(pp.boundingboxes), 1)

    def test_append_textelement_from_same_column(self):
        pp = converter.PDFParagraph()
        pp.append_textelement(self.textelements[0])
        pp.append_textelement(self.textelements[1])

        self.assertListEqual(pp.textelements, self.textelements[:-1])
        self.assertEqual(len(pp.boundingboxes), 1)
        self.assertEqual(pp.boundingboxes[-1].top, self.textelements[0].top)
        self.assertEqual(pp.boundingboxes[-1].left, self.textelements[1].left)
        self.assertEqual(pp.boundingboxes[-1].bottom, self.textelements[1].bottom)
        self.assertEqual(pp.boundingboxes[-1].right, self.textelements[1].right)

    def test_append_textelement_from_different_column(self):
        pp = converter.PDFParagraph()
        pp.append_textelement(self.textelements[0])
        pp.append_textelement(self.textelements[1])
        pp.append_textelement(self.textelements[2])

        self.assertListEqual(pp.textelements, self.textelements)

        self.assertEqual(len(pp.boundingboxes), 2)
        self.assertEqual(pp.boundingboxes[-2].top, self.textelements[0].top)
        self.assertEqual(pp.boundingboxes[-2].left, self.textelements[1].left)
        self.assertEqual(pp.boundingboxes[-2].bottom, self.textelements[1].bottom)
        self.assertEqual(pp.boundingboxes[-2].right, self.textelements[1].right)
        self.assertEqual(pp.boundingboxes[-1].top, self.textelements[2].top)
        self.assertEqual(pp.boundingboxes[-1].left, self.textelements[2].left)
        self.assertEqual(pp.boundingboxes[-1].bottom, self.textelements[2].bottom)
        self.assertEqual(pp.boundingboxes[-1].right, self.textelements[2].right)

    def test_is_same_paragraph_when_top_is_equal(self):
        '''Test is_same_paragraph

        Text elements that are on the same line should be considered to be
        in the same paragraph
        '''
        pp = converter.PDFParagraph()
        pp.append_textelement(
            converter.PDFTextElement(etree.fromstring(
                '<text top="323" left="117" width="305" height="16" font="2">gihligotteriektái</text>')))
        t1 = converter.PDFTextElement(etree.fromstring(
            '<text top="323" left="428" width="220" height="16" font="2">, sáhtte</text>'))

        self.assertTrue(pp.is_text_in_same_paragraph(t1))

    def test_is_same_paragraph_1(self):
        '''Two text elements, x distance less 1.5 times their height'''
        pp = converter.PDFParagraph()
        pp.append_textelement(
            converter.PDFTextElement(etree.fromstring(
                '<text top="106" left="117" width="305" height="19" font="2">Text1 </text>')))
        t1 = converter.PDFTextElement(etree.fromstring(
            '<text top="126" left="117" width="305" height="19" font="2">text2</text>'))

        self.assertTrue(pp.is_text_in_same_paragraph(t1))

    def test_is_same_paragraph_2(self):
        '''Two text elements, x distance larger 1.5 times their height'''
        pp = converter.PDFParagraph()
        pp.append_textelement(
            converter.PDFTextElement(etree.fromstring(
                '<text top="106" left="117" width="305" height="19" font="2"/>')))
        t1 = converter.PDFTextElement(etree.fromstring(
            '<text top="140" left="117" width="305" height="19" font="2"/>'))

        self.assertFalse(pp.is_text_in_same_paragraph(t1))

    def test_is_same_paragraph_3(self):
        '''Two text elements, different heights'''
        pp = converter.PDFParagraph()
        pp.append_textelement(
            converter.PDFTextElement(etree.fromstring(
                '<text top="106" left="117" width="305" height="19" font="2"/>')))
        t1 = converter.PDFTextElement(etree.fromstring(
            '<text top="126" left="117" width="305" height="20" font="2"/>'))

        self.assertFalse(pp.is_text_in_same_paragraph(t1))

    def test_is_same_paragraph_4(self):
        '''Two text elements, different fonts'''
        pp = converter.PDFParagraph()
        pp.append_textelement(
            converter.PDFTextElement(etree.fromstring(
                '<text top="106" left="117" width="305" height="19" font="1">Text1</text>')))
        t1 = converter.PDFTextElement(etree.fromstring(
            '<text top="126" left="117" width="305" height="19" font="2">Text2</text>'))

        self.assertTrue(pp.is_text_in_same_paragraph(t1))

    def test_is_same_paragraph_5(self):
        '''List characters signal a new paragraph start'''
        pp = converter.PDFParagraph()
        pp.append_textelement(
            converter.PDFTextElement(etree.fromstring(
                '<text top="106" left="117" width="305" height="19" font="2"/>')))
        t1 = converter.PDFTextElement(etree.fromstring(
            '<text top="126" left="117" width="305" height="19" font="2">•</text>'))

        self.assertFalse(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_6(self):
        '''Upper case char and in_list=True signals new paragraph start'''
        pp = converter.PDFParagraph()
        pp.append_textelement(
            converter.PDFTextElement(etree.fromstring(
                '<text top="300" left="104" width="324" height="18" font="1">'
                'linnjá</text>')))
        t1 = converter.PDFTextElement(etree.fromstring(
            '<text top="321" left="121" width="40" height="18" font="1">'
            'Nubbi dábáláš linnjá</text>'))

        self.assertTrue(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_7(self):
        '''and in_list=True signals same paragraph'''
        pp = converter.PDFParagraph()
        pp.append_textelement(
            converter.PDFTextElement(etree.fromstring(
                '<text top="300" left="104" width="324" height="18" font="1">'
                'linnjá</text>')))
        pp.in_list = True
        t1 = converter.PDFTextElement(etree.fromstring(
            '<text top="321" left="121" width="40" height="18" font="1">'
            ' nubbi dábáláš linnjá</text>'))

        self.assertTrue(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_on_different_column_or_page1(self):
        '''Not same paragraph if first letter in second element is number'''
        pp = converter.PDFParagraph()
        pp.append_textelement(
            converter.PDFTextElement(etree.fromstring(
                '<text top="1143" left="168" width="306" height="18" '
                'font="1">Kopp</text>')))
        t1 = converter.PDFTextElement(etree.fromstring(
            '<text top="492" left="523" width="309" height="18" '
            'font="1">2.</text>'))

        self.assertFalse(pp.is_same_paragraph(t1))

    def test_is_same_paragraph_on_different_column(self):
        '''Same paragraph if first letter in second element is lower case'''
        pp = converter.PDFParagraph()
        pp.append_textelement(
            converter.PDFTextElement(etree.fromstring(
                '<text top="1143" left="168" '
                'width="306" height="18" font="1">skuvl-</text>')))
        t1 = converter.PDFTextElement(etree.fromstring(
            '<text top="492" left="523" width="309" '
            'height="18" font="1">lain</text>'))

        self.assertTrue(pp.is_same_paragraph(t1))


class TestPDFTextExtractor(XMLTester):
    def test_extract_textelement1(self):
        '''Extract text from a plain pdf2xml text element'''
        p2x = converter.PDFTextExtractor()

        input = etree.fromstring(
            '<text top="649" left="545" width="269" height="14" font="20">'
            'berret bargat. </text>')
        p2x.extract_textelement(input)
        self.assertXmlEqual(etree.tostring(p2x.p, encoding='utf8'),
                            '<p>berret bargat. </p>')

    def test_extract_textelement3(self):
        '''Extract text from a pdf2xml text that contains an <i> element'''
        p2x = converter.PDFTextExtractor()

        input = etree.fromstring(
            '<text top="829" left="545" width="275" height="14" font="29">'
            '<i>Ei </i></text>')
        p2x.extract_textelement(input)
        self.assertXmlEqual(etree.tostring(p2x.p, encoding='utf8'),
                            '<p><em type="italic">Ei </em></p>')

    def test_extract_textelement4(self):
        '''Extract text from a pdf2xml text that contains a <b> element'''
        p2x = converter.PDFTextExtractor()

        input = etree.fromstring(
            '<text top="829" left="545" width="275" height="14" font="29">'
            '<b>Ei </b></text>')
        p2x.extract_textelement(input)
        self.assertXmlEqual(etree.tostring(p2x.p, encoding='utf8'),
                            '<p><em type="bold">Ei </em></p>')

    def test_extract_textelement5(self):
        '''Text that contains a <b> element inside the <i> element'''
        p2x = converter.PDFTextExtractor()

        input = etree.fromstring(
            '<text top="829" left="545" width="275" height="14" font="29">'
            '<i><b>Eiš </b></i></text>')
        p2x.extract_textelement(input)

        self.assertXmlEqual(etree.tostring(p2x.p, encoding='utf8'),
                            '<p><em type="italic">Eiš </em></p>')

    def test_extract_textelement6(self):
        '''Text that contains a <b> element including a tail'''
        p2x = converter.PDFTextExtractor()

        input = etree.fromstring(
            '<text top="829" left="545" width="275" height="14" font="29">'
            '<b>E</b> a</text>')
        p2x.extract_textelement(input)
        self.assertXmlEqual(etree.tostring(p2x.p, encoding='utf8'),
                            '<p><em type="bold">E</em> a</p>')

    def test_extract_textelement7(self):
        '''Extract text from a pdf2xml text that contains two <i> elements'''
        p2x = converter.PDFTextExtractor()

        input = etree.fromstring(
            '<text top="829" left="545" width="275" height="14" font="29">'
            '<i>E</i> a <i>b</i></text>')
        p2x.extract_textelement(input)

        self.assertXmlEqual(etree.tostring(p2x.p, encoding='utf8'),
                            '<p><em type="italic">E</em> a <em type="italic">b</em></p>')

    def test_extract_textelement8(self):
        '''Text that contains one <i> element with several <b> elements'''
        p2x = converter.PDFTextExtractor()

        input = etree.fromstring(
            '<text top="837" left="57" width="603" height="11" font="7">'
            '<i><b>Å.</b> B <b>F.</b> A </i></text>')
        p2x.extract_textelement(input)

        self.assertXmlEqual(etree.tostring(p2x.p, encoding='utf8'),
                            '<p><em type="italic">Å. B F. A </em></p>')

    def test_extract_textelement9(self):
        '''Text that contains one <b> element with several <i> elements'''
        p2x = converter.PDFTextExtractor()

        input = etree.fromstring(
            '<text top="837" left="57" width="603" height="11" font="7">'
            '<b><i>Å.</i> B <i>F.</i> A </b></text>')
        p2x.extract_textelement(input)

        self.assertXmlEqual(etree.tostring(p2x.p, encoding='utf8'),
                            '<p><em type="bold">Å. B F. A </em></p>')

    def test_get_body(self):
        '''Test the initial values when the class is initiated'''
        p2x = converter.PDFTextExtractor()

        self.assertXmlEqual(etree.tostring(p2x.body), u'<body><p/></body>')

    def test_handle_line_ending_shy(self):
        p2x = converter.PDFTextExtractor()
        p2x.extract_textelement(etree.fromstring(u'<text>a\xAD</text>'))
        p2x.handle_line_ending()

        self.assertXmlEqual(
            etree.tostring(p2x.p), u'<p>a\xAD</p>')

    def test_handle_line_ending_hyphen(self):
        p2x = converter.PDFTextExtractor()
        p2x.extract_textelement(etree.fromstring(u'<text>a-</text>'))
        p2x.handle_line_ending()

        self.assertXmlEqual(
            etree.tostring(p2x.p), u'<p>a\xAD</p>')

    def test_handle_line_not_shy_nor_hyphen(self):
        p2x = converter.PDFTextExtractor()
        p2x.extract_textelement(etree.fromstring(u'<text>a</text>'))
        p2x.handle_line_ending()

        self.assertXmlEqual(
            etree.tostring(p2x.p), u'<p>a </p>')

    def test_handle_upper_case_on_new_page(self):
        '''If the first paragraph begins with an uppercase letter, start a new p'''
        p2x = converter.PDFTextExtractor()
        p2x.p.text = 'not ending with sentence stop character'

        paragraphs = [converter.PDFParagraph()]
        paragraphs[-1].append_textelement(
            converter.PDFTextElement(etree.fromstring(
                '<text top="1" left="1" width="1" height="1">Upper case.</text>')))

        p2x.extract_text_from_page(paragraphs)

        self.assertXmlEqual(etree.tostring(p2x.body),
                            u'''
                            <body>
                                <p>not ending with sentence stop character</p>
                                <p>Upper case.</p>
                            </body>''')

    def test_handle_number_on_new_page(self):
        '''If the first paragraph begins with an uppercase letter, start a new p'''
        p2x = converter.PDFTextExtractor()
        p2x.p.text = 'not ending with sentence stop character'

        paragraphs = [converter.PDFParagraph()]
        paragraphs[-1].append_textelement(
            converter.PDFTextElement(etree.fromstring(
                '<text top="1" left="1" width="1" height="1">1 element.</text>')))

        p2x.extract_text_from_page(paragraphs)

        self.assertXmlEqual(etree.tostring(p2x.body),
                            u'''
                            <body>
                                <p>not ending with sentence stop character</p>
                                <p>1 element.</p>
                            </body>''')

Interval = collections.namedtuple('Interval', ['start', 'end'])


class TestPDFSection1(XMLTester):
    def setUp(self):
        self.textelements = [
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="51" width="25">258</text>''')),

            converter.PDFTextElement(etree.fromstring(u'''<text font="5" height="12" left="85" top="72" width="62">1. Mielddus</text>''')),

            converter.PDFTextElement(etree.fromstring(u'''<text font="9" height="15" left="85" top="377" width="86">
            <i>
                <b>6.1. tabealla.</b>
            </i>
            </text>''')),

            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="274" top="403" width="291">DoalloovttadagatOlbmotAlimus boazolohku</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="428" width="95">Elgå 6303 000</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="446" width="158">Riast/Hylling10514 500</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="463" width="121">Essand 10434 500</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="480" width="142">Trollheimen5201 600</text>''')),

            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="506" width="133">Submi 3114413 600</text>''')),

            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="560" width="347">Femunddas  lea  alimus  mearriduvvon  boazolohku</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="577" width="347">9 000  bohcco.  Boazolohku  lea  juhkkojuvvon  ovt-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="595" width="347">tamađe Riast/Hylling ja Essand orohagaid gaskka. Go</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="7" height="15" left="461" top="560" width="347">
            <b>6.2. tabeallas</b>meroštallá boazoeatnatvuođa ja buvtta-
            </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="577" width="347">deami juohke areálovttadaga nammii, leat Femundda</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="595" width="283">areálat juogáduvvon dán guovtti orohahkii.</text>''')),

            converter.PDFTextElement(etree.fromstring(u'''<text font="9" height="15" left="85" top="638" width="560">
            <i>
                <b>6.2. tabealla.</b>Lulli-Trøndelága/Hedmark boazodoalloguovllu eatnamiid geavaheapmi.
            </i>
            </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="299" top="666" width="210">AreálaBoazolohkuBuvttadeapmi</text>''')),

            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="308" top="684" width="263">km201.04.98juohke km2kg/km2kg/boazu</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="713" width="161">Elgå100730263,032,411</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="730" width="259">Femund (dálvejagi guohtun)1103(8887)</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="747" width="316">Riast/Hylling (bievlajahki)248143141,722,612,3</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="764" width="275">Essand (bievlajahki)287645731,617,310,5</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="782" width="216">Trollheimen223516300,77,910,7</text>''')),

            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="304" top="807" width="303">8598135431,618,211,2</text>''')),

            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="853" width="347">Lea mihá eambo boazoeatnatvuohta go Davvi-Trøn-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="871" width="347">delágas, Nordlánddas ja Romssas. Duogážin lea dál-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="888" width="347">vejagi  guohtumiid  vejolašvuohta,  ja  áigodaga  iešgu-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="905" width="347">đetlágan  guođohanvejolašvuohta.  Earret  Elgå,  leat</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="922" width="347">Lulli-Trøndelága/Hedmark  orohagaid  boazoeatnat-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="940" width="346">vuohta  vuollelis  go  Kárášjogas  (2,4  bohcco/km2)  ja</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="957" width="346">Oarje-Finnmárkkus  (3,1  bohcco/km2).  Riast/Hylling</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="974" width="347">orohagas lea eambbo buvttadeapmi bohcco ektui go</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="991" width="347">dáin earáin, muhto buot orohagaid dássi lea vuollelis</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="1009" width="347">go ovdal. Elgå:s lea mearkkašahtti alla boazolohku ja</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="1026" width="347">buvttadeapmi  juohke  areálovttadaga  nammii.  Eará</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="853" width="347">orohagain Norggas ii dáidde leat ná stuora areálbuvt-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="871" width="64">tadeapmi.</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="478" top="888" width="329">Maŋemus  golmma  jagi  njuovvandeattuid  oaidnit</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="7" height="15" left="461" top="905" width="347">
            <b>6.2. tabeallas.</b>Das oaidnit orohagaid siskkáldas ero-
            </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="922" width="347">husaid jagis jahkái. Dás boahtá ovdan ahte dássi lea</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="940" width="347">veahá vuollelis go Nordlánddas ja Davvi-Trøndelágas</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="957" width="347">ja arvat vuollelis Romssa. Orohagaid siskkáldas ero-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="974" width="347">husat jagis jahkái leat luonddudilálašvuođaid erohu-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="991" width="347">said  geažil,  muhto  erohusat  sáhttet  maiddái  váikku-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="1009" width="347">huvvot das makkár bohccuid leat njuovvan ja makkár</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="1026" width="130">ealihanbohccot leat.</text>''')),

            converter.PDFTextElement(etree.fromstring(u'''<text font="10" height="24" left="85" top="110" width="344">
            <b>6.1 Lulli-Trøndelága/Hedmark –</b>
            </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="10" height="24" left="136" top="134" width="227">
            <b>Jämtlándda leana, lulit</b>
            </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="10" height="24" left="136" top="158" width="69">
            <b>guovlu</b>
            </text>''')),

            converter.PDFTextElement(etree.fromstring(u'''<text font="9" height="15" left="85" top="198" width="76">
            <i>
                <b>Obbalaččat</b>
            </i>
            </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="215" width="347">Prinsihpas eai leat orohatrájit rievdaduvvon jagi 1894</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="232" width="347">rájes. Rievdadeamit leat váldosaččat dahkkon máŋg-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="250" width="347">gaid duomuid vuođul maid Alimusriekti lea meannu-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="267" width="347">dan. Das daddjo ahte orohagat leat ovddasvástádus-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="284" width="347">suorggit,  ja  dat  ii  dárbbaš  mearkkašit  ahte  dain  lea</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="301" width="346">vuoigatvuohta  guovlluide.  Lávdegotti  mandáhttan</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="319" width="347">ii leat  čiekŋudit  dien  áššái,  muhto  fágalávdegoddi</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="85" top="336" width="347">oaidná movt eahpečielga riektedilli lea dagahan labiila</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="112" width="347">dilálašvuođaid.  Dán  geažil  leage  lávdegoddái  váttis</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="129" width="347">suokkardit dálá guohtuneatnamiid geavaheami ja dan</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="146" width="289">vuođul evttohit rievdadusaid guohtunrájiide.</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="478" top="163" width="330">Guovllus leat 6 boazoorohaga. Riast ja Hylling lea</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="181" width="347">oktasaš. Essand ja Riast/Hylling orohagain lea oktasaš</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="198" width="347">dálvejagi  guohtun  Femunddas.  Elgå  ja  Trollheimen</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="215" width="347">leat  fas  birrajagiorohagat.  Trollheimen  lea  áidna</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="232" width="347">orohat  mii  ii  leat  riikaráji  guoras,  muhto  lea  sierra</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="250" width="347">eará orohagain eret. Danne eat čilge dárkileappot dán</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="267" width="347">orohaga  birra.  Eará  orohagaid  birra  mii  čilget</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="284" width="72">oktasaččat.</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="7" height="15" left="478" top="301" width="330">
            <b>6.1.  ja  6.2.  tabeallas</b>oaidnit  boazodoalloguovllu
            </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text font="4" height="15" left="461" top="319" width="190">struktuvrra ja eatnamiid anu.</text>''')),
        ]

        self.paragraphs = [
            Interval(start=0, end=1),
            Interval(start=1, end=2),
            Interval(start=2, end=3),
            Interval(start=3, end=4),
            Interval(start=4, end=8),
            Interval(start=8, end=9),
            Interval(start=9, end=15),
            Interval(start=15, end=16),
            Interval(start=16, end=18),
            Interval(start=18, end=23),
            Interval(start=23, end=24),
            Interval(start=24, end=46),
            Interval(start=46, end=49),
            Interval(start=49, end=72),
        ]

        self.sections = [
            Interval(start=0, end=1),
            Interval(start=1, end=2),
            Interval(start=2, end=3),
            Interval(start=3, end=4),
            Interval(start=4, end=8),
            Interval(start=8, end=9),
            Interval(start=9, end=15),
            Interval(start=15, end=16),
            Interval(start=16, end=18),
            Interval(start=18, end=23),
            Interval(start=23, end=24),
            Interval(start=24, end=46),
            Interval(start=46, end=72),
        ]

    def test_one_page(self):
        in_page = etree.fromstring('<page height="1261" left="0" number="258" position="absolute" top="0" width="892"/>')
        for textelement in self.textelements:
            in_page.append(textelement.t)

        pp = converter.PDFPage(in_page)

        got_page = etree.fromstring('<page height="1261" left="0" number="258" position="absolute" top="0" width="892"/>')
        for paragraph in pp.make_paragraphs():
            for textelement in paragraph.textelements:
                got_page.append(textelement.t)
        uff = etree.tostring(got_page, encoding=unicode, pretty_print=True)

        want_page = etree.fromstring('<page height="1261" left="0" number="258" position="absolute" top="0" width="892"/>')
        want_sections = [0, 1, 12]
        want_sections.extend(range(2, 12))

        for pos in want_sections:
            this_pos = self.sections[pos]
            for textelement in self.textelements[this_pos.start:this_pos.end]:
                want_page.append(textelement.t)

        self.assertEqual(uff, etree.tostring(want_page, encoding=unicode, pretty_print=True))

    def test_is_same_section_first_pdftextelement_is_true(self):
        t = converter.PDFTextElement(etree.fromstring(u'''<text font="10" height="24" left="85" top="110" width="344">
            <b>6.1 Lulli-Trøndelága/Hedmark –</b>
            </text>'''))
        p = converter.PDFParagraph()
        p.append_textelement(t)

        s = converter.PDFSection()
        self.assertTrue(s.is_same_section(p))

    def test_is_same_section_2(self):

        p1 = converter.PDFParagraph()
        for t in self.textelements[self.paragraphs[-2].start:self.paragraphs[-2].end]:
            p1.append_textelement(t)
        p2 = converter.PDFParagraph()
        for t in self.textelements[self.paragraphs[-1].start:self.paragraphs[-1].end]:
            p2.append_textelement(t)

        s = converter.PDFSection()
        s.append_paragraph(p1)

        self.assertTrue(s.is_same_section(p2))

    def test_is_same_section_3(self):
        for pos in range(1, len(self.paragraphs) - 1):
            prev_p = self.paragraphs[pos - 1]
            this_p = self.paragraphs[pos]
            p1 = converter.PDFParagraph()
            for t in self.textelements[prev_p.start:prev_p.end]:
                p1.append_textelement(t)
            p2 = converter.PDFParagraph()
            for t in self.textelements[this_p.start:this_p.end]:
                p2.append_textelement(t)

            s = converter.PDFSection()
            s.append_paragraph(p1)

            self.assertFalse(s.is_same_section(p2))

    def test_ordering_1(self):
        os = converter.OrderedPDFSections()
        sections = []

        s = converter.PDFSection()
        p = converter.PDFParagraph()
        for t in self.textelements[self.paragraphs[-3].start:self.paragraphs[-3].end]:
            p.append_textelement(t)
        s.append_paragraph(p)
        sections.append(s)
        os.insert_section(s)

        s = converter.PDFSection()
        p = converter.PDFParagraph()
        for t in self.textelements[self.paragraphs[-2].start:self.paragraphs[-2].end]:
            p.append_textelement(t)
        s.append_paragraph(p)

        s = converter.PDFSection()
        p = converter.PDFParagraph()
        for t in self.textelements[self.paragraphs[-2].start:self.paragraphs[-2].end]:
            p.append_textelement(t)
        s.append_paragraph(p)

        sections.insert(0, s)
        os.insert_section(s)

        self.assertListEqual(os.sections, sections)


class TestPDFSection2(XMLTester):
    def setUp(self):
        self.textelements = [
            converter.PDFTextElement(etree.fromstring(u'''<text top="51" left="85" width="17" height="15" font="4">12</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="72" left="85" width="62" height="12" font="5">1. Mielddus</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="193" left="85" width="213" height="24" font="10"><b>1.1 Bohcco dárbbut</b></text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="232" left="85" width="347" height="15" font="4">Miehtá  Davvikálohta  leat  asehis  guohtoneatnamat</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="250" left="85" width="347" height="15" font="4">bohccuide. Boazu lea luonddudilálašvuođaid hálddus</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="267" left="85" width="347" height="15" font="4">birra jagi. Guohtunšattut leat iešguđetláganat jagi ieš-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="284" left="85" width="347" height="15" font="4">guđetge áiggis, ja guohtundilli váikkuhage dasto man</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="301" left="85" width="347" height="15" font="4">ollu boazu guohtu ja movt johtala. Dákko dáfus lea</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="319" left="85" width="347" height="15" font="4">boazu  sierralágan  dilis,  Skandinávia  eará  dábmojuv-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="336" left="85" width="347" height="15" font="4">von  elliid  suktii.  Go  mii  árvvoštállat  guohtumiid,</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="353" left="85" width="347" height="15" font="4">bidjat  bohcco  fysiologalaš  dárbbuid  vuođđun  ja</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="370" left="85" width="231" height="15" font="4">makkár guohtuma boazu dárbbaša.</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="433" left="85" width="215" height="18" font="11"><i><b>1.1.1 Fysiologalaš dárbbut</b></i></text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="457" left="85" width="347" height="15" font="4">Boazu maiddái, nu movt earáge eallit, dárbbaša kar-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="474" left="85" width="347" height="15" font="4">bohydráhtaid ja buoiddi, maid joraha álšan ja doalaha</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="491" left="85" width="347" height="15" font="4">goruda doaimmaid, oažžu lieggasa ja sáhttá lihkadit.</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="508" left="85" width="347" height="15" font="4">Proteiinnat,  vitamiinnat  ja  minerálat  adnojit  hukset</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="526" left="85" width="347" height="15" font="4">dehkiid  ja  eará  gorutgođđosiid,  ja  mielkki  buvtta-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="543" left="85" width="59" height="15" font="4">deapmái.</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="560" left="102" width="330" height="15" font="4">Boazu lea, nu movt eará smirezasti eallit nai, ere-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="577" left="85" width="347" height="15" font="4">noamážit heivehuvvon smoldet guohtunšattuid. Alm-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="595" left="85" width="347" height="15" font="4">matge smoaldanit duššefal okta oasáš das maid boazu</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="612" left="85" width="347" height="15" font="4">guohtu. Dakkár guohtunšattut mat smoaldanit geahp-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="629" left="85" width="347" height="15" font="4">pasit,  leat  buorit  guohtun.  Ruonasšattut  smoaldanit</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="646" left="85" width="347" height="15" font="4">álkimusat dalle go leat beallešattus ja smoaldaneapmi</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="664" left="85" width="347" height="15" font="4">hedjona  dađi  mielde  go  šattuid  šaddandássi  ovdána.</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="681" left="85" width="347" height="15" font="4">Go biebmu smoaldahuvvá unnán, ii oaččo boazu nu</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="698" left="85" width="347" height="15" font="4">ollu energiija dehe álšša. Maiddái biebmojohtin čoliid</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="715" left="85" width="142" height="15" font="4">čađa mánná njozebut.</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="733" left="102" width="330" height="15" font="4">Boazu lea mihá buorebut, go eará smirezasti eallit,</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="750" left="85" width="347" height="15" font="4">heivehuvvon  smoldet  jeahkála.  Jeahkála  smoalda-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="767" left="85" width="347" height="15" font="4">neapmi  lea  buorre  birra  jagi.  Dainna  lágiin  nagoda</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="784" left="85" width="347" height="15" font="4">boazu  doalahit  buorren  obbalaš  biebmosmoldema,</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="802" left="85" width="347" height="15" font="4">vaikko vel eará guohtun leage vánis ja maiddái kvali-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="819" left="85" width="347" height="15" font="4">tehta lea rievddalmas. Dađistaga go čavččabeallái hed-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="836" left="85" width="347" height="15" font="4">jona  ruonasšattuid  smoaldaneapmi,  guohtugoahtá</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="853" left="85" width="347" height="15" font="4">boazu  eambbo  jeahkála,  iige  guođo  nu  ollu  ruonas-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="871" left="85" width="347" height="15" font="4">šattuid,  ja  nu  nagoda  almmatge  doalahit  dássedis</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="888" left="85" width="118" height="15" font="4">biebmosmoldema.</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="905" left="102" width="330" height="15" font="4">Jeagil smoaldana geahppasit, muhto lea ovttagear-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="922" left="85" width="347" height="15" font="4">dánis fuođđar. Jeagelšlájain oažžu boazu nu ollu álšša</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="940" left="85" width="347" height="15" font="4">(karbohydráhtaid)  ahte  ceavzá  badjel  dálvvi,  muhto</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="957" left="85" width="347" height="15" font="4">váilot  proteiinnat,  vitamiinnat  ja  minerálat.  Bohcco</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="974" left="85" width="346" height="15" font="4">guomočoavjebaktearat  dárbbašit  dađistaga  ee.  pro-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="991" left="85" width="347" height="15" font="4">teiinnat,  ja  danne  váikkuha  smolden  čoavjjis  ahte</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="1009" left="85" width="347" height="15" font="4">boazu, mii lea jeagelguohtumis, deahkkehuvvá dálvet.</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="1026" left="85" width="347" height="15" font="4">Boazu deahkkehuvvagoahtá dakkaviđe go boahtá jea-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="1043" left="85" width="347" height="15" font="4">gelguohtumii. Muhto bohccos lea sierralágan vuohki</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="1060" left="85" width="347" height="15" font="4">mainna easttada vai ii deahkkehuva, go boazu sáhttá</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="1078" left="85" width="347" height="15" font="4">“nuppádassii  geavahit”  nitrogena,  maid  eará  smire-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="1095" left="85" width="129" height="15" font="4">zasti eallit eai sáhte.</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="198" left="478" width="330" height="15" font="4">Vaikko  boazu  deahkkehuvváge,  sáhttá  dat  liikká</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="215" left="461" width="347" height="15" font="4">lossut  dálvet,  jus  fal  lea  buorre  jeagelguohtun,  mas</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="232" left="461" width="347" height="15" font="4">boazu oažžu eambbo energiija go dat man loaktá. Dát</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="250" left="461" width="347" height="15" font="4">energiija jorrá buoidin gorudii ja čoggo dohko nu ahte</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="267" left="461" width="107" height="15" font="4">boazu ii geahpo.</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="284" left="478" width="330" height="15" font="4">Boazu guoira gal dábálaččat dálvvis. Rávis njiŋŋe-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="301" left="461" width="347" height="15" font="4">las  geahppu  giđđii  15  %  čakčadeattu  ektui,  vaikko</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="319" left="461" width="347" height="15" font="4">leage čoavjjehin ja miessi deaddá 4-5 kg šattadettiin.</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="336" left="461" width="347" height="15" font="4">Sarvát  sáhttet  geahpput  30  %  čakčamánus  juovla-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="353" left="461" width="347" height="15" font="4">mánnui. Dálvvi mielde gehppot bohccot dađistaga ja</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="370" left="461" width="347" height="15" font="4">erenoamáš heajos guohtumis sáhttet geahpput gitta 50</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="388" left="461" width="347" height="15" font="4">% rádjái. Jus guohtun hedjona nu sakka ahte čoavje-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="405" left="461" width="347" height="15" font="4">liepma goiká, dehe nuppeládje dadjat ahte mikroorga-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="422" left="461" width="347" height="15" font="4">nismmat  nohket,  nealgugoahtá  boazu.  Lassin  dasa</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="439" left="461" width="347" height="15" font="4">ahte boazu dárbbaša eallámuša (proteiinnaid ja mine-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="457" left="461" width="347" height="15" font="4">rálaid),  gollada  boazu  deahkkemássa  ja  joraha  dán</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="474" left="461" width="347" height="15" font="4">energiijan. Guhkálmas nealgumiin ii nagat šat boazu</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="491" left="461" width="283" height="15" font="4">doalahit dábálaš gorutdoaimmaid ja jápmá.</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="508" left="478" width="330" height="15" font="4">Miesit  ja  boarrasit  varrásat  nelgot  bahábut  go</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="526" left="461" width="347" height="15" font="4">njiŋŋelasat ja čearpmahat. Sarvát rávžet ragatáiggi, ja</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="543" left="461" width="347" height="15" font="4">nuolppot  manahit  maiddái  bohccuidgaskasaš  árvo-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="560" left="461" width="347" height="15" font="4">dási.  Nuolppot  eai  bálle  guohtut  ráfis,  dannego</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="577" left="461" width="347" height="15" font="4">njiŋŋelasat doroldahttet nulpobohccuid eret suvnnjiin.</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="595" left="461" width="347" height="15" font="4">Gehppes  miesit  sáhttet  nealgut.  Smávva  áldduin  leat</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="612" left="461" width="347" height="15" font="4">dávjá  gehppes  miesit,  mii  fas  dagaha  stuorit  miesse-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="629" left="461" width="347" height="15" font="4">jámu. Heajos dálveguohtun dagaha fas áldduid mielk-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="646" left="461" width="347" height="15" font="4">keheabbon  go  dábálaš  dan  vuosttaš  geasi,  ja  dat  fas</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="664" left="461" width="347" height="15" font="4">váikkuha ahte miesit leat geahppaseappot čakčat. Boa-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="681" left="461" width="347" height="15" font="4">zomassimat, mat bohciidit fysiologalaš beliid sivas, eai</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="698" left="461" width="347" height="15" font="4">leat  nu  oidnosis  dannego  boraspirevahágat  lassánit</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="715" left="461" width="66" height="15" font="4">dađistaga.</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="733" left="478" width="330" height="15" font="4">Bohccuid  sáhttá  biebmat  fuođđariiguin  dálvet</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="750" left="461" width="347" height="15" font="4">heajos guohtumiid áigge, ja dustet váttisvuođa dáinna-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="767" left="461" width="347" height="15" font="4">lágiin.  Guomočoavjji  mikrobat  dahket  almmatge</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="784" left="461" width="347" height="15" font="4">duššin dáid iešguđetlágan fuođđaršlájaid. Danne dárb-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="802" left="461" width="347" height="15" font="4">bašit bohccot dagalduvvat fuođđariidda hui árrat, dan</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="819" left="461" width="347" height="15" font="4">bále go mikroorganismmat leat olleslogus čoavjjis ja</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="836" left="461" width="347" height="15" font="4">nákcejit smoldegoahtit ođđa fuođđariid. Eanas boazo-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="853" left="461" width="347" height="15" font="4">eaiggádat eai almmatge biebmagoađe bohccuid áiggil,</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="871" left="461" width="347" height="15" font="4">muhto vurdet eaigo guohtumat buorrán. Doloža rájes</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="888" left="461" width="347" height="15" font="4">lei  vierrun  diktit  ealu  lávdat  jus  heajos  guohtumat</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="905" left="461" width="347" height="15" font="4">biste guhkit áiggi. Dalle boazu ieš ohcá guohtuma mii</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="922" left="461" width="58" height="15" font="4">gávdnoš.</text>''')), converter.PDFTextElement(etree.fromstring(u'''<text top="940" left="478" width="330" height="15" font="4">Dálvet  guohtu  eallu  eanas  áigge,  lea  lodji,  iige</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="957" left="461" width="347" height="15" font="4">manat álššaid duššái. Lihkadeapmái adnojit álššat, ja</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="974" left="461" width="347" height="15" font="4">joavdelas  lihkahallan  dehe  lihkadeapmi  manaha</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="991" left="461" width="347" height="15" font="4">álššaid.  Lihkahallan  sáhttá  ovdamearkka  dihte  leat</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="1009" left="461" width="347" height="15" font="4">čohkkemat,  boraspiret  ja  mátkkošteaddjit  muose-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="1026" left="461" width="347" height="15" font="4">huhttet ealu, dehe eallu ruvgala jna. Lassin dasa gask-</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="1043" left="461" width="347" height="15" font="4">kalduvvá  guohtumiin.  Álšamanaheami  ii  sáhte  šat</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="1060" left="461" width="347" height="15" font="4">buhttet maŋŋil eambbo guohtumiin. Danne geahppu</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="1078" left="461" width="347" height="15" font="4">boazu,  ja  jus  hui  hejot  manná,  sáhttet  váibbahat</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="1095" left="461" width="316" height="15" font="4">jápmit go oalát nohkkojit duksejuvvon buoiddis.</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="110" left="239" width="416" height="30" font="6"><b>1. Boazoguohtumat Skandinavias</b></text>''')),
        ]

        self.paragraphs = [
            Interval(start=0, end=1),
            Interval(start=1, end=2),
            Interval(start=2, end=12),
            Interval(start=12, end=13),
            Interval(start=13, end=104),
            Interval(start=104, end=105),
        ]

        self.sections = [
            Interval(start=0, end=1),
            Interval(start=1, end=2),
            Interval(start=2, end=104),
            Interval(start=104, end=105),
        ]

    def test_one_page(self):
        in_page = etree.fromstring('<page height="1261" left="0" number="258" position="absolute" top="0" width="892"/>')
        for textelement in self.textelements:
            in_page.append(textelement.t)

        pp = converter.PDFPage(in_page)

        got_page = etree.fromstring('<page height="1261" left="0" number="258" position="absolute" top="0" width="892"/>')
        for paragraph in pp.make_paragraphs():
            for textelement in paragraph.textelements:
                got_page.append(textelement.t)
        uff = etree.tostring(got_page, encoding=unicode, pretty_print=True)

        want_page = etree.fromstring('<page height="1261" left="0" number="258" position="absolute" top="0" width="892"/>')
        want_sections = [0, 1, 3, 2]

        for pos in want_sections:
            this_pos = self.sections[pos]
            for textelement in self.textelements[this_pos.start:this_pos.end]:
                want_page.append(textelement.t)

        self.assertEqual(uff, etree.tostring(want_page, encoding=unicode, pretty_print=True))

    def test_is_same_section_1(self):
        p1 = converter.PDFParagraph()
        for t in self.textelements[self.paragraphs[-2].start:self.paragraphs[-2].end]:
            p1.append_textelement(t)
        p2 = converter.PDFParagraph()
        for t in self.textelements[self.paragraphs[-1].start:self.paragraphs[-1].end]:
            p2.append_textelement(t)

        s = converter.PDFSection()
        s.append_paragraph(p1)

        self.assertFalse(s.is_same_section(p2))


class TestPDFSection3(XMLTester):
    def setUp(self):
        self.textelements = [
            converter.PDFTextElement(etree.fromstring(u'''<text top="298" left="322" width="216" height="18" font="1">muital olus ohppiid birra geain leat </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="316" left="322" width="91" height="18" font="1">buorit gálggat.</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="352" left="322" width="180" height="18" font="1">Kártengeahččaleamit eai leat </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="370" left="322" width="175" height="18" font="1">geahččaleamit fágas, muhto </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="388" left="322" width="182" height="18" font="1">vuođđogálggain fágaid rastá. </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="406" left="322" width="223" height="18" font="1">Oahppoplánain leat vuođđogálggat </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="424" left="322" width="114" height="18" font="1">definerejuvvon ná:</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="442" left="322" width="128" height="18" font="1">• njálmmálaš gálggat</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="460" left="322" width="94" height="18" font="1">• máhttit lohkat</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="478" left="322" width="84" height="18" font="1">• máhttit čállit</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="496" left="322" width="124" height="18" font="1">• máhttit rehkenastit</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="514" left="322" width="103" height="18" font="1">• digitála gálggat</text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="550" left="322" width="213" height="18" font="1">Rehkenastinbihtáid ovdamearkkat </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="568" left="322" width="236" height="18" font="1">sáhttet leat lohkat, sirret loguid sturro- </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="586" left="322" width="218" height="18" font="1">dagaid mielde, loahpahit lohkogur- </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="604" left="322" width="210" height="18" font="1">gadasaid ja rehkenastit plussain ja </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="622" left="322" width="225" height="18" font="1">minusiin. Lohkamis sáhttá leat sáhka </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="640" left="322" width="235" height="18" font="1">ovdamearkka dihtii bustávaid čállimis, </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="658" left="322" width="237" height="18" font="1">sániid lohkamis ja cealkagiid lohkamis. </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="676" left="322" width="239" height="18" font="1">Guovddážis digitála gálggaid geahčča- </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="694" left="322" width="237" height="18" font="1">leami bihtáin lea háhkat ja meannudit, </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="712" left="322" width="249" height="18" font="1">buvttadit ja divodit, gulahallat ja digitála </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="730" left="322" width="202" height="18" font="1">árvvoštallannávccat. Guovddážis </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="748" left="322" width="241" height="18" font="1">eŋgelasgiellageahččaleamis lea dovdat </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="766" left="322" width="247" height="18" font="1">ja ipmirdit oahpes ja beaivválaš sániid ja </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="784" left="322" width="208" height="18" font="1">dajaldagaid, njálmmálaččat dahje </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="802" left="322" width="233" height="18" font="1">čálalaččat. Geahččaleamis leat guokte </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="820" left="322" width="209" height="18" font="1">oasi, guldalanoassi ja lohkanoassi. </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="838" left="322" width="212" height="18" font="1">Ohppiin ferte leat oaivetelefovdna </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="856" left="322" width="93" height="18" font="1">guldalanoasis.  </text>''')),
            converter.PDFTextElement(etree.fromstring(u'''<text top="298" left="593" width="170" height="19" font="0"><b>Bohtosat ja čuovvoleapmi</b></text>''')),
        ]

        self.paragraphs = [
            Interval(start=0, end=30),
            Interval(start=30, end=31),
        ]

        self.sections = [
            Interval(start=0, end=31),
        ]

    def test_is_same_section_1(self):
        p1 = converter.PDFParagraph()
        for t in self.textelements[self.paragraphs[-2].start:self.paragraphs[-2].end]:
            p1.append_textelement(t)
        p2 = converter.PDFParagraph()
        for t in self.textelements[self.paragraphs[-1].start:self.paragraphs[-1].end]:
            p2.append_textelement(t)

        s = converter.PDFSection()
        s.append_paragraph(p1)

        self.assertTrue(s.is_same_section(p2))


class TestPDFPage(XMLTester):
    def test_width(self):
        page = converter.PDFPage(etree.fromstring('<page number="1" height="1263" width="862"/>'))

        self.assertEqual(page.number, 1)
        self.assertEqual(page.height, 1263)
        self.assertEqual(page.width, 862)

    def test_remove_footnotes_superscript_1(self):
        '''Footnote superscript is in the middle of a sentence'''
        page = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '   <text top="323" left="117" width="305" height="16" font="2">'
            'gihligotteriektái</text>'
            '   <text top="319" left="422" width="6" height="11" font="7">3'
            '</text>'
            '   <text top="323" left="428" width="220" height="16" font="2">, '
            'sáhtte</text>'
            '</page>'
        )
        pdfpage = converter.PDFPage(page)
        pdfpage.remove_footnotes_superscript()

        page_want = [u'gihligotteriektái', '', u', sáhtte']

        self.assertListEqual([t.t.xpath('string()') for t in pdfpage.textelements],
                             page_want)

    def test_remove_footnotes_superscript_2(self):
        '''Footnote superscript is at the end of a sentence'''
        page = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '   <text top="323" left="117" width="305" height="16" font="2">'
            'gihligotteriektái</text>'
            '   <text top="319" left="422" width="6" height="11" font="7">'
            '3</text>'
            '   <text top="344" left="428" width="220" height="16" font="2">,'
            'sáhtte</text>'
            '</page>'
        )
        pdfpage = converter.PDFPage(page)
        pdfpage.remove_footnotes_superscript()

        page_want = [u'gihligotteriektái', '', u',sáhtte']

        self.assertListEqual([t.t.xpath('string()') for t in pdfpage.textelements],
                             page_want)

    def test_remove_footnotes_superscript_3(self):
        '''Footnote superscript in between i-elements'''
        page = etree.fromstring(
            '<page number="1" height="1263" width="892">'
            '    <text top="267" left="119" width="164" height="22" font="9"><i>riektedilálašvuođa</i></text>'
            '    <text top="265" left="283" width="15" height="15" font="7">16</text>'
            '    <text top="267" left="298" width="503" height="22" font="9"><i> </i>čielggadeamit&#34; (min deattuhus) ráddjejuvvot dasa mii </text>'
            '</page>'
        )
        pdfpage = converter.PDFPage(page)
        pdfpage.remove_footnotes_superscript()

        page_want = [u'riektedilálašvuođa', u'', u' čielggadeamit" (min deattuhus) ráddjejuvvot dasa mii ']

        self.assertListEqual([t.t.xpath('string()') for t in pdfpage.textelements],
                             page_want)

    def test_remove_footnotes_superscript_4(self):
        '''Footnote superscript contained in i-element'''
        page = etree.fromstring(
            '<page number="1" height="1263" width="892">'
            '   <text top="682" left="119" width="187" height="22" font="9"><i>báhcánvuoigatvuođa</i></text>'
            '   <text top="680" left="306" width="20" height="15" font="11"><i>59</i> </text>'
            '   <text top="704" left="119" width="666" height="22" font="2"> - nuppiin sániiguin dan mii áiggis áigái ii leat čuldon dahje earát váldán. </text>'
            '</page>'
        )
        pdfpage = converter.PDFPage(page)
        pdfpage.remove_footnotes_superscript()

        page_want = [u'báhcánvuoigatvuođa', u' ', u' - nuppiin sániiguin dan mii áiggis áigái ii leat čuldon dahje earát váldán. ']

        self.assertListEqual([t.t.xpath('string()') for t in pdfpage.textelements],
                             page_want)

    def test_remove_footnotes_superscript_5(self):
        '''Footnote superscript at the samel level as other text'''
        page = etree.fromstring(
            '<page number="1" height="1261" width="892">'
            '   <text top="560" left="102" width="231" height="15" font="4">Boazu lea, nu movt eará smirezasti</text>'
            '   <text top="560" left="333" width="8" height="9" font="12">1 </text>'
            '   <text top="560" left="341" width="91" height="15" font="4">eallit nai, ere-</text>'
            '</page>'
        )
        pdfpage = converter.PDFPage(page)
        pdfpage.remove_footnotes_superscript()

        page_want = [u'Boazu lea, nu movt eará smirezasti', u' ', u'eallit nai, ere-']

        self.assertListEqual([t.t.xpath('string()') for t in pdfpage.textelements],
                             page_want)

    def test_remove_footnotes_superscript_6(self):
        '''Footnote superscript inside two levels'''
        page = etree.fromstring(
            '<page number="1" height="1261" width="892">'
            '   <text top="560" left="102" width="231" height="15" font="4">Boazu lea, nu movt eará smirezasti</text>'
            '   <text top="560" left="333" width="8" height="9" font="12"><a><b>34</b></a></text>'
            '   <text top="560" left="341" width="91" height="15" font="4">eallit nai, ere-</text>'
            '</page>'
        )
        pdfpage = converter.PDFPage(page)
        pdfpage.remove_footnotes_superscript()

        page_want = [u"Boazu lea, nu movt eará smirezasti", u"", u"eallit nai, ere-"]

        self.assertListEqual([t.t.xpath('string()') for t in pdfpage.textelements],
                             page_want)

    def test_remove_elements_not_within_margin_1(self):
        '''Check that elements within inner_margins for a specific page are removed'''
        md = xslsetter.MetadataHandler('test.pdf.xsl', create=True)
        md.set_variable('inner_top_margin', '8=40')
        md.set_variable('inner_bottom_margin', '8=40')

        page = etree.fromstring(
            '\n'.join([
                '<page number="8" height="1263" width="862">',
                '<text top="500" left="80" width="512" height="19" font="0">1</text>'
                '<text top="600" left="80" width="512" height="19" font="0">2</text>'
                '<text top="800" left="80" width="512" height="19" font="0">3</text>'
                '</page>'
            ])
        )
        pdfpage = converter.PDFPage(page,
                                    metadata_inner_margins=md.inner_margins)
        pdfpage.remove_elements_not_within_margin()
        page_want = ["1", "3"]

        self.assertListEqual([t.t.xpath('string()') for t in pdfpage.textelements], page_want)

    def test_remove_elements_not_within_margin_2(self):
        '''Check that no elements are removed when inner_margins is not defined for the page'''
        md = xslsetter.MetadataHandler('test.pdf.xsl', create=True)
        md.set_variable('inner_top_margin', '1=40')
        md.set_variable('inner_bottom_margin', '1=40')

        page = etree.fromstring(
            '\n'.join([
                '<page number="8" height="1263" width="862">',
                '<text top="500" left="80" width="512" height="19" font="0">1</text>'
                '<text top="600" left="80" width="512" height="19" font="0">2</text>'
                '<text top="800" left="80" width="512" height="19" font="0">3</text>'
                '</page>'
            ])
        )
        pdfpage = converter.PDFPage(page, metadata_inner_margins=md.inner_margins)
        pdfpage.remove_elements_not_within_margin()
        page_want = ["1", "2", "3"]

        self.assertListEqual([t.t.xpath('string()') for t in pdfpage.textelements], page_want)

    def test_compute_default_margins(self):
        '''Test if the default margins are set'''
        page1 = converter.PDFPage(etree.fromstring(
            '<page number="1" height="1263" width="862"/>'))

        self.assertEqual(page1.compute_margins(), {'left_margin': 60,
                                                   'right_margin': 802,
                                                   'top_margin': 88,
                                                   'bottom_margin': 1175})

    def test_compute_margins1(self):
        '''Test parse_margin_lines'''
        md = xslsetter.MetadataHandler('test.pdf.xsl', create=True)
        md.set_variable('left_margin', '7=5')
        md.set_variable('right_margin', 'odd=10,even=15,3=5')
        md.set_variable('top_margin', '8=8')
        md.set_variable('bottom_margin', '9=20')

        page1 = converter.PDFPage(
            etree.fromstring('<page number="1" height="1263" width="862"/>'),
            metadata_margins=md.margins)

        self.assertEqual(page1.compute_margins(), {'left_margin': 60,
                                                   'right_margin': 776,
                                                   'top_margin': 88,
                                                   'bottom_margin': 1175})
        page2 = converter.PDFPage(
            etree.fromstring('<page number="2" height="1263" width="862"/>'),
            metadata_margins=md.margins)
        self.assertEqual(page2.compute_margins(), {'left_margin': 60,
                                                   'right_margin': 733,
                                                   'top_margin': 88,
                                                   'bottom_margin': 1175})
        page3 = converter.PDFPage(
            etree.fromstring('<page number="3" height="1263" width="862"/>'),
            metadata_margins=md.margins)
        self.assertEqual(page3.compute_margins(), {'left_margin': 60,
                                                   'right_margin': 819,
                                                   'top_margin': 88,
                                                   'bottom_margin': 1175})
        page7 = converter.PDFPage(
            etree.fromstring('<page number="7" height="1263" width="862"/>'),
            metadata_margins=md.margins)
        self.assertEqual(page7.compute_margins(), {'left_margin': 43,
                                                   'right_margin': 776,
                                                   'top_margin': 88,
                                                   'bottom_margin': 1175})
        page8 = converter.PDFPage(
            etree.fromstring('<page number="8" height="1263" width="862"/>'),
            metadata_margins=md.margins)
        self.assertEqual(page8.compute_margins(), {'left_margin': 60,
                                                   'right_margin': 733,
                                                   'top_margin': 101,
                                                   'bottom_margin': 1175})
        page9 = converter.PDFPage(
            etree.fromstring('<page number="9" height="1263" width="862"/>'),
            metadata_margins=md.margins)
        self.assertEqual(page9.compute_margins(), {'left_margin': 60,
                                                   'right_margin': 776,
                                                   'top_margin': 88,
                                                   'bottom_margin': 1011})

    def test_compute_inner_margins_1(self):
        '''Test if inner margins is set for the specified page'''
        md = xslsetter.MetadataHandler('test.pdf.xsl', create=True)
        md.set_variable('inner_top_margin', '1=40')
        md.set_variable('inner_bottom_margin', '1=40')

        page1 = converter.PDFPage(
            etree.fromstring('<page number="1" height="1263" width="862"/>'),
            metadata_inner_margins=md.inner_margins)

        self.assertEqual(page1.compute_inner_margins(),
                         {'inner_top_margin': 505, 'inner_bottom_margin': 758,
                          'inner_left_margin': 0, 'inner_right_margin': 862})

    def test_compute_inner_margins_2(self):
        '''Test that inner margins is empty for the specified page'''
        md = xslsetter.MetadataHandler('test.pdf.xsl', create=True)
        md.set_variable('inner_top_margin', '1=40')
        md.set_variable('inner_bottom_margin', '1=40')

        page1 = converter.PDFPage(
            etree.fromstring('<page number="2" height="1263" width="862"/>'),
            metadata_inner_margins=md.inner_margins)

        self.assertEqual(page1.compute_inner_margins(), {})

    def test_is_inside_margins1(self):
        '''top and left inside margins'''
        t = converter.PDFTextElement(etree.fromstring('<text top="109" left="135"/>'))
        margins = {}
        margins['left_margin'] = 62
        margins['right_margin'] = 802
        margins['top_margin'] = 88
        margins['bottom_margin'] = 1174

        p2x = converter.PDFPage(etree.fromstring('<page number="2" height="1263" width="862"/>'))

        self.assertTrue(p2x.is_inside_margins(t, margins))

    def test_is_inside_margins2(self):
        '''top above top margin and left inside margins'''
        t = converter.PDFTextElement(etree.fromstring('<text top="85" left="135"/>'))
        margins = {}
        margins['left_margin'] = 62
        margins['right_margin'] = 802
        margins['top_margin'] = 88
        margins['bottom_margin'] = 1174

        p2x = converter.PDFPage(etree.fromstring('<page number="2" height="1263" width="862"/>'))

        self.assertFalse(p2x.is_inside_margins(t, margins))

    def test_is_inside_margins3(self):
        '''top below bottom margin and left inside margins'''
        t = converter.PDFTextElement(etree.fromstring('<text top="1178" left="135"/>'))
        margins = {}
        margins['left_margin'] = 62
        margins['right_margin'] = 802
        margins['top_margin'] = 88
        margins['bottom_margin'] = 1174

        p2x = converter.PDFPage(etree.fromstring('<page number="2" height="1263" width="862"/>'))

        self.assertFalse(p2x.is_inside_margins(t, margins))

    def test_is_inside_margins4(self):
        '''top inside margins and left outside right margin'''
        t = converter.PDFTextElement(etree.fromstring('<text top="1000" left="50"/>'))
        margins = {}
        margins['left_margin'] = 62
        margins['right_margin'] = 802
        margins['top_margin'] = 88
        margins['bottom_margin'] = 1174

        p2x = converter.PDFPage(etree.fromstring('<page number="2" height="1263" width="862"/>'))

        self.assertFalse(p2x.is_inside_margins(t, margins))

    def test_is_inside_margins5(self):
        '''top inside margins and left outside left margin'''
        t = converter.PDFTextElement(etree.fromstring('<text top="1000" left="805"/>'))
        margins = {}
        margins['left_margin'] = 62
        margins['right_margin'] = 802
        margins['top_margin'] = 88
        margins['bottom_margin'] = 1174

        p2x = converter.PDFPage(etree.fromstring('<page number="2" height="1263" width="862"/>'))

        self.assertFalse(p2x.is_inside_margins(t, margins))

    def test_is_skip_page_1(self):
        '''Odd page should be skipped when odd is in skip_pages'''
        p2x = converter.PDFPage(etree.fromstring('<page number="1" height="1263" width="862"/>'))

        self.assertTrue(p2x.is_skip_page(['odd']))

    def test_is_skip_page_2(self):
        '''Even page should be skipped when even is in skip_pages'''
        p2x = converter.PDFPage(etree.fromstring('<page number="2" height="1263" width="862"/>'))

        self.assertTrue(p2x.is_skip_page(['even']))

    def test_is_skip_page_3(self):
        '''Even page should not be skipped when odd is in skip_pages'''
        p2x = converter.PDFPage(etree.fromstring('<page number="2" height="1263" width="862"/>'))

        self.assertFalse(p2x.is_skip_page(['odd']))

    def test_is_skip_page_4(self):
        '''Odd page should not be skipped when even is in skip_pages'''
        p2x = converter.PDFPage(etree.fromstring('<page number="1" height="1263" width="862"/>'))

        self.assertFalse(p2x.is_skip_page(['even']))

    def test_is_skip_page_5(self):
        '''Page should not be skipped when not in skip_range'''
        p2x = converter.PDFPage(etree.fromstring('<page number="1" height="1263" width="862"/>'))

        self.assertFalse(p2x.is_skip_page(['even', 3]))

    def test_is_skip_page_6(self):
        '''Page should be skipped when in skip_range'''
        p2x = converter.PDFPage(etree.fromstring('<page number="3" height="1263" width="862"/>'))

        self.assertTrue(p2x.is_skip_page(['even', 3]))

    def test_parse_page_textelement_witdh_zero_not_added(self):
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<text top="649" left="545" width="0" height="14" font="20">'
            'berret bargat. </text>'
            '</page>')

        pp = converter.PDFPage(page_element)
        pp.remove_invalid_elements()

        self.assertEqual(len(pp.textelements), 0)


class TestPDF2XMLConverter(XMLTester):
    '''Test the class that converts from pdf2xml to giellatekno/divvun xml'''
    def test_pdf_converter(self):
        pdfdocument = converter.PDF2XMLConverter(
            os.path.join(here, 'converter_data/pdf-test.pdf'))
        got = pdfdocument.convert2intermediate()
        want = etree.parse(
            os.path.join(here, 'converter_data/pdf-xml2pdf-test.xml'))

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_parse_page_1(self):
        '''Page with one paragraph, three <text> elements'''
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<text top="106" left="100" width="100" height="19">a </text>'
            '<text top="126" left="100" width="100" height="19">b </text>'
            '<text top="145" left="100" width="100" height="19">c.</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.extractor.body, encoding='unicode'),
            u'<body><p>a b c.</p></body>')

    def test_parse_page_2(self):
        '''Page with two paragraphs, four <text> elements'''
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<text top="106" left="100" width="100" height="19">a </text>'
            '<text top="126" left="100" width="100" height="19">b.</text>'
            '<text top="166" left="100" width="100" height="19">c </text>'
            '<text top="186" left="100" width="100" height="19">d.</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.extractor.body, encoding='unicode'),
            u'<body><p>a b.</p><p>c d.</p></body>')

    def test_parse_page_3(self):
        '''Page with one paragraph, one <text> elements'''
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<text top="145" left="100" width="100" height="19">3.</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.extractor.body, encoding='unicode'),
            u'<body><p>3.</p></body>')

    def test_parse_page_4(self):
        '''One text element with a ascii letter, the other one with a non-ascii

        This makes two parts lists. The first list contains one element that is
        of type str, the second list contains one element that is unicode.
        '''
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<text top="215" left="100" width="51" height="14">R</text>'
            '<text top="245" left="100" width="39" height="14">Ø</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.extractor.body, encoding='unicode'),
            u'<body><p>R</p><p>Ø</p></body>')

    def test_parse_page_5(self):
        '''Test parse pages

        One text element containing a <b>, the other one with a
        non-ascii string. Both belong to the same paragraph.
        '''
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<text top="215" left="100" width="51" height="14"><b>R</b></text>'
            '<text top="235" left="100" width="39" height="14">Ø</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.extractor.body, encoding='unicode'),
            u'<body><p><em type="bold">R</em>Ø</p></body>')

    def test_parse_page_6(self):
        '''One text element ending with a hyphen.'''
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<text top="215" left="100" width="51" height="14">R-</text>'
            '<text top="235" left="100" width="39" height="14">Ø</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.extractor.body, encoding='unicode'),
            u'<body><p>R\xADØ</p></body>')

    def test_parse_page_7(self):
        '''One text element ending with a hyphen.'''
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<text top="215" left="100" width="51" height="14">R -</text>'
            '<text top="235" left="100" width="39" height="14">Ø</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.extractor.body, encoding='unicode'),
            u'<body><p>R - Ø</p></body>')

    def test_parse_page_8(self):
        '''One text element ending with a hyphen.'''
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<text top="196" left="142" width="69" height="21" font="15">'
            '<b>JULE-</b></text>'
            '<text top="223" left="118" width="123" height="21" font="15">'
            '<b>HANDEL</b></text></page>')

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.extractor.body, encoding='unicode'),
            u'<body><p><em type="bold">JULE\xAD</em><em type="bold">HANDEL</em></p></body>')

    def test_parse_page_9(self):
        '''Two <text> elements. One is above the top margin.'''
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<text top="70" left="100" width="100" height="19">Page 1</text>'
            '<text top="145" left="100" width="100" height="19">3.</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.extractor.body, encoding='unicode'),
            u'<body><p>3.</p></body>')

    def test_parse_page_10(self):
        '''Two <text> elements. One is below the bottom margin.'''
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<text top="1200" left="100" width="100" height="19">Page 1</text>'
            '<text top="145" left="100" width="100" height="19">3.</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.extractor.body, encoding='unicode'),
            u'<body><p>3.</p></body>')

    def test_parse_page_11(self):
        '''Two <text> elements. One is to the left of the right margin.'''
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<text top="500" left="50" width="100" height="19">Page 1</text>'
            '<text top="145" left="100" width="100" height="19">3.</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.extractor.body, encoding='unicode'),
            u'<body><p>3.</p></body>')

    def test_parse_page_12(self):
        '''Two <text> elements. One is to the right of the left margin.'''
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<text top="500" left="850" width="100" height="19">Page 1</text>'
            '<text top="145" left="100" width="100" height="19">3.</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.extractor.body, encoding='unicode'),
            u'<body><p>3.</p></body>')

    def test_parse_page_13(self):
        '''Test list detection with • character'''
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

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(page_element)

        self.maxDiff = None
        self.assertXmlEqual(
            etree.tostring(p2x.extractor.body, encoding='unicode'),
            u'<body>'
            u'<p>vuosttaš dábálaš linnjá</p>'
            u'<p type="listitem"> Vuosttaš listolinnjá  '
            u'vuosttaš listolinnjá joaktta</p>'
            u'<p type="listitem"> Nubbi listo\xADlinnjá</p>'
            u'<p>Nubbi dábáláš linnjá</p>'
            u'</body>')

    def test_parse_page_14(self):
        '''Test that elements outside margin is not added'''
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<text top="1104" left="135" width="45" height="16" font="2">'
            '1751, </text>'
            '<text top="1184" left="135" width="4" height="15" font="0"> '
            '</text>'
            '<text top="1184" left="437" width="37" height="15" font="0">'
            '– 1 – </text>'
            '</page>')

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(page_element)

        self.assertEqual(
            etree.tostring(p2x.extractor.body, encoding='unicode'),
            u'<body>'
            u'<p>1751, </p>'
            u'</body>')

    def test_parse_page_soria_moria(self):
        '''The last element was not added to the p element'''
        page_element = etree.fromstring(
            '<page number="1" height="1263" width="862">'
            '<text top="666" left="104" width="312" height="18" font="1">A – <i>b </i></text>'
            '<text top="687" left="104" width="318" height="18" font="6"><i>c-d</i> – e-</text>'
            '<text top="708" left="104" width="328" height="18" font="1">f </text>'
            '</page>')

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(page_element)

        self.assertEqual(
            etree.tostring(p2x.extractor.body, encoding='unicode'),
            u'<body><p>A – <em type="italic">b </em><em type="italic">c-d</em> – e\xADf </p></body>')

    def test_parse_pdf2xmldoc1(self):
        '''Test how a parsing a simplistic pdf2xml document works'''
        pdf2xml = etree.fromstring(
            '<pdf2xml>'
            '<page number="1" height="1263" width="862"><fontspec/>'
            '<text top="145" left="100" width="100" height="19">1.</text>'
            '</page>'
            '<page number="2" height="1263" width="862">'
            '<text top="145" left="100" width="100" height="19">2.</text>'
            '</page>'
            '<page number="3" height="1263" width="862">'
            '<text top="145" left="100" width="100" height="19">3.</text>'
            '</page>'
            '</pdf2xml>')
        want = u'<body><p>1.</p><p>2.</p><p>3.</p></body>'

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(etree.tostring(p2x.extractor.body), want)

    def test_parse_pdf2xmldoc2(self):
        '''Test if pages really are skipped'''
        pdf2xml = etree.fromstring(
            '<pdf2xml>'
            '<page number="1" height="1263" width="862"><fontspec/>'
            '<text top="145" left="100" width="100" height="19">1.</text>'
            '</page>'
            '<page number="2" height="1263" width="862">'
            '<text top="145" left="100" width="100" height="19">2.</text>'
            '</page>'
            '<page number="3" height="1263" width="862">'
            '<text top="145" left="100" width="100" height="19">3.</text>'
            '</page>'
            '</pdf2xml>')
        want = u'<body><p>2.</p><p>3.</p></body>'

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.md.set_variable('skip_pages', '1')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(etree.tostring(p2x.extractor.body), want)

    def test_parse_pdf2xmldoc3(self):
        '''Check if paragraph is continued from page to page

        Paragraph should continue if the first character on next page is a
        lower case character
        '''
        pdf2xml = etree.fromstring(
            '<pdf2xml>'
            '<page number="1" position="absolute" top="0" left="0" '
            'height="1020" width="723">'
            '<text top="898" left="80" width="512" height="19" font="0">'
            'Dán </text>'
            '</page>'
            '<page number="2" position="absolute" top="0" left="0" '
            'height="1020" width="723">'
            '<text top="43" left="233" width="415" height="16" font="7">'
            'Top text </text>'
            '<text top="958" left="174" width="921" height="19" font="0">'
            '15 </text>'
            '<text top="93" left="131" width="512" height="19" font="0">'
            'barggus.</text>'
            '</page>'
            '</pdf2xml>')
        want = u'<body><p>Dán barggus.</p></body>'

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(etree.tostring(p2x.extractor.body), want)

    def test_parse_pdf2xmldoc4(self):
        '''Check if paragraph is continued from page to page

        Paragraph should continue if the first character on next page is a
        lower case character
        '''
        pdf2xml = etree.fromstring(
            '<pdf2xml>'
            '<page number="1" position="absolute" top="0" left="0" '
            'height="1020" width="723">'
            '<text top="898" left="80" width="512" height="19" font="0">'
            'Dán ovddidan-</text>'
            '</page>'
            '<page number="2" position="absolute" top="0" left="0" '
            'height="1020" width="723">'
            '<text top="43" left="233" width="415" height="16" font="7">'
            'Top text </text>'
            '<text top="958" left="174" width="921" height="19" font="0">'
            '15 </text>'
            '<text top="93" left="131" width="512" height="19" font="0">'
            'barggus.</text>'
            '</page>'
            '</pdf2xml>')
        want = u'<body><p>Dán ovddidan\xADbarggus.</p></body>'

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(etree.tostring(p2x.extractor.body), want)

    def test_text_disappears(self):
        '''bug 2115, Store deler av teksten blir borte'''
        pdf2xml = etree.fromstring(
            '''<pdf2xml>
<page number="40" position="absolute" top="0" left="0" height="1263" width="892">
<text top="1061" left="106" width="680" height="20" font="7"><i>vuođđooahpa-</i></text>
<text top="1085" left="106" width="653" height="20" font="7"><i>hussi. </i></text>
<text top="1110" left="106" width="5" height="20" font="7"><i> </i></text>
</page></pdf2xml>''')
        want = u'''<body><p><em type="italic">vuođđooahpa\xAD</em><em type="italic">hussi. </em></p></body>'''

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(etree.tostring(p2x.extractor.body, encoding='unicode'), want)

    def test_text_unwanted_line_shift(self):
        '''bug 2107, Linjeskift hvor det ikke skal være'''
        pdf2xml = etree.fromstring(
            '''<pdf2xml>
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
</page></pdf2xml>''')
        want = u'''<body><p>1.1. RIEKTEJOAVKKU MANDÁHTA JA ČOAHKÁDUS</p><p>1.1.1 Riektejoavkku nammadeami duogáš</p></body>'''

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(etree.tostring(p2x.extractor.body), want)

    def test_parse_pdf2xmldoc_ends_with_dot(self):
        '''If last string on a page ends with ., do not continue paragraph to next page'''
        pdf2xml = etree.fromstring(
            '<pdf2xml>'
            '<page number="1" height="1263" width="862"><fontspec/>'
            '<text top="145" left="100" width="100" height="19">1.</text>'
            '</page>'
            '<page number="2" height="1263" width="862">'
            '<text top="145" left="100" width="100" height="19">2.</text>'
            '</page>'

            '</pdf2xml>')
        want = u'<body><p>1.</p><p>2.</p></body>'

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(etree.tostring(p2x.extractor.body), want)

    def test_parse_pdf2xmldoc_ends_with_exclam(self):
        '''If last string on a page ends with !, do not continue paragraph to next page'''
        pdf2xml = etree.fromstring(
            '<pdf2xml>'
            '<page number="1" height="1263" width="862"><fontspec/>'
            '<text top="145" left="100" width="100" height="19">1!</text>'
            '</page>'
            '<page number="2" height="1263" width="862">'
            '<text top="145" left="100" width="100" height="19">2.</text>'
            '</page>'

            '</pdf2xml>')
        want = u'<body><p>1!</p><p>2.</p></body>'

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(etree.tostring(p2x.extractor.body), want)

    def test_parse_pdf2xmldoc_ends_with_question(self):
        '''If last string on a page ends with ?, do not continue paragraph to next page'''
        pdf2xml = etree.fromstring(
            '<pdf2xml>'
            '<page number="1" height="1263" width="862"><fontspec/>'
            '<text top="145" left="100" width="100" height="19">1?</text>'
            '</page>'
            '<page number="2" height="1263" width="862">'
            '<text top="145" left="100" width="100" height="19">2.</text>'
            '</page>'

            '</pdf2xml>')
        want = u'<body><p>1?</p><p>2.</p></body>'

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(etree.tostring(p2x.extractor.body), want)

    def test_parse_pdf2xmldoc_not_end_of_sentence(self):
        '''If last string on a page is not ended, continue paragraph'''
        pdf2xml = etree.fromstring(
            '<pdf2xml>'
            '<page number="1" height="1263" width="862"><fontspec/>'
            '<text top="145" left="100" width="100" height="19">a </text>'
            '</page>'
            '<page number="2" height="1263" width="862">'
            '<text top="145" left="100" width="100" height="19">b.</text>'
            '</page>'

            '</pdf2xml>')
        want = u'<body><p>a b.</p></body>'

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(etree.tostring(p2x.extractor.body), want)

    def test_parse_pdf2xmldoc_text_on_same_line_different_font(self):
        '''Test of bug2101'''
        pdf2xml = etree.fromstring(
            '<pdf2xml>'
            '<page number="1" height="1263" width="862"><fontspec/>'
            '<text top="187" left="64" width="85" height="14" font="20">bajás</text>'
            '<text top="187" left="149" width="6" height="14" font="8">š</text>'
            '<text top="187" left="155" width="280" height="14" font="20">addandili</text>'    '</page>'

            '</pdf2xml>')
        want = u'<body><p>bajásšaddandili</p></body>'

        p2x = converter.PDF2XMLConverter('bogus.xml')
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(etree.tostring(p2x.extractor.body), want)
