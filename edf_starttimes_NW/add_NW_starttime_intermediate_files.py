#Read in NW exported .txt and determine start times automatically (with ms resolution)
import os
import numpy as np
import h5py
import argparse
from datetime import datetime as dt
import pdb
import glob
import natsort

def main(loadpath,sbj):
    #loadpath = '/data1/users/stepeter/NW_start_times/'
    #sbj = 'a0f66459'
    #day = '1'

    ecog_files = natsort.natsorted(glob.glob(loadpath+sbj+'/'+sbj[0:3]+"_*.txt"))
    days = []
    for fileID in ecog_files:
        days.append(fileID.split('_')[-1].split('.')[0])

    for day in days:
        f = open(loadpath+sbj+'/'+sbj[0:3]+'_'+day+'.txt', "r", encoding = "utf-16")
        all_secs = []
        t_vals = []
        date_vals = []
        for line_val in f:
            t_val = line_val[11:19]
            all_secs.append(t_val[-2:])
            t_vals.append(t_val)
            date_vals.append(line_val[0:10])
        
        all_secs = [x for x in all_secs if x.isdigit()] #remove any non-numerical input
        diff_vals = np.nonzero(np.diff(np.asarray(all_secs).astype('int'))!=0)[0]
#        first_val_secs_count = len(np.nonzero(np.asarray(all_secs)==all_secs[0])[0])
#        second_val_secs_count = len(np.nonzero(np.asarray(all_secs)==all_secs[first_val_secs_count])[0])
#        pdb.set_trace()
        us_val = int(round((1-(diff_vals[0]/(diff_vals[1]-diff_vals[0])))*1e6,-3)) #first_val_secs_count/second_val_secs_count))*1e6,-3))

#        print('Start time for '+sbj+'_'+day+': '+t_vals[0]+'.'+str(int(us_val/(1e3))))

        ecog_lp = "/data1/ecog_project/derived/processed_ecog/"+sbj+"/preproc_hospital_ecog/processed_"+sbj+"_"+day+".h5"
        
        if os.path.isfile(ecog_lp):
            print('Start time for '+sbj+'_'+day+': '+t_vals[0]+'.'+str(int(us_val/(1e3))))
            fin = h5py.File(ecog_lp,'r+')
            edf_ts = dt.utcfromtimestamp(fin['start_timestamp'][()])
            NW_ts = dt.utcfromtimestamp(fin['start_timestamp'][()])
            #pdb.set_trace()
            NW_ts = NW_ts.replace(year=int(date_vals[0][6:10]), month=int(date_vals[0][0:2]), day=int(date_vals[0][3:5]), hour=int(t_vals[0][0:2]), minute=int(t_vals[0][-5:-3]), second=int(t_vals[0][-2:]), microsecond=us_val) #NW_ts.replace(minute=int(t_vals[0][-5:-3]), second=int(t_vals[0][-2:]), microsecond=us_val)
            NW_ts_secs = (NW_ts-dt.utcfromtimestamp(0)).total_seconds()
            diff_secs = (fin['start_timestamp'][()]-NW_ts_secs) #(edf_ts-NW_ts).total_seconds()
            print((NW_ts-dt.utcfromtimestamp(0)).total_seconds())
            print(fin['start_timestamp'][()])
            if (abs(diff_secs)<2):
                e = "/start_timestamp_nw" in fin
                if e:
                    del fin['start_timestamp_nw']
                NW_ts_secs = (NW_ts-dt.utcfromtimestamp(0)).total_seconds()
               # pdb.set_trace()
                fin.create_dataset("start_timestamp_nw", data=NW_ts_secs)
            else:
                print('New start time is >2 sec from EDF start time! NOT SAVING RESULT!')
            fin.close()
        else:
            print(' ')
            print('Skipping day '+day)
            print(' ')

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-lp','--loadpath',required=True,help='NW export file loadpath')
    parser.add_argument('-s','--sbj',required=True,help='subject ID to analyze')
    args = parser.parse_args()

    main(args.loadpath,args.sbj)
