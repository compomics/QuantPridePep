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
- parsing PRIDE mgf file using the Pride java library (*mzparser_1.0.0.jar*).  As output, it creates .moff2start file where MS2 spectra details are stored (mz,charge,index of the spectra)  
- retention time extraxtion from original thermo raw file using the ms2extraction.exe for all MS2 spectra recorder.As output it creates *.moff2scan* file.
- merging data contained in .moff2start and .moff2scan files to create input file from moFF (*create_input.py*). As output, it creates .ms2feat_input file 
- running moFF on the ms2feat_input file  and the Thermo raw file

- merging the result of moFF with the identidied peptide information present in the mzTab file. (*mzparser_1.0.0.jar*) 

---

## Output ##


The ouput file  with peptde MS1 intensities and their quality measures are produced  in two formats :
- .ms1_quant file (they are basically standard moFF output file)

- .mzTab file (where along with the original identified peptide information, the moFF quantitative data is added)


## Instal the pipeline and running  ##
 - Be sure that Java and mono are installed in your enviroment.
 - Clone and install moFF on your machine : `git clone -b master  --single-branch https://github.com/compomics/moff your_path/moFF`
 - Clone and install the pipeline : `git clone -b master  --single-branch https://github.com/compomics/QuantPridePep.git  your_path/moFF_pipeline`

Open the the file `create_input_from_mgf.py` with aany text editor and set on lines xx respectively the absolute path of your your_path/moFF and your_path/moFF_pipeline.
use `python launch_pipeline.py -h`
```
  --f       	       file contains a list of valid PXDxxx id
  --docker_run         flag to activate/deactivate docker setting
  --output_location    input folder e.g where all PXDxx folder are located
  --input_location     output folder e.g where to all the moFF result for each project
  --prod_env PROD_ENV  set if you run on production env. mztab file are located on the internal folder
```

Running the pipeline on :
` python   launch_pipeline.py -f list_PXD_file  --docker_run 0 --input_location your_input_folder  --output_location your_output_folder  >> high_level_log_output.txt `
The folder  your_input_folder should contains all the  project folders (PXD00xxxx) where are located the mgf and the raw file of each project.

In the output location, the pipeline will create for each project an output folder (PXDxxxx_moFF) where are located all the results and also all the intermediate files used.

Exhaustive pipeline logs are written in moFF_pride_pipeline.log instead of a more high level log is printed in the standard output

NOTE : with --prod_env 0 , the pipeline expect to find all the  original mgf , raw files and the pride mztab in the subfolder PXDxxxx/submitted. In case of --prod_env 1 the pipeline looks the originalm mgf anf raw file in the folder PXDxxxx/submitted but the pride mztab file in PXDxxxx/internal/

 


## Structure of the output folder and its content ##
For every project correctly quantified the output  folder PXDxxxx_moFF should contains the following files and sub folders:
 - *.moff2start : file contains all the information parsed by the original mgf files   
 - *.moff2scan : files  contain all the ms2 event 
 - *.ms2feat_input : input file ready to be parsed in moFF
 - moFF_output/ : this contians all the result and log file of moFF
 - result/ : this folder contians all the *.ms1_quant and the mzTab file with tha MS1 quant information added. 
 - log_moFF :  log of the moFf tasks run by GNU parallel
 - log_ms2scan : log of the MS2 extraction from the raw file produced by GNU parallel 


