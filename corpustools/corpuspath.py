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

import re
from dataclasses import dataclass
from pathlib import Path

from lxml import etree

from corpustools import xslsetter

CORPUS_DIR_RE = re.compile(
    r"(?P<parent>.*)/corpus-(?P<corpusdir>[^/]+)/(?P<corpusfile>.*)"
)


MODULES = [
    "correct-no-gs/converted",
    "goldstandard/converted",
    "stable/converted",
    "stable/tmx",
    "analysed",
    "converted",
    "korp_mono",
    "korp_tmx",
    "tmx",
]


def make_corpus_path(path):
    """Returns a CorpusPath from a given path

    Args:
        path (str): a path to a corpus file

    Raises:
        ValueError: the path is not part of a corpus.
    """

    def fix_filepath(filepath):
        for module in MODULES:
            if filepath.as_posix().startswith(module):
                mod_len = len(module.split("/"))
                if module.endswith("tmx"):
                    mod_len += 1
                return Path().joinpath(*filepath.parts[mod_len:]).with_suffix("")

        if any(filepath.suffix == suffix for suffix in [".xsl", ".log"]):
            return Path(filepath).with_suffix("")

        return Path(filepath)

    corpus_match = CORPUS_DIR_RE.search(Path(path).resolve().as_posix())

    if not corpus_match:
        raise ValueError(f"File is not part of a corpus: {path}")

    corpus_dict = corpus_match.groupdict()
    lang, *dirsuffixes = corpus_dict["corpusdir"].replace("-orig", "").split("-")

    return CorpusPath(
        root=Path(corpus_dict["parent"]),
        lang=lang,
        dirsuffix="-".join(dirsuffixes),
        filepath=fix_filepath(Path(corpus_dict["corpusfile"])),
    )


@dataclass
class CorpusPath:
    """Map filenames in a corpus."""

    root: Path
    lang: str
    filepath: Path
    dirsuffix: str = ""

    def __post_init__(self):
        """Initialise the metadata attribute."""
        self.metadata = xslsetter.MetadataHandler(self.xsl, create=True)

        # If we do not have access to the -orig part of the corpus
        # at least read the parallel info from the converted doc
        if not self.xsl.exists() and self.converted.exists():
            conv_xml = etree.parse(self.converted)
            for para_info in conv_xml.iter("parallel_text"):
                self.metadata.set_parallel_text(
                    language=para_info.attrib[
                        "{http://www.w3.org/XML/1998/namespace}lang"
                    ],
                    location=para_info.attrib["location"],
                )

    @property
    def orig_corpus_dir(self):
        return self.corpus_dir()

    @property
    def converted_corpus_dir(self):
        return self.corpus_dir(module="trigger_no_orig")

    @property
    def orig(self):
        """Return the path of the original file."""
        return self.orig_corpus_dir / self.filepath

    @property
    def xsl(self):
        """Return the path of the metadata file."""
        return self.orig.with_name(f"{self.orig.name}.xsl")

    @property
    def log(self):
        """Return the path of the log file."""
        return self.orig.with_name(f"{self.orig.name}.log")

    def corpus_dir(self, module=None, corpus_lang=None):
        this_lang = self.lang if corpus_lang is None else corpus_lang
        return (
            self.root / f"corpus-{this_lang}"
            f"{'-orig' if module is None else ''}"
            f"{'-' + self.dirsuffix if self.dirsuffix else ''}"
        )

    def name(  # noqa: PLR0913
        self,
        module=None,
        corpus_lang=None,
        target_lang=None,
        filepath=None,
        suffix=None,
    ):
        """Returns a path based on the module and extension.

        Args:
            module (str): string containing some corpus module
            corpus_lang (str): corpus language, as a three letter language code
            target_lang (str): string containing the target language of a tmx
                file
            filepath (str): path to the file
            suffix (str): file suffix
        """
        this_module = "" if module is None else module
        this_target_lang = "" if target_lang is None else target_lang
        this_filepath = (
            f"{self.filepath if filepath is None else filepath}"
            f"{'' if suffix is None else suffix}"
        )
        return (
            self.corpus_dir(module=module, corpus_lang=corpus_lang)
            / this_module
            / this_target_lang
            / this_filepath
        )

    @property
    def converted(self):
        """Return the path to the converted file."""
        module = "converted"
        if self.metadata.get_variable("conversion_status") == "correct":
            module = "goldstandard/converted"
        if self.metadata.get_variable("conversion_status") == "correct-no-gs":
            module = "correct-no-gs/converted"

        return self.name(module=module, suffix=".xml")

    @property
    def analysed(self):
        """Return the path to analysed file."""
        return self.name(module="analysed", suffix=".xml")

    @property
    def korp_mono(self):
        """Return the path to analysed file."""
        return self.name(module="korp_mono", suffix=".xml")

    def korp_tmx(self, target_language):
        """Return the path to korp processed tmx file."""
        return self.name(
            module="korp_tmx",
            target_lang=target_language,
            suffix=".tmx",
        )

    def parallel(self, language):
        """Check if there is a parallel for language.

        Args:
            language (str): language of the parallel file.

        Returns:
            (pathlib.Path): path to the parallel file if it exist, else None
        """
        if self.metadata.get_parallel_texts().get(language) is not None:
            return self.name(
                corpus_lang=language,
                filepath=self.filepath.with_name(
                    self.metadata.get_parallel_texts().get(language)
                ),
            )

    def parallels(self):
        """Return paths to all parallel files.

        Yields:
            (str): path to the orig path of a parallel file.
        """
        return (
            self.parallel(language) for language in self.metadata.get_parallel_texts()
        )

    def tmx(self, target_language):
        """Name of the tmx file.

        Args:
            target_language (str): language of the parallel

        Returns:
            (str): path to the tmx file
        """
        return self.name(
            module="tmx",
            target_lang=target_language,
            suffix=".tmx",
        )

    @property
    def tca2_input(self):
        """Compute the name of the tca2 input file.

        Returns:
            (pathlib.Path): the name of the tca2 input file
        """
        # Ensure we have 20 bytes of leeway to let TCA2 append
        # lang_sent_new.txt without going over the 255 byte limit:
        origfilename = self.crop_to_bytes(self.filepath.name, (255 - 20))
        return Path("/tmp") / f"{origfilename}_{self.lang}.sent"

    @property
    def tca2_output(self):
        """Compute the name of the tca2 output file.

        Returns:
            (pathlib.Path): the name of the tca2 output file
        """
        return self.tca2_input.with_name(
            self.tca2_input.name.replace(".sent", "_new.txt")
        )

    @property
    def tmp_filename(self):
        return self.converted_corpus_dir / "tmp" / self.filepath.name

    @staticmethod
    def crop_to_bytes(name, max_bytes):
        """Ensure `name` is less than `max_bytes` bytes.

        Do not split name in the middle of a wide byte.
        """
        while len(name.encode("utf-8")) > max_bytes:
            name = name[:-1]
        return name


def collect_files(entities, suffix):
    """Collect files with the specified suffix."""
    for entity in entities:
        entity_path = Path(entity).resolve()
        if entity_path.is_file() and entity_path.suffix == suffix:
            yield entity_path
        else:
            for file_ in entity_path.rglob(f"*{suffix}"):
                yield file_
