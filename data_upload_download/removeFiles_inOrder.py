#May require "sudo python ...py" to run
import pyedflib
import numpy as np

dirPath="/data2/users/hmc/"
subjName="#####" #replace ##### with subject last name (should be first part of file/foldernames)
#Find all files in directory
import glob, os
os.chdir(dirPath)
listDateTimes=[]
for file in glob.glob(subjName+"*.edf"):
    f = pyedflib.EdfReader(file)
    print(f.getStartdatetime())
    listDateTimes.append(f.getStartdatetime())
    f._close()
    del f

listDateTimesSorted=sorted(listDateTimes)
dateTimeInds=np.argsort(listDateTimes) #indices to turn listDateTimes into listDateTimesSorted
#print(listDateTimesSorted)
#print(dateTimeInds)
q=0

for file in glob.glob(subjName+"*.edf"):
    fileInd=np.where(dateTimeInds == q)[0]
    os.rename(file,subjName+"_"+str(fileInd[0]+1)+".edf")
    os.rename(file[0:-4],subjName+"_"+str(fileInd[0]+1))
    q=q+1

print("Done! :)")
