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
#   Copyright © 2013-2023 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""This file contains routines to crawl samas.no."""


import os

from lxml import html

from corpustools import adder, util


class SamasCrawler:
    """Collect pages from samas.no.

    We only want to fetch saami pages, and their parallels.

    <ul class="language-switcher-locale-url"> tells which language is active.
    If se is active, save the page and its parallels.
    If se is not active, check to see if it has a parallel. Save the page and its parallels.
    If the link of one of the list elements contain /node, skip it.
    """

    goaldir = str(os.getenv("GTFREE"))
    external_links = set()
    samas_languages = {"se": "sme", "nb": "nob", "en-UK": "eng"}

    def __init__(self):
        self.fetched_links = {
            "http://samas.no/en",
            "http://samas.no/nb",
            "http://samas.no/se",
        }
        self.corpus_adders = {
            lang: adder.AddToCorpus(
                self.goaldir, self.samas_languages[lang], "admin/allaskuvla/samas.no"
            )
            for lang in self.samas_languages
        }
        self.downloader = adder.UrlDownloader(os.path.join(self.goaldir, "tmp"))

    @staticmethod
    def get_samas_href(href):
        return f"http://samas.no{href}"

    def harvest_links(self, content):
        """Find interesting pages inside a topic.

        Args:
            content (etree.Element): content of a samas page, without the
                language_switcher element.

        Yields:
            (str): a url to a samas.no page
        """
        lang_switcher = content.find('.//ul[@class="language-switcher-locale-url"]')
        lang_switcher.getparent().remove(lang_switcher)

        for address in content.xpath("//a"):
            if self.is_internal(address.get("href")):
                yield self.get_samas_href(address.get("href").strip())

    def is_internal(self, href):
        return (
            href
            and "/node" not in href
            and "/Node" not in href
            and href.startswith("/")
            and "field_" not in href
            and "page=" not in href
            and "/user" not in href
        )

    def get_uff(self, tmpname):
        content = html.parse(tmpname).getroot()
        lang_switcher = content.find('.//ul[@class="language-switcher-locale-url"]')

        return {
            address.get("xml:lang"): address.get("href")
            for address in lang_switcher.xpath(".//a")
            if self.is_internal(address.get("href"))
        }

    def add_samas_page(self, link):
        """Get a saami samas.no page and its parallels.

        Args:
            link (str): a url to samas.no page, that has been vetted by
                the is_internal function.
        """
        paths = set()
        if link not in self.fetched_links:
            try:
                (request, tmpname) = self.downloader.download(link)
                uff = self.get_uff(tmpname)

                if "se" in uff:
                    util.note("")
                    util.print_frame(link, uff)
                    path = paths.add(self.uff_fetcher(uff, "se", link, tmpname, ""))

                    for lang in ["nb", "en-UK"]:
                        if lang in uff:
                            paths.add(self.uff_fetcher(uff, lang, link, tmpname, path))

            except (adder.AdderError, UserWarning) as error:
                util.note(error)

        for puth in paths:
            for lunk in self.harvest_links(html.parse(puth)):
                self.add_samas_page(lunk)

    def uff_fetcher(self, uff, lang, link, tmpname, path):
        lunk = self.get_samas_href(uff[lang])
        self.fetched_links.add(lunk)
        if lunk == link:
            return self.corpus_adders[lang].copy_file_to_corpus(
                tmpname, lunk, parallelpath=path
            )
        else:
            return self.corpus_adders[lang].copy_url_to_corpus(lunk, parallelpath=path)

    def crawl_site(self):
        for lang in self.samas_languages:
            (request, tmpname) = self.downloader.download(f"http://samas.no/{lang[:2]}")
            for link in self.harvest_links(html.parse(tmpname).getroot()):
                self.add_samas_page(link)

        for lang in self.corpus_adders:
            self.corpus_adders[lang].add_files_to_working_copy()
