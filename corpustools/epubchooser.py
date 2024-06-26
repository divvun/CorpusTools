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
#   Copyright © 2017-2023 The University of Tromsø &
#                    the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Set which parts of an epub should be omitted.

It is possible to filter away chapters and ranges of elements from an epub
file. This is a helper program for that purpose.
"""


import argparse
import sys

import epub
from prompt_toolkit import prompt

from corpustools import argparse_version, epubconverter, xslsetter


class RangeHandler:
    """Handle skip_elements ranges.

    Attributes:
        xpaths (list of str): the xpaths of the remaining html document
            after unwanted chapters have been removed.
        ranges (set of tuple of int):  Each tuple has a pair of ints
            pointing to places in the xpaths list.
    """

    xpaths = []
    _ranges = set()

    def clear_ranges(self):
        """Clear the _ranges set."""
        self._ranges.clear()

    def as_text(self, pair):
        """Return a range as text.

        Args:
            pair (tuple): pairs of indexes to elements in self.xpaths.
                The second part of the tuple may be empty.

        Returns:
            (str): the string representation
        """
        if pair[1]:
            return f"{self.xpaths[pair[0]]};{self.xpaths[pair[1]]}"
        else:
            return f"{self.xpaths[pair[0]]};"

    @property
    def ranges(self):
        """Return the textual version of the range."""
        return ",".join(
            [self.as_text(pair) for pair in sorted(self._ranges, reverse=True)]
        )

    def check_range(self, xpath_pair):
        """Check that the xpath_pair is a valid range.

        Args:
            xpath_pair (tuple of str): a pair of xpaths

        Raises:
            KeyError: if invalid content is found.
        """
        if not xpath_pair[0]:
            raise KeyError("First xpath is empty.")
        if xpath_pair[0] not in self.xpaths:
            raise KeyError(f"{xpath_pair[0]} does not exist in this context")
        if xpath_pair[1] and xpath_pair[1] not in self.xpaths:
            raise KeyError(f"{xpath_pair[1]} does not exist in this context")

    def check_overlap(self, xpath_pair):
        """Check if xpath_pair overlaps any of the existing ranges.

        Args:
            xpath_pair (tuple of str): a pair of xpaths
        """
        for xpath in xpath_pair:
            if xpath:
                for pair in self._ranges:
                    if pair[1] and pair[0] < self.xpaths.index(xpath) < pair[1] + 1:
                        raise IndexError(
                            "{} < {} < {}".format(
                                self.xpaths[pair[0]], xpath, self.xpaths[pair[1]]
                            )
                        )
                    if pair[0] == self.xpaths.index(xpath):
                        raise IndexError(f"{self.xpaths[pair[0]]} == {xpath}")
                    if pair[1] == self.xpaths.index(xpath):
                        raise IndexError(f"{self.xpaths[pair[1]]} == {xpath}")

    def add_range(self, xpath_pair):
        """Add a new range.

        Args:
            xpath_pair (tuple of str): a pair of xpaths.
        """
        self.check_range(xpath_pair)
        self.check_overlap(xpath_pair)

        if not xpath_pair[1]:
            self._ranges.add((self.xpaths.index(xpath_pair[0]), ""))
        else:
            self._ranges.add(
                tuple(
                    sorted(
                        (
                            self.xpaths.index(xpath_pair[0]),
                            self.xpaths.index(xpath_pair[1]),
                        )
                    )
                )
            )


class EpubPresenter:
    """Class to present metadata and content.

    Attributes:
        path (str): path to the epub document
        book (epub.Book): the epub document to handle.
        metadata (xslsetter.MetadataHandler): the corpus metadata
            attached to the book.
        xpaths (list of str): the xpaths of the remaining html document
            after unwanted chapters have been removed.
    """

    def __init__(self, path):
        """Initialise the EpubPresenter class.

        Args:
            path (str): path to the epub document
        """
        self.path = path
        self.book = epub.Book(epub.open_epub(sys.argv[1]))
        self.metadata = xslsetter.MetadataHandler(sys.argv[1] + ".xsl")
        self.rangehandler = RangeHandler()

    @property
    def book_titles(self):
        """Get the all linear chapters of the epub book.

        Args:
            book (epub.Book): The epub book element

        Returns:
            (list[str]): The body of an xhtml file found in the
                epub file.
        """
        return [
            epubconverter.read_chapter(chapter)
            .find(".//{http://www.w3.org/1999/xhtml}title")
            .text
            for chapter in self.book.chapters
        ]

    @property
    def excluded_chapters(self):
        """Show the excluded chapters."""
        return self.metadata.epub_excluded_chapters

    @excluded_chapters.setter
    def excluded_chapters(self, new_excluded):
        """Set the exluded chapters in the metadata file.

        Args:
            new_excluded (list of int): the chapters to exclude.
        """
        self.metadata.set_variable(
            "epub_excluded_chapters", ", ".join([str(index) for index in new_excluded])
        )

    def print_choice(self):
        """Present omitted and present chapters."""
        print("\nIncluded chapters:")
        for index in self.not_chosen:
            print(f"[{index}]:\t{self.book_titles[index]}")

        print("\nExcluded chapters:")
        for index in self.excluded_chapters:
            print(f"[{index}]:\t{self.book_titles[index]}")

    @property
    def not_chosen(self):
        """The chapter that are not excluded."""
        return list(
            {x for x in range(len(self.book_titles))} - set(self.excluded_chapters)
        )

    def save(self):
        """Save metadata."""
        self.metadata.set_variable("skip_elements", self.rangehandler.ranges)
        self.metadata.write_file()

    @property
    def skip_elements(self):
        """Return a string representing the html elements that is omitted."""
        return self.rangehandler.ranges

    @skip_elements.setter
    def skip_elements(self, elements):
        """Set the md set_variable skip_elements.

        Args:
            elements (str): the elements that should be skip
        """
        self.metadata.set_variable("skip_elements", elements)

    def present_html(self):
        """Print the html that is left after omitting chapters."""
        self.print_xpath(
            epubconverter.extract_content(self.path, self.metadata), 0, 4, sys.stdout
        )

    def print_xpath(self, element, level, indent, out, xpath="", element_no=1):
        """Format an html document and write xpaths at tags openings.

        This function formats html documents for readability and prints
        xpaths to at tag openings, to see the structure of the given document
        and make it possible to choose xpaths. It ruins white space in
        text parts.

        Args:
            element (etree._Element): the element to format.
            level (int): indicate at what level this element is.
            indent (int): indicate how many spaces this element should be
                indented
            out (stream): a buffer where the formatted element is written.
            xpath (str): The xpath of the parent of this element.
            element_no (int): the position of the element tag
        """
        counter = {}
        tag = element.tag.replace("{http://www.w3.org/1999/xhtml}", "")

        out.write(" " * (level * indent))
        out.write(f"<{tag}")

        for att_tag, att_value in element.attrib.items():
            out.write(" ")
            out.write(att_tag)
            out.write('="')
            out.write(att_value)
            out.write('"')

        out.write(">")
        if xpath and "/body" in xpath:
            new_xpath = "{}/{}".format(xpath.replace("/html/", ".//"), tag)
            if element_no > 1:
                new_xpath = f"{new_xpath}[{element_no}]"
            out.write("\t")
            out.write(new_xpath)
            self.rangehandler.xpaths.append(new_xpath)

        out.write("\n")

        if element.text is not None and element.text.strip():
            out.write(" " * ((level + 1) * indent))
            out.write(element.text.strip())
            out.write("\n")

        for child in element:
            if not counter.get(child.tag):
                counter[child.tag] = 0
            counter[child.tag] += 1
            if element_no > 1:
                new_xpath = xpath + "/" + tag + "[" + str(element_no) + "]"
            else:
                new_xpath = xpath + "/" + tag
            self.print_xpath(
                child,
                level + 1,
                indent,
                out,
                xpath=new_xpath,
                element_no=counter[child.tag],
            )

        out.write(" " * (level * indent))
        out.write(f"</{tag}>\n")

        if level > 0 and element.tail is not None and element.tail.strip():
            for _ in range(0, (level - 1) * indent):
                out.write(" ")
            out.write(element.tail.strip())
            out.write("\n")


class EpubChooser:
    """Class to determine which parts of an epub should be omitted.

    Attributes:
        presenter (EpubPresenter): the presenter of the metadata and content
            of the epub file.
    """

    def __init__(self, path):
        """Initialise the EpubChooser class.

        Args:
            path (str): path to the document
        """
        self.presenter = EpubPresenter(path)

    def exclude_chapters(self):
        """Choose which chapters should be omitted from the epub file."""
        while 1:
            self.presenter.print_choice()
            text = prompt(
                "\nWould you like to \n"
                "* [c]lear and edit empty range\n"
                "* s[a]ve this and go to next step\n"
                "* [s]ave and quit\n* [q]uit without saving\n"
                "[c/a/s/q]: "
            )
            if text == "c":
                edits = prompt("Make new range: ")
                new_excluded = [int(index) for index in edits.split()]
                self.presenter.excluded_chapters = new_excluded
            elif text == "a":
                break
            elif text == "s":
                self.presenter.save()
                raise SystemExit("Saved your choices")
            elif text == "q":
                raise SystemExit("Did not save anything")
            else:
                print("Invalid choice, trying again.")

    def do_xpaths_exist(self):
        """Check if xpaths exist in this document."""
        if self.presenter.skip_elements:
            print("Original:", self.presenter.skip_elements)

        pairs = [pair.strip() for pair in self.presenter.skip_elements.split(",")]
        for pair in pairs:
            try:
                self.presenter.rangehandler.add_range(tuple(pair.split(";")))
            except (KeyError, IndexError):
                self.presenter.rangehandler.clear_ranges()
                print("Original skip_elements is invalid, clearing it.")

    def exclude_tags(self):
        """Choose which html tags should be removed from epub file."""
        self.presenter.present_html()
        self.do_xpaths_exist()
        while 1:
            text = prompt(
                "Choose html ranges that should be removed\n"
                'Existing ranges are: "{}"\n'
                "* [c]lear and make new range\n"
                "* [a]add range\n"
                "* [s]ave and quit\n"
                "* [q]uit without saving\n"
                "[c/a/s/q]: ".format(self.presenter.rangehandler.ranges)
            )
            if text == "c":
                self.presenter.rangehandler.clear_ranges()
                start = prompt(
                    "Cut and paste xpath expressions found in "
                    "the text above\nFirst xpath: "
                )
                end = prompt("Second xpath: ")

                try:
                    self.presenter.rangehandler.add_range((start, end))
                except (IndexError, KeyError):
                    print("Invalid range")
                    break
            elif text == "a":
                start = prompt(
                    "Cut and paste xpath expressions found in "
                    "the text above\nFirst xpath: "
                )
                end = prompt("Second xpath: ")

                try:
                    self.presenter.rangehandler.add_range((start, end))
                except (IndexError, KeyError):
                    print("Invalid range")
                    break
            elif text == "s":
                self.presenter.save()
                raise SystemExit("Saved your choices")
            elif text == "q":
                raise SystemExit("Did not save anything")
            else:
                print("Invalid choice, trying again.")


def parse_options():
    """Parse the commandline options.

    Returns:
        (argparse.Namespace): the parsed commandline arguments
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Choose which chapters and html ranges "
        "should be omitted from an epub file.",
    )

    parser.add_argument("epubfile", help="Path to an epub file")

    args = parser.parse_args()

    return args


def main():
    """Set which parts of an epub should be omitted."""
    args = parse_options()

    chooser = EpubChooser(args.epubfile)
    chooser.exclude_chapters()
    chooser.exclude_tags()
