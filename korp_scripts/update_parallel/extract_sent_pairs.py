# -*- coding:utf-8 -*-
import re, os, errno, cgi, json, lxml
import sys, codecs, locale, getopt
from lxml.etree import ElementTree as ET
from lxml.etree import Element, SubElement, XMLParser
from subprocess import Popen, PIPE
from operator import itemgetter
from lxml.etree import parse
from importlib import reload
from collections import defaultdict

def main():
    lang = sys.argv[1]
    gr = sys.argv[2]
    lang_pair = sys.argv[3]
    #plang = sys.argv[3]
    date_stamp = sys.argv[4]
    in_dir = sys.argv[5]

    out_dir = lang_pair + "_" + date_stamp + "_out"
    out_file = lang_pair + "_" + gr + "_" + date_stamp + "-" + lang + ".vrt"
    corpus_id = lang_pair + "_" + gr + "_" + date_stamp + "-" + lang

    i = 1
    j = 1

    f_sl = open(out_file,"a+")

    cwd = os.getcwd()
    out_dir_path = os.path.join(cwd, out_dir)

    out_tree = Element("corpus")
    out_tree.set("id", corpus_id)

    if not os.path.exists(out_dir_path):
        os.makedirs(out_dir_path)

    for root, dirs, files in os.walk(in_dir): # Walk directory tree
        for f in files:
            if f.endswith("tmx"):
                print("... processing ", str(f))
                tree = parse(os.path.join(root,f))
                f_sl_root = tree.getroot()
                f_title = f_sl_root.find(".//prop")

                out_text = SubElement(out_tree, "text")
                text_id = "t" + str(j)
                out_text.set("id", text_id)
                out_text.set("title", f_title.text)
                out_text.set("lang", lang)
                out_text.set("gt_domain", gr)

                sentences = f_sl_root.findall('.//tuv[@lang="{value}"]/analysis'.format(value=lang))

                for sentence in sentences:
                    out_link = SubElement(out_text, "link")
                    link_id = "l" + str(i)
                    sentence_id = "l" + str(i) + "s" + str(i)
                    out_link.set('id', link_id)
                    out_sentence = SubElement(out_link, "sentence")
                    out_sentence.set('id', sentence_id)
                    out_sentence.text = sentence.text
                    i += 1

            j += 1

            ET(out_tree).write(out_dir_path+"/"+out_file, encoding="UTF-8", pretty_print=True)


    f_sl.close()

if __name__ == "__main__":
    reload(sys)
    main()
