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
#   Copyright © 2012-2025 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""This file manages conversion of files to the Giella xml format."""

import argparse
import logging
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial

from corpustools import argparse_version, converter, text_cat, util, xslsetter
from corpustools.common_arg_ncpus import NCpus

LOGGER = logging.getLogger(__name__)


class ConverterManager:
    """Manage the conversion of original files to corpus xml.

    Class/static variables:
        _languageguesser (text_cat.Classifier): Language guesser to indicate
            languages in the converted document.
    Attributes:
        write_intermediate (bool): indicate whether intermediate versions
            of the converted document should be written to disk.
        goldstandard (bool): indicating whether goldstandard documents
            should be converted.
        files (list of str): list of paths to original files that should
            be converted from original format to xml.
    """

    _languageguesser = None

    def languageguesser(self):
        """Return our language guesser.
        This is a class variable, but since it takes a while to initialise,
        we don't do it until it's needed."""
        if self._languageguesser is None:
            ConverterManager._languageguesser = text_cat.Classifier(None)
        return self._languageguesser

    def __init__(
        self, lazy_conversion=False, write_intermediate=False, goldstandard=False
    ):
        """Initialise the ConverterManager class.

        Args:
            lazy_conversion (bool): indicate whether conversion depends on the
                fact that metadata have changed since last conversion.
            write_intermediate (bool): indicating whether intermediate versions
                of the converted document should be written to disk.
            goldstandard (bool): indicating whether goldstandard documents
                should be converted.
        """
        self.lazy_conversion = lazy_conversion
        self.write_intermediate = write_intermediate
        self.goldstandard = goldstandard
        self.files = []

    def convert(self, orig_file):
        """Convert file to corpus xml format.

        Args:
            orig_file (str): the path to the original file.
        """
        try:
            conv = converter.Converter(orig_file, lazy_conversion=self.lazy_conversion)
            conv.write_complete(self.languageguesser())
        except (
            util.ConversionError,
            ValueError,
            IndexError,
        ) as error:
            LOGGER.warn("Could not convert %s\n%s", orig_file, error)
            raise

    def convert_in_parallel(self, pool_size):
        """Convert files using the multiprocessing module."""
        nfiles = len(self.files)
        futures = {}  # Future -> filename
        print(f"Starting parallel conversion with {pool_size} workers")
        failed = []
        with ProcessPoolExecutor(max_workers=pool_size) as pool:
            for file in self.files:
                fut = pool.submit(partial(self.convert, file))
                futures[fut] = file

            for i, future in enumerate(as_completed(futures), start=1):
                exc = future.exception()
                filename = futures[future]
                if exc is not None:
                    failed.append(filename)
                    print(f"[{i}/{nfiles} FAILED: {filename}")
                    print(exc)
                else:
                    print(f"[{i}/{nfiles}] done: {filename}")

        n_ok = nfiles - len(failed)
        print(f"all done converting. {n_ok} files converted ok, {len(failed)} failed")
        if failed:
            print("the files that failed to convert are:")
            for filename in failed:
                print(filename)

    def convert_serially(self):
        """Convert the files in one process."""
        LOGGER.info("Starting the conversion of %d files", len(self.files))

        for orig_file in self.files:
            LOGGER.debug("converting %s", orig_file)
            self.convert(orig_file)

    def add_file(self, xsl_file):
        """Add file for conversion.

        Args:
            xsl_file (str): path to a metadata file
        """
        if os.path.isfile(xsl_file) and os.path.isfile(xsl_file[:-4]):
            metadata = xslsetter.MetadataHandler(xsl_file)
            if (
                metadata.get_variable("conversion_status") in ["standard", "ocr"]
                and not self.goldstandard
            ) or (
                metadata.get_variable("conversion_status").startswith("correct")
                and self.goldstandard
            ):
                self.files.append(xsl_file[:-4])
        else:
            LOGGER.warn("%s does not exist", xsl_file[:-4])

    @staticmethod
    def make_xsl_file(source):
        """Write an xsl file if it does not exist."""
        xsl_file = source if source.endswith(".xsl") else source + ".xsl"
        if not os.path.isfile(xsl_file):
            metadata = xslsetter.MetadataHandler(xsl_file, create=True)
            metadata.set_lang_genre_xsl()
            metadata.write_file()

        return xsl_file

    def add_directory(self, directory):
        """Add all files in a directory for conversion."""
        for root, _, files in os.walk(directory):
            for file_ in files:
                if file_.endswith(".xsl"):
                    self.add_file(os.path.join(root, file_))

    def collect_files(self, sources):
        """Find all convertible files in sources.

        Args:
            sources (list of str): a list of files or directories where
                convertable files are found.
        """
        LOGGER.info("Collecting files to convert")

        for source in sources:
            if os.path.isfile(source):
                xsl_file = self.make_xsl_file(source)
                self.add_file(xsl_file)
            elif os.path.isdir(source):
                self.add_directory(source)
            else:
                LOGGER.error(
                    "Can not process %s\n" "This is neither a file nor a directory.",
                    source,
                )


def unwrap_self_convert(arg, **kwarg):
    """Unpack self from the arguments and call convert again.

    This is due to how multiprocess works:
    http://www.rueckstiess.net/research/snippets/show/ca1d7d90
    """
    return ConverterManager.convert(*arg, **kwarg)


def parse_options():
    """Parse the commandline options.

    Returns:
        (argparse.Namespace): the parsed commandline arguments
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Convert original files to giellatekno xml.",
    )

    parser.add_argument("--ncpus", action=NCpus)
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="skip converting files that are already converted (that already "
        "exist in the converted/ folder",
    )
    parser.add_argument(
        "--serial",
        action="store_true",
        help="use this for debugging the conversion \
                        process. When this argument is used files will \
                        be converted one by one.",
    )
    parser.add_argument(
        "--lazy-conversion",
        action="store_true",
        help="Reconvert only if metadata have changed.",
    )
    parser.add_argument(
        "--write-intermediate",
        action="store_true",
        help="Write the intermediate XML representation \
                        to ORIGFILE.im.xml, for debugging the XSLT.\
                        (Has no effect if the converted file already exists.)",
    )
    parser.add_argument(
        "--goldstandard",
        action="store_true",
        help="Convert goldstandard and .correct files",
    )
    parser.add_argument(
        "sources",
        nargs="+",
        help="The original file(s) or \
                        directory/ies where the original files exist",
    )

    args = parser.parse_args()

    return args


def sanity_check():
    """Check that needed programs and environment variables are set."""
    util.sanity_check(["pdftotext", "latex2html", "pandoc"])
    if not os.path.isfile(converter.Converter.get_dtd_location()):
        raise util.SetupError(
            "Couldn't find {}\n"
            "Check that GTHOME points at the right directory "
            "(currently: {}).".format(
                converter.Converter.get_dtd_location(), os.environ["GTHOME"]
            )
        )


def main():
    """Convert documents to giellatekno xml format."""
    LOGGER.setLevel(logging.WARNING)
    try:
        sanity_check()
    except (util.SetupError, util.ExecutableMissingError) as error:
        raise SystemExit(str(error)) from error

    args = parse_options()

    manager = ConverterManager(
        args.lazy_conversion, args.write_intermediate, args.goldstandard
    )
    manager.collect_files(args.sources)

    try:
        if args.serial:
            LOGGER.setLevel(logging.DEBUG)
            manager.convert_serially()
        else:
            manager.convert_in_parallel(args.ncpus)
    except util.ExecutableMissingError as error:
        raise SystemExit(str(error)) from error
