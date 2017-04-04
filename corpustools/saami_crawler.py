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
#   Copyright © 2013-2017 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

"""This file contains routines to crawl sites containing saami text."""


from __future__ import absolute_import, print_function

import argparse
import os
import re
import sys
from collections import defaultdict

import dateutil.parser
import feedparser
import requests
import six
from lxml import etree, html

from corpustools import (adder, argparse_version, namechanger, text_cat, util,
                         xslsetter)


class Crawler(object):
    """A base class to save downloaded files to the corpus."""

    def __init__(self):
        """Initialise the Crawler class."""
        self.goaldir = six.text_type(os.getenv('GTFREE'))
        self.unvisited_links = set()
        self.visited_links = set()
        self.download_links = set()
        self.corpus_adders = {}
        self.downloader = adder.UrlDownloader(os.path.join(
            self.goaldir, 'tmp'))

    def __del__(self):
        """Add all files to the corpus."""
        for (_, corpus_adder) in six.iteritems(self.corpus_adders):
            corpus_adder.add_files_to_working_copy()

    def save_pages(self, pages):
        """Write pages to disk.

        pages is a list of url, lang tuples
        """
        parallelpath = ''

        for (url, lang) in pages:
            try:
                (_, tmpname) = self.downloader.download(url)
            except adder.AdderError as error:
                util.print_frame(debug=str(error) + '\n')
            else:
                normalised_name = namechanger.normalise_filename(
                    os.path.basename(tmpname))
                normalised_path = os.path.join(
                    self.corpus_adders[lang].goaldir, normalised_name)

                if not os.path.exists(normalised_path):
                    parallelpath = self.corpus_adders[
                        lang].copy_file_to_corpus(
                            tmpname, url, parallelpath=parallelpath)
                    util.print_frame(
                        debug='adding {}'.format(parallelpath))
                else:
                    parallelpath = normalised_path
        print(file=sys.stderr)


class SamediggiFiCrawler(Crawler):
    u"""Notes about samediggi.fi.

    Start page is:
    http://www.samediggi.fi/index.php?option=com_frontpage&Itemid=39


    Empty pages contain either
    * "Käännöstä ei ole saatavilla"
    * "There are no translations available"

    Follow links starting with:
    * http://www.samediggi.fi/index (www.samediggi.fi == samediggi.fi)
    * index: prepend these adresses with http://www.samediggi.fi

    Remove any &lang=* parts from links,
    then re-add languages
    * &lang=finnish
    * &lang=davvi
    * &lang=anaras
    * &lang=nuortta
    * &lang=english

    Main content in div id="keski_mainbody"
    Content parts in table class="contentpaneopen"

    www.samediggi.fi/nuorat is a separate "domain"
    Links start with:
    * http://www.samediggi.fi/nuorat
    * nuorat/index

    languages
    * &lang=fi
    * &lang=sme
    * &lang=smn
    * &lang=sms

    Same procedure with links here
    """

    def __init__(self):
        """Initialise the SamediggiFiCrawler class."""
        super(SamediggiFiCrawler, self).__init__()

        self.unvisited_links.add(
            u'http://www.samediggi.fi/')
        self.old_urls = {}
        self.langs = {u'finnish': u'fin',
                      u'davvi': u'sme',
                      u'anaras': u'smn',
                      u'nuortta': u'sms',
                      u'english': u'eng'}

        for (natural, iso) in six.iteritems(self.langs):
            self.corpus_adders[natural] = adder.AddToCorpus(
                self.goaldir, iso, u'admin/sd/www.samediggi.fi')

        self.get_old_urls()

    def get_old_urls(self):
        """Collect the urls of already downloaded pages."""
        for (_, corpus_adder) in six.iteritems(self.corpus_adders):
            for root, _, files in os.walk(corpus_adder.goaldir):
                for file_ in files:
                    if file_.endswith('.xsl'):
                        path = os.path.join(root, file_)
                        mdh = xslsetter.MetadataHandler(path)
                        self.old_urls[mdh.get_variable(
                            'filename')] = path.replace('.xsl', '')

    def crawl_site(self):
        """Crawl samediggi.fi."""
        while self.unvisited_links:
            link = self.unvisited_links.pop()

            if link not in self.visited_links:
                util.print_frame(debug=link.encode('utf8'))
                util.print_frame(
                    debug='Before: unvisited_links {}'.format(
                        len(self.unvisited_links)))

                parallel_pages = []
                found_saami = False
                for lang in self.langs.keys():
                    result = requests.get(link, params={'lang': lang})

                    if result.history:
                        print('history', result.history)

                    if 'samediggi.fi' not in result.url:
                        print('url', result.url)

                    if ('www.samediggi.fi' in result.url and
                            result.status_code == requests.codes.ok and
                            not self.invalid_content(result.content)):
                        if lang in ['davvi', 'anaras', 'nuortta']:
                            found_saami = True
                        self.harvest_links(result.content)
                        print_url = self.get_print_url(result.content, lang)
                        if print_url is not None:
                            parallel_pages.append((print_url, lang))
                    else:
                        if 'samediggi.fi' not in result.url:
                            util.print_frame(
                                debug=u'Not fetching {} which was {}\n'.format(
                                    result.url.encode('utf8'),
                                    link.encode('utf8')))

                if found_saami and parallel_pages:
                    self.save_pages(parallel_pages)

                util.print_frame(debug='After: unvisited_links {}'.format(
                    len(self.unvisited_links)))

            self.visited_links.add(link)
            util.print_frame(
                debug='visited_links {}\n'.format(len(self.visited_links)))

    @staticmethod
    def get_print_url(content, lang):
        """Compute the print url of the page."""
        tree = html.document_fromstring(content)
        print_img = tree.find(
            './/img[@src="http://www.samediggi.fi/'
            'images/M_images/printButton.png"]')

        if print_img is not None:
            parent = print_img.getparent()
            href = six.moves.parse.urlparse(parent.get('href'))

            query = href.query
            newquery = [part for part in query.split('&')
                        if (part.startswith('option') or
                            part.startswith('id') or
                            part.startswith('task'))]
            newquery.append('lang=' + lang)

            newhref = six.moves.urllib.urlparse.urlunparse(
                (href.scheme,
                 href.netloc,
                 href.path,
                 href.params,
                 '&'.join(newquery),
                 href.fragment))

            return newhref

    @staticmethod
    def invalid_content(content):
        u"""Return true if the page does not contain the strings.

        * "Käännöstä ei ole saatavilla"
        * "There are no translations available"
        """
        return ('ei ole saatavilla' in content or
                'There are no translations available' in content or
                '<div class="login-form">' in content or
                'Sinulla ei ole tarvittavia' in content or
                'You need to login' in content)

    def harvest_links(self, content):
        """Harvest all links, bar some restrictions.

        Insert links into a set

        Discard links containing a href=
        * "#"
        * "*do_pdf*"
        * "pop=1"
        * com_events
        * com_search
        * www.samediggi.fi/haettavana
        * http://klemetti.blogspot.com/

        Don't follow (don't save content), but save links containg
        doc_download
        """
        tree = html.document_fromstring(content)

        for address in tree.findall('.//a'):
            href = address.get('href')
            if href is not None:
                href = href.replace('?lang=finnish', '')
                href = href.replace('?lang=davvi', '')
                href = href.replace('?lang=anaras', '')
                href = href.replace('?lang=nuortta', '')
                href = href.replace('?lang=english', '')
                href = href.replace('&lang=finnish', '')
                href = href.replace('&lang=davvi', '')
                href = href.replace('&lang=anaras', '')
                href = href.replace('&lang=nuortta', '')
                href = href.replace('&lang=english', '')

                if not href.startswith('http'):
                    href = os.path.join('http://www.samediggi.fi', href)

                if (href not in self.visited_links and not
                        re.search(
                            'klemetti.blogspot|/nuorat|/#|com_events|'
                            'com_search|haettavana|do_pdf|pop=1|com_docman|'
                            '/images|com_weblink|task=vcard|view_contact_id|'
                            'com_contact|mad4joomla|mailto|javascript|'
                            'administrator/',
                            href) and
                        href.startswith('http://www.samediggi.fi')):
                    self.unvisited_links.add(href)


class SamediggiNoPage(object):
    """Save a samediggi.no page to the corpus."""

    def __init__(self, url):
        """Initialise the SamediggiNoPage class."""
        result = requests.get(url)
        self.parsed_url = six.moves.urllib.parse.urlparse(result.url)
        self.tree = html.document_fromstring(result.content)

        self.ok_netlocs = ['www.sametinget.no',
                           'www.samediggi.no',
                           'www.saemiedigkie.no',
                           'www.samedigge.no']

    @property
    def url(self):
        """Get the url."""
        return self.parsed_url.geturl()

    @property
    def parallel_links(self):
        """Get links to the parallels of this document."""
        return [six.moves.urllib.parse.urlunparse((self.parsed_url.scheme,
                                                   self.parsed_url.netloc,
                                                   a.get('href'), '', '', ''))
                for a in self.tree.xpath(
                    './/ul[@id="languageList"]/li/a[@href]')]

    @property
    def print_url(self):
        """Get the print url of the document."""
        print_link = self.tree.find('.//link[@media="print"]')

        if print_link is not None:
            url = print_link.get('href')

            return six.moves.urllib.parse.urlunparse((
                self.parsed_url.scheme,
                self.parsed_url.netloc,
                url, '', '', ''))

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
                        '/Dahpahusat|javascript|tel:',
                        href):
                    if href.startswith('/'):
                        href = six.moves.urllib.parse.urlunparse(
                            (self.parsed_url.scheme,
                             self.parsed_url.netloc,
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


class SamediggiNoCrawler(Crawler):
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
            body_lang = self.languageguesser.classify(orig_page.body_text,
                                                      langs=self.langs)
            if orig_page.lang == body_lang:
                if body_lang in [u'sme', u'sma', u'smj']:
                    found_saami = True
                parallel_pages.append((orig_page.print_url,
                                       orig_page.lang))
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


class NrkSmeCrawler(Crawler):
    """Collect Northern Saami pages from nrk.no.

    Attributes:
        language_guesser (text_cat.Classifier): guess language from a given
            string
        goaldir (str): the directory where the working copy of the corpus is
        corpus_adder (adder.AddToCorpus): the working horse, adds urls to
            the corpus
        tags (dict of str to str): numerical tags that point to a specific topic
            on nrk.no
        invalid_links (set of str): all links containing 'gammelsystem'
        counter (collections.defaultdict of int): collect interesting
            statistics, such number of links visited and fetched links within
            a tag
        fetched_links (set of str): links to articles that have already been
            fetched
    """
    language_guesser = text_cat.Classifier(None)
    goaldir = six.text_type(os.getenv('GTBOUND'))
    corpus_adder = adder.AddToCorpus(goaldir, 'sme', 'news/nrk.no')
    tags = defaultdict(str)
    invalid_links = set()
    counter = defaultdict(int)

    def __init__(self):
        """Initialise the NrkSmeCrawler class."""
        super(NrkSmeCrawler, self).__init__()
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
            text = bytes(address.find('.//p[@class="plug-preamble"]').text,
                         encoding='latin1')
        except AttributeError:
            text = bytes(address.find('.//h2[@class="title"]').text,
                         encoding='latin1')

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
        page_links_template = (
            'https://www.nrk.no/serum/api/render/{tag}?'
            'size=18&perspective=BRIEF&alignment=AUTO&'
            'classes=surrogate-content&'
            'display=false&arrangement.offset={offset}&'
            'arrangement.quantity={quantity}&'
            'arrangement.repetition=PATTERN&'
            'arrangement.view[0].perspective=BRIEF&'
            'arrangement.view[0].size=6&'
            'arrangement.view[0].alignment=LEFT&'
            'paged=SIMPLE'
        )
        quantity = 10
        limit = 10000

        for offset in range(0, limit, quantity):
            print('.', end='')
            sys.stdout.flush()
            try:
                result = requests.get(page_links_template.format(
                    tag=tag, offset=offset, quantity=quantity))
            except requests.exceptions.ConnectionError:
                util.note('Connection error when fetching {}'.format(
                    tag, offset, quantity))
                break
            else:
                try:
                    yield html.document_fromstring(result.content)
                except etree.ParserError:
                    util.note('No more articles in tag: «{}»'.format(
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
            for address in tree.xpath(
                    '//a[@class="autonomous lp_plug"]'):
                self.counter[tag + '_total'] += 1
                href = address.get('href')

                if 'systemtest' in href:
                    self.invalid_links.add(href)
                if ('systemtest' not in href and
                        href not in self.fetched_links and
                        self.guess_lang(address) == 'sme'):
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
            util.note('Fetching articles from «{}»'.format(tagname))
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
        self.crawl_tag('1.13205591')  # NRK Sápmi – davvisámegillii
        self.crawl_tag('1.10892262')  # NuFal davvisámegillii
        self.crawl_additional_tags()
        self.corpus_adder.add_files_to_working_copy()
        self.report()

    def crawl_additional_tags(self):
        """Crawl all tags found in nrk.no documents."""
        for root, _, files in os.walk(self.corpus_adder.goaldir):
            for file_ in files:
                if file_.endswith('.html'):
                    for additional_tag, tag_name in self.pick_tags(
                            os.path.join(root, file_)):
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
    def add_metadata(path):
        """Get metadata from the nrk.no article.

        Arguments:
            path (str): path to the nrk.no article
        """
        article = html.parse(path)
        metadata = xslsetter.MetadataHandler(path + '.xsl')

        for twitter in article.xpath('//a[@class="author__twitter"]'):
            twitter.getparent().remove(twitter)

        count = 0
        for author in article.xpath('//span[@class="author__role"]'):
            text = author.text.strip()
            if text is not None and (text.startswith('Journ') or
                                     text.startswith('Komm') or
                                     text.startswith('Arti')):
                count += 1
                parts = author.getprevious().text.strip().split()
                metadata.set_variable('author' + str(count) + '_ln',
                                      parts[-1])
                metadata.set_variable('author' + str(count) + '_fn',
                                      ' '.join(parts[:-1]))

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
            xslsetter.MetadataHandler(os.path.join(root, file_)).get_variable(
                'filename')
            for root, _, files in os.walk(path)
            for file_ in files
            if file_.endswith('.xsl')}


def parse_options():
    """Parse the commandline options.

    Returns:
        a list of arguments as parsed by argparse.Argumentparser.
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Crawl saami sites (for now, only www.samediggi.fi).')

    parser.add_argument('sites',
                        nargs='+',
                        help="The sites to crawl")

    args = parser.parse_args()
    return args


def main():
    """Crawl sites."""
    args = parse_options()

    for site in args.sites:
        if site == 'www.samediggi.fi':
            print('Will crawl samediggi.fi')
            crawler = SamediggiFiCrawler()
            crawler.crawl_site()
        elif site == 'samediggi.no':
            print('Will crawl samediggi.no')
            crawler = SamediggiNoCrawler()
            crawler.crawl_site()
        elif site == 'nrk.no':
            print('Will crawl nrk.no')
            crawler = NrkSmeCrawler()
            crawler.crawl_site()
        else:
            print('Can not crawl {} yet'.format(site))
