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
            self.converter_inside_orig.getOrig(),
            os.path.join(
                os.getenv('GTHOME'),
                'tools/CorpusTools/corpustools/test/converter_data/\
fakecorpus/orig/nob/samediggi-article-16.html'))

        self.assertEqual(
            self.converter_outside_orig.getOrig(),
            os.path.join(
                os.getenv('GTHOME'),
                'tools/CorpusTools/corpustools/test/converter_data/\
samediggi-article-48.html'))

        self.assertEqual(
            self.converter_inside_freecorpus.getOrig(),
            os.path.join(
                os.getenv('GTFREE'),
                'orig/sme/admin/sd/samediggi.no/samediggi-article-48.html'))

    def test_get_xsl(self):
        self.assertEqual(
            self.converter_inside_orig.getXsl(),
            os.path.join(
                os.getenv('GTHOME'),
                'tools/CorpusTools/corpustools/test/converter_data/fakecorpus/\
orig/nob/samediggi-article-16.html.xsl'))

        self.assertEqual(
            self.converter_outside_orig.getXsl(),
            os.path.join(
                os.getenv('GTHOME'),
                'tools/CorpusTools/corpustools/test/converter_data/\
samediggi-article-48.html.xsl'))

        self.assertEqual(
            self.converter_inside_freecorpus.getXsl(),
            os.path.join(
                os.getenv('GTFREE'),
                'orig/sme/admin/sd/samediggi.no/\
samediggi-article-48.html.xsl'))

    def test_get_test(self):
        self.assertEqual(self.converter_inside_orig.getTest(), True)

        self.assertEqual(self.converter_outside_orig.getTest(), False)

        self.assertEqual(self.converter_inside_freecorpus.getTest(), False)

    def test_get_tmpdir(self):
        self.assertEqual(
            self.converter_inside_orig.getTmpdir(),
            os.path.join(
                os.getenv('GTHOME'),
                'tools/CorpusTools/corpustools/test/converter_data/\
fakecorpus/tmp'))

        self.assertEqual(
            self.converter_outside_orig.getTmpdir(),
            os.path.join(
                os.getenv('GTHOME'),
                'tools/CorpusTools/corpustools/test/tmp'))

        self.assertEqual(
            self.converter_inside_freecorpus.getTmpdir(),
            os.path.join(os.getenv('GTFREE'), 'tmp'))

    def test_get_corpusdir(self):
        self.assertEqual(
            self.converter_inside_orig.getCorpusdir(),
            os.path.join(
                os.getenv('GTHOME'),
                'tools/CorpusTools/corpustools/test/converter_data/\
fakecorpus'))

        self.assertEqual(
            self.converter_outside_orig.getCorpusdir(),
            os.path.join(
                os.getenv('GTHOME'),
                'tools/CorpusTools/corpustools/test'))

        self.assertEqual(
            self.converter_inside_freecorpus.getCorpusdir(),
            os.getenv('GTFREE'))

    def test_get_converted_name_inside_orig(self):
        self.assertEqual(
            self.converter_inside_orig.getConvertedName(),
            os.path.join(
                os.getenv('GTHOME'),
                'tools/CorpusTools/corpustools/test/converter_data/\
fakecorpus/converted/nob/samediggi-article-16.html.xml'))

    def test_get_converted_name_outside_orig(self):
        self.assertEqual(
            self.converter_outside_orig.getConvertedName(),
            os.path.join(
                os.getenv('GTHOME'),
                'tools/CorpusTools/corpustools/test/converted/\
samediggi-article-48.html.xml'))

    def test_get_converted_inside_freecorpus(self):
        self.assertEqual(
            self.converter_inside_freecorpus.getConvertedName(),
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
        self.avvir = converter.AvvirConverter(
            'converter_data/fakecorpus/orig/sme/news/Avvir_xml-filer/\
Avvir_2008_xml-filer/02nr028av.article.xml')

    def test_convert2intermediate(self):
        got = self.avvir.convert2intermediate()
        want = etree.parse('converter_data/gt-02nr028av.article.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))


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
        got = plaintext.toUnicode()

        # Ensure that the data in want is unicode
        file_ = codecs.open(
            'converter_data/winsami2-test-utf8.txt', encoding='utf8')
        want = file_.read()
        file_.close()

        self.assertEqual(got, want)

    def test_plaintext(self):
        plaintext = converter.PlaintextConverter(
            'converter_data/plaintext.txt')
        got = plaintext.convert2intermediate()
        want = etree.parse('converter_data/plaintext.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_newstext(self):
        newstext = converter.PlaintextConverter('converter_data/newstext.txt')
        got = newstext.convert2intermediate()
        want = etree.parse('converter_data/newstext.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_assu97(self):
        newstext = converter.PlaintextConverter('converter_data/assu97.txt')
        got = newstext.convert2intermediate()
        want = etree.parse('converter_data/assu97-unfixedutf8.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test__bilde(self):
        newstext = converter.PlaintextConverter('converter_data/bilde.txt')
        got = newstext.convert2intermediate()
        want = etree.parse('converter_data/bilde.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_ingress(self):
        newstext = converter.PlaintextConverter('converter_data/ingress.txt')
        got = newstext.convert2intermediate()
        want = etree.parse('converter_data/ingress.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_mtitt(self):
        newstext = converter.PlaintextConverter('converter_data/mtitt.txt')
        got = newstext.convert2intermediate()
        want = etree.parse('converter_data/mtitt.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_tekst(self):
        newstext = converter.PlaintextConverter('converter_data/tekst.txt')
        got = newstext.convert2intermediate()
        want = etree.parse('converter_data/tekst.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_nbsp(self):
        newstext = converter.PlaintextConverter('converter_data/nbsp.txt')
        got = newstext.convert2intermediate()
        want = etree.parse('converter_data/nbsp.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_tittel(self):
        newstext = converter.PlaintextConverter('converter_data/tittel.txt')
        got = newstext.convert2intermediate()
        want = etree.parse('converter_data/tittel.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test__byline(self):
        newstext = converter.PlaintextConverter('converter_data/byline.txt')
        got = newstext.convert2intermediate()
        want = etree.parse('converter_data/byline.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_stikktitt(self):
        newstext = converter.PlaintextConverter('converter_data/stikktitt.txt')
        got = newstext.convert2intermediate()
        want = etree.parse('converter_data/stikktitt.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_utitt(self):
        newstext = converter.PlaintextConverter('converter_data/utitt.txt')
        got = newstext.convert2intermediate()
        want = etree.parse('converter_data/utitt.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_udot_titt(self):
        newstext = converter.PlaintextConverter('converter_data/udottitt.txt')
        got = newstext.convert2intermediate()
        want = etree.parse('converter_data/udottitt.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_undertitt(self):
        newstext = converter.PlaintextConverter('converter_data/undertitt.txt')
        got = newstext.convert2intermediate()
        want = etree.parse('converter_data/undertitt.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_ttitt(self):
        newstext = converter.PlaintextConverter('converter_data/ttitt.txt')
        got = newstext.convert2intermediate()
        want = etree.parse('converter_data/ttitt.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_titt(self):
        newstext = converter.PlaintextConverter('converter_data/titt.txt')
        got = newstext.convert2intermediate()
        want = etree.parse('converter_data/titt.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_ttt(self):
        newstext = converter.PlaintextConverter('converter_data/ttt.txt')
        got = newstext.convert2intermediate()
        want = etree.parse('converter_data/ttt.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_tit(self):
        newstext = converter.PlaintextConverter('converter_data/tit.txt')
        got = newstext.convert2intermediate()
        want = etree.parse('converter_data/tit.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_two_lines(self):
        two_lines = converter.PlaintextConverter('converter_data/twolines.txt')
        got = two_lines.convert2intermediate()
        want = etree.parse('converter_data/twolines.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_hyph(self):
        two_lines = converter.PlaintextConverter('converter_data/hyph.txt')
        got = two_lines.convert2intermediate()
        want = etree.parse('converter_data/hyph.xml')

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
    def test_remove_op(self):
        got = converter.HTMLContentConverter(
            'with-o:p.html',
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" \
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\
            <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" \
            lang="nn"><head><title>regjeringen.no</title></head>\
            <body onload="javascript:Operatest();">\
            <o:p></o:p></body></html>').tidy()

        want = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"\
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html \
        xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" lang="nn"><head>\
        <title>regjeringen.no</title></head>\
        <body onload="javascript:Operatest();"></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_fblike(self):
        got = converter.HTMLContentConverter(
            'with-fb:like.html',
            '<html xmlns="http://www.w3.org/1999/xhtml"><body><fb:like \
            send="true" show_faces="false" action="recommend">\
            </fb:like></body></html>').tidy()

        want = '<html xmlns="http://www.w3.org/1999/xhtml"><head><title/>\
        </head><body></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_fbcomments(self):
        got = converter.HTMLContentConverter(
            'with-fb:comments.html',
            '<html xmlns="http://www.w3.org/1999/xhtml"><body><fb:comments \
            href="http://www.nord-salten.no/" num_posts="2" width="750">\
            </fb:comments></body></html>').tidy()

        want = '<html xmlns="http://www.w3.org/1999/xhtml"><head><title/>\
        </head><body></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_gplusone(self):
        got = converter.HTMLContentConverter(
            'with-g:plusone.html',
            '<html xmlns="http://www.w3.org/1999/xhtml"><body>\
            <g:plusone size="standard" count="true"></g:plusone>\
            </body></html>').tidy()

        want = '<html xmlns="http://www.w3.org/1999/xhtml"><head><title/>\
        </head><body></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_st1_country_region(self):
        got = converter.HTMLContentConverter(
            'with-o:p.html',
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"\
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\
            <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" \
            lang="nn"><head><title>regjeringen.no</title></head>\
            <body onload="javascript:Operatest();">\
            <st1:country-region w:st="on"></st1:country-region>\
            </body></html>').tidy()

        want = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"\
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" \
        lang="nn"><head><title>regjeringen.no</title></head>\
        <body onload="javascript:Operatest();"></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_st1_metric_converter(self):
        got = converter.HTMLContentConverter(
            'with-o:p.html',
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" \
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\
            <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" \
            lang="nn"><head><title>regjeringen.no</title></head>\
            <body onload="javascript:Operatest();">\
            <st1:metricconverter productid="1,85 G">\
            </st1:metricconverter></body></html>').tidy()

        want = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"\
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" \
        lang="nn"><head><title>regjeringen.no</title></head>\
        <body onload="javascript:Operatest();"></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_v_shape_type(self):
        got = converter.HTMLContentConverter(
            'with-o:p.html',
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" \
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\
            <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" \
            lang="nn"><head><title>regjeringen.no</title></head>\
            <body onload="javascript:Operatest();">\
            <v:shapetype></v:shapetype></body></html>').tidy()

        want = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"\
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" lang="nn">\
        <head><title>regjeringen.no</title></head>\
        <body onload="javascript:Operatest();"></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_v_shape(self):
        got = converter.HTMLContentConverter(
            'with-o:p.html',
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" \
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\
            <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" \
            lang="nn"><head><title>regjeringen.no</title></head>\
            <body onload="javascript:Operatest();"><v:shape></v:shape>\
            </body></html>').tidy()

        want = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 \
        Transitional//EN" \
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\
        <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" lang="nn">\
        <head><title>regjeringen.no</title></head>\
        <body onload="javascript:Operatest();"></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_area(self):
        got = converter.HTMLContentConverter(
            'with-o:p.html',
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" \
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\
            <html xmlns="http://www.w3.org/1999/xhtml" \
            xml:lang="nn" lang="nn"><head><title>Avdeling for havbruk, \
            sj&#248;mat og marknad - regjeringen.no</title></head>\
            <body onload="javascript:Operatest();">\
            <area title="Suodjalusministtar" \
            href="/fd/sami/p30007057/p30007075/bn.html" shape="rect" \
            alt="Suodjalusministtar" coords="230,10,374,24" />\
            </body></html>').tidy()

        want = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 \
        Transitional//EN" \
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\
        <html xmlns="http://www.w3.org/1999/xhtml" \
        xml:lang="nn" lang="nn"><head><title>Avdeling for havbruk, \
        sj&#248;mat og marknad - regjeringen.no</title></head>\
        <body onload="javascript:Operatest();"></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_object(self):
        got = converter.HTMLContentConverter(
            'with-o:p.html',
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" \
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\
            <html xmlns="http://www.w3.org/1999/xhtml" \
            xml:lang="nn" lang="nn"><head><title>Avdeling for havbruk, \
            sj&#248;mat og marknad - regjeringen.no</title></head>\
            <body onload="javascript:Operatest();">\
            <object width="640" height="385"><embed></embed></object>\
            </body></html>').tidy()

        want = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 \
        Transitional//EN" \
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\
        <html xmlns="http://www.w3.org/1999/xhtml" \
        xml:lang="nn" lang="nn"><head>\
        <title>Avdeling for havbruk, sj&#248;mat og marknad - \
        regjeringen.no</title></head>\
        <body onload="javascript:Operatest();"></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_comment(self):
        got = converter.HTMLContentConverter(
            'with-o:p.html',
            '<html><body><b><!--Hey, buddy. --></b></body></html>').tidy()

        want = '<html xmlns="http://www.w3.org/1999/xhtml">\
        <head><title/></head><body></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_style(self):
        got = converter.HTMLContentConverter(
            'with-o:p.html',
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" \
            "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\
            <html xmlns="http://www.w3.org/1999/xhtml"> <head>  \
            <style id="page-skin-1" type="text/css"></style> </head> \
            <body> </body></html>').tidy()

        want = '<html xmlns="http://www.w3.org/1999/xhtml">\
        <head><title/></head><body/></html>'

        self.assertXmlEqual(got, want)

    def test_remove_script(self):
        got = converter.HTMLContentConverter(
            'with-o:p.html',
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 \
            Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\
            <html xmlns="http://www.w3.org/1999/xhtml"> <head>\
            <script type="text/javascript">()();</script></head> \
            <body> </body></html>').tidy()

        want = '<html xmlns="http://www.w3.org/1999/xhtml">\
        <head><title/></head><body/></html>'

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
        self.testrtf = converter.RTFConverter('converter_data/Folkemøte.rtf')

    def test_convert2intermediate(self):
        got = self.testrtf.convert2intermediate()
        want = etree.parse('converter_data/Folkemøte.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))


class TestDocumentFixer(XMLTester):
    def test_fix__body_encoding(self):
        newstext = converter.PlaintextConverter(
            'converter_data/assu97-mac-sami.txt')

        document_fixer = converter.DocumentFixer(
            newstext.convert2intermediate())
        got = document_fixer.fixBodyEncoding()

        want = etree.parse('converter_data/assu97-fixedutf8.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_replace_ligatures(self):
        svgtext = converter.SVGConverter(
            'converter_data/Riddu_Riddu_avis_TXT.200923.svg')
        document_fixer = converter.DocumentFixer(
            etree.fromstring(etree.tostring(svgtext.convert2intermediate())))
        got = document_fixer.fixBodyEncoding()

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
        got_paragraph = document_fixer.detectQuote(
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
        got_paragraph = document_fixer.detectQuote(
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
        got_paragraph = document_fixer.detectQuote(
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
        got_paragraph = document_fixer.detectQuote(
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
        got_paragraph = document_fixer.detectQuote(
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
        got_paragraph = document_fixer.detectQuote(
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
        got_paragraph = document_fixer.detectQuote(
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
        got_paragraph = document_fixer.detectQuote(
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
        document_fixer.setWordCount()

        self.assertXmlEqual(etree.tostring(document_fixer.etree), expected_doc)


class TestXslMaker(XMLTester):
    def test_get_xsl(self):
        xslmaker = converter.XslMaker('converter_data/samediggi-article-48.\
html.xsl')
        got = xslmaker.getXsl()

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
        self.assertEqual(test_main_lang, language_detector.getMainlang())

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
        got_paragraph = language_detector.setParagraphLanguage(
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
        got_paragraph = language_detector.setParagraphLanguage(
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
        got_paragraph = language_detector.setParagraphLanguage(
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
        got_paragraph = language_detector.setParagraphLanguage(
            etree.fromstring(orig_paragraph))

        self.assertXmlEqual(etree.tostring(got_paragraph), expected_paragraph)

    def test_remove_quote(self):
        orig_paragraph = '<p>bla bla <span type="quote">bla1 bla</span> \
ble ble <span type="quote">bla2 bla</span> <b>bli</b> bli \
<span type="quote">bla3 bla</span> blo blo</p>'
        expected_paragraph = 'bla bla  ble ble  bli bli  blo blo'

        language_detector = converter.LanguageDetector(self.document)
        got_paragraph = language_detector.removeQuote(
            etree.fromstring(orig_paragraph))

        self.assertEqual(got_paragraph, expected_paragraph)

    def test_detect_language_with_multilingualtag(self):
        language_detector = converter.LanguageDetector(
            etree.parse('converter_data/samediggi-article-48s-before-\
lang-detection-with-multilingual-tag.xml'))
        language_detector.detectLanguage()
        got_document = language_detector.getDocument()

        expected_document = etree.parse('converter_data/\
samediggi-article-48s-after-lang-detection-with-multilingual-tag.xml')

        self.assertXmlEqual(etree.tostring(got_document),
                            etree.tostring(expected_document))

    def test_detect_language_without_multilingualtag(self):
        language_detector = converter.LanguageDetector(etree.parse(
            'converter_data/samediggi-article-48s-before-lang-detection-\
without-multilingual-tag.xml'))
        language_detector.detectLanguage()
        got_document = language_detector.getDocument()

        expected_document = etree.parse('converter_data/samediggi-article\
-48s-after-lang-detection-without-multilingual-tag.xml')

        self.assertXmlEqual(etree.tostring(got_document),
                            etree.tostring(expected_document))
