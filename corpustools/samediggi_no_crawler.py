# -*- coding:utf-8 -*-

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
#   Copyright © 2013-2018 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""This file contains routines to crawl sites containing saami text."""

from __future__ import absolute_import, print_function

import re

import requests
import os
import six
from lxml import html
from lxml import etree

from corpustools import (adder, corpuspath, text_cat, util, crawler, versioncontrol)


class SamediggiNoPage(object):
    """Save a samediggi.no page to the corpus."""

    def __init__(self, result):
        """Initialise the SamediggiNoPage class."""
        self.result = result
        self.parsed_url = six.moves.urllib.parse.urlparse(result.url)
        self.tree = html.document_fromstring(result.content)
        self.content = etree.Element('body')
        for xpath_directive in ['.//div[@class="newsIntroBox"]', './/article']:
            for element in self.tree.xpath(xpath_directive):
                self.content.append(element)

        self.ok_netlocs = [
            'www.sametinget.no', 'www.samediggi.no', 'www.saemiedigkie.no',
            'www.samedigge.no'
        ]
        self.corpuspath = corpuspath.CorpusPath(os.path.join(os.getenv('GTFREE'), 'orig', self.lang, 'admin/sd/samediggi.no', adder.url_to_filename(self.result)))

    @property
    def name(self):
        return self.corpuspath.name()

    def sanity_test(self):
        """Check if the pages seem to have the expected structure."""
        if not self.parallel_links:
            with open('errorpage.html', 'wb') as errorpage:
                errorpage.write(etree.tostring(self.tree, encoding='utf8', pretty_print=True))
            raise SystemExit(
                f'The format of links to parallel documents has changed {self.parsed_url}')
        if self.lang is None:
            raise SystemExit(
                'Language format has changed.')

    @property
    def url(self):
        """Get the url."""
        return self.parsed_url.geturl()

    @property
    def parallel_links(self):
        """Get links to the parallels of this document."""
        return [
            six.moves.urllib.parse.urlunparse((self.parsed_url.scheme,
                                               self.parsed_url.netloc,
                                               a.get('href'), '', '', ''))
            for a in self.tree.xpath('.//li[@class="itemLanguage"]/div/ul/li/a[@href]')
        ]

    @property
    def saveable(self):
        return self.result.ok and len(self.content)

    @property
    def lang(self):
        """Return the language of the file."""
        language_mapper = {
            'no-bokmaal': 'nob',
            'sma-NO': 'sma',
            'sme-NO': 'sme',
            'smj-NO': 'smj'
        }
        content_language = self.tree.find('.//meta[@name="Content-language"]')

        return language_mapper[content_language.get('content')]

    @property
    def links(self):
        """Get all the links found in a file."""
        links = set()
        for address in self.tree.findall('.//a'):
            href = address.get('href')
            if href is not None:
                if not re.search(
                        'tv.samediggi.no|^#|/rss/feed|switchlanguage|'
                        'facebook.com|'
                        'Web-tv|user/login|mailto|/Dokumenter|/Dokumeantta|'
                        '/Tjaatsegh|.pdf|.doc|.xls|/images/|/download/|'
                        '/Biejjielaahkoe|/Kalender|'
                        '/Dahpahusat|javascript|tel:', href):
                    if href.startswith('/'):
                        href = six.moves.urllib.parse.urlunparse(
                            (self.parsed_url.scheme, self.parsed_url.netloc,
                             href, '', '', ''))

                    add = False
                    for ok_netloc in self.ok_netlocs:
                        if ok_netloc in href:
                            add = True
                            links.add(href)

                    if not add:
                        util.print_frame(debug=href + '\n')

        return links

    @property
    def body_text(self):
        """Get all the text inside 'body'."""
        return ' '.join(self.content.xpath('.//text()'))

    def set_parallel_file(self, lang, name):
        self.corpuspath.metadata.set_parallel_text(lang, name)

    def save(self):
        with open(self.corpuspath.orig, 'wb') as xml:
            html = etree.Element('html')
            html.append(self.content)
            xml.write(etree.tostring(html, encoding='utf8', pretty_print=True))
        self.corpuspath.metadata.write_file()


class SamediggiNoCrawler(crawler.Crawler):
    """Crawl samediggi.no and save html documents to the corpus."""

    def __init__(self):
        """Initialise the SamediggiNoCrawler class."""
        super(SamediggiNoCrawler, self).__init__()
        self.unvisited_links.add(u'http://www.samediggi.no/')
        self.unvisited_links.add(u'http://www.sametinget.no/')
        self.unvisited_links.add(u'http://www.saemiedigkie.no/')
        self.unvisited_links.add(u'http://www.samedigge.no/')

        self.langs = [u'nob', u'sma', u'sme', u'smj']

        for iso in self.langs:
            self.corpus_adders[iso] = adder.AddToCorpus(
                self.goaldir, iso, u'admin/sd/samediggi.no')
        self.languageguesser = text_cat.Classifier()
        self.vcs = versioncontrol.vcs(self.goaldir)

    def crawl_page(self, link):
        """Collect links from a page."""
        self.visited_links.add(link)
        result = requests.get(link)

        if result.ok:
            orig_page = SamediggiNoPage(result)
            orig_page.sanity_test()
            self.visited_links.add(orig_page.url)
            self.unvisited_links = self.unvisited_links.union(orig_page.links)

            return orig_page

    def crawl_site(self):
        """Crawl samediggi.no."""
        x = 0
        while self.unvisited_links:
            x += 1
            link = self.unvisited_links.pop()

            if link not in self.visited_links:
                self.crawl_pageset(link)
            if x > 10:
                util.print_frame(f'Fetched {x} pages')
                break

    def add_page(self, orig_page, parallel_pages):
        if orig_page is not None and orig_page.saveable:
            body_lang = self.languageguesser.classify(
                orig_page.body_text, langs=self.langs)
            if orig_page.lang == body_lang:
                if body_lang == 'nob':
                    parallel_pages.append(orig_page)
                else:
                    parallel_pages.insert(0, orig_page)

    def fix_parallel_info(self, parallel_pages):
        for parallel_page1 in parallel_pages:
            for parallel_page2 in parallel_pages:
                if parallel_page1 != parallel_page2:
                    parallel_page1.set_parallel_file(parallel_page2.lang, parallel_page2.name)

    def crawl_pageset(self, link):
        """Crawl a pageset that link gives us."""
        parallel_pages = []

        orig_page = self.crawl_page(link)
        self.add_page(orig_page, parallel_pages)
        for parallel_link in orig_page.parallel_links:
            self.add_page(self.crawl_page(parallel_link), parallel_pages)

        if parallel_pages and parallel_pages[0].lang != 'nob':
            self.fix_parallel_info(parallel_pages)
            for parallel_page in parallel_pages:
                parallel_page.save()
                self.vcs.add(parallel_page.corpuspath.orig)
                self.vcs.add(parallel_page.corpuspath.xsl)
        else:
            util.print_frame(debug='No saami found')
