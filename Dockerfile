FROM conda/miniconda3

RUN apt-get update -y 
RUN conda install python=3.6
RUN conda install numpy pandas scikit-learn
RUN conda install -c conda-forge pynumpress
RUN conda install simplejson
RUN pip install pymzML pyteomics brain-isotopic-distribution
RUN apt-get update -y
RUN apt-get install git -y
RUN apt-get install gnupg -y 

RUN apt-get update -y

RUN apt-get install parallel -y

RUN RUN echo "deb http://download.mono-project.com/repo/debian wheezy-apache24-compat main" | tee -a /etc/apt/sources.list.d/mono-xamarin.list
RUN apt-get update 
RUN apt-get install mono-complete -y
RUN git clone  -b master  --single-branch https://github.com/compomics/moff /moFF
RUN git clone  -b master  --single-branch https://github.com/compomics/QuantPridePep.git  /moFF_pipeline

WORKDIR /moFF_pipeline
