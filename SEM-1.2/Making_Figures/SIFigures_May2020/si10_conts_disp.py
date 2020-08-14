#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 00:03:35 2019

@author: jacquelinedowling
"""

#Power dispatched
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
def make_four_digits(num):
    if len(str(num))==1:
        string = '000'+ str(num)
        return string
    elif len(str(num))==2:
        string = '00'+ str(num)
        return string
    elif len(str(num))==3:
        string = '0'+ str(num)
        return string
    elif len(str(num))==4:
        string = str(num)
        return string

def get_data_fixed_pgp():
    nums = []
    factors = []
    
    demand_source = []
    wind_source = []
    solar_source = []
    pgp_source = []
    batt_source = []
    
    demand_sink = []
    pgp_sink = []
    batt_sink = []
    
    path = '/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/Oct29_cont'
#    path = '/Users/jacquelinedowling/SEM-1.1/Output_Data/PGPtest5_varybatt'
#    path = "/Users/jacquelinedowling/SEM-1.1/Output_Data/PGPtest5_systemsensitivity"
    for filename in os.listdir(path):
#        PGPtest5_systemsensitivity_pgp0200batt0300.pickle
        if re.match("Oct29_cont_pgp1000batt\d+.pickle", filename):
            num = filename[-11:-7]
            nums.append(int(num))
#    print('before sort',nums)
    nums.sort()
    for i in range(0,len(nums)):
        factor = make_four_digits(nums[i])
        factors.append(factor)   
    print('after sort',factors)

    for i in range(0,len(factors)):
        pickle_in = open(str(path)+ "/Oct29_cont_pgp1000batt"+ str(factors[i])+".pickle","rb")
        base = pickle.load(pickle_in)
        
        info = base[0]
        inputs = base[1]
        results = base[2]
        
        demand_source.append(np.mean(inputs['DEMAND_SERIES']))
        wind_source.append(np.mean(results['DISPATCH_WIND']))
        solar_source.append(np.mean(results['DISPATCH_SOLAR']))
        pgp_source.append(np.mean(results['DISPATCH_FROM_PGP_STORAGE']))
        batt_source.append(np.mean(results['DISPATCH_FROM_STORAGE']))
        
        demand_sink.append(np.mean(inputs['DEMAND_SERIES']))
        pgp_sink.append(np.mean(results['DISPATCH_TO_PGP_STORAGE']))
        batt_sink.append(np.mean(results['DISPATCH_TO_STORAGE']))
    
    values = np.divide(nums, 1000)
    sources = (demand_source, wind_source, solar_source, pgp_source, batt_source)
    sinks = (demand_sink, pgp_sink, batt_sink)
    data = (values, sources, sinks)
    return data

def get_data_fixed_batt():
    nums = []
    factors = []
    
    demand_source = []
    wind_source = []
    solar_source = []
    pgp_source = []
    batt_source = []
    
    demand_sink = []
    pgp_sink = []
    batt_sink = []

    path = '/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/Oct29_cont'    
#    path = '/Users/jacquelinedowling/SEM-1.1/Output_Data/PGPtest5_varypgp'
#    path = "/Users/jacquelinedowling/SEM-1.1/Output_Data/PGPtest5_systemsensitivity"
    for filename in os.listdir(path):
#        PGPtest5_systemsensitivity_pgp0200batt0300.pickle
        if re.match("Oct29_cont_pgp\d+batt1000.pickle", filename):
            num = filename[-19:-15]
            nums.append(int(num))
#    print('before sort',nums)
    nums.sort()
    for i in range(0,len(nums)):
        factor = make_four_digits(nums[i])
        factors.append(factor)   
#    print('after sort',factors)

    for i in range(0,len(factors)):
        pickle_in = open(str(path)+ "/Oct29_cont_pgp"+ str(factors[i])+"batt1000.pickle","rb")
        base = pickle.load(pickle_in)
        
        info = base[0]
        inputs = base[1]
        results = base[2]
        
        demand_source.append(np.mean(inputs['DEMAND_SERIES']))
        wind_source.append(np.mean(results['DISPATCH_WIND']))
        solar_source.append(np.mean(results['DISPATCH_SOLAR']))
        pgp_source.append(np.mean(results['DISPATCH_FROM_PGP_STORAGE']))
        batt_source.append(np.mean(results['DISPATCH_FROM_STORAGE']))
        
        demand_sink.append(np.mean(inputs['DEMAND_SERIES']))
        pgp_sink.append(np.mean(results['DISPATCH_TO_PGP_STORAGE']))
        batt_sink.append(np.mean(results['DISPATCH_TO_STORAGE']))
    
    values = np.divide(nums, 1000)
    sources = (demand_source, wind_source, solar_source, pgp_source, batt_source)
    sinks = (demand_sink, pgp_sink, batt_sink)
    data = (values, sources, sinks)
    return data

##==============================================
plt.rcParams.update({'axes.titlesize': 'large'})
plt.rcParams.update({'axes.labelsize': 'large'})

import matplotlib.pylab as pylab
params = {'legend.fontsize': 'large',
          'figure.figsize': (12, 10), #6,5
         'axes.labelsize': 'large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'large',
         'ytick.labelsize':'large'}
pylab.rcParams.update(params)

fig = plt.figure()
##==============================================
##==============================================
#Vary pgp
##==============================================
data = get_data_fixed_batt()

x = data[0]

demand_source = data[1][0]
wind_source = data[1][1]
solar_source = data[1][2]
pgp_source = data[1][3]
batt_source = data[1][4]

demand_sink = np.multiply(data[2][0],-1)
pgp_sink = np.multiply(data[2][1],-1)
batt_sink = np.multiply(data[2][2],-1)

y1 = np.vstack([wind_source, solar_source, batt_source, pgp_source  ])
pal1 = ['blue', 'orange', 'purple','pink']
labels1 = ["Wind", "Solar", "Battery","LDS"  ]

y2 = np.vstack([demand_sink, batt_sink,pgp_sink ])
pal2 = ['black', 'purple','pink' ]
labels2 = ["Demand"]

#fig, ax = plt.subplots()
ax2 = plt.subplot2grid((2, 3), (0, 0), colspan=2, rowspan=1)
#ax2 = plt.subplot(326, sharey=ax1)
ax2.stackplot(x, y1, colors=pal1, labels=labels1)
ax2.stackplot(x, y2, colors=pal2, labels=labels2)
ax2.plot(x, demand_source, '-', color='black', linewidth=1)
ax2.axvline(x=1, color='red', linestyle='-', linewidth=1.5, label='Baseline pgp (1x)')
#ax2.set_title('Max battery dispatch')
#plt.setp(ax2.get_yticklabels(), visible=False)

ax2.set_xlim(4, 0)
ax2.set_ylim(-1.4, 1.4)

ax2.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax2.xaxis.set_minor_locator(ticker.MultipleLocator(0.5))
ax2.xaxis.set_major_formatter(FormatStrFormatter('%gx'))
ax2.set_xlabel('LDS cost')
ax2.set_ylabel('P', color='white')
##============================================== (log)
ax2 = plt.subplot2grid((2, 3), (0, 2), colspan=1, rowspan=1)
#ax2 = plt.subplot(326, sharey=ax1)
ax2.stackplot(x, y1, colors=pal1, labels=labels1)
ax2.stackplot(x, y2, colors=pal2, labels=labels2)
ax2.plot(x, demand_source, '-', color='black', linewidth=1)
ax2.axvline(x=1, color='red', linestyle='-', linewidth=1.7, label='Base case (1x)')
ax2.legend(loc='upper center', bbox_to_anchor=(1.75, 1.02))
#ax2.set_title('Max battery dispatch')
#plt.setp(ax2.get_yticklabels(), visible=False)
ax2.set_xscale('log')
ax2.invert_xaxis()
ax2.set_xlim(1.05, 0)
ax2.set_ylim(-1.4, 1.4)
ax2.set_yticklabels([])

ax2.xaxis.set_major_formatter(FormatStrFormatter('%.2fx'))
ax2.set_xlabel('LDS cost')

##==============================================
#Vary batt
##==============================================
data = get_data_fixed_pgp()

x = data[0]

demand_source = data[1][0]
wind_source = data[1][1]
solar_source = data[1][2]
pgp_source = data[1][3]
batt_source = data[1][4]

demand_sink = np.multiply(data[2][0],-1)
pgp_sink = np.multiply(data[2][1],-1)
batt_sink = np.multiply(data[2][2],-1)

y1 = np.vstack([wind_source, solar_source, pgp_source, batt_source ])
pal1 = ['blue', 'orange', 'pink','purple']
labels1 = ["Wind", "Solar", "PGP", "Battery" ]

y2 = np.vstack([demand_sink, pgp_sink, batt_sink])
pal2 = ['black', 'pink','purple' ]
labels2 = ["Demand"]

#fig, ax = plt.subplots()
ax2 = plt.subplot2grid((2, 3), (1, 0), colspan=2, rowspan=1)
#ax2 = plt.subplot(326, sharey=ax1)
ax2.stackplot(x, y1, colors=pal1, labels=labels1)
ax2.stackplot(x, y2, colors=pal2, labels=labels2)
ax2.plot(x, demand_source, '-', color='black', linewidth=1)
ax2.axvline(x=1, color='red', linestyle='-', linewidth=1.5, label='Baseline battery (1x)')
#ax2.set_title('Max battery dispatch')
#plt.setp(ax2.get_yticklabels(), visible=False)

ax2.set_xlim(4, 0)
ax2.set_ylim(-1.4, 1.4)

ax2.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax2.xaxis.set_minor_locator(ticker.MultipleLocator(0.5))
ax2.xaxis.set_major_formatter(FormatStrFormatter('%gx'))
ax2.set_xlabel('Battery cost\n More costly $\longrightarrow$ Less costly')
ax2.set_ylabel('P', color='white')

##============================================== (log)
ax2 = plt.subplot2grid((2, 3), (1, 2), colspan=1, rowspan=1)
#ax2 = plt.subplot(326, sharey=ax1)
ax2.stackplot(x, y1, colors=pal1, labels=labels1)
ax2.stackplot(x, y2, colors=pal2, labels=labels2)
ax2.plot(x, demand_source, '-', color='black', linewidth=1)
ax2.axvline(x=1, color='red', linestyle='-', linewidth=1.7, label='Baseline battery (1x)')
#ax2.set_title('Max battery dispatch')
#plt.setp(ax2.get_yticklabels(), visible=False)
ax2.set_xscale('log')
ax2.invert_xaxis()
ax2.set_xlim(1.05, 0)
ax2.set_ylim(-1.4, 1.4)
ax2.set_yticklabels([])

ax2.xaxis.set_major_formatter(FormatStrFormatter('%.2fx'))
ax2.set_xlabel('Battery cost')






##==============================================
##==============================================
fig.text(0.01, 0.5, 'Electricity sources and sinks (kW)', va='center', rotation='vertical', size='x-large' )
fig.text(.09, 0.96, 'a)', size='x-large')
fig.text(.55, 0.96, 'b)', size='x-large')
fig.text(.09, 0.48, 'c)', size='x-large')
fig.text(.55, 0.48, 'd)', size='x-large')
plt.tight_layout()
#plt.tight_layout(pad=1, w_pad=2, h_pad=1.0)
plt.savefig('si/SI_conts_disp.pdf', bbox_inches='tight')
plt.show()



