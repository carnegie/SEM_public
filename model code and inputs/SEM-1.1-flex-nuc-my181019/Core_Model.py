#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
NOTE: THIS VERSION OF THE MODEL NEEDS CVXPY-04.

File name: Core_Model.py

Simple Energy Model Ver 1

This is the heart of the Simple Energy Model. It reads in the case dictionary
that was created in Preprocess_Input.py, and then executes all of the cases.

Technology:
    Generation: natural gas, wind, solar, nuclear
    Energy storage: one generic (a pre-determined round-trip efficiency)
    Curtailment: Yes (free)
    Unmet demand: No
    
Optimization:
    Linear programming (LP)
    Energy balance constraints for the grid and the energy storage facility.

@author: Fan
Time
    Dec 1, 4-8, 11, 19, 22
    Jan 2-4, 24-27
    
'''

# -----------------------------------------------------------------------------



import cvxpy as cvx
import time
import datetime
import numpy as np

from Storage_Analysis import storage_analysis

from Save_Basic_Results import save_vector_results_as_csv
from Save_Basic_Results import pickle_raw_results

# Core function
#   Linear programming
#   Output postprocessing

# -----------------------------------------------------------------------------

def core_model_loop (global_dic, case_dic_list):
    verbose = global_dic['VERBOSE']
    if verbose:
        print ('Core_Model.py: Entering core model loop')
    num_cases = len(case_dic_list)
    
    for case_index in range(num_cases):

        if verbose:
            today = datetime.datetime.now()
            print ('solving ',case_dic_list[case_index]['CASE_NAME'],' time = ',today)
            
        result_dic = core_model (global_dic, case_dic_list[case_index])
                                           
        if verbose:
            today = datetime.datetime.now()
            print ('solved  ',case_dic_list[case_index]['CASE_NAME'],' time = ',today)
        
        # put raw results in file for later analysis
        if 'STORAGE' in case_dic_list[case_index]['SYSTEM_COMPONENTS']:
            sdic = storage_analysis(global_dic,case_dic_list[case_index],result_dic)
            for key in sdic.keys():
                result_dic[key] = sdic[key]
            
        if verbose:
            print ('writing out results for case ',case_dic_list[case_index]['CASE_NAME'])
            
        save_vector_results_as_csv( global_dic, case_dic_list[case_index], result_dic )
        pickle_raw_results( global_dic, case_dic_list[case_index], result_dic )
    return 

# -----------------------------------------------------------------------------

def core_model (global_dic, case_dic):
    verbose = global_dic['VERBOSE']
    numerics_cost_scaling = case_dic['NUMERICS_COST_SCALING']
    numerics_demand_scaling = case_dic['NUMERICS_DEMAND_SCALING']
    if verbose:
        print ('Core_Model.py: processing case ',case_dic['CASE_NAME'])
    demand_series = np.array(case_dic['DEMAND_SERIES'])*numerics_demand_scaling 
    solar_series = case_dic['SOLAR_SERIES'] # Assumed to be normalized per kW capacity
    wind_series = case_dic['WIND_SERIES'] # Assumed to be normalized per kW capacity

    
    # Fixed costs are assumed to be per time period (1 hour)
    fixed_cost_natgas = case_dic['FIXED_COST_NATGAS']*numerics_cost_scaling
    fixed_cost_solar = case_dic['FIXED_COST_SOLAR']*numerics_cost_scaling
    fixed_cost_wind = case_dic['FIXED_COST_WIND']*numerics_cost_scaling
    fixed_cost_nuclear = case_dic['FIXED_COST_NUCLEAR']*numerics_cost_scaling
    fixed_cost_storage = case_dic['FIXED_COST_STORAGE']*numerics_cost_scaling
    fixed_cost_pgp_storage = case_dic['FIXED_COST_PGP_STORAGE']*numerics_cost_scaling
    fixed_cost_to_pgp_storage = case_dic['FIXED_COST_TO_PGP_STORAGE']*numerics_cost_scaling
    fixed_cost_from_pgp_storage = case_dic['FIXED_COST_FROM_PGP_STORAGE']*numerics_cost_scaling

    # Variable costs are assumed to be kWh
    var_cost_natgas = case_dic['VAR_COST_NATGAS']*numerics_cost_scaling
    var_cost_solar = case_dic['VAR_COST_SOLAR']*numerics_cost_scaling
    var_cost_wind = case_dic['VAR_COST_WIND']*numerics_cost_scaling
    var_cost_nuclear = case_dic['VAR_COST_NUCLEAR']*numerics_cost_scaling
    var_cost_unmet_demand = case_dic['VAR_COST_UNMET_DEMAND']*numerics_cost_scaling
    var_cost_to_storage = case_dic['VAR_COST_TO_STORAGE']*numerics_cost_scaling
    var_cost_from_storage = case_dic['VAR_COST_FROM_STORAGE']*numerics_cost_scaling
    var_cost_to_pgp_storage = case_dic['VAR_COST_TO_PGP_STORAGE']*numerics_cost_scaling #to pgp storage
    var_cost_from_pgp_storage = case_dic['VAR_COST_FROM_PGP_STORAGE']*numerics_cost_scaling  # from pgp storage

    
    storage_charging_efficiency = case_dic['STORAGE_CHARGING_EFFICIENCY']
    storage_charging_time       = case_dic['STORAGE_CHARGING_TIME']
    storage_decay_rate          = case_dic['STORAGE_DECAY_RATE'] # fraction of stored electricity lost each hour
    pgp_storage_charging_efficiency = case_dic['PGP_STORAGE_CHARGING_EFFICIENCY']
    pgp_storage_decay_rate = case_dic['PGP_STORAGE_DECAY_RATE']
    
    system_components = case_dic['SYSTEM_COMPONENTS']
      
    num_time_periods = len(demand_series)
    
    #    discount_rate = 1.07**(1/(365.24*24))
    #    discount_vector = discount_rate**-np.arange(num_time_periods)

    # -------------------------------------------------------------------------
        
    #%% Construct the Problem
    
    # -----------------------------------------------------------------------------
    ## Define Variables
    
    # Number of generation technologies = fixed_cost_Power.size
    # Number of time steps/units in a given time duration = num_time_periods
    #       num_time_periods returns an integer value
    
    # Capacity_Power = Installed power capacities for all generation technologies = [kW]
    # dispatch_Power = Power generation at each time step for each generator = [kWh]
    
    # dispatch_Curtailment = Curtailed renewable energy generation at each time step = [kWh]
    #   This is more like a dummy variable
    
    # Capacity_Storage = Deployed size of energy storage = [kWh]
    # energy_storage = State of charge for the energy storage = [kWh]
    # DISPATCH_FROM_STORAGE_Charge = Charging energy flow for energy storage (grid -> storage) = [kW]
    # DISPATCH_FROM_STORAGE_dispatch = Discharging energy flow for energy storage (grid <- storage) = [kW]
    
    # UnmetDemand = unmet demand/load = [kWh]
    
    start_time = time.time()    # timer starts
    
    fcn2min = 0
    constraints = []

#---------------------- natural gas ------------------------------------------    
    if 'NATGAS' in system_components:
        capacity_natgas = cvx.Variable(1)
        dispatch_natgas = cvx.Variable(num_time_periods)
        constraints += [
                capacity_natgas >= 0,
                dispatch_natgas >= 0,
                dispatch_natgas <= capacity_natgas
                ]
        fcn2min += capacity_natgas * fixed_cost_natgas + cvx.sum(dispatch_natgas * var_cost_natgas)/num_time_periods
    else:
        capacity_natgas = 0
        dispatch_natgas = np.zeros(num_time_periods)
        
#---------------------- solar ------------------------------------------    
    if 'SOLAR' in system_components:
        capacity_solar = cvx.Variable(1)
        dispatch_solar = cvx.Variable(num_time_periods)
        constraints += [
                capacity_solar >= 0,
                dispatch_solar >= 0, 
                dispatch_solar <= capacity_solar * solar_series 
                ]
        fcn2min += capacity_solar * fixed_cost_solar + cvx.sum(dispatch_solar * var_cost_solar)/num_time_periods
    else:
        capacity_solar = 0
        dispatch_solar = np.zeros(num_time_periods)
        
#---------------------- wind ------------------------------------------    
    if 'WIND' in system_components:
        capacity_wind = cvx.Variable(1)
        dispatch_wind = cvx.Variable(num_time_periods)
        constraints += [
                capacity_wind >= 0,
                dispatch_wind >= 0, 
                dispatch_wind <= capacity_wind * wind_series 
                ]
        fcn2min += capacity_wind * fixed_cost_wind + cvx.sum(dispatch_wind * var_cost_wind)/num_time_periods
    else:
        capacity_wind = 0
        dispatch_wind = np.zeros(num_time_periods)
        
#---------------------- nuclear ------------------------------------------    
    if 'NUCLEAR' in system_components:
        capacity_nuclear = cvx.Variable(1)
        dispatch_nuclear = cvx.Variable(num_time_periods)
        constraints += [
                capacity_nuclear >= 0,
                dispatch_nuclear >= 0, 
                dispatch_nuclear <= capacity_nuclear 
                ]
        fcn2min += capacity_nuclear * fixed_cost_nuclear + cvx.sum(dispatch_nuclear * var_cost_nuclear)/num_time_periods
    else:
        capacity_nuclear = 0
        dispatch_nuclear = np.zeros(num_time_periods)
        
#---------------------- storage ------------------------------------------    
    if 'STORAGE' in system_components:
        capacity_storage = cvx.Variable(1)
        dispatch_to_storage = cvx.Variable(num_time_periods)
        dispatch_from_storage = cvx.Variable(num_time_periods)
        energy_storage = cvx.Variable(num_time_periods)
        constraints += [
                capacity_storage >= 0,
                dispatch_to_storage >= 0, 
                dispatch_to_storage <= capacity_storage / storage_charging_time,
                dispatch_from_storage >= 0, # dispatch_to_storage is negative value
                dispatch_from_storage <= capacity_storage / storage_charging_time,
                dispatch_from_storage <= energy_storage * (1 - storage_decay_rate), # you can't dispatch more from storage in a time step than is in the battery
                                                                                    # This constraint is redundant
                energy_storage >= 0,
                energy_storage <= capacity_storage
                ]

        fcn2min += capacity_storage * fixed_cost_storage +  \
            cvx.sum(dispatch_to_storage * var_cost_to_storage)/num_time_periods + \
            cvx.sum(dispatch_from_storage * var_cost_from_storage)/num_time_periods 
 
        for i in range(num_time_periods):

            constraints += [
                    energy_storage[(i+1) % num_time_periods] == 
                        energy_storage[i] + storage_charging_efficiency * dispatch_to_storage[i] 
                        - dispatch_from_storage[i] - energy_storage[i]*storage_decay_rate
                    ]

    else:
        capacity_storage = 0
        dispatch_to_storage = np.zeros(num_time_periods)
        dispatch_from_storage = np.zeros(num_time_periods)
        energy_storage = np.zeros(num_time_periods)
       
#---------------------- PGP storage (power to gas to power) -------------------  
# For PGP storage, there are three capacity decisions:
#   1.  to_storage (power):capacity_to_pgp_storage
#   2.  storage (energy):  capacity_pgp_storage
#   3.  from_storage (power):  capacity_from_pgp_storage
#
# For PGP storage, there are two deispatch decisions each time period:
#   1. dispatch to storage (power)
#   2. dispatch from storage (power)
#
    if 'PGP_STORAGE' in system_components:
        capacity_pgp_storage = cvx.Variable(1)  # energy storage capacity in kWh (i.e., tank size)
        capacity_to_pgp_storage = cvx.Variable(1) # maximum power input / output (in kW) fuel cell / electrolyzer size
        capacity_from_pgp_storage = cvx.Variable(1) # maximum power input / output (in kW) fuel cell / electrolyzer size
        dispatch_to_pgp_storage = cvx.Variable(num_time_periods)
        dispatch_from_pgp_storage = cvx.Variable(num_time_periods)  # this is dispatch FROM storage
        energy_pgp_storage = cvx.Variable(num_time_periods) # amount of energy currently stored in tank
        constraints += [
                capacity_pgp_storage >= 0,  # energy
                capacity_to_pgp_storage >= 0,  # power in
                capacity_from_pgp_storage >= 0,  # power out
                dispatch_to_pgp_storage >= 0, 
                dispatch_to_pgp_storage <= capacity_to_pgp_storage,
                dispatch_from_pgp_storage >= 0, # dispatch_to_storage is negative value
                dispatch_from_pgp_storage <= capacity_from_pgp_storage,
                dispatch_from_pgp_storage <= energy_pgp_storage * (1 - pgp_storage_decay_rate), # you can't dispatch more from storage in a time step than is in the battery
                                                                                    # This constraint is redundant
                energy_pgp_storage >= 0,
                energy_pgp_storage <= capacity_pgp_storage
                ]

        fcn2min += capacity_pgp_storage * fixed_cost_pgp_storage + \
            capacity_to_pgp_storage * fixed_cost_to_pgp_storage + capacity_from_pgp_storage * fixed_cost_from_pgp_storage + \
            cvx.sum(dispatch_to_pgp_storage * var_cost_to_pgp_storage)/num_time_periods + \
            cvx.sum(dispatch_from_pgp_storage * var_cost_from_pgp_storage)/num_time_periods 
 
        for i in range(num_time_periods):

            constraints += [
                    energy_pgp_storage[(i+1) % num_time_periods] == energy_pgp_storage[i] 
                    + pgp_storage_charging_efficiency * dispatch_to_pgp_storage[i] 
                    - dispatch_from_pgp_storage[i]- energy_pgp_storage[i]*pgp_storage_decay_rate
                    ]

    else:
        capacity_pgp_storage = 0  # energy storage capacity in kWh (i.e., tank size)
        capacity_to_pgp_storage = 0 # maximum power input / output (in kW) fuel cell / electrolyzer size
        capacity_from_pgp_storage = 0 # maximum power input / output (in kW) fuel cell / electrolyzer size
        dispatch_to_pgp_storage = np.zeros(num_time_periods)
        dispatch_from_pgp_storage = np.zeros(num_time_periods)
        energy_pgp_storage = np.zeros(num_time_periods) # amount of energy currently stored in tank

#---------------------- unmet demand ------------------------------------------    
    if 'UNMET_DEMAND' in system_components:
        dispatch_unmet_demand = cvx.Variable(num_time_periods)
        constraints += [
                dispatch_unmet_demand >= 0
                ]
        fcn2min += cvx.sum(dispatch_unmet_demand * var_cost_unmet_demand)/num_time_periods
    else:
        dispatch_unmet_demand = np.zeros(num_time_periods)
        
  
#---------------------- dispatch energy balance constraint ------------------------------------------    
    constraints += [
            dispatch_natgas + dispatch_solar + dispatch_wind + dispatch_nuclear + dispatch_from_storage + dispatch_from_pgp_storage + dispatch_unmet_demand  == 
                demand_series + dispatch_to_storage + dispatch_to_pgp_storage
            ]    
    
    # -----------------------------------------------------------------------------
    obj = cvx.Minimize(fcn2min)
    
    # -----------------------------------------------------------------------------
    # Problem solving
    
    # print cvx.installed_solvers()
    # print >>orig_stdout, cvx.installed_solvers()
    #print (constraints)
    #print (fcn2min)
    #print (system_components)
    
    # Form and Solve the Problem
    prob = cvx.Problem(obj, constraints)
#    prob.solve(solver = 'GUROBI')
    #prob.solve(solver = 'GUROBI',BarConvTol = 1e-11, feasibilityTol = 1e-6, NumericFocus = 3)
    prob.solve(solver = 'GUROBI')
#    prob.solve(solver = 'GUROBI',BarConvTol = 1e-11, feasibilityTol = 1e-9)
#    prob.solve(solver = 'GUROBI',BarConvTol = 1e-10, feasibilityTol = 1e-8)
#    prob.solve(solver = 'GUROBI',BarConvTol = 1e-8, FeasibilityTol = 1e-6)

    end_time = time.time()  # timer ends
   
    if verbose:
        print ('system cost ',prob.value/(numerics_cost_scaling * numerics_demand_scaling))
        print ('runtime: ', (end_time - start_time), 'seconds')

    #--------------- curtailment ----------------------------------------------
    curtailment_wind = np.zeros(num_time_periods)
    curtailment_solar = np.zeros(num_time_periods)
    curtailment_nuclear = np.zeros(num_time_periods)
    if 'WIND' in system_components :
        curtailment_wind = capacity_wind.value.flatten() * wind_series - dispatch_wind.value.flatten()
    if 'SOLAR' in system_components:
        curtailment_solar = capacity_solar.value.flatten() * solar_series - dispatch_solar.value.flatten()
#    if 'NUCLEAR' in system_components:
#        curtailment_nuclear = capacity_nuclear.value.flatten() - dispatch_nuclear.value.flatten()   
      
    # -----------------------------------------------------------------------------

    
    result={
            'SYSTEM_COST':prob.value/(numerics_cost_scaling * numerics_demand_scaling),
            'PROBLEM_STATUS':prob.status
            }
    
    result['PRICE'] = np.array(-1.0 * num_time_periods * constraints[-1].dual_value/ numerics_cost_scaling).flatten()
    # note that hourly pricing can be determined from the dual of the constraint on energy balance
    # The num_time_periods is in the above because the influence on the cost of an hour is much bigger then
    # the impact of average cost over the period. The divide by the cost scaling corrects for the cost scaling.
    
    
    if 'NATGAS' in system_components:
        result['CAPACITY_NATGAS'] = np.asscalar(capacity_natgas.value)/numerics_demand_scaling
        result['DISPATCH_NATGAS'] = np.array(dispatch_natgas.value).flatten()/numerics_demand_scaling
    else:
        result['CAPACITY_NATGAS'] = capacity_natgas/numerics_demand_scaling
        result['DISPATCH_NATGAS'] = dispatch_natgas/numerics_demand_scaling

    if 'SOLAR' in system_components:
        result['CAPACITY_SOLAR'] = np.asscalar(capacity_solar.value)/numerics_demand_scaling
        result['DISPATCH_SOLAR'] = np.array(dispatch_solar.value).flatten()/numerics_demand_scaling
        result['CURTAILMENT_SOLAR'] = np.array(curtailment_solar.flatten()) / numerics_demand_scaling
    else:
        result['CAPACITY_SOLAR'] = capacity_solar/numerics_demand_scaling
        result['DISPATCH_SOLAR'] = dispatch_solar/numerics_demand_scaling
        result['CURTAILMENT_SOLAR'] = curtailment_solar / numerics_demand_scaling

    if 'WIND' in system_components:
        result['CAPACITY_WIND'] = np.asscalar(capacity_wind.value)/numerics_demand_scaling
        result['DISPATCH_WIND'] = np.array(dispatch_wind.value).flatten()/numerics_demand_scaling
        result['CURTAILMENT_WIND'] = np.array(curtailment_wind.flatten()) / numerics_demand_scaling
    else:
        result['CAPACITY_WIND'] = capacity_wind/numerics_demand_scaling
        result['DISPATCH_WIND'] = dispatch_wind/numerics_demand_scaling
        result['CURTAILMENT_WIND'] = curtailment_wind / numerics_demand_scaling

    if 'NUCLEAR' in system_components:
        result['CAPACITY_NUCLEAR'] = np.asscalar(capacity_nuclear.value)/numerics_demand_scaling
        result['DISPATCH_NUCLEAR'] = np.array(dispatch_nuclear.value).flatten()/numerics_demand_scaling
        result['CURTAILMENT_NUCLEAR'] = np.array(curtailment_nuclear.flatten()) / numerics_demand_scaling
    else:
        result['CAPACITY_NUCLEAR'] = capacity_nuclear/numerics_demand_scaling
        result['DISPATCH_NUCLEAR'] = dispatch_nuclear/numerics_demand_scaling
        result['CURTAILMENT_NUCLEAR'] = curtailment_nuclear / numerics_demand_scaling

    if 'STORAGE' in system_components:
        result['CAPACITY_STORAGE'] = np.asscalar(capacity_storage.value)/numerics_demand_scaling
        result['DISPATCH_TO_STORAGE'] = np.array(dispatch_to_storage.value).flatten()/numerics_demand_scaling
        result['DISPATCH_FROM_STORAGE'] = np.array(dispatch_from_storage.value).flatten()/numerics_demand_scaling
        result['ENERGY_STORAGE'] = np.array(energy_storage.value).flatten()/numerics_demand_scaling
    else:
        result['CAPACITY_STORAGE'] = capacity_storage/numerics_demand_scaling
        result['DISPATCH_TO_STORAGE'] = dispatch_to_storage/numerics_demand_scaling
        result['DISPATCH_FROM_STORAGE'] = dispatch_from_storage/numerics_demand_scaling
        result['ENERGY_STORAGE'] = energy_storage/numerics_demand_scaling
        
    if 'PGP_STORAGE' in system_components:
        result['CAPACITY_PGP_STORAGE'] = np.asscalar(capacity_pgp_storage.value)/numerics_demand_scaling
        result['CAPACITY_TO_PGP_STORAGE'] = np.asscalar(capacity_to_pgp_storage.value)/numerics_demand_scaling
        result['CAPACITY_FROM_PGP_STORAGE'] = np.asscalar(capacity_from_pgp_storage.value)/numerics_demand_scaling
        result['DISPATCH_TO_PGP_STORAGE'] = np.array(dispatch_to_pgp_storage.value).flatten()/numerics_demand_scaling
        result['DISPATCH_FROM_PGP_STORAGE'] = np.array(dispatch_from_pgp_storage.value).flatten()/numerics_demand_scaling
        result['ENERGY_PGP_STORAGE'] = np.array(energy_pgp_storage.value).flatten()/numerics_demand_scaling
    else:
        result['CAPACITY_PGP_STORAGE'] = capacity_pgp_storage/numerics_demand_scaling
        result['CAPACITY_TO_PGP_STORAGE'] = capacity_to_pgp_storage/numerics_demand_scaling
        result['CAPACITY_FROM_PGP_STORAGE'] = capacity_from_pgp_storage/numerics_demand_scaling
        result['DISPATCH_TO_PGP_STORAGE'] = dispatch_to_pgp_storage/numerics_demand_scaling
        result['DISPATCH_FROM_PGP_STORAGE'] = dispatch_from_pgp_storage/numerics_demand_scaling
        result['ENERGY_PGP_STORAGE'] = energy_pgp_storage/numerics_demand_scaling
        
    if 'UNMET_DEMAND' in system_components:
        result['DISPATCH_UNMET_DEMAND'] = np.array(dispatch_unmet_demand.value).flatten()/numerics_demand_scaling
    else:
        result['DISPATCH_UNMET_DEMAND'] = dispatch_unmet_demand/numerics_demand_scaling     

    return result
  