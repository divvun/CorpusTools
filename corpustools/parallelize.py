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
#   Copyright © 2011-2025 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Classes and functions to sentence align two files."""

import argparse
import os
from pathlib import Path

from lxml import etree
from python_tca2.alignmentmodel import AlignmentModel
from python_tca2.anchorwordlist import AnchorWordList
from python_tca2.tmx import make_tmx

from corpustools import (
    argparse_version,
    corpuspath,
    generate_anchor_list,
    sentencedivider,
    util,
)

HERE = os.path.dirname(__file__)

DICTS: dict[str, str] = {}


def setup_anchors(
    lang1: str, lang2: str
) -> generate_anchor_list.GenerateAnchorList | None:
    """Setup anchor file.

    Args:
        lang1 (str): language 1
        lang2 (str): language 2

    Returns:
        (generate_anchor_list.GenerateAnchorList): The anchor list
    """
    path1 = os.path.join(
        os.environ["GTHOME"],
        f"gt/common/src/anchor-{lang1}-{lang2}.txt",
    )
    if os.path.exists(path1):
        return generate_anchor_list.GenerateAnchorList(
            lang1, lang2, [lang1, lang2], path1
        )

    path2 = os.path.join(
        os.environ["GTHOME"],
        f"gt/common/src/anchor-{lang2}-{lang1}.txt",
    )
    if os.path.exists(path2):
        return generate_anchor_list.GenerateAnchorList(
            lang1, lang2, [lang2, lang1], path2
        )

    return None


def make_dict(lang1: str, lang2: str) -> str:
    name = Path(f"/tmp/anchor-{lang1}-{lang2}.txt")
    gal = setup_anchors(lang1, lang2)
    if gal is not None:
        gal.generate_file(name.as_posix())
    else:
        name.write_text("fake1 / fake2\n")
    return name.as_posix()


def parallelise_file(
    source_lang_file: corpuspath.CorpusPath,
    para_lang_file: corpuspath.CorpusPath,
    anchor_file: str | None = None,
):
    """Align sentences of two parallel files."""
    anchor_word_list = AnchorWordList()
    if anchor_file is not None:
        anchor_word_list.load_from_file(anchor_file)

    aligner = AlignmentModel(
        sentences_tuple=(
            sentencedivider.make_valid_sentences(source_lang_file),
            sentencedivider.make_valid_sentences(para_lang_file),
        ),
        anchor_word_list=anchor_word_list,
    )

    aligned = aligner.suggest_without_gui()

    aligned_sentences = aligned.non_empty_pairs()

    tmx_result = make_tmx(
        file1_name=source_lang_file.orig.name,
        language_pair=(source_lang_file.lang, para_lang_file.lang),
        aligned_text_pairs=aligned_sentences,
    )
    tmx_path = source_lang_file.tmx(para_lang_file.lang)
    tmx_path.write_bytes(
        etree.tostring(
            tmx_result,
            pretty_print=True,
            encoding="utf-8",
        )
    )
    print(f"TMX file created: {tmx_path}")


def is_translated_from_lang2(path: corpuspath.CorpusPath, lang2: str) -> bool:
    """Find out if the given doc is translated from lang2."""
    translated_from = path.metadata.get_variable("translated_from")

    if translated_from is None:
        return False

    return translated_from == lang2


def get_dictionary(lang1: str, lang2: str) -> str:
    if DICTS.get(f"{lang1}{lang2}") is None:
        DICTS[f"{lang1}{lang2}"] = make_dict(lang1, lang2)

    return DICTS[f"{lang1}{lang2}"]


def get_filepair(
    orig_path: corpuspath.CorpusPath, para_lang: str
) -> tuple[corpuspath.CorpusPath, corpuspath.CorpusPath]:
    if is_translated_from_lang2(orig_path, para_lang):
        para_path = orig_path
        source_path = corpuspath.make_corpus_path(para_path.parallel(para_path.lang))
    else:
        source_path = orig_path
        para_path = corpuspath.make_corpus_path(source_path.parallel(para_lang))

    return para_path, source_path


def parse_options():
    """Parse the commandline options.

    Returns:
        (argparse.Namespace): the parsed commandline arguments
    """
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser], description="Sentence align file pairs."
    )

    parser.add_argument(
        "sources",
        nargs="+",
        help="Files or directories to search for " "parallelisable files",
    )
    parser.add_argument(
        "-d",
        "--dict",
        default=None,
        help="Use a different bilingual seed dictionary. "
        "Must have two columns, with input_file language "
        "first, and --parallel_language second, separated "
        "by `/'. By default, "
        "$GTHOME/gt/common/src/anchor.txt is used, but this "
        "file only supports pairings between "
        "sme/sma/smj/fin/eng/nob. ",
    )
    parser.add_argument(
        "-l2",
        "--lang2",
        help="Indicate which language the given file should be parallelised with",
        required=True,
    )

    args = parser.parse_args()
    return args


def main():
    """Parallelise files."""
    args = parse_options()

    for path in corpuspath.collect_files(args.sources, suffix=".xml"):
        orig_corpuspath = corpuspath.make_corpus_path(path)

        if orig_corpuspath.lang == args.lang2:
            raise SystemExit(
                "Error: change the value of the -l2 option.\n"
                f"The -l2 value ({args.lang2}) cannot be the same as the "
                f"language as the source documents ({orig_corpuspath.lang})"
            )

        try:
            para_path, source_path = get_filepair(orig_corpuspath, args.lang2)
        except TypeError:
            continue

        try:
            parallelise_file(
                source_path,
                para_path,
                anchor_file=(
                    get_dictionary(lang1=source_path.lang, lang2=para_path.lang)
                    if args.dict is None
                    else args.dict
                ),
            )
        except (OSError, UserWarning) as error:
            print(str(error))
        except util.ArgumentError as error:
            raise SystemExit(
                f"{error}\nMore info here: "
                "https://divvun.github.io/CorpusTools/scripts/parallelize/#compile-dependencies",
            ) from error
