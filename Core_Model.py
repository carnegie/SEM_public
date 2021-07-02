#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''

NOTE: THIS VERSION OF THE MODEL NEEDS CVXPY-04.

File name: Core_Model.py

Simple Energy Model Ver 1

This is the heart of the Simple Energy Model. It reads in the case dictionary
that was created in Preprocess_Input.py, and then executes all of the cases.

Technology:
    Generation: natural gas, wind, solar, nuclear, wind2, solar2, solar_csp
    Energy storage: one generic (a pre-determined round-trip efficiency)
                    plus PGP,
    Curtailment: Yes (free)
    Unmet demand: No

Optimization:
    Linear programming (LP)
    Energy balance constraints for the grid and the energy storage facility.

Time
    Dec 1, 4-8, 11, 19, 22
    Jan 2-4, 24-27

'''

# -----------------------------------------------------------------------------



import cvxpy as cvx
import time
import datetime
import numpy as np

from Storage_Analysis import storage_analysis, no_storage_analysis

from Save_Basic_Results import save_vector_results_as_csv
from Save_Basic_Results import pickle_raw_results

# Core function
#   Linear programming
#   Output postprocessing

# -----------------------------------------------------------------------------

def core_model_loop (global_dic, case_dic_list):
    verbose = global_dic['VERBOSE']
    num_cases = len(case_dic_list)

    for case_index in range(num_cases):

        if verbose:
            today = datetime.datetime.now()
            print('---')
            print ('solving ',case_dic_list[case_index]['CASE_NAME'],' time = ',today)

        result_dic = core_model (global_dic, case_dic_list[case_index])

        if result_dic['PROBLEM_STATUS'] != 'optimal':

#            if verbose:
#                today = datetime.datetime.now()
#                print ('solved  ',case_dic_list[case_index]['CASE_NAME'],' time = ',today)

            # put raw results in file for later analysis
            # NOTE: THIS NEEDS TO BE FIXED UP FOR STORAGE2
            # =============================================================================
            #             if 'STORAGE' in case_dic_list[case_index]['SYSTEM_COMPONENTS']:
            #                 sdic = storage_analysis(global_dic,case_dic_list[case_index],result_dic)
            #             else:
            #                 sdic = no_storage_analysis()
            #                 for key in sdic.keys():
            #                     result_dic[key] = sdic[key]
            # 
            # 
            # =============================================================================
        # else:

            if verbose:
                today = datetime.datetime.now()
                print ('failed to solve  ',case_dic_list[case_index]['CASE_NAME'],' time = ',today)

        save_vector_results_as_csv( global_dic, case_dic_list[case_index], result_dic )
        pickle_raw_results( global_dic, case_dic_list[case_index], result_dic )

    if verbose:
        print('---')
    return

# -----------------------------------------------------------------------------

def core_model (global_dic, case_dic):
    verbose = global_dic['VERBOSE']
    numerics_cost_scaling = case_dic['NUMERICS_COST_SCALING']
    numerics_demand_scaling = case_dic['NUMERICS_DEMAND_SCALING']

    #if verbose:
    #    print ('Core_Model.py: processing case ',case_dic['CASE_NAME'])
    demand_series = np.array(case_dic['DEMAND_SERIES'])*numerics_demand_scaling
    solar_series = case_dic['SOLAR_SERIES'] # Assumed to be normalized per kW capacity
    wind_series = case_dic['WIND_SERIES'] # Assumed to be normalized per kW capacity
    solar2_series = case_dic['SOLAR2_SERIES'] # Assumed to be normalized per kW capacity
    wind2_series = case_dic['WIND2_SERIES'] # Assumed to be normalized per kW capacity
    csp_series = case_dic['CSP_SERIES'] # Assumed to be normalized per kW capacity


    # Fixed costs are assumed to be per time period (1 hour)
    fixed_cost_natgas = case_dic['FIXED_COST_NATGAS']*numerics_cost_scaling
    fixed_cost_natgas_ccs = case_dic['FIXED_COST_NATGAS_CCS']*numerics_cost_scaling
    fixed_cost_solar = case_dic['FIXED_COST_SOLAR']*numerics_cost_scaling
    fixed_cost_wind = case_dic['FIXED_COST_WIND']*numerics_cost_scaling
    fixed_cost_solar2 = case_dic['FIXED_COST_SOLAR2']*numerics_cost_scaling
    fixed_cost_wind2 = case_dic['FIXED_COST_WIND2']*numerics_cost_scaling
    fixed_cost_nuclear = case_dic['FIXED_COST_NUCLEAR']*numerics_cost_scaling
    fixed_cost_fuel_electrolyzer = case_dic['FIXED_COST_FUEL_ELECTROLYZER']*numerics_cost_scaling
    fixed_cost_fuel_chem_plant = case_dic['FIXED_COST_FUEL_CHEM_PLANT']*numerics_cost_scaling
    fixed_cost_fuel_power = case_dic['FIXED_COST_FUEL_POWER']*numerics_cost_scaling
    fixed_cost_fuel_h2_storage = case_dic['FIXED_COST_FUEL_H2_STORAGE']*numerics_cost_scaling
    fixed_cost_storage = case_dic['FIXED_COST_STORAGE']*numerics_cost_scaling
    fixed_cost_storage2 = case_dic['FIXED_COST_STORAGE2']*numerics_cost_scaling
    fixed_cost_pgp_storage = case_dic['FIXED_COST_PGP_STORAGE']*numerics_cost_scaling
    fixed_cost_to_pgp_storage = case_dic['FIXED_COST_TO_PGP_STORAGE']*numerics_cost_scaling
    fixed_cost_from_pgp_storage = case_dic['FIXED_COST_FROM_PGP_STORAGE']*numerics_cost_scaling
    fixed_cost_csp = case_dic['FIXED_COST_CSP']*numerics_cost_scaling
    fixed_cost_csp_storage = case_dic['FIXED_COST_CSP_STORAGE']*numerics_cost_scaling

    # Variable costs are assumed to be kWh
    var_cost_natgas = case_dic['VAR_COST_NATGAS']*numerics_cost_scaling
    var_cost_natgas_ccs = case_dic['VAR_COST_NATGAS_CCS']*numerics_cost_scaling
    var_cost_solar = case_dic['VAR_COST_SOLAR']*numerics_cost_scaling
    var_cost_wind = case_dic['VAR_COST_WIND']*numerics_cost_scaling
    var_cost_solar2 = case_dic['VAR_COST_SOLAR2']*numerics_cost_scaling
    var_cost_wind2 = case_dic['VAR_COST_WIND2']*numerics_cost_scaling
    var_cost_nuclear = case_dic['VAR_COST_NUCLEAR']*numerics_cost_scaling
    var_cost_fuel_electrolyzer = case_dic['VAR_COST_FUEL_ELECTROLYZER']*numerics_cost_scaling
    var_cost_fuel_chem_plant = case_dic['VAR_COST_FUEL_CHEM_PLANT']*numerics_cost_scaling
    var_cost_fuel_co2 = case_dic['VAR_COST_FUEL_CO2']*numerics_cost_scaling
    var_cost_unmet_demand = case_dic['VAR_COST_UNMET_DEMAND']*numerics_cost_scaling
    var_cost_to_storage = case_dic['VAR_COST_TO_STORAGE']*numerics_cost_scaling
    var_cost_from_storage = case_dic['VAR_COST_FROM_STORAGE']*numerics_cost_scaling
    var_cost_to_storage2 = case_dic['VAR_COST_TO_STORAGE2']*numerics_cost_scaling
    var_cost_from_storage2 = case_dic['VAR_COST_FROM_STORAGE2']*numerics_cost_scaling
    var_cost_to_pgp_storage = case_dic['VAR_COST_TO_PGP_STORAGE']*numerics_cost_scaling #to pgp storage
    var_cost_from_pgp_storage = case_dic['VAR_COST_FROM_PGP_STORAGE']*numerics_cost_scaling  # from pgp storage
    var_cost_csp = case_dic['VAR_COST_CSP']*numerics_cost_scaling
    var_cost_csp_storage = case_dic['VAR_COST_CSP_STORAGE']*numerics_cost_scaling

    efficiency_fuel_electrolyzer = case_dic['EFFICIENCY_FUEL_ELECTROLYZER']
    efficiency_fuel_chem_conversion = case_dic['EFFICIENCY_FUEL_CHEM_CONVERSION']
    efficiency_fuel_power_conversion = case_dic['EFFICIENCY_FUEL_POWER_CONVERSION']
    decay_rate_fuel_h2_storage = case_dic['DECAY_RATE_FUEL_H2_STORAGE']
    fuel_value = case_dic['FUEL_VALUE']*numerics_cost_scaling
    fuel_demand = case_dic['FUEL_DEMAND']*numerics_demand_scaling

    charging_efficiency_storage = case_dic['CHARGING_EFFICIENCY_STORAGE']
    charging_time_storage       = case_dic['CHARGING_TIME_STORAGE']
    decay_rate_storage          = case_dic['DECAY_RATE_STORAGE'] # fraction of stored electricity lost each hour
    
    charging_efficiency_storage2 = case_dic['CHARGING_EFFICIENCY_STORAGE2']
    charging_time_storage2       = case_dic['CHARGING_TIME_STORAGE2']
    decay_rate_storage2          = case_dic['DECAY_RATE_STORAGE2'] # fraction of stored electricity lost each hour
    
    charging_efficiency_pgp_storage = case_dic['CHARGING_EFFICIENCY_PGP_STORAGE']
    decay_rate_pgp_storage = case_dic['DECAY_RATE_PGP_STORAGE']
    
    charging_efficiency_csp_storage = case_dic['CHARGING_EFFICIENCY_CSP_STORAGE']
    decay_rate_csp_storage = case_dic['DECAY_RATE_CSP_STORAGE']

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

    max_demand = np.max(demand_series)
    fcn2min = 0
    constraints = []

#%%-------------------- natural gas ------------------------------------------
    if 'NATGAS' in system_components:
        if(case_dic['CAPACITY_NATGAS']<0):
            capacity_natgas = cvx.Variable(1) # calculate natgas capacity
            constraints += [
                capacity_natgas >= 0]
                #capacity_natgas <= max_demand]
        else:
            capacity_natgas = case_dic['CAPACITY_NATGAS'] * numerics_demand_scaling

        dispatch_natgas = cvx.Variable(num_time_periods)
        constraints += [
                dispatch_natgas >= 0,
                dispatch_natgas <= capacity_natgas
                ]
        fcn2min += capacity_natgas * fixed_cost_natgas + cvx.sum(dispatch_natgas * var_cost_natgas)/num_time_periods
    else:
        capacity_natgas = 0
        dispatch_natgas = np.zeros(num_time_periods)

#%%-------------------- natural gas with CCS -----------------------------------
    if 'NATGAS_CCS' in system_components:
        if(case_dic['CAPACITY_NATGAS_CCS']<0):
            capacity_natgas_ccs = cvx.Variable(1) # calculate natgas capacity
            constraints += [
                capacity_natgas_ccs >= 0,
                #capacity_natgas_ccs <= max_demand
                ]
        else:
            capacity_natgas_ccs = case_dic['CAPACITY_NATGAS_CCS'] * numerics_demand_scaling

        dispatch_natgas_ccs = cvx.Variable(num_time_periods)
        constraints += [
                dispatch_natgas_ccs >= 0,
                dispatch_natgas_ccs <= capacity_natgas_ccs
                ]
        fcn2min += capacity_natgas_ccs * fixed_cost_natgas_ccs + cvx.sum(dispatch_natgas_ccs * var_cost_natgas_ccs)/num_time_periods
    else:
        capacity_natgas_ccs = 0
        dispatch_natgas_ccs = np.zeros(num_time_periods)

#%%-------------------- solar ------------------------------------------
    if 'SOLAR' in system_components:
        if(case_dic['CAPACITY_SOLAR']<0):
            capacity_solar = cvx.Variable(1) # calculate SOLAR capacity
            constraints += [
                capacity_solar >= 0]
        else:
            capacity_solar = case_dic['CAPACITY_SOLAR'] * numerics_demand_scaling

        dispatch_solar = cvx.Variable(num_time_periods)
        constraints += [
                dispatch_solar >= 0,
                dispatch_solar <= capacity_solar * solar_series
                ]
        fcn2min += capacity_solar * fixed_cost_solar + cvx.sum(dispatch_solar * var_cost_solar)/num_time_periods
    else:
        capacity_solar = 0
        dispatch_solar = np.zeros(num_time_periods)

#%%-------------------- wind ------------------------------------------
    if 'WIND' in system_components:
        if(case_dic['CAPACITY_WIND']<0):
            capacity_wind = cvx.Variable(1) # calculate wind capacity
            constraints += [
                capacity_wind >= 0]
        else:
            capacity_wind = case_dic['CAPACITY_WIND'] * numerics_demand_scaling

        dispatch_wind = cvx.Variable(num_time_periods)
        constraints += [
                dispatch_wind >= 0,
                dispatch_wind <= capacity_wind * wind_series
                ]
        fcn2min += capacity_wind * fixed_cost_wind + cvx.sum(dispatch_wind * var_cost_wind)/num_time_periods
    else:
        capacity_wind = 0
        dispatch_wind = np.zeros(num_time_periods)


#%%-------------------- solar2 ------------------------------------------
    if 'SOLAR2' in system_components:
        if(case_dic['CAPACITY_SOLAR2']<0):
            capacity_solar2 = cvx.Variable(1) # calculate SOLAR2 capacity
            constraints += [
                capacity_solar2 >= 0]
        else:
            capacity_solar2 = case_dic['CAPACITY_SOLAR2'] * numerics_demand_scaling

        dispatch_solar2 = cvx.Variable(num_time_periods)
        constraints += [
                dispatch_solar2 >= 0,
                dispatch_solar2 <= capacity_solar2 * solar2_series
                ]
        fcn2min += capacity_solar2 * fixed_cost_solar2 + cvx.sum(dispatch_solar2 * var_cost_solar2)/num_time_periods
    else:
        capacity_solar2 = 0
        dispatch_solar2 = np.zeros(num_time_periods)

#%%-------------------- wind2 ------------------------------------------
    if 'WIND2' in system_components:
        if(case_dic['CAPACITY_WIND2']<0):
            capacity_wind2 = cvx.Variable(1) # calculate SOLAR capacity
            constraints += [
                capacity_wind2 >= 0]
        else:
            capacity_wind2 = case_dic['CAPACITY_WIND2'] * numerics_demand_scaling

        dispatch_wind2 = cvx.Variable(num_time_periods)
        constraints += [
                dispatch_wind2 >= 0,
                dispatch_wind2 <= capacity_wind2 * wind2_series
                ]
        fcn2min += capacity_wind2 * fixed_cost_wind2 + cvx.sum(dispatch_wind2 * var_cost_wind2)/num_time_periods
    else:
        capacity_wind2 = 0
        dispatch_wind2 = np.zeros(num_time_periods)

#%%-------------------- nuclear ------------------------------------------
    if 'NUCLEAR' in system_components:
        if(case_dic['CAPACITY_NUCLEAR']<0):
            capacity_nuclear = cvx.Variable(1) # calculate SOLAR capacity
            constraints += [
                capacity_nuclear >= 0]
                #capacity_nuclear <= max_demand]
        else:
            capacity_nuclear = case_dic['CAPACITY_NUCLEAR'] * numerics_demand_scaling

        dispatch_nuclear = cvx.Variable(num_time_periods)
        constraints += [
                dispatch_nuclear >= 0,
                dispatch_nuclear <= capacity_nuclear
                ]
        fcn2min += capacity_nuclear * fixed_cost_nuclear + cvx.sum(dispatch_nuclear * var_cost_nuclear)/num_time_periods
    else:
        capacity_nuclear = 0
        dispatch_nuclear = np.zeros(num_time_periods)

#%%-------------------- liquid fuels ------------------------------------------
    idx_fuel_constraint = -1
    if 'FUEL' in system_components:
        # Three available capacities to optimize:
        # - water to H2 electrolyzer
        # - storage of H2
        # - chem plant for H2 + CO2 --> liquid hydrocarbons
        if(case_dic['CAPACITY_FUEL_ELECTROLYZER']<0):
            capacity_fuel_electrolyzer = cvx.Variable(1)
            constraints += [
                capacity_fuel_electrolyzer >= 0
                #capacity_fuel_electrolyzer <= 2000 * numerics_demand_scaling # prevent run away scenarios
                ]
        else:
            capacity_fuel_electrolyzer = case_dic['CAPACITY_FUEL_ELECTROLYZER'] * numerics_demand_scaling

        if(case_dic['CAPACITY_FUEL_CHEM_PLANT']<0):
            capacity_fuel_chem_plant = cvx.Variable(1)
            constraints += [
                capacity_fuel_chem_plant >= 0
                ]
        else:
            capacity_fuel_chem_plant = case_dic['CAPACITY_FUEL_CHEM_PLANT'] * numerics_demand_scaling

        # Can re-power the electricity system PGP-style
        if(case_dic['CAPACITY_FUEL_POWER']<0):
            capacity_fuel_power = cvx.Variable(1)
            constraints += [
                capacity_fuel_power >= 0
                ]
        else:
            capacity_fuel_power = case_dic['CAPACITY_FUEL_POWER'] * numerics_demand_scaling

        if(case_dic['CAPACITY_FUEL_H2_STORAGE']<0):
            capacity_fuel_h2_storage = cvx.Variable(1)
            constraints += [
                capacity_fuel_h2_storage >= 0
                ]
        else:
            capacity_fuel_h2_storage = case_dic['CAPACITY_FUEL_H2_STORAGE'] * numerics_demand_scaling

        dispatch_to_fuel_h2_storage = cvx.Variable(num_time_periods)
        dispatch_from_fuel_h2_storage_tot = cvx.Variable(num_time_periods)
        dispatch_from_fuel_h2_storage_chem = cvx.Variable(num_time_periods)
        dispatch_from_fuel_h2_storage_power = cvx.Variable(num_time_periods)
        fuel_h2_storage = cvx.Variable(num_time_periods)

        constraints += [
                dispatch_to_fuel_h2_storage >= 0,
                dispatch_to_fuel_h2_storage <= capacity_fuel_electrolyzer / efficiency_fuel_electrolyzer,
                dispatch_from_fuel_h2_storage_tot >= 0,
                dispatch_from_fuel_h2_storage_chem >= 0,
                dispatch_from_fuel_h2_storage_power >= 0,
                dispatch_from_fuel_h2_storage_tot == dispatch_from_fuel_h2_storage_chem + dispatch_from_fuel_h2_storage_power,
                dispatch_from_fuel_h2_storage_chem <= capacity_fuel_chem_plant / efficiency_fuel_chem_conversion,
                dispatch_from_fuel_h2_storage_power <= capacity_fuel_power / efficiency_fuel_power_conversion,
                fuel_h2_storage >= 0,
                fuel_h2_storage <= capacity_fuel_h2_storage 
                ]


        fcn2min += \
            capacity_fuel_electrolyzer * fixed_cost_fuel_electrolyzer +  \
            capacity_fuel_chem_plant * fixed_cost_fuel_chem_plant +  \
            capacity_fuel_power * fixed_cost_fuel_power +  \
            capacity_fuel_h2_storage * fixed_cost_fuel_h2_storage +  \
            cvx.sum(dispatch_to_fuel_h2_storage * efficiency_fuel_electrolyzer * var_cost_fuel_electrolyzer)/num_time_periods + \
            cvx.sum(dispatch_from_fuel_h2_storage_chem * efficiency_fuel_chem_conversion * (var_cost_fuel_chem_plant + var_cost_fuel_co2))/num_time_periods
            # Assume PGP like "capacity_fuel_power" has zero var cost

        # The following negative is from the cost function because we are "selling" it into the fuels market
        # at a fixed price
        if fuel_value > 0:
            fcn2min -= cvx.sum(dispatch_from_fuel_h2_storage_chem)/num_time_periods * efficiency_fuel_chem_conversion * fuel_value 

        if fuel_demand > 0:
            constraints += [
                    cvx.sum(dispatch_from_fuel_h2_storage_chem) * efficiency_fuel_chem_conversion / num_time_periods == fuel_demand
                ]

        idx_fuel_constraint = len(constraints)-1

        for i in range(num_time_periods):

            constraints += [
                    fuel_h2_storage[(i+1) % num_time_periods] == fuel_h2_storage[i]
                    + efficiency_fuel_electrolyzer * dispatch_to_fuel_h2_storage[i]
                    - dispatch_from_fuel_h2_storage_tot[i] - fuel_h2_storage[i]*decay_rate_fuel_h2_storage
                    ]

        #print ('done with FUEL')
        #print (constraints)
        #print (fcn2min)
    else:
        capacity_fuel_electrolyzer = 0
        capacity_fuel_chem_plant = 0
        capacity_fuel_power = 0
        capacity_fuel_h2_storage = 0
        dispatch_to_fuel_h2_storage = np.zeros(num_time_periods)
        dispatch_from_fuel_h2_storage_tot = np.zeros(num_time_periods)
        dispatch_from_fuel_h2_storage_chem = np.zeros(num_time_periods)
        dispatch_from_fuel_h2_storage_power = np.zeros(num_time_periods)
        fuel_h2_storage = np.zeros(num_time_periods)

#%%-------------------- storage ------------------------------------------
    if 'STORAGE' in system_components:
        if(case_dic['CAPACITY_STORAGE']<0):
            capacity_storage = cvx.Variable(1) # calculate SOLAR capacity
            constraints += [
                capacity_storage >= 0]
        else:
            capacity_storage = case_dic['CAPACITY_STORAGE'] * numerics_demand_scaling

        dispatch_to_storage = cvx.Variable(num_time_periods)
        dispatch_from_storage = cvx.Variable(num_time_periods)
        energy_storage = cvx.Variable(num_time_periods)
        constraints += [
                dispatch_to_storage >= 0,
                dispatch_to_storage <= capacity_storage / charging_time_storage,
                dispatch_from_storage >= 0, # dispatch_to_storage is negative value
                dispatch_from_storage <= capacity_storage / charging_time_storage,
                dispatch_from_storage <= energy_storage * (1 - decay_rate_storage), # you can't dispatch more from storage in a time step than is in the battery
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
                        energy_storage[i] + charging_efficiency_storage * dispatch_to_storage[i]
                        - dispatch_from_storage[i] - energy_storage[i]*decay_rate_storage
                    ]
        #print ('done with STORAGE')
        #print (constraints)
        #print (fcn2min)
    else:
        capacity_storage = 0
        dispatch_to_storage = np.zeros(num_time_periods)
        dispatch_from_storage = np.zeros(num_time_periods)
        energy_storage = np.zeros(num_time_periods)

#%%-------------------- storage ------------------------------------------
    if 'STORAGE2' in system_components:
        if(case_dic['CAPACITY_STORAGE2']<0):
            capacity_storage2 = cvx.Variable(1) # calculate SOLAR capacity
            constraints += [
                capacity_storage2 >= 0]
        else:
            capacity_storage2 = case_dic['CAPACITY_STORAGE2'] * numerics_demand_scaling

        dispatch_to_storage2 = cvx.Variable(num_time_periods)
        dispatch_from_storage2 = cvx.Variable(num_time_periods)
        energy_storage2 = cvx.Variable(num_time_periods)
        constraints += [
                dispatch_to_storage2 >= 0,
                dispatch_to_storage2 <= capacity_storage2 / charging_time_storage2,
                dispatch_from_storage2 >= 0, # dispatch_to_storage2 is negative value
                dispatch_from_storage2 <= capacity_storage2 / charging_time_storage2,
                dispatch_from_storage2 <= energy_storage2 * (1 - decay_rate_storage2), # you can't dispatch more from storage2 in a time step than is in the battery
                                                                                    # This constraint is redundant
                energy_storage2 >= 0,
                energy_storage2 <= capacity_storage2
                ]

        fcn2min += capacity_storage2 * fixed_cost_storage2 +  \
            cvx.sum(dispatch_to_storage2 * var_cost_to_storage2)/num_time_periods + \
            cvx.sum(dispatch_from_storage2 * var_cost_from_storage2)/num_time_periods

        #print ('done with STORAGE2')
        #print (constraints)
        #print (fcn2min)
        for i in range(num_time_periods):

            constraints += [
                    energy_storage2[(i+1) % num_time_periods] ==
                        energy_storage2[i] + charging_efficiency_storage2 * dispatch_to_storage2[i]
                        - dispatch_from_storage2[i] - energy_storage2[i]*decay_rate_storage2
                    ]

    else:
        capacity_storage2 = 0
        dispatch_to_storage2 = np.zeros(num_time_periods)
        dispatch_from_storage2 = np.zeros(num_time_periods)
        energy_storage2 = np.zeros(num_time_periods)

#%%-------------------- PGP storage (power to gas to power) -------------------
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
        if(case_dic['CAPACITY_PGP_STORAGE']<0):
            capacity_pgp_storage = cvx.Variable(1) # calculate pgp storage capacity
            constraints += [
                capacity_pgp_storage >= 0]
        else:
            capacity_pgp_storage = case_dic['CAPACITY_PGP_STORAGE'] * numerics_demand_scaling

        if(case_dic['CAPACITY_TO_PGP_STORAGE']<0):
            capacity_to_pgp_storage = cvx.Variable(1) # calculate pgp storage capacity
            constraints += [
                capacity_to_pgp_storage >= 0]
        else:
            capacity_to_pgp_storage = case_dic['CAPACITY_TO_PGP_STORAGE'] * numerics_demand_scaling

        if(case_dic['CAPACITY_FROM_PGP_STORAGE']<0):
            capacity_from_pgp_storage = cvx.Variable(1) # calculate pgp storage capacity
            constraints += [
                capacity_from_pgp_storage >= 0]
        else:
            capacity_from_pgp_storage = case_dic['CAPACITY_FROM_PGP_STORAGE'] * numerics_demand_scaling

        dispatch_to_pgp_storage = cvx.Variable(num_time_periods)
        dispatch_from_pgp_storage = cvx.Variable(num_time_periods)  # this is dispatch FROM storage
        energy_pgp_storage = cvx.Variable(num_time_periods) # amount of energy currently stored in tank
        constraints += [
                dispatch_to_pgp_storage >= 0,
                dispatch_to_pgp_storage <= capacity_to_pgp_storage,
                dispatch_from_pgp_storage >= 0, # dispatch_to_storage is negative value
                dispatch_from_pgp_storage <= capacity_from_pgp_storage,
                dispatch_from_pgp_storage <= energy_pgp_storage * (1 - decay_rate_pgp_storage), # you can't dispatch more from storage in a time step than is in the battery
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
                    + charging_efficiency_pgp_storage * dispatch_to_pgp_storage[i]
                    - dispatch_from_pgp_storage[i]- energy_pgp_storage[i]*decay_rate_pgp_storage
                    ]

    else:
        capacity_pgp_storage = 0  # energy storage capacity in kWh (i.e., tank size)
        capacity_to_pgp_storage = 0 # maximum power input / output (in kW) fuel cell / electrolyzer size
        capacity_from_pgp_storage = 0 # maximum power input / output (in kW) fuel cell / electrolyzer size
        dispatch_to_pgp_storage = np.zeros(num_time_periods)
        dispatch_from_pgp_storage = np.zeros(num_time_periods)
        energy_pgp_storage = np.zeros(num_time_periods) # amount of energy currently stored in tank

#%%S------------------- Concentrated solar power (CSP) -------------------  
# For CSP, the capacity components are:
#     1. CSP generator (capacity_csp)
#     2. Storage (capacity_csp_storage)
#
# For CSP, the dispatch components are:
#     1. CSP generator to grid (dispatch_csp)
#     2. CSP generator to storage (when dispatch demand met) (dispatch_csp_to_storage)
#     3. Storage to dispatch (when no/low generation) (DISPATCH_FROM_CSP)

    if 'CSP' in system_components:
        if(case_dic['CAPACITY_CSP']<0):
            capacity_csp = cvx.Variable(1) # calculate CSP capacity
            constraints += [
                capacity_csp >= 0]
        else:
            capacity_csp = case_dic['CAPACITY_CSP'] * numerics_demand_scaling
            
        if(case_dic['CAPACITY_CSP_STORAGE']<0):
            capacity_csp_storage = cvx.Variable(1) # calculate CSP storage capacity
            constraints += [
                capacity_csp_storage >= 0]
        else:
            capacity_csp_storage = case_dic['CAPACITY_CSP_STORAGE'] * numerics_demand_scaling
        
        dispatch_to_csp_storage = cvx.Variable(num_time_periods)
        dispatch_from_csp = cvx.Variable(num_time_periods)
        energy_csp_storage = cvx.Variable(num_time_periods) # amount of energy currently stored in CSP storage
        constraints += [
                dispatch_to_csp_storage >= 0, 
                dispatch_to_csp_storage <= capacity_csp * csp_series,  ######### might need to be changed to direct solar radiation??

                dispatch_from_csp >= 0,
                dispatch_from_csp <= energy_csp_storage * (1 - decay_rate_csp_storage) + \
                     charging_efficiency_storage * dispatch_to_csp_storage, 
                     # you can't dispatch more from storage in a time step than is
                     # in storage plus what you are adding now
                                                     
                energy_csp_storage >= 0,
                energy_csp_storage <= capacity_csp_storage
                ]
        
        fcn2min += capacity_csp * fixed_cost_csp + \
            capacity_csp_storage * fixed_cost_csp_storage +  \
            cvx.sum(dispatch_from_csp * var_cost_csp)/num_time_periods + \
            cvx.sum(energy_csp_storage * var_cost_csp_storage)/num_time_periods

        for i in range(num_time_periods):

            constraints += [
                    energy_csp_storage[(i+1) % num_time_periods] == 
                        energy_csp_storage[i]  \
                        + charging_efficiency_csp_storage * dispatch_to_csp_storage[i]  \
                        - dispatch_from_csp[i] \
                        - energy_csp_storage[i]*decay_rate_csp_storage
                    ]
    else:
        capacity_csp = 0
        capacity_csp_storage = 0
        dispatch_csp = np.zeros(num_time_periods)
        dispatch_to_csp_storage = np.zeros(num_time_periods)
        dispatch_from_csp = np.zeros(num_time_periods)
        energy_csp_storage = np.zeros(num_time_periods)
        
#%%------------------ unmet demand ------------------------------------------
    if 'UNMET_DEMAND' in system_components:
        dispatch_unmet_demand = cvx.Variable(num_time_periods)
        constraints += [
                dispatch_unmet_demand >= 0
                ]
        fcn2min += cvx.sum(dispatch_unmet_demand * var_cost_unmet_demand)/num_time_periods
    else:
        dispatch_unmet_demand = np.zeros(num_time_periods)
        
#%%------------------ unmet demand ------------------------------------------
    if case_dic['SYSTEM_RELIABILITY'] >= 0:
        sys_rel = case_dic['SYSTEM_RELIABILITY']
        constraints += [
                cvx.sum(dispatch_unmet_demand) ==  (1.-sys_rel)  * cvx.sum(demand_series)
                ]


#%%------------------- dispatch energy balance constraint ------------------------------------------
    constraints += [
            dispatch_natgas
            + dispatch_natgas_ccs
            + dispatch_solar
            + dispatch_wind
            + dispatch_solar2
            + dispatch_wind2
            + dispatch_nuclear
            + dispatch_from_storage
            + dispatch_from_storage2
            + dispatch_from_pgp_storage
            + dispatch_from_csp
            + dispatch_unmet_demand
            + dispatch_from_fuel_h2_storage_power * efficiency_fuel_power_conversion # dispatch_from_fuel_h2_storage_power is quantity of kWh leaving storage into fuel cell
            == demand_series + dispatch_to_storage + dispatch_to_storage2 + \
                    dispatch_to_pgp_storage + dispatch_to_fuel_h2_storage
            ]
    idx_energy_bal_constraint = len(constraints)-1
    
    # -----------------------------------------------------------------------------
    obj = cvx.Minimize(fcn2min)

    # -----------------------------------------------------------------------------
    # Problem solving

    # print cvx.installed_solvers()
    # print >>orig_stdout, cvx.installed_solvers()
    #print (constraints)
    #print (fcn2min)
    #print (system_components)
    #print (obj)
    # Form and Solve the Problem
    prob = cvx.Problem(obj, constraints)
#    prob.solve(solver = 'GUROBI')
    #prob.solve(solver = 'GUROBI',BarConvTol = 1e-11, feasibilityTol = 1e-6, NumericFocus = 3)

    try:

#       solver_parameter = {
#            'OutputFlag': 0,
#            }

      # Ask solvers to automatically output log files. The log file for Gurobi is "gurobi.log".
      #  prob.solve(solver = 'GUROBI', verbose = True)
        prob.solve(solver = 'GUROBI')
#    prob.solve(solver = 'GUROBI',BarConvTol = 1e-11, feasibilityTol = 1e-9)
#    prob.solve(solver = 'GUROBI',BarConvTol = 1e-10, feasibilityTol = 1e-8)
#    prob.solve(solver = 'GUROBI',BarConvTol = 1e-8, FeasibilityTol = 1e-6)

        if prob.status != 'solved' and prob.status != 'optimal':
            print(f'\n -- Initial GUROBI solve {prob.status}\n\n ---- Trying to solve again with NumericFocus = 3')
            prob.solve(solver = 'GUROBI', NumericFocus=3)
            if prob.status != 'solved' and prob.status != 'optimal':
                raise cvx.error.SolverError

        end_time = time.time()  # timer ends

    except cvx.error.SolverError as err:

        print('Solver error encounterd!', err)

        result = {
            'SYSTEM_COST': -1,
            'PROBLEM_STATUS':prob.status
            }

        result['CAPACITY_NATGAS'] = -1
        result['CAPACITY_NATGAS_CCS'] = -1
        result['CAPACITY_SOLAR'] = -1
        result['CAPACITY_WIND'] = -1
        result['CAPACITY_SOLAR2'] = -1
        result['CAPACITY_WIND2'] = -1
        result['CAPACITY_NUCLEAR'] = -1
        result['CAPACITY_FUEL_ELECTROLYZER'] = -1
        result['CAPACITY_FUEL_CHEM_PLANT'] = -1
        result['CAPACITY_FUEL_H2_STORAGE'] = -1
        result['CAPACITY_STORAGE'] = -1
        result['CAPACITY_STORAGE2'] = -1
        result['CAPACITY_PGP_STORAGE'] = -1
        result['CAPACITY_TO_PGP_STORAGE'] = -1
        result['CAPACITY_FROM_PGP_STORAGE'] = -1
        result['CAPACITY_CSP'] = -1
        result['CAPACITY_CSP_STORAGE'] = -1
        
        result['PRICE'] = -1 * np.ones(demand_series.size)
        result['PRICE_FUEL'] = -1 * np.ones(demand_series.size)
        
        result['DISPATCH_NATGAS'] = -1 * np.ones(demand_series.size)
        result['DISPATCH_NATGAS_CCS'] = -1 * np.ones(demand_series.size)
        result['DISPATCH_SOLAR'] = -1 * np.ones(demand_series.size)
        result['DISPATCH_WIND'] = -1 * np.ones(demand_series.size)
        result['DISPATCH_SOLAR2'] = -1 * np.ones(demand_series.size)
        result['DISPATCH_WIND2'] = -1 * np.ones(demand_series.size)
        result['DISPATCH_NUCLEAR'] = -1 * np.ones(demand_series.size)

        result['CURTAILMENT_SOLAR'] = -1 * np.ones(demand_series.size)
        result['CURTAILMENT_WIND'] = -1 * np.ones(demand_series.size)
        result['CURTAILMENT_SOLAR2'] = -1 * np.ones(demand_series.size)
        result['CURTAILMENT_WIND2'] = -1 * np.ones(demand_series.size)
        result['CURTAILMENT_CSP'] = -1 * np.ones(demand_series.size)
        result['CURTAILMENT_NUCLEAR'] = -1 * np.ones(demand_series.size)
 
        result['DISPATCH_TO_STORAGE'] = -1 * np.ones(demand_series.size)
        result['DISPATCH_FROM_STORAGE'] = -1 * np.ones(demand_series.size)
        result['ENERGY_STORAGE'] = -1 * np.ones(demand_series.size)
        
        result['DISPATCH_TO_STORAGE2'] = -1 * np.ones(demand_series.size)
        result['DISPATCH_FROM_STORAGE2'] = -1 * np.ones(demand_series.size)
        result['ENERGY_STORAGE2'] = -1 * np.ones(demand_series.size)
        
        result['DISPATCH_TO_PGP_STORAGE'] = -1 * np.ones(demand_series.size)
        result['DISPATCH_FROM_PGP_STORAGE'] = -1 * np.ones(demand_series.size)
        result['ENERGY_PGP_STORAGE'] = -1 * np.ones(demand_series.size)
        
        result['DISPATCH_CSP'] = -1 * np.ones(demand_series.size) 
        result['DISPATCH_TO_CSP_STORAGE'] = -1 * np.ones(demand_series.size)
        result['DISPATCH_FROM_CSP'] = -1 * np.ones(demand_series.size)
        result['ENERGY_CSP_STORAGE'] = -1 * np.ones(demand_series.size)

        result['DISPATCH_TO_FUEL_H2_STORAGE'] = -1 * np.ones(demand_series.size)
        result['DISPATCH_FROM_FUEL_H2_STORAGE_TOT'] = -1 * np.ones(demand_series.size)
        result['DISPATCH_FROM_FUEL_H2_STORAGE_CHEM'] = -1 * np.ones(demand_series.size)
        result['DISPATCH_FROM_FUEL_H2_STORAGE_POWER'] = -1 * np.ones(demand_series.size)
        result['FUEL_H2_STORAGE'] = -1 * np.ones(demand_series.size)
        
        result['DISPATCH_UNMET_DEMAND'] = -1 * np.ones(demand_series.size)

    else:

        if verbose:
            print ('system cost ',prob.value/(numerics_cost_scaling * numerics_demand_scaling),
                ' runtime: ', (end_time - start_time), 'seconds')

        # -----------------------------------------------------------------------------


        result={
                'SYSTEM_COST':prob.value/(numerics_cost_scaling * numerics_demand_scaling),
                'PROBLEM_STATUS':prob.status
                }

        try:
            result['PRICE'] = np.array(-1.0 * num_time_periods * constraints[idx_energy_bal_constraint].dual_value/ numerics_cost_scaling).flatten()
            # note that hourly pricing can be determined from the dual of the constraint on energy balance
            # The num_time_periods is in the above because the influence on the cost of an hour is much bigger then
            # the impact of average cost over the period. The divide by the cost scaling corrects for the cost scaling.
        except:
            result['PRICE']=np.zeros(num_time_periods)

        # Only check fuel dual if fuel was added
        if idx_fuel_constraint != -1:
            try:
                result['PRICE_FUEL'] = np.array(-1.0 * np.ones(num_time_periods) * constraints[idx_fuel_constraint].dual_value/ numerics_cost_scaling).flatten()
                # note that hourly pricing can be determined from the dual of the constraint on energy balance
                # The num_time_periods is in the above because the influence on the cost of an hour is much bigger then
                # the impact of average cost over the period. The divide by the cost scaling corrects for the cost scaling.
            except:
                result['PRICE_FUEL']=np.zeros(num_time_periods)

        if 'NATGAS' in system_components:
            if case_dic['CAPACITY_NATGAS'] < 0:
                result['CAPACITY_NATGAS'] = np.asscalar(capacity_natgas.value)/numerics_demand_scaling
            else:
                result['CAPACITY_NATGAS'] = case_dic['CAPACITY_NATGAS']
            result['DISPATCH_NATGAS'] = np.array(dispatch_natgas.value).flatten()/numerics_demand_scaling
        else:
            result['CAPACITY_NATGAS'] = capacity_natgas/numerics_demand_scaling
            result['DISPATCH_NATGAS'] = dispatch_natgas/numerics_demand_scaling

        if 'NATGAS_CCS' in system_components:
            if case_dic['CAPACITY_NATGAS_CCS'] < 0:
                result['CAPACITY_NATGAS_CCS'] = np.asscalar(capacity_natgas_ccs.value)/numerics_demand_scaling
            else:
                result['CAPACITY_NATGAS_CCS'] = case_dic['CAPACITY_NATGAS_CCS']
            result['DISPATCH_NATGAS_CCS'] = np.array(dispatch_natgas_ccs.value).flatten()/numerics_demand_scaling
        else:
            result['CAPACITY_NATGAS_CCS'] = capacity_natgas_ccs/numerics_demand_scaling
            result['DISPATCH_NATGAS_CCS'] = dispatch_natgas_ccs/numerics_demand_scaling

        if 'SOLAR' in system_components:
            if case_dic['CAPACITY_SOLAR'] < 0:
                result['CAPACITY_SOLAR'] = np.asscalar(capacity_solar.value)/numerics_demand_scaling
            else:
                result['CAPACITY_SOLAR'] = case_dic['CAPACITY_SOLAR']
            result['DISPATCH_SOLAR'] = np.array(dispatch_solar.value).flatten()/numerics_demand_scaling
            result['CURTAILMENT_SOLAR'] = result['CAPACITY_SOLAR'] * solar_series - result['DISPATCH_SOLAR']
        else:
            result['CAPACITY_SOLAR'] = capacity_solar/numerics_demand_scaling
            result['DISPATCH_SOLAR'] = dispatch_solar/numerics_demand_scaling
            result['CURTAILMENT_SOLAR'] = (capacity_solar-dispatch_solar)/numerics_demand_scaling

        if 'WIND' in system_components:
            if case_dic['CAPACITY_WIND'] < 0:
                result['CAPACITY_WIND'] = np.asscalar(capacity_wind.value)/numerics_demand_scaling
            else:
                result['CAPACITY_WIND'] = case_dic['CAPACITY_WIND']
            result['DISPATCH_WIND'] = np.array(dispatch_wind.value).flatten()/numerics_demand_scaling
            result['CURTAILMENT_WIND'] = result['CAPACITY_WIND'] * wind_series - result['DISPATCH_WIND']
        else:
            result['CAPACITY_WIND'] = capacity_wind/numerics_demand_scaling
            result['DISPATCH_WIND'] = dispatch_wind/numerics_demand_scaling
            result['CURTAILMENT_WIND'] = (capacity_wind-dispatch_wind)/numerics_demand_scaling

        if 'SOLAR2' in system_components:
            if case_dic['CAPACITY_SOLAR2'] < 0:
                result['CAPACITY_SOLAR2'] = np.asscalar(capacity_solar2.value)/numerics_demand_scaling
            else:
                result['CAPACITY_SOLAR2'] = case_dic['CAPACITY_SOLAR2']
            result['DISPATCH_SOLAR2'] = np.array(dispatch_solar2.value).flatten()/numerics_demand_scaling
            result['CURTAILMENT_SOLAR2'] = result['CAPACITY_SOLAR2'] * solar2_series - result['DISPATCH_SOLAR2']
        else:
            result['CAPACITY_SOLAR2'] = capacity_solar2/numerics_demand_scaling
            result['DISPATCH_SOLAR2'] = dispatch_solar2/numerics_demand_scaling
            result['CURTAILMENT_SOLAR2'] = (capacity_solar2-dispatch_solar2)/numerics_demand_scaling

        if 'WIND2' in system_components:
            if case_dic['CAPACITY_WIND2'] < 0:
                result['CAPACITY_WIND2'] = np.asscalar(capacity_wind2.value)/numerics_demand_scaling
            else:
                result['CAPACITY_WIND2'] = case_dic['CAPACITY_WIND2']
            result['DISPATCH_WIND2'] = np.array(dispatch_wind2.value).flatten()/numerics_demand_scaling
            result['CURTAILMENT_WIND2'] = result['CAPACITY_WIND2'] * wind2_series - result['DISPATCH_WIND2']
        else:
            result['CAPACITY_WIND2'] = capacity_wind2/numerics_demand_scaling
            result['DISPATCH_WIND2'] = dispatch_wind2/numerics_demand_scaling
            result['CURTAILMENT_WIND2'] = (capacity_wind2-dispatch_wind2)/numerics_demand_scaling

        if 'NUCLEAR' in system_components:
            if case_dic['CAPACITY_NUCLEAR'] < 0:
                result['CAPACITY_NUCLEAR'] = np.asscalar(capacity_nuclear.value)/numerics_demand_scaling
            else:
                result['CAPACITY_NUCLEAR'] = case_dic['CAPACITY_NUCLEAR']
            result['DISPATCH_NUCLEAR'] = np.array(dispatch_nuclear.value).flatten()/numerics_demand_scaling
            result['CURTAILMENT_NUCLEAR'] = result['CAPACITY_NUCLEAR'] * np.ones(num_time_periods) - result['DISPATCH_NUCLEAR']
        else:
            result['CAPACITY_NUCLEAR'] = capacity_nuclear/numerics_demand_scaling
            result['DISPATCH_NUCLEAR'] = dispatch_nuclear/numerics_demand_scaling
            result['CURTAILMENT_NUCLEAR'] = (capacity_nuclear-dispatch_nuclear)/numerics_demand_scaling

        if 'FUEL' in system_components:
            if case_dic['CAPACITY_FUEL_ELECTROLYZER'] < 0:
                result['CAPACITY_FUEL_ELECTROLYZER'] = np.asscalar(capacity_fuel_electrolyzer.value)/numerics_demand_scaling
            else:
                result['CAPACITY_FUEL_ELECTROLYZER'] = case_dic['CAPACITY_FUEL_ELECTROLYZER']
            if case_dic['CAPACITY_FUEL_CHEM_PLANT'] < 0:
                result['CAPACITY_FUEL_CHEM_PLANT'] = np.asscalar(capacity_fuel_chem_plant.value)/numerics_demand_scaling
            else:
                result['CAPACITY_FUEL_CHEM_PLANT'] = case_dic['CAPACITY_FUEL_CHEM_PLANT']
            if case_dic['CAPACITY_FUEL_POWER'] < 0:
                result['CAPACITY_FUEL_POWER'] = np.asscalar(capacity_fuel_power.value)/numerics_demand_scaling
            else:
                result['CAPACITY_FUEL_POWER'] = case_dic['CAPACITY_FUEL_POWER']
            if case_dic['CAPACITY_FUEL_H2_STORAGE'] < 0:
                result['CAPACITY_FUEL_H2_STORAGE'] = np.asscalar(capacity_fuel_h2_storage.value)/numerics_demand_scaling
            else:
                result['CAPACITY_FUEL_H2_STORAGE'] = case_dic['CAPACITY_FUEL_H2_STORAGE']
            result['DISPATCH_TO_FUEL_H2_STORAGE'] = np.array(dispatch_to_fuel_h2_storage.value).flatten()/numerics_demand_scaling
            result['DISPATCH_FROM_FUEL_H2_STORAGE_TOT'] = np.array(dispatch_from_fuel_h2_storage_tot.value).flatten()/numerics_demand_scaling
            result['DISPATCH_FROM_FUEL_H2_STORAGE_CHEM'] = np.array(dispatch_from_fuel_h2_storage_chem.value).flatten()/numerics_demand_scaling
            result['DISPATCH_FROM_FUEL_H2_STORAGE_POWER'] = np.array(dispatch_from_fuel_h2_storage_power.value).flatten()/numerics_demand_scaling
            result['FUEL_H2_STORAGE'] = np.array(fuel_h2_storage.value).flatten()/numerics_demand_scaling
            #result['CURTAILMENT_FUEL'] = result['CAPACITY_FUEL'] * np.ones(num_time_periods) - result['DISPATCH_TO_FUEL']
        else:
            result['CAPACITY_FUEL_ELECTROLYZER'] = capacity_fuel_electrolyzer/numerics_demand_scaling
            result['CAPACITY_FUEL_CHEM_PLANT'] = capacity_fuel_chem_plant/numerics_demand_scaling
            result['CAPACITY_FUEL_POWER'] = capacity_fuel_power/numerics_demand_scaling
            result['CAPACITY_FUEL_H2_STORAGE'] = capacity_fuel_h2_storage/numerics_demand_scaling
            result['DISPATCH_TO_FUEL_H2_STORAGE'] = dispatch_to_fuel_h2_storage/numerics_demand_scaling
            result['DISPATCH_FROM_FUEL_H2_STORAGE_TOT'] = dispatch_from_fuel_h2_storage_tot/numerics_demand_scaling
            result['DISPATCH_FROM_FUEL_H2_STORAGE_CHEM'] = dispatch_from_fuel_h2_storage_chem/numerics_demand_scaling
            result['DISPATCH_FROM_FUEL_H2_STORAGE_POWER'] = dispatch_from_fuel_h2_storage_power/numerics_demand_scaling
            result['FUEL_H2_STORAGE'] = fuel_h2_storage/numerics_demand_scaling
            #result['CURTAILMENT_FUEL'] = (capacity_fuel-dispatch_to_fuel)/numerics_demand_scaling

        if 'STORAGE' in system_components:
            if case_dic['CAPACITY_STORAGE'] < 0:
                result['CAPACITY_STORAGE'] = np.asscalar(capacity_storage.value)/numerics_demand_scaling
            else:
                result['CAPACITY_STORAGE'] = case_dic['CAPACITY_STORAGE']
            result['DISPATCH_TO_STORAGE'] = np.array(dispatch_to_storage.value).flatten()/numerics_demand_scaling
            result['DISPATCH_FROM_STORAGE'] = np.array(dispatch_from_storage.value).flatten()/numerics_demand_scaling
            result['ENERGY_STORAGE'] = np.array(energy_storage.value).flatten()/numerics_demand_scaling
        else:
            result['CAPACITY_STORAGE'] = capacity_storage/numerics_demand_scaling
            result['DISPATCH_TO_STORAGE'] = dispatch_to_storage/numerics_demand_scaling
            result['DISPATCH_FROM_STORAGE'] = dispatch_from_storage/numerics_demand_scaling
            result['ENERGY_STORAGE'] = energy_storage/numerics_demand_scaling

        if 'STORAGE2' in system_components:
            if case_dic['CAPACITY_STORAGE2'] < 0:
                result['CAPACITY_STORAGE2'] = np.asscalar(capacity_storage2.value)/numerics_demand_scaling
            else:
                result['CAPACITY_STORAGE2'] = case_dic['CAPACITY_STORAGE2']
            result['DISPATCH_TO_STORAGE2'] = np.array(dispatch_to_storage2.value).flatten()/numerics_demand_scaling
            result['DISPATCH_FROM_STORAGE2'] = np.array(dispatch_from_storage2.value).flatten()/numerics_demand_scaling
            result['ENERGY_STORAGE2'] = np.array(energy_storage2.value).flatten()/numerics_demand_scaling
        else:
            result['CAPACITY_STORAGE2'] = capacity_storage2/numerics_demand_scaling
            result['DISPATCH_TO_STORAGE2'] = dispatch_to_storage2/numerics_demand_scaling
            result['DISPATCH_FROM_STORAGE2'] = dispatch_from_storage2/numerics_demand_scaling
            result['ENERGY_STORAGE2'] = energy_storage2/numerics_demand_scaling

        if 'PGP_STORAGE' in system_components:
            if case_dic['CAPACITY_PGP_STORAGE'] < 0:
                result['CAPACITY_PGP_STORAGE'] = np.asscalar(capacity_pgp_storage.value)/numerics_demand_scaling
            else:
                result['CAPACITY_PGP_STORAGE'] = case_dic['CAPACITY_PGP_STORAGE']
            if case_dic['CAPACITY_TO_PGP_STORAGE'] < 0:
                result['CAPACITY_TO_PGP_STORAGE'] = np.asscalar(capacity_to_pgp_storage.value)/numerics_demand_scaling
            else:
                result['CAPACITY_TO_PGP_STORAGE'] = case_dic['CAPACITY_TO_PGP_STORAGE']
            if case_dic['CAPACITY_FROM_PGP_STORAGE'] < 0:
                result['CAPACITY_FROM_PGP_STORAGE'] = np.asscalar(capacity_from_pgp_storage.value)/numerics_demand_scaling
            else:
                result['CAPACITY_FROM_PGP_STORAGE'] = case_dic['CAPACITY_FROM_PGP_STORAGE']
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

        if 'CSP' in system_components:
            if case_dic['CAPACITY_CSP'] < 0:
                result['CAPACITY_CSP'] = np.asscalar(capacity_csp.value)/numerics_demand_scaling
            else:
                result['CAPACITY_CSP'] = case_dic['CAPACITY_CSP']
            if case_dic['CAPACITY_CSP_STORAGE'] < 0:
                result['CAPACITY_CSP_STORAGE'] = np.asscalar(capacity_csp_storage.value)/numerics_demand_scaling
            else:
                result['CAPACITY_CSP_STORAGE'] = case_dic['CAPACITY_CSP_STORAGE']
            result['DISPATCH_TO_CSP_STORAGE'] = np.array(dispatch_to_csp_storage.value).flatten()/numerics_demand_scaling
            result['DISPATCH_FROM_CSP'] = np.array(dispatch_from_csp.value).flatten()/numerics_demand_scaling
            result['ENERGY_CSP_STORAGE'] = np.array(energy_csp_storage.value).flatten()/numerics_demand_scaling
            result['CURTAILMENT_CSP'] = result['CAPACITY_CSP'] * csp_series - result['DISPATCH_TO_CSP_STORAGE']
        else:
            result['CAPACITY_CSP'] = capacity_csp/numerics_demand_scaling
            result['CAPACITY_CSP_STORAGE'] = capacity_csp_storage/numerics_demand_scaling
            result['DISPATCH_TO_CSP_STORAGE'] = dispatch_to_csp_storage/numerics_demand_scaling
            result['DISPATCH_FROM_CSP'] = dispatch_from_csp/numerics_demand_scaling
            result['ENERGY_CSP_STORAGE'] = energy_csp_storage/numerics_demand_scaling
            result['CURTAILMENT_CSP'] = (capacity_csp-dispatch_from_csp)/numerics_demand_scaling

        if 'UNMET_DEMAND' in system_components:
            result['DISPATCH_UNMET_DEMAND'] = np.array(dispatch_unmet_demand.value).flatten()/numerics_demand_scaling
        else:
            result['DISPATCH_UNMET_DEMAND'] = dispatch_unmet_demand/numerics_demand_scaling


    return result
