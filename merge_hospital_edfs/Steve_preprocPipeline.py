import os
os.environ["OMP_NUM_THREADS"] = "1" #avoid multithreading if have Anaconda numpy
import numpy as np
import pyedflib
from scipy import stats
from scipy import signal
import mne
import h5py
import os
import matplotlib
matplotlib.use('Agg') #turn off displaying figures
import matplotlib.pyplot as plt
import argparse
import gc
from datetime import datetime as dt
import pdb
    
def remove_large_artifacts_plus_filtering(patient_code,day,data_dir,savepath,ajileFormat=True):
    #Remove high amplitude artifacts and filter data
    
    #Load the data (change path if loading ajile format)
    if ajileFormat==True:
        ecog_fn = data_dir + "/purged_" + patient_code + "_day_" + str(day) + ".edf"
    else:
        ecog_fn = data_dir + "/" + patient_code + "_"+str(day)+".edf"
    print(ecog_fn)
    
    f = pyedflib.EdfReader(ecog_fn) # open the file

    #Get data information
    n = f.signals_in_file #number of data channels
    signal_labels = f.getSignalLabels()
    Fs=int(round(f.samplefrequency(1),-2)) #round to nearest 100 (so no worries if f_sample is slightly off from hospital)
    if Fs==300:
        Fs = 256
    downsample=int(Fs/500) #downsample factor
    if downsample<1:
        downsample = 1 #no downsampling if srate is too low (<500 Hz already)

    highArtInds_final=_determine_high_amplitude_artifact_inds(f,n,signal_labels) #remove high amplitude artifacts
    numBadPoints=len(highArtInds_final)

    #Read in the data, remove high drift artifact, and filter (then save the result)
    h5_fn=savepath+'processed_' + patient_code + '_' + str(day) + '.h5'
    _filter_resample_ecog(h5_fn,f,Fs,downsample,highArtInds_final,signal_labels,n,patient_code,day,numBadPoints,savepath)
    print('Done with filtering! :)')

    #Clean up file handle
    f._close()
    gc.collect()   

def common_median_reference_plus_channel_measures(patient_code,day,data_dir,savepath,ajileFormat=True):
    ##Load the data
    tstep=1000000 #window size to use for reref and bad data detection
    fin = h5py.File(savepath+'processed_' + patient_code + '_' + str(day) + '.h5',"r+")
    Fs=fin['f_sample'][()]
    highArtInds_final=fin['allChanArtifactInds'][()]
    Nsamples=int(len(fin['dataset'][0,:]))
    n=int(len(fin['dataset'][:,0])) #number of data channels
    Nbins=int(Nsamples/tstep)

    #Determine common median reference pattern from edf file (has electrode names)
    #This first part finds the electrode group names
    signal_labels=_add_signal_labels(data_dir,ajileFormat,fin,patient_code,day)
    gridGroupList=_electrode_group_indices(signal_labels)
    
    #Pull out small time windows of data, re-reference, and place them into new dataset
    _rereference_time_chunks(fin,Nbins,tstep,gridGroupList)
    print('Done with re-referencing!')
    
    #Calculate bad channel measures and standardization factor
    print('determining bad channels...')
    stdVals,kurtVals,d_MADs = _calculate_channel_metrics(fin,n,Nsamples)
    
    #Determine which channels are bad
    sdThresh=5
    kurtThresh=10
    goodChanInds=_determine_bad_channels(stdVals,kurtVals,sdThresh,kurtThresh)
    dset9 = fin.create_dataset("goodChanInds", data=goodChanInds)
    
    #Determine outlier frames at each channel (very basic, can be improved upon)
    #print('determining outlier frames...')
    #data=np.zeros([1,Nsamples])
    #iqrThreshold=20 #focus on flagging the worst artifacts
    #e = "/outlierFrameInds" in fin
    #if e:
    #    del fin['outlierFrameInds']
    #grp=fin.create_group('outlierFrameInds')
    #for i in range(n):
    #    outlierVals=[]
    #    data[0,:] = fin['dataset'][i,:]
    #    outlierVals=_flag_outlier_frames(data,iqrThreshold)
    #    grp.create_dataset(str(i),data=outlierVals)
    
    
    tStamp=_add_start_timestamp(data_dir,fin,ajileFormat,patient_code,day) #add starting timestamp to saved file
    
    #Clean up file handle
    fin.close()
    del fin


    
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

def _add_bad_border_window(highArtInds,datLength,badBorderDuration):
    #Try faster bad border window
    highArtInds_copy=np.copy(highArtInds)
    currentInd=0
    currLengthHighArtInds=len(highArtInds)
    highArtInds_final=np.array([])
    while currentInd<currLengthHighArtInds:
        print(highArtInds_copy[currentInd])
        overlapInds=np.where(np.logical_and(highArtInds_copy<(highArtInds_copy[currentInd]+(badBorderDuration/2)),(highArtInds_copy>highArtInds_copy[currentInd]))) #Do half window to encompass all windows
        #Delete overlapping indices
        highArtInds_copy=np.delete(highArtInds_copy,overlapInds[0][0:-2])

        #Add in bad window indices
        highArtInds_final=np.append(highArtInds_final,np.arange(highArtInds_copy[currentInd]-badBorderDuration,highArtInds_copy[currentInd]+badBorderDuration))
        #Update variables
        currentInd=currentInd+1
        currLengthHighArtInds=len(highArtInds_copy)
        print(len(highArtInds_copy))

    highArtInds_final=np.unique(highArtInds_final)
    highArtInds_final=highArtInds_final[highArtInds_final>-1]
    highArtInds_final=highArtInds_final[highArtInds_final<datLength]
    highArtInds_final=highArtInds_final.astype(int)

    del highArtInds
    del highArtInds_copy
    gc.collect()
    return highArtInds_final

def _flag_outlier_frames(data,iqrThreshold=50):
    #Removes bad data frames for one channel based on a threshold determined by the IQR
    #Returns indices for the outliers
    artThresh=iqrThreshold*stats.iqr(data) #set artifact threshold
    signalMag=np.absolute(data)
    #Find values above this threshold and set to 0
    highArtInds_temp=np.nonzero(signalMag > artThresh)
    highArtInds=highArtInds_temp[1]
    datLength=data.shape[1]
    badBorderDuration=500 #1 second
    highArtInds_final=_add_bad_border_window(highArtInds,datLength,badBorderDuration) #use bad border duration window to flag edges
    return highArtInds_final

def _determine_high_amplitude_artifact_inds(f,n,signal_labels):
    #Removes high amplitude artifact occurring across all channels
    #Read in the data and calculate mean signal magnitude across channels
    #Inputs: f is loaded edf file, n is number of channels, signal_labels are channel labels
    sigbufs = np.zeros((1, f.getNSamples()[0]))
    signalMag = 0*np.copy(sigbufs)
    for i in range(n):
        print("loading " + str(i) + ", signal: " + signal_labels[i])
        sigbufs = f.readSignal(i)
        sigbufs = sigbufs-np.median(sigbufs) #subtract off median
        signalMag = signalMag + np.absolute(sigbufs) #add up signal magnitudes
    del sigbufs
    gc.collect()
    signalMag/=n #convert to average

    #Artifact removal parameters
    print("High amplitude artifact removal...")
    numIQRthresh=50 #number of IQR's above average signal magnitude to mark as bad
    badBorderDuration=2000 #number of data points to left and to right of bad data points

    #Set artifact threshold
    artThresh=numIQRthresh*stats.iqr(signalMag)

    #Find values above this threshold and set to 0 (use bad border duration window to remove edges)
    highArtInds_temp=np.nonzero(signalMag > artThresh)
    highArtInds=highArtInds_temp[1] #grab the indices
    datLength=len(signalMag[0])
    del highArtInds_temp
    del signalMag
    gc.collect()
    numBadPoints=len(highArtInds)
    print(str(len(highArtInds))+' datapoints are marked bad')

    #Add bad window borders
    print("Adding bad window borders...")
    highArtInds_copy=np.copy(highArtInds)
    currentInd=0
    currLengthHighArtInds=len(highArtInds)
    highArtInds_final=np.array([])
    while currentInd<currLengthHighArtInds:
        print(highArtInds_copy[currentInd])
        overlapInds=np.where(np.logical_and(highArtInds_copy<(highArtInds_copy[currentInd]+(badBorderDuration/2)),(highArtInds_copy>highArtInds_copy[currentInd]))) #Do half window to encompass all windows
        #Delete overlapping indices
        highArtInds_copy=np.delete(highArtInds_copy,overlapInds[0][0:-2])

        #Add in bad window indices
        highArtInds_final=np.append(highArtInds_final,np.arange(highArtInds_copy[currentInd]-badBorderDuration,highArtInds_copy[currentInd]+badBorderDuration))
        #Update variables
        currentInd=currentInd+1
        currLengthHighArtInds=len(highArtInds_copy)
        print(len(highArtInds_copy))

    highArtInds_final=np.unique(highArtInds_final)
    highArtInds_final=highArtInds_final[highArtInds_final>-1]
    highArtInds_final=highArtInds_final[highArtInds_final<datLength]
    highArtInds_final=highArtInds_final.astype(int)

    del highArtInds
    del highArtInds_copy
    gc.collect()
    return highArtInds_final

def _filter_resample_ecog(h5_fn,f,Fs,downsample,highArtInds_final,signal_labels,n,patient_code,day,numBadPoints,savepath):
    #Filter parameters
    lo_cutoff=1 #Hz
    hi_cutoff=200 #Hz
    f_stop_mids=np.arange(60, 241, 60) #Hz
    
    if os.path.exists(h5_fn):
        os.remove(h5_fn)
    with h5py.File(h5_fn, "w") as fout:
        Fs_new=Fs/downsample
        dset3 = fout.create_dataset("f_sample", data=Fs_new)
        #Resample final artifact inds appropriately for later access
        tmpBadTimepoints=np.zeros((1,f.getNSamples()[0]))[0]
        tmpBadTimepoints[highArtInds_final]=1
        tmpBadTimepoints = mne.filter.resample(tmpBadTimepoints,down=downsample,npad='auto')
        newInds=np.where(tmpBadTimepoints>.9)[0] #Take indices where value is ~1
        dset4 = fout.create_dataset("allChanArtifactInds", data=newInds)

        #fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(10,6))
        for i in range(n):
            print("loading " + str(i) + ", signal: " + signal_labels[i])
            sigbufs = np.zeros((1, f.getNSamples()[0]))
            sigbufs[0,:] = f.readSignal(i)
            sigbufs=sigbufs-np.median(sigbufs) #Subtract off DC drift (otherwise setting artifact to 0 won't work)
            #Don't plot EKG channel with others
            #if i%10==1 & i<(n-1):
            #    ax1.plot(sigbufs[0,0:-1:int(4*Fs)]) #plot original signal in top subplot (downsampled for space)
            sigbufs[0,highArtInds_final]=0
            #if i%10==1 & i<(n-1):
            #    ax2.plot(sigbufs[0,0:-1:int(4*Fs)]) #Plot high-amplitude, artifact-corrected signal in middle subplot (downsampled for space)

            #Bandpass filter and remove line noise (plus harmonics)
            print("Filtering")
            sigbufs=mne.filter.filter_data(sigbufs,Fs,lo_cutoff,hi_cutoff) #FIR filter with hamming window
            sigbufs=mne.filter.notch_filter(sigbufs,Fs,f_stop_mids) #Notch line noise filter
            #if i%10==1 & i<(n-1):
            #    ax3.plot(sigbufs[0,0:-1:int(4*Fs)]) #Plot filtered signal in bottom subplot (downsampled for space)

            #Downsample to 500 Hz
            print("resampling...")
            sigbufs = mne.filter.resample(sigbufs,down=downsample,npad='auto')

            #Save the results
            if i==0:
                dset1 = fout.create_dataset("dataset", (n,np.size(sigbufs,axis=1)))
            dset1[i,:]=sigbufs[0,:]
            gc.collect()
        fout.close()
        del fout, dset1, sigbufs
        gc.collect()
    #ax1.set_title('Raw data')
    #ax2.set_title('High-amplitude drifts removed')
    #ax3.set_title('Filtered data')
    #plt.figure(fig.number) #set current plot (for saving)
    #savepath_fig = savepath[:-22]+'chan_preproc_plots/'
    #plt.savefig(savepath_fig+'ChannelPreproc_comparison_'+patient_code+'_day'+str(day)+'_traces_'+str(numBadPoints)+'badPts.png',bbox_inches='tight')
    #plt.close(fig)

def _add_start_timestamp(data_dir,fin,ajileFormat,patient_code,day):
    if ajileFormat==True:
        f = pyedflib.EdfReader(data_dir+'/purged_' + patient_code + '_day_' + str(day) + '.edf')
    else:
        f = pyedflib.EdfReader(data_dir+ '/'+patient_code + '_' + str(day) + '.edf')
    startDateTime=f.getStartdatetime()
    tStamp=(startDateTime-dt.utcfromtimestamp(0)).total_seconds() #convert back with dt.utcfromtimestamp()
    f._close()
    del f
    gc.collect()
    
    #Remove time vector (unnecessary)           
    e = "/time_sec" in fin
    if e:
        del fin['time_sec'] #Don't need time vector (can create it later)
    
    #Save timestamp
    e = "/start_timestamp" in fin
    if e:
        del fin['start_timestamp']
    fin.create_dataset("start_timestamp", data=tStamp)
    return tStamp
    
def _add_signal_labels(data_dir,ajileFormat,fin,patient_code,day):
    if ajileFormat==True:
        f = pyedflib.EdfReader(data_dir+'/purged_' + patient_code + '_day_' + str(day) + '.edf')
    else:
        f = pyedflib.EdfReader(data_dir+ '/'+patient_code + '_' + str(day) + '.edf')
    signal_labels = f.getSignalLabels()
    
    #Add channel labels to saved data
    e = "/chanLabels" in fin
    if not e:
        dset5 = fin.create_dataset("chanLabels", data=str(signal_labels))
    return signal_labels
    
def _electrode_group_indices(signal_labels):
    signal_labels2=signal_labels #[0:-1]
    lst2=[item[0:3] for item in signal_labels2]
    uniqueList=list(set(lst2))

    #Run through grid and each strip and reference separately
    gridGroupList=[]
    for i in range(len(uniqueList)):
        inds2ref=np.array([])
        for j in range(len(lst2)):
            if lst2[j][0:3]==uniqueList[i]:
                inds2ref=np.append(inds2ref,j)
        inds2ref=inds2ref.astype(int) #cast to integer
        if len(inds2ref)>2: #avoid ECG and EOG channels
            gridGroupList.append(inds2ref)
    return gridGroupList

def _calculate_channel_metrics(fin,n,Nsamples):
    stdVals=np.zeros([1,n])
    kurtVals=np.zeros([1,n])
    d_MADs=np.zeros([1,n])
    scale_factor=1.4826
    data=np.zeros([1,Nsamples])
    for i in range(n):
        print(str(i+1)+' of '+str(n))
        data[0,:] = fin['dataset'][i,:]
        stdVals[0,i]=np.std(data,axis=1)
        kurtVals[0,i]=stats.kurtosis(data,axis=1)
        d_MADs[0,i] = np.median(np.abs(data),axis=1)*scale_factor
        
    #Save results
    e = "/SD_channels" in fin
    if e:
        del fin['SD_channels']
    fin.create_dataset("SD_channels", data=stdVals)
    e = "/Kurt_channels" in fin
    if e:
        del fin['Kurt_channels']
    fin.create_dataset("Kurt_channels", data=kurtVals)
    e = "/standardizeDenoms" in fin
    if e:
        del fin['standardizeDenoms']
    fin.create_dataset("standardizeDenoms", data=d_MADs)
    return (stdVals,kurtVals,d_MADs)

def _rereference_time_chunks(fin,Nbins,tstep,gridGroupList):
    print('referencing...')
    for i in range(Nbins):
        print('Bin #'+str(i+1)+' of '+str(Nbins))
        data=[]
        #Rereference using common median indices from each strip
        if i==(Nbins-1):
            data = fin['dataset'][:,(i*tstep):-1] #go to the end of the data
            for j in range(len(gridGroupList)):
                inds2ref=gridGroupList[j]
                data[inds2ref,]=data[inds2ref,]-np.tile(np.median(data[inds2ref,],axis=0),(len(inds2ref),1))
            fin['dataset'][:,(i*tstep):-1]=data
        else:
            data = fin['dataset'][:,(i*tstep):((i+1)*tstep-1)]
            for j in range(len(gridGroupList)):
                inds2ref=gridGroupList[j]
                data[inds2ref,]=data[inds2ref,]-np.tile(np.median(data[inds2ref,],axis=0),(len(inds2ref),1))
            fin['dataset'][:,(i*tstep):((i+1)*tstep-1)]=data

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s','--subjID',required=True,help='subject ID')
    parser.add_argument('-d','--day',required=True,help='dataset day of interest')
    parser.add_argument('-lp','--loadPath',required=True,help='directory path to load data from')
    parser.add_argument('-sp','--savePath',required=True,help='directory path to save data to')
    parser.add_argument('-af','--ajileFormat',required=False,help='boolean indicating if load data is in AJILE format (True) or not (False)')
    args = parser.parse_args()
    
    print('Processing: '+args.subjID+str(args.day[11:-4]))
    #Run preprocessing pipeline
    if args.ajileFormat is not None:
        remove_large_artifacts_plus_filtering(args.subjID,args.day[11:-4],args.loadPath,args.savePath,args.ajileFormat)
        common_median_reference_plus_channel_measures(args.subjID,args.day[11:-4],args.loadPath,args.savePath,args.ajileFormat)
    else:
        remove_large_artifacts_plus_filtering(args.subjID,args.day[11:-4],args.loadPath,args.savePath)
        common_median_reference_plus_channel_measures(args.subjID,args.day[11:-4],args.loadPath,args.savePath)
