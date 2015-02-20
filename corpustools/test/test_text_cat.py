#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest
import os
import StringIO

from corpustools import text_cat

here = os.path.dirname(__file__)

class TestTextCat(unittest.TestCase):
    def setUp(self):
        pass

    def test_classify(self):
        guesser = text_cat.Classifier()
        self.assertEqual(
            guesser.classify("eg køyrer ikkje"),
            "nno")
        self.assertEqual(
            guesser.classify("Sámediggi nammada sámi báikenammakonsuleanttaid"),
            "sme")

    def test_folder_none(self):
        guesser = text_cat.Classifier(None)
        self.assertEqual(
            guesser.classify("eg køyrer ikkje"),
            "nno")
        self.assertEqual(
            guesser.classify("Almmá norggabeale guohtuneatnamiid ii leat vejolaš"),
            "sme")

    def test_restricted(self):
        guesser = text_cat.Classifier(langs=["nob","sma"])
        self.assertEqual(
            guesser.classify("Regional utvikling"),
            "nob")
        self.assertEqual(
            guesser.classify("Regijovnaale evtiedimmie"),
            "sma")
        self.assertEqual(
            guesser.classify("eg køyrer ikkje"),
            "nob")              # because restriction

    def test_charmodel_compare(self):
        swe_train = """riksspråkets långa i och u i en mängd ord här (och likartat i det övriga) motsvaras av dette. På samma sätt heter"""
        qer_train = """Ulið witå ig ir faingin få wårå jär å Skansem og sai åv liteð för ið um övkallmåleð. Merkwärdut naug ar eð itte weð kringt noger ar tålåð yvyr dyö jär, fast eð ärer Övdalim og övkallum til mier eld ollt eller."""
        swe_model = text_cat.CharModel().of_text(swe_train)
        qer_model = text_cat.CharModel().of_text(qer_train)
        qer_test = "Ig dalsker nu að ið ollum"
        swe_test = "sådan slåttermark som bara slås med orv och lie, oländig kanske stenig mark"
        swe_testmodel = text_cat.CharModel().of_text(swe_test)
        qer_testmodel = text_cat.CharModel().of_text(qer_test)
        self.assertLess(swe_model.compare(swe_testmodel),
                        qer_model.compare(swe_testmodel))
        self.assertLess(qer_model.compare(qer_testmodel),
                        swe_model.compare(qer_testmodel))

    def test_charmodel_model_file(self):
        model = text_cat.CharModel().of_text("šuhkoládagáhkku")
        model_file = StringIO.StringIO()
        model.to_model_file(model_file)
        lines = model_file.getvalue().decode('utf-8').split("\n")
        self.assertEqual(['k\t3'], lines[:1])
        self.assertIn('á\t2', lines)
        self.assertIn('hk\t2', lines)
        self.assertIn('_\t2', lines)
        self.assertIn('gáhk\t1', lines)

    def test_wordmodel_model_file(self):
        model = text_cat.WordModel().of_text("šuhkoláda ja gáhkku ja gáfe")
        model_file = StringIO.StringIO()
        model.to_model_file(model_file)
        lines = model_file.getvalue().decode('utf-8').split("\n")
        self.assertEqual(['2\tja'], lines[:1])
        self.assertIn('1\tgáhkku', lines)

    def test_compare_tc(self):
        sme_train = "girjerájusbálvalusaid mat leat sámi álbmogii danne go nationála girjerájusstatistihkka ii bija dan materiealla mii lea sámegillii sierra kategoriijan"
        nob_train = "Tocantins utgjorde opprinnelig nordre del av Goiás. Historisk sett har dette området vært adskilt fra resten av denne delstaten."
        nob_test = "kategori:Goiás"
        cmodel_sme = text_cat.CharModel().of_text(sme_train)
        wmodel_sme = text_cat.WordModel().of_text(sme_train)
        cmodel_nob = text_cat.CharModel().of_text(nob_train)
        wmodel_nob = text_cat.WordModel().of_text(nob_train)
        ctext_nob = text_cat.CharModel().of_text(nob_test)
        self.assertLess(wmodel_sme.compare_tc(nob_test, cmodel_sme.compare(ctext_nob)),
                        wmodel_nob.compare_tc(nob_test, cmodel_nob.compare(ctext_nob)))
        self.assertLess(3930431,
                        wmodel_nob.compare_tc(nob_test, cmodel_nob.compare(ctext_nob)))
        self.assertEqual(0,
                         wmodel_sme.compare_tc(nob_test, cmodel_sme.compare(ctext_nob)))
