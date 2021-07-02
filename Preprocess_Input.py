# -*- codiNatgas: utf-8 -*-
'''
This code reads a file called 'case_input.csv' which is assumed to exist in the directory in which the code is running.

It generates a result containing <global_dic> and <case_dic_list>

<global_dic> is a dictionary of values applied to all cases
    
<global_dic> contains:
    
    
<case_dic_list> is a list of dictionaries. Each element in that list corresponds to a different case to be run.

    'ROOT_PATH' -- PATH TO DATA FILES
    'OUTPUT_DIRECTORY' -- STRING CONTAINING NAME OF OUTPUT DIRECTORY

Each dictionary in <case_dic_list> ALWAYS contains:
    
    'SYSTEM_COMPONENTS' -- LIST OF COMPONENTS, CHOICES ARE: 'WIND','SOLAR', 
                 'NATGAS','NATGAS_CCS','NUCLEAR','STORAGE', 'PGP_STORAGE', 'CSP', 'UNMET'
    'DEMAND_SERIES' -- TIME SERIES OF DEMAND DATA
    
Each dictionary in <case_dic_list> OPTIONALLY contains keywords listed in the text below

'''

import csv
import numpy as np
from utilities import dict_of_lists_to_list_of_dicts



#%%
def import_case_input(case_input_path_filename):
    # Import case_input.csv file from local directory.
    # return 2 objects: param_list, and case_list
    # <param_list> contains information that is true for all cases in the set of runs
    # <case_list> contains information that is true for a particular case
    
    # first open the file and define the reader
    f = open(case_input_path_filename)
    rdr = csv.reader(f)
    
    #Throw away all lines up to and include the line that has 'BEGIN_GLOBAL_DATA' in the first cell of the line
    while True:
        line = next(rdr)
        if line[0] == 'BEGIN_GLOBAL_DATA':
            break
    
    # Now take all non-blank lines until 'BEGIN_ALL_CASES_DATA' or 'BEGIN_CASE_DATA'
    global_data = []
    while True:
        line = next(rdr)
        if line[0] == 'BEGIN_ALL_CASES_DATA' or line[0] == 'BEGIN_CASE_DATA':
            break
        if line[0] != '':
            global_data.append(line[0:2])
            
    # Now take all non-blank lines until 'BEGIN_CASE_DATA'
    all_cases_data = []
    if line[0] == 'BEGIN_ALL_CASES_DATA':
        while True:
            line = next(rdr)
            if line[0] == 'BEGIN_CASE_DATA':
                break
            if line[0] != '':
                all_cases_data.append(line[0:2])
            
    # Now take all non-blank lines until 'END_DATA'
    case_data = []
    while True:
        line = next(rdr)
        if line[0] == 'END_DATA':
            break
        if line[0] != '':
            case_data.append(line)
            
    return global_data,all_cases_data,case_data

def read_csv_dated_data_file(start_year,start_month,start_day,start_hour,
                             end_year,end_month,end_day,end_hour,
                             data_path, data_filename):
    
    # turn dates into yyyymmddhh format for comparison.
    # Assumes all datasets are on the same time step and are not missing any data.
    start_hour = start_hour + 100 * (start_day + 100 * (start_month + 100* start_year)) 
    end_hour = end_hour + 100 * (end_day + 100 * (end_month + 100* end_year)) 
      
    path_filename = data_path + '/' + data_filename
    
    data = []
    with open(path_filename) as fin:
        # read to keyword 'BEGIN_DATA' and then one more line (header line)
        data_reader = csv.reader(fin)
        
        #Throw away all lines up to and include the line that has 'BEGIN_GLOBAL_DATA' in the first cell of the line
        while True:
            line = next(data_reader)
            if line[0] == 'BEGIN_DATA':
                break
        # Now take the header row
        line = next(data_reader)
        
        # Now take all non-blank lines
        data = []
        while True:
            try:
                line = next(data_reader)
                if any(field.strip() for field in line):
                    data.append([int(line[0]),int(line[1]),int(line[2]),int(line[3]),float(line[4])])
                    # the above if clause was from: https://stackoverflow.com/questions/4521426/delete-blank-rows-from-csv
            except:
                break
            
    data_array = np.array(data) # make into a numpy object
    
    hour_num = data_array[:,3] + 100 * (data_array[:,2] + 100 * (data_array[:,1] + 100* data_array[:,0]))   
    

    series = [item[1] for item in zip(hour_num,data_array[:,4]) if item[0]>= start_hour and item[0] <= end_hour]
    
    return np.array(series).flatten() # return flatten series

def literal_to_boolean(text):
    if (text.strip())[0]=='T' or (text.strip())[0]=='t':  # if first non-space character is T or t, then True, else False
        answer = True
    else:
        answer = False
    return answer

def preprocess_input(case_input_path_filename):
    # This is the highest level function that reads in the case input file
    # and generated <case_dic_list> from this input.
        
    # -----------------------------------------------------------------------------
    # Recognized keywords in case_input.csv file
    
    keywords_logical = list(map(str.upper,
            ['VERBOSE','POSTPROCESS','QUICK_LOOK','NORMALIZE_DEMAND_TO_ONE']
            ))

    keywords_str = list(map(str.upper,
            ['DATA_PATH','DEMAND_FILE',
             'SOLAR2_CAPACITY_FILE','WIND2_CAPACITY_FILE',
             'SOLAR_CAPACITY_FILE','WIND_CAPACITY_FILE','CSP_CAPACITY_FILE','OUTPUT_PATH',
             'CASE_NAME','GLOBAL_NAME']
            ))
    
    keywords_real_scaled = list(map(str.upper,
            [             
            'CO2_PRICE',
            
            'FIXED_COST_NATGAS','VAR_COST_NATGAS',
            'FIXED_CO2_NATGAS','VAR_CO2_NATGAS',
            
            'FIXED_COST_NATGAS_CCS','VAR_COST_NATGAS_CCS',
            'FIXED_CO2_NATGAS_CCS','VAR_CO2_NATGAS_CCS',
            
            'FIXED_COST_SOLAR','VAR_COST_SOLAR',
            'FIXED_CO2_SOLAR','VAR_CO2_SOLAR',
            
            'FIXED_COST_SOLAR2','VAR_COST_SOLAR2',
            'FIXED_CO2_SOLAR2','VAR_CO2_SOLAR2', 
            
            'FIXED_COST_WIND','VAR_COST_WIND',
            'FIXED_CO2_WIND', 'VAR_CO2_WIND',
            
            'FIXED_COST_WIND2','VAR_COST_WIND2',
            'FIXED_CO2_WIND2','VAR_CO2_WIND2',
                        
            'FIXED_COST_NUCLEAR','VAR_COST_NUCLEAR',
            'FIXED_CO2_NUCLEAR','VAR_CO2_NUCLEAR',
            
            'FIXED_COST_STORAGE','VAR_COST_STORAGE',
            'VAR_COST_TO_STORAGE','VAR_COST_FROM_STORAGE',
           
            'FIXED_COST_STORAGE2','VAR_COST_STORAGE2',
            'VAR_COST_TO_STORAGE2','VAR_COST_FROM_STORAGE2',
            
            'FIXED_COST_PGP_STORAGE','FIXED_COST_TO_PGP_STORAGE','FIXED_COST_FROM_PGP_STORAGE',
            'VAR_COST_TO_PGP_STORAGE','VAR_COST_FROM_PGP_STORAGE',

            'FIXED_COST_CSP','VAR_COST_CSP',
            'FIXED_COST_CSP_STORAGE','VAR_COST_CSP_STORAGE',

            'FIXED_COST_FUEL_ELECTROLYZER', 'FIXED_COST_FUEL_CHEM_PLANT', 'FIXED_COST_FUEL_POWER',
            'FIXED_COST_FUEL_H2_STORAGE',
            'VAR_COST_FUEL_ELECTROLYZER', 'VAR_COST_FUEL_CHEM_PLANT', 'VAR_COST_FUEL_CO2',
            'EFFICIENCY_FUEL_ELECTROLYZER', 'EFFICIENCY_FUEL_CHEM_CONVERSION', 'EFFICIENCY_FUEL_POWER_CONVERSION',
            'FUEL_VALUE', 'FUEL_DEMAND',
            
            'VAR_COST_UNMET_DEMAND'

            ]
            ))
    
    keywords_real_notscaled = list(map(str.upper,
            [
            'NUMERICS_COST_SCALING','NUMERICS_DEMAND_SCALING',
            'END_DAY','END_HOUR','END_MONTH','END_YEAR',
            'START_DAY','START_HOUR','START_MONTH','START_YEAR',

            'CAPACITY_NATGAS',
            
            'CAPACITY_NATGAS_CCS',
            
            'CAPACITY_SOLAR',

            'CAPACITY_SOLAR2',

            'CAPACITY_WIND',

            'CAPACITY_WIND2',
            
            'CAPACITY_NUCLEAR',
            
            'CAPACITY_STORAGE','CHARGING_TIME_STORAGE',
            'CHARGING_EFFICIENCY_STORAGE','DECAY_RATE_STORAGE',
            
            'CAPACITY_STORAGE2','CHARGING_TIME_STORAGE2',
            'CHARGING_EFFICIENCY_STORAGE2','DECAY_RATE_STORAGE2',
            
            'CAPACITY_PGP_STORAGE','CAPACITY_TO_PGP_STORAGE','CAPACITY_FROM_PGP_STORAGE',
            'CHARGING_EFFICIENCY_PGP_STORAGE','DECAY_RATE_PGP_STORAGE',

            'CAPACITY_CSP','CAPACITY_CSP_STORAGE',
            'DECAY_RATE_CSP_STORAGE','CHARGING_EFFICIENCY_CSP_STORAGE',

            'CAPACITY_FUEL_ELECTROLYZER',
            'CAPACITY_FUEL_H2_STORAGE',
            'CAPACITY_FUEL_CHEM_PLANT',
            'CAPACITY_FUEL_POWER',
            'DECAY_RATE_FUEL_H2_STORAGE',
            
            'SYSTEM_RELIABILITY'
            ]
            ))
    
    #Capacity cost -- Cost per hour of capacity that must be incurred whether or 
    #  not a facility is actually generating electricity. 
    #  For generation technologies, units are $/h per kW capacity
    
    #Dispatch cost -- Incremental cost per kWh of electricity generation from 
    #  a technology that represents the difference in cost between dispatching 
    #  and curtailing generation. For generation, units are in $ per kWh
    
    # -----------------------------------------------------------------------------
    # Read in case data file
    
    # <import_case_input> reads in the file from the csv file, but does not parse
    # this data.
    global_data, all_cases_data, case_data = import_case_input(case_input_path_filename)

    # -----------------------------------------------------------------------------
    # the basic logic here is that if a keyword appears in the 'global'
    # section, then it is used for all cases if it is used in the 'case' section
    # then it applies to that particular case.
        
    # Parse global data
    global_dic = {}
    
    # Number of cases to run is number of rows in case input file.
    # Num cases and verbose are the only non-case specific inputs in case_list_dic.
    num_cases = len(case_data) - 1 # the 1 is for the keyword row
    global_dic['NUM_CASES'] = num_cases

    #------ DEFAULT VALUES FOR global_dic ---------
    # For now, default for quicklook output is True
    global_dic['QUICK_LOOK'] = True
    # default global values to help with numerical issues
    #------convert file input to dictionary of global data ---------
    for list_item in global_data:
        input_key = str.upper(list_item[0])
        input_value = list_item[1]
        if input_key in keywords_str:
            global_dic[input_key] = input_value
        elif input_key in keywords_real_scaled + keywords_real_notscaled:
            global_dic[input_key] = float(input_value)
        elif input_key in keywords_logical:
            global_dic[input_key] = literal_to_boolean(input_value)
    
    verbose = global_dic['VERBOSE']
#    print ( global_dic
    if verbose:
        print ( 'Preprocess_Input.py: Preparing case input for ',global_dic['GLOBAL_NAME'])
        
    # Parse all_cases_dic data
    all_cases_dic = {}
    
    # prevent missing values for keys, all will be -1 if not used.
    for key in keywords_real_scaled + keywords_real_notscaled:
        all_cases_dic[key] = -1.
    for key in keywords_str:
        all_cases_dic[key] = ''
    
    #------ DEFAULT VALUES FOR global_dic ---------
    # For now, default for quicklook output is True
    all_cases_dic['NORMALIZE_DEMAND_TO_ONE'] = False # If True, normalize mean demand to 1.0
    all_cases_dic['CO2_PRICE'] = 0.0 # If True, normalize mean demand to 1.0
    # default global values to help with numerical issues
    all_cases_dic['NUMERICS_COST_SCALING'] = 1e+12 # multiplies all costs by a factor and then divides at end
    all_cases_dic['NUMERICS_DEMAND_SCALING'] = 1e+12 # multiplies demand by a factor and then divides all costs and capacities at end
    


    for list_item in all_cases_data:
        input_key = str.upper(list_item[0])
        input_value = list_item[1]
        if input_key in keywords_str:
            all_cases_dic[input_key] = input_value
        elif input_key in keywords_real_scaled + keywords_real_notscaled:
            all_cases_dic[input_key] = float(input_value)
        elif input_key in keywords_logical:
            all_cases_dic[input_key] = literal_to_boolean(input_value)
    
#    print ( all_cases_data
#    print ( all_cases_dic        
    case_transpose = list(map(list,zip(*case_data))) # transpose list of lists.
    # Note that the above line could cause problems if not all numbers are
    # entered uniformly in the case input file.
        
    # Now each element of case_transpose is the potential keyword followed by data
    case_list_dic = {}
            
    # now add global variables to case_list_dic
    for keyword in all_cases_dic.keys():
        case_list_dic[keyword] = [all_cases_dic[keyword] for i in range(num_cases)] # replicate values
            
    for list_item in case_transpose:
        input_key = str.upper(list_item[0])
        input_values = list_item[1:]
        if input_key in keywords_str:
            case_list_dic[input_key] = input_values
        elif input_key in keywords_real_scaled:
            setNegToM1 = case_list_dic[input_key] * np.array(list(map(float,input_values)))
            setNegToM1[setNegToM1 < 0] = -1
            case_list_dic[input_key] = setNegToM1
        elif input_key in keywords_real_notscaled:
            setNegToM1 = np.array(list(map(float,input_values)))
            setNegToM1[setNegToM1 < 0] = -1
            case_list_dic[input_key] = setNegToM1
        elif input_key in keywords_logical:
            case_list_dic[input_key] = list(map(bool,input_values))

    # define all keywords in dictionary, but set to -1 if not present    
    dummy = [-1 for i in range(num_cases)]
    for keyword in list(set(keywords_real_scaled + keywords_real_notscaled).difference(case_list_dic.keys())):
        case_list_dic[keyword] = dummy

                                                
#%% 

    # ok, now we have everything from the case_input file in case_list_dic.
    # Let's add the other things we need. First, we will see what system components
    # are used in each case.
    
    # for wind, solar, and demand, we also need to get the relevant demand files
    
    have_keys = case_list_dic.keys()

    # Now develop list of component lists
    # If any of the cost variables for a technology is negative, that technology is assumed 
    # not to be in the mix.
    
    list_of_component_lists = []
    for case_index in range(num_cases):
        #if verbose:
        #    print ( 'Preprocess_Input.py:Components for ',case_list_dic['CASE_NAME'][case_index])
        component_list = []
        if 'FIXED_COST_NUCLEAR' in have_keys:
            if case_list_dic['FIXED_COST_NUCLEAR'][case_index] >= 0 and case_list_dic['VAR_COST_NUCLEAR'][case_index] >= 0 :
                component_list.append('NUCLEAR')
                                                
        if 'FIXED_COST_NATGAS' in have_keys:
            if case_list_dic['FIXED_COST_NATGAS'][case_index] >= 0 and case_list_dic['VAR_COST_NATGAS'][case_index] >= 0 :
                component_list.append('NATGAS')
                                                
        if 'FIXED_COST_NATGAS_CCS' in have_keys:
            if case_list_dic['FIXED_COST_NATGAS_CCS'][case_index] >= 0 and case_list_dic['VAR_COST_NATGAS_CCS'][case_index] >= 0 :
                component_list.append('NATGAS_CCS')
                                                
        if 'FIXED_COST_WIND' in have_keys:
            if case_list_dic['FIXED_COST_WIND'][case_index] >= 0 and case_list_dic['VAR_COST_WIND'][case_index] >= 0 :
                component_list.append('WIND')
                                                
        if 'FIXED_COST_SOLAR' in have_keys:
            if case_list_dic['FIXED_COST_SOLAR'][case_index] >= 0 and case_list_dic['VAR_COST_SOLAR'][case_index] >= 0 :
                component_list.append('SOLAR')
                                                
        if 'FIXED_COST_WIND2' in have_keys:
            if case_list_dic['FIXED_COST_WIND2'][case_index] >= 0 and case_list_dic['VAR_COST_WIND2'][case_index] >= 0 :
                component_list.append('WIND2')
                                                
        if 'FIXED_COST_SOLAR2' in have_keys:
            if case_list_dic['FIXED_COST_SOLAR2'][case_index] >= 0 and case_list_dic['VAR_COST_SOLAR2'][case_index] >= 0 :
                component_list.append('SOLAR2')
                                                
        if 'FIXED_COST_STORAGE' in have_keys:
            if (case_list_dic['FIXED_COST_STORAGE'][case_index] >= 0 and case_list_dic['VAR_COST_TO_STORAGE'][case_index] >= 0  and 
            case_list_dic['VAR_COST_FROM_STORAGE'][case_index] >= 0 and case_list_dic['CHARGING_EFFICIENCY_STORAGE'][case_index] >= 0 and
            case_list_dic['DECAY_RATE_STORAGE'][case_index] >= 0 and case_list_dic['CHARGING_TIME_STORAGE'][case_index] >= 0) :
                component_list.append('STORAGE')
                                                
        if 'FIXED_COST_STORAGE2' in have_keys:
            if (case_list_dic['FIXED_COST_STORAGE2'][case_index] >= 0 and case_list_dic['VAR_COST_TO_STORAGE2'][case_index] >= 0  and 
            case_list_dic['VAR_COST_FROM_STORAGE2'][case_index] >= 0 and case_list_dic['CHARGING_EFFICIENCY_STORAGE2'][case_index] >= 0 and
            case_list_dic['DECAY_RATE_STORAGE2'][case_index] >= 0 and case_list_dic['CHARGING_TIME_STORAGE2'][case_index] >= 0) :
                component_list.append('STORAGE2')
                
        if 'FIXED_COST_PGP_STORAGE' in have_keys:
            if (case_list_dic['FIXED_COST_PGP_STORAGE'][case_index] >= 0 and 
                case_list_dic['FIXED_COST_TO_PGP_STORAGE'][case_index] >= 0 and case_list_dic['VAR_COST_TO_PGP_STORAGE'][case_index] >= 0 and 
                case_list_dic['FIXED_COST_FROM_PGP_STORAGE'][case_index] >= 0 and case_list_dic['VAR_COST_FROM_PGP_STORAGE'][case_index] >= 0 and 
                case_list_dic['DECAY_RATE_PGP_STORAGE'][case_index] >= 0 and case_list_dic['CHARGING_EFFICIENCY_PGP_STORAGE'][case_index] >= 0) :
                component_list.append('PGP_STORAGE')
                
        if 'FIXED_COST_CSP' in have_keys:
            if (case_list_dic['FIXED_COST_CSP'][case_index] >= 0 and case_list_dic['VAR_COST_CSP'][case_index] >= 0 and 
                case_list_dic['FIXED_COST_CSP_STORAGE'][case_index] >= 0 and case_list_dic['VAR_COST_CSP_STORAGE'][case_index] >= 0 and 
                case_list_dic['DECAY_RATE_CSP_STORAGE'][case_index] >= 0 and case_list_dic['CHARGING_EFFICIENCY_CSP_STORAGE'][case_index] >= 0):
                component_list.append('CSP')
                
        if 'FIXED_COST_FUEL_ELECTROLYZER' in have_keys:
            if case_list_dic['FIXED_COST_FUEL_ELECTROLYZER'][case_index] >= 0 and case_list_dic['VAR_COST_FUEL_ELECTROLYZER'][case_index] >= 0 :
                component_list.append('FUEL')
                
        if 'VAR_COST_UNMET_DEMAND' in have_keys:
            if case_list_dic['VAR_COST_UNMET_DEMAND'][case_index] >= 0:
                component_list.append('UNMET_DEMAND')
                
        if 'SYSTEM_RELIABILITY' in have_keys:
            if case_list_dic['SYSTEM_RELIABILITY'][case_index] >= 0:
                if not 'UNMET_DEMAND' in component_list:  # If system reliability is specified make sure unmet demand is a possibility
                                                          # and set cost to zero if not otherwise set.
                    component_list.append('UNMET_DEMAND')
                    case_list_dic['VAR_COST_UNMET_DEMAND'][case_index] = 0
                                
        print("Included components:")
        print(component_list)
        list_of_component_lists.append(component_list)
    case_list_dic['SYSTEM_COMPONENTS'] = list_of_component_lists

#%%    
    solar_series_list = []
    wind_series_list = []
    solar2_series_list = []
    wind2_series_list = []
    demand_series_list = []
    csp_series_list = []

    for case_index in range(num_cases):
        if verbose:
            print ( 'Preprocess_Input.py: time series for ',case_list_dic['CASE_NAME'][case_index])
                
        # first read in demand series (which must exist)
        demand_series_list_item = read_csv_dated_data_file(
                    case_list_dic['START_YEAR'][case_index],
                    case_list_dic['START_MONTH'][case_index],
                    case_list_dic['START_DAY'][case_index],
                    case_list_dic['START_HOUR'][case_index],
                    case_list_dic['END_YEAR'][case_index],
                    case_list_dic['END_MONTH'][case_index],
                    case_list_dic['END_DAY'][case_index],
                    case_list_dic['END_HOUR'][case_index],
                    global_dic['DATA_PATH'],
                    case_list_dic['DEMAND_FILE'][case_index]
                    )
        if case_list_dic['NORMALIZE_DEMAND_TO_ONE'][case_index]:
            demand_series_list_item = demand_series_list_item / np.average(demand_series_list_item)
        demand_series_list.append(demand_series_list_item)
        
        # check on each technology one by one

        if 'FIXED_COST_SOLAR' in have_keys:
            if case_list_dic['FIXED_COST_SOLAR'][case_index] >= 0:
                solar_series_list.append(
                        read_csv_dated_data_file(
                                case_list_dic['START_YEAR'][case_index],
                                case_list_dic['START_MONTH'][case_index],
                                case_list_dic['START_DAY'][case_index],
                                case_list_dic['START_HOUR'][case_index],
                                case_list_dic['END_YEAR'][case_index],
                                case_list_dic['END_MONTH'][case_index],
                                case_list_dic['END_DAY'][case_index],
                                case_list_dic['END_HOUR'][case_index],
                                global_dic['DATA_PATH'],
                                case_list_dic['SOLAR_CAPACITY_FILE'][case_index]
                                )
                        )
            else:
                solar_series_list.append([])
        else:
            solar_series_list.append([])
                        
        if 'FIXED_COST_WIND' in have_keys:
            if case_list_dic['FIXED_COST_WIND'][case_index] >= 0:
                wind_series_list.append(
                        read_csv_dated_data_file(
                                case_list_dic['START_YEAR'][case_index],
                                case_list_dic['START_MONTH'][case_index],
                                case_list_dic['START_DAY'][case_index],
                                case_list_dic['START_HOUR'][case_index],
                                case_list_dic['END_YEAR'][case_index],
                                case_list_dic['END_MONTH'][case_index],
                                case_list_dic['END_DAY'][case_index],
                                case_list_dic['END_HOUR'][case_index],
                                global_dic['DATA_PATH'],
                                case_list_dic['WIND_CAPACITY_FILE'][case_index]
                                )
                        )
            else:
                wind_series_list.append([])
        else:
            wind_series_list.append([])

        if 'FIXED_COST_SOLAR2' in have_keys:
            if case_list_dic['FIXED_COST_SOLAR2'][case_index] >= 0:
                solar2_series_list.append(
                        read_csv_dated_data_file(
                                case_list_dic['START_YEAR'][case_index],
                                case_list_dic['START_MONTH'][case_index],
                                case_list_dic['START_DAY'][case_index],
                                case_list_dic['START_HOUR'][case_index],
                                case_list_dic['END_YEAR'][case_index],
                                case_list_dic['END_MONTH'][case_index],
                                case_list_dic['END_DAY'][case_index],
                                case_list_dic['END_HOUR'][case_index],
                                global_dic['DATA_PATH'],
                                case_list_dic['SOLAR2_CAPACITY_FILE'][case_index]
                                )
                        )
            else:
                solar2_series_list.append([])
        else:
            solar2_series_list.append([])
                        
        if 'FIXED_COST_WIND2' in have_keys:
            if case_list_dic['FIXED_COST_WIND2'][case_index] >= 0:
                wind2_series_list.append(
                        read_csv_dated_data_file(
                                case_list_dic['START_YEAR'][case_index],
                                case_list_dic['START_MONTH'][case_index],
                                case_list_dic['START_DAY'][case_index],
                                case_list_dic['START_HOUR'][case_index],
                                case_list_dic['END_YEAR'][case_index],
                                case_list_dic['END_MONTH'][case_index],
                                case_list_dic['END_DAY'][case_index],
                                case_list_dic['END_HOUR'][case_index],
                                global_dic['DATA_PATH'],
                                case_list_dic['WIND2_CAPACITY_FILE'][case_index]
                                )
                        )
            else:
                wind2_series_list.append([])
        else:
            wind2_series_list.append([])
                        
        if 'FIXED_COST_CSP' in have_keys:
            if case_list_dic['FIXED_COST_CSP'][case_index] >= 0:
                csp_series_list.append(
                        read_csv_dated_data_file(
                                case_list_dic['START_YEAR'][case_index],
                                case_list_dic['START_MONTH'][case_index],
                                case_list_dic['START_DAY'][case_index],
                                case_list_dic['START_HOUR'][case_index],
                                case_list_dic['END_YEAR'][case_index],
                                case_list_dic['END_MONTH'][case_index],
                                case_list_dic['END_DAY'][case_index],
                                case_list_dic['END_HOUR'][case_index],
                                global_dic['DATA_PATH'],
                                case_list_dic['CSP_CAPACITY_FILE'][case_index]
                                )
                        )
            else:
                csp_series_list.append([])
        else:
            csp_series_list.append([])
    
    case_list_dic['DEMAND_SERIES'] = demand_series_list
    case_list_dic['WIND_SERIES'] = wind_series_list
    case_list_dic['SOLAR_SERIES'] = solar_series_list
    case_list_dic['WIND2_SERIES'] = wind2_series_list
    case_list_dic['SOLAR2_SERIES'] = solar2_series_list
    case_list_dic['CSP_SERIES'] = csp_series_list
    
#%%
# update fixed and variable costs to reflect carbon prices
    for case_index in range(num_cases):
        if case_list_dic['CO2_PRICE'][case_index] > 0.0:  #  Note, negative CO2_PRICE is not allowed. Indicates no CO2 price.
            
            system_components = case_list_dic['SYSTEM_COMPONENTS'][case_index]
            
            if 'NUCLEAR' in system_components:
                case_list_dic['FIXED_COST_NUCLEAR'][case_index] = (case_list_dic['FIXED_COST_NUCLEAR'][case_index] 
                        + case_list_dic['CO2_PRICE'][case_index]*case_list_dic['FIXED_CO2_NUCLEAR'][case_index])
                case_list_dic['VAR_COST_NUCLEAR'][case_index] = (case_list_dic['VAR_COST_NUCLEAR'][case_index] 
                        + case_list_dic['CO2_PRICE'][case_index]*case_list_dic['VAR_CO2_NUCLEAR'][case_index])
                                                    
            if 'NATGAS' in system_components:
                case_list_dic['FIXED_COST_NATGAS'][case_index] = (case_list_dic['FIXED_COST_NATGAS'][case_index] 
                        + case_list_dic['CO2_PRICE'][case_index]*case_list_dic['FIXED_CO2_NATGAS'][case_index])
                case_list_dic['VAR_COST_NATGAS'][case_index] = (case_list_dic['VAR_COST_NATGAS'][case_index] 
                        + case_list_dic['CO2_PRICE'][case_index]*case_list_dic['VAR_CO2_NATGAS'][case_index])
                                                    
            if 'NATGAS_CCS' in system_components:
                case_list_dic['FIXED_COST_NATGAS_CCS'][case_index] = (case_list_dic['FIXED_COST_NATGAS_CCS'][case_index] 
                        + case_list_dic['CO2_PRICE'][case_index]*case_list_dic['FIXED_CO2_NATGAS_CCS'][case_index])
                case_list_dic['VAR_COST_NATGAS_CCS'][case_index] = (case_list_dic['VAR_COST_NATGAS_CCS'][case_index] 
                        + case_list_dic['CO2_PRICE'][case_index]*case_list_dic['VAR_CO2_NATGAS_CCS'][case_index])
                                                    
            if 'WIND' in system_components:
                case_list_dic['FIXED_COST_WIND'][case_index] = (case_list_dic['FIXED_COST_WIND'][case_index] 
                        + case_list_dic['CO2_PRICE'][case_index]*case_list_dic['FIXED_CO2_WIND'][case_index])
                case_list_dic['VAR_COST_WIND'][case_index] = (case_list_dic['VAR_COST_WIND'][case_index] 
                        + case_list_dic['CO2_PRICE'][case_index]*case_list_dic['VAR_CO2_WIND'][case_index])
                                                    
            if 'SOLAR' in system_components:
                case_list_dic['FIXED_COST_SOLAR'][case_index] = (case_list_dic['FIXED_COST_SOLAR'][case_index] 
                        + case_list_dic['CO2_PRICE'][case_index]*case_list_dic['FIXED_CO2_SOLAR'][case_index])
                case_list_dic['VAR_COST_SOLAR'][case_index] = (case_list_dic['VAR_COST_SOLAR'][case_index] 
                        + case_list_dic['CO2_PRICE'][case_index]*case_list_dic['VAR_CO2_SOLAR'][case_index])  
                                                    
            if 'WIND2' in system_components:
                case_list_dic['FIXED_COST_WIND2'][case_index] = (case_list_dic['FIXED_COST_WIND2'][case_index] 
                        + case_list_dic['CO2_PRICE'][case_index]*case_list_dic['FIXED_CO2_WIND2'][case_index])
                case_list_dic['VAR_COST_WIND2'][case_index] = (case_list_dic['VAR_COST_WIND2'][case_index] 
                        + case_list_dic['CO2_PRICE'][case_index]*case_list_dic['VAR_CO2_WIND2'][case_index])
                                                    
            if 'SOLAR2' in system_components:
                case_list_dic['FIXED_COST_SOLAR2'][case_index] = (case_list_dic['FIXED_COST_SOLAR2'][case_index] 
                        + case_list_dic['CO2_PRICE'][case_index]*case_list_dic['FIXED_CO2_SOLAR2'][case_index])
                case_list_dic['VAR_COST_SOLAR2'][case_index] = (case_list_dic['VAR_COST_SOLAR2'][case_index] 
                        + case_list_dic['CO2_PRICE'][case_index]*case_list_dic['VAR_CO2_SOLAR2'][case_index])  
                                                  
            #  NOTE:  Carbon embodied in STORAGE, PGP_STORAGE or CSP is not considered here !!!
            
            print  (case_list_dic['VAR_COST_NATGAS'][case_index] , case_list_dic['CO2_PRICE'][case_index],case_list_dic['VAR_CO2_NATGAS'][case_index])
            

    
    #Now case_dic is a dictionary of lists. We want to turn it into a list
    # of dictionaries.  
    case_dic_list = dict_of_lists_to_list_of_dicts(case_list_dic)
    
    return global_dic,case_dic_list
            
