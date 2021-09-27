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
from parameterized import parameterized

from corpustools import errormarkup


class TestErrorMarkup(unittest.TestCase):
    """Test errormarkup functions."""

    @staticmethod
    def assert_xml_equal(got, want):
        """Check if two stringified xml snippets are equal"""
        got = etree.tostring(got, encoding="unicode")
        want = etree.tostring(want, encoding="unicode")
        checker = doctestcompare.LXMLOutputChecker()
        if not checker.check_output(want, got, 0):
            message = checker.output_difference(doctest.Example("", want), got, 0)
            raise AssertionError(message)

    @parameterized.expand(
        [
            (
                "errorlang_infinity",
                "<p>{molekylærbiologimi}∞{kal,bio}</p>",
                "<p><errorlang>molekylærbiologimi<correct>kal,bio</correct></errorlang></p>",
            ),
            (
                "error_parser_errorlang_infinity_with_new_lines",
                "<p>\n\n\n\n{molekylærbiologimi}∞{kal,bio}\n\n\n\n</p>",
                "<p><errorlang>molekylærbiologimi<correct>kal,bio</correct></errorlang></p>",
            ),
            (
                "quote_char",
                "<p>{”sjievnnijis”}${conc,vnn-vnnj|sjievnnjis}</p>",
                '<p><errorort>”sjievnnijis”<correct errorinfo="conc,vnn-vnnj">sjievnnjis</correct></errorort></p>',
            ),
            (
                "error_parser_errorort1",
                "<p>{jne.}${adv,typo|jna.}</p>",
                '<p><errorort>jne.<correct errorinfo="adv,typo">jna.</correct></errorort></p>',
            ),
            (
                "error_parser_error_morphsyn1",
                "<p>{Nieiddat leat nuorra}£{a,spred,nompl,nomsg,agr|Nieiddat leat nuorat}</p>",
                "<p><errormorphsyn>Nieiddat leat nuorra<correct "
                'errorinfo="a,spred,nompl,nomsg,agr">Nieiddat leat nuorat'
                "</correct></errormorphsyn></p>",
            ),
            (
                "error_parser_with_two_simple_errors",
                "<p>gitta {Nordkjosbotn'ii}${Nordkjosbotnii} (mii lea ge "
                "{nordkjosbotn}${Nordkjosbotn} sámegillii? Muhtin, veahket mu!) "
                "gos</p>",
                "<p>gitta "
                "<errorort>Nordkjosbotn'ii<correct>Nordkjosbotnii</correct></errorort> "
                "(mii lea ge "
                "<errorort>nordkjosbotn<correct>Nordkjosbotn</correct></errorort> "
                "sámegillii? Muhtin, veahket mu!) gos</p>",
            ),
            (
                "only_text_in_element",
                "<p>Muittán doložiid</p>",
                "<p>Muittán doložiid</p>",
            ),
            (
                "paragraph_character",
                "<p>Vuodoláhkaj §110a</p>",
                "<p>Vuodoláhkaj §110a</p>",
            ),
            (
                "errorort1",
                "<p>{jne.}${adv,typo|jna.}</p>",
                '<p><errorort>jne.<correct errorinfo="adv,typo">jna.</correct></errorort></p>',
            ),
            (
                "errorort2",
                "<p>{daesn'}${daesnie}</p>",
                "<p><errorort>daesn'<correct>daesnie</correct></errorort></p>",
            ),
            (
                "input_contains_slash",
                "<p>{magistter/}${loan,vowlat,e-a|magisttar}</p>",
                '<p><errorort>magistter/<correct errorinfo="loan,vowlat,e-a">'
                "magisttar</correct></errorort></p>",
            ),
            (
                "error_correct1",
                "<p>{1]}§{Ij}</p>",
                "<p><error>1]<correct>Ij</correct></error></p>",
            ),
            (
                "error_correct2",
                "<p>{væ]keles}§{væjkeles}</p>",
                "<p><error>væ]keles<correct>væjkeles</correct></error></p>",
            ),
            (
                "error_correct3",
                "<p>{smávi-}§{smávit-}</p>",
                "<p><error>smávi-<correct>smávit-</correct></error></p>",
            ),
            (
                "error_correct4",
                "<p>{CD:t}§{CD:at}</p>",
                "<p><error>CD:t<correct>CD:at</correct></error></p>",
            ),
            (
                "error_correct5",
                "<p>{DNB-feaskáris}§{DnB-feaskáris}</p>",
                "<p><error>DNB-feaskáris<correct>DnB-feaskáris</correct></error></p>",
            ),
            (
                "error_correct6",
                "<p>{boade}§{boađe}</p>",
                "<p><error>boade<correct>boađe</correct></error></p>",
            ),
            (
                "error_correct7",
                "<p>{2005’as}§{2005:s}</p>",
                "<p><error>2005’as<correct>2005:s</correct></error></p>",
            ),
            (
                "error_correct8",
                "<p>{NSRii}§{NSR:i}</p>",
                "<p><error>NSRii<correct>NSR:i</correct></error></p>",
            ),
            (
                "error_correct9",
                "<p>{Nordkjosbotn'ii}§{Nordkjosbotnii}</p>",
                "<p><error>Nordkjosbotn'ii<correct>Nordkjosbotnii</correct>"
                "</error></p>",
            ),
            (
                "errorort3",
                "<p>{nourra}${a,meta|nuorra}</p>",
                '<p><errorort>nourra<correct errorinfo="a,meta">nuorra</correct></errorort></p>',
            ),
            (
                "error_morphsyn1",
                "<p>{Nieiddat leat nuorra}£{a,spred,nompl,nomsg,agr|Nieiddat leat nuorat}</p>",
                "<p><errormorphsyn>Nieiddat leat nuorra"
                '<correct errorinfo="a,spred,nompl,nomsg,agr">Nieiddat leat '
                "nuorat</correct></errormorphsyn></p>",
            ),
            (
                "error_syn1",
                "<p>{riŋgen nieidda lusa}¥{x,pph|riŋgen niidii}</p>",
                '<p><errorsyn>riŋgen nieidda lusa<correct errorinfo="x,pph">'
                "riŋgen niidii</correct></errorsyn></p>",
            ),
            (
                "error_syn2",
                "<p>{ovtta}¥{num,redun| }</p>",
                '<p><errorsyn>ovtta<correct errorinfo="num,redun"></correct>'
                "</errorsyn></p>",
            ),
            (
                "error_lex1",
                "<p>{dábálaš}€{adv,adj,der|dábálaččat}</p>",
                '<p><errorlex>dábálaš<correct errorinfo="adv,adj,der">dábálaččat'
                "</correct></errorlex></p>",
            ),
            (
                "error_ortreal1",
                "<p>{ráhččamušaid}¢{noun,mix|rahčamušaid}</p>",
                '<p><errorortreal>ráhččamušaid<correct errorinfo="noun,mix">'
                "rahčamušaid</correct></errorortreal></p>",
            ),
            (
                "error_ortreal2",
                "<p>gitta {Nordkjosbotn'ii}${Nordkjosbotnii} (mii lea ge "
                "{nordkjosbotn}${Nordkjosbotn} sámegillii? Muhtin, veahket mu!) "
                "gos</p>",
                "<p>gitta <errorort>Nordkjosbotn'ii<correct>Nordkjosbotnii"
                "</correct></errorort> (mii lea ge <errorort>nordkjosbotn"
                "<correct>Nordkjosbotn</correct></errorort> sámegillii? "
                "Muhtin, veahket mu!) gos</p>",
            ),
            (
                "error_morphsyn2",
                "<p>Čáppa muohtaskulptuvrraid ráhkadeapmi VSM olggobealde lei "
                "maiddái ovttasbargu gaskal {skuvla ohppiid}£"
                "{noun,attr,gensg,nomsg,case|skuvlla ohppiid}"
                "ja VSM.</p>",
                "<p>Čáppa muohtaskulptuvrraid ráhkadeapmi VSM olggobealde lei "
                "maiddái ovttasbargu gaskal <errormorphsyn>skuvla ohppiid"
                '<correct errorinfo="noun,attr,gensg,nomsg,case">skuvlla ohppiid'
                "</correct></errormorphsyn> ja VSM.</p>",
            ),
            (
                "errorort4",
                "<p>- ruksesruonáčalmmehisvuohta lea sullii "
                "{8%:as}${acr,suf|8%:s}</p>",
                "<p>- ruksesruonáčalmmehisvuohta lea sullii <errorort>8%:as"
                '<correct errorinfo="acr,suf">8%:s</correct></errorort></p>',
            ),
            (
                "error_ortreal3",
                "<p>( {nissonin}¢{noun,suf|nissoniin} dušše {0.6 %:s}£{0.6 %} )</p>",
                '<p>( <errorortreal>nissonin<correct errorinfo="noun,suf">'
                "nissoniin</correct></errorortreal> dušše <errormorphsyn>0.6 %:s"
                "<correct>0.6 %</correct></errormorphsyn> )</p>",
            ),
            (
                "errorort5",
                "<p>(haploida) ja {njiŋŋalas}${noun,á|njiŋŋálas} {ságahuvvon}"
                "${verb,a|sagahuvvon} manneseallas (diploida)</p>",
                '<p>(haploida) ja <errorort>njiŋŋalas<correct errorinfo="noun,á">'
                "njiŋŋálas</correct></errorort> <errorort>ságahuvvon"
                '<correct errorinfo="verb,a">sagahuvvon</correct></errorort> '
                "manneseallas (diploida)</p>",
            ),
            (
                "errorort6",
                "<p>(gii oahpaha) {giinu}${x,notcmp|gii nu} manai {intiánalávlagat}"
                "${loan,conc|indiánalávlagat} {guovža-klána}${noun,cmp|guovžaklána} "
                "olbmuid</p>",
                '<p>(gii oahpaha) <errorort>giinu<correct errorinfo="x,notcmp">'
                "gii nu</correct></errorort> manai <errorort>intiánalávlagat"
                '<correct errorinfo="loan,conc">indiánalávlagat</correct>'
                '</errorort> <errorort>guovža-klána<correct errorinfo="noun,cmp">'
                "guovžaklána</correct></errorort> olbmuid</p>",
            ),
            (
                "error_format",
                "<p>{{A  B}‰{notspace|A B}  C}‰{notspace|A B C}</p>",
                "<p>"
                "<errorformat>"
                "<errorformat>"
                'A  B<correct errorinfo="notspace">A B</correct></errorformat>'
                '  C<correct errorinfo="notspace">A B C</correct></errorformat>'
                "</p>",
            ),
            (
                "preserve_space_at_end_of_sentence",
                "<p>buvttadeaddji Anstein {Mikkelsens}${typo|Mikkelsen} lea "
                "ráhkadan. </p>",
                '<p>buvttadeaddji Anstein <errorort>Mikkelsens<correct errorinfo="typo">Mikkelsen</correct></errorort> lea ráhkadan. </p>',
            ),
            (
                "place_error_elements_before_old_element1",
                "<p>buvttadeaddji Anstein {Mikkelsens}${typo|Mikkelsen} lea "
                "ráhkadan. {bálkkášumi}${vowlat,á-a|bálkkašumi} miessemánu. <span "
                'type="quote" xml:lang="eng">«Best Shorts Competition»</span></p>',
                "<p>buvttadeaddji Anstein <errorort>Mikkelsens"
                '<correct errorinfo="typo">Mikkelsen</correct></errorort> lea ráhkadan. '
                '<errorort>bálkkášumi<correct errorinfo="vowlat,á-a">bálkkašumi</correct></errorort>'
                ' miessemánu. <span type="quote" xml:lang="eng">«Best Shorts '
                "Competition»</span></p>",
            ),
            (
                "place_error_elements_before_old_element2",
                "<p>{Mikkelsens}${typo|Mikkelsen} lea ráhkadan. "
                "{bálkkášumi}${vowlat,á-a|bálkkašumi} miessemánu. "
                '<span type="quote" xml:lang="eng">'
                "«Best Shorts Competition»</span></p>",
                '<p><errorort>Mikkelsens<correct errorinfo="typo">Mikkelsen</correct></errorort> lea ráhkadan. <errorort>bálkkášumi<correct errorinfo="vowlat,á-a">bálkkašumi</correct></errorort> miessemánu. <span type="quote" xml:lang="eng">«Best Shorts Competition»</span></p>',
            ),
            (
                "place_error_element_after_old_element",
                '<p>I 1864 ga han ut boka <span type="quote" xml:lang="swe">'
                '"Fornuftigt Madstel"</span>. {Asbjørsen}${prop,typo|Asbjørnsen} '
                "døde 5. januar 1885, nesten 73 år gammel.</p>",
                '<p>I 1864 ga han ut boka <span type="quote" xml:lang="swe">'
                '"Fornuftigt Madstel"</span>. <errorort>Asbjørsen'
                '<correct errorinfo="prop,typo">Asbjørnsen</correct></errorort> '
                "døde 5. januar 1885, nesten 73 år gammel.</p>",
            ),
            (
                "place_error_element_before_and_after_old_element",
                "<p>buvttadeaddji Anstein {Mikkelsens}${typo|Mikkelsen} lea "
                'ráhkadan. <span type="quote" xml:lang="eng">«Best Shorts '
                "Competition»</span> {bálkkášumi}${vowlat,á-a|bálkkašumi} "
                "miessemánu.</p>",
                "<p>buvttadeaddji Anstein <errorort>Mikkelsens"
                '<correct errorinfo="typo">Mikkelsen</correct></errorort> lea '
                'ráhkadan. <span type="quote" xml:lang="eng">«Best Shorts '
                "Competition»</span> <errorort>bálkkášumi"
                '<correct errorinfo="vowlat,á-a">bálkkašumi</correct></errorort> '
                "miessemánu.</p>",
            ),
            (
                "markup3Levels",
                "<p>buvttadeaddji Anstein <errorort>Mikkelsens<correct "
                'errorinfo="typo">Mikkelsen</correct></errorort> lea ráhkadan. '
                '<span type="quote" xml:lang="eng">«Best Shorts Competition»'
                '</span> <errorort>bálkkášumi<correct errorinfo="vowlat,á-a">'
                "bálkkašumi</correct></errorort> miessemánu. <em>buvttadeaddji "
                "Anstein {Mikkelsens}${typo|Mikkelsen} lea ráhkadan. <span "
                'type="quote" xml:lang="eng">«Best Shorts Competition»</span> '
                "{bálkkášumi}${vowlat,á-a|bálkkašumi} miessemánu.</em></p>",
                "<p>buvttadeaddji Anstein <errorort>Mikkelsens<correct "
                'errorinfo="typo">Mikkelsen</correct></errorort> lea ráhkadan. '
                '<span type="quote" xml:lang="eng">«Best Shorts Competition»'
                '</span> <errorort>bálkkášumi<correct errorinfo="vowlat,á-a">'
                "bálkkašumi</correct></errorort> miessemánu. <em>buvttadeaddji "
                'Anstein <errorort>Mikkelsens<correct errorinfo="typo">Mikkelsen'
                '</correct></errorort> lea ráhkadan. <span type="quote" '
                'xml:lang="eng">«Best Shorts Competition»</span> <errorort>'
                'bálkkášumi<correct errorinfo="vowlat,á-a">bálkkašumi</correct>'
                "</errorort> miessemánu.</em></p>",
            ),
            (
                "inline multiple corrections",
                "<p>{leimme}£{leimmet///leat}</p>",
                "<p><errormorphsyn>leimme"
                "<correct>leimmet</correct>"
                "<correct>leat</correct>"
                "</errormorphsyn></p>",
            ),
        ]
    )
    def test_add_error_markup(self, name, in_string, want_string):
        """Test plain errormarkup."""
        in_elem = etree.fromstring(in_string)
        want = etree.fromstring(want_string)

        errormarkup.add_error_markup(in_elem)
        self.assert_xml_equal(in_elem, want)

    # Nested markup
    @parameterized.expand(
        [
            (
                "<p>{{šaddai}${verb,conc|šattai} ollu áššit}£{verb,fin,pl3prs,sg3prs,tense|šadde ollu áššit}</p>",
                '<p><errormorphsyn><errorort>šaddai<correct errorinfo="verb,conc">'
                "šattai</correct></errorort> ollu áššit<correct "
                'errorinfo="verb,fin,pl3prs,sg3prs,tense">šadde ollu áššit'
                "</correct></errormorphsyn></p>",
            ),
            (
                "<p>{guokte {ganddat}§{n,á|gánddat}}£{n,nump,gensg,nompl,case|guokte gándda}</p>",
                '<p><errormorphsyn>guokte <error>ganddat<correct errorinfo="n,á">'
                "gánddat</correct></error><correct "
                'errorinfo="n,nump,gensg,nompl,case">guokte gándda</correct>'
                "</errormorphsyn></p>",
            ),
            (
                "<p>{Nieiddat leat {nourra}${adj,meta|nuorra}}"
                "£{adj,spred,nompl,nomsg,agr|Nieiddat leat nuorat}</p>",
                "<p><errormorphsyn>Nieiddat leat <errorort>nourra<correct "
                'errorinfo="adj,meta">nuorra</correct></errorort>'
                '<correct errorinfo="adj,spred,nompl,nomsg,agr">Nieiddat leat '
                "nuorat</correct></errormorphsyn></p>",
            ),
            (
                "<p>{leat {okta máná}£{n,spred,nomsg,gensg,case|okta mánná}}"
                "£{v,v,sg3prs,pl3prs,agr|lea okta mánná}</p>",
                "<p><errormorphsyn>leat <errormorphsyn>okta máná<correct "
                'errorinfo="n,spred,nomsg,gensg,case">okta mánná</correct>'
                '</errormorphsyn><correct errorinfo="v,v,sg3prs,pl3prs,agr">'
                "lea okta mánná</correct></errormorphsyn></p>",
            ),
            (
                "<p>heaitit {dáhkaluddame}${verb,a|dahkaluddame} ahte sis "
                "{máhkaš}¢{adv,á|mahkáš} livččii {makkarge}${adv,á|makkárge} "
                "politihkka, muhto rahpasit baicca muitalivčče {{makkar}"
                "${interr,á|makkár} soga}€{man soga} sii {ovddasttit}"
                "${verb,conc|ovddastit}.</p>",
                '<p>heaitit <errorort>dáhkaluddame<correct errorinfo="verb,a">'
                "dahkaluddame</correct></errorort> ahte sis <errorortreal>"
                'máhkaš<correct errorinfo="adv,á">mahkáš</correct></errorortreal>'
                'livččii <errorort>makkarge<correct errorinfo="adv,á">makkárge'
                "</correct></errorort> politihkka, muhto rahpasit baicca "
                "muitalivčče <errorlex><errorort>makkar<correct "
                'errorinfo="interr,á">makkár</correct></errorort> soga<correct>'
                "man soga</correct></errorlex> sii <errorort>ovddasttit"
                '<correct errorinfo="verb,conc">ovddastit</correct></errorort>.</p>',
            ),
            (
                "<p>{{Bearpmahat}${noun,svow|Bearpmehat} "
                "{earuha}€{verb,v,w|sirre}}£{verb,fin,pl3prs,sg3prs,agr|Bearpmehat"
                " sirrejit} uskki ja loaiddu.</p>",
                "<p><errormorphsyn><errorort>Bearpmahat<correct "
                'errorinfo="noun,svow">Bearpmehat</correct></errorort><errorlex>'
                'earuha<correct errorinfo="verb,v,w">sirre</correct></errorlex>'
                '<correct errorinfo="verb,fin,pl3prs,sg3prs,agr">Bearpmehat '
                "sirrejit</correct></errormorphsyn> uskki ja loaiddu.</p>",
            ),
            (
                "<p>Mirja ja Line leaba {{gulahallan olbmožat}"
                "¢{noun,cmp|gulahallanolbmožat}}€{gulahallanolbmot}</p>",
                "<p>Mirja ja Line leaba <errorlex><errorortreal>gulahallan "
                'olbmožat<correct errorinfo="noun,cmp">gulahallanolbmožat'
                "</correct></errorortreal><correct>gulahallanolbmot</correct>"
                "</errorlex></p>",
            ),
            (
                "<p>{Ovddit geasis}£{noun,advl,gensg,locsg,case|Ovddit geasi} "
                "{{{čoaggen}${verb,mono|čoggen} ollu jokŋat}"
                "£{noun,obj,genpl,nompl,case|čoggen ollu joŋaid} ja sarridat}"
                "£{noun,obj,genpl,nompl,case|čoggen ollu joŋaid ja sarridiid}</p>",
                "<p><errormorphsyn>Ovddit geasis<correct "
                'errorinfo="noun,advl,gensg,locsg,case">Ovddit geasi</correct>'
                "</errormorphsyn><errormorphsyn><errormorphsyn><errorort>čoaggen"
                '<correct errorinfo="verb,mono">čoggen</correct></errorort> '
                'ollu jokŋat<correct errorinfo="noun,obj,genpl,nompl,case">'
                "čoggen ollu joŋaid</correct></errormorphsyn> ja sarridat"
                '<correct errorinfo="noun,obj,genpl,nompl,case">čoggen ollu '
                "joŋaid ja sarridiid</correct></errormorphsyn></p>",
            ),
            (
                "<p>Bruk {{epoxi}${noun,cons|epoksy} lim}¢{noun,mix|epoksylim} "
                "med god kvalitet.</p>",
                "<p>Bruk <errorortreal><errorort>epoxi"
                '<correct errorinfo="noun,cons">epoksy</correct></errorort> lim'
                '<correct errorinfo="noun,mix">epoksylim</correct></errorortreal> '
                "med god kvalitet.</p>",
            ),
        ]
    )
    def test_nested_markup(self, in_string, want_string):
        in_elem = etree.fromstring(in_string)
        want = etree.fromstring(want_string)

        errormarkup.add_error_markup(in_elem)
        self.assert_xml_equal(in_elem, want)

