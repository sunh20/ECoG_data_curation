# ECoG processing pipeline

There are many steps to processing the ECoG data, but it should only be necessary to do one time per subject. The result of this pipeline will be processed ECoG files from midnight to midnight that can be easily synchronized with video events.

## ECoG pipeline

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


## Step 3: Preprocess the EDF data


## Merging hospital EDFs into full days (midnight to midnight)

### Overview

When we receive the EDF/video files from the hospital, they are broken up based on when the ECoG system was turned on/off. This means that they can start throughout the day (usually around 8-10am) and can last from a couple hours to an entire day. Because of this, we 
