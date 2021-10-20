# -*- coding:utf-8 -*-
import argparse
import multiprocessing
import os
from functools import partial

import lxml.etree as ET

from corpustools import modes


def append_files(folder_path):
    return (
        os.path.join(root, file)
        for root, _, files in os.walk(folder_path)
        for file in files
        if file.endswith(".tmx")
    )


def make_done_dir(genre_str):
    done_dir = "done_" + genre_str
    cwd = os.getcwd()
    done_dir_path = os.path.join(cwd, done_dir)

    if not os.path.exists(done_dir_path):
        os.mkdir(done_dir_path)

    return done_dir_path


def process_in_parallel(files_list, args):
    """Process file in parallel."""

    pool_size = multiprocessing.cpu_count() * 2
    pool = multiprocessing.Pool(processes=pool_size)
    pool.map(
        partial(
            process_file,
            lang=args.lang,
            genre_str=args.genre,
            done_dir_path=make_done_dir(args.genre),
        ),
        files_list,
    )
    pool.close()  # no more tasks
    pool.join()  # wrap up current tasks
    return


def parse_options():
    parser = argparse.ArgumentParser(description="Prepare tmx files for use in Korp.")

    parser.add_argument("lang", help="language of the files to process")
    parser.add_argument("in_dir", help="the directory of the analysed files")
    parser.add_argument("genre", help="optional genre", nargs="?", default="")

    return parser.parse_args()


def main():
    args = parse_options()
    files_list = append_files(args.in_dir)
    process_in_parallel(files_list, args)


def handle_header(header, genre_str):
    genre = ET.Element("genre")
    if genre_str:
        genre.text = genre_str
        header.insert(1, genre)


def make_analysis_element(tuv, pipeline, lang):
    seg = tuv.find("seg")
    out = pipeline.run(seg.text.encode("utf8"))

    analysis = ET.Element("analysis")
    analysis.text = (
        "\n".join(
            [
                make_formatted_line(lang, current_cohort)
                for current_cohort in filter(None, out.split('\n"<'))
            ]
        )
        + "\n"
    )

    return analysis


def process_file(f, lang, genre_str, done_dir_path):
    print("... processing", str(f))

    tree = ET.parse(f)
    f_root = tree.getroot()

    handle_header(f_root.find(".//header"), genre_str)
    add_analysis_elements(tree, modes.Pipeline("hfst", lang))
    write_file(done_dir_path, f, tree)


def add_analysis_elements(tree, pipeline):
    for tuv in tree.xpath(
        './/tuv[@xml:lang="' + lang + '"]',
        namespaces={"xml": "http://www.w3.org/XML/1998/namespace"},
    ):
        tuv.insert(1, make_analysis_element(tuv, pipeline, lang))


def write_file(done_dir_path, f, tree):
    done_path = os.path.join(done_dir_path, str(f.split("/")[-1]))
    print("DONE. Wrote", done_path, "\n\n")
    with open(done_path, "wb") as done_stream:
        done_stream.write(ET.tostring(tree, xml_declaration=True, encoding="utf-8"))


def make_formatted_line(lang, current_cohort):
    wform, lemma, analysis, pos = make_line_parts(lang, current_cohort)
    return wform + "\t" + lemma + "\t" + pos + "\t" + analysis


def make_line_parts(lang, current_cohort):
    (wform, *cc_list) = current_cohort.split("\n\t")

    wform = make_wordform(wform)
    l_a = sorted(cc_list)[0]
    lemma = make_lemma(l_a)
    analysis = make_analysis(lang, l_a)
    pos = analysis.partition(".")[0]

    return wform, lemma, analysis, pos


def make_analysis(lang, l_a):
    analysis = l_a.partition('" ')[2].partition("@")[0]

    if "?" in analysis:
        return "___"

    for (unwanted, replacement) in [
        ("Err/Orth", ""),
        (" <" + lang + ">", ""),
        (" <vdic>", ""),
        (" Sem/Date", ""),
        (" Sem/Org", ""),
        (" Sem/Sur", ""),
        (" Sem/Fem", ""),
        (" Sem/Mal", ""),
        (" Sem/Plc", ""),
        (" Sem/Obj", ""),
        (" Sem/Adr", ""),
        ("Sem/Adr ", ""),
        (" Sem/Year", ""),
        (" IV", ""),
        (" TV", ""),
        ("v1 ", ""),
        ("v2 ", ""),
        ("Hom1 ", ""),
        ("Hom2 ", ""),
    ]:
        analysis = analysis.replace(unwanted, replacement)
    if analysis.startswith("Arab Num"):
        analysis = analysis.replace("Arab Num", "Num Arab")
    analysis = analysis.strip()
    analysis = analysis.replace("  ", " ")
    analysis = analysis.replace(" ", ".")

    return analysis


def make_lemma(l_a):
    lemma = l_a.partition('" ')[0].strip()
    lemma = lemma.replace("#", "")
    lemma = lemma.replace(" ", "_")
    if lemma.startswith('"'):
        lemma = lemma[1:]

    return lemma


def make_wordform(wform):
    wform = wform.strip()
    if wform.startswith('"<'):
        wform = wform[2:]
    if wform.endswith('>"'):
        wform = wform[:-2]
    wform = wform.replace(" ", "_")

    return wform


if __name__ == "__main__":
    main()
