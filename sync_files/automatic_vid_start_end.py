import glob
from datetime import datetime as dt
from dateutil import tz
from datetime import timedelta as td
import numpy as np
import os
import natsort
import csv
import pdb

#Open VTC .txt file
subjects2use = ['a0f66459', 'ab2431d9', 'c95c1e82', 'd6532718', 'e5bad52f', 'ec374ad0', 'fcb01f7a', 'c7980193', 'cb46fd46', 'd7d5f068', 'e70923c4', 'f64993a3', 'ffb52f92', 'a86a4375'] 
for subject in subjects2use:
    print('Processing for '+subject)
    # subject = 'a0f66459'

    vtc_lp = '/data1/users/stepeter/videos_timestamp_test/manyVTCfiles/'
    snc_lp = '/data1/users/stepeter/videos_timestamp_test/manySNCfiles/'
    save_file = '/data2/ecog_project/derived/vid_start_end_new/'+subject+'.csv'

    #Determine which days to use
    fname_vtc = natsort.natsorted(glob.glob(vtc_lp + subject +'/'+subject+'_*.txt'))
    days_vtc=[]
    for file_ID in fname_vtc:
        days_vtc.append(file_ID[(len(vtc_lp)+len(subject)+1):-4])

    fname_snc = natsort.natsorted(glob.glob(snc_lp + subject +'/'+subject+'_*.txt'))
    days_snc=[]
    for file_ID in fname_snc:
        days_snc.append(file_ID[(len(snc_lp)+len(subject)+1):-4])
    days = natsort.natsorted(list(set(days_vtc).intersection(days_snc)))
    
    vtc_start_times_all, vid_file_names_all = [], []
    for day in days:
        print(day)
        fname = glob.glob(vtc_lp + subject+'/'+ day + '.txt')[0]
        with open(fname) as f:
            content = f.readlines()
        
        content = [x.strip() for x in content]

        #Read in VTC timestamps and convert from UTC to pacific timezone (with DST correction)
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz('America/Los_Angeles')
        vtc_start_times, vtc_vid_number = [], []
        for i in np.arange(10,len(content)):
            if content[i]!='':
                start_time_cur = content[i].split('[')[1][:-2]
                start_time_cur_dt = dt.strptime(start_time_cur, '%d/%m/%Y %H:%M:%S.%f')

                # Tell the datetime object that it's in UTC time zone since 
                # datetime objects are 'naive' by default
                start_time_cur_dt = start_time_cur_dt.replace(tzinfo=from_zone)

                # Convert time zone
                pacific = start_time_cur_dt.astimezone(to_zone)
                vtc_start_times.append(pacific)
                vtc_vid_number.append(content[i].split('[')[0][-9:-5])


        #Open SNC .txt file
        fname = glob.glob(snc_lp + subject +'/'+ day + '.txt')[0]
        with open(fname) as f:
            content_snc = f.readlines()

        content_snc = [x.strip() for x in content_snc]

        #Read in SNC corrections and timestamps
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz('America/Los_Angeles')
        snc_timestamps, snc_corrections = [], []
        prev_timestamp = int(content_snc[8].split('\t')[-1])
        prev_timeDiff = int(content_snc[8].split('\t')[0])
        for i in np.arange(8,len(content_snc)):
            curr_timestamp = int(content_snc[i].split('\t')[-1])
            curr_timeDiff = int(content_snc[i].split('\t')[0])
            orig_time = int((int(curr_timestamp)/1e4)-11644473600000)/1e3
            utc_time = dt.utcfromtimestamp(orig_time)
            utc_time = utc_time.replace(tzinfo=from_zone)
            pacific_time = utc_time.astimezone(to_zone)
            snc_timestamps.append(pacific_time)

            correction = (curr_timestamp-prev_timestamp)/1e7 - (curr_timeDiff-prev_timeDiff)/1e3
            snc_corrections.append(round(correction,3))


        #Perform SNC correction on VTC timestamps
        #Find maximum SNC timestamp that precedes each VTC timestamp
        for s in range(len(vtc_start_times)):
            timestamp_diffs = []
            for i in range(len(snc_timestamps)):
                diff_btwn_stamps = (vtc_start_times[s]-snc_timestamps[i]).total_seconds()
                if diff_btwn_stamps<0:
                    diff_btwn_stamps = 1e7
                timestamp_diffs.append(diff_btwn_stamps)
            # for start_time in vtc_start_times:
            correctionInd2use = np.argmin(np.asarray(timestamp_diffs))

            vtc_start_times[s] = vtc_start_times[s]-td(seconds=snc_corrections[correctionInd2use])
        
        if len(vtc_start_times)>0:
            print(vtc_start_times[s])

        curr_vid_file_names = []
        for i in range(len(vtc_start_times)):
            curr_vid_file_names.append(day+ '_' +vtc_vid_number[i]+'.avi')

        vtc_start_times_all.extend(vtc_start_times)
        vid_file_names_all.extend(curr_vid_file_names)

    #Write results to csv file
    if os.path.exists(save_file):
        os.remove(save_file)
    with open(save_file, mode='w') as vid_start_end_file:
        vid_start_end_writer = csv.writer(vid_start_end_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for i in range(len(vtc_start_times_all)):
            vid_start_end_writer.writerow([vid_file_names_all[i], vtc_start_times_all[i].year, vtc_start_times_all[i].month, vtc_start_times_all[i].day, vtc_start_times_all[i].hour, vtc_start_times_all[i].minute, vtc_start_times_all[i].second, vtc_start_times_all[i].microsecond])
