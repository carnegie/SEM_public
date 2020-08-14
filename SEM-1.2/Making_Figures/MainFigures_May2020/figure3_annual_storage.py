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


pgp_q = 'pink' 
batt_q = 'purple'



date1 = datetime.datetime(2018, 1, 1, 0)
date2 = datetime.datetime(2019, 1, 1, 0)
delta = datetime.timedelta(hours=1)
dates = drange(date1, date2, delta)
print(len(dates))
##===========================================
#Read in Base Case: PGP Batteries, Wind Solar
##===========================================

pickle_in = open('/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/Oct29_combos/Oct29_combos_SolarWind_PGPbatt.pickle', 'rb')
#pickle_in = open('/Users/jacquelinedowling/Documents/SEM-1.1_20190114/Output_Data/PGPtest5/PGPtest5_WindSolarPGPBatt_2015.pickle','rb')
base = pickle.load(pickle_in)
info = base[0]
inputs = base[1]
results = base[2]

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
          'figure.figsize': (8, 8),
         'axes.labelsize': 'large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'large',
         'ytick.labelsize':'large'}
pylab.rcParams.update(params)

#take in the data
batt_energy = results["ENERGY_STORAGE"]
pgp_energy = results["ENERGY_PGP_STORAGE"]

fig = plt.figure()

ax1 = plt.subplot2grid((2, 1), (0, 0), colspan=1, rowspan=1)
#ax2 = plt.subplot2grid((1, 2), (0, 0), colspan=1, rowspan=1)
#ax2 = plt.subplot2grid((1, 2), (0, 0), colspan=1, rowspan=1)
#=========================================
#PGP energy
pgp_energy_days = pgp_energy/24
#fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot_date(dates, pgp_energy, '-', color=pgp_q, linewidth=2)
ax2.plot_date(dates, pgp_energy_days, '-',color=pgp_q, linewidth=2)

ax1.fill_between(dates, pgp_energy, interpolate=True, color=pgp_q)
ax2.fill_between(dates, pgp_energy_days, interpolate=True, color=pgp_q)

#ax1.set_title('Energy Stored in PGP, 2006 View')
ax1.set_xlim(dates[0], dates[-1])
ax1.set_ylim(bottom=0)
ax2.set_ylim(bottom=0)
ax1.xaxis.set_major_locator(AutoDateLocator())
ax1.xaxis.set_major_formatter(DateFormatter('%b-%Y'))

#ax1.set_xlabel('Time')
ax1.set_ylabel('Energy in PGP storage \n (hours of mean CONUS demand)')
ax2.set_ylabel('(days of mean CONUS demand)')
ax1.set_xticklabels([])
ax2.set_xticklabels([])

#ax1.yaxis.set_ticks_position('both')  # Adding ticks to both top and bottom
ax1.yaxis.set_tick_params(direction='out', which='both')
ax2.yaxis.set_tick_params(direction='out', which='both')
ax1.xaxis.set_tick_params(direction='out', which='both')

ax1.yaxis.set_major_locator(ticker.MultipleLocator(200))
ax1.yaxis.set_minor_locator(ticker.MultipleLocator(100))

ax2.yaxis.set_major_locator(ticker.MultipleLocator(5))
ax2.yaxis.set_minor_locator(ticker.MultipleLocator(5))

#fig.autofmt_xdate()
#plt.savefig('pgp_energy.eps', bbox_inches='tight')
#plt.show()

print(max(pgp_energy))
print(max(pgp_energy_days))
#=========================================
#Battery energy, year
ax3 = plt.subplot2grid((2, 1), (1, 0), colspan=1, rowspan=1)
#fig, ax = plt.subplots()
ax3.plot_date(dates, batt_energy, '-',color=batt_q, linewidth=0.5)
ax3.fill_between(dates, batt_energy, interpolate=True, color=batt_q)

ax3.set_ylim(top=2, bottom= 0)  # adjust the top leaving bottom unchanged
ax3.set_xlim(dates[0], dates[-1])
#ax.set_title('Energy Stored in Batteries, 2015 View')

ax3.set_ylabel('Energy in battery storage \n (hours of mean CONUS demand)')
ax3.yaxis.set_major_locator(ticker.MultipleLocator(.5))
ax3.yaxis.set_minor_locator(ticker.MultipleLocator(0.25))

#ax3.set_xlabel('Time')
ax3.xaxis.set_major_locator(AutoDateLocator())
ax3.xaxis.set_major_formatter(DateFormatter('%b'))

print(max(batt_energy))

ax3.yaxis.set_tick_params(direction='out', which='both')
ax3.xaxis.set_tick_params(direction='out', which='both')

#ax.xaxis.set_minor_locator(HourLocator())
#ax.fmt_xdata = DateFormatter('%Y-%m-%d %H:%M:%S')
#fig.autofmt_xdate()
#ax3.xaxis.set_ticks_position('both')
#ax3.tick_params(axis='x', direction='in', which='bottom')
#plt.savefig('battery_energy.eps', bbox_inches='tight')
#plt.show()
#=========================================
plt.tight_layout()
fig.text(.155, 0.94, 'a)', size='large')
fig.text(.155, 0.46, 'b)', size='large')
plt.savefig('figs/figure3_annualstorage.pdf', bbox_inches='tight')
plt.savefig('eps/figure3_annualstorage.eps', bbox_inches='tight')
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