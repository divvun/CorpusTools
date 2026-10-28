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
#   Copyright © 2014-2023 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Test the converter module."""

import tempfile
from pathlib import Path

from lxml import etree

from corpustools import converter, util
from corpustools.corpuspath import CorpusPath
from tests.xmltester import XMLTester


class TestConverter(XMLTester):
    """Test the converter functions."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.names = CorpusPath(
            root=Path(self.tmp.name),
            lang="nob",
            filepath=Path("admin/samediggi-article-16.html"),
        )

    def test_get_tmpdir(self):
        """Get the temp dir."""
        self.assertEqual(
            converter.get_tmpdir(self.names),
            Path(self.tmp.name) / "corpus-nob" / "tmp",
        )

    def test_dependencies(self):
        """The orig file and the metadata file are dependencies."""
        self.assertEqual(
            converter.dependencies(self.names), [self.names.orig, self.names.xsl]
        )

    def test_validate_complete(self):
        """Check that an exception is raised if a document is invalid."""
        self.names.log.parent.mkdir(parents=True)
        complete = etree.fromstring("<document/>")

        self.assertRaises(
            util.ConversionError, converter.validate_complete, complete, self.names
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

        self.names.metadata.set_variable("conversion_status", "correct")
        converter.fix_document(got, self.names)

        self.assertXmlEqual(got, etree.fromstring(want_string))
