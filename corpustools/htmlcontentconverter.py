# -*- coding: utf-8 -*-

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
#   Copyright © 2012-2017 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
u"""Convert html content to the Giella xml format."""

import six
from lxml import etree, html
from lxml.html import clean

from corpustools import util


class HTMLContentConverter(object):
    """Convert html documents to the Giella xml format."""
    soup = None

    @staticmethod
    def superclean(content):
        """Remove unwanted elements from an html document.

        Arguments:
            content is a string containing an html document.

        Returns:
            a string containing the cleaned up html document.
        """
        cleaner = clean.Cleaner(
            page_structure=False,
            scripts=True,
            javascript=True,
            comments=True,
            style=True,
            processing_instructions=True,
            remove_unknown_tags=True,
            embedded=True,
            kill_tags=[
                'img',
                'area',
                'address',
                'hr',
                'cite',
                'footer',
                'figcaption',
                'aside',
                'time',
                'figure',
                'nav',
                'noscript',
                'map',
                'ins',
                's',
                'colgroup',
            ])

        return cleaner.clean_html(content)

    @staticmethod
    def remove_cruft(content):
        """Remove cruft from svenskakyrkan.se documents.

        Args:
            content (str): the content of a document.

        Returns:
            str: The content of the document without the cruft.
        """
        replacements = [
            (u'//<script', u'<script'),
            (u'&nbsp;', u' '),
            (u' ', u' '),
        ]
        return util.replace_all(replacements, content)

    def simplify_tags(self):
        u"""Turn tags to divs.

        We don't care about the difference between <fieldsets>, <legend>
        etc. – treat them all as <div>'s for xhtml2corpus
        """
        superfluously_named_tags = self.soup.xpath(
            "//fieldset | //legend | //article | //hgroup "
            "| //section | //dl | //dd | //dt"
            "| //menu",)
        for elt in superfluously_named_tags:
            elt.tag = 'div'

    def fix_spans_as_divs(self):
        """Turn div like elements into div.

        XHTML doesn't allow (and xhtml2corpus doesn't handle) span-like
        elements with div-like elements inside them; fix this and
        similar issues by turning them into divs.
        """
        spans_as_divs = self.soup.xpath(
            "//*[( descendant::div or descendant::p"
            "      or descendant::h1 or descendant::h2"
            "      or descendant::h3 or descendant::h4"
            "      or descendant::h5 or descendant::h6 ) "
            "and ( self::span or self::b or self::i"
            "      or self::em or self::strong "
            "      or self::a )"
            "    ]",)
        for elt in spans_as_divs:
            elt.tag = 'div'

        ps_as_divs = self.soup.xpath("//p[descendant::div]",)
        for elt in ps_as_divs:
            elt.tag = 'div'

        lists_as_divs = self.soup.xpath("//*[( child::ul or child::ol ) "
                                        "and ( self::ul or self::ol )"
                                        "    ]",)
        for elt in lists_as_divs:
            elt.tag = 'div'

    def remove_empty_p(self):
        """Remove empty p elements."""
        paragraphs = self.soup.xpath('//p')

        for elt in paragraphs:
            if elt.text is None and elt.tail is None and not len(elt):
                elt.getparent().remove(elt)

    def remove_empty_class(self):
        """Delete empty class attributes."""
        for element in self.soup.xpath('.//*[@class=""]'):
            del element.attrib['class']

    def remove_elements(self):
        """Remove unwanted tags from a html document.

        The point with this exercise is to remove all but the main content of
        the document.
        """
        unwanted_classes_ids = {
            'div': {
                'class': [
                    'AddThis',  # lansstyrelsen.se
                    'InnholdForfatter',  # unginordland
                    'NavigationLeft',  # lansstyrelsen.se
                    'QuickNav',
                    'ad',
                    'andrenyheter',  # tysfjord.kommune.no
                    'art-layout-cell art-sidebar2',  # gaaltije.se
                    'art-postheadericons art-metadata-icons',  # gaaltije.se
                    'article-ad',
                    'article-bottom-element',
                    'article-column',
                    ('article-dateline article-dateline-footer '
                     'meta-widget-content'),  # nrk.no
                    ('article-dateline article-footer '
                     'container-widget-content cf'),  # nrk.no
                    'article-heading-wrapper',  # 1177.se
                    'article-info',  # regjeringen.no
                    'article-related',
                    'article-toolbar__tool',  # umo.se
                    'article-universe-teaser container-widget-content',
                    'articleImageRig',
                    'articlegooglemap',  # tysfjord.kommune.no
                    'articleTags',  # nord-salten.no
                    'attribute-related_object',  # samediggi.no
                    'authors',
                    'authors ui-helper-clearfix',  # nord-salten.no
                    'back_button',
                    'banner-element',
                    'bl_linktext',
                    'bottom-center',
                    'breadcrumbs ',
                    'breadcrumbs',
                    'breadcrums span-12',
                    'btm_menu',
                    'byline',  # arran.no
                    'c1',  # jll.se
                    'art-bar art-nav',  # gaaltije.se
                    'art-layout-cell art-sidebar1',  # gaaltije.se
                    'clearfix breadcrumbsAndSocial noindex',  # udir.no
                    'complexDocumentBottom',  # regjeringen.no
                    'container-widget-content',  # nrk.no
                    'container_full',
                    'content-body attribute-vnd.openxmlformats-'
                    'officedocument.spreadsheetml.sheet',  # samediggi.no
                    'content-language-links',  # metsa.fi
                    'content-wrapper',  # siida.fi
                    'control-group field-wrapper tiedotteet-period',  # metsa.fi
                    'control-group form-inline',  # metsa.fi
                    'documentInfoEm',
                    'documentPaging',
                    'documentPaging PagingBtm',  # regjeringen.no
                    'documentTop',  # regjeringen.no
                    'dotList',  # nord-salten.no
                    'dropmenudiv',  # calliidlagadus.org
                    'embedded-breadcrumbs',
                    'egavpi',  # calliidlagadus.org
                    'egavpi_fiskes',  # calliidlagadus.org
                    'esite_footer',
                    'esite_header',
                    'expandable',
                    'feedbackContainer noindex',  # udir.no
                    'file',  # samediggi.no
                    'fixed-header',
                    'g100 col fc s18 sg6 sg9 sg12 menu-reference',  # nrk.no
                    'g100 col fc s18 sg6 sg9 sg12 flow-reference',  # nrk.no
                    'g11 col fl s2 sl6 sl9 sl12 sl18',  # nrk.no
                    'g22 col fl s4 sl6 sl9 sl12 sl18 '
                    'article-header-sidebar',  # nrk.no
                    'g94 col fl s17 sl18 sg6 sg9 sg12 meta-widget',  # nrk.no
                    'globmenu',  # visitstetind.no
                    'grid cf',  # nrk.no
                    'help closed hidden-xs',
                    'historic-info',  # regjeringen.no
                    'historic-label',  # regjeringen.no
                    'imagecontainer',
                    'innholdsfortegenlse-child',
                    'inside',  # samas.no
                    'latestnews_uutisarkisto',
                    'ld-navbar',
                    'logo-links',  # metsa.fi
                    'meta',
                    'meta ui-helper-clearfix',  # nord-salten.no
                    'authors ui-helper-clearfix',  # nord-salten.no
                    'menu',  # visitstetind.no
                    'metaWrapper',
                    'moduletable_oikopolut',
                    'moduletable_etulinkki',  # www.samediggi.fi
                    'navigation',  # latex2html docs
                    'nav-menu nav-menu-style-dots',  # metsa.fi
                    'naviHlp',  # visitstetind.no
                    'noindex',  # ntfk
                    'nrk-globalfooter',  # nrk.no
                    'nrk-globalfooter-dk lp_globalfooter',  # nrk.no
                    'nrk-globalnavigation',  # nrk.no
                    'nrkno-share bulletin-share',  # nrk.no
                    'outer-column',
                    'page-inner',  # samas.no
                    'person_info',  # samediggi.no
                    'plug-teaser',  # nrk.no
                    'post-footer',
                    'printbutton-wrapper',  # 1177.se
                    'printContact',
                    'right',  # ntfk
                    'rightverticalgradient',  # udir.no
                    'sharebutton-wrapper',  # 1177.se
                    'sharing',
                    'sidebar',
                    'spalte300',  # osko.no
                    'span12 tiedotteet-show',
                    'subpage-bottom',
                    'subfooter',  # visitstetind.no
                    'subnavigation',  # oikeusministeriö
                    'tabbedmenu',
                    'tipformcontainer',  # tysfjord.kommune.no
                    'tipsarad mt6 selfClear',
                    'titlepage',
                    'toc-placeholder',  # 1177.se
                    'toc',
                    'tools',  # arran.no
                    'topic',  # samediggi.no
                    'trail',  # siida.fi
                    'translations',  # siida.fi
                    'upperheader',
                ],
                'id': [
                    'print-logo-wrapper',  # 1177.se
                    'AreaLeft',
                    'AreaLeftNav',
                    'AreaRight',
                    'AreaTopRight',
                    'AreaTopSiteNav',
                    'NAVbreadcrumbContainer',
                    'NAVfooterContainer',
                    'NAVheaderContainer',
                    'NAVrelevantContentContainer',
                    'NAVsubmenuContainer',
                    'PageFooter',
                    'PageLanguageInfo',  # regjeringen.no
                    'PrintDocHead',
                    'SamiDisclaimer',
                    'ShareArticle',
                    'WIPSELEMENT_CALENDAR',  # learoevierhtieh.no
                    'WIPSELEMENT_HEADING',  # learoevierhtieh.no
                    'WIPSELEMENT_MENU',  # learoevierhtieh.no
                    'WIPSELEMENT_MENURIGHT',  # learoevierhtieh.no
                    'WIPSELEMENT_NEWS',  # learoevierhtieh.no
                    'WebPartZone1',  # lansstyrelsen.se
                    'aa',
                    'andrenyheter',  # tysfjord.kommune.no
                    'article_footer',
                    'attached',  # tysfjord.kommune.no
                    'blog-pager',
                    'bottom',  # samas.no
                    'breadcrumbs-bottom',
                    'bunninformasjon',  # unginordland
                    'chatBox',
                    'chromemenu',  # calliidlagadus.org
                    'crumbs',  # visitstetind.no
                    'ctl00_AccesskeyShortcuts',  # lansstyrelsen.se
                    'ctl00_ctl00_ArticleFormContentRegion_'
                    'ArticleBodyContentRegion_ctl00_'
                    'PageToolWrapper',  # 1177.se
                    'ctl00_ctl00_ArticleFormContentRegion_'
                    'ArticleBodyContentRegion_ctl03_'
                    'PageToolWrapper',  # 1177.se
                    'ctl00_Cookies',  # lansstyrelsen.se
                    'ctl00_FullRegion_CenterAndRightRegion_HitsControl_'
                    'ctl00_FullRegion_CenterAndRightRegion_Sorting_sortByDiv',
                    'ctl00_LSTPlaceHolderFeedback_'
                    'editmodepanel31',  # lansstyrelsen.se
                    'ctl00_LSTPlaceHolderSearch_'
                    'SearchBoxControl',  # lansstyrelsen.se
                    'ctl00_MidtSone_ucArtikkel_ctl00_ctl00_ctl01_divRessurser',
                    'ctl00_MidtSone_ucArtikkel_ctl00_divNavigasjon',
                    'ctl00_PlaceHolderMain_EditModePanel1',  # lansstyrelsen.se
                    'ctl00_PlaceHolderTitleBreadcrumb_'
                    'DefaultBreadcrumb',  # lansstyrelsen.se
                    'ctl00_TopLinks',  # lansstyrelsen.se
                    'deleModal',
                    'document-header',
                    'errorMessageContainer',  # nord-salten.no
                    'final-footer-wrapper',  # 1177.se
                    'flu-vaccination',  # 1177.se
                    'footer',  # forrest, too, tysfjord.kommune.no
                    'footer-wrapper',
                    'frontgallery',  # visitstetind.no
                    'header',
                    'headerBar',
                    'headWrapper',  # osko.no
                    'hoyre',  # unginordland
                    'innholdsfortegnelse',  # regjeringen.no
                    'leftMenu',
                    'leftPanel',
                    'leftbar',  # forrest (divvun and giellatekno sites)
                    'leftcol',  # new samediggi.no
                    'leftmenu',
                    'main_navi_main',  # www.samediggi.fi
                    'mainContentBookmark',  # udir.no
                    'mainsidebar',  # arran.no
                    'menu',
                    'mobile-header',
                    'mobile-subnavigation',
                    'murupolku',  # www.samediggi.fi
                    'nav-content',
                    'navbar',  # tysfjord.kommune.no
                    'ncFooter',  # visitstetind.no
                    'ntfkFooter',  # ntfk
                    'ntfkHeader',  # ntfk
                    'ntfkNavBreadcrumb',  # ntfk
                    'ntfkNavMain',  # ntfk
                    'pageFooter',
                    'path',  # new samediggi.no, tysfjord.kommune.no
                    'phone-bar',  # 1177.se
                    'publishinfo',  # 1177.se
                    'readspeaker_button1',
                    'right-wrapper',  # ndla
                    'rightAds',
                    'rightCol',
                    'rightside',
                    's4-leftpanel',  # ntfk
                    'searchBox',
                    'searchHitSummary',
                    'sendReminder',
                    'share-article',
                    'sidebar',  # finlex.fi, too
                    'sidebar-wrapper',
                    'sitemap',
                    'skipLinks',  # udir.no
                    'skiplink',  # tysfjord.kommune.no
                    'spraakvelger',  # osko.no
                    'subfoote',  # visitstetind.no
                    'submenu',  # nord-salten.no
                    'svid10_49531bad1412ceb82564aea',  # ostersund.se
                    'svid10_6ba9fa711d2575a2a7800024318',  # jll.se
                    'svid10_6c1eb18a13ec7d9b5b82ee7',  # ostersund.se
                    'svid10_b0dabad141b6aeaf101229',  # ostersund.se
                    'svid10_49531bad1412ceb82564af3',  # ostersund.se
                    'svid10_6ba9fa711d2575a2a7800032145',  # jll.se
                    'svid10_6ba9fa711d2575a2a7800032151',  # jll.se
                    'svid10_6ba9fa711d2575a2a7800024344',  # jll.se
                    'svid10_6ba9fa711d2575a2a7800032135',  # jll.se
                    'svid10_6c1eb18a13ec7d9b5b82ee3',  # ostersund.se
                    'svid10_6c1eb18a13ec7d9b5b82edf',  # ostersund.se
                    'svid10_6c1eb18a13ec7d9b5b82edd',  # ostersund.se
                    'svid10_6c1eb18a13ec7d9b5b82eda',  # ostersund.se
                    'svid10_6c1eb18a13ec7d9b5b82ed5',  # ostersund.se
                    'svid12_6ba9fa711d2575a2a7800032140',  # jll.se
                    'theme-area-label-wrapper',  # 1177.se
                    'tipafriend',
                    'tools',  # arran.no
                    'topHeader',  # nord-salten.no
                    'topMenu',
                    'topUserMenu',
                    'top',  # arran.no
                    'topnav',  # tysfjord.kommune.no
                    'toppsone',  # unginordland
                    'vedleggogregistre',  # regjeringen.no
                    'venstre',  # unginordland
                ],
            },
            'p': {
                'class': [
                    'WebPartReadMoreParagraph',
                    'breadcrumbs',
                    'langs',  # oahpa.no
                    'art-page-footer',  # gaaltije.se
                ],
                'id': [
                    'skip-link',  # samas.no
                ],
            },
            'ul': {
                'id': [
                    'AreaTopLanguageNav',
                    'AreaTopPrintMeny',
                    'skiplinks',  # umo.se
                ],
                'class': [
                    'QuickNav',
                    'article-tools',
                    'article-universe-list',  # nrk.no
                    'byline',
                    'chapter-index',  # lovdata.no
                    'footer-nav',  # lovdata.no
                    'hidden',  # unginordland
                ],
            },
            'span': {
                'id': ['skiplinks'],
                'class': [
                    'K-NOTE-FOTNOTE',
                    'graytext',  # svenskakyrkan.se
                    'breadcrumbs pathway',  # gaaltije.se
                ],
            },
            'a': {
                'id': [
                    'ctl00_IdWelcome_ExplicitLogin',  # ntfk
                    'leftPanelTab',
                ],
                'class': [
                    'addthis_button_print',  # ntfk
                    'mainlevel',
                    'share-paragraf',  # lovdata.no
                    'mainlevel_alavalikko',  # www.samediggi.fi
                    'sublevel_alavalikko',  # www.samediggi.fi
                    'skip-link',  # 1177.se
                    'toggle-link expanded',  # 1177.se
                ],
                'name': [
                    'footnote-ref',  # footnotes in running text
                ],
            },
            'td': {
                'id': [
                    "hakulomake",  # www.samediggi.fi
                    "paavalikko_linkit",  # www.samediggi.fi
                    'sg_oikea',  # www.samediggi.fi
                    'sg_vasen',  # www.samediggi.fi
                ],
                'class': [
                    "modifydate",
                ],
            },
            'tr': {
                'id': [
                    "sg_ylaosa1",
                    "sg_ylaosa2",
                ]
            },
            'header': {
                'id': [
                    'header',  # umo.se
                ],
                'class': [
                    'nrk-masthead-content cf',  # nrk.no
                    'pageHeader ',  # regjeringen.no
                ],
            },
            'section': {
                'class': [
                    'section-theme-sub-nav',  # 1177.se
                    'span3',  # samernas.se
                    'tree-menu current',  # umo.se
                    'tree-menu',  # umo.se
                ],
            },
            'table': {
                'id': [
                    'Table_01',
                ],
            },
        }

        namespace = {'html': 'http://www.w3.org/1999/xhtml'}
        for tag, attribs in six.iteritems(unwanted_classes_ids):
            for key, values in six.iteritems(attribs):
                for value in values:
                    search = ('.//{}[@{}="{}"]'.format(tag, key, value))
                    for unwanted in self.soup.xpath(
                            search, namespaces=namespace):
                        unwanted.getparent().remove(unwanted)

    def add_p_around_text(self):
        """Add p around text after an hX element."""
        stop_tags = ['p', 'h3', 'h2', 'div', 'table']
        for tag in self.soup.xpath('.//body/*'):
            if tag.tail is not None and tag.tail.strip() != '':
                paragraph = etree.Element('p')
                paragraph.text = tag.tail
                tag.tail = None
                for next_element in iter(tag.getnext, None):
                    if next_element.tag in stop_tags:
                        break
                    paragraph.append(next_element)

                tag_parent = tag.getparent()
                tag_parent.insert(tag_parent.index(tag) + 1, paragraph)

        # br's are not allowed right under body in XHTML:
        for elt in self.soup.xpath('.//body/br'):
            elt.tag = 'p'
            elt.text = ' '

    def center2div(self):
        """Convert center to div in tidy style."""
        for center in self.soup.xpath('.//center'):
            center.tag = 'div'
            center.set('class', 'c1')

    def body_i(self):
        """Wrap bare elements inside a p element."""
        for tag in ['a', 'i', 'em', 'u', 'strong', 'span']:
            for body_tag in self.soup.xpath('.//body/{}'.format(tag)):
                paragraph = etree.Element('p')
                bi_parent = body_tag.getparent()
                bi_parent.insert(bi_parent.index(body_tag), paragraph)
                paragraph.append(body_tag)

    @staticmethod
    def handle_font_text(font_elt):
        """Incorporate font.text into correct element.

        Args:
            font_elt (etree.Element): a font element.
        """
        font_parent = font_elt.getparent()
        font_index = font_parent.index(font_elt)

        if font_elt.text is not None:
            if font_index > 0:
                previous_element = font_parent[font_index - 1]
                if previous_element.tail is not None:
                    previous_element.tail += font_elt.text
                else:
                    previous_element.tail = font_elt.text
            else:
                if font_elt.text is not None:
                    if font_parent.text is not None:
                        font_parent.text += font_elt.text
                    else:
                        font_parent.text = font_elt.text

    @staticmethod
    def handle_font_children(font_elt):
        """Incorporate font children into correct element.

        Args:
            font_elt (etree.Element): a font element.
        """
        font_parent = font_elt.getparent()
        font_index = font_parent.index(font_elt)

        for position, font_child in enumerate(font_elt, start=font_index):
            if font_elt.tail is not None:
                if font_elt[-1].tail is not None:
                    font_elt[-1].tail += font_elt.tail
                else:
                    font_elt[-1].tail = font_elt.tail
            font_parent.insert(position, font_child)

    @staticmethod
    def handle_font_tail(font_elt):
        """Incorporate font.tail into correct element.

        Args:
            font_elt (etree.Element): a font element.
        """
        font_parent = font_elt.getparent()
        font_index = font_parent.index(font_elt)
        previous_element = font_parent[font_index - 1]

        if font_elt.tail is not None:
            if font_index > 0:
                if previous_element.tail is not None:
                    previous_element.tail += font_elt.tail
                else:
                    previous_element.tail = font_elt.tail
            else:
                if font_parent.text is not None:
                    font_parent.text += font_elt.tail
                else:
                    font_parent.text = font_elt.tail

    def remove_font(self):
        """Remove font elements, incorporate content into it's parent."""
        for font_elt in reversed(list(self.soup.iter('{*}font'))):
            self.handle_font_text(font_elt)

            if len(font_elt) > 0:
                self.handle_font_children(font_elt)
            else:
                self.handle_font_tail(font_elt)

            font_elt.getparent().remove(font_elt)

    def body_text(self):
        """Wrap bare text inside a p element."""
        body = self.soup.find('.//body')

        if body.text is not None:
            paragraph = etree.Element('p')
            paragraph.text = body.text
            body.text = None
            body.insert(0, paragraph)

    def convert2xhtml(self, content):
        """Clean up the html document.

        Destructively modifies self.soup, trying
        to create strict xhtml for xhtml2corpus.xsl
        """
        c_content = self.remove_cruft(content)

        c_clean = self.superclean(c_content)
        print(c_clean.split('\n')[0])
        self.soup = html.document_fromstring(c_clean)
        print(type(self.soup))
        print(self.soup.tag)
        self.remove_empty_class()
        self.remove_empty_p()
        self.remove_elements()
        self.remove_font()
        self.add_p_around_text()
        self.center2div()
        self.body_i()
        self.body_text()
        self.simplify_tags()
        self.fix_spans_as_divs()

        util.print_frame(etree.tostring(self.soup, encoding='unicode', pretty_print=True))

        return self.soup
