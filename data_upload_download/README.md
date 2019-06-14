# Data upload/download scripts

Several provided scripts for uploading and downloading video/ECoG data between a local directory and S3, Glacier, or Azure.

**Sections:**

A:  Uploading pipeline for new data

B:  Downloading data


## Section A: Uploading pipeline for new data

### Overview

When we receive new patients from the hospital, the file names are de-identified (replaced with an 8-digit code) and backed up on both Amazon S3 and Glacier. S3 is an easy to access backup, while Glacier is a last-resort backup in case several things go wrong (it also takes longer to back data up). The data should also be backed up on NAS so that people can access it across computers, which will happen if the data is placed in an 'ecog_project' folder on Cylon/Salarian.

Additionally, we have old copies of files on Azure, which can be useful if some Natus files are missing for a particular subject.


**Contents:**

I.      De-identification

II.     Uploading to S3

III.    Uploading to Glacier    


### Part I: De-identification

Once the data has been uploaded onto a lab computer, de-identify the folder names. You will need these scripts, which can be run in Python 3:

- removeFiles_inOrder.py
    
- de_id.py


#### Step 1: If there are folders with the SNC/VTC text output, change the subject names in their foldernames to all lowercase

This avoids confusion in later scripts.

#### Step 2: Add patient’s last name to removeFiles_inOrder.py and then run the script in python 

This sorts the EDF/video files by datetime automatically and numbers the filenames appropriately.
```
python removeFiles_inOrder.py
```

#### Step 3: Move all *video* files into a folder (1 folder per patient) with the patient’s last name on it and change its permissions

Make sure to leave out the EDF folders.
Change all the permissions of this folder to 775. **If this doesn't work, make sure you are part of the ecog group. Using sudo here is dangerous!**
```
chmod -R 777 /folder
```

#### Step 4: Add patient’s last name to de_id.py and run the script

Include generated subject ID if used an ID previously and are re-running it.
```
python de_id.py
```

#### Step 5: Save the generated subject ID to the online spreadsheet

#### Step 6: Manually change the EDF filenames to the generated subject ID and move them all into a folder with named sbjID_edf

```
mv sbj_last_name_1.edf sbjID_1.edf
```

#### Step 7: Manually determine the order of the SNC/VTC output files and rename the files appropriately

Note the first datetime in each corresponding VTC and SNC filename should be roughly similar within ~10 minutes.

#### Step 8: De-identify the EDF headers

Replace subject last name with subject code.
```
edfbrowser>Tools>header editor>change Subject line
```

### Part II: Uploading to S3

We have 2 separate folders (buckets) on Amazon S3, 1 for EDF files and 1 for the video files. By logging onto S3 online, it is possible to determine which files have been uploading in near realtime.

Additionally, the scripts can upload multiple patients' files at once.

#### Step 1: Change folder permissions to 775, if not already done

**If this doesn't work, make sure you are part of the ecog group. Using sudo here is dangerous!**
```
chmod -R 777 /folder
```

#### Step 2: Run the upload_to_s3.py script

After running the script on the video files, you will be asked to enter an encryption password. Use the main password for our lab.
```
upload_to_s3.py -d <data_source> -b <bucket_name> -t <data_type>
```
**data_source** should be the folder above all of the patients' video/EDF folders (I usually put them in a *to_upload* folder). If there are multiple patients under this folder, they will all be uploaded.

**bucket_name** is the S3 bucket (or folder) that the data goes into.

- For video, use *uwecogvidwest*
        
- For EDF, use *uwecogwest*
        
**data_type** specifies which type of data you are uploading

- For video, use *v*
        
- For EDF, use *e*

### Part III: Uploading to Glacier

Glacier is super slow. This makes doing anything with it really annoying and time-consuming. The main point of it is to have a fail-safe backup in case something happens to the local data and S3 data.

#### Step 1: Change folder permissions to 775, if not already done

**If this doesn't work, make sure you are part of the ecog group. Using sudo here is dangerous!**
```
chmod -R 777 /folder
```

#### Step 2: Run upload_glacier.py to upload files

##### Single subject upload: run upload_glacier.py

This script does 2 things. First, it compresses the data into a tarball. Then, it uploads the tarball to Glacier. The tarball is not removed by this script, which can be helpful in case there is an uploading problem with Glacier. After running the script on the video files, you will be asked to enter an encryption password. Use the main password for our lab.

```
python upload_glacier.py -d <data_source> -td <temp_dir> -t <data_type>
```
**data_source** should be the patients video/EDF folder (aka the subfolder below the *to_upload* folder used for S3). This only uploads one subject at a time.

**temp_dir** is the a temporary directory. The script will compress the data, which will be stored in this temporary directory. Then this tarball will be uploaded to glacier.
        
**data_type** specifies which type of data you are uploading

- For video, use *vid*
        
- For EDF, use *edf*


##### Multi-subject upload: run runMultGlacierUploads.sh

This bash script runs *upload_glacier.py* for multiple subjects in series and deletes the tarballs after to save space. This requires modifying the *upload_glacier.py* to have the password already set (change it back afterwards). The downside with this script is that a subject's upload might not work and you'll have to make the tarball again. However, this can be useful for multiple subjects instead of waiting for each one to finish.

Also, be sure to modify *runMultGlacierUploads.sh* so that the filepaths, temporary directories, and patient IDs are correct.

```
./runMultGlacierUploads.sh
```


#### Step 3: Check Glacier to ensure the files were properly uploaded

Glacier has weird inventory code, where you enter the code below and wait a couple hours and then run the code again to see what files Glacier has. If you wait too long (about a day), though, the results will time out. It's pretty annoying.

I suggest copying the results from this into a MS Word file and using the find command to see if the patient's video/EDF folders have been uploaded.

```
glacier-cmd inventory ecog-video
```


## Section B: Downloading data

### Overview

Having backup files is of little use if we cannot download them. The steps below outline the appropriate scripts and methods to use to download the data.


**Contents:**

I.      Downloading from Azure

II.     Downloading from S3

III.    Downloading from Glacier    


### Part I: Downloading from Azure

The data on Azure is old. It was used before we backed files up on S3 and Glacier. It can be helpful to look at these files if you are missing Natus files and need them.


#### Step 1: Download the files with azcopy

This assumes the computer is running azcopy. There are newer versions of this with slightly different syntax, but the arguments are roughly the same.

```
azcopy --source <source_path> --destination <destination_path> --source-key <source_key>
```

**source_path** is the online path to the file on Azure. Click on the file online, and copy the URL link for this argument

**destination_path** is the local directory (including the filename for what is being downloaded)
        
**source_key** is the key to be able to download the data. Copy one of the access keys (primary or secondary) from the storage account home page


#### Step 2: Decrypt the file using openssl

This decrypts the file and ouputs a tarball.

```
openssl enc -d -des -in sbjID_vid -out sbjID_vid.tar -pass pass:<passwd> -nopad
```

**passwd** is the main password for the lab


#### Step 3: Expand the tarball

```
tar -xvzf /path_to_file/sbjID_vid.tar
```

Once the tarball is expanded, you can look at the files.


### Part II. Downloading from S3

Use *download_from_s3.py*. It has similar arguments to the upload script.


### Part III. Downloading from Glacier

TBD
