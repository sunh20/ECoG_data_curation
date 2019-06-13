import hashlib, binascii
import os
import sys
import glob
import re
import pdb
#from pyESig2.util.error import *

def generate_id(sbj_id_raw):
    dk = hashlib.pbkdf2_hmac('sha256', sbj_id_raw.encode('utf-8'), os.urandom(8), 8)
    while not(binascii.hexlify(dk)[0:1].isalpha()):
        dk = hashlib.pbkdf2_hmac('sha256', sbj_id_raw.encode('utf-8'), os.urandom(8), 8)
    sbj_id = binascii.hexlify(dk)[:8]
    return sbj_id.decode("utf-8")

def main():
    if not(len(sys.argv) == 3 or len(sys.argv) == 4):
        raise varError("Arguments should be <File path> <Subject last name>\
 <sbj_id or NONE>")
    file_loc = sys.argv[1]
    sbj_id_raw = sys.argv[2]
    if len(sys.argv)==4:
        sbj_id = sys.argv[3]
    else:
        sbj_id = generate_id(sbj_id_raw)

    print(sbj_id)
    # Change filename
    for f in glob.glob(file_loc + '*' + sbj_id_raw + '*//*//*'):
        (parent, filename) = os.path.split(f)
        day = re.search( r'[0-9]{1,2}$', os.path.split(parent)[1]).group()
        name, ext = os.path.splitext(filename)
        ind = re.search( r'_[0-9]{3,4}$', name)
        
        if ext in [".etc", ".avi", ".erd"] and ind is not None:
            ext = ind.group() + ext
        if ext == ".doc":
            ext = name[-25:] + ext
         
        os.rename(f, parent + "//" + sbj_id + '_' + day + ext)
    #Change filenames for Decimated folders as well
    for f in glob.glob(file_loc + '*' + sbj_id_raw + '*//*//*//*'):
        (parent, filename) = os.path.split(f)
        day = re.search( r'[0-9]{1,2}$', os.path.split(parent)[1]).group()
        name, ext = os.path.splitext(filename)
        ind = re.search( r'_[0-9]{3,4}$', name)
        
        if ext in [".etc", ".avi", ".erd"] and ind is not None:
            ext = ind.group() + ext
        if ext == ".doc":
            ext = name[-25:] + ext
         
        os.rename(f, parent + "//" + sbj_id + '_' + day + ext)
    # Change subdir
    for f in glob.glob(file_loc + '*' + sbj_id_raw + '*//*'):
        (parent, filename) = os.path.split(f)
        day = re.search( r'[0-9]{1,2}$', filename).group()
        filename = sbj_id + '_' + day
        os.rename(f, parent + "//" + filename)

    # Change dir

    (parent, filename) = os.path.split(file_loc + sbj_id_raw)
    filename = sbj_id
    #pdb.set_trace()
    os.rename(file_loc+ sbj_id_raw, parent + "//" + filename)

if __name__ == "__main__":
    #sys.argv = ['', 'E://', 'Ball']
    sys.argv = ['', '/data2/users/hmc/','Thacker'] # '#####'] #replace ##### with subject's last name
    main()
