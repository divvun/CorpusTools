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
#   Copyright © 2011-2023 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Classes and functions to sentence align two files."""


from lxml import etree

from corpustools import corpuspath, util


class CorpusXMLFile:
    """A class to handle all the info of a corpus xml file."""

    def __init__(self, name):
        """Initialise the CorpusXMLFile class.

        Args:
            name (str): path to the xml file.
        """
        self.corpus_path = corpuspath.make_corpus_path(name)
        self.etree = etree.parse(name)
        self.root = self.etree.getroot()
        self.sanity_check()

    def sanity_check(self):
        """Check if the file really is a corpus xml file."""
        if self.root.tag != "document":
            raise util.ArgumentError(
                "Expected Corpus XML file (output of convert2xml) with "
                "<document> as the root tag, got {} -- did you pass the "
                "wrong file?".format(
                    self.root.tag,
                )
            )

    @property
    def lang(self):
        """Get the lang of the file."""
        return self.corpus_path.lang

    @property
    def word_count(self):
        """Return the word count of the file."""
        word_count = self.root.find(".//wordcount")
        if word_count is not None:
            return word_count.text
        else:
            raise AttributeError("wordcount not found!")

    @property
    def ocr(self):
        """Check if the ocr element exists.

        :returns: the ocr element or None
        """
        return self.root.find(".//ocr")

    @property
    def translated_from(self):
        """Get the translated_from element from the orig doc."""
        translated_from = self.root.find(".//translated_from")

        if translated_from is not None:
            return translated_from.attrib["{http://www.w3.org/XML/1998/namespace}lang"]

    def remove_version(self):
        """Remove the version element.

        This is often the only difference between the otherwise
        identical files in converted and prestable/converted
        """
        version_element = self.root.find(".//version")
        version_element.getparent().remove(version_element)

    def remove_skip(self):
        """Remove the skip element.

        This contains text that is not wanted in e.g. sentence alignment
        """
        skip_list = self.root.findall(".//skip")

        for skip_element in skip_list:
            skip_element.getparent().remove(skip_element)

    def move_later(self):
        """Move the later elements to the end of the body element."""
        body = self.root.xpath("/document/body")[0]

        later_list = self.root.xpath(".//later")

        for later_element in later_list:
            body.append(later_element)

    def set_body(self, new_body):
        """Replace the body element with new_body element."""
        if new_body.tag == "body":
            oldbody = self.etree.find(".//body")
            oldbody.getparent().replace(oldbody, new_body)

    def write(self, file_name=None):
        """Write self.etree."""
        if file_name is None:
            file_name = self.corpus_path

        self.etree.write(
            file_name, encoding="utf8", pretty_print=True, xml_declaration=True
        )
