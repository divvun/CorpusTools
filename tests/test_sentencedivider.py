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
#   Copyright © 2011-2023 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Test sentence division functionality."""

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
            "10. ON-vuogádat",
            "ON doaimmaid oktavuođas;",
            "ovddasvástádus sihkkarastit?",
            "buot ON orgánat!",
            ".....",
            "wow.",
            '"',
            "mom.).",
            "mom.:",
            "kult.",
            "”",
            "váldočoahkkima nammadit.",
            "dievaslaš čađaheami, [2019 – 2020] …",
            "(rávvagiid)",
        ]
        divider = sentencedivider.SentenceDivider("sme")
        self.assertListEqual(divider.make_valid_sentences(ccat_output), want)

    def test_with_dot_and_paragraph(self):
        """Test the sentence divider with a sentence ending with . ¶."""
        ccat_output = """mielddisbuvttii. ¶
Odd Einar Dørum ¶
"""
        want = [
            "mielddisbuvttii.",
            "Odd Einar Dørum",
        ]
        divider = sentencedivider.SentenceDivider("sme")
        self.assertEqual(divider.make_valid_sentences(ccat_output), want)

    def test_with_empty_head_sentence(self):
        """Test the sentence divider with an empty first sentence."""
        ccat_output = """. ¶
Odd Einar Dørum ¶
"""
        want = [
            ".",
            "Odd Einar Dørum",
        ]
        divider = sentencedivider.SentenceDivider("sme")
        self.assertEqual(divider.make_valid_sentences(ccat_output), want)
