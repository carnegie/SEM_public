#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 16:58:58 2019

@author: jacquelinedowling
"""

##===================================================================
# #Multiple years
# Scroll to the very end to decide what pickle file you want to plot!

##===================================================================
#Importing and Image sizing
##===================================================================
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
#import pandas as pd

import os
import re
import matplotlib.patches as mpatches
import statistics
import itertools

#date1 = datetime.datetime(1980, 1, 1, 1)
#date2 = datetime.datetime(2016, 1, 1, 1)
#delta = datetime.timedelta(hours=1)
#dates = drange(date1, date2, delta)
#print(len(dates))


#print('Base')
#print('=====================INFO====================================================================')
#print(info)
#print('=====================INPUTS====================================================================')
#print(inputs)
#print('=====================RESULTS====================================================================')
#print(results)
##===================================================================
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
# Get what you need from each pickle file
##===================================================================

groupings = [1,2,3,4,5,6]
# Groupings are defined as years of optimization. Groupings represent single year runs, double, triple, 4, 5, and 6 year runs.
# We get data for each grouping here.



def get_group(grouping):

    unsorted_pickles = [] #collection of all pickle files for triple year runs for ex
    startyrs_list =[]
    
    path = "/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/Oct29_yrs/"
    for filename in os.listdir(path):
        if re.match("Oct29_yrs_"+str(grouping)+"yrs_\d+_\d+.pickle",filename):
            pickle_in = open(str(path)+ filename,"rb")
            base = pickle.load(pickle_in)
            inputs = base[1]
            start_year = int(inputs['START_YEAR'])
            
            unsorted_pickles.append(base)
            startyrs_list.append(start_year)
    sorted_pickles = [i for _,i in sorted(zip(startyrs_list, unsorted_pickles))]

    return sorted_pickles

#Example here
double_years = get_group(2)


# Here, result is defined as something you would plot, for ex, system cost, pgp_capacity etc.
# This function will return y values for
# result options inclue
#    #y values that are capacities
#    pgp_energy_cap = [] CAPACITY_PGP_STORAGE
#    batt_energy_cap = [] CAPACITY_STORAGE
#    wind_cap = [] CAPACITY_WIND
#    solar_cap =[] CAPACITY_SOLAR
#    
#    #y values that are costs
#    sys_cost = [] SYSTEM_COST
#    wind_cost = []
#    solar_cost = []
#    pgp_cost = []
#    batt_cost = []



natural_results = ['CAPACITY_PGP_STORAGE', 'CAPACITY_STORAGE', 'CAPACITY_WIND', 'CAPACITY_SOLAR',
                    'SYSTEM_COST']
def get_result(group, result_type):
    pickles = get_group(group)
    x_years = [] 
    y_values = []
    
    for i in range(0, len(pickles)):
        info = pickles[i][0] 
        inputs = pickles[i][1]
        results = pickles[i][2]
        #There will be two x values (start and end year). We'll duplicate the y value such that each x value matches a y value.
        x_years.append(inputs['START_YEAR'])
        y_values.append(results[str(result_type)])
        x_years.append(inputs['END_YEAR']+1) #the plus one is because the run ends at the end of this year
        y_values.append(results[str(result_type)])
    
    return x_years, y_values
#Example here
x_years, y_values = get_result(6, 'CAPACITY_PGP_STORAGE')


derived_results = ['wind_cost', 'solar_cost', 'pgp_cost', 'batt_cost']

def derive_result(group, result_type):
    pickles = get_group(group)
    x_years = [] 
    y_values = []
    
    for i in range(0, len(pickles)):
        info = pickles[i][0] 
        inputs = pickles[i][1]
        results = pickles[i][2]
        wind_cost, solar_cost , pgp_cost, batt_cost = get_cost_contributions(pickles[i])
        #There will be two x values (start and end year). We'll duplicate the y value such that each x value matches a y value.
        if result_type == 'wind_cost':
            cost = wind_cost
        if result_type == 'solar_cost':
            cost = solar_cost
        if result_type == 'pgp_cost':
            cost = pgp_cost
        if result_type == 'batt_cost':
            cost = batt_cost
        
        x_years.append(inputs['START_YEAR'])
        y_values.append(cost)
        x_years.append(inputs['END_YEAR']+1) #the plus one is because the run ends at the end of this year
        y_values.append(cost)
    
    return x_years, y_values

derive_result(6,'wind_cost')




# Now time for plotting!











###===================================================================
## Plot variable over 36 yrs
## data = (years, pgp_energy_capacity, batt_energy_capacity, sys_cost, wind_y, solar_y, pgp_y, batt_y)
## data =  0         1                          2               3        4       5        6      7

##===========================================
plt.rcParams.update({'axes.titlesize': 'large'})
plt.rcParams.update({'axes.labelsize': 'large'})

import matplotlib.pylab as pylab
params = {'legend.fontsize': 'medium',
          'figure.figsize': (10,12),
         'axes.labelsize': 'large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'large',
         'ytick.labelsize':'large'}
pylab.rcParams.update(params)
##===========================================
colorlist = (0,'red', 'gold', 'lime', 'aqua', 'blue', 'darkviolet')
fig = plt.figure()
###===================================================================

#PGP energy capacity

ax1 = plt.subplot2grid((3, 2), (0, 0), colspan=1, rowspan=1)
ax2 = ax1.twinx()
#pgp_energy_days = np.divide(pgp_energy_capacity, 24)
#ax1.plot(years, pgp_energy_capacity, '-', color='magenta', linewidth=1.6)
#ax2.plot(years, pgp_energy_days, '-',color='magenta', linewidth=1.6)
linelist = []
for i in range(0,7):
    x, y = get_result(i, 'CAPACITY_PGP_STORAGE')
    line = ax1.plot(x, y, '-', color=colorlist[i], linewidth=1.6)
    linelist.append(line)
    pgp_energy_days = np.divide(y, 24)
    ax2.plot(x, pgp_energy_days, '-',color=colorlist[i], linewidth=1.6)

#ax1.legend()
ax1.set_xlim(1980, 2020)
ax1.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax1.set_ylim(bottom=0)
ax2.set_ylim(bottom=0)
ax1.yaxis.set_major_locator(ticker.MultipleLocator(200))
ax1.yaxis.set_minor_locator(ticker.MultipleLocator(100))
ax2.yaxis.set_major_locator(ticker.MultipleLocator(10))
ax2.yaxis.set_minor_locator(ticker.MultipleLocator(5))


#ax1.set_xlabel('Year')
ax1.set_ylabel('Hours of mean U.S. demand')
ax2.set_ylabel('Days of mean U.S. demand')
#fig.autofmt_xdate()


#plt.legend(loc='upper center', bbox_to_anchor=(1.45, 1.02))
#plt.show()
#plt.legend((linelist[0], linelist[1], linelist[2], linelist[3], linelist[4], linelist[5]),('1', '2', '3', '4', '5', '6'))
#plt.savefig('years_batt_energy_cap.pdf', bbox_inches='tight')
#plt.show()
pos1 = ax1.get_position() # get the original position 
left, width = 0.1 , .9
bottom, height = 0.1, .9
right = left + width
top = bottom + height
# axes coordinates are 0,0 is bottom left and 1,1 is upper right
p = mpatches.Rectangle(
    (left, bottom), width, height,
    fill=False, transform=ax1.transAxes, clip_on=False, color='white')
ax1.add_patch(p)
ax1.text(left, bottom, 'a) LDS energy capacity', size = 'large',
        horizontalalignment='left',
        verticalalignment='bottom',
        transform=ax1.transAxes)

##=========================================
##=========================================
#Battery energy capacity
ax = plt.subplot2grid((3, 2), (0, 1), colspan=1, rowspan=1)

#ax.plot(years, batt_energy_capacity, '-', color='purple', linewidth=1.6)

for i in range(0,7):
    x, y = get_result(i, 'CAPACITY_STORAGE')
    ax.plot(x, y, '-', color=colorlist[i], linewidth=1.6)

ax.set_xlim(1980, 2020)
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax.set_ylim(bottom=0, top =3)
ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.5))

#ax.set_xlabel('Year')
ax.set_ylabel('Hours of mean U.S. demand')
#fig.autofmt_xdate()
#plt.savefig('years_batt_energy_cap.pdf', bbox_inches='tight')
#plt.show()
pos1 = ax.get_position() # get the original position 
left, width = 0.1 , .9
bottom, height = 0.1, .9
right = left + width
top = bottom + height
# axes coordinates are 0,0 is bottom left and 1,1 is upper right
p = mpatches.Rectangle(
    (left, bottom), width, height,
    fill=False, transform=ax.transAxes, clip_on=False, color='white')
ax.add_patch(p)
ax.text(left, bottom, 'b) Battery energy capacity', size = 'large',
        horizontalalignment='left',
        verticalalignment='bottom',
        transform=ax.transAxes)

###=========================================
##=========================================
#Wind power capacity
ax = plt.subplot2grid((3, 2), (1, 0), colspan=1, rowspan=1)

#ax.plot(years, batt_energy_capacity, '-', color='purple', linewidth=1.6)
for i in range(0,7):
    x, y = get_result(i, 'CAPACITY_WIND')
    ax.plot(x, y, '-', color=colorlist[i], linewidth=1.6)

ax.set_xlim(1980, 2020)
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax.set_ylim(bottom=0, top =3)
ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.5))

#ax.set_xlabel('Year')
ax.set_ylabel('1 = mean U.S. demand')
#fig.autofmt_xdate()
#plt.savefig('years_batt_energy_cap.pdf', bbox_inches='tight')
#plt.show()
pos1 = ax.get_position() # get the original position 
left, width = 0.1 , .9
bottom, height = 0.1, .9
right = left + width
top = bottom + height
# axes coordinates are 0,0 is bottom left and 1,1 is upper right
p = mpatches.Rectangle(
    (left, bottom), width, height,
    fill=False, transform=ax.transAxes, clip_on=False, color='white')
ax.add_patch(p)
ax.text(left, bottom, 'c) Wind power capacity', size = 'large',
        horizontalalignment='left',
        verticalalignment='bottom',
        transform=ax.transAxes)

###=========================================
##=========================================
#Solar power capacity
ax = plt.subplot2grid((3, 2), (1, 1), colspan=1, rowspan=1)

#ax.plot(years, batt_energy_capacity, '-', color='purple', linewidth=1.6)
for i in range(0,7):
    x, y = get_result(i, 'CAPACITY_SOLAR')
    ax.plot(x, y, '-', color=colorlist[i], linewidth=1.6)

ax.set_xlim(1980, 2020)
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax.set_ylim(bottom=0, top=3)
ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.5))

#ax.set_xlabel('Year')
ax.set_ylabel('1 = mean U.S. demand')
#fig.autofmt_xdate()
#plt.savefig('years_batt_energy_cap.pdf', bbox_inches='tight')
#plt.show()
pos1 = ax.get_position() # get the original position 
left, width = 0.1 , .9
bottom, height = 0.1, .9
right = left + width
top = bottom + height
# axes coordinates are 0,0 is bottom left and 1,1 is upper right
p = mpatches.Rectangle(
    (left, bottom), width, height,
    fill=False, transform=ax.transAxes, clip_on=False, color='white')
ax.add_patch(p)
ax.text(left, bottom, 'd) Solar power capacity', size = 'large',
        horizontalalignment='left',
        verticalalignment='bottom',
        transform=ax.transAxes)

###=========================================
##=========================================
#System cost
ax = plt.subplot2grid((3, 2), (2, 0), colspan=1, rowspan=1)

#ax.plot(years, batt_energy_capacity, '-', color='purple', linewidth=1.6)
for i in range(0,7):
    x, y = get_result(i, 'SYSTEM_COST')
    ax.plot(x, y, '-', color=colorlist[i], linewidth=1.6)

ax.set_xlim(1980, 2020)
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax.set_ylim(bottom=0, top=0.15)
ax.yaxis.set_major_locator(ticker.MultipleLocator(0.04))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.02))

#ax.set_xlabel('Year')
ax.set_ylabel('$/kWh')
#fig.autofmt_xdate()
#plt.savefig('years_batt_energy_cap.pdf', bbox_inches='tight')
#plt.show()

pos1 = ax.get_position() # get the original position 
left, width = 0.1 , .9
bottom, height = 0.1, .9
right = left + width
top = bottom + height
# axes coordinates are 0,0 is bottom left and 1,1 is upper right
p = mpatches.Rectangle(
    (left, bottom), width, height,
    fill=False, transform=ax.transAxes, clip_on=False, color='white')
ax.add_patch(p)
ax.text(left, bottom, 'e) Total system cost', size = 'large',
        horizontalalignment='left',
        verticalalignment='bottom',
        transform=ax.transAxes)

##=========================================
#Blank spot
ax = plt.subplot2grid((3, 2), (2, 1), colspan=1, rowspan=1)

#for i in range(0,6):
#    ax.plot(allyears[i], allcost[i], '-', color=colorlist[i], linewidth=1.6)

ax.set_xlim(1980, 2020)
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax.set_ylim(bottom=0, top=0.15)
ax.yaxis.set_major_locator(ticker.MultipleLocator(0.04))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.02))

ax.set_yticklabels([])
ax.set_xticklabels([])

ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)

ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)


pos1 = ax.get_position() # get the original position 
left, width = 0.1 , .9
bottom, height = 0.1, .9
right = left + width
top = bottom + height
# axes coordinates are 0,0 is bottom left and 1,1 is upper right
p = mpatches.Rectangle(
    (left, bottom), width, height,
    fill=False, transform=ax.transAxes, clip_on=False, color='white')
ax.add_patch(p)
ax.text(0.5*(left+right), 0.5*(bottom+1.4*top), 'Simulation\nperiod', size = 'large',
        horizontalalignment='center',
        verticalalignment='bottom',
        transform=ax.transAxes)


#ax.set_xlabel('Year')
ax.set_ylabel('Total system cost ($/kWh)', color = 'white')
#fig.autofmt_xdate()
#plt.savefig('years_batt_energy_cap.pdf', bbox_inches='tight')
#plt.show()
###=========================================

handlelist=[]
for i in range(1,7):
    patch = mpatches.Patch(color=colorlist[i], label=str(i)+'-year')
    handlelist.append(patch)

plt.legend(loc='right', bbox_to_anchor=(0.7, 0.5),handles=[handlelist[5],handlelist[4],handlelist[3],handlelist[2],handlelist[1],handlelist[0]])

###=========================================

plt.tight_layout()
plt.savefig('si/SI_multipleyears_caps.pdf', bbox_inches='tight')
plt.show()
#
###=========================================














# Same Figure except for plotting costs now





##===========================================
colorlist = (0,'red', 'gold', 'lime', 'aqua', 'blue', 'darkviolet')
fig = plt.figure()
###===================================================================

#PGP energy capacity

ax1 = plt.subplot2grid((3, 2), (0, 0), colspan=1, rowspan=1)
#ax2 = ax1.twinx()
#pgp_energy_days = np.divide(pgp_energy_capacity, 24)
#ax1.plot(years, pgp_energy_capacity, '-', color='magenta', linewidth=1.6)
#ax2.plot(years, pgp_energy_days, '-',color='magenta', linewidth=1.6)
linelist = []
for i in range(0,7):
    x, y = derive_result(i, 'pgp_cost')
    line = ax1.plot(x, y, '-', color=colorlist[i], linewidth=1.6)
    linelist.append(line)
#    pgp_energy_days = np.divide(y, 24)
#    ax2.plot(x, pgp_energy_days, '-',color=colorlist[i], linewidth=1.6)

#ax1.legend()
ax1.set_xlim(1980, 2020)
ax1.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax1.set_ylim(bottom=0, top=0.06)
ax1.yaxis.set_major_locator(ticker.MultipleLocator(0.02))
ax1.yaxis.set_minor_locator(ticker.MultipleLocator(0.01))
#ax2.set_ylim(bottom=0)


#ax1.set_xlabel('Year')
ax1.set_ylabel('LDS cost ($/kWh)')
#ax2.set_ylabel('(days of mean CONUS demand)')
#fig.autofmt_xdate()


#plt.legend(loc='upper center', bbox_to_anchor=(1.45, 1.02))
#plt.show()
#plt.legend((linelist[0], linelist[1], linelist[2], linelist[3], linelist[4], linelist[5]),('1', '2', '3', '4', '5', '6'))
#plt.savefig('years_batt_energy_cap.pdf', bbox_inches='tight')
#plt.show()
pos1 = ax1.get_position() # get the original position 
left, width = 0.1 , .9
bottom, height = 0.1, .9
right = left + width
top = bottom + height
# axes coordinates are 0,0 is bottom left and 1,1 is upper right
p = mpatches.Rectangle(
    (left, bottom), width, height,
    fill=False, transform=ax1.transAxes, clip_on=False, color='white')
ax1.add_patch(p)
ax1.text(left, bottom, 'a) LDS cost', size = 'large',
        horizontalalignment='left',
        verticalalignment='bottom',
        transform=ax1.transAxes)

##=========================================
##=========================================
#Battery energy capacity
ax = plt.subplot2grid((3, 2), (0, 1), colspan=1, rowspan=1)

#ax.plot(years, batt_energy_capacity, '-', color='purple', linewidth=1.6)

for i in range(0,7):
    x, y = derive_result(i, 'batt_cost')
    ax.plot(x, y, '-', color=colorlist[i], linewidth=1.6)

ax.set_xlim(1980, 2020)
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax.set_ylim(bottom=0, top=0.06)
ax.yaxis.set_major_locator(ticker.MultipleLocator(0.02))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.01))
#ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.0))

#ax.set_xlabel('Year')
ax.set_ylabel('Battery cost ($/kWh)')
#fig.autofmt_xdate()
#plt.savefig('years_batt_energy_cap.pdf', bbox_inches='tight')
#plt.show()
pos1 = ax.get_position() # get the original position 
left, width = 0.1 , .9
bottom, height = 0.1, .9
right = left + width
top = bottom + height
# axes coordinates are 0,0 is bottom left and 1,1 is upper right
p = mpatches.Rectangle(
    (left, bottom), width, height,
    fill=False, transform=ax.transAxes, clip_on=False, color='white')
ax.add_patch(p)
ax.text(left, top -.2, 'b) Battery cost', size = 'large',
        horizontalalignment='left',
        verticalalignment='bottom',
        transform=ax.transAxes)

###=========================================
##=========================================
#Wind power capacity
ax = plt.subplot2grid((3, 2), (1, 0), colspan=1, rowspan=1)

#ax.plot(years, batt_energy_capacity, '-', color='purple', linewidth=1.6)
for i in range(0,7):
    x, y = derive_result(i, 'wind_cost')
    ax.plot(x, y, '-', color=colorlist[i], linewidth=1.6)

ax.set_xlim(1980, 2020)
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax.set_ylim(bottom=0, top=0.06)
ax.yaxis.set_major_locator(ticker.MultipleLocator(0.02))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.01))
#ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.5))

#ax.set_xlabel('Year')
ax.set_ylabel('Wind cost ($/kWh)')
#fig.autofmt_xdate()
#plt.savefig('years_batt_energy_cap.pdf', bbox_inches='tight')
#plt.show()
pos1 = ax.get_position() # get the original position 
left, width = 0.1 , .9
bottom, height = 0.1, .9
right = left + width
top = bottom + height
# axes coordinates are 0,0 is bottom left and 1,1 is upper right
p = mpatches.Rectangle(
    (left, bottom), width, height,
    fill=False, transform=ax.transAxes, clip_on=False, color='white')
ax.add_patch(p)
ax.text(left, bottom, 'c) Wind cost', size = 'large',
        horizontalalignment='left',
        verticalalignment='bottom',
        transform=ax.transAxes)

###=========================================
##=========================================
#Solar power capacity
ax = plt.subplot2grid((3, 2), (1, 1), colspan=1, rowspan=1)

#ax.plot(years, batt_energy_capacity, '-', color='purple', linewidth=1.6)
for i in range(0,7):
    x, y = derive_result(i, 'solar_cost')
    ax.plot(x, y, '-', color=colorlist[i], linewidth=1.6)

ax.set_xlim(1980, 2020)
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax.set_ylim(bottom=0, top=0.06)
ax.yaxis.set_major_locator(ticker.MultipleLocator(0.02))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.01))
#ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.25))

#ax.set_xlabel('Year')
ax.set_ylabel('Solar cost ($/kWh)')
#fig.autofmt_xdate()
#plt.savefig('years_batt_energy_cap.pdf', bbox_inches='tight')
#plt.show()
pos1 = ax.get_position() # get the original position 
left, width = 0.1 , .9
bottom, height = 0.1, .9
right = left + width
top = bottom + height
# axes coordinates are 0,0 is bottom left and 1,1 is upper right
p = mpatches.Rectangle(
    (left, bottom), width, height,
    fill=False, transform=ax.transAxes, clip_on=False, color='white')
ax.add_patch(p)
ax.text(left, top -.2, 'd) Solar cost', size = 'large',
        horizontalalignment='left',
        verticalalignment='bottom',
        transform=ax.transAxes)

###=========================================
##=========================================
#System cost
ax = plt.subplot2grid((3, 2), (2, 0), colspan=1, rowspan=1)

#ax.plot(years, batt_energy_capacity, '-', color='purple', linewidth=1.6)
for i in range(0,7):
    x, y = get_result(i, 'SYSTEM_COST')
    ax.plot(x, y, '-', color=colorlist[i], linewidth=1.6)

ax.set_xlim(1980, 2020)
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax.set_ylim(bottom=0, top=0.13)
ax.yaxis.set_major_locator(ticker.MultipleLocator(0.04))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.02))

#ax.set_xlabel('Year')
ax.set_ylabel('Total system cost ($/kWh)')
#fig.autofmt_xdate()
#plt.savefig('years_batt_energy_cap.pdf', bbox_inches='tight')
#plt.show()

pos1 = ax.get_position() # get the original position 
left, width = 0.1 , .9
bottom, height = 0.1, .9
right = left + width
top = bottom + height
# axes coordinates are 0,0 is bottom left and 1,1 is upper right
p = mpatches.Rectangle(
    (left, bottom), width, height,
    fill=False, transform=ax.transAxes, clip_on=False, color='white')
ax.add_patch(p)
ax.text(left, bottom, 'e) Total system cost', size = 'large',
        horizontalalignment='left',
        verticalalignment='bottom',
        transform=ax.transAxes)

##=========================================
#Blank spot
ax = plt.subplot2grid((3, 2), (2, 1), colspan=1, rowspan=1)

#for i in range(0,6):
#    ax.plot(allyears[i], allcost[i], '-', color=colorlist[i], linewidth=1.6)

ax.set_xlim(1980, 2020)
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax.set_ylim(bottom=0, top=0.13)
ax.yaxis.set_major_locator(ticker.MultipleLocator(0.04))
ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.02))

ax.set_yticklabels([])
ax.set_xticklabels([])

ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)

ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)


pos1 = ax.get_position() # get the original position 
left, width = 0.1 , .9
bottom, height = 0.1, .9
right = left + width
top = bottom + height
# axes coordinates are 0,0 is bottom left and 1,1 is upper right
p = mpatches.Rectangle(
    (left, bottom), width, height,
    fill=False, transform=ax.transAxes, clip_on=False, color='white')
ax.add_patch(p)
ax.text(0.5*(left+right), 0.5*(bottom+1.4*top), 'Simulation\nperiod', size = 'large',
        horizontalalignment='center',
        verticalalignment='bottom',
        transform=ax.transAxes)


#ax.set_xlabel('Year')
ax.set_ylabel('Total system cost ($/kWh)', color = 'white')
#fig.autofmt_xdate()
#plt.savefig('years_batt_energy_cap.pdf', bbox_inches='tight')
#plt.show()
###=========================================

handlelist=[]
for i in range(1,7):
    patch = mpatches.Patch(color=colorlist[i], label=str(i)+'-year')
    handlelist.append(patch)

plt.legend(loc='right', bbox_to_anchor=(0.7, 0.5),handles=[handlelist[5],handlelist[4],handlelist[3],handlelist[2],handlelist[1],handlelist[0]])

###=========================================

plt.tight_layout()
plt.savefig('si/SI_multipleyears_costs.pdf', bbox_inches='tight')
plt.show()
#
###=========================================
#%%===================================================================
# Make the data bundle 'smult' for use in the boxplot.

# modify the earlier functions to work better with the boxplot
##===================================================================


natural_results = ['CAPACITY_PGP_STORAGE', 'CAPACITY_STORAGE', 'CAPACITY_WIND', 'CAPACITY_SOLAR',
                    'SYSTEM_COST']
def get_result_box(group, result_type):
    pickles = get_group(group)
    x_years = [] 
    y_values = []
    
    for i in range(0, len(pickles)):
        info = pickles[i][0] 
        inputs = pickles[i][1]
        results = pickles[i][2]
        #There will be two x values (start and end year). We'll duplicate the y value such that each x value matches a y value.
        x_years.append(inputs['START_YEAR'])
        y_values.append(results[str(result_type)])
#        x_years.append(inputs['END_YEAR']+1) #the plus one is because the run ends at the end of this year
#        y_values.append(results[str(result_type)])
    
    return x_years, y_values
#Example here
x_years, y_values = get_result(6, 'CAPACITY_PGP_STORAGE')


derived_results = ['wind_cost', 'solar_cost', 'pgp_cost', 'batt_cost']

def derive_result_box(group, result_type):
    pickles = get_group(group)
    x_years = [] 
    y_values = []
    
    for i in range(0, len(pickles)):
        info = pickles[i][0] 
        inputs = pickles[i][1]
        results = pickles[i][2]
        wind_cost, solar_cost , pgp_cost, batt_cost = get_cost_contributions(pickles[i])
        #There will be two x values (start and end year). We'll duplicate the y value such that each x value matches a y value.
        if result_type == 'wind_cost':
            cost = wind_cost
        if result_type == 'solar_cost':
            cost = solar_cost
        if result_type == 'pgp_cost':
            cost = pgp_cost
        if result_type == 'batt_cost':
            cost = batt_cost
        
        x_years.append(inputs['START_YEAR'])
        y_values.append(cost)
#        x_years.append(inputs['END_YEAR']+1) #the plus one is because the run ends at the end of this year
#        y_values.append(cost)
    
    return x_years, y_values

derive_result(4,'wind_cost')

#%%===================================================================
#Structure of the bundled data
##===================================================================

#smult is a single bundle including a list of lists

# The first level in is simulation groupings: 1, 2, 3, 4, 5, 6 yr periods
# smult[0] will get you data for 1-yr groupings
# smult[5] will get you data for 6-yr groupings
# But smult[i] is also a list of lists...


# Each simulation grouping contains 10 lists. This is the second level in.
#ind0: start_years,
#ind1: pgp_energy_capacity,
#ind2: batt_energy_capacity,
#ind3: sys_cost,
#ind4: wind_y,
#ind5: solar_y,
#ind6: pgp_y,
#ind7: batt_y,
#ind8: wind__power_capacity,
#ind9: solar__power_capcity

# smult[0][2] will get you batt_energy_capacity data for 1-yr groupings
# smult[5][8] will get you wind__power_capacity for 6-yr groupings


#%%===================================================================
# Use 

natural_results_box1 = ['CAPACITY_PGP_STORAGE', 'CAPACITY_STORAGE', 'SYSTEM_COST']
derived_results_box = ['wind_cost', 'solar_cost', 'pgp_cost', 'batt_cost']
natural_results_box2 = ['CAPACITY_WIND', 'CAPACITY_SOLAR']

#for i in range(0,7):
#    x, y = derive_result(i, 'batt_cost')

#for i in range(0,7):
#    x, y = get_result(i, 'SYSTEM_COST')

def get_group_data(grouping): # grouping =1 for ex if you want all the data for single yrs
    grouping_list = [] #for ex all data lists that are for single years
    x1,y1 = get_result_box(grouping,'CAPACITY_PGP_STORAGE') #chose random var
    grouping_list.append(x1) #we just need the start years in there
    for var1 in natural_results_box1:
        x1,y1 = get_result_box(grouping,var1)
        grouping_list.append(y1)
    for var2 in derived_results:
        x2,y2 = derive_result_box(grouping,var2)
        grouping_list.append(y2)
    for var1 in natural_results_box2:
        x1,y1 = get_result_box(grouping,var1)
        grouping_list.append(y1)
    return grouping_list
     
smult = []   
for i in range (1,7):
    grouping = get_group_data(i)
    smult.append(grouping)

#%%===================================================================
#  Make boxplot
# rectangular box plot
def boxplot(ax,listOfLists,xlabel,ylabel):
    bplot = ax.boxplot(listOfLists,
                       vert=True,   # vertical box aligmnent
                       patch_artist=True,   # fill with color
                       whis=1000000000) # make whiskers cover full range

    numCats = len(listOfLists)

    # fill with colors
    colors = ['chocolate','peru','burlywood','wheat','blanchedalmond','oldlace']
    
    for i in range(numCats):
        bplot['boxes'][i].set_facecolor( colors[np.mod(i,numCats)] )
        bplot['medians'][i].set_color( 'black' )
    
    
    # adding horizontal grid lines
    ax.yaxis.grid(True)
    ax.set_xticks([y+1 for y in range(numCats)], )
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    
    #ax.set_ylim([0,1.1*np.max(listOfLists)])
    ylimit = 1.1*max(map(lambda x: max(x), listOfLists))
    ax.set_ylim([0,ylimit])
    

smult_transpose = list(map(list, zip(*smult)))
smult_flat  = list(itertools.chain(*smult_transpose))

fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(12,9))

#boxplot(axes,smult_transpose[4])
items = ['Years','LDS energy capacity (hours)', 'Battery energy capacity (hours)', 'System cost ($/kWh)', 
         'Wind cost ($/kWh)', 'Solar cost ($/kWh)', 'LDS cost ($/kWh)', 'Battery cost ($/kWh)', 'Wind capacity (kW)', 'Solar capacity (kW)']

mapping = [0,3,4,5,6,7,8,9,1,2]
#mapping = [0,7,2,3,5,8,1,4,6,9]
for ii in range(len(smult_transpose)):
    if ii != 0:
        iii = mapping[ii]
        icol = np.mod(ii-1,3)
        irow = int((ii-1)/3)
        boxplot(axes[irow,icol],smult_transpose[iii],'Simulation period (years)',items[iii])

# add x-tick labels
#plt.setp(axes, xticks=[y+1 for y in range(len(smult_transpose))],
#             xticklabels=['1', '2', '3', '4','5','6'])
plt.tight_layout() 
plt.savefig('figs/figure4_boxplot.pdf')
plt.savefig('eps/figure4_boxplot.eps')
 
plt.show()


##===================================================================
#Method for getting stats
##===================================================================

def get_stats(list_):
    max_ = round(max(list_),3)
    p75 = round(np.percentile(list_, 75),3)
    mid = round(statistics.median(list_),3)
    p25 = round(np.percentile(list_, 25),3)
    min_ = round(min(list_),3)
#    print("list_: ", list_)
    print("max_: ", max_)
    print("75p: ", p75)
    print("mid: ", mid)
    print("25p: ", p25)
    print("min_: ", min_)
    spread = round(np.divide((max(list_)-min(list_)),min(list_))*100,0)
#    print('some times capacities were', spread,'percent larger than others')
#    print(spread, '%')
    
#    print("list_: ", list_)
    print( max_)
    print(p75)
    print(mid)
    print(p25)
    print(min_)
    print(spread, '%')
    stats = (max_, p75, mid ,p25 , min_, spread)
    return stats

##===================================================================
# Get stats for each variable you want
    
# data = years, pgp_energy_capacity, batt_energy_capacity, sys_cost, wind_y, solar_y, pgp_y, batt_y, wind_cap, solar_cap
# smult[i][1] = pgp_energy_capacity
# smult[i][2] = batt_energy_capacity
# smult[i][3] = system cost
# smult[i][-2] = wind_power_capacity
# smult[i][-1] = solar_power_capacity
    
# i loops through the groupings (1, 2, 3, 4, 5, 6 -yr periods)
    
#natural_results_box1 = ['CAPACITY_PGP_STORAGE', 'CAPACITY_STORAGE', 'SYSTEM_COST']
#derived_results_box = ['wind_cost', 'solar_cost', 'pgp_cost', 'batt_cost']
#natural_results_box2 = ['CAPACITY_WIND', 'CAPACITY_SOLAR']

##===================================================================
#Capacity table
#ind = (1,2, -2, -1, 3)
#rep = ('pgp_energy_cap', 'batt_energy_cap', 'wind_power_cap',
#       'solar_power_cap', 'total_sys_cost')
#
#for j in range(0,len(ind)):
#    print('')
#    print( rep[j])
#    for i in range(0,len(smult)):
#        print(i+1,'-year simulations:')
#        max_, p75, mid ,p25 , min_, spread = get_stats(smult[i][ind[j]])

##===================================================================
## Cost table
#ind = (6,7, 4, 5, 3)
#rep = ('pgp_cost', 'batt_cost', 'wind_cost',
#       'solar_cost', 'total_sys_cost')
#
#for j in range(0,len(ind)):
#    print('')
#    print( rep[j])
#    for i in range(0,len(smult)):
#        print(i+1,'-year simulations:')
#        max_, p75, mid ,p25 , min_, spread = get_stats(smult[i][ind[j]])
    

# END STATS SECTION
#%%
    # MAKE FIG FOR MAIN TEXT

##===========================================
plt.rcParams.update({'axes.titlesize': 'large'})
plt.rcParams.update({'axes.labelsize': 'large'})

import matplotlib.pylab as pylab
params = {'legend.fontsize': 'medium',
          'figure.figsize': (9,5),
         'axes.labelsize': 'large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'large',
         'ytick.labelsize':'large'}
pylab.rcParams.update(params)
##===========================================
colorlist = (0,'red', 'gold', 'lime', 'aqua', 'blue', 'darkviolet')    
fig = plt.figure()
###===================================================================

#PGP energy capacity

ax1 = plt.subplot2grid((1, 1), (0, 0), colspan=1, rowspan=1)
ax2 = ax1.twinx()
#pgp_energy_days = np.divide(pgp_energy_capacity, 24)
#ax1.plot(years, pgp_energy_capacity, '-', color='magenta', linewidth=1.6)
#ax2.plot(years, pgp_energy_days, '-',color='magenta', linewidth=1.6)
linelist = []
for i in range(0,7):
    x, y = get_result(i, 'CAPACITY_PGP_STORAGE')
    line = ax1.plot(x, y, '-', color=colorlist[i], linewidth=1.6)
    linelist.append(line)
    pgp_energy_days = np.divide(y, 24)
    ax2.plot(x, pgp_energy_days, '-',color=colorlist[i], linewidth=1.6)

#ax1.legend()
ax1.set_xlim(1980, 2020)
ax1.xaxis.set_major_locator(ticker.MultipleLocator(5))
ax1.set_ylim(bottom=0)
ax2.set_ylim(bottom=0)
ax1.yaxis.set_major_locator(ticker.MultipleLocator(200))
ax1.yaxis.set_minor_locator(ticker.MultipleLocator(100))
ax2.yaxis.set_major_locator(ticker.MultipleLocator(10))
ax2.yaxis.set_minor_locator(ticker.MultipleLocator(5))


#ax1.set_xlabel('Year')
ax1.set_ylabel('Hours of mean U.S. demand')
ax2.set_ylabel('Days of mean U.S. demand')
#fig.autofmt_xdate()


#plt.legend(loc='upper center', bbox_to_anchor=(1.45, 1.02))
#plt.show()
#plt.legend((linelist[0], linelist[1], linelist[2], linelist[3], linelist[4], linelist[5]),('1', '2', '3', '4', '5', '6'))
#plt.savefig('years_batt_energy_cap.pdf', bbox_inches='tight')
#plt.show()
pos1 = ax1.get_position() # get the original position 
left, width = 0.1 , .9
bottom, height = 0.1, .9
right = left + width
top = bottom + height
# axes coordinates are 0,0 is bottom left and 1,1 is upper right
p = mpatches.Rectangle(
    (left, bottom), width, height,
    fill=False, transform=ax1.transAxes, clip_on=False, color='white')
ax1.add_patch(p)
#ax1.text(left, bottom, 'a) Long duration storage capacity', size = 'large')
#        horizontalalignment='left',
#        verticalalignment='bottom',
#        transform=ax1.transAxes)

p = mpatches.Rectangle(
    (left, bottom), width, height,
    fill=False, transform=ax1.transAxes, clip_on=False, color='white')
ax1.add_patch(p)
ax1.text(.46*(left+right), 0.5*(bottom+.7*top), 'Simulation\nperiod', size = 'medium',
        horizontalalignment='center',
        verticalalignment='bottom',
        transform=ax.transAxes)

##=========================================
handlelist=[]
for i in range(1,7):
    patch = mpatches.Patch(color=colorlist[i], label=str(i)+'-year')
    handlelist.append(patch)

plt.legend(loc='right',bbox_to_anchor=(1, 0.17),handles=[handlelist[5],handlelist[4],handlelist[3],handlelist[2],handlelist[1],handlelist[0]])


##=========================================
##=========================================
##Battery energy capacity
#ax = plt.subplot2grid((2, 1), (1, 0), colspan=1, rowspan=2)
#
##ax.plot(years, batt_energy_capacity, '-', color='purple', linewidth=1.6)
#
#for i in range(0,7):
#    x, y = get_result(i, 'CAPACITY_STORAGE')
#    ax.plot(x, y, '-', color=colorlist[i], linewidth=1.6)
#
#ax.set_xlim(1980, 2020)
#ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
#ax.set_ylim(bottom=0, top =3)
#ax.set_ylabel('Hours of mean CONUS demand')
#ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
#ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.5))
#
##ax.set_xlabel('Year')
#
##fig.autofmt_xdate()
##plt.savefig('years_batt_energy_cap.pdf', bbox_inches='tight')
##plt.show()
#pos1 = ax.get_position() # get the original position 
#left, width = 0.1 , .9
#bottom, height = 0.1, .9
#right = left + width
#top = bottom + height
## axes coordinates are 0,0 is bottom left and 1,1 is upper right
#p = mpatches.Rectangle(
#    (left, bottom), width, height,
#    fill=False, transform=ax.transAxes, clip_on=False, color='white')
#ax.add_patch(p)
#ax.text(left, bottom, 'b) Battery energy capacity', size = 'large',
#        horizontalalignment='left',
#        verticalalignment='bottom',
#        transform=ax.transAxes)

###=========================================

##=========================================
##Blank spot
#ax = plt.subplot2grid((2, 3), (2, 0), colspan=1, rowspan=1)
#
##for i in range(0,6):
##    ax.plot(allyears[i], allcost[i], '-', color=colorlist[i], linewidth=1.6)
#
#ax.set_xlim(1980, 2020)
#ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
#ax.set_ylim(bottom=0, top=0.15)
#ax.yaxis.set_major_locator(ticker.MultipleLocator(0.04))
#ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.02))
#
#ax.set_yticklabels([])
#ax.set_xticklabels([])
#
#ax.get_xaxis().set_visible(False)
#ax.get_yaxis().set_visible(False)
#
#ax.spines['right'].set_visible(False)
#ax.spines['top'].set_visible(False)
#ax.spines['bottom'].set_visible(False)
#ax.spines['left'].set_visible(False)

##=========================================
##Blank spot
#ax = plt.subplot2grid((2, 3), (0, 2), colspan=1, rowspan=1)
#
##for i in range(0,6):
##    ax.plot(allyears[i], allcost[i], '-', color=colorlist[i], linewidth=1.6)
#
#ax.set_xlim(1980, 2020)
#ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
#ax.set_ylim(bottom=0, top=0.15)
#ax.yaxis.set_major_locator(ticker.MultipleLocator(0.04))
#ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.02))
#
#ax.set_yticklabels([])
#ax.set_xticklabels([])
#
#ax.get_xaxis().set_visible(False)
#ax.get_yaxis().set_visible(False)
#
#ax.spines['right'].set_visible(False)
#ax.spines['top'].set_visible(False)
#ax.spines['bottom'].set_visible(False)
#ax.spines['left'].set_visible(False)


#pos1 = ax.get_position() # get the original position 
#left, width = 0.1 , .9
#bottom, height = 0.1, .9
#right = left + width
#top = bottom + height
## axes coordinates are 0,0 is bottom left and 1,1 is upper right
#p = mpatches.Rectangle(
#    (left, bottom), width, height,
#    fill=False, transform=ax.transAxes, clip_on=False, color='white')
#ax.add_patch(p)
#ax.text(0.5*(left+right), 0.5*(bottom+1.4*top), 'Simulation\nperiod', size = 'large',
#        horizontalalignment='center',
#        verticalalignment='bottom',
#        transform=ax.transAxes)


#ax.set_xlabel('Year')
#ax.set_ylabel('Total system cost ($/kWh)', color = 'white')
#fig.autofmt_xdate()
#plt.savefig('years_batt_energy_cap.pdf', bbox_inches='tight')
#plt.show()
###=========================================

#handlelist=[]
#for i in range(1,7):
#    patch = mpatches.Patch(color=colorlist[i], label=str(i)+'-year')
#    handlelist.append(patch)
#
#plt.legend(loc='right', bbox_to_anchor=(0.7, 0.5),handles=[handlelist[5],handlelist[4],handlelist[3],handlelist[2],handlelist[1],handlelist[0]])

###=========================================

plt.tight_layout()
plt.savefig('figs/figure4d_multyrs.pdf', bbox_inches='tight')
plt.savefig('eps/figure4d_multyrs.eps', bbox_inches='tight')
plt.show()
#
###=========================================

        