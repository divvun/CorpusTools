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


def process_file(f, lang, genre_str, done_dir_path):
    pipeline = modes.Pipeline("hfst", lang)
    namespaces = {"xml": "http://www.w3.org/XML/1998/namespace"}

    print("... processing ", str(f))
    print("/".join(f.split("/")))
    root = "/".join(f.split("/")[:-1])
    print("root=", root)

    tree = ET.parse(f)
    f_root = tree.getroot()

    header = f_root.find(".//header")

    genre = ET.Element("genre")
    if genre_str:
        genre.text = genre_str
        header.insert(1, genre)
    tuvs = tree.xpath('.//tuv[@xml:lang="' + lang + '"]', namespaces=namespaces)
    for tuv in tuvs:
        seg = tuv.find("seg")
        out = pipeline.run(seg.text.encode("utf8"))
        c_analysis = ""
        current_analysis = filter(None, out.split('\n"<'))
        for current_cohort in current_analysis:
            cc_list = current_cohort.split("\n\t")

            wform = cc_list[0]
            wform = wform.strip()
            if wform.startswith('"<'):
                wform = wform[2:]
            if wform.endswith('>"'):
                wform = wform[:-2]
            wform = wform.replace(" ", "_")

            cc_list.pop(0)
            sccl = sorted(cc_list)
            l_a = sccl[0]

            lemma = l_a.partition('" ')[0]
            lemma = lemma.strip()
            lemma = lemma.replace("#", "")
            lemma = lemma.replace(" ", "_")
            if lemma.startswith('"'):
                lemma = lemma[1:]

            analysis = l_a.partition('" ')[2]
            p_analysis = l_a.partition('" ')[2]
            analysis = analysis.partition("@")[0]
            analysis = analysis.replace("Err/Orth", "")
            analysis = analysis.replace(" <" + lang + ">", "")
            analysis = analysis.replace(" <vdic>", "")
            analysis = analysis.replace(" Sem/Date", "")
            analysis = analysis.replace(" Sem/Org", "")
            analysis = analysis.replace(" Sem/Sur", "")
            analysis = analysis.replace(" Sem/Fem", "")
            analysis = analysis.replace(" Sem/Mal", "")
            analysis = analysis.replace(" Sem/Plc", "")
            analysis = analysis.replace(" Sem/Obj", "")
            analysis = analysis.replace(" Sem/Adr", "")
            analysis = analysis.replace("Sem/Adr ", "")
            analysis = analysis.replace(" Sem/Year", "")
            analysis = analysis.replace(" IV", "")
            analysis = analysis.replace(" TV", "")
            analysis = analysis.replace("v1 ", "")
            analysis = analysis.replace("v2 ", "")
            analysis = analysis.replace("Hom1 ", "")
            analysis = analysis.replace("Hom2 ", "")
            analysis = analysis.replace("/", "_")
            if analysis.startswith("Arab Num"):
                analysis = analysis.replace("Arab Num", "Num Arab")
            analysis = analysis.strip()
            if "?" in analysis:
                analysis = "___"
            analysis = analysis.strip()
            analysis = analysis.replace("  ", " ")
            analysis = analysis.replace(" ", ".")
            pos = analysis.partition(".")[0]

            formated_line = wform + "\t" + lemma + "\t" + pos + "\t" + analysis
            c_analysis = c_analysis + "\n" + formated_line

        analysis = ET.Element("analysis")
        analysis.text = c_analysis + "\n"
        tuv.insert(1, analysis)

    done_path = os.path.join(done_dir_path, str(f.split("/")[-1]))
    print("DONE. Wrote", done_path, "\n\n")
    with open(done_path, "wb") as done_stream:
        done_stream.write(ET.tostring(tree, xml_declaration=True, encoding="utf-8"))


if __name__ == "__main__":
    main()
