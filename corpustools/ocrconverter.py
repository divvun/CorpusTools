# Description: Functions to convert PDF files to ALTO XML, plain text, and XML.
from pathlib import Path
from typing import Iterable

import pytesseract  # type: ignore
from lxml.etree import Element, SubElement, _Element
from PIL import Image

from corpustools.util import ConversionError, ExternalCommandRunner


def to_tiff(path: Path) -> None:
    """Convert a PDF to a series of tiff images.

    Args:
        path (Path): The path to the PDF file.

    Raises:
        ConversionError: If the conversion fails.
    """
    command = f"pdfimages -tiff {path} {path.stem}"

    runner = ExternalCommandRunner()
    runner.run(command, cwd="/tmp")

    if runner.returncode != 0:
        with open(str(path) + ".log", "w") as logfile:
            print(f"stdout\n{runner.stdout}\n", file=logfile)
            print(f"stderr\n{runner.stderr}\n", file=logfile)
            raise ConversionError(
                "{} failed. More info in the log file: {}".format(
                    command[0], str(path) + ".log"
                )
            )


def to_alto_xml(path: Path) -> Iterable[str]:
    return (
        pytesseract.image_to_alto_xml(Image.open(image_file))
        for image_file in Path("/tmp").glob(f"{path.stem}-*.tiff")
    )


def to_plaintext(path: Path, language: str) -> Iterable[str]:
    """Convert a PDF containing ocr'd text to an iterable containing text paragraphs.

    Pick up the tiff images created by to_tiff and use pytesseract to extract text from
    them.

    Args:
        path (Path): The path to the PDF file.
        language (str): The language of the text in the PDF file.
    """
    to_tiff(path)
    return (
        paragraph
        for image_file in Path("/tmp").glob(f"{path.stem}-*.tiff")
        for paragraph in pytesseract.image_to_string(
            Image.open(image_file), lang=language
        ).split("\n\n")
    )


def to_xml(path: Path, language: str) -> _Element:
    """Convert a PDF containing ocr'd text to a Giella xml document.

    Args:
        path (Path): The path to the PDF file.
        language (str): The language of the text in the PDF file.
    Returns:
        (_Element): The xml document.
    """
    document = Element("document")
    SubElement(document, "header")
    body = SubElement(document, "body")
    for text in to_plaintext(path, language):
        SubElement(body, "p").text = text

    return document
