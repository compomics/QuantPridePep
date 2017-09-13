# QuantPridePep
This pipeline provides MS1 peptides intensities for PRIDE "complete" submitted project using moFF.

---


## Minimum Requirements ##

Required java version :
- Java Runtime Environment (JRE) 8


[moFF] (https://github.com/compomics/moFF/blob/multipr_rawfilereader/) should be installed separately on your machine.

Required python libraries for moFF :
- Python 2.7
- pandas  > 0.20
- numpy > 1.10.0
- argparse > 1.2.1 
- scikit-learn > 0.17
- pymzML > 0.7.7

Required library for MSFilereader by Thermo 
mono library version 4.2.1
 
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


The ouput file  with peptde MS1 intensities and their quality measures are produced  in two format :
.ms1_quant file ( they are basically standard moFF output file)

.mzTab file (where along with the original identified peptide information the quantitative data are added)


