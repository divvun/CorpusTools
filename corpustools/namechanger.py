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
#   Copyright © 2013-2023 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Classes and functions change names of corpus files."""


import hashlib
import os
import re
from collections import namedtuple
from pathlib import Path
from urllib.parse import unquote

import unidecode

from corpustools import corpuspath, versioncontrol


class NamechangerError(Exception):
    """This exception is raised when errors occurs in this module."""


PathPair = namedtuple("PathPair", "oldpath newpath")


class CorpusFileRemover:
    """Remove an original file and all its derived files."""

    def __init__(self, oldpath):
        """Class to remove corpus files.

        Args:
            oldpath (unicode): the old path
        """
        self.old_corpus_path = corpuspath.make_corpus_path(oldpath)
        p = Path(oldpath)
        if not p.exists():
            raise SystemExit(f"{oldpath} does not exist!")
        self.orig_vcs = versioncontrol.vcs(self.old_corpus_path.orig_corpus_dir)
        self.conv_vcs = versioncontrol.vcs(self.old_corpus_path.converted_corpus_dir)

    def remove_files(self):
        """Remove all the files that are under version control."""
        self.orig_vcs.remove(self.old_corpus_path.orig)
        self.orig_vcs.remove(self.old_corpus_path.xsl)
        self.conv_vcs.remove(self.old_corpus_path.converted)
        for lang in self.old_corpus_path.metadata.get_parallel_texts():
            if os.path.exists(self.old_corpus_path.tmx(lang)):
                self.conv_vcs.remove(self.old_corpus_path.tmx(lang))


def compute_hexdigest(afile, blocksize=65536):
    """Compute the hexdigest of the file in path.

    Args:
        afile (file): a file like object

    Returns:
        a hexdigest of the file
    """
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while buf:
        hasher.update(buf)
        buf = afile.read(blocksize)

    return hasher.hexdigest()


def normalise_filename(filename):
    """Normalise filename to ascii only.

    Downcase filename, replace non-ascii characters with ascii ones and
    remove or replace unwanted characters.

    Args:
        filename (str): name of the file

    Returns:
        a downcased string containing only ascii chars
    """
    if os.sep in filename:
        raise NamechangerError(
            "Invalid filename {}.\n"
            "Filename is not allowed to contain {}".format(filename, os.sep)
        )

    # unicode.decode wants a unicode string
    if not isinstance(filename, str):
        filename = filename.decode("utf8")

    # unidecode.unidecode makes ascii only
    # urllib.unquote replaces %xx escapes by their single-character equivalent.
    asciiname = unidecode.unidecode(unquote(filename))

    while asciiname.startswith(("-", "_")):
        asciiname = asciiname[1:]

    unwanted = re.compile("[+ ()'–?,!,<>\"&;&#\\|$]+")

    return unwanted.sub("_", asciiname).lower()


def are_duplicates(oldpath, newpath):
    """Check if oldpath and newpath are duplicates of each other.

    Args:
        oldpath (unicode): old path of the file
        newpath (unicode): the wanted, new path of the file

    Returns:
        a boolean indicating if the two files are duplicates
    """
    if os.path.isfile(oldpath) and os.path.isfile(newpath):
        with open(oldpath, "rb") as oldcontent, open(newpath, "rb") as newcontent:
            return compute_hexdigest(oldcontent) == compute_hexdigest(newcontent)
    else:
        return False


def compute_new_basename(orig_path):
    """Compute the new path.

    Args:
        path (Path): path to file, basename should possibly be normalised

    Returns:
        Path: lower cased, ascii path
    """
    wanted_basename = normalise_filename(orig_path.name)
    new_path = orig_path.with_name(wanted_basename)
    index = 1
    while os.path.exists(new_path):
        if are_duplicates(orig_path, new_path):
            raise UserWarning(f"{orig_path} and {new_path} are duplicates. ")
        else:
            if "." in wanted_basename:
                dot = wanted_basename.rfind(".")
                extension = wanted_basename[dot:]
                pre_extension = wanted_basename[:dot]
                new_basename = pre_extension + "_" + str(index) + extension
            else:
                new_basename = wanted_basename + str(index)
            new_path = orig_path.with_name(new_basename)
            index += 1

    return new_path
