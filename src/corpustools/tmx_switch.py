import argparse
from pathlib import Path

from lxml import etree

from corpustools import argparse_version


def parse_options():
    """Parse the given options."""
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser], description="Analyse files in parallel."
    )

    parser.add_argument(
        "tmx_file",
        help="file where language switches should be made",
    )

    return parser.parse_args()


def set_metadata(tmx_header: etree.Element, tmx_xml: etree.Element) -> None:
    second_tuv = tmx_xml.find(".//tuv[2]")
    if second_tuv is not None:
        try:
            second_lang = second_tuv.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
            tmx_header.set("srclang", second_lang)
        except KeyError as error:
            raise SystemExit(
                "Could not find language attribute in first <tuv> element."
            ) from error
    else:
        raise SystemExit("No <tuv> elements found in the first TMX file.")


def make_body(new_tmx_root: etree.Element, old_tmx_root: etree.Element) -> None:
    body = etree.SubElement(new_tmx_root, "body")

    tus = old_tmx_root.findall(".//tu")
    print(f"Switching {len(tus)} TUs")
    for index, old_tu in enumerate(tus, start=1):
        print(f"Switching TU number: {index}", end="\r")
        tu = etree.SubElement(body, "tu")
        for tuv in reversed(old_tu.findall("tuv")):
            # Clear whitespace before/after element to let pretty_print handle it
            tu.append(tuv)
            
def main():
    """Switch languages of the given TMX file."""
    args = parse_options()

    old_xml = etree.parse(args.tmx_file)
    old_tmx_root = old_xml.getroot()
    header = old_tmx_root.find("header")
    if header is None:
        raise SystemExit("No <header> element found in the TMX file.")
    set_metadata(header, old_tmx_root)

    new_tmx_root = etree.Element("tmx")
    new_tmx_root.append(header)
    
    make_body(new_tmx_root, old_tmx_root)

    switched_file = Path("switched.tmx")
    switched_file.write_bytes(
        etree.tostring(
            new_tmx_root, pretty_print=True, encoding="UTF-8"
        )
    )