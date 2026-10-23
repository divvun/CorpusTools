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
#   Copyright © 2013-2025 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""This file contains routines to crawl nrk.no containing saami text."""


from collections import defaultdict
from pathlib import Path
from pprint import pprint
from time import sleep

import requests
from lxml import etree

from corpustools.crawler import Crawler
from corpustools.nrk_no_page import NrkNoPage, NrkNoUnknownPageError
from corpustools.versioncontrol import vcs


class NrkNoCrawler(Crawler):
    """Collect pages from nrk.no."""

    langs: list[str] = ["sme", "sma", "smj", "nob"]
    limit: int = 1000
    counter: defaultdict[str, int] = defaultdict(int)

    def __init__(self) -> None:
        super().__init__()
        print("init nrk.no")
        self.visited_links = self.get_fetched_ids()
        print("visited links:", len(self.visited_links))
        self.unvisited_links = self.fetchable_ids()
        print("unvisited links:", len(self.unvisited_links))
        self.vcs = {
            lang: vcs(self.corpus_parent / f"corpus-{lang}-orig-x-closed")
            for lang in self.langs
        }

    def get_article_ids(self) -> set[str]:
        """Get article ids from NRK Sápmi.

        Returns:
            A set of article ids.
        """
        json_sources = [
            f"https://www.nrk.no/serum/api/content/json/1.11160953?start=2&limit={self.limit}",  # https://www.nrk.no/sapmi/nyheter/
            f"https://www.nrk.no/serum/api/content/json/1.13572949?start=2&limit={self.limit}&context=items",  # https://www.nrk.no/sapmi/davvisamegillii/
            f"https://www.nrk.no/serum/api/content/json/1.13572946?start=2&limit={self.limit}&context=items",  # https://www.nrk.no/sapmi/julevsabmaj/
            f"https://www.nrk.no/serum/api/content/json/1.13572943?start=2&limit={self.limit}&context=items",  # https://www.nrk.no/sapmi/aaarjelsaemiengielesne/
        ]

        responses = (requests.get(url) for url in json_sources)

        response_jsons = (response.json() for response in responses)

        return {
            relation.get("id")
            for data in response_jsons
            for relation in data.get("relations")
        }

    def fetchable_ids(self) -> set[str]:
        article_ids = self.get_article_ids()
        return article_ids - self.visited_links

    def get_fetched_ids(self) -> set[str]:
        """Find articles ids of fetched documents.

        Args:
            path (str): path to the directory where nrk articles are found.

        Returns:
            A set of strings, where the strings are ids of the
            fetched articles.
        """
        corpus_dirs = [
            self.corpus_parent / f"corpus-{lang}-orig-x-closed" / "news/nrk.no"
            for lang in self.langs
        ]

        return {
            file_.stem.replace(".html", "").split("-")[-1]
            for path in corpus_dirs
            for file_ in Path(path).glob("*.xsl")
        }

    def crawl_page(self, article_id: str) -> NrkNoPage | None:
        """Collect links from a page."""
        self.visited_links.add(article_id)
        try:
            result = requests.get(f"https://nrk.no/sapmi/{article_id}", timeout=10)
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            return None

        if not result.ok:
            return None

        content_type = result.headers.get("content-type")
        if content_type is None:
            return None

        if "html" not in content_type.lower():
            return None

        tree = etree.HTML(result.text)

        if tree is None:
            return None

        orig_page = NrkNoPage(result.url, etree.HTML(result.text), self.corpus_parent)

        self.unvisited_links.update(orig_page.links)

        return orig_page

    def crawl_site(self):
        print("Crawling nrk.no.")
        while self.unvisited_links:
            article_id = self.unvisited_links.pop()
            if article_id not in self.visited_links:
                try:
                    self.crawl_pageset(article_id)
                except NrkNoUnknownPageError as error:
                    print(f"Error: {error}")
                sleep(0.5)

            self.unvisited_links.difference_update(self.visited_links)
            print(
                article_id,
                "U:",
                len(self.unvisited_links),
                "V:",
                len(self.visited_links),
                end="\r",
            )

        pprint(self.counter)

    @staticmethod
    def set_parallel_info(parallel_pages):
        """Set the parallels for this set of parallel pages."""
        lang_combinations = (
            (parallel_page1, parallel_page2)
            for parallel_page1 in parallel_pages
            for parallel_page2 in parallel_pages
            if parallel_page1 != parallel_page2
        )

        for parallel_page1, parallel_page2 in lang_combinations:
            parallel_page1.set_parallel_file(
                parallel_page2.lang, parallel_page2.basename
            )

    def crawl_pageset(self, article_id: str) -> None:
        orig_page = self.crawl_page(article_id)
        if orig_page is None:
            print(f"Could not crawl {article_id}.")
            return

        pages = self.get_page_set(orig_page=orig_page)

        self.set_parallel_info(pages)
        for page in pages:
            page.save()
            self.vcs[page.lang].add(page.fullpath.orig)
            self.vcs[page.lang].add(page.fullpath.xsl)
            self.counter[page.lang] += 1

    def get_page_set(self, orig_page) -> list[NrkNoPage]:
        """Get parallel pages for the original page.

        Args:
            orig_page: The original page to get parallel pages for.

        Returns:
            A list of parallel pages.
        """
        pages = [orig_page]
        pages.extend([self.crawl_page(link) for link in orig_page.parallel_ids])

        # If we only have norwegian, we don't want to save any pages
        page_langs = {page.lang for page in pages if page is not None}
        if len(page_langs) == 1 and "nob" in page_langs:
            return []

        return [page for page in pages if page is not None]
