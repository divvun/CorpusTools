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
from urllib.parse import unquote

from pathlib import Path
import unidecode

from corpustools import util, versioncontrol, xslsetter, corpuspath


class NamechangerError(Exception):
    """This exception is raised when errors occurs in this module."""


PathPair = namedtuple("PathPair", "oldpath newpath")


class MovepairComputer:
    """Compute oldname, newname pairs."""

    def __init__(self):
        """Initialise the MovepairComputer.

        filepairs (list of PathPairs): List of filepairs that should be moved.
        """
        self.filepairs = []

    def compute_orig_movepair(self, oldpath, newpath, nochange=False):
        """Add the oldpath and the new goalpath to filepairs.

        Args:
            oldpath (unicode): the old path to an original file
            newpath (unicode): the new path of an original file
        """
        if not newpath:
            self.filepairs.append(PathPair(oldpath, ""))
        else:
            normalisedpath = os.path.join(
                os.path.dirname(newpath), normalise_filename(os.path.basename(newpath))
            )
            if normalisedpath == newpath and nochange:
                non_dupe_path = newpath
            else:
                non_dupe_path = compute_new_basename(oldpath, normalisedpath)

            self.filepairs.append(PathPair(oldpath, non_dupe_path))

    def compute_parallel_movepairs(self, oldpath, newpath):
        """Add the parallel files of oldpath to filepairs.

        Args:
            oldpath (unicode): the old path
            newpath (unicode): the new path
        """
        old_corpus_path = corpuspath.CorpusPath(oldpath)
        if not newpath:
            newpath = oldpath

        for parallel_name in old_corpus_path.parallels():
            old_parallel_corpus_path = corpuspath.CorpusPath(parallel_name)
            new_corpus_path = corpuspath.CorpusPath(newpath)
            new_parallel_name = old_parallel_corpus_path.move_orig(
                genre=new_corpus_path.pathcomponents.genre,
                subdirs=new_corpus_path.pathcomponents.subdirs,
            )
            self.compute_orig_movepair(parallel_name, new_parallel_name)

    def compute_all_movepairs(self, oldpath, newpath):
        """Compute all the potential name pairs that should be moved.

        Args:
            oldpath (str): path to the original file.
            newpath (str): path to the new file.
        """
        self.compute_orig_movepair(oldpath, newpath)
        self.compute_parallel_movepairs(oldpath, newpath)


class CorpusFileMover:
    """Move an original file and all its derived files."""

    def __init__(self, oldpath, newpath):
        """Class to move corpus files.

        Args:
            oldpath (unicode): the old path of the original file.
            newpath (unicode): the new path of tht original file.
        """
        self.old_corpus_path = corpuspath.CorpusPath(oldpath)
        p = Path(oldpath)
        if not p.exists():
            raise SystemExit(f"{oldpath} does not exist!")
        self.new_corpus_path = corpuspath.CorpusPath(newpath)
        self.new_corpus_path.metadata = self.old_corpus_path.metadata
        self.orig_vcs = versioncontrol.vcs(self.old_corpus_path.orig_corpus_dir)
        self.conv_vcs = versioncontrol.vcs(self.old_corpus_path.converted_corpus_dir)

    def move_files(self):
        """Move all files that are under version control."""
        p = Path(self.new_corpus_path.orig)
        if not p.parent.exists():
            p.parent.mkdir(parents=True)

        self.orig_vcs.move(self.old_corpus_path.orig, self.new_corpus_path.orig)
        self.orig_vcs.move(self.old_corpus_path.xsl, self.new_corpus_path.xsl)

        if os.path.exists(self.old_corpus_path.converted):
            p = Path(self.new_corpus_path.converted)
            if not p.parent.exists():
                p.parent.mkdir(parents=True)
            self.conv_vcs.move(
                self.old_corpus_path.converted, self.new_corpus_path.converted
            )
        if not self.old_corpus_path.metadata.get_variable("translated_from"):
            for lang in self.old_corpus_path.metadata.get_parallel_texts():
                if os.path.exists(self.old_corpus_path.tmx(lang)):
                    p = Path(self.new_corpus_path.tmx(lang))
                    if not p.parent.exists():
                        p.parent.mkdir(parents=True)
                    self.conv_vcs.move(
                        self.old_corpus_path.tmx(lang), self.new_corpus_path.tmx(lang)
                    )


class CorpusFileRemover:
    """Remove an original file and all its derived files."""

    def __init__(self, oldpath):
        """Class to remove corpus files.

        Args:
            oldpath (unicode): the old path
        """
        self.old_corpus_path = corpuspath.CorpusPath(oldpath)
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


class CorpusFilesetMoverAndUpdater:
    """Move or remove a file within a repository.

    When moving a file inside the same directory:
    * move the original file
    * move the metadata file
    * move the prestable/converted file
    * move the prestable/toktmx file
    * move the prestable/tmx file
    * change the metadata in the metadata file, if needed
    * change the reference to the file name in the parallel files'
      metadata, if needed
    * if the parallel files need name normalisation, move them the same way the
      original file is handled

    Removal is signaled by an empty string for the newpath argument.
    When removing a file. :
    * remove the original file
    * remove the metadata file
    * remove the prestable/converted file
    * remove the prestable/toktmx file
    * remove the prestable/tmx file
    * change the reference to the file name in the parallel files' metadata
    * if the parallel files need name normalisation, move them the same way the
      original file is handled

    When moving a file from one subdirectory to another:
    * move the original file
    * move the metadata file
    * move the prestable/converted file
    * move the prestable/toktmx file
    * move the prestable/tmx file
    * change the metadata in the metadata file, if needed
    * change the reference to the file name in the parallel files'
      metadata, if needed
    * change the reference to the file name in the parallel files'
      metadata if needed
    * move the parallel files the same way the original file has been moved.

    When moving a file to a new genre:
    * the subdirectory move operations +
    * change the genre reference in the metadata files

    When moving a file to a new language:
    * move the original file
    * move the metadata file
    * move the prestable/converted file
    * move the prestable/toktmx file
    * move the prestable/tmx file
    * change the language of the file in the parallel files' metadata
    * if the parallel files need name normalisation, move them the same way the
      original file is handled

    Normalise a file name: Replace non-ascii char with ascii ones and remove
    unwanted characters.

    When doing these operations, detect name clashes for the original files.

    If a name clash is found, check if the files are duplicates. If they are
    duplicates, raise an exception, otherwise suggest a new name.
    """

    def __init__(self, oldpath, newpath):
        """Initialise the CorpusFilesetMoverAndUpdater class.

        oldpath (str): path to the file that should be renamed.
        newpath (str): path to the new name of the file.
        """
        orig_corpus_path = corpuspath.CorpusPath(oldpath)
        orig_corpus_path.metadata.set_lang_genre_xsl()
        orig_corpus_path.metadata.write_file()

        self.old_components = orig_corpus_path.pathcomponents
        self.vcs = versioncontrol.vcs(
            os.path.join(
                orig_corpus_path.pathcomponents.root,
                f"corpus-{orig_corpus_path.pathcomponents.lang}{orig_corpus_path.pathcomponents.dirsuffix}",
            )
        )
        # self.vcs.add(orig_corpus_path.xsl)

        self.move_computer = MovepairComputer()
        self.move_computer.compute_all_movepairs(oldpath, newpath)

    def move_files(self):
        """Move all files under version control that belong to the original."""
        for filepair in self.move_computer.filepairs:
            if not filepair.newpath:
                cfr = CorpusFileRemover(filepair.oldpath)
                cfr.remove_files()
            elif filepair.oldpath != filepair.newpath:
                cfm = CorpusFileMover(filepair.oldpath, filepair.newpath)
                cfm.move_files()

    def update_own_metadata(self):
        """Update metadata."""
        for filepair in self.move_computer.filepairs:
            if filepair.newpath:
                old_components = corpuspath.CorpusPath(filepair.oldpath).pathcomponents
                new_components = corpuspath.CorpusPath(filepair.newpath).pathcomponents

                metadataname = filepair.newpath + ".xsl"
                if os.path.isfile(metadataname):
                    metadatafile = xslsetter.MetadataHandler(metadataname)
                    if old_components.genre != new_components.genre:
                        metadatafile.set_variable("genre", new_components.genre)
                    if old_components.lang != new_components.lang:
                        metadatafile.set_variable("mainlang", new_components.lang)
                    metadatafile.write_file()
                    self.vcs.add(metadataname)

    def update_parallel_file_metadata(self, old_components, newpath, parallel_name):
        """Update metadata in a metadata file.

        Args:
            old_components (util.PathComponents): A named tuple
                representing the path to the old name of the file
            newpath (str): path to the new file
            parallel_name (str) : name of the parallel file
        """
        parallel_metadatafile = xslsetter.MetadataHandler(parallel_name)

        if newpath:
            new_components = corpuspath.CorpusPath(newpath).pathcomponents
            if old_components.lang != new_components.lang:
                parallel_metadatafile.set_parallel_text(old_components.lang, "")
                parallel_metadatafile.set_parallel_text(
                    new_components.lang, new_components.basename
                )
            elif old_components.basename != new_components.basename:
                parallel_metadatafile.set_parallel_text(
                    new_components.lang, new_components.basename
                )

        else:
            parallel_metadatafile.set_parallel_text(old_components.lang, "")

        parallel_metadatafile.write_file()
        self.vcs.add(parallel_name)

    def update_parallel_files_metadata(self):
        """Update the info in the parallel files."""
        for filepair in self.move_computer.filepairs:
            parallel_filepairs = list(self.move_computer.filepairs)
            parallel_filepairs.remove(filepair)
            old_components = corpuspath.CorpusPath(filepair.oldpath).pathcomponents

            for parallel_filepair in parallel_filepairs:
                parallel_name = parallel_filepair.newpath + ".xsl"
                if os.path.isfile(parallel_name):
                    self.update_parallel_file_metadata(
                        old_components, filepair.newpath, parallel_name
                    )


def compute_hexdigest(afile, blocksize=65536):
    """Compute the hexdigest of the file in path.

    Args:
        afile: a file like object

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


def compute_new_basename(oldpath, wanted_path):
    """Compute the new path.

    Args:
        oldpath (unicode): path to the old file
        wanted_path (unicode): the path that one wants to move the file to

    Returns:
        a unicode string pointing to the new path
    """
    wanted_basename = os.path.basename(wanted_path)
    new_basename = os.path.basename(wanted_path)
    newpath = os.path.join(os.path.dirname(wanted_path), new_basename)
    index = 1

    while os.path.exists(newpath):
        if are_duplicates(oldpath, newpath):
            raise UserWarning(f"{oldpath} and {newpath} are duplicates. ")
        else:
            if "." in wanted_basename:
                dot = wanted_basename.rfind(".")
                extension = wanted_basename[dot:]
                pre_extension = wanted_basename[:dot]
                new_basename = pre_extension + "_" + str(index) + extension
            else:
                new_basename = wanted_basename + str(index)
            newpath = os.path.join(os.path.dirname(wanted_path), new_basename)
            index += 1

    return newpath
