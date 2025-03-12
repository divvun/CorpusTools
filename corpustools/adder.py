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
#   Copyright © 2013-2025 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""This file contains classes to add files to a corpus directory."""


import argparse
import os
import shutil
from email.message import Message
from pathlib import Path

import requests

from corpustools import argparse_version, corpuspath, namechanger, util, versioncontrol


class AdderError(Exception):
    """Raise this exception when errors happen in this module."""


def add_url_extension(url, content_type):
    """Add an extension to the file depending on the content type."""
    basename = url.split("/")[-2] if url.endswith("/") else "index"

    content_type_extension = {
        "text/html": ".html",
        "application/msword": ".doc",
        "application/pdf": ".pdf",
        "text/plain": ".txt",
    }

    for name, extension in content_type_extension.items():
        if name in content_type and not url.endswith(extension):
            return f"{basename}{extension}"

    return basename


def content_disposition_to_filename(response):
    """Compute filename from response."""
    try:
        msg = Message()
        msg["Content-Disposition"] = response.headers["Content-Disposition"]
        params = dict(msg.get_params(header="Content-Disposition"))
        return params["filename"]
    except KeyError:
        return None


def url_to_filename(response):
    """Compute the filename.

    Args:
        response (requests.get response): The response object

    Returns:
        (str): Name of the file.
    """
    filename = content_disposition_to_filename(response)
    if filename is not None:
        return filename

    return add_url_extension(response.url, response.headers["content-type"])


class UrlDownloader:
    """Download a document from a url."""

    def __init__(self, download_dir):
        """Initialise the UrlDownloader class.

        Args:
            download_dir (str): the path where the file should be saved.
        """
        self.download_dir = download_dir
        self.headers = {
            "user-agent": (
                "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) "
                "Gecko/20130331 Firefox/21.0"
            )
        }

    def download(self, url, wanted_name="", params=None):
        """Download a url to a temporary file.

        Return the request object and the name of the temporary file
        """
        try:
            request = requests.get(url, headers=self.headers, params=params)
            if request.status_code == requests.codes.ok:
                filename = wanted_name if wanted_name else url_to_filename(request)
                tmpname = os.path.join(self.download_dir, filename)
                with util.ignored(OSError):
                    os.makedirs(self.download_dir)
                with open(tmpname, "wb") as tmpfile:
                    tmpfile.write(request.content)

                return (request, tmpname)
            raise AdderError("ERROR:", url, "does not exist")
        except requests.exceptions.MissingSchema as error:
            raise AdderError(str(error)) from error
        except requests.exceptions.ConnectionError as error:
            raise AdderError(str(error)) from error


class AddToCorpus:
    """Class to add files, urls and dirs to the corpus."""

    def __init__(self, corpus_directory, sub_directory):
        """Initialise the AddToCorpus class.

        Args:
            corpus_directory (str): the directory where the corpus is
            sub_directory (str): subdirectory in the corpus
        """
        self.corpusdir = corpus_directory
        self.goalpath = Path(corpus_directory) / sub_directory
        self.goalpath.mkdir(parents=True, exist_ok=True)
        self.vcs = versioncontrol.vcs(corpus_directory)
        self.additions = []

    def copy_url_to_corpus(self, url, wanted_name="", parallelpath=""):
        """Add a URL to the corpus.

        Copy a downloaded url to the corpus
        """
        downloader = UrlDownloader(os.path.join(self.corpusdir, "tmp"))
        (request, tmpname) = downloader.download(url, wanted_name=wanted_name)

        return self.copy_file_to_corpus(
            origpath=tmpname, metadata_filename=request.url, parallelpath=parallelpath
        )

    def copy_file_to_corpus(self, origpath, metadata_filename, parallelpath=""):
        """Add a file from the hard disk to the corpus.

        Args:
            origpath (str): path where the original file exists
            metadata_filename (str): the value of the filename in the
                metadata file
            parallelpath (str): where the parallel file of the original
                file exists in the corpus

        Returns:
            (str): path to where the origfile exists in the corpus
        """
        origpath = Path(origpath)
        none_dupe_path = corpuspath.make_corpus_path(
            namechanger.compute_new_basename(Path(self.goalpath) / origpath.name)
        )
        none_dupe_path.orig.write_bytes(origpath.read_bytes())
        self.additions.append(none_dupe_path.orig)
        self.add_metadata_to_corpus(none_dupe_path, metadata_filename)
        if parallelpath:
            self.update_parallel_data(none_dupe_path, parallelpath)
        print("Added", none_dupe_path.orig)
        return none_dupe_path.orig

    def add_metadata_to_corpus(self, none_dupe_path, meta_filename):
        """Add the metadata file to the corpus."""
        new_metadata = none_dupe_path.metadata
        new_metadata.set_variable("filename", meta_filename)
        new_metadata.set_variable("mainlang", none_dupe_path.lang)
        new_metadata.set_variable("genre", none_dupe_path.filepath.parts[0])
        new_metadata.write_file()
        self.additions.append(none_dupe_path.xsl)

    @staticmethod
    def update_parallel_data(none_dupe_path, parallelpath):
        """Update metadata in the parallel files.

        Args:
            none_dupe_path (util.PathComponents): of none_dupe_path
            parallelpath (str): path of the parallel file
        """
        if not os.path.exists(parallelpath):
            raise AdderError(f"{parallelpath} does not exist")

        parallel_corpuspath = corpuspath.make_corpus_path(parallelpath)

        none_dupe_path.metadata.set_parallel_text(
            parallel_corpuspath.lang,
            parallel_corpuspath.filepath.name,
        )
        for (
            lang,
            parallel_file,
        ) in parallel_corpuspath.metadata.get_parallel_texts().items():
            this_para_corpuspath = corpuspath.make_corpus_path(
                parallel_corpuspath.name(
                    corpus_lang=lang,
                    filepath=parallel_corpuspath.filepath.with_name(parallel_file),
                )
            )
            this_para_corpuspath.metadata.set_parallel_text(
                none_dupe_path.lang, none_dupe_path.filepath.name
            )
            this_para_corpuspath.metadata.write_file()
            none_dupe_path.metadata.set_parallel_text(
                this_para_corpuspath.lang,
                this_para_corpuspath.filepath.name,
            )
        none_dupe_path.metadata.write_file()

        parallel_corpuspath.metadata.set_parallel_text(
            none_dupe_path.lang, none_dupe_path.filepath.name
        )
        parallel_corpuspath.metadata.write_file()

    def none_dupe_basename(self, orig_basename):
        """Compute the none duplicate path of the file to be added.

        Args:
            orig_basename (str): basename of the original file
        """
        return namechanger.compute_new_basename(
            self.goalpath,
            namechanger.normalise_filename(orig_basename),
        )

    def copy_files_in_dir_to_corpus(self, origpath):
        """Add a directory to the corpus.

        * Recursively walks through the given original directory
            * First checks for duplicates, raises an error printing a list
              of duplicate files if duplicates are found
            * For each file, do the "add file to the corpus" operations
              (minus the parallel info).

        """
        self.find_duplicates(origpath)
        for root, _, files in os.walk(origpath):
            for file_ in files:
                orig_f = os.path.join(root, file_)
                self.copy_file_to_corpus(origpath=orig_f, metadata_filename=orig_f)

    @staticmethod
    def find_duplicates(origpath):
        """Find duplicates based on the hex digests of the corpus files."""
        duplicates = {}
        for root, _, files in os.walk(origpath):
            for file_ in files:
                path = os.path.join(root, file_)
                with open(path, "rb") as content:
                    file_hash = namechanger.compute_hexdigest(content)
                    if file_hash in duplicates:
                        duplicates[file_hash].append(path)
                    else:
                        duplicates[file_hash] = [path]

        results = [x for x in list(duplicates.values()) if len(x) > 1]
        if results:
            print("Duplicates Found:")
            print("___")
            for result in results:
                for subresult in result:
                    print(f"\t{subresult}")
                print("___")

            raise AdderError("Found duplicates")

    def add_files_to_working_copy(self):
        """Add the downloaded files to the working copy."""
        self.vcs.add(self.additions)


def parse_args():
    """Parse the commandline options.

    Returns:
        (argparse.Namespace): The parsed commandline arguments
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Add file(s) to a corpus directory. The filenames are "
        "converted to ascii only names. Metadata files containing the "
        "original name, the main language, the genre and possibly parallel "
        "files are also made. The files are added to the working copy.",
    )
    parser.add_argument(
        "origs",
        nargs="+",
        help="The original files, urls or directories where "
        "the original files reside (not the corpus repository)",
    )
    parser.add_argument(
        "--name",
        dest="name",
        help="Specify the name of the file in the corpus. "
        "Especially files fetched from the net often have "
        "names that are not human friendly. Use this "
        "option to guard against that.",
    )

    parallel = parser.add_argument_group("parallel")
    parallel.add_argument(
        "-p",
        "--parallel",
        dest="parallel_file",
        help="Path to an existing file in the corpus that "
        "will be parallel to the orig that is about to be added",
    )
    parallel.add_argument(
        "-l", "--lang", dest="lang", help="Language of the file to be added"
    )

    no_parallel = parser.add_argument_group("no_parallel")
    no_parallel.add_argument(
        "-d",
        "--directory",
        dest="directory",
        help="The directory where the origs should be placed",
    )

    return parser.parse_args()


def main():
    """Add files, directories and urls to the corpus."""
    args = parse_args()

    if args.parallel_file is None:
        if args.lang is not None:
            raise SystemExit(
                "The argument -l|--lang is not allowed together with " "-d|--directory"
            )
        corpus_path = corpuspath.make_corpus_path(
            (Path(args.directory) / "dummy.txt").as_posix()
        )

        if corpus_path.name == "dummy.txt":
            raise SystemExit(
                "Error!\n"
                "You must add genre to the directory\ne.g. {}".format(
                    os.path.join(args.directory, "admin")
                )
            )

        adder = AddToCorpus(
            corpus_path.orig_corpus_dir,
            corpus_path.filepath.parent,
        )
        for orig in args.origs:
            if os.path.isfile(orig):
                if args.name:
                    newname = os.path.join(os.path.dirname(orig), args.name)
                    try:
                        shutil.copy(orig, newname)
                    except FileNotFoundError:
                        raise SystemExit(f"Not a valid filename: {args.name}")
                    orig = newname
                adder.copy_file_to_corpus(
                    origpath=orig, metadata_filename=os.path.basename(orig)
                )
            elif orig.startswith("http"):
                adder.copy_url_to_corpus(orig, wanted_name=args.name)
            elif os.path.isdir(orig):
                if args.name:
                    raise SystemExit(
                        "It makes no sense to use the --name "
                        "option together with --directory."
                    )
                adder.copy_files_in_dir_to_corpus(orig)
            else:
                raise SystemExit(
                    "Cannot handle the orig named: {}.\n"
                    "If you used the --name option and a name with spaces, "
                    "encase it in quote marks.".format(orig)
                )
    else:
        if args.directory is not None:
            raise SystemExit(
                "The argument -d|--directory is not allowed together with "
                "-p|--parallel\n"
                "Only -l|--lang is allowed together with -p|--parallel"
            )
        if not os.path.exists(args.parallel_file):
            raise SystemExit(
                "The given parallel file\n\t{}\n"
                "does not exist".format(args.parallel_file)
            )
        if len(args.origs) > 1:
            raise SystemExit(
                "When the -p option is given, it only makes "
                "sense to add one file at a time."
            )
        if len(args.origs) == 1 and os.path.isdir(args.origs[-1]):
            raise SystemExit(
                "It is not possible to add a directory " "when the -p option is given."
            )

        parallel_corpus_path = corpuspath.make_corpus_path(args.parallel_file)
        corpus_path = corpuspath.make_corpus_path(
            parallel_corpus_path.name(corpus_lang=args.lang)
        )
        adder = AddToCorpus(
            corpus_directory=corpus_path.orig_corpus_dir,
            sub_directory=corpus_path.filepath.parent,
        )

        orig = args.origs[0]
        if os.path.isfile(orig):
            if args.name:
                newname = os.path.join(os.path.dirname(orig), args.name)
                shutil.copy(orig, newname)
                orig = newname
            adder.copy_file_to_corpus(
                origpath=orig, metadata_filename=orig, parallelpath=args.parallel_file
            )
        elif orig.startswith("http"):
            adder.copy_url_to_corpus(
                orig, wanted_name=args.name, parallelpath=args.parallel_file
            )

    adder.add_files_to_working_copy()
