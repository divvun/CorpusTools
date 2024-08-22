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
#   Copyright © 2013-2023 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

import io
import unittest

from lxml import etree

from corpustools import ccat


class TestCcatHyph(unittest.TestCase):
    """Test how ccat handles hyph"""

    def test_hyph1(self):
        """Test the default treatment of hyph tags"""
        xml_printer = ccat.XMLPrinter()
        buffer = io.StringIO()
        xml_printer.etree = etree.parse(
            io.BytesIO(
                b'<document id="no_id" xml:lang="nob">'
                b"<body><p>mellom<hyph/>krigs<hyph/>tiden</p></body>"
                b"</document>"
            )
        )

        buffer = xml_printer.process_file()
        self.assertEqual(buffer.getvalue(), "mellomkrigstiden ¶\n")

    def test_hyph2(self):
        '''Test hyph tags when hyph_replacement is set to "xml"'''
        xml_printer = ccat.XMLPrinter(hyph_replacement="xml")
        buffer = io.StringIO()
        xml_printer.etree = etree.parse(
            io.BytesIO(
                b'<document id="no_id" xml:lang="nob">'
                b"<body><p>mellom<hyph/>krigs<hyph/>tiden</p></body>"
                b"</document>"
            )
        )

        buffer = xml_printer.process_file()
        self.assertEqual(buffer.getvalue(), "mellom<hyph/>krigs<hyph/>tiden ¶\n")

    def test_hyph3(self):
        '''Test hyph tags when hyph_replacement is set to "-"'''
        xml_printer = ccat.XMLPrinter(hyph_replacement="-")
        buffer = io.StringIO()
        xml_printer.etree = etree.parse(
            io.BytesIO(
                b'<document id="no_id" xml:lang="nob">'
                b"<body><p>mellom<hyph/>krigs<hyph/>tiden</p></body>"
                b"</document>"
            )
        )

        buffer = xml_printer.process_file()
        self.assertEqual(buffer.getvalue(), "mellom-krigs-tiden ¶\n")

    def test_hyph4(self):
        """Test the treatment of two hyph tags in a row"""
        xml_printer = ccat.XMLPrinter(hyph_replacement="-")
        buffer = io.StringIO()

        xml_printer.etree = etree.parse(
            io.BytesIO(
                b'<document id="no_id" xml:lang="nob">'
                b"<body><p>mellom<hyph/><hyph/>tiden</p></body>"
                b"</document>"
            )
        )

        buffer = xml_printer.process_file()
        self.assertEqual(buffer.getvalue(), "mellom-tiden ¶\n")


class TestCcatErrormarkup(unittest.TestCase):
    """Test how ccat handles errormarkup"""

    def test_single_error_inline(self):
        """Plain error element, default text flow"""
        xml_printer = ccat.XMLPrinter()
        input_error = etree.fromstring(
            "<errorortreal>"
            "fiske leting"
            '<correct errtype="nosplit" pos="noun">fiskeleting</correct>'
            "</errorortreal>"
        )

        textlist = []
        parentlang = "sme"
        xml_printer.collect_inline_errors(input_error, textlist, parentlang)
        got = "".join(textlist)

        self.assertEqual(got, "fiskeleting")

    def test_multi_error_inline(self):
        """Nested error element, default text flow"""
        xml_printer = ccat.XMLPrinter()

        input_error = etree.fromstring(
            "<errormorphsyn>"
            "skoledagene er så "
            "<errorort>"
            "vanskerlig"
            '<correct errtype="nosilent" pos="adj">vanskelig</correct>'
            "</errorort>"
            '<correct cat="x" const="spred" errtype="agr" orig="x" pos="adj">'
            "skoledagene er så vanskelige"
            "</correct>"
            "</errormorphsyn>"
        )
        textlist = []
        parentlang = "nob"
        xml_printer.collect_inline_errors(input_error, textlist, parentlang)
        got = "".join(textlist)

        self.assertEqual(got, "skoledagene er så vanskelige")

    def test_single_error_not_inline(self):
        """Plain error element, one word per line output"""
        xml_printer = ccat.XMLPrinter(one_word_per_line=True)
        input_error = etree.fromstring(
            "<errorortreal>"
            "fiske leting"
            '<correct errtype="nosplit" pos="noun">fiskeleting</correct>'
            "</errorortreal>"
        )

        textlist = []
        xml_printer.collect_not_inline_errors(input_error, textlist)
        got = "".join(textlist)

        self.assertEqual(
            got,
            ("fiske leting\tfiskeleting\t#errtype=nosplit,pos=noun"),
        )

    def test_single_error_not_inline_with_filename(self):
        """Plain error element, one word per line output, with filename"""
        xml_printer = ccat.XMLPrinter(print_filename=True, one_word_per_line=True)
        input_error = etree.fromstring(
            "<errorortreal>"
            "fiske leting"
            '<correct errtype="nosplit" pos="noun">fiskeleting</correct>'
            "</errorortreal>"
        )

        xml_printer.filename = "p.xml"

        textlist = []
        xml_printer.collect_not_inline_errors(input_error, textlist)
        got = "".join(textlist)

        self.assertEqual(
            got,
            ("fiske leting\tfiskeleting" "\t#errtype=nosplit,pos=noun, file: p.xml"),
        )

    def test_single_error_not_inline_with_filename_without_attributes(self):
        xml_printer = ccat.XMLPrinter(print_filename=True, one_word_per_line=True)
        input_error = etree.fromstring(
            "<errorortreal>"
            "fiske leting"
            "<correct>fiskeleting</correct>"
            "</errorortreal>"
        )

        xml_printer.filename = "p.xml"

        textlist = []
        xml_printer.collect_not_inline_errors(input_error, textlist)
        got = "".join(textlist)

        self.assertEqual(got, "fiske leting\tfiskeleting\t#file: p.xml")

    def test_multi_errormorphsyn_not_inline_with_filename(self):
        """Nested error element, one word per line output, with filename"""
        input_error = etree.fromstring(
            "<errormorphsyn>"
            "skoledagene er så "
            "<errorort>"
            "vanskerlig"
            '<correct errtype="nosilent" pos="adj">vanskelig</correct>'
            "</errorort>"
            '<correct cat="x" const="spred" errtype="agr" orig="x" pos="adj">'
            "skoledagene er så vanskelige"
            "</correct>"
            "</errormorphsyn>"
        )

        xml_printer = ccat.XMLPrinter(one_word_per_line=True, print_filename=True)
        xml_printer.filename = "p.xml"

        textlist = []
        xml_printer.collect_not_inline_errors(input_error, textlist)
        got = "\n".join(textlist)

        self.assertEqual(
            got,
            (
                "skoledagene er så vanskelig\tskoledagene er så vanskelige"
                "\t#cat=x,const=spred,errtype=agr,orig=x,pos=adj, file: p.xml\n"
                "vanskerlig\tvanskelig\t#errtype=nosilent,pos=adj, file: p.xml"
            ),
        )

    def test_multi_errorlex_not_inline(self):
        """Nested error element, one word per line output"""
        input_error = etree.fromstring(
            "<errorlex>"
            "<errorort>"
            "makkar"
            '<correct errtype="á" pos="interr">'
            "makkár"
            "</correct>"
            "</errorort>"
            " soga"
            "<correct>man soga</correct>"
            "</errorlex>"
        )

        xml_printer = ccat.XMLPrinter(typos=True)
        textlist = []
        xml_printer.collect_not_inline_errors(input_error, textlist)
        got = "\n".join(textlist)

        self.assertEqual(
            got,
            ("makkár soga\tman soga\nmakkar\tmakkár\t#errtype=á,pos=interr"),
        )

    def test_multiple_corrections(self):
        """One word per line, multiple corrections."""
        input_error = etree.fromstring(
            "<p>"
            "<errormorphsyn>"
            "leimme"
            "<correct>"
            "leimmet"
            "</correct>"
            "<correct>"
            "leat"
            "</correct>"
            "</errormorphsyn>"
            "</p>",
        )

        xml_printer = ccat.XMLPrinter(typos=True)
        textlist = []
        xml_printer.collect_not_inline_errors(input_error, textlist)
        got = "\n".join(textlist)

        self.assertEqual(
            got,
            ("leimme\tleimmet\nleimme\tleat"),
        )


class TestCcat(unittest.TestCase):
    def test_p(self):
        """Test the output of a plain p with default text flow"""
        xml_printer = ccat.XMLPrinter()
        buffer = io.StringIO()
        input_p = etree.fromstring(
            "<p>Et stykke av Norge som er lite kjent - "
            "Litt om Norge i mellomkrigstiden</p>"
        )

        xml_printer.collect_text(input_p, "nob", buffer)
        self.assertEqual(
            buffer.getvalue(),
            (
                "Et stykke av Norge som er lite kjent - "
                "Litt om Norge i mellomkrigstiden ¶\n"
            ),
        )

    def test_p_with_span(self):
        """The output of a plain p with a span element"""
        xml_printer = ccat.XMLPrinter()
        buffer = io.StringIO()

        input_p = etree.fromstring(
            "<p>I 1864 ga han ut boka "
            '<span type="quote" xml:lang="dan">'
            '"Fornuftigt Madstel"'
            "</span>."
            "</p>"
        )

        xml_printer.collect_text(input_p, "nob", buffer)
        self.assertEqual(
            buffer.getvalue(), 'I 1864 ga han ut boka "Fornuftigt Madstel". ¶\n'
        )

    def test_p_with_error(self):
        """The output of a p containing a nested error element"""
        xml_printer = ccat.XMLPrinter()
        buffer = io.StringIO()

        input_p = etree.fromstring(
            "<p>"
            "<errormorphsyn>"
            '<errorort correct="Bearpmehat" errtype="svow" pos="noun">'
            "Bearpmahat"
            "</errorort>"
            "<errorlex>"
            " earuha"
            '<correct errtype="w" origpos="v" pos="verb">sirre</correct>'
            "</errorlex>"
            '<correct cat="pl3prs" const="fin"  errtype="agr" orig="sg3prs" '
            'pos="verb">Bearpmehat sirrejit</correct>'
            "</errormorphsyn>"
            " uskki ja loaiddu."
            "</p>"
        )

        xml_printer.collect_text(input_p, "sme", buffer)
        self.assertEqual(buffer.getvalue(), "Bearpmahat earuha uskki ja loaiddu. ¶\n")

    def test_p_one_word_per_line(self):
        """Test the output of a plain p element, one word per line"""
        input_p = etree.fromstring(
            "<p>Et stykke av Norge som er lite kjent - "
            "Litt om Norge i mellomkrigstiden</p>"
        )

        xml_printer = ccat.XMLPrinter(one_word_per_line=True)

        buffer = io.StringIO()

        xml_printer.collect_text(input_p, "nob", buffer)
        self.assertEqual(
            buffer.getvalue(),
            (
                "Et\n"
                "stykke\n"
                "av\n"
                "Norge\n"
                "som\n"
                "er\n"
                "lite\n"
                "kjent\n"
                "-\n"
                "Litt\n"
                "om\n"
                "Norge\n"
                "i\n"
                "mellomkrigstiden\n"
            ),
        )

    def test_p_with_span_one_word_per_line(self):
        """Output a plain p that contains a span element

        one_word_per-line is True
        """
        input_p = etree.fromstring(
            "<p>I 1864 ga han ut boka "
            '    <span type="quote" xml:lang="dan">'
            '        "Fornuftigt Madstel"'
            "    </span>."
            "</p>"
        )

        xml_printer = ccat.XMLPrinter(one_word_per_line=True)
        buffer = io.StringIO()

        xml_printer.collect_text(input_p, "nob", buffer)
        self.assertEqual(
            buffer.getvalue(),
            (
                "I\n"
                "1864\n"
                "ga\n"
                "han\n"
                "ut\n"
                "boka\n"
                '"Fornuftigt\n'
                'Madstel"\n'
                ".\n"
            ),
        )

    def test_p_with_error_one_word_per_line(self):
        input_p = etree.fromstring(
            "<p>livččii "
            "<errorort>"
            "makkarge"
            '<correct errtype="á" pos="adv">makkárge</correct>'
            "</errorort>"
            " politihkka, muhto rahpasit baicca muitalivčče "
            "<errorlex>"
            "<errorort>"
            "makkar"
            '<correct errtype="á" pos="interr">makkár</correct>'
            "</errorort>"
            " soga"
            "<correct>man soga</correct>"
            "</errorlex>"
            " sii"
            "</p>"
        )

        xml_printer = ccat.XMLPrinter(one_word_per_line=True)

        buffer = io.StringIO()
        xml_printer.collect_text(input_p, "sme", buffer)
        self.assertEqual(
            buffer.getvalue(),
            (
                "livččii\n"
                "makkarge\tmakkárge\t#errtype=á,pos=adv\n"
                "politihkka,\nmuhto\nrahpasit\nbaicca\nmuitalivčče\n"
                "makkár soga\tman soga\n"
                "makkar\tmakkár\t#errtype=á,pos=interr\nsoga\nsii\n"
            ),
        )

    def test_p_with_error_correction(self):
        """correction = True, print all corrections"""
        input_p = etree.fromstring(
            "<p>livččii "
            "<errorort>"
            "makkarge"
            '<correct errtype="á" pos="adv">makkárge</correct>'
            "</errorort>"
            " politihkka, muhto rahpasit baicca muitalivčče "
            "<errorlex>"
            "<errorort>"
            "makkar"
            '<correct errtype="á" pos="interr">makkár</correct>'
            "</errorort>"
            " soga"
            "<correct>man soga</correct>"
            "</errorlex>"
            " sii"
            "</p>"
        )

        xml_printer = ccat.XMLPrinter(correction=True)

        buffer = io.StringIO()
        xml_printer.collect_text(input_p, "sme", buffer)
        self.assertEqual(
            buffer.getvalue(),
            (
                "livččii makkárge politihkka, muhto rahpasit baicca muitalivčče "
                "man soga sii ¶\n"
            ),
        )

    def test_p_with_error_filtering_errorlex(self):
        """errorlex = True, print errorlex corrections"""
        input_p = etree.fromstring(
            "<p>livččii "
            "<errorort>"
            "makkarge"
            '<correct errtype="á" pos="adv">makkárge</correct>'
            "</errorort>"
            " politihkka, muhto rahpasit baicca muitalivčče "
            "<errorlex>"
            "<errorort>"
            "makkar"
            '<correct errtype="á" pos="interr">makkár</correct>'
            "</errorort>"
            " soga"
            "<correct>man soga</correct>"
            "</errorlex>"
            " sii"
            "</p>"
        )

        xml_printer = ccat.XMLPrinter(errorlex=True)

        buffer = io.StringIO()
        xml_printer.collect_text(input_p, "sme", buffer)
        self.assertEqual(
            buffer.getvalue(),
            (
                "livččii makkarge politihkka, muhto rahpasit baicca muitalivčče "
                "man soga sii ¶\n"
            ),
        )

    def test_p_with_error_filtering_errormorphsyn(self):
        """errormorphsyn = True, print errormorphsyn corrections"""
        input_p = etree.fromstring(
            "<p>livččii "
            "<errorort>"
            "makkarge"
            '<correct errtype="á" pos="adv">makkárge</correct>'
            "</errorort>"
            " politihkka, muhto rahpasit baicca muitalivčče "
            "<errorlex>"
            "<errorort>"
            "makkar"
            '<correct errtype="á" pos="interr">makkár</correct>'
            "</errorort>"
            " soga"
            "<correct>man soga</correct>"
            "</errorlex>"
            " sii"
            "</p>"
        )

        xml_printer = ccat.XMLPrinter(errormorphsyn=True)

        buffer = io.StringIO()
        xml_printer.collect_text(input_p, "sme", buffer)
        self.assertEqual(
            buffer.getvalue(),
            (
                "livččii makkarge politihkka, muhto rahpasit baicca muitalivčče "
                "makkar soga sii ¶\n"
            ),
        )

    def test_p_with_error_filtering_errorort(self):
        """errorort = True, print errorort corrections"""
        xml_printer = ccat.XMLPrinter(errorort=True)

        input_p = etree.fromstring(
            "<p>livččii "
            "<errorort>"
            "makkarge"
            '<correct errtype="á" pos="adv">makkárge</correct>'
            "</errorort>"
            " politihkka, muhto rahpasit baicca muitalivčče "
            "<errorlex>"
            "<errorort>"
            "makkar"
            '<correct errtype="á" pos="interr">makkár</correct>'
            "</errorort>"
            " soga"
            "<correct>man soga</correct>"
            "</errorlex>"
            " sii"
            "</p>"
        )

        buffer = io.StringIO()
        xml_printer.collect_text(input_p, "sme", buffer)
        self.assertEqual(
            buffer.getvalue(),
            (
                "livččii makkárge politihkka, muhto rahpasit baicca muitalivčče "
                "makkár soga sii ¶\n"
            ),
        )

    def test_p_with_error_filtering_errorortreal(self):
        xml_printer = ccat.XMLPrinter(errorortreal=True)

        input_p = etree.fromstring(
            "<p>livččii "
            "<errorort>"
            "makkarge"
            '<correct errtype="á" pos="adv">makkárge</correct>'
            "</errorort>"
            " politihkka, muhto rahpasit baicca muitalivčče "
            "<errorlex>"
            "<errorort>"
            "makkar"
            '<correct errtype="á" pos="interr">makkár</correct>'
            "</errorort>"
            " soga"
            "<correct>man soga</correct>"
            "</errorlex>"
            " sii"
            "</p>"
        )

        buffer = io.StringIO()
        xml_printer.collect_text(input_p, "sme", buffer)
        self.assertEqual(
            buffer.getvalue(),
            (
                "livččii makkarge politihkka, muhto rahpasit baicca muitalivčče "
                "makkar soga sii ¶\n"
            ),
        )

    def test_visit_this_p_default(self):
        """Visit only plain p and <p type=text> elements"""
        xml_printer = ccat.XMLPrinter()

        for types in [' type="title"', ' type="listitem"', ' type="tablecell"']:
            input_xml = etree.fromstring("<p" + types + ">ášŧŋđžčøåæ</p>")
            self.assertFalse(xml_printer.visit_this_node(input_xml))

        for types in ["", ' type="text"']:
            input_xml = etree.fromstring("<p" + types + ">ášŧŋđžčøåæ</p>")
            self.assertTrue(xml_printer.visit_this_node(input_xml))

    def test_visit_this_p_title_set(self):
        """Visit only <p type=title> elements when title is True"""
        xml_printer = ccat.XMLPrinter(title=True)

        for types in ["", ' type="text"', ' type="listitem"', ' type="tablecell"']:
            input_xml = etree.fromstring("<p" + types + ">ášŧŋđžčøåæ</p>")
            self.assertFalse(xml_printer.visit_this_node(input_xml))

        for types in [' type="title"']:
            input_xml = etree.fromstring("<p" + types + ">ášŧŋđžčøåæ</p>")
            self.assertTrue(xml_printer.visit_this_node(input_xml))

    def test_visit_this_p_listitem_set(self):
        """Visit only <p type=listitem> elements when listitem is True"""
        xml_printer = ccat.XMLPrinter(listitem=True)

        for types in ["", ' type="text"', ' type="title"', ' type="tablecell"']:
            input_xml = etree.fromstring("<p" + types + ">ášŧŋđžčøåæ</p>")
            self.assertFalse(xml_printer.visit_this_node(input_xml))

        for types in [' type="listitem"']:
            input_xml = etree.fromstring("<p" + types + ">ášŧŋđžčøåæ</p>")
            self.assertTrue(xml_printer.visit_this_node(input_xml))

    def test_visit_this_p_tablecell_set(self):
        """Visit only <p type=tablecell> elements when table is True"""
        xml_printer = ccat.XMLPrinter(table=True)

        for types in ["", ' type="text"', ' type="title"', ' type="listitem"']:
            input_xml = etree.fromstring("<p" + types + ">ášŧŋđžčøåæ</p>")
            self.assertFalse(xml_printer.visit_this_node(input_xml))

        for types in [' type="tablecell"']:
            input_xml = etree.fromstring("<p" + types + ">ášŧŋđžčøåæ</p>")
            self.assertTrue(xml_printer.visit_this_node(input_xml))

    def test_visit_this_p_allp_set(self):
        """Visit all p elements when all_paragraphs is True"""
        xml_printer = ccat.XMLPrinter(all_paragraphs=True)

        for types in [
            "",
            ' type="text"',
            ' type="title"',
            ' type="listitem"',
            ' type="tablecell"',
        ]:
            input_xml = etree.fromstring("<p" + types + ">ášŧŋđžčøåæ</p>")
            self.assertTrue(xml_printer.visit_this_node(input_xml))

    def test_process_file_default(self):
        """Default settings, print content of p elements

        Check the output of plain p elements, with default settings
        Specifically, check that only plain p gets output, whereas
        p elements with the type title, listitem and tablecell get no output.
        """
        xml_printer = ccat.XMLPrinter()

        for types in [' type="title"', ' type="listitem"', ' type="tablecell"']:
            document = (
                """<document id="no_id" xml:lang="sme"><body><p"""
                + types
                + """>ášŧŋđžčøåæ</p></body></document>"""
            )

            xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))
            buffer = xml_printer.process_file()
            self.assertEqual(buffer.getvalue(), "")

        for types in ["", ' type="text"']:
            document = (
                """<document id="no_id" xml:lang="sme"><body><p"""
                + types
                + """>ášŧŋđžčøåæ</p></body></document>"""
            )

            xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))
            buffer = xml_printer.process_file()
            self.assertEqual(buffer.getvalue(), "ášŧŋđžčøåæ ¶\n")

    def test_process_file_title_set(self):
        """Print only content of p elements with type=title."""
        xml_printer = ccat.XMLPrinter(title=True)

        for types in ["", ' type="text"', ' type="listitem"', ' type="tablecell"']:
            document = (
                '<document id="no_id" xml:lang="sme"><body><p {}>'
                "ášŧŋđžčøåæ</p></body></document>".format(types)
            )
            xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))
            buffer = xml_printer.process_file()
            self.assertEqual(buffer.getvalue(), "")

        for types in [' type="title"']:
            document = (
                '<document id="no_id" xml:lang="sme"><body><p {}>'
                "ášŧŋđžčøåæ</p></body></document>".format(types)
            )
            xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))
            buffer = xml_printer.process_file()
            self.assertEqual(buffer.getvalue(), "ášŧŋđžčøåæ ¶\n")

    def test_process_file_listitem_set(self):
        """Print only content of p elements with type=listitem."""
        xml_printer = ccat.XMLPrinter(listitem=True)

        for types in ["", ' type="text"', ' type="title"', ' type="tablecell"']:
            document = (
                """<document id="no_id" xml:lang="sme"><body><p"""
                + types
                + """>ášŧŋđžčøåæ</p></body></document>"""
            )
            xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))
            buffer = xml_printer.process_file()
            self.assertEqual(buffer.getvalue(), "")

        for types in [' type="listitem"']:
            document = (
                """<document id="no_id" xml:lang="sme"><body><p"""
                + types
                + """>ášŧŋđžčøåæ</p></body></document>"""
            )
            xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))
            buffer = xml_printer.process_file()
            self.assertEqual(buffer.getvalue(), "ášŧŋđžčøåæ ¶\n")

    def test_process_file_tablecell_set(self):
        """Print only content of p elements with type=title gets output."""
        xml_printer = ccat.XMLPrinter(table=True)

        for types in ["", ' type="text"', ' type="title"', ' type="listitem"']:
            document = (
                '<document id="no_id" xml:lang="sme"><body><p '
                + types
                + ">ášŧŋđžčøåæ</p></body></document>"
            )

            xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))
            buffer = xml_printer.process_file()
            self.assertEqual(buffer.getvalue(), "")

        for types in [' type="tablecell"']:
            document = (
                '<document id="no_id" xml:lang="sme"><body><p '
                + types
                + ">ášŧŋđžčøåæ</p></body></document>"
            )
            xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))
            buffer = xml_printer.process_file()
            self.assertEqual(buffer.getvalue(), "ášŧŋđžčøåæ ¶\n")

    def test_process_file_allp_set(self):
        """all_paragraphs option is True, all p elements get output."""
        xml_printer = ccat.XMLPrinter(all_paragraphs=True)

        for types in [
            "",
            ' type="text"',
            ' type="title"',
            ' type="listitem"',
            ' type="tablecell"',
        ]:
            document = (
                """<document id="no_id" xml:lang="sme"><body><p"""
                + types
                + """>ášŧŋđžčøåæ</p></body></document>"""
            )
            xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))
            buffer = xml_printer.process_file()
            self.assertEqual(buffer.getvalue(), "ášŧŋđžčøåæ ¶\n")

    def test_process_file_one_word_per_line_errorlex(self):
        """Print only errorlex content

        Check the output of a p element containing two error elements,
        a plain errorort one, and a nested errorlex one when
        the one_word_per_line and errorlex options are True.
        """
        document = (
            '<document id="no_id" xml:lang="sme">'
            "<body>"
            "<p>livččii "
            "<errorort>"
            "makkarge"
            '<correct errtype="á" pos="adv">makkárge</correct>'
            "</errorort>"
            " politihkka, muhto rahpasit baicca muitalivčče "
            "<errorlex>"
            "<errorort>"
            "makkar"
            '<correct errtype="á" pos="interr">makkár</correct>'
            "</errorort>"
            " soga"
            "<correct>man soga</correct>"
            "</errorlex>"
            " sii"
            "</p>"
            "</body>"
            "</document>"
        )

        xml_printer = ccat.XMLPrinter(one_word_per_line=True, errorlex=True)
        xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = xml_printer.process_file()
        self.assertEqual(
            buffer.getvalue(),
            (
                "livččii\n"
                "makkarge\n"
                "politihkka,\n"
                "muhto\n"
                "rahpasit\n"
                "baicca\n"
                "muitalivčče\n"
                "makkár soga\tman soga\n"
                "sii\n"
            ),
        )

    def test_process_file_one_word_per_line_errorort(self):
        """Print only errorort content

        Check the output of a p element containing two error elements,
        a plain errorort one, and a nested errorlex one when
        the one_word_per_line and errorort options are True
        """
        document = (
            '<document id="no_id" xml:lang="sme">'
            "<body>"
            "<p>livččii "
            "<errorort>"
            "makkarge"
            '<correct errtype="á" pos="adv">makkárge</correct>'
            "</errorort>"
            " politihkka, muhto rahpasit baicca muitalivčče "
            "<errorlex>"
            "<errorort>"
            "makkar"
            '<correct errtype="á" pos="interr">makkár</correct>'
            "</errorort>"
            " soga"
            "<correct>man soga</correct>"
            "</errorlex>"
            " sii"
            "</p>"
            "</body>"
            "</document>"
        )

        xml_printer = ccat.XMLPrinter(one_word_per_line=True, errorort=True)
        xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = xml_printer.process_file()
        got = buffer.getvalue()
        want = (
            "livččii\n"
            "makkarge\tmakkárge\t#errtype=á,pos=adv\n"
            "politihkka,\n"
            "muhto\n"
            "rahpasit\n"
            "baicca\n"
            "muitalivčče\n"
            "makkar\tmakkár\t#errtype=á,pos=interr\n"
            "soga\n"
            "sii\n"
        )
        self.assertEqual(got, want)

    def test_process_file_typos(self):
        """Print all error content

        Check the output of a p element containing two error elements,
        a plain errorort one, and a nested errorlex one when
        the typos option True
        """
        document = (
            '<document id="no_id" xml:lang="sme">'
            "<body>"
            "<p>livččii "
            "<errorort>"
            "makkarge"
            '<correct errtype="á" pos="adv">makkárge</correct>'
            "</errorort>"
            " politihkka, muhto rahpasit baicca muitalivčče "
            "<errorlex>"
            "<errorort>"
            "makkar"
            '<correct errtype="á" pos="interr">makkár</correct>'
            "</errorort>"
            " soga"
            "<correct>man soga</correct>"
            "</errorlex>"
            " sii"
            "</p>"
            "</body>"
            "</document>"
        )

        xml_printer = ccat.XMLPrinter(typos=True)
        xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = xml_printer.process_file()
        self.assertEqual(
            buffer.getvalue(),
            (
                "makkarge\tmakkárge\t#errtype=á,pos=adv\n"
                "makkár soga\tman soga\n"
                "makkar\tmakkár\t#errtype=á,pos=interr\n"
            ),
        )

    def test_process_file_typos_errorlex(self):
        """Print only errorlex content

        Check the output of a p element containing two error elements,
        a plain errorort one, and a nested errorlex one when
        the typos and errorlex options are True
        """
        document = (
            '<document id="no_id" xml:lang="sme">'
            "<body>"
            "<p>livččii "
            "<errorort>"
            "makkarge"
            '<correct errtype="á" pos="adv">makkárge</correct>'
            "</errorort>"
            " politihkka, muhto rahpasit baicca muitalivčče "
            "<errorlex>"
            "<errorort>"
            "makkar"
            '<correct errtype="á" pos="interr">makkár</correct>'
            "</errorort>"
            " soga"
            "<correct>man soga</correct>"
            "</errorlex>"
            " sii"
            "</p>"
            "</body>"
            "</document>"
        )

        xml_printer = ccat.XMLPrinter(typos=True, errorlex=True)
        xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = xml_printer.process_file()
        self.assertEqual(buffer.getvalue(), "makkár soga\tman soga\n")

    def test_process_file_typos_errorort(self):
        """Print only errorort content

        Check the output of a p element containing two error elements,
        a plain errorort one, and a nested errorlex one when
        the one_word_per_line, typos and errorort options are True
        """
        document = (
            '<document id="no_id" xml:lang="sme">'
            "<body>"
            "<p>livččii "
            "<errorort>"
            "makkarge"
            '<correct errtype="á" pos="adv">makkárge</correct>'
            "</errorort>"
            " politihkka, muhto rahpasit baicca muitalivčče "
            "<errorlex>"
            "<errorort>"
            "makkar"
            '<correct errtype="á" pos="interr">makkár</correct>'
            "</errorort>"
            " soga"
            "<correct>man soga</correct>"
            "</errorlex>"
            " sii"
            "</p>"
            "</body>"
            "</document>"
        )

        xml_printer = ccat.XMLPrinter(typos=True, one_word_per_line=True, errorort=True)
        xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = xml_printer.process_file()
        self.assertEqual(
            buffer.getvalue(),
            (
                "makkarge\tmakkárge\t#errtype=á,pos=adv\n"
                "makkar\tmakkár\t#errtype=á,pos=interr\n"
            ),
        )

    def test_get_lang(self):
        """Check that get_lang finds the main lang of the document"""
        xml_printer = ccat.XMLPrinter()
        xml_printer.etree = etree.parse(
            io.BytesIO(b'<document id="no_id" xml:lang="sme"/>')
        )

        self.assertEqual(xml_printer.get_lang(), "sme")

    def test_get_element_language_same_as_parent(self):
        """xml:lang is not set in the p element. Return parent language."""
        xml_printer = ccat.XMLPrinter()

        element = etree.fromstring("<p/>")
        self.assertEqual(xml_printer.get_element_language(element, "sme"), "sme")

    def test_get_element_language_different_from_parent(self):
        """Check that the value of xml:lang is returned when it is set."""
        xml_printer = ccat.XMLPrinter()

        element = etree.fromstring('<p xml:lang="nob"/>')
        self.assertEqual(xml_printer.get_element_language(element, "sme"), "nob")

    def test_process_file_language_nob(self):
        """lang=nob, only nob content should be output"""
        xml_printer = ccat.XMLPrinter(lang="nob")
        xml_printer.etree = etree.parse(
            io.BytesIO(
                b'<document id="no_id" xml:lang="nob">'
                b"<body>"
                b"<p>"
                b"nob1 "
                b'<span type="quote" xml:lang="dan">dan1</span>'
                b" nob2</p>"
                b"</body>"
                b"</document>"
            )
        )

        buffer = xml_printer.process_file()
        self.assertEqual(buffer.getvalue(), "nob1  nob2 ¶\n")

    def test_process_two_paragraphs(self):
        """Check that the ¶ character is printed"""
        xml_printer = ccat.XMLPrinter()
        xml_printer.etree = etree.parse(
            io.BytesIO(
                b'<document id="no_id" xml:lang="nob">'
                b"    <body>"
                b"        <p>nob1</p>"
                b"        <p>nob2</p>"
                b"    </body>"
                b"</document>"
            )
        )

        buffer = xml_printer.process_file()
        self.assertEqual(buffer.getvalue(), "nob1 ¶\nnob2 ¶\n")

    def test_process_minus_l_sme(self):
        """lang=sme, no elements are sme

        Check that nothing is output when the wanted language
        (set in the lang option) is not the same language as any of the
        content of the elements.
        """
        document = (
            '<document id="no_id" xml:lang="nob">'
            "<body>"
            '<p type="text">'
            "men "
            "<errormorphsyn>"
            "skoledagene er så "
            "<errorort>"
            "vanskerlig"
            '<correct errtype="nosilent" pos="adj">vanskelig</correct>'
            "</errorort>"
            '<correct cat="x" const="spred" errtype="agr" orig="x" pos="adj">'
            "koledagene er så vanskelige"
            "</correct>"
            "</errormorphsyn>"
            " å komme igjennom,"
            "</p>"
            "</body>"
            "</document>"
        )

        xml_printer = ccat.XMLPrinter(lang="sme")
        xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = xml_printer.process_file()

        self.assertEqual(buffer.getvalue(), "")

    def test_foreign(self):
        """Check the output of a p containing an errorlang element

        The errorlang option is True.
        """
        xml_printer = ccat.XMLPrinter(errorlang=True)
        document = (
            '<document id="no_id" xml:lang="nob">'
            "<body>"
            "<p>"
            "Vijmak bierjjedak! "
            "<errorlang>"
            "Pjuh"
            "<correct>nor</correct>"
            "</errorlang>"
            " vijmak de bierjjedak "
            "<errorort>"
            "sjattáj"
            '<correct errorinfo="vowlat,á-a">sjattaj</correct>'
            "</errorort>"
            "."
            "</p>"
            "</body>"
            "</document>"
        )

        xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = xml_printer.process_file()

        self.assertEqual(
            buffer.getvalue(),
            ("Vijmak bierjjedak! nor vijmak de bierjjedak sjattáj. ¶\n"),
        )

    def test_no_foreign(self):
        """noforeign option is True

        Neither the errorlang.text nor the correct attribute should be output.
        Check that this really happens.
        """
        xml_printer = ccat.XMLPrinter(noforeign=True)
        document = (
            '<document id="no_id" xml:lang="nob">'
            "<body>"
            "<p>"
            "Vijmak bierjjedak! "
            "<errorlang>"
            "Pjuh"
            "<correct>nor</correct>"
            "</errorlang>"
            " vijmak de bierjjedak "
            "<errorort>"
            "sjattáj"
            '<correct errorinfo="vowlat,á-a">sjattaj</correct>'
            "</errorort>"
            "."
            "</p>"
            "</body>"
            "</document>"
        )

        xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = xml_printer.process_file()

        self.assertEqual(
            buffer.getvalue(), ("Vijmak bierjjedak!  vijmak de bierjjedak sjattáj. ¶\n")
        )

    def test_no_foreign_typos(self):
        """noforeign is True, typos is True

        When the noforeign option is True, neither the errorlang.text
        nor the correct attribute should be output. Check that this really
        happens even when the typos option is set.
        """
        xml_printer = ccat.XMLPrinter(typos=True, noforeign=True)
        document = (
            '<document id="no_id" xml:lang="nob">'
            "<body>"
            "<p>"
            "Vijmak bierjjedak! "
            "<errorlang>"
            "Pjuh"
            "<correct>nor</correct>"
            "</errorlang>"
            " vijmak de bierjjedak "
            "<errorort>"
            "sjattáj"
            '<correct errorinfo="vowlat,á-a">sjattaj</correct>'
            "</errorort>"
            "."
            "</p>"
            "</body>"
            "</document>"
        )

        xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = xml_printer.process_file()

        self.assertEqual(buffer.getvalue(), "sjattáj\tsjattaj\t#errorinfo=vowlat,á-a\n")

    def test_typos_errordepth3(self):
        """Check the output of a p containing a nested error element

        typos option is True, depth is 3
        """
        document = (
            '<document id="no_id" xml:lang="nob">'
            "<body>"
            "<p>"
            "<errormorphsyn>"
            "<errormorphsyn>"
            "<errorort>"
            "čoaggen"
            '<correct errtype="mono" pos="verb">čoggen</correct>'
            "</errorort>"
            " ollu jokŋat"
            '<correct cat="genpl" const="obj" errtype="case" orig="nompl" pos="noun">'
            "čoggen ollu joŋaid"
            "</correct>"
            "</errormorphsyn>"
            " ja sarridat"
            '<correct cat="genpl" const="obj" errtype="case" orig="nompl" pos="noun">'
            "čoggen ollu joŋaid ja sarridiid"
            "</correct>"
            "</errormorphsyn>"
            "</p>"
            "</body>"
            "</document>"
        )
        xml_printer = ccat.XMLPrinter(typos=True)
        xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))

        buffer = xml_printer.process_file()
        got = buffer.getvalue()
        want = (
            "čoggen ollu joŋaid ja sarridat"
            "\tčoggen ollu joŋaid ja sarridiid"
            "\t#cat=genpl,const=obj,errtype=case,orig=nompl,pos=noun\n"
            "čoggen ollu jokŋat\tčoggen ollu joŋaid"
            "\t#cat=genpl,const=obj,errtype=case,orig=nompl,pos=noun\n"
            "čoaggen\tčoggen\t#errtype=mono,pos=verb\n"
        )

        self.maxDiff = None
        self.assertEqual(got, want)

    def test_typos_errormorphsyn_twice(self):
        """Check the output of a plain p

        The p contains a doubly nested
        errormorphsyn element when the typos and errormorphsyn
        options are True
        """
        document = (
            '<document id="no_id" xml:lang="nob">'
            "<body>"
            "<p>"
            "<errormorphsyn>"
            "leat "
            "<errormorphsyn>"
            "okta máná"
            '<correct cat="nomsg" const="spred" errtype="case" orig="gensg" pos="n">'
            "okta mánná"
            "</correct>"
            "</errormorphsyn>"
            '<correct cat="sg3prs" const="v" errtype="agr" orig="pl3prs" pos="v">'
            "lea okta mánná"
            "</correct>"
            "</errormorphsyn>"
            "</p>"
            "</body>"
            "</document>"
        )

        xml_printer = ccat.XMLPrinter(typos=True, errormorphsyn=True)
        xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))

        buffer = xml_printer.process_file()

        self.assertEqual(
            buffer.getvalue(),
            (
                "leat okta mánná\tlea okta mánná"
                "\t#cat=sg3prs,const=v,errtype=agr,orig=pl3prs,pos=v\n"
                "okta máná\tokta mánná"
                "\t#cat=nomsg,const=spred,errtype=case,orig=gensg,pos=n\n"
            ),
        )

    def test_process_file1(self):
        """Test process_file with a disambiguation element as input"""
        xml_printer = ccat.XMLPrinter(disambiguation=True)
        document = (
            '<document id="no_id" xml:lang="nob">\n'
            "    <body>\n"
            '        <disambiguation>"&lt;Muhto&gt;"\n'
            '\t"muhto" CC &lt;sme&gt; @CVP\n"&lt;gaskkohagaid&gt;"\n'
            '\t"gaskkohagaid" Adv &lt;sme&gt;\n"&lt;,&gt;"\n'
            '\t"," CLB\n"&lt;ja&gt;"\n'
            '\t"ja" CC &lt;sme&gt; @CNP\n"&lt;erenoamážit&gt;"\n'
            '\t"erenoamážit" Adv &lt;sme&gt;\n"&lt;dalle_go&gt;"\n'
            '\t"dalle_go" MWE CS &lt;sme&gt; @CVP\n"&lt;lei&gt;"\n'
            '\t"leat" V &lt;sme&gt; IV Ind Prt Sg3 @+FMAINV\n'
            '"&lt;buolaš&gt;"\n'
            '\t"buolaš" Sem/Wthr N &lt;sme&gt; Sg Nom\n"&lt;,&gt;"\n'
            '\t"," CLB\n"&lt;de&gt;"\n'
            '\t"de" Adv &lt;sme&gt;\n"&lt;aggregáhta&gt;"\n'
            '\t"aggregáhta" N &lt;sme&gt; Sg Nom\n"&lt;billánii&gt;"\n'
            '\t"billánit" V &lt;sme&gt; IV Ind Prt Sg3 @+FMAINV\n'
            '"&lt;.&gt;"\n\t"." CLB\n\n"&lt;¶&gt;"\n'
            '\t"¶" CLB\n\n</disambiguation></body></document>'
        )

        xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = xml_printer.process_file()

        self.assertEqual(
            buffer.getvalue(),
            (
                '"<Muhto>"\n\t"muhto" CC <sme> @CVP\n"<gaskkohagaid>"\n'
                '\t"gaskkohagaid" Adv <sme>\n"<,>"\n'
                '\t"," CLB\n"<ja>"\n\t"ja" CC <sme> @CNP\n"<erenoamážit>"\n'
                '\t"erenoamážit" Adv <sme>\n"<dalle_go>"\n'
                '\t"dalle_go" MWE CS <sme> @CVP\n"<lei>"\n'
                '\t"leat" V <sme> IV Ind Prt Sg3 @+FMAINV\n"<buolaš>"\n'
                '\t"buolaš" Sem/Wthr N <sme> Sg Nom\n"<,>"\n'
                '\t"," CLB\n"<de>"\n\t"de" Adv <sme>\n"<aggregáhta>"\n'
                '\t"aggregáhta" N <sme> Sg Nom\n"<billánii>"\n'
                '\t"billánit" V <sme> IV Ind Prt Sg3 @+FMAINV\n"<.>"\n'
                '\t"." CLB\n\n"<¶>"\n\t"¶" CLB\n\n'
            ),
        )

    def test_process_file2(self):
        """Test process_file with a dependency element as input"""
        xml_printer = ccat.XMLPrinter(dependency=True)
        document = (
            '<document id="no_id" xml:lang="nob">\n'
            "    <body>\n"
            '        <dependency>"&lt;Muhto&gt;"\n'
            '\t"muhto" CC @CVP #1-&gt;1 \n"&lt;gaskkohagaid&gt;"\n'
            '\t"gaskkohagaid" Adv @ADVL&gt; #2-&gt;12 \n"&lt;,&gt;"\n'
            '\t"," CLB #3-&gt;4 \n"&lt;ja&gt;"\n'
            '\t"ja" CC @CNP #4-&gt;2 \n"&lt;erenoamážit&gt;"\n'
            '\t"erenoamážit" Adv @ADVL&gt; #5-&gt;12 \n'
            '"&lt;dalle_go&gt;"\n'
            '\t"dalle_go" CS @CVP #6-&gt;7 \n"&lt;lei&gt;"\n'
            '\t"leat" V IV Ind Prt Sg3 @FS-ADVL&gt; #7-&gt;12 \n'
            '"&lt;buolaš&gt;"\n'
            '\t"buolaš" N Sg Nom @&lt;SPRED #8-&gt;7 \n"&lt;,&gt;"\n'
            '\t"," CLB #9-&gt;6 \n"&lt;de&gt;"\n'
            '\t"de" Adv @ADVL&gt; #10-&gt;12 \n"&lt;aggregáhta&gt;"\n'
            '\t"aggregáhta" N Sg Nom @SUBJ&gt; #11-&gt;12 \n'
            '"&lt;billánii&gt;"\n'
            '\t"billánit" V IV Ind Prt Sg3 @FS-ADVL&gt; #12-&gt;0 \n'
            '"&lt;.&gt;"\n\t"." CLB #13-&gt;12 \n\n"&lt;¶&gt;"\n'
            '\t"¶" CLB #1-&gt;1 \n\n</dependency>\n'
            "    </body>\n"
            "</document>"
        )

        xml_printer.etree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = xml_printer.process_file()

        self.assertEqual(
            buffer.getvalue(),
            (
                '"<Muhto>"\n\t"muhto" CC @CVP #1->1 \n"<gaskkohagaid>"\n'
                '\t"gaskkohagaid" Adv @ADVL> #2->12 \n"<,>"\n'
                '\t"," CLB #3->4 \n"<ja>"\n'
                '\t"ja" CC @CNP #4->2 \n"<erenoamážit>"\n'
                '\t"erenoamážit" Adv @ADVL> #5->12 \n"<dalle_go>"\n'
                '\t"dalle_go" CS @CVP #6->7 \n"<lei>"\n'
                '\t"leat" V IV Ind Prt Sg3 @FS-ADVL> #7->12 \n"<buolaš>"\n'
                '\t"buolaš" N Sg Nom @<SPRED #8->7 \n"<,>"\n'
                '\t"," CLB #9->6 \n"<de>"\n'
                '\t"de" Adv @ADVL> #10->12 \n"<aggregáhta>"\n'
                '\t"aggregáhta" N Sg Nom @SUBJ> #11->12 \n"<billánii>"\n'
                '\t"billánit" V IV Ind Prt Sg3 @FS-ADVL> #12->0 \n"<.>"\n'
                '\t"." CLB #13->12 \n\n"<¶>"\n\t"¶" CLB #1->1 \n\n'
            ),
        )
