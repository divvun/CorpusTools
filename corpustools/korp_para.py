# -*- coding:utf-8 -*-
import argparse
import multiprocessing
import os
import re

from lxml import etree

from corpustools import argparse_version, corpuspath, korp_mono, modes, util

LANGS_RE = re.compile("/(\w+)2(\w+)/")


def append_files(folder_paths):
    return (
        os.path.join(root, file)
        for folder_path in folder_paths
        for root, _, files in os.walk(folder_path)
        for file in files
        if file.endswith(".tmx")
    )


def process_in_parallel(files_list):
    """Process file in parallel."""

    pool_size = multiprocessing.cpu_count() * 2
    pool = multiprocessing.Pool(processes=pool_size)
    pool.map(process_file, files_list)
    pool.close()  # no more tasks
    pool.join()  # wrap up current tasks
    return


def process_serially(files_list):
    for file_ in files_list:
        print(f"Converting: {file_}")
        process_file(file_)


def handle_header(header, file_name):
    c = corpuspath.CorpusPath(file_name)
    c.pathcomponents.genre
    genre = etree.Element("genre")
    genre.text = c.pathcomponents.genre
    header.insert(1, genre)


def make_analysis_element(seg, pipeline, lang):
    analysis = pipeline.run(seg.text.encode("utf8"))

    analysis_element = etree.Element("analysis")
    analysis_element.text = (
        "\n".join(korp_mono.make_sentences(korp_mono.valid_sentences(analysis), lang))
        + "\n"
    )

    return analysis_element


def process_file(tmx_file):
    print("... processing", str(tmx_file))
    langs = LANGS_RE.search(tmx_file).groups()

    tree = etree.parse(tmx_file)
    f_root = tree.getroot()
    handle_header(f_root.find(".//header"), tmx_file)
    for lang in langs:
        add_analysis_elements(tree, lang)
    write_file(tmx_file, tree)


def make_pipeline(lang):
    try:
        pipeline = modes.Pipeline("hfst", lang)
        pipeline.sanity_check()
    except util.ArgumentError:
        pipeline = modes.Pipeline("hfst_no_korp", lang)
        pipeline.sanity_check()
    finally:
        return pipeline


def add_analysis_elements(tree, lang):
    pipeline = make_pipeline(lang)

    for tuv in tree.xpath(
        './/tuv[@xml:lang="' + lang + '"]',
        namespaces={"xml": "http://www.w3.org/XML/1998/namespace"},
    ):
        tuv.insert(1, make_analysis_element(tuv.find("seg"), pipeline, lang))


def write_file(tmx_file, tree):
    korp_tmx_file = tmx_file.replace("/tmx", "/korp_tmx")
    with util.ignored(OSError):
        os.makedirs(os.path.dirname(korp_tmx_file))

    print("DONE. Wrote", korp_tmx_file, "\n\n")
    with open(korp_tmx_file, "wb") as done_stream:
        done_stream.write(etree.tostring(tree, xml_declaration=True, encoding="utf-8"))


def parse_options():
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Prepare tmx files for use in Korp.",
    )

    parser.add_argument(
        "--serial",
        action="store_true",
        help="When this argument is used files will be converted one by one.",
    )
    parser.add_argument("in_dirs", nargs="+", help="the tmx directories")

    return parser.parse_args()


def main():
    args = parse_options()
    if args.serial:
        process_serially(append_files(args.in_dirs))
    else:
        process_in_parallel(append_files(args.in_dirs))
