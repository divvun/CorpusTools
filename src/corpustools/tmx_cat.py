import argparse
from pathlib import Path

from lxml import etree

from corpustools import argparse_version
from corpustools.corpuspath import collect_files


def parse_options():
    """Parse the given options."""
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser], description="Analyse files in parallel."
    )

    parser.add_argument(
        "tmx_dir",
        help="directory containing the TMX files to concatenate",
    )

    return parser.parse_args()


def make_header(tmx_root: etree.Element) -> etree.Element:
    """Create TMX header element."""
    tmx_header = etree.SubElement(tmx_root, "header")
    tmx_header.set("creationtool", "tmx_cat")
    tmx_header.set("segtype", "sentence")
    tmx_header.set("o-tmf", "OmegaT TMX")
    tmx_header.set("adminlang", "en-us")
    tmx_header.set("datatype", "plaintext")
    return tmx_header


def set_metadata(tmx_header: etree.Element, tmx_xml: etree.ElementTree) -> None:
    first_tuv = tmx_xml.find(".//tuv[1]")
    if first_tuv is not None:
        try:
            first_lang = first_tuv.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
            tmx_header.set("srclang", first_lang)
        except KeyError as error:
            raise SystemExit(
                "Could not find language attribute in first <tuv> element."
            ) from error
    else:
        raise SystemExit("No <tuv> elements found in the first TMX file.")


def make_body(tmx_root: etree.Element, tmx_header: etree.Element, tmx_dir: str) -> None:
    body = etree.SubElement(tmx_root, "body")
    for file_no, tmx_file in enumerate(collect_files([tmx_dir], suffix=".tmx")):
        print(f"Processing TMX file: {tmx_file}", end="\r")
        tmx_xml = etree.parse(tmx_file)
        if file_no == 0:
            set_metadata(tmx_header, tmx_xml)
        for tu in tmx_xml.iter("tu"):
            body.append(tu)


def main():
    """Analyse files in the given directories."""
    args = parse_options()

    tmx_root = etree.Element("tmx")
    tmx_header = make_header(tmx_root)

    make_body(tmx_root, tmx_header, args.tmx_dir)

    concatenated_file = Path("concatenated.tmx")
    concatenated_file.write_bytes(
        etree.tostring(
            tmx_root, pretty_print=True, encoding="UTF-8"
        )
    )

    print(f"Concatenated TMX file written to: {concatenated_file}")
