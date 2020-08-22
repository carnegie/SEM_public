# -*- codiNatgas: utf-8 -*-
'''
Simple Energy Model Ver 1.1
  
Purpose
    This model generated results for the following paper:
        Tong, F.; Yuan, M.; Lewis, N.S.; Davis, S.J.; Caldeira, K.* 
            Effects of deep reductions in energy storage costs on highly reliable 
            wind and solar electricity systems. Forthcoming at iScience. 
 
Programming Environment
    Python v3.
    cvxpy, version 0.4.11 -- python library
    Gurubi -- solver

    See additional comments in README.md.
 
Model Version
    Last updated 2018/12
  
'''

from Core_Model import core_model_loop
from Preprocess_Input import preprocess_input
from Postprocess_Results import post_process
from Save_Basic_Results import save_basic_results
from Quick_Look import quick_look

from shutil import copy2
import os
import time
# import pdb

start_time = time.time()

# Input files for different runs/scenarios are defined in the "Input_Data" folder. Each technology scenario has a seperate folder.
case_input_path_filename = './Input_Data/WS_Base/case_input_1yearby36.csv'

# -----------------------------------------------------------------------------
# =============================================================================

print ('Simple_Energy_Model: Pre-processing input')
global_dic,case_dic_list = preprocess_input(case_input_path_filename)

# -----------------------------------------------------------------------------

# copy the input data file to the output folder

output_folder = global_dic['OUTPUT_PATH'] + '/' + global_dic['GLOBAL_NAME']

if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    
copy2(case_input_path_filename, output_folder)

# -----------------------------------------------------------------------------

print ('Simple_Energy_Model: Executing core model loop')
core_model_loop (global_dic, case_dic_list)

print ('Simple_Energy_Model: Saving basic results')
# Note that results for individual cases are output from core_model_loop
scalar_names,scalar_table = save_basic_results(global_dic, case_dic_list)

# -----------------------------------------------------------------------------

# copy the Gurobi log file to the output folder
#   The Verbose field in SOLVE function in CORE_MODEL.PY determined if a gurobi.log is generated.
#   delete the gurobi log to eliminate cumulations from previous runs.

if os.path.exists("./gurobi.log"):    
   copy2("./gurobi.log", output_folder)
   try:
       os.remove("./gurobi.log")
   except:
       print ('gurboi.log not erased')
     
# -----------------------------------------------------------------------------

if global_dic['POSTPROCESS']:
    print ('Simple_Energy_Model: Post-processing results')
    post_process(global_dic) # Lei's old postprocessing

if global_dic['QUICK_LOOK']:
    print ('Simple_Energy_Model: Preparing quick look at results')
    pickle_file_name = './Output_Data/'+global_dic['GLOBAL_NAME']+'/'+global_dic['GLOBAL_NAME']+'.pickle'
    quick_look(global_dic, case_dic_list)  # Fan's new postprocessing

end_time = time.time()
print ('runtime: ', (end_time - start_time), 'seconds')
