# -*- coding:utf-8 -*-

import MySQLdb
from settings_not_in_svn import *


class From_vrt:
    def __init__(self, string, lemma, pos, analyses, position, relation, parent, sentence_id, token_count, string_id):
        self.string = string
        self.lemma = lemma
        self.pos = pos
        self.analyses = analyses
        self.position = position
        self.relation = relation
        self.parent = parent
        self.sentence_id = sentence_id
        self.token_count = token_count
        self.string_id = string_id

def sql_escape(s):
    return MySQLdb.escape_string(s).decode("utf-8") if isinstance(s, str) else s

def insert_rel(id, head, rel, dep, bfhead, bfdep, wfhead, wfdep, pos_head, pos_dep, sent_id, case):
    row_array = []
    query = "INSERT INTO relations_" + corpus_name + "(id, head, rel, dep, freq, bfhead, bfdep, wfhead, wfdep) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE freq = freq + 1;"
    id += 1
    args = (id, head, rel, dep, 1, bfhead, bfdep, wfhead, wfdep)
    cursor.execute(query, args)
    sql = "SELECT * FROM relations_" + corpus_name + " where head = '" + str(head) + "' AND rel = '" + str(rel) + "' AND dep = '" + str(dep) + "';"
    cursor.execute(sql)
    if not cursor.rowcount == 0:
        for row in cursor:
            id_r = row[0]
            if bfhead and bfdep:
                sql = "SELECT * FROM relations_" + corpus_name + "_sentences where id = '" + str(id_r) +  "' AND sentence = '" + str(sent_id) + "' AND start = '" + str(pos_head) + "' AND end = '" + str(pos_dep) + "';"
                cursor.execute(sql)
                if cursor.rowcount == 0:
                    # sentences
                    query = "INSERT INTO relations_" + corpus_name + "_sentences" + "(id, sentence, start, end) VALUES(%s, %s, %s, %s);"
                    args = (id_r, sent_id, pos_head, pos_dep)
                    cursor.execute(query, args)
                    row_array.append([head, rel, dep, bfhead, bfdep])
            else:
                # sentences
                query = "INSERT INTO relations_" + corpus_name + "_sentences" + "(id, sentence, start, end) VALUES(%s, %s, %s, %s);"
                args = (row[0], sent_id, pos_head, pos_dep)
                cursor.execute(query, args)
    else:
        sql = "SELECT id FROM relations_" + corpus_name + " where head = '" + str(head) + "' AND rel = '" + rel + "' AND dep = '" + str(dep) + "' AND bfhead = " + str(bfhead) + " AND bfdep = " + str(bfdep) + " AND wfhead = " + str(wfhead) + " AND wfdep = " + str(wfdep)  + ";"
        cursor.execute(sql)
        for row in cursor:
            id_r = row[0]
            # sentences
            query = "INSERT INTO relations_" + corpus_name + "_sentences" + "(id, sentence, start, end) VALUES(%s, %s, %s, %s);"
            args = (id_r, sent_id, pos_head, pos_dep)
            cursor.execute(query, args)
    return id


string_id = 0
i = 0
sentences = list()
single_sentence = From_vrt([], [], [], [], [], [], [], '', -1, [])

logfile = open(logfileName, 'w')

with open(fileName) as f:
    for line in f:
        print("line", line)
        if i == single_sentence.token_count:
            sentences.append(single_sentence)
            i = 0
        if 'sentence id' in line:
            single_sentence = From_vrt([], [], [], [], [], [], [], '', 0, [])
            single_sentence.sentence_id = line.split('"')[1]
            single_sentence.token_count = int(line.split('"')[len(line.split('"'))-2])
        else:
            if '/sentence' not in line and 'corpus id' not in line and 'text id' not in line and '/text' not in line and '/corpus' not in line:
                single_sentence.string.append(line.split()[0])
                single_sentence.lemma.append(line.split()[1])
                single_sentence.lemma.append(line.split()[1])
                single_sentence.string.append(line.split()[1])
                str_escaped = sql_escape(line.split()[0])
                lemma_escaped = sql_escape(line.split()[1])

                query = "SELECT id FROM relations_" + corpus_name + "_strings WHERE string = '" + str_escaped + "' AND lemma = '" + lemma_escaped + "';"
                cursor.execute(query)
                if cursor.rowcount == 0:
                    single_sentence.string_id.append(string_id)
                    ### relations_CORPUSNAME_strings - string
                    query = "INSERT INTO relations_" + corpus_name + "_strings(id, string, stringextra, pos, lemma) VALUES(%s, %s, %s, %s, %s);"
                    args = (string_id, line.split()[0], "", line.split()[2], line.split()[1])
                    try:
                        cursor.execute(query, args)
                    except:
                        logfile.write('===== error writing in mysql for line \n')
                        logfile.write(line)
                    string_id += 1
                else:
                    for row in cursor:
                        single_sentence.string_id.append(row[0])

                if len(line.split()) == 7:
                    single_sentence.pos.append(line.split()[2])
                    single_sentence.analyses.append(line.split()[3])
                    single_sentence.position.append(line.split()[4])
                    single_sentence.relation.append(line.split()[5])
                    single_sentence.parent.append(line.split()[6])
                else:
                    print("Error in line: ", line)

                query = "SELECT id FROM relations_" + corpus_name + "_strings WHERE string = '" + lemma_escaped + "' AND lemma = '" + lemma_escaped + "';"
                cursor.execute(query)
                if cursor.rowcount == 0:
                    single_sentence.string_id.append(string_id)
                    ### relations_CORPUSNAME_strings - lemma
                    query = "INSERT INTO relations_" + corpus_name + "_strings(id, string, stringextra, pos, lemma) VALUES(%s, %s, %s, %s, %s);"
                    args = (string_id, line.split()[1], "", line.split()[2], line.split()[1])
                    try:
                        cursor.execute(query, args)
                    except:
                        logfile.write('===== error writing in mysql for line \n')
                        logfile.write(line)
                    string_id += 1
                else:
                    for row in cursor:
                        single_sentence.string_id.append(row[0])

                if len(line.split()) == 7:
                    single_sentence.pos.append(line.split()[2])
                    single_sentence.analyses.append(line.split()[3])
                    single_sentence.position.append(line.split()[4])
                    single_sentence.relation.append(line.split()[5])
                    single_sentence.parent.append(line.split()[6])
                else:
                    #print("Error in line: ", line)
                    logfile.write('===== error in line \n')
                    logfile.write(line)
                i += 1

f.close()

id_rel = 0
string_id = 0

print("===== DONE relations_" + corpus_name + "_strings =====")

for sentence in sentences:
    k = 0
    for string in sentence.string:

        try:
            if k % 2 == 0:
                bfhead = False
                wfhead = False
                bfdep = False
                wfdep = False
                if not sentence.parent[k] == '0':
                    head = sentence.string_id[int(sentence.parent[k])*2-2]
                    head_str = sentence.string[int(sentence.parent[k])*2-2]
                    pos_head = int(sentence.parent[k])
                    pos_dep = int(sentence.position[k])
                    dep = sentence.string_id[k]
                    rel = sentence.relation[pos_dep*2-1]
                    dep_str = sentence.string[k]
                    dep_lemma_str = sentence.lemma[pos_dep*2-1]
                    head_lemma_str = sentence.lemma[pos_head*2-1]
                    head_lemma = sentence.string_id[pos_head*2-1]
                    dep_lemma = sentence.string_id[pos_dep*2-1]
                    if (head != dep) and (rel != 'X'):
                        if dep_str.lower() == dep_lemma_str.lower():
                            bfdep = True
                        else:
                            wfdep = True
                        if head_str.lower() == head_lemma_str.lower():
                            bfhead = True
                        else:
                            wfhead = True

                    if wfhead and wfdep:
                        # head_lemma - dep_wordform
                        id_rel = insert_rel(id_rel, head_lemma, rel, dep, True, False, False, True, pos_head, pos_dep, sentence.sentence_id, "1")
                        # head_wordform - dep_lemma
                        id_rel = insert_rel(id_rel, head, rel, dep_lemma, False, True, True, False, pos_head, pos_dep, sentence.sentence_id, "2")
                    if wfhead and bfdep:
                        # head_wordform - dep_lemma
                        id_rel = insert_rel(id_rel, head, rel, dep_lemma, False, True, True, True, pos_head, pos_dep, sentence.sentence_id, "2")
                    elif bfhead and wfdep:
                        # head_wordform - dep_lemma
                        id_rel = insert_rel(id_rel, head, rel, dep_lemma, True, True, True, False, pos_head, pos_dep, sentence.sentence_id, "2")
                    elif bfhead and bfdep:
                        # head_lemma - dep_lemma
                        id_rel = insert_rel(id_rel, head_lemma, rel, dep_lemma, True, True, True, True, pos_head, pos_dep, sentence.sentence_id, "case_4")

                    ### relations_CORPUSNAME_head_rel
                    query_hr = "INSERT INTO relations_" + corpus_name + "_head_rel(head, rel, freq) VALUES(%s, %s, %s) ON DUPLICATE KEY UPDATE freq = freq + 1;"
                    args_hr = (head, rel, 1)
                    cursor.execute(query_hr, args_hr)
                    if wfhead:
                        query_hr = "INSERT INTO relations_" + corpus_name + "_head_rel(head, rel, freq) VALUES(%s, %s, %s) ON DUPLICATE KEY UPDATE freq = freq + 1;"
                        args_hr = (head_lemma, rel, 1)
                        cursor.execute(query_hr, args_hr)

                    ### relations_CORPUSNAME_dep_rel
                    query_dr = "INSERT INTO relations_" + corpus_name + "_dep_rel(dep, rel, freq) VALUES(%s, %s, %s) ON DUPLICATE KEY UPDATE freq = freq + 1;"
                    args_dr = (dep, rel, 1)
                    cursor.execute(query_dr, args_dr)
                    if wfdep:
                        query_dr = "INSERT INTO relations_" + corpus_name + "_dep_rel(dep, rel, freq) VALUES(%s, %s, %s) ON DUPLICATE KEY UPDATE freq = freq + 1;"
                        args_dr = (dep_lemma, rel, 1)
                        cursor.execute(query_dr, args_dr)

                    ### relations_CORPUSNAME_rel
                    query_r = "INSERT INTO relations_" + corpus_name + "_rel(rel, freq) VALUES(%s, %s) ON DUPLICATE KEY UPDATE freq = freq + 1;"
                    args_r = (rel, 1)
                    cursor.execute(query_r, args_r)

        except IndexError:
            logfile.write('===== error in sentence \n')
            logfile.write(str(vars(sentence)))

        k += 1

print('===== DONE =====')

logfile.close()

db.commit()
db.close()
