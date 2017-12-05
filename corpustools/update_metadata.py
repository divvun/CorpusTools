# -*- coding: utf-8 -*-

#
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
#   Copyright © 2017 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#

"""Update metadata files in given directories."""


from __future__ import absolute_import, print_function

import argparse
import os

from corpustools import argparse_version, xslsetter

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__),
                             'xslt/XSL-template.xsl')


def find_xsl_files(directories):
    """Find .xsl files found in directories.

    Arguments:
        directories (list of str): paths to directories

    Yields:
        str: path to an .xsl file
    """
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file_ in files:
                if file_.endswith('.xsl'):
                    yield os.path.join(root, file_)


def parse_options():
    """Parse the commandline options.

    Returns:
        a list of arguments as parsed by argparse.Argumentparser.
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description='Update metadata files to look like XSL-template.xsl, '
        'but with original content. This script exists because the '
        'XSL-template is updated with new variables and documentation. '
        'This script will propagate these changes to existing '
        'metadata files.')

    parser.add_argument(
        'directories', nargs='+',
        help='Directories where metadata files should be updated.')

    args = parser.parse_args()

    return args


def update_xsl_file(filename):
    """Update the xsl file with XSL-template.xsl.

    Arguments:
        filename (str): path to a metadata file.
    """
    avoid_names = ['danlang', 'englang', 'finlang', 'fkvlang', 'gerlang',
                   'isllang', 'kallang', 'nnolang', 'noblang', 'smalang',
                   'smelang', 'smjlang', 'swelang', 'kpvlang', 'ruslang',
                   'multilingual', 'columns', 'parallel_texts', 'lower']

    orig_metadata = xslsetter.MetadataHandler(filename)
    template_metadata = xslsetter.MetadataHandler(TEMPLATE_PATH)

    for language in orig_metadata.mlangs:
        template_metadata.set_mlang(language)

    for name, value in orig_metadata.get_set_variables():
        if name not in avoid_names:
            if name.startswith('mlang_'):
                template_metadata.set_mlang(name.replace('mlang_', ''))
            elif name.startswith('para_'):
                template_metadata.set_parallel_text(name.replace('para_', ''),
                                                    value)
            elif name == 'excluded':
                template_metadata.set_variable('skip_pages', value)
            else:
                template_metadata.set_variable(name, value)

    for language, location in orig_metadata.get_parallel_texts().items():
        template_metadata.set_parallel_text(language, location)

    template_element = template_metadata.tree.getroot()
    for template in orig_metadata.xsl_templates:
        template_element.append(template)

    orig_metadata.tree = template_metadata.tree
    orig_metadata.write_file()


def main():
    """Update metadata files."""
    args = parse_options()
    for xsl_file in find_xsl_files(args.directories):
        try:
            update_xsl_file(xsl_file)
        except (AttributeError, UserWarning) as error:
            print(str(error))
            print(xsl_file)
            raise SystemExit(4)
