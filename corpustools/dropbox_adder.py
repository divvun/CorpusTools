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
#   Copyright © 2021 The University of Tromsø
#   http://giellatekno.uit.no & http://divvun.no
#
"""Add files received from Sámediggi as zipfiles to freecorpus."""


import os
import sys
from corpustools import adder
import zipfile


def pairs(files):
    for f in files:
        parts = f.split(".")
        no_suffix = ".".join(parts[:-1])
        if no_suffix[-3:].lower() == "nob":
            for i in ["sme", "SME", "sam", "SAM", "sám"]:
                thissme = no_suffix[:-3] + i + "." + parts[-1]
                if thissme in files:
                    yield f, thissme


def main():
    """Add files from zip files"""
    dropbox_adders = {
        lang: adder.AddToCorpus(
            os.getenv("GTFREE"), lang, os.path.join("admin", "sd", "dropbox")
        )
        for lang in ["nob", "sme"]
    }

    sami_zip = sys.argv[1]
    subdir = f'/tmp/{os.path.basename(sami_zip.replace(".zip", ""))}'
    zipfile.ZipFile(sami_zip).extractall(subdir)

    for (nob, sme) in pairs(
        {os.path.join(root, f) for root, _, files in os.walk(subdir) for f in files}
    ):
        try:
            nob_in_free = dropbox_adders["nob"].copy_file_to_corpus(
                origpath=nob, metadata_filename=os.path.basename(nob)
            )
            dropbox_adders["sme"].copy_file_to_corpus(
                origpath=sme,
                metadata_filename=os.path.basename(sme),
                parallelpath=nob_in_free,
            )
        except UserWarning:
            pass
        os.remove(nob)
        os.remove(sme)

    for dropbox_adder in dropbox_adders.values():
        dropbox_adder.add_files_to_working_copy()
