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
#   Copyright © 2013-2023 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Classes and functions to handle apertium modes.xml files."""

import os
import sys

from lxml import etree

from corpustools import util


def list_modes():
    modefile = etree.parse(os.path.join(os.path.dirname(__file__), "xml/modes.xml"))
    return [
        mode.get("name")
        for mode in modefile.iter("mode")
        if any(program.get("name") == "vislcg3" for program in mode.xpath(".//program"))
    ]


class Pipeline:
    """Make a pipeline out of modes.xml file.

    Attributes:
        modename: a mode element from a modes.xml file.
        lang: the language that the mode is for.
        giella_prefix: Set this variable if the installed giella files
            are not found in the standard places.
    """

    def __init__(self, modename: str, lang: str, giella_prefix: str | None = None):
        """Initialise the Pipeline class.

        Args:
            modename: name of a mode that is expected to be found
                in the modes.xml file.
            lang: the language that the mode is for.
            giella_prefix: directory where the filenames given in the
                modes.xml file exist.
        """
        modefile = etree.parse(os.path.join(os.path.dirname(__file__), "xml/modes.xml"))
        mode = modefile.find(f'.//mode[@name="{modename}"]')
        if mode is None:
            raise util.ArgumentError(f"ERROR: mode {modename} not found in modes.xml")
        self.mode: etree.Element = mode

        self.giella_prefix = self.valid_path(giella_prefix, lang)
        self.sanity_check()

    @staticmethod
    def valid_path(giella_prefix: str | None, lang: str) -> str:
        """Check if resources needed by modes exists.

        Args:
            giella_prefix (str): user provided directory where resources exist.
            lang (str): the language that modes is asked to serve.

        Returns:
            (str): A directory where resources for the given language exist.

        Raises:
            utils.ArgumentError: if no resources are found.
        """
        prefixes = [
            "/usr/local",
            "/usr",
        ]
        home = os.getenv("HOME")
        if home is not None:
            prefixes.insert(0, os.path.join(home, ".local"))

        if giella_prefix is not None:
            return os.path.join(giella_prefix, "share/giella", lang)
        else:
            for prefix in prefixes:
                path = os.path.join(prefix, "share/giella", lang)
                if os.path.isdir(path) and os.listdir(path):
                    return path

        raise (util.ArgumentError(f"ERROR: found no resources for {lang}"))

    @staticmethod
    def raise_unless_exists(filenames: list[str]) -> None:
        """Raise an ArgumentError if filename does not exist.

        Args:
            filenames: list of filenames harvested from the
                mode element.

        Raises:
            util.ArgumentError: if a filename does not exist.
        """
        for filename in filenames:
            if not os.path.exists(filename):
                raise (util.ArgumentError(f"ERROR: {filename} does not exist"))

    def sanity_check(self):
        """Check that programs and files found in a program element exist."""
        util.sanity_check(
            [
                name
                for program in self.mode.iter("program")
                if (name := program.get("name")) is not None
            ]
        )
        self.raise_unless_exists(
            [
                os.path.join(self.giella_prefix, file_name)
                for file_elem in self.mode.iter("file")
                if (file_name := file_elem.get("name")) is not None
            ]
        )

    @staticmethod
    def check_error(command: list[str], error: bytes | None) -> None:
        """Print errors."""
        if error:
            print(
                "{} failed:\n{}".format(" ".join(command), error.decode("utf8")),
                file=sys.stderr,
            )

    def tag2commandpart(self, element: etree.Element) -> str:
        """Turn program elements to a command part.

        Args:
            element (lxml.Element): a program subelement

        Returns:
            (str): a program, a program option or a path to a file
        """
        if element.tag == "file" and (name := element.get("name")) is not None:
            return os.path.join(self.giella_prefix, name)

        return name if (name := element.get("name")) is not None else ""

    def program2command(self, program: etree.Element) -> list[str]:
        """Turn a program element to a subprocess compatible command.

        Args:
            program: a program element

        Returns:
            a subprocess compatible command
        """
        return [self.tag2commandpart(element) for element in program.iter()]

    @property
    def commands(self) -> list[list[str]]:
        """Make a list of subprocess compatible commands.

        Returns:
            (list[list]): a list of subprocess compatible commands.
        """
        return [self.program2command(program) for program in self.mode.iter("program")]

    def run(self, instring: str) -> str:
        """Run the pipeline using input.

        Args:
            instring: utf-8 encoded input to the pipeline

        Returns:
            output of the pipeline
        """
        for command in self.commands:
            instring = util.run_external_command(command, instring)

        return instring
