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

import os
import re

import requests
import six
from lxml import html

from corpustools import adder, crawler, util, xslsetter


class SamediggiFiCrawler(crawler.Crawler):
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

        self.unvisited_links.add(u'http://www.samediggi.fi/')
        self.old_urls = {}
        self.langs = {
            u'finnish': u'fin',
            u'davvi': u'sme',
            u'anaras': u'smn',
            u'nuortta': u'sms',
            u'english': u'eng'
        }

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
                util.print_frame(debug='Before: unvisited_links {}'.format(
                    len(self.unvisited_links)))

                parallel_pages = []
                found_saami = False
                for lang in self.langs.keys():
                    result = requests.get(link, params={'lang': lang})

                    if result.history:
                        print('history', result.history)

                    if 'samediggi.fi' not in result.url:
                        print('url', result.url)

                    if ('www.samediggi.fi' in result.url
                            and result.status_code == requests.codes.ok
                            and not self.invalid_content(result.content)):
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
        print_img = tree.find('.//img[@src="http://www.samediggi.fi/'
                              'images/M_images/printButton.png"]')

        if print_img is not None:
            parent = print_img.getparent()
            href = six.moves.parse.urlparse(parent.get('href'))

            query = href.query
            newquery = [
                part for part in query.split('&')
                if (part.startswith('option') or part.startswith('id')
                    or part.startswith('task'))
            ]
            newquery.append('lang=' + lang)

            newhref = six.moves.urllib.urlparse.urlunparse(
                (href.scheme, href.netloc, href.path, href.params,
                 '&'.join(newquery), href.fragment))

            return newhref

    @staticmethod
    def invalid_content(content):
        u"""Return true if the page does not contain the strings.

        * "Käännöstä ei ole saatavilla"
        * "There are no translations available"
        """
        return ('ei ole saatavilla' in content
                or 'There are no translations available' in content
                or '<div class="login-form">' in content
                or 'Sinulla ei ole tarvittavia' in content
                or 'You need to login' in content)

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

                if (href not in self.visited_links and not re.search(
                        'klemetti.blogspot|/nuorat|/#|com_events|'
                        'com_search|haettavana|do_pdf|pop=1|com_docman|'
                        '/images|com_weblink|task=vcard|view_contact_id|'
                        'com_contact|mad4joomla|mailto|javascript|'
                        'administrator/', href)
                        and href.startswith('http://www.samediggi.fi')):
                    self.unvisited_links.add(href)
