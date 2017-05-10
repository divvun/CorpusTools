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

from __future__ import absolute_import

import codecs
import collections
import doctest
import io
import os
import unittest

import lxml.doctestcompare as doctestcompare
import lxml.etree as etree
import lxml.html as html5parser
import lxml.objectify as objectify
import six
import testfixtures
from nose_parameterized import parameterized

from corpustools import converter, corpuspath, text_cat, xslsetter
from corpustools.test.test_xhtml2corpus import assertXmlEqual

here = os.path.dirname(__file__)
LANGUAGEGUESSER = text_cat.Classifier(None)


class XMLTester(unittest.TestCase):

    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal."""
        got = etree.tostring(got, encoding='unicode')
        want = etree.tostring(want, encoding='unicode')

        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(
                doctest.Example("", want), got, 0)
            raise AssertionError(message)


TestItem = collections.namedtuple('TestItem', ['name', 'orig', 'expected'])


def test_detect_quote():

    quote_tests = [
        TestItem(
            name='quote within QUOTATION MARK',
            orig='<p>bla "bla" bla "bla" bla </p>',
            expected=(
                '<p>bla <span type="quote">"bla"</span> bla'
                '<span type="quote">"bla"</span> bla</p>')),
        TestItem(
            name='quote within RIGHT DOUBLE QUOTATION MARK',
            orig='<p>bla bla ”bla bla” bla bla </p>',
            expected=(
                '<p>bla bla <span type="quote">”bla bla”</span> '
                'bla bla</p>')),
        TestItem(
            name=(
                'quote within LEFT DOUBLE QUOTATION MARK and '
                'RIGHT DOUBLE QUOTATION MARK'),
            orig='<p>bla bla “bla bla” bla bla</p>',
            expected=(
                '<p>bla bla <span type="quote">“bla bla”</span> bla bla</p>')),
        TestItem(
            name=(
                'quote within RIGHT DOUBLE QUOTATION MARK and '
                'quote within LEFT DOUBLE QUOTATION MARK and '
                'RIGHT DOUBLE QUOTATION MARK'),
            orig='<p>bla “bla” bla ”bla” bla</p>',
            expected=(
                '<p>bla <span type="quote">“bla”</span> bla '
                '<span type="quote">”bla”</span> bla</p>')),
        TestItem(name='simple_detect_quote3',
                 orig='<p>bla bla «bla bla» bla bla</p>',
                 expected=(
                     '<p>bla bla <span type="quote">«bla bla»</span> '
                     'bla bla</p>')),
        TestItem(name='simple_detect_quote4',
                 orig='<p type="title">Sámegiel čálamearkkat Windows XP várás.</p>',
                 expected=(
                     '<p type="title">Sámegiel čálamearkkat Windows XP várás.</p>')),
        TestItem(name='simple_detect_quote2_quotes',
                 orig='<p>bla bla «bla bla» bla bla «bla bla» bla bla</p>',
                 expected=(
                     '<p>bla bla <span type="quote">«bla bla»</span> bla bla '
                     '<span type="quote">«bla bla»</span> bla bla</p>')),
        TestItem(name='detect_quote_with_following_tag',
                 orig='<p>bla bla «bla bla» <em>bla bla</em></p>',
                 expected=(
                     '<p>bla bla <span type="quote">«bla bla»</span> <em>'
                     'bla bla</em></p>')),
        TestItem(name='detect_quote_with_tag_infront',
                 orig='<p>bla bla <em>bla bla</em> «bla bla»</p>',
                 expected=(
                     '<p>bla bla <em>bla bla</em> <span type="quote">'
                     '«bla bla»</span></p>')),
        TestItem(name='detect_quote_within_tag',
                 orig='<p>bla bla <em>bla bla «bla bla»</em></p>',
                 expected=(
                     '<p>bla bla <em>bla bla <span type="quote">'
                     '«bla bla»</span></em></p>')),
    ]

    for i in '.,?!:':
        quote_tests.append(
            TestItem(
                name='quote followed by {}'.format(i),
                orig=(
                    '<p>“bla”{} bla ”bla”</p>'.format(i)),
                expected=(
                    '<p><span type="quote">“bla”</span>{} bla '
                    '<span type="quote">”bla”</span></p>'.format(i))))

    for name, orig, expected in quote_tests:
        yield check_quote_detection, name, orig, expected


def check_quote_detection(name, orig, expected):
    document_fixer = converter.DocumentFixer(
        etree.parse(
            os.path.join(here,
                         'converter_data/samediggi-article-48s-before-'
                         'lang-detection-without-multilingual-tag.xml')))
    got_paragraph = document_fixer.detect_quote(
        etree.fromstring(orig))

    assertXmlEqual(got_paragraph, etree.fromstring(expected))


class TestComputeCorpusnames(unittest.TestCase):

    def name(self, module):
        return os.path.join(here, module, 'sme/admin/subdir/subsubdir/filename.html')

    def setUp(self):
        self.cp = corpuspath.CorpusPath(self.name('orig'))

    def test_compute_orig(self):
        self.assertEqual(
            self.cp.orig, self.name('orig'))

    def test_compute_xsl(self):
        self.assertEqual(self.cp.xsl, self.name('orig') + '.xsl')

    def test_compute_log(self):
        self.assertEqual(self.cp.log, self.name('orig') + '.log')

    def test_compute_converted(self):
        self.assertEqual(self.cp.converted, self.name('converted') + '.xml')

    def test_compute_prestable_converted(self):
        self.assertEqual(self.cp.prestable_converted,
                         self.name('prestable/converted') + '.xml')

    def test_compute_goldstandard_converted(self):
        self.cp.metadata.set_variable('conversion_status', 'correct')
        self.assertEqual(self.cp.converted,
                         self.name('goldstandard/converted') + '.xml')

    def test_compute_prestable_goldstandard_converted(self):
        self.cp.metadata.set_variable('conversion_status', 'correct')
        self.assertEqual(self.cp.prestable_converted,
                         self.name('prestable/goldstandard/converted') + '.xml')

    def test_compute_analysed(self):
        self.assertEqual(self.cp.analysed, self.name('analysed') + '.xml')


class TestConverter(XMLTester):

    def setUp(self):
        self.converter_inside_orig = converter.Converter(
            os.path.join(here,
                         'converter_data/fakecorpus/orig/nob/admin/samediggi-'
                         'article-16.html'),
            True)

        self.converter_inside_freecorpus = converter.Converter(
            os.path.join(
                os.getenv('GTFREE'),
                'orig/sme/admin/sd/samediggi.no/samediggi-article-48.html'),
            False)

    def test_get_orig(self):
        self.assertEqual(
            self.converter_inside_orig.names.orig,
            os.path.join(
                here,
                'converter_data/fakecorpus/orig/nob/admin/samediggi-article-'
                '16.html'))

        self.assertEqual(
            self.converter_inside_freecorpus.names.orig,
            os.path.join(
                os.getenv('GTFREE'),
                'orig/sme/admin/sd/samediggi.no/samediggi-article-48.html'))

    def test_get_xsl(self):
        self.assertEqual(
            self.converter_inside_orig.names.xsl,
            os.path.join(
                here,
                'converter_data/fakecorpus/orig/nob/admin/samediggi-'
                'article-16.html.xsl'))

        self.assertEqual(
            self.converter_inside_freecorpus.names.xsl,
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
            self.converter_inside_freecorpus.tmpdir,
            os.path.join(os.getenv('GTFREE'), 'tmp'))

    def test_get_corpusdir(self):
        self.assertEqual(
            self.converter_inside_orig.corpusdir.rstrip(os.path.sep),
            os.path.join(
                here,
                'converter_data/fakecorpus'))

        self.assertEqual(
            self.converter_inside_freecorpus.corpusdir.rstrip(
                os.path.sep),
            os.getenv('GTFREE').rstrip(os.path.sep))

    def test_get_converted_name_inside_orig(self):
        self.assertEqual(
            self.converter_inside_orig.names.converted,
            os.path.join(
                here,
                'converter_data/fakecorpus/converted/nob/admin/samediggi-'
                'article-16.html.xml'))

    def test_get_converted_inside_freecorpus(self):
        self.assertEqual(
            self.converter_inside_freecorpus.names.converted,
            os.path.join(
                os.getenv('GTFREE'),
                'converted/sme/admin/sd/samediggi.no/samediggi-'
                'article-48.html.xml'))

    def test_validate_complete(self):
        """Check that an exception is raised if a document is invalid."""
        complete = etree.fromstring('<document/>')

        self.assertRaises(converter.ConversionError,
                          self.converter_inside_orig.validate_complete,
                          complete)

    def test_detect_quote_is_skipped_on_errormarkup_documents(self):
        """quote detection should not be done in errormarkup documents

        This is a test for that covers the case covered in
        http://giellatekno.uit.no/bugzilla/show_bug.cgi?id=2151
        """
        want_string = '''
            <document xml:lang="smj" id="no_id">
            <header>
                <title/>
                <genre code="ficti"/>
                <year>2011</year>
                <wordcount>15</wordcount>
            </header>
                <body>
                    <p>
                        Lev lähkám Skánen,
                        <errorort correct="Evenskjeran" errorinfo="vowm,á-a">
                            Evenskjerán
                        </errorort>
                        Sáme
                        <errorort correct="gilppusijn" errorinfo="infl">
                            gilppojn
                        </errorort>
                        ja lev aj dán vahko lähkám
                        <errorort
                            correct="&quot;hárjjidallamskåvlån&quot;"
                            errorinfo="conc,rj-rjj;cmp,2-X">
                                hárjidallam-"skåvlån"
                        </errorort>
                        <errorort correct="tjuojggusijn" errorinfo="vowlat,o-u">
                            tjuojggosijn
                        </errorort>.
                    </p>
                </body>
            </document>
        '''
        got = etree.fromstring(want_string)

        c = converter.PlaintextConverter('orig/sme/admin/blogg_5.correct.txt')
        c.md = xslsetter.MetadataHandler(c.names.xsl, create=True)
        c.md.set_variable('conversion_status', 'correct')
        c.fix_document(got)

        self.assertXmlEqual(got, etree.fromstring(want_string))


class TestDocConverter(XMLTester):

    def setUp(self):
        self.testdoc = converter.DocConverter(
            os.path.join(
                here, 'converter_data/fakecorpus/orig/sme/riddu/doc-test.doc'),
            'bogus')

    def test_convert2intermediate(self):
        got = self.testdoc.convert2intermediate()
        want = etree.parse(
            os.path.join(here,
                         'converter_data/doc-test.xml'))

        self.assertXmlEqual(got, want)


class TestDocxConverter(XMLTester):

    def setUp(self):
        self.testdoc = converter.DocxConverter(
            os.path.join(
                here, 'converter_data/fakecorpus/orig/sme/riddu/doc-test.docx'),
            'bogus')

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

        self.assertXmlEqual(got, etree.fromstring(want))


class TestEpubConverter(XMLTester):
    """Test the epub converter."""

    def setUp(self):
        self.testdoc = converter.EpubConverter(
            os.path.join(
                here, 'converter_data/fakecorpus/orig/sme/riddu/test.epub'),
            'bogus')

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

    def test_convert2intermediate(self):
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

    def test_convert2intermediate_with_skip_elements(self):
        """Test with skip_elements."""
        self.testdoc.md.set_variable(
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
        self.testdoc = converter.EpubConverter(
            os.path.join(
                here, 'converter_data/fakecorpus/orig/sme/riddu/test2.epub'),
            'bogus')

    def test_convert2intermediate(self):
        """Range of same depth, with the same name in the next to last level."""
        self.testdoc.md.set_variable(
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
        self.testdoc.md.set_variable(
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
            document_fixer = converter.DocumentFixer(etree.fromstring(u'''
                <document>
                    <header/>
                    <body>
                        <p>''' + key + u'''</p>
                    </body>
                </document>
            '''))
            document_fixer.insert_spaces_after_semicolon()
            got = document_fixer.get_etree()
            want = etree.fromstring(u'''
                <document>
                    <header/>
                    <body>
                        <p>''' + value + u'''</p>
                    </body>
                </document>
            ''')

            self.assertXmlEqual(got, want)

    def test_fix_newstags_bold_1(self):
        """Test conversion of the @bold: newstag."""
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

        self.assertXmlEqual(got, want)

    def test_fix_newstags_bold_2(self):
        """Test conversion of the @bold: newstag."""
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

        self.assertXmlEqual(got, want)

    def test_fix_newstags_bold_3(self):
        """Test conversion of the @bold: newstag."""
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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

    def test_tekst_6(self):
        document_fixer = converter.DocumentFixer(etree.fromstring(
            '<document>'
            '   <header/>'
            '   <body>'
            '       <p>Ê@tekst:ii</p>'
            '   </body>'
            '</document>'))
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            '<document>'
            '   <header/>'
            '   <body>'
            '       <p>ii</p>'
            '   </body>'
            '</document>')

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

    def test_fix_newstags_4(self):
        """Check that p attributes are kept."""
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

        self.assertXmlEqual(got, want)

    def test_fix_body_encoding(self):
        newstext = converter.PlaintextConverter(
            'orig/sme/riddu/tullball.txt', LANGUAGEGUESSER)
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
        document_fixer.fix_body_encoding('sme')
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

        self.assertXmlEqual(got, want)

    def test_replace_ligatures(self):
        svgtext = converter.SVGConverter(
            os.path.join(here,
                         'converter_data/fakecorpus/orig/sme/riddu/'
                         'Riddu_Riddu_avis_TXT.200923.svg'),
            LANGUAGEGUESSER)
        document_fixer = converter.DocumentFixer(
            etree.fromstring(etree.tostring(svgtext.convert2intermediate())))
        document_fixer.fix_body_encoding('sme')
        got = document_fixer.get_etree()

        want = etree.parse(
            os.path.join(here,
                         'converter_data/Riddu_Riddu_avis_TXT.200923.xml'))

        self.assertXmlEqual(got, want)

    #def test_word_count(self):
        #document = (
            #'<document xml:lang="sma" id="no_id"><header><title/><genre/>'
            #'<author><unknown/></author><availability><free/>'
            #'</availability><multilingual/></header><body><p>Bïevnesh '
            #'naasjovnalen pryövoej bïjre</p><p>2008</p><p>Bïevnesh '
            #'eejhtegidie, tjidtjieh aehtjieh bielide naasjovnalen '
            #'pryövoej bïjre giej leah maanah 5. jïh 8. '
            #'tsiehkine</p></body></document>')
        #if six.PY3:
            #document = document.encode('utf8')
        #orig_doc = etree.parse(
            #io.BytesIO(document))

        #expected_doc = (
            #'<document xml:lang="sma" id="no_id"><header><title/><genre/>'
            #'<author><unknown/></author><wordcount>20</wordcount>'
            #'<availability><free/></availability><multilingual/></header>'
            #'<body><p>Bïevnesh naasjovnalen pryövoej bïjre</p>'
            #'<p>2008</p><p>Bïevnesh eejhtegidie, tjidtjieh aehtjieh bielide '
            #'naasjovnalen pryövoej bïjre giej leah maanah 5. jïh 8. '
            #'tsiehkine</p></body></document>')

        #document_fixer = converter.DocumentFixer(orig_doc)
        #document_fixer.set_word_count()

        #self.assertXmlEqual(document_fixer.root,
                            #etree.fromstring(expected_doc))

    def test_replace_shy1(self):
        document = (
            '<document xml:lang="sma" id="no_id"><header><title/><genre/>'
            '<author><unknown/></author><availability><free/>'
            '</availability><multilingual/></header><body><p>a­b­c'
            '<span>d­e</span>f­g</p></body></document>')
        if six.PY3:
            document = document.encode('utf8')
        orig_doc = etree.parse(
            io.BytesIO(document))

        expected_doc = (
            '<document xml:lang="sma" id="no_id"><header><title/><genre/>'
            '<author><unknown/></author><availability><free/></availability>'
            '<multilingual/></header><body><p>a<hyph/>b<hyph/>c<span>d<hyph/>'
            'e</span>f<hyph/>g</p></body></document>')

        document_fixer = converter.DocumentFixer(orig_doc)
        document_fixer.soft_hyphen_to_hyph_tag()

        self.assertXmlEqual(document_fixer.root,
                            etree.fromstring(expected_doc))

    def test_replace_shy2(self):
        document = (
            '<document xml:lang="sma" id="no_id">'
            '<header><title/><genre/><author><unknown/></author>'
            '<availability><free/></availability><multilingual/></header>'
            '<body><p>a­b­c<span>d­e</span></p></body></document>')
        if six.PY3:
            document = document.encode('utf8')
        orig_doc = etree.parse(
            io.BytesIO(document))

        expected_doc = (
            '<document xml:lang="sma" id="no_id"><header><title/><genre/>'
            '<author><unknown/></author><availability><free/></availability>'
            '<multilingual/></header><body><p>a<hyph/>b<hyph/>c<span>d'
            '<hyph/>e</span></p></body></document>')

        document_fixer = converter.DocumentFixer(orig_doc)
        document_fixer.soft_hyphen_to_hyph_tag()

        self.assertXmlEqual(document_fixer.root,
                            etree.fromstring(expected_doc))

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

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

        self.assertXmlEqual(got, want)

    def test_fix_sms1(self):
        """\u2019 (’) should be replaced by \u02BC (ʼ)"""
        document_fixer = converter.DocumentFixer(etree.fromstring(
            u'<document xml:lang="sms">'
            u'  <header/>'
            u'  <body>'
            u'     <p>'
            u'       Mätt’temaaunâstuâjj '
            u'     </p>'
            u'  </body>'
            u'</document>'))
        document_fixer.fix_body_encoding('sms')
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

        self.assertXmlEqual(got, want)

    def test_fix_sms2(self):
        """\u0027 (')  should be replaced by \u02BC (ʼ)"""
        document_fixer = converter.DocumentFixer(etree.fromstring(
            u'<document xml:lang="sms">'
            u'  <header/>'
            u'  <body>'
            u'     <p>'
            u"       ǩiõll'laž da kulttuursaž vuõiggâdvuõđi"
            u'     </p>'
            u'  </body>'
            u'</document>'))
        document_fixer.fix_body_encoding('sms')
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

        self.assertXmlEqual(got, want)

    def test_fix_sms3(self):
        """\u2032 (′)  should be replaced by \u02B9 (ʹ)"""
        document_fixer = converter.DocumentFixer(etree.fromstring(
            u'<document xml:lang="sms">'
            u'  <header/>'
            u'  <body>'
            u'     <p>'
            u'       Mon tõzz še njui′ǩǩeem tõ′st dõõzze.'
            u'     </p>'
            u'  </body>'
            u'</document>'))
        document_fixer.fix_body_encoding('sms')
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

        self.assertXmlEqual(got, want)

    def test_fix_sms4(self):
        r"""\u00B4 (´)  should be replaced by \u02B9 (ʹ)"""
        document_fixer = converter.DocumentFixer(etree.fromstring(
            u'<document xml:lang="sms">'
            u'  <header/>'
            u'  <body>'
            u'     <p>'
            u'       Materialbaaŋk čuä´jtumuš'
            u'     </p>'
            u'  </body>'
            u'</document>'))
        document_fixer.fix_body_encoding('sms')
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

        self.assertXmlEqual(got, want)

    def test_fix_sms5(self):
        r"""\u0301 ( ́)  should be replaced by \u02B9 (ʹ)"""
        document_fixer = converter.DocumentFixer(etree.fromstring(
            u'<document xml:lang="sms">'
            u'  <header/>'
            u'  <body>'
            u'     <p>'
            u'       Materialbaaŋk čuä́jtumuš'
            u'     </p>'
            u'  </body>'
            u'</document>'))
        document_fixer.fix_body_encoding('sms')
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

        self.assertXmlEqual(got, want)


class TestXslMaker(XMLTester):

    def test_get_xsl(self):

        xslmaker = converter.XslMaker(
            etree.parse(
                os.path.join(here,
                             'converter_data/samediggi-article-48.html.xsl')))
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
        self.assertXmlEqual(got, want)
