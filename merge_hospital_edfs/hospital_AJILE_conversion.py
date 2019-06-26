"""
Functions to convert between AJILE (midnight to midnight) and hospital time coordinate systems.
"""

import os
os.environ["OMP_NUM_THREADS"] = "1" #avoid multithreading if have Anaconda numpy
import numpy as np
import h5py
import pandas
import glob
from datetime import datetime as dt
from datetime import timedelta
from math import ceil
import natsort
import pandas as pd
import gc
import os
import pdb
from scipy import stats
import matplotlib
matplotlib.use('Agg') #turn off displaying figures
import matplotlib.pyplot as plt

def merge_files_individual_days(patient_id,loadpath,merge_day_start=0):
    """
    Takes preprocessed h5 ECoG files from hospital time and converts them to time where days start/end at midnight instead of arbitrary times. Missing data segments are denoted with NaNs. merge_day_start allows to start off at later merge day (in case of error during one of the merges)
    """
    tmp_path = '/data1/users/stepeter/tmp_for_nas/'+patient_id+'/' #temp directory for merge TXT files
    #Remove any bad files for the merge
    bad_files = list(np.atleast_1d(np.loadtxt(tmp_path+'merge_ignore.txt', delimiter=" ", dtype=np.str)))
    ecog_files_tmp = natsort.natsorted(glob.glob(loadpath+'/processed'+'*.h5'))
    for s,fileIDs in enumerate(bad_files):
        bad_files[s] = loadpath+fileIDs
    ecog_files = natsort.natsorted(list(set(ecog_files_tmp) - set(bad_files)))
#     ecog_files = natsort.natsorted(glob.glob(loadpath+'/processed'+'*.h5'))
    len_ecog_files = len(ecog_files)
    days = []
    for i in range(len_ecog_files):
        days.append(int(ecog_files[i][len(loadpath):].split('_')[-1].split('.')[0])) #extract day from filename
    first_file_day = days[0] #use later for naming AJILE files
    
    #Part I: computes start and end times and which files to merge; merged file indices are saved
    start_times, end_times, true_days_start, true_days_end = [], [], [], []
    for i in range(len_ecog_files):
        #Get data start time
        fin = h5py.File(ecog_files[i],"r")
        #try:
#        pdb.set_trace()
        temp_time=dt.utcfromtimestamp(fin['start_timestamp_nw'][()]) #'start_timestamp'][()])
            
        ms_time = ceil(temp_time.microsecond/1000/2)*2*1000 #round to .002 because using 500 Hz sampling rate
        temp_time = temp_time.replace(microsecond = ms_time)
        #except KeyError:
        #    print('hi')
        #    temp_time=dt.utcfromtimestamp(fin['start_timestamp'][()]) #'start_timestamp'][()])
        start_times.append(temp_time)
        
        #Compute data end time based on data length
        temp_len = len(fin['dataset'][0,:])
        Fs = int(round(fin['f_sample'][()],-2)) #round to nearest 100 (so no worries if f_sample is slightly off from hospital)
        scaled_len = temp_len*(1000/Fs) #scale data length to msec (finest resolution possible)
        end_time_temp = temp_time + timedelta(milliseconds=int(scaled_len))
        end_times.append(end_time_temp)
        
        true_days_start.append(temp_time.day)
        true_days_end.append(end_time_temp.day)
        
    #Obtain unique days (in day, not numeric, order)
    def unique_natorder(in_list):
        unique_list=[]
        for i,val in enumerate(in_list):
            if val not in unique_list:
                unique_list.append(val)
        return unique_list
    
    small_inds = np.nonzero(np.asarray(true_days_start)<true_days_start[0])[0]
    true_days_start_arr = np.asarray(true_days_start)
    true_days_start_arr[small_inds] += max(true_days_start)
    true_days_start = true_days_start_arr.tolist()

    small_inds = np.nonzero(np.asarray(true_days_end)<true_days_end[0])[0]
    true_days_end_arr = np.asarray(true_days_end)
    true_days_end_arr[small_inds] += max(true_days_end)
    true_days_end = true_days_end_arr.tolist()

    unique_days = natsort.natsorted(unique_natorder(true_days_start+true_days_end))
    
    #Decide how to merge the files based on days
    days_np = np.asarray(days)
    merge_inds = [ [] for i in range(len(unique_days)) ]
    day_merge_inds = [ [] for i in range(len(unique_days)) ] #just for output file (saved by day in filename)
    for i in range(len(unique_days)):
        inds_temp_start = np.nonzero(np.asarray(true_days_start)==unique_days[i])[0]
        inds_temp_end = np.nonzero(np.asarray(true_days_end)==unique_days[i])[0]
        #Concatenate arrays in an interleaved order
        inds_temp_all = np.empty((inds_temp_start.size + inds_temp_end.size,), dtype=inds_temp_start.dtype)
        if inds_temp_start.size>inds_temp_end.size:
            inds_temp_all[0::2] = inds_temp_start
            inds_temp_all[1::2] = inds_temp_end
        else:
            inds_temp_all[0::2] = inds_temp_end
            inds_temp_all[1::2] = inds_temp_start
        inds_temp_all = list(inds_temp_all) #np.concatenate((inds_temp_start,inds_temp_end)))
        inds_temp_all_unique = unique_natorder(inds_temp_all)
        merge_inds[i] = inds_temp_all_unique
        day_merge_inds[i] = list(days_np[inds_temp_all_unique])
    
    #Part II: performs merging
    #Pick channels with nonzero variance (and keep labels)
    chan_labels=fin['chanLabels'][()]
    chan_label_array=chan_labels.split(",")
    chan_label_array_final = []
    keep_inds = np.loadtxt(tmp_path+'chan_inds_use.txt').astype('int')
    #keep_inds = np.nonzero(fin['SD_channels'][()]!=0)[1] #keep channels with nonzero variance
    orig_chan_len = fin['SD_channels'][()].shape[1]
    num_chan_labels = len(chan_labels.split(","))
    #Record which channels were kept
    for i in keep_inds:
        if i==0:
            chan_label_array_final.append(chan_labels.split(",")[i][1:].strip()[1:-1])
        elif i==num_chan_labels:
            chan_label_array_final.append(chan_labels.split(",")[i][:-1].strip()[1:-1])
        else:
            chan_label_array_final.append(chan_labels.split(",")[i].strip()[1:-1])
#     chan_label_final = str(chan_label_array_final)
    
    new_days_np = (np.asarray(unique_days)+1-unique_days[0])
    merge_days = [] #List of merge days used for each hospital day
    for day_val in days_np:
        merge_days.append(list(new_days_np[np.nonzero(np.asarray([day_val in sl for sl in day_merge_inds]))[0]])) #days_np[np.nonzero(np.asarray([day_val in sl for sl in day_merge_inds]))[0]]))
    
    #Create merged files, saving h5 files with appropriate information
    curr_day = first_file_day
    merge_day_start = merge_day_start - curr_day #convert merge_day_start to index
    curr_day = curr_day+merge_day_start
    
    #Account for case when file numbering starts after 1
    if merge_day_start<0:
        curr_day+=abs(merge_day_start)
        merge_day_start=0
    
    for i in range(merge_day_start,len(merge_inds)):
        #Case 1: Determine if need to trim ecog data because of late start time (only if first file starts on same day as day currently on)
        start_timestamp_out = 0
        trim_time_start = 0
        if unique_days[i]==start_times[merge_inds[i][0]].day: #avoids case where first merge sbj starts earlier than day of interest
            #Figure out how much time can be trimmed off the start time (save file space)
            start_time_curr = start_times[merge_inds[i][0]]
            start_time_midnight = start_time_curr.replace(hour=0, minute=0,second=0,microsecond=0)
            trim_time_start = (start_time_curr - start_time_midnight).total_seconds()*Fs
            start_timestamp_out = start_time_curr
        #pdb.set_trace()
        ecog_data_final = np.empty([len(keep_inds),int(24*3600*Fs-trim_time_start)]) #Create dataset that is 24 hours long with channels to keep
        ecog_data_final[:] = np.nan #make all missing data NaN
        
        curr_frame_index = 0
        for j in merge_inds[i]:
            #Check if file start or end time goes outside of whole day boundary (which would need to be clipped)
            start_time_curr = start_times[j]
            start_time_midnight = start_time_curr.replace(hour=0, minute=0,second=0,microsecond=0)
            
            print('Loading '+ecog_files[j]+'...')
            fin = h5py.File(ecog_files[j],"r")
            num_chans = fin['dataset'][:,0].shape[0]
            if orig_chan_len==num_chans: #Prevents adding datasets with different numbers of channels
                #Go one channel at a time because of memory constraints
                for chan_ind in range(len(keep_inds)):
                    ecog_data_loaded = fin['dataset'][keep_inds[chan_ind],:]
                    ecog_data_loaded = np.expand_dims(ecog_data_loaded,0)

                    #Make all channel bad indices as NaNs
                    highArtInds=fin['allChanArtifactInds'][()]
                    inFrameInds = np.arange(0,ecog_data_loaded.shape[1])
                    ecog_data_loaded = _changeval_AllChanArtifactInds(highArtInds,ecog_data_loaded,inFrameInds,newValue=float('nan'))

                    #Case 1 (continued)
                    if (trim_time_start>0) and (j==merge_inds[i][0]):
                        #Just add in data if nothing before midnight (cases for size of data relative to rest of day)
                        if ecog_data_loaded.shape[1]>ecog_data_final.shape[1]:
                            ecog_data_final[chan_ind,:] = ecog_data_loaded[0,0:ecog_data_final.shape[1]]
                        else:
                            ecog_data_final[chan_ind,0:ecog_data_loaded.shape[1]]=ecog_data_loaded

                    #Case 2: hospital data starts before midnight
                    elif (j==merge_inds[i][0]) and (unique_days[i]!=start_times[j].day):
                        #Clip off beginning of file to match whole day length
                        start_time_loaded_dat = start_times[j]
                        start_time_midnight = start_time_loaded_dat.replace(hour=0, minute=0,second=0,microsecond=0)
                        start_time_midnight = start_time_midnight + timedelta(days=1) #set to midnight next day
                        trim_time_before_start = (start_time_midnight - start_time_loaded_dat).total_seconds()*Fs
                        out_dat_ind_len = ecog_data_loaded.shape[1] - trim_time_before_start
                        diffLen = len(ecog_data_final[chan_ind,0:int(out_dat_ind_len)]) - len(ecog_data_loaded[0,int(trim_time_before_start):])
                        ecog_data_final[chan_ind,0:(int(out_dat_ind_len)-int(diffLen))]= ecog_data_loaded[0,int(trim_time_before_start):]
                        #ecog_data_final[chan_ind,0:int(out_dat_ind_len)]=ecog_data_loaded[0,int(trim_time_before_start):]  

                        #Add start timestamp, if not already added
                        start_timestamp_out = start_time_midnight

                    #Case 3: hospital data ends after midnight
                    elif (j==merge_inds[i][-1]) and (unique_days[i]!=end_times[j].day):
                        #Clip off end of file to match whole day length
                        end_time_loaded_dat = end_times[j]
                        end_time_midnight = end_time_loaded_dat.replace(hour=0, minute=0,second=0,microsecond=0)
                        trim_time_after_end = (end_time_loaded_dat - end_time_midnight).total_seconds()*Fs
                        out_dat_ind_len = ecog_data_loaded.shape[1] - trim_time_after_end

                        curr_frame_index = ((start_times[j]-start_times[j].replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()*Fs) - trim_time_start
                        #Take difference, in case off by 1 frame
                        diffLen = len(ecog_data_final[chan_ind,int(curr_frame_index):]) - len(ecog_data_loaded[0,:int(out_dat_ind_len)])
                        ecog_data_final[chan_ind,(int(curr_frame_index)+int(diffLen)):]= ecog_data_loaded[0,:int(out_dat_ind_len)]
                        #ecog_data_final[chan_ind,int(curr_frame_index):]=ecog_data_loaded[0,:int(out_dat_ind_len)]

                        #Add start timestamp, if not already added
                        if start_timestamp_out==0:
                            start_timestamp_out = start_times[j]
                            start_timestamp_out = start_timestamp_out.replace(hour=0, minute=0,second=0,microsecond=0)

                    #Case 4: Adding data in middle of the day
                    else:
                        len_loaded_dat = ecog_data_loaded.shape[1]
                        curr_frame_index = ((start_times[j]-start_times[j].replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()*Fs) - trim_time_start
                        diffLen = len(ecog_data_final[chan_ind,int(curr_frame_index):int(curr_frame_index+len_loaded_dat)]) - ecog_data_loaded.shape[1]
                        ecog_data_final[chan_ind,int(curr_frame_index):(int(curr_frame_index+len_loaded_dat)-int(diffLen))]=ecog_data_loaded
                        #ecog_data_final[chan_ind,int(curr_frame_index):int(curr_frame_index+len_loaded_dat)]=ecog_data_loaded

                        #Add start timestamp, if not already added
                        if start_timestamp_out==0:
                            start_timestamp_out = start_times[j]
                            start_timestamp_out = start_timestamp_out.replace(hour=0, minute=0,second=0,microsecond=0)

                fin.close() #Clean up file handle
                del ecog_data_loaded, fin
                gc.collect()
            else:
                merge_days[j] = [] #blank out this for txt file because won't merge this dataset
                print('Discarding '+ecog_files[j]+'...')
                
        #Add start timestamp, if not already added
        if start_timestamp_out==0:
            start_timestamp_out = start_times[merge_inds[i][0]]
            start_timestamp_out = start_timestamp_out.replace(hour=0, minute=0,second=0,microsecond=0)
        
        #Save merged data
        savepath = '/data1/ecog_project/derived/processed_ecog/'+patient_id+'/full_day_ecog/'
        h5_fn = savepath +'/'+patient_id+'_fullday_'+str(curr_day)+'.h5'
        stdVals,kurtVals,d_MADs = _calculate_channel_metrics(ecog_data_final)
        sdThresh=5
        kurtThresh=10
        goodChanInds=_determine_bad_channels(stdVals,kurtVals,sdThresh,kurtThresh)
        tStamp=(start_timestamp_out-dt.utcfromtimestamp(0)).total_seconds()
        
        #Convert data to float32 to save space
        ecog_data_final = np.float32(ecog_data_final)
        
        #Create dataframe for channel info
        col_headers = np.array(['SD_channels','Kurt_channels','standardizeDenoms','goodChanInds']) #,'X_coor','Y_coor','Z_coor'])
#         chan_locs = np.loadtxt(loadpath + patient_id + '_elec_locs_4fullday.txt',delimiter='\t') #3 x N, load channel locations for txt file (locations need to be aligned to channel locations)
#         goodChanInds_final = np.intersect1d(goodChanInds,np.nonzero(chan_locs.mean(axis=0)!=0)[0]) #bad channel if no electrode locations
        goodChan_4df = np.zeros_like(stdVals)
        goodChan_4df[0, goodChanInds] = 1 #goodChanInds_final] = 1
        data_vals = np.concatenate((stdVals,kurtVals,d_MADs,goodChan_4df),axis=0) #, chan_locs[:, keep_inds]),axis=0)
        df = pd.DataFrame(data = data_vals, index=col_headers, columns = chan_label_array_final)

        if os.path.exists(h5_fn):
            os.remove(h5_fn)
        with h5py.File(h5_fn, "w") as fout:
            dset1 = fout.create_dataset("dataset", data=ecog_data_final, chunks=True)
            del ecog_data_final
            gc.collect()
            #dset2 = fout.create_dataset("Kurt_channels", data=kurtVals)
            #dset3 = fout.create_dataset("SD_channels", data=stdVals)
            #dset4 = fout.create_dataset("standardizeDenoms", data=d_MADs)
            #dset5 = fout.create_dataset("chanLabels", data=chan_label_final)
            dset6 = fout.create_dataset("f_sample", data=Fs,dtype="f") #
            #dset7 = fout.create_dataset("goodChanInds", data=goodChanInds)
            dset8 = fout.create_dataset("start_timestamp", data=tStamp)
        
        print('Finished day '+str(curr_day)+'!')
        curr_day+=1 #iterate current day for saving
        fout.close() #Clean up file handle
        del fout

        #Write out channel info
        df.to_hdf(h5_fn,key='chan_info',mode='r+')
        
    #Save text file with merge indices (based on original filename days)
    merge_dict = {'hospital_ind':days, 'merge_days':merge_days, 'hospital_start_time':[pd.Timestamp(j) for j in start_times], 'hospital_end_time':[pd.Timestamp(j) for j in end_times]}
    df = pd.DataFrame(merge_dict)
    df.to_csv(savepath +'/allday_merge_info.txt', index=None) #save without row names
#     np.savetxt(savepath +'/allday_merge_info.txt',day_merge_inds)
        
def _calculate_channel_metrics(data):
    n = data.shape[0]
    stdVals=np.zeros([1,n])
    kurtVals=np.zeros([1,n])
    d_MADs=np.zeros([1,n])
    scale_factor=1.4826
    for i in range(n):
        numerical_inds = np.nonzero(1-np.isnan(data[i,:]).astype('int'))[0] #only use available data
        data_temp = data[i,numerical_inds] 
        stdVals[0,i]=np.std(data_temp)
        kurtVals[0,i]=stats.kurtosis(data_temp)
        d_MADs[0,i] = np.median(np.abs(data_temp))*scale_factor
    return stdVals,kurtVals,d_MADs

def _changeval_AllChanArtifactInds(highArtInds,ecog_data,inFrameInds,newValue=float('nan')):
    #Changes the values of the ECoG data at the marked higher amplitude artifact indices
    #Can specify a numerical value or NaN
    highArtIndsFinal=np.intersect1d(highArtInds,inFrameInds)-inFrameInds[0]
    for i in range(ecog_data.shape[0]):
        ecog_data[i,highArtIndsFinal]=newValue
    return ecog_data

def _determine_bad_channels(sdChans,kurtChans,sdThresh=5,kurtThresh=10):
    #Takes in standard deviations and kurtosis values calculated for each channels
    #Returns the good channel indices (goodChan_ecog_data=dataset[goodChanInds,:])
    
    n=len(sdChans[0])
    #Set thresholds (can adjust if want)
    sdChan_thresh=np.median(sdChans)+sdThresh*stats.iqr(sdChans) #sdThresh*np.std(sdChans) #
    kurtthresh=np.median(kurtChans)+kurtThresh*stats.iqr(kurtChans) #np.std(kurtChans) #
    
    #Looking for channels with SD's well above the rest (and not =0)
    badChanInds_sd=np.array([])
    for i in range(n):
        if sdChans[0,i]>sdChan_thresh or sdChans[0,i]==0:
            badChanInds_sd=np.append(badChanInds_sd,int(i))
    badChanInds_sd=badChanInds_sd.astype(int)
    
    #Determine bad channels from kurtosis
    badChanInds_kurt=np.array([])
    for i in range(n):
        if kurtChans[0,i]>kurtthresh:
            badChanInds_kurt=np.append(badChanInds_kurt,int(i))
    badChanInds_kurt=badChanInds_kurt.astype(int)

    #Combine bad channels from both methods
    badChannelsAll=np.array([])
    badChannelsAll=np.append(badChannelsAll,badChanInds_sd)
    badChannelsAll=np.append(badChannelsAll,badChanInds_kurt)
    badChannelsAll=np.unique(badChannelsAll)
    badChannelsAll=badChannelsAll.astype(int)
    print('Found '+str(len(badChannelsAll))+' bad channels!')
    goodChanInds=np.setdiff1d(np.arange(1,n),badChannelsAll)
    return goodChanInds

def plot_merged_data(patient_id,loadpath,merge_day_start=0):
    """
    Produces downsampled plot of merged data. Helps visualize where breaks are occuring in data, so can manually check with hospital times.
    """
    ecog_files = natsort.natsorted(glob.glob(loadpath+'/'+patient_id+'_fullday*.h5'))
    len_ecog_files = len(ecog_files)
    days = []
    for i in range(len_ecog_files):
        days.append(int(ecog_files[i][len(loadpath):].split('_')[-1].split('.')[0])) #extract day from filename
    
    merge_day_start = merge_day_start - days[0]
    for i in range(merge_day_start,len_ecog_files):
        #Get data start time
        fin = h5py.File(ecog_files[i],"r")
        fig, ax1 = plt.subplots(1, 1, figsize=(10,6))
        n_channels = len(fin['dataset'][:,0])
        len_data_time = len(fin['dataset'][0,:])
        Fs = fin['f_sample'][()]
        #Plot one channel (just to see breaks)
        downsample_factor = 4*Fs
        t = np.arange(0, len_data_time, int(downsample_factor))/Fs/3600 #Convert to hours
        print('loading one channel...')
        sigbufs = np.zeros([1, len_data_time])
        sigbufs[0,:] = fin['dataset'][2,:]
        ax1.plot(t,sigbufs[0,0:-1:int(downsample_factor)]) #plot downsampled data
        ax1.set_title('Raw data')
        plt.figure(fig.number) #set current plot (for saving)
        plt.savefig(loadpath+'/Data_trace'+patient_id+'_fullday'+str(days[i])+'.png', bbox_inches='tight')
        plt.close(fig)
                

def hospital_2_AJILE(intime,patient,AJILE_day):
    
    return hospital_time
    
def AJILE_2_hospital(intime,patient,hospital_day):
    
    return AJILE_time
