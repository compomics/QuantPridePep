#!/bin/bash


##
# to set aliases you need add the followinf in .bashrc
#export cdmoFFwdir="/home/compomics/moFF_multipr_rawfile" 

## -- PATH where the run_pipeline.sh is launched
#export cdInitwdir="/home/compomics/second_disk/Pride_pipeline_local"

##

deployDir=/home/compomics/second_disk/Pride_pipeline_local
input_folder=${deployDir}/$1

#moFf_workdir= /home/compomics/moFF_multipr_rawfile

timestamp=$1'_moFF'
deployDir=${deployDir}/$timestamp


if [ ! -d "$deployDir" ]; then 
	echo "MGF parsing --> creating .moff2start"
	mkdir $deployDir
fi


#<< comment
echo "MGF parsing --> creating .moff2start"
java -jar mzparser-1.0.0.jar  -i $input_folder -o $deployDir -m


echo "Extraction MS2 info from raw file --> creating .moff2scan "
## extraxt MS2 scan from raw file 

#ls "$input_folder"/submitted/*.raw  | parallel --no-notice  --joblog log_ms2scan   "mono ms2extract.exe -f  {1} >  $deployDir/{/.}.ms2scan"

ls "$input_folder"/submitted/*.RAW  | parallel --no-notice  --joblog log_ms2scan   "mono ms2extract.exe -f  {1} >  $deployDir/{/.}.ms2scan"

echo "Join moFF2start with ms2scan --> create moFf input"

# parse mgf, and perform join with the MS2 scan output --> create input file for moFF
python create_input_from_mgf.py --start_folder $deployDir --output $deployDir --type mgf


# note change dir in  bash : you shoudl add the script to the patch and run like.scriptname


cd $cdmoFFwdir

#ls 

# run moFF for all the moFf input file 
echo 'running moFF on all the ms2feat_input file '
## file .raw
#ls $deployDir/*.ms2feat_input | parallel --no-notice --joblog $deployDir/log_moff python moff.py --inputtsv {1} --inputraw $input_folder/submitted/{/.}.raw --tol 10 --rt_w 2 --rt_p 0.4 --output_folder $deployDir/moff_output

## file .RAW capitals
ls $deployDir/*.ms2feat_input | parallel --no-notice --joblog $deployDir/log_moff python moff.py --inputtsv {1} --inputraw $input_folder/submitted/{/.}.RAW --tol 10 --rt_w 2 --rt_p 0.4 --output_folder $deployDir/moff_output

timestamp='_result'
deployDirRes=${deployDir}/$timestamp




cd $cdInitwdir

#comment

# this will be replaced and this step will be done in the java code
# parse mgf, and perform join with the MS2 scan output --> create input file for moFF

timestamp='_result'
deployDirRes=${deployDir}/$timestamp
mkdir $deployDirRes



#python create_input_from_mgf.py --start_folder $deployDir/moff_output --output $deployDir --type mztab

echo "mztab parsing & merging with moff result --> creating mztab.txt with quantification data"
java -jar mzparser-1.0.0.jar  -i $input_folder -o $deployDir/moff_output -z

if [[ $(ls -A $deployDir/moff_output/*.mztab) ]]; then 
	echo "Parsing done moving on result folder"
	#timestamp='_result'
	#deployDirRes=${deployDir}/$timestamp
	#mkdir $deployDirRes
	mv $deployDir/moff_output/*.mztab $deployDirRes
fi

#if [ [   $(ls -A $deplyDir/*.ms1_quant)   ] ]; then 
#	echo "Movinf ms1 quant file on result folder"
#	mv $deplyDir/*.ms1_quant $deployDirRes
#fi





