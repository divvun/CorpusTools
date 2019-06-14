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
#   Copyright © 2013-2019 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""This file contains routines to crawl sites containing saami text."""

from __future__ import absolute_import, print_function

import os
import re

import requests
import six
from lxml import etree

from corpustools import (adder, corpuspath, crawler, namechanger, text_cat,
                         versioncontrol)


class SamediggiNoPage(object):
    """Save a samediggi.no page to the corpus."""
    address_re = re.compile(r'/\w')
    unwanted_endings = ('.pdf', '.jpg', '.docx', '.xslx', '.csv', '.pptx',
                        '.eps')

    def __init__(self, result):
        """Initialise the SamediggiNoPage class."""
        self.result = result
        self.url = result.url
        self.parsed_url = six.moves.urllib.parse.urlparse(self.url)
        self.tree = etree.HTML(result.text)
        self.content = self.make_new_content()
        self.corpuspath = corpuspath.CorpusPath(
            os.path.join(
                os.getenv('GTFREE'), 'orig', self.lang,
                'admin/sd/samediggi.no',
                namechanger.normalise_filename(
                    adder.url_to_filename(self.result))))
        self.set_initial_metadata()

    def make_new_content(self):
        """Extract only the content that is interesting from the web page."""
        content = etree.Element('body')
        for xpath_directive in ['.//div[@class="newsIntroBox"]', './/article']:
            for element in self.tree.xpath(xpath_directive):
                content.append(etree.fromstring(etree.tostring(element)))

        return content

    def set_initial_metadata(self):
        """Extract metadata from the web page."""
        self.corpuspath.metadata.set_variable(
            'title',
            self.tree.find('.//title').text.strip())
        self.corpuspath.metadata.set_variable('filename', self.url)
        self.corpuspath.metadata.set_variable('genre', 'admin')
        self.corpuspath.metadata.set_variable('mainlang', self.lang)
        self.corpuspath.metadata.set_variable('license_type', 'free')
        if self.lang != 'nob':
            self.corpuspath.metadata.set_variable('translated_from', 'nob')
        time = self.tree.find('.//time')
        if time is not None:
            self.corpuspath.metadata.set_variable(
                'year',
                self.tree.find('.//time').get('datetime')[:4])

    @property
    def basename(self):
        """Get the basename of the corpus filename."""
        return os.path.basename(self.corpuspath.orig)

    def sanity_test(self):
        """Check if the pages seem to have the expected structure."""
        if not self.parallel_links:
            with open('errorpage.html', 'wb') as errorpage:
                errorpage.write(
                    etree.tostring(
                        self.tree, encoding='utf8', pretty_print=True))
            raise SystemExit(
                'The format of links to parallel documents has changed {}'.
                format(self.parsed_url))
        if self.lang is None:
            raise SystemExit('Language format has changed.')

    @property
    def parallel_links(self):
        """Get links to the parallels of this document."""
        return [
            'https:{}'.format(a.get("href")) for a in self.tree.xpath(
                './/li[@class="itemLanguage"]/div/ul/li/a[@href]')
        ]

    @property
    def saveable(self):
        """Check if the content of this file is worth saving."""
        return self.result.ok and len(
            self.content) and len(self.body_text.split()) > 40

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

    def is_valid_address(self, href):
        """Check if this is an address that should be crawled."""
        match = self.address_re.match(href)
        return (match and 'Sametingets-vedtak-1989-2004' not in href
                and not href.endswith(self.unwanted_endings))

    @property
    def links(self):
        """Get all the links found in a file."""
        return {
            six.moves.urllib.parse.urlunparse(
                (self.parsed_url.scheme, self.parsed_url.netloc,
                 address.get('href'), '', '', ''))
            for address in self.tree.xpath('.//a[@href]')
            if self.is_valid_address(address.get('href'))
        }

    @property
    def body_text(self):
        """Get all the text inside 'body'."""
        return ' '.join(self.content.xpath('.//text()'))

    def set_parallel_file(self, lang, name):
        """Update metadata info on parallel files."""
        self.corpuspath.metadata.set_parallel_text(lang, name)

    def save(self):
        """Save html and metadata."""
        with open(self.corpuspath.orig, 'wb') as xml:
            html = etree.Element('html')
            html.append(self.content)
            xml.write(etree.tostring(html, encoding='utf8', pretty_print=True))
        self.corpuspath.metadata.write_file()


class SamediggiNoCrawler(crawler.Crawler):
    """Crawl samediggi.no and save html documents to the corpus."""
    langs = [u'nob', u'sma', u'sme', u'smj']
    languageguesser = text_cat.Classifier()

    def __init__(self):
        """Initialise the SamediggiNoCrawler class."""
        super(SamediggiNoCrawler, self).__init__()
        self.unvisited_links.add(u'https://www.samediggi.no/')
        self.unvisited_links.add(u'https://www.sametinget.no/')
        self.unvisited_links.add(u'https://www.saemiedigkie.no/')
        self.unvisited_links.add(u'https://www.samedigge.no/')

        self.vcs = versioncontrol.vcs(self.goaldir)

    def crawl_page(self, link):
        """Collect links from a page."""
        self.visited_links.add(link)
        result = requests.get(link)

        if result.ok and 'html' in result.headers['content-type'].lower():
            orig_page = SamediggiNoPage(result)
            orig_page.sanity_test()
            self.visited_links.add(orig_page.url)
            self.unvisited_links = self.unvisited_links.union(orig_page.links)

            return orig_page

        return None

    def crawl_site(self):
        """Crawl samediggi.no."""
        while self.unvisited_links:
            link = self.unvisited_links.pop()

            if link not in self.visited_links:
                self.crawl_pageset(link)

    def add_page(self, page, parallel_pages):
        """Add a page to the list of parallel pages."""
        if page is not None and page.saveable:
            body_lang = self.languageguesser.classify(
                page.body_text, langs=self.langs)
            if page.lang == body_lang:
                if body_lang == 'nob':
                    parallel_pages.append(page)
                else:
                    parallel_pages.insert(0, page)

    @staticmethod
    def fix_parallel_info(parallel_pages):
        """Set the parallels for this set of parallel pages."""
        for parallel_page1 in parallel_pages:
            for parallel_page2 in parallel_pages:
                if parallel_page1 != parallel_page2:
                    parallel_page1.set_parallel_file(parallel_page2.lang,
                                                     parallel_page2.basename)

    def crawl_pageset(self, link):
        """Crawl a pageset that link gives us."""
        pages = []

        print(link)
        orig_page = self.crawl_page(link)
        if orig_page is not None:
            self.add_page(orig_page, pages)
            for parallel_link in orig_page.parallel_links:
                self.add_page(self.crawl_page(parallel_link), pages)

            if pages and pages[0].lang != 'nob':
                self.fix_parallel_info(pages)
                for parallel_page in pages:
                    print('\t{}'.format(parallel_page.corpuspath.orig))
                    parallel_page.save()
                    self.vcs.add(parallel_page.corpuspath.orig)
                    self.vcs.add(parallel_page.corpuspath.xsl)
                print()
