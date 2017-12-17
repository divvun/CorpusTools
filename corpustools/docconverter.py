# -*- coding: utf-8 -*-

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
#   Copyright © 2012-2017 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Convert doc files to the Giella xml format."""

from __future__ import absolute_import, print_function

import io
import os
import re

from lxml import html

from corpustools import util
from corpustools.htmlconverter import convert2xhtml, xhtml2intermediate


class DocError(Exception):
    """Use this when errors occur in this module."""

    pass


def doc_to_html_elt(filename):
    return html.parse(io.StringIO(doc_to_unicodehtml(filename)))


def doc_to_unicodehtml(filename):
    """Convert a doc file to xhtml.

    Arguments:
        filename (str): path to the file

    Returns:
        A string containing the xhtml version of the doc file.
    """
    text = extract_text(filename)
    try:
        return text.decode('utf8')
    except UnicodeDecodeError:
        # remove control characters
        remove_re = re.compile(u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F{}]')

        return remove_re.subn(
            '',
            text.decode('windows-1252'))[0]


def fix_wv_output():
    u"""Fix headers in the docx xhtml output.

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
    pass


def extract_text(filename, command):
    """Extract the text from a document.

    Arguments:
        filename (str): path to the document
        command (list of str): the command and the arguments sent to
            ExternalCommandRunner.

    Returns:
        bytes: the output of the program
    """
    runner = util.ExternalCommandRunner()
    runner.run(command, cwd='/tmp')

    if runner.returncode != 0:
        with open(filename + '.log', 'w') as logfile:
            print('stdout\n{}\n'.format(runner.stdout), file=logfile)
            print('stderr\n{}\n'.format(runner.stderr), file=logfile)
            raise util.ConversionError(
                '{} failed. More info in the log file: {}'.format(
                    command[0], filename + '.log'))

    return runner.stdout


def convert2intermediate(filename):
    """Convert a Microsoft Word document to the Giella xml format.

    Arguments:
        filename (str): path to the document

    Returns:
        etree.Element: the root element of the Giella xml document
    """
    return xhtml2intermediate(
        convert2xhtml(doc_to_html_elt(filename)))
