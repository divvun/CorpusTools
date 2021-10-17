#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import inspect
import logging
import multiprocessing
import os
import re
import sys
import xml.etree.ElementTree as ET
from imp import reload
from subprocess import PIPE, Popen

DOMAIN_MAPPING = {
    "admin": "administration",
    "bible": "bible",
    "facta": "facts",
    "ficti": "fiction",
    "literature": "fiction",
    "law": "law",
    "laws": "law",
    "news": "news",
    "science": "science",
    "blogs": "blog",
    "wikipedia": "wikipedia",
    "": "",
}
DEPREL_MAPPING = {
    ">A": "→A",
    ">ADVL": "→ADVL",
    ">CC": "→CC",
    ">N": "→N",
    ">Num": "→Num",
    ">P": "→P",
    ">Pron": "→Pron",
    "<ADVL": "←ADVL",
    "<OBJ": "←OBJ",
    "<OPRED": "←OPRED",
    "<PPRED": "←PPRED",
    "<SPRED": "←SPRED",
    "<SUBJ": "←SUBJ",
    "+FMAINV": "+FMAINV",
    "-F<ADVL": "-F←ADVL",
    "-F<OBJ": "-F←OBJ",
    "-F<OPRED": "-F←OPRED",
    "-F<SUBJ": "-F←SUBJ",
    "-FADVL>": "-FADVL→",
    "-FMAINV": "-FMAINV",
    "-FOBJ>": "-FOBJ→",
    "-FSUBJ>": "-FSUBJ→",
    "A<": "A←",
    "ADVL": "ADVL",
    "ADVL>": "ADVL→",
    "ADVL>CS": "ADVL→CS",
    "ADVL<": "ADVL←",
    "APP-ADVL<": "APP-ADVL←",
    "APP-N<": "APP-N←",
    "APP-Pron<": "APP-Pron←",
    "CNP": "CNP",
    "COMP-CS<": "COMP-CS←",
    "CVP": "CVP",
    "FAUX": "FAUX",
    "-FAUX": "-FAUX",
    "-FAUXV": "-FAUXV",
    "FMV": "FMV",
    "FMVdic": "FMVdic",
    "FS-<ADVL": "FS-←ADVL",
    "FS-<SUBJ": "FS-←SUBJ",
    "FS-ADVL>": "FS-ADVL→",
    "FS-IAUX": "FS-IAUX",
    "FS-IMV": "FS-IMV",
    "FS-N<": "FS-N←",
    "FS-N<IAUX": "FS-N←IAUX",
    "FS-N<IMV": "FS-N←IMV",
    "FS-OBJ": "FS-OBJ",
    "FS-P<": "FS-P←",
    "FS-VFIN<": "FS-VFIN←",
    "FS-STA": "FS-STA",
    "HNOUN": "HNOUN",
    "IAUX": "IAUX",
    "ICL-OBJ": "ICL-OBJ",
    "ICL-SUBJ": "ICL-SUBJ",
    "IMV": "IMV",
    "IMVdic": "IMVdic",
    "INTERJ": "INTERJ",
    "N<": "N←",
    "Num<": "Num←",
    "OBJ>": "OBJ→",
    "OPRED>": "OPRED→",
    "P<": "P←",
    "PCLE": "PCLE",
    "Pron<": "Pron←",
    "S<": "S←",
    "SPRED>": "SPRED→",
    "SPRED<OBJ": "SPRED←OBJ",
    "SUBJ>": "SUBJ→",
    "VOC": "VOC",
    "SPRED": "SPRED",
    "SUBJ": "SUBJ",
    "HAB": "HAB",
    "<P": "←P",
    "NUM<": "NUM←",
    "N>": "N→",
    "NES": "NES",
    "LOC": "LOC",
    "X": "X",
}
WORDFORM_FILTER = [
    '"< suohkanbargi>"',
    '"< suohkanbargiide>"',
    '"< suohkanbargiin>"',
    '"< suohkanbargit>"',
    '"< suohkanbáhpa>"',
    '"< suohkanbáhpain>"',
    '"< suohkanbáhpas>"',
    '"< suohkanbáhppa>"',
    '"< suohkanbáhppan>"',
    '"< suohkanbáhppavirgi>"',
    '"< suohkanbáhppavirgái>"',
    '"< suohkandoaktáris>"',
    '"< suohkandoavtterbálvalusas>"',
    '"< suohkandoavttir>"',
    '"< suohkanekonomiija>"',
    '"< suohkangirji>"',
    '"< suohkangirjji>"',
    '"< suohkanhálddahusas>"',
    '"< suohkanluottain>"',
    '"< suohkanmearka>"',
    '"< suohkanpolitihkar>"',
    '"< suohkanpolitihkarin>"',
    '"< suohkanpolitihkka>"',
    '"< suohkanpolitihkkarat>"',
    '"< suohkanpolitihkkariid>"',
    '"< suohkanpolitihkkariiguin>"',
    '"< suohkanpolitihkkariin>"',
    '"< suohkanpolitihkkár>"',
    '"< suohkanpolitihkkárat>"',
    '"< suohkanpolitihkkáriid>"',
    '"< suohkanpsykologa>"',
    '"< suohkanrádjái>"',
    '"< suohkanráji>"',
    '"< suohkanrájiid>"',
    '"< suohkanrájit>"',
    '"< suohkanstivra>"',
    '"< suohkanstivracoahkin>"',
    '"< suohkanstivralahttu>"',
    '"< suohkanstivralahtut>"',
    '"< suohkanstivraáirasat>"',
    '"< suohkanstivraáirasiid>"',
    '"< suohkanstivraáirras>"',
    '"< suohkanstivraášši>"',
    '"< suohkanstivračoahkkimis>"',
    '"< suohkanstivračoahkkin>"',
    '"< suohkanstivrii>"',
    '"< suohkanstivrra>"',
    '"< suohkanstivrraid>"',
    '"< suohkanstivrraláhttu>"',
    '"< suohkanstivrras>"',
    '"< suohkanstivrrat>"',
    '"< suohkanstivrraválga>"',
    '"< suohkanstivrraáirras>"',
    '"< suohkanstivrračoahkkima>"',
    '"< suohkanviesu>"',
    '"< suohkanviesus>"',
    '"< suohkanvissui>"',
    '"< suohkanvisteseaidnái>"',
    '"< suohkanvistti>"',
    '"< suohkanváldodoavttir>"',
    '"< suohkanválga>"',
    '"< suohkanválggaid>"',
    '"< suohkanválggaide>"',
    '"< suohkanválggain>"',
    '"< suohkanválggas>"',
    '"< suohkanválggat>"',
    '"< suohkanválgii>"',
    '"< suohkanássit>"',
    '"< suohkanšibitdoavttir>"',
    '"<.>"',
    '"<Bearj>"',
    '"<Duorast>"',
    '"<Gaskav>"',
    '"<Geassem>"',
    '"<Golggotm>"',
    '"<Guovdageainnu>"',
    '"<Guovvam>"',
    '"<Juovlam>"',
    '"<Lávv>"',
    '"<Miessem>"',
    '"<Njukčam>"',
    '"<Ođđaj>"',
    '"<Skábmam>"',
    '"<St.meld. nr>"',
    '"<St.meld>"',
    '"<bearj>"',
    '"<borgem>"',
    '"<cuoŋom>"',
    '"<duorast>"',
    '"<gaskav>"',
    '"<geassem>"',
    '"<golggotm>"',
    '"<guovvam>"',
    '"<juovlam>"',
    '"<lávv>"',
    '"<miessem>"',
    '"<njukč>"',
    '"<njukčam>"',
    '"<ot. meld>"',
    '"<ovd>"',
    '"<ođđaj>"',
    '"<ođđajagem>"',
    '"<skábmam>"',
    '"<st.meld. nr>"',
    '"<st.meld>"',
    '"<suoidnem>"',
    '"<Čakčam>"',
    '"<čakčam>"',
]


def vrt_format(elem):
    i = "\n"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i
        for elem in elem:
            vrt_format(elem)
        for child in elem:
            vrt_format(child)
    if not elem.tail or not elem.tail.strip():
        elem.tail = padding


def append_files(files_list, folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".xml"):
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
    files_list = []
    in_dir = sys.argv[1]

    append_files(files_list, in_dir)
    process_in_parallel(files_list)


def process_file(current_file):

    # for debugging purposes
    # Try printing inspect.stack() you can see current stack and pick whatever you want
    # file_name = __FILE__
    # current_line_no = inspect.stack()[0][2]
    # current_function_name = inspect.stack()[0][3]

    in_dir = sys.argv[1]
    debug_index = ""
    out_dir = "_od_" + in_dir + "_" + debug_index
    logging.basicConfig(
        filename="proc_" + in_dir + "_" + debug_index + ".log", level=logging.DEBUG
    )

    # to be adjusted as needed
    if len(sys.argv) != 3:
        print("wrong number of arguments")
        sys.exit("Error")

    cwd = os.getcwd()
    out_dir_path = os.path.join(cwd, out_dir)
    if not os.path.exists(out_dir_path):
        print("_od_ ::: " + out_dir_path)
        os.mkdir(out_dir_path)

    # parameters to be adjusted as needed
    lang = sys.argv[2]
    fst_type = "hfstol"
    debug_fst = False
    rel_fst_file = "/src/analyser-disamb-gt-desc." + fst_type
    langs_dir = "$GTLANGS/lang-"
    lookup = ""
    lookup2cg = ""
    vislcg3 = ""

    done_dir = "done_multi_" + lang
    done_dir_path = os.path.join(cwd, done_dir)
    if not os.path.exists(done_dir_path):
        os.mkdir(done_dir_path)

    if fst_type == "xfst":
        plup = Popen("which lookup", shell=True, stdout=PIPE, stderr=PIPE)
        olup, elup = plup.communicate()
        ###print("___ lookup is ",olup.decode())
    if fst_type == "hfstol":
        plup = Popen(
            "which hfst-optimised-lookup", shell=True, stdout=PIPE, stderr=PIPE
        )
        olup, elup = plup.communicate()

    if not olup.decode():
        print("No lookup found, please install it!")
        sys.exit("Error")
    lookup = olup.decode().strip()

    plup2cg = Popen("which lookup2cg", shell=True, stdout=PIPE, stderr=PIPE)
    olup2cg, elup2cg = plup2cg.communicate()

    if not olup2cg.decode():
        print("No lookup2cg found, please install it!")
        sys.exit("Error")
    lookup2cg = olup2cg.decode().strip()

    pvislcg3 = Popen("which vislcg3", shell=True, stdout=PIPE, stderr=PIPE)
    ovislcg3, evislcg3 = pvislcg3.communicate()

    if not ovislcg3.decode():
        print("No vislcg3 found, please install it!")
        sys.exit("Error")
    vislcg3 = ovislcg3.decode().strip()

    # for root, dirs, files in os.walk(in_dir): # Walk directory tree
    #    print("Input dir {0} with {1} files ...".format(root, len(files)))

    # for current_file in files:
    #    if len(files) == 0 :
    #        continue
    if current_file.endswith(".xml"):
        # print('... processing ', str(root))
        # print('... processing ', str(current_file))

        # logging.warning(str(os.path.join(root,current_file))+'\n')

        root = "/".join(current_file.split("/")[:-1])
        # print("root=", root)
        current_out_dir_path = os.path.join(out_dir_path, root)
        # current_out_dir_path = out_dir_path
        print("... processing current_out_dir_path", str(current_out_dir_path))
        if not os.path.exists(current_out_dir_path):
            os.makedirs(current_out_dir_path, exist_ok=True)
            ###print('___ processed ', str(current_out_dir_path))

        # xml_tree = ET.parse(os.path.join(root,current_file), ET.XMLParser(encoding='utf-8'))
        xml_tree = ET.parse(current_file, ET.XMLParser(encoding="utf-8"))
        # xml_tree = ET.parse(current_file, ET.XMLParser(encoding='utf-8'))
        f_root = xml_tree.getroot()
        content_el = f_root.find(".//body/dependency")
        content = content_el.text

        # attributes the a text element
        # title="Sámi_oskkuoahpahusplána"
        # lang="sme"
        # orig_lang="___"
        # gt_domain="bible"
        # first_name="___"
        # last_name="___"
        # nationality="___"
        # date="2011-01-01"
        # datefrom="20110101"
        # dateto="20110101"
        # timefrom="000000"
        # timeto="235959"

        f_title = ""
        f_genre = ""
        f_lang = ""
        f_orig_lang = ""
        f_first_name_author = ""
        f_last_name_author = ""
        f_nationality = ""
        year_value = ""
        f_date = "0000-00-00"
        f_datefrom = "00000000"
        f_dateto = "00000000"
        f_timefrom = "000000"
        f_timeto = "235959"

        f_title = (
            f_root.find(".//header/title").text.strip()
            if f_root.find(".//header/title").text
            else ""
        )
        f_genre = (
            f_root.find(".//header/genre").attrib.get("code")
            if f_root.find(".//header/genre").attrib.get("code")
            else ""
        )

        if f_root.find(".//header/author/person") is not None:
            f_first_name_author = f_root.find(".//header/author/person").attrib.get(
                "firstname"
            )
            f_last_name_author = f_root.find(".//header/author/person").attrib.get(
                "lastname"
            )
            f_nationality = f_root.find(".//header/author/person").attrib.get(
                "nationality"
            )

        f_lang = f_root.get("{http://www.w3.org/XML/1998/namespace}lang")

        if f_root.find(".//header/translated_from") is not None:
            f_orig_lang = f_root.find(".//header/translated_from").attrib.get(
                "{http://www.w3.org/XML/1998/namespace}lang"
            )

        # no element year in the header
        if f_root.find(".//header/year") is None:
            f_date = "0000-00-00"
            f_datefrom = "00000000"
            f_dateto = "00000000"
        else:
            year_value = str(f_root.find(".//header/year").text)
            # <year>unknown</year>
            if year_value == "unknown":
                f_date = "0000-00-00"
                f_datefrom = "00000000"
                f_dateto = "00000000"
            # <year>2018</year>
            elif re.match(r"^[0-9]{4,4}$", year_value):
                f_date = year_value + "-01-01"
                f_datefrom = year_value + "0101"
                f_dateto = year_value + "0101"
            # <year>2011-2012</year>
            elif re.match(r"^([0-9]{4,4})\-([0-9]{4,4})$", year_value):
                first, last = re.split("\-", year_value)
                f_date = first + "-01-01"
                f_datefrom = first + "0101"
                f_dateto = last + "0101"
            # <year>05.10.2004</year>
            elif re.match(r"^[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{4,4}$", year_value):
                day, month, year = re.split("\.", year_value)
                f_date = year + "-" + month + "-" + day
                f_datefrom = year + month + day
                f_dateto = year + month + day
            else:
                f_date = "0000-00-00"
                f_datefrom = "00000000"
                f_dateto = "00000000"

        # logging.info('... title|' + f_title +'|_')
        # logging.info('... genre|' + f_genre + '|and domain|' + get_domain_string(f_genre) +'|_')
        # logging.info('... lang|' + f_lang +'|_')
        # logging.info('... orig_lang|' + f_orig_lang +'|_')
        # logging.info('... first name|' + f_first_name_author +'|_')
        # logging.info('... last name|' + f_last_name_author +'|_')
        # logging.info('... nationality|' + f_nationality +'|_')
        # logging.info('... date|' + f_date +'|_')
        # logging.info('... datefrom|' + f_datefrom +'|_')
        # logging.info('... dateto|' + f_dateto +'|_')
        # logging.info('... timefrom|' + f_timefrom +'|_')
        # logging.info('... timeto|' + f_timeto +'|_')

        f_root.clear()
        f_root.tag = "text"
        f_root.set("title", f_title)
        f_root.set("lang", f_lang)
        f_root.set("orig_lang", f_orig_lang)
        f_root.set("first_name", f_first_name_author)
        f_root.set("last_name", f_last_name_author)
        f_root.set("nationality", f_nationality)
        f_root.set("gt_domain", DOMAIN_MAPPING[f_genre])
        f_root.set("date", f_date)
        f_root.set("datefrom", f_datefrom)
        f_root.set("dateto", f_dateto)
        f_root.set("timefrom", f_timefrom)
        f_root.set("timeto", f_timeto)

        sentences = split_cohort(content, lang)

        # converting the analysis output into a suitable xml format for vrt
        # transformation (vrt is the cwb input format)

        for s_id, sentence in enumerate(sentences):
            current_sentence = ET.SubElement(f_root, "sentence")
            current_sentence.set("id", str(s_id + 1))
            positional_attributes = "\n"

            output_type = "vrt"
            for token in sentence:
                ### logging.info('_current_token_|'+str(token)+'|_')
                if output_type == "xml":
                    current_word = ET.SubElement(current_sentence, "word")
                    # NB: the names of the xml attributes of the word element are sorted alphabetically, e.g., 'dcs' comes first!
                    for i, positional_feature in enumerate(token):
                        if i == 0:
                            current_word.set("form", positional_feature)
                        elif i == 1:
                            current_word.set("lemma", positional_feature)
                        elif i == 2:
                            current_word.set("pos", positional_feature)
                        elif i == 3:
                            current_word.set("msd", positional_feature)
                        elif i == 4:
                            current_word.set("sID", positional_feature)
                        elif i == 5:
                            current_word.set("depRel", positional_feature)
                        elif i == 6:
                            current_word.set("pID", positional_feature)
                        elif i == 7:
                            current_word.set("dcs", positional_feature)

                if output_type == "vrt":
                    for i, positional_feature in enumerate(token):
                        if i == 0:
                            positional_attributes += positional_feature
                        else:
                            if i == 5:
                                ###print('_posfit_|' + positional_feature + '|_posfit_')
                                # print("positional_feature=",positional_feature)
                                positional_feature = DEPREL_MAPPING[positional_feature]
                            positional_attributes += "\t" + positional_feature
                    positional_attributes += "\n"
            current_sentence.text = positional_attributes

        # delete the original dependency node
        dep_nodes = f_root.findall(".//body/dependency")
        while len(dep_nodes):
            parent = f_root.findall(".//body/dependency" + "/..")[0]
            parent.remove(dep_nodes[0])
            dep_nodes = f_root.findall(".//body/dependency")

        vrt_format(f_root)

        # print("out path=", os.path.join(out_dir_path,str(current_file)))
        print("path=", os.path.join(current_out_dir_path, str(current_file)))
        # xml_tree.write(os.path.join(out_dir_path,str(current_file)),
        xml_tree.write(
            os.path.join(current_out_dir_path, str(current_file.split("/")[-1])),
            xml_declaration=False,
            encoding="utf-8",
            method="xml",
        )
        print("DONE ", current_file, "\n\n")

        mv_cmd = "mv " + current_file + " " + done_dir_path
        print("MOVED file ", current_file, " in done folder \n\n")
        p = Popen(mv_cmd, shell=True, stdout=PIPE, stderr=PIPE)
        mv_out, mv_err = p.communicate()


def split_cohort(analysis, current_lang):

    _current_lang = current_lang
    debug_output = False
    # generate_der_comp_lemma = False

    _analysis = analysis
    # ambiguity hack: mask '<' as lemma, i.e., in the context of '\n\t\"<'
    _analysis = re.sub('\n\t"<', '\n\t"\\<', _analysis)
    _analysis = re.sub('\n\t">', '\n\t"\\>', _analysis)
    _analysis = re.sub(
        """:\s*
\s*

\s*""",
        ":\n",
        _analysis,
    )
    # remove weights
    _analysis = re.sub(r"<W\:[0-9]*\.*[0-9]*>", "", _analysis)

    # another hack while waiting for the fix: delete all initial line of a file starting with a colon
    if _analysis.startswith(":"):
        _analysis = re.sub("^:[^\n]*\n", "", _analysis)

    # - waiting for specifications on how these pieces of information will be
    # deployed in the corpus and presented in Korp: as substrings of the
    # msd-string or as extra attribute-value pairs choosable via the Korp
    # interface? - for now they ar just filtered away

    for extra_tag in [
        "<cohort-with-dynamic-compound>",
        "<ext>",
        "<cs>",
        "<hab>",
        "<loc>",
        "<gen>",
        "<ctjHead>",
    ]:
        _analysis = re.sub(" " + extra_tag, "", _analysis)

    for wordform in WORDFORM_FILTER:
        _analysis = re.sub(" " + wordform, "", _analysis)

    ###logging.info('ANALYSIS_sentence|'+ _analysis + '|_')

    _sentences = []

    for current_sentence in [x for x in re.split("\n\n", _analysis) if x != ""]:
        sentence = []
        ###print('...1_sentence|'+ current_sentence + '|_')
        # split the tokens+analyses based on ('"<'
        for current_cohort in [x for x in re.split('"<', current_sentence) if x != ""]:
            # discard all lines starting with ':' (= giella format of hfst)
            cohort = re.split("\n:", current_cohort)[0]
            # print("cohort=", cohort)
            ### print('...2_cohort|'+ cohort + '|_')

            # split word form from analysis
            word_form = re.split('>"\n', cohort)[0]
            rest_cohort = re.split('>"\n', cohort)
            # print('...3_wf|'+ word_form + '|_')
            # print('...3_rc|'+ str(rest_cohort) + '|_')

            # further split non-disambiguated analyses based on '\n\t"'
            # print("rest_cohort=",rest_cohort)
            # print("rest_cohort[1]=",rest_cohort[1])
            cohort_lines = re.split('\n\t"', rest_cohort[1])
            ### print('...4_cohort_lines|'+ str(cohort_lines) + '|_')
            split_analysis = []
            # explicit marking of boundaries between:
            # lemma, derivation strings, analysis of parts of compounds
            for line in cohort_lines:
                # delete '\t"' at the beginning of the analysis
                ###print('...5_ln_x1x|'+ line + '|_')
                line = line.lstrip("\t")
                ###print('...6_ln_x2x|'+ line + '|_')
                if line.startswith('"'):
                    line = line[1:]
                ###print('...7_ln_x3x|'+ line + '|_')
                # delete '\n' at the end of the analysis
                line = line.rstrip("\n")
                # delimiter between lemma and msd (morpho-syntactic description)
                line = re.sub('"\s', "_∞_", line)
                # delimiter between the compound parts
                line = re.sub("\n\t", "_™_", line)
                # keep track of the embedding of the different parts for compounds split into more than two parts
                line = re.sub('\t"', "_™_", line)
                line = re.sub("\t", "_™_", line)

                split_analysis.append(line)

            ###print('_unsorted_cohort_|'+str(split_analysis)+'|__')

            # sort cohort
            sorted_analysis_lines = []

            # if there are mixed analyses with and without Error tags
            # filter away all instances containing Error tags
            # however, if there are only analyses containing Error tags
            # sort the cohort and choose the first version

            filtered_analysis = [i for i in split_analysis if not ("Err/" in i)]

            if len(filtered_analysis) > 0:
                ### logging.info('_filtered_cohort_|'+str(filtered_analysis)+'|__')
                sorted_analysis_lines = sorted(
                    filtered_analysis, key=lambda name: name.lower()
                )
                ### logging.info('_filtered_sorted_cohort_|'+str(sorted_analysis_lines)+'|__')
            else:
                ### logging.info('_unfiltered_unsorted_cohort_|'+str(split_analysis)+'|__')
                sorted_analysis_lines = sorted(
                    split_analysis, key=lambda name: name.lower()
                )
                ### logging.info('_unfiltered_sorted_cohort_|'+str(sorted_analysis_lines)+'|__')

            ### if len(split_analysis) > 1:
            ###     logging.info('_unsorted_cohort_|'+str(split_analysis)+'|__')

            ### if len(split_analysis) > 1:
            ###     logging.info('_sorted_cohort_|'+str(sorted_analysis_lines)+'|__')

            # take the first analysis in case there are more than one non-disambiguated analyses
            used_analysis = sorted_analysis_lines[0]
            # filter all Err- and Sem-tags from the string
            used_analysis = re.sub("Err/[^\s]+\s", "", used_analysis)
            used_analysis = re.sub("Sem/[^\s]+\s", "", used_analysis)
            used_analysis = re.sub("Use/[^\s]+\s", "", used_analysis)
            used_analysis = re.sub("Gram/[^\s]+\s", "", used_analysis)
            used_analysis = re.sub("OLang/[^\s]+\s", "", used_analysis)
            used_analysis = re.sub("Dial/[^\s]+\s", "", used_analysis)
            used_analysis = re.sub("CmpN/[^\s]+\s", "", used_analysis)
            used_analysis = re.sub("CmpNP/[^\s]+\s", "", used_analysis)
            used_analysis = re.sub("G3+\s", "", used_analysis)
            used_analysis = re.sub("v9+\s", "", used_analysis)

            if debug_output:
                # print('8_used_analysis_|'+str(used_analysis)+'|_')
                logging.info("8_used_analysis_|" + str(used_analysis) + "|_")

            # keep this strig for lemma generation
            original_analysis = used_analysis

            ex_index = used_analysis.find("Ex/")
            tm_index = used_analysis.find("_™_")
            current_line_no = inspect.stack()[0][2]
            ### print('_ex-tm_|'+str(ex_index)+'|'+str(tm_index)+'|__|'+str(current_line_no)+'|__')

            ### print('_|'+ word_form + '|_|' + str(used_analysis) + '|_')

            if "Ex/" in used_analysis and not "_™_" in used_analysis:
                lemma = used_analysis.split("_∞_", 1)[0]
                msd = used_analysis.split("_∞_", 1)[1]
                # print("msd=", msd)
                # print("used_analysis=", used_analysis)
                swapped_msd = get_correct_pos(msd)
                used_analysis = lemma + "_∞_" + swapped_msd
                ###print('_LMSU__|'+ lemma + '|_|' + msd + '|_|' + swapped_msd+ '|_|' + used_analysis+ '|__LMSU_')

            # extra handling of the combination of derivation of the head
            # and compounding
            if (
                "Ex/" in used_analysis
                and "_™_" in used_analysis
                and ex_index < tm_index
            ):
                # logging.info('_XXX_|'+used_analysis+'|_')

                lemma = used_analysis.split("_∞_", 1)[0]
                msd = used_analysis.split("_∞_", 1)[1]
                derivation = msd.split("_™_", 1)[0]
                rest = msd.split("_™_", 1)[1]
                swapped_msd = get_correct_pos(derivation)
                used_analysis = lemma + "_∞_" + swapped_msd + "_™_" + rest
                # logging.info('_YYY_|'+used_analysis+'|_')

            # put a clear delimiter between the (first) pos value and the rest of msd
            # in order to disambiguate from the rest of whitespaces
            # print("used_analysis=",used_analysis)
            parts = re.compile(
                "(_∞_\w+\s?|_∞_\?\s?|_∞_\<ehead>\s?|_∞_#|_∞_\<mv>\s?)"
            ).split(used_analysis, 1)
            ###logging.info('_parts_|'+str(parts)+'|_')
            # print("parts=",parts)

            parts[1] = parts[1].replace("_∞_", "").strip()
            lemma = parts[0]
            pos = parts[1]
            rest = parts[2]
            # print("lemma=",lemma)
            # print("pos=",pos)
            # print("rest=",rest)

            # print('_YYY_|'+used_analysis+'|_')
            # print("lemma="+lemma)

            # logging.info('_LEN_the-parts_|'+str(len(parts))+'|_')
            # logging.info('_1_the-parts_|'+str(parts)+'|_')

            ex_in_r = rest.find("_©_")
            tm_in_r = rest.find("_™_")
            # current_line_no = inspect.stack()[0][2]
            # logging.info('_exr-tmr_|'+str(ex_in_r)+'|'+str(tm_in_r)+'|_|'+str(current_line_no)+'|_')

            # derivation-composition string
            dcs = ""
            # morpho-syntactic description
            msd = ""

            # split derivation/composition string from the rest of MSD
            # and put it in and extra tuple at the end of the tuple list,
            # otherwise add a default tuple '___'
            # no derivation, no composition
            if ex_in_r == -1 and tm_in_r == -1:
                msd = rest
                dcs = "___"
                ###logging.info('_msd_cds_1_|'+str(msd)+'|_|'+str(dcs)+'|_')
            # no derivation, but composition
            elif (ex_in_r == -1 and not tm_in_r == -1) or (
                not ex_in_r == -1 and not tm_in_r == -1 and tm_in_r < ex_in_r
            ):
                msd, dcs = re.compile("_™_").split(rest, 1)
                dcs = "_™_" + dcs
                ###logging.info('_msd_cds_2_|'+str(msd)+'|_|'+str(dcs)+'|_')

            # derivation, but no composition
            elif (not ex_in_r == -1 and tm_in_r == -1) or (
                not ex_in_r == -1 and not tm_in_r == -1 and ex_in_r < tm_in_r
            ):
                msd, dcs = re.compile("_©_").split(rest, 1)
                dcs = "_©_" + dcs
                ###logging.info('_msd_cds_3_|'+str(msd)+'|_|'+str(dcs)+'|_')
            # covered all relevant combinations?
            else:
                logging.info("_msd_cds_4_|" + str(rest) + "|_")

            # processing msd: splitting function label, selfID and parentID from the msd string
            msd_drel = re.compile(" #").split(msd)
            head = ""
            tail = ""
            # print('_XXX_|'+str(msd_drel)+'|_')
            ###print('_YYY_|'+str(len(msd_drel))+'|_')

            if len(msd_drel) == 1:
                head = "___"
                ###print('IF ... head ', head)
                tail = msd_drel[0].lstrip("#")
                ###print('IF ... tail ', tail)
            else:
                ### here to debug
                head = msd_drel[0]
                ###print('ELSE ... head ', head)
                tail = msd_drel[1]
                ###print('ELSE ... tail ', tail)

            current_msd = ""
            fct_label = ""
            ### here to debug
            # print('_the-tail_|'+str(tail)+'|_')
            if tail and "->" in tail:
                self_id, parent_id = re.compile("->").split(tail)
            else:
                self_id, parent_id = "", ""
            ###print('_ID_|'+str(self_id)+'|_|'+str(parent_id)+'|_')

            # splitting the fuction label
            if not head == "___":
                if not "@" in head:
                    current_msd = head
                    fct_label = "X"
                    # logging.info('_head_|'+str(head)+'|_')
                else:
                    msd_fct = re.compile(" @").split(head)
                    if len(msd_fct) == 1:
                        current_msd = "___"
                        fct_label = msd_fct[0].lstrip("@")
                        # logging.info('_msd_fct_1_|'+str(msd_fct)+'|_')
                    else:
                        current_msd = msd_fct[0]
                        fct_label = msd_fct[1]
                        # logging.info('_msd_fct_2_|'+str(msd_fct)+'|_')
            else:
                current_msd = "___"
                fct_label = "X"

            # TODO: update the description below
            # MDS can be complex and partitioned with specific separators:
            # 1. _™_ for each TAB for parts of the compounds
            # 2. _∞_ as separator between lemma and POS+MSD in a part of a compound
            # Ex.: ('juovlavuonasildi', 'sildi',
            #        'N', 'Sem/Ani Sg Nom @HNOUN_™__™_vuotna_∞_N Sem/Plc Cmp/SgGen Cmp_™__™__™_juovllat_∞_N Sem/Time Cmp/SgNom Cmp')
            # 3. _©_ as separator between the MSD and the derivation tags
            # Ex.: ('stellejuvvot', 'stellet', 'V', 'IV Inf @-FMAINV_©_Ex/V Ex/TV Der/PassL')

            # TODO: split Sem-tags and put them into as a separate position attribute for an updated corpus format for Korp
            # so that semantic attributes can be searchable via Korp interface

            if pos == "?":
                pos = "___"

            # analysed data as an 8-tuple: (WORD_FORM, LEMMA, POS, MSD, SELF_ID, FUNCTION_LABEL, PARENT_ID, DERIVATION-COMPOUNDING-STRING)

            # ambiguity hack: unmask '<' and '>' as lemma
            lemma = lemma.replace("\\", "")

            ### DONE
            ### replace here lemma with the generated lemma;
            ### delete derivation/composition tags
            ### CAVEAT: the tuple will not be a 8-tuple but a 7-tuple

            # lemma generation string
            lemma_generation_string = ""
            generated_lemma = ""
            # if generate_der_comp_lemma:
            if "Ex/" in original_analysis or "_™_" in original_analysis:
                lemma_generation_string = get_generation_string(
                    original_analysis, pos, current_msd, _current_lang
                )

            if lemma_generation_string:
                ### logging.info('xxx_lem-gen-str_|'+lemma_generation_string+'|_')
                generated_lemma = generate_lemma(lemma_generation_string, _current_lang)

            # msd clean up
            ### logging.info('_1_msd_|' + current_msd + '|_')

            current_msd = re.sub("IV\s", "", current_msd)
            current_msd = re.sub("TV\s", "", current_msd)
            current_msd = re.sub("Relc", "Rel", current_msd)
            current_msd = re.sub("Dyn", "", current_msd)
            current_msd = re.sub("Known", "", current_msd)
            current_msd = current_msd.strip()
            current_msd = re.sub("/", "_", current_msd)
            current_msd = re.sub("\s", ".", current_msd)
            # add the pos as fist element of the msd string
            if current_msd == "___":
                current_msd = pos
            else:
                current_msd = pos + "." + current_msd

            ### logging.info('_2_msd_|' + current_msd + '|_')

            analysis_tuple = ()
            ### logging.info('_generated_lemma_|' + generated_lemma + '|_')
            if generated_lemma == "":
                analysis_tuple = (
                    word_form,
                    lemma,
                    pos,
                    current_msd,
                    self_id,
                    fct_label,
                    parent_id,
                )
            else:
                analysis_tuple = (
                    word_form,
                    generated_lemma,
                    pos,
                    current_msd,
                    self_id,
                    fct_label,
                    parent_id,
                )

            ### logging.info("_current_tuple_|"+str(analysis_tuple)+"|_")

            # filter away '¶', which is used only to have some clause boundary if there is no one there
            # TODO: as well as other strings that are most likely noise
            if not word_form == "¶":
                sentence.append(analysis_tuple)

        # filter empty "sentences" due to filtering of  '¶'
        if sentence:
            ###logging.info("_analysed_token_tuples_|"+str(sentence)+"|_")
            _sentences.append(sentence)

    return _sentences


def get_correct_pos(input_string):
    _input_string = input_string
    ###print('_instr_|' + _input_string + '|_')
    der_pos_msd = re.split("( V | N | A | Adv | Po )", input_string)
    ###print('_der_pos_msd_|' + str(der_pos_msd) + '|_')
    swapped_string = (
        der_pos_msd[1].strip() + " " + der_pos_msd[2].strip() + "_©_" + der_pos_msd[0]
    )
    return swapped_string


def get_generation_string(in_analysis, in_pos, in_msd, in_lang):

    _used_analysis = in_analysis
    _pos = in_pos
    _msd = in_msd
    _lang = in_lang
    _string2generate = ""

    _lemma = _used_analysis.split("_∞_", 1)[0]
    _tail = _used_analysis.split("_∞_", 1)[1]

    # ignore function and dependence relation here
    _tail = re.sub("\s@[^\s]+", "", _tail)
    _tail = re.sub("\s#\d+->\d+", "", _tail)

    ex_index = _tail.find("Ex/")
    tm_index = _tail.find("_™_")
    current_line_no = inspect.stack()[0][2]
    ### print('_ex-tm_|'+str(ex_index)+'|'+str(tm_index)+'|__|'+str(current_line_no)+'|__')

    if "Ex/" in _tail:
        if (not "_™_" in _tail) or ("_™_" in _tail and ex_index < tm_index):
            _string2generate = _lemma + "_∞1EX∞_" + _tail

    if "_™_" in _tail:
        if (not "Ex/" in _tail) or ("Ex/" in _tail and tm_index < ex_index):
            _string2generate = _lemma + "_∞1CO∞_" + _tail

    ### replace all delimiter by '+' and '_™_' by '#'
    _string2generate = re.sub("\s+", "+", _string2generate)
    _string2generate = re.sub("_∞1EX∞_", "+", _string2generate)
    _string2generate = re.sub("Ex/", "", _string2generate)
    _string2generate = re.sub("_∞1CO∞_", "+", _string2generate)
    _string2generate = re.sub("_∞_", "+", _string2generate)
    _string2generate = re.sub("(_™_)+", "_™_", _string2generate)

    ### construct the correct order of generation for compund parts
    parts = _string2generate.split("_™_")
    swapped_string = ""
    if len(parts) > 1:
        ###print('_the_parts_|'+str(parts)+'|_')
        for i, p in reversed(list(enumerate(parts))):
            swapped_string += p
            if i > 0:
                swapped_string += "#"

        _string2generate = swapped_string

    ### logging.info('_bfr_str2gen_|'+_string2generate+'|_')

    # replace inflection tags of the analysed string with the corresponding baseform tags
    str_first = _string2generate.rpartition("+" + _pos + "+")[0]
    str_last = _string2generate.rpartition("+" + _pos + "+")[2]
    ### logging.info('_mid_str2gen_|'+str(_string2generate.rpartition('+'+_pos+'+'))+'|_')

    if _pos == "V":
        _string2generate = str_first + "+" + _pos + "+" + "Inf"

    if _pos == "N":
        _string2generate = str_first + "+" + _pos + "+" + "Sg+Nom"

    if _pos == "A":
        if _lang == "sma":
            if "Comp" in str_last:
                _string2generate = str_first + "+" + _pos + "+" + "Comp+Attr"
            elif "Superl" in str_last:
                _string2generate = str_first + "+" + _pos + "+" + "Superl+Attr"
            else:
                _string2generate = str_first + "+" + _pos + "+" + "Attr"
        else:
            _string2generate = str_first + "+" + _pos + "+" + "Sg+Nom"

    ### logging.info('_afr_str2gen_|'+_string2generate+'|_')

    return _string2generate


def generate_lemma(in_string, c_lang):

    _in_string = in_string
    _current_lang = c_lang
    _analysis_lemma = re.split("\+", _in_string, 1)[0]
    _generated_lemma = "TODO_" + _in_string
    langs_dir = "$GTLANGS/lang-"

    generation_cmd = (
        " | hfst-lookup -q "
        + langs_dir
        + _current_lang
        + "/src/generator-gt-norm.hfstol"
    )

    pFST = Popen(
        "echo '" + _in_string + "'" + generation_cmd,
        shell=True,
        stdout=PIPE,
        stderr=PIPE,
    )
    outFST, errFST = pFST.communicate()
    outFST = outFST.decode()
    outFST = re.split("\n", outFST, 1)[0]
    _generated_lemma = re.split("\t", outFST)[1]
    if _generated_lemma.endswith("+?"):
        _generated_lemma = _analysis_lemma

    ### logging.info('___gen-out___ ' + outFST + '______')

    return _generated_lemma


if __name__ == "__main__":
    reload(sys)
    main()
