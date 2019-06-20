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

**Step 1: **

```
python add_NW_starttime_intermediate_files.py -lp <NW_starttimes_folderpath> -s <sbjID>
```
