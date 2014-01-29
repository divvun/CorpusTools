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

from corpustools import parallelize


class TestCorpusXMLFile(unittest.TestCase):
    """
    A test class for the CorpusXMLFile class
    """
    def setUp(self):
        self.pfile = parallelize.CorpusXMLFile(os.environ['GTFREE'] + "/prestable/converted/sme/facta/skuvlahistorja2/aarseth2-s.htm.xml", "nob")

    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal
        """
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)

    def testBasename(self):
        self.assertEqual(self.pfile.getBasename(), "aarseth2-s.htm.xml")

    def testDirname(self):
        self.assertEqual(self.pfile.getDirname(), os.path.join(os.environ['GTFREE'] + "/prestable/converted/sme/facta/skuvlahistorja2"))

    def testName(self):
        self.assertEqual(self.pfile.getName(), os.environ['GTFREE'] + "/prestable/converted/sme/facta/skuvlahistorja2/aarseth2-s.htm.xml")

    def testLang(self):
        self.assertEqual(self.pfile.getLang(), "sme")

    def testGetParallelBasename(self):
        self.assertEqual(self.pfile.getParallelBasename(), "aarseth2-n.htm")

    def testGetParallelFilename(self):
        self.assertEqual(self.pfile.getParallelFilename(), os.environ['GTFREE'] + "/prestable/converted/nob/facta/skuvlahistorja2/aarseth2-n.htm.xml")

    def testGetOriginalFilename(self):
        self.assertEqual(self.pfile.getOriginalFilename(), os.environ['GTFREE'] + "/orig/sme/facta/skuvlahistorja2/aarseth2-s.htm")

    def testGetTranslatedFrom(self):
        self.assertEqual(self.pfile.getTranslatedFrom(), "nob")

    def testGetWordCount(self):
        corpusfile = parallelize.CorpusXMLFile('parallelize_data/aarseth2-n-with-version.htm.xml', 'sme')
        self.assertEqual(corpusfile.getWordCount(), "4009")

    def testRemoveVersion(self):
        fileWithVersion = parallelize.CorpusXMLFile('parallelize_data/aarseth2-n-with-version.htm.xml', 'sme')
        fileWithoutVersion = parallelize.CorpusXMLFile('parallelize_data/aarseth2-n-without-version.htm.xml', 'sme')

        fileWithVersion.removeVersion()

        got = etree.tostring(fileWithoutVersion.geteTree())
        want = etree.tostring(fileWithVersion.geteTree())

        self.assertXmlEqual(got, want)

    def testRemoveSkip(self):
        fileWithSkip = parallelize.CorpusXMLFile('parallelize_data/aarseth2-s-with-skip.htm.xml', 'sme')
        fileWithoutSkip = parallelize.CorpusXMLFile('parallelize_data/aarseth2-s-without-skip.htm.xml', 'sme')

        fileWithSkip.removeSkip()

        got = etree.tostring(fileWithoutSkip.geteTree())
        want = etree.tostring(fileWithSkip.geteTree())

        self.assertXmlEqual(got, want)

    def testMoveLater(self):
        fileWithLater = parallelize.CorpusXMLFile('parallelize_data/aarseth2-s-with-later.htm.xml', 'sme')
        fileWithMovedLater = parallelize.CorpusXMLFile('parallelize_data/aarseth2-s-with-moved-later.htm.xml', 'sme')

        fileWithLater.moveLater()
        got = etree.tostring(fileWithMovedLater.geteTree())
        want = etree.tostring(fileWithLater.geteTree())
        self.assertXmlEqual(got, want)

class TestSentenceDivider(unittest.TestCase):
    """A test class for the SentenceDivider class
    """
    def setUp(self):
        self.sentenceDivider = parallelize.SentenceDivider("parallelize_data/finnmarkkulahka_web_lettere.pdf.xml", "nob")

    def assertXmlEqual(self, got, want):
        """
        Check if two xml snippets are equal
        """
        string_got = etree.tostring(got, pretty_print = True)
        string_want = etree.tostring(want, pretty_print = True)

        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(string_want, string_got, 0):
            message = checker.output_difference(doctest.Example("", string_want), string_got, 0).encode('utf-8')
            raise AssertionError(message)

    def testConstructor(self):
        """Check that the constructor makes what it is suppposed to
        """
        self.assertEqual(self.sentenceDivider.sentenceCounter, 0)
        self.assertEqual(self.sentenceDivider.docLang, 'sme')
        self.assertEqual(self.sentenceDivider.inputEtree.__class__.__name__, '_ElementTree')

    def testProcessAllParagraphs(self):
        self.sentenceDivider.processAllParagraphs()
        got = self.sentenceDivider.document

        want = etree.parse('parallelize_data/finnmarkkulahka_web_lettere.pdfsme_sent.xml.test')

        self.assertXmlEqual(got, want)

    def testProcessOneParagraph(self):
        """Check the output of processOneParagraph
        """
        self.sentenceDivider.docLang = 'sme'
        p = etree.XML('<p>Jápmá go sámi kultuvra veahážiid mielde go nuorat ovdal guldalit Britney Spears go Áilluhačča? máksá Finnmárkkuopmodat. § 10 Áššit meahcceeatnamiid</p>')
        got = self.sentenceDivider.processOneParagraph(p)
        want = etree.XML('<p><s id="0">Jápmá go sámi kultuvra veahážiid mielde go nuorat ovdal guldalit Britney Spears go Áilluhačča ?</s><s id="1">máksá Finnmárkkuopmodat .</s><s id="2">§ 10 Áššit meahcceeatnamiid </s></p>')
        self.assertXmlEqual(got, want)

        p = etree.XML('<p>Stuora oassi Romssa universitehta doaimmain lea juohkit dieđuid sámi, norgga ja riikkaidgaskasaš dutkanbirrasiidda, sámi ja norgga eiseválddiide, ja sámi servodagaide (geahča mielddus A <em type="italic"><span type="quote">“Romssa universitehta ja guoskevaš institušuvnnaid sámi dutkan ja oahpahus”</span></em>  álggahusa ).</p>')
        got = self.sentenceDivider.processOneParagraph(p)
        want = etree.XML('<p><s id="3">Stuora oassi Romssa universitehta doaimmain lea juohkit dieđuid sámi , norgga ja riikkaidgaskasaš dutkanbirrasiidda , sámi ja norgga eiseválddiide , ja sámi servodagaide ( geahča mielddus A “ Romssa universitehta ja guoskevaš institušuvnnaid sámi dutkan ja oahpahus ” álggahusa ) .</s></p>')
        self.assertXmlEqual(got, want)



        self.sentenceDivider.docLang = 'nob'
        p = etree.XML('<p>Artikkel i boka Samisk skolehistorie 2 . Davvi Girji 2007.</p>')
        got = self.sentenceDivider.processOneParagraph(p)
        want = etree.XML('<p><s id="4">Artikkel i boka Samisk skolehistorie 2 .</s><s id="5">Davvi Girji 2007 .</s></p>')
        self.assertXmlEqual(got, want)

        p = etree.XML('<p><em type="bold">Bjørn Aarseth med elever på skitur - på 1950-tallet.</em> (Foto: Trygve Madsen)</p>')
        got = self.sentenceDivider.processOneParagraph(p)
        want = etree.XML('<p><s id="6">Bjørn Aarseth med elever på skitur - på 1950-tallet .</s><s id="7">( Foto : Trygve Madsen )</s></p>')
        self.assertXmlEqual(got, want)

        p = etree.XML('<p>finne rom for etablering av en fast tilskuddsordning til allerede etablerte språksentra..</p>')
        got = self.sentenceDivider.processOneParagraph(p)
        want = etree.XML('<p><s id="8">finne rom for etablering av en fast tilskuddsordning til allerede etablerte språksentra . .</s></p>')
        self.assertXmlEqual(got, want)

        p = etree.XML('<p>elevene skal få!  Sametingsrådet mener målet</p>')
        got = self.sentenceDivider.processOneParagraph(p)
        want = etree.XML('<p><s id="9">elevene skal få !</s><s id="10">Sametingsrådet mener målet</s></p>')
        self.assertXmlEqual(got, want)

        p = etree.XML('<p>Sametinget.............................................................................................................................. 2 Utdannings- og forskningsdepartementet............................................................................... 3 Kultur- og kirkedepartementet ............................................................................................... 7 Kommunal- og regionaldepartementet................................................................................... 9</p>')
        got = self.sentenceDivider.processOneParagraph(p)
        want = etree.XML('<p><s id="11">Sametinget ... 2 Utdannings- og forskningsdepartementet ... 3 Kultur- og kirkedepartementet ... 7 Kommunal- og regionaldepartementet ... 9</s></p>')
        self.assertXmlEqual(got, want)

        self.sentenceDivider.docLang = 'sme'
        p = etree.XML('<p>Allaskuvllas lea maiddái ovddasvástádus julevsámegielas ja máttasámegielas. (... ). Berre leat vejolaš váldit oahpaheaddjeoahpu, mas erenoamáš deaddu lea davvi-, julev-, máttasámegielas ja kultuvrras.</p>')
        got = self.sentenceDivider.processOneParagraph(p)
        want = etree.XML('<p><s id="12">Allaskuvllas lea maiddái ovddasvástádus julevsámegielas ja máttasámegielas .</s><s id="13">Berre leat vejolaš váldit oahpaheaddjeoahpu , mas erenoamáš deaddu lea davvi- , julev- , máttasámegielas ja kultuvrras .</s></p>')
        self.assertXmlEqual(got, want)

    def testDotFollowedByDot(self):
        """Test of how processOneParagraph handles a paragraph
        with . and ... in the end.
        tca2 doesn't accept sentences without real letters, so we have to make
        sure the ... doesn't end up alone inside a s tag"""
        self.sentenceDivider.docLang = 'nob'
        p = etree.XML('<p>Alt det som har med norsk å gjøre, har jeg gruet meg for og hatet hele mitt liv - og kommer kanskje til å fortsette med det. ...</p>')
        got = self.sentenceDivider.processOneParagraph(p)
        want = etree.XML('<p><s id="0">Alt det som har med norsk å gjøre , har jeg gruet meg for og hatet hele mitt liv - og kommer kanskje til å fortsette med det . ...</s></p>')
        self.assertXmlEqual(got, want)

    def testQuotemarks(self):
        """Test how SentenceDivider handles quotemarks
        """
        self.sentenceDivider.docLang = 'nob'
        p = etree.XML('<p>Forsøksrådet for skoleverket godkjente det praktiske opplegget for kurset i brev av 18/8 1959 og uttalte da bl.a.: «Selve innholdet i kurset virker gjennomtenkt og underbygd og ser ut til å konsentrere seg om vesentlige emner som vil få stor betydning for elevene i deres yrkesarbeid. Med flyttsame-kunnskapen som bakgrunn er det grunn til å vente seg mye av dette kursopplegget.» Med denne tillitserklæring i ryggen har vi så fra år til år søkt å forbedre kursoppleggene til vi foran 1963-kursene står med planer som vi anser tilfredsstillende , men ikke endelige .)</p>')
        got = self.sentenceDivider.processOneParagraph(p)
        want = etree.XML('<p><s id="0">Forsøksrådet for skoleverket godkjente det praktiske opplegget for kurset i brev av 18/8 1959 og uttalte da bl.a. : « Selve innholdet i kurset virker gjennomtenkt og underbygd og ser ut til å konsentrere seg om vesentlige emner som vil få stor betydning for elevene i deres yrkesarbeid .</s><s id="1"> Med flyttsame-kunnskapen som bakgrunn er det grunn til å vente seg mye av dette kursopplegget . »</s><s id="2">Med denne tillitserklæring i ryggen har vi så fra år til år søkt å forbedre kursoppleggene til vi foran 1963-kursene står med planer som vi anser tilfredsstillende , men ikke endelige . )</s></p>')
        self.assertXmlEqual(got, want)

    def testSpuriousComma(self):
        self.sentenceDivider.docLang = 'nob'
        p = etree.XML('<p>Etter Sametingets oppfatning vil forslagene til ny § 1 Lovens formål og § 2 Kulturminner og kulturmiljØer - definisjoner; gjøre at det blir en større grad av overensstemmelse mellom lovens begreper og det begrepsapparatet som er nyttet innenfor samisk kulturminnevern. , </p>')
        got = self.sentenceDivider.processOneParagraph(p)
        want = etree.XML('<p><s id="0">Etter Sametingets oppfatning vil forslagene til ny § 1 Lovens formål og § 2 Kulturminner og kulturmiljØer - definisjoner ; gjøre at det blir en større grad av overensstemmelse mellom lovens begreper og det begrepsapparatet som er nyttet innenfor samisk kulturminnevern .</s></p>')
        self.assertXmlEqual(got, want)

        self.sentenceDivider.docLang = 'nob'
        p = etree.XML('<p>, </p>')
        got = self.sentenceDivider.processOneParagraph(p)
        want = etree.XML('<p/>')
        self.assertXmlEqual(got, want)

    def testSpuriousDot(self):
        self.sentenceDivider.docLang = 'nob'
        p = etree.XML('<p>..</p>')
        got = self.sentenceDivider.processOneParagraph(p)
        want = etree.XML('<p/>')
        self.assertXmlEqual(got, want)

    def testLoneQuestionmark(self):
        self.sentenceDivider.docLang = 'nob'
        p = etree.XML('<p>?</p>')
        got = self.sentenceDivider.processOneParagraph(p)
        want = etree.XML('<p/>')
        self.assertXmlEqual(got, want)

    def testDotInSentenceStart(self):
        self.sentenceDivider.docLang = 'nob'
        p = etree.XML('<p> . Cálliidlágádus 1999)</p>')
        got = self.sentenceDivider.processOneParagraph(p)
        want = etree.XML('<p><s id="0">Cálliidlágádus 1999 )</s></p>')
        self.assertXmlEqual(got, want)

    def testSpanInP(self):
        self.sentenceDivider.docLang = 'nob'
        p = etree.XML('<p>( Styrke institusjonssamarbeidet (Urfolksnettverket og <span type="quote">“Forum for urfolksspørsmål i bistanden”</span>)</p>')
        got = self.sentenceDivider.processOneParagraph(p)
        want = etree.XML('<p><s id="0">( Styrke institusjonssamarbeidet ( Urfolksnettverket og “ Forum for urfolksspørsmål i bistanden ” )</s></p>')
        self.assertXmlEqual(got, want)

    def testMakeSentence(self):
        s = self.sentenceDivider.makeSentence([u'Sámerievtti ', u'ovdáneapmi', u'lea', u'dahkan', u'vuđđosa', u'Finnmárkkuláhkii'])

        self.assertEqual(s.attrib["id"], '0')
        self.assertEqual(s.text, u'Sámerievtti ovdáneapmi lea dahkan vuđđosa Finnmárkkuláhkii')

class TestParallelize(unittest.TestCase):
    """
    A test class for the Parallelize class
    """
    def setUp(self):
        self.parallelize = parallelize.Parallelize(os.environ['GTFREE'] + "/prestable/converted/sme/facta/skuvlahistorja2/aarseth2-s.htm.xml", "nob")

    def testOrigPath(self):
        self.assertEqual(self.parallelize.getOrigfile1(), os.environ['GTFREE'] + "/prestable/converted/nob/facta/skuvlahistorja2/aarseth2-n.htm.xml")

    def testParallelPath(self):
        self.assertEqual(self.parallelize.getOrigfile2(), os.environ['GTFREE'] + "/prestable/converted/sme/facta/skuvlahistorja2/aarseth2-s.htm.xml")

    def testLang1(self):
        self.assertEqual(self.parallelize.getLang1(), "nob")

    def testLang2(self):
        self.assertEqual(self.parallelize.getLang2(), "sme")

    def testGetSentFilename(self):
        self.assertEqual(self.parallelize.getSentFilename(self.parallelize.getFilelist()[0]), os.environ['GTFREE'] + "/tmp/aarseth2-n.htmnob_sent.xml")

    def testDividePIntoSentences(self):
        self.assertEqual(self.parallelize.dividePIntoSentences(), 0)

    def testParallizeFiles(self):
        self.assertEqual(self.parallelize.parallelizeFiles(), 0)

    def testGenerateAnchorFile(self):
        self.assertEqual(self.parallelize.generateAnchorFile(), os.path.join(os.environ['GTFREE'], 'anchor-nobsme.txt'))

class TestTmx(unittest.TestCase):
    """
    A test class for the Tmx class
    """
    def setUp(self):
        self.tmx = parallelize.Tmx(etree.parse('parallelize_data/aarseth2-n.htm.toktmx'))

    def assertXmlEqual(self, got, want):
        """
        Check if two xml snippets are equal
        """
        string_got = etree.tostring(got, pretty_print = True)
        string_want = etree.tostring(want, pretty_print = True)

        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(string_want, string_got, 0):
            message = checker.output_difference(doctest.Example("", string_want), string_got, 0).encode('utf-8')
            raise AssertionError(message)


    def testGetSrcLang(self):
        """Test the getSrcLang routine
        """
        self.assertEqual(self.tmx.getSrcLang(), "nob")

    def testTuToString(self):
        tu = etree.XML('<tu><tuv xml:lang="sme"><seg>Sámegiella</seg></tuv><tuv xml:lang="nob"><seg>Samisk</seg></tuv></tu>')

        self.assertEqual(self.tmx.tuToString(tu), "Sámegiella\tSamisk\n")

    def testTuvToString(self):
        tuv = etree.XML('<tuv xml:lang="sme"><seg>Sámegiella</seg></tuv>')

        self.assertEqual(self.tmx.tuvToString(tuv), "Sámegiella")

    def testLangToStringList(self):
        f = open('parallelize_data/aarseth2-n.htm.toktmx.as.txt', 'r')
        stringList = f.readlines()

        nobList = []
        smeList = []
        for string in stringList:
            pairList = string.split('\t')
            nobList.append(pairList[0])
            smeList.append(pairList[1].strip())

        self.assertEqual(self.tmx.langToStringlist('nob'), nobList)
        self.assertEqual(self.tmx.langToStringlist('sme'), smeList)

    def testTmxToStringlist(self):
        f = open('parallelize_data/aarseth2-n.htm.toktmx.as.txt', 'r')
        wantList = f.readlines()
        f.close()
        #self.maxDiff = None
        self.assertEqual(self.tmx.tmxToStringlist(), wantList)

    def testPrettifySegs(self):
        wantXml = etree.XML('<tu><tuv xml:lang="nob"><seg>ubba gubba. ibba gibba.</seg></tuv><tuv xml:lang="sme"><seg>abba gabba. ebba gebba.</seg></tuv></tu>')
        gotXml = etree.XML('<tu><tuv xml:lang="nob"><seg>ubba gubba. ibba gibba.\n</seg></tuv><tuv xml:lang="sme"><seg>abba gabba. ebba gebba.\n</seg></tuv></tu>')
        self.assertXmlEqual(self.tmx.prettifySegs(gotXml), wantXml)

    def testCheckIfEmtpySeg(self):
        empty1 = etree.XML('<tu><tuv xml:lang="nob"><seg>ubba gubba. ibba gibba.</seg></tuv><tuv xml:lang="sme"><seg></seg></tuv></tu>')
        self.assertRaises(AttributeError, self.tmx.checkIfEmtpySeg, empty1)

        empty2 = etree.XML('<tu><tuv xml:lang="nob"><seg></seg></tuv><tuv xml:lang="sme"><seg>abba gabba. ebba gebba.</seg></tuv></tu>')
        self.assertRaises(AttributeError, self.tmx.checkIfEmtpySeg, empty2)

    def testRemoveUnwantedSpaceFromSegs(self):
        wantXml = etree.XML('<tu><tuv xml:lang="nob"><seg>[30] (juli) «skoleturer».</seg></tuv><tuv xml:lang="sme"><seg>[30] (suoidnemánnu) «skuvlatuvrrat».</seg></tuv></tu>')
        gotXml = etree.XML('<tu><tuv xml:lang="nob"><seg>[ 30 ] ( juli ) « skoleturer » .\n</seg></tuv><tuv xml:lang="sme"><seg>[ 30 ] ( suoidnemánnu ) « skuvlatuvrrat » .\n</seg></tuv></tu>')
        self.assertXmlEqual(self.tmx.removeUnwantedSpaceFromSegs(gotXml), wantXml)

    def testRemoveUnwantedSpaceFromString(self):
        got = self.tmx.removeUnwantedSpaceFromString(u'sámesearvvi ; [ 31 ] ( suoidnemánnu ) « skuvlatuvrrat » bargu lea :  okta , guokte .')
        want = u'sámesearvvi; [31] (suoidnemánnu) «skuvlatuvrrat» bargu lea: okta, guokte.'
        self.assertEqual(got, want)

    def testRemoveTuWithEmptySeg(self):
        gotTmx = parallelize.Tmx(etree.parse('parallelize_data/aarseth2-n.htm.toktmx'))
        gotTmx.removeTuWithEmptySeg()

        wantTmx = parallelize.Tmx(etree.parse('parallelize_data/aarseth2-n-without-empty-seg.htm.toktmx'))

        self.assertXmlEqual(gotTmx.getTmx(), wantTmx.getTmx())

    #def testRemoveTuWithWrongLang(self):
        #gotTmx = parallelize.Tmx(etree.parse('parallelize_data/nyheter.html_id=174.withsouthsami.toktmx'))
        #gotTmx.removeTuWithEmptySeg()
        #gotTmx.removeTuWithWrongLang('sme')

        #wantTmx = parallelize.Tmx(etree.parse('parallelize_data/nyheter.html_id=174.withoutsouthsami.tmx'))

        #self.assertXmlEqual(gotTmx.getTmx(), wantTmx.getTmx())

    def testCheckLanguage(self):
        tuWithSme = etree.XML('<tu><tuv xml:lang="sme"><seg>Bargo- ja searvadahttindepartemeanta (BSD) nanne sámiid árbedieđu čohkkema, systematiserema ja gaskkusteami Norggas oktiibuot 1,6 milj. ruvnnuin.</seg></tuv><tuv xml:lang="nob"><seg>Samisk</seg></tuv></tu>')

        self.assertTrue(self.tmx.checkLanguage(tuWithSme, 'sme'))

        tuWithSma = etree.XML('<tu><tuv xml:lang="sme"><seg>Barkoe- jïh ektiedimmiedepartemente (AID) galka nænnoestidh dovne tjöönghkeme- jïh öörnemebarkoem , jïh aaj bæjkoehtimmiem saemien aerpiemaahtoen muhteste Nöörjesne, abpe 1,6 millijovnh kråvnajgujmie.</seg></tuv><tuv xml:lang="nob"><seg>Samisk</seg></tuv></tu>')

        self.assertFalse(self.tmx.checkLanguage(tuWithSma, 'sme'))

class TestTca2ToTmx(unittest.TestCase):
    """
    A test class for the Tca2ToTmx class
    """
    def setUp(self):
        """
        Hand the data from the Parallelize class to the tmx class
        """
        para = parallelize.Parallelize(os.environ['GTFREE'] + "/prestable/converted/sme/facta/skuvlahistorja2/aarseth2-s.htm.xml", "nob")

        self.tmx = parallelize.Tca2ToTmx(para.getFilelist())

    def assertXmlEqual(self, got, want):
        """
        Check if two xml snippets are equal
        """
        string_got = etree.tostring(got, pretty_print = True)
        string_want = etree.tostring(want, pretty_print = True)

        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(string_want, string_got, 0):
            message = checker.output_difference(doctest.Example("", string_want), string_got, 0).encode('utf-8')
            raise AssertionError(message)


    def testMakeTu(self):
        line1 = '<s id="1">ubba gubba.</s> <s id="2">ibba gibba.</s>'
        line2 = '<s id="1">abba gabba.</s> <s id="2">ebba gebba.</s>'

        gotTu = self.tmx.makeTu(line1, line2)

        wantTu = etree.XML('<tu><tuv xml:lang="nob"><seg>ubba gubba. ibba gibba.</seg></tuv><tuv xml:lang="sme"><seg>abba gabba. ebba gebba.</seg></tuv></tu>')

        self.assertXmlEqual(gotTu, wantTu)

    def testMakeTuv(self):
        line =  '<s id="1">ubba gubba.</s> <s id="2">ibba gibba.</s>'
        lang = 'smi'
        gotTuv = self.tmx.makeTuv(line, lang)

        wantTuv = etree.XML('<tuv xml:lang="smi"><seg>ubba gubba. ibba gibba.</seg></tuv>')

        self.assertXmlEqual(gotTuv, wantTuv)

    def testMakeTmxHeader(self):
        lang = 'smi'
        gotTuv = self.tmx.makeTmxHeader(lang)

        wantTuv = etree.XML('<header segtype="sentence" o-tmf="OmegaT TMX" adminlang="en-US" srclang="smi" datatype="plaintext"/>')

        self.assertXmlEqual(gotTuv, wantTuv)

    def testRemoveSTag(self):
        got = self.tmx.removeSTag('<s id="1">ubba gubba.</s> <s id="2">ibba gibba.</s>')
        want =  'ubba gubba. ibba gibba.'

        self.assertEqual(got, want)

    def testGetOutfileName(self):
        self.assertEqual(self.tmx.getOutfileName(), os.path.join(os.environ['GTFREE'], 'prestable/toktmx/nob2sme/facta/skuvlahistorja2/aarseth2-n.htm.toktmx'))

    #def testWriteTmxFile(self):
        #want = etree.parse('parallelize_data/aarseth2-n.htm.toktmx')
        #self.tmx.writeTmxFile(self.tmx.getOutfileName())
        #got = etree.parse(self.tmx.getOutfileName())

        #self.assertXmlEqual(got, want)

class TestTmxComparator(unittest.TestCase):
    """
    A test class for the TmxComparator class
    """
    def testEqualTmxes(self):
        comp = parallelize.TmxComparator(parallelize.Tmx(etree.parse('parallelize_data/aarseth2-n.htm.toktmx')), parallelize.Tmx(etree.parse('parallelize_data/aarseth2-n.htm.toktmx')))

        self.assertEqual(comp.getNumberOfDifferingLines(), -1)
        self.assertEqual(comp.getLinesInWantedfile(), 274)
        self.assertEqual(len(comp.getDiffAsText()), 0)

    #def testUnEqualTmxes(self):
        #gotFile = os.path.join(os.environ['GTFREE'], 'prestable/toktmx/nob2sme/laws/other_files/finnmarksloven.pdf.tmx')
        #wantFile = os.path.join(os.environ['GTFREE'], 'prestable/toktmx/goldstandard/nob2sme/laws/other_files/finnmarksloven.pdf.tmx')
        #comp = parallelize.TmxComparator(parallelize.Tmx(etree.parse(wantFile)), parallelize.Tmx(etree.parse(gotFile)))

        #self.assertEqual(comp.getNumberOfDifferingLines(), 7)
        #self.assertEqual(comp.getLinesInWantedfile(), 632)
        #self.assertEqual(len(comp.getDiffAsText()), 28)

    #def testReversedlang(self):
        #wantFile = parallelize.Tmx(etree.parse('aarseth2-n.htm.tmx'))
        #gotFile = parallelize.Tmx(etree.parse('aarseth2-s.htm.tmx'))
        #gotFile.reverseLangs()

        #comp = parallelize.TmxComparator(wantFile, gotFile)

        #print comp.getDiffAsText()
        #self.assertEqual(comp.getNumberOfDifferingLines(), -1)
        #self.assertEqual(comp.getLinesInWantedfile(), 274)
        #self.assertEqual(len(comp.getDiffAsText()), 0)

#class TestTmxTestDataWriter(unittest.TestCase):
    #"""
    #A class to test TmxTestDataWriter
    #"""
    #def setUp(self):
        #self.writer = parallelize.TmxTestDataWriter("testfilename")

    #def assertXmlEqual(self, got, want):
        #"""
        #Check if two xml snippets are equal
        #"""
        #string_got = etree.tostring(got, pretty_print = True)
        #string_want = etree.tostring(want, pretty_print = True)

        #checker = doctestcompare.LXMLOutputChecker()
        #if not checker.check_output(string_want, string_got, 0):
            #message = checker.output_difference(doctest.Example("", string_want), string_got, 0).encode('utf-8')
            #raise AssertionError(message)

    #def testGetFilename(self):
        #self.assertEqual(self.writer.getFilename(), "testfilename")

    #def testMakeFileElement(self):
        #wantElement = etree.XML('<file name="abc" gspairs="634" diffpairs="84"/>')
        #gotElement = self.writer.makeFileElement("abc", "634", "84")

        #self.assertXmlEqual(gotElement, wantElement)

    #def testMakeTestrunElement(self):
        #wantElement = etree.XML('<testrun datetime="20111208-1234"><file name="abc" gspairs="634" diffpairs="84"/></testrun>')
        #gotElement = self.writer.makeTestrunElement("20111208-1234")
        #fileElement = self.writer.makeFileElement("abc", "634", "84")
        #gotElement.append(fileElement)

        #self.assertXmlEqual(gotElement, wantElement)

    #def testMakeParagstestingElement(self):
        #wantElement = etree.XML('<paragstesting><testrun datetime="20111208-1234"><file name="abc" gspairs="634" diffpairs="84"/></testrun></paragstesting>')
        #gotElement = self.writer.makeParagstestingElement()
        #testrunElement = self.writer.makeTestrunElement("20111208-1234")
        #fileElement = self.writer.makeFileElement("abc", "634", "84")
        #testrunElement.append(fileElement)
        #gotElement.append(testrunElement)

        #self.assertXmlEqual(gotElement, wantElement)

    #def testInsertTestrunElement(self):
        #wantElement = etree.XML('<paragstesting><testrun datetime="20111208-2345"><file name="abc" gspairs="634" diffpairs="84"/></testrun><testrun datetime="20111208-1234"><file name="abc" gspairs="634" diffpairs="84"/></testrun></paragstesting>')

        #gotElement = self.writer.makeParagstestingElement()
        #self.writer.setParagsTestingElement(gotElement)
        #testrunElement = self.writer.makeTestrunElement("20111208-1234")
        #fileElement = self.writer.makeFileElement("abc", "634", "84")
        #testrunElement.append(fileElement)
        #gotElement.append(testrunElement)

        #testrunElement = self.writer.makeTestrunElement("20111208-2345")
        #fileElement = self.writer.makeFileElement("abc", "634", "84")
        #testrunElement.append(fileElement)

        #self.writer.insertTestrunElement(testrunElement)

        #self.assertXmlEqual(gotElement, wantElement)

    #def testWriteParagstestingData(self):
        #want = etree.XML('<paragstesting><testrun datetime="20111208-1234"><file name="abc" gspairs="634" diffpairs="84"/></testrun></paragstesting>')

        #gotElement = self.writer.makeParagstestingElement()
        #self.writer.setParagsTestingElement(gotElement)
        #testrunElement = self.writer.makeTestrunElement("20111208-1234")
        #fileElement = self.writer.makeFileElement("abc", "634", "84")
        #testrunElement.append(fileElement)
        #gotElement.append(testrunElement)


        #self.writer.writeParagstestingData()
        #got = etree.parse(self.writer.filename)

        #self.assertXmlEqual(got, want)

