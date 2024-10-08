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
#   Copyright © 2013-2023 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#


import codecs
import unittest

from parameterized import parameterized

from corpustools import decode, util


def handler(err):
    """Handle UnicodeDecodeError.

    Args:
        err (exceptions.UnicodeDecodeError): the error.

    Returns:
        (str): The fixed string
    """
    start = err.start
    end = err.end
    return (
        "".join([f"&#{err.object[i]};" for i in range(start, end)]),
        end,
    )


codecs.register_error("backslashreffcallback", handler)

want = "á š č đ ž ŋ Á Č ŧ Š Đ Ŋ Ž Ŧ ø Ø å Å æ Æ"

test_input = {
    "mac-sami_to_cp1252": ["‡ » ¸ ¹ ½ º ç ¢ ¼ ´ ° ± · µ ¿ ¯ Œ  ¾ ®"],
    "mac-sami_to_latin1": [" » ¸ ¹ ½ º ç ¢ ¼ ´ ° ± · µ ¿ ¯   ¾ ®"],
    "mac-sami_to_mac": ["á ª ∏ π Ω ∫ Á ¢ º ¥ ∞ ± ∑ µ ø Ø å Å æ Æ"],
    "winsami2_to_cp1252": ["á š „ ˜ ¿ ¹ Á ‚ ¼ Š ‰ ¸ ¾ º ø Ø å Å æ Æ"],
    "mix-mac-sami-and-some-unknown-encoding": [
        " _ ã ÷ À ŋ ç â ¼ Š Đ Ŋ Ž Ŧ ¿ Ø å Å æ Æ"
    ],
    "latin4_to_cp1252": ["á ¹ è ð ¾ ¿ Á È ¼ © Ð ½ ® ¬ ø Ø å Å æ Æ"],
    "winsam_to_cp1252": ["á ó ç ð þ ñ Á Ç ý Ó Ð Ñ Þ Ý ø Ø å Å æ Æ"],
    "iso-ir-197_to_cp1252": ["á ³ ¢ ¤ º ± Á ¡ ¸ ² £ ¯ ¹ µ ø Ø å Å æ Æ"],
    "mix-of-latin4-and-iso-ir-197_to_cp1252": [
        "á ó ç ¤ º ŋ Á Ç ŧ Ó £ Ŋ Ž Ŧ ø Ø å Å æ Æ"
    ],
    "double-utf8": ["Ã¡ Å¡ Ä? Ä‘ Âº Å‹ Ã? ÄŒ Å§ Å  Đ ÅŠ Å½ Ŧ Ã¸ Ã˜ Ã¥ Ã… Ã¦ Æ"],
    "finnish-lawtexts-in-pdf": ["á š þ đ ž ŋ Á Č ŧ Š Đ Ŋ Ž Ŧ ø Ø å Å æ Æ"],
}


class TestEncodingGuesser(unittest.TestCase):
    @parameterized.expand(
        [
            (index, example)
            for index in decode.CTYPES.keys()
            for example in test_input[index]
        ]
    )
    def test_encoding_guesser(self, index, example):
        self.assertEqual(decode.guess_body_encoding(example, "sme"), index)

    @parameterized.expand([(index) for index in test_input.keys()])
    def test_round_trip_x(self, index):
        unicode_content = "á š č đ ž ŋ Á Č ŧ Š Đ Ŋ Ž Ŧ ø Ø å Å æ Æ"
        content = test_input[index][0]
        test_content = decode.decode_para(index, content)

        self.assertEqual(unicode_content, test_content)

    @staticmethod
    def to_pervertedsami(instring, from_enc, to_enc):
        util.print_frame(type(instring), from_enc, to_enc)
        encoded_string = instring.encode(from_enc)
        decoded_string = encoded_string.decode(to_enc, errors="backslashreffcallback")

        return decoded_string

    def test_macsami_cp1252(self):
        uff = "áÁšŠŧŦŋŊđĐžŽčČøØöÖåÅäÄǯǮʒƷǧǦǥǤǩǨ"
        perverted = self.to_pervertedsami(uff, "macsami", "cp1252")
        util.print_frame("\n", perverted)
        util.print_frame("\n", decode.fix_macsami_cp1252(perverted))
        self.assertEqual(decode.fix_macsami_cp1252(perverted), uff)
        self.assertEqual(
            decode.fix_macsami_cp1252(test_input["mac-sami_to_cp1252"][0]), want
        )

    def test_macsami_latin1(self):
        uff = "áÁšŠŧŦŋŊđĐžŽčČøØöÖåÅäÄǯǮʒƷǧǦǥǤǩǨ"
        perverted = self.to_pervertedsami(uff, "macsami", "latin1")
        util.print_frame("\n", perverted)
        util.print_frame("\n", decode.fix_macsami_latin1(perverted))
        self.assertEqual(decode.fix_macsami_latin1(perverted), uff)
        self.assertEqual(
            decode.fix_macsami_latin1(test_input["mac-sami_to_latin1"][0]), want
        )

    def test_macsami_mac(self):
        uff = "áÁšŠŧŦŋŊđĐžŽčČøØöÖåÅäÄǯǮʒƷǧǦǥǤǩǨ"
        perverted = self.to_pervertedsami(uff, "macsami", "macroman")
        util.print_frame("\n", perverted)
        util.print_frame("\n", decode.fix_macsami_mac(perverted))
        self.assertEqual(decode.fix_macsami_mac(perverted), uff)
        self.assertEqual(decode.fix_macsami_mac(test_input["mac-sami_to_mac"][0]), want)

    def test_winsami2_cp1252(self):
        uff = "áÁšŠŧŦŋŊđĐžŽčČøØöÖåÅäÄǯǮʒƷǧǦǥǤǩǨ"
        perverted = self.to_pervertedsami(uff, "ws2", "cp1252")
        util.print_frame("\n", perverted)
        util.print_frame("\n", decode.fix_winsami2_cp1252(perverted))
        self.assertEqual(decode.fix_winsami2_cp1252(perverted), uff)
        self.assertEqual(
            decode.fix_winsami2_cp1252(test_input["winsami2_to_cp1252"][0]), want
        )

    def test_meadowmari_cp1252(self):
        correct = "ОЙСАВЫШ 139 В.ЕГОРОВ. Романыште ҥ Ҥ ӱ Ӱ ӧ Ӧ ӱ Ӱ ӧ Ӧ"
        uncorrect = "ÎÉÑÀÂÛØ 139 Â.ÅÃÎÐÎÂ. Ðîìàíûøòå ‰ ˆ ¢ ™ º ª ў Ў є Є"
        self.assertEqual(decode.fix_meadowmari_cp1252(uncorrect), correct)

    def test_macsami_macroman(self):
        uff = "Ω"
        self.assertEqual(decode.fix_macsami_mac(uff), "ž")

    def test_winsami2_cp1252_with_dstroke(self):
        uff = "đ"
        self.assertEqual(decode.fix_macsami_mac(uff), "&#273;")
