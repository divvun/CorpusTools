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


import collections
import io
import os

from lxml import etree

from corpustools import documentfixer, plaintextconverter, svgconverter
from corpustools.test.test_xhtml2corpus import assertXmlEqual
from corpustools.test.xmltester import XMLTester

HERE = os.path.dirname(__file__)

TestItem = collections.namedtuple("TestItem", ["name", "orig", "expected"])


def test_detect_quote():
    """Test the detect_quote function."""
    quote_tests = [
        TestItem(
            name="quote within QUOTATION MARK",
            orig='<p>bla "bla" bla "bla" bla </p>',
            expected=(
                '<p>bla <span type="quote">"bla"</span> bla'
                '<span type="quote">"bla"</span> bla</p>'
            ),
        ),
        TestItem(
            name="quote within RIGHT DOUBLE QUOTATION MARK",
            orig="<p>bla bla ”bla bla” bla bla </p>",
            expected=('<p>bla bla <span type="quote">”bla bla”</span> ' "bla bla</p>"),
        ),
        TestItem(
            name=(
                "quote within LEFT DOUBLE QUOTATION MARK and "
                "RIGHT DOUBLE QUOTATION MARK"
            ),
            orig="<p>bla bla “bla bla” bla bla</p>",
            expected=('<p>bla bla <span type="quote">“bla bla”</span> bla bla</p>'),
        ),
        TestItem(
            name=(
                "quote within RIGHT DOUBLE QUOTATION MARK and "
                "quote within LEFT DOUBLE QUOTATION MARK and "
                "RIGHT DOUBLE QUOTATION MARK"
            ),
            orig="<p>bla “bla” bla ”bla” bla</p>",
            expected=(
                '<p>bla <span type="quote">“bla”</span> bla '
                '<span type="quote">”bla”</span> bla</p>'
            ),
        ),
        TestItem(
            name="simple_detect_quote3",
            orig="<p>bla bla «bla bla» bla bla</p>",
            expected=('<p>bla bla <span type="quote">«bla bla»</span> ' "bla bla</p>"),
        ),
        TestItem(
            name="simple_detect_quote4",
            orig='<p type="title">Sámegiel čálamearkkat Windows XP várás.</p>',
            expected=('<p type="title">Sámegiel čálamearkkat Windows XP várás.</p>'),
        ),
        TestItem(
            name="simple_detect_quote2_quotes",
            orig="<p>bla bla «bla bla» bla bla «bla bla» bla bla</p>",
            expected=(
                '<p>bla bla <span type="quote">«bla bla»</span> bla bla '
                '<span type="quote">«bla bla»</span> bla bla</p>'
            ),
        ),
        TestItem(
            name="detect_quote_with_following_tag",
            orig="<p>bla bla «bla bla» <em>bla bla</em></p>",
            expected=(
                '<p>bla bla <span type="quote">«bla bla»</span> <em>' "bla bla</em></p>"
            ),
        ),
        TestItem(
            name="detect_quote_with_tag_infront",
            orig="<p>bla bla <em>bla bla</em> «bla bla»</p>",
            expected=(
                '<p>bla bla <em>bla bla</em> <span type="quote">' "«bla bla»</span></p>"
            ),
        ),
        TestItem(
            name="detect_quote_within_tag",
            orig="<p>bla bla <em>bla bla «bla bla»</em></p>",
            expected=(
                '<p>bla bla <em>bla bla <span type="quote">' "«bla bla»</span></em></p>"
            ),
        ),
    ]

    for i in ".,?!:":
        quote_tests.append(
            TestItem(
                name=f"quote followed by {i}",
                orig=(f"<p>“bla”{i} bla ”bla”</p>"),
                expected=(
                    '<p><span type="quote">“bla”</span>{} bla '
                    '<span type="quote">”bla”</span></p>'.format(i)
                ),
            )
        )

    for name, orig, expected in quote_tests:
        yield check_quote_detection, name, orig, expected


def check_quote_detection(name, orig, expected):
    document_fixer = documentfixer.DocumentFixer(
        etree.parse(
            os.path.join(
                HERE,
                "converter_data/samediggi-article-48s-before-"
                "lang-detection-without-multilingual-tag.xml",
            )
        )
    )
    got_paragraph = document_fixer._detect_quote(etree.fromstring(orig))

    assertXmlEqual(got_paragraph, etree.fromstring(expected))


class TestDocumentFixer(XMLTester):
    """Test the DocumentFixer class."""

    def test_insert_spaces_after_semicolon(self):
        a = {
            "Govven:Á": "Govven: Á",
            "govven:á": "govven: á",
            "GOVVEN:Á": "GOVVEN: Á",
            "Govva:Á": "Govva: Á",
            "govva:á": "govva: á",
            "GOVVA:Á": "GOVVA: Á",
            "GOVVEJEADDJI:Á": "GOVVEJEADDJI: Á",
            "Govva:": "Govva:",
            "<em>Govven:Á</em>": "<em>Govven: Á</em>",
        }
        for key, value in a.items():
            document_fixer = documentfixer.DocumentFixer(
                etree.fromstring(
                    """
                <document>
                    <header/>
                    <body>
                        <p>"""
                    + key
                    + """</p>
                    </body>
                </document>
            """
                )
            )
            document_fixer.insert_spaces_after_semicolon()
            got = document_fixer.get_etree()
            want = etree.fromstring(
                """
                <document>
                    <header/>
                    <body>
                        <p>"""
                + value
                + """</p>
                    </body>
                </document>
            """
            )

            self.assertXmlEqual(got, want)

    def test_fix_newstags_bold_1(self):
        """Test conversion of the @bold: newstag."""
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@bold:buoidi
seaggi</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p><em type="bold">buoidi</em></p>
        <p>seaggi</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_fix_newstags_bold_2(self):
        """Test conversion of the @bold: newstag."""
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@bold:buoidi
@tekst:seaggi</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p><em type="bold">buoidi</em></p>
        <p>seaggi</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_fix_newstags_bold_3(self):
        """Test conversion of the @bold: newstag."""
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@bold :DON</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p><em type="bold">DON</em></p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_byline1(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <author>
            <unknown/>
        </author>
    </header>
    <body>
        <p>@byline: Kárášjohka: Elle Merete Utsi</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(
            """<document>
    <header>
        <author>
            <person firstname="" lastname="Elle Merete Utsi"/>
        </author>
    </header>
    <body/>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_byline2(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <author>
            <unknown/>
        </author>
    </header>
    <body>
        <p>&lt;pstyle:byline&gt;NORGA: Åse Pulk</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(
            """<document>
    <header>
        <author>
            <person firstname="" lastname="Åse Pulk"/>
        </author>
    </header>
    <body/>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_byline3(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <author>
            <unknown/>
        </author>
    </header>
    <body>
        <p>@byline:KçRç´JOHKA:Elle Merete Utsi</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(
            """<document>
    <header>
        <author>
            <person firstname="" lastname="Elle Merete Utsi"/>
        </author>
    </header>
    <body/>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_byline4(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <author>
            <unknown/>
        </author>
    </header>
    <body>
        <p>@byline:Elle Merete Utsi</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(
            """<document>
    <header>
        <author>
            <person firstname="" lastname="Elle Merete Utsi"/>
        </author>
    </header>
    <body/>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_byline5(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <author>
            <unknown/>
        </author>
    </header>
    <body>
        <p> @byline:Elle Merete Utsi</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(
            """<document>
    <header>
        <author>
            <person firstname="" lastname="Elle Merete Utsi"/>
        </author>
    </header>
    <body/>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_byline6(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <author>
            <person firstname="" lastname="Juvven"/>
        </author>
    </header>
    <body>
        <p> @byline:Elle Merete Utsi</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(
            """<document>
    <header>
        <author>
            <person firstname="" lastname="Juvven"/>
        </author>
    </header>
    <body/>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_byline7(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <author>
            <unknown/>
        </author>
    </header>
    <body>
        <p> @BYLINE:Elle Merete Utsi</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(
            """<document>
    <header>
        <author>
            <person firstname="" lastname="Elle Merete Utsi"/>
        </author>
    </header>
    <body/>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_byline8(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <author>
            <unknown/>
        </author>
    </header>
    <body>
        <p><em>@BYLINE:Elle Merete Utsi </em> </p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(
            """<document>
    <header>
        <author>
            <person firstname="" lastname="Elle Merete Utsi"/>
        </author>
    </header>
    <body/>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_kursiv(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@kursiv:(Gáldu)</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(
            r"""<document>
    <header/>
    <body>
        <p><em type="italic">(Gáldu)</em></p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_ledtekst(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@LEDtekst:Dat mearkkaša</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(
            r"""<document>
    <header/>
    <body>
        <p>Dat mearkkaša</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_bildetekst(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>Bildetekst:Dat mearkkaša</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(
            r"""<document>
    <header/>
    <body>
        <p>Dat mearkkaša</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_logo(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@logo:Finnmark jordskifterett</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(
            r"""<document>
    <header/>
    <body>
        <p>Finnmark jordskifterett</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_fotobyline(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@fotobyline:Finnmark jordskifterett</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(
            r"""<document>
    <header/>
    <body>
        <p>Finnmark jordskifterett</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_foto(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@foto: govva1</p>
        <p><em>foto: govva2</em></p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(
            r"""<document>
    <header/>
    <body>
        <p>govva1</p>
        <p><em>govva2</em></p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_bildetitt(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@bildetitt:Finnmark jordskifterett</p>
        <p>Bildetitt:Finnmark jordskifterett</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(
            r"""<document>
    <header/>
    <body>
        <p>Finnmark jordskifterett</p>
        <p>Finnmark jordskifterett</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_bilde(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@bilde:NSR PRESIDEANTAEVTTOHAS? Berit Ranveig Nilssen
B 13  @bilde:DEANU-LEAGIS: Nils Porsanger.
B8  @bilde:SOHPPARIS: Bajit-Sohpparis Nils Andersen.
@bilde :E
BILDE 3:oahppat
&lt;pstyle:bilde&gt;Ii
Billedtekst: 3</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p>NSR PRESIDEANTAEVTTOHAS? Berit Ranveig Nilssen</p>
        <p>DEANU-LEAGIS: Nils Porsanger.</p>
        <p>SOHPPARIS: Bajit-Sohpparis Nils Andersen.</p>
        <p>E</p>
        <p>oahppat</p>
        <p>Ii</p>
        <p>3</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_ingress_1(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@ingress:Ragnhild Nystad, Aili Keskitalo.
@ingres:Guovdageainnu lagasradio
 @ingress: Eallu
@ingress. duottar
'@ingress:Golbma
@ingress Odne
Samleingress 1
Samleingress: 2
@Samleingress: 3
&lt;pstyle:ingress&gt;Buot
TEKST/INGRESS: 5
@ Ingress: 6</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p>Ragnhild Nystad, Aili Keskitalo.</p>
        <p>Guovdageainnu lagasradio</p>
        <p>Eallu</p>
        <p>duottar</p>
        <p>Golbma</p>
        <p>Odne</p>
        <p>1</p>
        <p>2</p>
        <p>3</p>
        <p>Buot</p>
        <p>5</p>
        <p>6</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_ingress_2(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p><em>@ingress: Gos?</em></p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p><em>Gos?</em></p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_mtitt1(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@m.titt:Juovllat
m.titt:Guolli
@mtitt:Juovllat
M:TITT:Lea go dus meahccebiila?
@m.titt. Maŋemus gártemat
&lt;pstyle:m.titt&gt;Divvot
 @m.titt:Eai</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p type="title">Juovllat</p>
        <p type="title">Guolli</p>
        <p type="title">Juovllat</p>
        <p type="title">Lea go dus meahccebiila?</p>
        <p type="title">Maŋemus gártemat</p>
        <p type="title">Divvot</p>
        <p type="title">Eai</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_mtitt2(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p><em>@m.titt: Maid?</em></p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p type="title"><em>Maid?</em></p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_tekst_1(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                """<document>
    <header/>
    <body>
        <p>@tekst:veadjá šaddat.
tekst:NSR ii áiggo.
TEKST:ÐMii lea suohttaseamos geassebargu dus?
&lt;pstyle:tekst&gt;Sámi</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p>veadjá šaddat.</p>
        <p>NSR ii áiggo.</p>
        <p>ÐMii lea suohttaseamos geassebargu dus?</p>
        <p>Sámi</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_tekst_2(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                """<document>
    <header/>
    <body>
        <p>@tekst:veadjá šaddat.
NSR ii áiggo.</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p>veadjá šaddat. NSR ii áiggo.</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_tekst_3(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                """<document>
    <header/>
    <body>
        <p>@tekst:veadjá šaddat.
@tekst:NSR ii áiggo.</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p>veadjá šaddat.</p>
        <p>NSR ii áiggo.</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_tekst_4(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                """<document>
    <header/>
    <body>
        <p>NSR <em>ii áiggo.</em></p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p>NSR <em>ii áiggo.</em></p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_tekst_5(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                """<document>
    <header/>
    <body>
        <p>  @tekst:ii</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p>ii</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_tekst_6(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                "<document>"
                "   <header/>"
                "   <body>"
                "       <p>Ê@tekst:ii</p>"
                "   </body>"
                "</document>"
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            "<document>"
            "   <header/>"
            "   <body>"
            "       <p>ii</p>"
            "   </body>"
            "</document>"
        )

        self.assertXmlEqual(got, want)

    def test_stikktitt(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@stikktitt:Dološ sámegiel máinnas Várjjagis</p>
        <p>@stikk.titt:Dološ sámegiel máinnas Várjjagis</p>
        <p>@stikktittel:Dološ sámegiel máinnas Várjjagis</p>
        <p> @stikk:Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_utitt1(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@utitt:Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_utitt2(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p> @utitt:Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_udot_titt(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@u.titt:Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_undertitt(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@undertitt:Dološ sámegiel máinnas Várjjagis
undertitt:Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_undertittel(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>Undertittel: Ja</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p type="title">Ja</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_ttitt(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@ttitt:Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_headertitletags_1(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <title/>
    </header>
    <body>
        <p>@tittel:Eanebuidda</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_headertitletags_2(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <title/>
    </header>
    <body>
        <p> @tittel:Eanebuidda</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_headertitletags_3(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <title/>
    </header>
    <body>
        <p>@titt:Eanebuidda</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_headertitletags_4(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <title/>
    </header>
    <body>
        <p> @titt:Eanebuidda</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_headertitletags_5(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <title/>
    </header>
    <body>
        <p>TITT:Eanebuidda</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_headertitletags_6(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <title/>
    </header>
    <body>
        <p>Tittel:Eanebuidda</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_headertitletags_7(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <title/>
    </header>
    <body>
        <p>@LEDtitt:Eanebuidda</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_headertitletags_8(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <title/>
    </header>
    <body>
        <p>&lt;pstyle:tittel&gt;Eanebuidda</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_headertitletags_9(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <title/>
    </header>
    <body>
        <p>HOVEDTITTEL:Eanebuidda</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_headertitletags_10(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <title/>
    </header>
    <body>
        <p>TITTEL:Eanebuidda</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_headertitletags_11(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <title/>
    </header>
    <body>
        <p>@Titt:Guolli
titt:Ruovttusuodjaleaddjit
 @titt:Eanebuidda</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header>
        <title>Guolli</title>
    </header>
    <body>
        <p type="title">Guolli</p>
        <p type="title">Ruovttusuodjaleaddjit</p>
        <p type="title">Eanebuidda</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_headertitletags_12(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <title/>
    </header>
    <body>
        <p>Hovedtitt:Eanebuidda</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_headertitletags_13(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <title/>
    </header>
    <body>
        <p>@hovedtitt:Eanebuidda</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_headertitletags_14(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <title/>
    </header>
    <body>
        <p>@titt 2:Eanebuidda</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_headertitletags_15(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <title/>
    </header>
    <body>
        <p>OVERTITTEL:Eanebuidda</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header>
        <title>Eanebuidda</title>
    </header>
    <body>
        <p type="title">Eanebuidda</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_headertitletags_16(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <title/>
    </header>
    <body>
        <p>@tittel:Gii boahtá Nystø maŋis?
@LEDtitt:Gii boahtá Keskitalo maŋis?
@tittel:Gii boahtá Olli maŋis?
TITT:njeallje suorpma boaris.
&lt;pstyle:tittel&gt;Ii
 @tittel: 1
HOVEDTITTEL: 2
TITTEL: 3</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()

        want = etree.fromstring(
            """<document>
    <header>
        <title>Gii boahtá Nystø maŋis?</title>
    </header>
    <body>
        <p type="title">Gii boahtá Nystø maŋis?</p>
        <p type="title">Gii boahtá Keskitalo maŋis?</p>
        <p type="title">Gii boahtá Olli maŋis?</p>
        <p type="title">njeallje suorpma boaris.</p>
        <p type="title">Ii</p>
        <p type="title">1</p>
        <p type="title">2</p>
        <p type="title">3</p>
    </body>
</document>
"""
        )

        self.assertXmlEqual(got, want)

    def test_ttt(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@ttt:Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_newstags_tit(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@tit:Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p type="title">Dološ sámegiel máinnas Várjjagis</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_newstags_text_before_titletags(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@tekst: text
@m.titt: title</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p>text</p>
        <p type="title">title</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_newstags_text_before_headtitletags(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <title/>
    </header>
    <body>
        <p>@tekst: text
@tittel: title</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header>
        <title>title</title>
    </header>
    <body>
        <p>text</p>
        <p type="title">title</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_newstags_text_before_bylinetags(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header>
        <author>
            <unknown/>
        </author>
    </header>
    <body>
        <p>@tekst: text
@byline: title</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header>
        <author>
            <person firstname="" lastname="title"></person>
        </author>
    </header>
    <body>
        <p>text</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_newstags_text_before_boldtags(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@tekst: text
@bold: title</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p>text</p>
        <p><em type="bold">title</em></p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_newstags_text_before_kursiv(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p>@tekst: text
@kursiv: title</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p>text</p>
        <p><em type="italic">title</em></p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_fix_newstags_4(self):
        """Check that p attributes are kept."""
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p type="title">title</p>
    </body>
</document>"""
            )
        )
        document_fixer.fix_newstags()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p type="title">title</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_fix_body_encoding(self):
        newstext = plaintextconverter.PlaintextConverter("orig/sme/riddu/tullball.txt")
        text = newstext.content2xml(
            io.StringIO(
                """ÐMun lean njeallje jagi boaris.

Nu beaivvdat.

TITT:njeallje suorpma boaris.

TEKST:Olggobealde ç»»u

M:TITT:Lea go dus meahccebiila ?

TEKST:ÐMii lea suohttaseamos geassebargu dus ?

@bold:Suohkana beara»sodagaid juohkin

LOGO: Smi kulturfestivala 1998
"""
            )
        )

        document_fixer = documentfixer.DocumentFixer(text)
        document_fixer.fix_body_encoding("sme")
        got = document_fixer.get_etree()

        want = etree.fromstring(
            """<document>
    <header></header>
        <body>
            <p>–Mun lean njeallje jagi boaris.</p>
            <p>Nu beaivvádat.</p>
            <p>TITT:njeallje suorpma boaris.</p>
            <p>TEKST:Olggobealde Áššu</p>
            <p>M:TITT:Lea go dus meahccebiila ?</p>
            <p>TEKST:–Mii lea suohttaseamos geassebargu dus ?</p>
            <p>@bold:Suohkana bearašásodagaid juohkin</p>
            <p>LOGO: Sámi kulturfestivala 1998</p>
        </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_replace_ligatures(self):
        xml = svgconverter.convert2intermediate(
            os.path.join(
                HERE,
                "converter_data/fakecorpus/orig/sme/riddu/"
                "Riddu_Riddu_avis_TXT.200923.svg",
            )
        )
        document_fixer = documentfixer.DocumentFixer(xml)
        document_fixer.fix_body_encoding("sme")
        got = document_fixer.get_etree()

        want = etree.parse(
            os.path.join(HERE, "converter_data/Riddu_Riddu_avis_TXT.200923.xml")
        )

        self.assertXmlEqual(got, want)

    # def test_word_count(self):
    # document = (
    #'<document xml:lang="sma" id="no_id"><header><title/><genre/>'
    #'<author><unknown/></author><availability><free/>'
    #'</availability><multilingual/></header><body><p>Bïevnesh '
    #'naasjovnalen pryövoej bïjre</p><p>2008</p><p>Bïevnesh '
    #'eejhtegidie, tjidtjieh aehtjieh bielide naasjovnalen '
    #'pryövoej bïjre giej leah maanah 5. jïh 8. '
    #'tsiehkine</p></body></document>')
    # if six.PY3:
    # document = document.encode('utf8')
    # orig_doc = etree.parse(
    # io.BytesIO(document))

    # expected_doc = (
    #'<document xml:lang="sma" id="no_id"><header><title/><genre/>'
    #'<author><unknown/></author><wordcount>20</wordcount>'
    #'<availability><free/></availability><multilingual/></header>'
    #'<body><p>Bïevnesh naasjovnalen pryövoej bïjre</p>'
    #'<p>2008</p><p>Bïevnesh eejhtegidie, tjidtjieh aehtjieh bielide '
    #'naasjovnalen pryövoej bïjre giej leah maanah 5. jïh 8. '
    #'tsiehkine</p></body></document>')

    # document_fixer = documentfixer.DocumentFixer(orig_doc)
    # document_fixer.set_word_count()

    # self.assertXmlEqual(document_fixer.root,
    # etree.fromstring(expected_doc))

    def test_replace_shy1(self):
        document = (
            '<document xml:lang="sma" id="no_id"><header><title/><genre/>'
            "<author><unknown/></author><availability><free/>"
            "</availability><multilingual/></header><body><p>a­b­c"
            "<span>d­e</span>f­g</p></body></document>"
        )
        document = document.encode("utf8")
        orig_doc = etree.parse(io.BytesIO(document))

        expected_doc = (
            '<document xml:lang="sma" id="no_id"><header><title/><genre/>'
            "<author><unknown/></author><availability><free/></availability>"
            "<multilingual/></header><body><p>a<hyph/>b<hyph/>c<span>d<hyph/>"
            "e</span>f<hyph/>g</p></body></document>"
        )

        document_fixer = documentfixer.DocumentFixer(orig_doc)
        document_fixer.soft_hyphen_to_hyph_tag()

        self.assertXmlEqual(document_fixer.root, etree.fromstring(expected_doc))

    def test_replace_shy2(self):
        document = (
            '<document xml:lang="sma" id="no_id">'
            "<header><title/><genre/><author><unknown/></author>"
            "<availability><free/></availability><multilingual/></header>"
            "<body><p>a­b­c<span>d­e</span></p></body></document>"
        )
        document = document.encode("utf8")
        orig_doc = etree.parse(io.BytesIO(document))

        expected_doc = (
            '<document xml:lang="sma" id="no_id"><header><title/><genre/>'
            "<author><unknown/></author><availability><free/></availability>"
            "<multilingual/></header><body><p>a<hyph/>b<hyph/>c<span>d"
            "<hyph/>e</span></p></body></document>"
        )

        document_fixer = documentfixer.DocumentFixer(orig_doc)
        document_fixer.soft_hyphen_to_hyph_tag()

        self.assertXmlEqual(document_fixer.root, etree.fromstring(expected_doc))

    def test_compact_em1(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p><em>1</em> <em>2</em></p>
    </body>
</document>"""
            )
        )
        document_fixer.compact_ems()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p><em>1 2</em></p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_compact_em2(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p><em>1</em> <em>2</em> 3</p>
    </body>
</document>"""
            )
        )
        document_fixer.compact_ems()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p><em>1 2</em> 3</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_compact_em3(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p><em>1</em> <em>2</em> <span/> <em>3</em> <em>4</em></p>
    </body>
</document>"""
            )
        )
        document_fixer.compact_ems()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p><em>1 2</em> <span/> <em>3 4</em></p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_compact_em4(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p><em>1</em> <em>2</em> 5<span/> <em>3</em> <em>4</em> 6</p>
    </body>
</document>"""
            )
        )
        document_fixer.compact_ems()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p><em>1 2</em> 5<span/> <em>3 4</em> 6</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_compact_em5(self):
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                r"""<document>
    <header/>
    <body>
        <p><em></em> <em>2</em> 5<span/> <em>3</em> <em></em> 6</p>
    </body>
</document>"""
            )
        )
        document_fixer.compact_ems()
        got = document_fixer.get_etree()
        want = etree.fromstring(
            """<document>
    <header/>
    <body>
        <p><em>2</em> 5<span/> <em>3</em> 6</p>
    </body>
</document>"""
        )

        self.assertXmlEqual(got, want)

    def test_fix_sms1(self):
        r"""\u2019 (’) should be replaced by \u02BC (ʼ)"""
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                '<document xml:lang="sms">'
                "  <header/>"
                "  <body>"
                "     <p>"
                "       Mätt’temaaunâstuâjj "
                "     </p>"
                "  </body>"
                "</document>"
            )
        )
        document_fixer.fix_body_encoding("sms")
        got = document_fixer.get_etree()
        want = etree.fromstring(
            '<document xml:lang="sms">'
            "  <header/>"
            "  <body>"
            "     <p>"
            "       Mättʼtemaaunâstuâjj "
            "     </p>"
            "  </body>"
            "</document>"
        )

        self.assertXmlEqual(got, want)

    def test_fix_sms2(self):
        r"""\u0027 (')  should be replaced by \u02BC (ʼ)"""
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                '<document xml:lang="sms">'
                "  <header/>"
                "  <body>"
                "     <p>"
                "       ǩiõll'laž da kulttuursaž vuõiggâdvuõđi"
                "     </p>"
                "  </body>"
                "</document>"
            )
        )
        document_fixer.fix_body_encoding("sms")
        got = document_fixer.get_etree()
        want = etree.fromstring(
            '<document xml:lang="sms">'
            "  <header/>"
            "  <body>"
            "     <p>"
            "       ǩiõllʼlaž da kulttuursaž vuõiggâdvuõđi"
            "     </p>"
            "  </body>"
            "</document>"
        )

        self.assertXmlEqual(got, want)

    def test_fix_sms3(self):
        r"""\u2032 (′)  should be replaced by \u02B9 (ʹ)"""
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                '<document xml:lang="sms">'
                "  <header/>"
                "  <body>"
                "     <p>"
                "       Mon tõzz še njui′ǩǩeem tõ′st dõõzze."
                "     </p>"
                "  </body>"
                "</document>"
            )
        )
        document_fixer.fix_body_encoding("sms")
        got = document_fixer.get_etree()
        want = etree.fromstring(
            '<document xml:lang="sms">'
            "  <header/>"
            "  <body>"
            "     <p>"
            "       Mon tõzz še njuiʹǩǩeem tõʹst dõõzze."
            "     </p>"
            "  </body>"
            "</document>"
        )

        self.assertXmlEqual(got, want)

    def test_fix_sms4(self):
        r"""\u00B4 (´)  should be replaced by \u02B9 (ʹ)"""
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                '<document xml:lang="sms">'
                "  <header/>"
                "  <body>"
                "     <p>"
                "       Materialbaaŋk čuä´jtumuš"
                "     </p>"
                "  </body>"
                "</document>"
            )
        )
        document_fixer.fix_body_encoding("sms")
        got = document_fixer.get_etree()
        want = etree.fromstring(
            '<document xml:lang="sms">'
            "  <header/>"
            "  <body>"
            "     <p>"
            "       Materialbaaŋk čuäʹjtumuš"
            "     </p>"
            "  </body>"
            "</document>"
        )

        self.assertXmlEqual(got, want)

    def test_fix_sms5(self):
        r"""\u0301 ( ́)  should be replaced by \u02B9 (ʹ)"""
        document_fixer = documentfixer.DocumentFixer(
            etree.fromstring(
                '<document xml:lang="sms">'
                "  <header/>"
                "  <body>"
                "     <p>"
                "       Materialbaaŋk čuä́jtumuš"
                "     </p>"
                "  </body>"
                "</document>"
            )
        )
        document_fixer.fix_body_encoding("sms")
        got = document_fixer.get_etree()
        want = etree.fromstring(
            '<document xml:lang="sms">'
            "  <header/>"
            "  <body>"
            "     <p>"
            "       Materialbaaŋk čuäʹjtumuš"
            "     </p>"
            "  </body>"
            "</document>"
        )

        self.assertXmlEqual(got, want)
