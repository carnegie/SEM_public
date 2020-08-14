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
                 'NATGAS','NATGAS_CCS','NUCLEAR','STORAGE', 'PGP_STORAGE', 'UNMET'
    'DEMAND_SERIES' -- TIME SERIES OF DEMAND DATA
    
Each dictionary in <case_dic_list> OPTIONALLY contains:
    
           ['NUMERICS_COST_SCALING','NUMERICS_DEMAND_SCALING',
             'END_DAY','END_HOUR','END_MONTH',
            'END_YEAR','FIXED_COST_NATGAS','FIXED_COST_NATGAS_CCS','FIXED_COST_SOLAR','FIXED_COST_WIND',
            'FIXED_COST_NUCLEAR','FIXED_COST_STORAGE',
            'START_DAY','START_HOUR','START_MONTH',
            'START_YEAR','STORAGE_CHARGING_EFFICIENCY',
            'VAR_COST_STORAGE','VAR_COST_TO_STORAGE',
            'VAR_COST_NATGAS','VAR_COST_NATGAS_CCS','VAR_COST_SOLAR','STORAGE_DECAY_RATE',
            'VAR_COST_WIND','VAR_COST_NUCLEAR','VAR_COST_UNMET_DEMAND',
            'STORAGE_CHARGING_TIME',
            'FIXED_COST_PGP_STORAGE',
            'FIXED_COST_TO_PGP_STORAGE','FIXED_COST_FROM_PGP_STORAGE',
            'VAR_COST_TO_PGP_STORAGE','VAR_COST_FROM_PGP_STORAGE',
            'PGP_STORAGE_CHARGING_EFFICIENCY']

'''

import csv
import numpy as np



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
             'SOLAR_CAPACITY_FILE','WIND_CAPACITY_FILE','OUTPUT_PATH',
             'CASE_NAME','GLOBAL_NAME']
            ))
    
    keywords_real = list(map(str.upper,
            ['NUMERICS_COST_SCALING','NUMERICS_DEMAND_SCALING',
             'END_DAY','END_HOUR','END_MONTH','CO2_PRICE',
            'END_YEAR','FIXED_COST_NATGAS','FIXED_COST_NATGAS_CCS','FIXED_COST_SOLAR','FIXED_COST_WIND',
            'FIXED_COST_NUCLEAR','FIXED_COST_STORAGE',
            'FIXED_CO2_NATGAS','FIXED_CO2_NATGAS_CCS','FIXED_CO2_NUCLEAR','FIXED_CO2_WIND','FIXED_CO2_SOLAR',
            'VAR_CO2_NATGAS','VAR_CO2_NATGAS_CCS','VAR_CO2_NUCLEAR','VAR_CO2_WIND','VAR_CO2_SOLAR',
            'START_DAY','START_HOUR','START_MONTH',
            'START_YEAR','STORAGE_CHARGING_EFFICIENCY',
            'VAR_COST_FROM_STORAGE','VAR_COST_TO_STORAGE',
            'VAR_COST_NATGAS','VAR_COST_NATGAS_CCS','VAR_COST_SOLAR','STORAGE_DECAY_RATE',
            'VAR_COST_WIND','VAR_COST_NUCLEAR','VAR_COST_UNMET_DEMAND',
            'STORAGE_CHARGING_TIME',
            'FIXED_COST_PGP_STORAGE',
            'FIXED_COST_TO_PGP_STORAGE','FIXED_COST_FROM_PGP_STORAGE',
            'VAR_COST_TO_PGP_STORAGE','VAR_COST_FROM_PGP_STORAGE',
            'PGP_STORAGE_CHARGING_EFFICIENCY','PGP_STORAGE_DECAY_RATE',
            'CAPACITY_NATGAS','CAPACITY_NATGAS_CCS','CAPACITY_SOLAR',
            'CAPACITY_WIND','CAPACITY_NUCLEAR','CAPACITY_STORAGE',
            'CAPACITY_PGP_STORAGE','CAPACITY_TO_PGP_STORAGE','CAPACITY_FROM_PGP_STORAGE']
            ))
    
    keywords_real_notscaled = list(map(str.upper,
            ['NUMERICS_COST_SCALING','NUMERICS_DEMAND_SCALING',
             'END_DAY','END_HOUR','END_MONTH',
            'END_YEAR',
            'START_DAY','START_HOUR','START_MONTH',
            'START_YEAR',
            'PGP_STORAGE_CHARGING_EFFICIENCY','PGP_STORAGE_DECAY_RATE',
            'STORAGE_CHARGING_EFFICIENCY','STORAGE_DECAY_RATE',
            'CAPACITY_NATGAS','CAPACITY_NATGAS_CCS','CAPACITY_SOLAR',
            'CAPACITY_WIND','CAPACITY_NUCLEAR','CAPACITY_STORAGE',
            'CAPACITY_PGP_STORAGE','CAPACITY_TO_PGP_STORAGE','CAPACITY_FROM_PGP_STORAGE']
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
        test_key = str.upper(list_item[0])
        test_value = list_item[1]
        if test_key in keywords_str:
            global_dic[test_key] = test_value
        elif test_key in keywords_real:
            global_dic[test_key] = float(test_value)
        elif test_key in keywords_logical:
            global_dic[test_key] = literal_to_boolean(test_value)
    
    verbose = global_dic['VERBOSE']
#    print ( global_dic
    if verbose:
        print ( 'Preprocess_Input.py: Preparing case input for ',global_dic['GLOBAL_NAME'])
        
    # Parse all_cases_dic data
    all_cases_dic = {}
    
    #------ DEFAULT VALUES FOR global_dic ---------
    # For now, default for quicklook output is True
    all_cases_dic['NORMALIZE_DEMAND_TO_ONE'] = False # If True, normalize mean demand to 1.0
    all_cases_dic['CO2_PRICE'] = 0.0 # If True, normalize mean demand to 1.0
    # default global values to help with numerical issues
    all_cases_dic['NUMERICS_COST_SCALING'] = 1e+12 # multiplies all costs by a factor and then divides at end
    all_cases_dic['NUMERICS_DEMAND_SCALING'] = 1e+12 # multiplies demand by a factor and then divides all costs and capacities at end
    
    #                'CAPACITY_NATGAS','CAPACITY_NATGAS_CCS','CAPACITY_SOLAR',
    #            'CAPACITY_WIND','CAPACITY_NUCLEAR','CAPACITY_STORAGE,
    #            'CAPACITY_PGP_STORAGE','CAPACITY_TO_PGP_STORAGE','CAPACITY_FROM_PGP_STORAGE']
    
    all_cases_dic['CAPACITY_NATGAS'] = -1. # if < 0, then calculated in optimization
    all_cases_dic['CAPACITY_NATGAS_CCS'] = -1. # if < 0, then calculated in optimization
    all_cases_dic['CAPACITY_SOLAR'] = -1. # if < 0, then calculated in optimization
    all_cases_dic['CAPACITY_WIND'] = -1. # if < 0, then calculated in optimization
    all_cases_dic['CAPACITY_NUCLEAR'] = -1. # if < 0, then calculated in optimization
    all_cases_dic['CAPACITY_STORAGE'] = -1. # if < 0, then calculated in optimization
    all_cases_dic['CAPACITY_PGP_STORAGE'] = -1. # if < 0, then calculated in optimization
    all_cases_dic['CAPACITY_TO_PGP_STORAGE'] = -1. # if < 0, then calculated in optimization
    all_cases_dic['CAPACITY_FROM_PGP_STORAGE'] = -1. # if < 0, then calculated in optimization

    for list_item in all_cases_data:
        test_key = str.upper(list_item[0])
        test_value = list_item[1]
        if test_key in keywords_str:
            all_cases_dic[test_key] = test_value
        elif test_key in keywords_real:
            all_cases_dic[test_key] = float(test_value)
        elif test_key in keywords_logical:
            all_cases_dic[test_key] = literal_to_boolean(test_value)
    
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
        test_key = str.upper(list_item[0])
        test_values = list_item[1:]
        if test_key in keywords_str:
            case_list_dic[test_key] = test_values
        elif test_key in keywords_real:
            if test_key in keywords_real_notscaled:
                setNegToM1 = np.array(list(map(float,test_values)))
            else:
                setNegToM1 = case_list_dic[test_key] * np.array(list(map(float,test_values)))
            setNegToM1[setNegToM1 < 0] = -1
            case_list_dic[test_key] = setNegToM1
        elif test_key in keywords_logical:
            case_list_dic[test_key] = list(map(bool,test_values))

    # define all keywords in dictionary, but set to -1 if not present    
    dummy = [-1 for i in range(num_cases)]
    for keyword in list(set(keywords_real).difference(case_list_dic.keys())):
        case_list_dic[keyword] = dummy
    
    # ok, now we have everything from the case_input file in case_list_dic.
    # Let's add the other things we need. First, we will see what system components
    # are used in each case.
    
    # for wind, solar, and demand, we also need to get the relevant demand files
    

    
    have_keys = case_list_dic.keys()

    solar_series_list = []
    wind_series_list = []
    demand_series_list = []

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
    
    case_list_dic['DEMAND_SERIES'] = demand_series_list
    case_list_dic['WIND_SERIES'] = wind_series_list
    case_list_dic['SOLAR_SERIES'] = solar_series_list
                                                
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
                                                
        if 'FIXED_COST_STORAGE' in have_keys:
            if case_list_dic['FIXED_COST_STORAGE'][case_index] >= 0 and case_list_dic['VAR_COST_TO_STORAGE'][case_index] >= 0  and case_list_dic['VAR_COST_FROM_STORAGE'][case_index] >= 0 :
                component_list.append('STORAGE')
                
        if 'FIXED_COST_PGP_STORAGE' in have_keys:
            if (case_list_dic['FIXED_COST_PGP_STORAGE'][case_index] >= 0 and case_list_dic['VAR_COST_FROM_PGP_STORAGE'][case_index] >= 0  and 
                case_list_dic['VAR_COST_TO_PGP_STORAGE'][case_index] >= 0 and case_list_dic['PGP_STORAGE_CHARGING_EFFICIENCY'][case_index] >= 0):
                component_list.append('PGP_STORAGE')
                
        if 'VAR_COST_UNMET_DEMAND' in have_keys:
            if case_list_dic['VAR_COST_UNMET_DEMAND'][case_index] >= 0:
                component_list.append('UNMET_DEMAND')
                                
        list_of_component_lists.append(component_list)
    case_list_dic['SYSTEM_COMPONENTS'] = list_of_component_lists
    
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
            
            print  (case_list_dic['VAR_COST_NATGAS'][case_index] , case_list_dic['CO2_PRICE'][case_index],case_list_dic['VAR_CO2_NATGAS'][case_index])
            

    
    #Now case_dic is a dictionary of lists. We want to turn it into a list
    # of dictionaries.  The method for doing this is taken from:
    # https://stackoverflow.com/questions/5558418/list-of-dicts-to-from-dict-of-lists
    
    # case_dic_list = [dict(zip(case_list_dic,t)) for t in zip(*case_list_dic.values())]
    
    # The fancy thing didn't work for me so I will brute force it.
    #
    keywords = case_list_dic.keys()
    case_dic_list = [ {} for  case in range(num_cases)]
    for i in range(num_cases):
        dic = case_dic_list[i]
        for keyword in keywords:
            dic[keyword] = case_list_dic[keyword][i]
        case_dic_list[i] = dic
    
    return global_dic,case_dic_list

             
