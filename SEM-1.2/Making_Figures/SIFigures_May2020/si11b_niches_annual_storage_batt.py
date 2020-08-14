#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 14 17:50:50 2019

@author: jacquelinedowling
"""
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

import os
import re
import matplotlib.patches as mpatches

import math

date1 = datetime.datetime(2018, 1, 1, 0)
date2 = datetime.datetime(2019, 1, 1, 0)
delta = datetime.timedelta(hours=1)
dates = drange(date1, date2, delta)
print(len(dates))
##===========================================
#Read in Base Case: PGP Batteries, Wind Solar
##===========================================

#pickle_in = open('/Users/jacquelinedowling/Documents/SEM-1.1_20190114/Output_Data/PGPtest5/PGPtest5_WindSolarPGPBatt_2015.pickle','rb')
#base = pickle.load(pickle_in)
#info = base[0]
#inputs = base[1]
#results = base[2]

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

def get_data_fixed_pgp(pgp):
    nums = []
    factors = []

    batt_energy = [] 
    pgp_energy = [] 
    
    path = '/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/Oct29_syscont'
#    path = "/Users/jacquelinedowling/SEM-1.1/Output_Data/PGPtest5_systemsensitivity"
    for filename in os.listdir(path):
#        PGPtest5_systemsensitivity_pgp0200batt0300.pickle
        if re.match("Oct29_syscont_pgp"+str(pgp)+"batt\d+.pickle", filename):
            num = filename[-11:-7]
            nums.append(int(num))
#    print('before sort',nums)
    nums.sort()
    for i in range(0,len(nums)):
        factor = make_four_digits(nums[i])
        factors.append(factor)   
#    print('after sort',factors)

    for i in range(0,len(factors)):
        pickle_in = open(str(path)+ "/Oct29_syscont_pgp"+str(pgp)+"batt"+ str(factors[i])+".pickle","rb")
        base = pickle.load(pickle_in)
        
        info = base[0]
        inputs = base[1]
        results = base[2]
        if results['SYSTEM_COST'] == -1:
#            costs.append(None)
            print('Failed to solve:',"pgp"+str(pgp)+"batt"+ str(factors[i]))
        else:
            batt_energy.append(results["ENERGY_STORAGE"])
            pgp_energy.append(results["ENERGY_PGP_STORAGE"])

    name = 'pgp'+str(pgp)
    values = np.divide(nums, 1000)
    data = (name, values, pgp_energy, batt_energy)
    return data

#strings= ['0000', '0007', '0010', '0020', '0050', '0067', '0100', '0150', '0200', '0250', '0300', '0350', '0400', '0450', '0500', '0550', '0600', '0650', '0700', '0750', '0800', '0850', '0900', '0950', '1000']



data = get_data_fixed_pgp('1000')
names = data[0]
values = data[1]
pgp_e = data[2]
batt_e = data[3]

times_cheaper = []
for i in range(0, len(values)):
    if values[i] == 0:
        times_cheaper.append(None)
    else:
        times_cheaper.append(math.ceil(1 / values[i]))


#1/10
#Out[193]: 0.1
#
#1/15
#Out[194]: 0.06666666666666667
#
#1/20
#Out[195]: 0.05
#
#1/50
#Out[196]: 0.02


##======================================================================================================
# (Figure 2) Storage time series plots 
##======================================================================================================
#=======================================================
# Figure size settings
#=======================================================

plt.rcParams.update({'axes.titlesize': 'large'})
plt.rcParams.update({'axes.labelsize': 'large'})

import matplotlib.pylab as pylab
params = {'legend.fontsize': 'large',
          'figure.figsize': (16, 8),
         'axes.labelsize': 'large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'large',
         'ytick.labelsize':'large'}
pylab.rcParams.update(params)

#take in the data
#batt_energy = results["ENERGY_STORAGE"]
#pgp_energy = results["ENERGY_PGP_STORAGE"]

fig = plt.figure()
#===================================================
#===================================================
#===================================================
toplot = [6,4,3,2] #6,5,4,3
plots = len(toplot)
for i in range(0,plots):
    ax1 = plt.subplot2grid((2, plots), (0, i), colspan=1, rowspan=1)
    name = times_cheaper[toplot[i]]
    pgp_energy = pgp_e[toplot[i]]
    batt_energy = batt_e[toplot[i]]
    
    #ax2 = plt.subplot2grid((1, 2), (0, 0), colspan=1, rowspan=1)
    #ax2 = plt.subplot2grid((1, 2), (0, 0), colspan=1, rowspan=1)
    #=========================================
    #PGP energy
    pgp_energy_days = pgp_energy/24
    #fig, ax1 = plt.subplots() 
    ax2 = ax1.twinx()
    ax1.plot_date(dates, pgp_energy, '-', color='pink', linewidth=1.2)
    ax2.plot_date(dates, pgp_energy_days, '-',color='pink', linewidth=1.2)
    
    ax1.fill_between(dates, pgp_energy, interpolate=True, color='pink')
    ax2.fill_between(dates, pgp_energy_days, interpolate=True, color='pink')
    
    ax1.set_title(str(name)+ 'x cheaper battery')
    ax1.set_xlim(dates[0], dates[-1])
    ax1.set_ylim(top= 350, bottom=0)
    ax2.set_ylim(top= 14.58, bottom=0)
    ax1.yaxis.set_major_locator(ticker.MultipleLocator(100))
    ax2.yaxis.set_major_locator(ticker.MultipleLocator(5))
    ax1.xaxis.set_major_locator(MonthLocator(interval = 2))
    ax1.xaxis.set_major_formatter(DateFormatter('%b-%Y'))
    
    #ax1.set_xlabel('Time')
    if i == 0:
        ax1.set_ylabel('Energy in LDS storage \n Hours of mean U.S. demand')
        plt.setp(ax2.get_yticklabels(), visible=False)
    elif i == (plots-1):
        ax2.set_ylabel('Days of mean CONUS demand')
        plt.setp(ax1.get_yticklabels(), visible=False)
    else:
        plt.setp(ax1.get_yticklabels(), visible=False)
        plt.setp(ax2.get_yticklabels(), visible=False)
    #fig.autofmt_xdate()
    #plt.savefig('pgp_energy.eps', bbox_inches='tight')
    #plt.show()
    
    
    #=========================================
    #Battery energy, year
    ax3 = plt.subplot2grid((2, plots), (1, i), colspan=1, rowspan=1)
    #fig, ax = plt.subplots()
    ax3.plot_date(dates, batt_energy, '-',color='purple', linewidth=0.5)
    ax3.set_ylim(top=350, bottom= 0)  # adjust the top leaving bottom unchanged
    ax3.set_xlim(dates[0], dates[-1])
    ax3.yaxis.set_major_locator(ticker.MultipleLocator(100))
    ax3.yaxis.set_minor_locator(ticker.MultipleLocator(25))
    ax3.fill_between(dates, batt_energy, interpolate=True, color='purple')
    #ax.set_title('Energy Stored in Batteries, 2015 View')
    
    if i == 0:
        ax3.set_ylabel('Energy in battery storage \n Hours of mean U.S. demand')
    else:
        plt.setp(ax3.get_yticklabels(), visible=False)
    
#    ax3.set_ylabel('Energy in battery storage \n (hours of mean CONUS demand)')
#    ax3.yaxis.set_major_locator(ticker.MultipleLocator(1))
#    ax3.yaxis.set_minor_locator(ticker.MultipleLocator(0.5))
    
    #ax3.set_xlabel('Time')
    ax3.xaxis.set_major_locator(MonthLocator(interval = 2))
    ax3.xaxis.set_major_formatter(DateFormatter('%b-%Y'))
    
    #ax.xaxis.set_minor_locator(HourLocator())
    #ax.fmt_xdata = DateFormatter('%Y-%m-%d %H:%M:%S')
    fig.autofmt_xdate()
    #plt.savefig('battery_energy.eps', bbox_inches='tight')
    #plt.show()
##===================================================
##===================================================
##===================================================
#ax1 = plt.subplot2grid((2, 4), (0, 1), colspan=1, rowspan=1)
#name = names[4]
#pgp_energy = pgp_e[4]
#batt_energy = batt_e[4]
#
##ax2 = plt.subplot2grid((1, 2), (0, 0), colspan=1, rowspan=1)
##ax2 = plt.subplot2grid((1, 2), (0, 0), colspan=1, rowspan=1)
##=========================================
##PGP energy
#pgp_energy_days = pgp_energy/24
##fig, ax1 = plt.subplots()
#ax2 = ax1.twinx()
#ax1.plot_date(dates, pgp_energy, '-', color='pink', linewidth=1.2)
#ax2.plot_date(dates, pgp_energy_days, '-',color='pink', linewidth=1.2)
#ax1.set_title('Batt value:'+str(name))
#ax1.set_xlim(dates[0], dates[-1])
#ax1.set_ylim(bottom=0)
#ax2.set_ylim(bottom=0)
#ax1.xaxis.set_major_locator(AutoDateLocator())
#ax1.xaxis.set_major_formatter(DateFormatter('%b-%Y'))
#
##ax1.set_xlabel('Time')
#ax1.set_ylabel('Energy in PGP storage \n (hours of mean CONUS demand)')
#ax2.set_ylabel('(days of mean CONUS demand)')
##fig.autofmt_xdate()
##plt.savefig('pgp_energy.eps', bbox_inches='tight')
##plt.show()
##=========================================
##Battery energy, year
#ax3 = plt.subplot2grid((2, 4), (1, 1), colspan=1, rowspan=1)
##fig, ax = plt.subplots()
#ax3.plot_date(dates, batt_energy, '-',color='purple', linewidth=0.5)
#ax3.set_ylim(top=2.5, bottom= 0)  # adjust the top leaving bottom unchanged
#ax3.set_xlim(dates[0], dates[-1])
##ax.set_title('Energy Stored in Batteries, 2015 View')
#
#ax3.set_ylabel('Energy in battery storage \n (hours of mean CONUS demand)')
#ax3.yaxis.set_major_locator(ticker.MultipleLocator(1))
#ax3.yaxis.set_minor_locator(ticker.MultipleLocator(0.5))
#
##ax3.set_xlabel('Time')
#ax3.xaxis.set_major_locator(AutoDateLocator())
#ax3.xaxis.set_major_formatter(DateFormatter('%b-%Y'))
#
##ax.xaxis.set_minor_locator(HourLocator())
##ax.fmt_xdata = DateFormatter('%Y-%m-%d %H:%M:%S')
#fig.autofmt_xdate()
##plt.savefig('battery_energy.eps', bbox_inches='tight')
##plt.show()
##=========================================


#=========================================
plt.tight_layout()
#fig.text(.15, 0.935, 'a)', size='large')
#fig.text(.15, 0.47, 'b)', size='large')
plt.savefig('si/SI_niches_batt.pdf', bbox_inches='tight')
plt.show()

#=========================================



##Battery energy, month
#fig, ax = plt.subplots()
#ax.plot(dates, batt_energy, '-', color='purple', linewidth=1)
##ax.set_xlim(dates[(31*24)], dates[(31*24+10*24)])
##ax.set_title('Energy Stored in Batteries, \n January View')
#ax.set_ylabel('Energy in battery storage \n (hours of mean CONUS demand)')
#ax.set_ylim(top=2.5, bottom = 0)  # adjust the top leaving bottom unchanged
#ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
#ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.5))
#ax.set_xlabel('Time')
#ax.set_xlim(dates[0], dates[31*24])
#loc = WeekdayLocator(byweekday=MO)
#ax.xaxis.set_major_locator(loc)
#ax.xaxis.set_major_formatter(DateFormatter('%d-%b'))
#fig.autofmt_xdate()
#chartBox = ax.get_position()
#ax.set_position([chartBox.x0, chartBox.y0, chartBox.width*0.6, chartBox.height])
#plt.savefig('battery_energy_month.eps', bbox_inches='tight')
#plt.show()