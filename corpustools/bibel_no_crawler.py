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
#   Copyright © 2021 The University of Tromsø &
#                    the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Functions to fetch bible texts from bibel.no."""
import functools
import os
from datetime import datetime

import requests
from corpustools import corpuspath, namechanger, util
from lxml import etree, html


@functools.lru_cache
def fetch_page(address):
    """Fetch a page."""
    main_content = requests.get(address)
    return html.document_fromstring(main_content.text)


def get_books(tree):
    """Get the addresses for the books on bible.no."""
    books = {"ot": [], "nt": []}
    for table_row in tree.xpath(".//table[@class='booklist']/tr"):
        for (index, address) in enumerate(table_row.xpath("./td[@class='tablePR']/a")):
            if index == 1:
                books["ot"].append(address.get("href"))
            if index == 3:
                books["nt"].append(address.get("href"))

    return books


def get_chapter_addresses(first_chapter_page):
    """Extract the addresses to the other chapters."""
    return (
        (address.text.strip(), address.get("href"))
        for address in first_chapter_page.xpath(".//a[@class='versechapter']")
    )


def get_verses(chapter_page):
    """Extract the chapter content.

    If the table does not exist, then this chapter does not exist. This is the
    case for some sámi translations.
    """

    content_element = chapter_page.find(".//table[@class='biblesingle']/tr/td")
    if content_element is not None:

        for bibleref in content_element.xpath(".//div[@class='bibleref']"):
            bibleref.getparent().remove(bibleref)

        body = etree.Element("body")
        lastparent = body
        for element in content_element:
            if element.get("class") in ["versenumberdropcap", "versenumber"]:
                verse_number = element.get("name")
            if element.get("class") == "verse":
                text = " ".join("".join(element.itertext()).split())
                if text:
                    verse = etree.SubElement(lastparent, "verse")
                    verse.set("number", verse_number)
                    verse.text = text
            if element.get("class") == "verseheader" and element.text is not None:
                lastparent = etree.SubElement(body, "section")
                lastparent.set("title", element.text.strip())

        return body

    return None


def save_page(language, bookname, filename, body, address):
    """Save chapter page."""
    language_year = {"nob": 2011, "sme": 2019.0}
    name = os.path.join(
        os.getenv("GTBOUND"),
        "orig",
        language,
        "bible",
        bookname,
        "bibel.no",
        f"{filename}.xml",
    )
    with util.ignored(OSError):
        os.makedirs(os.path.dirname(name))

    path = corpuspath.CorpusPath(name)
    path.metadata.set_variable("filename", address)
    path.metadata.set_variable("mainlang", language)
    path.metadata.set_variable("genre", "bible")
    path.metadata.set_variable("monolingual", "1")
    path.metadata.set_variable("license_type", "standard")
    path.metadata.set_variable("publisher", "Det Norske Bibelselskap")
    path.metadata.set_variable("publChannel", "https://bibel.no/nettbibelen")
    path.metadata.set_variable("year", language_year.get(language, datetime.now().year))

    path.metadata.write_file()
    root = etree.Element("document")
    root.append(body)

    with open(name, "wb") as page_stream:
        page_stream.write(
            etree.tostring(root, encoding="utf8", pretty_print=True) + b"\n"
        )

    return path


def fetch_other_languages(book_name, bookindex, chapternumber, address):
    """Given an address, fetch all parallels."""
    languages = {
        "nob": "bokmal11",
        "sme": "nordsamisk19",
        "sma": "sorsamisk",
        "smj": "lulesamisk",
    }

    parallels = []
    for lang in ["nob", "sme", "smj", "sma"]:
        new_address = f'{address.replace("bokmal11", languages[lang])}'
        # first_page = html.parse("nob_mat11.html")
        first_page = fetch_page(new_address)
        body = get_verses(first_page)
        if body is not None:
            header = first_page.find(".//h1").text.strip()
            parallels.append(
                save_page(
                    lang,
                    book_name,
                    filename=namechanger.normalise_filename(
                        f"{bookindex:0>2}_{chapternumber:0>3}_{header}"
                    ),
                    body=body,
                    address=new_address,
                )
            )

        for this_parallel in parallels:
            for that_parallel in parallels:
                if this_parallel != that_parallel:
                    this_parallel.metadata.set_parallel_text(
                        that_parallel.metadata.get_variable("mainlang"),
                        os.path.basename(that_parallel.orig),
                    )
            this_parallel.metadata.write_file()


def main():
    """"Fetch bible texts from bibel.no"""
    prefix = "https://bibel.no"
    books = get_books(fetch_page("https://bibel.no/nettbibelen?slang=bokmal11"))
    for book_name in books:
        for (bookindex, first_address) in enumerate(books[book_name], start=1):
            address = f"{prefix}{first_address}"
            first_page = fetch_page(address)
            fetch_other_languages(book_name, bookindex, 1, address)
            for (chapter_number, chapter_address) in get_chapter_addresses(first_page):
                chapter_address = f"{prefix}{chapter_address}"
                fetch_other_languages(
                    book_name, bookindex, chapter_number, chapter_address
                )


if __name__ == "__main__":
    main()
