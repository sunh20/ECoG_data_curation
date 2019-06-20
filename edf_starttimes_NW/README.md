# Automatically determining EDF start times from Neuroworks export files

The EDF files come with a start time, but this time is only precise to the nearest second. Because the ECoG data is sampled at 1000 Hz (most of the time), it is important to have this value be precise to the nearest **millisecond**. Unfortunately, this can really only be done with the proprietary Xltek/Natus files. The pipeline is to load these files into Neuroworks (aka Natus Datashare), export one channel's data at the start of the recording, and then use the timestamps from this exported file to obtain a more precise ECoG start time.

**Sections:**

A. Exporting data from Neuroworks

B. Obtaining timestamps from the exported data


## Section A: Exporting data from Neuroworks

### Overview

Neuroworks (also known as Natus Datashare; Neuroworks usually references the complete version used by the hospital) allows us to read the proprietary files from the hospital. Unlike the EDF and AVI files, we are unable to read the proprietary files using any free software except Neuroworks. The ultimate goal of this data preprocessing is to extract all of the information we need from these proprietary files only one time for each patient so that we are not dependent on specific software to read these files.

Currently, Neuroworks is set up on a Windows virtual machine on Salarian. This is because Neuroworks only runs on Windows. A virtual machine is useful because it has access to files directly on Salarian (which has access to NAS), so transferring files between Salarian and the virtual machine is quite easy and fast.

**Contents**:

I. Starting up Neuroworks on virtual machine

II. Loading ECoG data and exporting

### Part I: Starting up Neuroworks on virtual machine

**Step 1: Start VirtualBox**

The virtual machine is on VirtualBox (https://www.virtualbox.org). To start, type:

```
virtualbox
```

**Note:** This can be performed directly on Salarian or over SSH (with -X command). However, the virtual machine will notably lag over SSH, so I recommend working directly on Salarian for this, if possible.


**Step 2: Start virtual machine**

Click on the virtual machine on the left-side menu to start. There should only be 1 option here. If you do not see anything, check the permissions of */data1/users/stepeter/Windows\ 10\ EKG/Windows 10 EKG.vbox*. One annoyance with VirtualBox is that it will write the .vbox permissions to be read/write only for the user who used it last. If you need to, use *chown* to change ownership of the .vbox file to your username **(be cautious with this command as chown on the wrong directory can seriously mess up the computer!)**


**Step 3: Log in**

Log into Windows. There should be a default username that pops up, and it asks for a code. Type in 8675 to log in.


**Step 4: Start Neuroworks**

Neuroworks can be started by either going to Computer>Neuroworks>Wave.exe or by clicking on a .eeg file. If you start Wave.exe, the program will look like it is still loading, but it is waiting for you to load a file. Go to File>Review and you can load the file.


### Part II: Loading ECoG data and exporting

**Step 1: Load proprietary ECoG files to virtual machine**

Use the shared folders to download the proprietary ECoG files onto the virtual machine (Neuroworks will not run if you try to run it directly on shared folder files). One of the shared folders should be connected to NAS, which should have most files of interest. Shared folders can be configured on the first VirtualBox screen that popped up (not the virtual machine).

The files needed are the first EEG, ENT, EPO, ERD, ETC, SNC, STC, VT2, VTC files, along with ETC_0001, ERD_0001, AVI_0000, and AVI_0001. This should be a much quicker transfer than downloading all of the files for the entire day. I suggest copying these files to the *Documents* folder. **Be sure to copy, not move, these files so that nothing is later accidentally deleted.**

**Step 2: Open the EEG file in Neuroworks**

First, the files will all need to be re-identified. Open up the VT2 file and copy The filename before *_0000.avi* (should be something of the form *Last~ First_########-####-####-####-############*). Use this to change all of the files.

Double-click on the EEG file to start Neuroworks. If you see a warning (yellow sign) that says *Cannot create additional picks!*, press *OK*.

**Note:** If receive ‘Runtime Error!’, you can still do the export in the next steps (do it before clicking OK, as this will close the program). Always make sure the export process did create a file that has timestamps in it. 


**Step 3: Export the data**

Go to File>Export. Pick a location and name for the exported data TXT file. In the next menu, select the first channel only. Select approximately the first minute of recording time and deselect *photic stimulator* and *comment* checkboxes. Then click *Export*

**Note:** If this is a file with a *Runtime Error!* from earlier, you will need to drag the cursor to set the start time to the beginning (values might shift slightly later than originally) or else the export process may error out.


**Step 4: Check file and clean up**

Check the exported TXT file to make sure the export worked. There should be a column of timestamps and other columns that include data and whatnot. The first column is what is important. Then delete the copied proprietary files from the virtual machine.



## Section B: Obtaining timestamps from the exported data

### Overview

Once we have the exported TXT files (transferred to Salarian from the virtual machine), we can determine the start time with millisecond resolution using *add_NW_starttime_intermediate_files.py*. This file counts how many times the first timestamp is repeated and then checks how many times the following timestamp (first timetsamp +1 second) is repeated. The first timestamp repetitions will tell us how much time elapsed before changing to a new second. The number of second timestamp repetitions tell us how many repetitions occur in 1 second (usually 1000, but not always). The start time can be calculated adding the result of the following formula to the first timestamp:

```
ms_offset = (1 - (1st_ts_reps/2nd_ts_reps))
```

**Note:** These scripts assume that the intermediate data files are located locally on */data1/ecog_project/derived/processed_ecog/<sbjID>/preproc_hospital_ecog/*

### Single-subject processing

To run a single subject, use the *add_NW_starttime_intermediate_files.py* code as shown:

```
python add_NW_starttime_intermediate_files.py -lp <NW_starttimes_folderpath> -s <sbjID>
```

**<NW_starttimes_folderpath>** is the folder path containing the exported data from Neuroworks (inside separate folders for each subject)

**<sbjID>** is the patient ID
  

### Multi-subject processing

To run multiple subjects (batch processing), use *run_add_NW_starttime.sh*. Be sure to modify the code to specify the correct exported data folder and patient IDs. Then run using

```
./run_add_NW_starttime.sh
```
