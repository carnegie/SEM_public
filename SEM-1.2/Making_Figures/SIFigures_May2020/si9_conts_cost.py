#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 15:36:29 2019

@author: jacquelinedowling
"""
#Cost contribution figures
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
    
    sys_cost = []
    wind_y = []
    solar_y = []
    pgp_y = []
    batt_y = []
    
    path = '/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/Oct29_cont'
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
        
#    print('after sort',factors)

    for i in range(0,len(factors)):
        pickle_in = open(str(path)+ "/Oct29_cont_pgp1000batt"+ str(factors[i])+".pickle","rb")
        base = pickle.load(pickle_in)
        
        info = base[0]
        inputs = base[1]
        results = base[2]
        
        sys_cost.append(results['SYSTEM_COST'])
        
        wind, solar, pgp, batt = get_cost_contributions(base)
        wind_y.append(wind)
        solar_y.append(solar)
        pgp_y.append(pgp)
        batt_y.append(batt)
        
    values = np.divide(nums, 1000)
    data = (values, solar_y, wind_y, batt_y, pgp_y)
    return data

def get_data_fixed_batt():
    nums = []
    factors = []
    
    sys_cost = []
    wind_y = []
    solar_y = []
    pgp_y = []
    batt_y = []
    
    path = '/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/Oct29_cont'
#    path = "/Users/jacquelinedowling/SEM-1.1/Output_Data/PGPtest5_systemsensitivity"
    for filename in os.listdir(path):
#        PGPtest5_systemsensitivity_pgp0200batt0300.pickle
        if re.match("Oct29_cont_pgp\d+batt1000.pickle", filename):
            num = filename[-19:-15]
#            print('num', num)
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
        
        sys_cost.append(results['SYSTEM_COST'])
        
        wind, solar, pgp, batt = get_cost_contributions(base)
        wind_y.append(wind)
        solar_y.append(solar)
        pgp_y.append(pgp)
        batt_y.append(batt)
        
    values = np.divide(nums, 1000)
    data = (values, solar_y, wind_y, batt_y, pgp_y)
    return data

##==============================================
plt.rcParams.update({'axes.titlesize': 'large'})
plt.rcParams.update({'axes.labelsize': 'large'})

import matplotlib.pylab as pylab
params = {'legend.fontsize': 'large',
          'figure.figsize': (10, 10),
         'axes.labelsize': 'large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'large',
         'ytick.labelsize':'large'}
pylab.rcParams.update(params)

fig = plt.figure()
##==============================================
#Vary pgp
##==============================================
data1 = get_data_fixed_batt()

#
factors = data1[0]
sun_cost = data1[1]
wind_cost = data1[2]
batt_cost = data1[3]
pgp_cost = data1[4]

x = factors
y = np.vstack([wind_cost, sun_cost, batt_cost, pgp_cost])
pal = ['blue', 'orange', 'purple', 'pink']
labels = ["Wind", "Solar", "Battery", "LDS"]

#plotting Linear
ax3 = plt.subplot2grid((2, 3), (0, 0), colspan=2, rowspan=1)
ax3.stackplot(x, y, colors=pal, labels=labels)
ax3.axvline(x=1, color='red', linestyle='-', linewidth=1.5, label='Baseline LDS (1x)')
#ax3.legend(loc='upper center', bbox_to_anchor=(1.5, 1.03))
chartBox = ax3.get_position()
ax3.set_position([chartBox.x0, chartBox.y0, chartBox.width*1, chartBox.height])
ax3.set_xlim(4, 0)
ax3.set_ylim(0, 0.155)
ax3.yaxis.set_major_locator(ticker.MultipleLocator(0.05))
ax3.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax3.xaxis.set_minor_locator(ticker.MultipleLocator(0.5))
ax3.xaxis.set_major_formatter(FormatStrFormatter('%gx'))
#ax.set_title('Contribution of each technology\nto total system cost \n vs. PGP costs')
ax3.set_ylabel('P',color='white')
ax3.set_xlabel('LDS cost \n ')
#ax.set_xlabel('Expensive $\longleftrightarrow$ Cheap\nBaseline PGP capacity cost =\n 1x electrolyzer ($1,100/kW), \n1x fuel cell ($4,600/kW), \n 1x storage ($0.30/kWh)')
#plt.savefig('pgp_costcontributions_linear.pdf', bbox_inches='tight')
#plt.show()

#plotting log
ax4 = plt.subplot2grid((2, 3), (0, 2), colspan=1, rowspan=1)
ax4.stackplot(x, y, colors=pal, labels=labels)
ax4.axvline(x=1, color='red', linestyle='-', linewidth=1.7, label='Base case (1x)')
chartBox = ax4.get_position()
ax4.set_position([chartBox.x0, chartBox.y0, chartBox.width*0.6, chartBox.height])
ax4.legend(loc='upper center', bbox_to_anchor=(1.5, 1.02))
ax4.set_xscale('log')
ax4.invert_xaxis()
ax4.set_xlim(1.05, 0)
ax4.set_ylim(0, 0.155)
ax4.yaxis.set_major_locator(ticker.MultipleLocator(0.05))
ax4.xaxis.set_major_formatter(FormatStrFormatter('%.2fx'))
#ax.set_title('Contribution of each technology\nto total system cost \n vs. Battery costs ')
#ax4.set_ylabel('System cost contribution ($/kWh)')
ax4.set_xlabel('LDS cost\n ')
ax4.set_yticklabels([])
#ax.set_xlabel('Expensive $\longleftrightarrow$ Cheap\nBaseline PGP capacity cost = \n 1x electrolyzer ($1,100/kW), \n1x fuel cell ($4,600/kW), \n 1x storage ($0.30/kWh)')


##==============================================
#Vary batt
##==============================================
data = get_data_fixed_pgp()

#
factors = data[0]
sun_cost = data[1]
wind_cost = data[2]
batt_cost = data[3]
pgp_cost = data[4]

x = factors
y = np.vstack([wind_cost, sun_cost, pgp_cost,batt_cost ])
pal = ['blue', 'orange', 'pink','purple' ]
labels = ["Wind", "Solar", "LDS","Battery"]

#plotting Linear
ax1 = plt.subplot2grid((2, 3), (1, 0), colspan=2, rowspan=1)
ax1.stackplot(x, y, colors=pal, labels=labels)
ax1.axvline(x=1, color='red', linestyle='-', linewidth=1.5, label='Baseline battery (1x)')
#ax1.legend(loc='upper center', bbox_to_anchor=(1.5, 1.03))
chartBox = ax1.get_position()
ax1.set_position([chartBox.x0, chartBox.y0, chartBox.width*1, chartBox.height])
ax1.set_xlim(4, 0)
ax1.set_ylim(0, 0.155)
ax1.yaxis.set_major_locator(ticker.MultipleLocator(0.05))
ax1.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax1.xaxis.set_minor_locator(ticker.MultipleLocator(0.5))
ax1.xaxis.set_major_formatter(FormatStrFormatter('%gx'))
#ax.set_title('Contribution of each technology\nto total system cost \n vs. PGP costs')
ax1.set_ylabel('P',color='white')
ax1.set_xlabel('Battery cost \n More costly $\longrightarrow$ Less costly')
#ax.set_xlabel('Expensive $\longleftrightarrow$ Cheap\nBaseline PGP capacity cost =\n 1x electrolyzer ($1,100/kW), \n1x fuel cell ($4,600/kW), \n 1x storage ($0.30/kWh)')
#plt.savefig('batt_costcontributions_linear.pdf', bbox_inches='tight')
#plt.show()

#plotting log
ax2 = plt.subplot2grid((2, 3), (1, 2), colspan=1, rowspan=1)
ax2.stackplot(x, y, colors=pal, labels=labels)
ax2.axvline(x=1, color='red', linestyle='-', linewidth=1.7, label='Baseline battery (1x)')
chartBox = ax2.get_position()
ax2.set_position([chartBox.x0, chartBox.y0, chartBox.width*0.6, chartBox.height])
#ax2.legend(loc='upper center', bbox_to_anchor=(1.7, 1.03))
ax2.set_xscale('log')
ax2.invert_xaxis()
ax2.set_xlim(1.05, 0)
ax2.set_ylim(0, 0.155)
ax2.yaxis.set_major_locator(ticker.MultipleLocator(0.05))
ax2.xaxis.set_major_formatter(FormatStrFormatter('%.2fx'))
ax2.set_yticklabels([])
#ax.set_title('Contribution of each technology\nto total system cost \n vs. Battery costs ')
#ax2.set_ylabel('System cost contribution ($/kWh)')
ax2.set_xlabel('Battery cost \n ')
#ax.set_xlabel('Expensive $\longleftrightarrow$ Cheap\nBaseline PGP capacity cost = \n 1x electrolyzer ($1,100/kW), \n1x fuel cell ($4,600/kW), \n 1x storage ($0.30/kWh)')
#plt.savefig('batt_costcontributions_log.pdf', bbox_inches='tight')
#plt.show()



##==============================================
fig.text(0.01, 0.5, 'System cost contribution ($/kWh)', va='center', rotation='vertical', size='x-large' )
fig.text(.10, 0.96, 'a)', size='x-large')
fig.text(.68, 0.96, 'b)', size='x-large')
fig.text(.10, 0.47, 'c)', size='x-large')
fig.text(.68, 0.47, 'd)', size='x-large')
plt.tight_layout(pad=1, w_pad=2, h_pad=1.0)
plt.savefig('si/SI_conts_cost.pdf', bbox_inches='tight')
plt.show()