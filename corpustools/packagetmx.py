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
#   Copyright © 2012-2021 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Add tmx files to a zipfile."""


import argparse
import os
import time
import zipfile


class PackageTmx:
    """A class to package tmx files into a zip file."""

    def __init__(self, dirname):
        """Set the counter on which filenames are based."""
        self.fileId = 1
        self.date = time.strftime("%Y-%m-%d", time.localtime())
        self.dirname = dirname
        self.zipname = self.dirname + "-" + self.date + ".zip"
        self.zipfile = zipfile.ZipFile(self.zipname, mode="w")

    def __del__(self):
        """Close the zipfile."""
        print("All tmx files are in", self.zipname)
        self.zipfile.close()

    def find_tmx_files(self):
        """Find the tmx files in dirname, return them as a list."""
        filelist = []
        for root, dirs, files in os.walk(
            os.path.join(os.environ["GTFREE"], "prestable/tmx/" + self.dirname)
        ):
            for f in files:
                if f.endswith(".tmx"):
                    filelist.append(os.path.join(root, f))

        return filelist

    def generate_filename(self):
        """Generate a new file name. Return the new filename."""
        name = "".join([self.dirname, "-", self.date, f"-{self.fileId:06d}", ".tmx"])
        self.fileId += 1

        return name

    def write_new_file(self, tmxFile):
        """Write the file to the zipfile with a new filename."""
        # print "Writing", self.tmxFile, 'as', self.generateFilename()
        self.zipfile.write(
            tmxFile,
            arcname=self.generate_filename(),
            compress_type=zipfile.ZIP_DEFLATED,
        )


def parse_options():
    """Parse the command line. No arguments expected."""
    parser = argparse.ArgumentParser(
        description="Run this to add tmx "
        "files to a zip archive. It depends on "
        "tmx files to exist in "
        "$GTFREE/prestable/tmx."
    )

    parser.parse_args()


def main():
    """Make a package containing the tmx files."""
    parse_options()

    for dirname in ["nob2sme"]:
        packagetmx = PackageTmx(dirname)
        for filename in packagetmx.find_tmx_files():
            packagetmx.write_new_file(filename)
