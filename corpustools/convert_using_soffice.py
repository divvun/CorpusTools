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
#   Copyright © 2023 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Convert doc that LibreOffice knows to html."""

import subprocess
import sys
from pathlib import Path

from lxml import html
from lxml.etree import ElementTree


def to_html_elt(filename: str) -> ElementTree:
    """Convert the content of a writenow file to an ElementTree.

    Args:
        filename (str): path to the document

    Returns:
        (ElementTree): An element containing the HTML version of the given file.
    """
    filepath = Path(filename)
    outdir = filepath.parent
    subprocess.run(
        [
            "/Applications/LibreOffice.app/Contents/MacOS/soffice"
            if sys.platform == "darwin"
            else "soffice",
            "--convert-to",
            "html",
            "--outdir",
            outdir,
            str(filepath),
        ],
        encoding="utf-8",
        check=False,
    )

    outname = f"{filepath.stem}.html"
    parsed_html = html.parse(outdir / outname)
    (outdir / outname).unlink()

    return parsed_html
