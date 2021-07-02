# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 17:12:02 2018

@author: kcaldeira
"""
import numpy as np


    
#%% LIFO stack storage calculation

# <storage_calculation> takes storage fluxes and prices and computes
#
#  <max_headroom> how much headroom the storage needed to deliver the electricity in each hour.
#  <mean_storage_time> mean storage time of electricity delivered in each hour.
#  <max_storage_time> maximum storage time of electricity delivered in each hour. 

#  <net_revenue> net_revenue from storage considering cost of electricity plus variable costs associated with storage.
#  <cost_elec_storage> cost of electricity sold from storage in each hour
#  <var_cost_storage> variable costs associated with electricity sold from storage in each hour
#  <revenue_elec_storage> revenue from electricity sold from storage in each hour
    
def storage_analysis(global_dic,case_dic,result_dic):
    epsilon = 1e-8

    var_cost_to_storage = case_dic['VAR_COST_TO_STORAGE']
    var_cost_from_storage = case_dic['VAR_COST_FROM_STORAGE']
    charging_efficiency_storage = case_dic['CHARGING_EFFICIENCY_STORAGE']
    decay_rate_storage = case_dic['DECAY_RATE_STORAGE']
    
    dispatch_to_storage = result_dic['DISPATCH_TO_STORAGE']
    dispatch_from_storage = result_dic['DISPATCH_FROM_STORAGE']
    energy_storage = result_dic['ENERGY_STORAGE']
    price = result_dic['PRICE']
    
    num_time_periods = price.size
        
    zero_idx = np.where(energy_storage < epsilon )[0][-1] # find index of last time storage was empty

    lifo_stack = [[-1,0,0,0]] # start off with nothing
    

    max_headroom = np.zeros_like(price)
    mean_storage_time = np.zeros_like(price)
    max_storage_time = np.zeros_like(price)
    
    net_revenue = np.zeros_like(price)
    elec_cost_elec_storage = np.zeros_like(price)
    var_cost_elec_storage = np.zeros_like(price)
    
    # Note that the relevant code for storage in <Core_Model.py> is:
    
    #            constraints += [
    #                energy_storage[(i+1) % num_time_periods] == 
    #                    energy_storage[i] + charging_efficiency_storage * dispatch_to_storage[i] 
    #                    - dispatch_from_storage[i] - energy_storage[i]*decay_rate_storage
    
    # and
    
    #            fcn2min += capacity_storage * fixed_cost_storage +  \
    #            cvx.sum_entries(dispatch_to_storage * var_cost_to_storage)/num_time_periods + \
    #            cvx.sum_entries(dispatch_from_storage * var_cost_from_storage)/num_time_periods 

    # This means that, if we think storage is quantized in time,
    # storage decay happens at the start of the time interval (i.e., on the amount at the begining of the time step)
    # dispatch and charging are at the end of the time step.

    # We are going to go around this loop start at the last time the storage is empty.
    
    # Note that if we are at a cost minimum storage should be empty on at least one
    # time step of the simulation.
    
   
    for idx0 in range(zero_idx - num_time_periods, num_time_periods):
        idx = idx0 % num_time_periods
        max_head = 0
        mean_res = 0
        max_res = 0
        
        cost_elec = 0
        cost_var = 0
        
        # all of the electricity decays between time steps
        lifo_stack = [[item[0],                             #idx
                       item[1]*(1.-decay_rate_storage),     #energy
                       item[2],                             #electricity cost
                       item[3]                              #variable cost to storage
                       ] for item in lifo_stack]
        
        if dispatch_to_storage[idx] > 0:  # push on stack
            lifo_stack.append([
                    idx0,
                    dispatch_to_storage[idx]*charging_efficiency_storage,
                    price[idx]*dispatch_to_storage[idx],
                    var_cost_to_storage*dispatch_to_storage[idx]
                    ] )
            # index of when added to storage, how much added to storage, and how much it cost to add that to storage
        if dispatch_from_storage[idx] > 0:
            dispatch_remaining = dispatch_from_storage[idx]
            accum_time = 0
            while dispatch_remaining > 0:
                if lifo_stack != []:
                    top_of_stack = lifo_stack.pop()
                    if top_of_stack[1] > dispatch_remaining:
                        # partial removal
                        accum_time = accum_time + dispatch_remaining * (idx - top_of_stack[0])
                        new_top = np.copy(top_of_stack)
                        new_top[1] = top_of_stack[1] - dispatch_remaining
                        new_top[2] = top_of_stack[2] *(1.0 - dispatch_remaining/top_of_stack[1])
                        new_top[3] = top_of_stack[3] *(1.0 - dispatch_remaining/top_of_stack[1])
                        cost_elec = cost_elec + top_of_stack[2] * dispatch_remaining/top_of_stack[1] 
                        cost_var = cost_var + top_of_stack[3] * dispatch_remaining/top_of_stack[1] 
                        # reducing amount of money associated with fraction that is delivered.
                        lifo_stack.append(new_top) # put back the remaining power at the old time
                        dispatch_remaining = 0
                    else: 
                        # full removal of top of stack
                        accum_time = accum_time + top_of_stack[1] * (idx - top_of_stack[0])
                        dispatch_remaining = dispatch_remaining - top_of_stack[1]
                        cost_elec = cost_elec + top_of_stack[2]
                        cost_var  = cost_var  + top_of_stack[3]
                else:
                    dispatch_remaining = 0 # stop while loop if stack is empty
                    # This should call an error condition
            mean_res = accum_time / dispatch_from_storage[idx]
            max_res = idx - top_of_stack[0]
            # maximum headroom needed is the max of the storage between idx and top_of_stack[0]
            #    minus the amount of storage at time idx + 1
            energy_vec = np.concatenate([energy_storage,energy_storage,energy_storage])
            max_head = np.max(energy_vec[int(top_of_stack[0]+num_time_periods):int(idx + 1+num_time_periods)]) - energy_vec[int(idx + 1 + num_time_periods)]   # dl-->could be negative?
        max_headroom[idx] = max_head
        mean_storage_time[idx] = mean_res
        max_storage_time[idx] = max_res
        
        elec_cost_elec_storage[idx] = cost_elec
        var_cost_elec_storage[idx] = cost_var
        
    revenue_elec_storage = dispatch_from_storage * price
    var_cost_from_elec_storage = dispatch_from_storage * var_cost_from_storage
    net_cost_elec_storage =  elec_cost_elec_storage + var_cost_elec_storage + var_cost_from_elec_storage
    net_revenue = revenue_elec_storage -  net_cost_elec_storage 
    
    net_revenue_perkWh = np.divide(net_revenue, dispatch_from_storage, 
                                   out=np.zeros_like(net_revenue), where=dispatch_from_storage!=0)
    
    storage_cost_perkWh = np.divide(net_cost_elec_storage, dispatch_from_storage, 
                                   out=np.zeros_like(net_cost_elec_storage), where=dispatch_from_storage!=0)
    
    net_revenue_perkWh = np.divide(net_revenue, dispatch_from_storage, 
                                   out=np.zeros_like(net_revenue), where=dispatch_from_storage!=0)
    

    
    storage_dic = {
            "max_headroom":     max_headroom,
            "mean_storage_time":      mean_storage_time,
            "max_storage_time":       max_storage_time,
            "elec_cost_elec_storage":   elec_cost_elec_storage,
            "var_cost_elec_storage":    var_cost_elec_storage,
            "net_cost_elec_storage":    net_cost_elec_storage,
            "revenue_elec_storage":     revenue_elec_storage,
            "net_revenue":              net_revenue,
            "net_revenue_perkWh":       net_revenue_perkWh,
            "storage_cost_perkWh":      storage_cost_perkWh
            }
            #  <max_headroom> how much headroom the storage needed to deliver the electricity in each hour.
            #  <mean_storage_time> mean storage time of electricity delivered in each hour.
            #  <max_storage_time> maximum storage time of electricity delivered in each hour. 
            
            #  <net_revenue> net_revenue from storage considering cost of electricity plus variable costs associated with storage.
            #  <cost_elec_storage> cost of electricity sold from storage in each hour
            #  <var_cost_storage> variable costs associated with electricity sold from storage in each hour
            #  <revenue_elec_storage> revenue from electricity sold from storage in each hour
        
    return storage_dic


# Need to return an empty storage dict so that the restults keys are consistent
# across all cases
def no_storage_analysis():

    storage_dic = {
            "max_headroom":             -1,
            "mean_storage_time":        -1,
            "max_storage_time":         -1,
            "elec_cost_elec_storage":   -1,
            "var_cost_elec_storage":    -1,
            "net_cost_elec_storage":    -1,
            "revenue_elec_storage":     -1,
            "net_revenue":              -1,
            "net_revenue_perkWh":       -1,
            "storage_cost_perkWh":      -1
            }
    return storage_dic
