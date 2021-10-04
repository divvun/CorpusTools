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
#   Copyright © 2014-2020 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Test the Converter class."""


import os

import lxml.etree as etree

from corpustools import converter, text_cat, util, xslsetter
from corpustools.test.xmltester import XMLTester

HERE = os.path.dirname(__file__)
LANGUAGEGUESSER = text_cat.Classifier(None)


class TestConverter(XMLTester):
    """Test the converter class."""

    def setUp(self):
        self.converter_inside_orig = converter.Converter(
            os.path.join(
                HERE,
                "converter_data/fakecorpus/orig/nob/admin/samediggi-" "article-16.html",
            ),
            True,
        )

    def test_get_orig(self):
        """Get the original name."""
        self.assertEqual(
            self.converter_inside_orig.names.orig,
            os.path.join(
                HERE,
                "converter_data/fakecorpus/orig/nob/admin/samediggi-article-" "16.html",
            ),
        )

    def test_get_xsl(self):
        """Get the name of the metadata file."""
        self.assertEqual(
            self.converter_inside_orig.names.xsl,
            os.path.join(
                HERE,
                "converter_data/fakecorpus/orig/nob/admin/samediggi-"
                "article-16.html.xsl",
            ),
        )

    def test_get_tmpdir(self):
        """Get the temp dir."""
        self.assertEqual(
            self.converter_inside_orig.tmpdir,
            os.path.join(HERE, "converter_data/fakecorpus/tmp"),
        )

    def test_get_corpusdir(self):
        """Get the corpus directory."""
        self.assertEqual(
            self.converter_inside_orig.corpusdir.rstrip(os.path.sep),
            os.path.join(HERE, "converter_data/fakecorpus"),
        )

    def test_get_converted_name(self):
        """Get the name of the converted file."""
        self.assertEqual(
            self.converter_inside_orig.names.converted,
            os.path.join(
                HERE,
                "converter_data/fakecorpus/converted/nob/admin/samediggi-"
                "article-16.html.xml",
            ),
        )

    def test_validate_complete(self):
        """Check that an exception is raised if a document is invalid."""
        complete = etree.fromstring("<document/>")

        self.assertRaises(
            util.ConversionError, self.converter_inside_orig.validate_complete, complete
        )

    def test_detect_quote_is_skipped_on_errormarkup_documents(self):
        """quote detection should not be done in errormarkup documents

        This is a test for that covers the case covered in
        http://giellatekno.uit.no/bugzilla/show_bug.cgi?id=2151
        """
        want_string = """
            <document xml:lang="smj" id="no_id">
            <header>
                <title/>
                <genre code="ficti"/>
                <year>2011</year>
                <wordcount>15</wordcount>
            </header>
                <body>
                    <p>
                        Lev lähkám Skánen,
                        <errorort correct="Evenskjeran" errorinfo="vowm,á-a">
                            Evenskjerán
                        </errorort>
                        Sáme
                        <errorort correct="gilppusijn" errorinfo="infl">
                            gilppojn
                        </errorort>
                        ja lev aj dán vahko lähkám
                        <errorort
                            correct="&quot;hárjjidallamskåvlån&quot;"
                            errorinfo="conc,rj-rjj;cmp,2-X">
                                hárjidallam-"skåvlån"
                        </errorort>
                        <errorort correct="tjuojggusijn" errorinfo="vowlat,o-u">
                            tjuojggosijn
                        </errorort>.
                    </p>
                </body>
            </document>
        """
        got = etree.fromstring(want_string)

        conv = converter.Converter("orig/sme/admin/blogg_5.correct.txt")
        conv.metadata = xslsetter.MetadataHandler(conv.names.xsl, create=True)
        conv.metadata.set_variable("conversion_status", "correct")
        conv.fix_document(got)

        self.assertXmlEqual(got, etree.fromstring(want_string))
