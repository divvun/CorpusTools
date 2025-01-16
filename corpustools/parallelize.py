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
#   Copyright © 2011-2023 The University of Tromsø &
#                         the Norwegian Sámi Parliament
#   http://giellatekno.uit.no & http://divvun.no
#
"""Classes and functions to sentence align two files."""

import argparse
import os
import re
import subprocess
from pathlib import Path

from lxml import etree

from corpustools import (
    argparse_version,
    corpuspath,
    generate_anchor_list,
    sentencedivider,
    tmx,
    util,
)

HERE = os.path.dirname(__file__)

SREGEX = re.compile('<s id="[^ ]*">')
DICTS = {}


def make_tca2_input(xmlfile):
    """Make sentence xml that tca2 can use.

    Args:
        xmlfile (str): name of the xmlfile

    Returns:
        (lxml.etree.Element): an xml element containing all sentences.
    """
    document = etree.Element("document")

    divider = sentencedivider.SentenceDivider(xmlfile.lang)
    for index, sentence in enumerate(
        divider.make_valid_sentences(sentencedivider.to_plain_text(xmlfile))
    ):
        s_elem = etree.Element("s")
        s_elem.attrib["id"] = str(index)
        s_elem.text = sentence
        document.append(s_elem)

    return document


def divide_p_into_sentences(filepair):
    """Tokenize the text in the given file and reassemble it again."""
    for pfile in filepair:
        pfile.tca2_input.parent.mkdir(parents=True, exist_ok=True)
        pfile.tca2_input.write_bytes(
            etree.tostring(
                make_tca2_input(pfile),
                pretty_print=True,
                encoding="utf8",
                xml_declaration=True,
            )
        )


def run_command(command):
    """Run a parallelize command and return its output."""
    subp = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (output, error) = subp.communicate()

    return subp.returncode, output, error


def remove_s_tag(line):
    """Remove the s tags that tca2 has added."""
    line = line.replace("</s>", "")
    line = SREGEX.sub("", line)
    return line


def setup_anchors(lang1, lang2):
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


def tca2_align(file1, file2, anchor_filename):
    """Parallelize two files using tca2.

    Args:
        file1 (CorpusPath): file1
        file2 (CorpusPath): file2
        anchor_filename (str): filename

    Returns:
        (list[str]): the sentence aligned output of tca2
    """
    divide_p_into_sentences([file1, file2])

    tca2_jar = os.path.join(HERE, "tca2/dist/lib/alignment.jar")
    command = (
        f"java -Xms512m -Xmx1024m -jar {tca2_jar} -cli-plain -anchor={anchor_filename} "
        f"-in1={file1.tca2_input} -in2={file2.tca2_input}"
    )

    (returncode, output, error) = run_command(command.split())

    if returncode != 0:
        raise UserWarning(
            f"Could not parallelize {file1.converted} and {file2.converted} into "
            f"sentences\n{output.decode('utf8')}\n\n{error.decode('utf8')}\n"
        )

    return [
        [remove_s_tag(line) for line in sentpath.read_text().split("\n")]
        for sentpath in [
            file1.tca2_output,
            file2.tca2_output,
        ]
    ]


def make_dict(lang1, lang2):
    name = Path(f"/tmp/anchor-{lang1}-{lang2}.txt")
    gal = setup_anchors(lang1, lang2)
    if gal is not None:
        gal.generate_file(name.as_posix())
    else:
        name.write_text("fake1 / fake2\n")
    return name.as_posix()


def parallelise_file(source_lang_file, para_lang_file, dictionary):
    """Align sentences of two parallel files."""
    aligned_sentences = tca2_align(source_lang_file, para_lang_file, dictionary)
    if aligned_sentences:
        tmxfile = source_lang_file.tmx(para_lang_file.lang)
        tmxfile.parent.mkdir(parents=True, exist_ok=True)
        source_lang_file.tmx(para_lang_file.lang).write_bytes(
            etree.tostring(
                tmx.make_tmx(
                    source_lang_file.filepath.name,
                    source_lang_file.lang,
                    para_lang_file.lang,
                    aligned_sentences,
                ),
                pretty_print=True,
                encoding="utf8",
            )
        )
        print(f"Made {source_lang_file.tmx(para_lang_file.lang)}")


def is_translated_from_lang2(path, lang2):
    """Find out if the given doc is translated from lang2."""
    translated_from = path.metadata.get_variable("translated_from")

    if translated_from is not None:
        return translated_from == lang2
    else:
        return False


def get_dictionary(para_path, source_path):
    if DICTS.get(f"{source_path.lang}{para_path.lang}") is None:
        DICTS[f"{source_path.lang}{para_path.lang}"] = make_dict(
            source_path.lang, para_path.lang
        )

    return DICTS.get(f"{source_path.lang}{para_path.lang}")


def get_filepair(orig_path, para_lang):
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
                dictionary=(
                    get_dictionary(para_path, source_path)
                    if args.dict is None
                    else args.dict
                ),
            )
        except (OSError, UserWarning) as error:
            print(str(error))
        except util.ArgumentError as error:
            raise SystemExit(
                f"{error}\nMore info here: "
                "https://giellalt.github.io/CorpusTools/scripts/parallelize/#compile-dependencies",
            )
