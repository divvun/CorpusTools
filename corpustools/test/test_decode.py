# -*- coding: utf-8 -*-

import unittest

from corpustools import decode

   #"á š č đ ž ŋ Á Č ŧ Š Đ Ŋ Ž Ŧ ø Ø å Å æ Æ",
test_input = {
    u"mac-sami_to_mac": "á ª ∏ π Ω ∫ Á ¢ º ¥ ∞ ± ∑ µ ø Ø å Å æ Æ",
    u"winsami2_to_cp1252": "á š „ ˜ ¿ ¹ Á ‚ ¼ Š ‰ ¸ ¾ º ø Ø å Å æ Æ",
    u"iso-ir-197_to_cp1252": "á ³ ¢ ¤ º ± Á ¡ ¸ ² £ ¯ ¹ µ ø Ø å Å æ Æ",
    u"mac-sami_to_latin1": " » ¸ ¹ ½ º ç ¢ ¼ ´ ° ± · µ ¿ ¯ Œ  ¾ ®",
    u"winsam_to_cp1252": "á ó ç ð þ ñ Á Ç ý Ó Ð Ñ Þ Ý ø Ø å Å æ Æ",
    u"latin4_to_cp1252": "á ¹ è ð ¾ ¿ Á È ¼ © Ð ½ ® ¬ ø Ø å Å æ Æ",
    u"mix-of-latin4-and-iso-ir-197_to_cp1252": "á ó ç ¤ º ŋ Á Ç ŧ Ó £ Ŋ Ž Ŧ ø Ø å Å æ Æ",
    u"mix-mac-sami-and-some-unknown-encoding": " _ ã ÷ À ŋ ç â ¼ Š Đ Ŋ Ž Ŧ ¿ Ø å Å æ Æ",
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

        print test_content
        print utf8_content

        self.assertEqual(utf8_content, test_content)

    def test_round_tripping(self):
        for k in test_input.keys():
            self.round_trip_x(k)
