# -*- coding: utf-8 -*-
"""

Takes output from the simple energy model and produces time series of hourly
cost of delivering electricity.

Created on Wed Aug 22 17:50:11 2018

@author: kcaldeira
"""
import numpy as np

#%%
#  Takes a capacity cost (fixed cost) and dispatch cost (variable cost) and
#  a time series of generation, and returns the hourly cost under the assumption
#  that the fixed costs are distributed across the generation that needed that
#  amount of capacity or less.
#
#  For example, let's say you had 5 hours of operation, with dispatch of
#     dispatch = [ 0, 1, 1, 1, 2 ]
#  And a fixed_cost and var_cost of 1 $/kWh
#  The dispatch related costs would be [0, 1, 1, 1, 2]
#
#  But with 2 kW of capacity for 5 hours, you needed 1 kW of capacity for 4 hours, adding
#  5/4 = 1.25 $/hr to the cost of those hours. You needed an additional 1 kW
#  of capacity, adding 5/1 = 5 $/hr for that time so the capacity related costs
#  would be [0, 1.25, 1.25, 1.25, 6.25] for a grand total of
#  cost_per_hour = [0 , 2.25, 2.25, 2.25, 8.25 ] as the cost per hour.
#  This must be divided by kW to get cost per kWh
#  cost_per_kWh = [0, 2.25, 2.25, 2.25, 4.125 ]
#
def cost_model_dispatchable(fixed_cost_in, var_cost_in, dispatch_in):
    fixed_cost = float(fixed_cost_in) # avoid integer arithmatic
    var_cost = float(var_cost_in)
    dispatch = np.array(dispatch_in)
    num_hours = len(dispatch)
    
    order = np.argsort(dispatch)[::-1] # indices of dispatch in descending order
    unsort_order = np.argsort(order)
    
    # The highest amount of use is used for 1 hour, the second highest is needed for 2 hours, etc
    needed_hours = 1. + np.arange(num_hours)
    
    incr_capacity = dispatch[order[:-1]] - dispatch[order[1:]]
    incr_capacity= np.append(incr_capacity,dispatch[order[-1]])
    
    incr_capacity_div_hours_used = incr_capacity / needed_hours
    
    cum_incr_capacity_sorted= np.cumsum(incr_capacity_div_hours_used[::-1])[::-1]
    
    cum_incr_capacity = cum_incr_capacity_sorted[unsort_order]
    
    cost_per_hour = var_cost * dispatch + fixed_cost * num_hours * cum_incr_capacity
    cost_per_kWh = cost_per_hour / dispatch
    
    return cost_per_hour, cost_per_kWh # cost of generation for each hour


#%%
#  Takes a capacity cost (fixed cost) and dispatch cost (variable cost) and
#  a time series of generation, and returns the hourly cost under the assumption
#  that the fixed costs are distributed across the generation that needed that
#  amount of capacity or less.
#
#  For example, let's say you had 5 hours of operation, with dispatch of
#     dispatch = [ 0, 1, 2, 1, 1 ]
#  But let's say that the wind power available per hour was:
#     capacity = [ 0, 1, 2, 0.5, 1]
#  where this is the capacity per unit capacity installed.
#
#  Then the amount of capacity needed for each hour is these two divide 
#       capacity_needed = [0, 1, 1, 2, 1]
#
#  And a fixed_cost and var_cost of 1 $/kWh
#  The dispatch related costs would be [0, 1, 2, 1, 1]
#
#  But with 2 kW of capacity for 5 hours, you needed 1 kW of capacity for 4 hours, adding
#  5/4 = 1.25 $/hr to the cost of those hours. You needed an additional 1 kW
#  of capacity, adding 5/1 = 5 $/hr for that time so the capacity related costs
#  would be [0, 1.25, 1.25, 6.25, 1.25] for a grand total of
#  cost_per_hour = [0 , 2.25, 3.25, 7.25, 2.25 ] as the cost per hour.
#  This must be divided by kW to get cost per kWh
#  cost_per_kWh = [0, 2.25, 1.125, 7.25, 2.25 ]
#
def cost_model_intermittent(fixed_cost_in, var_cost_in, dispatch_in, capacity_in):
    fixed_cost = float(fixed_cost_in) # avoid integer arithmatic
    var_cost = float(var_cost_in)
    dispatch = np.array(dispatch_in, dtype=float) # dispatch time series
    capacity = np.array(capacity_in, dtype=float) # hourly generation capacity per unit capacity installed
    capacity_needed = np.divide(dispatch, capacity, out = np.zeros_like(dispatch), where=capacity!=0)
    
    num_hours = len(dispatch)
    
    order = np.argsort(capacity_needed)[::-1] # indices of dispatch in descending order
    unsort_order = np.argsort(order)
    
    # The highest amount of use is used for 1 hour, the second highest is needed for 2 hours, etc
    needed_hours = 1. + np.arange(num_hours)
    
    incr_capacity = capacity_needed[order[:-1]] - capacity_needed[order[1:]]
    incr_capacity= np.append(incr_capacity,capacity_needed[order[-1]])
    
    incr_capacity_div_hours_used = incr_capacity / needed_hours
    
    cum_incr_capacity_sorted= np.cumsum(incr_capacity_div_hours_used[::-1])[::-1]
    
    cum_incr_capacity = cum_incr_capacity_sorted[unsort_order]
    
    cost_per_hour = var_cost * dispatch + fixed_cost * num_hours * cum_incr_capacity
    cost_per_kWh = cost_per_hour / dispatch
    
    return cost_per_hour, cost_per_kWh # cost of generation for each hour

#%%
# time loop cost calculations so as to include battery (and later PGP costs)
#
# This code is assumed to have in it data from an individual simulation in the
# form of <global_dic>, a single element of <case_dic_list> and <result_list>.
    
# This code returns its result by updating dictionary <result> which should be a pointer.

def cost_and_storage_calculation( global_dic, case_dic, result ):
    
    num_time_periods = len(case_dic['DEMAND_SERIES'])
    zeroVec = np.zeros(num_time_periods,dtype=float)
    totalDispatch = zeroVec[:]
    totalCost = zeroVec[:]
    
    system_components = case_dic['SYSTEM_COMPONENTS']  
    
    if 'NATGAS' in system_components:
        dispatch = result['DISPATCH_NATGAS']
        costPerHour = cost_model_dispatchable(
                case_dic['FIXED_COST_NATGAS'],
                case_dic['VAR_COST_NATGAS'],
                dispatch
                )
        result['COST_NATGAS_PERHOUR'] = costPerHour 
        result['COST_NATGAS_PERKWH'] = costPerHour / dispatch
        totalDispatch += dispatch
        totalCost += costPerHour
    else:
        result['COST_NATGAS_PERHOUR'] = zeroVec
        result['COST_NATGAS_PERKWH'] = zeroVec

    if 'SOLAR' in system_components:
        dispatch = result['DISPATCH_SOLAR']
        costPerHour = cost_model_dispatchable(
                case_dic['FIXED_COST_SOLAR'],
                case_dic['VAR_COST_SOLAR'],
                dispatch
                )
        result['COST_SOLAR_PERHOUR'] = costPerHour 
        result['COST_SOLAR_PERKWH'] = costPerHour / dispatch
        totalDispatch += dispatch
        totalCost += costPerHour
    else:
        result['COST_SOLAR_PERHOUR'] = zeroVec
        result['COST_SOLAR_PERKWH'] = zeroVec

    if 'WIND' in system_components:
        dispatch = result['DISPATCH_WIND']
        costPerHour = cost_model_dispatchable(
                case_dic['FIXED_COST_WIND'],
                case_dic['VAR_COST_WIND'],
                dispatch
                )
        result['COST_WIND_PERHOUR'] = costPerHour 
        result['COST_WIND_PERKWH'] = costPerHour / dispatch
        totalDispatch += dispatch
        totalCost += costPerHour
    else:
        result['COST_WIND_PERHOUR'] = zeroVec
        result['COST_WIND_PERKWH'] = zeroVec

    if 'NUCLEAR' in system_components:
        dispatch = result['VAR_NUCLEAR']
        costPerHour = cost_model_dispatchable(
                case_dic['FIXED_COST_NUCLEAR'],
                case_dic['VAR_COST_NUCLEAR'],
                dispatch
                )
        result['COST_NUCLEAR_PERHOUR'] = costPerHour 
        result['COST_NUCLEAR_PERKWH'] = costPerHour / dispatch
        totalDispatch += dispatch
        totalCost += costPerHour
    else:
        result['COST_NUCLEAR_PERHOUR'] = zeroVec
        result['COST_NUCLEAR_PERKWH'] = zeroVec
        
        
    if 'UNMET_DEMAND' in system_components:
        dispatch = result['VAR_UNMET_DEMAND']
        costPerHour = dispatch * case_dic['VAR_COST_UNMET_DEMAND'] # Assume no fixed cost to UNMET_DEMAND
        result['COST_UNMET_DEMAND_PERHOUR'] = costPerHour 
        result['COST_UNMET_DEMAND_PERKWH'] = costPerHour / dispatch
        totalDispatch += dispatch
        totalCost += costPerHour
    else:
        result['COST_UNMET_DEMAND_PERHOUR'] = zeroVec
        result['COST_UNMET_DEMAND_PERKWH'] = zeroVec

    # first just do capacity part of storage (i.e., not dispatch costs, and not electricity costs)
    if ('STORAGE' in system_components) or ('PGP+STORAGE' in system_components):
        cost_and_storage_lifo_stack_analysis( global_dic, case_dic, result )
        # storage_capacity_and_cost_analysis adds the following items to <result>
        # result['COST_STORAGE_PERKWH']  cost of electricity from storage in $/kWh
        # result['COST_STORAGE_PERHOUR'] cost of electricity from storage per hour in $/hr (includes subcomponents listed below)
        
        # result['COST_TO_STORAGE_PERHOUR'] variable cost of charging (other than nelectricity cost) contribution to hourly cost of electricity from storage
        # result['COST_ELECTRICITY_TO_STORAGE_PERHOUR'] charging electricity cost contribution to hourly cost of electricity from storage
        # result['COST_FROM_STORAGE_PERHOUR'] variable cost of discharging contribution to hourly cost of electricity from storage
        # result['COST_STORAGE_FIXED_COST_PERHOUR'] allocation of fixed cost of storage to cost of electricity from storage
        # result['STORAGE_CAPACITY_NEEDED'] amount of storage capacity needed to supply the electricity needed for that hour, treating storage as a LIFO stack
        
        # result['COST_PGP_STORAGE_PERKWH']  cost of electricity from PGP_STORAGE in $/kWh
        
        # result['COST_PGP_STORAGE_PERHOUR'] cost of electricity from PGP_STORAGE per hour in $/hr (includes subcomponents listed below)
        
        # result['COST_TO_PGP_STORAGE_PERHOUR'] variable cost of charging (other than nelectricity cost) contribution to hourly cost of electricity from PGP_STORAGE
        # result['COST_ELECTRICITY_TO_PGP_STORAGE_PERHOUR'] charging electricity cost contribution to hourly cost of electricity from PGP_STORAGE
        # result['COST_FROM_PGP_STORAGE_PERHOUR'] variable cost of discharging contribution to hourly cost of electricity from PGP_STORAGE
        # result['COST_PGP_STORAGE_FIXED_COST_PERHOUR'] allocation of fixed cost of PGP_STORAGE to cost of electricity from PGP_STORAGE
        # result['PGP_STORAGE_CAPACITY_NEEDED'] amount of PGP_STORAGE energy capacity needed to supply the electricity needed for that hour, treating PGP_STORAGE as a LIFO stack
    else:
        result['COST_STORAGE_PERKWH'] =  zeroVec # cost of electricity from storage in $/kWh
        
        result['COST_STORAGE_PERHOUR'] =  zeroVec #  cost of electricity from storage per hour in $/hr (includes subcomponents listed below)
        
        result['COST_TO_STORAGE_PERHOUR'] =  zeroVec #  variable cost of charging (other than nelectricity cost) contribution to hourly cost of electricity from storage
        result['COST_ELECTRICITY_TO_STORAGE_PERHOUR'] =  zeroVec #  charging electricity cost contribution to hourly cost of electricity from storage
        result['COST_FROM_STORAGE_PERHOUR'] =  zeroVec #  variable cost of discharging contribution to hourly cost of electricity from storage
        result['COST_STORAGE_FIXED_COST_PERHOUR'] =  zeroVec #  allocation of fixed cost of storage to cost of electricity from storage
        result['STORAGE_CAPACITY_NEEDED'] =  zeroVec #  amount of storage capacity needed to supply the electricity needed for that hour, treating storage as a LIFO stack
        
        result['COST_PGP_STORAGE_PERKWH'] =  zeroVec #   cost of electricity from PGP_STORAGE in $/kWh
        
        result['COST_PGP_STORAGE_PERHOUR'] =  zeroVec #  cost of electricity from PGP_STORAGE per hour in $/hr (includes subcomponents listed below)
        
        result['COST_TO_PGP_STORAGE_PERHOUR'] =  zeroVec #  variable cost of charging (other than nelectricity cost) contribution to hourly cost of electricity from PGP_STORAGE
        result['COST_ELECTRICITY_TO_PGP_STORAGE_PERHOUR'] =  zeroVec #  charging electricity cost contribution to hourly cost of electricity from PGP_STORAGE
        result['COST_FROM_PGP_STORAGE_PERHOUR'] =  zeroVec #  variable cost of discharging contribution to hourly cost of electricity from PGP_STORAGE
        result['COST_PGP_STORAGE_FIXED_COST_PERHOUR'] =  zeroVec #  allocation of fixed cost of PGP_STORAGE to cost of electricity from PGP_STORAGE
        result['PGP_STORAGE_CAPACITY_NEEDED'] =  zeroVec #  amount of PGP_STORAGE energy capacity needed to supply the electricity needed for that hour, treating PGP_STORAGE as a LIFO stack
        

#%%    def cost_and_storage_lifo_stack_analysis( global_dic, case_dic, result ):
        
        # The basic idea of the following code is to treat battery plus PGP storage 

        # storage_capacity_and_cost_analysis adds the following items to <result>
        # result['COST_STORAGE_PERKWH']  cost of electricity from storage in $/kWh
        
        # result['COST_STORAGE_PERHOUR'] cost of electricity from storage per hour in $/hr (includes subcomponents listed below)
        
        # result['COST_TO_STORAGE_PERHOUR'] variable cost of charging (other than nelectricity cost) contribution to hourly cost of electricity from storage
        # result['COST_ELECTRICITY_TO_STORAGE_PERHOUR'] charging electricity cost contribution to hourly cost of electricity from storage
        # result['COST_FROM_STORAGE_PERHOUR'] variable cost of discharging contribution to hourly cost of electricity from storage
        # result['COST_STORAGE_FIXED_COST_PERHOUR'] allocation of fixed cost of storage to cost of electricity from storage
        # result['STORAGE_CAPACITY_NEEDED'] amount of storage capacity needed to supply the electricity needed for that hour, treating storage as a LIFO stack
        
        # result['COST_PGP_STORAGE_PERKWH']  cost of electricity from PGP_STORAGE in $/kWh
        
        # result['COST_PGP_STORAGE_PERHOUR'] cost of electricity from PGP_STORAGE per hour in $/hr (includes subcomponents listed below)
        
        # result['COST_TO_PGP_STORAGE_PERHOUR'] variable cost of charging (other than nelectricity cost) contribution to hourly cost of electricity from PGP_STORAGE
        # result['COST_ELECTRICITY_TO_PGP_STORAGE_PERHOUR'] charging electricity cost contribution to hourly cost of electricity from PGP_STORAGE
        # result['COST_FROM_PGP_STORAGE_PERHOUR'] variable cost of discharging contribution to hourly cost of electricity from PGP_STORAGE
        # result['COST_PGP_STORAGE_FIXED_COST_PERHOUR'] allocation of fixed cost of PGP_STORAGE to cost of electricity from PGP_STORAGE
        # result['PGP_STORAGE_CAPACITY_NEEDED'] amount of PGP_STORAGE energy capacity needed to supply the electricity needed for that hour, treating PGP_STORAGE as a LIFO stack

def cost_and_storage_lifo_stack_analysis( global_dic, case_dic, result ):
    
    # To allocate costs associated with storage, we want to allocate costs of storage capital and
    # costs of charging and discharging the battery attributable per kWh or per hour for each hour of electricity delivery
    
    # This calculation treats the storage reservoirs as LIFO (Last-In First-Out) stacks where the costs and amounts of electricity are stored.
    
    # cost of electricity upon discharge must include the cost 
    
    num_time_periods = len(case_dic['DEMAND_SERIES'])
    zeroVec = np.zeros(num_time_periods,dtype=float)
    
    system_components = case_dic['SYSTEM_COMPONENTS'] 
    
    # costOfElectricity, amountOfElectricity
    costOfElectricityOther = (
            result['COST_NATGAS_PERHOUR'] 
            + result['COST_WIND_PERHOUR']
            + result['COST_SOLAR_PERHOUR']
            + result['COST_NUCLEAR_PERHOUR']
            + result['COST_UNMET_DEMAND']
            )
    amountOfElectricityOther = (
            result['DISPATCH_NATGAS'] 
            + result['DISPATCH_WIND']
            + result['DISPATCH_SOLAR']
            + result['DISPATCH_NUCLEAR']
            + result['DISPATCH_UNMET_DEMAND']
            )
    lifo_stack = []

    # We need to cycle to get a good initial condition.
    # Initially, we know the amount but not the age or cost of stored energy.
    # So, we make the assumption that the cost was zero and the age was -1.
    num_cycles = 3
    tmp = 0.
    
    for idx in range(num_time_periods-start_point):
        idx = idx + start_point
        tmp = tmp + DISPATCH_TO_STORAGE[idx] - DISPATCH_FROM_STORAGE[idx]
              
        if DISPATCH_TO_STORAGE[idx] > 0:  # push on stack (with time moved up 1 cycle)
            lifo_stack.append([idx-num_time_periods,DISPATCH_TO_STORAGE[idx]*CHARGING_EFFICIENCY_STORAGE ])
        if DISPATCH_FROM_STORAGE[idx] > 0:
            dispatch_remaining = DISPATCH_FROM_STORAGE[idx]
            while dispatch_remaining > 0:
                #print (len(lifo_stack),DISPATCH_FROM_STORAGE[idx],dispatch_remaining
                if len(lifo_stack) != 0:
                    top_of_stack = lifo_stack.pop()
                    if top_of_stack[1] > dispatch_remaining:
                        # partial removal
                        new_top = np.copy(top_of_stack)
                        new_top[1] = new_top[1] - dispatch_remaining
                        lifo_stack.append(new_top)
                        dispatch_remaining = 0
                    else:
                        dispatch_remaining = dispatch_remaining - top_of_stack[1]
                else:
                    dispatch_remaining = 0 # stop while loop if stack is empty
    # Now we have the stack as an initial condition and can do it for real
    max_headroom = np.zeros(num_time_periods)
    mean_residence_time = np.zeros(num_time_periods)
    max_residence_time = np.zeros(num_time_periods)
    
    # energy storage at time t is the amount of energy in storage in the beginning of the time step.
    #   constraints += [
    #        energy_storage[(i+1) % num_time_periods] == energy_storage[i] + charging_efficiency_storage * dispatch_to_storage[i] - dispatch_from_storage[i] - energy_storage[i]*decay_rate_storage
    #        ]
    #
    #   constraints += [
    #        energy_pgp_storage[(i+1) % num_time_periods] == energy_pgp_storage[i] 
    #        + charging_efficiency_pgp_storage * dispatch_to_pgp_storage[i] 
    #        - dispatch_from_pgp_storage[i] 
    #        ]

    # each item on lifo stack is a list:
    #  lifo[0] == time_idx
    #  lifo[1] == amount of electricitity to storage
    #  lifo[2] == cost of putting that much electricity in storage
    
    lifo_storage = []
    lifo_storage.append([-1,result['ENERGY_STORAGE'][0],0.]) # dummy cost and time of placement in battery
    
    lifo_pgp_storage = []
    lifo_pgp_storage.append([-1,result['ENERGY_PGP_STORAGE'][0],0.]) # dummy cost and time of placement in battery
    

    for time_idx in range(2 * num_time_periods):
        max_head = 0
        mean_res = 0
        max_res = 0
        if DISPATCH_TO_STORAGE[time_idx] > 0:  # push on stack
            lifo_stack.append([time_idx,DISPATCH_TO_STORAGE[time_idx % num_time_periods]*CHARGING_EFFICIENCY_STORAGE ])
        if DISPATCH_FROM_STORAGE[time_idx] > 0:
            dispatch_remaining = DISPATCH_FROM_STORAGE[time_idx % num_time_periods]
            accum_time = 0
            while dispatch_remaining > 0:
                if lifo_stack != []:
                    top_of_stack = lifo_stack.pop()
                    if top_of_stack[1] > dispatch_remaining:
                        # partial removal
                        accum_time = accum_time + dispatch_remaining * (time_idx - top_of_stack[0])
                        new_top = np.copy(top_of_stack)
                        new_top[1] = new_top[1] - dispatch_remaining
                        lifo_stack.append(new_top) # put back the remaining power at the old time
                        dispatch_remaining = 0
                    else: 
                        # full removal of top of stack
                        accum_time = accum_time + top_of_stack[1] * (time_idx - top_of_stack[0])
                        dispatch_remaining = dispatch_remaining - top_of_stack[1]
                else:
                    dispatch_remaining = 0 # stop while loop if stack is empty
            mean_res = accum_time / DISPATCH_FROM_STORAGE[time_idx % num_time_periods]
            max_res = time_idx - top_of_stack[0]
            # maximum headroom needed is the max of the storage between time_idx and top_of_stack[0]
            #    minus the amount of storage at time time_idx + 1
            energy_vec = np.concatenate([ENERGY_STORAGE,ENERGY_STORAGE,ENERGY_STORAGE])
            max_head = np.max(energy_vec[int(top_of_stack[0]+num_time_periods):int(time_idx + 1+num_time_periods)]) - energy_vec[int(time_idx + 1 + num_time_periods)]   # dl-->could be negative?
        max_headroom[time_idx % num_time_periods] = max_head
        mean_residence_time[time_idx % num_time_periods] = mean_res
        max_residence_time[time_idx % num_time_periods] = max_res
    return max_headroom,mean_residence_time,max_residence_time
    
