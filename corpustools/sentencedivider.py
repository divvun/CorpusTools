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
#   http://divvun.no & http://giellatekno.uit.no
#
"""Classes and functions to sentence align two files."""


from pathlib import Path

from corpustools import ccat
from corpustools.corpuspath import CorpusPath
from corpustools.util import ArgumentError, lang_resource_dirs, run_external_command

STOPS = [";", "!", "?", ".", "..", "...", "¶", "…"]


def get_tokeniser(lang: str) -> Path:
    """Check if resources needed by modes exists.

    Args:
        lang: the language that modes is asked to serve.

    Returns:
        A path to the zpipe file.

    Raises:
        utils.ArgumentError: if no resources are found.
    """
    for lang_dir in lang_resource_dirs(lang):
        full_path = lang_dir / "tokeniser-disamb-gt-desc.pmhfst"
        if full_path.exists():
            return full_path

    raise (ArgumentError(f"ERROR: no tokeniser for {lang}"))


def tokenise(text: str, lang: str) -> str:
    """Turn a string into a list of tokens.

    Args:
        text: the text to be tokenised
        lang: the language of the text

    Returns:
        The tokenised text, one token per line.
    """

    return run_external_command(
        command=f"hfst-tokenise --print-all {get_tokeniser(lang)}".split(),
        instring=text,
    )


def make_sentences(tokenised_output):
    """Turn ccat output into cleaned up sentences.

    Args:
        tokenised_output (str): plain text output of ccat.

    Yields:
        (str): a cleaned up sentence
    """

    token_buffer = []
    for token in tokenised_output.split("\n"):
        if token != "¶":
            token_buffer.append(token)
        if token.strip() in STOPS:
            yield "".join(token_buffer).strip()
            token_buffer[:] = []
    if token_buffer:
        yield "".join(token_buffer).strip()


def make_valid_sentences(corpus_path: CorpusPath) -> list[str]:
    """Turn ccat output into full sentences.

    Args:
        corpus_path (CorpusPath): The path to the corpus file.

    Returns:
        The ccat output has been turned into a list of full sentences.
    """
    return [
        sentence
        for sentence in make_sentences(
            tokenised_output=run_external_command(
                command="hfst-tokenise --print-all "
                f"{get_tokeniser(corpus_path.lang)}".split(),
                instring=ccat.ccatter(corpus_path),
            )
        )
        if sentence.strip()
    ]
