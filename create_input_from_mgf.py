import sys
import os
import glob
import re
import argparse
import fnmatch
import pandas as pd

#  merge ms2scan file and mgf 
# output ms2feature file 

def merge_mgf_MS2data( f1,f2,name,args):
    #open 2 file
    mgf_df =pd.read_csv(f1,sep="\t")
    ms2raw_df =pd.read_csv(f2,sep="\t",header=None,names=['SCANS', 'time','masterScan', 'ionizationMode', 'precursorMass', 'monoisotopicMass', 'collisionEnergy', 'isolationWidth'])
    print mgf_df.shape, ms2raw_df.shape
    # convert to int the scan number
    ms2raw_df['SCANS']= ms2raw_df['SCANS'].astype('int64')
    mgf_df['SCANS']= mgf_df['SCANS'].astype('int64')
    #print mgf_df[mgf_df['INDEX']== 1004]
    #print ms2raw_df[ms2raw_df['SCANS']== 13714 ]
    #  SQL left join . mgf_df drives the join result
    test= pd.merge(mgf_df,ms2raw_df,on='SCANS',how='left')
    #print test.head(5)
    test= test[['CHARGE','INDEX','time','precursorMass']]
    test.columns= ['charge','#spectraindex','rt','mz']
    #print test[test['#spectraindex']==1004]
    #print test.columns
    #print 'Join df cleaned',test.shape
    # cnaive check if the join works weel ||| should be updated 
    if test.shape [0] == mgf_df.shape[0]:
        test.to_csv(os.path.join(args.output, os.path.basename(name +'.ms2feat_input')) ,sep='\t',index=False )
        return 0
    else:
        return -1
    #open 2

# merge moff output and mztab
# Not  used  anymore 
# This step is actually performed in the java


def merge_moff_mztab(f1,f2,name ,args):
    moff_df =pd.read_csv(f1,sep="\t")
    mztab_df =pd.read_csv(f2,sep="\t")
    print 'input mztab',mztab_df.shape, 'moff output',moff_df.shape
    print 'moff output', moff_df['#spectraindex'].min(),  moff_df['#spectraindex'].max(), moff_df['#spectraindex'].unique().shape
    moff_df['#spectraindex']= moff_df['#spectraindex'].astype('int64')
    moff_df['charge'] = moff_df['charge'].str.split('+').str[0]
    moff_df['charge'] =  moff_df['charge'].astype('int64')
    # charge  #spectraindex   rt      mz      intensity       rt_peak lwhm    rwhm    5p_noise        10p_noise       SNR     log_L_R log_int
    #print mztab_df['spectraRef'].shape
    #print mztab_df["spectraRef"].str.split('=').str[1].shape
    mztab_df['#spectraindex']=  mztab_df["spectraRef"].str.split('=').str[1]
    mztab_df['#spectraindex']= mztab_df['#spectraindex'].astype('int64')
    print  'mztab',mztab_df['#spectraindex'].min(),  mztab_df['#spectraindex'].max(), mztab_df['#spectraindex'].unique().shape
    #mztab_df.columns= ['prot',  'expMZ'   ,'calcMZ',  'modification' ,'peptide charge', 'spectraRef']
    # prot    expMZ   calcMZ  modification    peptide charge  spectraRef
    test= pd.merge(mztab_df,moff_df,on=['#spectraindex','charge' ],how='left')
    #print test['intensity'][pd.isnull(test['intensity'])].shape
    # filtering moff -1
    print 'missing hit',test[test['intensity']==-1].shape
    #print 'missing hit',test[test['intensity']==-1]
    if test.shape [0] == mztab_df.shape[0]:
        test = test[test['intensity'] !=-1]
        print '\t\t','final output size (filtered moff output) :',name ,test.shape 
        
        test.to_csv(os.path.join(args.output, os.path.basename(name +'.ms1_quant')) ,sep='\t',index=False )
        return 0
    else:
        return -1

    return 
# parsing header for MGF
# Not used used

def parse_header( lista_x ,count ):
    # mass,chare,rt,mz_computed,scans
    value_retrieved=[-1,-1,-1,-1,-1,-1]
    for x in lista_x :
        #print x
        if 'CHARGE' in x:
                 value_retrieved[1] = int(x.strip().split('CHARGE=')[1].split('+')[0])
        if 'RTINSECONDS' in x:
                 value_retrieved[2] = float(x.strip().split('=')[1])
        if 'PEPMASS' in x:
                if ' ' in x:
                        ## case with  optional intensity associated to get out
                        value_retrieved[0] = float(x.strip().split('PEPMASS=')[1].split(' ')[0])
                else:
                         value_retrieved[0] = float(x.strip().split('PEPMASS=')[1])
        if 'SCANS' in x:
                 value_retrieved[4] = float(x.strip().split('=')[1])

    if  value_retrieved[0] != -1 and value_retrieved[1] != -1 :
             value_retrieved[3]=  (value_retrieved[0] +  value_retrieved[1] ) / value_retrieved[1]
    value_retrieved[5]=count
    #only for standard output writing
    value_retrieved  = [ str(x)  for x in value_retrieved]
    return value_retrieved

'''
check_scannumber:
input : mgf file path
output : moff2start file with scan rt and the other info

it return:
[0]
'''
## parsing mfg 
# not used anymore
def check_scannumber(file2scan,args):
    col_list=['mz','charge','rt','mass','scan',"#spectramgf"]
    init_str='BEGIN IONS'
    end_str='END IONS'
    pos=[]
    output_name_mgfparsed= os.path.basename(file2scan).split('.')[0] + ".moff2start"
    with open(file2scan ,'r') as f:
        for num, line in enumerate(f, 1):
           # print line
                if init_str in line:
                        pos.append(num)
                if end_str in line:
                        pos.append(num)
    f.close()

    f= open(os.path.join(os.getcwd(),file2scan),'r')
    f2=open ( os.path.join(args.output,output_name_mgfparsed),'w' )
    f2.write('\t'.join(col_list)+'\n' )
    print '# Spectra',len(pos)
    total=f.readlines()
    # for just one spectra !i
    #mass =-1
    #rt =-1
    #charge = -1
    count=0
    for (i, k) in zip(pos[::2], pos[1::2]):

        # thuis offset is up to the user
        ads = total[i:i+6]
        #clean the string
        ads = [ x.strip()  for x in ads]
        result =parse_header(ads,count)
        #print '# spectra',count,resulti
        #print '\t'.join(result)
        f2.write('\t'.join(result)+'\n' )
        '''
        if count==0 :
            df= pd.DataFrame(data=[result], columns = col_list)
        else:
            df= df.append(result)
        '''
        count+=1
    f.close()
    f2.close()
    return (os.path.join( args.output ,output_name_mgfparsed), os.path.join(args.output, os.path.basename(file2scan).split('.')[0]+'.ms2scan'), os.path.basename(file2scan).split('.')[0] )

# run methods for the mgf parsing 
# not used anymore
def run_parser (args):
    rt_tag=[]
    scan_tag=[]
    print args.start + '/submitted/*.mgf'
    for name in glob.glob(args.start + '/submitted/*.mgf'):
        print '\t', name
        #print file_in
        res = check_scannumber(name,args)
        # res containes the path and file name for the two file of the marging and just the name of file
        final_data = merge_mgf_MS2data( res[0],res[1],res[2],args)
        if final_data == -1:
            print 'Error : Joinning failed No input file for ',name
        

    return 0

# run methods for the mgf  to MS2 data 
#Still used in the pipemline
def run_join (args):
        print args.start + '/*.moff2start'
        
        mgf_proc= sorted(glob.glob(args.start + '/*.moff2start' ))
        scan_proc= sorted(glob.glob(args.start + '/*.ms2scan' ))
        print len (mgf_proc),len(scan_proc)
        print mgf_proc[0]
        print  scan_proc[0]
        for ii in range(0,len(mgf_proc)):
            print '\t', mgf_proc[ii],scan_proc[ii]
            
            # res containes the path and file name for the two file of the marging and just the name of file
            final_data = merge_mgf_MS2data(mgf_proc[ii],scan_proc[ii],os.path.basename(mgf_proc[ii]).split('.')[0] ,args)
            if final_data == -1:
                exit('Error : Joinning failed No input file for ',name)
                
        return 0

# parsing moff result with the pride.txt result (from mztab)
# not used anymore , this step will be embedded into tha java code
def run_join_mztab( args):
    print args.start + '/*._moff_result.txt'
    moff_proc= sorted(glob.glob(args.start + '/*_moff_result.txt' ))
    mztab_proc= sorted(glob.glob(args.output + '/*.pride.txt' ))
    print len (moff_proc),len(mztab_proc)
    #print mgf_proc[0]
    #print  scan_proc[0]
    for ii in range(0,len(moff_proc)):
        print '\t', moff_proc[ii],mztab_proc[ii]      
        # res containes the path and file name for the two file of the marging and just the name of 
        final_data = merge_moff_mztab(moff_proc[ii],mztab_proc[ii],os.path.basename(mztab_proc[ii]).split('.')[0] ,args)
        if final_data == -1:
            exit('Error : Joinning failed No input file for ',name)
    return 0
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Checking rt or scan number throw the Pride dataset ')

    parser.add_argument('--start_folder', dest='start', action='store',
                        help='specify the folder of the input MS2 peptide files  REQUIRED]', required=True)

    parser.add_argument('--output', dest='output', action='store',
                                    help='specify the output folder of the prepproccesed files  REQUIRED]', required=True)
    parser.add_argument('--type',dest='type',action='store',help='Specify the type of merge:  mgf ( join mgf -> scan data)  mztab(join moff -> mztab REQUIRED',required=True )


    args = parser.parse_args()
    print args
    if args.type=='mgf':
        result_pride_id = run_join(args)
    # actually not used but implemented using a java
    if args.type=='mztab':
        result_pride_id = run_join_mztab(args)
    

