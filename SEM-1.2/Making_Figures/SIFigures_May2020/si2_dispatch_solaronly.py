#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 15:19:53 2020

@author: jacquelinedowling
"""
#SOLAR ONLY

##===========================================
#Import stuff
##===========================================
from __future__ import division
import os
import sys
import copy
import numpy as np

import pickle
import numpy as np
from numpy import genfromtxt
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker

import datetime
from matplotlib.dates import DayLocator, MonthLocator, HourLocator, AutoDateLocator, DateFormatter, drange
from matplotlib.dates import MO, TU, WE, TH, FR, SA, SU, WeekdayLocator
from numpy import arange
from matplotlib.ticker import ScalarFormatter
from matplotlib.ticker import FormatStrFormatter

import matplotlib.cm as cm
import matplotlib.mlab as mlab


##===========================================
#Read in Base Case: PGP Batteries, Wind Solar
##===========================================

#‎#/Users/jacquelinedowling/SEM-1.1/Output_Data/newcosts/newcosts_PGPbatt_SolarWind.pickle

pickle_in = open('/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/Oct29_combos/Oct29_combos_Solar_PGPbatt.pickle', 'rb')
#pickle_in = open('/Users/jacquelinedowling/Documents/SEM-1.1_20190114/Output_Data/PGPtest5/PGPtest5_WindSolarPGPBatt_2015.pickle','rb')
base = pickle.load(pickle_in)

##===========================================
#Supporting Functions
##===========================================
def func_time_conversion (input_data, window_size, operation_type = 'mean'):
    
    # NOTE: THIS FUNCTION HAS ONLY BEEN VERIFIED FOR PROPER WRAP-AROUND BEHAVIOR
    #       FOR 'mean'
    # For odd windows sizes, easy. For even need to consider ends where you have half hour of data.

    N_periods = len(input_data)
    input_data_x3 = np.concatenate((input_data,input_data,input_data))
    
    half_size = window_size / 2.
    half_size_full = int(half_size) # number of full things for the mean

    output_data = np.zeros(len(input_data))
    
    for ii in range(len(output_data)):
        if half_size != float (half_size_full): # odd number, easy
            if (operation_type == 'mean'):
                output_data[ii] = np.sum(input_data_x3[N_periods + ii - half_size_full : N_periods + ii + half_size_full + 1 ])/ float(window_size)
            elif(operation_type == 'min'):
                output_data[ii] = np.min(input_data_x3[N_periods + ii - half_size_full : N_periods + ii + half_size_full + 1 ])
            elif(operation_type == 'max'):
                output_data[ii] = np.max(input_data_x3[N_periods + ii - half_size_full : N_periods + ii + half_size_full  + 1])
            elif(operation_type == 'sum'):
                output_data[ii] = np.sum(input_data_x3[N_periods + ii - half_size_full : N_periods + ii + half_size_full  + 1])
        else: # even number need to include half of last ones
            if (operation_type == 'mean'):
                output_data[ii] = ( np.sum(input_data_x3[N_periods + ii - half_size_full : N_periods + ii + half_size_full ])  \
                        + input_data_x3[N_periods + ii - half_size_full -1 ] *0.5 +  input_data_x3[N_periods + ii + half_size_full + 1 ] *0.5) / window_size
            elif(operation_type == 'min'):
                output_data[ii] = np.min(input_data_x3[N_periods + ii - half_size_full -1 : N_periods + ii + half_size_full + 1 ])
            elif(operation_type == 'max'):
                output_data[ii] = np.max(input_data_x3[N_periods + ii - half_size_full -1 : N_periods + ii + half_size_full + 1 ])
            elif(operation_type == 'sum'):
                output_data[ii] = (
                        np.sum(input_data_x3[N_periods + ii - half_size_full : N_periods + ii + half_size_full ]) 
                        + input_data_x3[N_periods + ii - half_size_full -1 ] *0.5 +  input_data_x3[N_periods + ii + half_size_full + 1 ] *0.5
                        ) 
        
    return output_data
##===========================================
def func_find_period (input_data):
    
    window_size = input_data['window_size']
    eff_window_size = copy.deepcopy(window_size) # If even go up to next odd number
    if eff_window_size == 2 * int (eff_window_size /2 ):  # check if even
        eff_window_size = eff_window_size + 1             # if so, add 1
    data = input_data['data']
    search_option = input_data['search_option']
    print_option = input_data['print_option']
    
    # -------------------------------------------------------------------------
    
    # Get the down-scaled data
    
    data_in_window = func_time_conversion(data, eff_window_size, 'mean')
    
    # -------------------------------------------------------------------------
    
    if search_option == 'max':
        
        center_index = int(np.argmax(data_in_window))
        value = np.max(data_in_window)
        
    elif search_option == 'min':

        center_index = int(np.argmin(data_in_window))
        value = np.min(data_in_window)

    # -------------------------------------------------------------------------
    # If interval would go over boundary, then move inteval
    if center_index < int(eff_window_size/2):
        center_index = int(eff_window_size/2)
    if center_index > len(data)- int(eff_window_size/2) - 1:
        center_index = len(data) - 1 - int(eff_window_size/2)

    # The same algorithm as in func_time_conversion()

    left_index = center_index - int(eff_window_size/2)
    right_index = center_index + int(eff_window_size/2)

    # -------------------------------------------------------------------------

    # output

    if print_option == 1:
        
        print ( 'center index = {}, value = {}'.format(center_index, value))
        print ( 'left index = {}, right index = {}'.format(left_index, right_index))

    output = {
        'value':        value,
        'left_index':   left_index,
        'right_index':  right_index,
        'center_index': center_index,
        }

    return output
##===========================================
def get_cost_contributions(base):
    info = base[0]
    inputs = base[1]
    results = base[2]
    # Costs over time
    wind_t = (np.multiply(inputs["FIXED_COST_WIND"], results["CAPACITY_WIND"]) +
             np.multiply(inputs["VAR_COST_WIND"], results["DISPATCH_WIND"]) )
    
    solar_t = (np.multiply(inputs["FIXED_COST_SOLAR"], results["CAPACITY_SOLAR"]) +
             np.multiply(inputs["VAR_COST_SOLAR"], results["DISPATCH_SOLAR"]) )
    
    pgp_t = (np.multiply(inputs["FIXED_COST_PGP_STORAGE"], results["CAPACITY_PGP_STORAGE"]) +
             np.multiply(inputs["FIXED_COST_TO_PGP_STORAGE"], results["CAPACITY_TO_PGP_STORAGE"]) +
             np.multiply(inputs["FIXED_COST_FROM_PGP_STORAGE"], results["CAPACITY_FROM_PGP_STORAGE"]) +
             np.multiply(inputs["VAR_COST_TO_PGP_STORAGE"], results["DISPATCH_TO_PGP_STORAGE"]) +
             np.multiply(inputs["VAR_COST_FROM_PGP_STORAGE"], results["DISPATCH_FROM_PGP_STORAGE"]) )
    
    batt_t = (np.multiply(inputs["FIXED_COST_STORAGE"], results["CAPACITY_STORAGE"]) +
             np.multiply(inputs["VAR_COST_TO_STORAGE"], results["DISPATCH_TO_STORAGE"]) +
             np.multiply(inputs["VAR_COST_FROM_STORAGE"], results["DISPATCH_FROM_STORAGE"]) )
    # Mean costs
    wind_m = np.mean(wind_t)
    solar_m = np.mean(solar_t)
    pgp_m = np.mean(pgp_t)
    batt_m = np.mean(batt_t)
    
#    print('System Cost Contributions =')
#    print(results['SYSTEM_COST'])
#    print('My calcs =')
#    calc_sys_cost = wind_m + solar_m + pgp_m + batt_m
#    print(calc_sys_cost)
    return wind_m, solar_m , pgp_m, batt_m
#=========================================
info = base[0]
inputs = base[1]
results = base[2]
#print('Base')
#print('=====================INFO====================================================================')
#print(info)
#print('=====================INPUTS====================================================================')
#print(inputs)
#print('=====================RESULTS====================================================================')
#print(results)


##===========================================================================================================
# (Figure 1: Dispatch Curves)
##============================================================================================================
# 5-day averaging
hours_to_avg = 5*24

demand_source = func_time_conversion(inputs['DEMAND_SERIES'], hours_to_avg)
wind_source = func_time_conversion(results['DISPATCH_WIND'], hours_to_avg)
solar_source = func_time_conversion(results['DISPATCH_SOLAR'], hours_to_avg)
batt_source = func_time_conversion(results['DISPATCH_FROM_STORAGE'], hours_to_avg)
pgp_source = func_time_conversion(results['DISPATCH_FROM_PGP_STORAGE'], hours_to_avg)

demand_sink = np.multiply(func_time_conversion(inputs['DEMAND_SERIES'], hours_to_avg), -1)
batt_sink = np.multiply(func_time_conversion(results['DISPATCH_TO_STORAGE'], hours_to_avg), -1)
pgp_sink = np.multiply(func_time_conversion(results['DISPATCH_TO_PGP_STORAGE'], hours_to_avg), -1)

#=================
#Electricity Sources AND Sinks
#=======================================================
#Figure size settings
#=======================================================

plt.rcParams.update({'axes.titlesize': 'large'})
plt.rcParams.update({'axes.labelsize': 'large'})

#import matplotlib.pylab as pylab
#params = {'legend.fontsize': 'large',
#          'figure.figsize': (12, 6), #7 3.5
#         'axes.labelsize': 'x-large',
#         'axes.titlesize':'x-large',
#         'xtick.labelsize':'large',
#         'ytick.labelsize':'large'}
#pylab.rcParams.update(params)

import matplotlib.pylab as pylab
params = {'legend.fontsize': 'large',
          'figure.figsize': (12, 6), #7 3.5
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'large',
         'ytick.labelsize':'large'}
pylab.rcParams.update(params)

date1 = datetime.datetime(2017, 1, 1, 0)
date2 = datetime.datetime(2017, 12, 31, 23)
delta = datetime.timedelta(hours=1)
quick_dates = drange(date1, date2, delta)
print(len(quick_dates))
x = quick_dates

y1 = np.vstack([wind_source, solar_source, batt_source, pgp_source  ])
pal1 = ['blue', 'orange', 'purple','pink']
labels1 = ["Wind", "Solar",  "Battery", "PGP"]

y2 = np.vstack([demand_sink, pgp_sink, batt_sink])
pal2 = ['black', 'pink','purple' ]
labels2 = ["Demand"]

#fig, ax = plt.subplots()
#fig, (ax1, ax2, ax3) = plt.subplots(2, 2, sharey=True)
fig = plt.figure()
ax3 = plt.subplot2grid((2, 4), (0, 0), colspan=2, rowspan=2)
#ax3 = plt.subplot(211)
ax3.stackplot(x, y1, colors=pal1, labels=labels1)
ax3.stackplot(x, y2, colors=pal2, labels=labels2)
ax3.plot(x, demand_source, '-', color='black', linewidth=1)
ax3.set_xlim(quick_dates[0], quick_dates[-1])
ax3.set_ylim(-4, 4)
#ax3.legend(loc='upper center', bbox_to_anchor=(1.2, 1.04))
chartBox = ax3.get_position()
ax3.set_position([chartBox.x0, chartBox.y0, chartBox.width*1, chartBox.height])

ax3.xaxis.set_major_locator(AutoDateLocator())
ax3.xaxis.set_major_formatter(DateFormatter('%b'))
ax3.xaxis.set_tick_params(direction='out', which='both')
ax3.yaxis.set_tick_params(direction='out', which='both')

ax3.yaxis.set_major_locator(ticker.MultipleLocator(1))
#plt.xticks(rotation=30, ha='right')
#ax3.set_ylabel('Electricity sources and sinks (kW)')
#ax3.set_xlabel('Time')
#fig.autofmt_xdate()
#ax3.set_xlabel('Expensive $\longleftrightarrow$ Cheap\nBaseline PGP capacity cost =\n 1x electrolyzer ($1,100/kW), \n1x fuel cell ($4,600/kW), \n 1x storage ($0.30/kWh)')
#plt.savefig('sources_sinks.eps', bbox_inches='tight')
#plt.show()
##=================
##=================
##=================
##=================
##=================


#from __future__ import division
#import os
#import sys
#import copy
#import numpy as np
#
#
##Find 5-day periods
###===========================================
##Import stuff
###===========================================
#import pickle
#import numpy as np
#from numpy import genfromtxt
#import matplotlib.pyplot as plt
#import matplotlib.gridspec as gridspec
#import matplotlib.ticker as ticker
#
#
#import datetime
#from matplotlib.dates import DayLocator, MonthLocator, HourLocator, AutoDateLocator, DateFormatter, drange
#from matplotlib.dates import MO, TU, WE, TH, FR, SA, SU, WeekdayLocator
#from numpy import arange
#from matplotlib.ticker import ScalarFormatter
#from matplotlib.ticker import FormatStrFormatter
#
#import matplotlib.cm as cm
#import matplotlib.mlab as mlab



##===========================================
def func_time_conversion (input_data, window_size, operation_type = 'mean'):
    
    # NOTE: THIS FUNCTION HAS ONLY BEEN VERIFIED FOR PROPER WRAP-AROUND BEHAVIOR
    #       FOR 'mean'
    # For odd windows sizes, easy. For even need to consider ends where you have half hour of data.

    N_periods = len(input_data)
    input_data_x3 = np.concatenate((input_data,input_data,input_data))
    
    half_size = window_size / 2.
    half_size_full = int(half_size) # number of full things for the mean

    output_data = np.zeros(len(input_data))
    
    for ii in range(len(output_data)):
        if half_size != float (half_size_full): # odd number, easy
            if (operation_type == 'mean'):
                output_data[ii] = np.sum(input_data_x3[N_periods + ii - half_size_full : N_periods + ii + half_size_full + 1 ])/ float(window_size)
            elif(operation_type == 'min'):
                output_data[ii] = np.min(input_data_x3[N_periods + ii - half_size_full : N_periods + ii + half_size_full + 1 ])
            elif(operation_type == 'max'):
                output_data[ii] = np.max(input_data_x3[N_periods + ii - half_size_full : N_periods + ii + half_size_full  + 1])
            elif(operation_type == 'sum'):
                output_data[ii] = np.sum(input_data_x3[N_periods + ii - half_size_full : N_periods + ii + half_size_full  + 1])
        else: # even number need to include half of last ones
            if (operation_type == 'mean'):
                output_data[ii] = ( np.sum(input_data_x3[N_periods + ii - half_size_full : N_periods + ii + half_size_full ])  \
                        + input_data_x3[N_periods + ii - half_size_full -1 ] *0.5 +  input_data_x3[N_periods + ii + half_size_full + 1 ] *0.5) / window_size
            elif(operation_type == 'min'):
                output_data[ii] = np.min(input_data_x3[N_periods + ii - half_size_full -1 : N_periods + ii + half_size_full + 1 ])
            elif(operation_type == 'max'):
                output_data[ii] = np.max(input_data_x3[N_periods + ii - half_size_full -1 : N_periods + ii + half_size_full + 1 ])
            elif(operation_type == 'sum'):
                output_data[ii] = (
                        np.sum(input_data_x3[N_periods + ii - half_size_full : N_periods + ii + half_size_full ]) 
                        + input_data_x3[N_periods + ii - half_size_full -1 ] *0.5 +  input_data_x3[N_periods + ii + half_size_full + 1 ] *0.5
                        ) 
        
    return output_data
##===========================================
def func_find_period (input_data):
    
    window_size = input_data['window_size']
    eff_window_size = copy.deepcopy(window_size) # If even go up to next odd number
    if eff_window_size == 2 * int (eff_window_size /2 ):  # check if even
        eff_window_size = eff_window_size + 1             # if so, add 1
    data = input_data['data']
    search_option = input_data['search_option']
    print_option = input_data['print_option']
    
    # -------------------------------------------------------------------------
    
    # Get the down-scaled data
    
    data_in_window = func_time_conversion(data, eff_window_size, 'mean')
    
    # -------------------------------------------------------------------------
    
    if search_option == 'max':
        
        center_index = int(np.argmax(data_in_window))
        value = np.max(data_in_window)
        
    elif search_option == 'min':

        center_index = int(np.argmin(data_in_window))
        value = np.min(data_in_window)

    # -------------------------------------------------------------------------
    # If interval would go over boundary, then move inteval
    if center_index < int(eff_window_size/2):
        center_index = int(eff_window_size/2)
    if center_index > len(data)- int(eff_window_size/2) - 1:
        center_index = len(data) - 1 - int(eff_window_size/2)

    # The same algorithm as in func_time_conversion()

    left_index = center_index - int(eff_window_size/2)
    right_index = center_index + int(eff_window_size/2)

    # -------------------------------------------------------------------------

    # output

    if print_option == 1:
        
        print ( 'center index = {}, value = {}'.format(center_index, value))
        print ( 'left index = {}, right index = {}'.format(left_index, right_index))

    output = {
        'value':        value,
        'left_index':   left_index,
        'right_index':  right_index,
        'center_index': center_index,
        }

    return output

##===========================================
    

 
##=====================================================


pickle_in = open('/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/Oct29_combos/Oct29_combos_Solar_PGPbatt.pickle', 'rb')

#pickle_in = open('/Users/jacquelinedowling/Documents/SEM-1.1_20190114/Output_Data/PGPtest5/PGPtest5_WindSolarPGPBatt_2015.pickle','rb')
base = pickle.load(pickle_in)
info = base[0]
inputs = base[1]
results = base[2]


demand_source = inputs['DEMAND_SERIES']
wind_source = results['DISPATCH_WIND']
solar_source = results['DISPATCH_SOLAR']
batt_source = results['DISPATCH_FROM_STORAGE']
pgp_source = results['DISPATCH_FROM_PGP_STORAGE']

demand_sink = inputs['DEMAND_SERIES']
batt_sink = results['DISPATCH_TO_STORAGE']
pgp_sink = results['DISPATCH_TO_PGP_STORAGE']


study_variable_dict_1 = {
        'window_size':      5*24,
        'data':             results['DISPATCH_FROM_PGP_STORAGE'], 
        'print_option':     0,
        'search_option':    'max'
        }
study_variable_dict_2 = {
        'window_size':      5*24,
        'data':             results['DISPATCH_FROM_STORAGE'], 
        'print_option':     0,
        'search_option':    'max'
        }
#study_variable_dict_3 = {
#        'window_size':      5*24,
#        'data':             results['DISPATCH_FROM_WIND'], 
#        'print_option':     0,
#        'search_option':    'max'
#        }


study_output_1 = func_find_period(study_variable_dict_1)  
study_output_2 = func_find_period(study_variable_dict_2)   

start_hour1 = study_output_1['left_index']
end_hour1 = study_output_1['right_index']

start_hour2 = study_output_2['left_index']
end_hour2 = study_output_2['right_index']
    
 
##=======================================================
# Figure size settings
##=======================================================

#plt.rcParams.update({'axes.titlesize': 'large'})
#plt.rcParams.update({'axes.labelsize': 'large'})
#
##import matplotlib.pylab as pylab
##params = {'legend.fontsize': 'large',
##          'figure.figsize': (7, 3.5),
##         'axes.labelsize': 'x-large',
##         'axes.titlesize':'large',
##         'xtick.labelsize':'large',
##         'ytick.labelsize':'large'}
##pylab.rcParams.update(params)


##=================================================
#Convert hours to datetime units for plotting
##=================================================


months = [0]
months.append(months[0] + 31*24)
months.append(months[1] + 28*24)
months.append(months[2] + 31*24)
months.append(months[3] + 30*24) 
months.append(months[4] + 31*24)
months.append(months[5] + 30*24)
months.append(months[6] + 31*24) 
months.append(months[7] + 31*24) 
months.append(months[8] + 30*24) 
months.append(months[9] + 31*24)  
months.append(months[10] + 30*24)   
months.append(months[11] + 31*24)   

#Start hours is 2015, 9, 6, 12
#End hours is 2015, 9, 11, 12
def convert_start_end (start_hour, end_hour):
    start_m = -1
    start_h = -1
    start_d = -1
    hours_remaining_in_month = -1
    for i, month in enumerate(months):
        if start_hour < month:
            start_m = i
            hours_remaining_in_month = start_hour - months[i-1]
            break
    
    if hours_remaining_in_month > 0:
        start_d = hours_remaining_in_month // 24 + 1
        start_h = hours_remaining_in_month % 24
    else:
        print("Error")
    
    print("start_m, start_d, start_h")
    print(start_m, start_d, start_h)

    end_m = -1
    end_h = -1
    end_d = -1
    hours_remaining_in_month = -1
    for i, month in enumerate(months):
        if end_hour < month:
            end_m = i
            hours_remaining_in_month = end_hour - months[i-1]
            break
    
    if hours_remaining_in_month > 0:
        end_d = hours_remaining_in_month // 24 + 1
        end_h = hours_remaining_in_month % 24
    else:
        print("Error")
    
    print("end_m, end_d, end_h")
    print(end_m, end_d, end_h)
    
    return start_m, start_d, start_h, end_m, end_d, end_h


##=================================================
# Two subplots, unpack the axes array immediately
#fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
#ax1.plot(x, y)
#ax1.set_title('Sharing Y axis')
#ax2.scatter(x, y)    
##=================================================
#PGP MAX 5-DAYS

print("PGP MAX 5-days")
times = convert_start_end (start_hour1-6, end_hour1-6)
#The -6 is to convert from UTC to CST

date1 = datetime.datetime(2018, times[0], times[1], times[2])
date2 = datetime.datetime(2018, times[3], times[4], times[5])
#date1 = datetime.datetime(2018, times[0], times[1], times[2] -6)
#date2 = datetime.datetime(2018, times[3], times[4], times[5] -6)

delta = datetime.timedelta(hours=1)
dates = drange(date1, date2, delta)
print(len(dates))

#x = np.arange(start_hour, end_hour)
x = dates
start_hour = start_hour1
end_hour = end_hour1

demand_source1 = demand_source[start_hour:end_hour]
wind_source1 = wind_source[start_hour:end_hour]
solar_source1 = solar_source[start_hour:end_hour]
pgp_source1 = pgp_source[start_hour:end_hour]
batt_source1 = batt_source[start_hour:end_hour]

demand_sink1 = np.multiply(demand_sink[start_hour:end_hour],-1)
batt_sink1 = np.multiply(batt_sink[start_hour:end_hour],-1)
pgp_sink1 = np.multiply(pgp_sink[start_hour:end_hour],-1)

y1 = np.vstack([ solar_source1, pgp_source1, batt_source1 ])
pal1 = [ 'orange', 'pink','purple']
labels1 = [ "Solar", "LDS", "Battery" ]

y2 = np.vstack([demand_sink1, pgp_sink1, batt_sink1])
pal2 = ['black', 'pink','purple' ]
labels2 = ["Demand"]

#fig, ax = plt.subplots()
ax1 = plt.subplot2grid((2, 4), (0, 3), colspan=1, rowspan=2)
#ax1 = plt.subplot(325)
ax1.stackplot(x, y1, colors=pal1, labels=labels1)
ax1.stackplot(x, y2, colors=pal2, labels=labels2)
ax1.plot(x, demand_source1, '-', color='black', linewidth=1)
#ax1.set_title('Max PGP dispatch')

ax1.set_xlim(dates[0], dates[-1])
ax1.set_ylim(-4, 4)
ax1.legend(loc='upper center', bbox_to_anchor=(1.45, 1.02))
chartBox = ax1.get_position()
ax1.set_position([chartBox.x0, chartBox.y0, chartBox.width*1, chartBox.height])
#ax.xaxis.set_major_locator(AutoDateLocator())
#ax.xaxis.set_major_locator(HourLocator(interval=24))
ax1.xaxis.set_major_locator(HourLocator(byhour=range(24),interval=24))
#ax1.xaxis.set_major_formatter(DateFormatter('%b %dth')) #This is CST!!! 7am
ax1.xaxis.set_major_formatter(DateFormatter('%b %d')) #This is CST!!! 7am
#ax1.xaxis.set_major_formatter(DateFormatter('%d-%b%H:%M')) #This is CST!!! 7am
plt.setp(ax1.get_yticklabels(), visible=False)

ax1.yaxis.set_major_locator(ticker.MultipleLocator(1))
plt.xticks(rotation=30, ha='right')
ax1.xaxis.set_tick_params(direction='out', which='both')
ax1.yaxis.set_tick_params(direction='out', which='both')
#ax1.set_ylabel('Electricity sources and sinks (kW)')
#ax1.set_xlabel('Time')

#fig.autofmt_xdate()
#ax.set_xlabel('Expensive $\longleftrightarrow$ Cheap\nBaseline PGP capacity cost =\n 1x electrolyzer ($1,100/kW), \n1x fuel cell ($4,600/kW), \n 1x storage ($0.30/kWh)')
#plt.savefig('5day_PGP.pdf', bbox_inches='tight')
#plt.show()

##=================================================
#Batt Max 5-DAYS

print("Batt MAX 5-days")
times = convert_start_end (start_hour2-6, end_hour2-6)
#The -6 is to convert from UTC to CST

#The +1 is because days count up from 1, not zero.
print ('times', times)
date1 = datetime.datetime(2015, times[0], times[1], times[2])
date2 = datetime.datetime(2015, times[3], times[4], times[5])
#date1 = datetime.datetime(2018, times[0], times[1], times[2] -6)
#date2 = datetime.datetime(2018, times[3], times[4], times[5] -6)
delta = datetime.timedelta(hours=1)
dates = drange(date1, date2, delta)
print(len(dates))

#x = np.arange(start_hour, end_hour)
x = dates
start_hour = start_hour2
end_hour = end_hour2

demand_source2 = demand_source[start_hour:end_hour]
wind_source2 = wind_source[start_hour:end_hour]
solar_source2 = solar_source[start_hour:end_hour]
pgp_source2 = pgp_source[start_hour:end_hour]
batt_source2 = batt_source[start_hour:end_hour]

demand_sink2 = np.multiply(demand_sink[start_hour:end_hour],-1)
batt_sink2 = np.multiply(batt_sink[start_hour:end_hour],-1)
pgp_sink2 = np.multiply(pgp_sink[start_hour:end_hour],-1)

y1 = np.vstack([wind_source2, solar_source2, pgp_source2, batt_source2 ])
pal1 = ['blue', 'orange', 'pink','purple']
labels1 = ["Wind", "Solar", "PGP", "Battery" ]

y2 = np.vstack([demand_sink2, pgp_sink2, batt_sink2])
pal2 = ['black', 'pink','purple' ]
labels2 = ["Demand"]

#fig, ax = plt.subplots()
ax2 = plt.subplot2grid((2, 4), (0, 2), colspan=1, rowspan=2)
#ax2 = plt.subplot(326, sharey=ax1)
ax2.stackplot(x, y1, colors=pal1, labels=labels1)
ax2.stackplot(x, y2, colors=pal2, labels=labels2)
ax2.plot(x, demand_source2, '-', color='black', linewidth=1)
#ax2.set_title('Max battery dispatch')
plt.setp(ax2.get_yticklabels(), visible=False)

ax2.set_xlim(dates[0], dates[-1])
ax2.set_ylim(-4, 4)
#ax2.legend(loc='upper center', bbox_to_anchor=(1.45, 1.02))
chartBox = ax2.get_position()
ax2.set_position([chartBox.x0, chartBox.y0, chartBox.width*1, chartBox.height])
#ax.xaxis.set_major_locator(AutoDateLocator())
#ax.xaxis.set_major_locator(HourLocator(interval=24))
ax2.xaxis.set_major_locator(HourLocator(byhour=range(24),interval=24))
#ax2.xaxis.set_major_formatter(DateFormatter('%d-%b-%H:%M')) #This is CST!!! Midnight
#ax2.xaxis.set_major_formatter(DateFormatter('%b %dth')) #This is CST!!! Midnight
ax2.xaxis.set_major_formatter(DateFormatter('%b %d')) #This is CST!!! Midnight


ax2.yaxis.set_major_locator(ticker.MultipleLocator(1))
plt.xticks(rotation=30, ha='right')
ax2.xaxis.set_tick_params(direction='out', which='both')
ax2.yaxis.set_tick_params(direction='out', which='both')
#ax2.set_ylabel('Electricity sources and sinks (kW)')
#ax2.set_xlabel('Time')
#fig.autofmt_xdate()
#ax.set_xlabel('Expensive $\longleftrightarrow$ Cheap\nBaseline PGP capacity cost =\n 1x electrolyzer ($1,100/kW), \n1x fuel cell ($4,600/kW), \n 1x storage ($0.30/kWh)')
#plt.savefig('5day_Batt.pdf', bbox_inches='tight')
#plt.show()





#fig.text(0.5, 0.04, 'Time', ha='center')
fig.text(0.06, 0.5, 'Electricty sources and sinks (kW)', va='center', rotation='vertical', size='xx-large' )
fig.text(.135, 0.84, 'a)', size='large')
fig.text(.54, 0.84, 'b)', size='large')
fig.text(.74, 0.84, 'c)', size='large')
#plt.savefig('figure1.pdf', bbox_inches='tight')
#plt.show()

plt.savefig('si/SI_dispatch_solaronly.pdf', bbox_inches='tight')
plt.show()