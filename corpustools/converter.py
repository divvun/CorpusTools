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

"""This file contains classes to convert files to the Giella xml format."""


from __future__ import absolute_import, print_function

import argparse
import codecs
import collections
import distutils.dep_util
import distutils.spawn
import io
import logging
import multiprocessing
import os
import re
import sys
from copy import deepcopy

import epub
import six
from lxml import etree, html
from lxml.html import clean, html5parser
from odf.odf2xhtml import ODF2XHTML
from pydocx.export import PyDocXHTMLExporter
from pyth.plugins.rtf15.reader import Rtf15Reader
from pyth.plugins.xhtml.writer import XHTMLWriter

from corpustools import (argparse_version, ccat, corpuspath, decode,
                         errormarkup, text_cat, util, xslsetter)

here = os.path.dirname(__file__)


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class ConversionError(Exception):
    """Raise this exception when an error occurs in the converter module."""

    pass


class Converter(object):
    """Take care of data common to all Converter classes."""

    def __init__(self, filename, write_intermediate=False):
        """Initialise the Converter class.

        Arguments:
            filename: string containing the path to the file that should
            be converted
            write_intermediate: boolean which decides whether intermediate
            versions of the converted document should be written (used for
            debugging purposes).
        """
        codecs.register_error('mixed', self.mixed_decoder)
        self.names = corpuspath.CorpusPath(filename)
        self.write_intermediate = write_intermediate
        try:
            self.md = xslsetter.MetadataHandler(self.names.xsl, create=True)
        except xslsetter.XsltError as e:
            raise ConversionError(e)

        self.md.set_lang_genre_xsl()
        with util.ignored(OSError):
            os.makedirs(self.tmpdir)

    @property
    def dependencies(self):
        """Return files that converted files depend on."""
        return [self.names.orig, self.names.xsl]

    @property
    def standard(self):
        """Return a boolean indicating if the file is convertable."""
        return self.md.get_variable('conversion_status') == 'standard'

    @property
    def goldstandard(self):
        """Return a boolean indicating if the file is a gold standard doc."""
        return self.md.get_variable('conversion_status') == 'correct'

    def convert2intermediate(self):
        """Convert from original format to an intermediate corpus file."""
        raise NotImplementedError(
            'You have to subclass and override convert2intermediate')

    @staticmethod
    def get_dtd_location():
        """Return the path to the corpus dtd file."""
        return os.path.join(here, 'dtd/corpus.dtd')

    def validate_complete(self, complete):
        """Validate the complete document."""
        dtd = etree.DTD(Converter.get_dtd_location())

        if not dtd.validate(complete):
            with codecs.open(self.names.log, 'w', encoding='utf8') as logfile:
                logfile.write('Error at: {}'.format(
                    six.text_type(util.lineno())))
                for entry in dtd.error_log:
                    logfile.write('\n')
                    logfile.write(six.text_type(entry))
                    logfile.write('\n')
                util.print_element(complete, 0, 4, logfile)

            raise ConversionError(
                '{}: Not valid XML. More info in the log file: '
                '{}'.format(type(self).__name__, self.names.log))

    def maybe_write_intermediate(self, intermediate):
        """Write intermediate file.

        Used for debugging purposes.
        """
        if not self.write_intermediate:
            return
        im_name = self.names.orig + '.im.xml'
        with open(im_name, 'w') as im_file:
            im_file.write(etree.tostring(intermediate,
                                         encoding='utf8',
                                         pretty_print='True'))

    def transform_to_complete(self):
        """Combine the intermediate xml document with its medatata."""
        intermediate = self.convert2intermediate()
        self.fix_document(intermediate)
        self.maybe_write_intermediate(intermediate)
        try:
            xm = XslMaker(self.md.tree)
            complete = xm.transformer(intermediate)

            return complete.getroot()
        except etree.XSLTApplyError as e:
            with open(self.names.log, 'w') as logfile:
                logfile.write('Error at: {}'.format(
                    six.text_type(util.lineno())))
                for entry in e.error_log:
                    logfile.write(six.text_type(entry))
                    logfile.write('\n')

            raise ConversionError("Check the syntax in: {}".format(
                self.names.xsl))
        except etree.XSLTParseError as e:
            with open(self.names.log, 'w') as logfile:
                logfile.write('Error at: {}'.format(
                    six.text_type(util.lineno())))
                for entry in e.error_log:
                    logfile.write(six.text_type(entry))
                    logfile.write('\n')

            raise ConversionError("XSLTParseError in: {}\nError {}".format(
                self.names.xsl, str(e)))

    def convert_errormarkup(self, complete):
        """Convert error markup to xml."""
        if self.goldstandard:
            try:
                em = errormarkup.ErrorMarkup(self.names.orig)

                for element in complete.find('body'):
                    em.add_error_markup(element)
            except IndexError as e:
                with open(self.names.log, 'w') as logfile:
                    logfile.write('Error at: {}'.format(
                        six.text_type(util.lineno())))
                    logfile.write("There is a markup error\n")
                    logfile.write("The error message: ")
                    logfile.write(six.text_type(e))
                    logfile.write("\n\n")
                    logfile.write("This is the xml tree:\n")
                    logfile.write(etree.tostring(complete,
                                                 encoding='utf8',
                                                 pretty_print=True))
                    logfile.write('\n')

                raise ConversionError(
                    u"Markup error. More info in the log file: {}".format(
                        self.names.log))

    def fix_document(self, complete):
        """Fix a misc. issues found in converted document."""
        fixer = DocumentFixer(complete)

        fixer.fix_newstags()
        fixer.soft_hyphen_to_hyph_tag()
        self.md.set_variable('wordcount', fixer.calculate_wordcount())

        if not self.goldstandard:
            fixer.detect_quotes()

        # The above line adds text to hyph, fix that
        for hyph in complete.iter('hyph'):
            hyph.text = None

        if (self.md.get_variable('mainlang') in
                ['sma', 'sme', 'smj', 'smn', 'sms', 'nob', 'fin', 'swe',
                 'nno', 'dan', 'fkv', 'sju', 'sje', 'mhr']):
            try:
                fixer.fix_body_encoding(self.md.get_variable('mainlang'))
            except UserWarning as error:
                util.print_frame(error)
                util.print_frame(self.names.orig)

    mixed_to_unicode = {
        'e4': u'ä',
        '85': u'…',            # u'\u2026' ... character.
        '96': u'–',            # u'\u2013' en-dash
        '97': u'—',            # u'\u2014' em-dash
        '91': u"‘",            # u'\u2018' left single quote
        '92': u"’",            # u'\u2019' right single quote
        '93': u'“',            # u'\u201C' left double quote
        '94': u'”',            # u'\u201D' right double quote
        '95': u"•"             # u'\u2022' bullet
    }

    def mixed_decoder(self, decode_error):
        """Convert text to unicode."""
        badstring = decode_error.object[decode_error.start:decode_error.end]
        badhex = badstring.encode('hex')
        repl = self.mixed_to_unicode.get(badhex, u'\ufffd')
        if repl == u'\ufffd':   # � unicode REPLACEMENT CHARACTER
            logger.warn("Skipped bad byte \\x{}, seen in {}".format(
                badhex, self.names.orig))
        return repl, (decode_error.start + len(repl))

    def make_complete(self, languageGuesser):
        """Make a complete Giella xml file.

        Combine the intermediate Giella xml file and the metadata into
        a complete Giella xml file.
        Fix the character encoding
        Detect the languages in the xml file
        """
        complete = self.transform_to_complete()
        self.validate_complete(complete)
        self.convert_errormarkup(complete)
        ld = LanguageDetector(complete, languageGuesser)
        ld.detect_language()

        return complete

    @staticmethod
    def has_content(complete):
        """Find out if the xml document has any content.

        Arguments:
            complete: a etree element containing the converted document.

        Returns:
            The length of the content in complete.
        """
        xml_printer = ccat.XMLPrinter(all_paragraphs=True,
                                      hyph_replacement=None)
        xml_printer.etree = etree.ElementTree(complete)

        return len(xml_printer.process_file().getvalue())

    def write_complete(self, languageguesser):
        """Write the complete converted document to disk.

        Arguments:
            languageguesser: a text.Classifier
        """
        if distutils.dep_util.newer_group(
                self.dependencies, self.names.converted):
            with util.ignored(OSError):
                os.makedirs(os.path.dirname(self.names.converted))

            if self.standard or self.goldstandard:
                complete = self.make_complete(languageguesser)

                if self.has_content(complete):
                    with open(self.names.converted, 'wb') as converted:
                        converted.write(etree.tostring(complete,
                                                       encoding='utf8',
                                                       pretty_print='True'))
                else:
                    logger.error("{} has no text".format(self.names.orig))

    @property
    def tmpdir(self):
        """Return the directory where temporary files should be placed."""
        return os.path.join(self.names.pathcomponents.root, 'tmp')

    @property
    def corpusdir(self):
        """Return the directory where the corpus directory is."""
        return self.names.pathcomponents.root

    def extract_text(self, command):
        """Extract the text from a document.

        :command: a list containing the command and the arguments sent to
        ExternalCommandRunner.
        :returns: byte string containing the output of the program
        """
        runner = util.ExternalCommandRunner()
        runner.run(command, cwd=self.tmpdir)

        if runner.returncode != 0:
            with open(self.names.log, 'w') as logfile:
                print('stdout\n{}\n'.format(runner.stdout), file=logfile)
                print('stderr\n{}\n'.format(runner.stderr), file=logfile)
                raise ConversionError(
                    '{} failed. More info in the log file: {}'.format(
                        command[0], self.names.log))

        return runner.stdout

    def handle_syntaxerror(self, e, lineno, invalid_input):
        """Handle an xml syntax error.

        Arguments:
            e: an exception
            lineno: the line number in this module where the error happened.
            invalid_input: a string containing the invalid input.
        """
        with open(self.names.log, 'w') as logfile:
            logfile.write('Error at: {}'.format(lineno))
            for entry in e.error_log:
                logfile.write('\n{}: {} '.format(
                    six.text_type(entry.line), six.text_type(entry.column)))
                try:
                    logfile.write(entry.message)
                except ValueError:
                    logfile.write(entry.message.encode('latin1'))

                logfile.write('\n')

            if six.PY3:
                logfile.write(invalid_input)
            else:
                logfile.write(invalid_input.encode('utf8'))

        raise ConversionError(
            "{}: log is found in {}".format(type(self).__name__, self.names.log))


class HTMLContentConverter(object):
    """Convert html documents to the Giella xml format."""

    def superclean(self, content):
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

        try:
            return cleaner.clean_html(content)
        except etree.ParserError as e:
            raise ConversionError(six.text_type(e))

    def remove_cruft(self, content):
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
            "| //menu",
            )
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
            "    ]",
            )
        for elt in spans_as_divs:
            elt.tag = 'div'

        ps_as_divs = self.soup.xpath(
            "//p[descendant::div]",
            )
        for elt in ps_as_divs:
            elt.tag = 'div'

        lists_as_divs = self.soup.xpath(
            "//*[( child::ul or child::ol ) "
            "and ( self::ul or self::ol )"
            "    ]",
            )
        for elt in lists_as_divs:
            elt.tag = 'div'

    def remove_empty_p(self):
        """Remove empty p elements."""
        ps = self.soup.xpath(
            '//p',
            )

        for elt in ps:
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
                    'documentInfoEm',
                    'documentPaging',
                    'documentPaging PagingBtm',  # regjeringen.no
                    'documentTop',  # regjeringen.no
                    'dotList',  # nord-salten.no
                    'dropmenudiv',  # calliidlagadus.org
                    'egavpi',  # calliidlagadus.org
                    'egavpi_fiskes',  # calliidlagadus.org
                    'expandable',
                    'feedbackContainer noindex',  # udir.no
                    'fixed-header',
                    'g100 col fc s18 sg6 sg9 sg12 menu-reference',  # nrk.no
                    'g100 col fc s18 sg6 sg9 sg12 flow-reference',  # nrk.no
                    'g11 col fl s2 sl6 sl9 sl12 sl18',  # nrk.no
                    'g22 col fl s4 sl6 sl9 sl12 sl18 article-header-sidebar',  # nrk.no
                    'g94 col fl s17 sl18 sg6 sg9 sg12 meta-widget',  # nrk.no
                    'globmenu',  # visitstetind.no
                    'grid cf',  # nrk.no
                    'help closed hidden-xs',
                    'historic-info',  # regjeringen.no
                    'historic-label',  # regjeringen.no
                    'imagecontainer',
                    'innholdsfortegenlse-child',
                    'latestnews_uutisarkisto',
                    'ld-navbar',
                    'meta',
                    'meta ui-helper-clearfix',  # nord-salten.no
                    'authors ui-helper-clearfix',  # nord-salten.no
                    'menu',  # visitstetind.no
                    'metaWrapper',
                    'moduletable_oikopolut',
                    'moduletable_etulinkki',  # www.samediggi.fi
                    'naviHlp',  # visitstetind.no
                    'noindex',  # ntfk
                    'nrk-globalfooter',  # nrk.no
                    'nrk-globalfooter-dk lp_globalfooter',  # nrk.no
                    'nrk-globalnavigation',  # nrk.no
                    'nrkno-share bulletin-share',  # nrk.no
                    'outer-column',
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
                    'subfooter',  # visitstetind.no
                    'tabbedmenu',
                    'tipformcontainer',  # tysfjord.kommune.no
                    'tipsarad mt6 selfClear',
                    'titlepage',
                    'toc-placeholder',  # 1177.se
                    'toc',
                    'tools',  # arran.no
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
                    'PageLanguageInfo',   # regjeringen.no
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
                    'main_navi_main',           # www.samediggi.fi
                    'mainContentBookmark',  # udir.no
                    'mainsidebar',  # arran.no
                    'menu',
                    'murupolku',                # www.samediggi.fi
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
                'id': [
                    'skiplinks'
                ],
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
        }

        ns = {'html': 'http://www.w3.org/1999/xhtml'}
        for tag, attribs in six.iteritems(unwanted_classes_ids):
            for key, values in six.iteritems(attribs):
                for value in values:
                    search = ('.//{}[@{}="{}"]'.format(tag, key, value))
                    for unwanted in self.soup.xpath(search, namespaces=ns):
                        unwanted.getparent().remove(unwanted)

    def add_p_around_text(self):
        """Add p around text after an hX element."""
        stop_tags = [
            'p',
            'h3',
            'h2',
            'div',
            'table']
        for h in self.soup.xpath(
                './/body/*',
                ):
            if h.tail is not None and h.tail.strip() != '':
                p = etree.Element('p')
                p.text = h.tail
                h.tail = None
                for next_element in iter(h.getnext, None):
                    if next_element.tag in stop_tags:
                        break
                    p.append(next_element)

                h_parent = h.getparent()
                h_parent.insert(h_parent.index(h) + 1, p)

        # br's are not allowed right under body in XHTML:
        for elt in self.soup.xpath(
                './/body/br',
                ):
            elt.tag = 'p'
            elt.text = ' '

    def center2div(self):
        """Convert center to div in tidy style."""
        for center in self.soup.xpath(
                './/center',
                ):
            center.tag = 'div'
            center.set('class', 'c1')

    def body_i(self):
        """Wrap bare elements inside a p element."""
        for tag in ['a', 'i', 'em', 'u', 'strong', 'span']:
            for bi in self.soup.xpath(
                    './/body/{}'.format(tag),
                    ):
                p = etree.Element('p')
                bi_parent = bi.getparent()
                bi_parent.insert(bi_parent.index(bi), p)
                p.append(bi)

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
        body = self.soup.find(
            './/body')

        if body.text is not None:
            p = etree.Element('p')
            p.text = body.text
            body.text = None
            body.insert(0, p)

    def convert2xhtml(self, content):
        """Clean up the html document.

        Destructively modifies self.soup, trying
        to create strict xhtml for xhtml2corpus.xsl
        """
        c_content = self.remove_cruft(content)

        c_clean = self.superclean(c_content)
        self.soup = html.document_fromstring(c_clean)
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

        return self.soup


class HTMLConverter(Converter):
    """Convert html pages to Giella xml documents."""

    @property
    def content(self):
        """Return the content of the html doc as a string.

        Returns:
            a string containing the html document.
        """
        for encoding in ['utf-8', 'windows-1252', 'latin1']:
            try:
                with codecs.open(self.names.orig, encoding=encoding) as f:
                    return etree.tostring(
                        html.document_fromstring(
                            self.remove_declared_encoding(f.read())
                        ),
                        encoding='unicode'
                    )
            except UnicodeDecodeError:
                pass

        raise ConversionError('HTML error'.format(self.names.orig))

    def remove_declared_encoding(self, content):
        """Remove declared decoding.

        lxml explodes if we send a decoded Unicode string with an
        xml-declared encoding
        http://lxml.de/parsing.html#python-unicode-strings

        Arguments:
            content: a string containing the html document.

        Returns:
            a string where the declared decoding is removed.
        """
        xml_encoding_declaration_re = re.compile(
            r"^<\?xml [^>]*encoding=[\"']([^\"']+)[^>]*\?>[ \r\n]*",
            re.IGNORECASE)

        return re.sub(xml_encoding_declaration_re, "", content)

    def convert2xhtml(self):
        """Convert html document to a cleaned up xhtml document.

        Returns:
            a cleaned up xhtml document as an etree element.
        """
        converter = HTMLContentConverter()

        return converter.convert2xhtml(self.content)

    @staticmethod
    def replace_bare_text_in_body_with_p(body):
        """Replace bare text in body with a p elemnt."""
        if body.text is not None and body.text.strip() != '':
            new_p = etree.Element('p')
            new_p.text = body.text
            body.text = None
            body.insert(0, new_p)

    @staticmethod
    def add_p_instead_of_tail(intermediate):
        """Convert tail in list and p to a p element."""
        for element in ['list', 'p']:
            for found_element in intermediate.findall('.//' + element):
                if found_element.tail is not None and found_element.tail.strip() != '':
                    new_p = etree.Element('p')
                    new_p.text = found_element.tail
                    found_element.tail = None
                    found_element.addnext(new_p)

    def convert2intermediate(self):
        """Convert the original document to the Giella xml format.

        The resulting xml is stored in intermediate
        """
        converter_xsl = os.path.join(here, 'xslt/xhtml2corpus.xsl')

        html_xslt_root = etree.parse(converter_xsl)
        transform = etree.XSLT(html_xslt_root)

        intermediate = transform(self.convert2xhtml())

        self.replace_bare_text_in_body_with_p(intermediate.find('.//body'))
        self.add_p_instead_of_tail(intermediate)

        return intermediate.getroot()


class RTFConverter(HTMLConverter):
    """Convert rtf documents to the Giella xml format."""

    @property
    def content(self):
        """Convert the content of an rtf file to xhtml.

        Returns:
            A string containing the xhtml version of the rtf file.
        """
        with open(self.names.orig, "rb") as rtf_document:
            content = rtf_document.read()
            try:
                pyth_doc = Rtf15Reader.read(
                    io.BytesIO(content.replace(b'fcharset256', b'fcharset255')))
                return six.text_type(XHTMLWriter.write(
                    pyth_doc, pretty=True).read(), encoding='utf8')
            except UnicodeDecodeError:
                raise ConversionError('Unicode problems in {}'.format(
                    self.names.orig))


class OdfConverter(HTMLConverter):
    """Convert odf documents to the Giella xml format."""

    @property
    def content(self):
        """Convert the content of an odf file to xhtml.

        Returns:
            A string contaning the xhtml version of the odf file.
        """
        generatecss = False
        embedable = True
        odhandler = ODF2XHTML(generatecss, embedable)
        try:
            return odhandler.odf2xhtml(six.text_type(self.names.orig))
        except TypeError as e:
            raise ConversionError('Error: {}'.format(e))


class DocxConverter(HTMLConverter):
    """Convert docx documents to the Giella xml format."""

    @property
    def content(self):
        """Convert the content of a docx file to xhtml.

        Returns:
            A string contaning the xhtml version of the docx file.
        """
        return PyDocXHTMLExporter(self.names.orig).export()

    def remove_elements(self):
        """Remove some docx specific html elements."""
        super(DocxConverter, self).remove_elements()

        unwanted_classes_ids = {
            'a': {
                'name': [
                    'footnote-ref',  # footnotes in running text
                ],
            }
        }
        ns = {'html': 'http://www.w3.org/1999/xhtml'}
        for tag, attribs in six.iteritems(unwanted_classes_ids):
            for key, values in six.iteritems(attribs):
                for value in values:
                    search = ('.//html:{}[starts-with(@{}, "{}")]'.format(
                        tag, key, value))
                    for unwanted in self.soup.xpath(search, namespaces=ns):
                        unwanted.getparent().remove(unwanted)


class EpubConverter(HTMLConverter):
    """Convert epub documents to the Giella xml format.

    Epub files are zip files that contain text in xhtml files. This class reads
    all xhtml files found in this archive. The body element of these files are
    converted to div elements, and appended inside a new body element.

    It is possible to filter away ranges of elements from this new xhtml file.
    These ranges consist pairs of xpath paths, specified inside the metadata
    file that belongs to this epub file.
    """

    @staticmethod
    def read_chapter(chapter):
        """Read the contents of a epub_file chapter.

        Args:
            chapter (epub.BookChapter): the chapter of an epub file

        Returns:
            str: The contents of a chapter

        Raises:
            ConversionException
        """
        try:
            return etree.fromstring(chapter.read())
        except KeyError as e:
            raise ConversionError(e)

    def chapters(self):
        """Get the all linear chapters of the epub book.

        Yields:
            etree._Element: The body of an xhtml file found in the epub file.
        """
        book = epub.Book(epub.open_epub(self.names.orig))

        for chapter in book.chapters:
            chapterbody = self.read_chapter(chapter).find(
                '{http://www.w3.org/1999/xhtml}body')
            chapterbody.tag = '{http://www.w3.org/1999/xhtml}div'
            yield chapterbody

    @property
    def content(self):
        """Append all chapter bodies as divs to an html file.

        Returns:
            a string containing the content of all xhtml files
            found in the epub file.
        """
        mainbody = etree.Element('{http://www.w3.org/1999/xhtml}body')

        for chapterbody in self.chapters():
            mainbody.append(chapterbody)

        html = etree.Element('{http://www.w3.org/1999/xhtml}html')
        html.append(etree.Element('{http://www.w3.org/1999/xhtml}head'))
        html.append(mainbody)

        if self.md.skip_elements:
            for pairs in self.md.skip_elements:
                self.remove_range(pairs[0], pairs[1], html)

        return etree.tostring(html, encoding='unicode')

    @staticmethod
    def remove_siblings_shorten_path(parts, content, preceding=False):
        """Remove all siblings before or after an element.

        Args:
            parts (list of str): a xpath path split on /
            content (etree._Element): an xhtml document
            preceding (bool): When True, iterate through the preceding siblings
                of the found element, otherwise iterate throughe the following
                siblings.

        Returns:
            list of str: the path to the parent of parts.
        """
        path = '/'.join(parts)
        found = content.find(
            path, namespaces={'html': 'http://www.w3.org/1999/xhtml'})
        parent = found.getparent()
        for sibling in found.itersiblings(preceding=preceding):
            parent.remove(sibling)

        return parts[:-1]

    def shorten_longest_path(self, path1, path2, content):
        """Remove elements from the longest path.

        If starts is longer than ends, remove the siblings following starts,
        shorten starts with one step (going to the parent). If starts still is
        longer than ends, remove the siblings following the parent. This is
        done untill starts and ends are of equal length.

        If on the other hand ends is longer than starts, remove the siblings
        preceding ends, then shorten ends (going to its parent).

        Args:
            path1 (str): path to first element
            path2 (str): path to second element
            content (etree._Element): xhtml document, where elements are
                removed.

        Returns:
            tuple of list of str: paths to the new start and end element, now
                with the same length.
        """
        starts, ends = path1.split('/'), path2.split('/')

        while len(starts) > len(ends):
            starts = self.remove_siblings_shorten_path(starts, content)

        while len(ends) > len(starts):
            ends = self.remove_siblings_shorten_path(
                ends, content, preceding=True)

        return starts, ends

    def remove_trees_with_unequal_parents(self, path1, path2, content):
        """Remove tree nodes that do not have the same parents.

        While the parents in starts and ends are unequal (that means that
        starts and ends belong in different trees), remove elements
        following starts and preceding ends. Shorten the path to the parents
        of starts and ends and remove more elements if needed. starts and
        ends are of equal length.

        Args:
            path1 (str): path to first element
            path2 (str): path to second element
            content (etree._Element): xhtml document, where elements are
                removed.

        Returns:
            tuple of list of str: paths to the new start and end element.
        """
        starts, ends = self.shorten_longest_path(path1, path2, content)

        while starts[:-1] != ends[:-1]:
            starts = self.remove_siblings_shorten_path(starts, content)
            ends = self.remove_siblings_shorten_path(
                ends, content, preceding=True)

        return starts, ends

    def remove_trees_with_equal_parents(self, starts, ends, content):
        """Remove tree nodes that have the same parents.

        Now that the parents of starts and ends are equal, remove the last
        trees of nodes between starts and ends (if necessary).

        Args:
            starts (list of str): path to first element
            ends (list of str): path to second element
            content (etree._Element): xhtml document, where elements are
                removed.
        """
        deepest_start = content.find(
            '/'.join(starts), namespaces={'html': 'http://www.w3.org/1999/xhtml'})
        deepest_end = content.find(
            '/'.join(ends), namespaces={'html': 'http://www.w3.org/1999/xhtml'})
        parent = deepest_start.getparent()
        for sibling in deepest_start.itersiblings():
            if sibling == deepest_end:
                break
            else:
                parent.remove(sibling)

    @staticmethod
    def remove_first_element(path1, content):
        """Remove the first element in the range.

        Args:
            path1 (str): path to the first element to remove.
            content (etree._Element): the xhtml document that should
                be altered.
        """
        first_start = content.find(
            path1, namespaces={'html': 'http://www.w3.org/1999/xhtml'})
        first_start.getparent().remove(first_start)

    def remove_range(self, path1, path2, content):
        """Remove a range of elements from an xhtml document.

        Args:
            path1 (str): path to first element
            path2 (str): path to second element
            content (etree._Element): xhtml document
        """
        starts, ends = self.remove_trees_with_unequal_parents(path1, path2,
                                                              content)
        self.remove_trees_with_equal_parents(starts, ends, content)
        self.remove_first_element(path1, content)


class DocConverter(HTMLConverter):
    """Convert Microsoft Word documents to the Giella xml format."""

    @property
    def content(self):
        """Convert a doc file to xhtml.

        Returns:
            A string containing the xhtml version of the doc file.
        """
        command = ['wvHtml',
                   os.path.realpath(self.names.orig),
                   '-']
        try:
            return self.extract_text(command).decode('utf8')
        except:
            return self.extract_text(command).decode('windows-1252')

    def fix_wv_output(self):
        u"""Fix headers in the docx xhtml output.

        Examples of headings:

        h1:
        <html:ul>
            <html:li value="2">
                <html:p/>
                <html:div align="left" name="Overskrift 1">
                    <html:p>
                        <html:b>
                            <html:span>
                                OVTTASKASOLBMOT
                            </html:span>
                        </html:b>
                    </html:p>
                </html:div>
            </html:li>
        </html:ul>

        h2:
        <html:ol type="1">
            <html:li value="1">
                <html:p/>
                <html:div align="left" name="Overskrift 2">
                    <html:p>
                        <html:b>
                            <html:span>
                                čoahkkáigeassu
                            </html:span>
                        </html:b>
                    </html:p>
                </html:div>
            </html:li>
        </html:ol>

        <html:ol type="1">
            <html:ol type="1">
                <html:li value="2">
                    <html:p/>
                    <html:div align="left" name="Overskrift 2">
                        <html:p>
                            <html:b>
                                <html:span>
                                    Ulbmil ja váldooasit
                                </html:span>
                            </html:b>
                        </html:p>
                    </html:div>
                </html:li>
            </html:ol>
        </html:ol>

        h3:
        <html:ol type="1">
            <html:ol type="1">
                <html:ol type="1">
                    <html:li value="1">
                        <html:p>
                        </html:p>
                        <html:div align="left" name="Overskrift 3">
                            <html:p>
                                <html:b>
                                    <html:span>
                                        Geaográfalaš
                                    </html:span>
                                </html:b>
                                <html:b>
                                    <html:span>
                                        ráddjen
                                    </html:span>
                                </html:b>

                            </html:p>
                        </html:div>
                    </html:li>

                </html:ol>
            </html:ol>
        </html:ol>

        <html:ol type="1">
            <html:ol type="1">
                <html:ol type="1">
                    <html:li value="1">
                        <html:p>
                        </html:p>
                        <html:div align="left" name="Overskrift 3">
                            <html:p>
                                <html:b>
                                <html:span>Iskanjoavku ja sámegielaga
                                definišuvdn</html:span></html:b>
                                <html:b><html:span>a</html:span></html:b>
                            </html:p>
                        </html:div>
                    </html:li>

                </html:ol>
            </html:ol>
        </html:ol>

        h4:
        <html:div align="left" name="Overskrift 4">
            <html:p>
                <html:b>
                    <html:i>
                        <html:span>
                            Mildosat:
                        </html:span>
                    </html:i>
                </html:b>
            </html:p>
        </html:div>

        """
        pass


class DocumentFixer(object):
    """Fix the content of a Giella xml document.

    Receive a stringified etree from one of the raw converters,
    replace ligatures, fix the encoding and return an etree with correct
    characters
    """

    def __init__(self, document):
        """Initialise the DocumentFixer class."""
        self.root = document

    def get_etree(self):
        """Get the root of the xml document."""
        return self.root

    def compact_ems(self):
        """Compact consecutive em elements into a single em if possible."""
        word = re.compile(u'\w+', re.UNICODE)
        for element in self.root.iter('p'):
            if len(element.xpath('.//em')) > 1:
                lines = []
                for em in element.iter('em'):
                    next = em.getnext()
                    if (next is not None and next.tag == 'em' and
                            (em.tail is None or not word.search(em.tail))):
                        if em.text is not None:
                            lines.append(em.text.strip())
                        em.getparent().remove(em)
                    else:
                        if em.text is not None:
                            lines.append(em.text.strip())
                        em.text = ' '.join(lines)
                        if em.tail is not None:
                            em.tail = ' {}'.format(em.tail)
                        lines = []

    def soft_hyphen_to_hyph_tag(self):
        """Replace soft hyphen chars with hyphen tags."""
        for element in self.root.iter('p'):
            self.replace_shy(element)

    def replace_shy(self, element):
        """Replace shy with a hyph element.

        Arguments:
            element: an etree element
        """
        for child in element:
            self.replace_shy(child)

        text = element.text
        if text is not None:
            parts = text.split(u'­')
            if len(parts) > 1:
                element.text = parts[0]
                for x, part in enumerate(parts[1:]):
                    hyph = etree.Element('hyph')
                    hyph.tail = part
                    element.insert(x, hyph)

        text = element.tail
        if text is not None:
            parts = text.split(u'­')
            if len(parts) > 1:
                element.tail = parts[0]
                for part in parts[1:]:
                    hyph = etree.Element('hyph')
                    hyph.tail = part
                    element.getparent().append(hyph)

    def insert_spaces_after_semicolon(self):
        """Insert space after semicolon where needed."""
        irritating_words_regex = re.compile(u'(govv(a|en|ejeaddji):)([^ ])',
                                            re.UNICODE | re.IGNORECASE)
        for child in self.root.find('.//body'):
            self.insert_space_after_semicolon(child, irritating_words_regex)

    def insert_space_after_semicolon(self, element, irritating_words_regex):
        """Insert space after words needing it.

        Arguments:
            element: an etree element
            irritating_words_regex: regex
        """
        if element.text is not None:
            element.text = irritating_words_regex.sub(r'\1 \3', element.text)
        for child in element:
            self.insert_space_after_semicolon(child, irritating_words_regex)
        if element.tail is not None:
            element.tail = irritating_words_regex.sub(r'\1 \3', element.tail)

    def replace_ligatures(self):
        """Replace unwanted chars."""
        replacements = {
            u"[dstrok]": u"đ",
            u"[Dstrok]": u"Đ",
            u"[tstrok]": u"ŧ",
            u"[Tstrok]": u"Ŧ",
            u"[scaron]": u"š",
            u"[Scaron]": u"Š",
            u"[zcaron]": u"ž",
            u"[Zcaron]": u"Ž",
            u"[ccaron]": u"č",
            u"[Ccaron]": u"Č",
            u"[eng": u"ŋ",
            u" ]": u"",
            u"Ď": u"đ",  # cough
            u"ď": u"đ",  # cough
            "\x03": u"",
            "\x04": u"",
            "\x07": u"",
            "\x08": u"",
            "\x0F": u"",
            "\x10": u"",
            "\x11": u"",
            "\x13": u"",
            "\x14": u"",
            "\x15": u"",
            "\x17": u"",
            "\x18": u"",
            "\x1A": u"",
            "\x1B": u"",
            "\x1C": u"",
            "\x1D": u"",
            "\x1E": u"",
            u"ﬁ": "fi",
            u"ﬂ": "fl",
            u"ﬀ": "ff",
            u"ﬃ": "ffi",
            u"ﬄ": "ffl",
            u"ﬅ": "ft",
        }

        for element in self.root.iter('p'):
            if element.text:
                for key, value in six.iteritems(replacements):
                    element.text = element.text.replace(key + ' ', value)
                    element.text = element.text.replace(key, value)

    def replace_bad_unicode(self):
        """Replace some chars in an otherwise 'valid utf-8' document.

        These chars e.g. 'valid utf-8' (don't give UnicodeDecodeErrors), but
        we still want to replace them to what they most likely were
        meant to be.

        :param content: a unicode string
        :returns: a cleaned up unicode string
        """
        # u'š'.encode('windows-1252') gives '\x9a', which sometimes
        # appears in otherwise utf-8-encoded documents with the
        # meaning 'š'
        replacements = [(u'\x9a', u'š'),
                        (u'\x8a', u'Š'),
                        (u'\x9e', u'ž'),
                        (u'\x8e', u'Ž')]
        for element in self.root.iter('p'):
            if element.text:
                element.text = util.replace_all(replacements, element.text)

    def fix_sms(self, element):
        """Replace invalid accents with valid ones for the sms language."""
        replacement_pairs = [
            (u'\u2019', u'\u02BC'),
            (u'\u0027', u'\u02BC'),
            (u'\u2032', u'\u02B9'),
            (u'\u00B4', u'\u02B9'),
            (u'\u0301', u'\u02B9'),
        ]

        for replacement_pair in replacement_pairs:
            if element.text:
                element.text = element.text.replace(replacement_pair[0],
                                                    replacement_pair[1])
            if element.tail:
                element.tail = element.tail.replace(replacement_pair[0],
                                                    replacement_pair[1])
        for child in element:
            self.fix_sms(child)

    def fix_body_encoding(self, mainlang):
        """Replace wrongly encoded saami chars with proper ones.

        Send a stringified version of the body into the EncodingGuesser class.
        It returns the same version, but with fixed characters.
        Parse the returned string, insert it into the document
        """
        self.replace_ligatures()

        body = self.root.find('body')
        bodyString = etree.tostring(body, encoding='unicode')
        body.getparent().remove(body)

        eg = decode.EncodingGuesser()
        encoding = eg.guess_body_encoding(bodyString)

        try:
            body = etree.fromstring(eg.decode_para(encoding, bodyString))
        except UnicodeEncodeError as error:
            util.print_frame('Detected encoding: {}'.format(encoding))
            util.print_frame(bodyString[:error.start], '\n')
            util.print_frame(bodyString[error.start:error.end],
                             ord(bodyString[error.start:error.start + 1]),
                             hex(ord(bodyString[error.start:error.start + 1])), '\n')
            util.print_frame(bodyString, '\n')
            raise UserWarning(str(error))
        self.root.append(body)

        if mainlang == 'sms':
            self.fix_sms(self.root.find('body'))

    def fix_title_person(self, encoding):
        """Fix encoding problems."""
        eg = decode.EncodingGuesser()

        title = self.root.find('.//title')
        if title is not None and title.text is not None:
            text = title.text

            text = text
            util.print_frame(encoding)
            title.text = eg.decode_para(encoding, text)

        persons = self.root.findall('.//person')
        for person in persons:
            if person is not None:
                lastname = person.get('lastname')

                if encoding == 'mac-sami_to_latin1':
                    lastname = lastname.replace(u'‡', u'á')
                    lastname = lastname.replace(u'Œ', u'å')

                person.set(
                    'lastname',
                    eg.decode_para(
                        encoding,
                        lastname))

                firstname = person.get('firstname')

                if encoding == 'mac-sami_to_latin1':
                    firstname = firstname.replace(u'‡', u'á')
                    firstname = firstname.replace(u'Œ', u'å')

                person.set(
                    'firstname',
                    eg.decode_para(
                        encoding,
                        firstname))

    @staticmethod
    def get_quote_list(text):
        """Get list of quotes from the given text.

        Arguments:
            text: string

        Returns:
            A list of span tuples containing indexes to quotes found in text.
        """
        unwanted = '[^:,!?.\s]'
        quote_regexes = [re.compile('"{0}.+?{0}"'.format(unwanted)),
                         re.compile(u'«.+?»'),
                         re.compile(u'“.+?”'),
                         re.compile(u'”{0}.+?{0}”'.format(unwanted)), ]
        quote_list = [m.span()
                      for quote_regex in quote_regexes
                      for m in quote_regex.finditer(text)]
        quote_list.sort()

        return quote_list

    @staticmethod
    def append_quotes(element, text, quote_list):
        """Append quotes to an element.

        Arguments:
            text: a string that contains the plain text of the element.
            quote_list: A list of span tuples containing indexes to quotes
            found in text.
        """
        for x in six.moves.range(0, len(quote_list)):
            span = etree.Element('span')
            span.set('type', 'quote')
            span.text = text[quote_list[x][0]:quote_list[x][1]]
            if x + 1 < len(quote_list):
                span.tail = text[quote_list[x][1]:quote_list[x + 1][0]]
            else:
                span.tail = text[quote_list[x][1]:]
            element.append(span)

    def detect_quote(self, element):
        """Insert span elements around quotes.

        Arguments:
            element: an etree element.
        """
        newelement = deepcopy(element)

        element.text = ''
        for child in element:
            child.getparent().remove(child)

        text = newelement.text
        if text:
            quote_list = self.get_quote_list(text)
            if quote_list:
                element.text = text[0:quote_list[0][0]]
                self.append_quotes(element, text, quote_list)
            else:
                element.text = text

        for child in newelement:
            if (child.tag == 'span' and child.get('type') == 'quote'):
                element.append(child)
            else:
                element.append(self.detect_quote(child))

            if child.tail:
                text = child.tail
                quote_list = self.get_quote_list(text)
                if quote_list:
                    child.tail = text[0:quote_list[0][0]]
                    self.append_quotes(element, text, quote_list)

        return element

    def detect_quotes(self):
        """Detect quotes in all paragraphs."""
        for paragraph in self.root.iter('p'):
            paragraph = self.detect_quote(paragraph)

    def calculate_wordcount(self):
        """Count the words in the file."""
        plist = [etree.tostring(paragraph, method='text', encoding='unicode')
                 for paragraph in self.root.iter('p')]

        return six.text_type(len(re.findall(u'\S+', ' '.join(plist))))

    def make_element(self, eName, text, attributes={}):
        """Make an xml element.

        :param eName: the name of the element
        :param text: the content of the element
        :param attributes: the elements attributes

        :returns: lxml.etree.Element
        """
        el = etree.Element(eName)
        for key in attributes:
            el.set(key, attributes[key])

        el.text = text

        return el

    def fix_newstags(self):
        """Convert newstags found in text to xml elements."""
        newstags = re.compile(
            u'(@*logo:|[\s+\']*@*\s*ingres+[\.:]*|.*@*.*bilde\s*\d*:|\W*(@|'
            u'LED|bilde)*tekst:|@*foto:|@fotobyline:|@*bildetitt:|'
            u'<pstyle:bilde>|<pstyle:ingress>|<pstyle:tekst>|'
            u'@*Samleingress:*|tekst/ingress:|billedtekst:|.@tekst:)', re.IGNORECASE)
        titletags = re.compile(
            u'\s*@m.titt[\.:]|\s*@*stikk:|Mellomtittel:|@*(stikk\.*|'
            u'under)titt(el)*:|@ttt:|\s*@*[utm]*[:\.]*tit+:|<pstyle:m.titt>|'
            u'undertittel:', re.IGNORECASE)
        headertitletags = re.compile(
            u'(\s*@*(led)*tittel:|\s*@*titt(\s\d)*:|@LEDtitt:|'
            u'<pstyle:tittel>|@*(hoved|over)titt(el)*:)', re.IGNORECASE)
        bylinetags = re.compile('(<pstyle:|\s*@*)[Bb]yline[:>]*\s*(\S+:)*',
                                re.UNICODE | re.IGNORECASE)
        boldtags = re.compile(u'@bold\s*:')

        header = self.root.find('.//header')
        unknown = self.root.find('.//unknown')

        for em in self.root.iter('em'):
            paragraph = em.getparent()
            if not len(em) and em.text:
                if bylinetags.match(em.text):
                    line = bylinetags.sub('', em.text).strip()
                    if unknown is not None:
                        person = etree.Element('person')
                        person.set('lastname', line)
                        person.set('firstname', '')
                        unknown.getparent().replace(unknown, person)
                        paragraph.getparent().remove(paragraph)
                elif titletags.match(em.text):
                    em.text = titletags.sub('', em.text).strip()
                    paragraph.set('type', 'title')
                elif newstags.match(em.text):
                    em.text = newstags.sub('', em.text).strip()

        for paragraph in self.root.iter('p'):
            if not len(paragraph) and paragraph.text:
                index = paragraph.getparent().index(paragraph)
                lines = []

                for line in paragraph.text.split('\n'):
                    if newstags.match(line):
                        if lines:
                            index += 1
                            paragraph.getparent().insert(
                                index,
                                self.make_element('p',
                                                  ' '.join(lines).strip(),
                                                  attributes=paragraph.attrib))
                        lines = []

                        lines.append(newstags.sub('', line))
                    elif bylinetags.match(line):
                        if lines:
                            index += 1
                            paragraph.getparent().insert(
                                index,
                                self.make_element('p',
                                                  ' '.join(lines).strip(),
                                                  attributes=paragraph.attrib))
                        line = bylinetags.sub('', line).strip()

                        if unknown is not None:
                            person = etree.Element('person')
                            person.set('lastname', line)
                            person.set('firstname', '')

                            unknown.getparent().replace(unknown, person)
                            unknown = None

                        lines = []
                    elif boldtags.match(line):
                        if lines:
                            index += 1
                            paragraph.getparent().insert(
                                index,
                                self.make_element('p',
                                                  ' '.join(lines).strip(),
                                                  attributes=paragraph.attrib))
                        line = boldtags.sub('', line).strip()
                        lines = []
                        index += 1
                        p = etree.Element('p')
                        p.append(self.make_element('em', line.strip(),
                                                   {'type': 'bold'}))
                        paragraph.getparent().insert(index, p)
                    elif line.startswith('@kursiv:'):
                        if lines:
                            index += 1
                            paragraph.getparent().insert(
                                index,
                                self.make_element('p',
                                                  ' '.join(lines).strip(),
                                                  attributes=paragraph.attrib))
                        line = line.replace('@kursiv:', '')
                        lines = []
                        index += 1
                        p = etree.Element('p')
                        p.append(self.make_element('em', line.strip(),
                                                   {'type': 'italic'}))
                        paragraph.getparent().insert(index, p)
                    elif headertitletags.match(line):
                        if lines:
                            index += 1
                            paragraph.getparent().insert(
                                index,
                                self.make_element('p',
                                                  ' '.join(lines).strip(),
                                                  attributes=paragraph.attrib))
                        line = headertitletags.sub('', line)
                        lines = []
                        index += 1
                        title = header.find('./title')
                        if title is not None and title.text is None:
                            title.text = line.strip()
                        paragraph.getparent().insert(
                            index,
                            self.make_element('p', line.strip(),
                                              {'type': 'title'}))
                    elif titletags.match(line):
                        if lines:
                            index += 1
                            paragraph.getparent().insert(
                                index,
                                self.make_element('p',
                                                  ' '.join(lines).strip(),
                                                  attributes=paragraph.attrib))
                        line = titletags.sub('', line)
                        lines = []
                        index += 1
                        paragraph.getparent().insert(
                            index,
                            self.make_element(
                                'p', line.strip(), {'type': 'title'}))
                    elif line == '' and lines:
                        index += 1
                        paragraph.getparent().insert(
                            index,
                            self.make_element('p',
                                              ' '.join(lines).strip(),
                                              attributes=paragraph.attrib))
                        lines = []
                    else:
                        lines.append(line)

                if lines:
                    index += 1
                    paragraph.getparent().insert(
                        index, self.make_element('p',
                                                 ' '.join(lines).strip(),
                                                 attributes=paragraph.attrib))

                paragraph.getparent().remove(paragraph)


class XslMaker(object):
    """Make an xsl file to combine with the intermediate xml file.

    To convert the intermediate xml to a fullfledged  giellatekno document
    a combination of three xsl files + the intermediate xml file is needed.
    """

    def __init__(self, xslfile):
        """Initialise the XslMaker class.

        Arguments:
            xslfile: a string containing the path to the xsl file.
        """
        self.filexsl = xslfile

    @property
    def logfile(self):
        """Return the name of the logfile."""
        return self.filename + '.log'

    @property
    def xsl(self):
        """Return an etree of the xsl file.

        Raises:
            In case of an xml syntax error, raise ConversionException.
        """
        preprocessXsl = etree.parse(
            os.path.join(here, 'xslt/preprocxsl.xsl'))
        preprocessXslTransformer = etree.XSLT(preprocessXsl)

        common_xsl_path = os.path.join(
            here, 'xslt/common.xsl').replace(' ', '%20')

        return preprocessXslTransformer(
            self.filexsl,
            commonxsl=etree.XSLT.strparam('file://{}'.format(common_xsl_path)))

    @property
    def transformer(self):
        """Make an etree.XSLT transformer.

        Raises:
            raise a ConversionException in case of invalid XML in the xsl file.
        Returns:
            an etree.XSLT transformer
        """
        return etree.XSLT(self.xsl)


class LanguageDetector(object):
    """Detect and set the languages of a document."""

    def __init__(self, document, languageGuesser):
        """Initialise the LanguageDetector class.

        Arguments:
            document: an etree element.
            languageGuesser: a text_cat.Classifier.
        """
        self.document = document
        self.languageGuesser = languageGuesser

    @property
    def inlangs(self):
        """Return the predifined possible languages of the document."""
        inlangs = [language.get('{http://www.w3.org/XML/1998/namespace}'
                                'lang')
                   for language in self.document.findall(
            'header/multilingual/language')]
        if inlangs:
            inlangs.append(self.mainlang)

        return inlangs

    @property
    def mainlang(self):
        """Get the mainlang of the file."""
        return self.document.\
            attrib['{http://www.w3.org/XML/1998/namespace}lang']

    def set_paragraph_language(self, paragraph):
        """Set xml:lang of paragraph.

        Extract the text outside the quotes, use this text to set
        language of the paragraph.
        Set the language of the quotes in the paragraph.
        """
        if paragraph.get('{http://www.w3.org/XML/1998/namespace}lang') is None:
            paragraph_text = self.remove_quote(paragraph)
            if self.languageGuesser is not None:
                lang = self.languageGuesser.classify(paragraph_text,
                                                     langs=self.inlangs)
                if lang != self.mainlang:
                    paragraph.set('{http://www.w3.org/XML/1998/namespace}lang',
                                  lang)

                self.set_span_language(paragraph)

        return paragraph

    def set_span_language(self, paragraph):
        """Set xml:lang of span element."""
        for element in paragraph.iter("span"):
            if element.get("type") == "quote":
                if element.text is not None:
                    lang = self.languageGuesser.classify(element.text,
                                                         langs=self.inlangs)
                    if lang != self.mainlang:
                        element.set(
                            '{http://www.w3.org/XML/1998/namespace}lang',
                            lang)

    def remove_quote(self, paragraph):
        """Extract all text except the one inside <span type='quote'>."""
        text = ''
        for element in paragraph.iter():
            if (element.tag == 'span' and
                    element.get('type') == 'quote' and
                    element.tail is not None):
                text = text + element.tail
            else:
                if element.text is not None:
                    text = text + element.text
                if element.tail is not None:
                    text = text + element.tail

        return text

    def detect_language(self):
        """Detect language in all the paragraphs in self.document."""
        if self.document.find('header/multilingual') is not None:
            for paragraph in self.document.iter('p'):
                self.set_paragraph_language(paragraph)


