#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 10:36:47 2020

@author: jacquelinedowling
"""



#Fixed capacities unmet demand
#6 year test period in chunks



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


def get_group(cap_per):

    unsorted_pickles = [] #collection of all pickle files for triple year runs for ex
    startyrs_list =[]
    
    path = "/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/fixedcaps_chunks/"
#    fixedcaps_chunks_1yrcaps_2018_2018_chunk2
    for filename in os.listdir(path):
        if re.match("fixedcaps_chunks_"+str(cap_per)+"yrcaps_\d+_2018_chunk\d+.pickle",filename):
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



def get_met_demand(cap_per):
    print(cap_per)
    pickles = get_group(cap_per)
    x_years = [] 
    y_values = []
    
    for i in range(0, len(pickles)):
        info = pickles[i][0] 
        inputs = pickles[i][1]
        results = pickles[i][2]
        
        #demand - unmet)/demand will give you the % demand met
        #diff = sum(inputs["DEMAND_SERIES"]) - sum(results['DISPATCH_UNMET_DEMAND'])
        #pcent_met = (diff / sum(inputs["DEMAND_SERIES"]))*100
        
        h_unmet = sum(results['DISPATCH_UNMET_DEMAND'])
        
        #There will be two x values (start and end year). We'll duplicate the y value such that each x value matches a y value.
        x_years.append(inputs['START_YEAR'])
        y_values.append(h_unmet)
        x_years.append(inputs['END_YEAR']+1) #the plus one is because the run ends at the end of this year
#        y_values.append(pcent_met)
    
    return y_values










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
          'figure.figsize': (10, 7),
         'axes.labelsize': 'large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'large',
         'ytick.labelsize':'large'}
pylab.rcParams.update(params)


### Create lists for the plot
##materials = ['Aluminum', 'Copper', 'Steel']
#cap_pers = ['1-yr', '2-yr', '3-yr', '4-yr', '5-yr', '6-yr']
##x_pos = np.arange(len(materials))
#x_pos = np.arange(len(cap_pers))
##CTEs = [aluminum_mean, copper_mean, steel_mean]
##error = [aluminum_std, copper_std, steel_std]
#CTEs = []
#error = []
#for i in range(1,7):
#    demands = get_met_demand(i)
#    CTEs.append(np.mean(demands))
#    error.append(np.std(demands))
#
##($\degree C^{-1}$)
##
### Build the plot
#fig, ax = plt.subplots()
#ax.bar(x_pos, CTEs, yerr=error, align='center', alpha=0.5, ecolor='black', capsize=10)
#ax.set_ylabel('Demand met in each year')
#ax.set_xticks(x_pos)
#ax.set_xticklabels(cap_pers)
#ax.set_ylim(99.7,100.1)
##ax.set_title('Coefficent of Thermal Expansion (CTE) of Three Metals')
#ax.yaxis.grid(True)
##
### Save the figure and show
#plt.tight_layout()
#plt.savefig('bar_plot_with_error_bars.pdf')
#plt.show()
#


data = [get_met_demand(1),get_met_demand(2),get_met_demand(3),
            get_met_demand(4),get_met_demand(5),get_met_demand(6)]


#  Make boxplot
# rectangular box plot
def boxplot(ax,listOfLists,xlabel,ylabel, xticks=None):
    bplot = ax.boxplot(listOfLists,
                       vert=True,   # vertical box aligmnent
                       patch_artist=True,   # fill with color
                       whis=1000000000
                       ) # make whiskers cover full range

    numCats = len(listOfLists)

    # fill with colors
    colors = ['chocolate','peru','burlywood','wheat','blanchedalmond','oldlace']
    
    for i in range(numCats):
        bplot['boxes'][i].set_facecolor( colors[np.mod(i,numCats)] )
        bplot['medians'][i].set_color( 'black' )
    
    
    # adding horizontal grid lines
    ax.yaxis.grid(True)
    if xticks is not None:
        ax1.set_xticks([y+1 for y in range(numCats)], xticks)
        print(xticks)
        #print(xticks)
        #ticks = list(ax1.get_xticks())
        #print(ticks)
        #for i, label in enumerate(xticks):
        #    ticks[i].set_text(label)
        #plt.setp(ax1, xticks)
    else:
        ax.set_xticks([y+1 for y in range(numCats)],)
#    ax.set_xticks('1yr: 2018', '1yr: 2018','1yr: 2018','1yr: 2018','1yr: 2018','1yr: 2018',)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
#    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=2))
    
    #ax.set_ylim([0,1.1*np.max(listOfLists)])
#    ylimit = 1.1*max(map(lambda x: max(x), listOfLists))
#    ax.set_ylim(top=100)
    
fig2, ax2 = plt.subplots()   
boxplot(ax2,data, "Simulation period used to determine fixed capacities",
        "Unmet demand in 6-yr test periods across 1980-2018 (hours)",
        xticks=['1yr: 2018', '2yr: 2018','3yr: 2018','4yr: 2018','5yr: 2018','6yr: 2018'])

plt.xticks(range(1,7), labels=['1-yr:\n2018-2018', '2-yr:\n2017-2018','3-yr:\n2016-2018','4-yr:\n2015-2018','5-yr:\n2014-2018','6-yr:\n2013-2018'])
## Save the figure and show

fig2.text(.09, 0.94, 'b)', size='large')

plt.tight_layout()
plt.savefig('si/SI_fixedcaps_boxplot.pdf')
plt.show()

#
#colorlist = ('red', 'gold', 'lime', 'aqua', 'blue', 'darkviolet')
###take in the data
##x,y = get_met_demand(1)
##
#fig = plt.figure()
#ax1 = plt.subplot2grid((2, 1), (0, 0), colspan=1, rowspan=1)
#
##linelist = []
##avglist = []
##for i in range(1,7):
##    y = get_met_demand(i)
##    line = ax1.plot(x, y, '-', color=colorlist[i-1], linewidth=1.6)
##    print(i, np.average(y), np.std(y))
##    avglist.append(np.average(y))
##    linelist.append(line)
#
##
#
##ax1 = df['myvar'].plot(kind='bar')
#ax1.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=2))
#
#
#ax1.set_xlim(1980, 1987)
##ax1.set_ylim(99.98,100)
#ax1.set_ylabel("Demand met in each year")
##ax1.set_title("Fixed capacities.\nUnmet demand = $10/kWh")
#
##periods = ['2018-2018', '2017-2018', '2016-2018','2015-2018','2014-2018','2013-2018']
##
##handlelist=[]
##for i in range(1,7):
##    patch = mpatches.Patch(color=colorlist[i-1], label=str(i)+'-yr: '+str(periods[i-1]))
##    handlelist.append(patch)
##
##plt.legend(loc='right',bbox_to_anchor=(1.45, .5),handles=[handlelist[5],handlelist[4],handlelist[3],handlelist[2],handlelist[1],handlelist[0]])
#
#
#pos1 = ax1.get_position() # get the original position 
#left, width = 0.1 , .9
#bottom, height = 0.1, .9
#right = left + width
#top = bottom + height
## axes coordinates are 0,0 is bottom left and 1,1 is upper right
#p = mpatches.Rectangle(
#    (left, bottom), width, height,
#    fill=False, transform=ax1.transAxes, clip_on=False, color='white')
#ax1.add_patch(p)
#ax1.text(left, bottom, 'Fixed capacities based\non the 2018 base case.', size = 'large',
#        horizontalalignment='left',
#        verticalalignment='bottom',
#        transform=ax1.transAxes)
#
#p = mpatches.Rectangle(
#    (left, bottom), width, height,
#    fill=False, transform=ax1.transAxes, clip_on=False, color='white')
#ax1.add_patch(p)
##ax1.text(1.2*(left+right), 0.5*(bottom+1.5*top), 'Fixed capacities based\non results from these \nsimulation periods:', size = 'large',
##        horizontalalignment='center',
##        verticalalignment='bottom',
##        transform=ax1.transAxes)
#
##ax2 = plt.subplot2grid((2, 1), (1, 0), colspan=1, rowspan=1)
##xlist = [1,2,3,4,5,6]
##ax2.plot(xlist, avglist)
##ax2.set_title('Average demand met for each simulation period')
##
#
#plt.tight_layout()
##fig.text(.155, 0.94, 'a)', size='large')
##fig.text(.155, 0.46, 'b)', size='large')
#plt.savefig('fixedcaps_2018.pdf', bbox_inches='tight')
#plt.show()

