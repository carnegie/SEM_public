#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 15:42:36 2020

@author: jacquelinedowling
"""

#Fixed capacities unmet demand


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

import matplotlib.ticker as mtick



#UPDATE TO 2018!!!!

pgp_q = 'pink' 
batt_q = 'purple'

#pgp_q = '#ffb3ff' 
#batt_q = '#8c1aff'
#dem_c = 'black'

#pgp_q = '#ffb3ff' 
#batt_q = '#8c1aff'
#pgp_q = 'pink'
#batt_q = 'xkcd:violet'


##===========================================
#Read in Base Case: PGP Batteries, Wind Solar
##===========================================

pickle_in = open('/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/fixedcaps_yrs/fixedcaps_yrs_1yrs_2018_2018_tst1980.pickle', 'rb')
#pickle_in = open('/Users/jacquelinedowling/Documents/SEM-1.1_20190114/Output_Data/PGPtest5/PGPtest5_WindSolarPGPBatt_2015.pickle','rb')
base = pickle.load(pickle_in)
info = base[0]
inputs = base[1]
results = base[2]



#def get_pickles():
#
#    unsorted_pickles = [] #collection of all pickle files for triple year runs for ex
#    startyrs_list =[]
#    
#    path = "/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/fixedcaps_2018/"
#    for filename in os.listdir(path):
#        if re.match("fixedcaps_2018_SolarWindPGPbatt2018_\d+.pickle",filename):
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


def get_group(grouping):

    unsorted_pickles = [] #collection of all pickle files for triple year runs for ex
    startyrs_list =[]
    
    path = "/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/fixedcaps_yrs/"
    for filename in os.listdir(path):
        if re.match("fixedcaps_yrs_"+str(grouping)+"yrs_\d+_\d+_tst\d+.pickle",filename):
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



def get_met_demand(group):
    print(group)
    pickles = get_group(group)
    x_years = [] 
    y_values = []
    
    for i in range(0, len(pickles)):
        info = pickles[i][0] 
        inputs = pickles[i][1]
        results = pickles[i][2]
        
#        #demand - unmet)/demand will give you the % demand met
#        diff = sum(inputs["DEMAND_SERIES"]) - sum(results['DISPATCH_UNMET_DEMAND'])
#        pcent_met = (diff / sum(inputs["DEMAND_SERIES"]))*100
#        
#        #There will be two x values (start and end year). We'll duplicate the y value such that each x value matches a y value.
#        x_years.append(inputs['START_YEAR'])
#        y_values.append(pcent_met)
#        x_years.append(inputs['END_YEAR']+1) #the plus one is because the run ends at the end of this year
#        y_values.append(pcent_met)
        
        #demand - unmet)/demand will give you the % demand met
#        diff = sum(inputs["DEMAND_SERIES"]- results['DISPATCH_UNMET_DEMAND'])
#        pcent_met = (diff / sum(inputs["DEMAND_SERIES"]))*100
        
        h_unmet = sum(results['DISPATCH_UNMET_DEMAND'])#8765.82- diff #/8765.82
        
        #There will be two x values (start and end year). We'll duplicate the y value such that each x value matches a y value.
        x_years.append(inputs['START_YEAR'])
        y_values.append(h_unmet)
        x_years.append(inputs['END_YEAR']+1) #the plus one is because the run ends at the end of this year
        y_values.append(h_unmet)
    
    return x_years, y_values










#======================================================================================================
# Fixed capacity plotting 
#======================================================================================================
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
#

colorlist = ('red', 'gold', 'lime', 'aqua', 'blue', 'darkviolet')
##take in the data
#x,y = get_met_demand(1)
#
fig = plt.figure()
ax1 = plt.subplot2grid((2, 1), (0, 0), colspan=1, rowspan=1)

linelist = []
avglist = []
for i in range(1,7):
    x, y = get_met_demand(i)
    line = ax1.plot(x, y, '-', color=colorlist[i-1], linewidth=1.6)
    print(i, np.average(y), np.std(y))
    avglist.append(np.average(y))
    linelist.append(line)
    break
#

#ax1 = df['myvar'].plot(kind='bar')

#THIS ONE
#ax1.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=2))


ax1.set_xlim(1980, 2020)
#ax1.set_ylim(99.98,100)
ax1.set_ylabel("Unmet demand in each year (hours)")
#ax1.set_title("Fixed capacities.\nUnmet demand = $10/kWh")

#periods = ['2018-2018', '2017-2018', '2016-2018','2015-2018','2014-2018','2013-2018']
#
#handlelist=[]
#for i in range(1,7):
#    patch = mpatches.Patch(color=colorlist[i-1], label=str(i)+'-yr: '+str(periods[i-1]))
#    handlelist.append(patch)
#
#plt.legend(loc='right',bbox_to_anchor=(1.45, .5),handles=[handlelist[5],handlelist[4],handlelist[3],handlelist[2],handlelist[1],handlelist[0]])


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
ax1.text(left, top-.2, 'a) Fixed capacities based\non the 2018 base case.', size = 'large',
        horizontalalignment='left',
        verticalalignment='bottom',
        transform=ax1.transAxes)

p = mpatches.Rectangle(
    (left, bottom), width, height,
    fill=False, transform=ax1.transAxes, clip_on=False, color='white')
ax1.add_patch(p)
#ax1.text(1.2*(left+right), 0.5*(bottom+1.5*top), 'Fixed capacities based\non results from these \nsimulation periods:', size = 'large',
#        horizontalalignment='center',
#        verticalalignment='bottom',
#        transform=ax1.transAxes)

#ax2 = plt.subplot2grid((2, 1), (1, 0), colspan=1, rowspan=1)
#xlist = [1,2,3,4,5,6]
#ax2.plot(xlist, avglist)
#ax2.set_title('Average demand met for each simulation period')
#

plt.tight_layout()
#fig.text(.155, 0.94, 'a)', size='large')
#fig.text(.155, 0.46, 'b)', size='large')
plt.savefig('si/SI_fixedcaps_2018.pdf', bbox_inches='tight')
plt.show()

##ax2 = plt.subplot2grid((1, 2), (0, 0), colspan=1, rowspan=1)
##ax2 = plt.subplot2grid((1, 2), (0, 0), colspan=1, rowspan=1)
##=========================================
##PGP energy
#pgp_energy_days = pgp_energy/24
##fig, ax1 = plt.subplots()
#ax2 = ax1.twinx()
#ax1.plot_date(dates, pgp_energy, '-', color=pgp_q, linewidth=2)
#ax2.plot_date(dates, pgp_energy_days, '-',color=pgp_q, linewidth=2)
#
#ax1.fill_between(dates, pgp_energy, interpolate=True, color=pgp_q)
#ax2.fill_between(dates, pgp_energy_days, interpolate=True, color=pgp_q)
#
##ax1.set_title('Energy Stored in PGP, 2006 View')
#ax1.set_xlim(dates[0], dates[-1])
#ax1.set_ylim(bottom=0)
#ax2.set_ylim(bottom=0)
#ax1.xaxis.set_major_locator(AutoDateLocator())
#ax1.xaxis.set_major_formatter(DateFormatter('%b-%Y'))
#
##ax1.set_xlabel('Time')
#ax1.set_ylabel('Energy in PGP storage \n (hours of mean CONUS demand)')
#ax2.set_ylabel('(days of mean CONUS demand)')
#ax1.set_xticklabels([])
#ax2.set_xticklabels([])
#
##ax1.yaxis.set_ticks_position('both')  # Adding ticks to both top and bottom
#ax1.yaxis.set_tick_params(direction='out', which='both')
#ax2.yaxis.set_tick_params(direction='out', which='both')
#ax1.xaxis.set_tick_params(direction='out', which='both')
#
#ax1.yaxis.set_major_locator(ticker.MultipleLocator(200))
#ax1.yaxis.set_minor_locator(ticker.MultipleLocator(100))
#
#ax2.yaxis.set_major_locator(ticker.MultipleLocator(5))
#ax2.yaxis.set_minor_locator(ticker.MultipleLocator(5))
#
##fig.autofmt_xdate()
##plt.savefig('pgp_energy.eps', bbox_inches='tight')
##plt.show()
#
#print(max(pgp_energy))
#print(max(pgp_energy_days))
##=========================================
##Battery energy, year
#ax3 = plt.subplot2grid((2, 1), (1, 0), colspan=1, rowspan=1)
##fig, ax = plt.subplots()
#ax3.plot_date(dates, batt_energy, '-',color=batt_q, linewidth=0.5)
#ax3.fill_between(dates, batt_energy, interpolate=True, color=batt_q)
#
#ax3.set_ylim(top=2, bottom= 0)  # adjust the top leaving bottom unchanged
#ax3.set_xlim(dates[0], dates[-1])
##ax.set_title('Energy Stored in Batteries, 2015 View')
#
#ax3.set_ylabel('Energy in battery storage \n (hours of mean CONUS demand)')
#ax3.yaxis.set_major_locator(ticker.MultipleLocator(.5))
#ax3.yaxis.set_minor_locator(ticker.MultipleLocator(0.25))
#
##ax3.set_xlabel('Time')
#ax3.xaxis.set_major_locator(AutoDateLocator())
#ax3.xaxis.set_major_formatter(DateFormatter('%b'))
#
#print(max(batt_energy))
#
#ax3.yaxis.set_tick_params(direction='out', which='both')
#ax3.xaxis.set_tick_params(direction='out', which='both')
#
##ax.xaxis.set_minor_locator(HourLocator())
##ax.fmt_xdata = DateFormatter('%Y-%m-%d %H:%M:%S')
##fig.autofmt_xdate()
##ax3.xaxis.set_ticks_position('both')
##ax3.tick_params(axis='x', direction='in', which='bottom')
##plt.savefig('battery_energy.eps', bbox_inches='tight')
##plt.show()
##=========================================
#plt.tight_layout()
#fig.text(.155, 0.94, 'a)', size='large')
#fig.text(.155, 0.46, 'b)', size='large')
#plt.savefig('figure2.pdf', bbox_inches='tight')
#plt.savefig('figure2.eps', bbox_inches='tight')
#plt.show()
#
##=========================================
    

#=======================================================
#date1 = datetime.datetime(int(inputs['START_YEAR']), int(inputs['START_MONTH']),
#                          int(inputs['START_DAY']), int(inputs['START_HOUR']))
#date2 = datetime.datetime(int(inputs['END_YEAR']), int(inputs['END_MONTH']),
#                          int(inputs['END_DAY']), int(inputs['END_HOUR']))

#date1 = datetime.datetime(2017, 12, 31 ,23)
#date2 = datetime.datetime(2018, 12, 31 ,23)
##date1 = datetime.datetime(int(inputs['START_YEAR']), 1, 1 ,1)
##date2 = datetime.datetime(int(inputs['END_YEAR']+1), 1, 1, 1)
#delta = datetime.timedelta(hours=1)
#dates = drange(date1, date2, delta)
#print(len(dates))

