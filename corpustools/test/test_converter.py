# -*- coding: utf-8 -*-
import unittest
import codecs
import io
import os
import lxml.etree as etree
import lxml.doctestcompare as doctestcompare
import doctest

from corpustools import converter


class TestConverter(unittest.TestCase):
    def setUp(self):
        self.converter_inside_orig = converter.Converter(
            'converter_data/fakecorpus/orig/nob/samediggi-article-16.html',
            True)

        self.converter_outside_orig = converter.Converter(
            'converter_data/samediggi-article-48.html', False)

        self.converter_inside_freecorpus = converter.Converter(
            os.path.join(
                os.getenv('GTFREE'),
                'orig/sme/admin/sd/samediggi.no/samediggi-article-48.html'),
            False)

    def test_get_orig(self):
        self.assertEqual(
            self.converter_inside_orig.get_orig(),
            os.path.join(
                os.getenv('GTHOME'),
                'tools/CorpusTools/corpustools/test/converter_data/\
fakecorpus/orig/nob/samediggi-article-16.html'))

        self.assertEqual(
            self.converter_outside_orig.get_orig(),
            os.path.join(
                os.getenv('GTHOME'),
                'tools/CorpusTools/corpustools/test/converter_data/\
samediggi-article-48.html'))

        self.assertEqual(
            self.converter_inside_freecorpus.get_orig(),
            os.path.join(
                os.getenv('GTFREE'),
                'orig/sme/admin/sd/samediggi.no/samediggi-article-48.html'))

    def test_get_xsl(self):
        self.assertEqual(
            self.converter_inside_orig.get_xsl(),
            os.path.join(
                os.getenv('GTHOME'),
                'tools/CorpusTools/corpustools/test/converter_data/fakecorpus/\
orig/nob/samediggi-article-16.html.xsl'))

        self.assertEqual(
            self.converter_outside_orig.get_xsl(),
            os.path.join(
                os.getenv('GTHOME'),
                'tools/CorpusTools/corpustools/test/converter_data/\
samediggi-article-48.html.xsl'))

        self.assertEqual(
            self.converter_inside_freecorpus.get_xsl(),
            os.path.join(
                os.getenv('GTFREE'),
                'orig/sme/admin/sd/samediggi.no/\
samediggi-article-48.html.xsl'))

    def test_get_tmpdir(self):
        self.assertEqual(
            self.converter_inside_orig.get_tmpdir(),
            os.path.join(
                os.getenv('GTHOME'),
                'tools/CorpusTools/corpustools/test/converter_data/\
fakecorpus/tmp'))

        self.assertEqual(
            self.converter_outside_orig.get_tmpdir(),
            os.path.join(
                os.getenv('GTHOME'),
                'tools/CorpusTools/corpustools/test/tmp'))

        self.assertEqual(
            self.converter_inside_freecorpus.get_tmpdir(),
            os.path.join(os.getenv('GTFREE'), 'tmp'))

    def test_get_corpusdir(self):
        self.assertEqual(
            self.converter_inside_orig.get_corpusdir(),
            os.path.join(
                os.getenv('GTHOME'),
                'tools/CorpusTools/corpustools/test/converter_data/\
fakecorpus'))

        self.assertEqual(
            self.converter_outside_orig.get_corpusdir(),
            os.path.join(
                os.getenv('GTHOME'),
                'tools/CorpusTools/corpustools/test'))

        self.assertEqual(
            self.converter_inside_freecorpus.get_corpusdir(),
            os.getenv('GTFREE'))

    def test_get_converted_name_inside_orig(self):
        self.assertEqual(
            self.converter_inside_orig.get_converted_name(),
            os.path.join(
                os.getenv('GTHOME'),
                'tools/CorpusTools/corpustools/test/converter_data/\
fakecorpus/converted/nob/samediggi-article-16.html.xml'))

    def test_get_converted_name_outside_orig(self):
        self.assertEqual(
            self.converter_outside_orig.get_converted_name(),
            os.path.join(
                os.getenv('GTHOME'),
                'tools/CorpusTools/corpustools/test/converted/\
samediggi-article-48.html.xml'))

    def test_get_converted_inside_freecorpus(self):
        self.assertEqual(
            self.converter_inside_freecorpus.get_converted_name(),
            os.path.join(
                os.getenv('GTFREE'),
                'converted/sme/admin/sd/samediggi.no/\
samediggi-article-48.html.xml'))


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
        self.assertXmlEqual(etree.tostring(self.avvir.intermediate), etree.tostring(want))

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
        self.assertXmlEqual(etree.tostring(self.avvir.intermediate), etree.tostring(want))

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
        self.assertXmlEqual(etree.tostring(self.avvir.intermediate), etree.tostring(want))

class TestSVGConverter(XMLTester):
    def setUp(self):
        self.svg = converter.SVGConverter(
            'converter_data/Riddu_Riddu_avis_TXT.200923.svg')

    def test_convert2intermediate(self):
        got = self.svg.convert2intermediate()
        want = etree.parse(
            'converter_data/Riddu_Riddu_avis_TXT.200923.svg.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))


class TestPlaintextConverter(XMLTester):
    def test_to_unicode(self):
        plaintext = converter.PlaintextConverter(
            'converter_data/winsami2-test-ws2.txt')
        got = plaintext.to_unicode()

        # Ensure that the data in want is unicode
        file_ = codecs.open(
            'converter_data/winsami2-test-utf8.txt', encoding='utf8')
        want = file_.read()
        file_.close()

        self.assertEqual(got, want)

    def test_strip_chars(self):
        plaintext = converter.PlaintextConverter(
            'tullball.txt')
        got = plaintext.strip_chars(u'''ÊÊ
<\!q>
\x0d
<*B>
<*P>
<*I>
<ASCII-MAC>
<vsn:3.000000>''')
        want = u'''\n\n\n \n\n\n\n\n\n\n'''

        self.assertEqual(got, want)

    def test_bold(self):
        plaintext = converter.PlaintextConverter(
            'tullball.txt')
        got = plaintext.content2xml(io.StringIO(u'''@bold:Suohkana beara»sodagaid juohkin'''))

        want = etree.fromstring(r'''<document>
    <header/>
    <body>
        <p><em type="bold">Suohkana beara»sodagaid juohkin</em></p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_kursiv(self):
        plaintext = converter.PlaintextConverter(
            'tullball.txt')
        got = plaintext.content2xml(io.StringIO(u'''@kursiv:(Gáldu)
'''))

        want = etree.fromstring(r'''<document>
    <header/>
    <body>
        <p><em type="italic">(Gáldu)</em></p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_ledtekst(self):
        plaintext = converter.PlaintextConverter(
            'tullball.txt')
        got = plaintext.content2xml(io.StringIO(u'''@LEDtekst:Dat mearkkaša'''))

        want = etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>Dat mearkkaša</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_logo(self):
        plaintext = converter.PlaintextConverter(
            'tullball.txt')
        got = plaintext.content2xml(io.StringIO(u'''@logo:Finnmark jordskifterett'''))

        want = etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>Finnmark jordskifterett</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_fotobyline(self):
        plaintext = converter.PlaintextConverter(
            'tullball.txt')
        got = plaintext.content2xml(io.StringIO(u'''@fotobyline:Finnmark jordskifterett'''))

        want = etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>Finnmark jordskifterett</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_bildetitt(self):
        plaintext = converter.PlaintextConverter(
            'tullball.txt')
        got = plaintext.content2xml(io.StringIO(u'''@bildetitt:Finnmark jordskifterett'''))

        want = etree.fromstring(r'''<document>
    <header/>
    <body>
        <p>Finnmark jordskifterett</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

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

    #def test_newstext(self):
        #newstext = converter.PlaintextConverter('converter_data/newstext.txt')
        #got = newstext.convert2intermediate()
        #want = etree.parse('converter_data/newstext.xml')

        #self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_bilde(self):
        newstext = converter.PlaintextConverter('tullball.txt')
        got = newstext.content2xml(io.StringIO(u'''@bilde:NSR PRESIDEANTAEVTTOHAS? Berit Ranveig Nilssen
B 13  @bilde:DEANU-LEAGIS: Nils Porsanger.
B8  @bilde:SOHPPARIS: Bajit-Sohpparis Nils Andersen.
@bilde :E
BILDE 3:oahppat
<pstyle:bilde>Ii'''))
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>NSR PRESIDEANTAEVTTOHAS? Berit Ranveig Nilssen</p>
        <p>DEANU-LEAGIS: Nils Porsanger.</p>
        <p>SOHPPARIS: Bajit-Sohpparis Nils Andersen.</p>
        <p>E</p>
        <p>oahppat</p>
        <p>Ii</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_ingress(self):
        newstext = converter.PlaintextConverter('tullball.txt')
        got = newstext.content2xml(io.StringIO(u'''@ingress:Ragnhild Nystad, Aili Keskitalo.
@ingres:Guovdageainnu lagasradio
 @ingress: Eallu
@ingress. duottar
'@ingress:Golbma
@ingress Odne
<pstyle:ingress>Buot'''))
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>Ragnhild Nystad, Aili Keskitalo.</p>
        <p>Guovdageainnu lagasradio</p>
        <p>Eallu</p>
        <p>duottar</p>
        <p>Golbma</p>
        <p>Odne</p>
        <p>Buot</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_mtitt(self):
        newstext = converter.PlaintextConverter('tullball.txt')
        got = newstext.content2xml(io.StringIO(u'''@m.titt:Juovllat
m.titt:Guolli
@mtitt:Juovllat
@m.titt:@ingress:Romssa OG
M:TITT:Lea go dus meahccebiila?
@m.titt. Maŋemus gártemat
<pstyle:m.titt>Divvot'''))
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p type="title">Juovllat</p>
        <p type="title">Guolli</p>
        <p type="title">Juovllat</p>
        <p type="title">Romssa OG</p>
        <p type="title">Lea go dus meahccebiila?</p>
        <p type="title">Maŋemus gártemat</p>
        <p type="title">Divvot</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_tekst(self):
        newstext = converter.PlaintextConverter('tullball.txt')
        got = newstext.content2xml(io.StringIO(u'''@tekst:veadjá šaddat.
tekst:NSR ii áiggo.
TEKST:ÐMii lea suohttaseamos geassebargu dus?
<pstyle:tekst>Sámi'''))

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

    def test_nbsp(self):
        newstext = converter.PlaintextConverter('tullball.txt')
        got = newstext.content2xml(io.StringIO(u'''  Son lea'''))
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p>Son lea</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_tittel(self):
        newstext = converter.PlaintextConverter('tullball.txt')
        got = newstext.content2xml(io.StringIO(u'''@tittel:Gii boahtá Nystø maŋis?
@LEDtitt:Gii boahtá Keskitalo maŋis?
@tittel:Gii boahtá Olli maŋis?
TITT:njeallje suorpma boaris.
<pstyle:tittel>Ii'''))
        want = etree.fromstring(u'''<document>
    <header>
        <title>Gii boahtá Nystø maŋis?</title>
    </header>
    <body>
        <p type="title">Gii boahtá Keskitalo maŋis?</p>
        <p type="title">Gii boahtá Olli maŋis?</p>
        <p type="title">njeallje suorpma boaris.</p>
        <p type="title">Ii</p>
    </body>
</document>
''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_byline(self):
        newstext = converter.PlaintextConverter('tullball.txt')
        got = newstext.content2xml(io.StringIO(u'''@byline:Elle Merete Utsi'''))
        want = etree.fromstring(u'''<document>
    <header>
        <author>
            <person firstname="Elle Merete" lastname="Utsi"/>
        </author>
    </header>
    <body/>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_stikktitt(self):
        newstext = converter.PlaintextConverter('tullball.txt')
        got = newstext.content2xml(io.StringIO(u'''@stikktitt:Dološ sámegiel máinnas Várjjagis'''))
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_utitt(self):
        newstext = converter.PlaintextConverter('tullball.txt')
        got = newstext.content2xml(io.StringIO(u'''@utitt:Dološ sámegiel máinnas Várjjagis'''))
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_udot_titt(self):
        newstext = converter.PlaintextConverter('tullball.txt')
        got = newstext.content2xml(io.StringIO(u'''@u.titt:Dološ sámegiel máinnas Várjjagis'''))
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_undertitt(self):
        newstext = converter.PlaintextConverter('tullball.txt')
        got = newstext.content2xml(io.StringIO(u'''@undertitt:Dološ sámegiel máinnas Várjjagis
undertitt:Dološ sámegiel máinnas Várjjagis
'''))
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_ttitt(self):
        newstext = converter.PlaintextConverter('tullball.txt')
        got = newstext.content2xml(io.StringIO(u'''@ttitt:Dološ sámegiel máinnas Várjjagis'''))
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_titt(self):
        newstext = converter.PlaintextConverter('tullball.txt')
        got = newstext.content2xml(io.StringIO(u'''@Titt:Guolli
titt:Ruovttusuodjaleaddjit
'''))
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p type="title">Guolli</p>
        <p type="title">Ruovttusuodjaleaddjit</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_ttt(self):
        newstext = converter.PlaintextConverter('tullball.txt')
        got = newstext.content2xml(io.StringIO(u'''@ttt:Dološ sámegiel máinnas Várjjagis
'''))
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>''')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_tit(self):
        newstext = converter.PlaintextConverter('tullball.txt')
        got = newstext.content2xml(io.StringIO(u'''@tit:Dološ sámegiel máinnas Várjjagis
'''))
        want = etree.fromstring(u'''<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
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
        <p>Guovssahasa nieida. Filbma lea.</p>
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
        pdfdocument = converter.PDFConverter('converter_data/pdf-test.pdf')
        got = pdfdocument.convert2intermediate()
        want = etree.parse('converter_data/pdf-test.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))


class TestDocConverter(XMLTester):
    def setUp(self):
        self.testdoc = converter.DocConverter('converter_data/doc-test.doc')

    def test_convert2intermediate(self):
        got = self.testdoc.convert2intermediate()
        want = etree.parse('converter_data/doc-test.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))


class TestBiblexmlConverter(XMLTester):
    def setUp(self):
        self.testdoc = converter.BiblexmlConverter(
            'converter_data/bible-test.xml')

    def test_convert2intermediate(self):
        got = self.testdoc.convert2intermediate()
        want = etree.parse('converter_data/bible-test.xml.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))


class TestHTMLConverter(XMLTester):
    def setUp(self):
        self.testhtml = converter.HTMLConverter(
            'converter_data/samediggi-article-48s.html')

    def test_convert2intermediate(self):
        got = self.testhtml.convert2intermediate()
        want = etree.parse('converter_data/samediggi-article-48s.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))


class TestHTMLContentConverter(XMLTester):
    def test_remove_empty_class(self):
        got = converter.HTMLContentConverter(
            'with-o:p.html',
            '<html><body><div class=""/><div class="a"><span class="">b</span></div></html>').tidy()

        want = '<html xmlns="http://www.w3.org/1999/xhtml">\
        <head><title/></head><body><div class="a"><span>b</span></div></body></html>'

        self.assertXmlEqual(got, want)

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
                    'ctl00_FullRegion_CenterAndRightRegion_Sorting_sortByDiv',
                    'ctl00_FullRegion_CenterAndRightRegion_HitsControl_searchHitSummary',
                    'AreaTopSiteNav', 'SamiDisclaimer', 'AreaTopRight',
                    'AreaLeft', 'AreaRight', 'ShareArticle', 'tipafriend',
                    'AreaLeftNav', 'PageFooter', 'blog-pager',
                    'NAVheaderContainer', 'NAVbreadcrumbContainer',
                    'NAVsubmenuContainer', 'NAVrelevantContentContainer',
                    'NAVfooterContainer', 'sidebar-wrapper', 'footer-wrapper',
                    'share-article', 'topUserMenu', 'rightAds', 'menu', 'aa',
                    'sidebar', 'footer', 'chatBox', 'sendReminder',
                    'ctl00_MidtSone_ucArtikkel_ctl00_divNavigasjon',
                    'ctl00_MidtSone_ucArtikkel_ctl00_ctl00_ctl01_divRessurser'],
                },
            'p': {
                'class': ['WebPartReadMoreParagraph', 'breadcrumbs'],
                },
            'ul': {
                'id': ['AreaTopPrintMeny', 'AreaTopLanguageNav',],
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
                    hc = converter.HTMLContentConverter(tag + key + value + '.html',
                                                 '<html>\
                                                 <body>\
                                                 <' + tag + " " + key + '="' + value + '">content:' + tag + key + value + \
                                                     '</' + tag + '>\
                                                 <div class="ada"/></body>\
                                                 </html>')
                    hc.remove_elements()

                    want = '<html><body><div class="ada"/></body></html>'

                    self.assertXmlEqual(hc.soup.prettify(), want)

    def test_remove_unwanted_tags(self):
        unwanted_tags = [
            'script', 'style', 'o:p', 'st1:country-region', 'v:shapetype',
            'v:shape', 'st1:metricconverter', 'area', 'object', 'meta',
            'fb:like', 'fb:comments', 'g:plusone', 'hr', 'nf', 'mb', 'ms',
            'img', 'cite', 'embed', 'footer', 'figcaption', 'aside', 'time',
            'figure', 'nav', 'select', 'noscript', 'iframe', 'map', 'img', 'colgroup']
        for unwanted_tag in unwanted_tags:
            got = converter.HTMLContentConverter(unwanted_tag + '.html',
                                                 '<html>\
                                                 <body>\
                                                 <p>p1</p>\
                                                 <' + unwanted_tag + '/>\
                                                 <p>p2</p2></body>\
                                                 </html>').tidy()
            want = '<html xmlns="http://www.w3.org/1999/xhtml">\
            <head><title/></head><body>\
            <p>p1</p><p>p2</p></body></html>'

            self.assertXmlEqual(got, want)

    def test_remove_comment(self):
        got = converter.HTMLContentConverter(
            'with-o:p.html',
            '<html><body><b><!--Hey, buddy. --></b></body></html>').tidy()

        want = '<html xmlns="http://www.w3.org/1999/xhtml">\
        <head><title/></head><body></body></html>'

        self.assertXmlEqual(got, want)

    def test_add_p_around_text(self):
        got = converter.HTMLContentConverter(
            'withoutp.html',
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN">\
            <html><head><meta http-equiv="Content-type" \
            content="text/html; charset=utf-8">\
            <title>– Den utdøende stammes frykt</title>\
            <link rel="stylesheet" type="text/css" href="ssh1.css" />\
            </head><body><h3>VI</h3>... Stockfleth<a href=#[1]>\
            [1]</a> saa<p>Dette høres<h3>VII</h3>... Finnerne<p>Der</body>\
            </html>').tidy()

        want = '<?xml version="1.0"?><!DOCTYPE html PUBLIC "-//W3C//DTD \
        XHTML 1.0 Strict//EN"    \
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\
        <html xmlns="http://www.w3.org/1999/xhtml"><head><title>\
        – Den utdøende stammes frykt</title>  \
        <link rel="stylesheet" type="text/css" href="ssh1.css" />\
        </head><body>  <h3>VI</h3>  <p>... Stockfleth<a href="#[1]">[1]</a>\
        saa</p>  <p>Dette høres</p>  <h3>VII</h3>  <p>... Finnerne</p>\
        <p>Der</p></body></html>'

        self.assertXmlEqual(got, want)


class TestRTFConverter(XMLTester):
    def setUp(self):
        self.testrtf = converter.RTFConverter('converter_data/folkemote.rtf')

    def test_convert2intermediate(self):
        got = self.testrtf.convert2intermediate()
        want = etree.parse('converter_data/folkemote.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))


class TestDocumentFixer(XMLTester):
    def test_fix__body_encoding(self):
        newstext = converter.PlaintextConverter(
            'converter_data/assu97-mac-sami.txt')

        document_fixer = converter.DocumentFixer(
            newstext.convert2intermediate())
        document_fixer.fix_body_encoding()
        got = document_fixer.get_etree()

        want = etree.parse('converter_data/assu97-fixedutf8.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_replace_ligatures(self):
        svgtext = converter.SVGConverter(
            'converter_data/Riddu_Riddu_avis_TXT.200923.svg')
        document_fixer = converter.DocumentFixer(
            etree.fromstring(etree.tostring(svgtext.convert2intermediate())))
        document_fixer.fix_body_encoding()
        got = document_fixer.get_etree()

        want = etree.parse('converter_data/Riddu_Riddu_avis_TXT.200923.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_simple_detect_quote1(self):
        orig_paragraph = '<p>bla bla "bla bla" bla bla </p>'
        expected_paragraph = '<p>bla bla <span type="quote">"bla bla"\
        </span> bla bla</p>'

        document_fixer = converter.DocumentFixer(
            etree.parse(
                'converter_data/samediggi-article-48s-before-lang-detection-\
with-multilingual-tag.xml'))
        got_paragraph = document_fixer.detect_quote(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_simple_detect_quote2(self):
        orig_paragraph = '<p>bla bla “bla bla” bla bla</p>'
        expected_paragraph = '<p>bla bla <span type="quote">“bla bla”\
        </span> bla bla</p>'

        document_fixer = converter.DocumentFixer(
            etree.parse(
                'converter_data/samediggi-article-48s-before-lang-detection-\
with-multilingual-tag.xml'))
        got_paragraph = document_fixer.detect_quote(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_simple_detect_quote3(self):
        orig_paragraph = '<p>bla bla «bla bla» bla bla</p>'
        expected_paragraph = '<p>bla bla <span type="quote">«bla bla»\
        </span> bla bla</p>'

        document_fixer = converter.DocumentFixer(
            etree.parse(
                'converter_data/samediggi-article-48s-before-lang-detection-\
with-multilingual-tag.xml'))
        got_paragraph = document_fixer.detect_quote(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_simple_detect_quote4(self):
        orig_paragraph = '<p type="title">Sámegiel čálamearkkat Windows \
        XP várás.</p>'
        expected_paragraph = '<p type="title">Sámegiel čálamearkkat Windows \
        XP várás.</p>'

        document_fixer = converter.DocumentFixer(
            etree.parse(
                'converter_data/samediggi-article-48s-before-lang-detection-\
with-multilingual-tag.xml'))
        got_paragraph = document_fixer.detect_quote(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_simple_detect_quote2_quotes(self):
        orig_paragraph = '<p>bla bla «bla bla» bla bla «bla bla» bla bla</p>'
        expected_paragraph = '<p>bla bla <span type="quote">«bla bla»\
        </span> bla bla <span type="quote">«bla bla»</span> bla bla</p>'

        document_fixer = converter.DocumentFixer(
            etree.parse(
                'converter_data/samediggi-article-48s-before-lang-detection-\
with-multilingual-tag.xml'))
        got_paragraph = document_fixer.detect_quote(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_detect_quote_with_following_tag(self):
        orig_paragraph = '<p>bla bla «bla bla» <em>bla bla</em></p>'
        expected_paragraph = '<p>bla bla <span type="quote">«bla bla»\
        </span> <em>bla bla</em></p>'

        document_fixer = converter.DocumentFixer(
            etree.parse(
                'converter_data/samediggi-article-48s-before-lang-detection-\
with-multilingual-tag.xml'))
        got_paragraph = document_fixer.detect_quote(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_detect_quote_with_tag_infront(self):
        orig_paragraph = '<p>bla bla <em>bla bla</em> «bla bla»</p>'
        expected_paragraph = '<p>bla bla <em>bla bla</em> \
        <span type="quote">«bla bla»</span></p>'

        document_fixer = converter.DocumentFixer(
            etree.parse(
                'converter_data/samediggi-article-48s-before-lang-detection-\
with-multilingual-tag.xml'))
        got_paragraph = document_fixer.detect_quote(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_detect_quote_within_tag(self):
        orig_paragraph = '<p>bla bla <em>bla bla «bla bla»</em></p>'
        expected_paragraph = '<p>bla bla <em>bla bla <span type="quote">\
        «bla bla»</span></em></p>'

        document_fixer = converter.DocumentFixer(
            etree.parse(
                'converter_data/samediggi-article-48s-before-lang-detection-\
with-multilingual-tag.xml'))
        got_paragraph = document_fixer.detect_quote(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph),
                            expected_paragraph)

    def test_word_count(self):
        orig_doc = etree.parse(
            io.BytesIO('<document xml:lang="sma" id="no_id"><header><title/>\
                <genre/><author><unknown/></author><availability><free/>\
                </availability><multilingual/></header><body><p>Bïevnesh \
                naasjovnalen pryövoej bïjre</p><p>2008</p><p>Bïevnesh \
                eejhtegidie, tjidtjieh aehtjieh bielide naasjovnalen \
                pryövoej bïjre giej leah maanah 5. jïh 8. tsiehkine</p>\
                </body></document>'))

        expected_doc = '<document xml:lang="sma" id="no_id"><header>\
        <title/><genre/><author><unknown/></author><wordcount>20</wordcount>\
        <availability><free/></availability><multilingual/></header><body>\
        <p>Bïevnesh naasjovnalen pryövoej bïjre</p><p>2008</p><p>Bïevnesh \
        eejhtegidie, tjidtjieh aehtjieh bielide naasjovnalen pryövoej bïjre \
        giej leah maanah 5. jïh 8. tsiehkine</p></body></document>'

        document_fixer = converter.DocumentFixer(orig_doc)
        document_fixer.set_word_count()

        self.assertXmlEqual(etree.tostring(document_fixer.etree), expected_doc)

    def test_replace_shy1(self):
        orig_doc = etree.parse(
            io.BytesIO('<document xml:lang="sma" id="no_id"><header><title/>\
                <genre/><author><unknown/></author><availability><free/>\
                </availability><multilingual/></header><body><p>a­b­c<span>d­e</span>f­g</p>\
                </body></document>'))

        expected_doc = '<document xml:lang="sma" id="no_id"><header>\
        <title/><genre/><author><unknown/></author>\
        <availability><free/></availability><multilingual/></header><body>\
        <p>a<hyph/>b<hyph/>c<span>d<hyph/>e</span>f<hyph/>g</p></body></document>'

        document_fixer = converter.DocumentFixer(orig_doc)
        document_fixer.soft_hyphen_to_hyph_tag()

        self.assertXmlEqual(etree.tostring(document_fixer.etree), expected_doc)

    def test_replace_shy2(self):
        orig_doc = etree.parse(
            io.BytesIO('<document xml:lang="sma" id="no_id"><header><title/>\
                <genre/><author><unknown/></author><availability><free/>\
                </availability><multilingual/></header><body><p>a­b­c<span>d­e</span></p>\
                </body></document>'))

        expected_doc = '<document xml:lang="sma" id="no_id"><header>\
        <title/><genre/><author><unknown/></author>\
        <availability><free/></availability><multilingual/></header><body>\
        <p>a<hyph/>b<hyph/>c<span>d<hyph/>e</span></p></body></document>'

        document_fixer = converter.DocumentFixer(orig_doc)
        document_fixer.soft_hyphen_to_hyph_tag()

        self.assertXmlEqual(etree.tostring(document_fixer.etree), expected_doc)

class TestXslMaker(XMLTester):
    def test_get_xsl(self):
        xslmaker = converter.XslMaker('converter_data/samediggi-article-48.\
html.xsl')
        got = xslmaker.get_xsl()

        want = etree.parse('converter_data/test.xsl')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))


class TestLanguageDetector(XMLTester):
    """
    Test the functionality of LanguageDetector
    """
    def setUp(self):
        self.document = etree.parse('converter_data/samediggi-article-48s-\
before-lang-detection-with-multilingual-tag.xml')

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
        orig_paragraph = '<p>Sámegiella lea 2004 čavčča rájes standárda \
        giellaválga Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša \
        ahte sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. \
        Buot leat dás dán fitnodaga Service Pack 2-páhkas, maid ferte viežžat \
        ja bidjat dihtorii. Boađus lea ahte buot boahttevaš Microsoft \
        prográmmat dorjot sámegiela. Dattetge sáhttet deaividit váttisvuođat \
        go čálát sámegiela Outlook-kaleandaris dahje e-poastta namahussajis, \
        ja go čálát sámegillii dakkár prográmmain, maid Microsoft ii leat \
        ráhkadan.</p>'
        expected_paragraph = '<p>Sámegiella lea 2004 čavčča rájes standárda \
        giellaválga Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša \
        ahte sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. \
        Buot leat dás dán fitnodaga Service Pack 2-páhkas, maid ferte viežžat \
        ja bidjat dihtorii. Boađus lea ahte buot boahttevaš Microsoft \
        prográmmat dorjot sámegiela. Dattetge sáhttet deaividit váttisvuođat \
        go čálát sámegiela Outlook-kaleandaris dahje e-poastta namahussajis, \
        ja go čálát sámegillii dakkár prográmmain, maid Microsoft ii leat \
        ráhkadan.</p>'

        language_detector = converter.LanguageDetector(self.document)
        got_paragraph = language_detector.set_paragraph_language(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_set_paragraph_language_mainlanguage_quote_mainlang(self):
        orig_paragraph = '<p>Sámegiella lea 2004 čavčča rájes standárda \
        giellaválga Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša \
        ahte sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. \
        <span type="quote">«Buot leat dás dán fitnodaga Service Pack \
        2-páhkas, maid ferte viežžat ja bidjat dihtorii»</span>. Boađus lea \
        ahte buot boahttevaš Microsoft prográmmat dorjot sámegiela. Dattetge \
        sáhttet deaividit váttisvuođat go čálát sámegiela Outlook-kaleandaris \
        dahje e-poastta namahussajis, ja go čálát sámegillii dakkár \
        prográmmain, maid Microsoft ii leat ráhkadan.</p>'
        expected_paragraph = '<p>Sámegiella lea 2004 čavčča rájes standárda \
        giellaválga Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša \
        ahte sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. \
        <span type="quote">«Buot leat dás dán fitnodaga Service Pack \
        2-páhkas, maid ferte viežžat ja bidjat dihtorii»</span>. Boađus lea\
        ahte buot boahttevaš Microsoft prográmmat dorjot sámegiela. Dattetge \
        sáhttet deaividit váttisvuođat go čálát sámegiela Outlook-kaleandaris \
        dahje e-poastta namahussajis, ja go čálát sámegillii dakkár \
        prográmmain, maid Microsoft ii leat ráhkadan.</p>'

        language_detector = converter.LanguageDetector(self.document)
        got_paragraph = language_detector.set_paragraph_language(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_set_paragraph_language_mainlanguage_quote_not_mainlang(self):
        orig_paragraph = '<p>Sámegiella lea 2004 čavčča rájes standárda \
        giellaválga Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša \
        ahte sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. \
        <span type="quote">«Alt finnes i den foreliggende Service Pack 2 fra \
        selskapet, som må lastes ned og installeres på din datamaskin. \
        Konsekvensen er at all framtidig programvare fra Microsoft vil \
        inneholde støtte for samisk»</span>. Boađus lea ahte buot boahttevaš \
        Microsoft prográmmat dorjot sámegiela. Dattetge sáhttet deaividit \
        váttisvuođat go čálát sámegiela Outlook-kaleandaris dahje e-poastta \
        namahussajis, ja go čálát sámegillii dakkár prográmmain, maid \
        Microsoft ii leat ráhkadan.</p>'
        expected_paragraph = '<p>Sámegiella lea 2004 čavčča rájes standárda \
        giellaválga Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša \
        ahte sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. \
        <span type="quote" xml:lang="nob">«Alt finnes i den foreliggende \
        Service Pack 2 fra selskapet, som må lastes ned og installeres på din \
        datamaskin. Konsekvensen er at all framtidig programvare fra \
        Microsoft vil inneholde støtte for samisk»</span>. Boađus lea ahte \
        buot boahttevaš Microsoft prográmmat dorjot sámegiela. Dattetge \
        sáhttet deaividit váttisvuođat go čálát sámegiela Outlook-kaleandaris \
        dahje e-poastta namahussajis, ja go čálát sámegillii dakkár \
        prográmmain, maid Microsoft ii leat ráhkadan.</p>'

        language_detector = converter.LanguageDetector(self.document)
        got_paragraph = language_detector.set_paragraph_language(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_set_paragraph_language_not_mainlanguage(self):
        orig_paragraph = '<p>Samisk er fra høsten 2004 et standard språkvalg \
        Microsofts operativsystem Windows XP. I praksis betyr det at samiske \
        bokstaver og formater kan velges i alle programmer. Alt finnes i den \
        foreliggende Service Pack 2 fra selskapet, som må lastes ned og \
        installeres på din datamaskin. Konsekvensen er at all framtidig \
        programvare fra Microsoft vil inneholde støtte for samisk. Du vil \
        imidlertid fremdeles kunne oppleve problemer med å skrive samisk i \
        Outlook-kalenderen eller i tittel-feltet i e-post, og med å skrive \
        samisk i programmer levert av andre enn Microsoft.</p>'
        expected_paragraph = '<p xml:lang="nob">Samisk er fra høsten 2004 et \
        standard språkvalg Microsofts operativsystem Windows XP. I praksis \
        betyr det at samiske bokstaver og formater kan velges i alle \
        programmer. Alt finnes i den foreliggende Service Pack 2 fra \
        selskapet, som må lastes ned og installeres på din datamaskin. \
        Konsekvensen er at all framtidig programvare fra Microsoft vil \
        inneholde støtte for samisk. Du vil imidlertid fremdeles kunne \
        oppleve problemer med å skrive samisk i Outlook-kalenderen eller \
        i tittel-feltet i e-post, og med å skrive samisk i programmer \
        levert av andre enn Microsoft.</p>'

        language_detector = converter.LanguageDetector(self.document)
        got_paragraph = language_detector.set_paragraph_language(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_remove_quote(self):
        orig_paragraph = '<p>bla bla <span type="quote">bla1 bla</span> \
ble ble <span type="quote">bla2 bla</span> <b>bli</b> bli \
<span type="quote">bla3 bla</span> blo blo</p>'
        expected_paragraph = 'bla bla  ble ble  bli bli  blo blo'

        language_detector = converter.LanguageDetector(self.document)
        got_paragraph = language_detector.remove_quote(
            etree.fromstring(orig_paragraph))

        self.assertEqual(got_paragraph, expected_paragraph)

    def test_detect_language_with_multilingualtag(self):
        language_detector = converter.LanguageDetector(
            etree.parse('converter_data/samediggi-article-48s-before-\
lang-detection-with-multilingual-tag.xml'))
        language_detector.detect_language()
        got_document = language_detector.get_document()

        expected_document = etree.parse('converter_data/\
samediggi-article-48s-after-lang-detection-with-multilingual-tag.xml')

        self.assertXmlEqual(etree.tostring(got_document),
                            etree.tostring(expected_document))

    def test_detect_language_without_multilingualtag(self):
        language_detector = converter.LanguageDetector(etree.parse(
            'converter_data/samediggi-article-48s-before-lang-detection-\
without-multilingual-tag.xml'))
        language_detector.detect_language()
        got_document = language_detector.get_document()

        expected_document = etree.parse('converter_data/samediggi-article\
-48s-after-lang-detection-without-multilingual-tag.xml')

        self.assertXmlEqual(etree.tostring(got_document),
                            etree.tostring(expected_document))
