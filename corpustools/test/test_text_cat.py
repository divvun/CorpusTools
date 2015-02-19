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

