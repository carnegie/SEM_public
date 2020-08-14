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
import matplotlib.patches as mpatches


#pgp_q = 'xkcd:green' 
pgp_q = 'pink' 




##===========================================
#Read in Base Case: PGP Batteries, Wind Solar
##===========================================

#pickle_in = open('/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/Oct29_combos/Oct29_combos_SolarWind_PGPbatt.pickle', 'rb')
##pickle_in = open('/Users/jacquelinedowling/Documents/SEM-1.1_20190114/Output_Data/PGPtest5/PGPtest5_WindSolarPGPBatt_2015.pickle','rb')
#base = pickle.load(pickle_in)
#info = base[0]
#inputs = base[1]
#results = base[2]


#def get_group(grouping):
#
#    unsorted_pickles = [] #collection of all pickle files for triple year runs for ex
#    startyrs_list =[]
#    
#    path = "/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/Oct29_yrs/"
#    for filename in os.listdir(path):
#        if re.match("Oct29_yrs_"+str(grouping)+"yrs_\d+_\d+.pickle",filename):
#            pickle_in = open(str(path)+ filename,"rb")
#            base = pickle.load(pickle_in)
#            inputs = base[1]
#            start_year = int(inputs['START_YEAR'])
#            
#            unsorted_pickles.append(base)
#            startyrs_list.append(start_year)
#    sorted_pickles = [i for _,i in sorted(zip(startyrs_list, unsorted_pickles))]
#
#    return sorted_pickles
#
#
##Example here
#double_years = get_group(2)
#
#
#natural_results = ['CAPACITY_PGP_STORAGE', 'CAPACITY_STORAGE', 'CAPACITY_WIND', 'CAPACITY_SOLAR',
#                    'SYSTEM_COST', 'ENERGY_PGP_STORAGE', 'ENERGY_STORAGE']
#def get_result(group, result_type):
#    pickles = get_group(group)
#    x_years = [] 
#    y_values = []
##    Ve_values=[]
#    
#    for i in range(0, len(pickles)):
#        info = pickles[i][0] 
#        inputs = pickles[i][1]
#        results = pickles[i][2]
#        print(results)
#        #There will be two x values (start and end year). We'll duplicate the y value such that each x value matches a y value.
#        x_years.append(inputs['START_YEAR'])
#        y_values.append(results[str(result_type)])
#        x_years.append(inputs['END_YEAR']+1) #the plus one is because the run ends at the end of this year
##        y_values.append(results[str(result_type)]) #Don't do it twice in this situation.
#        
#        print('Search window', int(inputs['START_YEAR']), int(inputs['END_YEAR']+1))
#        
##        maxs, mins = getwindow(wind_df['wind capacity'], int(inputs['START_YEAR']), int(inputs['END_YEAR']+1))
##        Ve = np.sum(maxs['data']) - np.sum(mins['data'])
##        Ve_values.append(Ve)
#    
#    return x_years, y_values
##Example here
#x_years, pgp_values = get_result(6, 'CAPACITY_PGP_STORAGE')

pickle_in = open("/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/Oct29_yrs/Oct29_yrs_6yrs_1980_1985.pickle",'rb')
#pickle_in = open("/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/April16_yrs/April16_yrs_6yrs_2013_2018.pickle",'rb')
base = pickle.load(pickle_in)
info = base[0]
inputs = base[1]
results6 = base[2]


pickle_in = open("/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/Oct29_yrs/Oct29_yrs_3yrs_1980_1982.pickle",'rb')
#pickle_in = open("/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/April16_yrs/April16_yrs_6yrs_2013_2018.pickle",'rb')
base = pickle.load(pickle_in)
info = base[0]
inputs = base[1]
results3 = base[2]

pickle_in = open("/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/Oct29_yrs/Oct29_yrs_1yrs_1980_1980.pickle",'rb')
#pickle_in = open("/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/April16_yrs/April16_yrs_6yrs_2013_2018.pickle",'rb')
base = pickle.load(pickle_in)
info = base[0]
inputs = base[1]
results1 = base[2]

###=================================================

##======================================================================================================
# (Figure 2) Storage time series plots 
##======================================================================================================
date1 = datetime.datetime(1980, 1, 1, 0)
date2 = datetime.datetime(1985, 12, 31, 23)
delta = datetime.timedelta(hours=1)
dates6 = drange(date1, date2, delta)[::10]
print(len(dates6))

date1 = datetime.datetime(1980, 1, 1, 0)
date2 = datetime.datetime(1982, 12, 31, 23)
delta = datetime.timedelta(hours=1)
dates3 = drange(date1, date2, delta)[::10]
print(len(dates3))

date1 = datetime.datetime(1980, 1, 1, 0)
date2 = datetime.datetime(1980, 12, 31, 23)
delta = datetime.timedelta(hours=1)
dates1 = drange(date1, date2, delta)[::10]
print(len(dates1))

#=======================================================
# Figure size settings
#=======================================================

plt.rcParams.update({'axes.titlesize': 'large'})
plt.rcParams.update({'axes.labelsize': 'large'})

import matplotlib.pylab as pylab
params = {'legend.fontsize': 'large',
          'figure.figsize': (14, 8),
         'axes.labelsize': 'large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'large',
         'ytick.labelsize':'large'}
pylab.rcParams.update(params)

#take in the data

pgp_energy6 = results6["ENERGY_PGP_STORAGE"][::10]
pgp_energy3 = results3["ENERGY_PGP_STORAGE"][::10]
pgp_energy1 = results1["ENERGY_PGP_STORAGE"][::10]

fig = plt.figure()

ax1 = plt.subplot2grid((3, 6), (2, 0), colspan=6, rowspan=1)
#ax2 = plt.subplot2grid((1, 2), (0, 0), colspan=1, rowspan=1)
#ax2 = plt.subplot2grid((1, 2), (0, 0), colspan=1, rowspan=1)
#=========================================
#PGP energy
pgp_energy_days = pgp_energy6/24
#fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot_date(dates6, pgp_energy6, '-', color=pgp_q, linewidth=2)
ax2.plot_date(dates6, pgp_energy_days, '-',color=pgp_q, linewidth=2)

ax1.fill_between(dates6, pgp_energy6, interpolate=True, color=pgp_q)
ax2.fill_between(dates6, pgp_energy_days, interpolate=True, color=pgp_q)

#ax1.set_title('Energy Stored in PGP, 2006 View')
ax1.set_xlim(dates6[0], dates6[-1])
ax1.set_ylim(bottom=0, top=650)
ax2.set_ylim(bottom=0, top=650/24)
ax1.xaxis.set_major_locator(AutoDateLocator())
ax1.xaxis.set_major_formatter(DateFormatter('%Y-%b'))

#ax1.set_xlabel('Time')
#ax1.set_ylabel('Energy in PGP storage \n (hours of mean CONUS demand)')
ax2.set_ylabel('Days of mean\n U.S. demand')
#ax1.set_xticklabels([])
#ax2.set_xticklabels([])

loc = MonthLocator(bymonth=[1,7])
ax1.xaxis.set_major_locator(loc)
#ax1.xaxis.set_major_formatter(DateFormatter('%Y-%b'))

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

print(max(pgp_energy6))
#=========================================

ax3 = plt.subplot2grid((3, 6), (1, 0), colspan=3, rowspan=1)

#PGP energy
pgp_energy_days = pgp_energy3/24
#fig, ax1 = plt.subplots()
ax4 = ax3.twinx()
ax3.plot_date(dates3, pgp_energy3, '-', color=pgp_q, linewidth=2)
ax4.plot_date(dates3, pgp_energy_days, '-',color=pgp_q, linewidth=2)

ax3.fill_between(dates3, pgp_energy3, interpolate=True, color=pgp_q)
ax4.fill_between(dates3, pgp_energy_days, interpolate=True, color=pgp_q)

#ax1.set_title('Energy Stored in PGP, 2006 View')
ax3.set_xlim(dates3[0], dates3[-1])
ax3.set_ylim(bottom=0, top=650)
ax4.set_ylim(bottom=0, top=650/24)
ax3.xaxis.set_major_locator(AutoDateLocator())
ax3.xaxis.set_major_formatter(DateFormatter('%Y-%b'))

#ax1.set_xlabel('Time')
#ax3.set_ylabel('Energy in PGP storage (hours of mean CONUS demand)')
ax4.set_ylabel('Days of mean\n U.S. demand')
#ax1.set_xticklabels([])
#ax2.set_xticklabels([])

loc = MonthLocator(bymonth=[1,7])
ax3.xaxis.set_major_locator(loc)
#ax1.xaxis.set_major_formatter(DateFormatter('%Y-%b'))

#ax1.yaxis.set_ticks_position('both')  # Adding ticks to both top and bottom
ax3.yaxis.set_tick_params(direction='out', which='both')
ax4.yaxis.set_tick_params(direction='out', which='both')
ax3.xaxis.set_tick_params(direction='out', which='both')

ax3.yaxis.set_major_locator(ticker.MultipleLocator(200))
ax3.yaxis.set_minor_locator(ticker.MultipleLocator(100))

ax4.yaxis.set_major_locator(ticker.MultipleLocator(5))
ax4.yaxis.set_minor_locator(ticker.MultipleLocator(5))

#fig.autofmt_xdate()
#plt.savefig('pgp_energy.eps', bbox_inches='tight')
#plt.show()

print(max(pgp_energy3))

#=========================================

ax5 = plt.subplot2grid((3, 6), (0, 0), colspan=1, rowspan=1)

#PGP energy
pgp_energy_days = pgp_energy1/24
#fig, ax1 = plt.subplots()
ax6 = ax5.twinx()
ax5.plot_date(dates1, pgp_energy1, '-', color=pgp_q, linewidth=2)
ax6.plot_date(dates1, pgp_energy_days, '-',color=pgp_q, linewidth=2)

ax5.fill_between(dates1, pgp_energy1, interpolate=True, color=pgp_q)
ax6.fill_between(dates1, pgp_energy_days, interpolate=True, color=pgp_q)

#ax1.set_title('Energy Stored in PGP, 2006 View')
ax5.set_xlim(dates1[0], dates1[-1])
ax5.set_ylim(bottom=0, top=650)
ax6.set_ylim(bottom=0, top=650/24)
ax5.xaxis.set_major_locator(AutoDateLocator())
ax5.xaxis.set_major_formatter(DateFormatter('%Y-%b'))

#ax1.set_xlabel('Time')
#ax5.set_ylabel('Energy in PGP storage \n (hours of mean CONUS demand)')
ax6.set_ylabel('Days of mean\n U.S. demand')
#ax1.set_xticklabels([])
#ax2.set_xticklabels([])

loc = MonthLocator(bymonth=[1,7])
ax5.xaxis.set_major_locator(loc)
#ax1.xaxis.set_major_formatter(DateFormatter('%Y-%b'))

#ax1.yaxis.set_ticks_position('both')  # Adding ticks to both top and bottom
ax5.yaxis.set_tick_params(direction='out', which='both')
ax6.yaxis.set_tick_params(direction='out', which='both')
ax5.xaxis.set_tick_params(direction='out', which='both')

ax5.yaxis.set_major_locator(ticker.MultipleLocator(200))
ax5.yaxis.set_minor_locator(ticker.MultipleLocator(100))

ax6.yaxis.set_major_locator(ticker.MultipleLocator(5))
ax6.yaxis.set_minor_locator(ticker.MultipleLocator(5))

#fig.autofmt_xdate()
#plt.savefig('pgp_energy.eps', bbox_inches='tight')
#plt.show()

print(max(pgp_energy1))


#=========================================
#pos1 = ax2.get_position() # get the original position 
#left, width = 0.1 , .9
#bottom, height = 0.1, .9
#right = left + width
#top = bottom + height
## axes coordinates are 0,0 is bottom left and 1,1 is upper right
#p = mpatches.Rectangle(
#    (left, bottom), width, height,
#    fill=False, transform=ax1.transAxes, clip_on=False, color='white')
#ax2.add_patch(p)
#ax2.text(left, bottom, 'a) PGP energy capacity', size = 'large',
#        horizontalalignment='left',
#        verticalalignment='bottom',
#        transform=ax2.transAxes)

#p = mpatches.Rectangle(
#    (left, bottom), width, height,
#    fill=False, transform=ax1.transAxes, clip_on=False, color='white')
#ax1.add_patch(p)
#ax1.text(0.17*(left+right), 0.5*(bottom+3.55*top), 'Simulation\nperiod', size = 'large',
#        horizontalalignment='center',
#        verticalalignment='bottom',
#        transform=ax1.transAxes)

#=========================================
#plt.tight_layout()

#fig.text(0.5, 0.00, 'common X', ha='center', size='xx-large')
fig.text(0.06, 0.5, 'Energy in long duration storage (hours of mean U.S. demand)', va='center', rotation='vertical', size='x-large')
#fig.text(1.02, 0.5, '(days of mean CONUS demand)', va='center', rotation='vertical', size='x-large')

fig.text(.13, 0.85, 'a)', size='large')
fig.text(.13, 0.585, 'b)', size='large')
fig.text(.13, 0.32, 'c)', size='large')
plt.savefig('eps/figure4abc_multyrs.eps', bbox_inches='tight')
plt.savefig('figs/figure4abc_multyrs.pdf', bbox_inches='tight')
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