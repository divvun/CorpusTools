# -*- coding:utf-8 -*-

#
#   This file contains routines to crawl sites containing saami text
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
#   Copyright © 2013-2016 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

from __future__ import absolute_import, print_function

import argparse
import os
import re
import shutil
import sys

import lxml.etree as etree
import lxml.html
import requests
import six

from corpustools import (adder, argparse_version, namechanger, text_cat, util,
                         xslsetter)


class Crawler(object):

    def __init__(self):
        self.goaldir = six.text_type(os.getenv('GTFREE'))
        self.unvisited_links = set()
        self.visited_links = set()
        self.download_links = set()
        self.corpus_adders = {}
        self.downloader = adder.UrlDownloader(os.path.join(
            self.goaldir, 'tmp'))

    def __del__(self):
        for (lang, corpus_adder) in six.iteritems(self.corpus_adders):
            corpus_adder.add_files_to_working_copy()

    def save_pages(self, pages):
        '''Write pages to disk

        pages is a list of url, lang tuples
        '''
        parallelpath = ''

        for (url, lang) in pages:
            try:
                (r, tmpname) = self.downloader.download(url)
            except adder.AdderException as e:
                util.print_frame(debug=str(e) + '\n')
            else:
                normalised_name = namechanger.normalise_filename(
                    os.path.basename(tmpname))
                normalised_path = os.path.join(
                    self.corpus_adders[lang].goaldir, normalised_name)

                if not os.path.exists(normalised_path):
                    parallelpath = self.corpus_adders[lang].copy_file_to_corpus(
                        tmpname, url, parallelpath=parallelpath)
                    util.print_frame(
                        debug='adding {}'.format(parallelpath))
                else:
                    parallelpath = normalised_path
        print(file=sys.stderr)


class SamediggiFiCrawler(Crawler):
    '''Notes about samediggi.fi

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
    '''

    def __init__(self):
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
        for (lang, corpus_adder) in six.iteritems(self.corpus_adders):
            for root, dirs, files in os.walk(corpus_adder.goaldir):
                for f in files:
                    if f.endswith('.xsl'):
                        path = os.path.join(root, f)
                        mdh = xslsetter.MetadataHandler(path)
                        self.old_urls[mdh.get_variable(
                            'filename')] = path.replace('.xsl', '')

    def crawl_site(self):
        '''Crawl samediggi.fi'''
        while self.unvisited_links:
            link = self.unvisited_links.pop()

            if link not in self.visited_links:
                util.print_frame(debug=link.encode('utf8'))
                util.print_frame(
                    debug='Before: unvisited_links {}'.format(len(self.unvisited_links)))

                parallel_pages = []
                found_saami = False
                for lang in self.langs.keys():
                    r = requests.get(link, params={'lang': lang})

                    if r.history:
                        print('history', r.history)

                    if 'samediggi.fi' not in r.url:
                        print('url', r.url)

                    if ('www.samediggi.fi' in r.url and
                            r.status_code == requests.codes.ok and
                            not self.invalid_content(r.content)):
                        if lang in ['davvi', 'anaras', 'nuortta']:
                            found_saami = True
                        self.harvest_links(r.content)
                        print_url = self.get_print_url(r.content, lang)
                        if print_url is not None:
                            parallel_pages.append((print_url, lang))
                    else:
                        if 'samediggi.fi' not in r.url:
                            util.print_frame(
                                debug=u'Not fetching {} which was {}\n'.format(
                                    r.url.encode('utf8'), link.encode('utf8')))

                if found_saami and parallel_pages:
                    self.save_pages(parallel_pages)

                util.print_frame(debug='After: unvisited_links {}'.format(
                    len(self.unvisited_links)))

            self.visited_links.add(link)
            util.print_frame(
                debug='visited_links {}\n'.format(len(self.visited_links)))

    def get_print_url(self, content, lang):
        tree = lxml.html.document_fromstring(content)
        print_img = tree.find(
            './/img[@src="http://www.samediggi.fi/images/M_images/printButton.png"]')

        if print_img is not None:
            parent = print_img.getparent()
            href = six.moves.parse.urlparse(parent.get('href'))

            query = href.query
            newquery = [part for part in query.split('&')
                        if (part.startswith('option') or
                            part.startswith('id') or
                            part.startswith('task'))]
            newquery.append('lang=' + lang)

            newhref = urlparse.urlunparse(
                (href.scheme,
                    href.netloc,
                    href.path,
                    href.params,
                    '&'.join(newquery),
                    href.fragment))

            return newhref

    def invalid_content(self, content):
        '''Return true if the page does not contain the strings

        * "Käännöstä ei ole saatavilla"
        * "There are no translations available"
        '''
        return ('ei ole saatavilla' in content or
                'There are no translations available' in content or
                '<div class="login-form">' in content or
                'Sinulla ei ole tarvittavia' in content or
                'You need to login' in content)

    def harvest_links(self, content):
        '''Harvest all links, bar some restrictions

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
        '''
        tree = lxml.html.document_fromstring(content)

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

    def __init__(self, url):
        r = requests.get(url)
        self.parsed_url = six.moves.urllib.parse.urlparse(r.url)
        self.tree = lxml.html.document_fromstring(r.content)

        self.ok_netlocs = ['www.sametinget.no',
                           'www.samediggi.no',
                           'www.saemiedigkie.no',
                           'www.samedigge.no']

    @property
    def url(self):
        return self.parsed_url.geturl()

    @property
    def parallel_links(self):
        return [six.moves.urllib.parse.urlunparse((self.parsed_url.scheme,
                                                   self.parsed_url.netloc,
                                                   a.get('href'), '', '', ''))
                for a in self.tree.xpath('.//ul[@id="languageList"]/li/a[@href]')]

    @property
    def print_url(self):
        print_link = self.tree.find('.//link[@media="print"]')

        if print_link is not None:
            url = print_link.get('href')

            return six.moves.urllib.parse.urlunparse((
                self.parsed_url.scheme,
                self.parsed_url.netloc,
                url, '', '', ''))

    @property
    def lang(self):
        uff = {}
        uff['no-bokmaal'] = 'nob'
        uff['sma-NO'] = 'sma'
        uff['sme-NO'] = 'sme'
        uff['smj-no'] = 'smj'
        content_language = self.tree.find('.//meta[@name="Content-language"]')

        if content_language is not None:
            return uff[content_language.get('content')]
        else:
            uff = 'no language {}'.format(self.url.encode('utf8'))
            util.print_frame(debug=uff)

    @property
    def links(self):
        links = set()
        for address in self.tree.findall('.//a'):
            href = address.get('href')
            if href is not None:
                if not re.search(
                        'tv.samediggi.no|^#|/rss/feed|switchlanguage|facebook.com|'
                        'Web-tv|user/login|mailto|/Dokumenter|/Dokumeantta|'
                        '/Tjaatsegh|.pdf|.doc|.xls|/images/|/download/|/Biejjielaahkoe|/Kalender|'
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
        body = self.tree.find('.//body')

        return ' '.join(body.xpath('.//text()'))


class SamediggiNoCrawler(Crawler):

    def __init__(self):
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
        self.visited_links.add(link)
        util.print_frame(debug=link.encode('utf8'))
        try:
            orig_page = SamediggiNoPage(link)
        except requests.exceptions.SSLError as e:
            util.print_frame(debug=str(e))
        else:
            self.visited_links.add(orig_page.url)
            self.unvisited_links = self.unvisited_links.union(orig_page.links)

            util.print_frame(debug=orig_page.url.encode('utf8') + '\n')

            return orig_page

    def crawl_site(self):
        '''Crawl samediggi.no'''
        while self.unvisited_links:
            link = self.unvisited_links.pop()

            if link not in self.visited_links:
                self.crawl_pageset(link)

    def crawl_pageset(self, link):
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
                        body_lang = self.languageguesser.classify(parallel_page.body_text,
                                                                  langs=self.langs)
                        if parallel_page.lang == body_lang:
                            if body_lang in [u'sme', u'sma', u'smj']:
                                found_saami = True
                            util.print_frame()
                            parallel_pages.append((parallel_page.print_url,
                                                   parallel_page.lang))
                        else:
                            uff = 'not same lang {}:\n orig: {} body: {}'.format(
                                parallel_page.url.encode('utf8'), parallel_page.lang, body_lang)
                            util.print_frame(debug=uff)

        if found_saami:
            self.save_pages(parallel_pages)
        else:
            util.print_frame(debug='No saami found')


def parse_options():
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Crawl saami sites (for now, only www.samediggi.fi).')

    parser.add_argument('sites',
                        nargs='+',
                        help="The sites to crawl")

    args = parser.parse_args()
    return args


def main():
    args = parse_options()

    for site in args.sites:
        if site == 'www.samediggi.fi':
            print('Will crawl samediggi.fi')
            sc = SamediggiFiCrawler()
            sc.crawl_site()
        elif site == 'samediggi.no':
            print('Will crawl samediggi.no')
            sc = SamediggiNoCrawler()
            sc.crawl_site()
        else:
            print('Can not crawl {} yet'.format(site))
