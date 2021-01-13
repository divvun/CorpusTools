# -*- coding: utf-8 -*-

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
#   Copyright © 2012-2020 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""This file manages conversion of files to the Giella xml format."""

import argparse
import logging
import multiprocessing
import os

import six

from corpustools import argparse_version, converter, text_cat, util, xslsetter

LOGGER = logging.getLogger(__name__)


class ConverterManager(object):
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

    def __init__(self,
                 lazy_conversion=False,
                 write_intermediate=False,
                 goldstandard=False):
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
            orig_file: string containing the path to the original file.
        """
        try:
            conv = converter.Converter(
                orig_file, lazy_conversion=self.lazy_conversion)
            conv.write_complete(self.languageguesser())
        except (util.ConversionError, ValueError) as error:
            LOGGER.warn('Could not convert %s\n%s', orig_file,
                        six.text_type(error))

    def convert_in_parallel(self):
        """Convert files using the multiprocessing module."""
        LOGGER.info('Starting the conversion of %d files', len(self.files))

        pool_size = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(processes=pool_size, )
        pool.map(unwrap_self_convert,
                 list(six.moves.zip([self] * len(self.files), self.files)))
        pool.close()
        pool.join()

    def convert_serially(self):
        """Convert the files in one process."""
        LOGGER.info('Starting the conversion of %d files', len(self.files))

        for orig_file in self.files:
            LOGGER.debug('converting %s', orig_file)
            self.convert(orig_file)

    def add_file(self, xsl_file):
        """Add file for conversion.

        Args:
            xsl_file (str): path to a metadata file
        """
        if os.path.isfile(xsl_file) and os.path.isfile(xsl_file[:-4]):
            metadata = xslsetter.MetadataHandler(xsl_file)
            if ((metadata.get_variable('conversion_status') == 'standard'
                 and not self.goldstandard)
                    or (metadata.get_variable('conversion_status').startswith(
                        'correct') and self.goldstandard)):
                self.files.append(xsl_file[:-4])
        else:
            LOGGER.warn('%s does not exist', xsl_file[:-4])

    @staticmethod
    def make_xsl_file(source):
        """Write an xsl file if it does not exist."""
        xsl_file = source if source.endswith('.xsl') else source + '.xsl'
        if not os.path.isfile(xsl_file):
            metadata = xslsetter.MetadataHandler(xsl_file, create=True)
            metadata.set_lang_genre_xsl()
            metadata.write_file()

        return xsl_file

    def add_directory(self, directory):
        """Add all files in a directory for conversion."""
        for root, _, files in os.walk(directory):
            for file_ in files:
                if file_.endswith('.xsl'):
                    self.add_file(os.path.join(root, file_))

    def collect_files(self, sources):
        """Find all convertible files in sources.

        Args:
            sources: a list of files or directories where convertable
            files are found.
        """
        LOGGER.info('Collecting files to convert')

        for source in sources:
            if os.path.isfile(source):
                xsl_file = self.make_xsl_file(source)
                self.add_file(xsl_file)
            elif os.path.isdir(source):
                self.add_directory(source)
            else:
                LOGGER.error(
                    'Can not process %s\n'
                    'This is neither a file nor a directory.', source)


def unwrap_self_convert(arg, **kwarg):
    """Unpack self from the arguments and call convert again.

    This is due to how multiprocess works:
    http://www.rueckstiess.net/research/snippets/show/ca1d7d90
    """
    return ConverterManager.convert(*arg, **kwarg)


def parse_options():
    """Parse the commandline options.

    Returns:
        a list of arguments as parsed by argparse.Argumentparser.
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Convert original files to giellatekno xml.')

    parser.add_argument(
        u'--serial',
        action=u"store_true",
        help=u"use this for debugging the conversion \
                        process. When this argument is used files will \
                        be converted one by one.")
    parser.add_argument(
        u'--lazy-conversion',
        action=u"store_true",
        help=u"Reconvert only if metadata have changed.")
    parser.add_argument(
        u'--write-intermediate',
        action=u"store_true",
        help=u"Write the intermediate XML representation \
                        to ORIGFILE.im.xml, for debugging the XSLT.\
                        (Has no effect if the converted file already exists.)")
    parser.add_argument(
        u'--goldstandard',
        action=u"store_true",
        help=u'Convert goldstandard and .correct files')
    parser.add_argument(
        'sources',
        nargs='+',
        help="The original file(s) or \
                        directory/ies where the original files exist")

    args = parser.parse_args()

    return args


def sanity_check():
    """Check that needed programs and environment variables are set."""
    util.sanity_check([u'wvHtml', u'pdftotext', 'latex2html'])
    if not os.path.isfile(converter.Converter.get_dtd_location()):
        raise util.SetupError(
            "Couldn't find {}\n"
            "Check that GTHOME points at the right directory "
            "(currently: {}).".format(converter.Converter.get_dtd_location(),
                                      os.environ['GTHOME']))


def main():
    """Convert documents to giellatekno xml format."""
    LOGGER.setLevel(logging.WARNING)
    try:
        sanity_check()
    except (util.SetupError, util.ExecutableMissingError) as error:
        raise SystemExit(str(error))

    args = parse_options()

    manager = ConverterManager(args.lazy_conversion, args.write_intermediate,
                               args.goldstandard)
    manager.collect_files(args.sources)

    try:
        if args.serial:
            LOGGER.setLevel(logging.DEBUG)
            manager.convert_serially()
        else:
            manager.convert_in_parallel()
    except util.ExecutableMissingError as error:
        raise SystemExit(str(error))
