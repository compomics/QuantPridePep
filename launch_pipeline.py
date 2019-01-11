import numpy as np
import pandas as pd
import os as os
import sys
import fnmatch
import subprocess
import shlex 
import logging
import argparse
import glob


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)



## output is a tupple 
## erro_code , Flag_for_only_MS2_scan_available

def run_command ( cmd ,  msg_cmd ,  log , flag_shell = False):
    p= subprocess.Popen( cmd ,stdout=subprocess.PIPE,stderr= subprocess.PIPE, shell = flag_shell )  
    output,err = p.communicate( )
    if p.returncode == 2:
        log.info('   ' + msg_cmd +  ' -->  DONE'  )
        return (0,True)
        ## 
    else:
        if p.returncode != 0:
            log.info('   ' + msg_cmd +' ERROR %s', err  )
            log.info('    %s', output  )
            return (1,False)
        else:
            log.info('   ' + msg_cmd +  ' -->  DONE'  )
            return (0,False)
    

def run_pipeline( prj_loc,log, DATAINPUT_LOC,  DATAOUTPUT_LOC, START_LOC , moFF_PATH ,flag_prod ):
     
    skip_steps_flag = False
    if not (os.path.isdir(   os.path.join( DATAOUTPUT_LOC, prj_loc  +'_moFF'  )   )): 
        os.makedirs(os.path.join(DATAOUTPUT_LOC, prj_loc +'_moFF'  ))
        output_folder = os.path.join(DATAOUTPUT_LOC, prj_loc    + '_moFF'  )
    else:
        output_folder = os.path.join(DATAOUTPUT_LOC, prj_loc    + '_moFF'  )
    
    input_folder = os.path.join( DATAINPUT_LOC, prj_loc  )
    
    result_folder = os.path.join(output_folder,  'result'  )
    if not (os.path.isdir(  result_folder   )):
        os.makedirs(result_folder)
    
        
    #log.info( '   Prj %s  -->  setting input folder  %s',  prj_loc, input_folder )
    #log.info( '   Prj %s  --> setting output folder %s',  prj_loc,output_folder )
   
    cap_flag= 0

    for f in os.listdir( os.path.join(input_folder, "submitted/" )):
        if fnmatch.fnmatch( f, '*.raw') :
            cap_flag = 0
            break
        if fnmatch.fnmatch( f, '*.RAW') :
            cap_flag = 1
            break

     
        
    # 1 step
    if cap_flag ==0:
        cmd =  " ls " + os.path.join(input_folder, "submitted/") + "*.raw | parallel --no-notice --joblog "+ os.path.join(output_folder ,"log_ms2scan")  + "  \" mono " +  os.path.join(START_LOC, "ms2extract.exe") + " -f {1}  > " + output_folder + "/{/.}.ms2scan \" "
    else:
        cmd= " ls " + os.path.join(input_folder, "submitted/") + "*.RAW | parallel --no-notice --joblog "+ os.path.join(output_folder ,"log_ms2scan")  + "  \" mono " +  os.path.join(START_LOC, "ms2extract.exe") + " -f {1}  > " + output_folder + "/{/.}.ms2scan \" "
    code_exec,flag_onlyMS2 =  run_command( cmd, '  1- Creating ms2scan file by ms2extractor', log, True  )

    if  code_exec== 1:
        return ( 0 )
     
    # 2 step 
    cmd = "python create_input_from_mgf.py --start_folder " + output_folder   +" --output " +  output_folder + " --type prems2 "
    code_exec,flag_onlyMS2 = run_command(  cmd, '  2- Creating moFF input ',log,True )

    if  code_exec== 1:
        return ( 0 )
    
    # 3  step
    
    if cap_flag ==0:
        cmd = " ls " + output_folder + "/*.ms2feat_input | parallel --no-notice  -j 3  --joblog "+ os.path.join(output_folder ,"log_moFF")  + " python " +  os.path.join(moFF_PATH ,'moff_all.py') + " --tsv_list {1}  --raw_list "+ input_folder + "/submitted/{/.}.raw --tol 10 --mbr off  --xic_length 3 --rt_peak_win 1 --loc_out " + os.path.join(output_folder,'moff_output' )
    else:
        cmd = " ls " + output_folder + "/*.ms2feat_input | parallel --no-notice  -j 3  --joblog "+ os.path.join(output_folder ,"log_moFF")  + " python " +  os.path.join(moFF_PATH ,'moff_all.py') + " --tsv_list {1}  --raw_list "+ input_folder + "/submitted/{/.}.RAW --tol 10 --mbr off --xic_length 3 --rt_peak_win 1 --loc_out " + os.path.join(output_folder,'moff_output' )

    code_exec,flag_onlyMS2    =run_command( cmd, '  3-  Running moFF ' ,log, True  )

    if  code_exec== 1:
        return ( 0 )
    

    # 4 step 
    # version with in house Pride reprocessing with ionbot 

    cmd ="python create_input_from_mgf.py  --start_folder " + input_folder  + " --output " + output_folder + " --type omega "
    
    code_exec,flag_onlyMS2 =  run_command( cmd, '  4- Merging with Omega result '  ,log , True )
    
    if  code_exec== 1:
        return ( 0 )


    
    '''
    #old version  supposed to wotk on Pride side . 
    # 4 step
    args= shlex.split( "java -jar  mzparser-testing.jar" + " -i " + input_folder  + " -o " + output_folder  + " -m"  )
    code_exec,flag_onlyMS2 = run_command ( args, '  4- Parsing mgf file by mzparser-1.0.0.jar',  log,  False )
    

    if  code_exec== 1:
        return ( 0 )
    
     
    
    # 5 step 
    cmd = "python create_input_from_mgf.py --start_folder " + output_folder   +" --output " + os.path.join(output_folder,'moff_output')   + " --type mgf "
    code_exec,flag_onlyMS2 = run_command(  cmd, '  5- Join mgf info to moFF result ',log,True )
    
    if flag_onlyMS2 :
        log.critical('   >>  only the MS2 scans have been quantified'  )
        return 1
    if  code_exec== 1:
        return ( 0 )


    
    #6 step

    
    if flag_prod == 1:
        cmd= "java -jar mzparser-1.0.0-merger_internal.jar  -i " + input_folder  + " -o "+ output_folder +"/moff_output"  + " -s"
    else:
        cmd= "java -jar  mzparser-testing.jar  -i " + input_folder  + " -o "+ output_folder +"/moff_output"  + " -s"
    
    code_exec,flag_onlyMS2  = run_command(cmd, '  6- Parsing mzTAB data for ms1_quant output ' , log   , True   )
    if  code_exec== 1:
        return ( 0 )

    #7 step 

    cmd =  "python create_input_from_mgf.py  --start_folder " + os.path.join(output_folder,'moff_output')  + " --output " + os.path.join(output_folder,"moff_output") + " --type mztab "
    
    code_exec,flag_onlyMS2 =  run_command( cmd, '  7- Creating ms1_quant output '  ,log , True )
    if  code_exec== 1:
        return ( 0 )

    #8 step 

    if flag_prod == 1:
        cmd = "java -jar  mzparser-1.0.0-merger_internal.jar  -i " + input_folder  + " -o " +  output_folder +"/moff_output"  + " -z"
    else:
        cmd = "java -jar   mzparser-testing.jar  -i " + input_folder  + " -o " +  output_folder +"/moff_output"  + " -z"

    code_exec,flag_onlyMS2 = run_command(cmd,'  8- Creating mzTAB output', log, True)
    if  code_exec== 1:
        return ( 0 )
        
    # 9 step    
    cmd = "  mv " +   os.path.join(output_folder,'moff_output') +  "/*.mztab "+  result_folder     
    code_exec,flag_onlyMS2 = run_command( cmd,'  9- Move result mzTab file ' ,log , True  )
    if  code_exec== 1:
        return ( 0 )
        

    #10 step     
    cmd= "  mv " +   os.path.join(output_folder,'moff_output') +  "/*.ms1_quant " + result_folder
    code_exec,flag_onlyMS2 = run_command(  cmd, '  10- Move result ms1_quant file', log,  True )
    if  code_exec== 1:
        return ( 0 )

    '''
    return 1

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='moFF-Pride pipeline')

    parser.add_argument('--f', dest='file_prj_id', action='store',help=' file contains a list of valid PXDxxx id', required=False)
    parser.add_argument('--docker_run', dest='docker_run_mode', action='store', type= int , default=0,  help='flag to activate/deactivate docker setting', required=True)
    
    parser.add_argument('--output_location', dest='output_loc', action='store',   help='input folder e.g where all PXDxx folder are located', required=True)
    parser.add_argument('--input_location', dest='input_loc', action='store',   help='output folder e.g where to all the moFF result for each project ', required=True)


    args = parser.parse_args()

    if args.docker_run_mode ==1:
        START_LOC = os.environ.get('START_LOC', '/moFF_pipeline'   )
        moFF_PATH = os.environ.get('moFF_PATH', '/moFF')
    else:
        # change with your apropiate location.
        START_LOC = os.environ.get('START_LOC', '/home/compomics/second_disk/Pride_pipeline_local')
        moFF_PATH = os.environ.get('moFF_PATH', '/home/compomics/moFF_master_pipeline')
        
    DATAINPUT_LOC = os.environ.get('DATAINPUT_LOC', args.input_loc  )
    DATAOUTPUT_LOC = os.environ.get('DATAOUTPUT_LOC', args.output_loc )
    
        
    ch = logging.StreamHandler( sys.stdout ) 
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - moFF-PRIDE pipeline - %(message)s')
    ch.setFormatter( formatter)
    fh = logging.FileHandler('moFF_pride_pipeline.log', mode='w')
    fh.setFormatter( formatter)
    fh.setLevel(logging.INFO)
    log.addHandler(ch)
    log.addHandler(fh)

    log.critical( 'pipeline folder : %s |  moFF path :  %s', START_LOC , moFF_PATH  )

    if args.file_prj_id:
        f = open( args.file_prj_id , "r")
        list_pxdID = f.read().splitlines()
        f.close()
    else:
        ##  option for testing specific spec. PXD id 
        list_pxdID=['PXD000561'] # PXD002796  PXD004612
    for pxd_id in list_pxdID:
        log.critical( ' start processing : %s', pxd_id  )
        status = run_pipeline( pxd_id  ,log, DATAINPUT_LOC,  DATAOUTPUT_LOC, START_LOC , moFF_PATH,args.prod_env ) 
        if status == 1:
            log.critical(' >> ended  correctly  : %s', pxd_id  )
        else: 
            log.critical(' >> error occured in : >>  %s', pxd_id )







