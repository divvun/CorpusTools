import hashlib
import os
from copy import deepcopy
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from lxml import etree

from corpustools import adder, corpuspath, namechanger
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
