import os
import glob
import pdb
import codecs
import argparse


def extract_orig_name(loc, name, id ):
    print(loc)
    file = glob.glob(loc + "*.vt2")[0]
    with open(file, "rb") as f:
        line = f.read()
        result_start = line.find(str.encode(name))
        result_end = line.find(str.encode(".avi"))
#     with codecs.open(file, "r") as infile:
#         line = infile.readline()
#         result_start = line.find(name)
#         result_end = line.find(".avi")
    return line[result_start:result_end-5].decode()


def main(dir_path,last_name,mode):
    for d in glob.glob(dir_path + "*"):
        if not (d[-4:]=="misc") and not (d[-7:]=="cinepak") and not (d[-5:] == "other"):
            print(d)
            orig_name = extract_orig_name(d + "/", last_name, d.split("/")[-1])
            for f in glob.glob(d + "/*"):

                if len(orig_name) > 0:
                    if not (f[-3:] == "avi") and not (f[-3:]=="erd") and f[-5]=="_":
                            print(f)
                            new_f = f[:-5] + f[-4:]
                    else:
                            new_f = f
                    parent, base = os.path.split(new_f)
                    grandparent, id = os.path.split(parent)
                    if mode=="i":
                            new_name = base.replace( orig_name, id )
                    elif mode=="d":
                            new_name = base.replace( id, orig_name )
                    else:
                            print("Incorrect mode")
                            return
                    os.rename(f, parent + "/" + new_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir_path', required=True, help="Main directory that the files are in")
    parser.add_argument('-n', '--last_name', required=True, help="Last name of patient")
    parser.add_argument('-m', '--mode', required=True, help="i for name -> id and d for id -> name")
    args = parser.parse_args()
    main(args.dir_path,args.last_name,args.mode)

