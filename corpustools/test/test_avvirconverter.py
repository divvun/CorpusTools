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
"""Test conversion of Ávvir xml files."""

import lxml.etree as etree

from corpustools import avvirconverter
from corpustools.test import xmltester


class TestAvvirConverter(xmltester.XMLTester):
    """Test the functionality of the Avvir class."""

    def setUp(self):
        """Setup a common AvvirConverter instance."""
        self.avvir = etree.fromstring(
            "<article>"
            '    <story id="a" class="Tittel">'
            "        <p>a</p>"
            "    </story>"
            '    <story id="b" class="Undertittel">'
            "        <p>b</p>"
            "    </story>"
            '    <story id="c" class="ingress">'
            "        <p>c</p>"
            "    </story>"
            '    <story id="d" class="body">'
            '        <p class="tekst">d<br/>e<br/></p>'
            "        <p>f</p>"
            "    </story>"
            '    <story id="g" class="body">'
            '        <p class="tekst">h<span>i</span>j</p>'
            "    </story>"
            '    <story id="k" class="body">'
            "        <p>l"
            "            <span>"
            "                m"
            "                <br/>"
            "                n"
            "            </span>"
            "            o"
            "        </p>"
            "    </story>"
            '    <story id="a">'
            "        <p>a<p>b</p></p>"
            "    </story>"
            "</article>"
        )

    def test_remove_identical_ids(self):
        """Check that only the first of stories with identical ids are kept."""
        want = etree.fromstring(
            "<article>"
            '    <story id="a" class="Tittel">'
            "        <p>a</p>"
            "    </story>"
            '    <story id="b" class="Undertittel">'
            "        <p>b</p>"
            "    </story>"
            '    <story id="c" class="ingress">'
            "        <p>c</p>"
            "    </story>"
            '    <story id="d" class="body">'
            '        <p class="tekst">d<br/>e<br/></p>'
            "        <p>f</p>"
            "    </story>"
            '    <story id="g" class="body">'
            '        <p class="tekst">h<span>i</span>j</p>'
            "    </story>"
            '    <story id="k" class="body">'
            "        <p>l"
            "            <span>"
            "                m"
            "                <br/>"
            "                n"
            "            </span>"
            "            o"
            "        </p>"
            "    </story>"
            "</article>"
        )

        avvirconverter.remove_identical_ids(self.avvir)
        self.assertXmlEqual(self.avvir, want)

    def test_convert_p_1(self):
        """Check when p does not contain p."""
        want = etree.fromstring(
            "<article>"
            '    <story class="Tittel" id="a">'
            "        <p>a</p>"
            "    </story>"
            '    <story class="Undertittel" id="b">'
            "        <p>b</p>"
            "    </story>"
            '    <story class="ingress" id="c">'
            "        <p>c</p>"
            "    </story>"
            '    <story class="body" id="d">'
            "        <p>d</p>"
            "        <p>e</p>"
            "        <p>f</p>"
            "    </story>"
            '    <story class="body" id="g">'
            "        <p>h</p>"
            "        <p>i</p>"
            "        <p>j</p>"
            "    </story>"
            '    <story class="body" id="k">'
            "        <p>l</p>"
            "        <p>m</p>"
            "        <p>n</p>"
            "        <p>o</p>"
            "    </story>"
            "</article>"
        )

        avvirconverter.remove_identical_ids(self.avvir)
        avvirconverter.convert_p(self.avvir)

        self.assertXmlEqual(self.avvir, want)

    def test_convert_p_2(self):
        """Check when p contains only p."""
        avvir = etree.fromstring(
            "<article>"
            '   <story class="body">'
            "       <p>corrected text <p>text with typo</p>with tail</p>"
            "   </story>"
            "</article>"
        )

        want = etree.fromstring(
            "<article>"
            '   <story class="body">'
            "       <p>corrected text with tail</p>"
            "   </story>"
            "</article>"
        )

        avvirconverter.convert_p(avvir)

        self.assertXmlEqual(avvir, want)

    def test_convert_p_3(self):
        """Check when p contains span and p."""
        avvir = etree.fromstring(
            "<article>"
            '   <story class="body">'
            "       <p>"
            "           <span>bla bla</span>"
            "           corrected text <p>text with typo</p>with tail"
            "       </p>"
            "   </story>"
            "</article>"
        )

        want = etree.fromstring(
            "<article>"
            '   <story class="body">'
            "       <p>bla bla</p>"
            "       <p>corrected text with tail</p>"
            "   </story>"
            "</article>"
        )

        avvirconverter.convert_p(avvir)

        self.assertXmlEqual(avvir, want)

    def test_convert_p_4(self):
        """p.text is None."""
        avvir = etree.fromstring(
            "<article>"
            '   <story class="body">'
            "       <p><p> </p>with tail"
            "       </p>"
            "   </story>"
            "</article>"
        )

        want = etree.fromstring(
            "<article>"
            '   <story class="body">'
            "       <p> with tail</p>"
            "   </story>"
            "</article>"
        )

        avvirconverter.convert_p(avvir)

        self.assertXmlEqual(avvir, want)

    def test_convert_p_5(self):
        """sub_p.tail is None."""
        avvir = etree.fromstring(
            "<article>"
            '   <story class="body">'
            '       <p>láigovistti <p class="NormalParagraphStyle">85</p>'
            "       </p>"
            "   </story>"
            "</article>"
        )

        want = etree.fromstring(
            "<article>"
            '   <story class="body">'
            "       <p>láigovistti </p>"
            "   </story>"
            "</article>"
        )

        avvirconverter.convert_p(avvir)

        self.assertXmlEqual(avvir, want)

    def test_convert_p_6(self):
        """previous.text not None, sub_p.tail is None."""
        avvir = etree.fromstring(
            "<article>"
            '   <story class="body">'
            '       <p class="Privat ann tittel">Stohpu<br/>vuovdemassi'
            '<p class="NormalParagraphStyle">85</p><br/></p>'
            "   </story>"
            "</article>"
        )

        want = etree.fromstring(
            "<article>"
            '   <story class="body">'
            "       <p>Stohpu</p>"
            "       <p>vuovdemassi</p>"
            "   </story>"
            "</article>"
        )

        avvirconverter.convert_p(avvir)

        self.assertXmlEqual(avvir, want)

    def test_convert_p_7(self):
        """previous.tail is None, sub_p.tail not None."""
        avvir = etree.fromstring(
            "<article>"
            '   <story class="body">'
            '       <p class="Privat ann tittel">'
            '<br/><p class="NormalParagraphStyle">157</p>Ozan visttáža <br/>'
            "       </p>"
            "   </story>"
            "</article>"
        )

        want = etree.fromstring(
            "<article>"
            '   <story class="body">'
            "       <p>Ozan visttáža</p>"
            "   </story>"
            "</article>"
        )

        avvirconverter.convert_p(avvir)

        self.assertXmlEqual(avvir, want)

    def test_convert_story(self):
        """Test convert_story."""
        want = etree.fromstring(
            "<article>"
            "    <section>"
            '        <p type="title">a</p>'
            "    </section>"
            "    <section>"
            '        <p type="title">b</p>'
            "    </section>"
            "    <p>c</p>"
            "    <p>d</p>"
            "    <p>e</p>"
            "    <p>f</p>"
            "    <p>h</p>"
            "    <p>i</p>"
            "    <p>j</p>"
            "    <p>l</p>"
            "    <p>m</p>"
            "    <p>n</p>"
            "    <p>o</p>"
            "</article>"
        )

        avvirconverter.remove_identical_ids(self.avvir)
        avvirconverter.convert_p(self.avvir)
        avvirconverter.convert_story(self.avvir)

        self.assertXmlEqual(self.avvir, want)

    def test_convert_article(self):
        """Test convert_article."""
        want = etree.fromstring(
            "<document>"
            "    <body>"
            "        <section>"
            '            <p type="title">a</p>'
            "        </section>"
            "        <section>"
            '            <p type="title">b</p>'
            "        </section>"
            "        <p>c</p>"
            "        <p>d</p>"
            "        <p>e</p>"
            "        <p>f</p>"
            "        <p>h</p>"
            "        <p>i</p>"
            "        <p>j</p>"
            "        <p>l</p>"
            "        <p>m</p>"
            "        <p>n</p>"
            "        <p>o</p>"
            "    </body>"
            "</document>"
        )

        avvirconverter.remove_identical_ids(self.avvir)
        avvirconverter.convert_p(self.avvir)
        avvirconverter.convert_story(self.avvir)

        self.assertXmlEqual(avvirconverter.convert_article(self.avvir), want)
