# -*- coding: utf-8 -*-
import unittest
import os

from corpustools import text_cat
from corpustools import converter

here = os.path.dirname(__file__)
LANGUAGEGUESSER = text_cat.Classifier()

class TestTextCat(unittest.TestCase):
    def setUp(self):
        pass

    def test_classify(self):
        self.assertEqual(
            LANGUAGEGUESSER.classify("eg køyrer ikkje"),
            "nno")
        self.assertEqual(
            LANGUAGEGUESSER.classify("Sámediggi nammada sámi báikenammakonsuleanttaid"),
            "sme")

    def test_folder_none(self):
        fullguesser = text_cat.Classifier(None)
        self.assertEqual(
            fullguesser.classify("eg køyrer ikkje"),
            "nno")
        self.assertEqual(
            fullguesser.classify("Almmá norggabeale guohtuneatnamiid ii leat vejolaš jođihit"),
            "sme")

    def test_restricted(self):
        littleguesser = text_cat.Classifier(langs=["nob","sma"])
        self.assertEqual(
            littleguesser.classify("Regional utvikling"),
            "nob")
        self.assertEqual(
            littleguesser.classify("Regijovnaale evtiedimmie"),
            "sma")
