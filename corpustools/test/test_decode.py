# -*- coding: utf-8 -*-

import unittest

from corpustools import decode


class TestEncodingGuesser(unittest.TestCase):
    def test_encoding_guesser(self):
        guesser = decode.EncodingGuesser()
        for i in range(0, len(decode.CTYPES)):
            self.assertEqual(guesser.guess_file_encoding(
                'decode_data/decode-' +
                str(i) + '.txt'), i)

    def round_trip_x(self, index):
        eg = decode.EncodingGuesser()

        utf8 = open('decode_data/decode-utf8.txt')
        utf8_content = utf8.read()
        utf8.close()

        eight_bit = open('decode_data/decode-' + str(index) + '.txt')
        content = eight_bit.read()
        eight_bit.close()

        test_content = eg.decode_para(index, content)

        self.assertEqual(utf8_content, test_content)

    def test_round_tripping0(self):
        self.round_trip_x(0)

    def test_round_tripping1(self):
        self.round_trip_x(1)

    def test_round_tripping2(self):
        self.round_trip_x(2)

    def test_round_tripping3(self):
        self.round_trip_x(3)

    def test_round_tripping4(self):
        self.round_trip_x(4)

    def test_round_tripping5(self):
        self.round_trip_x(5)

    def test_round_tripping6(self):
        self.round_trip_x(6)

    def test_round_tripping7(self):
        self.round_trip_x(7)

    def test_round_tripping8(self):
        self.round_trip_x(8)

    def test_round_tripping_false_positive(self):
        guesser = decode.EncodingGuesser()
        self.assertEqual(
            guesser.guess_file_encoding(
                'decode_data/decode-falsepositive.txt'), -1)
