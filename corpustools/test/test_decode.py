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
#   Copyright © 2013-2016 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

import unittest

from corpustools import decode

#       "á š č đ ž ŋ Á Č ŧ Š Đ Ŋ Ž Ŧ ø Ø å Å æ Æ",
test_input = {
    u"mac-sami_to_latin1":
        " » ¸ ¹ ½ º ç ¢ ¼ ´ ° ± · µ ¿ ¯   ¾ ®",
    u"mac-sami_to_mac":
        "á ª ∏ π Ω ∫ Á ¢ º ¥ ∞ ± ∑ µ ø Ø å Å æ Æ",
    u"winsami2_to_cp1252":
        "á š „ ˜ ¿ ¹ Á ‚ ¼ Š ‰ ¸ ¾ º ø Ø å Å æ Æ",
    u"mix-mac-sami-and-some-unknown-encoding":
        " _ ã ÷ À ŋ ç â ¼ Š Đ Ŋ Ž Ŧ ¿ Ø å Å æ Æ",
    u"latin4_to_cp1252":
        "á ¹ è ð ¾ ¿ Á È ¼ © Ð ½ ® ¬ ø Ø å Å æ Æ",
    u"winsam_to_cp1252":
        "á ó ç ð þ ñ Á Ç ý Ó Ð Ñ Þ Ý ø Ø å Å æ Æ",
    u"iso-ir-197_to_cp1252":
        "á ³ ¢ ¤ º ± Á ¡ ¸ ² £ ¯ ¹ µ ø Ø å Å æ Æ",
    u"mix-of-latin4-and-iso-ir-197_to_cp1252":
        "á ó ç ¤ º ŋ Á Ç ŧ Ó £ Ŋ Ž Ŧ ø Ø å Å æ Æ",
    u"double-utf8":
        "Ã¡ Å¡ Ä? Ä‘ Âº Å‹ Ã? ÄŒ Å§ Å  Đ ÅŠ Å½ Ŧ Ã¸ Ã˜ Ã¥ Ã… Ã¦ Æ",
    u"finnish-lawtexts-in-pdf":
        "á š þ đ ž ŋ Á Č ŧ Š Đ Ŋ Ž Ŧ ø Ø å Å æ Æ",
}


class TestEncodingGuesser(unittest.TestCase):

    def test_encoding_guesser(self):
        guesser = decode.EncodingGuesser()
        for i in decode.CTYPES.keys():
            self.assertEqual(guesser.guess_body_encoding(
                test_input[i]), i)

    def round_trip_x(self, index):
        eg = decode.EncodingGuesser()

        utf8_content = "á š č đ ž ŋ Á Č ŧ Š Đ Ŋ Ž Ŧ ø Ø å Å æ Æ"

        content = test_input[index]

        test_content = eg.decode_para(index, content)

        self.assertEqual(utf8_content, test_content)

    def test_round_tripping(self):
        for k in test_input.keys():
            self.round_trip_x(k)
