#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import argparse
import logging
import multiprocessing
import os
import re
import xml.etree.ElementTree as ET
from functools import partial
from subprocess import run

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
    """Make sure empty text or tail is padded with newline."""
    padding = "\n"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = padding
        for child in elem:
            vrt_format(child)
    if not elem.tail or not elem.tail.strip():
        elem.tail = padding


def append_files(files_list, folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".xml"):
                files_list.append(os.path.join(root, file))


def process_in_parallel(done_dir_path, lang, files_list):
    """Process file in parallel."""

    pool_size = multiprocessing.cpu_count() * 2
    pool = multiprocessing.Pool(processes=pool_size)
    pool.map(partial(process_file, done_dir_path=done_dir_path, lang=lang), files_list)
    pool.close()  # no more tasks
    pool.join()  # wrap up current tasks
    return


def parse_options():
    parser = argparse.ArgumentParser(
        description="Turn analysed files into vrt format xml files."
    )

    parser.add_argument("in_dir", help="the directory of the analysed files")
    parser.add_argument("lang", help="language of the files to process")

    return parser.parse_args()


def group_sem(analysis):
    dict_sem = {
        "Hum": ["Hum", "Hum-abstr", "Hum-prof", "Mal", "Fem", "Sur"],
        "Org": ["Org"],
        "Ani": ["Ani", "Ani-fish"],
        "Plc": ["Adr", "Plc", "Plc-abstr", "Plc-elevate", "Plc-line", "Plc-water", "Event", "Edu", "Build", "Build-room"],
        "Time": ["Time", "Year", "Time-clock", "Date"],
        "Obj": ["Aniprod", "Body", "Buildpart", "Clth", "Clth-jewl", "Clthpart", "Drink", "Food", "Food-med", "Fruit", "Furn", "Obj", "Obj-clo", "Obj-el", "Obj-ling", "Obj-rope", "Obj-surfc", "Plant", "Plantpart", "Prod", "Prod-audio", "Prod-cogn", "Prod-ling", "Prod-vis", "Txt", "Wpn", "Substnc", "Mat", "Part"],
        "Abstr": ["Body-abstr", "Cat", "Ctain-abstr", "Ctain-clth", "Geom", "Group", "Obj-cogn", "Semcon", "Lang", "Feat-phys", "Feat-psych", "Feat-measr", "Perc-cogn", "Perc-emo", "Perc-phys", "Perc-psych", "Feat ", "Ideol", "Rule", "Pos", "Rel", "State", "Phonenr", "Sign", "Symbol", "State-sick", "ID", "Wthr"],
        "Instr": ["Tool", "Tool-catch", "Tool-clean", "Tool-it", "Tool-measr", "Tool-music", "Tool-write", "Wpn", "Curr", "Domain"],
        "Veh": ["Veh"],
        "Amount": ["Amount", "Measr", "Money"],
        "Act": ["Act", "Dance", "Game", "Sport", "Process"],
        "Route": ["Route", "Dir"]
    }

    if (re.search(r'Group_', analysis) and not re.search(r'Group_∞', analysis)) or re.search(r'_Group', analysis):
        dict_sem['Abstr'] = ["Body-abstr", "Cat", "Ctain-abstr", "Ctain-clth", "Geom", "Obj-cogn", "Semcon", "Lang", "Feat-phys", "Feat-psych", "Feat-measr", "Perc-cogn", "Perc-emo", "Perc-phys", "Perc-psych", "Feat ", "Ideol", "Rule", "Pos", "Rel", "State", "Phonenr", "Sign", "Symbol", "State-sick", "ID", "Wthr"]
        analysis = re.sub("_Group", "", analysis)
        analysis = re.sub("Group_", "", analysis)

    sem_ = re.search("Sem/([a-zA-Z]*_*)+", analysis)
    if sem_:
        repl = sem_.group().replace("_", " Sem/")
        #sem_parts = sem_.group().split("Sem/")[1].split("_")
        #for part in sem_parts:
        #    repl = repl + " Sem/" + part
        analysis = re.sub("Sem/([a-zA-Z]*_*)+", repl, analysis)

    for key, value in dict_sem.items():
        for sem in value:
                my_reg = "Sem/[a-zA-Z]*" + re.escape(sem) + "[a-zA-Z]*\s"
                analysis = re.sub(my_reg, "Sem/" + key + " ", analysis)

    return analysis


def main():
    args = parse_options()

    files_list = []

    debug_index = ""
    out_dir = "_od_" + args.in_dir + "_" + debug_index
    logging.basicConfig(
        filename="proc_" + args.in_dir + "_" + debug_index + ".log", level=logging.DEBUG
    )

    cwd = os.getcwd()
    out_dir_path = os.path.join(cwd, out_dir)
    if not os.path.exists(out_dir_path):
        print("_od_ ::: " + out_dir_path)
        os.makedirs(out_dir_path)

    done_dir = "done_multi_" + args.lang
    done_dir_path = os.path.join(cwd, done_dir)
    if not os.path.exists(done_dir_path):
        os.makedirs(done_dir_path)

    append_files(files_list, args.in_dir)
    process_in_parallel(done_dir_path, args.lang, files_list)


def make_root_element(f_root):
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

    f_orig_lang = ""
    f_first_name_author = ""
    f_last_name_author = ""
    f_nationality = ""
    year_value = ""
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
        f_nationality = f_root.find(".//header/author/person").attrib.get("nationality")

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

    root = ET.Element("text")
    root.set("title", f_title)
    root.set("lang", f_lang)
    root.set("orig_lang", f_orig_lang)
    root.set("first_name", f_first_name_author)
    root.set("last_name", f_last_name_author)
    root.set("nationality", f_nationality)
    root.set("gt_domain", DOMAIN_MAPPING[f_genre])
    root.set("date", f_date)
    root.set("datefrom", f_datefrom)
    root.set("dateto", f_dateto)
    root.set("timefrom", f_timefrom)
    root.set("timeto", f_timeto)

    return root


def process_file(current_file, done_dir_path, lang):
    """Convert analysed file into vrt format file."""
    print(f"... processing {current_file}")
    path = os.path.join(done_dir_path, os.path.basename(current_file))
    print(f"path={path}")
    with open(path, "wb") as newfile_stream:
        newfile_stream.write(
            ET.tostring(
                make_vrt_xml(current_file, lang),
                xml_declaration=False,
                encoding="utf-8",
            )
        )
    print("DONE ", path, "\n\n")


def make_vrt_xml(current_file, lang):
    """Convert analysis of a file into a vrt file

    Converting the analysis output into a suitable xml format for vrt
    transformation (vrt is the cwb input format)
    """
    xml_tree = ET.parse(current_file, ET.XMLParser(encoding="utf-8"))
    old_root = xml_tree.getroot()

    f_root = make_root_element(old_root)
    for s_id, sentence in enumerate(
        split_cohort(old_root.find(".//body/dependency").text, lang)
    ):
        current_sentence = ET.SubElement(f_root, "sentence")
        current_sentence.set("id", str(s_id + 1))
        current_sentence.text = make_positional_attributes(sentence)

    vrt_format(f_root)

    return f_root


def make_positional_attributes(sentence):
    positional_attributes = "\n"

    for token in sentence:
        ### logging.info('_current_token_|'+str(token)+'|_')
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
    return positional_attributes


def reshape_analysis(analysis):
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

    return _analysis


def extract_original_analysis(used_analysis, language):
    """Filter all Err- and Sem-tags from the string."""
    if language == 'sme':
        used_analysis = group_sem(used_analysis)
    else:
        used_analysis = re.sub("Sem/[^\s]+\s","", used_analysis)

    for regex in [
        "Use/[^\s]+\s",
        "Gram/[^\s]+\s",
        "OLang/[^\s]+\s",
        "Dial/[^\s]+\s",
        "CmpN/[^\s]+\s",
        "CmpNP/[^\s]+\s",
        "G3+\s",
        "v9+\s",
        "Err/[^\s]+\s",
    ]:
        used_analysis = re.sub(regex, "", used_analysis)

    return used_analysis


def extract_used_analysis(used_analysis):
    ### print('_|'+ word_form + '|_|' + str(used_analysis) + '|_')
    ex_index = used_analysis.find("Ex/")
    tm_index = used_analysis.find("_™_")
    if "Ex/" in used_analysis and not "_™_" in used_analysis:
        (lemma, msd) = used_analysis.split("_∞_", 1)

        # print("msd=", msd)
        # print("used_analysis=", used_analysis)
        swapped_msd = get_correct_pos(msd)
        used_analysis = lemma + "_∞_" + swapped_msd
        ###print('_LMSU__|'+ lemma + '|_|' + msd + '|_|' + swapped_msd+ '|_|' + used_analysis+ '|__LMSU_')

    # extra handling of the combination of derivation of the head
    # and compounding
    if "Ex/" in used_analysis and "_™_" in used_analysis and ex_index < tm_index:
        # logging.info('_XXX_|'+used_analysis+'|_')
        (lemma, msd) = used_analysis.split("_∞_", 1)
        (derivation, rest) = msd.split("_™_", 1)
        swapped_msd = get_correct_pos(derivation)
        used_analysis = lemma + "_∞_" + swapped_msd + "_™_" + rest
        # logging.info('_YYY_|'+used_analysis+'|_')

    return used_analysis


def reshape_cohort_line(line):
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

    return line


def sort_cohort(cohort_lines):
    split_analysis = [reshape_cohort_line(cohort_line) for cohort_line in cohort_lines]
    # if there are mixed analyses with and without Error tags
    # filter away all instances containing Error tags
    # however, if there are only analyses containing Error tags
    # sort the cohort and choose the first version

    filtered_analysis = [i for i in split_analysis if not ("Err/" in i)]
    if len(filtered_analysis) > 0:
        ### logging.info('_filtered_cohort_|'+str(filtered_analysis)+'|__')
        return sorted(filtered_analysis, key=lambda name: name.lower())
        ### logging.info('_filtered_sorted_cohort_|'+str(sorted_analysis_lines)+'|__')

    ### logging.info('_unfiltered_unsorted_cohort_|'+str(split_analysis)+'|__')
    return sorted(split_analysis, key=lambda name: name.lower())
    ### logging.info('_unfiltered_sorted_cohort_|'+str(sorted_analysis_lines)+'|__')


def make_morpho_syntactic_description(rest):
    """Extract morpho_syntactic_description"""
    ex_in_r = rest.find("_©_")
    tm_in_r = rest.find("_™_")

    # split derivation/composition string from the rest of MSD
    # and put it in and extra tuple at the end of the tuple list,
    # otherwise add a default tuple '___'
    # no derivation, no composition
    if ex_in_r == -1 and tm_in_r == -1:
        return rest
        ###logging.info('_msd_cds_1_|'+str(msd)+'|_|'+str(dcs)+'|_')
    # no derivation, but composition
    elif (ex_in_r == -1 and not tm_in_r == -1) or (
        not ex_in_r == -1 and not tm_in_r == -1 and tm_in_r < ex_in_r
    ):
        return re.compile("_™_").split(rest, 1)[0]
    # derivation, but no composition
    elif (not ex_in_r == -1 and tm_in_r == -1) or (
        not ex_in_r == -1 and not tm_in_r == -1 and ex_in_r < tm_in_r
    ):
        return re.compile("_©_").split(rest, 1)[0]
    # covered all relevant combinations?
    else:
        return ""


def make_head_tail(morpho_syntactic_description_drel):
    # processing msd: splitting function label, selfID and parentID from the msd string

    if len(morpho_syntactic_description_drel) == 1:
        return ("___", morpho_syntactic_description_drel[0].lstrip("#"))

    return (morpho_syntactic_description_drel[0], morpho_syntactic_description_drel[1])


def split_function_label(head):
    # splitting the function label
    if not head == "___":
        if not "@" in head:
            return (head, "X")
        else:
            msd_fct = re.compile(" @").split(head)
            if len(msd_fct) == 1:
                return ("___", msd_fct[0].lstrip("@"))
            else:
                return (msd_fct[0], msd_fct[1])

    return ("___", "X")


def lemma_generation(original_analysis, pos, _current_lang):
    """Generate lemma."""
    if "Ex/" in original_analysis or "_™_" in original_analysis:
        lemma_generation_string = get_generation_string(
            original_analysis, pos, _current_lang
        )

        if lemma_generation_string:
            return generate_lemma(lemma_generation_string, _current_lang)

    return ""


def clean_msd(current_msd, pos):
    current_msd = current_msd.strip()
    for (regex, replacement) in [
        ("IV\s", ""),
        ("TV\s", ""),
        ("Relc", "Rel"),
        ("Dyn", ""),
        (
            "Known",
            "",
        ),
        ("/", "_"),
        ("\s", "."),
    ]:
        current_msd = re.sub(regex, replacement, current_msd)
    # add the pos as first element of the msd string
    if current_msd == "___":
        return pos
    return pos + "." + current_msd


def get_wordform_rest(current_cohort):
    # discard all lines starting with ':' (= giella format of hfst)
    cohort = re.split("\n:", current_cohort)[0]
    # split word form from analysis
    (word_form, *rest_cohort) = re.split('>"\n', cohort)
    return (word_form, rest_cohort[0])


def non_empty_cohorts(current_sentence):
    for cohort in re.split('^"<|\n"<', current_sentence):
        if cohort != "":
            (word_form, rest_cohort) = get_wordform_rest(cohort)
            if word_form != "¶":
                yield (word_form, rest_cohort)


def make_analysis_tuple(word_form, rest_cohort, language):
    # take the first analysis in case there are more than one non-disambiguated analyses
    original_analysis = extract_original_analysis(
        sort_cohort(cohort_lines=re.split('\n\t"', rest_cohort))[0], language
    )

    # put a clear delimiter between the (first) pos value and the rest of msd
    # in order to disambiguate from the rest of whitespaces
    parts = re.compile("(_∞_\w+\s?|_∞_\?\s?|_∞_\<ehead>\s?|_∞_#|_∞_\<mv>\s?)").split(
        extract_used_analysis(original_analysis), maxsplit=1
    )

    # ambiguity hack: unmask '<' and '>' as lemma
    lemma = parts[0].replace("\\", "")
    maybe_pos = parts[1].replace("_∞_", "").strip()
    pos = "___" if maybe_pos == "?" else maybe_pos
    (head, tail) = make_head_tail(
        re.compile(" #").split(make_morpho_syntactic_description(parts[2]))
    )
    (self_id, parent_id) = (
        re.compile("->").split(tail) if tail and "->" in tail else ("", "")
    )
    (morpho_syntactic_description, function_label) = split_function_label(head)

    generated_lemma = lemma_generation(original_analysis, pos, language)

    return (
        word_form,
        lemma if generated_lemma == "" else generated_lemma,
        pos,
        clean_msd(morpho_syntactic_description, pos),
        self_id,
        function_label,
        parent_id,
    )


def valid_sentences(analysis):
    return (
        sentence
        for sentence in re.split("\n\n", reshape_analysis(analysis))
        if sentence != "" and not sentence.startswith('"<¶')
    )


def split_cohort(analysis, current_lang):
    """Make sentences from the current analysis."""
    return [
        [
            make_analysis_tuple(word_form, rest_cohort, current_lang)
            for (word_form, rest_cohort) in non_empty_cohorts(current_sentence)
        ]
        for current_sentence in valid_sentences(analysis)
    ]


def get_correct_pos(input_string):
    der_pos_msd = re.split("( V | N | A | Adv | Po )", input_string)
    swapped_string = (
        der_pos_msd[1].strip() + " " + der_pos_msd[2].strip() + "_©_" + der_pos_msd[0]
    )
    return swapped_string


def get_generation_string(used_analysis, pos, lang):
    (lemma, tail) = used_analysis.split("_∞_", 1)

    string2generate = make_string2generate(lemma, tail)

    if not string2generate:
        return ""

    string2generate = clean_string2generate(string2generate)

    ### construct the correct order of generation for compund parts
    parts = string2generate.split("_™_")
    if len(parts) > 1:
        swapped_string = ""
        for index, part in reversed(list(enumerate(parts))):
            swapped_string += part
            if index > 0:
                swapped_string += "#"

        string2generate = swapped_string

    if pos not in ["V", "N", "A"]:
        return string2generate

    # replace inflection tags of the analysed string with the corresponding baseform tags
    str_first = string2generate.rpartition("+" + pos + "+")[0]
    str_last = string2generate.rpartition("+" + pos + "+")[2]

    if pos == "V":
        return str_first + "+" + pos + "+" + "Inf"

    if pos == "N":
        return str_first + "+" + pos + "+" + "Sg+Nom"

    if pos == "A":
        if lang == "sma":
            if "Comp" in str_last:
                return str_first + "+" + pos + "+" + "Comp+Attr"
            elif "Superl" in str_last:
                return str_first + "+" + pos + "+" + "Superl+Attr"

            return str_first + "+" + pos + "+" + "Attr"

        return str_first + "+" + pos + "+" + "Sg+Nom"


def clean_string2generate(string2generate):
    ### replace all delimiter by '+' and '_™_' by '#'
    for (regex, replacement) in [
        ("\s+", "+"),
        ("_∞1EX∞_", "+"),
        ("Ex/", ""),
        ("_∞1CO∞_", "+"),
        ("_∞_", "+"),
        ("(_™_)+", "_™_"),
    ]:
        string2generate = re.sub(regex, replacement, string2generate)

    return string2generate


def make_string2generate(lemma, tail):
    # ignore function and dependence relation here
    tail = re.sub("\s@[^\s]+", "", tail)
    tail = re.sub("\s#\d+->\d+", "", tail)

    ex_index = tail.find("Ex/")
    tm_index = tail.find("_™_")

    if "Ex/" in tail:
        if (not "_™_" in tail) or ("_™_" in tail and ex_index < tm_index):
            return lemma + "_∞1EX∞_" + tail

    if "_™_" in tail:
        if (not "Ex/" in tail) or ("Ex/" in tail and tm_index < ex_index):
            return lemma + "_∞1CO∞_" + tail

    return ""


def generate_lemma(in_string, c_lang):
    langs_dir = f"{os.getenv('GTLANGS')}/lang-{c_lang}"
    first_line = (
        run(
            f"hfst-lookup -q {langs_dir}/src/generator-gt-norm.hfstol".split(),
            check=True,
            input=in_string.encode("utf-8"),
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .split("\n")[0]
    )
    generated_lemma = first_line.split("\t")[1]

    return (
        generated_lemma
        if not generated_lemma.endswith("+?")
        else in_string.split("+")[0]
    )


if __name__ == "__main__":
    main()
