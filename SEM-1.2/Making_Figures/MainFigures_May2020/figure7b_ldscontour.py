#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 17:05:10 2020

@author: jacquelinedowling
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 09:38:11 2020

@author: jacquelinedowling
"""


#New LDS contour plot

#countour plots
import numpy as np
import pandas as pd
from numpy import genfromtxt
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker

from numpy import arange
from matplotlib.ticker import ScalarFormatter
from matplotlib.ticker import FormatStrFormatter

import matplotlib.cm as cm
import matplotlib.mlab as mlab

import numpy as np
import pickle
from numpy import genfromtxt
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker

import os
import re
import matplotlib.patches as mpatches


#==================================================================
    # Get what you need from each pickle file
##===================================================================
def sort_pair_of_lists(cost_list, unsorted_pickles):
    new_indices = np.argsort(cost_list)
    sorted_pickles = [None] * len(new_indices)
    sorted_costs = [None] * len(cost_list)
    for i in range(len(new_indices)):
        sorted_pickles[i]= unsorted_pickles[new_indices[i]]
        sorted_costs[i] = cost_list[new_indices[i]]
    
    return sorted_costs, sorted_pickles

##===================================================================
    
def get_syscost_array(exterior_pics):
    e_base = 1.47092052560716E-06
    topgp_base = 1.48026537223673E-02
    frompgp_base = 6.30375922961022E-02
    
    syscost_shaped = []
    for i in range(len(exterior_pics)):
        syscost_shaped.append([])
        for j in range(len(exterior_pics[i])):
            pickle = exterior_pics[i][j] #j is inner list
            inputs = pickle[1]
            eng = inputs['FIXED_COST_PGP_STORAGE']/e_base
            pwr = inputs['FIXED_COST_TO_PGP_STORAGE']/topgp_base
            results = pickle[2]
            syscost = results['SYSTEM_COST']
            syscost_shaped[i].append(syscost) #add to the correct outer list
            if syscost == -1:
                print('Failed to solve: eng', eng, 'pwr',pwr)
                
                
    print('----------')
    return syscost_shaped

def almost_equal(x, y):
    return abs(x-y) / min(y, x) < .001

##===================================================================

def get_pickles():
    e_base = 1.47092052560716E-06
    topgp_base = 1.48026537223673E-02
    frompgp_base = 6.30375922961022E-02
    
    unsorted_pickles = [] #collection of all pickle files for triple year runs for ex
    cost_list =[]
    
    path= '/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/April2020_ldscont/'
    for filename in os.listdir(path):
        if filename.endswith(".pickle"):
            pickle_in = open(str(path)+ filename,"rb")
            base = pickle.load(pickle_in)
            inputs = base[1]
            cost = inputs['FIXED_COST_PGP_STORAGE']
            unsorted_pickles.append(base)
            cost_list.append(cost)
    sorted1_costs, sorted1_pickles = sort_pair_of_lists(cost_list, unsorted_pickles)
    #while it's the same as the one before, keep going
    #if it's a new cost
    #then start sorting within
    
    #reshaped to a 2D array (sort exterior lists)
    costs1_shaped = []
    pics1_shaped = []
    
    for i in range(len(sorted1_costs)):
#        print(sorted1_costs[i])
        if sorted1_costs[i] == sorted1_costs[i-1]: #if it's the same as the one before
            costs1_shaped[-1].append(sorted1_costs[i])
            pics1_shaped[-1].append(sorted1_pickles[i])
        elif almost_equal(sorted1_costs[i], sorted1_costs[i-1]):
            costs1_shaped[-1].append(sorted1_costs[i])
            pics1_shaped[-1].append(sorted1_pickles[i])
        else: #if not the same as the one before
            #then start a new sublist
#            print(sorted1_costs[i], sorted1_costs[i-1])
            sublist_c = []
            sublist_p = []
            sublist_c.append(sorted1_costs[i])
            sublist_p.append(sorted1_pickles[i])
            costs1_shaped.append(sublist_c) 
            pics1_shaped.append(sublist_p)
#    print([len(c) for c in costs1_shaped])
    #prep for the sorting function on the interior lists (say how you want it sorted by)
    costs2_shaped = []
    for i in range(len(pics1_shaped)):
        costs2_shaped.append([]) #adds an additional exterior list
        for j in range(len(pics1_shaped[i])):
            base = pics1_shaped[i][j]
            inputs = base[1]
            cost2 = inputs['FIXED_COST_TO_PGP_STORAGE']
            costs2_shaped[i].append(cost2) #adds to each interior list
            #we can only do the sort method on interior lists
    
    #sort interior lists
    exterior_cost = []
    exterior_pics = []
    for i in range(len(costs2_shaped)):
        interior_cost = costs2_shaped[i]
        interior_pic = pics1_shaped[i] #unsorted / behind. because it's labeled 1 we are making a pics2
        sorted2_costs, sorted2_pickles = sort_pair_of_lists(interior_cost, interior_pic)
        exterior_cost.append(sorted2_costs)
        exterior_pics.append(sorted2_pickles)
    
    to_plot = get_syscost_array(exterior_pics)
#    print(to_plot)
#Things you sorted by that you can return:        
    return to_plot, exterior_pics, costs1_shaped, exterior_cost   

##===================================================================

plotarray, pickles2D, sortbyvar1, sortbyvar2 = get_pickles()
#print("hellooooo")


#checking it works
e_base = 1.47092052560716E-06
topgp_base = 1.48026537223673E-02
frompgp_base = 6.30375922961022E-02

#sorted_pickles = get_pickles()
#for i in range(0,len(sorted_pickles)):
#    print(sorted_pickles[i][1]['FIXED_COST_PGP_STORAGE']/e_base)

##===================================================================
#    
def get_axes():
    plotarray, pickles2D, sortbyvar1, sortbyvar2 = get_pickles()
    
    e_base = 1.47092052560716E-06
    topgp_base = 1.48026537223673E-02
    frompgp_base = 6.30375922961022E-02  
    
    e_costs = [] 
    p_costs = []
#    sys_costs =[]
    
    for i in range(len(pickles2D)):
        for j in range(len(pickles2D[i])):
            inputs1 = pickles2D[i][j][1]
            inputs2 = pickles2D[j][i][1]
            #There will be two x values (start and end year). We'll duplicate the y value such that each x value matches a y value.
            e_costs.append(float(inputs2['FIXED_COST_PGP_STORAGE'])/e_base)
            p_costs.append(float(inputs1['FIXED_COST_TO_PGP_STORAGE'])/topgp_base)
#                           + float(inputs1['FIXED_COST_FROM_PGP_STORAGE'])/frompgp_base)
    #        sys_costs.append(results['SYSTEM_COST'])
            
        break
    return e_costs, p_costs #, sys_costs
#Example here
e, p = get_axes()            

#print('e')
#print(e)
#print('p')
#print(p)



#==================================================================
# Getting Data
##===================================================================
#stringsp= ['0000', '0007', '0010', '0020', '0050', '0067', '0100', '0150', '0200', '0250', '0300', '0350', '0400', '0450', '0500', '0550', '0600', '0650', '0700', '0750', '0800', '0850', '0900', '0950', '1000']
#stringse= [  '1000',  '17600',  '34200',  '50800',  '67400',  '84000', '100600',
#       '117200', '133800', '150400', '167000', '183600', '200200', '216800',
#       '233400', '250000']
#
##engpgp250000pwrpgp0000
#plist = []
#for i in range(0, len(stringsp)):
#    data = get_data_fixed_pwr(stringsp[i])
#    plist.append(data)
#
#elist = []
#for i in range(0, len(stringse)):
#    data = get_data_fixed_eng(stringse[i])
#    elist.append(data)



#==================================================================
# Plotting
##===================================================================
##===========================================
plt.rcParams.update({'axes.titlesize': 'large'})
plt.rcParams.update({'axes.labelsize': 'large'})

import matplotlib.pylab as pylab
params = {'legend.fontsize': 'large',
          'figure.figsize': (6, 5),
         'axes.labelsize': 'large',
         'axes.titlesize':'large',
         'xtick.labelsize':'large',
         'ytick.labelsize':'large'}
pylab.rcParams.update(params)
##===========================================
#TEST
#x = [1,2,3,4,5]
#y = [2,4,6,8,10]
#z = [[1,1,1,1,1],[1,2,3,4,5],[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1]] 

#Real
#points = [0.   , 0.007, 0.01 , 0.02 , 0.05 , 0.067, 0.1  , 0.15 , 0.2  ,
#        0.25 , 0.3  , 0.35 , 0.4  , 0.45 , 0.5  , 0.55 , 0.6  , 0.67 ,
#        0.7  , 0.75 , 0.8  , 0.85 , 0.9  , 0.95 , 1.   ]
#newpoints = [  1. ,  17.6,  34.2,  50.8,  67.4,  84. , 100.6, 117.2, 133.8,
#       150.4, 167. , 183.6, 200.2, 216.8, 233.4, 250. ]


plotarray, pickles2D, sortbyvar1, sortbyvar2 = get_pickles()
e, p = get_axes()
x = e
y = p
z = plotarray

X, Y = np.meshgrid(x, y)
Z = np.array(z)

#print("contour")
#print(X)
#print(Y)
#print(Z)

ax2 = plt.figure()
levels = [0.06, 0.065,0.07,0.075, 0.08, 0.085, 0.09, 0.095,
          0.1, 0.105, 0.11, 0.115, 0.12,0.125,0.13,0.135,0.14,0.145, .15]
#levels = np.linspace(.06,.145,17)
#levels = [0.07,0.075, 0.08, 0.085, 0.09, 0.095, 0.1, 0.105, 0.11, 0.115, 0.12, .125, ]
CS = plt.contourf(X, Y, np.array(Z).T, levels, cmap = plt.set_cmap('viridis_r'))
#CS2 = plt.contour(CS,  levels=CS.levels[::2], colors='k')


CS2 = plt.contour(CS, levels=[0.07, 0.08, 0.09,0.1,0.11,0.12, 0.13, .14], colors='k')

#CS2 = plt.contour(CS, levels=CS.levels[::2], colors='k')
fmt = ticker.FormatStrFormatter('$%.2f')
q = plt.clabel(CS2, inline=1, fontsize=10, fmt=fmt)

#ax2 = plt.figure()
##levels = [0.06, 0.065,0.07,0.075, 0.08, 0.085, 0.09, 0.095, 0.1, 0.105, 0.11, 0.115, 0.12]
##levels = [0.07,0.075, 0.08, 0.085, 0.09, 0.095, 0.1, 0.105, 0.11, 0.115, 0.12]
#CS = plt.contourf(X, Y, Z, cmap = plt.set_cmap('viridis_r'))
#CS2 = plt.contour(CS,  colors='k')
##CS2 = plt.contour(CS, levels=CS.levels[::2], colors='k')
#fmt = ticker.FormatStrFormatter('$%.2f')
#q = plt.clabel(CS2, inline=1, fontsize=10, fmt=fmt)

#q[0].set_y(-0.5)
#q[0].set_x(-0.5)
#q[0].y=-0.5
#for i in q:
#    print('I',i)
#plt.clabel(CS2, inline=1, fontsize=10, fmt=fmt)
#ax2.set_xscale("log")


ax2 = plt.axes()


ax2.set_yscale("log")
ax2.set_xscale("log")

ax2.set_ylim(0.0005, 1)
ax2.set_xlim(1, 250)
ax2.yaxis.set_major_formatter(FormatStrFormatter('%.3gx'))
ax2.xaxis.set_major_formatter(FormatStrFormatter('%gx')) 
#ax2.yaxis.set_major_formatter(ticker.PercentFormatter(decimals=3))
#ax2.xaxis.set_major_formatter(ticker.PercentFormatter(decimals=0))

plt.xticks([1, 10, 100, 250])


#plt.title('System cost sensitivity\nto storage costs')
plt.xlabel('Long-duration storage energy cost\n(multiple of base case)')
plt.ylabel('Long-duration storage power cost\n(multiple of base case)')

# Make a colorbar for the ContourSet returned by the contourf call.
cbar = plt.colorbar(CS, shrink=0.8, extend='both',format='%.2f')
#for label in cbar.ax.yaxis.get_ticklabels()[::2]:
#    label.set_visible(False)
cbar.ax.set_ylabel('System cost ($/kWh)')

cbar.add_lines(CS2)

#====================================================================
#PGP
ax2.scatter(1, 1, marker="o", color='white', s=50)
ax2.text(1.28, .6, "PGP", color='white', fontsize=12, fontweight='bold')

#PGP with H2 turbines
#ax2.scatter(1, 0.144675926, marker="o", color='white', s=50)
#ax2.text(1.28, .08, "PGP\nwith H2\nturbines", color='white', fontsize=12, fontweight='bold')

#PHS
ax2.scatter(210.7399821, 0.063716503, marker="o", color='white', s=50)
ax2.text(135, .1, "PHS", color='white', fontsize=12, fontweight='bold')
#CAES
ax2.scatter(10.9375, 0.068500386, marker="o", color='white', s=50)
ax2.text(8, .1, "CAES", color='white',fontsize=12, fontweight='bold')
#ax2.text(8, .1, "CAES\n*not renewable", color='white',fontsize=12, fontweight='bold')
#====================================================================

#====================================================================

#ax2.set_xlim(1, Mx*2)
#ax2.set_ylim(100, My*2)
#--------------------------------------------------
#--------------------------------------------------
#plt.show()

plt.savefig('figs/figure7b_ldscontour.pdf', bbox_inches='tight')
plt.savefig('eps/figure7b_ldscontour.eps', bbox_inches='tight')
plt.show()

#data = pd.DataFrame(data={'material':['Si','Ge','GaAs'],
#                          'lattice constant (angstroms)':[5.43095,5.646,5.6533]}) 
#print(data)
