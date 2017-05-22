#!/bin/bash

deployDir=/home/compomics/second_disk/Pride_pipeline_local
input_folder=${deployDir}/$1

#moFf_workdir= /home/compomics/moFF_multipr_rawfile

timestamp=$1'_moFF'
deployDir=${deployDir}/$timestamp


if [ ! -d "$deployDir" ]; then 
	echo "MGF parsing --> creating .moff2start"
	mkdir $deployDir
fi
#ls folder/submmited/*.raw | parallel mono ms2extract.exe  {1} 

<< comment
echo "MGF parsing --> creating .moff2start"
java -jar mzparser-1.0.0.jar  -i $input_folder -o $deployDir -m


echo "mztab parsing --> creating .txt with identification data"
java -jar mzparser-1.0.0.jar  -i $input_folder -o $deployDir -z

echo "Extraction MS2 info from raw file --> creating .moff2scan "
## extraxt MS2 scan from raw file 

#ls "$input_folder"/submitted/*.raw  | parallel --no-notice  --joblog log_ms2scan   "mono ms2extract.exe -f  {1} >  $deployDir/{/.}.ms2scan"

ls "$input_folder"/submitted/*.RAW  | parallel --no-notice  --joblog log_ms2scan   "mono ms2extract.exe -f  {1} >  $deployDir/{/.}.ms2scan"

echo "Join moFF2start with ms2scan --> create moFf input"

# parse mgf, and perform join with the MS2 scan output --> create input file for moFF
python create_input_from_mgf.py --start_folder $deployDir --output $deployDir --type mgf


# note change dir in  bash : you shoudl add the script to the patch and run like.scriptname
comment
cd $cdmoFFwdir

#ls 

# run moFF for all the moFf input file 
echo 'running moFF on all the ms2feat_input file '
## file .raw
#ls $deployDir/*.ms2feat_input | parallel --no-notice --joblog $deployDir/log_moff python moff.py --inputtsv {1} --inputraw $input_folder/submitted/{/.}.raw --tol 10 --rt_w 2 --rt_p 0.4 --output_folder $deployDir/moff_output

## file .RAW capitals
ls $deployDir/Cha2*.ms2feat_input | parallel --no-notice --joblog $deployDir/log_moff python moff.py --inputtsv {1} --inputraw $input_folder/submitted/{/.}.RAW --tol 10 --rt_w 2 --rt_p 0.4 --output_folder $deployDir/moff_output



cd $cdInitwdir
<< comment2

echo "Join moFf result with mztab proccessed --> create moFF quant with identification result "

# parse mgf, and perform join with the MS2 scan output --> create input file for moFF
python create_input_from_mgf.py --start_folder $deployDir/moff_output --output $deployDir --type mztab

comment2
