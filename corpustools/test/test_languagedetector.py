# -*- coding: utf-8 -*-
import unittest
import os
import lxml.etree as etree
import lxml.doctestcompare as doctestcompare
import doctest

from corpustools import converter
from corpustools import text_cat


here = os.path.dirname(__file__)


class XMLTester(unittest.TestCase):
    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal
        """
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(
                doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)


class TestLanguageDetector(XMLTester):
    """
    Test the functionality of LanguageDetector
    """
    def setUp(self):
        self.classifier = text_cat.Classifier()
        self.document = etree.parse(
            os.path.join(here,
                         'converter_data/samediggi-article-48s-before-lang-'
                         'detection-with-multilingual-tag.xml'))

    def test_get_main_lang(self):
        test_main_lang = 'sme'
        language_detector = converter.LanguageDetector(self.document,
                                                       self.classifier)
        self.assertEqual(test_main_lang, language_detector.get_mainlang())

    def test_set_paragraph_language_preset_language(self):
        orig_paragraph = '<p xml:lang="sme">I Orohagat</p>'
        expected_paragraph = '<p xml:lang="sme">I Orohagat</p>'

        language_detector = converter.LanguageDetector(self.document,
                                                       self.classifier)
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

        language_detector = converter.LanguageDetector(self.document,
                                                       self.classifier)
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

        language_detector = converter.LanguageDetector(self.document,
                                                       self.classifier)
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

        language_detector = converter.LanguageDetector(self.document,
                                                       self.classifier)
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

        language_detector = converter.LanguageDetector(self.document,
                                                       self.classifier)
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

        language_detector = converter.LanguageDetector(self.document,
                                                       self.classifier)
        got_paragraph = language_detector.remove_quote(
            etree.fromstring(orig_paragraph))

        self.assertEqual(got_paragraph, expected_paragraph)

    def test_detect_language_with_multilingualtag(self):
        language_detector = converter.LanguageDetector(
            etree.parse(
                os.path.join(here,
                             'converter_data/samediggi-article-48s-before-'
                             'lang-detection-with-multilingual-tag.xml')),
            self.classifier)
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
                         'detection-without-multilingual-tag.xml')),
            self.classifier)
        language_detector.detect_language()
        got_document = language_detector.get_document()

        expected_document = etree.parse(
            os.path.join(here,
                         'converter_data/samediggi-article-48s-after-lang-'
                         'detection-without-multilingual-tag.xml'))

        self.assertXmlEqual(etree.tostring(got_document),
                            etree.tostring(expected_document))
