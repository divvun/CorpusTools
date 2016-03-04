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

from __future__ import print_function

import argparse
import lxml.etree as etree
import lxml.html
import os
import re
import requests
import shutil
import sys
import urlparse

import adder
import argparse_version
import namechanger
import util
import xslsetter


class Crawler(object):
    def __init__(self):
        self.goaldir = unicode(os.getenv('GTFREE'))
        self.unvisited_links = set()
        self.visited_links = set()
        self.download_links = set()
        self.corpus_adders = {}
        self.downloader = adder.UrlDownloader(os.path.join(
            self.goaldir, 'tmp'))

    def __del__(self):
        for (lang, corpus_adder) in self.corpus_adders.items():
            corpus_adder.add_files_to_working_copy()

    def save_pages(self, pages):
        '''Write pages to disk

        pages is a list of url, lang tuples
        '''
        (url, lang) = pages[0]
        (r, tmpname) = self.downloader.download(url)

        normalised_name = namechanger.normalise_filename(
            os.path.basename(tmpname))
        normalised_path = os.path.join(
            self.corpus_adders[lang].goaldir, normalised_name)

        if not os.path.exists(normalised_path):
            parallelpath = self.corpus_adders[lang].copy_file_to_corpus(
                tmpname, url)
            util.print_frame(
                    debug='adding {}\n'.format(parallelpath))
        else:
            parallelpath = normalised_path

        for (url, lang) in pages[1:]:
            (r, tmpname) = self.downloader.download(url)

            normalised_name = namechanger.normalise_filename(
                os.path.basename(tmpname))
            normalised_path = os.path.join(
                self.corpus_adders[lang].goaldir, normalised_name)

            if not os.path.exists(normalised_path):
                util.print_frame(debug='adding {}\n'.format(
                    self.corpus_adders[lang].copy_file_to_corpus(
                        tmpname, url, parallelpath=parallelpath)))


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

        for (natural, iso) in self.langs.items():
            self.corpus_adders[natural] = adder.AddToCorpus(
                self.goaldir, iso, u'admin/sd/www.samediggi.fi')

        self.get_old_urls()

    def get_old_urls(self):
        for (lang, corpus_adder) in self.corpus_adders.items():
            for root, dirs, files in os.walk(corpus_adder.goaldir):
                for f in files:
                    if f.endswith('.xsl'):
                        path = os.path.join(root, f)
                        mdh = xslsetter.MetadataHandler(path)
                        self.old_urls[mdh.get_variable('filename')] = path.replace('.xsl', '')

    def crawl_site(self):
        while len(self.unvisited_links) > 0:
            link = self.unvisited_links.pop()

            if link not in self.visited_links:
                util.print_frame(debug=link)
                util.print_frame(
                    debug='Before: unvisited_links {}'.format(len(self.unvisited_links)))

                parallel_pages = []
                found_saami = False
                for lang in self.langs.keys():
                    r = requests.get(link, params={'lang': lang})

                    if len(r.history) > 0:
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
                                    r.url, link))

                if found_saami and len(parallel_pages) > 0:
                    self.save_pages(parallel_pages)

                util.print_frame(debug='After: unvisited_links {}'.format(len(self.unvisited_links)))

            self.visited_links.add(link)
            util.print_frame(
                debug='visited_links {}\n'.format(len(self.visited_links)))

    def get_print_url(self, content, lang):
        tree = lxml.html.document_fromstring(content)
        print_img = tree.find('.//img[@src="http://www.samediggi.fi/images/M_images/printButton.png"]')

        if print_img is not None:
            parent = print_img.getparent()
            href = urlparse.urlparse(parent.get('href'))

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
        else:
            print('Can not crawl {} yet'.format(site))


if __name__ == "__main__":
    main()
