#!/bin/sh
python upload_glacier.py -t edf -td /data2/users/stepeter/ -d /data2/users/hmc/edf/df5c5206/ > df5c5206.txt
rm /data2/users/stepeter/df5c5206_edf.tar.gz.enc
python upload_glacier.py -t edf -td /data2/users/stepeter/ -d /data2/users/hmc/edf/ec761078_pt1/ > ec761078_pt1.txt
rm /data2/users/stepeter/ec761078_pt1_edf.tar.gz.enc
python upload_glacier.py -t edf -td /data2/users/stepeter/ -d /data2/users/hmc/edf/ec761078_pt2/ > ec761078_pt2.txt
rm /data2/users/stepeter/ec761078_pt2_edf.tar.gz.enc
python upload_glacier.py -t edf -td /data2/users/stepeter/ -d /data2/users/hmc/edf/f482a8c0_pt1/ > f482a8c0_pt1.txt
rm /data2/users/stepeter/f482a8c0_pt1_edf.tar.gz.enc
python upload_glacier.py -t edf -td /data2/users/stepeter/ -d /data2/users/hmc/edf/f482a8c0_pt2/ > f482a8c0_pt2.txt
rm /data2/users/stepeter/f482a8c0_pt2_edf.tar.gz.enc

python upload_glacier.py -t vid -td /data2/users/stepeter/ -d /data2/users/hmc/video/df5c5206/ > df5c5206.txt
rm /data2/users/stepeter/df5c5206_vid.tar.gz.enc
python upload_glacier.py -t vid -td /data2/users/stepeter/ -d /data2/users/hmc/video/ec761078_pt1/ > ec761078_pt1.txt
rm /data2/users/stepeter/ec761078_pt1_vid.tar.gz.enc
python upload_glacier.py -t vid -td /data2/users/stepeter/ -d /data2/users/hmc/video/ec761078_pt2/ > ec761078_pt2.txt
rm /data2/users/stepeter/ec761078_pt2_vid.tar.gz.enc
python upload_glacier.py -t vid -td /data2/users/stepeter/ -d /data2/users/hmc/video/ec761078_pt3/ > ec761078_pt3.txt
rm /data2/users/stepeter/ec761078_pt3_vid.tar.gz.enc
python upload_glacier.py -t vid -td /data2/users/stepeter/ -d /data2/users/hmc/video/ec761078_pt4/ > ec761078_pt4.txt
rm /data2/users/stepeter/ec761078_pt4_vid.tar.gz.enc
python upload_glacier.py -t vid -td /data2/users/stepeter/ -d /data2/users/hmc/video/f482a8c0_pt1/ > f482a8c0_pt1.txt
rm /data2/users/stepeter/f482a8c0_pt1_vid.tar.gz.enc
python upload_glacier.py -t vid -td /data2/users/stepeter/ -d /data2/users/hmc/video/f482a8c0_pt2/ > f482a8c0_pt2.txt
rm /data2/users/stepeter/f482a8c0_pt2_vid.tar.gz.enc
python upload_glacier.py -t vid -td /data2/users/stepeter/ -d /data2/users/hmc/video/f482a8c0_pt3/ > f482a8c0_pt3.txt
rm /data2/users/stepeter/f482a8c0_pt3_vid.tar.gz.enc