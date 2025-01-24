from pathlib import Path
from typing import Iterable

from lxml import etree

from corpustools.corpuspath import make_corpus_path
from corpustools.text_cat import Classifier


class NrkNoUnknownPageError(Exception):
    """Raise an error if the page is not recognised."""

    pass


class NrkNoPage:
    """Save a NRK sápmi page to the corpus."""

    languageguesser = Classifier()
    language_codes = {
        "nob",
        "sma",
        "sme",
        "smj",
    }

    def __init__(
        self,
        original_url: str,
        html_element: etree._Element,
        corpus_parent: Path,
    ):
        """Initialise the NrkNoPage class."""
        self.corpus_parent = corpus_parent
        self.url = original_url
        self.tree = html_element
        self.lang = self.languageguesser.classify(
            self.body_text, langs=list(self.language_codes)
        )
        self.article_id = self.url.split("/")[-1]
        self.links = {
            link.get("ec-id", "").replace("pp:", "")
            for link in self.tree.findall(".//a[@ec-id]")
            if link.get("ec-id") is not None and "pp:" in link.get("ec-id", "")
        }
        self.fullpath = make_corpus_path(
            self.corpus_parent
            / f"corpus-{self.lang}-orig-x-closed"
            / "news/nrk.no"
            / f"{self.url.split("/")[-1]}.html"
        )

        self.set_initial_metadata()

    @property
    def basename(self) -> str:
        """Get the name of the corpus path."""
        return self.fullpath.orig.name

    @property
    def canonical_url(self) -> str:
        """Return the link to the article."""
        url = self.tree.find('.//link[@rel="canonical"]')
        if url is None:
            raise SystemExit(f"No url found in {self.url}.")

        href = url.get("href")
        if href is None:
            raise SystemExit(f"No href found in {self.url}.")

        return href

    @property
    def body_text(self):
        """Get all the text inside 'body'."""
        return " ".join(self.content.xpath(".//text()"))

    @property
    def content(self) -> etree._Element:
        """Extract only the content that is interesting to save from the web page."""
        article_content = self.tree.find(".//article[@role='main']")
        if article_content is not None:
            return article_content

        bulletin_content = self.tree.find(".//div[@class='bulletin-text-body']")
        if bulletin_content is not None:
            article_content = bulletin_content.getparent()
            if article_content is not None:
                return article_content

        kortstokk_content = self.tree.find(".//kortstokk-app")
        if kortstokk_content is not None:
            return kortstokk_content

        raise NrkNoUnknownPageError(f"No content found in {self.url}.")

    @property
    def content_string(self):
        """This will be the content of the saved file."""
        return etree.tostring(self.content, encoding="utf8", pretty_print=True)

    @property
    def valid_authors(self) -> Iterable[list[str]]:
        """Find authors with the correct roles.

        Args:
            article (etree.Element): The parsed html document.

        Yields:
            (tuple[str, ...]): Authors
        """
        authors = [
            author_role.text
            for author_role in self.tree.findall('.//meta[@property="article:author"]')
            if author_role.text is not None
        ]

        if not authors:

            author = self.tree.find('.//meta[@name="author"]')
            if author is None:
                raise SystemExit(f"No authors found in {self.url}.")

            authors = [author.get("content", "")]

        return (author.split("/")[0].split() for author in authors)

    @property
    def parallel_ids(self) -> set[str]:
        """Get the id of the parallel document."""

        parellel_ids = [
            article_element.get("ec-id")
            for article_element in self.content.findall(".//a")
            if any(
                text in article_element.get("ec-name", "").lower()
                for text in [
                    "lohkh",
                    "lågå",
                    "loga",
                    "les på",
                ]
            )
        ]

        return {
            parallel_id.replace("pp:", "")
            for parallel_id in parellel_ids
            if parallel_id is not None
        }

    @property
    def title(self) -> str:
        title_element = self.tree.find('.//meta[@property="og:title"]')
        if title_element is None:
            raise SystemExit(f"No title element found in {self.url}.")

        title = title_element.get("content")

        if title is None:
            raise SystemExit(f"No content found in {self.url}.")

        return title

    @property
    def year(self) -> str:
        time_element = self.tree.find('.//meta[@name="dc.date.issued"]')
        if time_element is None:
            raise SystemExit(f"No time found in {self.url}.")

        time_str = time_element.get("content")

        if time_str is None:
            raise SystemExit(f"No time found in {self.url}.")

        return time_str[:4]

    def set_initial_metadata(self):
        """Set the metadata for the page."""
        for count, author_parts in enumerate(self.valid_authors, start=1):
            self.fullpath.metadata.set_variable(
                "author" + str(count) + "_ln", author_parts[-1]
            )
            self.fullpath.metadata.set_variable(
                "author" + str(count) + "_fn", " ".join(author_parts[:-1])
            )

        self.fullpath.metadata.set_variable("filename", self.canonical_url)
        self.fullpath.metadata.set_variable("title", self.title)
        self.fullpath.metadata.set_variable("year", self.year)
        self.fullpath.metadata.set_variable("publisher", "NRK")
        self.fullpath.metadata.set_variable("publChannel", "https://nrk.no/sapmi")
        self.fullpath.metadata.set_variable("license_type", "standard")

    def set_parallel_file(self, lang, name):
        """Update metadata info on parallel files."""
        self.fullpath.metadata.set_parallel_text(lang, name)

    def save(self):
        """Save html and metadata."""
        self.fullpath.orig.parent.mkdir(parents=True, exist_ok=True)
        self.fullpath.orig.write_bytes(self.content_string)
        self.fullpath.metadata.write_file()
