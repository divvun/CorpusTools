# -*- coding: utf-8 -*-
import unittest
import codecs
import io
import decimal
import os
import lxml.etree as etree
import lxml.doctestcompare as doctestcompare
import doctest

from corpustools import converter

class TestConverter(unittest.TestCase):
    def setUp(self):
        self.converterInsideOrig = \
        converter.Converter('converter_data/fakecorpus/orig/nob/samediggi-article-16.html', True)

        self.converterOutsideOrig = \
        converter.Converter('converter_data/samediggi-article-48.html', False)

        self.converterInsideFreecorpus = \
        converter.Converter(os.path.join(os.getenv('GTFREE'), \
        'orig/sme/admin/sd/samediggi.no/samediggi-article-48.html'), False)

    def test_get_orig(self):
        self.assertEqual(self.converterInsideOrig.getOrig(), \
        os.path.join(os.getenv('GTHOME'),\
        'tools/CorpusTools/corpustools/test/converter_data/fakecorpus/orig/nob/samediggi-article-16.html'))

        self.assertEqual(self.converterOutsideOrig.getOrig(), \
        os.path.join(os.getenv('GTHOME'), \
        'tools/CorpusTools/corpustools/test/converter_data/samediggi-article-48.html'))

        self.assertEqual(self.converterInsideFreecorpus.getOrig(), \
        os.path.join(os.getenv('GTFREE'), \
        'orig/sme/admin/sd/samediggi.no/samediggi-article-48.html'))

    def test_get_xsl(self):
        self.assertEqual(self.converterInsideOrig.getXsl(), \
        os.path.join(os.getenv('GTHOME'),\
        'tools/CorpusTools/corpustools/test/converter_data/fakecorpus/orig/nob/samediggi-article-16.html.xsl'))

        self.assertEqual(self.converterOutsideOrig.getXsl(), \
        os.path.join(os.getenv('GTHOME'), \
        'tools/CorpusTools/corpustools/test/converter_data/samediggi-article-48.html.xsl'))

        self.assertEqual(self.converterInsideFreecorpus.getXsl(), \
        os.path.join(os.getenv('GTFREE'), \
        'orig/sme/admin/sd/samediggi.no/samediggi-article-48.html.xsl'))

    def test_get_test(self):
        self.assertEqual(self.converterInsideOrig.getTest(), True)

        self.assertEqual(self.converterOutsideOrig.getTest(), False)

        self.assertEqual(self.converterInsideFreecorpus.getTest(), False)

    def test_get_tmpdir(self):
        self.assertEqual(self.converterInsideOrig.getTmpdir(), \
            os.path.join(os.getenv('GTHOME'), \
            'tools/CorpusTools/corpustools/test/converter_data/fakecorpus/tmp'))

        self.assertEqual(self.converterOutsideOrig.getTmpdir(), \
            os.path.join(os.getenv('GTHOME'), \
            'tools/CorpusTools/corpustools/test/tmp'))

        self.assertEqual(self.converterInsideFreecorpus.getTmpdir(), \
            os.path.join(os.getenv('GTFREE'), 'tmp'))

    def test_get_corpusdir(self):
        self.assertEqual(self.converterInsideOrig.getCorpusdir(), \
            os.path.join(os.getenv('GTHOME'), \
            'tools/CorpusTools/corpustools/test/converter_data/fakecorpus'))

        self.assertEqual(self.converterOutsideOrig.getCorpusdir(), \
            os.path.join(os.getenv('GTHOME'), \
            'tools/CorpusTools/corpustools/test'))

        self.assertEqual(self.converterInsideFreecorpus.getCorpusdir(), \
            os.getenv('GTFREE'))

    def test_get_converted_name_inside_orig(self):
        self.assertEqual(self.converterInsideOrig.getConvertedName(),
            os.path.join(os.getenv('GTHOME'), \
            'tools/CorpusTools/corpustools/test/converter_data/fakecorpus/converted/nob/samediggi-article-16.html.xml'))

    def test_get_converted_name_outside_orig(self):
        self.assertEqual(self.converterOutsideOrig.getConvertedName(), \
            os.path.join(os.getenv('GTHOME'), \
            'tools/CorpusTools/corpustools/test/converted/samediggi-article-48.html.xml'))

    def test_get_converted_inside_freecorpus(self):
        self.assertEqual(self.converterInsideFreecorpus.getConvertedName(), \
            os.path.join(os.getenv('GTFREE'), \
            'converted/sme/admin/sd/samediggi.no/samediggi-article-48.html.xml'))

class TestAvvirConverter(unittest.TestCase):
    def setUp(self):
        self.avvir = converter.AvvirConverter('converter_data/fakecorpus/orig/sme/news/Avvir_xml-filer/Avvir_2008_xml-filer/02nr028av.article.xml')

    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal
        """
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)

    def test_convert2intermediate(self):
        got = self.avvir.convert2intermediate()
        want = etree.parse('converter_data/gt-02nr028av.article.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

class TestSVGConverter(unittest.TestCase):
    def setUp(self):
        self.svg = converter.SVGConverter('converter_data/Riddu_Riddu_avis_TXT.200923.svg')

    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal
        """
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)

    def test_convert2intermediate(self):
        got = self.svg.convert2intermediate()
        want = etree.parse('converter_data/Riddu_Riddu_avis_TXT.200923.svg.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

class TestPlaintextConverter(unittest.TestCase):
    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal
        """
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)

    def test_to_unicode(self):
        plaintext = converter.PlaintextConverter('converter_data/winsami2-test-ws2.txt')
        got  = plaintext.toUnicode()

        # Ensure that the data in want is unicode
        f = codecs.open('converter_data/winsami2-test-utf8.txt', encoding = 'utf8')
        want = f.read()
        f.close()

        self.assertEqual(got, want)

    def test_plaintext(self):
        plaintext = converter.PlaintextConverter('converter_data/plaintext.txt')
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
        twoLines = converter.PlaintextConverter('converter_data/twolines.txt')
        got = twoLines.convert2intermediate()
        want = etree.parse('converter_data/twolines.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_hyph(self):
        twoLines = converter.PlaintextConverter('converter_data/hyph.txt')
        got = twoLines.convert2intermediate()
        want = etree.parse('converter_data/hyph.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

class TestPDFConverter(unittest.TestCase):
    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal
        """
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)

    def test_pdf_converter(self):
        pdfdocument = converter.PDFConverter('converter_data/pdf-test.pdf')
        got = pdfdocument.convert2intermediate()
        want = etree.parse('converter_data/pdf-test.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

class TestDocConverter(unittest.TestCase):
    def setUp(self):
        self.testdoc = converter.DocConverter('converter_data/doc-test.doc')

    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal
        """
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)

    def test_convert2intermediate(self):
        got = self.testdoc.convert2intermediate()
        want = etree.parse('converter_data/doc-test.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

class TestBiblexmlConverter(unittest.TestCase):
    def setUp(self):
        self.testdoc = converter.BiblexmlConverter('converter_data/bible-test.xml')

    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal
        """
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)

    def test_convert2intermediate(self):
        got = self.testdoc.convert2intermediate()
        want = etree.parse('converter_data/bible-test.xml.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

class TestHTMLConverter(unittest.TestCase):
    def setUp(self):
        self.testhtml = converter.HTMLConverter('converter_data/samediggi-article-48s.html')

    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal
        """
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)

    def test_convert2intermediate(self):
        got = self.testhtml.convert2intermediate()
        want = etree.parse('converter_data/samediggi-article-48s.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

class TestHTMLContentConverter(unittest.TestCase):
    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal
        """
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)

    def test_remove_op(self):
        got = converter.HTMLContentConverter('with-o:p.html', '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" lang="nn"><head><title>Avdeling for havbruk, sj&#248;mat og marknad - regjeringen.no</title></head><body onload="javascript:Operatest();"><o:p><font face="Times New Roman" size="3">&nbsp;</font></o:p></body></html>').tidy()

        want = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" lang="nn"><head><title>Avdeling for havbruk, sj&#248;mat og marknad - regjeringen.no</title></head><body onload="javascript:Operatest();"></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_fblike(self):
        got = converter.HTMLContentConverter('with-fb:like.html', '<html xmlns="http://www.w3.org/1999/xhtml"><body><fb:like send="true" show_faces="false" action="recommend"></fb:like></body></html>').tidy()

        want = '<html xmlns="http://www.w3.org/1999/xhtml"><head><title/></head><body></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_fbcomments(self):
        got = converter.HTMLContentConverter('with-fb:comments.html', '<html xmlns="http://www.w3.org/1999/xhtml"><body><fb:comments href="http://www.nord-salten.no/no/nyheter/samisk/hellmocuhppa.4032" num_posts="2" width="750"></fb:comments></body></html>').tidy()

        want = '<html xmlns="http://www.w3.org/1999/xhtml"><head><title/></head><body></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_gplusone(self):
        got = converter.HTMLContentConverter('with-g:plusone.html', '<html xmlns="http://www.w3.org/1999/xhtml"><body><g:plusone size="standard" count="true"></g:plusone></body></html>').tidy()

        want = '<html xmlns="http://www.w3.org/1999/xhtml"><head><title/></head><body></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_st1_country_region(self):
        got = converter.HTMLContentConverter('with-o:p.html', '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" lang="nn"><head><title>Avdeling for havbruk, sj&#248;mat og marknad - regjeringen.no</title></head><body onload="javascript:Operatest();"><st1:country-region w:st="on"><st1:place w:st="on">Norway</st1:place></st1:country-region></body></html>').tidy()

        want = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" lang="nn"><head><title>Avdeling for havbruk, sj&#248;mat og marknad - regjeringen.no</title></head><body onload="javascript:Operatest();"></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_st1_metric_converter(self):
        got = converter.HTMLContentConverter('with-o:p.html', '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" lang="nn"><head><title>Avdeling for havbruk, sj&#248;mat og marknad - regjeringen.no</title></head><body onload="javascript:Operatest();"><st1:metricconverter productid="1,85 G"><span lang="I-SAMI-NO" style="mso-ansi-language: I-SAMI-NO">1,85 G</span></st1:metricconverter></body></html>').tidy()

        want = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" lang="nn"><head><title>Avdeling for havbruk, sj&#248;mat og marknad - regjeringen.no</title></head><body onload="javascript:Operatest();"></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_v_shape_type(self):
        got = converter.HTMLContentConverter('with-o:p.html', '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" lang="nn"><head><title>Avdeling for havbruk, sj&#248;mat og marknad - regjeringen.no</title></head><body onload="javascript:Operatest();"><v:shapetype id="_x0000_t75" path="m@4@5l@4@11@9@11@9@5xe" stroked="f" filled="f" o:preferrelative="t" o:spt="75" coordsize="21600,21600"> <v:stroke joinstyle="miter"></v:stroke><v:formulas><v:f eqn="if lineDrawn pixelLineWidth 0"></v:f><v:f eqn="sum @0 1 0"></v:f><v:f eqn="sum 0 0 @1"></v:f><v:f eqn="prod @2 1 2"></v:f><v:f eqn="prod @3 21600 pixelWidth"></v:f><v:f eqn="prod @3 21600 pixelHeight"></v:f><v:f eqn="sum @0 0 1"></v:f><v:f eqn="prod @6 1 2"></v:f><v:f eqn="prod @7 21600 pixelWidth"></v:f><v:f eqn="sum @8 21600 0"></v:f><v:f eqn="prod @7 21600 pixelHeight"></v:f><v:f eqn="sum @10 21600 0"></v:f></v:formulas><v:path o:connecttype="rect" gradientshapeok="t" o:extrusionok="f"></v:path><?xml:namespace prefix = o ns = "urn:schemas-microsoft-com:office:office"/?><o:lock aspectratio="t" v:ext="edit"></o:lock></v:shapetype></body></html>').tidy()

        want = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" lang="nn"><head><title>Avdeling for havbruk, sj&#248;mat og marknad - regjeringen.no</title></head><body onload="javascript:Operatest();"></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_v_shape(self):
        got = converter.HTMLContentConverter('with-o:p.html', '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" lang="nn"><head><title>Avdeling for havbruk, sj&#248;mat og marknad - regjeringen.no</title></head><body onload="javascript:Operatest();"><v:shape style="WIDTH: 405pt; HEIGHT: 202.5pt" id="_x0000_i1025" type="#_x0000_t75" alt="Jens Stoltenberg, Dmitrij Medvedjev og Jonas Gahr Støre. Foto: Statsministerens kontor"><v:imagedata src="file:///C:\DOCUME~1\oeoe\LOCALS~1\Temp\msohtml1\01\clip_image001.jpg" o:href="http://www.regjeringen.no/upload/SMK/Nyhetsbilder/2010/Stoltenberg-og-Medvedjev_samtaler1_540x270.jpg"></v:imagedata></v:shape></body></html>').tidy()

        want = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" lang="nn"><head><title>Avdeling for havbruk, sj&#248;mat og marknad - regjeringen.no</title></head><body onload="javascript:Operatest();"></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_area(self):
        got = converter.HTMLContentConverter('with-o:p.html', '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" lang="nn"><head><title>Avdeling for havbruk, sj&#248;mat og marknad - regjeringen.no</title></head><body onload="javascript:Operatest();"><area title="Suodjalusministtar" href="/fd/sami/p30007057/p30007075/bn.html" shape="rect" alt="Suodjalusministtar" coords="230,10,374,24" /></body></html>').tidy()

        want = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" lang="nn"><head><title>Avdeling for havbruk, sj&#248;mat og marknad - regjeringen.no</title></head><body onload="javascript:Operatest();"></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_object(self):
        got = converter.HTMLContentConverter('with-o:p.html', '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" lang="nn"><head><title>Avdeling for havbruk, sj&#248;mat og marknad - regjeringen.no</title></head><body onload="javascript:Operatest();"><object width="640" height="385"><param name="movie" value="http://www.youtube.com/v/1HH5pmM4SAs&amp;hl=nb_NO&amp;fs=1&amp;rel=0" /><param name="allowFullScreen" value="true" /><param name="allowscriptaccess" value="always" /><embed src="http://www.youtube.com/v/1HH5pmM4SAs&amp;hl=nb_NO&amp;fs=1&amp;rel=0" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="640" height="385"></embed></object></body></html>').tidy()

        want = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="nn" lang="nn"><head><title>Avdeling for havbruk, sj&#248;mat og marknad - regjeringen.no</title></head><body onload="javascript:Operatest();"></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_comment(self):
        got = converter.HTMLContentConverter('with-o:p.html', '<html><body><b><!--Hey, buddy. Want to buy a used parser?--></b></body></html>').tidy()

        want = '<html xmlns="http://www.w3.org/1999/xhtml"><head><title/></head><body></body></html>'

        self.assertXmlEqual(got, want)

    def test_remove_style(self):
        got = converter.HTMLContentConverter('with-o:p.html', '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"><html xmlns="http://www.w3.org/1999/xhtml"> <head>  <style id="page-skin-1" type="text/css">   <!--------------------------------------------------->  </style> </head> <body> </body></html>').tidy()

        want = '<html xmlns="http://www.w3.org/1999/xhtml"><head><title/></head><body/></html>'

        self.assertXmlEqual(got, want)

    def test_remove_script(self):
        got = converter.HTMLContentConverter('with-o:p.html', '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"><html xmlns="http://www.w3.org/1999/xhtml"> <head><script type="text/javascript">(function() { var a=window;function e(b){this.t={};this.tick=function(c,h,d){d=d?d:(new Date).getTime();this.t[c]=[d,h]};this.tick("start",null,b)}var f=new e;a.jstiming={Timer:e,load:f};try{a.jstiming.pt=a.gtbExternal&&a.gtbExternal.pageT()||a.external&&a.external.pageT}catch(g){};a.tickAboveFold=function(b){b=b;var c=0;if(b.offsetParent){do c+=b.offsetTop;while(b=b.offsetParent)}b=c;b<=750&&a.jstiming.load.tick("aft")};var i=false;function j(){if(!i){i=true;a.jstiming.load.tick("firstScrollTime")}}a.addEventListener?a.addEventListener("scroll",j,false):a.attachEvent("onscroll",j); })();</script></head> <body> </body></html>').tidy()

        want = '<html xmlns="http://www.w3.org/1999/xhtml"><head><title/></head><body/></html>'

        self.assertXmlEqual(got, want)

    def test_add_p_around_text(self):
        got = converter.HTMLContentConverter('withoutp.html', '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Final//EN"><html><head><meta http-equiv="Content-type" content="text/html; charset=utf-8"><title>– Den utdøende stammes frykt</title><link rel="stylesheet" type="text/css" href="ssh1.css" /></head><body><h3>VI</h3>... Stockfleth<a href=#[1]>[1]</a> saa<p>Dette høres<h3>VII</h3>... Finnerne<p>Der</body></html>').tidy()

        want = '<?xml version="1.0"?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"><html xmlns="http://www.w3.org/1999/xhtml"><head><title>– Den utdøende stammes frykt</title>  <link rel="stylesheet" type="text/css" href="ssh1.css" /></head><body>  <h3>VI</h3>  <p>... Stockfleth<a href="#[1]">[1]</a> saa</p>  <p>Dette høres</p>  <h3>VII</h3>  <p>... Finnerne</p>  <p>Der</p></body></html>'

        self.assertXmlEqual(got, want)

class TestRTFConverter(unittest.TestCase):
    def setUp(self):
        self.testrtf = converter.RTFConverter('converter_data/Folkemøte.rtf')

    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal
        """
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)

    def test_convert2intermediate(self):
        got = self.testrtf.convert2intermediate()
        want = etree.parse('converter_data/Folkemøte.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

class TestDocumentFixer(unittest.TestCase):
    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal
        """
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)

    def test_fix__body_encoding(self):
        newstext = converter.PlaintextConverter('converter_data/assu97-mac-sami.txt')

        eg = converter.DocumentFixer(newstext.convert2intermediate())
        got = eg.fixBodyEncoding()

        want = etree.parse('converter_data/assu97-fixedutf8.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_replace_ligatures(self):
        svgtext = converter.SVGConverter('converter_data/Riddu_Riddu_avis_TXT.200923.svg')
        eg = converter.DocumentFixer(etree.fromstring(etree.tostring(svgtext.convert2intermediate())))
        got = eg.fixBodyEncoding()

        want = etree.parse('converter_data/Riddu_Riddu_avis_TXT.200923.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_simple_detect_quote1(self):
        origParagraph = '<p>bla bla "bla bla" bla bla </p>'
        expectedParagraph = '<p>bla bla <span type="quote">"bla bla"</span> bla bla</p>'

        df = converter.DocumentFixer(etree.parse('converter_data/samediggi-article-48s-before-lang-detection-with-multilingual-tag.xml'))
        gotParagraph = df.detectQuote(etree.fromstring(origParagraph))

        self.assertXmlEqual(etree.tostring(gotParagraph), expectedParagraph)

    def test_simple_detect_quote2(self):
        origParagraph = '<p>bla bla “bla bla” bla bla</p>'
        expectedParagraph = '<p>bla bla <span type="quote">“bla bla”</span> bla bla</p>'

        df = converter.DocumentFixer(etree.parse('converter_data/samediggi-article-48s-before-lang-detection-with-multilingual-tag.xml'))
        gotParagraph = df.detectQuote(etree.fromstring(origParagraph))

        self.assertXmlEqual(etree.tostring(gotParagraph), expectedParagraph)

    def test_simple_detect_quote3(self):
        origParagraph = '<p>bla bla «bla bla» bla bla</p>'
        expectedParagraph = '<p>bla bla <span type="quote">«bla bla»</span> bla bla</p>'

        df = converter.DocumentFixer(etree.parse('converter_data/samediggi-article-48s-before-lang-detection-with-multilingual-tag.xml'))
        gotParagraph = df.detectQuote(etree.fromstring(origParagraph))

        self.assertXmlEqual(etree.tostring(gotParagraph), expectedParagraph)

    def test_simple_detect_quote4(self):
        origParagraph = '<p type="title">Sámegiel čálamearkkat Windows XP várás.</p>'
        expectedParagraph = '<p type="title">Sámegiel čálamearkkat Windows XP várás.</p>'

        df = converter.DocumentFixer(etree.parse('converter_data/samediggi-article-48s-before-lang-detection-with-multilingual-tag.xml'))
        gotParagraph = df.detectQuote(etree.fromstring(origParagraph))

        self.assertXmlEqual(etree.tostring(gotParagraph), expectedParagraph)

    def test_simple_detect_quote2_quotes(self):
        origParagraph = '<p>bla bla «bla bla» bla bla «bla bla» bla bla</p>'
        expectedParagraph = '<p>bla bla <span type="quote">«bla bla»</span> bla bla <span type="quote">«bla bla»</span> bla bla</p>'

        df = converter.DocumentFixer(etree.parse('converter_data/samediggi-article-48s-before-lang-detection-with-multilingual-tag.xml'))
        gotParagraph = df.detectQuote(etree.fromstring(origParagraph))

        self.assertXmlEqual(etree.tostring(gotParagraph), expectedParagraph)

    def test_detect_quote_with_following_tag(self):
        origParagraph = '<p>bla bla «bla bla» <em>bla bla</em></p>'
        expectedParagraph = '<p>bla bla <span type="quote">«bla bla»</span> <em>bla bla</em></p>'

        df = converter.DocumentFixer(etree.parse('converter_data/samediggi-article-48s-before-lang-detection-with-multilingual-tag.xml'))
        gotParagraph = df.detectQuote(etree.fromstring(origParagraph))

        self.assertXmlEqual(etree.tostring(gotParagraph), expectedParagraph)

    def test_detect_quote_with_tag_infront(self):
        origParagraph = '<p>bla bla <em>bla bla</em> «bla bla»</p>'
        expectedParagraph = '<p>bla bla <em>bla bla</em> <span type="quote">«bla bla»</span></p>'

        df = converter.DocumentFixer(etree.parse('converter_data/samediggi-article-48s-before-lang-detection-with-multilingual-tag.xml'))
        gotParagraph = df.detectQuote(etree.fromstring(origParagraph))

        self.assertXmlEqual(etree.tostring(gotParagraph), expectedParagraph)

    def test_detect_quote_within_tag(self):
        origParagraph = '<p>bla bla <em>bla bla «bla bla»</em></p>'
        expectedParagraph = '<p>bla bla <em>bla bla <span type="quote">«bla bla»</span></em></p>'

        df = converter.DocumentFixer(etree.parse('converter_data/samediggi-article-48s-before-lang-detection-with-multilingual-tag.xml'))
        gotParagraph = df.detectQuote(etree.fromstring(origParagraph))

        self.assertXmlEqual(etree.tostring(gotParagraph), expectedParagraph)

    def test_word_count(self):
        origDoc = etree.parse(io.BytesIO('<document xml:lang="sma" id="no_id"><header><title/><genre/><author><unknown/></author><availability><free/></availability><multilingual/></header><body><p>Bïevnesh naasjovnalen pryövoej bïjre</p><p>2008</p><p>Bïevnesh eejhtegidie, tjidtjieh aehtjieh bielide naasjovnalen pryövoej bïjre giej leah maanah 5. jïh 8. tsiehkine</p></body></document>'))

        expectedDoc = '<document xml:lang="sma" id="no_id"><header><title/><genre/><author><unknown/></author><wordcount>20</wordcount><availability><free/></availability><multilingual/></header><body><p>Bïevnesh naasjovnalen pryövoej bïjre</p><p>2008</p><p>Bïevnesh eejhtegidie, tjidtjieh aehtjieh bielide naasjovnalen pryövoej bïjre giej leah maanah 5. jïh 8. tsiehkine</p></body></document>'

        df = converter.DocumentFixer(origDoc)
        df.setWordCount()

        self.assertXmlEqual(etree.tostring(df.etree), expectedDoc)

class TestXslMaker(unittest.TestCase):
    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal
        """
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)

    def test_get_xsl(self):
        xslmaker = converter.XslMaker('converter_data/samediggi-article-48.html.xsl')
        got = xslmaker.getXsl()

        want = etree.parse('converter_data/test.xsl')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

class TestLanguageDetector(unittest.TestCase):
    """
    Test the functionality of LanguageDetector
    """
    def setUp(self):
        self.document = etree.parse('converter_data/samediggi-article-48s-before-lang-detection-with-multilingual-tag.xml')

    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal
        """
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)

    def test_get_main_lang(self):
        testMainLang = 'sme'
        ld = converter.LanguageDetector(self.document)
        self.assertEqual(testMainLang, ld.getMainlang())

    def test_set_paragraph_language_mainlanguage(self):
        origParagraph = '<p>Sámegiella lea 2004 čavčča rájes standárda giellaválga Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša ahte sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. Buot leat dás dán fitnodaga Service Pack 2-páhkas, maid ferte viežžat ja bidjat dihtorii. Boađus lea ahte buot boahttevaš Microsoft prográmmat dorjot sámegiela. Dattetge sáhttet deaividit váttisvuođat go čálát sámegiela Outlook-kaleandaris dahje e-poastta namahussajis, ja go čálát sámegillii dakkár prográmmain, maid Microsoft ii leat ráhkadan.</p>'
        expectedParagraph = '<p>Sámegiella lea 2004 čavčča rájes standárda giellaválga Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša ahte sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. Buot leat dás dán fitnodaga Service Pack 2-páhkas, maid ferte viežžat ja bidjat dihtorii. Boađus lea ahte buot boahttevaš Microsoft prográmmat dorjot sámegiela. Dattetge sáhttet deaividit váttisvuođat go čálát sámegiela Outlook-kaleandaris dahje e-poastta namahussajis, ja go čálát sámegillii dakkár prográmmain, maid Microsoft ii leat ráhkadan.</p>'

        ld = converter.LanguageDetector(self.document)
        gotParagraph = ld.setParagraphLanguage(etree.fromstring(origParagraph))

        self.assertXmlEqual(etree.tostring(gotParagraph), expectedParagraph)

    def test_set_paragraph_language_mainlanguage_quote_mainlang(self):
        origParagraph = '<p>Sámegiella lea 2004 čavčča rájes standárda giellaválga Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša ahte sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. <span type="quote">«Buot leat dás dán fitnodaga Service Pack 2-páhkas, maid ferte viežžat ja bidjat dihtorii»</span>. Boađus lea ahte buot boahttevaš Microsoft prográmmat dorjot sámegiela. Dattetge sáhttet deaividit váttisvuođat go čálát sámegiela Outlook-kaleandaris dahje e-poastta namahussajis, ja go čálát sámegillii dakkár prográmmain, maid Microsoft ii leat ráhkadan.</p>'
        expectedParagraph = '<p>Sámegiella lea 2004 čavčča rájes standárda giellaválga Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša ahte sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. <span type="quote">«Buot leat dás dán fitnodaga Service Pack 2-páhkas, maid ferte viežžat ja bidjat dihtorii»</span>. Boađus lea ahte buot boahttevaš Microsoft prográmmat dorjot sámegiela. Dattetge sáhttet deaividit váttisvuođat go čálát sámegiela Outlook-kaleandaris dahje e-poastta namahussajis, ja go čálát sámegillii dakkár prográmmain, maid Microsoft ii leat ráhkadan.</p>'

        ld = converter.LanguageDetector(self.document)
        gotParagraph = ld.setParagraphLanguage(etree.fromstring(origParagraph))

        self.assertXmlEqual(etree.tostring(gotParagraph), expectedParagraph)

    def test_set_paragraph_language_mainlanguage_quote_not_mainlang(self):
        origParagraph = '<p>Sámegiella lea 2004 čavčča rájes standárda giellaválga Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša ahte sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. <span type="quote">«Alt finnes i den foreliggende Service Pack 2 fra selskapet, som må lastes ned og installeres på din datamaskin. Konsekvensen er at all framtidig programvare fra Microsoft vil inneholde støtte for samisk»</span>. Boađus lea ahte buot boahttevaš Microsoft prográmmat dorjot sámegiela. Dattetge sáhttet deaividit váttisvuođat go čálát sámegiela Outlook-kaleandaris dahje e-poastta namahussajis, ja go čálát sámegillii dakkár prográmmain, maid Microsoft ii leat ráhkadan.</p>'
        expectedParagraph = '<p>Sámegiella lea 2004 čavčča rájes standárda giellaválga Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša ahte sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. <span type="quote" xml:lang="nob">«Alt finnes i den foreliggende Service Pack 2 fra selskapet, som må lastes ned og installeres på din datamaskin. Konsekvensen er at all framtidig programvare fra Microsoft vil inneholde støtte for samisk»</span>. Boađus lea ahte buot boahttevaš Microsoft prográmmat dorjot sámegiela. Dattetge sáhttet deaividit váttisvuođat go čálát sámegiela Outlook-kaleandaris dahje e-poastta namahussajis, ja go čálát sámegillii dakkár prográmmain, maid Microsoft ii leat ráhkadan.</p>'

        ld = converter.LanguageDetector(self.document)
        gotParagraph = ld.setParagraphLanguage(etree.fromstring(origParagraph))

        self.assertXmlEqual(etree.tostring(gotParagraph), expectedParagraph)

    def test_set_paragraph_language_not_mainlanguage(self):
        origParagraph = '<p>Samisk er fra høsten 2004 et standard språkvalg Microsofts operativsystem Windows XP. I praksis betyr det at samiske bokstaver og formater kan velges i alle programmer. Alt finnes i den foreliggende Service Pack 2 fra selskapet, som må lastes ned og installeres på din datamaskin. Konsekvensen er at all framtidig programvare fra Microsoft vil inneholde støtte for samisk. Du vil imidlertid fremdeles kunne oppleve problemer med å skrive samisk i Outlook-kalenderen eller i tittel-feltet i e-post, og med å skrive samisk i programmer levert av andre enn Microsoft.</p>'
        expectedParagraph = '<p xml:lang="nob">Samisk er fra høsten 2004 et standard språkvalg Microsofts operativsystem Windows XP. I praksis betyr det at samiske bokstaver og formater kan velges i alle programmer. Alt finnes i den foreliggende Service Pack 2 fra selskapet, som må lastes ned og installeres på din datamaskin. Konsekvensen er at all framtidig programvare fra Microsoft vil inneholde støtte for samisk. Du vil imidlertid fremdeles kunne oppleve problemer med å skrive samisk i Outlook-kalenderen eller i tittel-feltet i e-post, og med å skrive samisk i programmer levert av andre enn Microsoft.</p>'

        ld = converter.LanguageDetector(self.document)
        gotParagraph = ld.setParagraphLanguage(etree.fromstring(origParagraph))

        self.assertXmlEqual(etree.tostring(gotParagraph), expectedParagraph)

    def test_remove_quote(self):
        origParagraph = '<p>bla bla <span type="quote">bla1 bla</span> ble ble <span type="quote">bla2 bla</span> <b>bli</b> bli <span type="quote">bla3 bla</span> blo blo</p>'
        expectedParagraph = 'bla bla  ble ble  bli bli  blo blo'

        ld = converter.LanguageDetector(self.document)
        gotParagraph = ld.removeQuote(etree.fromstring(origParagraph))

        self.assertEqual(gotParagraph, expectedParagraph)

    def test_detect_language_with_multilingualtag(self):
        ld = converter.LanguageDetector(etree.parse('converter_data/samediggi-article-48s-before-lang-detection-with-multilingual-tag.xml'))
        ld.detectLanguage()
        gotDocument = ld.getDocument()

        expectedDocument = etree.parse('converter_data/samediggi-article-48s-after-lang-detection-with-multilingual-tag.xml')

        self.assertXmlEqual(etree.tostring(gotDocument), etree.tostring(expectedDocument))

    def test_detect_language_without_multilingualtag(self):
        ld = converter.LanguageDetector(etree.parse('converter_data/samediggi-article-48s-before-lang-detection-without-multilingual-tag.xml'))
        ld.detectLanguage()
        gotDocument = ld.getDocument()

        expectedDocument = etree.parse('converter_data/samediggi-article-48s-after-lang-detection-without-multilingual-tag.xml')

        self.assertXmlEqual(etree.tostring(gotDocument), etree.tostring(expectedDocument))

class TestDocumentTester(unittest.TestCase):
    def setUp(self):
        pass

    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal
        """
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)


    def test_remove_foreign_language1(self):
        origDoc = etree.parse(io.BytesIO('<document xml:lang="sma" id="no_id"><header><title/><genre/><author><unknown/></author><availability><free/></availability><multilingual/></header><body><p>Bïevnesh naasjovnalen</p></body></document>'))

        expectedDoc = '<document xml:lang="sma" id="no_id"><header><title/><genre/><author><unknown/></author><availability><free/></availability><multilingual/></header><body><p>Bïevnesh naasjovnalen</p></body></document>'

        dt = converter.DocumentTester(origDoc)
        dt.removeForeignLanguage()

        self.assertXmlEqual(etree.tostring(dt.document), expectedDoc)

    def test_remove_foreign_language2(self):
        origDoc = etree.parse(io.BytesIO('<document xml:lang="sma" id="no_id"><header><title/><genre/><author><unknown/></author><availability><free/></availability><multilingual/></header><body><p xml:lang="nob">Nasjonale prøver</p></body></document>'))

        expectedDoc = '<document xml:lang="sma" id="no_id"><header><title/><genre/><author><unknown/></author><availability><free/></availability><multilingual/></header><body></body></document>'

        dt = converter.DocumentTester(origDoc)
        dt.removeForeignLanguage()

        self.assertXmlEqual(etree.tostring(dt.document), expectedDoc)

    def test_remove_foreign_language3(self):
        origDoc = etree.parse(io.BytesIO('<document xml:lang="sma" id="no_id"><header><title/><genre/><author><unknown/></author><availability><free/></availability><multilingual/></header><body><p xml:lang="nob">Nasjonale prøver<span type="quote">Bïevnesh naasjovnalen </span></p></body></document>'))

        expectedDoc = '<document xml:lang="sma" id="no_id"><header><title/><genre/><author><unknown/></author><availability><free/></availability><multilingual/></header><body><p>Bïevnesh naasjovnalen </p></body></document>'

        dt = converter.DocumentTester(origDoc)
        dt.removeForeignLanguage()

        self.assertXmlEqual(etree.tostring(dt.document), expectedDoc)

    def test_remove_foreign_language4(self):
        origDoc = etree.parse(io.BytesIO('<document xml:lang="sma" id="no_id"><header><title/><genre/><author><unknown/></author><availability><free/></availability><multilingual/></header><body><p>Bïevnesh naasjovnalen <span type="quote" xml:lang="nob">Nasjonale prøver</span></p></body></document>'))

        expectedDoc = '<document xml:lang="sma" id="no_id"><header><title/><genre/><author><unknown/></author><availability><free/></availability><multilingual/></header><body><p>Bïevnesh naasjovnalen <span type="quote" xml:lang="nob"></span></p></body></document>'

        dt = converter.DocumentTester(origDoc)
        dt.removeForeignLanguage()

        self.assertXmlEqual(etree.tostring(dt.document), expectedDoc)

    def test_get_main_lang_ratio(self):
        origDoc = etree.parse(io.BytesIO('<document xml:lang="sma" id="no_id"><header><title/><genre/><author><unknown/></author><wordcount>12</wordcount><availability><free/></availability><multilingual/></header><body><p>Bïevnesh naasjovnalen</p><p xml:lang="nob">Nasjonale prøver</p><p xml:lang="nob">Nasjonale prøver <span type="quote">Bïevnesh naasjovnalen </span></p><p>Bïevnesh naasjovnalen <span type="quote" xml:lang="nob">Nasjonale prøver</span></p></body></document>'))

        dt = converter.DocumentTester(origDoc)

        self.assertEqual(dt.getMainlangRatio(), 0.50)

    def test_get_unknown_words_ratio(self):
        origDoc = etree.parse(io.BytesIO('<document xml:lang="sme" id="no_id"><header><title/><genre/><author><unknown/></author><wordcount>86</wordcount><availability><free/></availability><multilingual/></header><body><p>Sámegiellaqw leaqw 2004 čavččaqw rájesqw standárdaqw giellaválgaqw Microsoftaqw qwoperatiivavuogádagas qwWindows qwXP. qwDat mearkkaša ahte sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. <span type="quote" xml:lang="nob">«Alt finnes i den foreliggende Service Pack 2 fra selskapet, som må lastes ned og installeres på din datamaskin. Konsekvensen er at all framtidig programvare fra Microsoft vil inneholde støtte for samisk»</span>. Boađus lea ahte buot boahttevaš Microsoft prográmmat dorjot sámegiela. Dattetge sáhttet deaividit váttisvuođat go čálát sámegiela Outlook-kaleandaris dahje e-poastta namahussajis, ja go čálát sámegillii dakkár prográmmain, maid Microsoft ii leat ráhkadan.</p></body></document>'))

        dt = converter.DocumentTester(origDoc)

        self.assertEqual(decimal.Decimal(dt.getUnknownWordsRatio()).quantize(decimal.Decimal('.1'), rounding=decimal.ROUND_DOWN) , decimal.Decimal('0.2').quantize(decimal.Decimal('.1'), rounding=decimal.ROUND_DOWN))

class TestDocumentFixer(unittest.TestCase):
    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal
        """
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)

    def test_fix__body_encoding(self):
        newstext = converter.PlaintextConverter('converter_data/assu97-mac-sami.txt')

        eg = converter.DocumentFixer(newstext.convert2intermediate())
        got = eg.fixBodyEncoding()

        want = etree.parse('converter_data/assu97-fixedutf8.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_replace_ligatures(self):
        svgtext = converter.SVGConverter('converter_data/Riddu_Riddu_avis_TXT.200923.svg')
        eg = converter.DocumentFixer(etree.fromstring(etree.tostring(svgtext.convert2intermediate())))
        got = eg.fixBodyEncoding()

        want = etree.parse('converter_data/Riddu_Riddu_avis_TXT.200923.xml')

        self.assertXmlEqual(etree.tostring(got), etree.tostring(want))

    def test_simple_detect_quote1(self):
        origParagraph = '<p>bla bla "bla bla" bla bla </p>'
        expectedParagraph = '<p>bla bla <span type="quote">"bla bla"</span> bla bla</p>'

        df = converter.DocumentFixer(etree.parse('converter_data/samediggi-article-48s-before-lang-detection-with-multilingual-tag.xml'))
        gotParagraph = df.detectQuote(etree.fromstring(origParagraph))

        self.assertXmlEqual(etree.tostring(gotParagraph), expectedParagraph)

    def test_simple_detect_quote2(self):
        origParagraph = '<p>bla bla “bla bla” bla bla</p>'
        expectedParagraph = '<p>bla bla <span type="quote">“bla bla”</span> bla bla</p>'

        df = converter.DocumentFixer(etree.parse('converter_data/samediggi-article-48s-before-lang-detection-with-multilingual-tag.xml'))
        gotParagraph = df.detectQuote(etree.fromstring(origParagraph))

        self.assertXmlEqual(etree.tostring(gotParagraph), expectedParagraph)

    def test_simple_detect_quote3(self):
        origParagraph = '<p>bla bla «bla bla» bla bla</p>'
        expectedParagraph = '<p>bla bla <span type="quote">«bla bla»</span> bla bla</p>'

        df = converter.DocumentFixer(etree.parse('converter_data/samediggi-article-48s-before-lang-detection-with-multilingual-tag.xml'))
        gotParagraph = df.detectQuote(etree.fromstring(origParagraph))

        self.assertXmlEqual(etree.tostring(gotParagraph), expectedParagraph)

    def test_simple_detect_quote4(self):
        origParagraph = '<p type="title">Sámegiel čálamearkkat Windows XP várás.</p>'
        expectedParagraph = '<p type="title">Sámegiel čálamearkkat Windows XP várás.</p>'

        df = converter.DocumentFixer(etree.parse('converter_data/samediggi-article-48s-before-lang-detection-with-multilingual-tag.xml'))
        gotParagraph = df.detectQuote(etree.fromstring(origParagraph))

        self.assertXmlEqual(etree.tostring(gotParagraph), expectedParagraph)

    def test_simple_detect_quote2_quotes(self):
        origParagraph = '<p>bla bla «bla bla» bla bla «bla bla» bla bla</p>'
        expectedParagraph = '<p>bla bla <span type="quote">«bla bla»</span> bla bla <span type="quote">«bla bla»</span> bla bla</p>'

        df = converter.DocumentFixer(etree.parse('converter_data/samediggi-article-48s-before-lang-detection-with-multilingual-tag.xml'))
        gotParagraph = df.detectQuote(etree.fromstring(origParagraph))

        self.assertXmlEqual(etree.tostring(gotParagraph), expectedParagraph)

    def test_detect_quote_with_following_tag(self):
        origParagraph = '<p>bla bla «bla bla» <em>bla bla</em></p>'
        expectedParagraph = '<p>bla bla <span type="quote">«bla bla»</span> <em>bla bla</em></p>'

        df = converter.DocumentFixer(etree.parse('converter_data/samediggi-article-48s-before-lang-detection-with-multilingual-tag.xml'))
        gotParagraph = df.detectQuote(etree.fromstring(origParagraph))

        self.assertXmlEqual(etree.tostring(gotParagraph), expectedParagraph)

    def test_detect_quote_with_tag_infront(self):
        origParagraph = '<p>bla bla <em>bla bla</em> «bla bla»</p>'
        expectedParagraph = '<p>bla bla <em>bla bla</em> <span type="quote">«bla bla»</span></p>'

        df = converter.DocumentFixer(etree.parse('converter_data/samediggi-article-48s-before-lang-detection-with-multilingual-tag.xml'))
        gotParagraph = df.detectQuote(etree.fromstring(origParagraph))

        self.assertXmlEqual(etree.tostring(gotParagraph), expectedParagraph)

    def test_detect_quote_within_tag(self):
        origParagraph = '<p>bla bla <em>bla bla «bla bla»</em></p>'
        expectedParagraph = '<p>bla bla <em>bla bla <span type="quote">«bla bla»</span></em></p>'

        df = converter.DocumentFixer(etree.parse('converter_data/samediggi-article-48s-before-lang-detection-with-multilingual-tag.xml'))
        gotParagraph = df.detectQuote(etree.fromstring(origParagraph))

        self.assertXmlEqual(etree.tostring(gotParagraph), expectedParagraph)

    def test_word_count(self):
        origDoc = etree.parse(io.BytesIO('<document xml:lang="sma" id="no_id"><header><title/><genre/><author><unknown/></author><availability><free/></availability><multilingual/></header><body><p>Bïevnesh naasjovnalen pryövoej bïjre</p><p>2008</p><p>Bïevnesh eejhtegidie, tjidtjieh aehtjieh bielide naasjovnalen pryövoej bïjre giej leah maanah 5. jïh 8. tsiehkine</p></body></document>'))

        expectedDoc = '<document xml:lang="sma" id="no_id"><header><title/><genre/><author><unknown/></author><wordcount>20</wordcount><availability><free/></availability><multilingual/></header><body><p>Bïevnesh naasjovnalen pryövoej bïjre</p><p>2008</p><p>Bïevnesh eejhtegidie, tjidtjieh aehtjieh bielide naasjovnalen pryövoej bïjre giej leah maanah 5. jïh 8. tsiehkine</p></body></document>'

        df = converter.DocumentFixer(origDoc)
        df.setWordCount()

        self.assertXmlEqual(etree.tostring(df.etree), expectedDoc)

