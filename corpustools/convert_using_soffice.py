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
"""Convert writenow files to the html format."""

import sys
import os
import subprocess

from lxml import html


def to_html_elt(filename):
    """Convert the content of an writenow file to xhtml.

    Args:
        filename (str): path to the document

    Returns:
        (str): A string containing the html version of the writenow file.
    """
    outdir = os.path.dirname(filename)
    subprocess.run(
        [
            "/Applications/LibreOffice.app/Contents/MacOS/soffice"
            if sys.platform == "darwin"
            else "soffice",
            "--convert-to",
            "html",
            "--outdir",
            outdir,
            filename,
        ],
        encoding="utf-8",
    )

    outname = f"{os.path.splitext(filename)[0]}.html"
    parsed_html = html.parse(outname)
    os.remove(outname)

    return parsed_html
