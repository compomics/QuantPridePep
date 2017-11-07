FROM continuumio/anaconda

RUN apt-get update
RUN conda install numpy pandas scikit-learn 
RUN pip install argparse pymzML==0.7.8
RUN pip install simplejson
RUN apt-get install git
RUN apt-get install software-properties-common
RUN add-apt-repository http://ppa.launchpad.net/webupd8team/java/ubuntu
RUN echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" >>  /etc/apt/sources.list.d/java-8-debian.list 
RUN apt-get update
RUN apt-get install oracle-java8-installer

RUN apt-get install parallel

RUN echo "deb http://download.mono-project.com/repo/debian wheezy-apache24-compat main" | tee -a /etc/apt/sources.list.d/mono-xamarin.list
RUN echo "echo "deb http://download.mono-project.com/repo/debian jessie main" | tee /etc/apt/sources.list.d/mono-official.list
RUN apt-get update
RUN apt-get install -y mono-complete
RUN git clone  -b master  --single-branch https://github.com/compomics/moff /moFF
RUN git clone  -b master  --single-branch https://github.com/compomics/QuantPridePep.git  /moFF_pipeline

WORKDIR /moFF_pipeline
