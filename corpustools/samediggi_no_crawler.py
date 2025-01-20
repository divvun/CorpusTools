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


import hashlib
import os
from copy import deepcopy
from pathlib import Path
from typing import Iterator
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import requests
from lxml import etree

from corpustools import (
    adder,
    corpuspath,
    crawler,
    namechanger,
    text_cat,
    versioncontrol,
)
from corpustools.samediggi_no_links import get_filtered_links


def make_digest(bytestring: bytes) -> str:
    """Make a md5 hash to identify possible dupes."""
    hasher = hashlib.md5()
    hasher.update(bytestring)
    return hasher.hexdigest()


class SamediggiNoPage:
    """Save a samediggi.no page to the corpus."""

    language_mapper = {
        "nb": "nob",
        "sma": "sma",
        "se": "sme",
        "smj": "smj",
    }
    corpus_dir = os.getenv("GTLANGS")
    content_min_word_length = 10

    def __init__(
        self,
        original_url: str,
        html_element: etree._Element,
        dupe_table: dict[str, Path],
    ):
        """Initialise the SamediggiNoPage class."""
        self.url = original_url
        self.parsed_url = urlparse(self.url)
        self.tree = html_element
        self.dupe = False
        self.links = get_filtered_links(self.parsed_url, self.tree)

        if self.corpus_dir is None:
            raise SystemExit("GTLANGS is not set!")

        fullpath = (
            Path(self.corpus_dir)
            / f"corpus-{self.claimed_lang}-orig"
            / "admin/sd/samediggi.no"
            / namechanger.normalise_filename(self.create_filename())
        )

        self.digest = make_digest(self.content_string)
        possible_dupe = dupe_table.get(self.digest, fullpath)
        self.corpuspath = corpuspath.make_corpus_path(possible_dupe)
        if fullpath == possible_dupe:
            self.set_initial_metadata()
        else:
            self.dupe = True

    def create_filename(self):
        title = (
            self.tree.findtext(".//title").strip().replace("/", "_").replace(".", "_")
        )
        if title:
            return title.rsplit(" - S")[0] + ".html"

        return adder.url_to_filename(self.url)

    @property
    def content(self):
        """Extract only the content that is interesting from the web page."""
        content = etree.Element("html")
        body = etree.SubElement(content, "body")
        for xpath_directive in [
            './/article[@class="artikkel"]',
        ]:
            for element in self.tree.xpath(xpath_directive):
                body.append(self.filter_content((deepcopy(element))))

        return content

    @staticmethod
    def filter_content(element):
        """Remove elements without interesting content."""
        for unwanted in [
            './/div[@class="legacy-content-block"]',
            './/div[starts-with(@class, "InnholdForfatter")]',
            './/div[@class="videodetector"]',
            './/div[starts-with(@class, "il-feedback-form")]',
            './/div[starts-with(@class, "liste")]',
            ".//iframe",
            './/span[@class="file-ext-size"]',
            './/div[@class="fil"]',
            './/a[@class="InnholdLinkTekst  "]',
            './/div[contains(@id, "Script")]',
        ]:
            for unwanted_element in element.xpath(unwanted):
                unwanted_element.getparent().remove(unwanted_element)

        return element

    @property
    def content_string(self):
        """This will be the content of the saved file."""
        return etree.tostring(self.content, encoding="utf8", pretty_print=True)

    def set_initial_metadata(self):
        """Extract metadata from the web page."""
        self.corpuspath.metadata.set_variable(
            "title", self.tree.find(".//title").text.strip()
        )
        self.corpuspath.metadata.set_variable("filename", self.url)
        self.corpuspath.metadata.set_variable("genre", "admin")
        self.corpuspath.metadata.set_variable("mainlang", self.claimed_lang)
        self.corpuspath.metadata.set_variable("license_type", "free")
        if self.claimed_lang != "nob":
            self.corpuspath.metadata.set_variable("translated_from", "nob")
        time = self.tree.find('.//span[@class="byline__published-date-value"]')
        if time is not None:
            self.corpuspath.metadata.set_variable("year", time.text[6:10])

    @property
    def basename(self) -> str:
        """Get the name of the corpus path."""
        return self.corpuspath.orig.name

    def sanity_test(self):
        """Check if the pages seem to have the expected structure."""
        if not self.parallel_links:
            raise SystemExit(
                "The format of links to parallel documents has changed {}".format(
                    self.url
                )
            )
        for parallel_link in self.parallel_links:
            if not parallel_link.startswith("https://sametinget.no"):
                raise SystemExit(
                    f"The links to parallel documents has changed {self.url}"
                )
        if self.claimed_lang is None:
            raise SystemExit("Language format has changed.")

    @property
    def parallel_links(self):
        """Get links to the parallels of this document."""

        def fix_urlparts(lang):
            param = {"sprak": f"{langcode[lang]}"}
            query.update(param)
            url_parts[4] = urlencode(query)

            return urlunparse(url_parts)

        langcode = {"sme": 12, "smj": 15, "sma": 14, "nob": 1}
        these_langs = [lang for lang in langcode if lang != self.claimed_lang]

        url_parts = list(self.parsed_url)
        query = dict(parse_qsl(url_parts[4]))

        return [fix_urlparts(lang) for lang in these_langs]

    @property
    def saveable(self):
        """Check if the content of this file is worth saving."""
        return (
            len(self.content) and len(self.body_text.split()) > self.content_min_length
        )

    @property
    def claimed_lang(self):
        """Return the language of the file."""
        content_language = self.tree.find('.//meta[@name="language"]')

        return self.language_mapper[content_language.get("content")]

    @property
    def body_text(self):
        """Get all the text inside 'body'."""
        return " ".join(self.content.xpath(".//text()"))

    def set_parallel_file(self, lang, name):
        """Update metadata info on parallel files."""
        self.corpuspath.metadata.set_parallel_text(lang, name)

    def save(self):
        """Save html and metadata."""
        self.corpuspath.orig.write_bytes(self.content_string)
        self.corpuspath.metadata.write_file()


class SamediggiNoCrawler(crawler.Crawler):
    """Crawl samediggi.no and save html documents to the corpus."""

    langs = ["nob", "sma", "sme", "smj"]
    languageguesser = text_cat.Classifier()

    def __init__(self):
        """Initialise the SamediggiNoCrawler class."""
        super().__init__()
        self.unvisited_links.add("https://sametinget.no/")
        self.vcs = {
            lang: versioncontrol.vcs(self.goaldir / f"corpus-{lang}-orig")
            for lang in self.langs
        }

        self.dupe_table = self.make_dupe_tuple()

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

    def make_dupe_tuple(self) -> dict[str, Path]:
        """Make a hash/filename tuple to be used in the dupe table."""
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
            result.url, etree.HTML(result.text), self.dupe_table()
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

        body_lang = self.languageguesser.classify(page.body_text, langs=self.langs)
        return page.saveable and page.claimed_lang == body_lang

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
        pages: list[SamediggiNoPage] = []

        if self.is_page_addable(orig_page):
            pages.append(orig_page)

        for parallel_link in orig_page.parallel_links:
            page = self.crawl_page(parallel_link)
            if self.is_page_addable(page):
                pages.append(page)

        # If there is only a norwegian page, return an empty list
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
            self.vcs[page.lang].add(page.corpuspath.orig)
            self.vcs[page.lang].add(page.corpuspath.xsl)
