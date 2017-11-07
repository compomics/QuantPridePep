import numpy as np
import pandas as pd
import os as os
import sys
import fnmatch
import subprocess
import shlex 
import logging
import argparse



log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)





def run_command ( cmd ,  msg_cmd ,  log , flag_shell = False):
    
    p= subprocess.Popen( cmd , stdout=subprocess.PIPE,stderr= subprocess.PIPE, shell = flag_shell )  
    output,err = p.communicate( )
    if p.returncode != 0:
        log.critical(  msg_cmd +' ERROR %s', err  )
        log.critical(' %s', output  )
        return 1
    else:
        log.critical( msg_cmd +  ' -->  DONE'  )
        return 0
    

def run_pipeline( prj_loc,log, DATAINPUT_LOC,  DATAOUTPUT_LOC, START_LOC , moFF_PATH  ):
    log.critical( '%s', START_LOC   )
    if not (os.path.isdir(   os.path.join( DATAOUTPUT_LOC, prj_loc  +'_moFF'  )   )): 
        os.makedirs(os.path.join(DATAOUTPUT_LOC, prj_loc +'_moFF'  ))
        output_folder = os.path.join(DATAOUTPUT_LOC, prj_loc    + '_moFF'  )
    else:
        output_folder = os.path.join(DATAOUTPUT_LOC, prj_loc    + '_moFF'  )
    
    input_folder = os.path.join( DATAINPUT_LOC, prj_loc  )
    
    result_folder = os.path.join(output_folder,  'result'  )
    if not (os.path.isdir(  result_folder   )):
        os.makedirs(result_folder)
    
        
    log.critical( 'Prj %s  -->  setting input folder  %s',  prj_loc, input_folder )
    log.critical( 'Prj %s  --> setting output folder %s',  prj_loc,output_folder )
    
    # 1 step
    args= shlex.split( "java -jar  mzparser-1.0.0.jar" + " -i " + input_folder  + " -o " + output_folder  + " -m"  )
    code_exec = run_command ( args, 'parsing mgf file by mzparser-1.0.0.jar',  log,  False )
    

    if  code_exec== 1:
        return ( 0 )

    cap_flag= 0
    
    for f in os.listdir( os.path.join(input_folder, "submitted/" )):
        if fnmatch.fnmatch( f, '*.raw') : 
            cap_flag = 0
            break
        if fnmatch.fnmatch( f, '*.RAW') :     
            cap_flag = 1
            break
    
    # 2 step
    if cap_flag ==0: 
        cmd =  " ls " + os.path.join(input_folder, "submitted/") + "*.raw | parallel --no-notice --joblog "+ os.path.join(output_folder ,"log_ms2scan")  + "  \" mono " +  os.path.join(START_LOC, "ms2extract.exe") + " -f {1}  > " + output_folder + "/{/.}.ms2scan \" " 
    else:
        cmd = " ls " + os.path.join(input_folder, "submitted/") + "*.RAW | parallel --no-notice --joblog "+ os.path.join(output_folder ,"log_ms2scan")  + "  \" mono " +  os.path.join(START_LOC, "ms2extract.exe") + " -f {1}  > " + output_folder + "/{/.}.ms2scan \" " 
    
    code_exec =  run_command( cmd, 'creating ms2scan file by ms2extractor', log, True  )

    if  code_exec== 1:
        return ( 0 )

    # 3 step 
    cmd = "python create_input_from_mgf.py --start_folder " + output_folder   +" --output " +  output_folder + " --type mgf "
    code_exec = run_command(  cmd, 'creating moFF input ',log,True )

    if  code_exec== 1:
        return ( 0 )

    
    #4 step

    if cap_flag ==0: 
        cmd = " ls " + output_folder + "/*.ms2feat_input | parallel --no-notice --joblog "+ os.path.join(output_folder ,"log_moFF")  + " python " +  os.path.join(moFF_PATH ,'moff.py') + " --inputtsv {1}  --inputraw "+ input_folder + "/submitted/{/.}.raw --tol 10 --rt_w 2 --rt_p 1 --output_folder " + os.path.join(output_folder,'moff_output')
    else:
        cmd = " ls " + output_folder + "/*.ms2feat_input | parallel --no-notice --joblog "+ os.path.join(output_folder ,"log_moFF")  + " python " +  os.path.join(moFF_PATH ,'moff.py') + " --inputtsv {1}  --inputraw "+ input_folder + "/submitted/{/.}.RAW --tol 10 --rt_w 2 --rt_p 1 --output_folder " + os.path.join(output_folder,'moff_output')

    code_exec =run_command( cmd, ' moFF  ' ,log, True  )

    if  code_exec== 1:
        return ( 0 )
 
    #5 step  
    
    cmd= "java -jar  mzparser-1.0.0.jar  -i " + input_folder  + " -o "+ output_folder +"/moff_output"  + " -s"
    
    code_exec = run_command(cmd, ' Parsing mzTAB data for ms1_quant output ' , log   , True   )
    if  code_exec== 1:
        return ( 0 )

    #6 step 

    cmd =  "python create_input_from_mgf.py  --start_folder " + os.path.join(output_folder,'moff_output')  + " --output " + os.path.join(output_folder,"moff_output") + " --type mztab "
    
    code_exec =  run_command( cmd, 'Creating ms1_quant output '  ,log , True )
    if  code_exec== 1:
        return ( 0 )

    #7 step 
    cmd = "java -jar  mzparser-1.0.0.jar  -i " + input_folder  + " -o " +  output_folder +"/moff_output"  + " -z"

    code_exec = run_command(cmd,'Creating mzTAB output', log, True)
    if  code_exec== 1:
        return ( 0 )
        
    # 8 step    
    cmd = "  mv " +   os.path.join(output_folder,'moff_output') +  "/*.mztab "+  result_folder     
    code_exec = run_command( cmd,'Move result mzTab file ' ,log , True  )
    if  code_exec== 1:
        return ( 0 )
        

    #8 step     
    cmd= "  mv " +   os.path.join(output_folder,'moff_output') +  "/*.ms1_quant " + result_folder
    code_exec = run_command(  cmd, 'Move result ms1_quant file', log,  True )
    if  code_exec== 1:
        return ( 0 )


    return 1

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='moFF-Pride pipeline')

    parser.add_argument('--f', dest='file_prj_id', action='store',help=' file contains a list of valid PXDxxx id', required=False)
    parser.add_argument('--docker_run', dest='docker_run_mode', action='store', default=0,  help='flag to activate/deactivate docker setting', required=True)
    
    parser.add_argument('--output_location', dest='output_loc', action='store',   help='input folder e.g where all PXDxx folder are located', required=True)
    parser.add_argument('--input_location', dest='input_loc', action='store',   help='output folder e.g where to all the moFF result for each project ', required=True)

    args = parser.parse_args()

    if args.docker_run_mode ==1:
        START_LOC = os.environ.get('START_LOC', '/moFF_pipeline'   )
        moFF_PATH = os.environ.get('moFF_PATH', '/moFF')
    else:
        # change with your apropiate location.
        START_LOC = os.environ.get('START_LOC', '/home/compomics/second_disk/Pride_pipeline_local')
        moFF_PATH = os.environ.get('moFF_PATH', '/home/compomics/moFF_multipr_rawfile')
        
    DATAINPUT_LOC = os.environ.get('DATAINPUT_LOC', args.input_loc  )
    DATAOUTPUT_LOC = os.environ.get('DATAOUTPUT_LOC', args.output_loc )
    
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s  - %(message)s')
    ch.setFormatter( formatter)
    log.addHandler(ch)
    

    list_pxdID=['PXD004612']
    for pxd_id in list_pxdID:
        run_pipeline( pxd_id  ,log, DATAINPUT_LOC,  DATAOUTPUT_LOC, START_LOC , moFF_PATH) 









