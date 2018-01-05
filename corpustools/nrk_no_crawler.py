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
"""This file contains routines to crawl nrk.no containing saami text."""

import json
import os
import sys
from collections import defaultdict

import dateutil.parser
import feedparser
import requests
import six
from lxml import etree, html

from corpustools import adder, text_cat, util, xslsetter


class NrkSmeCrawler(object):
    """Collect Northern Saami pages from nrk.no.

    Attributes:
        language_guesser (text_cat.Classifier): guess language from a given
            string
        goaldir (str): the directory where the working copy of the corpus is
        corpus_adder (adder.AddToCorpus): the working horse, adds urls to
            the corpus
        tags (dict of str to str): numerical tags that point to a specific
            topic on nrk.no
        invalid_links (set of str): all links containing 'gammelsystem'
        counter (collections.defaultdict of int): collect interesting
            statistics, such number of links visited and fetched links within
            a tag
        fetched_links (set of str): links to articles that have already been
            fetched
        authors (set of str): authors of articles
    """
    language_guesser = text_cat.Classifier(None)
    goaldir = six.text_type(os.getenv('GTBOUND'))
    corpus_adder = adder.AddToCorpus(goaldir, 'sme', 'news/nrk.no')
    tags = defaultdict(str)
    invalid_links = set()
    counter = defaultdict(int)
    authors = set()

    def __init__(self):
        """Initialise the NrkSmeCrawler class."""
        self.fetched_links = self.get_fetched_links(self.corpus_adder.goaldir)
        self.fetched_links.add(
            'https://www.nrk.no/sapmi/utgir-ny-kristen-cd-med-joik-og-sang'
            '-1.13050654')

    def guess_lang(self, address):
        """Guess the language of the address element.

        Arguments:
            address (html.Element): An element where interesting text is found

        Returns:
            str containing the language of the text
        """
        # This bytes hoopla is done because the text
        # comes out as utf8 encoded as latin1 …
        try:
            text = bytes(
                address.find('.//p[@class="plug-preamble"]').text,
                encoding='latin1')
        except AttributeError:
            text = bytes(
                address.find('.//h2[@class="title"]').text, encoding='latin1')

        return self.language_guesser.classify(text)

    def get_tag_page_trees(self, tag):
        """Fetch topic pages containing links to articles.

        By using the page_links_template, one can fetch `quantity` number of
        links to articles within `tag` at a time.

        Attributes:
            page_links_template: a url to a specific topic in nrk.no.
            quantity (int): the number of links to fetch a time
            limit (int): max number of links that one tries to fetch

        Arguments:
            tag (str): a numerical tag, pointing to a specific topic on nrk.no

        Yields:
            lxml.html.HtmlElement: a parsed html document.
        """
        page_links_template = ('https://www.nrk.no/serum/api/render/{tag}?'
                               'size=18&perspective=BRIEF&alignment=AUTO&'
                               'classes=surrogate-content&'
                               'display=false&arrangement.offset={offset}&'
                               'arrangement.quantity={quantity}&'
                               'arrangement.repetition=PATTERN&'
                               'arrangement.view[0].perspective=BRIEF&'
                               'arrangement.view[0].size=6&'
                               'arrangement.view[0].alignment=LEFT&'
                               'paged=SIMPLE')
        quantity = 10
        limit = 10000

        for offset in range(0, limit, quantity):
            print('.', end='')
            sys.stdout.flush()
            try:
                result = requests.get(
                    page_links_template.format(
                        tag=tag, offset=offset, quantity=quantity))
            except requests.exceptions.ConnectionError:
                util.note(u'Connection error when fetching {}'.format(tag))
                break
            else:
                try:
                    yield html.document_fromstring(result.content)
                except etree.ParserError:
                    util.note(u'No more articles in tag: «{}»'.format(
                        self.tags[tag]))
                    break

    def interesting_links(self, tag):
        """Find interesting pages inside a topic.

        Arguments:
            tag (str): a numerical tag pointing to a specific topic.

        Yields:
            str: a url to an nrk.no article
        """
        for tree in self.get_tag_page_trees(tag):
            for address in tree.xpath('//a[@class="autonomous lp_plug"]'):
                self.counter[tag + '_total'] += 1
                href = address.get('href')

                if 'systemtest' in href:
                    self.invalid_links.add(href)
                if ('systemtest' not in href and href not in self.fetched_links
                        and self.guess_lang(address) == 'sme'):
                    self.counter[tag + '_fetched'] += 1
                    yield href

    @staticmethod
    def pick_tags(path):
        """Find tags in an nrk.no article.

        Tags potientially contain more Northern Sámi articles.

        Arguments:
            path (str): path to an nrk.no article

        Yields:
            tuple of str: a numerical tag, used internally by nrk.no to point
                to a specific topic and a short description of the topic.
        """
        article = html.parse(path)

        for address in article.xpath(
                '//a[@class="universe widget reference article-universe-link '
                'universe-teaser skin-border skin-text lp_universe_link"]'):
            href = address.get('href')
            yield href[href.rfind('-') + 1:], address[0].tail.strip()

    def crawl_tag(self, tag, tagname):
        """Look for articles in nrk.no tags.

        Arguments:
            tag (str): an internal nrk.no tag
        """
        if tag not in self.tags:
            util.note(u'Fetching articles from «{}»'.format(tagname))
            self.tags[tag] = tagname
            for href in self.interesting_links(tag):
                self.add_nrk_article(href)

            self.counter['total'] += self.counter[tag + '_total']
            self.counter['fetched'] += self.counter[tag + '_fetched']

    def add_nrk_article(self, href):
        """Copy an article to the working copy.

        Arguments:
            href (str): a url to an nrk article.
        """
        self.fetched_links.add(href)
        try:
            path = self.corpus_adder.copy_url_to_corpus(href)
            self.add_metadata(path)
        except (requests.exceptions.TooManyRedirects,
                adder.AdderError) as error:
            util.note(href)
            util.note(error)

    def crawl_site(self):
        """Fetch Northern Saami pages from nrk.no."""
        self.crawl_oanehaccat()
        self.crawl_existing_tags()
        self.crawl_authors()
        self.corpus_adder.add_files_to_working_copy()
        self.report()

    def find_nrk_files(self):
        """Find all nrk.no files."""
        for root, _, files in os.walk(self.corpus_adder.goaldir):
            for file_ in files:
                if file_.endswith('.html'):
                    yield os.path.join(root, file_)

    def crawl_existing_tags(self):
        """Crawl all tags found in nrk.no documents."""
        for nrk_file in self.find_nrk_files():
            for additional_tag, tag_name in self.pick_tags(nrk_file):
                self.crawl_tag(additional_tag, tag_name)

    def crawl_oanehaccat(self):
        """Crawl short news, provided by an rss feed.

        This feed only contains Northern Sámi articles.
        """
        util.note('Fetching articles from {}'.format('oanehaččat'))
        self.tags['oanehaččat'] = 'oanehaččat'
        for entry in feedparser.parse(
                'https://www.nrk.no/sapmi/oanehaccat.rss').entries:
            self.counter['oanehaččat_total'] += 1
            if entry['link'] not in self.fetched_links:
                self.counter['oanehaččat_fetched'] += 1
                self.add_nrk_article(entry['link'])

        self.counter['total'] += self.counter['oanehaččat_total']
        self.counter['fetched'] += self.counter['oanehaččat_fetched']

    def handle_search_hits(self, hits):
        for hit in hits:
            if hit['url'] not in self.fetched_links and hit.get(
                    'description') and self.language_guesser.classify(
                        hit['description']) == 'sme':
                self.counter['authors_fetched'] += 1
                self.add_nrk_article(hit['url'])

    def crawl_authors(self):
        """Search for authors on nrk.no.

        Not all articles have are represented under the tags found, so
        a search on author names is also done.
        """
        self.tags['authors'] = 'authors'
        for nrk_file in self.find_nrk_files():
            self.counter['nrk_file'] += 1
            article = html.parse(nrk_file)
            for author_body in article.xpath('.//div[@class="author__body"]'):
                self.counter['author__body'] += 1
                author_name = author_body.find('./a[@class="author__name"]')
                if author_name is not None:
                    self.authors.add(
                        author_name.text.strip().split()[-1].lower())
                    self.counter['name'] += 1

        for author_parts in self.authors:
            index = 0
            while True:
                try:
                    hits = self.get_search_page(
                        'https://www.nrk.no/sok/?format=json&scope=nrkno&filter=nrkno&q={}&from={}'.
                        format(author_parts, str(index)))
                    self.handle_search_hits(hits['hits'])
                    if index > int(hits['total']):
                        break
                    index += 20
                    util.print_frame(author_parts, hits['from'], hits['total'],
                                    len(hits['hits']))
                except json.decoder.JSONDecodeError as error:
                    util.note(str(error))
                    util.note(hits)
                    break

    @staticmethod
    def get_search_page(search_link):
        result = requests.get(search_link)
        return json.loads(result.content.decode('utf8'))

    def report(self):
        """Print a report on what was found."""
        print('{} invalid links.'.format(len(self.invalid_links)))
        for invalid_link in self.invalid_links:
            print(invalid_link)
        print()
        print('Searched through {} tags'.format(len(self.tags)))
        print('Fetched {fetched} pages'.format(**self.counter))
        for tag in self.tags:
            if self.counter[tag + '_fetched']:
                print(
                    'Fetched {} articles from category {} from nrk.no'.format(
                        self.counter[tag + '_fetched'], self.tags[tag]))

    @staticmethod
    def valid_authors(article):
        """Find authors with the correct roles.

        Arguments:
            article (etree.Element): The parsed html document.

        Yields:
            tuple of str
        """
        for author_role in article.xpath('.//span[@class="author__role"]'):
            text = author_role.text.strip()
            if text is not None and (text.startswith('Journ')
                                     or text.startswith('Komm')
                                     or text.startswith('Arti')):
                parts = author_role.getprevious().text.strip().split()

                yield parts

    def add_metadata(self, path):
        """Get metadata from the nrk.no article.

        Arguments:
            path (str): path to the nrk.no article
        """
        article = html.parse(path)
        metadata = xslsetter.MetadataHandler(path + '.xsl')

        for twitter in article.xpath('//a[@class="author__twitter"]'):
            twitter.getparent().remove(twitter)

        for count, author_parts in enumerate(
                self.valid_authors(article), start=1):
            metadata.set_variable('author' + str(count) + '_ln',
                                  author_parts[-1])
            metadata.set_variable('author' + str(count) + '_fn', ' '.join(
                author_parts[:-1]))

        time = article.find('//time[@itemprop="datePublished"]')
        if time is None:
            time = article.find('//time[@class="relative bulletin-time"]')
        date = dateutil.parser.parse(time.get('datetime'))
        metadata.set_variable('year', date.year)

        metadata.set_variable('publisher', 'NRK')
        metadata.set_variable('license_type', 'standard')
        metadata.write_file()

    @staticmethod
    def get_fetched_links(path):
        """Find fetched links.

        Arguments:
            path (str): path to the directory where nrk articles are found.

        Returns:
            set of strings, where the strings are links to the articles.
        """
        return {
            xslsetter.MetadataHandler(os.path.join(
                root, file_)).get_variable('filename')
            for root, _, files in os.walk(path) for file_ in files
            if file_.endswith('.xsl')
        }
