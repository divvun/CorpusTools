# -*- coding: utf-8 -*-

import unittest

from corpustools import util

class TestSplitPath(unittest.TestCase):
    def test_split_converted(self):
        self.assertEqual(
            util.split_path("/home/me/src/freecorpus-git/converted/sma/admin/"
                            "depts/other_files/tips.html.xml"),
            ('/home/me/src/freecorpus-git',
             'converted',
             'sma',
             'admin',
             'depts/other_files',
             'tips.html.xml'))

    def test_split_orig(self):
        self.assertEqual(
            util.split_path("/home/me/freecorpus/orig/nob/bible/osko/omoss.html"),
            ('/home/me/freecorpus',
             'orig',
             'nob',
             'bible',
             'osko',
             'omoss.html'))
