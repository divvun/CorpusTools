# -*- coding:utf-8 -*-

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
#   Copyright © 2013-2016 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

"""Get and set metadata in metadata files."""


from __future__ import absolute_import, print_function, unicode_literals

import os
import sys

import lxml.etree as etree
import six

from corpustools import util

here = os.path.dirname(__file__)


class XsltException(Exception):
    """Raise this exception when errors arise in this module."""

    pass


class MetadataHandler(object):
    """Class to handle metadata in .xsl files.

    This class makes the xsl file
    """

    lang_key = "{http://www.w3.org/XML/1998/namespace}lang"

    def __init__(self, filename, create=False):
        """Initialise the MetadataHandler class.

        Args:
            filename (str): path to the metadata file.
            create (bool): Define if a MetadataHandler will be created from a
                metadata file belonging to a original file inside the corpus or
                created from a template file containing default values.

                If false, try to read a metadata file, and create a
                MetadataHandler from this. If the file does not exist, raise a
                util.ArgumentError.

                If True, create a new MetadataHandler with default values
                from the template file.

        Raises:
            util.ArgumentError if create is False and the filename does not
            exist.
            XsltException if there is a syntax error in the metadata file.
        """
        self.filename = filename

        if not os.path.exists(filename):
            if not create:
                raise util.ArgumentError("{} does not exist!".format(filename))
            self.tree = etree.parse(os.path.join(here,
                                                 'xslt/XSL-template.xsl'))
        else:
            try:
                self.tree = etree.parse(filename)
            except etree.XMLSyntaxError as e:
                raise XsltException('Syntax error in {}:\n{}'.format(
                    self.filename, e))

    def _get_variable_elt(self, key):
        """Get the variable element.

        Args:
            key (str): The name of the variable that should be looked up.

        Returns:
            etree._Element: The element that contains the key.
        """
        return self.tree.getroot().find(
            "{{http://www.w3.org/1999/XSL/Transform}}"
            "variable[@name='{}']".format(key))

    def set_variable(self, key, value):
        """Set the value of a variable.

        Args:
            key (str): Name of the variable to set.
            value (str): The value the variable should be set to.
        """
        try:
            variable = self._get_variable_elt(key)
            variable.attrib['select'] = "'{}'".format(value)
        except AttributeError as e:
            raise UserWarning(
                'Tried to update {} with value {}\n'
                'Error was {}'.format(key, value, str(e)))

    def get_variable(self, key):
        """Get the value associated with the key.

        Args:
            key (str): Name of the variable to get.

        Returns:
            str or None: The string contains the value associated with the key.
        """
        variable = self._get_variable_elt(key)
        if variable is not None:
            value = variable.attrib['select']
            if value is not None:
                return value.replace("'", "")
        return None

    def get_parallel_texts(self):
        """Get the parallel texts.

        Returns:
            dict: A dict of parallel files containing language:filename pairs.
        """
        parallels = self._get_variable_elt("parallels")
        if parallels is None:
            return {}
        else:
            elts = parallels.findall("parallel_text")
            return {p.attrib[self.lang_key]: p.attrib["location"].strip("'")
                    for p in elts
                    if p.attrib["location"].strip("'") != ""}

    def set_parallel_text(self, language, location):
        """Insert the name of a parallel file into the parallels element.

        Args:
            language (str): the language of the parallel file.
            location (str): the name of the parallel file.
        """
        attrib = {self.lang_key: language,
                  "location": location}
        parallels = self._get_variable_elt("parallels")
        if parallels is None:
            parallels = etree.Element(
                "{http://www.w3.org/1999/XSL/Transform}variable",
                name="parallels")
            parallels.text, parallels.tail = "\n", "\n\n"
            self.tree.getroot().append(parallels)
        elt = parallels.find("parallel_text[@{}='{}']".format(self.lang_key,
                                                              language))
        if elt is not None:
            elt.attrib.update(attrib)
        else:
            elt = etree.Element("parallel_text", attrib=attrib)
            elt.tail = "\n"
            parallels.append(elt)

    @property
    def skip_pages(self):
        """Turn a skip_pages entry into a list of pages."""
        pages = []
        skip_pages = self.get_variable('skip_pages')
        if skip_pages is not None:
            if 'odd' in skip_pages and 'even' in skip_pages:
                raise XsltException(
                    'Invalid format: Cannot have both "even" and "odd" in this line\n'
                    '{}'.format(skip_pages))

            if 'odd' in skip_pages:
                pages.append('odd')
                skip_pages = skip_pages.replace('odd', u'')
            if 'even' in skip_pages:
                pages.append('even')
                skip_pages = skip_pages.replace('even', '')

            # Turn single pages into single-page ranges, e.g. 7 → 7-7
            skip_ranges_norm = ((r if '-' in r else r + "-" + r)
                                for r in skip_pages.strip().split(",")
                                if r != "")

            skip_ranges = (tuple(six.moves.map(int, r.split('-')))
                           for r in skip_ranges_norm)

            try:
                pages.extend([page
                              for start, end in sorted(skip_ranges)
                              for page in six.moves.range(start, end + 1)])

            except ValueError:
                raise XsltException(
                    "Invalid format: {}".format(skip_pages))

        return pages

    def get_margin_lines(self, position=''):
        """Get the margin lines from the metadata file.

        Args:
            position (str): empty if getting regular margin lines,
                otherwise inner_ if getting inner margin lines.

        Returns:
            dict: Contains marginname:percentage pairs.
        """
        margin_lines = {
            key: self.get_variable(key).strip()
            for key in [position + 'right_margin', position + 'top_margin',
                        position + 'left_margin', position + 'bottom_margin']
            if (self.get_variable(key) is not None and
                self.get_variable(key).strip() != '')}

        return margin_lines

    def validate_and_set_margins(self, margin_lines):
        """Set and validate the margin lines.

        Args:
            margin_lines (dict): The dict consists of
                marginname:percentage pairs

        Returns:
            dict: The dict consists of marginname:percentage pairs.

        Raises:
            XsltException: Raise this exception if there are errors in the
                margin_lines.
        """
        _margins = {}
        for key, value in six.iteritems(margin_lines):
            if ('all' in value and ('odd' in value or 'even' in value) or
                    '=' not in value):
                raise XsltException(
                    'Invalid format in the variable {} in the file:\n{}\n{}\n'
                    'Format must be [all|odd|even|pagenumber]=integer'.format(
                        key, self.filename, value))
            try:
                _margins[key] = self.parse_margin_line(value)
            except ValueError:
                raise XsltException(
                    'Invalid format in the variable {} in the file:\n{}\n{}\n'
                    'Format must be [all|odd|even|pagenumber]=integer'.format(
                        key, self.filename, value))

        return _margins

    @property
    def margins(self):
        """Parse margin lines fetched from the .xsl file.

        Returns:
            dict: The dict consists of marginname:percentage pairs.
        """
        margin_lines = self.get_margin_lines()

        return self.validate_and_set_margins(margin_lines)

    @property
    def inner_margins(self):
        """Parse inner margin lines fetched from the .xsl file.

        Returns:
            dict: The dict consists of marginname:percentage pairs.

        Raises:
            XsltException: Raise this exception if there are errors in the
                inner_margin_lines.
        """
        margin_lines = self.get_margin_lines(position='inner_')
        _inner_margins = self.validate_and_set_margins(margin_lines)

        keys = list(_inner_margins.keys())
        for key in keys:
            if key == 'inner_left_margin':
                if 'inner_right_margin' not in keys:
                    raise XsltException(
                        'Invalid format in {}:\nboth '
                        'inner_right_margin and inner_left_margin must '
                        'be set'.format(self.filename))
                if sorted(_inner_margins['inner_left_margin']) != \
                        sorted(_inner_margins['inner_right_margin']):
                    raise XsltException(
                        'Invalid format in {}:\nboth '
                        'margins for the same pages must be set in '
                        'inner_right_margin and inner_left_margin'.format(
                            self.filename))
            if key == 'inner_right_margin' and 'inner_left_margin' not in keys:
                raise XsltException(
                    'Invalid format in {}:\nboth inner_right_margin '
                    'and inner_left_margin must be set'.format(self.filename))
            if key == 'inner_bottom_margin':
                if 'inner_top_margin' not in keys:
                    raise XsltException(
                        'Invalid format in {}:\nboth '
                        'inner_bottom_margin and inner_top_margin must '
                        'be set'.format(self.filename))
                if sorted(_inner_margins['inner_bottom_margin']) != \
                        sorted(_inner_margins['inner_top_margin']):
                    raise XsltException(
                        'Invalid format in {}:\n'
                        'margins for the same pages must be set in '
                        'inner_top_margin and inner_bottom_margin'.format(
                            self.filename))
            if key == 'inner_top_margin' and 'inner_bottom_margin' not in keys:
                raise XsltException(
                    'Invalid format in {}:\nboth inner_bottom_margin '
                    'and inner_top_margin must be set'.format(self.filename))

        return _inner_margins

    @staticmethod
    def parse_margin_line(value):
        """Parse a margin line read from the .xsl file.

        Args:
            param (str): contains the margin settings for a particular
                margin (right_margin, left_margin, top_margin, bottom_margin)

        Returns:
            dict: marginname: int (in percentage) pairs
        """
        m = {}
        for part in value.split(','):
            (pages, margin) = tuple(part.split('='))
            for page in pages.split(';'):
                m[page.strip()] = int(margin)

        return m

    def set_lang_genre_xsl(self):
        """Set the mainlang and genre variables in the xsl file, if possible."""
        with util.ignored(TypeError):
            xsl_tuple = util.split_path(self.filename)
            self.set_variable('mainlang', xsl_tuple.lang)
            self.set_variable('genre', xsl_tuple.genre)

    def write_file(self):
        """Write self.tree to self.filename."""
        try:
            with open(self.filename, 'wb') as f:
                f.write(etree.tostring(self.tree,
                                       encoding="UTF-8",
                                       xml_declaration=True))
        except IOError as e:
            print('cannot write', self.filename)
            print(e)
            sys.exit(254)
