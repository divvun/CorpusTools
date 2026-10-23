# the file analyse_xxx_tmx.py is not used

# scriptet corpustools/korp_para lager ei mappe tmx
#   undermapper: språk (3bokstavs iso kode) - for hvert språk dette språket "går til"
#     under der igjen: kategori (mappe) / underkateogri (...osv) / FIL.tmx
"""Compile and build data/ and registry/ folders for parallel corpora."""

import argparse
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

from corpustools.compile_cwb_mono import Corpus
from corpustools.modes import Pipeline


def analyse():
    pass  # hfst_lookup()


def analyse_tmx(corpus):
    pipeline = Pipeline("hfst", lang)

    for f in corpus.iter_files(suffix="tmx"):
        tree = ET.parse(f)
        root = tree.getroot()
        header = root.find(".//header")

        tuvs = root.findall(f'.//tuv[@lang="{lang}"]')
        for tuv in tuvs:
            # only one <seg> in each <tuv>?
            seg = tuv.find("seg")

            analysis = pipeline.run(seg.text.encode("utf"), corpus.lang)
            analysis = analysis.split('\n"<')
            lines = (line for line in analysis if line)
            # for cohort in lines:
            # cc_list = cohort.split("\n\t")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, default=".", required=False)
    parser.add_argument("--para-lang", nargs="*")

    parser.add_argument(
        "--date",
        type=date.fromisoformat,
        default=date.today(),
        help=(
            "Date of compilation, in iso format (YYYYMMDD). This should "
            "be the date the corpus was analysed. Defaults to todays date if "
            "not given"
        ),
    )
    parser.add_argument(
        "--cwb-binaries-dir",
        help="directory where the cwb binaries (such as cwb-encode, etc) "
        "are located. Only necessary if the `cwb-xxx` commands are not "
        "available on the system path",
    )

    args = parser.parse_args()
    print(args)

    try:
        args.corpus = Corpus.from_path(args.corpus)
    except Exception as e:
        parser.error(f"argument `corpus`: {e}\n")

    return args


def main():
    args = parse_args()

    analyse_tmx(args.corpus)
    # analyse_xxx_tmx() ??
    # extract_sentence_pairs()
    # encode_gt_corpus(lang)
    # encode_gt_corpus(parallel_lang)
    # align_files()

    raise NotImplementedError("TO BE DONE")
