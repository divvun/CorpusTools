# -*- coding: utf-8 -*-

#
#   This file contains routines to change names of corpus files
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
#   Copyright © 2013-2021 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

import doctest
import unittest

import lxml.doctestcompare as doctestcompare
from lxml import etree

from corpustools import errormarkup


class TestErrorMarkup(unittest.TestCase):
    def assertXmlEqual(self, got, want):
        """Check if two stringified xml snippets are equal"""
        got = etree.tostring(got, encoding="unicode")
        want = etree.tostring(want, encoding="unicode")
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(doctest.Example("", want), got, 0)
            raise AssertionError(message)

    def test_only_text_in_element(self):
        in_elem = etree.fromstring("<p>Muittán doložiid</p>")
        want = etree.fromstring("<p>Muittán doložiid</p>")

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_error_parser_errorlang_infinity(self):
        in_elem = "{molekylærbiologimi}∞{kal,bio}"
        want = etree.fromstring(
            "<errorlang>molekylærbiologimi<correct>kal,bio</correct></errorlang>"
        )

        got = errormarkup.error_parser(in_elem)
        self.assertEqual(len(got), 1)
        self.assertXmlEqual(got[0], want)

    def test_error_parser_errorlang_infinity_with_new_lines(self):
        in_elem = "\n\n\n\n{molekylærbiologimi}∞{kal,bio}\n\n\n\n"
        want = etree.fromstring(
            "<errorlang>molekylærbiologimi<correct>kal,bio</correct></errorlang>"
        )

        got = errormarkup.error_parser(in_elem)
        self.assertEqual(len(got), 2)
        self.assertXmlEqual(got[1], want)

    def test_quote_char(self):
        in_elem = "{”sjievnnijis”}${conc,vnn-vnnj|sjievnnjis}"
        want = etree.fromstring(
            '<errorort>”sjievnnijis”<correct errorinfo="conc,vnn-vnnj">sjievnnjis</correct></errorort>'
        )

        got = errormarkup.error_parser(in_elem)
        self.assertEqual(len(got), 1)
        self.assertXmlEqual(got[0], want)

    def test_paragraph_character(self):
        in_elem = etree.fromstring("<p>Vuodoláhkaj §110a</p>")
        want = etree.fromstring("<p>Vuodoláhkaj §110a</p>")

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_error_parser_errorort1(self):
        in_elem = "{jne.}${adv,typo|jna.}"
        want = etree.fromstring(
            '<errorort>jne.<correct errorinfo="adv,typo">jna.</correct></errorort>'
        )

        got = errormarkup.error_parser(in_elem)
        self.assertEqual(len(got), 1)
        self.assertXmlEqual(got[0], want)

    def test_errorort1(self):
        in_elem = etree.fromstring("<p>{jne.}${adv,typo|jna.}</p>")
        want = etree.fromstring(
            '<p><errorort>jne.<correct errorinfo="adv,typo">jna.</correct></errorort></p>'
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_errorort2(self):
        in_elem = etree.fromstring("<p>{daesn'}${daesnie}</p>")
        want = etree.fromstring(
            "<p><errorort>daesn'<correct>daesnie</correct></errorort></p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_input_contains_slash(self):
        in_elem = etree.fromstring("<p>{magistter/}${loan,vowlat,e-a|magisttar}</p>")
        want = etree.fromstring(
            '<p><errorort>magistter/<correct errorinfo="loan,vowlat,e-a">'
            "magisttar</correct></errorort></p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_error_correct1(self):
        in_elem = etree.fromstring("<p>{1]}§{Ij}</p>")
        want = etree.fromstring("<p><error>1]<correct>Ij</correct></error></p>")

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_error_correct2(self):
        in_elem = etree.fromstring("<p>{væ]keles}§{væjkeles}</p>")
        want = etree.fromstring(
            "<p><error>væ]keles<correct>væjkeles</correct></error></p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_error_correct3(self):
        in_elem = etree.fromstring("<p>{smávi-}§{smávit-}</p>")
        want = etree.fromstring(
            "<p><error>smávi-<correct>smávit-</correct></error></p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_error_correct4(self):
        in_elem = etree.fromstring("<p>{CD:t}§{CD:at}</p>")
        want = etree.fromstring("<p><error>CD:t<correct>CD:at</correct></error></p>")

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_error_correct5(self):
        in_elem = etree.fromstring("<p>{DNB-feaskáris}§{DnB-feaskáris}</p>")
        want = etree.fromstring(
            "<p><error>DNB-feaskáris<correct>DnB-feaskáris</correct></error></p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_error_correct6(self):
        in_elem = etree.fromstring("<p>{boade}§{boađe}</p>")
        want = etree.fromstring("<p><error>boade<correct>boađe</correct></error></p>")

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_error_correct7(self):
        in_elem = etree.fromstring("<p>{2005’as}§{2005:s}</p>")
        want = etree.fromstring(
            "<p><error>2005’as<correct>2005:s</correct></error></p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_error_correct8(self):
        in_elem = etree.fromstring("<p>{NSRii}§{NSR:i}</p>")
        want = etree.fromstring("<p><error>NSRii<correct>NSR:i</correct></error></p>")

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_error_correct9(self):
        in_elem = etree.fromstring("<p>{Nordkjosbotn'ii}§{Nordkjosbotnii}</p>")
        want = etree.fromstring(
            "<p><error>Nordkjosbotn'ii<correct>Nordkjosbotnii</correct>" "</error></p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_errorort3(self):
        in_elem = etree.fromstring("<p>{nourra}${a,meta|nuorra}</p>")
        want = etree.fromstring(
            '<p><errorort>nourra<correct errorinfo="a,meta">nuorra</correct></errorort></p>'
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_error_morphsyn1(self):
        in_elem = etree.fromstring(
            "<p>{Nieiddat leat nuorra}£{a,spred,nompl,nomsg,agr|Nieiddat leat nuorat}</p>"
        )
        want = etree.fromstring(
            "<p><errormorphsyn>Nieiddat leat nuorra"
            '<correct errorinfo="a,spred,nompl,nomsg,agr">Nieiddat leat '
            "nuorat</correct></errormorphsyn></p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_error_parser_error_morphsyn1(self):
        in_elem = (
            "{Nieiddat leat nuorra}£{a,spred,nompl,nomsg,agr|Nieiddat leat nuorat}"
        )
        want = etree.fromstring(
            "<errormorphsyn>Nieiddat leat nuorra<correct "
            'errorinfo="a,spred,nompl,nomsg,agr">Nieiddat leat nuorat'
            "</correct></errormorphsyn>"
        )

        got = errormarkup.error_parser(in_elem)
        self.assertEqual(len(got), 1)
        self.assertXmlEqual(got[0], want)

    def test_error_syn1(self):
        in_elem = etree.fromstring("<p>{riŋgen nieidda lusa}¥{x,pph|riŋgen niidii}</p>")
        want = etree.fromstring(
            '<p><errorsyn>riŋgen nieidda lusa<correct errorinfo="x,pph">'
            "riŋgen niidii</correct></errorsyn></p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_error_syn2(self):
        in_elem = etree.fromstring("<p>{ovtta}¥{num,redun| }</p>")
        want = etree.fromstring(
            '<p><errorsyn>ovtta<correct errorinfo="num,redun"></correct>'
            "</errorsyn></p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_erro_lex1(self):
        in_elem = etree.fromstring("<p>{dábálaš}€{adv,adj,der|dábálaččat}</p>")
        want = etree.fromstring(
            '<p><errorlex>dábálaš<correct errorinfo="adv,adj,der">dábálaččat'
            "</correct></errorlex></p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_error_ortreal1(self):
        in_elem = etree.fromstring("<p>{ráhččamušaid}¢{noun,mix|rahčamušaid}</p>")
        want = etree.fromstring(
            '<p><errorortreal>ráhččamušaid<correct errorinfo="noun,mix">'
            "rahčamušaid</correct></errorortreal></p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_error_ortreal2(self):
        in_elem = etree.fromstring(
            "<p>gitta {Nordkjosbotn'ii}${Nordkjosbotnii} (mii lea ge "
            "{nordkjosbotn}${Nordkjosbotn} sámegillii? Muhtin, veahket mu!) "
            "gos</p>"
        )
        want = etree.fromstring(
            "<p>gitta <errorort>Nordkjosbotn'ii<correct>Nordkjosbotnii"
            "</correct></errorort> (mii lea ge <errorort>nordkjosbotn"
            "<correct>Nordkjosbotn</correct></errorort> sámegillii? "
            "Muhtin, veahket mu!) gos</p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_error_parser_with_two_simple_errors(self):
        in_elem = (
            "gitta {Nordkjosbotn'ii}${Nordkjosbotnii} (mii lea ge "
            "{nordkjosbotn}${Nordkjosbotn} sámegillii? Muhtin, veahket mu!) "
            "gos"
        )
        got = errormarkup.error_parser(in_elem)

        self.assertEqual(len(got), 3)
        self.assertEqual(got[0], "gitta ")
        self.assertEqual(
            etree.tostring(got[1], encoding="unicode"),
            "<errorort>Nordkjosbotn'ii<correct>Nordkjosbotnii</correct></errorort> "
            "(mii lea ge ",
        )
        self.assertEqual(
            etree.tostring(got[2], encoding="unicode"),
            "<errorort>nordkjosbotn<correct>Nordkjosbotn</correct></errorort> "
            "sámegillii? Muhtin, veahket mu!) gos",
        )

    def test_error_morphsyn2(self):
        in_elem = etree.fromstring(
            "<p>Čáppa muohtaskulptuvrraid ráhkadeapmi VSM olggobealde lei "
            "maiddái ovttasbargu gaskal {skuvla ohppiid}£"
            "{noun,attr,gensg,nomsg,case|skuvlla ohppiid}"
            "ja VSM.</p>"
        )
        want = etree.fromstring(
            "<p>Čáppa muohtaskulptuvrraid ráhkadeapmi VSM olggobealde lei "
            "maiddái ovttasbargu gaskal <errormorphsyn>skuvla ohppiid"
            '<correct errorinfo="noun,attr,gensg,nomsg,case">skuvlla ohppiid'
            "</correct></errormorphsyn> ja VSM.</p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_errorort4(self):
        in_elem = etree.fromstring(
            "<p>- ruksesruonáčalmmehisvuohta lea sullii " "{8%:as}${acr,suf|8%:s}</p>"
        )
        want = etree.fromstring(
            "<p>- ruksesruonáčalmmehisvuohta lea sullii <errorort>8%:as"
            '<correct errorinfo="acr,suf">8%:s</correct></errorort></p>'
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_error_ortreal3(self):
        in_elem = etree.fromstring(
            "<p>( {nissonin}¢{noun,suf|nissoniin} dušše {0.6 %:s}£{0.6 %} )</p>"
        )
        want = etree.fromstring(
            '<p>( <errorortreal>nissonin<correct errorinfo="noun,suf">'
            "nissoniin</correct></errorortreal> dušše <errormorphsyn>0.6 %:s"
            "<correct>0.6 %</correct></errormorphsyn> )</p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_errorort5(self):
        in_elem = etree.fromstring(
            "<p>(haploida) ja {njiŋŋalas}${noun,á|njiŋŋálas} {ságahuvvon}"
            "${verb,a|sagahuvvon} manneseallas (diploida)</p>"
        )
        want = etree.fromstring(
            '<p>(haploida) ja <errorort>njiŋŋalas<correct errorinfo="noun,á">'
            "njiŋŋálas</correct></errorort> <errorort>ságahuvvon"
            '<correct errorinfo="verb,a">sagahuvvon</correct></errorort> '
            "manneseallas (diploida)</p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_errorort6(self):
        in_elem = etree.fromstring(
            "<p>(gii oahpaha) {giinu}${x,notcmp|gii nu} manai {intiánalávlagat}"
            "${loan,conc|indiánalávlagat} {guovža-klána}${noun,cmp|guovžaklána} "
            "olbmuid</p>"
        )
        want = etree.fromstring(
            '<p>(gii oahpaha) <errorort>giinu<correct errorinfo="x,notcmp">'
            "gii nu</correct></errorort> manai <errorort>intiánalávlagat"
            '<correct errorinfo="loan,conc">indiánalávlagat</correct>'
            '</errorort> <errorort>guovža-klána<correct errorinfo="noun,cmp">'
            "guovžaklána</correct></errorort> olbmuid</p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_error_format(self):
        in_elem = etree.fromstring("<p>{{A  B}‰{notspace|A B}  C}‰{notspace|A B C}</p>")
        want = etree.fromstring(
            "<p>"
            '<errorformat correct="A B C" errorinfo="notspace">'
            '<errorformat correct="A B" errorinfo="notspace">'
            "A  B</errorformat>"
            "  C</errorformat>"
            "</p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_preserve_space_at_end_of_sentence(self):
        in_elem = etree.fromstring(
            "<p>buvttadeaddji Anstein {Mikkelsens}${typo|Mikkelsen} lea "
            "ráhkadan. </p>"
        )

        want = '<p>buvttadeaddji Anstein <errorort>Mikkelsens<correct errorinfo="typo">Mikkelsen</correct></errorort> lea ráhkadan. </p>'

        errormarkup.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding="unicode")
        self.assertEqual(got, want)

    def test_place_error_elements_before_old_element1(self):
        """Test if errorlements are inserted before the span element."""
        in_elem = etree.fromstring(
            "<p>buvttadeaddji Anstein {Mikkelsens}${typo|Mikkelsen} lea "
            "ráhkadan. {bálkkášumi}${vowlat,á-a|bálkkašumi} miessemánu. <span "
            'type="quote" xml:lang="eng">«Best Shorts Competition»</span></p>'
        )

        want = (
            "<p>buvttadeaddji Anstein <errorort>Mikkelsens"
            '<correct errorinfo="typo">Mikkelsen</correct></errorort> lea ráhkadan. '
            '<errorort>bálkkášumi<correct errorinfo="vowlat,á-a">bálkkašumi</correct></errorort>'
            ' miessemánu. <span type="quote" xml:lang="eng">«Best Shorts '
            "Competition»</span></p>"
        )

        errormarkup.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding="unicode")
        self.assertEqual(got, want)

    def test_place_error_elements_before_old_element2(self):
        """Test if errorlements are inserted before the span element."""
        in_elem = etree.fromstring(
            "<p>{Mikkelsens}${typo|Mikkelsen} lea ráhkadan. "
            "{bálkkášumi}${vowlat,á-a|bálkkašumi} miessemánu. "
            '<span type="quote" xml:lang="eng">'
            "«Best Shorts Competition»</span></p>"
        )

        want = '<p><errorort>Mikkelsens<correct errorinfo="typo">Mikkelsen</correct></errorort> lea ráhkadan. <errorort>bálkkášumi<correct errorinfo="vowlat,á-a">bálkkašumi</correct></errorort> miessemánu. <span type="quote" xml:lang="eng">«Best Shorts Competition»</span></p>'

        errormarkup.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding="unicode")
        self.assertEqual(got, want)

    def test_place_error_element_after_old_element(self):
        in_elem = etree.fromstring(
            '<p>I 1864 ga han ut boka <span type="quote" xml:lang="swe">'
            '"Fornuftigt Madstel"</span>. {Asbjørsen}${prop,typo|Asbjørnsen} '
            "døde 5. januar 1885, nesten 73 år gammel.</p>"
        )

        want = (
            '<p>I 1864 ga han ut boka <span type="quote" xml:lang="swe">'
            '"Fornuftigt Madstel"</span>. <errorort>Asbjørsen'
            '<correct errorinfo="prop,typo">Asbjørnsen</correct></errorort> '
            "døde 5. januar 1885, nesten 73 år gammel.</p>"
        )

        errormarkup.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding="unicode")
        self.assertEqual(got, want)

    def test_place_error_element_before_and_after_old_element(self):
        """The input:

        buvttadeaddji Anstein {Mikkelsens}${typo|Mikkelsen} lea ráhkadan.
        «Best Shorts Competition» {bálkkášumi}${vowlat,á-a|bálkkašumi}
        miessemánu.

        gets converted to this:
         <p>buvttadeaddji Anstein <span type="quote" xml:lang="eng">
         «Best Shorts Competition»</span>
         {bálkkášumi}${vowlat,á-a|bálkkašumi} miessemánu.
         <errorort correct="Mikkelsen" errorinfo="typo">Mikkelsens</errorort>
         lea ráhkadan.</p>
        """
        in_elem = etree.fromstring(
            "<p>buvttadeaddji Anstein {Mikkelsens}${typo|Mikkelsen} lea "
            'ráhkadan. <span type="quote" xml:lang="eng">«Best Shorts '
            "Competition»</span> {bálkkášumi}${vowlat,á-a|bálkkašumi} "
            "miessemánu.</p>"
        )

        want = (
            "<p>buvttadeaddji Anstein <errorort>Mikkelsens"
            '<correct errorinfo="typo">Mikkelsen</correct></errorort> lea '
            'ráhkadan. <span type="quote" xml:lang="eng">«Best Shorts '
            "Competition»</span> <errorort>bálkkášumi"
            '<correct errorinfo="vowlat,á-a">bálkkašumi</correct></errorort> '
            "miessemánu.</p>"
        )

        errormarkup.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding="unicode")
        self.assertEqual(got, want)

    def test_add_error_markup3Levels(self):
        """The input:

        buvttadeaddji Anstein {Mikkelsens}${typo|Mikkelsen} lea ráhkadan.
        «Best Shorts Competition» {bálkkášumi}${vowlat,á-a|bálkkašumi}
        miessemánu.

        gets converted to this:
         <p>buvttadeaddji Anstein <span type="quote" xml:lang="eng">
         «Best Shorts Competition»</span>
         {bálkkášumi}${vowlat,á-a|bálkkašumi} miessemánu.
         <errorort correct="Mikkelsen" errorinfo="typo">Mikkelsens</errorort>
         lea ráhkadan.</p>
        """
        in_elem = etree.fromstring(
            "<p>buvttadeaddji Anstein <errorort>Mikkelsens<correct "
            'errorinfo="typo">Mikkelsen</correct></errorort> lea ráhkadan. '
            '<span type="quote" xml:lang="eng">«Best Shorts Competition»'
            '</span> <errorort>bálkkášumi<correct errorinfo="vowlat,á-a">'
            "bálkkašumi</correct></errorort> miessemánu. <em>buvttadeaddji "
            "Anstein {Mikkelsens}${typo|Mikkelsen} lea ráhkadan. <span "
            'type="quote" xml:lang="eng">«Best Shorts Competition»</span> '
            "{bálkkášumi}${vowlat,á-a|bálkkašumi} miessemánu.</em></p>"
        )

        want = (
            "<p>buvttadeaddji Anstein <errorort>Mikkelsens<correct "
            'errorinfo="typo">Mikkelsen</correct></errorort> lea ráhkadan. '
            '<span type="quote" xml:lang="eng">«Best Shorts Competition»'
            '</span> <errorort>bálkkášumi<correct errorinfo="vowlat,á-a">'
            "bálkkašumi</correct></errorort> miessemánu. <em>buvttadeaddji "
            'Anstein <errorort>Mikkelsens<correct errorinfo="typo">Mikkelsen'
            '</correct></errorort> lea ráhkadan. <span type="quote" '
            'xml:lang="eng">«Best Shorts Competition»</span> <errorort>'
            'bálkkášumi<correct errorinfo="vowlat,á-a">bálkkašumi</correct>'
            "</errorort> miessemánu.</em></p>"
        )

        errormarkup.add_error_markup(in_elem)
        got = etree.tostring(in_elem, encoding="unicode")
        self.assertEqual(got, want)

    # Nested markup
    def test_nested_markup1(self):
        in_elem = etree.fromstring(
            "<p>{{šaddai}${verb,conc|šattai} ollu áššit}£{verb,fin,pl3prs,sg3prs,tense|šadde ollu áššit}</p>"
        )
        want = etree.fromstring(
            '<p><errormorphsyn errorinfo="verb,fin,pl3prs,sg3prs,tense" '
            'correct="šadde ollu áššit"><errorort errorinfo="verb,conc" '
            'correct="šattai">šaddai</errorort> ollu áššit'
            "</errormorphsyn></p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_nested_markup2(self):
        in_elem = etree.fromstring(
            "<p>{guokte {ganddat}§{n,á|gánddat}}£{n,nump,gensg,nompl,case|guokte gándda}</p>"
        )
        want = etree.fromstring(
            '<p><errormorphsyn errorinfo="n,nump,gensg,nompl,case" '
            'correct="guokte gándda">guokte <error errorinfo="n,á" '
            'correct="gánddat">ganddat</error></errormorphsyn></p>'
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_nested_markup3(self):
        in_elem = etree.fromstring(
            "<p>{Nieiddat leat {nourra}${adj,meta|nuorra}}"
            "£{adj,spred,nompl,nomsg,agr|Nieiddat leat nuorat}</p>"
        )
        want = etree.fromstring(
            '<p><errormorphsyn errorinfo="adj,spred,nompl,nomsg,agr" '
            'correct="Nieiddat leat nuorat">Nieiddat leat <errorort '
            'errorinfo="adj,meta" '
            'correct="nuorra">nourra</errorort></errormorphsyn></p>'
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_nested_markup4(self):
        in_elem = etree.fromstring(
            "<p>{leat {okta máná}£{n,spred,nomsg,gensg,case|okta mánná}}"
            "£{v,v,sg3prs,pl3prs,agr|lea okta mánná}</p>"
        )
        want = etree.fromstring(
            '<p><errormorphsyn errorinfo="v,v,sg3prs,pl3prs,agr" correct="'
            'lea okta mánná">leat <errormorphsyn errorinfo="n,spred,nomsg,'
            'gensg,case" correct="okta mánná">okta máná</errormorphsyn>'
            "</errormorphsyn></p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_nested_markup5(self):
        in_elem = etree.fromstring(
            "<p>heaitit {dáhkaluddame}${verb,a|dahkaluddame} ahte sis "
            "{máhkaš}¢{adv,á|mahkáš} livččii {makkarge}${adv,á|makkárge} "
            "politihkka, muhto rahpasit baicca muitalivčče {{makkar}"
            "${interr,á|makkár} soga}€{man soga} sii {ovddasttit}"
            "${verb,conc|ovddastit}.</p>"
        )
        want = etree.fromstring(
            '<p>heaitit <errorort correct="dahkaluddame" errorinfo="verb,a">'
            'dáhkaluddame</errorort> ahte sis <errorortreal correct="mahkáš" '
            'errorinfo="adv,á">máhkaš</errorortreal> livččii <errorort '
            'correct="makkárge" errorinfo="adv,á">makkarge</errorort> '
            'politihkka, muhto rahpasit baicca muitalivčče <errorlex correct="'
            'man soga"><errorort correct="makkár" errorinfo="interr,á">'
            "makkar</errorort> soga</errorlex> sii <errorort "
            'correct="ovddastit" errorinfo="verb,conc">ovddasttit'
            "</errorort>.</p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_process_text29(self):
        text = (
            "{{Bearpmahat}${noun,svow|Bearpmehat} {earuha}€{verb,v,w|sirre}}"
            "£{verb,fin,pl3prs,sg3prs,agr|Bearpmehat sirrejit} uskki ja "
            "loaiddu."
        )
        want = [
            "{{Bearpmahat}",
            "${noun,svow|Bearpmehat}",
            " {earuha}",
            "€{verb,v,w|sirre}",
            "}",
            "£{verb,fin,pl3prs,sg3prs,agr|Bearpmehat sirrejit}",
            " uskki ja loaiddu.",
        ]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_nested_markup6(self):
        in_elem = etree.fromstring(
            "<p>{{Bearpmahat}${noun,svow|Bearpmehat} {earuha}€{verb,v,w|sirre}}£{verb,fin,pl3prs,sg3prs,agr|Bearpmehat sirrejit} uskki ja "
            "loaiddu.</p>"
        )
        want = etree.fromstring(
            '<p><errormorphsyn errorinfo="verb,fin,pl3prs,sg3prs,agr" '
            'correct="Bearpmehat sirrejit"><errorort errorinfo="noun,svow" '
            'correct="Bearpmehat">Bearpmahat</errorort> <errorlex '
            'errorinfo="verb,v,w" correct="sirre">earuha</errorlex>'
            "</errormorphsyn> uskki ja loaiddu.</p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_process_text30(self):
        text = (
            "Mirja ja Line leaba {gulahallan olbmožat}"
            "¢{noun,cmp|gulahallanolbmožat}€{gulahallanolbmot}"
        )
        want = [
            "Mirja ja Line leaba {gulahallan olbmožat}",
            "¢{noun,cmp|gulahallanolbmožat}",
            "€{gulahallanolbmot}",
        ]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_nested_markup7(self):
        in_elem = etree.fromstring(
            "<p>Mirja ja Line leaba {gulahallan olbmožat}"
            "¢{noun,cmp|gulahallanolbmožat}€{gulahallanolbmot}</p>"
        )
        want = etree.fromstring(
            "<p>Mirja ja Line leaba <errorlex><errorortreal>gulahallan "
            'olbmožat<correct errorinfo="noun,cmp">gulahallanolbmožat'
            "</correct></errorortreal><correct>gulahallanolbmot</correct>"
            "</errorlex></p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_nested_markup8(self):
        in_elem = etree.fromstring(
            "<p>{Ovddit geasis}£{noun,advl,gensg,locsg,case|Ovddit geasi} "
            "{{{čoaggen}${verb,mono|čoggen} ollu jokŋat}"
            "£{noun,obj,genpl,nompl,case|čoggen ollu joŋaid} ja sarridat}"
            "£{noun,obj,genpl,nompl,case|čoggen ollu joŋaid ja sarridiid}</p>"
        )
        want = etree.fromstring(
            '<p><errormorphsyn errorinfo="noun,advl,gensg,locsg,case" '
            'correct="Ovddit geasi">Ovddit geasis</errormorphsyn> '
            '<errormorphsyn errorinfo="noun,obj,genpl,nompl,case" '
            'correct="čoggen ollu joŋaid ja sarridiid"><errormorphsyn '
            'errorinfo="noun,obj,genpl,nompl,case" correct="čoggen ollu '
            'joŋaid"><errorort errorinfo="verb,mono" correct="čoggen">'
            "čoaggen</errorort> ollu jokŋat</errormorphsyn> ja sarridat"
            "</errormorphsyn></p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_nested_markup9(self):
        in_elem = etree.fromstring(
            "<p>Bruk {{epoxi}${noun,cons|epoksy} lim}¢{noun,mix|epoksylim} "
            "med god kvalitet.</p>"
        )
        want = etree.fromstring(
            '<p>Bruk <errorortreal errorinfo="noun,mix" correct="epoksylim">'
            '<errorort errorinfo="noun,cons" correct="epoksy">epoxi'
            "</errorort> lim</errorortreal> med god kvalitet.</p>"
        )

        errormarkup.add_error_markup(in_elem)
        self.assertXmlEqual(in_elem, want)

    def test_process_text1(self):
        text = "{jne.}${adv,typo|jna.}"
        want = ["{jne.}", "${adv,typo|jna.}"]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text2(self):
        text = "{daesn'}${daesnie}"
        want = ["{daesn'}", "${daesnie}"]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text3(self):
        text = "{1]}§{Ij}"
        want = ["{1]}", "§{Ij}"]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text4(self):
        text = "{væ]keles}§{væjkeles}"
        want = ["{væ]keles}", "§{væjkeles}"]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text5(self):
        text = "{smávi-}§{smávit-}"
        want = ["{smávi-}", "§{smávit-}"]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text6(self):
        text = "{CD:t}§{CD:at}"
        want = ["{CD:t}", "§{CD:at}"]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text7(self):
        text = "{DNB-feaskáris}§{DnB-feaskáris}"
        want = ["{DNB-feaskáris}", "§{DnB-feaskáris}"]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text8(self):
        text = "{boade}§{boađe}"
        want = ["{boade}", "§{boađe}"]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text9(self):
        text = "{2005’as}§{2005:s}"
        want = ["{2005’as}", "§{2005:s}"]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text10(self):
        text = "{NSRii}§{NSR:ii}"
        want = ["{NSRii}", "§{NSR:ii}"]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text11(self):
        text = "{Nordkjosbotn'ii}§{Nordkjosbotnii}"
        want = ["{Nordkjosbotn'ii}", "§{Nordkjosbotnii}"]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text12(self):
        text = "{nourra}${a,meta|nuorra}"
        want = ["{nourra}", "${a,meta|nuorra}"]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text13(self):
        text = (
            "{Nieiddat leat nuorra}" "£{a,spred,nompl,nomsg,agr|Nieiddat leat nuorat}"
        )
        want = [
            "{Nieiddat leat nuorra}",
            "£{a,spred,nompl,nomsg,agr|Nieiddat leat nuorat}",
        ]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text14(self):
        text = "{riŋgen nieidda lusa}¥{x,pph|riŋgen niidii}"
        want = ["{riŋgen nieidda lusa}", "¥{x,pph|riŋgen niidii}"]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text15(self):
        text = "{ovtta}¥{num,redun| }"
        want = ["{ovtta}", "¥{num,redun| }"]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text16(self):
        text = "{dábálaš}€{adv,adj,der|dábálaččat}"
        want = ["{dábálaš}", "€{adv,adj,der|dábálaččat}"]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text17(self):
        text = "{ráhččamušaid}¢{noun,mix|rahčamušaid}"
        want = ["{ráhččamušaid}", "¢{noun,mix|rahčamušaid}"]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text18(self):
        text = (
            "gitta {Nordkjosbotn'ii}${Nordkjosbotnii} (mii lea ge "
            "{nordkjosbotn}${Nordkjosbotn} sámegillii? Muhtin, veahket mu!) "
            "gos"
        )
        want = [
            "gitta {Nordkjosbotn'ii}",
            "${Nordkjosbotnii}",
            " (mii lea ge {nordkjosbotn}",
            "${Nordkjosbotn}",
            " sámegillii? Muhtin, veahket mu!) gos",
        ]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text19(self):
        text = "gaskal {skuvla ohppiid}£{noun,attr,gensg,nomsg,case|skuvlla ohppiid} ja VSM."
        want = [
            "gaskal {skuvla ohppiid}",
            "£{noun,attr,gensg,nomsg,case|skuvlla ohppiid}",
            " ja VSM.",
        ]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text20(self):
        text = "- ruksesruonáčalmmehisvuohta lea sullii {8%:as}${acr,suf|8%:s}"
        want = ["- ruksesruonáčalmmehisvuohta lea sullii {8%:as}", "${acr,suf|8%:s}"]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text21(self):
        text = "( {nissonin}¢{noun,suf|nissoniin} dušše {0.6 %:s}£{0.6 %} )"
        want = [
            "( {nissonin}",
            "¢{noun,suf|nissoniin}",
            " dušše {0.6 %:s}",
            "£{0.6 %}",
            " )",
        ]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text22(self):
        text = (
            "(haploida) ja {njiŋŋalas}${noun,á|njiŋŋálas} {ságahuvvon}"
            "${verb,a|sagahuvvon} manneseallas (diploida)"
        )
        want = [
            "(haploida) ja {njiŋŋalas}",
            "${noun,á|njiŋŋálas}",
            " {ságahuvvon}",
            "${verb,a|sagahuvvon}",
            " manneseallas (diploida)",
        ]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text23(self):
        text = (
            "(gii oahpaha) {giinu}${x,notcmp|gii nu} manai {intiánalávlagat}"
            "${loan,conc|indiánalávlagat} {guovža-klána}"
            "${noun,cmp|guovžaklána} olbmuid"
        )
        want = [
            "(gii oahpaha) {giinu}",
            "${x,notcmp|gii nu}",
            " manai {intiánalávlagat}",
            "${loan,conc|indiánalávlagat}",
            " {guovža-klána}",
            "${noun,cmp|guovžaklána}",
            " olbmuid",
        ]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text24(self):
        text = (
            "{{šaddai}${verb,conc|šattai} ollu áššit}"
            "£{verb,fin,pl3prs,sg3prs,tense|šadde ollu áššit}"
        )
        want = [
            "{{šaddai}",
            "${verb,conc|šattai}",
            " ollu áššit}",
            "£{verb,fin,pl3prs,sg3prs,tense|šadde ollu áššit}",
        ]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text25(self):
        text = (
            "{guokte {ganddat}§{n,á|gánddat}}"
            "£{n,nump,gensg,nompl,case|guokte gándda}"
        )
        want = [
            "{guokte {ganddat}",
            "§{n,á|gánddat}",
            "}",
            "£{n,nump,gensg,nompl,case|guokte gándda}",
        ]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text26(self):
        text = (
            "{Nieiddat leat {nourra}${adj,meta|nuorra}}"
            "£{adj,spred,nompl,nomsg,agr|Nieiddat leat nuorat}"
        )
        want = [
            "{Nieiddat leat {nourra}",
            "${adj,meta|nuorra}",
            "}",
            "£{adj,spred,nompl,nomsg,agr|Nieiddat leat nuorat}",
        ]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text27(self):
        text = (
            "{leat {okta máná}£{n,spred,nomsg,gensg,case|okta mánná}}"
            "£{v,v,sg3prs,pl3prs,agr|lea okta mánná}"
        )
        want = [
            "{leat {okta máná}",
            "£{n,spred,nomsg,gensg,case|okta mánná}",
            "}",
            "£{v,v,sg3prs,pl3prs,agr|lea okta mánná}",
        ]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text28(self):
        text = (
            "heaitit {dáhkaluddame}${verb,a|dahkaluddame} ahte sis "
            "{máhkaš}¢{adv,á|mahkáš} livččii {makkarge}${adv,á|makkárge} "
            "politihkka, muhto rahpasit baicca muitalivčče {{makkar}"
            "${interr,á|makkár} soga}€{man soga} sii {ovddasttit}"
            "${verb,conc|ovddastit}."
        )
        want = [
            "heaitit {dáhkaluddame}",
            "${verb,a|dahkaluddame}",
            " ahte sis {máhkaš}",
            "¢{adv,á|mahkáš}",
            " livččii {makkarge}",
            "${adv,á|makkárge}",
            " politihkka, muhto rahpasit baicca muitalivčče {{makkar}",
            "${interr,á|makkár}",
            " soga}",
            "€{man soga}",
            " sii {ovddasttit}",
            "${verb,conc|ovddastit}",
            ".",
        ]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text31(self):
        text = (
            "{Ovddit geasis}£{noun,advl,gensg,locsg,case|Ovddit geasi} "
            "{{{čoaggen}${verb,mono|čoggen} ollu jokŋat}"
            "£{noun,obj,genpl,nompl,case|čoggen ollu joŋaid} ja sarridat}"
            "£{noun,obj,genpl,nompl,case|čoggen ollu joŋaid ja sarridiid}"
        )
        want = [
            "{Ovddit geasis}",
            "£{noun,advl,gensg,locsg,case|Ovddit geasi}",
            " {{{čoaggen}",
            "${verb,mono|čoggen}",
            " ollu jokŋat}",
            "£{noun,obj,genpl,nompl,case|čoggen ollu joŋaid}",
            " ja sarridat}",
            "£{noun,obj,genpl,nompl,case|čoggen ollu joŋaid ja sarridiid}",
        ]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text32(self):
        text = (
            "Bruk {{epoxi}${noun,cons|epoksy} lim}¢{noun,mix|epoksylim} med "
            "god kvalitet."
        )
        want = [
            "Bruk {{epoxi}",
            "${noun,cons|epoksy}",
            " lim}",
            "¢{noun,mix|epoksylim}",
            " med god kvalitet.",
        ]

        self.assertEqual(errormarkup.process_text(text), want)

    def test_process_text33(self):
        text = "a {error}" "£{fix1}///" "£{fix2}///" "¥{fix3}" " b."
        want = ["a {error}", "£{fix1}", "///", "£{fix2}", "///", "¥{fix3}", " b."]
        """
        <p>
            ja geas
            <errormulti>
                <errormorphsyn
                    errorinfo='noun,spred,nomsg,nompl,kongr'
                    correct='ii leat mangelágan čanastat'
                />
                <errormorphsyn
                    errorinfo='noun,spred,nompl,nomsg,kongr'
                    correct='eai leat mangelágan čanastagat'
                />
                ii leat mangelágan čanastagat
            </errormulti>
        </p>
        """
        self.assertEqual(errormarkup.process_text(text), want)

    def test_is_correction1(self):
        text = "${noun,cons|epoksy}"
        self.assertTrue(errormarkup.is_correction(text))

    def test_is_correction2(self):
        text = "Bruk {{epoxi}"
        self.assertTrue(not errormarkup.is_correction(text))

    def test_is_error_with_slash(self):
        text = "{aba/}"
        self.assertTrue(errormarkup.is_error(text))
