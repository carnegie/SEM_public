#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 10:10:50 2020

@author: jacquelinedowling
"""

##===========================================
#Figure 3, Simple Combos with NGCCS
##===========================================
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



###=========================================
#System Cost Calculations
##=========================================
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
    
    ccs_t = (np.multiply(inputs["FIXED_COST_NATGAS_CCS"], results["CAPACITY_NATGAS_CCS"]) +
             np.multiply(inputs["VAR_COST_NATGAS_CCS"], results["DISPATCH_NATGAS_CCS"]) )
   

    # Mean costs
    wind_m = np.mean(wind_t)
    solar_m = np.mean(solar_t)
    pgp_m = np.mean(pgp_t)
    batt_m = np.mean(batt_t)
    ccs_m = np.mean(ccs_t)
    
#    print('System Cost Contributions =')
#    print(results['SYSTEM_COST'])
#    print('My calcs =')
#    calc_sys_cost = wind_m + solar_m + pgp_m + batt_m
#    print(calc_sys_cost)
    return wind_m, solar_m , pgp_m, batt_m, ccs_m
##======================================================================================================
# (Figure 3) Bar graph- simple combos 
##======================================================================================================


import matplotlib.pylab as pylab
params = {'legend.fontsize': 'medium',
          'figure.figsize': (6, 3),
         'axes.labelsize': 'large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'small',
         'ytick.labelsize':'large'}
pylab.rcParams.update(params)
##===========================================
#Looking at data in Simple Combinations Run
##===========================================
cases = ('Solar_batt', 'Solar_PGP', 'Solar_PGPbatt',
         'Wind_batt', 'Wind_PGP', 'Wind_PGPbatt',
         'SolarWind_batt', 'SolarWind_PGP', 'SolarWind_PGPbatt')
case = cases[0]

#/Users/jacquelinedowling/SEM-1.1/Output_Data/PGPtest5_simplecombos_fixed/PGPtest5_simplecombos_fixed_Solar_batt.pickle
pickle_in = open('/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/Oct29_combos_ngccs/Oct29_combos_ngccs_SolarWind_PGPbatt.pickle', 'rb')
#pickle_in = open('/Users/jacquelinedowling/SEM-1.1/Output_Data/PGPtest5_simplecombos_fixed/PGPtest5_simplecombos_fixed_Solar_PGP.pickle','rb')
base = pickle.load(pickle_in)
info = base[0]
inputs = base[1]
results = base[2]

print('Base')
print('=====================INFO====================================================================')
print(info)
print('=====================INPUTS====================================================================')
print(inputs)
print('=====================RESULTS====================================================================')
print(results)
#====================================================================
# Get what you need from each pickle file
##===================================================================

sys_costs = []
wind_costs = []
solar_costs = []
pgp_costs = []
batt_costs = []
ccs_costs = []
cases = ('Solar_batt', 'Solar_PGP', 'Solar_PGPbatt',
         'Wind_batt', 'Wind_PGP', 'Wind_PGPbatt',
         'SolarWind_batt', 'SolarWind_PGP', 'SolarWind_PGPbatt')

#Need to rerun these! The input file is messed up.

for case in cases:
#    pickle_in = open("/Users/jacquelinedowling/SEM-1.1/Output_Data/PGPtest5_simplecombos_tanks/PGPtest5_simplecombos_tanks_" + case + ".pickle","rb")
#    pickle_in = open("/Users/jacquelinedowling/SEM-1.1/Output_Data/PGPtest5_simplecombos_fixed/PGPtest5_simplecombos_fixed_" + case + ".pickle","rb")
    pickle_in = open('/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/Oct29_combos_ngccs/Oct29_combos_ngccs_' + case + '.pickle', 'rb')
    print(case)
    base = pickle.load(pickle_in)
    info = base[0]
    inputs = base[1]
    results = base[2]
    sys_costs.append(results['SYSTEM_COST'])
    wind_c, solar_c , pgp_c, batt_c, ccs_c = get_cost_contributions(base)
    wind_costs.append(wind_c)
    solar_costs.append(solar_c)
    pgp_costs.append(pgp_c)
    batt_costs.append(batt_c)
    ccs_costs.append(ccs_c)
    

#my_data = genfromtxt('BaseBinaries_NoUnmetDemand_iso.csv', delimiter=',')
#
#print(my_data.shape)
#my_data = my_data.transpose()
#print(my_data.shape)
#
#solar = my_data[2]
#wind = my_data[3]
#battery = my_data[4]
#pgp = my_data[5]
#print(my_data[6])
##=========================================

#Prep for plotting, add blank spaces between each category
data = (solar_costs, wind_costs, ccs_costs, batt_costs, pgp_costs) 
newdata = []

for i in data:
    insert1 = np.insert(i, 3, 0)
    newlist = np.insert(insert1, 7, 0)
    newdata.append(newlist)


N = 11
ind = np.arange(N)    # the x locations for the groups
width = 0.6       # the width of the bars: can also be len(x) sequence

#dataset1 = np.array(solar)
#dataset2 = np.array(wind)
#dataset3 = np.array(battery)
#dataset4 = np.array(pgp)

dataset1 = np.array(newdata[0])
dataset2 = np.array(newdata[1])
dataset3 = np.array(newdata[2])
dataset4 = np.array(newdata[3])
dataset5 = np.array(newdata[4])

fig = plt.figure()

p1 = plt.bar(ind, dataset1, width, color='orange')
p2 = plt.bar(ind, dataset2, width, bottom=dataset1, color='blue')
p3 = plt.bar(ind, dataset3, width, bottom=dataset1+dataset2, color='green')
p4 = plt.bar(ind, dataset4, width, bottom=dataset1+dataset2+dataset3,
             color='purple')
p5 = plt.bar(ind, dataset5, width, bottom=dataset1+dataset2+dataset3+dataset4,
             color='pink')

plt.ylabel('System cost ($/kWh) ')
#plt.title('Simple combinations of base case components\n')
plt.xticks(rotation=45, ha='right')



ax2 = plt.axes()
xticks = ax2.xaxis.get_major_ticks()
xticks[3].label1.set_visible(False)
xticks[7].label1.set_visible(False)
ax2.set_ylim(0, 0.13)
ax2.yaxis.set_major_locator(ticker.MultipleLocator(0.02))
#ax2.yaxis.set_minor_locator(ticker.MultipleLocator(0.025))
ax2.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
plt.xticks(ind, ('Battery only', 'LDS only', 'LDS+Battery', '',
                 'Battery only', 'LDS only', 'LDS+Battery', '',
                 'Battery only', 'LDS only', 'LDS+Battery'))
#plt.yticks(np.arange(0, 81, 10))
plt.legend((p1[0], p2[0], p3[0], p4[0], p5[0] ), ('Solar', 'Wind', 'NatgasCCS','Battery','LDS' ),loc='upper center', bbox_to_anchor=(1.15, 1.03))

#chartBox = ax2.get_position()
#ax2.set_position([chartBox.x0, chartBox.y0, chartBox.width*1, chartBox.height])
#ax2.legend(loc='upper center', bbox_to_anchor=(1.45, 1.02))

# Add xticks on the middle of the group bars
#plt.xlabel('Simulations\n Vary generation: Solar, Wind, Solar+Wind \nVary storage: PGP, Battery, PGP+Battery')
fig.text(.25, 0.77, 'NatgasCCS\nSolar', size='medium', ha = 'center')
fig.text(.51, 0.77, 'NatgasCCS\nWind', size='medium',ha = 'center')
fig.text(.71, 0.77, 'NatgasCCS\nWind+Solar', size='medium')


plt.savefig('si/SI_combos_ngccs.pdf', bbox_inches='tight')

plt.show()
