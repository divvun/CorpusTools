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
#   Copyright © 2013-2025 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Tests for error_annotated_sentence module, ported from Rust tests."""

import pytest
from lxml import etree

from corpustools.error_annotated_sentence import (
    ErrorAnnotatedSentence,
    parse_markup_to_sentence,
)
from corpustools.error_markup import ErrorMarkup
from corpustools.error_types import ErrorType


def test_sentence_no_errors():
    """Test creating a sentence with no errors."""
    sentence = ErrorAnnotatedSentence(text="Muittán doložiid")

    assert sentence.text == "Muittán doložiid"
    assert sentence.error_count() == 0


def test_sentence_with_errors():
    """Test adding errors to a sentence."""
    error = ErrorMarkup(
        form="čohke",
        start=0,
        end=6,
        errortype=ErrorType.ERRORORTREAL,
        suggestions=["čohkke"],
    )

    sentence = ErrorAnnotatedSentence(text="čohke is wrong")
    sentence.errors.append(error)

    assert sentence.error_count() == 1


@pytest.mark.parametrize(
    ("name", "error_sentence", "error_string", "expected_xml"),
    [
        (
            "errorlang_infinity",
            "{molekylærbiologimi}∞{kal,bio}",
            "molekylærbiologimi",
            "<p><errorlang>molekylærbiologimi<correct>kal,bio</correct></errorlang></p>",
        ),
        (
            "quote_char",
            "{”sjievnnijis”}${conc,vnn-vnnj|”sjievnnjis”}",
            "”sjievnnijis”",
            '<p><errorort>”sjievnnijis”<correct errorinfo="conc,vnn-vnnj">sjievnnjis</correct></errorort></p>',
        ),
        (
            "only_text_in_element",
            "Muittán doložiid",
            "Muittán doložiid",
            "<p>Muittán doložiid</p>",
        ),
        (
            "paragraph_character",
            "Vuodoláhkaj §110a",
            "Vuodoláhkaj §110a",
            "<p>Vuodoláhkaj §110a</p>",
        ),
        (
            "errorort1",
            "{jne.}${adv,typo|jna.}",
            "jne.",
            '<p><errorort>jne.<correct errorinfo="adv,typo">jna.</correct></errorort></p>',
        ),
        (
            "errorort2",
            "{daesn'}${daesnie}",
            "daesn'",
            "<p><errorort>daesn'<correct>daesnie</correct></errorort></p>",
        ),
        (
            "input_contains_slash",
            "{magistter/}${loan,vowlat,e-a|magisttar/}",
            "magistter/",
            '<p><errorort>magistter/<correct errorinfo="loan,vowlat,e-a">'
            "magisttar/</correct></errorort></p>",
        ),
        (
            "error_correct1",
            "{1]}§{Ij}",
            "1]",
            "<p><error>1]<correct>Ij</correct></error></p>",
        ),
        (
            "error_correct2",
            "{væ]keles}§{væjkeles}",
            "væ]keles",
            "<p><error>væ]keles<correct>væjkeles</correct></error></p>",
        ),
        (
            "error_correct3",
            "{smávi-}§{smávit-}",
            "smávi-",
            "<p><error>smávi-<correct>smávit-</correct></error></p>",
        ),
        (
            "error_correct4",
            "{CD:t}§{CD:at}",
            "CD:t",
            "<p><error>CD:t<correct>CD:at</correct></error></p>",
        ),
        (
            "error_correct5",
            "{DNB-feaskáris}§{DnB-feaskáris}",
            "DNB-feaskáris",
            "<p><error>DNB-feaskáris<correct>DnB-feaskáris</correct></error></p>",
        ),
        (
            "error_correct6",
            "{boade}§{boađe}",
            "boade",
            "<p><error>boade<correct>boađe</correct></error></p>",
        ),
        (
            "error_correct7",
            "{2005’as}§{2005:s}",
            "2005’as",
            "<p><error>2005’as<correct>2005:s</correct></error></p>",
        ),
        (
            "error_correct8",
            "{NSRii}§{NSR:i}",
            "NSRii",
            "<p><error>NSRii<correct>NSR:i</correct></error></p>",
        ),
        (
            "error_correct9",
            "{Nordkjosbotn'ii}§{Nordkjosbotnii}",
            "Nordkjosbotn'ii",
            "<p><error>Nordkjosbotn'ii<correct>Nordkjosbotnii</correct></error></p>",
        ),
        (
            "errorort3",
            "{nourra}${a,meta|nuorra}",
            "nourra",
            '<p><errorort>nourra<correct errorinfo="a,meta">nuorra</correct>'
            "</errorort></p>",
        ),
        (
            "error_morphsyn1",
            "{Nieiddat leat nuorra}£{a,spred,nompl,nomsg,agr|Nieiddat leat nuorat}",
            "Nieiddat leat nuorra",
            "<p><errormorphsyn>Nieiddat leat nuorra"
            '<correct errorinfo="a,spred,nompl,nomsg,agr">Nieiddat leat '
            "nuorat</correct></errormorphsyn></p>",
        ),
        (
            "error_syn1",
            "{riŋgen nieidda lusa}¥{x,pph|riŋgen niidii}",
            "riŋgen nieidda lusa",
            '<p><errorsyn>riŋgen nieidda lusa<correct errorinfo="x,pph">'
            "riŋgen niidii</correct></errorsyn></p>",
        ),
        (
            "error_syn2",
            "{ovtta}¥{num,redun| }",
            "ovtta",
            '<p><errorsyn>ovtta<correct errorinfo="num,redun"></correct>'
            "</errorsyn></p>",
        ),
        (
            "error_lex1",
            "{dábálaš}€{adv,adj,der|dábálaččat}",
            "dábálaš",
            '<p><errorlex>dábálaš<correct errorinfo="adv,adj,der">dábálaččat'
            "</correct></errorlex></p>",
        ),
        (
            "error_ortreal1",
            "{ráhččamušaid}¢{noun,mix|rahčamušaid}",
            "ráhččamušaid",
            '<p><errorortreal>ráhččamušaid<correct errorinfo="noun,mix">'
            "rahčamušaid</correct></errorortreal></p>",
        ),
        (
            "error_ortreal2",
            "gitta {Nordkjosbotn'ii}${Nordkjosbotnii} (mii lea ge "
            "{nordkjosbotn}${Nordkjosbotn} sámegillii? Muhtin, veahket mu!) "
            "gos",
            "gitta Nordkjosbotn'ii (mii lea ge nordkjosbotn sámegillii? "
            "Muhtin, veahket mu!) gos",
            "<p>gitta <errorort>Nordkjosbotn'ii<correct>Nordkjosbotnii"
            "</correct></errorort> (mii lea ge <errorort>nordkjosbotn"
            "<correct>Nordkjosbotn</correct></errorort> sámegillii? "
            "Muhtin, veahket mu!) gos</p>",
        ),
        (
            "error_morphsyn2",
            "Čáppa muohtaskulptuvrraid ráhkadeapmi VSM olggobealde lei "
            "maiddái ovttasbargu gaskal {skuvla ohppiid}£"
            "{noun,attr,gensg,nomsg,case|skuvlla ohppiid} "
            "ja VSM.",
            "Čáppa muohtaskulptuvrraid ráhkadeapmi VSM olggobealde lei "
            "maiddái ovttasbargu gaskal skuvla ohppiid ja VSM.",
            "<p>Čáppa muohtaskulptuvrraid ráhkadeapmi VSM olggobealde lei "
            "maiddái ovttasbargu gaskal <errormorphsyn>skuvla ohppiid"
            '<correct errorinfo="noun,attr,gensg,nomsg,case">skuvlla ohppiid'
            "</correct></errormorphsyn> ja VSM.</p>",
        ),
        (
            "errorort4",
            "- ruksesruonáčalmmehisvuohta lea sullii {8%:as}${acr,suf|8%:s}",
            "- ruksesruonáčalmmehisvuohta lea sullii 8%:as",
            "<p>- ruksesruonáčalmmehisvuohta lea sullii <errorort>8%:as"
            '<correct errorinfo="acr,suf">8%:s</correct></errorort></p>',
        ),
        (
            "error_ortreal3",
            "( {nissonin}¢{noun,suf|nissoniin} dušše {0.6 %:s}£{0.6 %} )",
            "( nissonin dušše 0.6 %:s )",
            '<p>( <errorortreal>nissonin<correct errorinfo="noun,suf">'
            "nissoniin</correct></errorortreal> dušše <errormorphsyn>0.6 %:s"
            "<correct>0.6 %</correct></errormorphsyn> )</p>",
        ),
        (
            "errorort5",
            "(haploida) ja {njiŋŋalas}${noun,á|njiŋŋálas} {ságahuvvon}"
            "${verb,a|sagahuvvon} manneseallas (diploida)",
            "(haploida) ja njiŋŋalas ságahuvvon manneseallas (diploida)",
            '<p>(haploida) ja <errorort>njiŋŋalas<correct errorinfo="noun,á">'
            "njiŋŋálas</correct></errorort> <errorort>ságahuvvon"
            '<correct errorinfo="verb,a">sagahuvvon</correct></errorort> '
            "manneseallas (diploida)</p>",
        ),
        (
            "errorort6",
            "(gii oahpaha) {giinu}${x,notcmp|gii nu} manai {intiánalávlagat}"
            "${loan,conc|indiánalávlagat} {guovža-klána}${noun,cmp|guovžaklána} "
            "olbmuid",
            "(gii oahpaha) giinu manai intiánalávlagat guovža-klána olbmuid",
            '<p>(gii oahpaha) <errorort>giinu<correct errorinfo="x,notcmp">'
            "gii nu</correct></errorort> manai <errorort>intiánalávlagat"
            '<correct errorinfo="loan,conc">indiánalávlagat</correct>'
            '</errorort> <errorort>guovža-klána<correct errorinfo="noun,cmp">'
            "guovžaklána</correct></errorort> olbmuid</p>",
        ),
        (
            "error_format",
            "{{A  B}‰{notspace|A B}  C}‰{notspace|A B C}",
            "A  B  C",
            "<p>"
            "<errorformat>"
            "<errorformat>"
            'A  B<correct errorinfo="notspace">A B</correct></errorformat>'
            '  C<correct errorinfo="notspace">A B C</correct></errorformat>'
            "</p>",
        ),
        (
            "preserve_space_at_end_of_sentence",
            "buvttadeaddji Anstein {Mikkelsens}${typo|Mikkelsen} lea ráhkadan. ",
            "buvttadeaddji Anstein Mikkelsens lea ráhkadan. ",
            '<p>buvttadeaddji Anstein <errorort>Mikkelsens<correct errorinfo="typo">'
            "Mikkelsen</correct></errorort> lea ráhkadan. </p>",
        ),
        (
            "errorlang_and_errorort",
            "I 1864 ga han ut boka "
            '{"Fornuftigt Madstel"}∞{swe|}. {Asbjørsen}${prop,typo|Asbjørnsen} '
            "døde 5. januar 1885, nesten 73 år gammel.",
            'I 1864 ga han ut boka "Fornuftigt Madstel". Asbjørsen '
            "døde 5. januar 1885, nesten 73 år gammel.",
            '<p>I 1864 ga han ut boka <errorlang xml:lang="swe">'
            '"Fornuftigt Madstel"</errorlang>. <errorort>Asbjørsen'
            '<correct errorinfo="prop,typo">Asbjørnsen</correct></errorort> '
            "døde 5. januar 1885, nesten 73 år gammel.</p>",
        ),
        (
            "place_error_element_before_and_after_old_element",
            "buvttadeaddji Anstein {Mikkelsens}${typo|Mikkelsen} lea ráhkadan. "
            "{«Best Shorts Competition»}∞{eng|} {bálkkášumi}${vowlat,á-a|bálkkašumi} "
            "miessemánu.",
            "buvttadeaddji Anstein Mikkelsens lea ráhkadan. "
            "«Best Shorts Competition» bálkkášumi "
            "miessemánu.",
            "<p>buvttadeaddji Anstein <errorort>Mikkelsens"
            '<correct errorinfo="typo">Mikkelsen</correct></errorort> lea '
            'ráhkadan. <errorlang xml:lang="eng">«Best Shorts»</errorlang> '
            '<errorort>bálkkášumi<correct errorinfo="vowlat,á-a">bálkkašumi</correct>'
            "</errorort> miessemánu.</p>",
        ),
        (
            "inline multiple corrections",
            "{leimme}£{leimmet///leat}",
            "leimme",
            "<p><errormorphsyn>leimme"
            "<correct>leimmet</correct>"
            "<correct>leat</correct>"
            "</errormorphsyn></p>",
        ),
        (
            "nested errormorphsyn/errorort",
            "{{šaddai}${verb,conc|šattai} ollu áššit}£{verb,fin,pl3prs,sg3prs,tense|"
            "šadde ollu áššit}",
            "šaddai ollu áššit",
            '<p><errormorphsyn><errorort>šaddai<correct errorinfo="verb,conc">'
            "šattai</correct></errorort> ollu áššit<correct "
            'errorinfo="verb,fin,pl3prs,sg3prs,tense">šadde ollu áššit'
            "</correct></errormorphsyn></p>",
        ),
        (
            "nested errormorphsyn/error",
            "{guokte {ganddat}§{n,á|gánddat}}£{n,nump,gensg,nompl,case|guokte gándda}",
            "guokte ganddat",
            '<p><errormorphsyn>guokte <error>ganddat<correct errorinfo="n,á">'
            "gánddat</correct></error><correct "
            'errorinfo="n,nump,gensg,nompl,case">guokte gándda</correct>'
            "</errormorphsyn></p>",
        ),
        (
            "nested errormorphsyn/errorort 2",
            "{Nieiddat leat {nourra}${adj,meta|nuorra}}"
            "£{adj,spred,nompl,nomsg,agr|Nieiddat leat nuorat}",
            "Nieiddat leat nourra",
            "<p><errormorphsyn>Nieiddat leat <errorort>nourra<correct "
            'errorinfo="adj,meta">nuorra</correct></errorort>'
            '<correct errorinfo="adj,spred,nompl,nomsg,agr">Nieiddat leat '
            "nuorat</correct></errormorphsyn></p>",
        ),
        (
            "nested errormorphsyn/errormorphsyn",
            "{leat {okta máná}£{n,spred,nomsg,gensg,case|okta mánná}}"
            "£{v,v,sg3prs,pl3prs,agr|lea okta mánná}",
            "leat okta máná",
            "<p><errormorphsyn>leat <errormorphsyn>okta máná<correct "
            'errorinfo="n,spred,nomsg,gensg,case">okta mánná</correct>'
            '</errormorphsyn><correct errorinfo="v,v,sg3prs,pl3prs,agr">'
            "lea okta mánná</correct></errormorphsyn></p>",
        ),
        (
            "complex nested errors",
            "heaitit {dáhkaluddame}${verb,a|dahkaluddame} ahte sis "
            "{máhkaš}¢{adv,á|mahkáš} livččii {makkarge}${adv,á|makkárge} "
            "politihkka, muhto rahpasit baicca muitalivčče {{makkar}"
            "${interr,á|makkár} soga}€{man soga} sii {ovddasttit}"
            "${verb,conc|ovddastit}.",
            "heaitit dáhkaluddame ahte sis máhkaš livččii makkarge "
            "politihkka, muhto rahpasit baicca muitalivčče makkar soga sii ovddasttit.",
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
            "nested errormorphsyn/errorort/errorlex",
            "{{Bearpmahat}${noun,svow|Bearpmehat} "
            "{earuha}€{verb,v,w|sirre}}£{verb,fin,pl3prs,sg3prs,agr|Bearpmehat"
            " sirrejit} uskki ja loaiddu.",
            "Bearpmahat earuha uskki ja loaiddu.",
            "<p><errormorphsyn><errorort>Bearpmahat<correct "
            'errorinfo="noun,svow">Bearpmehat</correct></errorort><errorlex>'
            'earuha<correct errorinfo="verb,v,w">sirre</correct></errorlex>'
            '<correct errorinfo="verb,fin,pl3prs,sg3prs,agr">Bearpmehat '
            "sirrejit</correct></errormorphsyn> uskki ja loaiddu.</p>",
        ),
        (
            "nested errorlex/errorortreal",
            "Mirja ja Line leaba {{gulahallan olbmožat}"
            "¢{noun,cmp|gulahallanolbmožat}}€{gulahallanolbmot}",
            "Mirja ja Line leaba gulahallan olbmožat",
            "<p>Mirja ja Line leaba <errorlex><errorortreal>gulahallan "
            'olbmožat<correct errorinfo="noun,cmp">gulahallanolbmožat'
            "</correct></errorortreal><correct>gulahallanolbmot</correct>"
            "</errorlex></p>",
        ),
        (
            "multiple nested errormorphsyn/errorort",
            "{Ovddit geasis}£{noun,advl,gensg,locsg,case|Ovddit geasi} "
            "{{{čoaggen}${verb,mono|čoggen} ollu jokŋat}"
            "£{noun,obj,genpl,nompl,case|čoggen ollu joŋaid} ja sarridat}"
            "£{noun,obj,genpl,nompl,case|čoggen ollu joŋaid ja sarridiid}",
            "Ovddit geasis čoaggen ollu jokŋat ja sarridat",
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
            "nested errorortreal/errorort",
            "Bruk {{epoxi}${noun,cons|epoksy} lim}¢{noun,mix|epoksylim} "
            "med god kvalitet.",
            "Bruk epoxi lim med god kvalitet.",
            "<p>Bruk <errorortreal><errorort>epoxi"
            '<correct errorinfo="noun,cons">epoksy</correct></errorort> lim'
            '<correct errorinfo="noun,mix">epoksylim</correct></errorortreal> '
            "med god kvalitet.</p>",
        ),
    ],
)
def test_to_errormarkupxml(
    name: str, error_sentence: str, error_string: str, expected_xml: str
):
    """Test plain errormarkup."""
    error_annotated_sentence = parse_markup_to_sentence(error_sentence)
    result_elem = error_annotated_sentence.to_errormarkupxml()
    result_xml = etree.tostring(result_elem, encoding="unicode")
    assert error_annotated_sentence.text == error_string
    assert (
        result_xml == expected_xml
        or f"Test '{name}' failed: got {result_xml}, expected {expected_xml}"
    )
