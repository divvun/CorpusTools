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

import glob
import os
import shutil

import lxml.etree as etree

from corpustools import util
from corpustools.htmlconverter import (convert2xhtml, webpage_to_unicodehtml,
                                       xhtml2intermediate)


def latex_dir(filename):
    """Turn filename to the path where the converted html files are found."""
    return os.path.join(os.path.dirname(filename),
                        util.basename_noext(filename, '.tex'))


def latex_to_dir(filename):
    """Convert a doc file to xhtml.

    Arguments:
        filename (str): path to the file

    Returns:
        str: path to the temporary directory where the files are found
    """
    command = 'latex2html {}'.format(os.path.realpath(filename)).split()

    runner = util.ExternalCommandRunner()
    runner.run(command, cwd='/tmp')

    if runner.returncode != 0:
        with open(filename + '.log', 'w') as logfile:
            print('stdout\n{}\n'.format(runner.stdout), file=logfile)
            print('stderr\n{}\n'.format(runner.stderr), file=logfile)
            raise util.ConversionError(
                '{} failed. More info in the log file: {}'.format(
                    command[0], filename + '.log'))


def latexdir_to_html(filename):
    """Turn documents found in latex_dir to one html document."""
    mainbody = etree.Element('body')
    html = etree.Element('html')
    html.append(etree.Element('head'))
    html.append(mainbody)

    for nodediv in latexnode_to_div(filename):
        mainbody.append(nodediv)

    return html


def latexnode_to_div(filename):
    """Extract body elements from node*.html documents."""
    html_docs = glob.glob('{}/{}'.format(
        latex_dir(filename), 'node*.html'))

    for html_doc in html_docs[:-1]:
        latex_html = convert2xhtml(webpage_to_unicodehtml(html_doc))
        nodebody = latex_html.find('.//body')
        nodebody.tag = 'div'

        yield nodebody


def convert2intermediate(filename):
    """Extract content from the latex file.

    Arguments:
        filename (str): path to the document

    Returns:
        etree.Element: the content of the latex file as html
    """
    latex_to_dir(filename)
    html = latexdir_to_html(filename)

    shutil.rmtree(latex_dir(filename))

    return xhtml2intermediate(html)
