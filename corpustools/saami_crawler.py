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
import lxml.html
import os
import re
import requests
import sys


import adder
import argparse_version
import util
import xslsetter


class SamediggiFiCrawler(object):

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
        self.unvisited_links = set()
        self.unvisited_links.add(
            u'http://www.samediggi.fi/')
        self.visited_links = set()
        self.download_links = set()
        self.old_urls = {}
        self.langs = {u'finnish': u'fin',
                      u'davvi': u'sme',
                      u'anaras': u'smn',
                      u'nuortta': u'sms',
                      u'english': u'eng'}

        self.corpus_adders = {
            u'finnish': adder.AddToCorpus(
                unicode(os.getenv('GTFREE')), u'fin', u'admin/sd/www.samediggi.fi'),
            u'davvi': adder.AddToCorpus(
                unicode(os.getenv('GTFREE')), u'sme', u'admin/sd/www.samediggi.fi'),
            u'anaras': adder.AddToCorpus(
                unicode(os.getenv('GTFREE')), u'smn', u'admin/sd/www.samediggi.fi'),
            u'nuortta': adder.AddToCorpus(
                unicode(os.getenv('GTFREE')), u'sms', u'admin/sd/www.samediggi.fi'),
            u'english': adder.AddToCorpus(
                unicode(os.getenv('GTFREE')), u'eng', u'admin/sd/www.samediggi.fi'),
        }
        self.get_old_urls()

    def get_old_urls(self):
        for (lang, corpus_adder) in self.corpus_adders.items():
            for root, dirs, files in os.walk(corpus_adder.goaldir):
                for f in files:
                    if f.endswith('.xsl'):
                        path = os.path.join(root, f)
                        mdh = xslsetter.MetadataHandler(path)
                        self.old_urls[mdh.get_variable('filename')] = path.replace('.xsl', '')

    def __del__(self):
        for (lang, corpus_adder) in self.corpus_adders.items():
            corpus_adder.add_files_to_working_copy()

    def fix_dupe(self):
        possible_dupe = {
            'Itemid=149': 'Itemid=195',
            'Itemid=323': 'Itemid=195',
            'Itemid=327': 'Itemid=195',
            'Itemid=112': 'Itemid=195',
            'Itemid=128': 'Itemid=195',
            'Itemid=306': 'Itemid=195',
            'Itemid=307': 'Itemid=195',
            'Itemid=273': 'Itemid=195',
            'Itemid=279': 'Itemid=195',
            'Itemid=280': 'Itemid=195',
            'Itemid=251': 'Itemid=195',
            'Itemid=61': 'Itemid=195',
            'Itemid=39': 'Itemid=195',
            'Itemid=256': 'Itemid=195',
        }

        link = self.unvisited_links.pop()

        for (unwanted, wanted) in possible_dupe.items():
            if unwanted in link:
                self.visited_links.add(link)
                link = link.replace(unwanted, wanted)

        return link

    def download_pages(self):
        while len(self.unvisited_links) > 0:
            link = self.fix_dupe()

            if link not in self.visited_links:
                util.print_frame(debug='About to visit ' + link)
                util.print_frame(
                    debug='Before: unvisited_links {}'.format(len(self.unvisited_links)))

                try:
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
                            if ('blogcategory' not in r.url):
                                parallel_pages.append((r, lang))
                        else:
                            if 'samediggi.fi' not in r.url:
                                util.print_frame(
                                    debug=u'Not fetching {} which was {}\n'.format(
                                        r.url, link))

                    if found_saami and len(parallel_pages) > 0:
                        self.save_pages(parallel_pages)
                except UserWarning:
                    print(link, u'does not exist', file=sys.stderr)

                util.print_frame(debug='After: unvisited_links {}'.format(len(self.unvisited_links)))

            self.visited_links.add(link)
            util.print_frame(
                debug='visited_links {}\n'.format(len(self.visited_links)))

    def invalid_content(self, content):
        '''Return true if the page does not contain the strings

        * "Käännöstä ei ole saatavilla"
        * "There are no translations available"
        '''
        return ('ei ole saatavilla' in content or
                'There are no translations available' in content or
                '<div class="login-form">' in content or
                'Sinulla ei ole tarvittavia' in content)

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
                            'com_contact|mad4joomla|mailto',
                            href) and
                        href.startswith('http://www.samediggi.fi')):
                    self.unvisited_links.add(href)

    def save_pages(self, pages):
        '''Write pages to disk

        pages is a list of r.url, lang tuples
        '''
        (rurl, lang) = pages[0]
        if rurl.url in self.old_urls.keys():
            util.print_frame(debug='updating {}'.format(self.old_urls[rurl.url]))
            with open(self.old_urls[rurl.url], 'wb') as oldfile:
                oldfile.write(rurl.content)
            parallel_path = self.old_urls[rurl.url]
        else:
            parallel_path = self.corpus_adders[lang].copy_url_to_corpus(rurl.url)

        for (rurl, lang) in pages[1:]:
            if rurl.url in self.old_urls.keys():
                util.print_frame(debug='updating {}'.format(self.old_urls[rurl.url]))
                with open(self.old_urls[rurl.url], 'wb') as oldfile:
                    oldfile.write(rurl.content)
                self.corpus_adders[lang].update_parallel_data(
                    util.split_path(self.old_urls[rurl.url]),
                    parallel_path)
            else:
                util.print_frame(
                    debug='adding {}'.format(
                        self.corpus_adders[lang].copy_url_to_corpus(rurl.url,
                                                                    parallel_path)))


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
            sc.download_pages()
        else:
            print('Can not crawl {} yet'.format(site))


if __name__ == "__main__":
    main()
