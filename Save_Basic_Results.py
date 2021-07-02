# -*- coding: utf-8 -*-

"""

Save_Basic_Results.py

save basic results for the simple energy model
    
"""

# -----------------------------------------------------------------------------


import os
import copy
import numpy as np
import csv
import datetime
import contextlib
import pickle
from utilities import list_of_dicts_to_dict_of_lists, unique_list_of_lists



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
             
    if len(case_dic['WIND2_SERIES']) == 0:
        case_dic['WIND2_SERIES'] = ( 0.*np.array(case_dic['DEMAND_SERIES'])).tolist()
    if len(case_dic['SOLAR2_SERIES']) == 0:
        case_dic['SOLAR2_SERIES'] = ( 0.*np.array(case_dic['DEMAND_SERIES'])).tolist()
    
    if len(case_dic['CSP_SERIES']) == 0:
        case_dic['CSP_SERIES'] = ( 0.*np.array(case_dic['DEMAND_SERIES'])).tolist()
    
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

    header_list += ['solar2 capacity factor (-)']
    series_list.append( np.array(case_dic['SOLAR2_SERIES']))    
    
    header_list += ['wind2 capacity factor (-)']
    series_list.append( np.array(case_dic['WIND2_SERIES']))

    header_list += ['dispatch natgas (kW)']
    series_list.append( result_dic['DISPATCH_NATGAS'].flatten() )
    
    header_list += ['dispatch natgas_ccs (kW)']
    series_list.append( result_dic['DISPATCH_NATGAS_CCS'].flatten() )
    
    header_list += ['dispatch solar (kW)']
    series_list.append( result_dic['DISPATCH_SOLAR'].flatten() ) 
    
    header_list += ['dispatch wind (kW)']
    series_list.append( result_dic['DISPATCH_WIND'].flatten() )
    
    header_list += ['dispatch solar2 (kW)']
    series_list.append( result_dic['DISPATCH_SOLAR2'].flatten() ) 
    
    header_list += ['dispatch wind2 (kW)']
    series_list.append( result_dic['DISPATCH_WIND2'].flatten() )
    
    header_list += ['dispatch nuclear (kW)']
    series_list.append( result_dic['DISPATCH_NUCLEAR'].flatten() )
    
    header_list += ['dispatch to fuel h2 storage (kW)']
    series_list.append( result_dic['DISPATCH_TO_FUEL_H2_STORAGE'].flatten() )
    
    header_list += ['dispatch from fuel h2 storage tot (kW)']
    series_list.append( result_dic['DISPATCH_FROM_FUEL_H2_STORAGE_TOT'].flatten() )

    header_list += ['dispatch from fuel h2 storage chem plant (kW)']
    series_list.append( result_dic['DISPATCH_FROM_FUEL_H2_STORAGE_CHEM'].flatten() )

    header_list += ['dispatch from fuel h2 storage power (kW)']
    series_list.append( result_dic['DISPATCH_FROM_FUEL_H2_STORAGE_POWER'].flatten() )

    header_list += ['fuel h2 storage (kWh)']
    series_list.append( result_dic['FUEL_H2_STORAGE'].flatten() )
    
    header_list += ['dispatch to storage (kW)']
    series_list.append( result_dic['DISPATCH_TO_STORAGE'].flatten() )
    
    header_list += ['dispatch from storage (kW)']
    series_list.append( result_dic['DISPATCH_FROM_STORAGE'].flatten() )  # THere is no FROM in dispatch results

    header_list += ['energy storage (kWh)']
    series_list.append( result_dic['ENERGY_STORAGE'].flatten() )
    
    header_list += ['dispatch to storage2 (kW)']
    series_list.append( result_dic['DISPATCH_TO_STORAGE2'].flatten() )
    
    header_list += ['dispatch from storage2 (kW)']
    series_list.append( result_dic['DISPATCH_FROM_STORAGE2'].flatten() )  # THere is no FROM in dispatch results

    header_list += ['energy storage2 (kWh)']
    series_list.append( result_dic['ENERGY_STORAGE2'].flatten() )
    
    header_list += ['dispatch to pgp storage (kW)']
    series_list.append( result_dic['DISPATCH_TO_PGP_STORAGE'].flatten() )
    
    header_list += ['dispatch pgp storage (kW)']
    series_list.append( result_dic['DISPATCH_FROM_PGP_STORAGE'].flatten() )

    header_list += ['energy pgp storage (kWh)']
    series_list.append( result_dic['ENERGY_PGP_STORAGE'].flatten() )
    
    header_list += ['dispatch to csp storage (kW)']
    series_list.append( result_dic['DISPATCH_TO_CSP_STORAGE'].flatten() )  # THere is no FROM in dispatch results
    
    header_list += ['dispatch from csp storage (kW)']
    series_list.append( result_dic['DISPATCH_FROM_CSP'].flatten() )  # THere is no FROM in dispatch results

    header_list += ['energy csp storage (kWh)']
    series_list.append( result_dic['ENERGY_CSP_STORAGE'].flatten() )
    
    header_list += ['dispatch unmet demand (kW)']
    series_list.append( result_dic['DISPATCH_UNMET_DEMAND'].flatten() )
    
    header_list += ['cutailment solar (kW)']
    series_list.append( result_dic['CURTAILMENT_SOLAR'].flatten() )
    
    header_list += ['cutailment wind (kW)']
    series_list.append( result_dic['CURTAILMENT_WIND'].flatten() )
    
    header_list += ['cutailment solar2 (kW)']
    series_list.append( result_dic['CURTAILMENT_SOLAR2'].flatten() )
    
    header_list += ['cutailment wind2 (kW)']
    series_list.append( result_dic['CURTAILMENT_WIND2'].flatten() )
    
    header_list += ['cutailment csp (kW)']
    series_list.append( result_dic['CURTAILMENT_CSP'].flatten() )
    
    header_list += ['cutailment nuclear (kW)']
    series_list.append( result_dic['CURTAILMENT_NUCLEAR'].flatten() )
    
    header_list += ['price ($/kWh)']
    series_list.append( result_dic['PRICE'].flatten() )
     
    if 'PRICE_FUEL' in result_dic.keys():
        header_list += ['fuel price ($/kWh)']
        series_list.append( result_dic['PRICE_FUEL'].flatten() )
     
    output_file_name = global_dic['GLOBAL_NAME']+'_'+case_dic['CASE_NAME']
    
    with contextlib.closing(open(output_folder + "/" + output_file_name + '.csv', 'w',newline='')) as output_file:
        writer = csv.writer(output_file)
        writer.writerow(header_list)
        writer.writerows((np.asarray(series_list)).transpose())
        output_file.close()
        
#%%
# save scalar results for all cases
def save_basic_results( global_dic, case_dic_list ):
    global case_list_dic,case_dic_list_0
    
    verbose = global_dic['VERBOSE']
    
    case_dic_list_0 = copy.deepcopy(case_dic_list)
    
    demand_series_vect = case_dic_list_0[0]['DEMAND_SERIES'] # <--- this was being flattened to a mean value
    # if anything in case_dic_list_0 is a vector, take its mean
    for i in range(len(case_dic_list_0)):
        for key in list(case_dic_list_0[i]):
            res = case_dic_list_0[i][key]
            if isinstance(res,list) or isinstance(res,np.ndarray):
                try:
                    case_dic_list_0[i][key] = np.average(np.array(res))
                except:
                    if not key == 'SYSTEM_COMPONENTS':
                        print ('failed to average (dic):',key)
            else:
                case_dic_list_0[i][key] = res
                
                
    # add scalar means of vector results to dic
    for i in range(len(case_dic_list_0)):
        case_dic = case_dic_list_0[i]
        result_dic = read_pickle_raw_results(global_dic, case_dic)
        for key in list(result_dic):
            res = result_dic[key]
            if isinstance(res,list) or isinstance(res,np.ndarray):
                try:
                    case_dic_list_0[i][key] = np.average(np.array(res))
                    #print (case_dic_list_0[i][key])
                except:
                    print ('failed to average (res):',key)
            else:
                case_dic_list_0[i][key] = res
    
    # cvt list of dictionaries to dictionary of lists    
    case_list_dic = list_of_dicts_to_dict_of_lists (case_dic_list_0)
    
    components = unique_list_of_lists(case_list_dic['SYSTEM_COMPONENTS'])

    header_list = []
    series_list = []
    
    #==========================================================================
    header_list += ['case name']
    series_list.append( case_list_dic['CASE_NAME'])

    header_list += ['system reliability']
    series_list.append( case_list_dic['SYSTEM_RELIABILITY'])

    header_list += ['CO2 price ($/kgCO2)']
    series_list.append( case_list_dic['CO2_PRICE'])

    # Demand
    
    header_list += ['norm. demand to 1']
    series_list.append(case_list_dic['NORMALIZE_DEMAND_TO_ONE'])
    
    header_list += ['demand file']
    series_list.append(case_list_dic['DEMAND_FILE'])
    
    header_list += ['mean demand (kW)']
    series_list.append(case_list_dic['DEMAND_SERIES'])
    
    # Input: NATGAS
    if 'NATGAS' in components:
        header_list += ['fixed cost natgas ($/kW/h)']
        series_list.append( case_list_dic['FIXED_COST_NATGAS'])
    
        header_list += ['var cost natgas ($/kW/h)']
        series_list.append( case_list_dic['VAR_COST_NATGAS'])

    # Input: NATGAS_CCS
    if 'NATGAS_CCS' in components:
        header_list += ['fixed cost natgas_ccs ($/kW/h)']
        series_list.append( case_list_dic['FIXED_COST_NATGAS_CCS'])
    
        header_list += ['var cost natgas_ccs ($/kW/h)']
        series_list.append( case_list_dic['VAR_COST_NATGAS_CCS'])
   
    # Input: SOLAR
    if 'SOLAR' in components: 
        header_list += ['fixed cost solar ($/kW/h)']
        series_list.append( case_list_dic['FIXED_COST_SOLAR'])
     
        header_list += ['var cost solar ($/kW/h)']
        series_list.append( case_list_dic['VAR_COST_SOLAR'])
    
        header_list += ['solar file']
        series_list.append(case_list_dic['SOLAR_CAPACITY_FILE'])
    
        header_list += ['cap factor solar (-)']
        series_list.append( case_list_dic['SOLAR_SERIES'])
    
    # Input: SOLAR2
    if 'SOLAR2' in components: 
        header_list += ['fixed cost solar2 ($/kW/h)']
        series_list.append( case_list_dic['FIXED_COST_SOLAR2'])
    
        header_list += ['var cost solar2 ($/kW/h)']
        series_list.append( case_list_dic['VAR_COST_SOLAR2'])
    
        header_list += ['solar2 file']
        series_list.append(case_list_dic['SOLAR2_CAPACITY_FILE'])
        
        header_list += ['cap factor solar2 (-)']
        series_list.append( case_list_dic['SOLAR2_SERIES'])

    # Input: WIND
    if 'WIND' in components: 
        header_list += ['fixed cost wind ($/kW/h)']
        series_list.append( case_list_dic['FIXED_COST_WIND'])
    
        header_list += ['var cost wind ($/kW/h)']
        series_list.append( case_list_dic['VAR_COST_WIND'] )
    
        header_list += ['wind file']
        series_list.append(case_list_dic['WIND_CAPACITY_FILE'])
    
        header_list += ['cap factor wind (-)']
        series_list.append(case_list_dic['WIND_SERIES'])
    
    # Input: WIND2
    if 'WIND2' in components: 
        header_list += ['fixed cost wind2 ($/kW/h)']
        series_list.append( case_list_dic['FIXED_COST_WIND2'])
    
        header_list += ['var cost wind2 ($/kW/h)']
        series_list.append( case_list_dic['VAR_COST_WIND2'] )
    
        header_list += ['wind2 file']
        series_list.append(case_list_dic['WIND2_CAPACITY_FILE'])
    
        header_list += ['cap factor wind2 (-)']
        series_list.append( case_list_dic['WIND2_SERIES'])
    
    # Input: NUCLEAR
    if 'NUCLEAR' in components: 
        header_list += ['fixed cost nuclear ($/kW/h)']
        series_list.append( case_list_dic['FIXED_COST_NUCLEAR'] )
    
        header_list += ['var cost nuclear ($/kW/h)']
        series_list.append( case_list_dic['VAR_COST_NUCLEAR'] )

    # Input: FUEL
    if 'FUEL' in components: 
        header_list += ['fixed cost fuel electrolyzer ($/kW/h)']
        series_list.append( case_list_dic['FIXED_COST_FUEL_ELECTROLYZER'] )
    
        header_list += ['fixed cost fuel chem plant ($/kW/h)']
        series_list.append( case_list_dic['FIXED_COST_FUEL_CHEM_PLANT'] )
    
        header_list += ['fixed cost fuel power ($/kW/h)']
        series_list.append( case_list_dic['FIXED_COST_FUEL_POWER'] )
    
        header_list += ['fixed cost fuel h2 storage ($/kWh/h)']
        series_list.append( case_list_dic['FIXED_COST_FUEL_H2_STORAGE'] )
    
        header_list += ['var cost fuel electrolyzer ($/kW/h)']
        series_list.append( case_list_dic['VAR_COST_FUEL_ELECTROLYZER'] )

        header_list += ['var cost fuel chem plant ($/kW/h)']
        series_list.append( case_list_dic['VAR_COST_FUEL_CHEM_PLANT'] )

        header_list += ['var cost fuel co2 ($/kW/h)']
        series_list.append( case_list_dic['VAR_COST_FUEL_CO2'] )

        header_list += ['efficiency fuel electrolyzer']
        series_list.append( case_list_dic['EFFICIENCY_FUEL_ELECTROLYZER'] )

        header_list += ['efficiency fuel chem conversion']
        series_list.append( case_list_dic['EFFICIENCY_FUEL_CHEM_CONVERSION'] )

        header_list += ['efficiency fuel power conversion']
        series_list.append( case_list_dic['EFFICIENCY_FUEL_POWER_CONVERSION'] )

        header_list += ['fuel cost ($/GGE)']
        series_list.append( case_list_dic['FUEL_VALUE'] )

        header_list += ['fuel demand (kWh)']
        series_list.append( case_list_dic['FUEL_DEMAND'] )

    # Input: STORAGE
    if 'STORAGE' in components: 
        header_list += ['fixed cost storage ($/kWh/h)']
        series_list.append( case_list_dic['FIXED_COST_STORAGE'])
    
        header_list += ['var cost storage ($/kWh/h)']
        series_list.append( case_list_dic['VAR_COST_STORAGE'] )
    
        header_list += ['storage charging efficiency']
        series_list.append( case_list_dic['CHARGING_EFFICIENCY_STORAGE'])
    
        header_list += ['storage charging time (h)']
        series_list.append( case_list_dic['CHARGING_TIME_STORAGE'] )
    
        header_list += ['storage decay rate (1/h))']
        series_list.append( case_list_dic['DECAY_RATE_STORAGE'] )
    
    # Input: STORAGE2
    if 'STORAGE2' in components: 
        header_list += ['fixed cost storage2 ($/kWh/h)']
        series_list.append( case_list_dic['FIXED_COST_STORAGE2'])
    
        header_list += ['var cost storage2 ($/kWh/h)']
        series_list.append( case_list_dic['VAR_COST_STORAGE2'])
    
        header_list += ['storage2 charging efficiency']
        series_list.append( case_list_dic['CHARGING_EFFICIENCY_STORAGE2'])
    
        header_list += ['storage2 charging time (h)']
        series_list.append( case_list_dic['CHARGING_TIME_STORAGE2'])
    
        header_list += ['storage2 decay rate (1/h))']
        series_list.append( case_list_dic['DECAY_RATE_STORAGE2'] )

    # Input: PGP_STORAGE
    if 'PGP_STORAGE' in components: 
        header_list += ['fixed cost pgp storage ($/kWh/h)']
        series_list.append( case_list_dic['FIXED_COST_PGP_STORAGE'] )
    
        header_list += ['fixed cost to pgp storage ($/kW/h)']
        series_list.append( case_list_dic['FIXED_COST_TO_PGP_STORAGE'])
    
        header_list += ['fixed cost from pgp storage ($/kW/h)']
        series_list.append ( case_list_dic['FIXED_COST_FROM_PGP_STORAGE'])
    
        header_list += ['var cost to pgp storage ($/kW/h)']
        series_list.append( case_list_dic['VAR_COST_TO_PGP_STORAGE'])
    
        header_list += ['var cost from pgp storage ($/kW/h)']
        series_list.append( case_list_dic['VAR_COST_FROM_PGP_STORAGE'])
    
        header_list += ['pgp storage charging efficiency']
        series_list.append( case_list_dic['CHARGING_EFFICIENCY_PGP_STORAGE'])
    
        header_list += ['pgp storage decay rate (1/h))']
        series_list.append( case_list_dic['DECAY_RATE_PGP_STORAGE'])
    
    # Input: CSP
    if 'CSP' in components: 
        header_list += ['fixed cost csp ($/kW/h)']
        series_list.append( case_list_dic['FIXED_COST_CSP'])
    
        header_list += ['var cost csp ($/kW/h)']
        series_list.append( case_list_dic['VAR_COST_CSP'])
    
        header_list += ['fixed cost csp storage ($/kWh/h)']
        series_list.append( case_list_dic['FIXED_COST_CSP_STORAGE'])
        
        header_list += ['var cost csp storage ($/kWh/h)']
        series_list.append( case_list_dic['VAR_COST_CSP_STORAGE'])
        
        header_list += ['csp charging efficiency']
        series_list.append( case_list_dic['CHARGING_EFFICIENCY_CSP_STORAGE'])
    
        header_list += ['csp storage decay rate (1/h))']
        series_list.append( case_list_dic['DECAY_RATE_CSP_STORAGE'])
    
        header_list += ['csp file']
        series_list.append(case_list_dic['CSP_CAPACITY_FILE'])
        
        header_list += ['cap factor csp (-)']
        series_list.append(case_list_dic['CSP_SERIES'])
          
    # Input: UNMET_DEMAND
    if 'UNMET_DEMAND' in components: 
        header_list += ['var cost unmet demand ($/kWh)']
        series_list.append( case_list_dic['VAR_COST_UNMET_DEMAND'])

    #==========================================================================
    # OUTPUT VARIABLES
    header_list += ['problem status']
    series_list.append( case_list_dic['PROBLEM_STATUS'])
    
    header_list += ['system cost ($ or $/kWh)']
    series_list.append( case_list_dic['SYSTEM_COST'])

    # Results: NATGAS
    if 'NATGAS' in components: 
        header_list += ['capacity natgas (kW)']
        series_list.append( case_list_dic['CAPACITY_NATGAS'])
        print(" --- capacity natgas (kW) {}".format(case_list_dic['CAPACITY_NATGAS']))
    
        header_list += ['dispatch natgas (kW)']
        series_list.append( case_list_dic['DISPATCH_NATGAS'])
    
    # Results: NATGAS_CCS
    if 'NATGAS_CCS' in components: 
        header_list += ['capacity natgas_ccs (kW)']
        series_list.append( case_list_dic['CAPACITY_NATGAS_CCS'])
    
        header_list += ['dispatch natgas_ccs (kW)']
        series_list.append( case_list_dic['DISPATCH_NATGAS_CCS'])
    
    # Results: SOLAR
    if 'SOLAR' in components: 
        header_list += ['capacity solar (kW)']
        series_list.append(  case_list_dic['CAPACITY_SOLAR'])
        print(' --- capacity solar (kW) {}'.format(result_dic['CAPACITY_SOLAR']))
    
        header_list += ['dispatch solar (kW)']
        series_list.append( case_list_dic['DISPATCH_SOLAR'])
    
        header_list += ['curtailment solar (kW)']
        series_list.append( case_list_dic['CURTAILMENT_SOLAR'])
    
    # Results: SOLAR2
    if 'SOLAR2' in components: 
        header_list += ['capacity solar2 (kW)']
        series_list.append(  case_list_dic['CAPACITY_SOLAR2'])
    
        header_list += ['dispatch solar2 (kW)']
        series_list.append( case_list_dic['DISPATCH_SOLAR2'])
    
        header_list += ['curtailment solar2 (kW)']
        series_list.append( case_list_dic['CURTAILMENT_SOLAR2'])
    
    # Results: WIND
    if 'WIND' in components: 
        header_list += ['capacity wind (kW)']
        series_list.append(  case_list_dic['CAPACITY_WIND'])
        print(' --- capacity wind (kW) {}'.format(result_dic['CAPACITY_WIND']))
    
        header_list += ['dispatch wind (kW)']
        series_list.append( case_list_dic['DISPATCH_WIND'])
    
        header_list += ['curtailment wind (kW)']
        series_list.append( case_list_dic['CURTAILMENT_WIND'])
    
    # Results: WIND2
    if 'WIND2' in components: 
        header_list += ['capacity wind2 (kW)']
        series_list.append(  case_list_dic['CAPACITY_WIND2'])
    
        header_list += ['dispatch wind2 (kW)']
        series_list.append( case_list_dic['DISPATCH_WIND2'])
    
        header_list += ['curtailment wind2 (kW)']
        series_list.append( case_list_dic['CURTAILMENT_WIND2'])
    
    # Results: NUCLEAR
    if 'NUCLEAR' in components: 
        header_list += ['capacity nuclear (kW)']
        series_list.append(  case_list_dic['CAPACITY_NUCLEAR'])
        print(' --- capacity nuclear (kW) {}'.format(result_dic['CAPACITY_NUCLEAR']))
    
        header_list += ['dispatch nuclear (kW)']
        series_list.append( case_list_dic['DISPATCH_NUCLEAR'])
    
        header_list += ['curtailment nuclear (kW)']
        series_list.append( case_list_dic['CURTAILMENT_NUCLEAR'])
    
    # Results: FUEL
    if 'FUEL' in components: 
        header_list += ['capacity fuel electrolyzer (kW)']
        series_list.append(  case_list_dic['CAPACITY_FUEL_ELECTROLYZER'])
        print(' --- capacity fuel electrolyzer (kW) {}'.format(result_dic['CAPACITY_FUEL_ELECTROLYZER']))
        header_list += ['capacity fuel chem plant (kW)']
        series_list.append(  case_list_dic['CAPACITY_FUEL_CHEM_PLANT'])
        print(' --- capacity fuel chem plant (kW) {}'.format(result_dic['CAPACITY_FUEL_CHEM_PLANT']))
        header_list += ['capacity fuel power (kW)']
        series_list.append(  case_list_dic['CAPACITY_FUEL_POWER'])
        print(' --- capacity fuel power (kW) {}'.format(result_dic['CAPACITY_FUEL_POWER']))
        header_list += ['capacity fuel h2 storage (kWh)']
        series_list.append(  case_list_dic['CAPACITY_FUEL_H2_STORAGE'])
        print(' --- capacity fuel h2 storage (kWh) {}'.format(result_dic['CAPACITY_FUEL_H2_STORAGE']))
    
        header_list += ['dispatch to fuel h2 storage (kW)']
        series_list.append( case_list_dic['DISPATCH_TO_FUEL_H2_STORAGE'])
        f_len = len(result_dic['DISPATCH_TO_FUEL_H2_STORAGE'].flatten())
        f_sum = sum(result_dic['DISPATCH_TO_FUEL_H2_STORAGE'].flatten())
        print(' --- dispatch to fuel (kW) {} from n entries {} = {} / hour'.format(f_sum, f_len, f_sum/f_len))

        header_list += ['dispatch from fuel h2 storage tot (kW)']
        series_list.append( case_list_dic['DISPATCH_FROM_FUEL_H2_STORAGE_TOT'])
        f_len = len(result_dic['DISPATCH_FROM_FUEL_H2_STORAGE_TOT'].flatten())
        f_sum = sum(result_dic['DISPATCH_FROM_FUEL_H2_STORAGE_TOT'].flatten())
        print(' --- dispatch from fuel (kW) {} from n entries {} = {} / hour'.format(f_sum, f_len, f_sum/f_len))
        header_list += ['dispatch from fuel h2 storage chem plant (kW)']
        series_list.append( case_list_dic['DISPATCH_FROM_FUEL_H2_STORAGE_CHEM'])
        header_list += ['dispatch from fuel h2 storage power (kW)']
        series_list.append( case_list_dic['DISPATCH_FROM_FUEL_H2_STORAGE_POWER'])

        if 'PRICE_FUEL' in result_dic.keys():
            header_list += ['fuel price ($/kWh)']
            series_list.append( [ result_dic['PRICE_FUEL'].flatten().item(0) ] )
            header_list += ['mean price ($/kWh)']
            series_list.append( [ np.mean(result_dic['PRICE'].flatten() * demand_series_vect) ] )
            print(" --- mean price ($/kWh) = {}".format(series_list[-1]))
            header_list += ['max price ($/kWh)']
            series_list.append( [ np.max(result_dic['PRICE'].flatten()) ] )
     

        header_list += ['fuel h2 storage (kWh)']
        series_list.append( case_list_dic['FUEL_H2_STORAGE'] )
    
    # Results: STORAGE
    if 'STORAGE' in components: 
        header_list += ['capacity storage (kWh)']
        series_list.append(  case_list_dic['CAPACITY_STORAGE'])
    
        header_list += ['energy storage (kWh)']
        series_list.append( case_list_dic['ENERGY_STORAGE'])
    
        header_list += ['dispatch to storage (kW)']
        series_list.append( case_list_dic['DISPATCH_TO_STORAGE'])
    
        header_list += ['dispatch from storage (kW)']
        series_list.append( case_list_dic['DISPATCH_FROM_STORAGE'])
    
    # Results: STORAGE2
    if 'STORAGE2' in components: 
        header_list += ['capacity storage2 (kWh)']
        series_list.append(  case_list_dic['CAPACITY_STORAGE2'])
    
        header_list += ['energy storage2 (kWh)']
        series_list.append( case_list_dic['ENERGY_STORAGE2'])
    
        header_list += ['dispatch to storage2 (kW)']
        series_list.append( case_list_dic['DISPATCH_TO_STORAGE2'])
    
        header_list += ['dispatch from storage2 (kW)']
        series_list.append( case_list_dic['DISPATCH_FROM_STORAGE2'])
   
    # Results: PGP STORAGE
    if 'PGP_STORAGE' in components: 
        header_list += ['capacity pgp storage (kW)']
        series_list.append(  case_list_dic['CAPACITY_PGP_STORAGE'])
       
        header_list += ['capacity to pgp storage (kW)']
        series_list.append(  case_list_dic['CAPACITY_TO_PGP_STORAGE'])
       
        header_list += ['capacity from pgp storage (kW)']
        series_list.append(  case_list_dic['CAPACITY_FROM_PGP_STORAGE'])
    
        header_list += ['energy pgp storage (kW)']
        series_list.append( case_list_dic['ENERGY_PGP_STORAGE'])
    
        header_list += ['dispatch to pgp storage (kW)']
        series_list.append( case_list_dic['DISPATCH_TO_PGP_STORAGE'])
    
        header_list += ['dispatch from pgp storage (kW)']
        series_list.append( case_list_dic['DISPATCH_FROM_PGP_STORAGE'])
   
    # Results: CSP
    if 'CSP' in components: 
        header_list += ['capacity csp (kW)']
        series_list.append( case_list_dic['CAPACITY_CSP'])
       
        header_list += ['capacity csp storage (kW)']
        series_list.append( case_list_dic['CAPACITY_CSP_STORAGE'])
    
        header_list += ['energy csp storage (kW)']
        series_list.append( case_list_dic['ENERGY_CSP_STORAGE'])
    
        header_list += ['dispatch to csp storage (kW)']
        series_list.append( case_list_dic['DISPATCH_TO_CSP_STORAGE'])
    
        header_list += ['dispatch from csp (kW)']
        series_list.append( case_list_dic['DISPATCH_FROM_CSP'])
    
        header_list += ['curtailment csp (kW)']
        series_list.append( case_list_dic['CURTAILMENT_CSP'])

    #Results: UNMET_DEMAND   
    if 'UNMET_DEMAND' in components: 
        header_list += ['dispatch unmet demand (kW)']
        series_list.append( case_list_dic['DISPATCH_UNMET_DEMAND'])

    #=========================================================================
    # set missing vector means to zero
    # I am not sure why I am doing this in such a bad way, but I could not get
    # better way to work
    for i in range(len(series_list)):
        if type(series_list[i][0]) != str:
            sl = np.array(series_list[i])
            sl[np.isnan(sl)] = 0
            series_list[i] = sl.tolist()
        
    
    output_array = np.array(series_list).T.tolist()
    output_array.insert(0,header_list)    
    output_array = np.array(output_array).T.tolist()
    
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
        writer.writerows(output_array)
        output_file.close()
        
    if verbose: 
        print ( 'file written: ' + output_file_name + '.csv')

