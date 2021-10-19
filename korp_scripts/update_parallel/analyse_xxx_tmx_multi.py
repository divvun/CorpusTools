# -*- coding:utf-8 -*-
import cgi
import codecs
import errno
import getopt
import json
import locale
import multiprocessing
import os
import re
import sys
import xml
import lxml.etree as ET
from collections import defaultdict
from importlib import reload
from operator import itemgetter
from subprocess import PIPE, Popen
from xml.dom.minidom import parse, parseString
from corpustools import modes


def append_files(files_list, folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".tmx"):
                files_list.append(os.path.join(root, file))


def process_in_parallel(files_list):
    """Process file in parallel."""
    pool_size = multiprocessing.cpu_count() * 2
    pool = multiprocessing.Pool(processes=pool_size)
    pool.map(process_file, files_list)
    pool.close()  # no more tasks
    pool.join()  # wrap up current tasks
    return


def main():
    # The script expects 2 (and 1 optional) parameters:
    # language to analyse, input_directory (and genre)
    files_list = []
    in_dir = sys.argv[2]

    append_files(files_list, in_dir)
    process_in_parallel(files_list)


def process_file(f):
    lang = sys.argv[1]
    in_dir = sys.argv[2]
    if len(sys.argv) == 4:
        genre_str = sys.argv[3]
    else:
        genre_str = ""
    hfst_pipeline = modes.Pipeline("hfst", lang)
    out_dir = "out_" + lang + "_" + in_dir
    done_dir = "done_" + genre_str
    err_dir = "error_" + genre_str
    cwd = os.getcwd()
    out_dir_path = os.path.join(cwd, out_dir)
    done_dir_path = os.path.join(cwd, done_dir)
    err_dir_path = os.path.join(cwd, err_dir)

    if not os.path.exists(out_dir_path):
        os.makedirs(out_dir_path)
    if not os.path.exists(done_dir_path):
        os.mkdir(done_dir_path)
    if not os.path.exists(err_dir_path):
        os.mkdir(err_dir_path)

    debug_fst = False

    namespaces = {"xml": "http://www.w3.org/XML/1998/namespace"}

    print("... processing ", str(f))
    print("/".join(f.split("/")))
    root = "/".join(f.split("/")[:-1])
    print("root=", root)

    # tree = ET.parse(os.path.join(root,f))
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
        seg_txt = seg.text
        # print('... seg ', str(seg_txt))
        out = hfst_pipeline.run(seg_txt.encode("utf8"))
        c_analysis = ""
        current_analysis = filter(None, out.split('\n"<'))
        for current_cohort in current_analysis:
            cc_list = current_cohort.split("\n\t")
            # print("cc_list=", cc_list)

            wform = cc_list[0]
            wform = wform.strip()
            if wform.startswith('"<'):
                wform = wform[2:]
            if wform.endswith('>"'):
                wform = wform[:-2]
            wform = wform.replace(" ", "_")
            # print("wform=", wform)

            cc_list.pop(0)
            # print("cc_list 2=", cc_list)
            sccl = sorted(cc_list)
            # print("sccl=", sccl)
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
