import subprocess
import getpass
import argparse
import os
import pdb

def upload_glacier(dir, tmp_dir, passwd, type):
    if dir[-1]=='/':
        dir=dir[:-1]
    save_file = "%s_%s.tar.gz.enc" % ("/".join([tmp_dir, dir.split("/")[-1]]), type)
    if not os.path.exists(save_file):
        subprocess.call("tar zcvf - %s | openssl enc -e -des -out %s -k %s" %(dir, save_file,  passwd), shell=True)
    try:
        subprocess.call("glacier-cmd upload ecog-video %s" % save_file, shell=True)
    except:
        return 1
    return 0 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', required=True, help="Directory of data to be uploaded (patient dir, video or edf)")
    parser.add_argument('-t', '--type', required=True, help="Type of data to be stored (vid or edf)")
    parser.add_argument('-td', '--tmp_dir', required=True, help="Temporary data storage location, needs to be able to handle a big file, at least 30GB")
    pass_flag = 0
    upload_flag = 1
    while pass_flag == 0:
        password = getpass.getpass()
        password2 = getpass.getpass()
        if not password == password2:
            print("passwords do not match, try again")
        else:
            pass_flag = 1
    args = parser.parse_args()
    while upload_flag:
        upload_flag = upload_glacier(args.dir, args.tmp_dir, password, args.type)

