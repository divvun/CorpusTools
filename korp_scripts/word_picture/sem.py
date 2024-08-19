#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
This is a tentative script to add sem tags in the wordpicture.
It creates a new vrt from the input one, checks if lemma has pos N and Sem/xxx in the analysis and adds a new line with lemma the Sem/xxx tag.
It also replaces all tags in:
subj = ['SUBJ→', '←SUBJ', '-FSUBJ→']
obj = ['OBJ→', '←OBJ', '-FOBJ→', '-F←OBJ']
with SUBJ and OBJ respectively.

The result is a .out file, but by running the wordpicture scripts with this the wordpicture doesn't work properly.
Might be bacause then the 2 copora (the original vrt by which the Kwic is generated and the new .out by which the wordpicture is generated do not match in terms of tokens).
'''

import re
import sys

infile_n = sys.argv[1]
infile = open(infile_n, 'r')
outfile = open(infile_n + '.sem', 'a')

lines = infile.readlines()

subj = ['SUBJ→', '←SUBJ', '-FSUBJ→']
obj = ['OBJ→', '←OBJ', '-FOBJ→', '-F←OBJ']
cnt = 0
cnt_sem = 0
cnt_set = 0
text_num = 0
cnt_a = []
cnt_d = {}
idx_sem = {}

def check_position(val_head, val_dep, val_line, val_idx_sem):
    if val_dep >= val_idx_sem[1][1]:
        cnt_mid = 0
        for key, value in val_idx_sem.items():
            if val_head > value[0] and val_dep < value[1]:
                cnt_mid += 1
        if cnt_mid > 0:
            val_line[6] = str(val_dep + cnt_mid) + '\n'
        else:
            if val_dep < val_head:
                if val_dep == val_head - 1 and "Sem_" not in val_line[3]:
                    val_line[6] = str(val_dep + cnt_sem) + '\n'
                else:
                    val_line[6] = str(val_dep + cnt_sem - 1) + '\n'
            else:
                val_line[6] = str(val_dep + cnt_sem) + '\n'
    return val_line

print('Processing ...')
for line in lines:
    if not line.startswith('<'):
        line_split = re.split(r'\t+', line.rstrip('\t'))
        line_new = line_split
        head = int(line_split[4])
        dep = int(line_split[6])
        pos = line_split[2]
        analysis = line_split[3]
        if pos == 'N' and 'Sem_' in analysis:
            cnt_sem += 1
            cnt += 1
            idx_sem[cnt_sem] = [head, dep]
            line_orig = line_split
            if cnt_sem == 1:
                line_orig[4] = str(head)
            else:
                line_orig[4] = str(head + cnt_sem - 1)
            line_orig = check_position(head, dep, line_orig, idx_sem)
            line_orig_a = '\t'.join(line_orig)
            outfile.write(line_orig_a)
            sem = re.findall(r'Sem_[a-zA-Z]*', analysis)
            sem = '/'.join(sem)
            line_new[1] = sem
            line_new[4] = str(head + cnt_sem)
            line_new = check_position(head, dep, line_new, idx_sem)
            line_new_s = '\t'.join(line_new)
            outfile.write(line_new_s)
            cnt += 1
        else:
            if cnt_sem > 0:
                line_new[4] = str(head + cnt_sem)
                line_new = check_position(head, dep, line_new, idx_sem)
            line_new_s = '\t'.join(line_new)
            outfile.write(line_new_s)
            cnt += 1
    else:
        if cnt != 0:
            cnt_a.append(cnt)
        if line.startswith('<text'):
            if text_num != 0:
                cnt_d[text_num] = cnt_set
            cnt_set = 0
            text_num += 1
        if line.startswith('<sentence'):
            cnt_set += 1


        cnt = 0
        cnt_sem = 0
        idx_sem = {}
        outfile.write(line)

cnt_d[text_num] = cnt_set

k = 1
shift = cnt_d[1]
text_tokens = 0
text_tokens_a = []
for i in range(0, len(cnt_a)):
    if i<shift:
        text_tokens += cnt_a[i]
        if i == len(cnt_a)-1:
            text_tokens_a.append(text_tokens)
    else:
        text_tokens_a.append(text_tokens)
        if i == shift:
            text_tokens = cnt_a[i]
        k += 1
        shift += cnt_d[k]

outfile.close()
print('Done writing!')

print('Updating tokens per sentence and replacing SUBJ, OBJ ...')
outfile = open(infile_n + '.sem', 'r')
outf = open(infile_n + '.out', 'a')


lines = outfile.readlines()
i = 0
k = 0
for line in lines:
    if 'sentence id' in line and 'token_count' in line and i<len(cnt_a):
        new = line.split('token_count')[0] + 'token_count="' + str(cnt_a[i]) + '">' + '\n'
        outf.write(new)
        #outf.write(line)
        i += 1
    else:
        if not line.startswith('<'):
            line_split = re.split(r'\t+', line.rstrip('\t'))
            if line_split[5] in subj:
                line_split[5] = 'SUBJ'
            if line_split[5] in obj:
                line_split[5] = 'OBJ'
            line_new = '\t'.join(line_split)
            outf.write(line_new)
        else:
            if line.startswith('<text'):
                part1 = line.split('token_count="')[0]
                new = str(part1) + 'token_count="' + str(text_tokens_a[k]) + '">\n'
                k += 1
                outf.write(new)
            else:
                outf.write(line)
print('Done updating tokens and replacing SUBJ, OBJ!')

outf.close()
outfile.close()
infile.close()
