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
#   along with program. If not, see <http://www.gnu.org/licenses/>.
#
#   Copyright © 2012-2023 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Add tmx files to a zipfile."""


import argparse
import time
import zipfile
from pathlib import Path

from corpustools import corpuspath


class PackageTmx:
    """A class to package tmx files into a zip file."""

    def __init__(self, packagename):
        """Set the counter on which filenames are based."""
        self.fileId = 1
        self.date = time.strftime("%Y-%m-%d", time.localtime())
        self.packagename = packagename
        self.zipname = self.packagename + "-" + self.date + ".zip"
        self.zipfile = zipfile.ZipFile(self.zipname, mode="w")

    def __del__(self):
        """Close the zipfile."""
        print(f"{self.packagename} tmx files are in {self.zipname}")
        self.zipfile.close()

    def find_tmx_files(self, tmxdir):
        """Find the tmx files in dirname, return them as a list."""
        return (
            path.as_posix()
            for path in corpuspath.collect_files([tmxdir], suffix=".tmx")
        )

    def generate_filename(self):
        """Generate a new file name. Return the new filename."""
        name = "".join(
            [self.packagename, "-", self.date, f"-{self.fileId:06d}", ".tmx"]
        )
        self.fileId += 1

        return name

    def write_new_file(self, tmxFile):
        """Write the file to the zipfile with a new filename."""
        self.zipfile.write(
            tmxFile,
            arcname=self.generate_filename(),
            compress_type=zipfile.ZIP_DEFLATED,
        )


def parse_options():
    """Parse the command line. No arguments expected."""
    parser = argparse.ArgumentParser(
        description="Package tmx files found in a corpus directory into zipfiles."
    )
    parser.add_argument("corpusdir", help="A corpus directory where tmx files exist")

    return parser.parse_args()


def main():
    """Make a package containing the tmx files."""
    args = parse_options()

    corpusdir = Path(args.corpusdir).resolve()
    lang1 = corpusdir.parts[-1].split("-")[1]
    for tmxdir in corpusdir.glob("tmx/*"):
        packagetmx = PackageTmx(f"{lang1}2{tmxdir.name}")
        for filename in packagetmx.find_tmx_files(tmxdir):
            packagetmx.write_new_file(filename)
