#!/bin/bash

#this script takes a txt file (from the .csv) of the x,y,z coordinates of all electrodes in a montage and converts them to MNI coords and then appends HO and Talairach labels
#Can be for pediatric or adult brains

if [ $# != 4 ]; then
	
	echo "
	
	Usage: sbjid TrodesCoordsList MPRAGE ageTemplate (1 = 2-3 yrs; 2 = 4-8; 3 = 7-11 yrs; 4 = adult)
	
	You need a .txt file of the trodes coords in PWD. COORDS ARE ALWAYS IN MM!
		
		-  MPRAGE must be Betized

    Will print out HO and Talairach region labels per electrode (only in adult brain)
		
	For pediatric brain, this script will register native into an
	AgeAppropriate template first

        Now registering into the 1 mm MNI template brain
	
	"
		
		
	exit
fi

echo "

To start: did you cd into the 'to be analyzed' directory?

"


SBJID=$1
TrodesCoordsList=$2
BRAIN=$3
ageTemplate=$4



	datadir=$PWD #stores the pwd (has to be caps on the command line) into a variable called datadir
	
	
	pwd 
	echo $datadir
	echo "These two directories should be the same!!!"
	echo "age appropriate templatae =" $ageTemplate
	echo ""
	echo "Creating transformation matrix"
	
	sleep 2
	
 #2.75-3.6 template brain
if [ "$ageTemplate" = "1" ] 
	then 
	
	#Flirt Native MPRAGE into Peds appropriate template brain
	echo "FLIRTING for 2-3 yr old brain"
	/home/stepeter/fsl/bin/flirt -in ${BRAIN} -ref /home/stepeter/fsl/data/standard/PedsAnatomicalTemplate/nihpd_asym_2.75-3.6/nihpd_asym_33-44_t1_bet.nii.gz -out native2peds -omat native2peds.mat -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12  -interp trilinear
	
	#Flrit Peds appropriate template brain onto MNI brain and apply transform to coreg'ed native to peds
	/home/stepeter/fsl/bin/flirt -in /home/stepeter/fsl/data/standard/PedsAnatomicalTemplate/nihpd_asym_2.75-3.6/nihpd_asym_33-44_t1_bet.nii.gz -ref /home/stepeter/fsl/data/standard/MNI152_T1_1mm_brain -out peds2MNI -omat peds2MNI.mat -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12  -interp trilinear
	/home/stepeter/fsl/bin/flirt -in native2peds.nii.gz -ref /home/stepeter/fsl/data/standard/MNI152_T1_1mm_brain -out peds2MNI_shadowreg_native2peds.nii.gz -applyxfm -init peds2MNI.mat -interp trilinear

	echo "Flirting completed"

elif [ "$ageTemplate" = "2" ] #4-8 yr old brain
then 
	
	#Flirt Native MPRAGE into Peds appropriate template brain
	echo "FLIRTING for 4-8 yr old brain"
	/home/stepeter/fsl/bin/flirt -in ${BRAIN} -ref /home/stepeter/fsl/data/standard/PedsAnatomicalTemplate/nihpd_asym_04.5-08.5_nifti/nihpd_asym_04.5-08.5_t1_bet.nii.gz -out native2peds -omat native2peds.mat -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12  -interp trilinear
	
	#Flrit Peds appropriate template brain onto MNI brain and apply transform to coreg'ed native to peds
	/home/stepeter/fsl/bin/flirt -in /home/stepeter/fsl/data/standard/PedsAnatomicalTemplate/nihpd_asym_04.5-08.5_nifti/nihpd_asym_04.5-08.5_t1_bet.nii.gz -ref /home/stepeter/fsl/data/standard/MNI152_T1_1mm_brain -out peds2MNI -omat peds2MNI.mat -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12  -interp trilinear
	/home/stepeter/fsl/bin/flirt -in native2peds.nii.gz -ref /home/stepeter/fsl/data/standard/MNI152_T1_1mm_brain -out peds2MNI_shadowreg_native2peds.nii.gz -applyxfm -init peds2MNI.mat -interp trilinear

	echo "Flirting completed"
elif [ "$ageTemplate" = "3" ] 
then 

	#Flirt Native MPRAGE into Peds appropriate template brain
	echo "FLIRTING for 9-11 yr old brain"
	/home/stepeter/fsl/bin/flirt -in ${BRAIN} -ref /home/stepeter/fsl/data/standard/PedsAnatomicalTemplate/nihpd_asym_07.0-11.0_nifti/nihpd_asym_07.0-11.0_t1_bet.nii.gz -out native2peds -omat native2peds.mat -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12  -interp trilinear
	
	#Flrit Peds appropriate template brain onto MNI brain and apply transform to coreg'ed native to peds
	/home/stepeter/fsl/bin/flirt -in /home/stepeter/fsl/data/standard/PedsAnatomicalTemplate/nihpd_asym_07.0-11.0_nifti/nihpd_asym_07.0-11.0_t1_bet.nii.gz -ref /home/stepeter/fsl/data/standard/MNI152_T1_1mm_brain -out peds2MNI -omat peds2MNI.mat -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12  -interp trilinear
	/home/stepeter/fsl/bin/flirt -in native2peds.nii.gz -ref /home/stepeter/fsl/data/standard/MNI152_T1_1mm_brain -out peds2MNI_shadowreg_native2peds.nii.gz -applyxfm -init peds2MNI.mat -interp trilinear
	
	echo "Flirting completed"
fi

if [ "$ageTemplate" = "4" ] #adult case - assumes MNI_1mm brain
then 
	
	#Flirt Native MPRAGE into MNI brain 
	echo "Flirting"
	/home/stepeter/fsl/bin/flirt -in ${BRAIN} -ref /home/stepeter/fsl/data/standard/MNI152_T1_1mm_brain.nii.gz -out native2mni -omat native2mni.mat -bins 256 -cost corratio -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 12  -interp trilinear
	
	echo "Flirting completed"
	
fi
	
########################################	
echo "Begin coordinate transform(s)"  
	
 #2.75-3.6 template brain
if [ "$ageTemplate" = "1" ] 
	then 
	
	echo "Transforming for 2-3 yr old brain"
	cat ${TrodesCoordsList} | img2stdcoord -img ${BRAIN} -std /home/stepeter/fsl/data/standard/PedsAnatomicalTemplate/nihpd_asym_2.75-3.6/nihpd_asym_33-44_t1_bet.nii.gz -xfm native2peds.mat -mm >> ${SBJID}_native2Peds_Coords.txt
	cat ${SBJID}_native2Peds_Coords.txt | img2stdcoord -img native2peds.nii.gz -std /home/stepeter/fsl/data/standard/MNI152_T1_1mm_brain.nii.gz -xfm peds2MNI.mat -mm >> ${SBJID}_Trodes_MNIcoords.txt

elif [ "$ageTemplate" = "2" ] #4-8 yr old brain
then 
	
	echo "Transforming for 4-8 yr old brain"
	cat ${TrodesCoordsList} | img2stdcoord -img ${BRAIN} -std /home/stepeter/fsl/data/standard/PedsAnatomicalTemplate/nihpd_asym_04.5-08.5_nifti/nihpd_asym_04.5-08.5_t1_bet.nii.gz -xfm native2peds.mat -mm >> ${SBJID}_native2Peds_Coords.txt
	cat ${SBJID}_native2Peds_Coords.txt | img2stdcoord -img native2peds.nii.gz -std /home/stepeter/fsl/data/standard/MNI152_T1_1mm_brain.nii.gz -xfm peds2MNI.mat -mm >> ${SBJID}_Trodes_MNIcoords.txt

elif [ "$ageTemplate" = "3" ] #9-11 yr old brain
then 
	
	echo "Transforming for 9-11 yr old brain"
	cat ${TrodesCoordsList} | img2stdcoord -img ${BRAIN} -std /home/stepeter/fsl/data/standard/PedsAnatomicalTemplate/nihpd_asym_07.0-11.0_nifti/nihpd_asym_07.0-11.0_t1_bet.nii.gz -xfm native2peds.mat -mm >> ${SBJID}_native2Peds_Coords.txt
	cat ${SBJID}_native2Peds_Coords.txt | img2stdcoord -img native2peds.nii.gz -std /home/stepeter/fsl/data/standard/MNI152_T1_1mm_brain.nii.gz -xfm peds2MNI.mat -mm >> ${SBJID}_Trodes_MNIcoords.txt

fi

if [ "$ageTemplate" = "4" ] #adult case - assumes MNI_1mm brain
then 
	
	echo "Transforming for the adult brain"
	x_coords=(`cat ${TrodesCoordsList} | img2stdcoord -img ${BRAIN} -std /home/stepeter/fsl/data/standard/MNI152_T1_1mm_brain -xfm native2mni.mat -mm | awk '{print $1}'`)
	y_coords=(`cat ${TrodesCoordsList} | img2stdcoord -img ${BRAIN} -std /home/stepeter/fsl/data/standard/MNI152_T1_1mm_brain -xfm native2mni.mat -mm | awk '{print $2}'`)        
	z_coords=(`cat ${TrodesCoordsList} | img2stdcoord -img ${BRAIN} -std /home/stepeter/fsl/data/standard/MNI152_T1_1mm_brain -xfm native2mni.mat -mm | awk '{print $3}'`)
        is_left=`echo ${x_coords[0]:0:1}`
        if [ "${is_left}" == "-" ]; then
          new_xs=()
          for i in ${x_coords[*]}; do
            new_xs=(${new_xs[*]} `echo "$i + 3" | bc -l`)
          done
        else
          new_xs=()
          for i in ${x_coords[*]}; do
            new_xs=(${new_xs[*]} `echo "$i - 3" | bc -l`)
          done
        fi
        
        ### Changing the Internal Field Separator allows us iterate over whole lines
        IFS=$'\n'
        echo "Working...."
        for j in `jot ${#new_xs[*]} 0`; do
          comma_coord=`echo "${new_xs[$j]} ${y_coords[$j]} ${z_coords[$j]}" | sed 's/ /,/g'`
          atlasout=(`atlasquery -a 'Harvard-Oxford Cortical Structural Atlas' -V -c ${comma_coord}`)
          Talairachout=(`atlasquery -a 'Talairach Daemon Labels' -V -c ${comma_coord}`)

          region=`echo ${atlasout[*]} | awk -F'>' '{print $4}'`
          Talregion=`echo ${Talairachout[*]} | awk -F'>' '{print $4}'`

                k=`echo "$j + 1" | bc` #count iteration equal to n + 1
                #echo "${j}" #debugging
                #echo "${k}" #debugging

            #echo "${new_xs[$j]}, ${y_coords[$j]}, ${z_coords[$j]}, ${region}" >> ${SBJID}_Trodes_MNIcoords.txt #original printing version
            echo "${x_coords[$j]}, ${y_coords[$j]}, ${z_coords[$j]}" >> ${SBJID}_Trodes_MNIcoords.txt
            echo "${k}, ${region}" >> ${SBJID}_Trodes_HO_Labels.txt
            echo "${k}, ${Talregion}" >> ${SBJID}_Trodes_Talairach_Labels.txt

          ### Get voxel coords to make point image(s)
          x_vox=`echo "(${x_coords[$j]} * -1) + 90" | bc`
          y_vox=`echo "${y_coords[$j]}  + 126" | bc`
          z_vox=`echo "${z_coords[$j]}  + 72" | bc`
          fslmaths /home/stepeter/fsl/data/standard/MNI152_T1_1mm_brain -mul 0 -add 1 -roi ${x_vox} 1 ${y_vox} 1 ${z_vox} 1 0 1 ${j}_point -odt float
          echo "Done with coords for electrode ${k}"
        done
        ### Just returning IFS to normal
        IFS=$' \t\n'
        ### And now let's merge all those point images we just made into one
        cmd=(`ls *point* | sed 's/.gz/.gz -add/g'`)
        cmd[${#cmd[*]}-1]=""
        fslmaths ${cmd[*]} coords.nii.gz
        rm *point.nii.gz*     

fi

echo "Cleaning up"

	#Clean up
	mkdir Coords_files	
	mv *.mat ./Coords_files
	mv *.nii.gz ./Coords_files
	mv *.txt ./Coords_files
	mv *.csv ./Coords_files
	
	cd Coords_files
	
	mv ${BRAIN} ../
	mv ${SBJID}_Trodes_MNIcoords.txt ../
    mv ${SBJID}_Trodes_HO_Labels.txt ../
    mv ${SBJID}_Trodes_Talairach_Labels.txt ../
	
	echo "
	
	DONE! Hope for the best
	
		
		"
		




