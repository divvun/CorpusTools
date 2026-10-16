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
#   Copyright © 2013-2026 The University of Tromsø &
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


def content_disposition_to_filename(response: requests.Response) -> str | None:
    """Compute filename from response."""
    try:
        msg = Message()
        msg["Content-Disposition"] = response.headers["Content-Disposition"]
        params = dict(msg.get_params(header="Content-Disposition"))
        return params["filename"]
    except KeyError:
        return None


def url_to_filename(response: requests.Response) -> str:
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

    def __init__(self, download_dir: str) -> None:
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

    def get_response(
        self, url: str, params: dict[str, str] | None = None
    ) -> requests.Response:
        """Get the content of a url.

        Args:
            url: the url to fetch
            params: optional parameters to pass to requests.get

        Returns:
            The response object
        """
        try:
            request = requests.get(url, headers=self.headers, params=params)
            if request.status_code == requests.codes.ok:
                return request
            raise AdderError("ERROR:", url, "does not exist")
        except requests.exceptions.MissingSchema as error:
            raise AdderError(str(error)) from error
        except requests.exceptions.ConnectionError as error:
            raise AdderError(str(error)) from error

    def download(
        self, url: str, params: dict[str, str] | None = None
    ) -> tuple[requests.Response, str]:
        """Download a url to a temporary file.

        Return the request object and the name of the temporary file
        """
        request = self.get_response(url, params=params)
        filename = url_to_filename(request)
        tmpname = os.path.join(self.download_dir, filename)
        with util.ignored(OSError):
            os.makedirs(self.download_dir)
        with open(tmpname, "wb") as tmpfile:
            tmpfile.write(request.content)

        return (request, tmpname)


class AddToCorpus:
    """Class to add files, urls and dirs to the corpus."""

    def __init__(self, corpus_directory: Path, sub_directory: Path) -> None:
        """Initialise the AddToCorpus class.

        Args:
            corpus_directory (str): the directory where the corpus is
            sub_directory (str): subdirectory in the corpus
        """
        self.corpusdir = corpus_directory
        self.goalpath = corpus_directory / sub_directory
        self.goalpath.mkdir(parents=True, exist_ok=True)
        self.vcs = versioncontrol.vcs(corpus_directory)
        self.additions: list[Path] = []

    def copy_url_to_corpus(
        self, url: str, wanted_name: str = "", parallelpath: str = ""
    ):
        """Add a URL to the corpus.

        Copy a downloaded url to the corpus
        """
        downloader = UrlDownloader(os.path.join(self.corpusdir, "tmp"))
        request = downloader.get_response(url)
        filename = wanted_name if wanted_name else url_to_filename(request)
        none_dupe_path = corpuspath.make_corpus_path(
            namechanger.compute_new_basename(self.goalpath / filename).as_posix()
        )
        none_dupe_path.orig.write_bytes(request.content)
        self.additions.append(none_dupe_path.orig)
        self.add_metadata_to_corpus(none_dupe_path, request.url)

        if parallelpath:
            self.update_parallel_data(none_dupe_path, parallelpath)

    def copy_file_to_corpus(
        self,
        origpath: Path,
        metadata_filename: str,
        wanted_name: str = "",
        parallelpath: str = "",
    ) -> Path:
        """Add a file from the hard disk to the corpus.

        Args:
            origpath: path where the original file exists
            metadata_filename: the value of the filename in the
                metadata file
            wanted_name: the name to give the file in the corpus
            parallelpath: where the parallel file of the original
                file exists in the corpus

        Returns:
            Path to where the origfile exists in the corpus
        """
        none_dupe_path = corpuspath.make_corpus_path(
            namechanger.compute_new_basename(
                self.goalpath / (wanted_name if wanted_name else origpath.name)
            ).as_posix()
        )
        none_dupe_path.orig.write_bytes(origpath.read_bytes())
        self.additions.append(none_dupe_path.orig)
        self.add_metadata_to_corpus(none_dupe_path, metadata_filename)
        if parallelpath:
            self.update_parallel_data(none_dupe_path, parallelpath)
        print("Added", none_dupe_path.orig)
        return none_dupe_path.orig

    def add_metadata_to_corpus(
        self, none_dupe_path: corpuspath.CorpusPath, meta_filename: str
    ) -> None:
        """Add the metadata file to the corpus."""
        new_metadata = none_dupe_path.metadata
        new_metadata.set_variable("filename", meta_filename)
        new_metadata.set_variable("mainlang", none_dupe_path.lang)
        new_metadata.set_variable("genre", none_dupe_path.filepath.parts[0])
        new_metadata.write_file()
        self.additions.append(none_dupe_path.xsl)

    @staticmethod
    def update_parallel_data(none_dupe_path: corpuspath.CorpusPath, parallelpath: str):
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
                ).as_posix()
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

    def none_dupe_basename(self, orig_basename: str) -> Path:
        """Compute the none duplicate path of the file to be added.

        Args:
            orig_basename (str): basename of the original file
        Returns:
            Path: path to the none duplicate file
        """
        return namechanger.compute_new_basename(
            self.goalpath / namechanger.normalise_filename(orig_basename),
        )

    def copy_files_in_dir_to_corpus(self, origpath: Path) -> None:
        """Add a directory to the corpus.

        * Recursively walks through the given original directory
            * First checks for duplicates, raises an error printing a list
              of duplicate files if duplicates are found
            * For each file, do the "add file to the corpus" operations
              (minus the parallel info).

        """
        self.find_duplicates(origpath)
        for root, _, files in origpath.walk():
            for file_ in files:
                orig_f = root / file_
                self.copy_file_to_corpus(origpath=orig_f, metadata_filename=file_)

    @staticmethod
    def find_duplicates(origpath: Path):
        """Find duplicates based on the hex digests of the corpus files."""
        duplicates: dict[str, list[Path]] = {}
        for root, _, files in origpath.walk():
            for file_ in files:
                path = root / file_
                file_hash = namechanger.compute_hexdigest(path.open("rb"))
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


def add_originals_to_corpus(args: argparse.Namespace) -> AddToCorpus:
    if args.lang is not None:
        raise SystemExit(
            "The argument -l|--lang is not allowed together with -d|--directory"
        )
    corpus_path = corpuspath.make_corpus_path(
        (Path(args.directory) / "dummy.txt").as_posix()
    )

    if corpus_path.name == "dummy.txt":
        raise SystemExit(
            "Error!\nYou must add genre to the directory\ne.g. {}".format(
                os.path.join(args.directory, "admin")
            )
        )

    adder = AddToCorpus(
        corpus_path.orig_corpus_dir,
        corpus_path.filepath.parent,
    )

    if args.orig.startswith("http"):
        adder.copy_url_to_corpus(args.orig, wanted_name=args.name, parallelpath="")
        return adder

    orig_path = Path(args.orig)
    if orig_path.is_file():
        adder.copy_file_to_corpus(
            origpath=orig_path,
            metadata_filename=orig_path.name,
            wanted_name=args.name,
            parallelpath=args.parallel_file,
        )
    elif orig_path.is_dir():
        if args.name:
            raise SystemExit(
                "It makes no sense to use the --name option together with --directory."
            )
        adder.copy_files_in_dir_to_corpus(orig_path)
    else:
        raise SystemExit(
            f"Cannot handle the orig named: {args.orig}.\n"
            "If you used the --name option and a name with spaces, "
            "encase it in quote marks."
        )
    return adder


def add_parallel_to_corpus(args: argparse.Namespace) -> AddToCorpus:
    if args.directory is not None:
        raise SystemExit(
            "The argument -d|--directory is not allowed together with "
            "-p|--parallel\n"
            "Only -l|--lang is allowed together with -p|--parallel"
        )
    if not os.path.exists(args.parallel_file):
        raise SystemExit(
            "The given parallel file\n\t{}\ndoes not exist".format(args.parallel_file)
        )
    if len(args.origs) > 1:
        raise SystemExit(
            "When the -p option is given, it only makes "
            "sense to add one file at a time."
        )
    if len(args.origs) == 1 and os.path.isdir(args.origs[-1]):
        raise SystemExit(
            "It is not possible to add a directory when the -p option is given."
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
    return adder


def parse_args() -> argparse.Namespace:
    """Parse the commandline options.

    Returns:
        (argparse.Namespace): The parsed commandline arguments
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Add a file, a url or a directory to a corpus directory. "
        "The filenames are converted to ascii only names. Metadata files containing "
        "the original name, the main language, the genre and possibly parallel "
        "files are also made. The files are added to the working copy.",
    )
    parser.add_argument(
        "orig",
        help="The original file, url or directory where "
        "the original file resides (not the corpus repository)",
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

    adder = (
        add_originals_to_corpus(args)
        if args.parallel_file is None
        else add_parallel_to_corpus(args)
    )
    adder.add_files_to_working_copy()
