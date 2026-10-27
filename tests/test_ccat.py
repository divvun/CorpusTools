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
import os
import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path

from lxml import etree

from corpustools import ccat


class TestCcatCLI(unittest.TestCase):
    def test_broken_pipe_is_suppressed(self):
        source_dir = str(Path(__file__).resolve().parents[1] / "src")
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join(
            filter(None, (source_dir, env.get("PYTHONPATH")))
        )
        for args in (["--list-orthographies"], ["--help"]):
            with self.subTest(args=args):
                process = subprocess.Popen(
                    [
                        sys.executable,
                        "-c",
                        "from corpustools.ccat import main; raise SystemExit(main())",
                        *args,
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                )
                assert process.stdout is not None
                assert process.stderr is not None
                process.stdout.close()
                stderr = process.stderr.read()
                return_code = process.wait()

                assert return_code == 1
                assert stderr == b""


class TestCcatHyph(unittest.TestCase):
    """Test how ccat handles hyph"""

    def test_hyph1(self):
        """Test the default treatment of hyph tags"""
        options = ccat.make_options()
        buffer = io.StringIO()
        tree = etree.parse(
            io.BytesIO(
                b'<document id="no_id" xml:lang="nob">'
                b"<body><p>mellom<hyph/>krigs<hyph/>tiden</p></body>"
                b"</document>"
            )
        )

        buffer = ccat.process_file(options, tree)
        assert buffer.getvalue() == "mellomkrigstiden ¶\n"

    def test_hyph2(self):
        '''Test hyph tags when hyph_replacement is set to "xml"'''
        options = ccat.make_options(hyph_replacement="xml")
        buffer = io.StringIO()
        tree = etree.parse(
            io.BytesIO(
                b'<document id="no_id" xml:lang="nob">'
                b"<body><p>mellom<hyph/>krigs<hyph/>tiden</p></body>"
                b"</document>"
            )
        )

        buffer = ccat.process_file(options, tree)
        assert buffer.getvalue() == "mellom<hyph/>krigs<hyph/>tiden ¶\n"

    def test_hyph3(self):
        '''Test hyph tags when hyph_replacement is set to "-"'''
        options = ccat.make_options(hyph_replacement="-")
        buffer = io.StringIO()
        tree = etree.parse(
            io.BytesIO(
                b'<document id="no_id" xml:lang="nob">'
                b"<body><p>mellom<hyph/>krigs<hyph/>tiden</p></body>"
                b"</document>"
            )
        )

        buffer = ccat.process_file(options, tree)
        assert buffer.getvalue() == "mellom-krigs-tiden ¶\n"

    def test_hyph4(self):
        """Test the treatment of two hyph tags in a row"""
        options = ccat.make_options(hyph_replacement="-")
        buffer = io.StringIO()

        tree = etree.parse(
            io.BytesIO(
                b'<document id="no_id" xml:lang="nob">'
                b"<body><p>mellom<hyph/><hyph/>tiden</p></body>"
                b"</document>"
            )
        )

        buffer = ccat.process_file(options, tree)
        assert buffer.getvalue() == "mellom-tiden ¶\n"


class TestCcatErrormarkup(unittest.TestCase):
    """Test how ccat handles errormarkup"""

    def test_single_error_inline(self):
        """Plain error element, default text flow"""
        options = ccat.make_options()
        input_error = etree.fromstring(
            "<errorortreal>"
            "fiske leting"
            '<correct errtype="nosplit" pos="noun">fiskeleting</correct>'
            "</errorortreal>"
        )

        textlist = []
        parentlang = "sme"
        ccat.collect_inline_errors(options, input_error, textlist, parentlang)
        got = "".join(textlist)

        assert got == "fiskeleting"

    def test_multi_error_inline(self):
        """Nested error element, default text flow"""
        options = ccat.make_options()

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
        ccat.collect_inline_errors(options, input_error, textlist, parentlang)
        got = "".join(textlist)

        assert got == "skoledagene er så vanskelige"

    def test_single_error_not_inline(self):
        """Plain error element, one word per line output"""
        options = ccat.make_options(one_word_per_line=True)
        input_error = etree.fromstring(
            "<errorortreal>"
            "fiske leting"
            '<correct errtype="nosplit" pos="noun">fiskeleting</correct>'
            "</errorortreal>"
        )

        textlist = []
        ccat.collect_not_inline_errors(options, input_error, textlist)
        got = "".join(textlist)

        assert got == "fiske leting\tfiskeleting\t#errtype=nosplit,pos=noun"

    def test_single_error_not_inline_with_filename(self) -> None:
        """Plain error element, one word per line output, with filename"""
        options = ccat.make_options(print_filename=True, one_word_per_line=True)
        input_error = etree.fromstring(
            "<errorortreal>"
            "fiske leting"
            '<correct errtype="nosplit" pos="noun">fiskeleting</correct>'
            "</errorortreal>"
        )

        options = replace(options, filename="p.xml")

        textlist: list[str] = []
        ccat.collect_not_inline_errors(options, input_error, textlist)
        got = "".join(textlist)

        assert (
            got == "fiske leting\tfiskeleting\t#errtype=nosplit,pos=noun, file: p.xml"
        )

    def test_single_error_not_inline_with_filename_without_attributes(self):
        options = ccat.make_options(print_filename=True, one_word_per_line=True)
        input_error = etree.fromstring(
            "<errorortreal>fiske leting<correct>fiskeleting</correct></errorortreal>"
        )

        options = replace(options, filename="p.xml")

        textlist = []
        ccat.collect_not_inline_errors(options, input_error, textlist)
        got = "".join(textlist)

        assert got == "fiske leting\tfiskeleting\t#file: p.xml"

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

        options = ccat.make_options(one_word_per_line=True, print_filename=True)
        options = replace(options, filename="p.xml")

        textlist = []
        ccat.collect_not_inline_errors(options, input_error, textlist)
        got = "\n".join(textlist)

        assert (
            got == "skoledagene er så vanskelig\tskoledagene er så vanskelige"
            "\t#cat=x,const=spred,errtype=agr,orig=x,pos=adj, file: p.xml\n"
            "vanskerlig\tvanskelig\t#errtype=nosilent,pos=adj, file: p.xml"
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

        options = ccat.make_options(typos=True)
        textlist = []
        ccat.collect_not_inline_errors(options, input_error, textlist)
        got = "\n".join(textlist)

        assert got == "makkár soga\tman soga\nmakkar\tmakkár\t#errtype=á,pos=interr"

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

        options = ccat.make_options(typos=True)
        textlist = []
        ccat.collect_not_inline_errors(options, input_error, textlist)
        got = "\n".join(textlist)

        assert got == "leimme\tleimmet\nleimme\tleat"


class TestCcat(unittest.TestCase):
    def test_p(self):
        """Test the output of a plain p with default text flow"""
        options = ccat.make_options()
        buffer = io.StringIO()
        input_p = etree.fromstring(
            "<p>Et stykke av Norge som er lite kjent - "
            "Litt om Norge i mellomkrigstiden</p>"
        )

        ccat.collect_text(options, input_p, "nob", buffer)
        assert (
            buffer.getvalue() == "Et stykke av Norge som er lite kjent - "
            "Litt om Norge i mellomkrigstiden ¶\n"
        )

    def test_p_with_span(self):
        """The output of a plain p with a span element"""
        options = ccat.make_options()
        buffer = io.StringIO()

        input_p = etree.fromstring(
            "<p>I 1864 ga han ut boka "
            '<span type="quote" xml:lang="dan">'
            '"Fornuftigt Madstel"'
            "</span>."
            "</p>"
        )

        ccat.collect_text(options, input_p, "nob", buffer)
        assert buffer.getvalue() == 'I 1864 ga han ut boka "Fornuftigt Madstel". ¶\n'

    def test_p_with_error(self):
        """The output of a p containing a nested error element"""
        options = ccat.make_options()
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

        ccat.collect_text(options, input_p, "sme", buffer)
        assert buffer.getvalue() == "Bearpmahat earuha uskki ja loaiddu. ¶\n"

    def test_p_one_word_per_line(self):
        """Test the output of a plain p element, one word per line"""
        input_p = etree.fromstring(
            "<p>Et stykke av Norge som er lite kjent - "
            "Litt om Norge i mellomkrigstiden</p>"
        )

        options = ccat.make_options(one_word_per_line=True)

        buffer = io.StringIO()

        ccat.collect_text(options, input_p, "nob", buffer)
        assert (
            buffer.getvalue() == "Et\n"
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

        options = ccat.make_options(one_word_per_line=True)
        buffer = io.StringIO()

        ccat.collect_text(options, input_p, "nob", buffer)
        assert (
            buffer.getvalue() == "I\n"
            "1864\n"
            "ga\n"
            "han\n"
            "ut\n"
            "boka\n"
            '"Fornuftigt\n'
            'Madstel"\n'
            ".\n"
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

        options = ccat.make_options(one_word_per_line=True)

        buffer = io.StringIO()
        ccat.collect_text(options, input_p, "sme", buffer)
        assert (
            buffer.getvalue() == "livččii\n"
            "makkarge\tmakkárge\t#errtype=á,pos=adv\n"
            "politihkka,\nmuhto\nrahpasit\nbaicca\nmuitalivčče\n"
            "makkár soga\tman soga\n"
            "makkar\tmakkár\t#errtype=á,pos=interr\nsoga\nsii\n"
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

        options = ccat.make_options(correction=True)

        buffer = io.StringIO()
        ccat.collect_text(options, input_p, "sme", buffer)
        assert (
            buffer.getvalue()
            == "livččii makkárge politihkka, muhto rahpasit baicca muitalivčče "
            "man soga sii ¶\n"
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

        options = ccat.make_options(errorlex=True)

        buffer = io.StringIO()
        ccat.collect_text(options, input_p, "sme", buffer)
        assert (
            buffer.getvalue()
            == "livččii makkarge politihkka, muhto rahpasit baicca muitalivčče "
            "man soga sii ¶\n"
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

        options = ccat.make_options(errormorphsyn=True)

        buffer = io.StringIO()
        ccat.collect_text(options, input_p, "sme", buffer)
        assert (
            buffer.getvalue()
            == "livččii makkarge politihkka, muhto rahpasit baicca muitalivčče "
            "makkar soga sii ¶\n"
        )

    def test_p_with_error_filtering_errorort(self):
        """errorort = True, print errorort corrections"""
        options = ccat.make_options(errorort=True)

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
        ccat.collect_text(options, input_p, "sme", buffer)
        assert (
            buffer.getvalue()
            == "livččii makkárge politihkka, muhto rahpasit baicca muitalivčče "
            "makkár soga sii ¶\n"
        )

    def test_p_with_error_filtering_errorortreal(self):
        options = ccat.make_options(errorortreal=True)

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
        ccat.collect_text(options, input_p, "sme", buffer)
        assert (
            buffer.getvalue()
            == "livččii makkarge politihkka, muhto rahpasit baicca muitalivčče "
            "makkar soga sii ¶\n"
        )

    def test_visit_this_p_default(self):
        """Visit only plain p and <p type=text> elements"""
        options = ccat.make_options()

        for types in [' type="title"', ' type="listitem"', ' type="tablecell"']:
            input_xml = etree.fromstring("<p" + types + ">ášŧŋđžčøåæ</p>")
            assert not ccat.visit_this_node(options, input_xml)

        for types in ["", ' type="text"']:
            input_xml = etree.fromstring("<p" + types + ">ášŧŋđžčøåæ</p>")
            assert ccat.visit_this_node(options, input_xml)

    def test_visit_this_p_title_set(self):
        """Visit only <p type=title> elements when title is True"""
        options = ccat.make_options(title=True)

        for types in ["", ' type="text"', ' type="listitem"', ' type="tablecell"']:
            input_xml = etree.fromstring("<p" + types + ">ášŧŋđžčøåæ</p>")
            assert not ccat.visit_this_node(options, input_xml)

        for types in [' type="title"']:
            input_xml = etree.fromstring("<p" + types + ">ášŧŋđžčøåæ</p>")
            assert ccat.visit_this_node(options, input_xml)

    def test_visit_this_p_listitem_set(self):
        """Visit only <p type=listitem> elements when listitem is True"""
        options = ccat.make_options(listitem=True)

        for types in ["", ' type="text"', ' type="title"', ' type="tablecell"']:
            input_xml = etree.fromstring("<p" + types + ">ášŧŋđžčøåæ</p>")
            assert not ccat.visit_this_node(options, input_xml)

        for types in [' type="listitem"']:
            input_xml = etree.fromstring("<p" + types + ">ášŧŋđžčøåæ</p>")
            assert ccat.visit_this_node(options, input_xml)

    def test_visit_this_p_tablecell_set(self):
        """Visit only <p type=tablecell> elements when table is True"""
        options = ccat.make_options(table=True)

        for types in ["", ' type="text"', ' type="title"', ' type="listitem"']:
            input_xml = etree.fromstring("<p" + types + ">ášŧŋđžčøåæ</p>")
            assert not ccat.visit_this_node(options, input_xml)

        for types in [' type="tablecell"']:
            input_xml = etree.fromstring("<p" + types + ">ášŧŋđžčøåæ</p>")
            assert ccat.visit_this_node(options, input_xml)

    def test_visit_this_p_allp_set(self):
        """Visit all p elements when all_paragraphs is True"""
        options = ccat.make_options(all_paragraphs=True)

        for types in [
            "",
            ' type="text"',
            ' type="title"',
            ' type="listitem"',
            ' type="tablecell"',
        ]:
            input_xml = etree.fromstring("<p" + types + ">ášŧŋđžčøåæ</p>")
            assert ccat.visit_this_node(options, input_xml)

    def test_process_file_default(self):
        """Default settings, print content of p elements

        Check the output of plain p elements, with default settings
        Specifically, check that only plain p gets output, whereas
        p elements with the type title, listitem and tablecell get no output.
        """
        options = ccat.make_options()

        for types in [' type="title"', ' type="listitem"', ' type="tablecell"']:
            document = (
                """<document id="no_id" xml:lang="sme"><body><p"""
                + types
                + """>ášŧŋđžčøåæ</p></body></document>"""
            )

            tree = etree.parse(io.BytesIO(document.encode("utf8")))
            buffer = ccat.process_file(options, tree)
            assert buffer.getvalue() == ""

        for types in ["", ' type="text"']:
            document = (
                """<document id="no_id" xml:lang="sme"><body><p"""
                + types
                + """>ášŧŋđžčøåæ</p></body></document>"""
            )

            tree = etree.parse(io.BytesIO(document.encode("utf8")))
            buffer = ccat.process_file(options, tree)
            assert buffer.getvalue() == "ášŧŋđžčøåæ ¶\n"

    def test_process_file_title_set(self):
        """Print only content of p elements with type=title."""
        options = ccat.make_options(title=True)

        for types in ["", ' type="text"', ' type="listitem"', ' type="tablecell"']:
            document = (
                '<document id="no_id" xml:lang="sme"><body><p {}>'
                "ášŧŋđžčøåæ</p></body></document>".format(types)
            )
            tree = etree.parse(io.BytesIO(document.encode("utf8")))
            buffer = ccat.process_file(options, tree)
            assert buffer.getvalue() == ""

        for types in [' type="title"']:
            document = (
                '<document id="no_id" xml:lang="sme"><body><p {}>'
                "ášŧŋđžčøåæ</p></body></document>".format(types)
            )
            tree = etree.parse(io.BytesIO(document.encode("utf8")))
            buffer = ccat.process_file(options, tree)
            assert buffer.getvalue() == "ášŧŋđžčøåæ ¶\n"

    def test_process_file_listitem_set(self):
        """Print only content of p elements with type=listitem."""
        options = ccat.make_options(listitem=True)

        for types in ["", ' type="text"', ' type="title"', ' type="tablecell"']:
            document = (
                """<document id="no_id" xml:lang="sme"><body><p"""
                + types
                + """>ášŧŋđžčøåæ</p></body></document>"""
            )
            tree = etree.parse(io.BytesIO(document.encode("utf8")))
            buffer = ccat.process_file(options, tree)
            assert buffer.getvalue() == ""

        for types in [' type="listitem"']:
            document = (
                """<document id="no_id" xml:lang="sme"><body><p"""
                + types
                + """>ášŧŋđžčøåæ</p></body></document>"""
            )
            tree = etree.parse(io.BytesIO(document.encode("utf8")))
            buffer = ccat.process_file(options, tree)
            assert buffer.getvalue() == "ášŧŋđžčøåæ ¶\n"

    def test_process_file_tablecell_set(self):
        """Print only content of p elements with type=title gets output."""
        options = ccat.make_options(table=True)

        for types in ["", ' type="text"', ' type="title"', ' type="listitem"']:
            document = (
                '<document id="no_id" xml:lang="sme"><body><p '
                + types
                + ">ášŧŋđžčøåæ</p></body></document>"
            )

            tree = etree.parse(io.BytesIO(document.encode("utf8")))
            buffer = ccat.process_file(options, tree)
            assert buffer.getvalue() == ""

        for types in [' type="tablecell"']:
            document = (
                '<document id="no_id" xml:lang="sme"><body><p '
                + types
                + ">ášŧŋđžčøåæ</p></body></document>"
            )
            tree = etree.parse(io.BytesIO(document.encode("utf8")))
            buffer = ccat.process_file(options, tree)
            assert buffer.getvalue() == "ášŧŋđžčøåæ ¶\n"

    def test_process_file_allp_set(self):
        """all_paragraphs option is True, all p elements get output."""
        options = ccat.make_options(all_paragraphs=True)

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
            tree = etree.parse(io.BytesIO(document.encode("utf8")))
            buffer = ccat.process_file(options, tree)
            assert buffer.getvalue() == "ášŧŋđžčøåæ ¶\n"

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

        options = ccat.make_options(one_word_per_line=True, errorlex=True)
        tree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = ccat.process_file(options, tree)
        assert buffer.getvalue() == (
            "livččii\n"
            "makkarge\n"
            "politihkka,\n"
            "muhto\n"
            "rahpasit\n"
            "baicca\n"
            "muitalivčče\n"
            "makkár soga\tman soga\n"
            "sii\n"
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

        options = ccat.make_options(one_word_per_line=True, errorort=True)
        tree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = ccat.process_file(options, tree)
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
        assert got == want

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

        options = ccat.make_options(typos=True)
        tree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = ccat.process_file(options, tree)
        assert buffer.getvalue() == (
            "makkarge\tmakkárge\t#errtype=á,pos=adv\n"
            "makkár soga\tman soga\n"
            "makkar\tmakkár\t#errtype=á,pos=interr\n"
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

        options = ccat.make_options(typos=True, errorlex=True)
        tree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = ccat.process_file(options, tree)
        assert buffer.getvalue() == "makkár soga\tman soga\n"

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

        options = ccat.make_options(typos=True, one_word_per_line=True, errorort=True)
        tree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = ccat.process_file(options, tree)
        assert (
            buffer.getvalue() == "makkarge\tmakkárge\t#errtype=á,pos=adv\n"
            "makkar\tmakkár\t#errtype=á,pos=interr\n"
        )

    def test_get_lang(self):
        """Check that get_lang finds the main lang of the document"""
        tree = etree.parse(io.BytesIO(b'<document id="no_id" xml:lang="sme"/>'))

        assert ccat.get_lang(tree) == "sme"

    def test_get_element_language_same_as_parent(self):
        """xml:lang is not set in the p element. Return parent language."""
        element = etree.fromstring("<p/>")
        assert ccat.get_element_language(element, "sme") == "sme"

    def test_get_element_language_different_from_parent(self):
        """Check that the value of xml:lang is returned when it is set."""
        element = etree.fromstring('<p xml:lang="nob"/>')
        assert ccat.get_element_language(element, "sme") == "nob"

    def test_process_file_language_nob(self):
        """lang=nob, only nob content should be output"""
        options = ccat.make_options(lang="nob")
        tree = etree.parse(
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

        buffer = ccat.process_file(options, tree)
        assert buffer.getvalue() == "nob1  nob2 ¶\n"

    def test_process_two_paragraphs(self):
        """Check that the ¶ character is printed"""
        options = ccat.make_options()
        tree = etree.parse(
            io.BytesIO(
                b'<document id="no_id" xml:lang="nob">'
                b"    <body>"
                b"        <p>nob1</p>"
                b"        <p>nob2</p>"
                b"    </body>"
                b"</document>"
            )
        )

        buffer = ccat.process_file(options, tree)
        assert buffer.getvalue() == "nob1 ¶\nnob2 ¶\n"

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

        options = ccat.make_options(lang="sme")
        tree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = ccat.process_file(options, tree)

        assert buffer.getvalue() == ""

    def test_foreign(self):
        """Check the output of a p containing an errorlang element

        The errorlang option is True.
        """
        options = ccat.make_options(errorlang=True)
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

        tree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = ccat.process_file(options, tree)

        assert buffer.getvalue() == (
            "Vijmak bierjjedak! nor vijmak de bierjjedak sjattáj. ¶\n"
        )

    def test_no_foreign(self):
        """noforeign option is True

        Neither the errorlang.text nor the correct attribute should be output.
        Check that this really happens.
        """
        options = ccat.make_options(noforeign=True)
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

        tree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = ccat.process_file(options, tree)

        assert buffer.getvalue() == (
            "Vijmak bierjjedak!  vijmak de bierjjedak sjattáj. ¶\n"
        )

    def test_no_foreign_typos(self):
        """noforeign is True, typos is True

        When the noforeign option is True, neither the errorlang.text
        nor the correct attribute should be output. Check that this really
        happens even when the typos option is set.
        """
        options = ccat.make_options(typos=True, noforeign=True)
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

        tree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = ccat.process_file(options, tree)

        assert buffer.getvalue() == "sjattáj\tsjattaj\t#errorinfo=vowlat,á-a\n"

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
        options = ccat.make_options(typos=True)
        tree = etree.parse(io.BytesIO(document.encode("utf8")))

        buffer = ccat.process_file(options, tree)
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
        assert got == want

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

        options = ccat.make_options(typos=True, errormorphsyn=True)
        tree = etree.parse(io.BytesIO(document.encode("utf8")))

        buffer = ccat.process_file(options, tree)

        assert buffer.getvalue() == (
            "leat okta mánná\tlea okta mánná"
            "\t#cat=sg3prs,const=v,errtype=agr,orig=pl3prs,pos=v\n"
            "okta máná\tokta mánná"
            "\t#cat=nomsg,const=spred,errtype=case,orig=gensg,pos=n\n"
        )

    def test_process_file1(self):
        """Test process_file with a disambiguation element as input"""
        options = ccat.make_options(disambiguation=True)
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

        tree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = ccat.process_file(options, tree)

        assert buffer.getvalue() == (
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
        )

    def test_process_file2(self):
        """Test process_file with a dependency element as input"""
        options = ccat.make_options(dependency=True)
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

        tree = etree.parse(io.BytesIO(document.encode("utf8")))
        buffer = ccat.process_file(options, tree)

        assert (
            buffer.getvalue()
            == '"<Muhto>"\n\t"muhto" CC @CVP #1->1 \n"<gaskkohagaid>"\n'
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
        )
