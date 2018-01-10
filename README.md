# QuantPridePep
This pipeline provides MS1 peptides intensities for PRIDE "complete" submitted project using moFF.

---


## Minimum Requirements ##

Required java version :
- Java Runtime Environment (JRE) 8


 [moFF](https://github.com/compomics/moFF/tree/master) should be installed separately on your machine.


Required python libraries for moFF :
- Python 2.7
- pandas  > 0.20
- numpy > 1.10.0
- argparse > 1.2.1 
- scikit-learn > 0.17
- pymzML > 0.7.7

Required library for MSFilereader by Thermo 
- mono library version 4.2.1
 
---


## Structure of the pipeline and its components  ##

The pipeline for each raw file present in the project runs the following steps:
- from each Thermo raw file, ms2extraction.exe extracts retention time and mz data for all MS2 spectra recorded. As output, it creates *.moff2scan* files

- starting from  *.moff2scan*, input file for moFF are created and stored as *ms2feat_input* 

- running moFF on the *ms2feat_input* file and their corrispondent Thermo raw files

- parsing PRIDE mgf file using the Pride java library. As output, it creates *.moff2start* file where MS2 spectra details are stored (mz,charge,spectra indexes )  

- merging data contained in .moff2start with the result of moFF *_moFF_result.txt*. As output, it creates *_moff_result_ms2id.txt* files that contain the MS1 intensities for all the spectras in the mgf. At this step we also save the output of moFF on all the MS2 spectra recorded in the standard output file of moFF (*_moff_result.txt*)

- Parsing all the idenfication result contained in the mzTab files of the project  and joining those information with the quantification result found in  *_moff_result_ms2id.txt* files. Two types of output are produced: one is still *mzTab* file but with all the quantitive information provided by moFF for each psm and the other is  that contains the same infomation but in simply tab delimited file *.ms1_quant* .  


---

## Output ##


The ouput file  with peptide MS1 intensities and their quality measures are produced  in two formats :
- .ms1_quant file (they are basically standard moFF output file)

- .mzTab file (where along with the original identified peptide information, the moFF quantitative data is added)


## Set-up and running  ##
 - Be sure that Java and mono are installed in your environment.
 - Clone and install moFF on your machine : 
 
 `git clone -b master  --single-branch https://github.com/compomics/moff your_path/moFF`
 
 - Clone and install the pipeline : 
 
 `git clone -b master  --single-branch https://github.com/compomics/QuantPridePep.git  your_path/moFF_pipeline`

Open the file `create_input_from_mgf.py` and with any text editor adjust on lines 167-168 the absolute path of your your_path/moFF and your_path/moFF_pipeline. 


Use `python launch_pipeline.py -h`
```
  --f       	       file contains a list of valid PXDxxx id
  --docker_run         flag to activate/deactivate docker setting
  --output_location    input folder e.g where all PXDxx folder are located
  --input_location     output folder e.g where to all the moFF result for each project
  --prod_env           set if you run on production enviroment mztab file are located on the internal folder
```

Running the pipeline with the following command:

` python   launch_pipeline.py -f list_PXD_file  --docker_run 0 --input_location your_input_folder  --output_location your_output_folder  >> high_level_log_output.txt `

The folder *your_input_folder* should contain all the project folders (PXDxxxx) where are located the mgf and the raw file of each project.

In the output location, the pipeline will create for each project an output folder (PXDxxxx_moFF) where are located all the results and also all the intermediate files used.

Exhaustive pipeline logs are written in *moFF_pride_pipeline.log* instead of a higher level log is printed in the standard output.

NOTE : with *--prod_env 0* , the pipeline expects to find all the  original mgf , raw files and the pride mztab in the subfolder PXDxxxx/submitted. In case of **--prod_env 1** the pipeline looks for the original mgf and raw file in the folder PXDxxxx/submitted but the pride mztab file in **PXDxxxx/internal/**


--- 

## Structure of the output folder and its content ##
For every project correctly quantified the output  folder PXDxxxx_moFF should contains the following files and sub folders:
 - *.moff2start :  all the information parsed by the original mgf files   
 - *.moff2scan : all the ms2 events 
 - *.ms2feat_input : input files ready to be processed by moFF
 - moFF_output/ :  all the moFf result and log file are stored in this folder
 - *_moff_result_ms2id.txt : result of moFF associated with the mgf data
 - *_moff_result : simply the result of moFf for all the ms2 spectra founded in the Thermo raw file
 - result/ : this folder contains all the .ms1_quant and the mzTab file with the MS1 quant information added to the identified peptied provided in mzTAb file of the project. 
 - log_moFF :  log of the moFF tasks run by GNU parallel
 - log_ms2scan : log of the MS2 extraction from the raw file produced by GNU parallel


