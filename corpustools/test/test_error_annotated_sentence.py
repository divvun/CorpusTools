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
#   Copyright © 2025-2026 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   https://giellatekno.uit.no & https://divvun.no
#
"""Tests for error_annotated_sentence module"""

import pytest
from lxml import etree

from corpustools.error_annotated_sentence import (
    CorrectionSegment,
    ErrorAnnotatedSentence,
    ErrorMarkup,
    ErrorMarkupSegment,
    parse_markup_to_sentence,
)
from corpustools.error_types import ErrorType


@pytest.mark.parametrize(
    (
        "name",
        "error_markup_string",
        "error_annotated_sentence",
        "uncorrected_text",
        "expected_xml",
    ),
    [
        (
            "no errors",
            "wrong",
            ErrorAnnotatedSentence(head="wrong", errors=[]),
            "wrong",
            "<p>wrong</p>",
        ),
        (
            "errorlang_infinity",
            "{molekylærbiologimi}∞{kal,bio|}",
            ErrorAnnotatedSentence(
                head="",
                errors=[
                    ErrorMarkupSegment(
                        error_markup=ErrorMarkup(
                            error=ErrorAnnotatedSentence(
                                head="molekylærbiologimi", errors=[]
                            ),
                            errortype=ErrorType.ERRORLANG,
                            correction=CorrectionSegment(
                                error_info="kal,bio",
                                suggestions=[""],
                            ),
                        ),
                        tail="",
                    )
                ],
            ),
            "molekylærbiologimi",
            '<p><errorlang>molekylærbiologimi<correct errorinfo="kal,bio"></correct>'
            "</errorlang></p>",
        ),
        (
            "error_correct",
            "{1]}§{Ij}",
            ErrorAnnotatedSentence(
                head="",
                errors=[
                    ErrorMarkupSegment(
                        error_markup=ErrorMarkup(
                            error=ErrorAnnotatedSentence(head="1]", errors=[]),
                            errortype=ErrorType.ERROR,
                            correction=CorrectionSegment(
                                error_info=None,
                                suggestions=["Ij"],
                            ),
                        ),
                        tail="",
                    )
                ],
            ),
            "1]",
            "<p><error>1]<correct>Ij</correct></error></p>",
        ),
        (
            "error_syn1",
            "{riŋgen nieidda lusa}¥{x,pph|riŋgen niidii}",
            ErrorAnnotatedSentence(
                head="",
                errors=[
                    ErrorMarkupSegment(
                        error_markup=ErrorMarkup(
                            error=ErrorAnnotatedSentence(
                                head="riŋgen nieidda lusa", errors=[]
                            ),
                            errortype=ErrorType.ERRORSYN,
                            correction=CorrectionSegment(
                                error_info="x,pph",
                                suggestions=["riŋgen niidii"],
                            ),
                        ),
                        tail="",
                    )
                ],
            ),
            "riŋgen nieidda lusa",
            '<p><errorsyn>riŋgen nieidda lusa<correct errorinfo="x,pph">'
            "riŋgen niidii</correct></errorsyn></p>",
        ),
        (
            "non-nested errormarkup",
            "a {e1}¢{c1} b {e2}${c2}.",
            ErrorAnnotatedSentence(
                head="a ",
                errors=[
                    ErrorMarkupSegment(
                        error_markup=ErrorMarkup(
                            error=ErrorAnnotatedSentence(head="e1", errors=[]),
                            errortype=ErrorType.ERRORORTREAL,
                            correction=CorrectionSegment(
                                error_info=None,
                                suggestions=["c1"],
                            ),
                        ),
                        tail=" b ",
                    ),
                    ErrorMarkupSegment(
                        error_markup=ErrorMarkup(
                            error=ErrorAnnotatedSentence(head="e2", errors=[]),
                            errortype=ErrorType.ERRORORT,
                            correction=CorrectionSegment(
                                error_info=None,
                                suggestions=["c2"],
                            ),
                        ),
                        tail=".",
                    ),
                ],
            ),
            "a e1 b e2.",
            "<p>a <errorortreal>e1<correct>c1</correct></errorortreal> b "
            "<errorort>e2<correct>c2</correct></errorort>.</p>",
        ),
        (
            "error_ortreal",
            "( {nissonin}¢{noun,suf|nissoniin} dušše {0.6 %:s}£{0.6 %} )",
            ErrorAnnotatedSentence(
                head="( ",
                errors=[
                    ErrorMarkupSegment(
                        error_markup=ErrorMarkup(
                            error=ErrorAnnotatedSentence(head="nissonin", errors=[]),
                            errortype=ErrorType.ERRORORTREAL,
                            correction=CorrectionSegment(
                                error_info="noun,suf",
                                suggestions=["nissoniin"],
                            ),
                        ),
                        tail=" dušše ",
                    ),
                    ErrorMarkupSegment(
                        error_markup=ErrorMarkup(
                            error=ErrorAnnotatedSentence(head="0.6 %:s", errors=[]),
                            errortype=ErrorType.ERRORMORPHSYN,
                            correction=CorrectionSegment(
                                error_info=None,
                                suggestions=["0.6 %"],
                            ),
                        ),
                        tail=" )",
                    ),
                ],
            ),
            "( nissonin dušše 0.6 %:s )",
            '<p>( <errorortreal>nissonin<correct errorinfo="noun,suf">'
            "nissoniin</correct></errorortreal> dušše <errormorphsyn>0.6 %:s"
            "<correct>0.6 %</correct></errormorphsyn> )</p>",
        ),
        (
            "error_format",
            "{{A  B}‰{notspace|A B}  C}‰{notspace|A B C}",
            ErrorAnnotatedSentence(
                head="",
                errors=[
                    ErrorMarkupSegment(
                        error_markup=ErrorMarkup(
                            error=ErrorAnnotatedSentence(
                                head="",
                                errors=[
                                    ErrorMarkupSegment(
                                        error_markup=ErrorMarkup(
                                            error=ErrorAnnotatedSentence(
                                                head="A  B", errors=[]
                                            ),
                                            errortype=ErrorType.ERRORFORMAT,
                                            correction=CorrectionSegment(
                                                error_info="notspace",
                                                suggestions=["A B"],
                                            ),
                                        ),
                                        tail="  C",
                                    )
                                ],
                            ),
                            errortype=ErrorType.ERRORFORMAT,
                            correction=CorrectionSegment(
                                error_info="notspace",
                                suggestions=["A B C"],
                            ),
                        ),
                        tail="",
                    )
                ],
            ),
            "A  B  C",
            "<p>"
            "<errorformat>"
            "<errorformat>"
            'A  B<correct errorinfo="notspace">A B</correct></errorformat>'
            '  C<correct errorinfo="notspace">A B C</correct></errorformat>'
            "</p>",
        ),
        (
            "nested errormorphsyn/errorort",
            "{{šaddai}${verb,conc|šattai} ollu áššit}£{verb,fin,pl3prs,sg3prs,tense|"
            "šadde ollu áššit}",
            ErrorAnnotatedSentence(
                head="",
                errors=[
                    ErrorMarkupSegment(
                        error_markup=ErrorMarkup(
                            error=ErrorAnnotatedSentence(
                                head="",
                                errors=[
                                    ErrorMarkupSegment(
                                        error_markup=ErrorMarkup(
                                            error=ErrorAnnotatedSentence(
                                                head="šaddai", errors=[]
                                            ),
                                            errortype=ErrorType.ERRORORT,
                                            correction=CorrectionSegment(
                                                error_info="verb,conc",
                                                suggestions=["šattai"],
                                            ),
                                        ),
                                        tail=" ollu áššit",
                                    )
                                ],
                            ),
                            errortype=ErrorType.ERRORMORPHSYN,
                            correction=CorrectionSegment(
                                error_info="verb,fin,pl3prs,sg3prs,tense",
                                suggestions=["šadde ollu áššit"],
                            ),
                        ),
                        tail="",
                    )
                ],
            ),
            "šaddai ollu áššit",
            '<p><errormorphsyn><errorort>šaddai<correct errorinfo="verb,conc">'
            "šattai</correct></errorort> ollu áššit<correct "
            'errorinfo="verb,fin,pl3prs,sg3prs,tense">šadde ollu áššit'
            "</correct></errormorphsyn></p>",
        ),
        (
            "complex nested errors",
            "heaitit {dáhkaluddame}${verb,a|dahkaluddame} ahte sis "
            "{máhkaš}¢{adv,á|mahkáš} livččii {makkarge}${adv,á|makkárge} "
            "politihkka, muhto rahpasit baicca muitalivčče {{makkar}"
            "${interr,á|makkár} soga}€{man soga} sii {ovddasttit}"
            "${verb,conc|ovddastit}.",
            ErrorAnnotatedSentence(
                head="heaitit ",
                errors=[
                    ErrorMarkupSegment(
                        error_markup=ErrorMarkup(
                            error=ErrorAnnotatedSentence(
                                head="dáhkaluddame", errors=[]
                            ),
                            errortype=ErrorType.ERRORORT,
                            correction=CorrectionSegment(
                                error_info="verb,a",
                                suggestions=["dahkaluddame"],
                            ),
                        ),
                        tail=" ahte sis ",
                    ),
                    ErrorMarkupSegment(
                        error_markup=ErrorMarkup(
                            error=ErrorAnnotatedSentence(head="máhkaš", errors=[]),
                            errortype=ErrorType.ERRORORTREAL,
                            correction=CorrectionSegment(
                                error_info="adv,á",
                                suggestions=["mahkáš"],
                            ),
                        ),
                        tail=" livččii ",
                    ),
                    ErrorMarkupSegment(
                        error_markup=ErrorMarkup(
                            error=ErrorAnnotatedSentence(head="makkarge", errors=[]),
                            errortype=ErrorType.ERRORORT,
                            correction=CorrectionSegment(
                                error_info="adv,á",
                                suggestions=["makkárge"],
                            ),
                        ),
                        tail=" politihkka, muhto rahpasit baicca muitalivčče ",
                    ),
                    ErrorMarkupSegment(
                        error_markup=ErrorMarkup(
                            error=ErrorAnnotatedSentence(
                                head="",
                                errors=[
                                    ErrorMarkupSegment(
                                        error_markup=ErrorMarkup(
                                            error=ErrorAnnotatedSentence(
                                                head="makkar", errors=[]
                                            ),
                                            errortype=ErrorType.ERRORORT,
                                            correction=CorrectionSegment(
                                                error_info="interr,á",
                                                suggestions=["makkár"],
                                            ),
                                        ),
                                        tail=" soga",
                                    )
                                ],
                            ),
                            errortype=ErrorType.ERRORLEX,
                            correction=CorrectionSegment(
                                error_info=None, suggestions=["man soga"]
                            ),
                        ),
                        tail=" sii ",
                    ),
                    ErrorMarkupSegment(
                        error_markup=ErrorMarkup(
                            error=ErrorAnnotatedSentence(head="ovddasttit", errors=[]),
                            errortype=ErrorType.ERRORORT,
                            correction=CorrectionSegment(
                                error_info="verb,conc",
                                suggestions=["ovddastit"],
                            ),
                        ),
                        tail=".",
                    ),
                ],
            ),
            "heaitit dáhkaluddame ahte sis máhkaš livččii makkarge "
            "politihkka, muhto rahpasit baicca muitalivčče makkar soga sii ovddasttit.",
            "<p>heaitit "
            "<errorort>dáhkaluddame"
            '<correct errorinfo="verb,a">dahkaluddame</correct>'
            "</errorort>"
            " ahte sis "
            "<errorortreal>máhkaš"
            '<correct errorinfo="adv,á">mahkáš</correct>'
            "</errorortreal>"
            " livččii "
            "<errorort>makkarge"
            '<correct errorinfo="adv,á">makkárge</correct>'
            "</errorort>"
            " politihkka, muhto rahpasit baicca muitalivčče "
            "<errorlex>"
            "<errorort>makkar"
            '<correct errorinfo="interr,á">makkár</correct>'
            "</errorort>"
            " soga"
            "<correct>man soga</correct>"
            "</errorlex>"
            " sii "
            "<errorort>ovddasttit"
            '<correct errorinfo="verb,conc">ovddastit</correct>'
            "</errorort>"
            ".</p>",
        ),
        (
            "multiple nested errormorphsyn/errorort",
            "{Ovddit geasis}£{noun,advl,gensg,locsg,case|Ovddit geasi} "
            "{{{čoaggen}${verb,mono|čoggen} ollu jokŋat}"
            "£{noun,obj,genpl,nompl,case|čoggen ollu joŋaid} ja sarridat}"
            "£{noun,obj,genpl,nompl,case|čoggen ollu joŋaid ja sarridiid}",
            ErrorAnnotatedSentence(
                head="",
                errors=[
                    ErrorMarkupSegment(
                        error_markup=ErrorMarkup(
                            error=ErrorAnnotatedSentence(
                                head="Ovddit geasis", errors=[]
                            ),
                            errortype=ErrorType.ERRORMORPHSYN,
                            correction=CorrectionSegment(
                                error_info="noun,advl,gensg,locsg,case",
                                suggestions=["Ovddit geasi"],
                            ),
                        ),
                        tail=" ",
                    ),
                    ErrorMarkupSegment(
                        error_markup=ErrorMarkup(
                            error=ErrorAnnotatedSentence(
                                head="",
                                errors=[
                                    ErrorMarkupSegment(
                                        error_markup=ErrorMarkup(
                                            error=ErrorAnnotatedSentence(
                                                head="",
                                                errors=[
                                                    ErrorMarkupSegment(
                                                        error_markup=ErrorMarkup(
                                                            error=ErrorAnnotatedSentence(
                                                                head="čoaggen",
                                                                errors=[],
                                                            ),
                                                            errortype=ErrorType.ERRORORT,
                                                            correction=CorrectionSegment(
                                                                error_info="verb,mono",
                                                                suggestions=["čoggen"],
                                                            ),
                                                        ),
                                                        tail=" ollu jokŋat",
                                                    )
                                                ],
                                            ),
                                            errortype=ErrorType.ERRORMORPHSYN,
                                            correction=CorrectionSegment(
                                                error_info="noun,obj,genpl,nompl,case",
                                                suggestions=["čoggen ollu joŋaid"],
                                            ),
                                        ),
                                        tail=" ja sarridat",
                                    )
                                ],
                            ),
                            errortype=ErrorType.ERRORMORPHSYN,
                            correction=CorrectionSegment(
                                error_info="noun,obj,genpl,nompl,case",
                                suggestions=["čoggen ollu joŋaid ja sarridiid"],
                            ),
                        ),
                        tail="",
                    ),
                ],
            ),
            "Ovddit geasis čoaggen ollu jokŋat ja sarridat",
            "<p><errormorphsyn>Ovddit geasis<correct "
            'errorinfo="noun,advl,gensg,locsg,case">Ovddit geasi</correct>'
            "</errormorphsyn> <errormorphsyn><errormorphsyn><errorort>čoaggen"
            '<correct errorinfo="verb,mono">čoggen</correct></errorort> '
            'ollu jokŋat<correct errorinfo="noun,obj,genpl,nompl,case">'
            "čoggen ollu joŋaid</correct></errormorphsyn> ja sarridat"
            '<correct errorinfo="noun,obj,genpl,nompl,case">čoggen ollu '
            "joŋaid ja sarridiid</correct></errormorphsyn></p>",
        ),
        (
            "nested errormarkup1",
            "Lávus {{bearpmahat}${noun,svow|bearpmehat} {earuha}€{verb,v,w|sirre}}£"
            "{verb,fin,pl3prs,sg3prs,agr|bearpmehat sirrejit} uskki ja loaiddu.",
            ErrorAnnotatedSentence(
                head="Lávus ",
                errors=[
                    ErrorMarkupSegment(
                        error_markup=ErrorMarkup(
                            error=ErrorAnnotatedSentence(
                                head="",
                                errors=[
                                    ErrorMarkupSegment(
                                        error_markup=ErrorMarkup(
                                            error=ErrorAnnotatedSentence(
                                                head="bearpmahat", errors=[]
                                            ),
                                            errortype=ErrorType.ERRORORT,
                                            correction=CorrectionSegment(
                                                error_info="noun,svow",
                                                suggestions=["bearpmehat"],
                                            ),
                                        ),
                                        tail=" ",
                                    ),
                                    ErrorMarkupSegment(
                                        error_markup=ErrorMarkup(
                                            error=ErrorAnnotatedSentence(
                                                head="earuha", errors=[]
                                            ),
                                            errortype=ErrorType.ERRORLEX,
                                            correction=CorrectionSegment(
                                                error_info="verb,v,w",
                                                suggestions=["sirre"],
                                            ),
                                        ),
                                        tail="",
                                    ),
                                ],
                            ),
                            errortype=ErrorType.ERRORMORPHSYN,
                            correction=CorrectionSegment(
                                error_info="verb,fin,pl3prs,sg3prs,agr",
                                suggestions=["bearpmehat sirrejit"],
                            ),
                        ),
                        tail=" uskki ja loaiddu.",
                    )
                ],
            ),
            "Lávus bearpmahat earuha uskki ja loaiddu.",
            "<p>Lávus <errormorphsyn>"
            "<errorort>bearpmahat"
            '<correct errorinfo="noun,svow">bearpmehat</correct></errorort> '
            "<errorlex>earuha"
            '<correct errorinfo="verb,v,w">sirre</correct></errorlex>'
            '<correct errorinfo="verb,fin,pl3prs,sg3prs,agr">bearpmehat sirrejit'
            "</correct>"
            "</errormorphsyn> uskki ja loaiddu.</p>",
        ),
    ],
)
def test_parse_markup_to_sentence(
    name: str,
    error_markup_string: str,
    error_annotated_sentence: ErrorAnnotatedSentence,
    uncorrected_text: str,
    expected_xml: str,
):
    parsed_sentence = parse_markup_to_sentence(iter(error_markup_string))
    assert parsed_sentence == error_annotated_sentence, f"Failed test case: {name}"
    assert parsed_sentence.uncorrected_text() == uncorrected_text, (
        f"Failed uncorrected text for test case: {name}"
    )
    assert (
        etree.tostring(parsed_sentence.to_xml(), encoding="unicode") == expected_xml
    ), f"Failed XML output for test case: {name}"
