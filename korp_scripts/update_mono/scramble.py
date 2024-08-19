#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import random
import sys
from imp import reload
from random import shuffle
from subprocess import PIPE, Popen


def main():
    in_dir = sys.argv[1]
    print(in_dir)
    out_dir = in_dir + "_out"

    cwd = os.getcwd()
    out_dir_path = os.path.join(cwd, out_dir)

    if not os.path.exists(out_dir_path):
        os.mkdir(out_dir_path)

    for root, dirs, files in os.walk(in_dir): 
        for current_file in files:
            block_sent = {}
            print('Processing: ', os.path.join(root,current_file))
            current_out_dir_path = os.path.join(out_dir_path, root)

            if not os.path.exists(current_out_dir_path):
                os.makedirs(current_out_dir_path, exist_ok=True)

            gr_cmd = "grep 'sentence id' " + os.path.join(root, current_file) + " | wc -l"
            p = Popen(gr_cmd, shell=True, stdout=PIPE, stderr=PIPE)
            gr_out, gr_err = p.communicate()
            f_in = open(os.path.join(root, current_file), "r")
            f_out = open(os.path.join(current_out_dir_path, str(current_file)), "a")
            tot_sent = random.sample(range(1, int(gr_out)+1), int(gr_out))
            i = 1
            j = 0
            first_line = ""
            for line in f_in.readlines():
                if "<text" in line:
                    first_line = line
                if "<text" not in line and "sentence" not in line and "</text" not in line:
                    if block_sent.get(j):
                        block_sent[j].append(line)
                    else:
                        block_sent[j] = [line]
                if  "sentence id" in line:
                    j += 1

            values = list(block_sent.values())
            shuffle(values)
            shuffled = dict(zip(block_sent, values, strict=False))
            f_out.write(first_line)
            for key, value in shuffled.items():
                f_out.write('<sentence id="' + str(i) + '">\n')
                f_out.write("".join(value))
                f_out.write("</sentence>\n")
                i += 1
            f_out.write("</text>")

            f_out.close()
            f_in.close()


if __name__ == "__main__":
    reload(sys)
    main()
