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
"""Classes and functions to make and handle Translation Memory eXchange files."""


import argparse
import codecs
import os
import re

from lxml import etree

from corpustools import argparse_version, util

HERE = os.path.dirname(__file__)


class Tmx:
    """A tmx file handler.

    A class that reads a tmx file, and implements a bare minimum of
    functionality to be able to compare two tmx's.
    It also contains functions to manipulate the tmx in several ways.
    """

    def __init__(self, tmx):
        """Input is a tmx element."""
        self.tmx = tmx

    @property
    def src_lang(self):
        """Get the srclang from the header element."""
        return self.tmx.find(".//header").attrib["srclang"][:3]

    @staticmethod
    def tu_to_string(transl_unit):
        """Extract the two strings of a tu element."""
        string = ""
        with util.ignored(AttributeError):
            string = string + transl_unit[0][0].text.strip()

        string += "\t"

        with util.ignored(AttributeError):
            string = string + transl_unit[1][0].text.strip()

        string += "\n"
        return string

    @staticmethod
    def tuv_to_string(tuv):
        """Extract the string from the tuv element."""
        string = ""
        with util.ignored(AttributeError):
            string = tuv[0].text.strip()

        return string

    def lang_to_stringlist(self, lang):
        """Find all sentences of lang."""
        all_tuv = self.tmx.xpath(
            './/tuv[@xml:lang="' + lang + '"]',
            namespaces={"xml": "http://www.w3.org/XML/1998/namespace"},
        )

        strings = []
        for tuv in all_tuv:
            strings.append(self.tuv_to_string(tuv))

        return strings

    def tmx_to_stringlist(self):
        """Extract all string pairs in a tmx to a list of strings."""
        all_tu = self.tmx.findall(".//tu")
        strings = []
        for transl_unit in all_tu:
            strings.append(self.tu_to_string(transl_unit))

        return strings

    @staticmethod
    def prettify_segs(transl_unit):
        """Strip white space from start and end of the strings.

        Input is a tu element
        Output is a tu element with white space stripped strings
        """
        with util.ignored(AttributeError):
            string = transl_unit[0][0].text.strip()
            transl_unit[0][0].text = string

        with util.ignored(AttributeError):
            string = transl_unit[1][0].text.strip()
            transl_unit[1][0].text = string

        return transl_unit

    # to debug here
    def reverse_langs(self):
        """Reverse the langs in a tmx.

        Return the reverted tmx
        """
        all_tu = self.tmx.findall(".//tu")
        body = etree.Element("body")
        for transl_unit in all_tu:
            tmp = etree.Element("tu")
            tmp.append(transl_unit[1])
            tmp.append(transl_unit[0])
            tmp = self.prettify_segs(tmp)
            body.append(tmp)

        tmx = etree.Element("tmx")
        tmx.append(body)

        self.tmx = tmx

    def remove_unwanted_space(self):
        """Remove unwanted spaces from sentences.

        The SentenceDivider adds spaces before and after punctuation,
        quotemarks, parentheses and so on.
        Remove those spaces so that the tmxes are more appropriate for real
        world™ use cases.
        """
        root = self.tmx
        for transl_unit in root.iter("tu"):
            transl_unit = self.remove_unwanted_space_from_segs(transl_unit)

    def remove_unwanted_space_from_segs(self, transl_unit):
        """Remove unwanted spaces.

        Remove spaces before and after punctuation,
        quotemarks, parentheses and so on as appropriate in the seg elements
        in the tu elements.
        Input is a tu element
        Output is a tu element with modified seg elements
        """
        with util.ignored(AttributeError):
            string = transl_unit[0][0].text.strip()
            string = self.remove_unwanted_space_from_string(string)
            transl_unit[0][0].text = string

        with util.ignored(AttributeError):
            string = transl_unit[1][0].text.strip()
            string = self.remove_unwanted_space_from_string(string)
            transl_unit[1][0].text = string

        return transl_unit

    @staticmethod
    def remove_unwanted_space_from_string(input_string):
        """Remove unwanted space from string.

        Args:
            input_string (str): the string we would like to remove
                unwanted space from:

        Returns:
            str without unwanted space.
        """
        result = input_string

        # regex to find space followed by punctuation
        space_punctuation = re.compile(r"(?P<space>\s)(?P<punctuation>[\)\]\.»:;,])")
        # for every match in the result string, replace the match
        # (space+punctuation) with the punctuation part
        result = space_punctuation.sub(lambda match: match.group("punctuation"), result)

        # regex to find punctuation followed by space
        punctuation_space = re.compile(r"(?P<punctuation>[\[\(«])(?P<space>\s)+")
        result = punctuation_space.sub(lambda match: match.group("punctuation"), result)

        # regex which matches multiple spaces
        multiple_space = re.compile(r"\s+")
        result = multiple_space.sub(lambda match: " ", result)

        return result

    def write_tmx_file(self, out_filename):
        """Write a tmx file given a tmx etree element and a filename."""
        out_dir = os.path.dirname(out_filename)
        with util.ignored(OSError):
            os.makedirs(out_dir)

        with open(out_filename, "wb") as tmx_file:
            tmx_file.write(
                etree.tostring(
                    self.tmx, pretty_print=True, encoding="utf-8", xml_declaration=True
                )
            )

    def tmx2html(self, out_filename):
        """Convert tmx to html.

        Args:
            out_filename (str): name of the html file
        """
        html2tmx_transformer = etree.XSLT(
            etree.parse(os.path.join(HERE, "xslt/tmx2html.xsl"))
        )

        with open(out_filename, "wb") as html_file:
            html_file.write(
                etree.tostring(
                    html2tmx_transformer(self.tmx),
                    pretty_print=True,
                    encoding="utf-8",
                    xml_declaration=True,
                )
            )

    def remove_tu_with_empty_seg(self):
        """Remove tu elements that contain empty seg element."""
        root = self.tmx
        for transl_unit in root.iter("tu"):
            try:
                self.check_if_emtpy_seg(transl_unit)
            except AttributeError:
                transl_unit.getparent().remove(transl_unit)

    @staticmethod
    def check_if_emtpy_seg(transl_units):
        """Check if a tu element contains empty strings.

        If there are any empty elements an AttributeError is raised
        """
        for transl_unit in transl_units:
            if not transl_unit[0].text.strip():
                raise AttributeError("Empty translation unit")

    def clean_toktmx(self):
        """Do the cleanup of the toktmx file."""
        self.remove_unwanted_space()
        self.remove_tu_with_empty_seg()


class AlignmentToTmx(Tmx):
    """A class to make tmx files based on the output of an aligner.

    This just implements some common methods for the TCA2 and hunalign
    subclasses.
    """

    def __init__(self, origfiles):
        """Input is a list of CorpusXMLFile objects."""
        self.origfiles = origfiles
        super().__init__(self.make_tmx())

    def make_tu(self, line1, line2):
        """Make a tmx tu element based on line1 and line2 as input."""
        transl_unit = etree.Element("tu")

        transl_unit.append(self.make_tuv(line1, self.origfiles[0].pathcomponents.lang))
        transl_unit.append(self.make_tuv(line2, self.origfiles[1].pathcomponents.lang))

        return transl_unit

    @staticmethod
    def make_tuv(line, lang):
        """Make a tuv element given an input line and a lang variable."""
        tuv = etree.Element("tuv")
        tuv.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = lang
        seg = etree.Element("seg")
        seg.text = line.strip()
        tuv.append(seg)

        return tuv

    @staticmethod
    def add_filename_id(filename):
        """Add the tmx filename as an prop element in the header."""
        prop = etree.Element("prop")
        prop.attrib["type"] = "x-filename"
        prop.text = os.path.basename(filename)

        return prop

    def make_tmx_header(self, filename, lang):
        """Make a tmx header based on the lang variable."""
        header = etree.Element("header")

        # Set various attributes
        header.attrib["segtype"] = "sentence"
        header.attrib["o-tmf"] = "OmegaT TMX"
        header.attrib["adminlang"] = "en-US"
        header.attrib["srclang"] = lang
        header.attrib["datatype"] = "plaintext"

        header.append(self.add_filename_id(filename))

        return header

    def make_tmx(self):
        """Make tmx file based on the output of the aligner."""
        tmx = etree.Element("tmx")
        header = self.make_tmx_header(
            self.origfiles[0].pathcomponents.basename,
            self.origfiles[0].pathcomponents.lang,
        )
        tmx.append(header)

        pfile1_data, pfile2_data = self.parse_alignment_results()

        body = etree.SubElement(tmx, "body")
        for line1, line2 in zip(pfile1_data, pfile2_data):
            transl_unit = self.make_tu(line1, line2)
            body.append(transl_unit)

        return tmx

    def parse_alignment_results(self):
        """Meta function."""
        raise NotImplementedError(
            "You have to subclass and override parse_alignment_results"
        )


class HunalignToTmx(AlignmentToTmx):
    """A class to make tmx files based on the output from hunalign."""

    def __init__(self, origfiles, output, threshold=0.0):
        """Input is a list of CorpusXMLFile objects."""
        self.output = output
        self.threshold = threshold
        super().__init__(origfiles)

    def parse_alignment_results(self):
        """Return parsed output files of tca2."""
        pairs = [line.split("\t") for line in self.output.split("\n") if line]
        pairs = [pair for pair in pairs if self.is_good_line(pair)]

        src_lines = [self.clean_line(l[0]) for l in pairs]
        trg_lines = [self.clean_line(l[1]) for l in pairs]
        return src_lines, trg_lines

    def is_good_line(self, line):
        """Determine whether this line should be used."""
        return (
            len(line) == 3
            and line[0] != "<p>"
            and line[1] != "<p>"
            and float(line[2]) > self.threshold
        )

    @staticmethod
    def clean_line(line):
        """Remove the ~~~ occuring in multi-sentence alignments."""
        multi_sep = re.compile(r" *~~~ *")
        return multi_sep.sub(" ", line)


class Tca2ToTmx(AlignmentToTmx):
    """A class to make tmx files based on the output from tca2."""

    def __init__(self, origfiles, sentfiles):
        """Input is a list of CorpusXMLFile objects."""
        self.sentfiles = sentfiles
        super().__init__(origfiles)

    def parse_alignment_results(self):
        """Return parsed output files of tca2."""
        return (
            self.read_tca2_output(self.sentfiles[0]),
            self.read_tca2_output(self.sentfiles[1]),
        )

    def read_tca2_output(self, sentfile):
        """Read the output of tca2.

        Args:
            sentfile (str): name of the output file of convert2xml

        Returns:
            list of str: The sentences found in the tca2 file
        """
        sentfile_name = sentfile.replace(".sent", "_new.txt")

        with codecs.open(sentfile_name, encoding="utf8") as tca2_output:
            return [self.remove_s_tag(line) for line in tca2_output]

    @staticmethod
    def remove_s_tag(line):
        """Remove the s tags that tca2 has added."""
        sregex = re.compile('<s id="[^ ]*">')
        line = line.replace("</s>", "")
        line = sregex.sub("", line)
        return line


def tmx2html(filename):
    """Turn a tmx file into an html file.

    Args:
        filename (str): name of a tmx file
    """
    translation_mem_ex = Tmx(etree.parse(filename))
    html_name = filename + ".html"
    translation_mem_ex.tmx2html(html_name)
    print(f"Wrote {html_name}")


def parse_options():
    """Parse the commandline options.

    Returns:
        a list of arguments as parsed by argparse.Argumentparser.
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser], description="Convert tmx files to html"
    )

    parser.add_argument(
        "sources", nargs="+", help="Files or directories to search for tmx files"
    )

    args = parser.parse_args()
    return args


def find_files(directory, ending):
    for root, _, files in os.walk(directory):
        for file_ in files:
            if file_.endswith(ending):
                yield os.path.join(root, file_)


def main():
    """Parallelise files."""
    args = parse_options()

    for source in args.sources:
        if os.path.isfile(source):
            if source.endswith(".tmx"):
                tmx2html(source)
            else:
                SystemExit(f"Not a tmx file:\n{source}")
        elif os.path.isdir(source):
            found = False
            for tmx_file in find_files(source, ".tmx"):
                found = True
                tmx2html(tmx_file)

            if not found:
                raise SystemExit(f"No tmx files found in:\n{source}")
