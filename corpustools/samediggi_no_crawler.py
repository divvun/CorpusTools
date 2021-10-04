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
#   Copyright © 2013-2021 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""This file contains routines to crawl sites containing saami text."""


import fnmatch
import hashlib
import os
import re

import requests
import six
from lxml import etree

from corpustools import (
    adder,
    corpuspath,
    crawler,
    namechanger,
    text_cat,
    versioncontrol,
)


def make_digest(bytestring):
    """Make a md5 hash to identify possible dupes."""
    hasher = hashlib.md5()
    hasher.update(bytestring)
    return hasher.hexdigest()


class SamediggiNoPage:
    """Save a samediggi.no page to the corpus."""

    address_re = re.compile(r"/\w")
    unwanted_endings = (
        ".pdf",
        ".jpg",
        ".docx",
        ".xlsx",
        ".csv",
        ".pptx",
        ".eps",
        ".doc",
        ".png",
        ".xls",
    )
    language_mapper = {
        "no-bokmaal": "nob",
        "sma-NO": "sma",
        "sme-NO": "sme",
        "smj-NO": "smj",
    }
    corpus_dir = os.path.join(os.getenv("GTFREE"), "orig")

    def __init__(self, result, dupe_table):
        """Initialise the SamediggiNoPage class."""
        self.result = result
        self.url = result.url
        self.parsed_url = six.moves.urllib.parse.urlparse(self.url)
        self.tree = etree.HTML(result.text)
        fullpath = os.path.join(
            self.corpus_dir,
            self.lang,
            "admin/sd/samediggi.no",
            namechanger.normalise_filename(adder.url_to_filename(self.result)),
        )
        possible_dupe = dupe_table.get(make_digest(self.content_string), fullpath)
        self.corpuspath = corpuspath.CorpusPath(possible_dupe)
        if fullpath == possible_dupe:
            self.set_initial_metadata()
        else:
            print(f"\nDupe! {self.url} is dupe of {possible_dupe}\n")

    @property
    def content(self):
        """Extract only the content that is interesting from the web page."""
        content = etree.Element("html")
        body = etree.SubElement(content, "body")
        for xpath_directive in [
            './/div[@class="newsIntroBox"]',
            ".//article",
            './/div[@class="news"]',
            './/section[@class="blockInfo"]',
        ]:
            for element in self.tree.xpath(xpath_directive):
                body.append(
                    self.filter_content(etree.fromstring(etree.tostring(element)))
                )

        return content

    @staticmethod
    def filter_content(element):
        """Remove elements without interesting content."""
        for unwanted in [
            './/div[@class="embedFile"]',
            './/div[@class="date"]',
            './/div[starts-with(@class, "person ")]',
            './/div[starts-with(@class, "listArticleLink")]',
            './/div[@class="accordion document-list"]',
            './/article[@class="regionPage"]',
            './/ul[@class="listLinksLine"]',
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
        self.corpuspath.metadata.set_variable("mainlang", self.lang)
        self.corpuspath.metadata.set_variable("license_type", "free")
        if self.lang != "nob":
            self.corpuspath.metadata.set_variable("translated_from", "nob")
        time = self.tree.find(".//time")
        if time is not None:
            self.corpuspath.metadata.set_variable(
                "year", self.tree.find(".//time").get("datetime")[:4]
            )

    @property
    def basename(self):
        """Get the basename of the corpus filename."""
        return os.path.basename(self.corpuspath.orig)

    def sanity_test(self):
        """Check if the pages seem to have the expected structure."""
        if not self.parallel_links:
            raise SystemExit(
                "The format of links to parallel documents has changed {}".format(
                    self.url
                )
            )
        for parallel_link in self.parallel_links:
            if not parallel_link.startswith("https://www.sa"):
                raise SystemExit(
                    f"The links to parallel documents has changed {self.url}"
                )
        if self.lang is None:
            raise SystemExit("Language format has changed.")

    @property
    def parallel_links(self):
        """Get links to the parallels of this document."""
        return [
            "https:{}".format(a.get("href"))
            for a in self.tree.xpath('.//li[@class="itemLanguage"]/div/ul/li/a[@href]')
        ]

    @property
    def saveable(self):
        """Check if the content of this file is worth saving."""
        return self.result.ok and len(self.content) and len(self.body_text.split()) > 40

    @property
    def lang(self):
        """Return the language of the file."""
        content_language = self.tree.find('.//meta[@name="Content-language"]')

        return self.language_mapper[content_language.get("content")]

    def is_valid_address(self, href):
        """Check if this is an address that should be crawled."""
        match = self.address_re.match(href)
        return (
            match
            and "sametingets-vedtak-1989-2004" not in href
            and not href.endswith(self.unwanted_endings)
        )

    @property
    def links(self):
        """Get all the links found in a file."""
        return {
            six.moves.urllib.parse.urlunparse(
                (
                    self.parsed_url.scheme,
                    self.parsed_url.netloc,
                    address.get("href"),
                    "",
                    "",
                    "",
                )
            )
            for address in self.tree.xpath(".//a[@href]")
            if self.is_valid_address(address.get("href").lower())
        }

    @property
    def body_text(self):
        """Get all the text inside 'body'."""
        return " ".join(self.content.xpath(".//text()"))

    def set_parallel_file(self, lang, name):
        """Update metadata info on parallel files."""
        self.corpuspath.metadata.set_parallel_text(lang, name)

    def save(self):
        """Save html and metadata."""
        with open(self.corpuspath.orig, "wb") as xml:
            html = etree.Element("html")
            html.append(self.content)
            xml.write(self.content_string)
        self.corpuspath.metadata.write_file()


class SamediggiNoCrawler(crawler.Crawler):
    """Crawl samediggi.no and save html documents to the corpus."""

    langs = ["nob", "sma", "sme", "smj"]
    languageguesser = text_cat.Classifier()

    def __init__(self):
        """Initialise the SamediggiNoCrawler class."""
        super().__init__()
        self.unvisited_links.add("https://www.samediggi.no/")
        self.unvisited_links.add("https://www.sametinget.no/")
        self.unvisited_links.add("https://www.saemiedigkie.no/")
        self.unvisited_links.add("https://www.samedigge.no/")

        self.vcs = versioncontrol.vcs(self.goaldir)
        self.dupe_table = {digest: name for digest, name in self.make_dupe_tuple()}

    def make_dupe_tuple(self):
        """Make a hash/filename tuple to be used in the dupe table."""
        for lang in self.langs:
            root = os.path.join(
                os.getenv("GTFREE"), "orig", lang, "admin/sd/samediggi.no"
            )
            for path, _, filelist in os.walk(root):
                for name in fnmatch.filter(filelist, "*.html"):
                    fullpath = os.path.join(path, name)
                    with open(fullpath, "rb") as html_stream:
                        yield make_digest(html_stream.read()), fullpath

    def crawl_page(self, link):
        """Collect links from a page."""
        self.visited_links.add(link)
        result = requests.get(link)

        if result.ok and "html" in result.headers["content-type"].lower():
            orig_page = SamediggiNoPage(result, self.dupe_table)
            orig_page.sanity_test()
            self.visited_links.add(orig_page.url)
            self.unvisited_links = self.unvisited_links.union(orig_page.links)

            return orig_page

        return None

    def crawl_site(self):
        """Crawl samediggi.no."""
        while self.unvisited_links:
            link = self.unvisited_links.pop()

            if link not in self.visited_links:
                self.crawl_pageset(link)

    def add_page(self, page, parallel_pages):
        """Add a page to the list of parallel pages."""
        if page is not None and page.saveable:
            body_lang = self.languageguesser.classify(page.body_text, langs=self.langs)
            if page.lang == body_lang:
                if body_lang == "nob":
                    parallel_pages.append(page)
                else:
                    parallel_pages.insert(0, page)

    @staticmethod
    def set_parallel_info(parallel_pages):
        """Set the parallels for this set of parallel pages."""
        for parallel_page1 in parallel_pages:
            for parallel_page2 in parallel_pages:
                if parallel_page1 != parallel_page2:
                    parallel_page1.set_parallel_file(
                        parallel_page2.lang, parallel_page2.basename
                    )

    def crawl_pageset(self, link):
        """Crawl a pageset that link gives us."""
        pages = []

        print(link)
        orig_page = self.crawl_page(link)
        if orig_page is not None:
            self.add_page(orig_page, pages)
            for parallel_link in orig_page.parallel_links:
                self.add_page(self.crawl_page(parallel_link), pages)

            if pages and pages[0].lang != "nob":
                self.set_parallel_info(pages)
                for parallel_page in pages:
                    print(f"\t{parallel_page.corpuspath.orig}")
                    self.dupe_table[
                        make_digest(parallel_page.content_string)
                    ] = parallel_page.corpuspath.orig
                    parallel_page.save()
                    self.vcs.add(parallel_page.corpuspath.orig)
                    self.vcs.add(parallel_page.corpuspath.xsl)
                print()
