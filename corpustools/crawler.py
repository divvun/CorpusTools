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
"""This file contains routines to crawl sites containing saami text."""


import os
import sys
from pathlib import Path

from corpustools import adder, namechanger, util
from corpustools.text_cat import Classifier


class Crawler:
    """A base class to save downloaded files to the corpus."""

    languageguesser = Classifier()
    unvisited_links: set[str] = set()
    visited_links: set[str] = set()
    download_links: set[str] = set()
    corpus_adders: dict[str, AddToCorpus] = {}

    def __init__(self) -> None:
        """Initialise the Crawler class."""
        gtlangs = os.getenv("GTLANGS")
        if not gtlangs:
            raise ValueError("GTLANGS not set")
        self.goaldir = Path(gtlangs)
        self.corpus_adders = {}
        self.downloader = adder.UrlDownloader(os.path.join(self.goaldir, "tmp"))

    def __del__(self):
        """Add all files to the corpus."""
        for _, corpus_adder in self.corpus_adders.items():
            corpus_adder.add_files_to_working_copy()

    def save_pages(self, pages):
        """Write pages to disk.

        pages is a list of url, lang tuples
        """
        parallelpath = ""

        for url, lang in pages:
            try:
                (_, tmpname) = self.downloader.download(url)
            except adder.AdderError as error:
                util.print_frame(debug=str(error) + "\n")
            else:
                normalised_name = namechanger.normalise_filename(
                    os.path.basename(tmpname)
                )
                normalised_path = os.path.join(
                    self.corpus_adders[lang].goalpath, normalised_name
                )

                if not os.path.exists(normalised_path):
                    parallelpath = self.corpus_adders[lang].copy_file_to_corpus(
                        tmpname, url, parallelpath=parallelpath
                    )
                    util.print_frame(debug=f"adding {parallelpath}")
                else:
                    parallelpath = normalised_path
        print(file=sys.stderr)

    def name_from_url(self, url):
        os.path.basename(url)
