# -*- coding: utf-8 -*-

"""

Save_Basic_Results.py

save basic results for the simple energy model
    
"""

# -----------------------------------------------------------------------------


import os
import numpy as np
import csv
import datetime
import contextlib
import pickle



#%%
def pickle_raw_results( global_dic, case_dic, result_dic ):
    
    output_path = global_dic['OUTPUT_PATH']
    global_name = global_dic['GLOBAL_NAME']
    case_name = case_dic['CASE_NAME']
    
    output_folder = output_path + '/' + global_name
    
    output_file_name = global_name + '_' + case_name + '.pickle'
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    with open(output_folder + "/" + output_file_name, 'wb') as db:
        pickle.dump([global_dic,case_dic,result_dic], db, protocol=pickle.HIGHEST_PROTOCOL)

#%%
def read_pickle_raw_results( global_dic, case_dic ):
    
    output_path = global_dic['OUTPUT_PATH']
    global_name = global_dic['GLOBAL_NAME']
    case_name = case_dic['CASE_NAME']
    
    output_folder = output_path + '/' + global_name
    
    output_file_name = global_name + '_' + case_name + '.pickle'
    
    with open(output_folder + "/" + output_file_name, 'rb') as db:
        [global_dic,case_dic,result_dic] = pickle.load( db )
    
    return result_dic

#%%
def pickle_raw_results_list( global_dic, case_dic_list, result_dic_list ):
    
    output_path = global_dic['OUTPUT_PATH']
    global_name = global_dic['GLOBAL_NAME']
    output_folder = output_path + '/' + global_name
    output_file_name = global_name + '.pickle'
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    with open(output_folder + "/" + output_file_name, 'wb') as db:
        pickle.dump([global_dic,case_dic_list,result_dic_list], db, protocol=pickle.HIGHEST_PROTOCOL)

#%%
def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

#%%
# save results by case
def save_list_of_vector_results_as_csv( global_dic, case_dic_list, result_dic_list ):
    
    for idx in range(len(result_dic_list)):
        
        case_dic = case_dic_list[idx]
        result_dic = result_dic_list[idx]
        save_vector_results_as_csv( global_dic, case_dic, result_dic )
        

#%%
# save results by case
def save_vector_results_as_csv( global_dic, case_dic, result_dic ):
    
    output_path = global_dic['OUTPUT_PATH']
    global_name = global_dic['GLOBAL_NAME']
    output_folder = output_path + '/' + global_name

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
             
    if len(case_dic['WIND_SERIES']) == 0:
        case_dic['WIND_SERIES'] = ( 0.*np.array(case_dic['DEMAND_SERIES'])).tolist()
    if len(case_dic['SOLAR_SERIES']) == 0:
        case_dic['SOLAR_SERIES'] = ( 0.*np.array(case_dic['DEMAND_SERIES'])).tolist()
    
    header_list = []
    series_list = []
    
    header_list += ['time (hr)']
    series_list.append( np.arange(len(case_dic['DEMAND_SERIES'])))
    
    header_list += ['demand (kW)']
    series_list.append( case_dic['DEMAND_SERIES'] )
    
    header_list += ['solar capacity factor (-)']
    series_list.append( np.array(case_dic['SOLAR_SERIES']))    
    
    header_list += ['wind capacity factor (-)']
    series_list.append( np.array(case_dic['WIND_SERIES']))

    header_list += ['dispatch natgas (kW)']
    series_list.append( result_dic['DISPATCH_NATGAS'].flatten() )
    
    header_list += ['dispatch natgas ccs (kW)']
    series_list.append( result_dic['DISPATCH_NATGAS_CCS'].flatten() )
    
    header_list += ['dispatch solar (kW)']
    series_list.append( result_dic['DISPATCH_SOLAR'].flatten() ) 
    
    header_list += ['dispatch wind (kW)']
    series_list.append( result_dic['DISPATCH_WIND'].flatten() )
    
    header_list += ['dispatch nuclear (kW)']
    series_list.append( result_dic['DISPATCH_NUCLEAR'].flatten() )
    
    header_list += ['dispatch to storage (kW)']
    series_list.append( result_dic['DISPATCH_TO_STORAGE'].flatten() )
    
    header_list += ['dispatch from storage (kW)']
    series_list.append( result_dic['DISPATCH_FROM_STORAGE'].flatten() )  # THere is no FROM in dispatch results

    header_list += ['energy storage (kWh)']
    series_list.append( result_dic['ENERGY_STORAGE'].flatten() )
  
    header_list += ['dispatch to pgp storage (kW)']
    series_list.append( result_dic['DISPATCH_TO_PGP_STORAGE'].flatten() )
    
    header_list += ['dispatch pgp storage (kW)']
    series_list.append( result_dic['DISPATCH_FROM_PGP_STORAGE'].flatten() )

    header_list += ['energy pgp storage (kWh)']
    series_list.append( result_dic['ENERGY_PGP_STORAGE'].flatten() )
    
    header_list += ['dispatch unmet demand (kW)']
    series_list.append( result_dic['DISPATCH_UNMET_DEMAND'].flatten() )
    
    header_list += ['cutailment solar (kW)']
    series_list.append( result_dic['CURTAILMENT_SOLAR'].flatten() )
    
    header_list += ['cutailment wind (kW)']
    series_list.append( result_dic['CURTAILMENT_WIND'].flatten() )
    
    header_list += ['cutailment nuclear (kW)']
    series_list.append( result_dic['CURTAILMENT_NUCLEAR'].flatten() )
    
    header_list += ['price ($/kWh)']
    series_list.append( result_dic['PRICE'].flatten() )
     
    output_file_name = global_dic['GLOBAL_NAME']+'_'+case_dic['CASE_NAME']
    
    with contextlib.closing(open(output_folder + "/" + output_file_name + '.csv', 'w',newline='')) as output_file:
        writer = csv.writer(output_file)
        writer.writerow(header_list)
        writer.writerows((np.asarray(series_list)).transpose())
        output_file.close()
        
#%%
# save scalar results for all cases
def save_basic_results( global_dic, case_dic_list ):
    
    verbose = global_dic['VERBOSE']
        
    scalar_names = [
            'case name',
            'CO2 price ($/kgCO2)',
            'fixed cost natgas ($/kW/h)',
            'fixed cost natgas ccs ($/kW/h)',
            'fixed cost solar ($/kW/h)',
            'fixed cost wind ($/kW/h)',
            'fixed cost nuclear ($/kW/h)',
            'fixed cost storage (($/h)/kWh)',
            'fixed cost pgp storage (($/h)/kWh)',
            
            'var cost natgas ($/kWh)',
            'var cost natgas ccs ($/kWh)',
            'var cost solar ($/kWh)',
            'var cost wind ($/kWh)',
            'var cost nuclear ($/kWh)',
            'var cost to storage ($/kWh)',
            'var cost storage ($/kWh)',
            'var cost to pgp storage ($/kWh)',
            'var cost pgp storage ($/kWh)',
            'var cost unmet demand ($/kWh)',
            
            'storage charging efficiency',
            'storage charging time (h)',
            'storage decay rate (1/h)',
            'pgp storage charging efficiency',
            'pgp storage decay rate (1/h)',
            
            'mean demand (kW)',
            'capacity factor solar series (-)',
            'capacity factor wind series (-)',
            
            'capacity natgas (kW)',
            'capacity natgas ccs (kW)',
            'capacity solar (kW)',
            'capacity wind (kW)',
            'capacity nuclear (kW)',
            'capacity storage (kWh)',
            'capacity pgp storage (kWh)',
            'capacity to pgp storage (kW)',
            'capacity from pgp storage (kW)',
            'system cost ($/kW/h)', # assuming demand normalized to 1 kW
            'problem status',
            
            'dispatch natgas (kW)',
            'dispatch natgas ccs (kW)',
            'dispatch solar (kW)',
            'dispatch wind (kW)',
            'dispatch nuclear (kW)',
            'dispatch to storage (kW)',
            'dispatch from storage (kW)',
            'energy storage (kWh)',
            'dispatch to pgp storage (kW)',
            'dispatch pgp storage (kW)',
            'energy pgp storage (kWh)',
            'dispatch unmet demand (kW)',
            
            'curtailment solar (kW)',
            'curtailment wind (kW)',
            'curtailment nuclear (kW)'
            ]

    scalar_table = []
    for idx in range(len(case_dic_list)):
        case_dic = case_dic_list[idx]
        result_dic = read_pickle_raw_results(global_dic, case_dic)
        
        scalar_table.append(
            [       case_dic['CASE_NAME'],
                    case_dic['CO2_PRICE'],
             
                    # assumptions
                    
                    case_dic['FIXED_COST_NATGAS'],
                    case_dic['FIXED_COST_NATGAS_CCS'],
                    case_dic['FIXED_COST_SOLAR'],
                    case_dic['FIXED_COST_WIND'],
                    case_dic['FIXED_COST_NUCLEAR'],
                    case_dic['FIXED_COST_STORAGE'],
                    case_dic['FIXED_COST_PGP_STORAGE'],
                    
                    case_dic['VAR_COST_NATGAS'],
                    case_dic['VAR_COST_NATGAS_CCS'],
                    case_dic['VAR_COST_SOLAR'],
                    case_dic['VAR_COST_WIND'],
                    case_dic['VAR_COST_NUCLEAR'],
                    case_dic['VAR_COST_TO_STORAGE'],
                    case_dic['VAR_COST_FROM_STORAGE'],
                    case_dic['VAR_COST_TO_PGP_STORAGE'],
                    case_dic['VAR_COST_FROM_PGP_STORAGE'],
                    case_dic['VAR_COST_UNMET_DEMAND'],
                    
                    case_dic['STORAGE_CHARGING_EFFICIENCY'],
                    case_dic['STORAGE_CHARGING_TIME'],
                    case_dic['STORAGE_DECAY_RATE'],
                    case_dic['PGP_STORAGE_CHARGING_EFFICIENCY'],
                    case_dic['PGP_STORAGE_DECAY_RATE'],
                    
                    # mean of time series assumptions
                    np.average(case_dic['DEMAND_SERIES']),
                    np.average(case_dic['SOLAR_SERIES']),
                    np.average(case_dic['WIND_SERIES']),
                                    
                    # scalar results
                    
                    result_dic['CAPACITY_NATGAS'],
                    result_dic['CAPACITY_NATGAS_CCS'],
                    result_dic['CAPACITY_SOLAR'],
                    result_dic['CAPACITY_WIND'],
                    result_dic['CAPACITY_NUCLEAR'],
                    result_dic['CAPACITY_STORAGE'],
                    result_dic['CAPACITY_PGP_STORAGE'],
                    result_dic['CAPACITY_TO_PGP_STORAGE'],
                    result_dic['CAPACITY_FROM_PGP_STORAGE'],
                    result_dic['SYSTEM_COST'],
                    result_dic['PROBLEM_STATUS'],
                    
                    # mean of time series results                
                                
                    np.average(result_dic['DISPATCH_NATGAS']),
                    np.average(result_dic['DISPATCH_NATGAS_CCS']),
                    np.average(result_dic['DISPATCH_SOLAR']),
                    np.average(result_dic['DISPATCH_WIND']),
                    np.average(result_dic['DISPATCH_NUCLEAR']),
                    np.average(result_dic['DISPATCH_TO_STORAGE']),
                    np.average(result_dic['DISPATCH_FROM_STORAGE']),
                    np.average(result_dic['ENERGY_STORAGE']),
                    np.average(result_dic['DISPATCH_TO_PGP_STORAGE']),
                    np.average(result_dic['DISPATCH_FROM_PGP_STORAGE']),
                    np.average(result_dic['ENERGY_PGP_STORAGE']),
                    np.average(result_dic['DISPATCH_UNMET_DEMAND']),
                    
                    np.average(result_dic['CURTAILMENT_SOLAR']),
                    np.average(result_dic['CURTAILMENT_WIND']),
                    np.average(result_dic['CURTAILMENT_NUCLEAR'])
                    
                    
             ]
            )
            
    output_path = global_dic['OUTPUT_PATH']
    global_name = global_dic['GLOBAL_NAME']
    output_folder = output_path + "/" + global_name
    today = datetime.datetime.now()
    todayString = str(today.year) + str(today.month).zfill(2) + str(today.day).zfill(2) + '_' + \
        str(today.hour).zfill(2) + str(today.minute).zfill(2) + str(today.second).zfill(2)
    
    output_file_name = global_name + '_' + todayString
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    with contextlib.closing(open(output_folder + "/" + output_file_name + '.csv', 'w',newline='')) as output_file:
        writer = csv.writer(output_file)
        writer.writerow(scalar_names)
        writer.writerows(scalar_table)
        output_file.close()
        
    if verbose: 
        print ( 'file written: ' + output_file_name + '.csv')
    
    return scalar_names,scalar_table
    
def out_csv(output_folder,output_file_name,names,table,verbose):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    with contextlib.closing(open(output_folder + "/" + output_file_name + '.csv', 'w',newline='')) as output_file:
        writer = csv.writer(output_file)
        writer.writerow(names)
        writer.writerows(table)
        output_file.close()
        
    if verbose: 
        print ( 'file written: ' + output_file_name + '.csv')
    


    
