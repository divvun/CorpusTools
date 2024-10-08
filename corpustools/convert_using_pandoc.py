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
#   Copyright © 2012-2022 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Convert files supported by pandoc to the html format."""

import subprocess

from lxml import html


def to_html_elt(filename):
    """Convert the content of the give file to an lxml element.

    Args:
        filename (str): path to the document

    Returns:
        (lxml.etree.Element): An lxml element containing the html
            version of the given file.
    """
    html_body = subprocess.run(
        ["pandoc", filename], encoding="utf-8", capture_output=True, check=False
    ).stdout

    return html.document_fromstring(f"<html><body>{html_body}</body></html>")
