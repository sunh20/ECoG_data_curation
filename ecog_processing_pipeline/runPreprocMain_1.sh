#!/bin/sh
subjects='q873748d abdb496b' #a0f66459 ab2431d9 b4ac1726 #c95c1e82 d6532718 ec374ad0 ffb52f92 aa97abcd c7980193 cb46fd46 e5bad52f fcb01f7a
for subject in $subjects
do
   mkdir /data1/ecog_project/derived/processed_ecog/$subject/
   mkdir /data1/ecog_project/derived/processed_ecog/$subject/preproc_hospital_ecog/
   mkdir /data1/ecog_project/derived/processed_ecog/$subject/chan_preproc_plots/
   #cd /data1/ecog_project/edf/$subject/
   cd /nas/ecog_project/edf/$subject/
   find . -name '*.edf' -exec python /home/stepeter/Documents/ECoG_Preprocessing/Steve_preprocPipeline.py -s $subject -d '{}' -lp /nas/ecog_project/edf/$subject/ -sp /data1/ecog_project/derived/processed_ecog/$subject/preproc_hospital_ecog/ -af False \;
done
