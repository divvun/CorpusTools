#!/usr/bin/env python

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
#   Copyright © 2013-2023 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Program to pick out documents to be saved to the corpus from samediggi.se.

The documents have been fetched using wget.
"""


import os
import shutil
import sys

from lxml import etree

from corpustools import util, xslsetter

here = os.path.dirname(__file__)
version = os.path.join(here, "_version.py")
scope = {}
exec(open(version).read(), scope)
version = scope["VERSION"]


class DocumentPicker:
    """Pick documents from samediggi.se to be added to the corpus."""

    def __init__(self, source_dir):
        self.freecorpus = os.getenv("GTFREE")
        self.source_dir = source_dir
        self.file_dict = {}
        self.file_dict.setdefault("sma", [])
        self.file_dict.setdefault("sme", [])
        self.file_dict.setdefault("smj", [])
        self.file_dict.setdefault("swe", [])
        self.file_dict.setdefault("none", [])
        self.parallel_dict = {}
        self.total_file = 0

    def classify_files(self):
        """Iterate through all files, classify them according to language"""
        for root, dirs, files in os.walk(self.source_dir):
            for f in files:
                if f.endswith(".html"):
                    self.total_file += 1
                    self.classify_file(os.path.join(root, f))

    def get_parallel_name(self, file_, a):
        dirname = os.path.dirname(file_)
        href = a.get("href").replace("http://www.samediggi.se/", "")

        if ".." in href:
            dirname_parts = dirname.split("/")
            href_parts = href.split("/")
            dirname = "/".join(dirname_parts[:-1])
            href = "/".join(href_parts[1:])

        return os.path.join(dirname, href)

    def append_parallel(self, file_, a):
        if os.path.exists(self.get_parallel_name(file_, a)):
            self.parallel_dict[file_].append(self.get_parallel_name(file_, a))
        else:
            print(
                util.lineno(),
                self.get_parallel_name(file_, a),
                "does not exist",
                a.get("title"),
                file_,
                file=sys.stderr,
            )

    def get_parallels(self, a, file_):
        self.parallel_dict.setdefault(file_, [])

        prev = a.getprevious()
        next_ = a.getnext()

        while prev is not None:
            if prev != a:
                self.append_parallel(file_, prev)
            prev = prev.getprevious()

        while next_ is not None:
            if next_ != a:
                self.append_parallel(file_, next_)
            next_ = next_.getnext()

    def append_file(self, language, file_):
        self.file_dict[language].append(file_)
        self.file_dict["none"].remove(file_)

    def classify_file(self, file_):
        """Identify the language of the file"""
        parser = etree.HTMLParser()
        html = etree.parse(file_, parser)
        self.file_dict["none"].append(file_)

        for img in html.iter("img"):
            if img.get("src") is not None and "icon_flag_sme_dim.gif" in img.get("src"):
                self.append_file("sme", file_)
                self.get_parallels(img.getparent(), file_)
            elif img.get("src") is not None and "icon_flag_smj_dim.gif" in img.get(
                "src"
            ):
                self.append_file("smj", file_)
                self.get_parallels(img.getparent(), file_)
            elif img.get("src") is not None and "icon_flag_sma_dim.gif" in img.get(
                "src"
            ):
                self.append_file("sma", file_)
                self.get_parallels(img.getparent(), file_)
            elif img.get("src") is not None and "icon_flag_swe_dim.gif" in img.get(
                "src"
            ):
                self.append_file("swe", file_)
                self.get_parallels(img.getparent(), file_)

    def conclude(self):
        total = 0
        for key, value in self.file_dict.items():
            total += len(self.file_dict[key])
            print(key, len(self.file_dict[key]))
        print(total, self.total_file)

    def check_consistency(self):
        """Check if all files that claim to have parallels actually exist

        Remove the parallel file from the list of parallels
        """
        for file_ in self.parallel_dict:
            for parallel_file in self.parallel_dict[file_]:
                try:
                    self.parallel_dict[parallel_file]
                    if file_ not in self.parallel_dict[parallel_file]:
                        self.parallel_dict[file_].remove(parallel_file)
                except KeyError:
                    self.parallel_dict[file_].remove(parallel_file)

    def get_goal_name(self, file_, lang):
        filename = os.path.basename(file_)
        goalfile = os.path.join(
            self.freecorpus, "orig", lang, "admin", "sd", "www.samediggi.se", filename
        )

        return goalfile

    def set_metadata(self, file_, lang):
        mh = xslsetter.MetadataHandler(
            self.get_goal_name(file_, lang) + ".xsl", create=True
        )
        for key, value in self.set_variables(file_, lang).items():
            mh.set_variable(key, value)
        mh.write_file()

    def set_variables(self, file_, lang):
        variables = {}
        variables["filename"] = "http://" + file_.replace(".html", "")
        variables["license_type"] = "free"
        variables["sub_name"] = "Børre Gaup"
        variables["sub_email"] = "borre.gaup@uit.no"
        variables["mainlang"] = lang
        variables["monolingual"] = "1"

        if lang != "swe":
            variables["translated_from"] = "swe"

        if self.parallel_dict[file_]:
            variables["parallel_texts"] = "1"
            para_langs = ["sma", "sme", "smj", "swe"]
            para_langs.remove(lang)
            for parallel_file in self.parallel_dict[file_]:
                for para_lang in para_langs:
                    if parallel_file in self.file_dict[para_lang]:
                        variables["para_" + para_lang] = os.path.basename(parallel_file)

        return variables

    def move_swe_file(self, file_):
        for candidate in self.parallel_dict[file_]:
            if candidate in self.file_dict["swe"]:
                shutil.copy(candidate, self.get_goal_name(candidate, "swe"))
                self.set_metadata(candidate, "swe")

    def move_files_set_metadata(self):
        for lang in ["sma", "smj", "sme"]:
            for file_ in self.file_dict[lang]:
                shutil.copy(file_, self.get_goal_name(file_, lang))
                self.move_swe_file(file_)
                self.set_metadata(file_, lang)


def main():
    if sys.argv[1] == "-v":
        print(version)
        sys.exit(1)

    dp = DocumentPicker(sys.argv[1])
    dp.classify_files()
    dp.conclude()
    dp.check_consistency()
    dp.move_files_set_metadata()


if __name__ == "__main__":
    main()
