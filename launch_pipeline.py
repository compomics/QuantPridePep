import numpy as np
import pandas as pd
import os as os
import sys
import fnmatch
import subprocess
import shlex 
import logging



log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


START_LOC = os.environ.get('START_LOC', '/home/compomics/second_disk/Pride_pipeline_local')
moFF_PATH = os.environ.get('moFF_PATH', '/home/compomics/moFF_multipr_rawfile')



def run_command ( cmd ,  msg_cmd ,  log , flag_shell = False):
    
    p= subprocess.Popen( cmd , stdout=subprocess.PIPE,stderr= subprocess.PIPE, shell = flag_shell )  
    output,err = p.communicate( )
    if p.returncode != 0:
        log.critical(  msg_cmd +' ERROR %s', err  )
        log.critical(' %s', output  )
        exit('--')
    else:
        log.critical( msg_cmd +  ' -->  DONE'  )
        return (output,err)
    

def run_pipeline( prj_loc,log  ):
    
    log.critical( '%s', START_LOC   )
    if not (os.path.isdir(   os.path.join(START_LOC, prj_loc  +'_moFF'  )   )): 
        os.makedirs(os.path.join(START_LOC, prj_loc +'_moFF'  ))
        output_folder = os.path.join(START_LOC, prj_loc    + '_moFF'  )
    else:
        output_folder = os.path.join(START_LOC, prj_loc    + '_moFF'  )
    
    input_folder = os.path.join( START_LOC, prj_loc  )
    
    result_folder = os.path.join(output_folder,  'result'  )
    if not (os.path.isdir(  result_folder   )):
        os.makedirs(result_folder)
    
        
    log.critical( 'Prj %s  -->  setting input folder  %s',  prj_loc, input_folder )
    log.critical( 'Prj %s  --> setting output folder %s',  prj_loc,output_folder )
    
    # 1 step
    args= shlex.split( "java -jar  mzparser-1.0.0.jar" + " -i " + input_folder  + " -o " + output_folder  + " -m"  )
    run_command ( args, 'parsing mgf file by mzparser-1.0.0.jar',  log,  False )
    
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
    
    run_command( cmd, 'creating ms2scan file by ms2extractor', log, True  )



    # 3 step 
    cmd = "python create_input_from_mgf.py --start_folder " + output_folder   +" --output " +  output_folder + " --type mgf "
    run_command(  cmd, 'creating moFF input ',log,True )
    
    #4 step

    if cap_flag ==0: 
        cmd = " ls " + output_folder + "/*.ms2feat_input | parallel --no-notice --joblog "+ os.path.join(output_folder ,"log_moFF")  + " python " +  os.path.join(moFF_PATH ,'moff.py') + " --inputtsv {1}  --inputraw "+ input_folder + "/submitted/{/.}.raw --tol 10 --rt_w 2 --rt_p 1 --output_folder " + os.path.join(output_folder,'moff_output')
    else:
        cmd = " ls " + output_folder + "/*.ms2feat_input | parallel --no-notice --joblog "+ os.path.join(output_folder ,"log_moFF")  + " python " +  os.path.join(moFF_PATH ,'moff.py') + " --inputtsv {1}  --inputraw "+ input_folder + "/submitted/{/.}.RAW --tol 10 --rt_w 2 --rt_p 1 --output_folder " + os.path.join(output_folder,'moff_output')

    run_command( cmd, ' moFF  ' ,log, True  )
 
    #5 step  
    
    cmd= "java -jar  mzparser-1.0.0.jar  -i " + input_folder  + " -o "+ output_folder +"/moff_output"  + " -s"
    
    run_command(cmd, ' Parsing mzTAB data for ms1_quant output ' , log   , True   )

    #6 step 

    cmd =  "python create_input_from_mgf.py  --start_folder " + os.path.join(output_folder,'moff_output')  + " --output " + os.path.join(output_folder,"moff_output") + " --type mztab "
    
    run_command( cmd, 'Creating ms1_quant output '  ,log , True )

    #7 step 
    cmd = "java -jar  mzparser-1.0.0.jar  -i " + input_folder  + " -o " +  output_folder +"/moff_output"  + " -z"

    run_command(cmd,'Creating mzTAB output', log, True)
        
    # 8 step    
    cmd = "  mv " +   os.path.join(output_folder,'moff_output') +  "/*.mztab "+  result_folder     
    run_command( cmd,'Move result mzTab file ' ,log , True  )
        

    #8 step     
    cmd= "  mv " +   os.path.join(output_folder,'moff_output') +  "/*.ms1_quant " + result_folder
    run_command(  cmd, 'Move result ms1_quant file', log,  True )


    return 1

if __name__ == '__main__':
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s  - %(message)s')
    ch.setFormatter( formatter)
    log.addHandler(ch)
    list_pxdID=['PXD004612','PXD004788']
    for pxd_id in list_pxdID:
        run_pipeline( pxd_id  ,log) 









