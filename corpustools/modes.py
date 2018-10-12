# -*- coding: utf-8 -*-

#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this file. If not, see <http://www.gnu.org/licenses/>.
#
#   Copyright © 2013-2018 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Classes and functions to do handle apertium modes.xml files."""

from __future__ import absolute_import, print_function, unicode_literals

import os
import sys

from lxml import etree

from corpustools import util


class Pipeline(object):
    """Make a pipeline out of modes.xml file.

    Attributes:
        modename (str): a mode element from a modes.xml file.
        giella_prefix (str): Set this variable if the installed giella files
            are not found in the standard places.
    """

    def __init__(self, modename, lang, giella_prefix=None):
        """Initialise the Pipeline class.

        Args:
            modename (str): name of a mode that is expected to be found
                in the modes.xml file.
            giella_prefix (str): directory where the filenames given in the
                modes.xml file exist.
        """
        modefile = etree.parse(
            os.path.join(os.path.dirname(__file__), 'xml/modes.xml'))
        self.mode = modefile.find('.//mode[@name="{}"]'.format(modename))
        self.giella_prefix = self.valid_path(giella_prefix, lang)
        self.sanity_check()

    @staticmethod
    def valid_path(giella_prefix, lang):
        """Check if resources needed by modes exists.

        Args:
            giella_prefix (str): user provided directory where resources exist.
            lang (str): the language that modes is asked to serve.

        Returns:
            A directory where resources for the given language exist.

        Raises:
            utils.ArgumentError if no resources are found.
        """
        if giella_prefix is not None:
            return os.path.join(giella_prefix, 'share/giella', lang)
        else:
            for prefix in [
                    os.path.join(os.getenv('HOME'), '.local'), '/usr/local',
                    '/usr'
            ]:
                path = os.path.join(prefix, 'share/giella', lang)
                if os.path.isdir(path) and os.listdir(path):
                    return path

        raise (util.ArgumentError(
            'ERROR: found no resources for {}'.format(lang)))

    @staticmethod
    def raise_unless_exists(filenames):
        """Raise an ArgumentError if filename does not exist.

        Args:
            filenames (list of str): list of filenames harvested from the
                mode element.

        Raises:
            util.ArgumentError if a filename does not exist.
        """
        for filename in filenames:
            if not os.path.exists(filename):
                raise (util.ArgumentError(
                    'ERROR: {} does not exist'.format(filename)))

    def sanity_check(self):
        """Check that programs and files found in a program element exist."""
        util.sanity_check(
            [program.get('name') for program in self.mode.iter('program')])
        self.raise_unless_exists([
            os.path.join(self.giella_prefix, file_elem.get('name'))
            for file_elem in self.mode.iter('file')
        ])

    def run_external_command(self, command, instring):
        """Run the command with input using subprocess.

        Args:
            command (list of str): a subprocess compatible command.
            instring (bytes): the input to the command.

        Returns:
            bytes: the output of the command
        """
        runner = util.ExternalCommandRunner()
        runner.run(command, to_stdin=instring)
        self.check_error(command, runner.stderr)

        return runner.stdout

    @staticmethod
    def check_error(command, error):
        """Print errors."""
        if error:
            print(
                u'{} failed:\n{}'.format(u' '.join(command),
                                         error.decode('utf8')),
                file=sys.stderr)

    def tag2commandpart(self, element):
        """Turn program elements to a command part.

        Args:
            element (lxml.Element): a program subelement

        Returns:
            str: a program, a program option or a path to a file
        """
        if element.tag == 'file':
            return os.path.join(self.giella_prefix, element.get('name'))

        return element.get('name')

    def program2command(self, program):
        """Turn a program element to a subprocess compatible command.

        Args:
            program (str): a program element

        Returns:
            list of str: a subprocess compatible command
        """
        return [self.tag2commandpart(element) for element in program.iter()]

    @property
    def commands(self):
        """Make a list of subprocess compatible commands.

        Returns:
            list of list: a list of subprocess compatible commands.
        """
        return [
            self.program2command(program)
            for program in self.mode.iter('program')
        ]

    def run(self, instring):
        """Run the pipeline using input.

        Args:
            instring (bytes): utf-8 encoded input to the pipeline

        Returns:
            str: output of the pipeline
        """
        for command in self.commands:
            instring = self.run_external_command(command, instring)

        return instring.decode('utf8')
