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

from __future__ import unicode_literals

import os
import unittest
import doctest
from lxml import etree
from lxml import doctestcompare

from corpustools import analyser
from corpustools import parallelize
from corpustools import util


here = os.path.dirname(__file__)


class TestAnalyser(unittest.TestCase):
    def setUp(self):
        self.a = analyser.Analyser(
            'sme',
            'xfst',
            fst_file=os.path.join(here, 'analyser.xfst'),
            disambiguation_analysis_file=os.path.join(here,
                                                      'disambiguation.cg3'),
            function_analysis_file=os.path.join(here, 'functions.cg3'),
            dependency_analysis_file=os.path.join(here, 'dependency.cg3'))
        self.a.xml_file = parallelize.CorpusXMLFile(
            os.path.join(here, 'smefile.xml'))

    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal
        """
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(
                doctest.Example("", want), got, 0).encode('utf-8')
            raise AssertionError(message)

    def test_raise_on_None_file(self):
        with self.assertRaises(TypeError):
            analyser.Analyser('sme', 'xfst', None, None, None, None)

    def test_raise_on_bad_file(self):
        with self.assertRaises(util.ArgumentError):
            analyser.Analyser('sme',
                              'xfst',
                              fst_file=os.path.join(here, 'notafile'),
                              disambiguation_analysis_file=os.path.join(here,
                                                                        'notafile'),
                              function_analysis_file=os.path.join(here, 'notafile'),
                              dependency_analysis_file=os.path.join(here, 'notafile'))

    def test_sme_ccat_output(self):
        """Test if the ccat output is what we expect it to be
        """
        got = self.a.ccat()
        want = (
            'Muhto gaskkohagaid, ja erenoamážit dalle go lei buolaš, '
            'de aggregáhta billánii. ¶\n')

        self.assertEqual(got, want.encode('utf8'))

    def test_sme_preprocess_output(self):
        """Test if the preprocess output is what we expect it to be
        """
        got = self.a.preprocess()
        want = (
            'Muhto\ngaskkohagaid\n,\nja\nerenoamážit\ndalle go\nlei\n'
            'buolaš\n,\nde\naggregáhta\nbillánii\n.\n¶\n')

        self.assertEqual(got, want.encode('utf8'))

    def test_sme_disambiguation_output(self):
        """Check if disambiguation analysis gives the expected output
        """
        self.a.disambiguation_analysis()
        got = self.a.get_disambiguation()
        want = (
            '"<Muhto>"\n\t"muhto" CC <sme> @CVP\n"<gaskkohagaid>"\n'
            '\t"gaskkohagaid" Adv <sme>\n"<,>"\n\t"," CLB\n"<ja>"\n'
            '\t"ja" CC <sme> @CNP\n"<erenoamážit>"\n'
            '\t"erenoamážit" Adv <sme>\n"<dalle_go>"\n'
            '\t"dalle_go" MWE CS <sme> @CVP\n"<lei>"\n'
            '\t"leat" V <sme> IV Ind Prt Sg3 @+FMAINV\n"<buolaš>"\n'
            '\t"buolaš" Sem/Wthr N <sme> Sg Nom\n"<,>"\n'
            '\t"," CLB\n"<de>"\n\t"de" Adv <sme>\n"<aggregáhta>"\n'
            '\t"aggregáhta" N <sme> Sg Nom\n"<billánii>"\n'
            '\t"billánit" V <sme> IV Ind Prt Sg3 @+FMAINV\n"<.>"\n'
            '\t"." CLB\n\n"<¶>"\n\t"¶" CLB\n\n')

        self.assertEqual(got, want.encode('utf8'))

    def test_sme_dependency_output(self):
        """Check if disambiguation analysis gives the expected output
        """
        self.a.dependency_analysis()
        got = self.a.get_dependency()
        want = (
            '"<Muhto>"\n\t"muhto" CC @CVP #1->1\n"<gaskkohagaid>"\n'
            '\t"gaskkohagaid" Adv @ADVL> #2->12\n"<,>"\n'
            '\t"," CLB #3->4\n"<ja>"\n\t"ja" CC @CNP #4->2\n"<erenoamážit>"\n'
            '\t"erenoamážit" Adv @ADVL> #5->12\n"<dalle_go>"\n'
            '\t"dalle_go" CS @CVP #6->7\n"<lei>"\n'
            '\t"leat" V IV Ind Prt Sg3 @FS-ADVL> #7->12\n"<buolaš>"\n'
            '\t"buolaš" N Sg Nom @<SPRED #8->7\n"<,>"\n'
            '\t"," CLB #9->6\n"<de>"\n'
            '\t"de" Adv @ADVL> #10->12\n"<aggregáhta>"\n'
            '\t"aggregáhta" N Sg Nom @SUBJ> #11->12\n"<billánii>"\n'
            '\t"billánit" V IV Ind Prt Sg3 @FS-ADVL> #12->0\n"<.>"\n'
            '\t"." CLB #13->12\n\n"<¶>"\n\t"¶" CLB #1->1\n\n')

        self.assertEqual(got, want.encode('utf8'))

    def test_analysisXml(self):
        """Check if the xml is what it is supposed to be
        """
        self.a.dependency_analysis()
        self.a.get_analysis_xml()
        got = self.a.xml_file.get_etree()
        want = (
            '<document xml:lang="sme" id="no_id">\n'
            '  <header>\n'
            '    <title>Internáhtta sosiálalaš giliguovddážin</title>\n'
            '    <genre code="facta"/>\n'
            '    <author>\n'
            '      <person firstname="Abba" lastname="Abbamar" sex="m" '
            'born="1900" nationality="nor"/>\n'
            '    </author>\n'
            '    <translator>\n'
            '      <person firstname="Ibba" lastname="Ibbamar" sex="unknown" '
            'born="" nationality=""/>\n'
            '    </translator>\n'
            '    <translated_from xml:lang="nob"/>\n'
            '    <year>2005</year>\n'
            '    <publChannel>\n'
            '      <publication>\n'
            '        <publisher>Almmuheaddji OS</publisher>\n'
            '      </publication>\n'
            '    </publChannel>\n'
            '    <wordcount>10</wordcount>\n'
            '    <availability>\n'
            '      <free/>\n'
            '    </availability>\n'
            '    <submitter name="Børre Gaup" '
            'email="boerre.gaup@samediggi.no"/>\n'
            '    <multilingual>\n'
            '      <language xml:lang="nob"/>\n'
            '    </multilingual>\n'
            '    <origFileName>aarseth_s.htm</origFileName>\n'
            '    <metadata>\n'
            '      <uncomplete/>\n'
            '    </metadata>\n'
            '    <version>XSLtemplate  1.9 ; file-specific xsl  '
            '$Revision: 1.3 $; common.xsl  $Revision$; </version>\n'
            '  </header>\n'
            '  <body><disambiguation><![CDATA["<Muhto>"\n'
            '\t"muhto" CC <sme> @CVP\n"<gaskkohagaid>"\n'
            '\t"gaskkohagaid" Adv <sme>\n"<,>"\n\t"," CLB\n"<ja>"\n'
            '\t"ja" CC <sme> @CNP\n"<erenoamážit>"\n'
            '\t"erenoamážit" Adv <sme>\n"<dalle_go>"\n'
            '\t"dalle_go" MWE CS <sme> @CVP\n"<lei>"\n'
            '\t"leat" V <sme> IV Ind Prt Sg3 @+FMAINV\n"<buolaš>"\n'
            '\t"buolaš" Sem/Wthr N <sme> Sg Nom\n"<,>"\n'
            '\t"," CLB\n"<de>"\n\t"de" Adv <sme>\n"<aggregáhta>"\n'
            '\t"aggregáhta" N <sme> Sg Nom\n"<billánii>"\n'
            '\t"billánit" V <sme> IV Ind Prt Sg3 @+FMAINV\n"<.>"\n'
            '\t"." CLB\n\n"<¶>"\n\t"¶" CLB\n\n]]></disambiguation>'
            '<dependency><![CDATA["<Muhto>"\n'
            '\t"muhto" CC @CVP #1->1\n"<gaskkohagaid>"\n'
            '\t"gaskkohagaid" Adv @ADVL> #2->12\n"<,>"\n'
            '\t"," CLB #3->4\n"<ja>"\n\t"ja" CC @CNP #4->2\n"<erenoamážit>"\n'
            '\t"erenoamážit" Adv @ADVL> #5->12\n"<dalle_go>"\n'
            '\t"dalle_go" CS @CVP #6->7\n"<lei>"\n'
            '\t"leat" V IV Ind Prt Sg3 @FS-ADVL> #7->12\n"<buolaš>"\n'
            '\t"buolaš" N Sg Nom @<SPRED #8->7\n"<,>"\n'
            '\t"," CLB #9->6\n"<de>"\n'
            '\t"de" Adv @ADVL> #10->12\n"<aggregáhta>"\n'
            '\t"aggregáhta" N Sg Nom @SUBJ> #11->12\n"<billánii>"\n'
            '\t"billánit" V IV Ind Prt Sg3 @FS-ADVL> #12->0\n"<.>"\n'
            '\t"." CLB #13->12\n\n"<¶>"\n'
            '\t"¶" CLB #1->1\n\n]]></dependency></body></document>')
        self.maxDiff = None
        self.assertEqual(etree.tostring(got, encoding='unicode'), want)
