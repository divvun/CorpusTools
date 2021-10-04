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
"""Add files received from Sámediggi by Dropbox to freecorpus."""


import glob
import os
import subprocess

from corpustools import adder


def main():
    """Add files from Dropbox"""
    subdir = "Bálddalas teavsttat"
    subprocess.run(
        "rsync", "-av", f"{os.getenv('HOME')}/Dropbox/{subdir}", f"/tmp/", check=True
    )
    dropbox_adders = {
        lang: adder.AddToCorpus(
            os.getenv("GTFREE"), lang, os.path.join("admin", "sd", "dropbox")
        )
        for lang in ["nob", "sme"]
    }

    files = glob.glob(f"/tmp/{subdir}/*")
    for (nob, sme) in [
        (f, f.replace("nob.", "sme."))
        for f in files
        if "nob.doc" in f and f.replace("nob.", "sme.") in files
    ]:
        nob_in_free = dropbox_adders["nob"].copy_file_to_corpus(
            origpath=nob, metadata_filename=os.path.basename(nob)
        )
        dropbox_adders["sme"].copy_file_to_corpus(
            origpath=sme,
            metadata_filename=os.path.basename(sme),
            parallelpath=nob_in_free,
        )
        os.remove(nob)
        os.remove(sme)

    for lang in ["sme", "nob"]:
        dropbox_adders[lang].add_files_to_working_copy()
