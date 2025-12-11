from pathlib import Path

from lxml import etree

from corpustools.error_annotated_sentence import parse_markup_to_sentence


def convert2intermediate(filename: Path) -> etree.Element:
    """Convert files containing error-annotated sentences to the GiellaLT xml format."""
    document = etree.Element("document")
    etree.SubElement(document, "header")
    body = etree.SubElement(document, "body")

    for line in filename.read_text(encoding="utf-8").splitlines():
        error_annotated = parse_markup_to_sentence(line)
        body.append(error_annotated.to_errormarkupxml())

    return document