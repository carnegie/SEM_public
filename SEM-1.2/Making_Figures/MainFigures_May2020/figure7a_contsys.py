#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 17:13:40 2019

@author: jacquelinedowling
"""

#New contour plot

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
    costs = []
    
    path = '/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/Oct29_syscont'
#    path = '/Users/jacquelinedowling/SEM-1.1/Output_Data/PGPtest5_systemsensitivity'
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
            costs.append(None)
            print('Failed to solve:',"pgp"+str(pgp)+"batt"+ str(factors[i]))
        else:
            costs.append(results['SYSTEM_COST'])

    name = 'pgp'+str(pgp)
    values = np.divide(nums, 1000)
    data = (name, values, costs)
    return data

def get_data_fixed_batt(batt):
    nums = []
    factors = []
    costs = []
    
    path = '/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Output_Data/Oct29_syscont'
#    path = "/Users/jacquelinedowling/SEM-1.1/Output_Data/PGPtest5_systemsensitivity"
    for filename in os.listdir(path):
#        PGPtest5_systemsensitivity_pgp0200batt0300.pickle
        if re.match("Oct29_syscont_pgp\d+batt"+str(batt)+".pickle", filename):
            num = filename[-19:-15]
            nums.append(int(num))
#    print('before sort',nums)
    nums.sort()
    for i in range(0,len(nums)):
        factor = make_four_digits(nums[i])
        factors.append(factor)   
#    print('after sort',factors)

    for i in range(0,len(factors)):
        pickle_in = open(str(path)+ "/Oct29_syscont_pgp"+ str(factors[i])+"batt"+str(batt)+".pickle","rb")
        base = pickle.load(pickle_in)
        
        info = base[0]
        inputs = base[1]
        results = base[2]
        if results['SYSTEM_COST'] == -1:
            costs.append(None)
            print('Failed to solve:',"pgp"+ str(factors[i])+"batt"+str(batt))
        else:
            costs.append(results['SYSTEM_COST'])
    
    values = np.divide(nums, 1000)
    name = 'batt'+str(batt)
    data = (costs)
    return data
#==================================================================
# Getting Data
##===================================================================
strings= ['0000', '0007', '0010', '0020', '0050', '0067', '0100', '0150', '0200', '0250', '0300', '0350', '0400', '0450', '0500', '0550', '0600', '0650', '0700', '0750', '0800', '0850', '0900', '0950', '1000']


pgplist = []
for i in range(0, len(strings)):
    data = get_data_fixed_pgp(strings[i])
    pgplist.append(data[2])

battlist = []
for i in range(0, len(strings)):
    data = get_data_fixed_batt(strings[i])
    battlist.append(data)



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
x = [1,2,3,4,5]
y = [2,4,6,8,10]
z = [[1,1,1,1,1],[1,2,3,4,5],[1,1,1,1,1],[1,1,1,1,1],[1,1,1,1,1]] 

#Real
points = [0.   , 0.007, 0.01 , 0.02 , 0.05 , 0.067, 0.1  , 0.15 , 0.2  ,
        0.25 , 0.3  , 0.35 , 0.4  , 0.45 , 0.5  , 0.55 , 0.6  , 0.67 ,
        0.7  , 0.75 , 0.8  , 0.85 , 0.9  , 0.95 , 1.   ]
x = points
y = points
z = battlist

X, Y = np.meshgrid(x, y)
Z = np.array(z)

#print("contour")
#print(X)
#print(Y)
#print(Z)

ax2 = plt.figure()
levels = [0.06, 0.065,0.07,0.075, 0.08, 0.085, 0.09, 0.095, 0.1, 0.105, 0.11, 0.115, 0.12]
#levels = [0.07,0.075, 0.08, 0.085, 0.09, 0.095, 0.1, 0.105, 0.11, 0.115, 0.12]
CS = plt.contourf(X, Y, Z, levels, cmap = plt.set_cmap('viridis_r'))
CS2 = plt.contour(CS, levels=[0.07, 0.08, 0.09,0.1,0.11,0.12], colors='k')
#CS2 = plt.contour(CS, levels=CS.levels[::2], colors='k')
fmt = ticker.FormatStrFormatter('$%.2f')
q = plt.clabel(CS2, inline=1, fontsize=10, fmt=fmt)

#q[0].set_y(-0.5)
#q[0].set_x(-0.5)
#q[0].y=-0.5
#for i in q:
#    print('I',i)
#plt.clabel(CS2, inline=1, fontsize=10, fmt=fmt)

ax2 = plt.axes()
ax2.xaxis.set_major_formatter(FormatStrFormatter('%gx'))
ax2.yaxis.set_major_formatter(FormatStrFormatter('%gx')) 
#ax2.set_ylim(0.0, 1.0)
#ax2.set_xlim(1.0, 0.0)
#plt.title('System cost sensitivity\nto storage costs')
plt.xlabel('LDS cost\n(multiple of base case)')
plt.ylabel('Battery cost\n(multiple of base case)')

# Make a colorbar for the ContourSet returned by the contourf call.
cbar = plt.colorbar(CS, shrink=0.8, extend='both',format='%.2f')
#for label in cbar.ax.yaxis.get_ticklabels()[::2]:
#    label.set_visible(False)
cbar.ax.set_ylabel('System cost ($/kWh)')

cbar.add_lines(CS2)
plt.savefig('figs/figure7a_contsys.pdf', bbox_inches='tight')
plt.savefig('eps/figure7a_contsys.eps', bbox_inches='tight')
plt.show()

#data = pd.DataFrame(data={'material':['Si','Ge','GaAs'],
#                          'lattice constant (angstroms)':[5.43095,5.646,5.6533]}) 
#print(data)
