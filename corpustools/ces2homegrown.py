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
#   Copyright © 2021-2023 The University of Tromsø &
#                    the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Turn cesDoc xml into our homegrown xml."""
import argparse
import glob
import os
from datetime import datetime

from lxml import etree

from corpustools import argparse_version, corpuspath, util


def parse_options():
    """Parse the options for this script."""
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Turn cesDoc xml into our homegrown xml.",
    )

    parser.add_argument("lang", help="Language of the file")
    parser.add_argument("testament", choices=["ot", "nt"], help="Old or new testament")
    parser.add_argument("cesdoc", help="The cesdoc that should be converted")

    return parser.parse_args()


def main():
    """Turn cesDoc to homegrown xml."""
    args = parse_options()
    tree = etree.parse(args.cesdoc)

    chapter_paths = (
        save_chapter(
            args.lang,
            args.testament,
            f"{bookindex:0>2}_{chapterindex:0>3}",
            get_verses(chapter),
            os.path.basename(args.cesdoc),
        )
        for (bookindex, book) in enumerate(tree.xpath(".//div[@type='book']"), start=1)
        for (chapterindex, chapter) in enumerate(
            book.xpath(".//div[@type='chapter']"), start=1
        )
    )

    set_parallels(chapter_paths, args.testament, args.lang)


def get_verses(chapter):
    """Extract the chapter content."""
    body = etree.Element("body")
    for seg in chapter.iter("seg"):
        verse = etree.SubElement(body, "verse")
        verse.set("number", seg.get("id").split(".")[-1])
        verse.text = seg.text.strip()

    return body


def save_chapter(language, testament, filename, body, address):
    """Save chapter info."""
    language_year = {"nob": 2011, "sme": 2019.0}
    name = os.path.join(
        os.getenv("GTBOUND"),
        "orig",
        language,
        "bible",
        testament,
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
    path.metadata.set_variable("year", language_year.get(language, datetime.now().year))

    path.metadata.write_file()
    root = etree.Element("document")
    root.append(body)

    with open(name, "wb") as page_stream:
        page_stream.write(etree.tostring(root, encoding="utf8", pretty_print=True))

    return path


def set_parallels(chapter_paths, testament, new_lang):
    """Set the parallels.

    Use the nob names as the base, it has all the books and chapters.
    """
    nob_names = sorted(
        glob.glob(
            f'{os.path.join(os.getenv("GTBOUND"), "orig/nob/bible", testament, "bibel.no")}/*.xml'
        )
    )
    for (chapter_path, nob_name) in zip(chapter_paths, nob_names):
        nob_path = corpuspath.CorpusPath(nob_name)
        nob_meta = nob_path.metadata
        chapter_meta = chapter_path.metadata

        chapter_meta.set_parallel_text("nob", os.path.basename(nob_name))
        nob_meta.set_parallel_text(new_lang, os.path.basename(chapter_path.orig))
        nob_meta.write_file()

        for (lang, filename) in nob_meta.get_parallel_texts().items():
            chapter_meta.set_parallel_text(lang, filename)
            parallel_path = corpuspath.CorpusPath(nob_path.parallel(lang))
            parallel_path.metadata.set_parallel_text(
                new_lang, os.path.basename(chapter_path.orig)
            )
            parallel_path.metadata.write_file()

        chapter_meta.write_file()
