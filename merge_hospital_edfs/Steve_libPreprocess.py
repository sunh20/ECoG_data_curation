import numpy as np
import pandas as pd
from scipy import stats
from scipy import signal
import mne
import h5py
import os
import argparse
import gc
from datetime import datetime as dt
import pdb
#Library of functions for importing processed data: allows for loading the data with specific channels/frames, removing bad channels based on variance, removing bad frames based on variance across all channels and for each channel, standardization, and time array creation (relative and absolute)

#Example usage:
# import h5py
# import numpy as np
# subjID='cb46fd46'
# day='3'

# #Load in data with bad channels and frames removed
# loadpath='/data2/users/stepeter/Preprocessing/processed_'+subjID+'_'+day+'.h5'
# fin = h5py.File(loadpath,"r")
# #Identify good channels from pre-existing thresholds
# goodChannelInds=ecog_removeBadChans(fin,-1,-1)
# print(goodChannelInds)
# goodChannelInds=np.array([1,2,3])

# #Load the data with just the good channels
# ecog_data,inFrameInds=ecog_loadData(fin,-1,np.arange(0,500*60))

# #Standardize the resulting ecog data (put in goodChannelInds because removed bad channels already)
# ecog_data=standardizeEcog(fin,ecog_data,-1,'SD')

# #Change value of artifactual data frames to NaN (put in goodChannelInds because removed bad channels already)
# ecog_data=changeval_BadFrames(fin,ecog_data,inFrameInds,float('nan'),goodChannelInds)

# #Also change across channel bad data frames to NaN (put in goodChannelInds because removed bad channels already)
# ecog_data=changeval_AllChanArtifactInds(fin,ecog_data,inFrameInds,newValue=float('nan'))

# #Calculate time array for data (absolute time)
# timeArray=create_timeArray(fin,inFrameInds,False)

def create_timeArray(fin,inFrameInds,relativeTime=True):
    #Creates corresponding time array to data either relative (in sec) or absolute (datetime)
    Fs=fin['f_sample'][()]
    ecog_chan=fin['dataset'][0,:]
    if relativeTime==True:
        NSamples=ecog_chan.shape[1]
        timeArray=np.arange(0,NSamples/Fs,1/Fs)
    else:
        #Calculate absolute time array
        startTime=dt.utcfromtimestamp(fin['start_timestamp'][()])
        srate_scale=1000/Fs
        timeArray = pd.timedelta_range(0, periods=len(ecog_chan), freq=str(srate_scale)+'L') # L means ms
        timeArray = timeArray + startTime
    return timeArray[inFrameInds]


def determineBadChannels(sdChans,kurtChans,sdThresh=5,kurtThresh=10):
    #Helper function for ecog_removeBadChans() that determines which channels are good
    
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

def ecog_removeBadChans(fin,sdThresh=-1,kurtThresh=-1):
    #Remove bad channels based on thresholding the standard deviation and kurtosis values
    #Idea is to remove channels that are much different from the rest
    #If sdThresh or kurtThresh is set to -1, will use 'goodChanInds'
    if sdThresh<0 or kurtThresh<0:
        finalGoodInds=fin['goodChanInds'][()]
    else:
        sdChans=fin['SD_channels'][()]
        kurtChans=fin['Kurt_channels'][()]
        finalGoodInds=determineBadChannels(sdChans,kurtChans,sdThresh,kurtThresh)
    return finalGoodInds


def standardizeEcog(fin,ecog_data,goodChanInds=-1,type='SD'):
    #Standardize ECoG data (if removed bad channels, include goodChanInds)
    #Can choose type to be 'SD' (standard deviation) or 'robust' (median variance calculation)
#     print('standardizing data...')
    if type=='robust':
        stdDenoms=fin['standardizeDenoms'][()]
    elif type=='SD':
        stdDenoms=fin['SD_channels'][()]
    else:
        print('Cannot identify standardization type requested!')

    ecog_dataStand=np.copy(ecog_data)
    for i in range(ecog_data.shape[0]):
        if np.any(goodChanInds==-1):
            #All channels are good
            ecog_dataStand[i,:]=ecog_data[i,:]/stdDenoms[0,i]
        else:
            #Some channels have been removed
            ecog_dataStand[i,:]=ecog_data[i,:]/stdDenoms[0,goodChanInds[i]]
#     print('Standardization finished!')
    return ecog_dataStand


def changeval_AllChanArtifactInds(fin,ecog_data,inFrameInds,newValue=float('nan')):
    #Changes the values of the ECoG data at the marked higher amplitude artifact indices
    #Can specify a numerical value or NaN
    highArtInds=fin['allChanArtifactInds'][()]
    highArtIndsFinal=np.intersect1d(highArtInds,inFrameInds)-inFrameInds[0]
    for i in range(ecog_data.shape[0]):
        ecog_data[i,highArtIndsFinal]=newValue
    return ecog_data


def ecog_loadData(fin,chanInds=-1,frameInds=-1):
    #Loads ECoG data (chanInds=-1 loads all channels, otherwise can specify; same for frameInds)
#     print('loading data...')
    origchanInds=chanInds
    origframeInds=frameInds
    if np.any(chanInds==-1):
        snipDat=fin['dataset'][:,0]
        chanInds=np.arange(0,snipDat.shape[0])
    if np.any(frameInds==-1):
        snipDatFrames=fin['dataset'][0,:]
        frameInds=np.arange(0,snipDatFrames.shape[0])

    if np.any(origchanInds==-1) and (not np.any(origframeInds==-1)):
        #Selecting certain frames, but not channels
        ecog_data=fin['dataset'][:,frameInds]
    elif np.any(origframeInds==-1) and (not np.any(origchanInds==-1)):
        #Selecting certain channels, but not frames
        ecog_data=fin['dataset'][chanInds,:]
    else:
        #Will select both frames and channels (may take more time/memory)
        snipDatFrames=fin['dataset'][0,:]
        frameInds2=np.arange(0,snipDatFrames.shape[0])
        frameIndsFinal=np.setdiff1d(frameInds2,frameInds)
        if len(chanInds)==1:
            ecog_data=np.zeros([1,(fin['dataset'][chanInds,:]).shape[1]])
            ecog_data[0,:]=fin['dataset'][chanInds,:]
        else:
            ecog_data=fin['dataset'][chanInds,:]
        ecog_data=np.delete(ecog_data,frameIndsFinal,axis=1)
#     print('Data loaded!')
    return ecog_data,frameInds


def changeval_BadFrames(fin,ecog_data,inFrameInds,replaceVal=float('nan'),goodChanInds=-1):
    #Remove bad frames and replace with 'replaceVal' value (if removed bad channels, include goodChanInds)
    if np.any(goodChanInds==-1):
        goodChanInds=np.arange(0,ecog_data.shape[0])
    for i in range(len(goodChanInds)):
        #Some channels have been removed
        badFrames=fin['outlierFrameInds/'+str(goodChanInds[i])]
        badFramesFinal=np.intersect1d(badFrames,inFrameInds)-inFrameInds[0]
        ecog_data[i,badFramesFinal]=replaceVal
    return ecog_data


def badBorderWindow(highArtInds,datLength,badBorderDuration):
    #Helper function for determineBadFrames_oneChannel() (adding bad border window to flagged data frames)
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

def determineBadFrames_oneChannel(ecog_data,iqrThreshold=50):
    #Removes bad data frames for one channel based on a threshold determined by the IQR
    #Returns indices for the bad frames
    artThresh=iqrThreshold*stats.iqr(ecog_data) #set artifact threshold
    signalMag=np.absolute(ecog_data)
    #Find values above this threshold and set to 0
    highArtInds_temp=np.nonzero(signalMag > artThresh)
    highArtInds=highArtInds_temp[1]
    datLength=ecog_data.shape[1]
    badBorderDuration=500 #1 second
    highArtInds_final=badBorderWindow(highArtInds,datLength,badBorderDuration) #use bad border duration window to flag edges
    return highArtInds_final