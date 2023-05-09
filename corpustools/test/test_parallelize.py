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


import codecs
import doctest
import os
import unittest

from lxml import doctestcompare, etree

from corpustools import corpuspath, parallelize, tmx

HERE = os.path.dirname(__file__)


class TestTca2SentenceDivider(unittest.TestCase):
    """A test class for the Tca2SentenceDivider class."""

    @staticmethod
    def assertXmlEqual(got, want):
        """Check if two xml snippets are equal."""
        string_got = etree.tostring(got, encoding="unicode")
        string_want = etree.tostring(want, encoding="unicode")

        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(string_want, string_got, 0):
            message = checker.output_difference(
                doctest.Example("", string_want), string_got, 0
            )
            raise AssertionError(message)

    def test_make_sentence_file(self):
        path = corpuspath.make_corpus_path(
            os.path.join(
                HERE,
                "parallelize_data/converted/sme/facta/skuvlahistorja2/",
                "finnmarkkulahka_web_lettere.pdf.xml",
            )
        )

        sentence_divider = parallelize.Tca2SentenceDivider()
        got = sentence_divider.make_sentence_xml(
            path.lang,
            path.converted,
            giella_prefix=os.path.join(HERE, "giella_shared"),
        )

        want = etree.parse(
            os.path.join(
                HERE,
                "parallelize_data/",
                "finnmarkkulahka_web_lettere.pdfsme_sent.xml.test",
            )
        )

        self.assertXmlEqual(got, want)


class TestParallelizeTCA2(unittest.TestCase):
    """A test class for the ParallelizeTCA2 class."""

    def setUp(self):
        self.parallelize = parallelize.ParallelizeTCA2(
            os.path.join(
                HERE,
                "parallelize_data",
                "converted/sme/facta/skuvlahistorja2/",
                "aarseth2-s.html.xml",
            ),
            "nob",
            quiet=True,
            giella_prefix=os.path.join(HERE, "giella_shared"),
        )

    def test_lang1(self):
        self.assertEqual(self.parallelize.lang1, "nob")

    def test_lang2(self):
        self.assertEqual(self.parallelize.lang2, "sme")


class TestParallelizeHunalign(unittest.TestCase):
    """A test class for the ParallelizeHunalign class."""

    def setUp(self):
        self.parallelize = parallelize.ParallelizeHunalign(
            os.path.join(
                HERE,
                "parallelize_data",
                "converted/sme/facta/skuvlahistorja2/",
                "aarseth2-s.html.xml",
            ),
            "nob",
            quiet=True,
        )

    def test_hunalign_dict(self):
        self.assertEqual(
            self.parallelize.anchor_to_dict(
                [
                    ("foo, bar", "fie"),
                    ("1, ein", "eins"),
                    ("2, два", "2, guokte"),
                ]
            ),
            [
                ("foo", "fie"),
                ("bar", "fie"),
                ("1", "eins"),
                ("ein", "eins"),
                ("2", "2"),
                ("2", "guokte"),
                ("два", "2"),
                ("два", "guokte"),
            ],
        )


class TestTmx(unittest.TestCase):
    """A test class for the Tmx class."""

    def setUp(self):
        self.tmx = tmx.Tmx(
            etree.parse(os.path.join(HERE, "parallelize_data/aarseth2-n.htm.toktmx"))
        )

    def assertXmlEqual(self, got, want):
        """Check if two xml snippets are equal."""
        string_got = etree.tostring(got, encoding="unicode")
        string_want = etree.tostring(want, encoding="unicode")

        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(string_want, string_got, 0):
            message = checker.output_difference(
                doctest.Example("", string_want), string_got, 0
            )
            raise AssertionError(message)

    def test_get_src_lang(self):
        """Test the get_src_lang routine."""
        self.assertEqual(self.tmx.src_lang, "nob")

    def test_tu_to_string(self):
        tu = etree.XML(
            '<tu><tuv xml:lang="sme"><seg>Sámegiella</seg></tuv>'
            '<tuv xml:lang="nob"><seg>Samisk</seg></tuv></tu>'
        )

        self.assertEqual(self.tmx.tu_to_string(tu), "Sámegiella\tSamisk\n")

    def test_tuv_to_string(self):
        tuv = etree.XML('<tuv xml:lang="sme"><seg>Sámegiella</seg></tuv>')

        self.assertEqual(self.tmx.tuv_to_string(tuv), "Sámegiella")

    def test_lang_to_string_list(self):
        toktmx_txt_name = os.path.join(
            HERE, "parallelize_data/aarseth2-n.htm.toktmx.as.txt"
        )
        with codecs.open(toktmx_txt_name, encoding="utf8") as toktmx_txt:
            string_list = toktmx_txt.read().split("\n")

            nob_list = []
            sme_list = []
            for string in string_list:
                pair_list = string.split("\t")
                if len(pair_list) == 2:
                    nob_list.append(pair_list[0])
                    sme_list.append(pair_list[1].strip())

            self.assertEqual(self.tmx.lang_to_stringlist("nob"), nob_list)
            self.assertEqual(self.tmx.lang_to_stringlist("sme"), sme_list)

    def test_tmx_to_stringlist(self):
        toktmx_txt_name = os.path.join(
            HERE, "parallelize_data/aarseth2-n.htm.toktmx.as.txt"
        )
        with codecs.open(toktmx_txt_name, encoding="utf8") as toktmx_txt:
            want_list = [l for l in toktmx_txt.readlines()]
            # self.maxDiff = None
            self.assertEqual(self.tmx.tmx_to_stringlist(), want_list)

    def test_prettify_segs(self):
        wantXml = etree.XML(
            '<tu><tuv xml:lang="nob"><seg>ubba gubba. ibba gibba.</seg></tuv>'
            '<tuv xml:lang="sme"><seg>abba gabba. ebba gebba.'
            "</seg></tuv></tu>"
        )
        gotXml = etree.XML(
            '<tu><tuv xml:lang="nob"><seg>ubba gubba. ibba gibba.\n</seg>'
            '</tuv><tuv xml:lang="sme"><seg>abba gabba. ebba gebba.\n</seg>'
            "</tuv></tu>"
        )
        self.assertXmlEqual(self.tmx.prettify_segs(gotXml), wantXml)

    def test_check_if_emtpy_seg(self):
        empty1 = etree.XML(
            '<tu><tuv xml:lang="nob"><seg>ubba gubba. ibba gibba.</seg></tuv>'
            '<tuv xml:lang="sme"><seg></seg></tuv></tu>'
        )
        self.assertRaises(AttributeError, self.tmx.check_if_emtpy_seg, empty1)

        empty2 = etree.XML(
            '<tu><tuv xml:lang="nob"><seg></seg></tuv><tuv xml:lang="sme">'
            "<seg>abba gabba. ebba gebba.</seg></tuv></tu>"
        )
        self.assertRaises(AttributeError, self.tmx.check_if_emtpy_seg, empty2)

    def test_remove_unwanted_space_from_segs(self):
        wantXml = etree.XML(
            '<tu><tuv xml:lang="nob"><seg>[30] (juli) «skoleturer».</seg>'
            '</tuv><tuv xml:lang="sme"><seg>[30] (suoidnemánnu) '
            "«skuvlatuvrrat».</seg></tuv></tu>"
        )
        gotXml = etree.XML(
            '<tu><tuv xml:lang="nob"><seg>[ 30 ] ( juli ) « skoleturer » .\n'
            '</seg></tuv><tuv xml:lang="sme"><seg>[ 30 ] ( suoidnemánnu ) « '
            "skuvlatuvrrat » .\n</seg></tuv></tu>"
        )
        self.assertXmlEqual(self.tmx.remove_unwanted_space_from_segs(gotXml), wantXml)

    def test_remove_unwanted_space_from_string(self):
        got = self.tmx.remove_unwanted_space_from_string(
            "sámesearvvi ; [ 31 ] ( suoidnemánnu ) « skuvlatuvrrat » "
            "bargu lea :  okta , guokte ."
        )
        want = (
            "sámesearvvi; [31] (suoidnemánnu) «skuvlatuvrrat» bargu lea: "
            "okta, guokte."
        )
        self.assertEqual(got, want)

    def test_remove_tu_with_empty_seg(self):
        got_tmx = tmx.Tmx(
            etree.parse(os.path.join(HERE, "parallelize_data/aarseth2-n.htm.toktmx"))
        )
        got_tmx.remove_tu_with_empty_seg()

        want_tmx = tmx.Tmx(
            etree.parse(
                os.path.join(
                    HERE, "parallelize_data/", "aarseth2-n-without-empty-seg.htm.toktmx"
                )
            )
        )

        self.assertXmlEqual(got_tmx.tmx, want_tmx.tmx)


class TestTca2ToTmx(unittest.TestCase):
    """A test class for the Tca2ToTmx class."""

    def setUp(self):
        """Hand the data from the Parallelize class to the tmx class."""
        para = parallelize.ParallelizeTCA2(
            os.path.join(
                HERE,
                "parallelize_data",
                "converted/nob/facta/skuvlahistorja2/",
                "aarseth2-n.html.xml",
            ),
            "sme",
        )
        self.para = para
        self.tmx = tmx.Tca2ToTmx(para.origfiles, para.sentfiles)

    def assertXmlEqual(self, got, want):
        """Check if two xml snippets are equal."""
        string_got = etree.tostring(got, encoding="unicode")
        string_want = etree.tostring(want, encoding="unicode")

        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(string_want, string_got, 0):
            message = checker.output_difference(
                doctest.Example("", string_want), string_got, 0
            )
            raise AssertionError(message)

    def test_make_tu(self):
        line1 = '<s id="1">ubba gubba.</s> <s id="2">ibba gibba.</s>'
        line2 = '<s id="1">abba gabba.</s> <s id="2">ebba gebba.</s>'

        got_tu = self.tmx.make_tu(
            self.tmx.remove_s_tag(line1), self.tmx.remove_s_tag(line2)
        )

        want_tu = etree.XML(
            '<tu><tuv xml:lang="nob"><seg>ubba gubba. ibba gibba.</seg>'
            '</tuv><tuv xml:lang="sme"><seg>abba gabba. ebba gebba.'
            "</seg></tuv></tu>"
        )

        self.assertXmlEqual(got_tu, want_tu)

    def test_make_tuv(self):
        line = '<s id="1">ubba gubba.</s> <s id="2">ibba gibba.</s>'
        lang = "smi"
        got_tuv = self.tmx.make_tuv(self.tmx.remove_s_tag(line), lang)

        want_tuv = etree.XML(
            '<tuv xml:lang="smi"><seg>ubba gubba. ibba gibba.</seg></tuv>'
        )

        self.assertXmlEqual(got_tuv, want_tuv)

    def test_make_tmx_header(self):
        lang = "smi"
        got_tuv = self.tmx.make_tmx_header("filename.tmx", lang)

        want_tuv = etree.XML(
            '<header segtype="sentence" o-tmf="OmegaT TMX" adminlang="en-US" '
            'srclang="smi" datatype="plaintext">'
            '<prop type="x-filename">filename.tmx</prop>'
            "</header>"
        )

        self.assertXmlEqual(got_tuv, want_tuv)

    def test_remove_s_tag(self):
        got = self.tmx.remove_s_tag(
            '<s id="1">ubba gubba.</s> <s id="2">ibba gibba.</s>'
        )
        want = "ubba gubba. ibba gibba."

        self.assertEqual(got, want)

    def test_get_outfile_name(self):
        self.assertEqual(
            self.para.outfile_name,
            os.path.join(
                HERE,
                "parallelize_data",
                "prestable/tmx/nob2sme/facta/skuvlahistorja2",
                "aarseth2-n.html.tmx",
            ),
        )
