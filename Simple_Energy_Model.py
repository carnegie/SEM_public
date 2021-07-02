# -*- codiNatgas: utf-8 -*-
'''
  Top level function for the Simple Energy Model Ver 1.
  
  The main thing a user needs to do to be able to run this code from a download
  from github is to make sure that <case_input_path_filename> points to the 
  appropriate case input file.
  
  The format of this file is documented in the file called <case_input.csv>.
  
  If you are in Spyder, under the Run menu you can select 'configuration per File' Fn+Ctrl+F6
  and enter the file name of your input .csv file, e.g., Check 'command line options'
  and enter ./case_input_base_190716.csv
  
'''

from Core_Model import core_model_loop
from Preprocess_Input import preprocess_input
from Postprocess_Results import post_process
#from Postprocess_Results_kc180214 import postprocess_key_scalar_results,merge_two_dicts
from Save_Basic_Results import save_basic_results
from Quick_Look import quick_look

from shutil import copy2
import os
import sys
 
# directory = 'D:/M/WORK/'
#root_directory = '/Users/kcaldeira/Google Drive/simple energy system model/Kens version/'
#whoami = subprocess.check_output('whoami')
#if whoami == 'kcaldeira-carbo\\kcaldeira\r\n':
#    case_input_path_filename = '/Users/kcaldeira/Google Drive/git/SEM-1/case_input.csv'
if len(sys.argv) == 1:
    #case_input_path_filename = './case_input.csv'
    case_input_path_filename = './case_input_test_190726.csv'
else:
    case_input_path_filename = sys.argv[1]

# -----------------------------------------------------------------------------
# =============================================================================

print ('Simple_Energy_Model: Pre-processing input')
global_dic,case_dic_list = preprocess_input(case_input_path_filename)

# -----------------------------------------------------------------------------

# copy the input data file to the output folder

output_folder = global_dic['OUTPUT_PATH'] + '/' + global_dic['GLOBAL_NAME']

if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    
try:
    copy2(case_input_path_filename, output_folder)
except:
    print ('case input file '+case_input_path_filename+' not copied. Perhaps it does not exist. Perhaps it is open and cannot be overwritten.')

# -----------------------------------------------------------------------------

print ('Simple_Energy_Model: Executing core model loop')
core_model_loop (global_dic, case_dic_list)

print ('Simple_Energy_Model: Saving basic results')
# Note that results for individual cases are output from core_model_loop
save_basic_results(global_dic, case_dic_list)

# -----------------------------------------------------------------------------

# copy the Gurobi log file to the output folder
#   The Verbose field in SOLVE function in CORE_MODEL.PY determined if a gurobi.log is generated.
#   delete the gurobi log to eliminate cumulations from previous runs.

#if os.path.exists("./gurobi.log"):    
#   copy2("./gurobi.log", output_folder)
#   try:
#       os.remove("./gurobi.log")
#   except:
#       print ('gurboi.log not erased')
     

# -----------------------------------------------------------------------------


if global_dic['POSTPROCESS']:
    print ('Simple_Energy_Model: Post-processing results')
    post_process(global_dic) # Lei's old postprocessing

if global_dic['QUICK_LOOK']:
    print ('Simple_Energy_Model: Preparing quick look at results')
    pickle_file_name = './Output_Data/'+global_dic['GLOBAL_NAME']+'/'+global_dic['GLOBAL_NAME']+'.pickle'
    #quick_look(global_dic, case_dic_list)  # Fan's new postprocessing
