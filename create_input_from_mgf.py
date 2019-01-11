import sys
import os
import glob
import re
import argparse
import fnmatch
import pandas as pd
import numpy as np
#  merge ms2scan file and mgf 
# output ms2feature file 


def preproc_MS2data2moFF ( f1,name ) : 
    ms2raw_df =pd.read_csv(f1,sep="\t",header=None,names=['SCANS', 'time','masterScan', 'ionizationMode', 'precursorMass', 'monoisotopicMass', 'collisionEnergy', 'isolationWidth'])
    ms2raw_df['CHARGE']=np.nan
    ms2raw_df['INDEX']=np.nan
    ms2raw_df = ms2raw_df[['CHARGE','INDEX','time','precursorMass','SCANS']]
    ms2raw_df.columns= ['charge','#spectraindex','rt','mz','scan']
    ms2raw_df.to_csv(os.path.join(args.output, os.path.basename(name +'.ms2feat_input')) ,sep='\t',index=False )
    return 0




def merge_omega_moFFquant(f1,f2,name,args):
    omega_df =pd.read_csv(f1,sep=",")
    # Case where spec_is is nameFile.sca.scan.charge
    # it could change !!! 
    omega_df['scan']=  omega_df['spec_id'].str.split(".",expand=True)[1]
    omega_df['scan'] = omega_df['scan'].astype(int)
    ms2raw_moff= pd.read_csv(f2,sep="\t")
    ## clean data from moFF side
    if ( ms2raw_moff[ ms2raw_moff['log_int'] == -1].shape[0] /  ms2raw_moff.shape[0] )  >=  0.5:
        print ( '{%s} detected missing intensity more the O.5 pec'.format(f1))

    ms2raw_moff = ms2raw_moff[ ms2raw_moff['log_int'] != -1]
    
    test= pd.merge(omega_df,ms2raw_moff[['scan','rt','mz','intensity','rt_peak','lwhm','rwhm','5p_noise','10p_noise','SNR','log_L_R','log_int']],on='scan',how='left')
    test.to_csv(os.path.join(args.output, 'result',os.path.basename(name +'_omega_quant.txt')) ,sep='\t',index=False )
    return 0


def merge_mgf_moFFquant( f1,f2,name,args):
    mgf_df =pd.read_csv(f1,sep="\t")
    if mgf_df.SCANS.any() == 'null':
        print ('\t  Input file is based ONLY of ms2 scan for {%r} '.format(f1))
        return 2
    #print  mgf_df.columns
    mgf_df.drop(['RTINSECONDS','PEPMASS'],axis=1,inplace=True)
    mgf_df.columns = ['#spectraindex','scan','charge']
    #print mgf_df.head()
    ms2raw_moff= pd.read_csv(f2,sep="\t")
    test= pd.merge(mgf_df,ms2raw_moff[['scan','rt','mz','intensity','rt_peak','lwhm','rwhm','5p_noise','10p_noise','SNR','log_L_R','log_int']],on='scan',how='left')
    ## attention I over write the result of moFF  
    test.to_csv(os.path.join(args.output, os.path.basename(name +'_moff_result_ms2id.txt')) ,sep='\t',index=False )
    return 0


def merge_mgf_MS2data( f1,f2,name,args):
    #open 2 file
    mgf_df =pd.read_csv(f1,sep="\t")
    ms2raw_df =pd.read_csv(f2,sep="\t",header=None,names=['SCANS', 'time','masterScan', 'ionizationMode', 'precursorMass', 'monoisotopicMass', 'collisionEnergy', 'isolationWidth'])
    #print mgf_df.shape, ms2raw_df.shape
    # convert to int the scan number
    if mgf_df.SCANS.any() == 'null':
        print ('\t  ','SCAN Id not available in the mgf file for {%r} '.format(f1))
        print ('\t  Input file is based ONLY of ms2 scan')
        ms2raw_df['CHARGE']=np.nan
        ms2raw_df['INDEX']=np.nan
        ms2raw_df = ms2raw_df[['CHARGE','INDEX','time','precursorMass','SCANS']]
        ms2raw_df.columns= ['charge','#spectraindex','rt','mz','scan']
        ms2raw_df.to_csv(os.path.join(args.output, os.path.basename(name +'.ms2feat_input')) ,sep='\t',index=False )
        return 2
    ms2raw_df['SCANS']= ms2raw_df['SCANS'].astype('int64')
    mgf_df['SCANS']= mgf_df['SCANS'].astype('int64')
    #print mgf_df[mgf_df['INDEX']== 1004]
    #print ms2raw_df[ms2raw_df['SCANS']== 13714 ]
    #  SQL left join . mgf_df drives the join result
    test= pd.merge(mgf_df,ms2raw_df,on='SCANS',how='left')
    #print test.head(5)
    test= test[['CHARGE','INDEX','time','precursorMass','SCANS']]
    test.columns= ['charge','#spectraindex','rt','mz','scan']
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
    #print 'input mztab',mztab_df.shape, 'moff output',moff_df.shape
    #print 'moff output min spectaIndex ' , moff_df['#spectraindex'].min(), 'max SpectraIndex',  moff_df['#spectraindex'].max(), '#uniqueIndex',moff_df['#spectraindex'].unique().shape
    moff_df['#spectraindex']= moff_df['#spectraindex'].astype('int64')
    moff_df['charge'] = moff_df['charge'].str.split('+').str[0]
    moff_df['charge'] =  moff_df['charge'].astype('int64')
    # charge  #spectraindex   rt      mz      intensity       rt_peak lwhm    rwhm    5p_noise        10p_noise       SNR     log_L_R log_int
    #print mztab_df['spectraRef'].shape
    #print mztab_df["spectraRef"].str.split('=').str[1].shape
    mztab_df['#spectraindex']=  mztab_df["spectraRef"].str.split('=').str[1]
    mztab_df['#spectraindex']= mztab_df['#spectraindex'].astype('int64')
    #print  'mztab  min spectaIndex ',mztab_df['#spectraindex'].min(), 'max SpectraIndex',  mztab_df['#spectraindex'].max(), '#uniqueIndex',mztab_df['#spectraindex'].unique().shape
    #mztab_df.columns= ['prot',  'expMZ'   ,'calcMZ',  'modification' ,'peptide charge', 'spectraRef']
    # prot    expMZ   calcMZ  modification    peptide charge  spectraRef
    test= pd.merge(mztab_df,moff_df,on=['#spectraindex','charge' ],how='left')
    #print test['intensity'][pd.isnull(test['intensity'])].shape
    # filtering moff -1
    #print 'missing hit on moFF',test[test['intensity']==-1].shape
    #print 'missing hit',test[test['intensity']==-1]
    if test.shape [0] == mztab_df.shape[0]:
        test = test[test['intensity'] !=-1]
        print ('\t\t {%r}final output size (filtered moff output){%r}:'.format(name ,test.shape) )
        
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
    print ('# Spectra {%i}'.format(len(pos)))
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
    print( args.start + '/submitted/*.mgf')
    for name in glob.glob(args.start + '/submitted/*.mgf'):
        print ('\t' + name)
        #print file_in
        res = check_scannumber(name,args)
        # res containes the path and file name for the two file of the marging and just the name of file
        final_data = merge_mgf_MS2data( res[0],res[1],res[2],args)
        if final_data == -1:
            print ('Error : Joinning failed No input file for  {%s}'.format(name))
        

    return 0


# run method to pre proc. MS2 data into feat input


def run_preproc (args):
    print (args.start + '/*.ms2scan')
            #mgf_proc= sorted(glob.glob(args.start + '/*.moff2start' ))
    scan_proc= sorted(glob.glob(args.start + '/*.ms2scan' ))
            #print len (mgf_proc),len(scan_proc)
            #print mgf_proc[0]
            #print  scan_proc[0]
    for ii in range(0,len(scan_proc)):
        print ('\t' + scan_proc[ii])
        final_data =  preproc_MS2data2moFF ( scan_proc[ii],os.path.basename(scan_proc[ii]).split('.')[0] )
        if final_data == -1:
            print ('Error : preproc failed  for {%s} '.format(scan_proc[ii]))
            exit(1 )
    return 1
        
def run_join_omega (args):
    print (args.start + '/omega/*.mgf.omega.csv')

    omega_proc= sorted(glob.glob(args.start + '/omega/*.mgf.omega.csv' ))
    scan_proc= sorted(glob.glob(args.output + '/moff_output/*_moff_result.txt' ))
    print ( len(omega_proc), len(scan_proc) )
    for ii in range(len(omega_proc)) :
        print ('\t' +  omega_proc[ii] + ' -- ' + scan_proc[ii] )
        final_data = merge_omega_moFFquant( omega_proc[ii],scan_proc[ii],os.path.basename(omega_proc[ii]).split('.')[0] ,args )
        if final_data == -1:
            print ('Error : Join failed No input file for {%s} '.format(omega_proc[ii]) )
            exit(1 )

    if final_data == 2:
        return 1
    else:
        return 0


# run methods for the mgf  to MS2 data 
#Still used in the pipeline
def run_join (args):
        print (args.start + '/*.moff2start')
        
        mgf_proc= sorted(glob.glob(args.start + '/*.moff2start' ))
        
        ## for pipeline where all the ms2  mgf spectra drive
        #scan_proc= sorted(glob.glob(args.start + '/*.ms2scan' ))
        
        #for pipeline where all the ms2even drive
        scan_proc= sorted(glob.glob(args.start + '/moff_output/*_moff_result.txt' ))
        #------

        print (len (mgf_proc) , len(scan_proc))
        #print mgf_proc[0]
        #print  scan_proc[0]
        for ii in range(0,len(mgf_proc)):
            print ('\t' +  mgf_proc[ii] + '_' +  scan_proc[ii] )
            
            # res containes the path and file name for the two file of the marging and just the name of file
            final_data = merge_mgf_moFFquant( mgf_proc[ii],scan_proc[ii],os.path.basename(mgf_proc[ii]).split('.')[0] ,args )
            # for prex version of the pipeline
            #final_data = merge_mgf_MS2data(mgf_proc[ii],scan_proc[ii],os.path.basename(mgf_proc[ii]).split('.')[0] ,args)
            if final_data == -1:
                print ('Error : Join failed No input file for {%s} '.format(mgf_proc[ii]) )
                exit(1 )

        if final_data==2:
            return 1
        else:
            return 0

# parsing moff result with the pride.txt result (from mztab)
# not used anymore , this step will be embedded into tha java code
def run_join_mztab( args):
    print (args.start + '/*_moff_result_ms2id.txt')
    # debug for pipeline drived by ms2 from mgf
    #moff_proc= sorted(glob.glob(args.start + '/*_moff_result.txt' ))
    # for new version of the pieeline
    moff_proc= sorted(glob.glob(args.start + '/*_moff_result_ms2id.txt' ))
    # for ms2identified 
    mztab_proc= sorted(glob.glob(args.output + '/*.pride.txt' ))
    
    #print moff_proc 
    #print '----- // -----'
    #print mztab_proc
    #print mgf_proc[0]
    #print  scan_proc[0]
    for ii in range(0,len(moff_proc)):
        #print '\t', moff_proc[ii]
        res =  [ s for s in mztab_proc  if os.path.basename(moff_proc[ii]).split('_moff_result_ms2id.txt')[0]  in s]
        if len(res) >= 1:
            print ('merging between {%r} {%r} '.format(  moff_proc[ii], res[0]))
            final_data = merge_moff_mztab(moff_proc[ii],res[0],os.path.basename(res[0]).split('.')[0] ,args)
            if final_data == -1:
                print ('Error : Merging failed No input file for {%r} {%r}' ,  moff_proc[ii],res[0] )
                exit(1)
            # res containes the path and file name for the two file of the marging and just the name of 
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='General Purpose code for join and preprocessin the moFF pipeline for Pride data preprocessing ')

    parser.add_argument('--start_folder', dest='start', action='store',
                        help='specify the folder of the input MS2 peptide files  REQUIRED]', required=True)

    parser.add_argument('--output', dest='output', action='store',
                                    help='specify the output folder of the prepproccesed files  REQUIRED]', required=True)
    parser.add_argument('--type',dest='type',action='store',help='Specify the type of merge:  mgf ( join mgf -> scan data)  mztab(join moff -> mztab REQUIRED',required=True )

    args = parser.parse_args()
    #print args

    if args.type=='prems2':
        result_pride_id = run_preproc ( args )

    if args.type=='mgf':
        result_pride_id = run_join(args)

    if args.type=='omega':
        result_pride_id = run_join_omega(args)
    # actually not used but implemented using a java
    if args.type=='mztab':
        result_pride_id = run_join_mztab(args)
    if result_pride_id == 1:
        exit(2) # special case fla
    else:
        exit(0)  #" good exit no erroe  
    

