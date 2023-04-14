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
"""This file contains classes to handle corpus filenames."""


from collections import namedtuple
import os
import re

from corpustools import util, xslsetter

CORPUS_DIR_RE = re.compile(
    r"(?P<parent>.*/)(?P<corpusdir>corpus-[^/]+)(?P<corpusfile>.*)"
)


PathComponents = namedtuple(
    "PathComponents", "root dirsuffix module lang genre subdirs basename goallang"
)


class CorpusPath:
    """Map filenames in a corpus.

    Args:
        path: path to a corpus file
    """

    def __init__(self, path):
        """Initialise the CorpusPath class."""
        self.pathcomponents = self.split_path(path)
        self.metadata = xslsetter.MetadataHandler(self.xsl, create=True)

    @staticmethod
    def split_on_module(path):
        """Split the path in three parts.

        Args:
            path: a path to a corpus file

        Returns:
            tuple of str: part one is the corpus directory, the second
                part is the module, the third part is the path of the
                corpus file inside the corpus

        Raises:
            ValueError: the path is not part of a corpus.
        """
        abspath = os.path.normpath(os.path.abspath(path))
        corpus_match = CORPUS_DIR_RE.search(abspath)

        if corpus_match:
            corpus_dict = corpus_match.groupdict()
            corpus_dir_parts = corpus_dict["corpusdir"].split("-")

            if len(corpus_dir_parts) > 2 and corpus_dir_parts[2] == "orig":
                return (
                    corpus_dict["parent"],
                    corpus_dir_parts[1],
                    "-" + "-".join(corpus_dir_parts[3:])
                    if len(corpus_dir_parts) > 3
                    else "",
                    "",
                    corpus_dict["corpusfile"],
                    "",
                )
            else:
                for module in [
                    "goldstandard",
                    "prestable/converted",
                    "prestable/toktmx",
                    "prestable/tmx",
                    "converted",
                    "analysed",
                    "stable/tmx",
                    "stable/converted",
                    "toktmx",
                    "tmx",
                    "korp",
                ]:
                    module_dir = "/" + module + "/"
                    if corpus_dict["corpusfile"].startswith(module_dir):
                        corpus_file_parts = corpus_dict["corpusfile"][
                            len(module_dir) :
                        ].split("/")

                        return (
                            corpus_dict["parent"],
                            corpus_dir_parts[1],
                            "-" + "-".join(corpus_dir_parts[3:])
                            if len(corpus_dir_parts) > 2
                            else "",
                            module,
                            "/".join(corpus_file_parts[1:])
                            if module.endswith("tmx")
                            else "/".join(corpus_file_parts),
                            corpus_file_parts[0] if module.endswith("tmx") else "",
                        )

        raise ValueError(f"File is not part of a corpus: {path}")

    def split_path(self, path):
        """Map path to the original file.

        Args:
            path: a path to a corpus file

        Returns:
            A PathComponents namedtuple containing the components of the
            original file
        """
        # Ensure we have at least one / before module, for safer splitting:
        root, lang, dirsuffix, module, corpusfile, goallang = self.split_on_module(path)

        corpusfile_parts = corpusfile.split("/")
        (genre, subdirs, basename) = (
            corpusfile_parts[0],
            corpusfile_parts[1:-1],
            corpusfile_parts[-1],
        )

        if not module:
            if basename.endswith(".xsl"):
                basename = util.basename_noext(basename, ".xsl")
            elif basename.endswith(".log"):
                basename = util.basename_noext(basename, ".log")
        elif "converted" in module or "analysed" in module:
            basename = util.basename_noext(basename, ".xml")
        elif "toktmx" in module:
            basename = util.basename_noext(basename, ".toktmx")
        elif "tmx" in module:
            basename = util.basename_noext(basename, ".tmx")

        return PathComponents(
            root, dirsuffix, "", lang, genre, "/".join(subdirs), basename, goallang
        )

    @property
    def orig(self):
        """Return the path of the original file."""
        return self.name()

    @property
    def xsl(self):
        """Return the path of the metadata file."""
        return self.orig + ".xsl"

    @property
    def log(self):
        """Return the path of the log file."""
        return self.orig + ".log"

    def name(self, module="", lang=None, name=None, extension=""):
        """Return a path based on the module and extension.

        Args:
            module (str): string containing some corpus module
            lang (str): string containing the goal language of a tmx file
            name (str): name of the wanted file
            extension (str): string containing a file extension
        """
        this_name = self.pathcomponents.basename if name is None else name
        return os.path.join(
            self.pathcomponents.root,
            f"corpus-{self.pathcomponents.lang}{self.pathcomponents.dirsuffix}"
            if module
            else f"corpus-{self.pathcomponents.lang}-orig{self.pathcomponents.dirsuffix}",
            module,
            lang if lang else "",
            self.pathcomponents.genre,
            self.pathcomponents.subdirs,
            this_name + extension,
        )

    @property
    def converted(self):
        """Return the path to the converted file."""
        module = "converted"
        if self.metadata.get_variable("conversion_status") == "correct":
            module = "goldstandard/converted"
        if self.metadata.get_variable("conversion_status") == "correct-no-gs":
            module = "correct-no-gs/converted"

        return self.name(module=module, extension=".xml")

    @property
    def analysed(self):
        """Return the path to analysed file."""
        return self.name(module="analysed", extension=".xml")

    @property
    def korp(self):
        """Return the path to analysed file."""
        return self.name(module="korp", extension=".xml")

    def parallel(self, language):
        """Check if there is a parallel for language.

        Args:
            language (str): language of the parallel file.

        Returns:
            str: path to the parallel file if it exist, otherwise empty string
        """
        try:
            return self.name(
                lang=language, name=self.metadata.get_parallel_texts().get(language)
            )
        except TypeError:
            return ""

    def parallels(self):
        """Return paths to all parallel files.

        Yields:
            str: path to the orig path of a parallel file.
        """
        for language, name in self.metadata.get_parallel_texts().items():
            yield self.name(lang=language, name=name)

    def tmx(self, language):
        """Name of the tmx file.

        Args:
            language (str): language of the parallel

        Returns:
            str: path to the tmx file
        """
        return self.name(
            module="tmx",
            lang=language,
            extension=".tmx",
        )

    @property
    def sent_filename(self):
        """Compute the name of the sentence file.

        Args:
            pfile (str): name of converted corpus file (produced by
                convert2xml)

        Returns:
            str: the name of the tca2 input file
        """
        # Ensure we have 20 bytes of leeway to let TCA2 append
        # lang_sent_new.txt without going over the 255 byte limit:
        origfilename = self.crop_to_bytes(self.pathcomponents.basename, (255 - 20))
        return os.path.join(
            self.pathcomponents.root,
            f"corpus-{self.pathcomponents.lang}{self.pathcomponents.dirsuffix}",
            "tmp",
            f"{origfilename}_{self.pathcomponents.lang}.sent",
        )

    @property
    def tmp_filename(self):
        return os.path.join(
            self.pathcomponents.root,
            f"corpus-{self.pathcomponents.lang}{self.pathcomponents.dirsuffix}",
            "tmp",
            f"{self.pathcomponents.basename}",
        )

    @staticmethod
    def crop_to_bytes(name, max_bytes):
        """Ensure `name` is less than `max_bytes` bytes.

        Do not split name in the middle of a wide byte.
        """
        while len(name.encode("utf-8")) > max_bytes:
            name = name[:-1]
        return name
