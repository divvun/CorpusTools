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


def test_add_error():
    """Test the add_error method."""
    sentence = ErrorAnnotatedSentence(text="some text")
    assert sentence.error_count() == 0

    sentence.errors.append(
        ErrorMarkup(
            form="error",
            start=0,
            end=5,
            errortype=ErrorType.ERROR,
        )
    )

    assert sentence.error_count() == 1


def test_multiple_errors():
    """Test adding multiple errors to a sentence."""
    sentence = ErrorAnnotatedSentence(text="text with errors")

    error1 = ErrorMarkup("error1", 0, 6, ErrorType.ERRORORT)
    error2 = ErrorMarkup("error2", 7, 13, ErrorType.ERRORSYN)

    sentence.errors.append(error1)
    sentence.errors.append(error2)

    assert sentence.error_count() == 2
    assert sentence.errors[0].form == "error1"
    assert sentence.errors[1].form == "error2"


def test_sentence_with_two_simple_errors():
    """Test sentence with two simple errors.

    Input: gitta {Nordkjosbotn'ii}${Nordkjosbotnii} (mii lea ge
    {nordkjosbotn}${Nordkjosbotn} sámegillii? Muhtin, veahket mu!) gos
    """
    text = "gitta Nordkjosbotn'ii (mii lea ge nordkjosbotn sámegillii? Muhtin, veahket mu!) gos"

    error1 = ErrorMarkup(
        form="Nordkjosbotn'ii",
        start=6,
        end=6 + len("Nordkjosbotn'ii"),
        errortype=ErrorType.ERRORORT,
        suggestions=["Nordkjosbotnii"],
    )

    error2 = ErrorMarkup(
        form="nordkjosbotn",
        start=35,
        end=35 + len("nordkjosbotn"),
        errortype=ErrorType.ERRORORT,
        suggestions=["Nordkjosbotn"],
    )

    sentence = ErrorAnnotatedSentence(text)
    sentence.errors.append(error1)
    sentence.errors.append(error2)

    assert sentence.error_count() == 2
    assert sentence.errors[0].suggestions == ["Nordkjosbotnii"]
    assert sentence.errors[1].suggestions == ["Nordkjosbotn"]


def test_paragraph_character():
    """Test that § character is not confused with error markup.

    Input: Vuodoláhkaj §110a
    """
    sentence = ErrorAnnotatedSentence("Vuodoláhkaj §110a")

    assert sentence.error_count() == 0
    assert sentence.text == "Vuodoláhkaj §110a"


def test_sentence_with_multiple_errors_different_types():
    """Test sentence with multiple errors of different types.

    Input: ( {nissonin}¢{noun,suf|nissoniin} dušše {0.6 %:s}£{0.6 %} )
    """
    error1 = ErrorMarkup(
        form="nissonin",
        start=2,
        end=2 + len("nissonin"),
        errortype=ErrorType.ERRORORTREAL,
        suggestions=["nissoniin"],
        errorinfo="noun,suf",
    )

    error2 = ErrorMarkup(
        form="0.6 %:s",
        start=2 + len("nissonin") + 7,
        end=2 + len("nissonin") + 7 + len("0.6 %:s"),
        errortype=ErrorType.ERRORMORPHSYN,
        suggestions=["0.6 %"],
    )

    sentence = ErrorAnnotatedSentence("( nissonin dušše 0.6 %:s )")
    sentence.errors.append(error1)
    sentence.errors.append(error2)

    assert sentence.error_count() == 2
    assert sentence.errors[0].errortype == ErrorType.ERRORORTREAL
    assert sentence.errors[1].errortype == ErrorType.ERRORMORPHSYN


def test_multiple_errors_in_sentence():
    """Test sentence with 3 errors."""
    error1 = ErrorMarkup(
        form="njiŋŋalas",
        start=15,
        end=15 + len("njiŋŋalas"),
        errortype=ErrorType.ERRORORT,
        suggestions=["njiŋŋálas"],
        errorinfo="noun,á",
    )

    error2 = ErrorMarkup(
        form="ságahuvvon",
        start=25,
        end=25 + len("ságahuvvon"),
        errortype=ErrorType.ERRORORT,
        suggestions=["sagahuvvon"],
        errorinfo="verb,a",
    )

    error3 = ErrorMarkup(
        form="guovža-klána",
        start=40,
        end=40 + len("guovža-klána"),
        errortype=ErrorType.ERRORORT,
        suggestions=["guovžaklána"],
        errorinfo="noun,cmp",
    )

    sentence = ErrorAnnotatedSentence(
        "(haploida) ja njiŋŋalas ságahuvvon manneseallas guovža-klána"
    )
    sentence.errors.append(error1)
    sentence.errors.append(error2)
    sentence.errors.append(error3)

    assert sentence.error_count() == 3
    assert sentence.errors[0].errorinfo == "noun,á"
    assert sentence.errors[1].errorinfo == "verb,a"
    assert sentence.errors[2].errorinfo == "noun,cmp"


@pytest.mark.parametrize(
    ("name", "input_xml", "expected_xml"),
    [
        (
            "errorlang_infinity",
            "{molekylærbiologimi}∞{kal,bio}",
            "<p><errorlang>molekylærbiologimi<correct>kal,bio</correct></errorlang></p>",
        ),
        (
            "quote_char",
            "{”sjievnnijis”}${conc,vnn-vnnj|sjievnnjis}",
            '<p><errorort>”sjievnnijis”<correct errorinfo="conc,vnn-vnnj">sjievnnjis</correct></errorort></p>',
        ),
        (
            "error_parser_errorort1",
            "{jne.}${adv,typo|jna.}",
            '<p><errorort>jne.<correct errorinfo="adv,typo">jna.</correct></errorort></p>',
        ),
        (
            "error_parser_error_morphsyn1",
            "{Nieiddat leat nuorra}£{a,spred,nompl,nomsg,agr|Nieiddat leat nuorat}",
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
            "{jne.}${adv,typo|jna.}",
            '<p><errorort>jne.<correct errorinfo="adv,typo">jna.</correct></errorort></p>',
        ),
        (
            "errorort2",
            "{daesn'}${daesnie}",
            "<p><errorort>daesn'<correct>daesnie</correct></errorort></p>",
        ),
        (
            "input_contains_slash",
            "{magistter/}${loan,vowlat,e-a|magisttar}",
            '<p><errorort>magistter/<correct errorinfo="loan,vowlat,e-a">'
            "magisttar</correct></errorort></p>",
        ),
        (
            "error_correct1",
            "{1]}§{Ij}",
            "<p><error>1]<correct>Ij</correct></error></p>",
        ),
        (
            "error_correct2",
            "{væ]keles}§{væjkeles}",
            "<p><error>væ]keles<correct>væjkeles</correct></error></p>",
        ),
        (
            "error_correct3",
            "{smávi-}§{smávit-}",
            "<p><error>smávi-<correct>smávit-</correct></error></p>",
        ),
        (
            "error_correct4",
            "{CD:t}§{CD:at}",
            "<p><error>CD:t<correct>CD:at</correct></error></p>",
        ),
        (
            "error_correct5",
            "{DNB-feaskáris}§{DnB-feaskáris}",
            "<p><error>DNB-feaskáris<correct>DnB-feaskáris</correct></error></p>",
        ),
        (
            "error_correct6",
            "{boade}§{boađe}",
            "<p><error>boade<correct>boađe</correct></error></p>",
        ),
        (
            "error_correct7",
            "{2005’as}§{2005:s}",
            "<p><error>2005’as<correct>2005:s</correct></error></p>",
        ),
        (
            "error_correct8",
            "{NSRii}§{NSR:i}",
            "<p><error>NSRii<correct>NSR:i</correct></error></p>",
        ),
        (
            "error_correct9",
            "{Nordkjosbotn'ii}§{Nordkjosbotnii}",
            "<p><error>Nordkjosbotn'ii<correct>Nordkjosbotnii</correct></error></p>",
        ),
        (
            "errorort3",
            "{nourra}${a,meta|nuorra}",
            '<p><errorort>nourra<correct errorinfo="a,meta">nuorra</correct></errorort></p>',
        ),
        (
            "error_morphsyn1",
            "{Nieiddat leat nuorra}£{a,spred,nompl,nomsg,agr|Nieiddat leat nuorat}",
            "<p><errormorphsyn>Nieiddat leat nuorra"
            '<correct errorinfo="a,spred,nompl,nomsg,agr">Nieiddat leat '
            "nuorat</correct></errormorphsyn></p>",
        ),
        (
            "error_syn1",
            "{riŋgen nieidda lusa}¥{x,pph|riŋgen niidii}",
            '<p><errorsyn>riŋgen nieidda lusa<correct errorinfo="x,pph">'
            "riŋgen niidii</correct></errorsyn></p>",
        ),
        (
            "error_syn2",
            "{ovtta}¥{num,redun| }",
            '<p><errorsyn>ovtta<correct errorinfo="num,redun"></correct>'
            "</errorsyn></p>",
        ),
        (
            "error_lex1",
            "{dábálaš}€{adv,adj,der|dábálaččat}",
            '<p><errorlex>dábálaš<correct errorinfo="adv,adj,der">dábálaččat'
            "</correct></errorlex></p>",
        ),
        (
            "error_ortreal1",
            "{ráhččamušaid}¢{noun,mix|rahčamušaid}",
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
            "<p>- ruksesruonáčalmmehisvuohta lea sullii {8%:as}${acr,suf|8%:s}",
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
            "{{A  B}‰{notspace|A B}  C}‰{notspace|A B C}",
            "<p>"
            "<errorformat>"
            "<errorformat>"
            'A  B<correct errorinfo="notspace">A B</correct></errorformat>'
            '  C<correct errorinfo="notspace">A B C</correct></errorformat>'
            "</p>",
        ),
        (
            "preserve_space_at_end_of_sentence",
            "<p>buvttadeaddji Anstein {Mikkelsens}${typo|Mikkelsen} lea ráhkadan. </p>",
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
            "{Mikkelsens}${typo|Mikkelsen} lea ráhkadan. "
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
            "{leimme}£{leimmet///leat}",
            "<p><errormorphsyn>leimme"
            "<correct>leimmet</correct>"
            "<correct>leat</correct>"
            "</errormorphsyn></p>",
        ),
        (
            "nested errormorphsyn/errorort",
            "{{šaddai}${verb,conc|šattai} ollu áššit}£{verb,fin,pl3prs,sg3prs,tense|šadde ollu áššit}",
            '<p><errormorphsyn><errorort>šaddai<correct errorinfo="verb,conc">'
            "šattai</correct></errorort> ollu áššit<correct "
            'errorinfo="verb,fin,pl3prs,sg3prs,tense">šadde ollu áššit'
            "</correct></errormorphsyn></p>",
        ),
        (
            "nested errormorphsyn/error",
            "{guokte {ganddat}§{n,á|gánddat}}£{n,nump,gensg,nompl,case|guokte gándda}",
            '<p><errormorphsyn>guokte <error>ganddat<correct errorinfo="n,á">'
            "gánddat</correct></error><correct "
            'errorinfo="n,nump,gensg,nompl,case">guokte gándda</correct>'
            "</errormorphsyn></p>",
        ),
        (
            "nested errormorphsyn/errorort 2",
            "{Nieiddat leat {nourra}${adj,meta|nuorra}}"
            "£{adj,spred,nompl,nomsg,agr|Nieiddat leat nuorat}",
            "<p><errormorphsyn>Nieiddat leat <errorort>nourra<correct "
            'errorinfo="adj,meta">nuorra</correct></errorort>'
            '<correct errorinfo="adj,spred,nompl,nomsg,agr">Nieiddat leat '
            "nuorat</correct></errormorphsyn></p>",
        ),
        (
            "nested errormorphsyn/errormorphsyn",
            "{leat {okta máná}£{n,spred,nomsg,gensg,case|okta mánná}}"
            "£{v,v,sg3prs,pl3prs,agr|lea okta mánná}",
            "<p><errormorphsyn>leat <errormorphsyn>okta máná<correct "
            'errorinfo="n,spred,nomsg,gensg,case">okta mánná</correct>'
            '</errormorphsyn><correct errorinfo="v,v,sg3prs,pl3prs,agr">'
            "lea okta mánná</correct></errormorphsyn></p>",
        ),
        (
            "complex nested errors",
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
            "nested errormorphsyn/errorort/errorlex",
            "{{Bearpmahat}${noun,svow|Bearpmehat} "
            "{earuha}€{verb,v,w|sirre}}£{verb,fin,pl3prs,sg3prs,agr|Bearpmehat"
            " sirrejit} uskki ja loaiddu.</p>",
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
            "<p>Bruk {{epoxi}${noun,cons|epoksy} lim}¢{noun,mix|epoksylim} "
            "med god kvalitet.</p>",
            "<p>Bruk <errorortreal><errorort>epoxi"
            '<correct errorinfo="noun,cons">epoksy</correct></errorort> lim'
            '<correct errorinfo="noun,mix">epoksylim</correct></errorortreal> '
            "med god kvalitet.</p>",
        ),
    ],
)
def test_to_errormarkupxml(name: str, input_xml: str, expected_xml: str):
    """Test plain errormarkup."""
    error_annotated_sentence = parse_markup_to_sentence(input_xml)
    result_elem = error_annotated_sentence.to_errormarkupxml()
    result_xml = etree.tostring(result_elem, encoding="unicode")
    assert (
        result_xml == expected_xml
        or f"Test '{name}' failed: got {result_xml}, expected {expected_xml}"
    )
