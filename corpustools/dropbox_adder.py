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
#   Copyright © 2021-2023 The University of Tromsø
#   http://giellatekno.uit.no & http://divvun.no
#
"""Add files received from Sámediggi as zipfiles to freecorpus."""


import os
import sys
import zipfile

from corpustools import adder

LANGUAGES = {"sma": ["sma"], "sme": ["sme", "SME", "sam", "SAM", "sám"], "smj": ["smj"]}


def pairs(files):
    for f in files:
        parts = f.split(".")
        no_suffix = ".".join(parts[:-1])
        if no_suffix[-3:].lower() == "nob":
            for lang in LANGUAGES:
                for possible_name in LANGUAGES[lang]:
                    thissmi = no_suffix[:-3] + possible_name + "." + parts[-1]
                    if thissmi in files:
                        yield f, thissmi, lang


def main():
    """Add files from zip files"""
    dropbox_adders = {
        lang: adder.AddToCorpus(
            os.getenv("GTFREE"), lang, os.path.join("admin", "sd", "dropbox")
        )
        for lang in ["nob"] + LANGUAGES.keys()
    }

    sami_zip = sys.argv[1]
    subdir = f'/tmp/{os.path.basename(sami_zip.replace(".zip", ""))}'
    zipfile.ZipFile(sami_zip).extractall(subdir)

    for (nob, smi, sami_lang) in pairs(
        {os.path.join(root, f) for root, _, files in os.walk(subdir) for f in files}
    ):
        try:
            nob_in_free = dropbox_adders["nob"].copy_file_to_corpus(
                origpath=nob, metadata_filename=os.path.basename(nob)
            )
            dropbox_adders[sami_lang].copy_file_to_corpus(
                origpath=smi,
                metadata_filename=os.path.basename(smi),
                parallelpath=nob_in_free,
            )
        except UserWarning:
            pass
        os.remove(nob)
        os.remove(smi)

    for dropbox_adder in dropbox_adders.values():
        dropbox_adder.add_files_to_working_copy()
