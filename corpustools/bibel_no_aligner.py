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
#   Copyright © 2021 The University of Tromsø &
#                    the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Functions to align bible texts from bibel.no."""
import argparse
import glob
import os

from corpustools import argparse_version, corpuspath, util
from lxml import etree


def make_tuv(line, lang):
    """Make a tuv element given an input line and a lang variable."""
    tuv = etree.Element("tuv")
    tuv.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = lang
    seg = etree.Element("seg")
    seg.text = line.strip()
    tuv.append(seg)

    return tuv


def add_filename_id(filename):
    """Add the tmx filename as an prop element in the header."""
    prop = etree.Element("prop")
    prop.attrib["type"] = "x-filename"
    prop.text = os.path.basename(filename)

    return prop


def make_tmx_header(filename, source_lang):
    """Make a tmx header based on the lang variable."""
    header = etree.Element("header")

    # Set various attributes
    header.attrib["segtype"] = "sentence"
    header.attrib["o-tmf"] = "OmegaT TMX"
    header.attrib["adminlang"] = "en-US"
    header.attrib["srclang"] = source_lang
    header.attrib["datatype"] = "plaintext"

    header.append(add_filename_id(filename))

    return header


def make_tmx_template(filename, source_lang):
    """Make tmx file based on the output of the aligner."""
    tmx = etree.Element("tmx")
    header = make_tmx_header(filename, source_lang)
    tmx.append(header)

    return tmx


def common_verses(filename, parallel_path):
    """Return string pairs from common verses."""

    orig = etree.parse(filename)
    parallel = etree.parse(parallel_path)

    orig_dict = {verse.get("number"): verse.text for verse in orig.iter("verse")}
    parallel_dict = {
        verse.get("number"): verse.text for verse in parallel.iter("verse")
    }

    common_verse_numbers = set(orig_dict.keys()).intersection(set(parallel_dict.keys()))

    return [
        (orig_dict[common_verse], parallel_dict[common_verse])
        for common_verse in sorted(common_verse_numbers)
    ]


def parse_options():
    """Gather options."""
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser], description="Align bibel.no texts."
    )

    parser.add_argument("source_lang", help="Source language")
    parser.add_argument("target_lang", help="Target language")

    return parser.parse_args()


def valid_path(source_lang, target_lang):
    """Yield a CorpusPath if the parallel file exists."""
    for testament in ["nt", "ot"]:
        source_dir = os.path.join(
            os.getenv("GTBOUND"), "orig", source_lang, "bible", testament, "bibel.no"
        )
        for filename in glob.glob(f"{source_dir}/*.xml"):
            path = corpuspath.CorpusPath(filename)
            parallel_path = path.parallel(target_lang)

            if os.path.exists(parallel_path):
                yield path


def make_tmx(path, source_lang, target_lang):
    """Make a tmx element with verse pairs."""
    print("Making", path.prestable_tmx(target_lang))
    tmx = make_tmx_template(path.orig, source_lang)
    body = etree.SubElement(tmx, "body")
    for common_verse_pair in common_verses(path.orig, path.parallel(target_lang)):
        translation_unit = etree.SubElement(body, "tu")
        translation_unit.append(make_tuv(common_verse_pair[0], source_lang))
        translation_unit.append(make_tuv(common_verse_pair[1], target_lang))

    return tmx


def write_tmx(tmx, tmx_filename):
    """Write a tmx file."""
    with util.ignored(OSError):
        os.makedirs(os.path.dirname(tmx_filename))

    with open(tmx_filename, "wb") as tmx_stream:
        tmx_stream.write(
            etree.tostring(
                tmx, encoding="utf8", pretty_print=True, xml_declaration=True
            )
        )


def main():
    """Make tmx files."""
    args = parse_options()

    for path in valid_path(args.source_lang, args.target_lang):
        write_tmx(
            make_tmx(path, args.source_lang, args.target_lang),
            path.prestable_tmx(args.target_lang),
        )
