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
#   Copyright © 2012-2023 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Convert doc files to the Giella xml format."""


import re

from lxml import html

from corpustools import util


class DocError(Exception):
    """Use this when errors occur in this module."""


def to_html_elt(filename):
    return html.document_fromstring(doc_to_unicodehtml(filename))


def doc_to_unicodehtml(filename):
    """Convert a doc file to xhtml.

    Args:
        filename (str): path to the file

    Returns:
        A string containing the xhtml version of the doc file.
    """
    text = extract_text(filename)
    try:
        return text.decode("utf8")
    except UnicodeDecodeError:
        # remove control characters
        remove_re = re.compile("[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F{}]")

        return remove_re.subn("", text.decode("windows-1252"))[0]


def fix_wv_output():
    """Fix headers in the docx xhtml output.

    Examples of headings:

    h1:
    <html:ul>
        <html:li value="2">
            <html:p/>
            <html:div align="left" name="Overskrift 1">
                <html:p>
                    <html:b>
                        <html:span>
                            OVTTASKASOLBMOT
                        </html:span>
                    </html:b>
                </html:p>
            </html:div>
        </html:li>
    </html:ul>

    h2:
    <html:ol type="1">
        <html:li value="1">
            <html:p/>
            <html:div align="left" name="Overskrift 2">
                <html:p>
                    <html:b>
                        <html:span>
                            čoahkkáigeassu
                        </html:span>
                    </html:b>
                </html:p>
            </html:div>
        </html:li>
    </html:ol>

    <html:ol type="1">
        <html:ol type="1">
            <html:li value="2">
                <html:p/>
                <html:div align="left" name="Overskrift 2">
                    <html:p>
                        <html:b>
                            <html:span>
                                Ulbmil ja váldooasit
                            </html:span>
                        </html:b>
                    </html:p>
                </html:div>
            </html:li>
        </html:ol>
    </html:ol>

    h3:
    <html:ol type="1">
        <html:ol type="1">
            <html:ol type="1">
                <html:li value="1">
                    <html:p>
                    </html:p>
                    <html:div align="left" name="Overskrift 3">
                        <html:p>
                            <html:b>
                                <html:span>
                                    Geaográfalaš
                                </html:span>
                            </html:b>
                            <html:b>
                                <html:span>
                                    ráddjen
                                </html:span>
                            </html:b>

                        </html:p>
                    </html:div>
                </html:li>

            </html:ol>
        </html:ol>
    </html:ol>

    <html:ol type="1">
        <html:ol type="1">
            <html:ol type="1">
                <html:li value="1">
                    <html:p>
                    </html:p>
                    <html:div align="left" name="Overskrift 3">
                        <html:p>
                            <html:b>
                            <html:span>Iskanjoavku ja sámegielaga
                            definišuvdn</html:span></html:b>
                            <html:b><html:span>a</html:span></html:b>
                        </html:p>
                    </html:div>
                </html:li>

            </html:ol>
        </html:ol>
    </html:ol>

    h4:
    <html:div align="left" name="Overskrift 4">
        <html:p>
            <html:b>
                <html:i>
                    <html:span>
                        Mildosat:
                    </html:span>
                </html:i>
            </html:b>
        </html:p>
    </html:div>

    """


def extract_text(filename):
    """Extract the text from a document.

    Args:
        filename (str): path to the document
        command (list of str): the command and the arguments sent to
            ExternalCommandRunner.

    Returns:
        bytes: the output of the program
    """
    command = ["wvHtml", filename, "-"]
    runner = util.ExternalCommandRunner()
    runner.run(command, cwd="/tmp")

    if runner.returncode != 0:
        with open(filename + ".log", "w") as logfile:
            print(f"stdout\n{runner.stdout}\n", file=logfile)
            print(f"stderr\n{runner.stderr}\n", file=logfile)
            raise util.ConversionError(
                "{} failed. More info in the log file: {}".format(
                    command[0], filename + ".log"
                )
            )

    return runner.stdout
