# -*- codiNatgas: utf-8 -*-
'''
  Top level function for the Simple Energy Model Ver 1.
  
  The main thing a user needs to do to be able to run this code from a download
  from github is to make sure that <case_input_path_filename> points to the 
  appropriate case input file.
  
  The format of this file is documented in the file called <case_input.csv>.
  
  updated by Mengyao for nuclear vs. renewables analysis 10/19/2018
    (a) Core_Model
        (i) Added curtailment calculations for wind, solar, and nuclear
        (ii) Added runtime estimation and display
    (b) Save_Basic Results
        (i) In "save_vector_results_as_csv", switched headers and corresponding results for 
            "solar capacity factor (kW)" and "dispatch solar (kW per unit deployed)"
            so that capacity factors and optimization results are listed separately
        (ii) In "save_basic_results", switched headers and corresopnding results for 
            "capacity factor solar series (kW)" and "capacity factor wind series (kW)"
            to make order of technologies consistent
        (iii) Removed "_" in all headers in output .csv files so text wrapping works better
        (iv) Added curtailment for wind, solar, and nuclear to saved results
    (c) Simple_Energy_Model
        Disabled quick look .pdf outputs
  
'''

from Core_Model import core_model_loop
from Preprocess_Input import preprocess_input
#from Postprocess_Results import post_process
#from Postprocess_Results_kc180214 import postprocess_key_scalar_results,merge_two_dicts
from Save_Basic_Results import save_basic_results
#from Quick_Look import quick_look
import sys

# user-specified input file
if len(sys.argv) == 1:
    case_input_path_filename = './input_ng_flex_nuc.csv'
else:
    case_input_path_filename = sys.argv[1]

# -----------------------------------------------------------------------------
# =============================================================================

print ('Simple_Energy_Model: Pre-processing input')
global_dic,case_dic_list = preprocess_input(case_input_path_filename)

print ('Simple_Energy_Model: Executing core model loop')
core_model_loop (global_dic, case_dic_list)

print ('Simple_Energy_Model: Saving basic results')
# Note that results for individual cases are output from core_model_loop
scalar_names,scalar_table = save_basic_results(global_dic, case_dic_list)

#if global_dic['POSTPROCESS']:
#    print ('Simple_Energy_Model: Post-processing results')
#    post_process(global_dic) # Lei's old postprocessing
#
#if global_dic['QUICK_LOOK']:
#    print ('Simple_Energy_Model: Preparing quick look at results')
#    pickle_file_name = './Output_Data/'+global_dic['GLOBAL_NAME']+'/'+global_dic['GLOBAL_NAME']+'.pickle'
#    quick_look(global_dic, case_dic_list)  # Fan's new postprocessing
    

