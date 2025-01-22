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
"""This file contains routines to crawl sites containing saami text."""


import os
from pathlib import Path
from typing import Iterator

import requests
from lxml import etree

from corpustools import (
    crawler,
    versioncontrol,
)
from corpustools.samediggi_no_page import SamediggiNoPage
from corpustools.util import make_digest


class SamediggiNoCrawler(crawler.Crawler):
    """Crawl samediggi.no and save html documents to the corpus."""

    langs = ["nob", "sma", "sme", "smj"]

    def __init__(self) -> None:
        """Initialise the SamediggiNoCrawler class."""
        super().__init__()
        self.unvisited_links.add("https://sametinget.no/")
        self.vcs = {
            lang: versioncontrol.vcs(self.corpus_parent / f"corpus-{lang}-orig")
            for lang in self.langs
        }

        self.dupe_table = self.make_dupe_dict()

    def samediggi_corpus_dirs(self) -> Iterator[Path]:
        gtlangs = os.getenv("GTLANGS")
        return (
            Path(gtlangs) / f"corpus-{lang}-orig" / "admin/sd/samediggi.no"
            for lang in self.langs
            if gtlangs
        )

    def samediggi_corpus_files(self) -> Iterator[Path]:
        return (
            html_path
            for corpus_dir in self.samediggi_corpus_dirs()
            for html_path in corpus_dir.rglob("*.html")
        )

    def make_dupe_dict(self) -> dict[str, Path]:
        """Make a dict to map md5-digest to filename."""
        return {
            make_digest(fullpath.read_bytes()): fullpath
            for fullpath in self.samediggi_corpus_files()
        }

    def crawl_page(self, link):
        """Collect links from a page."""
        self.visited_links.add(link)
        result: requests.Response = requests.get(link)

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

        orig_page = SamediggiNoPage(
            result.url, etree.HTML(result.text), self.corpus_parent, self.dupe_table()
        )

        orig_page.sanity_test()
        self.visited_links.add(orig_page.url)
        self.unvisited_links.update(orig_page.links)

        return orig_page

    def crawl_site(self):
        """Crawl samediggi.no."""
        while self.unvisited_links:
            link = self.unvisited_links.pop()

            if link not in self.visited_links:
                self.crawl_pageset(link)

            self.unvisited_links.difference_update(self.visited_links)

    def is_page_addable(self, page: SamediggiNoPage | None):
        """Add a page to the list of parallel pages."""
        if page is None:
            return False

        return page.saveable and page.claimed_lang == page.real_lang

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

    def get_page_set(self, orig_page) -> list[SamediggiNoPage]:
        """Get parallel pages for the original page.

        Args:
            orig_page: The original page to get parallel pages for.

        Returns:
            A list of parallel pages.
        """
        crawled_pages = [orig_page]
        crawled_pages.extend(
            [self.crawl_page(link) for link in orig_page.parallel_links]
        )

        pages = [page for page in crawled_pages if self.is_page_addable(page)]

        # If there is only a norwegian page, return an empty list
        # We are interested in the saami pages, the norwegian page is
        # valueable only if there is a saami page to compare it to
        if len(pages) and pages[0].claimed_lang == "nob":
            return []

        return pages

    def crawl_pageset(self, link):
        """Crawl a pageset that link gives us."""

        pages = self.get_page_set(self.crawl_page(link))

        self.set_parallel_info(pages)
        for page in pages:
            self.dupe_table[page.digest] = page.corpuspath.orig
            page.save()
            self.vcs[page.real_lang].add(page.corpuspath.orig)
            self.vcs[page.real_lang].add(page.corpuspath.xsl)
