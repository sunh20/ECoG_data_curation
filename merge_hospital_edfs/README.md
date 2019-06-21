# ECoG processing pipeline

There are many steps to processing the ECoG data, but it should only be necessary to do one time per subject. The result of this pipeline will be processed ECoG files from midnight to midnight that can be easily synchronized with video events.

## ECoG pipeline steps:

0. Obtain subject consent form from hospital

1. Download data from hospital and upload to Brunton lab computer

2. De-identify file names and backup video and EDF files on S3 and Glacier

3. Preprocess the EDF data

4. Merge the hospital EDFs into full days (midnight to midnight)

5. Add in location information

6. Create synchronization files for video events


## Step 0: Obtain subject consent form from hospital

Before downloading any data, we need to have the patient's consent form. Obtain the consent 

The data (video, audio and ECoG) are collected by Harborview Medical Center as part of standard patient care for intractable epilepsy. Harborview Medical Center is a regional epilepsy treatment center so we have patients from nearby states as well. Surgeries are performed by Dr. Jeffrey Ojemann and Dr. Andrew Ko. 

The patients are surgical candidates and have gone through likely years of medical interventions to arrive at this point. Typically, patients will have tried many different kinds of medication but they are still having enough seizures to severely interfere with normal life. First, they are placed under EEG monitoring, which also consists of electrodes, audio and video and we also have IRB approval to study these patients. There are usually around 7-10 EEG monitoring patients per week and they will stay in the hospital for a few days.  If the medical team believes that he or she indeed has epilepsy (~50% do not and the seizures are more likely psychiatric symptoms), and that it is focal, they may go through strips monitoring. They will be monitored with fewer electrodes that can be easily implanted with the goal of pinpointing the approximate location of the seizure source. Depending on the results, they may go under surgical excision this round or come back to be implanted with more electrodes, likely grid, but it could also be depth. These procedures are likely due to change as we go forward. Patients are opting for less invasive procedures as more options are made available. 

Steps to consent:

1. Get added to the GridLab calendar. Kurt Weaver (Research Professor on gridlab team) gets notified of new patients coming up and puts them on the calendar (https://calendar.google.com/calendar/embed?src=rc14n8tuqkfldbt0nvsrb3hsr0%40group.calendar.google.com&ctz=America%2FVancouver). Also, add yourself to the gridlab-recteam mailing list (search on mailman). This is how gridlab people communicate about patients, recons etc. 

2. Normally, Andrea Oliva (maoliva@uw.edu) consents the patient. However, sometimes she may be too busy so it's good to check in with her ~ 1 week ahead of the patient's surgical date. If Andrea does not consent the patient, do the consents on day 3 post surgery in the patient room.

She can mail the form but forms have been lost in the mail in the past so we currently pick up the consent forms from her in person just before downloading the data. 

3. There are **2** IRB approved consent forms: General procedures and HIPAA. Make sure the patient signs both before any data collection.  They are on the Team Drive (https://drive.google.com/a/uw.edu/file/d/153NDh73oe-KojbiGZhMWeLljPnlKR1op/view?usp=sharing, https://drive.google.com/open?id=13fh0ABXcK5Ik-04yQuqQY1T1b62eNWyl).


## Step 1: Download data from hospital and upload to Brunton lab computer

In the EEG monitoring room, log in with account and password. Search for the patient's name and select all files. First download with option "copy" . Then, download with option "edf". This will take about 3 hours each time. Unfortunately, I haven't found a way to schedule the two copies. 

**Note 1:** When too many people are using the server, sometimes it will cause the system to bug out and crash. Because of this, they would like us to download after normal working hours (after 4pm). Download can be continued overnight and picked up in the morning. Just remember to leave some contact information on the drive. 

**Note 2:** Patient medical records can be downloaded from Epic

**Note 3:** Patient electrode mapping can be downloaded from the Gridlab's computer (Krang). Use the gridlab patient identifier to download recon images and .mat files from krang.cs.washington.edu (need account access). 

**Note 4:** To download data, you need a badge, which, as of Jan 2017, can be obtained from Kris Shaw (kashaw@uw.edu). You also need to make an account on the servers in the EEG monitoring room. The head lab tech can do this. She used to be Julie Rae but she has since retired (as of April 2018, I am uncertain of who is the current lab tech head). 


## Step 2: De-identify file names and backup video and EDF files on S3 and Glacier

See the *data_upload_download* folder for information about this part.


## Step 3: Preprocess the EDF data (include Steve_preprocPipeline.py, runPreprocMain.sh, Steve_libPreprocess.py)

As far as we can tell, the ECoG data we recieve from the EDFs does not have any preprocessing done. This means that there are issues such as DC drift, common-mode noise, and high-amplitude activity that should be corrected regardless of the analysis performed later. The techniques used are pretty simple, but they take a long time to run because of the size of each EDF. Expect several hours (if not a day or two) for each subject. The end result will be an H5 file, which can be loaded into Matlab or Python (all steps shown here use Python).

### Code for preprocessing the data

The code for preprocessing the data is contained in *Steve_preprocPipeline.py*. However, I have a bash script, *runPreprocMain.sh*, which will make the appropriate directories and run the script across all days (the subject and load/savepaths may need to be revised).

```
./runPreprocMain.sh
```

Within *runPreprocMain.sh*, there are input arguments that may need to be revised based on where files are:

**subjects:** This is the 8 alphanumeric patient code for the patient you plan to preprocess

**-exec:** The path and filename of *Steve_preprocPipeline.py*

**-lp:** The path of the EDF files to be loaded (should be under */.../ecog_project/edf/$subject/*, note that the subject folder fills in automatically, using $subject)

**-sp:** The path to save the processed H5 files (currently, should be */.../ecog_project/derived/processed_ecog/$subject/preproc_hospital_ecog/*)

**-af:** Always set this to *False*


### Preprocessing steps

#### 1. Determine high-amplitude artifacts:  

These are high-amplitude artifacts that occur across all channels. Each electrode is loaded in one at a time and the absolute values of the median-sutracted signals are averaged into a global magnitude. Values in this magnitude outside 50 IQRs of the median magnitude (which is 0) are flagged as high-amplitude events. Then, a bad border of 2000 datapoints (2 seconds, usually) is then used to ensure that no high-amplitude artifacts just below the threshold are retained. These bad datapoints are set to 0.

The point of doing this is minimize filtering artifacts due to sharp changes in the signal. These high-amplitude artifacts will cause filter ringing into previously fine data. By setting these artifacts to 0 across all channels, filtering is less likely to create artifacts in the data.


#### 2. Filtering:

Filtering removes parts of the signal's frequency content. For ECoG data, we want to remove low-frequency drifts. Part of this has to do with the frequency content of ECoG data, where low frequencies dominate compared to higher frequencies. This can make it difficult to analyze higher frequencies, which can have useful information. Two filters are used here: 1) a bandpass filter that passes frequencies between 1-200 Hz and 2) a notch filter that removes 60 Hz line noise and its harmonics (120, 180, 240 Hz). The filters used are finite impulse response (FIR) using the MNE toolbox.


#### 3. Resampling

While higher frequencies do have information, there is a limit to what we want to analyze here. The ECoG data is usually sampled at 1000 Hz from the hospital, meaning that we can look at frequencies up to ~500 Hz. We only care about frequencies up to 200 Hz at the most, so the data is downsampled to 500 Hz. This cuts the preprocessed file's disk size in half, which is useful when working with such large files. Resampling needs to be performed with low-pass filtering to avoid anti-aliasing, so the MNE toolbox's downsample script is used here.

Note that some data is sampled at 2000 Hz or 256 Hz from the hospital (it happens rarely, though). In thse cases, the script automatically up/downsamples the data to 500 Hz. In addition, you may notice that the EDF sampling rate is not exactly 1000 Hz, but 999.94 Hz or something. This appears to be a bug in the code. Because of this, the script automatically rounds up the sampling rate to the appropriate value.



#### 4. Common median reference

The last preprocessing step is to remove common-mode noise by referencing. I use the common median here for each channel group that has more than 2 channels (this avoids re-referencing the ECG and EOG channels, if they exist). The common median is useful because it will be less influenced by any abnormally noisy channels in each group than the mean would be.



### Preprocessing output file structure

Structure of H5 files:

- fin[‘dataset’] -> ECoG data (electrodes x timepoints)

- fin['start_timestamp'][()] -> The timestamp (in sec) of the start time for the data. Using this and the sampling rate, can create an array of absolute or relative times (not in Pandas timedelta format because cannot be saved in H5 format)

- fin[‘f_sample’][()] -> sampling rate (500 Hz)

- fin[‘allChanArtifactInds’][()] -> indices of high amplitude artifact across all channels; these are set to 0 in the ECoG data

- fin[‘chanLabels’][()] -> labels of each ECoG electrode

- fin[‘SD_channels’][()] -> estimated standard deviation of each channel (channels with much higher standard deviations than others may want to be removed or at least noted as noisy)

- fin[‘Kurt_channels’][()] -> estimated kurtosis of each channel (channels with much higher kurtosis values than others may want to be removed or at least noted as noisy)

- fin['goodChanInds'][()] -> good channel indices, based on standard deviation (5) and kurtosis (10) thresholds on day-long channel data; different thresholds can be used as shown in Steve_libPreprocess.py>ecog_removeBadChans

- fin['standardizeDenoms'][()] -> used for standardizing the data with Kam's robust median variance calculation; since the data is already mean-zero, just divide each channel by it's respective value in this variable (alternatively, can use 'SD_channels' to standardize)

- fin['outlierFrameInds'][()] -> flagged outlier frames based on 20 IQR threshold; each variable in this group corresponds to one electrode, with the values being the flagged outlier indices (**Note:** This part takes much space and long time to run, so I have commented it out and most files do not have it.) 


**Note:** There is a Python script, *Steve_libPreprocess.py*, that can load and standardize the ECoG data from the preprocessed data files.


## Step 4: Merge the hospital EDFs into full days (midnight to midnight)

When we receive the EDF/video files from the hospital, they are broken up based on when the ECoG system was turned on/off. This means that they can start throughout the day (usually around 8-10am) and can last from a couple hours to an entire day. Because of this, we 

Talk about:
- start times from Neuroworks
- manual TXT files to generate (criteria for merge_ignore are different channel labels or no vtc/snc)
- running merge code

## Step 5: Add in location information

Talk about:
- Krang access
- Lining up Krang IDs with our patient IDs
- Skull stripping to get MNI coordinates (refer to Kurt for more info)
- Realigning to pial surface
- Pipelines for future improvements (pro's and con's)

## Step 6: Create synchronization files for video events

Talk about:
- Reading VTC/SNC files at hospital
- Automatically generating vid_start_end files
