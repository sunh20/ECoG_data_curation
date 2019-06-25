#!/bin/sh
subjects='fcb01f7a' #a0f66459 aa97abcd b4ac1726 c95c1e82 d6532718 e5bad52f ec374ad0 fcb01f7a a86a4375 ab2431d9 c7980193 cb46fd46 d7d5f068 ffb52f92'
for subject in $subjects
do
    python add_NW_starttime_intermediate_files.py -lp /data1/users/stepeter/NW_start_times/ -s $subject
done
