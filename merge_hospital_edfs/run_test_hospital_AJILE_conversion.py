"""
Functions to convert between AJILE (midnight to midnight) and hospital time coordinate systems.
"""

import sys
import os
sys.path.append('/home/stepeter/Documents/ECoG_Preprocessing')
from hospital_AJILE_conversion import *

patients_all = ['b45e3f7b']
# patient_id = 'ab2431d9'

for patient_id in patients_all:
    path1 = '/data1/ecog_project/derived/processed_ecog/'+patient_id+'/'
    path2 = '/data1/ecog_project/derived/processed_ecog/'+patient_id+'/full_day_ecog/'
    if not os.path.exists(path1):
        os.mkdir(path1)
    if not os.path.exists(path2):
        os.mkdir(path2)
    loadpath = '/data1/ecog_project/derived/processed_ecog/'+patient_id+'/preproc_hospital_ecog/' #'/nas/ecog_project/derived/processed_ecog/'+patient_id+'/preproc_hospital_ecog/'
    merge_day_start = 1 #start day to merge (should be 1 or greater)

    merge_files_individual_days(patient_id,loadpath,merge_day_start)

    #plot_merged_data(patient_id,loadpath)
