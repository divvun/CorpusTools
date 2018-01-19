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
import six
from lxml import html

from corpustools import (adder, text_cat, util, crawler)


class SamediggiNoPage(object):
    """Save a samediggi.no page to the corpus."""

    def __init__(self, url):
        """Initialise the SamediggiNoPage class."""
        result = requests.get(url)
        self.parsed_url = six.moves.urllib.parse.urlparse(result.url)
        self.tree = html.document_fromstring(result.content)

        self.ok_netlocs = [
            'www.sametinget.no', 'www.samediggi.no', 'www.saemiedigkie.no',
            'www.samedigge.no'
        ]

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
            for a in self.tree.xpath('.//ul[@id="languageList"]/li/a[@href]')
        ]

    @property
    def print_url(self):
        """Get the print url of the document."""
        print_link = self.tree.find('.//link[@media="print"]')

        if print_link is not None:
            url = print_link.get('href')

            return six.moves.urllib.parse.urlunparse(
                (self.parsed_url.scheme, self.parsed_url.netloc, url, '', '',
                 ''))

    @property
    def lang(self):
        """Return the language of the file."""
        uff = {}
        uff['no-bokmaal'] = 'nob'
        uff['sma-NO'] = 'sma'
        uff['sme-NO'] = 'sme'
        uff['smj-no'] = 'smj'
        content_language = self.tree.find('.//meta[@name="Content-language"]')

        if content_language is not None:
            return uff[content_language.get('content')]
        else:
            util.print_frame('no language {}'.format(self.url.encode('utf8')))

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
                    for uff in self.ok_netlocs:
                        if uff in href:
                            add = True
                            links.add(href)

                    if not add:
                        util.print_frame(debug=href + '\n')

        return links

    @property
    def body_text(self):
        """Get all the text inside 'body'."""
        body = self.tree.find('.//body')

        return ' '.join(body.xpath('.//text()'))


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

    def crawl_page(self, link):
        """Collect links from a page."""
        self.visited_links.add(link)
        util.print_frame(debug=link.encode('utf8'))
        try:
            orig_page = SamediggiNoPage(link)
        except requests.exceptions.SSLError as error:
            util.print_frame(debug=str(error))
        else:
            self.visited_links.add(orig_page.url)
            self.unvisited_links = self.unvisited_links.union(orig_page.links)

            util.print_frame(debug=orig_page.url.encode('utf8') + '\n')

            return orig_page

    def crawl_site(self):
        """Crawl samediggi.no."""
        while self.unvisited_links:
            link = self.unvisited_links.pop()

            if link not in self.visited_links:
                self.crawl_pageset(link)

    def crawl_pageset(self, link):
        """Crawl a pageset that link gives us."""
        parallel_pages = []

        found_saami = False
        orig_page = self.crawl_page(link)
        if orig_page is not None:
            body_lang = self.languageguesser.classify(
                orig_page.body_text, langs=self.langs)
            if orig_page.lang == body_lang:
                if body_lang in [u'sme', u'sma', u'smj']:
                    found_saami = True
                parallel_pages.append((orig_page.print_url, orig_page.lang))
            else:
                uff = 'not same lang {}:\n orig: {} body: {}'.format(
                    orig_page.url.encode('utf8'), orig_page.lang, body_lang)
                util.print_frame(debug=uff)

            for parallel_link in orig_page.parallel_links:
                if parallel_link not in self.visited_links:
                    parallel_page = self.crawl_page(parallel_link)
                    if parallel_page is not None:
                        body_lang = self.languageguesser.classify(
                            parallel_page.body_text, langs=self.langs)
                        if parallel_page.lang == body_lang:
                            if body_lang in [u'sme', u'sma', u'smj']:
                                found_saami = True
                            util.print_frame()
                            parallel_pages.append((parallel_page.print_url,
                                                   parallel_page.lang))
                        else:
                            util.print_frame(
                                'not same lang {}:\n orig: {} body: {}'.format(
                                    parallel_page.url.encode('utf8'),
                                    parallel_page.lang, body_lang))

        if found_saami:
            self.save_pages(parallel_pages)
        else:
            util.print_frame(debug='No saami found')