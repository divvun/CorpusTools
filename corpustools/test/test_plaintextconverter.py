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
#   Copyright © 2014-2021 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Test conversion of plaintext files."""

import codecs
import io
import os

import lxml.etree as etree

from corpustools import plaintextconverter
from corpustools.test import xmltester

HERE = os.path.dirname(__file__)


class TestPlaintextConverter(xmltester.XMLTester):
    """Test the PlaintextConverter."""

    def test_to_unicode(self):
        """Check that winsami2 is converted to unicode."""
        plaintext = plaintextconverter.PlaintextConverter(
            os.path.join(
                HERE,
                "converter_data/fakecorpus/orig/sme/riddu/" "winsami2-test-ws2.txt",
            )
        )
        got = plaintext.to_unicode()

        # Ensure that the data in want is unicode
        file_ = codecs.open(
            os.path.join(HERE, "converter_data/winsami2-test-utf8.txt"), encoding="utf8"
        )
        want = file_.read()
        file_.close()

        self.assertEqual(got, want)

    def test_strip_chars1(self):
        """Check that weird chars are converted as exptected."""
        plaintext = plaintextconverter.PlaintextConverter("orig/sme/riddu/tullball.txt")
        got = plaintext.strip_chars(
            "\x0d\n" "<ASCII-MAC>\n" "<vsn:3.000000>\n" "<\\!q>\n" "<\\!h>\n"
        )
        want = """\n\n\n\n\n\n"""

        self.assertEqual(got, want)

    def test_strip_chars2(self):
        """Check that special chars are converted as expected."""
        plaintext = plaintextconverter.PlaintextConverter("orig/sme/riddu/tullball.txt")
        got = plaintext.strip_chars(
            "<0x010C><0x010D><0x0110><0x0111><0x014A><0x014B><0x0160><0x0161>"
            "<0x0166><0x0167><0x017D><0x017E><0x2003>"
        )
        want = """ČčĐđŊŋŠšŦŧŽž """

        self.assertEqual(got, want)

    def test_plaintext(self):
        """Check that an empty line signal paragraph."""
        plaintext = plaintextconverter.PlaintextConverter("orig/sme/riddu/tullball.txt")
        got = plaintext.content2xml(
            io.StringIO(
                """Sámegiella.

Buot leat."""
            )
        )

        want = etree.fromstring(
            r"""<document>
    <header/>
    <body>
        <p>
            Sámegiella.
        </p>
        <p>
           Buot leat.
       </p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_two_lines(self):
        """Test that two consecutive lines are treated as a paragraph."""
        newstext = plaintextconverter.PlaintextConverter("orig/sme/admin/tullball.txt")
        got = newstext.content2xml(
            io.StringIO(
                """Guovssahasa nieida.
Filbma lea.
"""
            )
        )
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p>Guovssahasa nieida.
Filbma lea.</p>
    </body>
</document>
"""
        )

        self.assertXmlEqual(got, want)

    def test_hyph(self):
        """Check that hyph is conserved."""
        newstext = plaintextconverter.PlaintextConverter("orig/sme/riddu/tullball.txt")
        got = newstext.content2xml(io.StringIO("Guovssa<hyph/>hasa"))
        want = etree.fromstring(
            """
            <document>
            <header/>
            <body>
                <p>Guovssa<hyph/>hasa</p>
            </body>
            </document> """
        )

        self.assertXmlEqual(got, want)

    def test_skip_lines(self):
        """Check that lines are skipped."""
        content = """
a

b

c

d

e
"""
        want_string = """
<document>
    <header/>
    <body>
        <p>a</p>
        <p>d</p>
        <p>e</p>
    </body>
</document>
"""
        text = plaintextconverter.PlaintextConverter("orig/sme/riddu/tullball.txt")
        text.metadata.set_variable("skip_lines", "4-6")
        got = text.content2xml(io.StringIO(content))
        want = etree.fromstring(want_string)

        self.assertXmlEqual(got, want)
