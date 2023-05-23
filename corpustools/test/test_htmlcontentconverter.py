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
"""Test conversion of html content."""

import lxml.etree as etree
import lxml.html as html
from parameterized import parameterized

from corpustools import htmlcontentconverter
from corpustools.test import xmltester
from corpustools.test.test_xhtml2corpus import assertXmlEqual


def test_remove_unwanted_content():
    """Test if unwanted content is removed."""
    unwanted_classes_ids = {
        "div": {
            "class": [
                "latestnews_uutisarkisto",
                "InnholdForfatter",  # unginordland
                "QuickNav",
                "ad",
                "andrenyheter",  # tysfjord.kommune.no
                "article-ad",
                "article-bottom-element",
                "article-column",
                "article-dateline article-dateline-footer "
                "meta-widget-content",  # nrk.no
                "article-info",  # regjeringen.no
                "article-related",
                "articleImageRig",
                "articlegooglemap",  # tysfjord.kommune.no
                "articleTags",  # nord-salten.no
                "attribute-related_object",  # samediggi.no
                "authors",
                "authors ui-helper-clearfix",  # nord-salten.no
                "back_button",
                "banner-element",
                "breadcrumbs ",
                "breadcrumbs",
                "breadcrums span-12",
                "btm_menu",
                "byline",  # arran.no
                "clearfix breadcrumbsAndSocial noindex",  # udir.no
                "complexDocumentBottom",  # regjeringen.no
                "container_full",
                "documentInfoEm",
                "documentPaging",
                "documentTop",  # regjeringen.no
                "dotList",  # nord-salten.no
                "dropmenudiv",  # calliidlagadus.org
                "egavpi",  # calliidlagadus.org
                "egavpi_fiskes",  # calliidlagadus.org
                "expandable",
                "feedbackContainer noindex",  # udir.no
                "fixed-header",
                "g100 col fc s18 sg6 sg9 sg12 menu-reference",  # nrk.no
                "g100 col fc s18 sg6 sg9 sg12 flow-reference",  # nrk.no
                "g11 col fl s2 sl6 sl9 sl12 sl18",  # nrk.no
                "g22 col fl s4 sl6 sl9 sl12 sl18 " "article-header-sidebar",  # nrk.no
                "g94 col fl s17 sl18 sg6 sg9 sg12 meta-widget",  # nrk.no
                "globmenu",  # visitstetind.no
                "grid cf",  # nrk.no
                "help closed hidden-xs",
                "historic-info",  # regjeringen.no
                "historic-label",  # regjeringen.no
                "imagecontainer",
                "innholdsfortegenlse-child",
                "ld-navbar",
                "meta",
                "meta ui-helper-clearfix",  # nord-salten.no
                "authors ui-helper-clearfix",  # nord-salten.no
                "menu",  # visitstetind.no
                "metaWrapper",
                "moduletable_oikopolut",
                "moduletable_etulinkki",  # www.samediggi.fi
                "naviHlp",  # visitstetind.no
                "noindex",  # ntfk
                "nrk-globalfooter",  # nrk.no
                "nrk-globalfooter-dk lp_globalfooter",  # nrk.no
                "nrk-globalnavigation",  # nrk.no
                "outer-column",
                "post-footer",
                "printContact",
                "right",  # ntfk
                "rightverticalgradient",  # udir.no
                "sharing",
                "sidebar",
                "spalte300",  # osko.no
                "subfooter",  # visitstetind.no
                "tabbedmenu",
                "tipformcontainer",  # tysfjord.kommune.no
                "tipsarad mt6 selfClear",
                "titlepage",
                "toc",
                "tools",  # arran.no
            ],
            "id": [
                "AreaLeft",
                "AreaLeftNav",
                "AreaRight",
                "AreaTopRight",
                "AreaTopSiteNav",
                "NAVbreadcrumbContainer",
                "NAVfooterContainer",
                "NAVheaderContainer",
                "NAVrelevantContentContainer",
                "NAVsubmenuContainer",
                "PageFooter",
                "PrintDocHead",
                "SamiDisclaimer",
                "ShareArticle",
                "WIPSELEMENT_CALENDAR",  # learoevierhtieh.no
                "WIPSELEMENT_HEADING",  # learoevierhtieh.no
                "WIPSELEMENT_MENU",  # learoevierhtieh.no
                "WIPSELEMENT_MENURIGHT",  # learoevierhtieh.no
                "WIPSELEMENT_NEWS",  # learoevierhtieh.no
                "aa",
                "andrenyheter",  # tysfjord.kommune.no
                "article_footer",
                "attached",  # tysfjord.kommune.no
                "blog-pager",
                "breadcrumbs-bottom",
                "bunninformasjon",  # unginordland
                "chatBox",
                "chromemenu",  # calliidlagadus.org
                "crumbs",  # visitstetind.no
                "ctl00_FullRegion_CenterAndRightRegion_HitsControl_"
                "ctl00_FullRegion_CenterAndRightRegion_Sorting_sortByDiv",
                "ctl00_MidtSone_ucArtikkel_ctl00_ctl00_ctl01_divRessurser",
                "ctl00_MidtSone_ucArtikkel_ctl00_divNavigasjon",
                "deleModal",
                "document-header",
                "errorMessageContainer",  # nord-salten.no
                "footer",  # forrest, too, tysfjord.kommune.no
                "footer-wrapper",
                "frontgallery",  # visitstetind.no
                "header",
                "headerBar",
                "headWrapper",  # osko.no
                "hoyre",  # unginordland
                "innholdsfortegnelse",  # regjeringen.no
                "leftMenu",
                "leftPanel",
                "leftbar",  # forrest (divvun and giellatekno sites)
                "leftcol",  # new samediggi.no
                "leftmenu",
                "main_navi_main",  # www.samediggi.fi
                "mainsidebar",  # arran.no
                "menu",
                "murupolku",  # www.samediggi.fi
                "navbar",  # tysfjord.kommune.no
                "ncFooter",  # visitstetind.no
                "ntfkFooter",  # ntfk
                "ntfkHeader",  # ntfk
                "ntfkNavBreadcrumb",  # ntfk
                "ntfkNavMain",  # ntfk
                "pageFooter",
                "PageLanguageInfo",  # regjeringen.no
                "path",  # new samediggi.no, tysfjord.kommune.no
                "readspeaker_button1",
                "rightAds",
                "rightCol",
                "rightside",
                "s4-leftpanel",  # ntfk
                "searchBox",
                "searchHitSummary",
                "sendReminder",
                "share-article",
                "sidebar",  # finlex.fi, too
                "sidebar-wrapper",
                "sitemap",
                "skipLinks",  # udir.no
                "skiplink",  # tysfjord.kommune.no
                "spraakvelger",  # osko.no
                "subfoote",  # visitstetind.no
                "submenu",  # nord-salten.no
                "tipafriend",
                "tools",  # arran.no
                "topHeader",  # nord-salten.no
                "topMenu",
                "topUserMenu",
                "top",  # arran.no
                "topnav",  # tysfjord.kommune.no
                "toppsone",  # unginordland
                "vedleggogregistre",  # regjeringen.no
                "venstre",  # unginordland
            ],
        },
        "p": {
            "class": ["WebPartReadMoreParagraph", "breadcrumbs", "langs"],  # oahpa.no
        },
        "ul": {
            "id": [
                "AreaTopPrintMeny",
                "AreaTopLanguageNav",
                "skiplinks",  # umo.se
            ],
            "class": [
                "QuickNav",
                "article-tools",
                "byline",
                "chapter-index",  # lovdata.no
                "footer-nav",  # lovdata.no
                "hidden",  # unginordland
            ],
        },
        "span": {
            "id": ["skiplinks"],
            "class": [
                "K-NOTE-FOTNOTE",
                "graytext",  # svenskakyrkan.se
            ],
        },
        "a": {
            "id": [
                "ctl00_IdWelcome_ExplicitLogin",  # ntfk
                "leftPanelTab",
            ],
            "class": [
                "addthis_button_print",  # ntfk
                "mainlevel",
                "share-paragraf",  # lovdata.no
                "mainlevel_alavalikko",  # www.samediggi.fi
                "sublevel_alavalikko",  # www.samediggi.fi
            ],
        },
        "td": {
            "id": [
                "hakulomake",  # www.samediggi.fi
                "paavalikko_linkit",  # www.samediggi.fi
                "sg_oikea",  # www.samediggi.fi
                "sg_vasen",  # www.samediggi.fi
            ],
            "class": [
                "modifydate",
            ],
        },
        "tr": {
            "id": [
                "sg_ylaosa1",
                "sg_ylaosa2",
            ]
        },
        "header": {
            "id": [
                "header",  # umo.se
            ],
            "class": [
                "nrk-masthead-content cf",  # nrk.no
                "pageHeader ",  # regjeringen.no
            ],
        },
        "section": {
            "class": [
                "tree-menu current",  # umo.se
                "tree-menu",  # umo.se
            ],
        },
    }

    for tag, attribs in unwanted_classes_ids.items():
        for key, values in attribs.items():
            for value in values:
                yield check_unwanted_classes_and_ids, tag, key, value


def check_unwanted_classes_and_ids(tag, key, value):
    """Check that unwanted content is removed."""
    if tag == "tr":
        inner = (
            '<table><tbody><{0} {1}="{2}"><td>content:{0} {1} {2}</td>'
            "</tbody></table>".format(tag, key, value)
        )
        inner_r = "<table><tbody/></table>"
    elif tag == "td":
        inner = (
            '<table><tbody><tr><{0} {1}="{2}">content:{0} {1} {2}</tr>'
            "</tbody></table>".format(tag, key, value)
        )
        inner_r = "<table><tbody><tr/></tbody></table>"
    else:
        inner = '<{0} {1}="{2}">' "content:{0} {1} {2}" "</{0}>".format(tag, key, value)
        inner_r = ""
    content_xml = html.document_fromstring(
        f"<html><head/><body>{inner}</body></html>"
    )
    got = htmlcontentconverter.HTMLBeautifier(content_xml).beautify()

    want = html.document_fromstring(
        f"<html><head/><body>{inner_r}</body></html>"
    )

    if etree.tostring(got) != etree.tostring(want):
        raise AssertionError(
            "Remove classes and ids:\nexpected {}\n"
            "got {}".format(etree.tostring(want), etree.tostring(got))
        )


@parameterized(
    [
        "address",
        "script",
        "style",
        "area",
        "object",
        "meta",
        "hr",
        "nf",
        "mb",
        "ms",
        "img",
        "cite",
        "embed",
        "footer",
        "figcaption",
        "aside",
        "time",
        "figure",
        "nav",
        "select",
        "noscript",
        "iframe",
        "map",
        "colgroup",
        "st1:country-region",
        "v:shapetype",
        "v:shape",
        "st1:metricconverter",
        "fb:comments",
        "g:plusone",
        "fb:like",
    ]
)
def test_unwanted_tag(unwanted_tag):
    """Check if unwanted tags are removed."""
    content_xml = html.document_fromstring(
        "<html><head/><body><p>p1</p><%s/><p>p2</p2></body>" "</html>" % unwanted_tag
    )
    got = htmlcontentconverter.HTMLBeautifier(content_xml).beautify()
    want = html.document_fromstring(
        "<html><head/>" "<body><p>p1</p><p>p2" "</p></body></html>"
    )

    assertXmlEqual(got, want)


class TestHTMLContentConverter(xmltester.XMLTester):
    """Test the HTMLContentConverter class."""

    @parameterized.expand(
        [
            (
                "Remove an empty p.",
                "<html><head/><body><p/></html>",
                "<html><head/><body></body></html>",
            ),
            (
                "Do not remove a p with content.",
                "<html><head/><body><p><span>spanny</span></p></html>",
                "<html><head/><body><p><span>spanny</span></p></body></html>",
            ),
            (
                "Remove empty class",
                '<html><head/><body><div class="">a</div><div class="a">'
                '<span class="">b</span></div></html>',
                '<html><head/><body><div>a</div><div class="a">'
                "<span>b</span></div></body></html>",
            ),
            (
                "Remove comment",
                "<html><head/><body><b><!--Hey, buddy. --></b></body></html>",
                "<html><head/><body><b/></body></html>",
            ),
            (
                "Remove processing instruction",
                "<html><head/><body><b><?ProcessingInstruction?></b></body></html>",
                "<html><head/><body><b/></body></html>",
            ),
            (
                "Only text before next significant element",
                "<html><head><title>– Den utdøende stammes frykt</title>"
                "</head><body><h3>VI</h3>... Finnerne<p>Der</body></html>",
                "<html><head>"
                "<title>– Den utdøende stammes frykt</title></head><body>"
                "<h3>VI</h3>  <p>... Finnerne</p><p>Der</p></body></html>",
            ),
            (
                "Text and i element before next significant element",
                "<head><title>– Den utdøende stammes frykt</title>"
                "</head><body><h3>VI</h3>... Finnerne<i>Der</body></html>",
                "<html><head>"
                "<title>– Den utdøende stammes frykt</title></head><body>"
                "<h3>VI</h3>  <p>... Finnerne<i>Der</i></p></body></html>",
            ),
            (
                "h2 as a stop element",
                "<html><head>"
                "<title>– Den utdøende stammes frykt</title>"
                "</head><body><h3>VI</h3>... Finnerne"
                "<h2>Der</h2></body></html>",
                "<html><head><title>– Den "
                "utdøende stammes frykt</title>"
                "</head><body>  <h3>VI</h3>  "
                "<p>... Finnerne</p><h2>Der</h2></body></html>",
            ),
            (
                "center2div",
                '<html><head/><body><center><span class="">b</span></center></html>',
                '<html><head/><body><div class="c1"><span>b</span></div></body>'
                "</html>",
            ),
            (
                "test_body_i",
                "<html><head/><body><i>b</i></body></html>",
                "<html><head/><body><p><i>b</i></p></body></html>",
            ),
            (
                "Font elements with only text",
                "<html><head/><body><p>x "
                "<font>a, b </font>"
                "<font>c</font>"
                "<font>d</font>"
                "<font>e</font>"
                "<font> f</font>"
                "<font>. </font>"
                "</p></body></html>",
                "<html><head/><body><p>" "x a, b cde f. " "</p></body></html>",
            ),
            (
                "Font element containing other xml elements",
                "<html><head/><body><p>x "
                "<font>a <i>b</i> c.</font> d"
                "</p></body></html>",
                "<html><head/><body><p>x " "a <i>b</i> c. d" "</p></body></html>",
            ),
            (
                "Font element containing font elements",
                "<html><head/><body><p><font>x</font> "
                "<font>a <i>b</i> c.</font> <font>d</font>"
                "</p></body></html>",
                "<html><head/><body><p>x a <i>b</i> c. d" "</p></body></html>",
            ),
            (
                "test_body_a",
                "<html><head/><body><a>b</a></body></html>",
                "<html><head/><body><p><a>b</a></p></body></html>",
            ),
            (
                "test_body_em",
                "<html><head/><body><em>b</em></body></html>",
                "<html><head/><body><p><em>b</em></p></body></html>",
            ),
            (
                "test_body_font",
                "<html><head/><body><font>b</font></body></html>",
                "<html><head/><body><p>b</p></body></html>",
            ),
            (
                "test_body_u",
                "<html><head/><body><u>b</u></body></html>",
                "<html><head/><body><p><u>b</u></p></body></html>",
            ),
            (
                "test_body_strong",
                "<html><head/><body><strong>b</strong></body></html>",
                "<html><head/><body><p><strong>b</strong></p></body></html>",
            ),
            (
                "test_body_span",
                "<html><head/><body><span>b</span></body></html>",
                "<html><head/><body><p><span>b</span></p></body></html>",
            ),
            (
                "test_body_text",
                "<html><head/><body>b</body></html>",
                "<html><head/><body><p>b</p></body></html>",
            ),
        ]
    )
    def test_convert2xhtml(self, testname, test_input, want_input):
        """Test convert2xhtml.

        Args:
            testname (str): name of the test
            test_input (str): input sent to convert2xhtml
            want_input (str): input to html.document_fromstring

        Raises:
            AssertionError: if got and want are unequal.
        """
        hcc = htmlcontentconverter.HTMLBeautifier(html.document_fromstring(test_input))
        got = hcc.beautify()
        want = html.document_fromstring(want_input)

        self.assertXmlEqual(got, want)
