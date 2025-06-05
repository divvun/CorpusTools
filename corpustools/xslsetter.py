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
"""Get and set metadata in metadata files."""


import os
import re
import sys

from lxml import etree

from corpustools import corpuspath, util

here = os.path.dirname(__file__)


class XsltError(Exception):
    """Raise this exception when errors arise in this module."""


class MetadataHandler:
    """Class to handle metadata in .xsl files.

    This class makes the xsl file
    """

    lang_key = "{http://www.w3.org/XML/1998/namespace}lang"

    def __init__(self, filename: str, create=False):
        """Initialise the MetadataHandler class.

        Args:
            filename: path to the metadata file.
            create (bool): Define if a MetadataHandler will be created from a
                metadata file belonging to a original file inside the corpus or
                created from a template file containing default values.

                If false, try to read a metadata file, and create a
                MetadataHandler from this. If the file does not exist, raise a
                util.ArgumentError.

                If True, create a new MetadataHandler with default values
                from the template file.

        Raises:
            util.ArgumentError:if create is False and the filename does not
                exist.
            XsltException: if there is a syntax error in the metadata file.
        """
        self.filename = filename

        if not os.path.exists(filename):
            if not create:
                raise util.ArgumentError(f"{filename} does not exist!")
            self.tree = etree.parse(os.path.join(here, "xslt/XSL-template.xsl"))
        else:
            try:
                self.tree = etree.parse(filename)
            except etree.XMLSyntaxError as error:
                raise XsltError(f"Syntax error in {self.filename}:\n{error}") from error

    def _get_variable_elt(self, key: str) -> etree._Element | None:
        """Get the variable element.

        Args:
            key: The name of the variable that should be looked up.

        Returns:
            The element that contains the key.
        """

        return self.tree.getroot().find(
            "{{http://www.w3.org/1999/XSL/Transform}}"
            "variable[@name='{}']".format(key)
        )

    def set_variable(self, key: str, value: str):
        """Set the value of a variable.

        Args:
            key (str): Name of the variable to set.
            value (str): The value the variable should be set to.
        """
        try:
            variable = self._get_variable_elt(key)
            variable.attrib["select"] = f"'{value}'"
        except AttributeError as error:
            raise UserWarning(
                "Tried to update {} with value {}\n"
                "Error was {}".format(key, value, str(error))
            ) from error

    def get_variable(self, key: str) -> str | None:
        """Get the value associated with the key.

        Args:
            key (str): Name of the variable to get.

        Returns:
            (str|None): The string contains the value associated with the key.
        """
        variable = self._get_variable_elt(key)
        if variable is not None:
            value = variable.attrib["select"]
            if value is not None:
                clean_value = value.replace("'", "")
                if clean_value:
                    return clean_value
        return None

    def get_set_variables(self):
        """Find all set variables.

        Yields:
            (tuple[str, Any]): a key/value pair
        """
        ns = {"xsl": "http://www.w3.org/1999/XSL/Transform"}
        for variable in self.tree.getroot().xpath(
            ".//xsl:variable[@select]", namespaces=ns
        ):
            value = self.get_variable(variable.get("name"))
            if value is not None and value.strip():
                yield variable.get("name"), value

    def get_parallel_texts(self) -> dict[str, str]:
        """Get the parallel texts.

        Returns:
            (dict[str, str]): A dict of parallel files containing
                language:filename pairs.
        """
        parallels = self._get_variable_elt("parallels")
        if parallels is None:
            return {}
        else:
            elts = parallels.findall("parallel_text")
            return {
                p.attrib[self.lang_key]: p.attrib["location"].strip("'")
                for p in elts
                if p.attrib["location"].strip("'") != ""
            }

    @property
    def mlangs(self):
        """Get the languages to look for in the document.

        Returns:
            (set[str]): A set of languages to look for in the document
        """
        mlangs = self._get_variable_elt("mlangs")
        if mlangs is None:
            return set()
        else:
            return {mlang.get(self.lang_key) for mlang in mlangs.findall("language")}

    def make_xsl_variable(self, name):
        elt = etree.Element("{http://www.w3.org/1999/XSL/Transform}variable", name=name)
        self.tree.getroot().append(elt)

        return elt

    def set_mlang(self, language):
        """Set a language in mlangs.

        Args:
            language (str): a language code that should be set.
        """
        mlangs = self._get_variable_elt("mlangs")
        if mlangs is None:
            mlangs = self.make_xsl_variable("mlangs")

        if language not in self.mlangs:
            mlang = etree.Element("language")
            mlang.attrib.update({self.lang_key: language})
            mlangs.append(mlang)

    def set_parallel_text(self, language, location):
        """Insert the name of a parallel file into the parallels element.

        Args:
            language (str): the language of the parallel file.
            location (str): the name of the parallel file.
        """
        attrib = {self.lang_key: language, "location": location}
        parallels = self._get_variable_elt("parallels")
        if parallels is None:
            parallels = self.make_xsl_variable("parallels")

        elt = parallels.find(f"parallel_text[@{self.lang_key}='{language}']")
        if elt is not None:
            elt.attrib.update(attrib)
        else:
            elt = etree.Element("parallel_text", attrib=attrib)
            elt.tail = "\n"
            parallels.append(elt)

    @property
    def skip_pages(self):
        """Turn a skip_pages entry into a list of pages.

        Returns:
            list (mixed): the list can contain the strings 'all',
                'even' and 'odd' or specific page numbers as integers.
        """
        pages = []
        skip_pages = self.get_variable("skip_pages")
        if skip_pages is not None:
            if "odd" in skip_pages and "even" in skip_pages:
                raise XsltError(
                    'Invalid format: Cannot have both "even" and "odd" in this line\n'
                    "{}".format(skip_pages)
                )

            if "odd" in skip_pages:
                pages.append("odd")
                skip_pages = skip_pages.replace("odd", "")
            if "even" in skip_pages:
                pages.append("even")
                skip_pages = skip_pages.replace("even", "")

            # Turn single pages into single-page ranges, e.g. 7 → 7-7
            skip_ranges_norm = (
                (r if "-" in r else r + "-" + r)
                for r in skip_pages.strip().split(",")
                if r != ""
            )

            skip_ranges = (tuple(map(int, r.split("-"))) for r in skip_ranges_norm)

            try:
                pages.extend(
                    [
                        page
                        for start, end in sorted(skip_ranges)
                        for page in range(start, end + 1)
                    ]
                )

            except ValueError as error:
                raise XsltError(f"Invalid format: {skip_pages}") from error

        return pages

    @property
    def skip_lines(self):
        """Turn a skip_lines entry into a list of lines.

        Returns:
            list (int): list of line to skip numbers as integers.
        """
        lines = []
        skip_lines = self.get_variable("skip_lines")
        if skip_lines is not None:
            # Turn single lines into single-page ranges, e.g. 7 → 7-7
            skip_ranges_norm = (
                (r if "-" in r else r + "-" + r)
                for r in skip_lines.strip().split(",")
                if r != ""
            )

            skip_ranges = (tuple(map(int, r.split("-"))) for r in skip_ranges_norm)

            try:
                lines.extend(
                    [
                        line
                        for start, end in sorted(skip_ranges)
                        for line in range(start, end + 1)
                    ]
                )

            except ValueError as error:
                raise XsltError(f"Invalid format: {skip_lines}") from error

        return lines

    @property
    def epub_excluded_chapters(self):
        """Turn a skip_lines entry into a list of lines.

        Returns:
            list (int): list of line to skip numbers as integers.
        """
        lines = []
        chosen = self.get_variable("epub_excluded_chapters")
        if chosen is not None:
            # Turn single lines into single-page ranges, e.g. 7 → 7-7
            skip_ranges_norm = (
                (r if "-" in r else r + "-" + r)
                for r in chosen.strip().split(",")
                if r != ""
            )

            skip_ranges = (tuple(map(int, r.split("-"))) for r in skip_ranges_norm)

            try:
                lines.extend(
                    [
                        line
                        for start, end in sorted(skip_ranges)
                        for line in range(start, end + 1)
                    ]
                )

            except ValueError as error:
                raise XsltError(f"Invalid format: {chosen}") from error

        return lines

    def get_margin_lines(self, position=""):
        """Get the margin lines from the metadata file.

        Args:
            position (str): empty if getting regular margin lines,
                otherwise inner_ if getting inner margin lines.

        Returns:
            (dict[str, str]): A dictionary of margin name to percentages
        """
        margin_lines = {
            key: self.get_variable(key).strip()
            for key in [
                position + "right_margin",
                position + "top_margin",
                position + "left_margin",
                position + "bottom_margin",
            ]
            if (
                self.get_variable(key) is not None
                and self.get_variable(key).strip() != ""
            )
        }

        return margin_lines

    def validate_and_set_margins(self, margin_lines):
        """Set and validate the margin lines.

        Args:
            margin_lines (dict[str, str]): The dict consists of
                marginname:percentage pairs

        Returns:
            (dict[str, int]): The dict consists of marginname:percentage pairs.

        Raises:
            XsltException: Raise this exception if there are errors in the
                margin_lines.
        """
        _margins = {}
        for key, value in margin_lines.items():
            if (
                "all" in value
                and ("odd" in value or "even" in value)
                or "=" not in value
            ):
                raise XsltError(
                    "Invalid format in the variable {} in the file:\n{}\n{}\n"
                    "Format must be [all|odd|even|pagenumber]=integer".format(
                        key, self.filename, value
                    )
                )
            try:
                _margins[key] = self.parse_margin_line(value)
            except ValueError as error:
                raise XsltError(
                    "Invalid format in the variable {} in the file:\n{}\n{}\n"
                    "Format must be [all|odd|even|pagenumber]=integer".format(
                        key, self.filename, value
                    )
                ) from error

        return _margins

    @property
    def margins(self):
        """Parse margin lines fetched from the .xsl file.

        Returns:
            (dict): The dict consists of marginname:percentage pairs.
        """
        margin_lines = self.get_margin_lines()

        return self.validate_and_set_margins(margin_lines)

    @property
    def inner_margins(self):
        """Parse inner margin lines fetched from the .xsl file.

        Raises:
            XsltError: On errors in the inner_margin_lines.

        Returns:
            (dict): The dict consists of marginname:percentage pairs.
        """
        margin_lines = self.get_margin_lines(position="inner_")
        _inner_margins = self.validate_and_set_margins(margin_lines)

        keys = list(_inner_margins.keys())
        for key in keys:
            if key == "inner_left_margin":
                if "inner_right_margin" not in keys:
                    raise XsltError(
                        "Invalid format in {}:\nboth "
                        "inner_right_margin and inner_left_margin must "
                        "be set".format(self.filename)
                    )
                if sorted(_inner_margins["inner_left_margin"]) != sorted(
                    _inner_margins["inner_right_margin"]
                ):
                    raise XsltError(
                        "Invalid format in {}:\nboth "
                        "margins for the same pages must be set in "
                        "inner_right_margin and inner_left_margin".format(self.filename)
                    )
            if key == "inner_right_margin" and "inner_left_margin" not in keys:
                raise XsltError(
                    "Invalid format in {}:\nboth inner_right_margin "
                    "and inner_left_margin must be set".format(self.filename)
                )
            if key == "inner_bottom_margin":
                if "inner_top_margin" not in keys:
                    raise XsltError(
                        "Invalid format in {}:\nboth "
                        "inner_bottom_margin and inner_top_margin must "
                        "be set".format(self.filename)
                    )
                if sorted(_inner_margins["inner_bottom_margin"]) != sorted(
                    _inner_margins["inner_top_margin"]
                ):
                    raise XsltError(
                        "Invalid format in {}:\n"
                        "margins for the same pages must be set in "
                        "inner_top_margin and inner_bottom_margin".format(self.filename)
                    )
            if key == "inner_top_margin" and "inner_bottom_margin" not in keys:
                raise XsltError(
                    "Invalid format in {}:\nboth inner_bottom_margin "
                    "and inner_top_margin must be set".format(self.filename)
                )

        return _inner_margins

    @staticmethod
    def parse_margin_line(value):
        """Parse a margin line read from the .xsl file.

        Args:
            value (str): contains the margin settings for a particular
                margin (right_margin, left_margin, top_margin, bottom_margin)

        Returns:
            (dict[str, int]): a dictionary of margin name to percentages (as
                integers)
        """
        m = {}
        for part in value.split(","):
            (pages, margin) = tuple(part.split("="))
            for page in pages.split(";"):
                m[page.strip()] = int(margin)

        return m

    def set_lang_genre_xsl(self):
        """Set the mainlang and genre variables in the xsl file."""
        with util.ignored(TypeError):
            path = corpuspath.make_corpus_path(self.filename)
            self.set_variable("mainlang", path.lang)
            self.set_variable("genre", path.filepath.parts[0])

    def write_file(self):
        """Write self.tree to self.filename."""
        try:
            with open(self.filename, "wb") as outfile:
                self.tree.write(outfile, encoding="utf-8", xml_declaration=True)
                outfile.write(b"\n")
        except OSError as e:
            print("cannot write", self.filename)
            print(e)
            sys.exit(254)

    @property
    def skip_elements(self) -> list[tuple[str, str]]:
        """Get the skip_elements variable.

        Returns:
            (list[tuple[xpath, xpath]]): each tuple has a (start, end) xpath
                path pair. If the skip_elements variable is empty, return None.
        """

        def get_with_ns(path: str) -> str:
            return "/".join(
                [
                    (
                        "html:" + part
                        if not part.startswith("html:") and re.match(r"^\w", part)
                        else part
                    )
                    for part in path.split("/")
                ]
            )

        def get_pair(pair: str) -> tuple[str, str]:
            p = pair.split(";")
            return (get_with_ns(p[0].strip()), get_with_ns(p[1].strip()))

        if self.get_variable("skip_elements"):
            return [
                get_pair(pair) for pair in self.get_variable("skip_elements").split(",")
            ]

        return []

    @property
    def linespacing(self):
        """:obj:`dict` of :obj:`str` pairs

        The key may be all, odd, even or a pagenumber, the value is a
        floating point number.

        Raises:
            XsltError: On invalid format
        """
        value = self.get_variable("linespacing")

        if (value) and (
            "all" in value and ("odd" in value or "even" in value) or "=" not in value
        ):
            raise XsltError(
                "Invalid format in the variable linespacing in the file:"
                "\n{}\n{}\n"
                "Format must be [all|odd|even|pagenumber]=float".format(
                    self.filename, value
                )
            )

        try:
            return self.parse_linespacing_line(value)
        except ValueError as error:
            raise XsltError(
                "Invalid format in the variable linespacing in the file:"
                "\n{}\n{}\n"
                "Format must be [all|odd|even|pagenumber]=float".format(
                    self.filename, value
                )
            ) from error

    @staticmethod
    def parse_linespacing_line(value):
        """Parse a linespacing line read from the .xsl file.

        Args:
            value (str): contains the linespacing

        Returns:
            (dict[str, float]): page: float pairs
        """
        line_dict = {}
        if value:
            for part in value.split(","):
                (pages, linespacing) = tuple(part.split("="))
                for page in pages.split(";"):
                    line_dict[page.strip()] = float(linespacing)

        return line_dict

    @property
    def xsl_templates(self):
        """Find all xsl:template elements.

        Returns:
            (list[xml.etree.Element]): List of etree.Element
        """
        ns = {"xsl": "http://www.w3.org/1999/XSL/Transform"}
        return self.tree.getroot().xpath(".//xsl:template", namespaces=ns)
