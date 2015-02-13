# -*- coding: utf-8 -*-

#
#   This file contains a class to analyse text in giellatekno xml format
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this file. If not, see <http://www.gnu.org/licenses/>.
#
#   Copyright 2013-2014 Børre Gaup <borre.gaup@uit.no>
#

import os
import unittest
import doctest
from lxml import etree
from lxml import doctestcompare

from corpustools import analyser
from corpustools import parallelize


here = os.path.dirname(__file__)


class TestAnalyser(unittest.TestCase):
    def setUp(self):
        self.a = analyser.Analyser(u'sme')
        self.a.xml_file = parallelize.CorpusXMLFile(
            os.path.join(here, 'smefile.xml'))
        self.a.set_analysis_files(
            abbr_file=os.path.join(here, 'abbr.txt'),
            fst_file=os.path.join(here, 'analyser.xfst'),
            disambiguation_analysis_file=os.path.join(here,
                                                      'disambiguation.cg3'),
            function_analysis_file=os.path.join(here, 'functions.cg3'),
            dependency_analysis_file=os.path.join(here, 'dependency.cg3'))

    def assertXmlEqual(self, got, want):
        u"""Check if two stringified xml snippets are equal
        """
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(
                doctest.Example(u"", want), got, 0).encode(u'utf-8')
            raise AssertionError(message)

    def test_sme_ccat_output(self):
        u"""Test if the ccat output is what we expect it to be
        """
        got = self.a.ccat()
        want = (
            u'Muhto gaskkohagaid, ja erenoamážit dalle go lei buolaš, '
            u'de aggregáhta billánii. ¶\n')

        self.assertEqual(got, want.encode(u'utf8'))

    def test_sme_preprocess_output(self):
        u"""Test if the preprocess output is what we expect it to be
        """
        got = self.a.preprocess()
        want = (
            u'Muhto\ngaskkohagaid\n,\nja\nerenoamážit\ndalle go\nlei\n'
            u'buolaš\n,\nde\naggregáhta\nbillánii\n.\n¶\n')

        self.assertEqual(got, want.encode(u'utf8'))

    def test_sme_disambiguation_output(self):
        u"""Check if disambiguation analysis gives the expected output
        """
        self.a.disambiguation_analysis()
        got = self.a.get_disambiguation()
        want = (
            u'"<Muhto>"\n\t"muhto" CC <sme> @CVP\n"<gaskkohagaid>"\n'
            u'\t"gaskkohagaid" Adv <sme>\n"<,>"\n\t"," CLB\n"<ja>"\n'
            u'\t"ja" CC <sme> @CNP\n"<erenoamážit>"\n'
            u'\t"erenoamážit" Adv <sme>\n"<dalle_go>"\n'
            u'\t"dalle_go" MWE CS <sme> @CVP\n"<lei>"\n'
            u'\t"leat" V <sme> IV Ind Prt Sg3 @+FMAINV\n"<buolaš>"\n'
            u'\t"buolaš" Sem/Wthr N <sme> Sg Nom\n"<,>"\n'
            u'\t"," CLB\n"<de>"\n\t"de" Adv <sme>\n"<aggregáhta>"\n'
            u'\t"aggregáhta" N <sme> Sg Nom\n"<billánii>"\n'
            u'\t"billánit" V <sme> IV Ind Prt Sg3 @+FMAINV\n"<.>"\n'
            u'\t"." CLB\n\n"<¶>"\n\t"¶" CLB\n\n')

        self.assertEqual(got, want.encode(u'utf8'))

    def test_sme_dependency_output(self):
        u"""Check if disambiguation analysis gives the expected output
        """
        self.a.dependency_analysis()
        got = self.a.get_dependency()
        want = (
            u'"<Muhto>"\n\t"muhto" CC @CVP #1->1\n"<gaskkohagaid>"\n'
            u'\t"gaskkohagaid" Adv @ADVL> #2->12\n"<,>"\n'
            u'\t"," CLB #3->4\n"<ja>"\n\t"ja" CC @CNP #4->2\n"<erenoamážit>"\n'
            u'\t"erenoamážit" Adv @ADVL> #5->12\n"<dalle_go>"\n'
            u'\t"dalle_go" CS @CVP #6->7\n"<lei>"\n'
            u'\t"leat" V IV Ind Prt Sg3 @FS-ADVL> #7->12\n"<buolaš>"\n'
            u'\t"buolaš" N Sg Nom @<SPRED #8->7\n"<,>"\n'
            u'\t"," CLB #9->6\n"<de>"\n'
            u'\t"de" Adv @ADVL> #10->12\n"<aggregáhta>"\n'
            u'\t"aggregáhta" N Sg Nom @SUBJ> #11->12\n"<billánii>"\n'
            u'\t"billánit" V IV Ind Prt Sg3 @FS-ADVL> #12->0\n"<.>"\n'
            u'\t"." CLB #13->12\n\n"<¶>"\n\t"¶" CLB #1->1\n\n')

        self.assertEqual(got, want.encode(u'utf8'))

    def test_analysisXml(self):
        u"""Check if the xml is what it is supposed to be
        """
        self.a.dependency_analysis()
        self.a.get_analysis_xml()
        got = self.a.xml_file.get_etree()
        want = (
            u'<document xml:lang="sme" id="no_id">\n'
            u'  <header>\n'
            u'    <title>Internáhtta sosiálalaš giliguovddážin</title>\n'
            u'    <genre code="facta"/>\n'
            u'    <author>\n'
            u'      <person firstname="Abba" lastname="Abbamar" sex="m" '
            u'born="1900" nationality="nor"/>\n'
            u'    </author>\n'
            u'    <translator>\n'
            u'      <person firstname="Ibba" lastname="Ibbamar" sex="unknown" '
            u'born="" nationality=""/>\n'
            u'    </translator>\n'
            u'    <translated_from xml:lang="nob"/>\n'
            u'    <year>2005</year>\n'
            u'    <publChannel>\n'
            u'      <publication>\n'
            u'        <publisher>Almmuheaddji OS</publisher>\n'
            u'      </publication>\n'
            u'    </publChannel>\n'
            u'    <wordcount>10</wordcount>\n'
            u'    <availability>\n'
            u'      <free/>\n'
            u'    </availability>\n'
            u'    <submitter name="Børre Gaup" '
            u'email="boerre.gaup@samediggi.no"/>\n'
            u'    <multilingual>\n'
            u'      <language xml:lang="nob"/>\n'
            u'    </multilingual>\n'
            u'    <origFileName>aarseth_s.htm</origFileName>\n'
            u'    <metadata>\n'
            u'      <uncomplete/>\n'
            u'    </metadata>\n'
            u'    <version>XSLtemplate  1.9 ; file-specific xsl  '
            u'$Revision: 1.3 $; common.xsl  $Revision$; </version>\n'
            u'  </header>\n'
            u'  <body><disambiguation><![CDATA["<Muhto>"\n'
            u'\t"muhto" CC <sme> @CVP\n"<gaskkohagaid>"\n'
            u'\t"gaskkohagaid" Adv <sme>\n"<,>"\n\t"," CLB\n"<ja>"\n'
            u'\t"ja" CC <sme> @CNP\n"<erenoamážit>"\n'
            u'\t"erenoamážit" Adv <sme>\n"<dalle_go>"\n'
            u'\t"dalle_go" MWE CS <sme> @CVP\n"<lei>"\n'
            u'\t"leat" V <sme> IV Ind Prt Sg3 @+FMAINV\n"<buolaš>"\n'
            u'\t"buolaš" Sem/Wthr N <sme> Sg Nom\n"<,>"\n'
            u'\t"," CLB\n"<de>"\n\t"de" Adv <sme>\n"<aggregáhta>"\n'
            u'\t"aggregáhta" N <sme> Sg Nom\n"<billánii>"\n'
            u'\t"billánit" V <sme> IV Ind Prt Sg3 @+FMAINV\n"<.>"\n'
            u'\t"." CLB\n\n"<¶>"\n\t"¶" CLB\n\n]]></disambiguation>'
            u'<dependency><![CDATA["<Muhto>"\n'
            u'\t"muhto" CC @CVP #1->1\n"<gaskkohagaid>"\n'
            u'\t"gaskkohagaid" Adv @ADVL> #2->12\n"<,>"\n'
            u'\t"," CLB #3->4\n"<ja>"\n\t"ja" CC @CNP #4->2\n"<erenoamážit>"\n'
            u'\t"erenoamážit" Adv @ADVL> #5->12\n"<dalle_go>"\n'
            u'\t"dalle_go" CS @CVP #6->7\n"<lei>"\n'
            u'\t"leat" V IV Ind Prt Sg3 @FS-ADVL> #7->12\n"<buolaš>"\n'
            u'\t"buolaš" N Sg Nom @<SPRED #8->7\n"<,>"\n'
            u'\t"," CLB #9->6\n"<de>"\n'
            u'\t"de" Adv @ADVL> #10->12\n"<aggregáhta>"\n'
            u'\t"aggregáhta" N Sg Nom @SUBJ> #11->12\n"<billánii>"\n'
            u'\t"billánit" V IV Ind Prt Sg3 @FS-ADVL> #12->0\n"<.>"\n'
            u'\t"." CLB #13->12\n\n"<¶>"\n'
            u'\t"¶" CLB #1->1\n\n]]></dependency></body></document>')
        self.maxDiff = None
        self.assertEqual(etree.tostring(got, encoding=u'unicode'), want)
