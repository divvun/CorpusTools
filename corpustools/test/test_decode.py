# -*- coding: utf-8 -*-

import unittest

from corpustools import decode

class TestEncodingGuesser(unittest.TestCase):
    def testEncodingGuesser(self):
        eg = decode.EncodingGuesser()
        for i in range(0, len(decode.ctypes)):
            self.assertEqual(eg.guessFileEncoding('decode_data/decode-' + str(i) + '.txt'), i)

    def roundTripX(self, x):
        eg = decode.EncodingGuesser()

        f = open('decode_data/decode-utf8.txt')
        utf8_content = f.read()
        f.close()

        f = open('decode_data/decode-' + str(x) + '.txt')
        content = f.read()
        f.close()

        test_content = eg.decodePara(x, content)

        self.assertEqual(utf8_content, test_content)

    def testRoundTripping0(self):
        self.roundTripX(0)

    def testRoundTripping1(self):
        self.roundTripX(1)

    def testRoundTripping2(self):
        self.roundTripX(2)

    def testRoundTripping3(self):
        self.roundTripX(3)

    def testRoundTripping4(self):
        self.roundTripX(4)

    def testRoundTripping5(self):
        self.roundTripX(5)

    def testRoundTripping6(self):
        self.roundTripX(6)

    def testRoundTripping7(self):
        self.roundTripX(7)

    def testRoundTripping8(self):
        self.roundTripX(8)

    def testRoundTrippingFalsePositive(self):
        eg = decode.EncodingGuesser()
        self.assertEqual(eg.guessFileEncoding('decode_data/decode-falsepositive.txt'), -1)
