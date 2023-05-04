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
import os
import sys
from pathlib import Path

from corpustools import (argparse_version, corpuspath, namechanger,
                         versioncontrol)


def update_metadata(filepairs):
    """Update parallel info for all filepairs."""
    for filepair in filepairs:
        if filepair[0].pathcomponents.basename != filepair[1].pathcomponents.basename:
            for filepair1 in filepairs:
                if filepair1[0].orig != filepair[0].orig:
                    filepair1[1].metadata.set_parallel_text(
                        language=filepair[1].pathcomponents.lang,
                        location=filepair1[1].pathcomponents.basename,
                    )
                    parallel_vcs = versioncontrol.vcs(filepair1[1].orig_corpus_dir)
                    parallel_vcs.add(filepair1[1].xsl)


def move_corpuspath(old_corpuspath, new_corpuspath):
    """Move a set of corpus files to a new location."""
    orig_vcs = versioncontrol.vcs(old_corpuspath.orig_corpus_dir)
    conv_vcs = versioncontrol.vcs(old_corpuspath.converted_corpus_dir)

    orig_vcs.move(old_corpuspath.orig, new_corpuspath.orig)
    orig_vcs.move(old_corpuspath.xsl, new_corpuspath.xsl)

    if Path(old_corpuspath.converted).exists():
        p = Path(new_corpuspath.converted)
        if not p.parent.exists():
            p.parent.mkdir(parents=True)
        conv_vcs.move(old_corpuspath.converted, new_corpuspath.converted)

    if not old_corpuspath.metadata.get_variable("translated_from"):
        for lang in old_corpuspath.metadata.get_parallel_texts():
            if os.path.exists(old_corpuspath.tmx(lang)):
                p = Path(new_corpuspath.tmx(lang))
                if not p.parent.exists():
                    p.parent.mkdir(parents=True)
                conv_vcs.move(old_corpuspath.tmx(lang), new_corpuspath.tmx(lang))


def is_parallel_move_needed(old_components, new_components):
    return (
        old_components.lang != new_components.lang
        or f"{old_components.genre}/{old_components.subdirs}"
        != f"{new_components.genre}/{new_components.subdirs}"
    )


def compute_movenames(oldpath, newpath):
    """Make CorpusPath pairs for the files that needs to move.

    Args:
        oldpath (Path): path to the old file
        newpath (Path): path to the new file, with normalised name
    """
    filepairs = [
        (
            corpuspath.CorpusPath(oldpath),
            corpuspath.CorpusPath(os.path.join(newpath, os.path.basename(oldpath)))
            if os.path.isdir(newpath)
            else corpuspath.CorpusPath(newpath),
        ),
    ]
    compute_parallel_movenames(filepairs)

    return filepairs


def compute_parallel_movenames(filepairs):
    """Compute pairs of CorpusPaths for parallel files."""
    old_components = filepairs[0][0].pathcomponents
    new_components = filepairs[0][1].pathcomponents

    if is_parallel_move_needed(old_components, new_components):
        old_cp = filepairs[0][0]
        new_cp = filepairs[0][1]
        for para_lang, para_name in filepairs[0].metadata.get_parallel_texts.items():
            filepairs.append(
                (
                    corpuspath.CorpusPath(
                        old_cp.move_orig(
                            lang=para_lang,
                            genre=old_components.genre,
                            subdirs=old_components.subdirs,
                            name=para_name,
                        )
                    ),
                    corpuspath.CorpusPath(
                        new_cp.move_orig(
                            lang=para_lang,
                            genre=old_components.genre,
                            subdirs=old_components.subdirs,
                            name=para_name,
                        )
                    ),
                )
            )


def mover(oldpath, newpath):
    """Move filepairs and update metadata."""
    filepairs = compute_movenames(oldpath, newpath)
    for filepair in filepairs:
        move_corpuspath(old_corpuspath=filepair[0], new_corpuspath=filepair[1])

    update_metadata(filepairs)


def mover_parse_args():
    """Parse the commandline options.

    Returns:
        a list of arguments as parsed by argparse.Argumentparser.
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
            mover(oldpath, namechanger.compute_new_basename(newpath))
        except UserWarning as e:
            print("Can not move file:", str(e), file=sys.stderr)


def remove_metadata(remove_path):
    """Remove parallel info about remove_path."""
    for para_lang, para_name in remove_path.metadata.get_parallel_texts().items():
        para_path = corpuspath.CorpusPath(
            remove_path.move_orig(
                lang=para_lang,
                genre=remove_path.pathcomponents.genre,
                subdirs=remove_path.pathcomponents.subdirs,
                name=para_name,
            )
        )
        para_path.metadata.set_parallel_text(
            language=remove_path.pathcomponents.lang, location=""
        )
        para_path.metadata.write_file()
        parallel_vcs = versioncontrol.vcs(para_path.orig_corpus_dir)
        parallel_vcs.add(para_path.xsl)


def remover_parse_args():
    """Parse the commandline options.

    Returns:
        a list of arguments as parsed by argparse.Argumentparser.
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
        old_corpuspath = corpuspath.CorpusPath(args.oldpath)
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
