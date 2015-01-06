# -*- coding: utf-8 -*-
import unittest
import codecs
import io
import os
import lxml.etree as etree
import lxml.doctestcompare as doctestcompare
from lxml.html import html5parser
import doctest

from corpustools import converter


here = os.path.dirname(__file__)


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
            self.converter_inside_orig.get_orig(),
            os.path.join(
                here,
                'converter_data/fakecorpus/orig/nob/samediggi-article-'
                '16.html'))

        self.assertEqual(
            self.converter_outside_orig.get_orig(),
            os.path.join(
                here,
                'converter_data/samediggi-article-48.html'))

        self.assertEqual(
            self.converter_inside_freecorpus.get_orig(),
            os.path.join(
                os.getenv('GTFREE'),
                'orig/sme/admin/sd/samediggi.no/samediggi-article-48.html'))

    def test_get_xsl(self):
        self.assertEqual(
            self.converter_inside_orig.get_xsl(),
            os.path.join(
                here,
                'converter_data/fakecorpus/orig/nob/samediggi-'
                'article-16.html.xsl'))

        self.assertEqual(
            self.converter_outside_orig.get_xsl(),
            os.path.join(
                here,
                'converter_data/samediggi-article-48.html.xsl'))

        self.assertEqual(
            self.converter_inside_freecorpus.get_xsl(),
            os.path.join(
                os.getenv('GTFREE'),
                'orig/sme/admin/sd/samediggi.no/samediggi-article-'
                '48.html.xsl'))

    def test_get_tmpdir(self):
        self.assertEqual(
            self.converter_inside_orig.get_tmpdir(),
            os.path.join(
                here,
                'converter_data/fakecorpus/tmp'))

        self.assertEqual(
            self.converter_outside_orig.get_tmpdir(),
            os.path.join(
                here, 'converter_data'))

        self.assertEqual(
            self.converter_inside_freecorpus.get_tmpdir(),
            os.path.join(os.getenv('GTFREE'), 'tmp'))

    def test_get_corpusdir(self):
        self.assertEqual(
            self.converter_inside_orig.get_corpusdir(),
            os.path.join(
                here,
                'converter_data/fakecorpus'))

        self.assertEqual(
            self.converter_outside_orig.get_corpusdir(),
            os.path.join(here, 'converter_data'))

        self.assertEqual(
            self.converter_inside_freecorpus.get_corpusdir(),
            os.getenv('GTFREE'))

    def test_get_converted_name_inside_orig(self):
        self.assertEqual(
            self.converter_inside_orig.get_converted_name(),
            os.path.join(
                here,
                'converter_data/fakecorpus/converted/nob/samediggi-'
                'article-16.html.xml'))

    def test_get_converted_name_outside_orig(self):
        self.assertEqual(
            self.converter_outside_orig.get_converted_name(),
            os.path.join(
                here,
                'converter_data/samediggi-article-48.html.xml'))

    def test_get_converted_inside_freecorpus(self):
        self.assertEqual(
            self.converter_inside_freecorpus.get_converted_name(),
            os.path.join(
                os.getenv('GTFREE'),
                'converted/sme/admin/sd/samediggi.no/samediggi-'
                'article-48.html.xml'))


class XMLTester(unittest.TestCase):
    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal
        """
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(
                doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)


class TestAvvirConverter(XMLTester):
    def setUp(self):
        self.avvir = converter.AvvirConverter('fakename')
        self.avvir.intermediate = etree.fromstring(r'''<article>
    <story id="a" class="Tittel">
        <p>a</p>
    </story>
    <story id="b" class="Undertittel">
        <p>b</p>
    </story>
    <story id="c" class="ingress">
        <p>c</p>
    </story>
    <story id="d" class="body">
        <p class="tekst">d<br/>e<br/></p>
        <p>f</p>
    </story>
    <story id="g" class="body">
        <p class="tekst">h<span>i</span>j</p>
    </story>
    <story id="k" class="body">
        <p>l
            <span>
                m
                <br/>
                n
            </span>
            o
        </p>
    </story>
</article>''')

    def test_convert_p(self):
        want = etree.fromstring(r'''<article>
    <story class="Tittel" id="a">
        <p>a</p>
    </story>
    <story class="Undertittel" id="b">
        <p>b</p>
    </story>
    <story class="ingress" id="c">
        <p>c</p>
    </story>
    <story class="body" id="d">
        <p>d</p>
        <p>e</p>
        <p>f</p>
    </story>
    <story class="body" id="g">
        <p>h</p>
        <p>i</p>
        <p>j</p>
    </story>
    <story class="body" id="k">
        <p>l</p>
        <p>m</p>
        <p>n</p>
        <p>o</p>
    </story>
</article>''')

        self.avvir.convert_p()
        self.assertXmlEqual(
            etree.tostring(self.avvir.intermediate), etree.tostring(want))

    def test_convert_story(self):
        want = etree.fromstring('''<article>
    <section>
        <p type="title">a</p>
    </section>
    <section>
        <p type="title">b</p>
    </section>
    <p>c</p>
    <p>d</p>
    <p>e</p>
    <p>f</p>
    <p>h</p>
    <p>i</p>
    <p>j</p>
    <p>l</p>
    <p>m</p>
    <p>n</p>
    <p>o</p>
</article>''')

        self.avvir.convert_p()
        self.avvir.convert_story()
        self.assertXmlEqual(
            etree.tostring(self.avvir.intermediate), etree.tostring(want))

    def test_convert_article(self):
        want = etree.fromstring('''<document>
    <body>
        <section>
            <p type="title">a</p>
        </section>
        <section>
            <p type="title">b</p>
        </section>
        <p>c</p>
        <p>d</p>
        <p>e</p>
        <p>f</p>
        <p>h</p>
        <p>i</p>
        <p>j</p>
        <p>l</p>
        <p>m</p>
        <p>n</p>
        <p>o</p>
    </body>
</document>''')

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
            '\x0d\n'
            '<ASCII-MAC>\n'
            '<vsn:3.000000>\n'
            '<\!q>\n'
            '<\!h>\n')
        want = u'''\n\n\n\n\n\n'''

        self.assertEqual(got, want)

    def test_strip_chars2(self):
        plaintext = converter.PlaintextConverter(
            'tullball.txt')
        got = plaintext.strip_chars(
            '<0x010C><0x010D><0x0110><0x0111><0x014A><0x014B><0x0160><0x0161>'
            '<0x0166><0x0167><0x017D><0x017E><0x2003>')
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
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>Guovssa<hyph/>hasa</p>
    </body>
</document>
''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))


class TestPDFConverter(XMLTester):
    def test_pdf_converter(self):
        pdfdocument = converter.PDFConverter(
            os.path.join(here, 'converter_data/pdf-test.pdf'))
        got = pdfdocument.convert2intermediate()
        want = etree.parse(
            os.path.join(here, 'converter_data/pdf-test.xml'))

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))


class TestDocConverter(XMLTester):
    def setUp(self):
        self.testdoc = converter.DocConverter(
            os.path.join(here,
                         'converter_data/doc-test.doc'))

    def test_convert2intermediate(self):
        got = self.testdoc.convert2intermediate()
        want = etree.parse(
            os.path.join(here,
                         'converter_data/doc-test.xml'))

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_doc2html1(self):
        '''doc2html should raise an exception when wvHtml fails
        '''
        self.assertRaises(converter.ConversionException,
                          converter.DocConverter, filename='bogus.doc')


class TestBiblexmlConverter(XMLTester):
    def setUp(self):
        self.testdoc = converter.BiblexmlConverter(
            os.path.join(here,
                         'converter_data/bible-test.xml'))

    def test_convert2intermediate(self):
        got = self.testdoc.convert2intermediate()
        want = etree.parse(
            os.path.join(here,
                         'converter_data/bible-test.xml.xml'))

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))


class TestHTMLContentConverter(XMLTester):
    def test_remove_empty_class(self):
        got = converter.HTMLContentConverter(
            'with-o:p.html',
            '<html><body><div class="">a</div><div class="a">'
            '<span class="">b</span></div></html>',
            None).tidy()

        want = html5parser.document_fromstring(
            '<html><head/><body><div>a</div><div class="a">'
            '<span>b</span></div></body></html>')

        self.assertEqual(got, etree.tostring(want))

    def test_remove_unwanted_classes_and_ids(self):
        unwanted_classes_ids = {
            'div': {
                'class': [
                    'QuickNav', 'tabbedmenu', 'printContact', 'documentPaging',
                    'breadcrumbs', 'post-footer', 'documentInfoEm',
                    'article-column', 'nrk-globalfooter', 'article-related',
                    'outer-column', 'article-ad', 'article-bottom-element',
                    'banner-element', 'nrk-globalnavigation', 'sharing', 'ad',
                    'meta', 'authors', 'articleImageRig',  'btm_menu',
                    'expandable'],
                'id': [
                    'searchBox',
                    'murupolku',
                    'ctl00_FullRegion_CenterAndRightRegion_Sorting_sortByDiv',
                    (
                        'ctl00_FullRegion_CenterAndRightRegion_HitsControl_'
                        'searchHitSummary'),
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
            }

        for tag, attribs in unwanted_classes_ids.items():
            for key, values in attribs.items():
                for value in values:
                    hc = converter.HTMLContentConverter(
                        '.html'.format(tag, key, value),
                        ('<html><body><{0} {1}="{2}">content:{0}{1}{2}</{0}>'
                        '<div class="ada"/></body>'
                        '</html>').format(tag, key, value), None)
                    hc.remove_elements()

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
                (
                    '<html><body><p>p1</p><%s/><p>p2</p2></body>'
                    '</html>' % unwanted_tag
                ), None).tidy()
            want = (
                '<html:html xmlns:html="http://www.w3.org/1999/xhtml">'
                '<html:head/><html:body><html:p>p1</html:p><html:p>p2'
                '</html:p></html:body></html:html>')

            self.assertEqual(got, want)

    def test_remove_comment(self):
        got = converter.HTMLContentConverter(
            'with-o:p.html',
            '<html><body><b><!--Hey, buddy. --></b></body></html>',
            None).tidy()

        want = (
            '<html:html xmlns:html="http://www.w3.org/1999/xhtml"><html:head/>'
            '<html:body><html:b/></html:body></html:html>')

        self.assertEqual(got, want)

    def test_remove_processinginstruction(self):
        got = converter.HTMLContentConverter(
            'with-o:p.html',
            '<html><body><b><?ProcessingInstruction?></b></body></html>',
            None).tidy()

        want = (
            '<html:html xmlns:html="http://www.w3.org/1999/xhtml">'
            '<html:head/><html:body><html:b/></html:body></html:html>')

        self.assertEqual(got, want)

    def test_add_p_around_text1(self):
        '''Only text before next significant element
        '''
        hcc = converter.HTMLContentConverter(
            'withoutp.html',
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN">'
            '<html><head><meta http-equiv="Content-type" content="text/html; '
            'charset=utf-8"><title>– Den utdøende stammes frykt</title>'
            '</head><body><h3>VI</h3>... Finnerne<p>Der</body></html>', None)
        hcc.add_p_around_text()

        want = (
            '<?xml version="1.0"?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML '
            '1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1'
            '-strict.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><head>'
            '<title>– Den utdøende stammes frykt</title></head><body>'
            '<h3>VI</h3>  <p>... Finnerne</p><p>Der</p></body></html>')

        self.assertXmlEqual(etree.tostring(hcc.soup), want)

    def test_add_p_around_text2(self):
        '''Text and i element before next significant element
        '''
        hcc = converter.HTMLContentConverter(
            'withoutp.html',
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN">'
            '<html><head><meta http-equiv="Content-type" content="text/html; '
            'charset=utf-8"><title>– Den utdøende stammes frykt</title>'
            '</head><body><h3>VI</h3>... Finnerne<i>Der</body></html>', None)
        hcc.add_p_around_text()

        want = (
            '<?xml version="1.0"?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML '
            '1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-'
            'strict.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><head>'
            '<title>– Den utdøende stammes frykt</title></head><body>'
            '<h3>VI</h3>  <p>... Finnerne<i>Der</i></p></body></html>')

        self.assertXmlEqual(etree.tostring(hcc.soup), want)

    def test_add_p_around_text3(self):
        '''h2 as a stop element
        '''
        hcc = converter.HTMLContentConverter(
            'withoutp.html',
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN"><html>'
            '<head><meta http-equiv="Content-type" content="text/html; '
            'charset=utf-8"><title>– Den utdøende stammes frykt</title>'
            '</head><body><h3>VI</h3>... Finnerne<a/>'
            '<h2>Der</h2></body></html>', None)
        hcc.add_p_around_text()

        want = (
            '<?xml version="1.0"?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML '
            '1.0 Strict//EN" '
            '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
            '<html xmlns="http://www.w3.org/1999/xhtml"><head><title>– Den '
            'utdøende stammes frykt</title>  </head><body>  <h3>VI</h3>  '
            '<p>... Finnerne<a/></p><h2>Der</h2></body></html>')

        self.assertXmlEqual(etree.tostring(hcc.soup), want)

    def test_set_charset_1(self):
        '''Check that default charset is set, 1
        encoding_from_xsl = None, no charset in html header
        '''
        content = (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN"><html>'
            '<body></body></html>')
        encoding_from_xsl = None

        hcc = converter.HTMLContentConverter(
            'ugga.html',
            content, encoding_from_xsl)

        got = hcc.set_charset(content, encoding_from_xsl)

        self.assertEqual(got, 'utf-8')

    def test_set_charset_2(self):
        '''Check that default charset is set, 2
        encoding_from_xsl = '', no charset in html header
        '''
        content = (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN"><html>'
            '<body></body></html>')
        encoding_from_xsl = ''

        hcc = converter.HTMLContentConverter(
            'ugga.html',
            content, encoding_from_xsl)

        got = hcc.set_charset(content, encoding_from_xsl)

        self.assertEqual(got, 'utf-8')

    def test_set_charset_3(self):
        '''encoding_from_xsl = 'iso-8859-1', no charset in html header
        '''
        content = (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN"><html>'
            '<body></body></html>')
        encoding_from_xsl = 'iso-8859-1'

        hcc = converter.HTMLContentConverter(
            'ugga.html',
            content, encoding_from_xsl)

        got = hcc.set_charset(content, encoding_from_xsl)

        self.assertEqual(got, 'windows-1252')

    def test_set_charset_4(self):
        '''Check that encoding_from_xsl overrides meta charset
        encoding_from_xsl = 'iso-8859-1', charset in html header = utf-8
        '''
        content = (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN"><html>'
            '<head><meta http-equiv="Content-type" content="text/html; '
            'charset=utf-8"></head><body></body></html>')

        encoding_from_xsl = 'iso-8859-1'

        hcc = converter.HTMLContentConverter(
            'ugga.html',
            content, encoding_from_xsl)

        got = hcc.set_charset(content, encoding_from_xsl)

        self.assertEqual(got, 'windows-1252')

    def test_set_charset_5(self):
        '''encoding_from_xsl = None, charset in html header = iso-8859-1
        '''
        content = (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN"><html>'
            '<head><meta http-equiv="Content-type" content="text/html; '
            'charset=iso-8859-1"></head><body></body></html>')

        encoding_from_xsl = None

        hcc = converter.HTMLContentConverter(
            'ugga.html',
            content, encoding_from_xsl)

        got = hcc.set_charset(content, encoding_from_xsl)

        self.assertEqual(got, 'windows-1252')

    def test_set_charset_6(self):
        '''encoding_from_xsl = '', charset in html header = iso-8859-1
        '''
        content = (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN"><html>'
            '<head><meta http-equiv="Content-type" content="text/html; '
            'charset=iso-8859-1"></head><body></body></html>')

        encoding_from_xsl = ''

        hcc = converter.HTMLContentConverter(
            'ugga.html',
            content, encoding_from_xsl)

        got = hcc.set_charset(content, encoding_from_xsl)

        self.assertEqual(got, 'windows-1252')

    def test_set_charset_7(self):
        '''Test if set_charset works with ' as quote mark around charset
        encoding_from_xsl = '', charset in html header = iso-8859-1
        '''
        content = (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN"><html>'
            '<head><meta http-equiv="Content-type" content=\'text/html; '
            'charset=iso-8859-1\'></head><body></body></html>')

        encoding_from_xsl = ''

        hcc = converter.HTMLContentConverter(
            'ugga.html',
            content, encoding_from_xsl)

        got = hcc.set_charset(content, encoding_from_xsl)

        self.assertEqual(got, 'windows-1252')

    def test_set_charset_8(self):
        '''Test if set_charset works with ' as quote mark around charset when
        " is found later
        encoding_from_xsl = '', charset in html header = iso-8859-1
        '''
        content = (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN"><html>'
            '<head><meta http-equiv="Content-type" content=\'text/html; '
            'charset=iso-8859-1\'><link rel="index.html"></head><body>'
            '</body></html>')

        encoding_from_xsl = ''

        hcc = converter.HTMLContentConverter(
            'ugga.html',
            content, encoding_from_xsl)

        got = hcc.set_charset(content, encoding_from_xsl)

        self.assertEqual(got, 'windows-1252')

    def test_set_charset_9(self):
        '''Test if set_charset works with " as quote mark around charset
        when ' is found later
        encoding_from_xsl = '', charset in html header = iso-8859-1
        '''
        content = (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN"><html>'
            '<head><meta http-equiv="Content-type" content="text/html; '
            'charset=iso-8859-1"><link rel=\'index.html\'></head><body>'
            '</body></html>')

        encoding_from_xsl = ''

        hcc = converter.HTMLContentConverter(
            'ugga.html',
            content, encoding_from_xsl)

        got = hcc.set_charset(content, encoding_from_xsl)

        self.assertEqual(got, 'windows-1252')

    def test_center2div(self):
        got = converter.HTMLContentConverter(
            'center.html',
            '<html><body><center><span class="">b</span></center></html>',
            None).tidy()

        want = html5parser.document_fromstring(
            '<html><head/><body><div class="c1"><span>b</span></div></body>'
            '</html>')

        self.assertEqual(got, etree.tostring(want))

    def test_body_i(self):
        got = converter.HTMLContentConverter(
            'i.html',
            '<html><body><i>b</i></body></html>', None).tidy()

        want = html5parser.document_fromstring(
            '<html><head/><body><p><i>b</i></p></body></html>')

        self.assertEqual(got, etree.tostring(want))

    def test_body_a(self):
        got = converter.HTMLContentConverter(
            'a.html',
            '<html><body><a>b</a></body></html>', None).tidy()

        want = html5parser.document_fromstring(
            '<html><head/><body><p><a>b</a></p></body></html>')

        self.assertEqual(got, etree.tostring(want))

    def test_body_em(self):
        got = converter.HTMLContentConverter(
            'em.html',
            '<html><body><em>b</em></body></html>', None).tidy()

        want = html5parser.document_fromstring(
            '<html><head/><body><p><em>b</em></p></body></html>')

        self.assertEqual(got, etree.tostring(want))

    def test_body_font(self):
        got = converter.HTMLContentConverter(
            'font.html',
            '<html><body><font>b</font></body></html>', None).tidy()

        want = html5parser.document_fromstring(
            '<html><head/><body><p><font>b</font></p></body></html>')

        self.assertEqual(got, etree.tostring(want))

    def test_body_u(self):
        got = converter.HTMLContentConverter(
            'u.html',
            '<html><body><u>b</u></body></html>', None).tidy()

        want = html5parser.document_fromstring(
            '<html><head/><body><p><u>b</u></p></body></html>')

        self.assertEqual(got, etree.tostring(want))

    def test_body_strong(self):
        got = converter.HTMLContentConverter(
            'strong.html',
            '<html><body><strong>b</strong></body></html>', None).tidy()

        want = html5parser.document_fromstring(
            '<html><head/><body><p><strong>b</strong></p></body></html>')

        self.assertEqual(got, etree.tostring(want))

    def test_body_span(self):
        got = converter.HTMLContentConverter(
            'span.html',
            '<html><body><span>b</span></body></html>', None).tidy()

        want = html5parser.document_fromstring(
            '<html><head/><body><p><span>b</span></p></body></html>')

        self.assertEqual(got, etree.tostring(want))

    def test_body_text(self):
        got = converter.HTMLContentConverter(
            'text.html',
            '<html><body>b</body></html>', None).tidy()

        want = html5parser.document_fromstring(
            '<html><head/><body><p>b</p></body></html>')

        self.assertEqual(got, etree.tostring(want))


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
        '''Check if irritating words followed by semi colon are
        handled correctly
        '''
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
        '''Test conversion of the @bold: newstag
        '''
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
        '''Test conversion of the @bold: newstag
        '''
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
        '''Test conversion of the @bold: newstag
        '''
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

    def test_fix__body_encoding(self):
        newstext = converter.PlaintextConverter(
            'tullball.txt')
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
                         'converter_data/Riddu_Riddu_avis_TXT.200923.svg'))
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

        self.assertXmlEqual(etree.tostring(document_fixer.etree), expected_doc)

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

        self.assertXmlEqual(etree.tostring(document_fixer.etree), expected_doc)

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

        self.assertXmlEqual(etree.tostring(document_fixer.etree), expected_doc)

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


class TestXslMaker(XMLTester):
    def test_get_xsl(self):
        xslmaker = converter.XslMaker(
            os.path.join(here,
                         'converter_data/samediggi-article-48.html.xsl'))
        got = xslmaker.get_xsl()

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


class TestLanguageDetector(XMLTester):
    """
    Test the functionality of LanguageDetector
    """
    def setUp(self):
        self.document = etree.parse(
            os.path.join(here,
                         'converter_data/samediggi-article-48s-before-lang-'
                         'detection-with-multilingual-tag.xml'))

    def test_get_main_lang(self):
        test_main_lang = 'sme'
        language_detector = converter.LanguageDetector(self.document)
        self.assertEqual(test_main_lang, language_detector.get_mainlang())

    def test_set_paragraph_language_preset_language(self):
        orig_paragraph = '<p xml:lang="sme">I Orohagat</p>'
        expected_paragraph = '<p xml:lang="sme">I Orohagat</p>'

        language_detector = converter.LanguageDetector(self.document)
        got_paragraph = language_detector.set_paragraph_language(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_set_paragraph_language_mainlanguage(self):
        orig_paragraph = (
            '<p>Sámegiella lea 2004 čavčča rájes standárda giellaválga '
            'Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša ahte '
            'sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. '
            'Buot leat dás dán fitnodaga Service Pack 2-páhkas, maid ferte '
            'viežžat ja bidjat dihtorii. Boađus lea ahte buot boahttevaš '
            'Microsoft prográmmat dorjot sámegiela. Dattetge sáhttet '
            'deaividit váttisvuođat go čálát sámegiela Outlook-kaleandaris '
            'dahje e-poastta namahussajis, ja go čálát sámegillii dakkár '
            'prográmmain, maid Microsoft ii leat ráhkadan.</p>')
        expected_paragraph = (
            '<p>Sámegiella lea 2004 čavčča rájes standárda giellaválga '
            'Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša ahte '
            'sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. '
            'Buot leat dás dán fitnodaga Service Pack 2-páhkas, maid ferte '
            'viežžat ja bidjat dihtorii. Boađus lea ahte buot boahttevaš '
            'Microsoft prográmmat dorjot sámegiela. Dattetge sáhttet '
            'deaividit váttisvuođat go čálát sámegiela Outlook-kaleandaris '
            'dahje e-poastta namahussajis, ja go čálát sámegillii dakkár '
            'prográmmain, maid Microsoft ii leat ráhkadan.</p>')

        language_detector = converter.LanguageDetector(self.document)
        got_paragraph = language_detector.set_paragraph_language(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_set_paragraph_language_mainlanguage_quote_mainlang(self):
        orig_paragraph = (
            '<p>Sámegiella lea 2004 čavčča rájes standárda giellaválga '
            'Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša ahte '
            'sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. '
            '<span type="quote">«Buot leat dás dán fitnodaga Service Pack 2-'
            'páhkas, maid ferte viežžat ja bidjat dihtorii»</span>. Boađus '
            'lea ahte buot boahttevaš Microsoft prográmmat dorjot sámegiela. '
            'Dattetge sáhttet deaividit váttisvuođat go čálát sámegiela '
            'Outlook-kaleandaris dahje e-poastta namahussajis, ja go čálát '
            'sámegillii dakkár prográmmain, maid Microsoft ii leat '
            'ráhkadan.</p>')
        expected_paragraph = (
            '<p>Sámegiella lea 2004 čavčča rájes standárda giellaválga '
            'Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša ahte '
            'sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. '
            '<span type="quote">«Buot leat dás dán fitnodaga Service Pack 2-'
            'páhkas, maid ferte viežžat ja bidjat dihtorii»</span>. Boađus '
            'lea ahte buot boahttevaš Microsoft prográmmat dorjot sámegiela. '
            'Dattetge sáhttet deaividit váttisvuođat go čálát sámegiela '
            'Outlook-kaleandaris dahje e-poastta namahussajis, ja go čálát '
            'sámegillii dakkár prográmmain, maid Microsoft ii leat '
            'ráhkadan.</p>')

        language_detector = converter.LanguageDetector(self.document)
        got_paragraph = language_detector.set_paragraph_language(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_set_paragraph_language_mainlanguage_quote_not_mainlang(self):
        orig_paragraph = (
            '<p>Sámegiella lea 2004 čavčča rájes standárda giellaválga '
            'Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša ahte '
            'sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. '
            '<span type="quote">«Alt finnes i den foreliggende Service Pack 2 '
            'fra selskapet, som må lastes ned og installeres på din '
            'datamaskin. Konsekvensen er at all framtidig programvare fra '
            'Microsoft vil inneholde støtte for samisk»</span>. Boađus lea '
            'ahte buot boahttevaš Microsoft prográmmat dorjot sámegiela. '
            'Dattetge sáhttet deaividit váttisvuođat go čálát sámegiela '
            'Outlook-kaleandaris dahje e-poastta namahussajis, ja go čálát '
            'sámegillii dakkár prográmmain, maid Microsoft ii leat '
            'ráhkadan.</p>')
        expected_paragraph = (
            '<p>Sámegiella lea 2004 čavčča rájes standárda giellaválga '
            'Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša ahte '
            'sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. '
            '<span type="quote" xml:lang="nob">«Alt finnes i den foreliggende '
            'Service Pack 2 fra selskapet, som må lastes ned og installeres '
            'på din datamaskin. Konsekvensen er at all framtidig programvare '
            'fra Microsoft vil inneholde støtte for samisk»</span>. Boađus '
            'lea ahte buot boahttevaš Microsoft prográmmat dorjot sámegiela. '
            'Dattetge sáhttet deaividit váttisvuođat go čálát sámegiela '
            'Outlook-kaleandaris dahje e-poastta namahussajis, ja go čálát '
            'sámegillii dakkár prográmmain, maid Microsoft ii leat '
            'ráhkadan.</p>')

        language_detector = converter.LanguageDetector(self.document)
        got_paragraph = language_detector.set_paragraph_language(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_set_paragraph_language_not_mainlanguage(self):
        orig_paragraph = (
            '<p>Samisk er fra høsten 2004 et standard språkvalg Microsofts '
            'operativsystem Windows XP. I praksis betyr det at samiske '
            'bokstaver og formater kan velges i alle programmer. Alt finnes '
            'i den foreliggende Service Pack 2 fra selskapet, som må lastes '
            'ned og installeres på din datamaskin. Konsekvensen er at all '
            'framtidig programvare fra Microsoft vil inneholde støtte for '
            'samisk. Du vil imidlertid fremdeles kunne oppleve problemer med '
            'å skrive samisk i Outlook-kalenderen eller i tittel-feltet i '
            'e-post, og med å skrive samisk i programmer levert av andre enn '
            'Microsoft.</p>')

        language_detector = converter.LanguageDetector(self.document)
        got_paragraph = language_detector.set_paragraph_language(
            etree.fromstring(orig_paragraph))

        self.assertEqual(
            got_paragraph.get('{http://www.w3.org/XML/1998/namespace}lang'),
            'nob')

    def test_remove_quote(self):
        orig_paragraph = (
            '<p>bla bla <span type="quote">bla1 bla</span> ble ble '
            '<span type="quote">bla2 bla</span> <b>bli</b> bli '
            '<span type="quote">bla3 bla</span> blo blo</p>')
        expected_paragraph = 'bla bla  ble ble  bli bli  blo blo'

        language_detector = converter.LanguageDetector(self.document)
        got_paragraph = language_detector.remove_quote(
            etree.fromstring(orig_paragraph))

        self.assertEqual(got_paragraph, expected_paragraph)

    def test_detect_language_with_multilingualtag(self):
        language_detector = converter.LanguageDetector(
            etree.parse(
                os.path.join(here,
                             'converter_data/samediggi-article-48s-before-'
                             'lang-detection-with-multilingual-tag.xml')))
        language_detector.detect_language()
        got_document = language_detector.get_document()

        expected_document = etree.parse(
            os.path.join(here,
                         'converter_data/samediggi-article-48s-after-lang-'
                         'detection-with-multilingual-tag.xml'))

        self.assertXmlEqual(etree.tostring(got_document),
                            etree.tostring(expected_document))

    def test_detect_language_without_multilingualtag(self):
        language_detector = converter.LanguageDetector(etree.parse(
            os.path.join(here,
                         'converter_data/samediggi-article-48s-before-lang-'
                         'detection-without-multilingual-tag.xml')))
        language_detector.detect_language()
        got_document = language_detector.get_document()

        expected_document = etree.parse(
            os.path.join(here,
                         'converter_data/samediggi-article-48s-after-lang-'
                         'detection-without-multilingual-tag.xml'))

        self.assertXmlEqual(etree.tostring(got_document),
                            etree.tostring(expected_document))


class TestPDF2XMLConverter(XMLTester):
    '''Test the class that converts from pdf2xml to giellatekno/divvun xml
    '''
    def test_extract_textelement1(self):
        '''Extract text from a plain pdf2xml text element
        '''
        p2x = converter.PDF2XMLConverter()

        input = etree.fromstring(
            '<text top="649" left="545" width="269" height="14" font="20">'
            'berret bargat. </text>')
        p2x.extract_textelement(input)
        self.assertEqual(p2x.parts, [u'berret bargat. '])

    def test_extract_textelement2(self):
        '''Extract text from a pdf2xml text element with width less than 1
        '''
        p2x = converter.PDF2XMLConverter()

        input = etree.fromstring(
            '<text top="649" left="545" width="0" height="14" font="20">'
            'berret bargat. </text>')
        p2x.extract_textelement(input)
        self.assertEqual(p2x.parts, [])

    def test_extract_textelement3(self):
        '''Extract text from a pdf2xml text that contains an <i> element
        '''
        p2x = converter.PDF2XMLConverter()

        input = etree.fromstring(
            '<text top="829" left="545" width="275" height="14" font="29">'
            '<i>Ei </i></text>')
        p2x.extract_textelement(input)
        self.assertEqual(
            etree.tostring(p2x.parts[0], encoding='unicode'),
            u'<em type="italic">Ei </em>')

    def test_extract_textelement4(self):
        '''Extract text from a pdf2xml text that contains a <b> element
        '''
        p2x = converter.PDF2XMLConverter()

        input = etree.fromstring(
            '<text top="829" left="545" width="275" height="14" font="29">'
            '<b>Ei </b></text>')
        p2x.extract_textelement(input)
        self.assertEqual(
            etree.tostring(p2x.parts[0], encoding='unicode'),
            u'<em type="bold">Ei </em>')

    def test_extract_textelement5(self):
        '''Extract text from a pdf2xml text that contains a <b> element
        inside the <i> element
        '''
        p2x = converter.PDF2XMLConverter()

        input = etree.fromstring(
            '<text top="829" left="545" width="275" height="14" font="29">'
            '<i><b>Eiš </b></i></text>')
        p2x.extract_textelement(input)

        self.assertEqual(
            etree.tostring(p2x.parts[0], encoding='unicode'),
            u'<em type="italic">Eiš </em>')

    def test_extract_textelement6(self):
        '''Extract text from a pdf2xml text that contains a <b> element
        including a tail
        '''
        p2x = converter.PDF2XMLConverter()

        input = etree.fromstring(
            '<text top="829" left="545" width="275" height="14" font="29">'
            '<b>E</b> a</text>')
        p2x.extract_textelement(input)
        self.assertEqual(
            etree.tostring(p2x.parts[0], encoding='unicode'),
            u'<em type="bold">E</em> a')

    def test_extract_textelement7(self):
        '''Extract text from a pdf2xml text that contains two <i> elements
        '''
        p2x = converter.PDF2XMLConverter()

        input = etree.fromstring(
            '<text top="829" left="545" width="275" height="14" font="29">'
            '<i>E</i> a <i>b</i></text>')
        p2x.extract_textelement(input)

        self.assertEqual(len(p2x.parts), 2)
        self.assertEqual(
            etree.tostring(p2x.parts[0], encoding='unicode'),
            u'<em type="italic">E</em> a ')
        self.assertEqual(
            etree.tostring(p2x.parts[1], encoding='unicode'),
            u'<em type="italic">b</em>')

    def test_extract_textelement8(self):
        '''Extract text from a pdf2xml text that contains one <i> element
        with several <b> elements
        '''
        p2x = converter.PDF2XMLConverter()

        input = etree.fromstring(
            '<text top="837" left="57" width="603" height="11" font="7">'
            '<i><b>Å.</b> B <b>F.</b> A </i></text>')
        p2x.extract_textelement(input)

        self.assertEqual(
            etree.tostring(p2x.parts[0], encoding='unicode'),
            u'<em type="italic">Å. B F. A </em>')

    def test_extract_textelement9(self):
        '''Extract text from a pdf2xml text that contains one <b> element
        with several <i> elements
        '''
        p2x = converter.PDF2XMLConverter()

        input = etree.fromstring(
            '<text top="837" left="57" width="603" height="11" font="7">'
            '<b><i>Å.</i> B <i>F.</i> A </b></text>')
        p2x.extract_textelement(input)

        self.assertEqual(
            etree.tostring(p2x.parts[0], encoding='unicode'),
            u'<em type="bold">Å. B F. A </em>')

    def test_extract_textelement10(self):
        '''Extract text from a pdf2xml text that contains a string with a
        hyphen at the end.
        '''
        p2x = converter.PDF2XMLConverter()

        input = etree.fromstring(
            '<text top="215" width="51" height="14">R-</text>')
        p2x.extract_textelement(input)

        self.assertEqual(p2x.parts[0], u'R')
        self.assertXmlEqual(etree.tostring(p2x.parts[1]), u'<hyph/>')

    def test_extract_textelement11(self):
        '''Extract text from a pdf2xml text that contains a string with a
        hyphen at the end contained in a <b> element.
        '''
        p2x = converter.PDF2XMLConverter()

        input = etree.fromstring(
            '<text top="215" width="51" height="14"><b>R-</b></text>')
        p2x.extract_textelement(input)

        self.assertXmlEqual(
            etree.tostring(p2x.parts[0]), u'<em type="bold">R<hyph/></em>')

    def test_extract_textelement12(self):
        '''Extract text from a pdf2xml text that contains a string with a
        hyphen at the end contained in a <i> element.
        '''
        p2x = converter.PDF2XMLConverter()

        input = etree.fromstring(
            '<text top="215" width="51" height="14"><i>R-</i></text>')
        p2x.extract_textelement(input)

        self.assertXmlEqual(
            etree.tostring(p2x.parts[0]), u'<em type="italic">R<hyph/></em>')

    def test_extract_textelement13(self):
        '''Extract text from a pdf2xml text that contains a string with a
        hyphen at the end contained in a <i> contained in a <b> element.
        '''
        p2x = converter.PDF2XMLConverter()

        input = etree.fromstring(
            '<text top="215" width="51" height="14"><i><b>R-</b></i></text>')
        p2x.extract_textelement(input)

        self.assertXmlEqual(
            etree.tostring(p2x.parts[0]), u'<em type="italic">R<hyph/></em>')

    def test_extract_textelement14(self):
        '''Extract text from a pdf2xml text that contains a string with a
        hyphen at the end contained in a <b> contained in a <i> element.
        '''
        p2x = converter.PDF2XMLConverter()

        input = etree.fromstring(
            '<text top="215" width="51" height="14"><b><i>R-</i></b></text>')
        p2x.extract_textelement(input)

        self.assertXmlEqual(
            etree.tostring(p2x.parts[0]), u'<em type="bold">R<hyph/></em>')

    def test_make_paragraph_1(self):
        '''Pass a parts list consisting of only strings
        '''
        p2x = converter.PDF2XMLConverter()
        p2x.parts = ['a b c ']

        self.assertXmlEqual(
            etree.tostring(p2x.make_paragraph()),
            '<p>a b c </p>')

    def test_make_paragraph_2(self):
        '''Pass a parts list consisting of some strings and some etree.Elements
        '''
        p2x = converter.PDF2XMLConverter()
        p2x.parts = ['a b', etree.Element('em'), etree.Element('em')]

        self.assertXmlEqual(
            etree.tostring(p2x.make_paragraph()), '<p>a b<em/><em/></p>')

    def test_make_paragraph_3(self):
        '''Pass a parts list consisting of a string, a hyph element and another string.
        '''
        p2x = converter.PDF2XMLConverter()
        p2x.parts = ['a ', etree.Element('hyph'), ' c']

        self.assertXmlEqual(
            etree.tostring(p2x.make_paragraph()), '<p>a<hyph/>c</p>')

    def test_make_paragraph_4(self):
        '''Test if two "equal" em elements are joined when the first ends
        with a hyph element
        '''
        em1 = etree.Element('em')
        em1.set('type', 'bold')
        em1.text = 'a'
        em1.append(etree.Element('hyph'))

        em2 = etree.Element('em')
        em2.set('type', 'bold')
        em2.text = 'b'

        p2x = converter.PDF2XMLConverter()
        p2x.parts = [em1, em2]

        self.assertXmlEqual(
            etree.tostring(p2x.make_paragraph()),
            '<p><em type="bold">a<hyph/>b</em></p>')

    def test_make_paragraph_5(self):
        '''Test if two "unequal" em elements are joined when the first ends
        with a hyph element
        '''
        em1 = etree.Element('em')
        em1.set('type', 'italic')
        em1.text = 'a'
        em1.append(etree.Element('hyph'))

        em2 = etree.Element('em')
        em2.set('type', 'bold')
        em2.text = 'b'

        p2x = converter.PDF2XMLConverter()
        p2x.parts = [em1, em2]

        self.assertXmlEqual(
            etree.tostring(p2x.make_paragraph()),
            '<p><em type="italic">a<hyph/></em><em type="bold">b</em></p>')

    def test_is_same_paragraph_1(self):
        '''Test if two text elements belong to the same paragraph
        when the x distance between the two elements is less than
        1.5 times the height of them both.
        '''
        p2x = converter.PDF2XMLConverter()

        t1 = etree.fromstring('<text top="106" height="19" font="2"/>')
        t2 = etree.fromstring('<text top="126" height="19" font="2"/>')

        self.assertTrue(p2x.is_same_paragraph(t1, t2))

    def test_is_same_paragraph_2(self):
        '''Test if two text elements belong to the same paragraph
        when the x distance between the two elements is larger than
        1.5 times the height of them both.
        '''
        p2x = converter.PDF2XMLConverter()

        t1 = etree.fromstring('<text top="106" height="19" font="2"/>')
        t2 = etree.fromstring('<text top="140" height="19" font="2"/>')

        self.assertFalse(p2x.is_same_paragraph(t1, t2))

    def test_is_same_paragraph_3(self):
        '''Test if two text elements belong to the same paragraph
        when they have different heights
        '''
        p2x = converter.PDF2XMLConverter()

        t1 = etree.fromstring('<text top="106" height="19" font="2"/>')
        t2 = etree.fromstring('<text top="126" height="20" font="2"/>')

        self.assertFalse(p2x.is_same_paragraph(t1, t2))

    def test_is_same_paragraph_4(self):
        '''Test if two text elements belong to the same paragraph
        when they have different fonts
        '''
        p2x = converter.PDF2XMLConverter()

        t1 = etree.fromstring('<text top="106" height="19" font="1"/>')
        t2 = etree.fromstring('<text top="126" height="19" font="2"/>')

        self.assertFalse(p2x.is_same_paragraph(t1, t2))

    def test_is_inside_margins1(self):
        '''top and left inside margins
        '''
        t = etree.fromstring('<text top="109" left="135"/>')
        margins = {}
        margins['rm'] = 62
        margins['lm'] = 802
        margins['tm'] = 88
        margins['bm'] = 1174

        p2x = converter.PDF2XMLConverter()

        self.assertTrue(p2x.is_inside_margins(t, margins))

    def test_is_inside_margins2(self):
        '''top above top margin and left inside margins
        '''
        t = etree.fromstring('<text top="85" left="135"/>')
        margins = {}
        margins['rm'] = 62
        margins['lm'] = 802
        margins['tm'] = 88
        margins['bm'] = 1174

        p2x = converter.PDF2XMLConverter()

        self.assertFalse(p2x.is_inside_margins(t, margins))

    def test_is_inside_margins3(self):
        '''top below bottom margin and left inside margins
        '''
        t = etree.fromstring('<text top="1178" left="135"/>')
        margins = {}
        margins['rm'] = 62
        margins['lm'] = 802
        margins['tm'] = 88
        margins['bm'] = 1174

        p2x = converter.PDF2XMLConverter()

        self.assertFalse(p2x.is_inside_margins(t, margins))

    def test_is_inside_margins4(self):
        '''top inside margins and left outside right margin
        '''
        t = etree.fromstring('<text top="1000" left="50"/>')
        margins = {}
        margins['rm'] = 62
        margins['lm'] = 802
        margins['tm'] = 88
        margins['bm'] = 1174

        p2x = converter.PDF2XMLConverter()

        self.assertFalse(p2x.is_inside_margins(t, margins))

    def test_is_inside_margins5(self):
        '''top inside margins and left outside left margin
        '''
        t = etree.fromstring('<text top="1000" left="805"/>')
        margins = {}
        margins['rm'] = 62
        margins['lm'] = 802
        margins['tm'] = 88
        margins['bm'] = 1174

        p2x = converter.PDF2XMLConverter()

        self.assertFalse(p2x.is_inside_margins(t, margins))

    def test_parse_page_1(self):
        '''Page with one paragraph, three <text> elements
        '''
        page_element = etree.fromstring(
            '<page height="1263" width="862">'
            '<text top="106" left="100" width="100" height="19">1 </text>'
            '<text top="126" left="100" width="100" height="19">2 </text>'
            '<text top="145" left="100" width="100" height="19">3.</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter()
        p2x.parse_page(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.get_body(), encoding='unicode'),
            u'<body><p>1 2 3.</p></body>')

    def test_parse_page_2(self):
        '''Page with two paragraphs, four <text> elements
        '''
        page_element = etree.fromstring(
            '<page height="1263" width="862">'
            '<text top="106" left="100" width="100" height="19">1 </text>'
            '<text top="126" left="100" width="100" height="19">2.</text>'
            '<text top="166" left="100" width="100" height="19">3 </text>'
            '<text top="186" left="100" width="100" height="19">4.</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter()
        p2x.parse_page(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.get_body(), encoding='unicode'),
            u'<body><p>1 2.</p><p>3 4.</p></body>')

    def test_parse_page_3(self):
        '''Page with one paragraph, one <text> elements
        '''
        page_element = etree.fromstring(
            '<page height="1263" width="862">'
            '<text top="145" left="100" width="100" height="19">3.</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter()
        p2x.parse_page(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.get_body(), encoding='unicode'),
            u'<body><p>3.</p></body>')

    def test_parse_page_4(self):
        '''One text element with a ascii letter, the other one with a non-ascii

        This makes two parts lists. The first list contains one element that is
        of type str, the second list contains one element that is unicode.
        '''
        page_element = etree.fromstring(
            '<page height="1263" width="862">'
            '<text top="215" left="100" width="51" height="14">R</text>'
            '<text top="245" left="100" width="39" height="14">Ø</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter()
        p2x.parse_page(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.get_body(), encoding='unicode'),
            u'<body><p>R</p><p>Ø</p></body>')

    def test_parse_page_5(self):
        '''One text element with containing a <b>, the other one with a
        non-ascii string. Both belong to the same paragraph.
        '''
        page_element = etree.fromstring(
            '<page height="1263" width="862">'
            '<text top="215" left="100" width="51" height="14"><b>R</b></text>'
            '<text top="235" left="100" width="39" height="14">Ø</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter()
        p2x.parse_page(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.get_body(), encoding='unicode'),
            u'<body><p><em type="bold">R</em>Ø</p></body>')

    def test_parse_page_6(self):
        '''One text element ending with a hyphen.
        '''
        page_element = etree.fromstring(
            '<page height="1263" width="862">'
            '<text top="215" left="100" width="51" height="14">R-</text>'
            '<text top="235" left="100" width="39" height="14">Ø</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter()
        p2x.parse_page(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.get_body(), encoding='unicode'),
            u'<body><p>R<hyph/>Ø</p></body>')

    def test_parse_page_7(self):
        '''One text element ending with a hyphen.
        '''
        page_element = etree.fromstring(
            '<page height="1263" width="862">'
            '<text top="215" left="100" width="51" height="14">R -</text>'
            '<text top="235" left="100" width="39" height="14">Ø</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter()
        p2x.parse_page(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.get_body(), encoding='unicode'),
            u'<body><p>R - Ø</p></body>')

    def test_parse_page_8(self):
        '''One text element ending with a hyphen.
        '''
        page_element = etree.fromstring(
            '<page height="1263" width="862">'
            '<text top="196" left="142" width="69" height="21" font="15">'
            '<b>JULE-</b></text>'
            '<text top="223" left="118" width="123" height="21" font="15">'
            '<b>HANDEL</b></text></page>')

        p2x = converter.PDF2XMLConverter()
        p2x.parse_page(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.get_body(), encoding='unicode'),
            u'<body><p><em type="bold">JULE<hyph/>HANDEL</em></p></body>')

    def test_parse_page_9(self):
        '''Two <text> elements. One is above the top margin.
        '''
        page_element = etree.fromstring(
            '<page height="1263" width="862">'
            '<text top="70" left="100" width="100" height="19">Page 1</text>'
            '<text top="145" left="100" width="100" height="19">3.</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter()
        p2x.parse_page(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.get_body(), encoding='unicode'),
            u'<body><p>3.</p></body>')

    def test_parse_page_10(self):
        '''Two <text> elements. One is below the bottom margin.
        '''
        page_element = etree.fromstring(
            '<page height="1263" width="862">'
            '<text top="1200" left="100" width="100" height="19">Page 1</text>'
            '<text top="145" left="100" width="100" height="19">3.</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter()
        p2x.parse_page(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.get_body(), encoding='unicode'),
            u'<body><p>3.</p></body>')

    def test_parse_page_11(self):
        '''Two <text> elements. One is to the left of the right margin.
        '''
        page_element = etree.fromstring(
            '<page height="1263" width="862">'
            '<text top="500" left="50" width="100" height="19">Page 1</text>'
            '<text top="145" left="100" width="100" height="19">3.</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter()
        p2x.parse_page(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.get_body(), encoding='unicode'),
            u'<body><p>3.</p></body>')

    def test_parse_page_12(self):
        '''Two <text> elements. One is to the right of the left margin.
        '''
        page_element = etree.fromstring(
            '<page height="1263" width="862">'
            '<text top="500" left="850" width="100" height="19">Page 1</text>'
            '<text top="145" left="100" width="100" height="19">3.</text>'
            '</page>')

        p2x = converter.PDF2XMLConverter()
        p2x.parse_page(page_element)

        self.assertXmlEqual(
            etree.tostring(p2x.get_body(), encoding='unicode'),
            u'<body><p>3.</p></body>')

    def test_get_body(self):
        '''Test the initial values when the class is initiated
        '''
        p2x = converter.PDF2XMLConverter()

        self.assertXmlEqual(etree.tostring(p2x.get_body()), u'<body/>')

    def test_append_to_body(self):
        '''Check if an etree element really is appended to the body element
        '''
        p2x = converter.PDF2XMLConverter()
        p2x.append_to_body(etree.Element('uptown'))

        self.assertXmlEqual(
            etree.tostring(p2x.get_body()), u'<body><uptown/></body>')

    def test_parse_pdf2xmldoc1(self):
        '''Test how a parsing a simplistic pdf2xml document works
        '''
        pdf2xml = etree.fromstring(
            '<pdf2xml>'
            '<page height="1263" width="862"><fontspec/>'
            '<text top="145" left="100" width="100" height="19">1.</text>'
            '</page>'
            '<page height="1263" width="862">'
            '<text top="145" left="100" width="100" height="19">2.</text>'
            '</page>'
            '<page height="1263" width="862">'
            '<text top="145" left="100" width="100" height="19">3.</text>'
            '</page>'
            '</pdf2xml>')
        want = u'<body><p>1.</p><p>2.</p><p>3.</p></body>'

        p2x = converter.PDF2XMLConverter()
        p2x.skip_pages = []
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(etree.tostring(p2x.get_body()), want)

    def test_parse_pdf2xmldoc2(self):
        '''Test if pages really are skipped
        '''
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
        want = u'<body><p>1.</p><p>3.</p></body>'

        p2x = converter.PDF2XMLConverter()
        p2x.skip_pages = ["2"]
        p2x.parse_pages(pdf2xml)

        self.assertXmlEqual(etree.tostring(p2x.get_body()), want)

    def test_compute_margin(self):
        '''Test if the default margins are set
        '''
        p2x = converter.PDF2XMLConverter()

        self.assertEqual(p2x.compute_margin('rm', 1263, 862), 60)
        self.assertEqual(p2x.compute_margin('lm', 1263, 862), 801)
        self.assertEqual(p2x.compute_margin('tm', 1263, 862), 88)
        self.assertEqual(p2x.compute_margin('bm', 1263, 862), 1174)

    def test_set_margin(self):
        '''Test if the margin is set correctly
        '''
        p2x = converter.PDF2XMLConverter()

        self.assertEqual(p2x.set_margin('odd=230; even = 540 ; 8 = 340'),
                         {'odd': 230, 'even': 540, '8': 340})

    def test_set_margins(self):
        '''Test set_margins
        '''
        p2x = converter.PDF2XMLConverter()
        p2x.set_margins({'rm': 'odd=40;even=80;3=60',
                         'lm': '7=70',
                         'tm': '8=80',
                         'bm': '9=200'})

        self.assertEqual(p2x.margins, {'rm': {'odd': 40, 'even': 80, '3': 60},
                                       'lm': {'7': 70},
                                       'tm': {'8': 80},
                                       'bm': {'9': 200}})

    def test_compute_margins1(self):
        '''Test set_margins
        '''
        p2x = converter.PDF2XMLConverter()
        p2x.set_margins({'rm': 'odd=40;even=80;3=60',
                         'lm': '7=70',
                         'tm': '8=80',
                         'bm': '9=200'})

        page1 = etree.fromstring(
            '<page number="1" height="1263" width="862"/>')
        self.assertEqual(p2x.compute_margins(page1), {'rm': 40,
                                                      'lm': 801,
                                                      'tm': 88,
                                                      'bm': 1174})
        page2 = etree.fromstring(
            '<page number="2" height="1263" width="862"/>')
        self.assertEqual(p2x.compute_margins(page2), {'rm': 80,
                                                      'lm': 801,
                                                      'tm': 88,
                                                      'bm': 1174})
        page3 = etree.fromstring(
            '<page number="3" height="1263" width="862"/>')
        self.assertEqual(p2x.compute_margins(page3), {'rm': 60,
                                                      'lm': 801,
                                                      'tm': 88,
                                                      'bm': 1174})
        page7 = etree.fromstring(
            '<page number="7" height="1263" width="862"/>')
        self.assertEqual(p2x.compute_margins(page7), {'rm': 40,
                                                      'lm': 70,
                                                      'tm': 88,
                                                      'bm': 1174})
        page8 = etree.fromstring(
            '<page number="8" height="1263" width="862"/>')
        self.assertEqual(p2x.compute_margins(page8), {'rm': 80,
                                                      'lm': 801,
                                                      'tm': 80,
                                                      'bm': 1174})
        page9 = etree.fromstring(
            '<page number="9" height="1263" width="862"/>')
        self.assertEqual(p2x.compute_margins(page9), {'rm': 40,
                                                      'lm': 801,
                                                      'tm': 88,
                                                      'bm': 200})

    def test_compute_margins2(self):
        '''Test set_margins
        '''
        p2x = converter.PDF2XMLConverter()
        p2x.set_margins({'rm': 'odd=40;even=80;3=60',
                         'lm': 'all=70',
                         'tm': '8=80',
                         'bm': '9=200'})

        page1 = etree.fromstring(
            '<page number="1" height="1263" width="862"/>')
        self.assertEqual(p2x.compute_margins(page1), {'rm': 40,
                                                      'lm': 70,
                                                      'tm': 88,
                                                      'bm': 1174})
        page2 = etree.fromstring(
            '<page number="2" height="1263" width="862"/>')
        self.assertEqual(p2x.compute_margins(page2), {'rm': 80,
                                                      'lm': 70,
                                                      'tm': 88,
                                                      'bm': 1174})
        page3 = etree.fromstring(
            '<page number="3" height="1263" width="862"/>')
        self.assertEqual(p2x.compute_margins(page3), {'rm': 60,
                                                      'lm': 70,
                                                      'tm': 88,
                                                      'bm': 1174})
        page7 = etree.fromstring(
            '<page number="7" height="1263" width="862"/>')
        self.assertEqual(p2x.compute_margins(page7), {'rm': 40,
                                                      'lm': 70,
                                                      'tm': 88,
                                                      'bm': 1174})
        page8 = etree.fromstring(
            '<page number="8" height="1263" width="862"/>')
        self.assertEqual(p2x.compute_margins(page8), {'rm': 80,
                                                      'lm': 70,
                                                      'tm': 80,
                                                      'bm': 1174})
        page9 = etree.fromstring(
            '<page number="9" height="1263" width="862"/>')
        self.assertEqual(p2x.compute_margins(page9), {'rm': 40,
                                                      'lm': 70,
                                                      'tm': 88,
                                                      'bm': 200})
