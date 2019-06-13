# Data upload/download scripts

Several provided scripts for uploading and downloading video/ECoG data between a local directory and S3, Glacier, or Azure.

## Uploading pipeline for new data


###Overview

When we receive new patients from the hospital, the file names are de-identified (replaced with an 8-digit code) and backed up on both Amazon S3 and Glacier. S3 is an easy to access backup, while Glacier is a last-resort backup in case several things go wrong. The data should also be backed up on NAS so that people can access it across computers.

Additionally, we have old copies of files on Azure, which can be useful if some Natus files are missing for a particular subject.

###De-identification

Once the data has been uploaded onto a lab computer, de-identify the folder names. You will need these scripts, which can be run in Python 3:
    - removeFiles_inOrder.py
    - de_id.py

####Step 1: If there are folders with the SNC/VTC text output, change the subject names in their foldernames to all lowercase
This avoids confusion in later scripts.

####Step 2: Add patient’s last name to removeFiles_inOrder.py and then run the script in python 
This sorts the EDF/video files by datetime automatically and numbers the filenames appropriately.
```
python removeFiles_inOrder.py
```

####Step 3: Move all **video** files into a folder (1 folder per patient) with the patient’s last name on it and change its permissions
Make sure to leave out the EDF folders.
Change all the permissions of this folder to 777. **Be careful to select the correct folder! Do not select just the root folder or it will break the computer!**
```
sudo chmod -R 777 /folder
```

####Step 4: Add patient’s last name to de_id.py and run the script
Include generated subject ID if used an ID previously and are re-running it.
```
python de_id.py
```

####Step 5: Save the generated subject ID to the online spreadsheet

####Step 6: Manually change the EDF filenames to the generated subject ID and move them all into a folder with named sbjID_edf
```
mv sbj_last_name_1.edf sbjID_1.edf
```

####Step 7: Manually determine the order of the SNC/VTC output files and rename the files appropriately
Note the first datetime in each corresponding VTC and SNC filename should be roughly similar within ~10 minutes.
