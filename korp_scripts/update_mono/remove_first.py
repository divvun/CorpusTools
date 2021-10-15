import os, sys

in_dir = sys.argv[1]

out_dir = 'fixed_'+in_dir
cwd = os.getcwd()
out_dir_path = os.path.join(cwd, out_dir)
if not os.path.exists(out_dir_path):
    os.mkdir(out_dir_path)


for root, dirs, files in os.walk(in_dir): # Walk directory tree
    for current_file in files:

        current_out_dir_path = os.path.join(out_dir_path, root)
        print('... processing ', str(current_out_dir_path))
        if not os.path.exists(current_out_dir_path):
            os.makedirs(current_out_dir_path, exist_ok=True)

        cdata = False
        skipped = False
        print("processing ", str(current_file))
        f = open(os.path.join(root, current_file), "r")
        out_f = open(os.path.join(current_out_dir_path, current_file), "w")
        for line in f.readlines():
            if "CDATA[:\\n" in line:
                correct = line.split("CDATA")[0]+"CDATA["
                cdata = True
            else:
                if cdata:
                    skipped = True
                    cdata = False
                else:
                    if skipped:
                        out_f.write(correct + line)
                        skipped = False
                    else:
                        out_f.write(line)
        f.close()
        out_f.close()
