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
#   Copyright © 2014-2023 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#


import doctest
import os
import unittest

import lxml.doctestcompare as doctestcompare
import lxml.etree as etree

from corpustools import languagedetector, text_cat

HERE = os.path.dirname(__file__)
LANGUAGEGUESSER = text_cat.Classifier(None)


class XMLTester(unittest.TestCase):
    @staticmethod
    def assertXmlEqual(got, want):
        """Check if two stringified xml snippets are equal"""
        got = etree.tostring(got, encoding="unicode")
        want = etree.tostring(want, encoding="unicode")

        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(
                doctest.Example("", want), got, 0
            ).encode("utf-8")
            raise AssertionError(message)


class TestLanguageDetector(XMLTester):
    """Test the functionality of LanguageDetector"""

    def setUp(self):
        self.root = etree.parse(
            os.path.join(
                HERE,
                "converter_data/samediggi-article-48s-before-lang-"
                "detection-with-multilingual-tag.xml",
            )
        ).getroot()

    def test_get_main_lang(self):
        test_main_lang = "sme"
        language_detector = languagedetector.LanguageDetector(
            self.root, LANGUAGEGUESSER
        )
        self.assertEqual(test_main_lang, language_detector.mainlang)

    def test_set_paragraph_language_preset_language(self):
        orig_paragraph = '<p xml:lang="sme">I Orohagat</p>'
        expected_paragraph = etree.fromstring('<p xml:lang="sme">I Orohagat</p>')

        language_detector = languagedetector.LanguageDetector(
            self.root, LANGUAGEGUESSER
        )
        got_paragraph = language_detector.set_paragraph_language(
            etree.fromstring(orig_paragraph)
        )

        self.assertXmlEqual(got_paragraph, expected_paragraph)

    def test_set_paragraph_language_mainlanguage(self):
        orig_paragraph = (
            "<p>Sámegiella lea 2004 čavčča rájes standárda giellaválga "
            "Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša ahte "
            "sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. "
            "Buot leat dás dán fitnodaga Service Pack 2-páhkas, maid ferte "
            "viežžat ja bidjat dihtorii. Boađus lea ahte buot boahttevaš "
            "Microsoft prográmmat dorjot sámegiela. Dattetge sáhttet "
            "deaividit váttisvuođat go čálát sámegiela Outlook-kaleandaris "
            "dahje e-poastta namahussajis, ja go čálát sámegillii dakkár "
            "prográmmain, maid Microsoft ii leat ráhkadan.</p>"
        )
        expected_paragraph = etree.fromstring(
            "<p>Sámegiella lea 2004 čavčča rájes standárda giellaválga "
            "Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša ahte "
            "sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. "
            "Buot leat dás dán fitnodaga Service Pack 2-páhkas, maid ferte "
            "viežžat ja bidjat dihtorii. Boađus lea ahte buot boahttevaš "
            "Microsoft prográmmat dorjot sámegiela. Dattetge sáhttet "
            "deaividit váttisvuođat go čálát sámegiela Outlook-kaleandaris "
            "dahje e-poastta namahussajis, ja go čálát sámegillii dakkár "
            "prográmmain, maid Microsoft ii leat ráhkadan.</p>"
        )

        language_detector = languagedetector.LanguageDetector(
            self.root, LANGUAGEGUESSER
        )
        got_paragraph = language_detector.set_paragraph_language(
            etree.fromstring(orig_paragraph)
        )

        self.assertXmlEqual(got_paragraph, expected_paragraph)

    def test_set_paragraph_language_mainlanguage_quote_mainlang(self):
        orig_paragraph = (
            "<p>Sámegiella lea 2004 čavčča rájes standárda giellaválga "
            "Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša ahte "
            "sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. "
            '<span type="quote">«Buot leat dás dán fitnodaga Service Pack 2-'
            "páhkas, maid ferte viežžat ja bidjat dihtorii»</span>. Boađus "
            "lea ahte buot boahttevaš Microsoft prográmmat dorjot sámegiela. "
            "Dattetge sáhttet deaividit váttisvuođat go čálát sámegiela "
            "Outlook-kaleandaris dahje e-poastta namahussajis, ja go čálát "
            "sámegillii dakkár prográmmain, maid Microsoft ii leat "
            "ráhkadan.</p>"
        )
        expected_paragraph = etree.fromstring(
            "<p>Sámegiella lea 2004 čavčča rájes standárda giellaválga "
            "Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša ahte "
            "sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. "
            '<span type="quote">«Buot leat dás dán fitnodaga Service Pack 2-'
            "páhkas, maid ferte viežžat ja bidjat dihtorii»</span>. Boađus "
            "lea ahte buot boahttevaš Microsoft prográmmat dorjot sámegiela. "
            "Dattetge sáhttet deaividit váttisvuođat go čálát sámegiela "
            "Outlook-kaleandaris dahje e-poastta namahussajis, ja go čálát "
            "sámegillii dakkár prográmmain, maid Microsoft ii leat "
            "ráhkadan.</p>"
        )

        language_detector = languagedetector.LanguageDetector(
            self.root, LANGUAGEGUESSER
        )
        got_paragraph = language_detector.set_paragraph_language(
            etree.fromstring(orig_paragraph)
        )

        self.assertXmlEqual(got_paragraph, expected_paragraph)

    def test_set_paragraph_language_mainlanguage_quote_not_mainlang(self):
        orig_paragraph = (
            "<p>Sámegiella lea 2004 čavčča rájes standárda giellaválga "
            "Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša ahte "
            "sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. "
            '<span type="quote">«Alt finnes i den foreliggende Service Pack 2 '
            "fra selskapet, som må lastes ned og installeres på din "
            "datamaskin. Konsekvensen er at all framtidig programvare fra "
            "Microsoft vil inneholde støtte for samisk»</span>. Boađus lea "
            "ahte buot boahttevaš Microsoft prográmmat dorjot sámegiela. "
            "Dattetge sáhttet deaividit váttisvuođat go čálát sámegiela "
            "Outlook-kaleandaris dahje e-poastta namahussajis, ja go čálát "
            "sámegillii dakkár prográmmain, maid Microsoft ii leat "
            "ráhkadan.</p>"
        )
        expected_paragraph = etree.fromstring(
            "<p>Sámegiella lea 2004 čavčča rájes standárda giellaválga "
            "Microsofta operatiivavuogádagas Windows XP. Dat mearkkaša ahte "
            "sámegiel bustávaid ja hámiid sáhttá válljet buot prográmmain. "
            '<span type="quote" xml:lang="nob">«Alt finnes i den foreliggende '
            "Service Pack 2 fra selskapet, som må lastes ned og installeres "
            "på din datamaskin. Konsekvensen er at all framtidig programvare "
            "fra Microsoft vil inneholde støtte for samisk»</span>. Boađus "
            "lea ahte buot boahttevaš Microsoft prográmmat dorjot sámegiela. "
            "Dattetge sáhttet deaividit váttisvuođat go čálát sámegiela "
            "Outlook-kaleandaris dahje e-poastta namahussajis, ja go čálát "
            "sámegillii dakkár prográmmain, maid Microsoft ii leat "
            "ráhkadan.</p>"
        )

        language_detector = languagedetector.LanguageDetector(
            self.root, LANGUAGEGUESSER
        )
        got_paragraph = language_detector.set_paragraph_language(
            etree.fromstring(orig_paragraph)
        )

        self.assertXmlEqual(got_paragraph, expected_paragraph)

    def test_set_paragraph_language_not_mainlanguage(self):
        orig_paragraph = (
            "<p>Samisk er fra høsten 2004 et standard språkvalg Microsofts "
            "operativsystem Windows XP. I praksis betyr det at samiske "
            "bokstaver og formater kan velges i alle programmer. Alt finnes "
            "i den foreliggende Service Pack 2 fra selskapet, som må lastes "
            "ned og installeres på din datamaskin. Konsekvensen er at all "
            "framtidig programvare fra Microsoft vil inneholde støtte for "
            "samisk. Du vil imidlertid fremdeles kunne oppleve problemer med "
            "å skrive samisk i Outlook-kalenderen eller i tittel-feltet i "
            "e-post, og med å skrive samisk i programmer levert av andre enn "
            "Microsoft.</p>"
        )

        language_detector = languagedetector.LanguageDetector(
            self.root, LANGUAGEGUESSER
        )
        got_paragraph = language_detector.set_paragraph_language(
            etree.fromstring(orig_paragraph)
        )

        self.assertEqual(
            got_paragraph.get("{http://www.w3.org/XML/1998/namespace}lang"), "nob"
        )

    def test_remove_quote(self):
        orig_paragraph = (
            '<p>bla bla <span type="quote">bla1 bla</span> ble ble '
            '<span type="quote">bla2 bla</span> <b>bli</b> bli '
            '<span type="quote">bla3 bla</span> blo blo</p>'
        )
        expected_paragraph = "bla bla  ble ble  bli bli  blo blo"

        language_detector = languagedetector.LanguageDetector(
            self.root, LANGUAGEGUESSER
        )
        got_paragraph = language_detector.remove_quote(etree.fromstring(orig_paragraph))

        self.assertEqual(got_paragraph, expected_paragraph)

    def test_detect_language_with_multilingualtag(self):
        root = etree.parse(
            os.path.join(
                HERE,
                "converter_data/samediggi-article-48s-before-"
                "lang-detection-with-multilingual-tag.xml",
            )
        ).getroot()
        language_detector = languagedetector.LanguageDetector(root, LANGUAGEGUESSER)
        language_detector.detect_language()
        got_document = language_detector.document

        expected_document = etree.parse(
            os.path.join(
                HERE,
                "converter_data/samediggi-article-48s-after-lang-"
                "detection-with-multilingual-tag.xml",
            )
        )

        self.assertXmlEqual(got_document, expected_document)

    def test_detect_language_without_multilingualtag(self):
        root = etree.parse(
            os.path.join(
                HERE,
                "converter_data/samediggi-article-48s-before-lang-"
                "detection-without-multilingual-tag.xml",
            )
        ).getroot()
        language_detector = languagedetector.LanguageDetector(root, LANGUAGEGUESSER)
        language_detector.detect_language()
        got_document = language_detector.document

        expected_document = etree.parse(
            os.path.join(
                HERE,
                "converter_data/samediggi-article-48s-after-lang-"
                "detection-without-multilingual-tag.xml",
            )
        )

        self.assertXmlEqual(got_document, expected_document)

    def test_no_lang_guessing_without_models(self):
        test_document = """
            <document xml:lang="non_existing_mainlang">
                <header>
                    <title>title</title>
                    <multilingual>
                        <language xml:lang="non_existing_optional_lang"/>
                    </multilingual>
                </header>
                <body>
                    <p>content</p>
                </body>
            </document>
        """

        root = etree.fromstring(test_document)
        language_detector = languagedetector.LanguageDetector(root, LANGUAGEGUESSER)
        language_detector = languagedetector.LanguageDetector(root, LANGUAGEGUESSER)
        language_detector.detect_language()
        got_document = language_detector.document

        self.assertXmlEqual(got_document, root)
