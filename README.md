# QuantPridePep
This pipeline provides MS1 peptides intensities for PRIDE "complete" submitted project using moFF.


---

## Structure of the pipeline and its components  ##

The pipeline is tructures in the following step:
- Parsing PRIDE mgf file using the Pride java library (*mzparser_1.0.0.jar*).  As output it creates *.moff2start file where MS2spectra details are stored (mz,charge,index os the spectra)  
- Retention time extraxtion from original thermo raw file using the ms2extraction.exe for all MS2 spectra recorder.As output it creates *.moff2scan* file.
- Merging of the data contained in *.moff2start and in *.moff2scan* files to create input file from moFF (*create_input.py*) . As output it creates *.ms2feat_input* file 

---

##  ##




---



---

## Introduction ##

moFF is an OS independent tool designed to extract apex MS1 intensity using a set of identified MS2 peptides. It currently uses a Go library to directly extract data from Thermo Raw spectrum files, eliminating the need for conversions from other formats. Moreover, moFF also allows to work directly with mzML files.

moFF is built up from two standalone modules :
- *moff_mbr.py* :  match between run (mbr)
- *moff.py*: apex intensity

NOTE : Please use *moff_all.py* script to run the entire pipeline with both MBR and apex strategies.

The version presented here is a commandline tool that can easily be adapted to a cluster environment. A graphical user interface can be found [here](https://github.com/compomics/moff-gui). The latter is designed to be able to use [PeptideShaker](https://github.com/compomics/peptide-shaker) results as an input format. Please refer to the [moff-GUI](https://github.com/compomics/moff-gui) manual for more information on how to do this.

[Top of page](#moff)

----



