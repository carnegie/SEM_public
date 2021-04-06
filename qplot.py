# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 20:33:02 2018

Quick plots

@author: kcaldeira
"""

import numpy as np
import matplotlib.pyplot as plt

#%%

def qplot(x0,y0=[],xlabel='',ylabel='',title='',filename=''):
    
    if len(y0)==0:  #  one data argument
        if len(np.array(x0).shape) == 1:
            plt.plot(x0) # if vector, just plot it
        else: # assume all args are in x, with first column as x values
            x = np.array(x0)[:,0]
            y = np.array(x0)[:,1:]
            plt.plot(x,y)
    else:  # two data arguments
        if len(np.array(y0).shape) == 1:
            plt.plot(x0,y0)
        elif np.array(y0).shape[1] == len(x0): # check if y values need transposition
            y = np.array(y0).transpose()
            plt.plot(x0, y)
        else:
            plt.plot(x0, y0)

    if xlabel != '':
        plt.xlabel(xlabel)
    if ylabel != '':
        plt.ylabel(ylabel)
    if title != '':
        plt.title(title)
    plt.grid(True)
    if filename != '':
        plt.savefig(filename)
    plt.show()


#%%

# https://stackoverflow.com/questions/2236906/first-python-list-index-greater-than-x
  
#  next(x[0] for x in enumerate(L) if x[1] > 0.7)
    
# or next(idx for idx, value in enumerate(L) if value > 0.7)
    
# In this case, assumed sorted from high to low !!

def findval(val,vec):
    idx0 = next(idx for idx, value in enumerate(vec) if value < val) # change sign if sorted down
    idx1 = idx0 - 1  # +1 if sorted down
    idxval = ((val-vec[idx0])*idx1+(vec[idx1]-val)*idx0)/(vec[idx1]-vec[idx0])
    return val,idxval/len(vec)
    
#%%
#qplot([1,2,3],([[4,5,6],[7,8,9]]))
#qscatter([1,2,3],([[4,5,6],[7,8,9]]))

#hr = np.sort(result_dic['max_headroom'])[::-1]
#aa = np.array([findval(x,hr) for x in np.arange(1e-8,2.000001,0.01).tolist()])

    
