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
#   Copyright © 2015-2023 The University of Tromsø & the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Move a corpus file from oldpath to newpath."""


import argparse
import sys
from pathlib import Path

from git.exc import GitCommandError
from corpustools import argparse_version, corpuspath, namechanger, versioncontrol


def update_metadata(filepairs):
    """Update parallel info for all filepairs."""
    for filepair in filepairs:
        if filepair[0].filepath.name != filepair[1].filepath.name:
            for parallel_name in filepair[0].parallels():
                parallel_path = corpuspath.make_corpus_path(parallel_name)
                parallel_path.metadata.set_parallel_text(
                    language=filepair[1].lang,
                    location=filepair[1].filepath.name,
                )
                parallel_path.metadata.write_file()
                parallel_vcs = versioncontrol.vcs(parallel_path.orig_corpus_dir)
                parallel_vcs.add(parallel_path.xsl)


def move_corpuspath(old_corpuspath, new_corpuspath):
    """Move a set of corpus files to a new location."""
    orig_vcs = versioncontrol.vcs(old_corpuspath.orig_corpus_dir)
    conv_vcs = versioncontrol.vcs(old_corpuspath.converted_corpus_dir)

    new_corpuspath.orig.parent.mkdir(exist_ok=True, parents=True)
    orig_vcs.move(old_corpuspath.orig, new_corpuspath.orig)
    orig_vcs.move(old_corpuspath.xsl, new_corpuspath.xsl)

    if old_corpuspath.converted.exists():
        new_corpuspath.converted.parent.mkdir(exist_ok=True, parents=True)
        try:
            conv_vcs.move(old_corpuspath.converted, new_corpuspath.converted)
        except GitCommandError:
            old_corpuspath.converted.unlink()

    if not old_corpuspath.metadata.get_variable("translated_from"):
        for lang in old_corpuspath.metadata.get_parallel_texts():
            if old_corpuspath.tmx(lang).exists():
                old_corpuspath.tmx(lang).mkdir(exist_ok=True, parents=True)
                conv_vcs.move(old_corpuspath.tmx(lang), new_corpuspath.tmx(lang))


def is_parallel_move_needed(old_filepath, new_filepath):
    return old_filepath.parent != new_filepath.parent


def compute_movenames(oldpath, newpath):
    """Make CorpusPath pairs for the files that needs to move.

    Args:
        oldpath (Path): path to the old file
        newpath (Path): path to the new file, with normalised name

    Returns:
        (list[tuple]): List of tuples of the files that needs to be moved
    """
    filepairs = [
        (oldpath, newpath),
    ]
    filepairs.extend(compute_parallel_movenames(oldpath, newpath))

    return filepairs


def compute_parallel_movenames(old_corpuspath, new_corpuspath):
    """Compute pairs of CorpusPaths for parallel files.

    Args:
        old_corpuspath (CorpusPath): the existing file
        new_corpuspath (CorpusPath): the new name of the file

    Returns:
        (list[tuple]): List of tuples of the parallel files that needs to
            be moved
    """

    return (
        [
            (
                corpuspath.make_corpus_path(
                    old_corpuspath.name(
                        corpus_lang=para_lang,
                        filepath=old_corpuspath.filepath.with_name(para_name),
                    )
                ),
                corpuspath.make_corpus_path(
                    new_corpuspath.name(
                        corpus_lang=para_lang,
                        filepath=new_corpuspath.filepath.with_name(para_name),
                    )
                ),
            )
            for (
                para_lang,
                para_name,
            ) in old_corpuspath.metadata.get_parallel_texts().items()
        ]
        if is_parallel_move_needed(old_corpuspath.filepath, new_corpuspath.filepath)
        else []
    )


def mover(oldpath, newpath):
    """Move filepairs and update metadata."""
    filepairs = compute_movenames(oldpath, newpath)
    update_metadata(filepairs)
    for filepair in filepairs:
        move_corpuspath(old_corpuspath=filepair[0], new_corpuspath=filepair[1])


def mover_parse_args():
    """Parse the commandline options.

    Returns:
        (argparse.Namespace): the parsed commandline arguments
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Program to move or rename a file inside the corpus.",
    )

    parser.add_argument("oldpath", help="The path of the old file.")
    parser.add_argument(
        "newpath",
        help="The place to move the file to. newpath can "
        "be either a filename or a directory",
    )

    return parser.parse_args()


def main():
    """Move a file."""
    args = mover_parse_args()
    if args.oldpath == args.newpath:
        print(
            f"{args.oldpath} and {args.newpath} are the same file",
            file=sys.stderr,
        )
    else:
        oldpath = Path(args.oldpath)
        newpath = Path(args.newpath)

        if not newpath.suffix:
            newpath = newpath / oldpath.name

        try:
            mover(
                corpuspath.make_corpus_path(oldpath),
                corpuspath.make_corpus_path(namechanger.compute_new_basename(newpath)),
            )
        except UserWarning as e:
            print("Can not move file:", str(e), file=sys.stderr)


def remove_metadata(remove_path):
    """Remove parallel info about remove_path."""
    for para_lang, para_name in remove_path.metadata.get_parallel_texts().items():
        para_path = corpuspath.make_corpus_path(
            remove_path.name(
                corpus_lang=para_lang,
                filepath=remove_path.filepath.with_name(para_name),
            )
        )
        para_path.metadata.set_parallel_text(language=remove_path.lang, location="")
        para_path.metadata.write_file()
        parallel_vcs = versioncontrol.vcs(para_path.orig_corpus_dir)
        parallel_vcs.add(para_path.xsl)


def remover_parse_args():
    """Parse the commandline options.

    Returns:
        (argparse.Namespace): the parsed commandline arguments
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Program to remove a file from the corpus.",
    )

    parser.add_argument("oldpath", help="The path of the old file.")

    return parser.parse_args()


def remove_main():
    """Remove a file."""
    args = remover_parse_args()
    try:
        old_corpuspath = corpuspath.make_corpus_path(args.oldpath)
        remove_metadata(old_corpuspath)

        orig_vcs = versioncontrol.vcs(old_corpuspath.orig_corpus_dir)
        orig_vcs.remove(old_corpuspath.orig)
        orig_vcs.remove(old_corpuspath.xsl)

        conv_vcs = versioncontrol.vcs(old_corpuspath.converted_corpus_dir)

        if Path(old_corpuspath.converted).exists():
            conv_vcs.remove(old_corpuspath.converted)

        for lang in old_corpuspath.metadata.get_parallel_texts():
            tmx_path = Path(old_corpuspath.tmx(lang))
            if tmx_path.exists():
                conv_vcs.remove(tmx_path.as_posix())

    except UserWarning as e:
        print("Can not remove file:", str(e), file=sys.stderr)
