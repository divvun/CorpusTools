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
#   Copyright 2011-2014 Børre Gaup <borre.gaup@uit.no>
#

import unittest
from lxml import etree
from lxml import doctestcompare
import os
import doctest
import tempfile

from corpustools import parallelize
from corpustools import text_cat
from corpustools import generate_anchor_list


here = os.path.dirname(__file__)


class TestCorpusXMLFile(unittest.TestCase):
    """
    A test class for the CorpusXMLFile class
    """
    def setUp(self):
        self.pfile = parallelize.CorpusXMLFile(
            os.path.join(
                os.environ['GTFREE'],
                "prestable/converted/sme/facta/skuvlahistorja2/"
                "aarseth2-s.htm.xml"))

    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal
        """
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(
                doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)

    def test_basename(self):
        self.assertEqual(self.pfile.get_basename(), "aarseth2-s.htm.xml")

    def test_dirname(self):
        self.assertEqual(
            self.pfile.get_dirname(),
            os.path.join(os.environ['GTFREE'],
                         "prestable/converted/sme/facta/skuvlahistorja2"))

    def test_name(self):
        self.assertEqual(
            self.pfile.get_name(),
            os.path.join(
                os.environ['GTFREE'],
                "prestable/converted/sme/facta/skuvlahistorja2/"
                "aarseth2-s.htm.xml"))

    def test_lang(self):
        self.assertEqual(self.pfile.get_lang(), "sme")

    def test_get_parallel_basename(self):
        self.assertEqual(self.pfile.get_parallel_basename('nob'),
                         "aarseth2-n.htm")

    def test_get_parallel_filename(self):
        self.assertEqual(
            self.pfile.get_parallel_filename('nob'),
            os.path.join(
                os.environ['GTFREE'],
                "prestable/converted/nob/facta/skuvlahistorja2/"
                "aarseth2-n.htm.xml"))

    def test_get_original_filename(self):
        self.assertEqual(
            self.pfile.get_original_filename(),
            os.path.join(
                os.environ['GTFREE'],
                "orig/sme/facta/skuvlahistorja2/aarseth2-s.htm"))

    def test_get_translated_from(self):
        self.assertEqual(self.pfile.get_translated_from(), "nob")

    def test_get_word_count(self):
        corpusfile = parallelize.CorpusXMLFile(
            os.path.join(
                here,
                'parallelize_data/aarseth2-n-with-version.htm.xml'))
        self.assertEqual(corpusfile.get_word_count(), "4009")

    def test_remove_version(self):
        file_with_version = parallelize.CorpusXMLFile(
            os.path.join(
                here,
                'parallelize_data/aarseth2-n-with-version.htm.xml'))
        file_without_version = parallelize.CorpusXMLFile(
            os.path.join(
                here,
                'parallelize_data/aarseth2-n-without-version.htm.xml'))

        file_with_version.remove_version()

        got = etree.tostring(file_without_version.get_etree())
        want = etree.tostring(file_with_version.get_etree())

        self.assertXmlEqual(got, want)

    def test_remove_skip(self):
        file_with_skip = parallelize.CorpusXMLFile(
            os.path.join(
                here,
                'parallelize_data/aarseth2-s-with-skip.htm.xml'))
        file_without_skip = parallelize.CorpusXMLFile(
            os.path.join(
                here,
                'parallelize_data/aarseth2-s-without-skip.htm.xml'))

        file_with_skip.remove_skip()

        got = etree.tostring(file_without_skip.get_etree())
        want = etree.tostring(file_with_skip.get_etree())

        self.assertXmlEqual(got, want)

    def test_move_later(self):
        file_with_later = parallelize.CorpusXMLFile(
            os.path.join(
                here,
                'parallelize_data/aarseth2-s-with-later.htm.xml'))
        file_with_moved_later = parallelize.CorpusXMLFile(
            os.path.join(
                here,
                'parallelize_data/aarseth2-s-with-moved-later.htm.xml'))

        file_with_later.move_later()
        got = etree.tostring(file_with_moved_later.get_etree())
        want = etree.tostring(file_with_later.get_etree())
        self.assertXmlEqual(got, want)


class TestSentenceDivider(unittest.TestCase):
    """A test class for the SentenceDivider class
    """
    def setUp(self):
        self.sentence_divider = parallelize.SentenceDivider(
            os.path.join(
                here,
                "parallelize_data/finnmarkkulahka_web_lettere.pdf.xml"))

    def assertXmlEqual(self, got, want):
        """
        Check if two xml snippets are equal
        """
        string_got = etree.tostring(got, pretty_print=True)
        string_want = etree.tostring(want, pretty_print=True)

        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(string_want, string_got, 0):
            message = checker.output_difference(
                doctest.Example("", string_want),
                string_got, 0).encode('utf-8')
            raise AssertionError(message)

    def test_constructor(self):
        """Check that the constructor makes what it is suppposed to
        """
        self.assertEqual(self.sentence_divider.sentence_counter, 0)
        self.assertEqual(self.sentence_divider.doc_lang, 'sme')
        self.assertEqual(self.sentence_divider.input_etree.__class__.__name__,
                         '_ElementTree')

    def test_process_all_paragraphs(self):
        self.sentence_divider.process_all_paragraphs()
        got = self.sentence_divider.document

        want = etree.parse(
            os.path.join(
                here,
                'parallelize_data/'
                'finnmarkkulahka_web_lettere.pdfsme_sent.xml.test'))

        self.assertXmlEqual(got, want)

    def test_process_one_paragraph(self):
        """Check the output of process_one_paragraph
        """
        self.sentence_divider.doc_lang = 'sme'
        p = etree.XML(
            '<p>Jápmá go sámi kultuvra veahážiid mielde go nuorat ovdal '
            'guldalit Britney Spears go Áilluhačča? máksá Finnmárkkuopmodat. '
            '§ 10 Áššit meahcceeatnamiid</p>')
        got = self.sentence_divider.process_elts([p])[0]
        want = etree.XML(
            '<p><s id="0">Jápmá go sámi kultuvra veahážiid mielde go nuorat '
            'ovdal guldalit Britney Spears go Áilluhačča ?</s><s id="1">'
            'máksá Finnmárkkuopmodat .</s><s id="2">§ 10 Áššit '
            'meahcceeatnamiid </s></p>')
        self.assertXmlEqual(got, want)

        p = etree.XML(
            '<p>Stuora oassi Romssa universitehta doaimmain lea juohkit '
            'dieđuid sámi, norgga ja riikkaidgaskasaš dutkanbirrasiidda, '
            'sámi ja norgga eiseválddiide, ja sámi servodagaide (geahča '
            'mielddus A <em type="italic"><span type="quote">“Romssa '
            'universitehta ja guoskevaš institušuvnnaid sámi dutkan ja '
            'oahpahus”</span></em>  álggahusa ).</p>')
        got = self.sentence_divider.process_elts([p])[0]
        want = etree.XML(
            '<p><s id="3">Stuora oassi Romssa universitehta doaimmain lea '
            'juohkit dieđuid sámi , norgga ja riikkaidgaskasaš '
            'dutkanbirrasiidda , sámi ja norgga eiseválddiide , ja sámi '
            'servodagaide ( geahča mielddus A “ Romssa universitehta ja '
            'guoskevaš institušuvnnaid sámi dutkan ja oahpahus ” álggahusa ) '
            '.</s></p>')
        self.assertXmlEqual(got, want)

        self.sentence_divider.doc_lang = 'nob'
        p = etree.XML(
            '<p>Artikkel i boka Samisk skolehistorie 2 . Davvi Girji '
            '2007.</p>')
        got = self.sentence_divider.process_elts([p])[0]
        want = etree.XML(
            '<p><s id="4">Artikkel i boka Samisk skolehistorie 2 .</s>'
            '<s id="5">Davvi Girji 2007 .</s></p>')
        self.assertXmlEqual(got, want)

        p = etree.XML(
            '<p><em type="bold">Bjørn Aarseth med elever på skitur - på '
            '1950-tallet.</em> (Foto: Trygve Madsen)</p>')
        got = self.sentence_divider.process_elts([p])[0]
        want = etree.XML(
            '<p><s id="6">Bjørn Aarseth med elever på skitur - på '
            '1950-tallet .</s><s id="7">( Foto : Trygve Madsen )</s></p>')
        self.assertXmlEqual(got, want)

        p = etree.XML(
            '<p>finne rom for etablering av en fast tilskuddsordning til '
            'allerede etablerte språksentra..</p>')
        got = self.sentence_divider.process_elts([p])[0]
        want = etree.XML(
            '<p><s id="8">finne rom for etablering av en fast '
            'tilskuddsordning til allerede etablerte språksentra . .</s></p>')
        self.assertXmlEqual(got, want)

        p = etree.XML('<p>elevene skal få!  Sametingsrådet mener målet</p>')
        got = self.sentence_divider.process_elts([p])[0]
        want = etree.XML(
            '<p><s id="9">elevene skal få !</s><s id="10">Sametingsrådet '
            'mener målet</s></p>')
        self.assertXmlEqual(got, want)

        p = etree.XML(
            '<p>Sametinget..................................................'
            '...............................................................'
            '............. 2 Utdannings- og forskningsdepartementet.........'
            '...............................................................'
            '....... 3 Kultur- og kirkedepartementet .......................'
            '...............................................................'
            '......... 7 Kommunal- og regionaldepartementet.................'
            '...............................................................'
            '... 9</p>')
        got = self.sentence_divider.process_elts([p])[0]
        want = etree.XML(
            '<p><s id="11">Sametinget ... 2 Utdannings- og '
            'forskningsdepartementet ... 3 Kultur- og kirkedepartementet ... '
            '7 Kommunal- og regionaldepartementet ... 9</s></p>')
        self.assertXmlEqual(got, want)

        self.sentence_divider.doc_lang = 'sme'
        p = etree.XML(
            '<p>Allaskuvllas lea maiddái ovddasvástádus julevsámegielas ja '
            'máttasámegielas. (... ). Berre leat vejolaš váldit '
            'oahpaheaddjeoahpu, mas erenoamáš deaddu lea davvi-, julev-, '
            'máttasámegielas ja kultuvrras.</p>')
        got = self.sentence_divider.process_elts([p])[0]
        want = etree.XML(
            '<p><s id="12">Allaskuvllas lea maiddái ovddasvástádus '
            'julevsámegielas ja máttasámegielas .</s><s id="13">Berre leat '
            'vejolaš váldit oahpaheaddjeoahpu , mas erenoamáš deaddu lea '
            'davvi- , julev- , máttasámegielas ja kultuvrras .</s></p>')
        self.assertXmlEqual(got, want)

    def test_dot_followed_by_dot(self):
        """Test of how process_one_paragraph handles a paragraph
        with . and ... in the end.
        tca2 doesn't accept sentences without real letters, so we have to make
        sure the ... doesn't end up alone inside a s tag"""
        self.sentence_divider.doc_lang = 'nob'
        p = etree.XML(
            '<p>Alt det som har med norsk å gjøre, har jeg gruet meg for og '
            'hatet hele mitt liv - og kommer kanskje til å fortsette med '
            'det. ...</p>')
        got = self.sentence_divider.process_elts([p])[0]
        want = etree.XML(
            '<p><s id="0">Alt det som har med norsk å gjøre , har jeg gruet '
            'meg for og hatet hele mitt liv - og kommer kanskje til å '
            'fortsette med det . ...</s></p>')
        self.assertXmlEqual(got, want)

    def test_quotemarks(self):
        """Test how SentenceDivider handles quotemarks
        """
        self.sentence_divider.doc_lang = 'nob'
        p = etree.XML(
            '<p>Forsøksrådet for skoleverket godkjente det praktiske '
            'opplegget for kurset i brev av 18/8 1959 og uttalte da bl.a.: '
            '«Selve innholdet i kurset virker gjennomtenkt og underbygd og '
            'ser ut til å konsentrere seg om vesentlige emner som vil få '
            'stor betydning for elevene i deres yrkesarbeid. Med flyttsame-'
            'kunnskapen som bakgrunn er det grunn til å vente seg mye av '
            'dette kursopplegget.» Med denne tillitserklæring i ryggen har '
            'vi så fra år til år søkt å forbedre kursoppleggene til vi '
            'foran 1963-kursene står med planer som vi anser '
            'tilfredsstillende , men ikke endelige .)</p>')
        got = self.sentence_divider.process_elts([p])[0]
        want = etree.XML(
            '<p><s id="0">Forsøksrådet for skoleverket godkjente det '
            'praktiske opplegget for kurset i brev av 18/8 1959 og uttalte '
            'da bl.a. : « Selve innholdet i kurset virker gjennomtenkt og '
            'underbygd og ser ut til å konsentrere seg om vesentlige emner '
            'som vil få stor betydning for elevene i deres yrkesarbeid .</s>'
            '<s id="1"> Med flyttsame-kunnskapen som bakgrunn er det grunn '
            'til å vente seg mye av dette kursopplegget . »</s><s id="2">'
            'Med denne tillitserklæring i ryggen har vi så fra år til år '
            'søkt å forbedre kursoppleggene til vi foran 1963-kursene står '
            'med planer som vi anser tilfredsstillende , men ikke '
            'endelige . )</s></p>')
        self.assertXmlEqual(got, want)

    def test_spurious_comma(self):
        self.sentence_divider.doc_lang = 'nob'
        p = etree.XML(
            '<p>Etter Sametingets oppfatning vil forslagene til ny § 1 Lovens '
            'formål og § 2 Kulturminner og kulturmiljØer - definisjoner; '
            'gjøre at det blir en større grad av overensstemmelse mellom '
            'lovens begreper og det begrepsapparatet som er nyttet innenfor '
            'samisk kulturminnevern. , </p>')
        got = self.sentence_divider.process_elts([p])[0]
        want = etree.XML(
            '<p><s id="0">Etter Sametingets oppfatning vil forslagene til ny '
            '§ 1 Lovens formål og § 2 Kulturminner og kulturmiljØer - '
            'definisjoner ; gjøre at det blir en større grad av '
            'overensstemmelse mellom lovens begreper og det begrepsapparatet '
            'som er nyttet innenfor samisk kulturminnevern .</s></p>')
        self.assertXmlEqual(got, want)

        self.sentence_divider.doc_lang = 'nob'
        p = etree.XML('<p>, </p>')
        got = self.sentence_divider.process_elts([p])[0]
        want = etree.XML('<p/>')
        self.assertXmlEqual(got, want)

    def test_spurious_dot(self):
        self.sentence_divider.doc_lang = 'nob'
        p = etree.XML('<p>..</p>')
        got = self.sentence_divider.process_elts([p])[0]
        want = etree.XML('<p/>')
        self.assertXmlEqual(got, want)

    def test_lone_questionmark(self):
        self.sentence_divider.doc_lang = 'nob'
        p = etree.XML('<p>?</p>')
        got = self.sentence_divider.process_elts([p])[0]
        want = etree.XML('<p/>')
        self.assertXmlEqual(got, want)

    def test_dot_in_sentence_start(self):
        self.sentence_divider.doc_lang = 'nob'
        p = etree.XML('<p> . Cálliidlágádus 1999)</p>')
        got = self.sentence_divider.process_elts([p])[0]
        want = etree.XML('<p><s id="0">Cálliidlágádus 1999 )</s></p>')
        self.assertXmlEqual(got, want)

    def test_span_in_p(self):
        self.sentence_divider.doc_lang = 'nob'
        p = etree.XML(
            '<p>( Styrke institusjonssamarbeidet (Urfolksnettverket og '
            '<span type="quote">“Forum for urfolksspørsmål i '
            'bistanden”</span>)</p>')
        got = self.sentence_divider.process_elts([p])[0]
        want = etree.XML(
            '<p><s id="0">( Styrke institusjonssamarbeidet ( '
            'Urfolksnettverket og “ Forum for urfolksspørsmål i bistanden ” )'
            '</s></p>')
        self.assertXmlEqual(got, want)

    def test_make_sentence(self):
        s = self.sentence_divider.make_sentence(
            [u'Sámerievtti ', u'ovdáneapmi', u'lea', u'dahkan',
             u'vuđđosa', u'Finnmárkkuláhkii'])

        self.assertEqual(s.attrib["id"], '0')
        self.assertEqual(
            s.text,
            u'Sámerievtti ovdáneapmi lea dahkan vuđđosa Finnmárkkuláhkii')


class TestParallelize(unittest.TestCase):
    """
    A test class for the Parallelize class
    """
    def setUp(self):
        self.parallelize = parallelize.ParallelizeTCA2(
            os.path.join(
                os.environ['GTFREE'],
                'prestable/converted/sme/facta/skuvlahistorja2/'
                'aarseth2-s.htm.xml'),
            "nob")

    def test_orig_path(self):
        self.assertEqual(
            self.parallelize.get_origfile1(),
            os.path.join(
                os.environ['GTFREE'],
                'prestable/converted/nob/facta/skuvlahistorja2/'
                'aarseth2-n.htm.xml'))

    def test_parallel_path(self):
        self.assertEqual(
            self.parallelize.get_origfile2(),
            os.path.join(
                os.environ['GTFREE'],
                'prestable/converted/sme/facta/skuvlahistorja2/'
                'aarseth2-s.htm.xml'))

    def test_lang1(self):
        self.assertEqual(self.parallelize.get_lang1(), "nob")

    def test_lang2(self):
        self.assertEqual(self.parallelize.get_lang2(), "sme")

    def test_get_sent_filename(self):
        self.assertEqual(
            self.parallelize.get_sent_filename(
                self.parallelize.get_origfiles()[0]),
            os.path.join(os.environ['GTFREE'],
                         "tmp/aarseth2-n.htmnob_sent.xml"))

    def test_divide_p_into_sentences(self):
        self.parallelize.divide_p_into_sentences()

    def test_parallize_files(self):
        print self.parallelize.parallelize_files()

    def test_generate_anchor_file(self):
        self.assertEqual(self.parallelize.generate_anchor_file(),
                         os.path.join(os.environ['GTFREE'],
                                      'anchor-nobsme.txt'))

class TestGenerateAnchorFile(unittest.TestCase):
    """
    A test class for the GenerateAnchorList class
    """
    def test_generate_anchor_output(self):
        tmpdir = tempfile.mkdtemp()
        gal = generate_anchor_list.GenerateAnchorList('nob', 'sme', tmpdir)
        gal.generate_file([os.path.join(here, 'parallelize_data/anchor.txt')],
                          quiet=True)
        want = open(os.path.join(here, 'parallelize_data/anchor-nobsme.txt')).read()
        got = open(os.path.join(tmpdir, 'anchor-nobsme.txt')).read()
        self.assertEqual(got, want)


class TestTmx(unittest.TestCase):
    """
    A test class for the Tmx class
    """
    def setUp(self):
        self.tmx = parallelize.Tmx(etree.parse(
            os.path.join(
                here,
                'parallelize_data/aarseth2-n.htm.toktmx')))

    def assertXmlEqual(self, got, want):
        """
        Check if two xml snippets are equal
        """
        string_got = etree.tostring(got, pretty_print=True)
        string_want = etree.tostring(want, pretty_print=True)

        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(string_want, string_got, 0):
            message = checker.output_difference(
                doctest.Example("", string_want),
                string_got, 0).encode('utf-8')
            raise AssertionError(message)

    def test_get_src_lang(self):
        """Test the get_src_lang routine
        """
        self.assertEqual(self.tmx.get_src_lang(), "nob")

    def test_tu_to_string(self):
        tu = etree.XML(
            '<tu><tuv xml:lang="sme"><seg>Sámegiella</seg></tuv>'
            '<tuv xml:lang="nob"><seg>Samisk</seg></tuv></tu>')

        self.assertEqual(self.tmx.tu_to_string(tu), "Sámegiella\tSamisk\n")

    def test_tuv_to_string(self):
        tuv = etree.XML('<tuv xml:lang="sme"><seg>Sámegiella</seg></tuv>')

        self.assertEqual(self.tmx.tuv_to_string(tuv), "Sámegiella")

    def test_lang_to_string_list(self):
        toktmx_txt_name = os.path.join(
            here,
            'parallelize_data/aarseth2-n.htm.toktmx.as.txt')
        with open(toktmx_txt_name, 'r') as toktmx_txt:
            string_list = toktmx_txt.readlines()

            nob_list = []
            sme_list = []
            for string in string_list:
                pair_list = string.split('\t')
                nob_list.append(pair_list[0])
                sme_list.append(pair_list[1].strip())

            self.assertEqual(self.tmx.lang_to_stringlist('nob'), nob_list)
            self.assertEqual(self.tmx.lang_to_stringlist('sme'), sme_list)

    def test_tmx_to_stringlist(self):
        toktmx_txt_name = os.path.join(
            here,
            'parallelize_data/aarseth2-n.htm.toktmx.as.txt')
        with open(toktmx_txt_name, 'r') as toktmx_txt:
            want_list = toktmx_txt.readlines()
            # self.maxDiff = None
            self.assertEqual(self.tmx.tmx_to_stringlist(), want_list)

    def test_prettify_segs(self):
        wantXml = etree.XML(
            '<tu><tuv xml:lang="nob"><seg>ubba gubba. ibba gibba.</seg></tuv>'
            '<tuv xml:lang="sme"><seg>abba gabba. ebba gebba.'
            '</seg></tuv></tu>')
        gotXml = etree.XML(
            '<tu><tuv xml:lang="nob"><seg>ubba gubba. ibba gibba.\n</seg>'
            '</tuv><tuv xml:lang="sme"><seg>abba gabba. ebba gebba.\n</seg>'
            '</tuv></tu>')
        self.assertXmlEqual(self.tmx.prettify_segs(gotXml), wantXml)

    def test_check_if_emtpy_seg(self):
        empty1 = etree.XML(
            '<tu><tuv xml:lang="nob"><seg>ubba gubba. ibba gibba.</seg></tuv>'
            '<tuv xml:lang="sme"><seg></seg></tuv></tu>')
        self.assertRaises(AttributeError, self.tmx.check_if_emtpy_seg, empty1)

        empty2 = etree.XML(
            '<tu><tuv xml:lang="nob"><seg></seg></tuv><tuv xml:lang="sme">'
            '<seg>abba gabba. ebba gebba.</seg></tuv></tu>')
        self.assertRaises(AttributeError, self.tmx.check_if_emtpy_seg, empty2)

    def test_remove_unwanted_space_from_segs(self):
        wantXml = etree.XML(
            '<tu><tuv xml:lang="nob"><seg>[30] (juli) «skoleturer».</seg>'
            '</tuv><tuv xml:lang="sme"><seg>[30] (suoidnemánnu) '
            '«skuvlatuvrrat».</seg></tuv></tu>')
        gotXml = etree.XML(
            '<tu><tuv xml:lang="nob"><seg>[ 30 ] ( juli ) « skoleturer » .\n'
            '</seg></tuv><tuv xml:lang="sme"><seg>[ 30 ] ( suoidnemánnu ) « '
            'skuvlatuvrrat » .\n</seg></tuv></tu>')
        self.assertXmlEqual(self.tmx.remove_unwanted_space_from_segs(gotXml),
                            wantXml)

    def test_remove_unwanted_space_from_string(self):
        got = self.tmx.remove_unwanted_space_from_string(
            u'sámesearvvi ; [ 31 ] ( suoidnemánnu ) « skuvlatuvrrat » '
            u'bargu lea :  okta , guokte .')
        want = (
            u'sámesearvvi; [31] (suoidnemánnu) «skuvlatuvrrat» bargu lea: '
            'okta, guokte.')
        self.assertEqual(got, want)

    def test_remove_tu_with_empty_seg(self):
        got_tmx = parallelize.Tmx(etree.parse(
            os.path.join(
                here,
                'parallelize_data/aarseth2-n.htm.toktmx')))
        got_tmx.remove_tu_with_empty_seg()

        want_tmx = parallelize.Tmx(
            etree.parse(
                os.path.join(
                    here,
                    'parallelize_data/'
                    'aarseth2-n-without-empty-seg.htm.toktmx')))

        self.assertXmlEqual(got_tmx.get_tmx(), want_tmx.get_tmx())

    def test_check_language(self):
        self.tmx.language_guesser = text_cat.Classifier(None)

        tu_with_sme = etree.XML(
            '<tu><tuv xml:lang="sme"><seg>Bargo- ja '
            'searvadahttindepartemeanta (BSD) nanne sámiid árbedieđu '
            'čohkkema, systematiserema ja gaskkusteami Norggas oktiibuot 1,6 '
            'milj. ruvnnuin.</seg></tuv><tuv '
            'xml:lang="nob"><seg>Samisk</seg></tuv></tu>')

        self.assertTrue(self.tmx.check_language(tu_with_sme, 'sme'))

        tu_with_sma = etree.XML(
            '<tu><tuv xml:lang="sme"><seg>Barkoe- jïh ektiedimmiedepartemente '
            '(AID) galka nænnoestidh dovne tjöönghkeme- jïh öörnemebarkoem , '
            'jïh aaj bæjkoehtimmiem saemien aerpiemaahtoen muhteste '
            'Nöörjesne, abpe 1,6 millijovnh kråvnajgujmie.</seg></tuv>'
            '<tuv xml:lang="nob"><seg>Samisk</seg></tuv></tu>')

        self.assertFalse(self.tmx.check_language(tu_with_sma, 'sme'))


class TestTca2ToTmx(unittest.TestCase):
    """
    A test class for the Tca2ToTmx class
    """
    def setUp(self):
        """
        Hand the data from the Parallelize class to the tmx class
        """
        para = parallelize.Parallelize(
            os.path.join(
                os.environ['GTFREE'],
                'prestable/converted/sme/facta/skuvlahistorja2/'
                'aarseth2-s.htm.xml'),
            "nob")

        self.para = para
        self.tmx = parallelize.Tca2ToTmx(para.get_origfiles(),
                                         para.get_sentfiles())

    def assertXmlEqual(self, got, want):
        """
        Check if two xml snippets are equal
        """
        string_got = etree.tostring(got, pretty_print=True)
        string_want = etree.tostring(want, pretty_print=True)

        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(string_want, string_got, 0):
            message = checker.output_difference(
                doctest.Example("", string_want),
                string_got, 0).encode('utf-8')
            raise AssertionError(message)

    def test_make_tu(self):
        line1 = '<s id="1">ubba gubba.</s> <s id="2">ibba gibba.</s>'
        line2 = '<s id="1">abba gabba.</s> <s id="2">ebba gebba.</s>'

        got_tu = self.tmx.make_tu(self.tmx.remove_s_tag(line1),
                                  self.tmx.remove_s_tag(line2))

        want_tu = etree.XML(
            '<tu><tuv xml:lang="nob"><seg>ubba gubba. ibba gibba.</seg>'
            '</tuv><tuv xml:lang="sme"><seg>abba gabba. ebba gebba.'
            '</seg></tuv></tu>')

        self.assertXmlEqual(got_tu, want_tu)

    def test_make_tuv(self):
        line = '<s id="1">ubba gubba.</s> <s id="2">ibba gibba.</s>'
        lang = 'smi'
        got_tuv = self.tmx.make_tuv(self.tmx.remove_s_tag(line), lang)

        want_tuv = etree.XML(
            '<tuv xml:lang="smi"><seg>ubba gubba. ibba gibba.</seg></tuv>')

        self.assertXmlEqual(got_tuv, want_tuv)

    def test_make_tmx_header(self):
        lang = 'smi'
        got_tuv = self.tmx.make_tmx_header(lang)

        want_tuv = etree.XML(
            '<header segtype="sentence" o-tmf="OmegaT TMX" adminlang="en-US" '
            'srclang="smi" datatype="plaintext"/>')

        self.assertXmlEqual(got_tuv, want_tuv)

    def test_remove_s_tag(self):
        got = self.tmx.remove_s_tag(
            '<s id="1">ubba gubba.</s> <s id="2">ibba gibba.</s>')
        want = 'ubba gubba. ibba gibba.'

        self.assertEqual(got, want)

    def test_get_outfile_name(self):
        self.assertEqual(
            self.para.get_outfile_name(),
            os.path.join(
                os.environ['GTFREE'],
                ('prestable/toktmx/nob2sme/facta/skuvlahistorja2/'
                    'aarseth2-n.htm.toktmx')))


class TestTmxComparator(unittest.TestCase):
    """
    A test class for the TmxComparator class
    """
    def test_equal_tmxes(self):
        comp = parallelize.TmxComparator(
            parallelize.Tmx(etree.parse(
                os.path.join(
                    here,
                    'parallelize_data/aarseth2-n.htm.toktmx'))),
            parallelize.Tmx(etree.parse(
                os.path.join(
                    here,
                    'parallelize_data/aarseth2-n.htm.toktmx'))))

        self.assertEqual(comp.get_number_of_differing_lines(), -1)
        self.assertEqual(comp.get_lines_in_wantedfile(), 274)
        self.assertEqual(len(comp.get_diff_as_text()), 0)
