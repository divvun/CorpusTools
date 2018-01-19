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
#   Copyright © 2011-2018 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Test sentence division functionality."""
from __future__ import absolute_import, print_function, unicode_literals

import unittest

from corpustools import sentencedivider


class TestSentenceDivider(unittest.TestCase):
    """Test the SentenceDivider class."""

    def test_ccat_input(self):
        """Test the sentence divider."""
        ccat_output = """10. ON-vuogádat ¶
ON doaimmaid oktavuođas; ovddasvástádus sihkkarastit? buot ON orgánat!
..... ¶
wow." ¶
mom.). ¶
mom.: ¶
kult.” ¶
váldočoahkkima nammadit. dievaslaš čađaheami, [2019 – 2020] … ¶
(rávvagiid) ¶
"""
        want = [
            '10. ON-vuogádat',
            'ON doaimmaid oktavuođas;',
            'ovddasvástádus sihkkarastit?',
            'buot ON orgánat!',
            'wow."',
            'mom.).',
            'mom.:',
            'kult.”',
            'váldočoahkkima nammadit.',
            'dievaslaš čađaheami, [2019 – 2020] …',
            '(rávvagiid)',
        ]
        divider = sentencedivider.SentenceDivider('sme')
        self.assertListEqual(divider.make_valid_sentences(ccat_output), want)

    def test_with_dot_and_paragraph(self):
        """Test the sentence divider with a sentence ending with . ¶."""
        ccat_output = """mielddisbuvttii. ¶
Odd Einar Dørum ¶
"""
        want = [
            'mielddisbuvttii.',
            'Odd Einar Dørum',
        ]
        divider = sentencedivider.SentenceDivider('sme')
        self.assertEqual(divider.make_valid_sentences(ccat_output), want)

    def test_with_empty_head_sentence(self):
        """Test the sentence divider with an empty first sentence."""
        ccat_output = """. ¶
Odd Einar Dørum ¶
"""
        want = [
            'Odd Einar Dørum',
        ]
        divider = sentencedivider.SentenceDivider('sme')
        self.assertEqual(divider.make_valid_sentences(ccat_output), want)


class TestTrainingCorpusMaker(unittest.TestCase):
    """Test the TrainingCorpusMaker class.

    Attributes:
        sentencemaker (corpustools.TrainingCorpusMaker)
    """

    def setUp(self):
        """Set up the TrainingCorpusMaker."""
        self.sentencemaker = sentencedivider.TrainingCorpusMaker()

    def test_no_unknown(self):
        """Test with only known input."""
        test_input = '\n'.join([
            '"<Oahpa>"',
            '\t"Oahpa" N Prop Sem/Obj Sg Nom <W:0.0000000000> @HNOUN #1->0',
            '"<:>"',
            '\t":" CLB <W:0.0000000000> #2->1',
            ': ',
            '"<Soahki>"',
            '\t"soahki" N Sem/Plant Sg Nom <W:0.0000000000> @HNOUN #3->1',
            ': ',
            '"<¶>"',
            '\t"¶" CLB <W:0.0000000000> #4->1',
            ':\n',
            '"<addit>"',
            '\t"addit" V TV Inf <W:0.0000000000> @FS-N<IMV #13->11',
            ': ',
            '"<boahtte>"',
            '\t"boahtte" A Sem/Dummytag Attr <W:0.0000000000> @>N #14->15',
            ': ',
            '"<bulvii>"',
            '\t"buolva" N Sem/Body_Group_Hum_Time Sg Ill <W:0.0000000000> @<ADVL #15->13',
            '"<.>"',
            '\t"." CLB <W:0.0000000000> #16->4',
            ': ',
            '',
            '"<¶>"',
            '\t"¶" CLB <W:0.0000000000> #1->1',
            ':\n',
            '',
        ])

        want = 'Oahpa: Soahki\naddit boahtte bulvii.'
        got = '\n'.join([
            sentence
            for sentence in self.sentencemaker.parse_dependency(test_input)
            if sentence
        ])
        self.assertEqual(got, want)

    def test_with_comma(self):
        """Check that comma is handled correctly."""
        test_input = '\n'.join([
            '"<áhkuin>"',
            '\t"áhkku" N Sem/Hum Sg Com <W:0.0000000000> @<ADVL #6->1',
            '"<,>"',
            '\t"," CLB <W:0.0000000000> #7->6',
            ': ',
            '"<ádjáin>"',
            '\t"áddjá" N Sem/Hum Sg Com <W:0.0000000000> @<ADVL #8->1',
            ': ',
            '"<dahje>"',
            '\t"dahje" CC <W:0.0000000000> @CNP #9->8',
            ': ',
            '"<earáin>"',
            '\t"eará" Pron Indef Sg Com <W:0.0000000000> @<ADVL #10->1',
            '"<!>"',
            '\t"!" CLB <W:0.0000000000> #13->1',
            ': ',
            '',
            '"<¶>"',
            '\t"¶" CLB <W:0.0000000000> #1->1',
            ':\n',
        ])

        want = 'áhkuin, ádjáin dahje earáin!'
        got = '\n'.join([
            sentence
            for sentence in self.sentencemaker.parse_dependency(test_input)
            if sentence
        ])
        self.assertEqual(got, want)
