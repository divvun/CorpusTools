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
#   Copyright © 2012-2021 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Convert doc files to the Giella xml format."""


import glob
import os
import shutil

import lxml.etree as etree

from corpustools import htmlconverter, util


def latex_dir(filename):
    """Turn filename to the path where the converted html files are found."""
    return os.path.join(
        os.path.dirname(filename), util.basename_noext(filename, ".tex")
    )


def latex_to_dir(filename):
    """Convert a doc file to xhtml.

    Args:
        filename (str): path to the file

    Returns:
        str: path to the temporary directory where the files are found
    """
    command = f"latex2html {os.path.realpath(filename)}".split()

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


def to_html_elt(filename):
    """Turn documents found in latex_dir to one html document."""
    latex_to_dir(filename)

    mainbody = etree.Element("body")
    html = etree.Element("html")
    html.append(etree.Element("head"))
    html.append(mainbody)

    for nodediv in latexnode_to_div(filename):
        mainbody.append(nodediv)

    shutil.rmtree(latex_dir(filename))

    return html


def latexnode_to_div(filename):
    """Extract body elements from node*.html documents."""
    html_docs = glob.glob("{}/{}".format(latex_dir(filename), "node*.html"))

    for html_doc in html_docs[:-1]:
        latex_html = htmlconverter.to_html_elt(html_doc)
        nodebody = latex_html.find(".//body")
        nodebody.tag = "div"

        yield nodebody
