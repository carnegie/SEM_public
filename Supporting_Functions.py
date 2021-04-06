# -*- coding: utf-8 -*-
'''
Created on Fri Dec 01 16:31:28 2017

File name: Supporting_Functions.py

Goal
    This file is a collection/codebase for fundamental/low-level functions that 
    I defined and I will use in the Idealized Energy Modeling project.

Functions defined
    func_load_optimization_results()
    func_time_conversion()
    func_time_conversion()
    func_change_in_period()
    func_find_period()
    func_lines_plot()
    func_lines_2yaxes_plot()
    func_stack_plot()
    func_PMF_plot()

History
    Dec 1, 2017 started this script
    Jun 10, 2018 provided the functional comments
    Jun 17, 2018 added a func_line_plot() function
    Jun 19, 2018 added a func_plotting_two_axes() function
    
    Jun 19, 2018 changed some function names
    Jun 20, 2018 
        changed the input and output variables for func_lines_2yaxes_plot()
        added the LOCATION parameter for legend()
    Jun 21, 2018
        added parallel axes for func_lines_plot(), func_stack_plot()
        removed func_line_plot()
        added func_find_period()
    Jun 22, 2018
        updated func_find_period()
    Jun 23, 2018
        checked the code and comments
    Jul 12, 2018 removed parallel axes for plots (KC)

@author: Fan Tong
'''

from __future__ import division
import os
import sys
import copy
import numpy as np


# -----------------------------------------------------------------------------
# func_load_optimization_results()
#
# Function: load the optimization assumptions and results from files to the
#   system memory (variable names)
#
# Input
#   optimization_results_file_path -- full file path for the optimization
#                                       assumptions and results
#
# Output
#   A DICT variable with the following keys
#       model_inputs
#       model_results
#
# History
#   Feb 18, 2018 very early version (some commands)
#   Jun 19-20, 2018 rewrote as a function
#
# @ Fan Tong
# -----------------------------------------------------------------------------

def func_load_optimization_results(optimization_results_file_path):    
    
    # get the file extension automatically
    
    filename, optimization_results_data_type = os.path.splitext(optimization_results_file_path)

    # print ( optimization_results_data_type

    if optimization_results_data_type == '.npz':
    
        # How was the files generated?        
        # The file ABC.npz was created using the SAVEZ function of the numpy package.
    
        # Deal with dictionary variables    
        # First note that when you saved dict variables into .npz files and then retrieve
        # them back, they have data_type = object (more accurately, it is a numpy.ndarray
        # type), rather than dictionary, so you have to use them slightly differently.
        # However, model_results.item() is a dictionary type variable.
        # So, you access the files like these, model_results.item()['unmet_demand']    
    
        # ---------------------------------------------------------------------
    
        # Load the data file
        npzfile = np.load(optimization_results_file_path)
    
        # ---------------------------------------------------------------------
    
        # Look for what is in the file
        # The function will list all variable names
    
        model_inputs = npzfile['model_inputs'].item()
        model_results = npzfile['model_results'].item()
    
        # ---------------------------------------------------------------------
    
    elif optimization_results_data_type == '.pkl':
        
        import pickle
        
        f = open(optimization_results_file_path, 'rb')
        model_inputs, model_results = pickle.load(f)

    else:
        sys.exit('Error! Unsupported file types for optimization results!')

    # -------------------------------------------------------------------------

    output_data = {
            'model_inputs':     model_inputs,
            'model_results':    model_results,
            }

    return output_data

#%%
# -----------------------------------------------------------------------------
# func_time_conversion()
#
# Function
#   Downscale the time series (from hourly data to daily, weekly, etc.)
#
# Input
#   input_data [one dimentional] data to be downscaled.
#   window_size <scalar> downscale size, e.g. 24 (a day)
#   operation_type <string> there are a number of downscale operations (namely,
#       how to select a 'representative/aggregate' from a set of data)
#
# Output
#   output_data [one dimentional] data that is downscaled. Note the length has
#   changed/reduced.
#
# Note
#   If the length of the input_data are not multiples of window size, then I
#       only consider the segments of data [0, window_size * N] in the input_data
#       where N = floor ( input_data's length / window_size)
#
# History
#   Dec, 2017 started and finished the code.    
#   Jun 21, 2018 double checked the code when a bug arose due to using the
#       the actual division rather than a floor division
#
# @ Fan Tong    
# -----------------------------------------------------------------------------



#%%
# -----------------------------------------------------------------------------
# func_time_conversion()
#
# Function
#   calculate key statistics of the input_data in a moving window (rolling basis)
#
# Input
#   input_data [one dimentional]
#   window_size [scalar] the length/size of the moving window
#   operation_type <string> there are a number of downscale operations (namely,
#       how to select a 'representative/aggregate' from a set of data)
#
# Output
#   output_data [one dimentional] data that consists of key statistics calculated
#   for the moving window around each time step.
#
# History
#   Dec, 2017 started and finished the code.    
#   Jun 21, 2018 fixed the Type Error bug (float variables for integer applicaitons)
#       caused by using the actual division.
#
# @ Fan Tong    
# -----------------------------------------------------------------------------



#%%
# -----------------------------------------------------------------------------
# func_change_in_period()
#
# Function
#   calculate the changes over a moving window (rolling basis); specifically,
#   here I only calculate the difference at the window edges
#
# Input
#   input_data [one dimentional]
#   window_size [scalar] the length/size of the moving window
#
# Output
#   output_data [one dimentional] reports the difference for each time step
#
# Usage
#   Energy storage static analysis
#
# History
#   (early) Jun, 2018
#
# @ Fan Tong
# -----------------------------------------------------------------------------
def func_time_conversion (input_data, window_size, operation_type = 'mean'):
    
    # NOTE: THIS FUNCTION HAS ONLY BEEN VERIFIED FOR PROPER WRAP-AROUND BEHAVIOR
    #       FOR 'mean'
    # For odd windows sizes, easy. For even need to consider ends where you have half hour of data.

    N_periods = len(input_data)
    input_data_x3 = np.concatenate((input_data,input_data,input_data))
    
    half_size = window_size / 2.
    half_size_full = int(half_size) # number of full things for the mean

    output_data = np.zeros(len(input_data))
    
    for ii in range(len(output_data)):
        if half_size != float (half_size_full): # odd number, easy
            if (operation_type == 'mean'):
                output_data[ii] = np.sum(input_data_x3[N_periods + ii - half_size_full : N_periods + ii + half_size_full + 1 ])/ float(window_size)
            elif(operation_type == 'min'):
                output_data[ii] = np.min(input_data_x3[N_periods + ii - half_size_full : N_periods + ii + half_size_full + 1 ])
            elif(operation_type == 'max'):
                output_data[ii] = np.max(input_data_x3[N_periods + ii - half_size_full : N_periods + ii + half_size_full  + 1])
            elif(operation_type == 'sum'):
                output_data[ii] = np.sum(input_data_x3[N_periods + ii - half_size_full : N_periods + ii + half_size_full  + 1])
        else: # even number need to include half of last ones
            if (operation_type == 'mean'):
                output_data[ii] = ( np.sum(input_data_x3[N_periods + ii - half_size_full : N_periods + ii + half_size_full ])  \
                        + input_data_x3[N_periods + ii - half_size_full -1 ] *0.5 +  input_data_x3[N_periods + ii + half_size_full + 1 ] *0.5) / window_size
            elif(operation_type == 'min'):
                output_data[ii] = np.min(input_data_x3[N_periods + ii - half_size_full -1 : N_periods + ii + half_size_full + 1 ])
            elif(operation_type == 'max'):
                output_data[ii] = np.max(input_data_x3[N_periods + ii - half_size_full -1 : N_periods + ii + half_size_full + 1 ])
            elif(operation_type == 'sum'):
                output_data[ii] = (
                        np.sum(input_data_x3[N_periods + ii - half_size_full : N_periods + ii + half_size_full ]) 
                        + input_data_x3[N_periods + ii - half_size_full -1 ] *0.5 +  input_data_x3[N_periods + ii + half_size_full + 1 ] *0.5
                        ) 
        
    return output_data

def func_change_in_period (input_data, window_size):
    
    input_data = input_data + 0.0
    output_data = np.zeros(len(input_data))    
    
    # Padding trivial zeros at the beginning
    # Note the change in temporal index
    #       Originally, 0, 1, 2, ..., N-1
    #       Now 0,...0, window_size, ..., N+window_size-1
    
    input_data = np.concatenate((np.zeros(window_size), input_data + 0.0))    

    for ii in range(len(output_data)):
        output_data[ii] = input_data[ii + window_size] - input_data[ii]
        
    return output_data

#%%
# -----------------------------------------------------------------------------
# func_find_period()
#
# Function
#   for a selected window size, find the window that has the maximum or mimum 
#   value of a defined metric
#
# Input
#   input_data, a DICT variable that has the following keys
#       data <np.array> the data to be studied
#       window_size [scalar] the length/size of the moving window
#       search_option <string> 'max' or 'min'
#       print (_option <integer> treated as a logical variable
#
# Output
#   output_data <dict> reports the indice of the window location and the value
#       for this particular window    
#
# Usage
#   to dynamically determine the week that has the maximum or minimum dispatch
#       from a particular technology
#
# History
#   Jun 21-22, 2018 draftd the function
#
# @ Fan Tong
# -----------------------------------------------------------------------------

def func_find_period (input_data):
    
    window_size = input_data['window_size']
    eff_window_size = copy.deepcopy(window_size) # If even go up to next odd number
    if eff_window_size == 2 * int (eff_window_size /2 ):  # check if even
        eff_window_size = eff_window_size + 1             # if so, add 1
    data = input_data['data']
    search_option = input_data['search_option']
    print_option = input_data['print_option']
    
    # -------------------------------------------------------------------------
    
    # Get the down-scaled data
    
    data_in_window = func_time_conversion(data, eff_window_size, 'mean')
    
    # -------------------------------------------------------------------------
    
    if search_option == 'max':
        
        center_index = int(np.argmax(data_in_window))
        value = np.max(data_in_window)
        
    elif search_option == 'min':

        center_index = int(np.argmin(data_in_window))
        value = np.min(data_in_window)

    # -------------------------------------------------------------------------
    # If interval would go over boundary, then move inteval
    if center_index < int(eff_window_size/2):
        center_index = int(eff_window_size/2)
    if center_index > len(data)- int(eff_window_size/2) - 1:
        center_index = len(data) - 1 - int(eff_window_size/2)

    # The same algorithm as in func_time_conversion()

    left_index = center_index - int(eff_window_size/2)
    right_index = center_index + int(eff_window_size/2)

    # -------------------------------------------------------------------------

    # output

    if print_option == 1:
        
        print ( 'center index = {}, value = {}'.format(center_index, value))
        print ( 'left index = {}, right index = {}'.format(left_index, right_index))

    output = {
        'value':        value,
        'left_index':   left_index,
        'right_index':  right_index,
        'center_index': center_index,
        }

    return output

#%%
# -----------------------------------------------------------------------------
# func_bar_plot()
#
# Function
#   draw bar plots; each bar is independent from each other
#
# Input
#   input_data, a DICT variable
#   actual data:
#       x_data [one dimensional] data for determining the x-axis indices
#       y_data <np.ndarray> data for line plots. Each column is a (independent) line.
#   figure handle:
#       ax <figure>. It is usually generated this way
#           fig = plt.figure(figsize=(8,8))
#           ax = fig.add_subplot(111)
#   plotting controls:
#       line_width
#       grid_option
#       x_label
#       y_label
#       title
#       legend
#
# Output
#   ax <figure> subplot figure handle
#
# Usage
#   plotting basic case information
#
# History
#   Jun 22 2018 copied from Fang Tong code
#
# @ Ken Caldeira   
# -----------------------------------------------------------------------------

def func_bar_plot(input_data):
    
    x_data = input_data['x_data'] # should be character strings
    y_data = input_data['y_data'] # should be numbers
    ax = input_data['ax'] # should be axis handle from matplotlib
    
    # -------------------------------------------------------------------------
    
    # setting out the default values, if not provided
    
    if 'line_width' not in input_data.keys():
         line_width  = 1
    else:
        line_width = input_data['line_width']
        
    if 'grid_option' not in input_data.keys():
         grid_option = 0
    else:
         grid_option = input_data['grid_option']

    # -------------------------------------------------------------------------

    # each column is an (independent) bar
    
    idx = np.arange(len(x_data))
    ax.xticks(idx,x_data)
    ax.bar(idx, y_data)  
    
    str_val = ['{}%'.format(y_datum) for y_datum in y_data]
    for i in n:
        ax.text(i,child.get_bbox().y_data[i]*1.05,str_val[i], horizontalalignment ='center')
 
    # -------------------------------------------------------------------------

    # add the plotting styles when needed

    if 'x_label' in input_data.keys():
        ax.set_xlabel(input_data['x_label'])

    if 'y_label' in input_data.keys():
        ax.set_ylabel(input_data['y_label'])

    # ----------------------------
    
    if 'title' in input_data.keys():
        ax.set_title(input_data['title'])

    if 'legend' in input_data.keys():
        ax.legend(input_data['legend'],bbox_to_anchor=(1.04,1),loc=2, borderaxespad=0)    

    if grid_option:
        ax.grid()

    return ax

#%%
# -----------------------------------------------------------------------------
# func_lines_plot()
#
# Function
#   draw line plots; each line is independent from each other
#
# Input
#   input_data, a DICT variable
#   actual data:
#       x_data [one dimensional] data for determining the x-axis indices
#       y_data <np.ndarray> data for line plots. Each column is a (independent) line.
#       y2_data <np.ndarray> data for line plots. Each column is a (independent) line.    
#       x_data_range <tuple> determining the range to draw the plots. While its
#           name includes 'x_data', this variable applies to both x_data and y_data.
#   figure handle:
#       ax <figure>. It is usually generated this way
#           fig = plt.figure(figsize=(8,8))
#           ax = fig.add_subplot(111)
#   plotting controls:
#       line_width
#       grid_option
#       x_label
#       y_label
#       y2_label    
#       title
#       legend
#
# Output
#   ax <figure> subplot figure handle
#
# Usage
#   plotting dispatch mix
#
# History
#   Jun 4-5, 2018 started and finished the function
#   Jun 7-8, 10, 18-19 probably worked on the function    
#   Jun 21, 2018 added parallel axis
#
# @ Fan Tong    
# -----------------------------------------------------------------------------

def func_lines_plot(input_data):

    
    x_data = input_data['x_data']
    y_data = input_data['y_data']
    ax = input_data['ax']
    
    # -------------------------------------------------------------------------
    
    # setting out the default values, if not provided
    
    if 'line_width' not in input_data.keys():
         line_width  = 1
    else:
        line_width = input_data['line_width']
        
    if 'grid_option' not in input_data.keys():
         grid_option = 0
    else:
         grid_option = input_data['grid_option']


    # -------------------------------------------------------------------------

    # determining the plotting range, and then plot accordingly

    if 'x_data_range' in input_data.keys():
        x_data_range = input_data['x_data_range']
    else:
        x_data_range = [0, x_data.size]

    # each column is a (independent) line
    
    if len(y_data.shape) > 1: 
        for i in range(y_data.shape[1]):
            ax.plot(
                    x_data[x_data_range[0]:x_data_range[1]],
                    y_data[x_data_range[0]:x_data_range[1], i], 
                    linewidth = line_width)
    else:
        ax.plot(
                x_data[x_data_range[0]:x_data_range[1]],
                y_data[x_data_range[0]:x_data_range[1]], 
                linewidth = line_width)

    # -------------------------------------------------------------------------
    
    # If a parallel (2nd) y-axis is needed ...
    # I think the code works best when the two axes are scalers of each other.

    if 'y2_data' in input_data.keys():
        ax2 = ax.twinx()
        y2_data = input_data['y2_data']
    
            # each column is a (independent) line
        if len(y_data.shape) > 1: 
            for i in range(y_data.shape[1]):
                ax2.plot(
                        x_data[x_data_range[0]:x_data_range[1]],
                        y2_data[x_data_range[0]:x_data_range[1], i], 
                        linewidth = line_width)
        else:
            ax2.plot(
                    x_data[x_data_range[0]:x_data_range[1]],
                    y2_data[x_data_range[0]:x_data_range[1]], 
                    linewidth = line_width)

        ax2.set_ylabel(input_data['y2_label'])

    # -------------------------------------------------------------------------

    # add the plotting styles when needed

    if 'x_label' in input_data.keys():
        ax.set_xlabel(input_data['x_label'])

    if 'y_label' in input_data.keys():
        ax.set_ylabel(input_data['y_label'])
        
    # ----------------------------
    # axis tickes
    # -----------
    
    # it works, but just too tight.
    # ax.autoscale(enable=True, axis='both', tight=True)

    # set axis ticks
    # ax.tick_params(which='both', width=2, length=6, direction='in')

    # ----------------------------
    
    if 'title' in input_data.keys():
        ax.set_title(input_data['title'])

    if 'legend' in input_data.keys():
        ax.legend(input_data['legend'],bbox_to_anchor=(1.04,1),loc=2, borderaxespad=0)    

    if grid_option:
        ax.grid()
        
                  
    if 'x_scale' in input_data.keys():
        if "log" == input_data['x_scale']:
            ax.set_xscale("log", nonposx='clip')
        else:
            ax.set_xscale(input_data["x_scale"])
            
    if 'y_scale' in input_data.keys():
        if "log" == input_data['y_scale']:
            ax.set_yscale("log", nonposy='clip')
        else:
            ax.set_yscale(input_data["y_scale"])
            
    return ax


#%%
# -----------------------------------------------------------------------------
# func_scatter_plot()
#
# Function
#   draw line plots; each line is independent from each other
#
# Input
#   input_data, a DICT variable
#   actual data:
#       x_data [one dimensional] data for determining the x-axis indices
#       y_data <np.ndarray> data for line plots. Each column is a (independent) line.
#       y2_data <np.ndarray> data for line plots. Each column is a (independent) line.    
#       x_data_range <tuple> determining the range to draw the plots. While its
#           name includes 'x_data', this variable applies to both x_data and y_data.
#   figure handle:
#       ax <figure>. It is usually generated this way
#           fig = plt.figure(figsize=(8,8))
#           ax = fig.add_subplot(111)
#   plotting controls:
#       line_width
#       grid_option
#       x_label
#       y_label
#       y2_label    
#       title
#       legend
#
# Output
#   ax <figure> subplot figure handle
#
# Usage
#   plotting dispatch mix
#
# History
#   Jun 4-5, 2018 started and finished the function
#   Jun 7-8, 10, 18-19 probably worked on the function    
#   Jun 21, 2018 added parallel axis
#
# @ Fan Tong    
# -----------------------------------------------------------------------------

def func_scatter_plot(input_data):
    
    x_data = input_data['x_data']
    y_data = input_data['y_data']
    ax = input_data['ax']
    
    # -------------------------------------------------------------------------
    
    # setting out the default values, if not provided
    
    if 'line_width' not in input_data.keys():
         line_width  = 1
    else:
        line_width = input_data['line_width']
        
    if 'grid_option' not in input_data.keys():
         grid_option = 0
    else:
         grid_option = input_data['grid_option']

    # -------------------------------------------------------------------------

    # determining the plotting range, and then plot accordingly

    if 'x_data_range' in input_data.keys():
        x_data_range = input_data['x_data_range']
    else:
        x_data_range = [0, x_data.size]

    # each column is a (independent) line
    
    if len(y_data.shape) > 1: 
        for i in range(y_data.shape[1]):
            ax.scatter(
                    x_data[x_data_range[0]:x_data_range[1]],
                    y_data[x_data_range[0]:x_data_range[1], i], 
                    linewidth = line_width)
    else:
        ax.scatter(
                x_data[x_data_range[0]:x_data_range[1]],
                y_data[x_data_range[0]:x_data_range[1]], 
                linewidth = line_width)

    # -------------------------------------------------------------------------
    
    # If a parallel (2nd) y-axis is needed ...
    # I think the code works best when the two axes are scalers of each other.

    if 'y2_data' in input_data.keys():
        ax2 = ax.twinx()
        y2_data = input_data['y2_data']
    
            # each column is a (independent) line
        if len(y_data.shape) > 1: 
            for i in range(y_data.shape[1]):
                ax2.scatter(
                        x_data[x_data_range[0]:x_data_range[1]],
                        y2_data[x_data_range[0]:x_data_range[1], i], 
                        linewidth = line_width)
        else:
            ax2.scatter(
                    x_data[x_data_range[0]:x_data_range[1]],
                    y2_data[x_data_range[0]:x_data_range[1]], 
                    linewidth = line_width)

        ax2.set_ylabel(input_data['y2_label'])

    # -------------------------------------------------------------------------

    # add the plotting styles when needed

    if 'x_label' in input_data.keys():
        ax.set_xlabel(input_data['x_label'])

    if 'y_label' in input_data.keys():
        ax.set_ylabel(input_data['y_label'])
        
    # ----------------------------
    # axis tickes
    # -----------
    
    # it works, but just too tight.
    # ax.autoscale(enable=True, axis='both', tight=True)

    # set axis ticks
    # ax.tick_params(which='both', width=2, length=6, direction='in')

    # ----------------------------
    
    if 'title' in input_data.keys():
        ax.set_title(input_data['title'])

    if 'legend' in input_data.keys():
        ax.legend(input_data['legend'],bbox_to_anchor=(1.04,1),loc=2, borderaxespad=0)    

    if grid_option:
        ax.grid()

    return ax

#%%
# -----------------------------------------------------------------------------
# func_lines_2yaxes_plot()
#
# Motivation: plot two lines with two y-axes
# 
# Input
#   A DICT variable named input_data, with the following keys:
#    x_data <numpy array>
#    y1_data <numpy array or ndarray>
#    y2_data <numpy array or ndarray>
#   and, a number of graphics controlling keys
#
# Output    
#   figure: <figure> object.
#
# Usage
#   called upon in func_alternative_storage_graphics()    
#    
# History
#   June 3, 2018 wrote the code
#   June 18-19, 2018 packaged the code into this function
#
# @ Fan Tong    
# -----------------------------------------------------------------------------

def func_lines_2yaxes_plot (input_data):
    
    # -------------------------------------------------------------------------
    # get the input data
    
    ax1 = input_data['ax']
    x_data = input_data['x_data']
    y1_data = input_data['y1_data']
    y2_data = input_data['y2_data']
    
    # -------------------------------------------------------------------------
    # actual plotting      
    
    if len(y1_data.shape) > 1:
        
        # When y1_data is a numpy ndarray
        
        for i in range(y1_data.shape[1]):
            ax1.plot(x_data, y1_data[:, i], 'b')
    else:
        
        # When y1_data is a numpy array
        ax1.plot(x_data, y1_data, 'b')    
        
    ax2 = ax1.twinx()
    
    if len(y2_data.shape) > 1:
        
        # When y2_data is a numpy ndarray
        
        for i in range(y2_data.shape[1]):
            ax2.plot(x_data, y2_data[:, i], 'r')
    else:
        
        # When y2_data is a numpy array 
        
        ax2.plot(x_data, y2_data, 'r')
    
    ax1.tick_params(axis='y', labelcolor='b')        
    ax2.tick_params(axis='y', labelcolor='r')        
        
    # -------------------------------------------------------------------------
    # decoration
    
#    if 'x_axis_log' in input_data.keys():
#        ax1.set_xscale('log', nonposx='clip')
#        
#    if 'y1_axis_log' in input_data.keys():       
#        ax1.set_yscale('log', nonposx='clip')
#        
#    if 'y2_axis_log' in input_data.keys():
#        ax2.set_yscale('log', nonposx='clip')
    
    if 'x_label' in input_data.keys():
        ax1.set_xlabel(input_data['x_label'])

    if 'y1_label' in input_data.keys():
        ax1.set_ylabel(input_data['y1_label'], color='b')
        
    if 'y2_label' in input_data.keys():
        ax2.set_ylabel(input_data['y2_label'], color='r')
    
    if 'title' in input_data.keys():
        ax1.set_title(input_data['title'])

    if 'legend' in input_data.keys():
        ax1.legend(input_data['legend'],bbox_to_anchor=(1.04,1),loc=2, borderaxespad=0)
    
    return [ax1, ax2]

#%%
# -----------------------------------------------------------------------------
# func_stack_plot()
#
# Function
#   draw stacked line/area plots; each line/area is independent from each other
#
# Input
#   input_data, a DICT variable
#   actual data:
#       x_data [one dimensional] data for determining the x-axis indices
#       y_data <np.ndarray> data for line plots. Each column is a (independent) line.
#       y2_data <np.ndarray> data for line plots. Each column is a (independent) line.     
#       x_data_range <tuple> determining the range to draw the plots. While its
#           name includes 'x_data', this variable applies to both x_data and y_data.
#   figure handle:
#       ax <figure>. It is usually generated this way
#           fig = plt.figure(figsize=(8,8))
#           ax = fig.add_subplot(111)
#   plotting controls:
#       line_width
#       grid_option
#       x_label
#       y_label
#       y2_label    
#       title
#       legend
# 
#   note that there are some additional decorations
#       z_data
#       legend_z
#       line_width_z
#
# Output
#   ax <figure> subplot figure handle
#
# Usage
#   plotting dispatch mix
#
# History
#   Jun 4-5, 2018 started and finished the function
#   Jun 7-8, 10, 18-19 probably worked on the function    
#   Jun 21, 2018 added parallel axis
#
# @ Fan Tong
# -----------------------------------------------------------------------------

def func_stack_plot (input_data):
    
    x_data = input_data['x_data']
    y_data = input_data['y_data']
    ax = input_data['ax']
    
    # -------------------------------------------------------------------------
    
    # setting out the default values, if not provided
    
    if 'line_width' not in input_data.keys():
         line_width  = 1
    else:
        line_width = input_data['line_width']
    
    if 'legend' not in input_data.keys():
        legend  = []
    else:
        legend = input_data['legend']

    
    if 'grid_option' not in input_data.keys():
         grid_option = 0
    else:
         grid_option = input_data['grid_option']    

    # -----------------------------------------------------------------------

    # determining the plotting range, and then plot accordingly

    if 'x_data_range' in input_data.keys():
        x_data_range = input_data['x_data_range']
    else:
        x_data_range = [0, x_data.size]        
        
    ax.stackplot(
            x_data[x_data_range[0]:x_data_range[1]], 
            np.array(y_data[x_data_range[0]:x_data_range[1], :].T),
            linewidth = line_width)

    # -------------------------------------------------------------------------
    
    # If a parallel (2nd) y-axis is needed ...
    # I think the code works best when the two axes are scalers of each other.

    if 'y2_data' in input_data.keys():
        
        ax2 = ax.twinx()
        y2_data = input_data['y2_data']
    
        ax2.stackplot(
                x_data[x_data_range[0]:x_data_range[1]], 
                np.array(y2_data[x_data_range[0]:x_data_range[1], :].T),
                linewidth = line_width)
    
        ax2.set_ylabel(input_data['y2_label'])

    # -------------------------------------------------------------------------

    # the use of 'z_data' is to show the DEMAND line on the stacked plot (dispatch mix)
    # this is not the cleanest way, but bear with it

    if 'z_data' in input_data.keys():
        
        # print ( 'z plotting'
        
        ax.plot(
                x_data[x_data_range[0]:x_data_range[1]], 
                input_data['z_data'][x_data_range[0]:x_data_range[1]], 
                color='k', 
                linewidth = input_data['line_width_z'])
        
#        ax2.plot(
#                x_data[x_data_range[0]:x_data_range[1]], 
#                input_data['z2_data'][x_data_range[0]:x_data_range[1]], 
#                color='k', 
#                linewidth = input_data['line_width_z'])
        
        # add 'legend_z' at the beginning because this way could work
        legend = np.concatenate(([input_data['legend_z']], legend))
        
        # print ( legend

    # -------------------------------------------------------------------------

    # add the plotting styles when needed

    if 'x_label' in input_data.keys():
        ax.set_xlabel(input_data['x_label'])

    if 'y_label' in input_data.keys():
        ax.set_ylabel(input_data['y_label']) 

    # ----------------------------
    # axis tickes
    # -----------

    # It works, but just too tight.
    # ax.autoscale(enable=True, axis='both', tight=True)

    # Set axis ticks
    # ax.tick_params(which='both', width=2, length=6, direction='in')

    # ----------------------------

    if 'title' in input_data.keys():
        ax.set_title(input_data['title'])

    if 'legend' in input_data.keys():
#        ax.legend(legend, loc='best')    
        ax.legend(legend,bbox_to_anchor=(1.04,1),loc=2, borderaxespad=0)   # put legend to right of figure  

    if grid_option:
        ax.grid()

    return ax
        
#%%
# -----------------------------------------------------------------------------
# func_PMF_plot()
#
# Function
#   draw histogram figure
#   Note that there are at least three types,
#       frequency plot, for discret events
#       probability mass function, for discrete events
#       probability density function, for continual events.
#
# Input
#   input_data, a DICT variable
#   actual data:
#       x_data [one dimensional] data for determining the x-axis indices
#       y_data <np.ndarray> data for line plots. Each column is a (independent) line.
#       x_data_range <tuple> determining the range to draw the plots. While its
#           name includes 'x_data', this variable applies to both x_data and y_data.
#   figure handle:
#       ax <figure>. It is usually generated this way
#           fig = plt.figure(figsize=(8,8))
#           ax = fig.add_subplot(111)
#   plotting controls:
#       line_width
#       grid_option
#       x_label
#       y_label
#       title
#       legend
# 
#   note that there are some additional decorations
#       z_data
#       legend_z
#       line_width_z
#
# Output
#   ax <figure> subplot figure handle
#
# Usage
#   plotting dispatch mix
#
# History
#   May 31, 2018    
#
# @ Fan Tong
# -----------------------------------------------------------------------------

def func_PMF_plot(input_data):
    
    x_data = input_data['x_data']    
    num_bins = input_data['num_bins']
    ax = input_data['ax']    
    
    # -------------------------------------------------------------------------
    
    # draw the probability mass function histograms
    
    hist_weights = np.ones_like(x_data) / len(x_data)
    
    ax.hist(
            x_data, 
            bins=num_bins, 
            weights = hist_weights, 
            # color='blue',
            alpha=0.5,                  # transparency setting
            normed=False) 

    # -------------------------------------------------------------------------

    # add the plotting styles when needed

    if 'x_label' in input_data.keys():
        ax.set_xlabel(input_data['x_label'])

    if 'y_label' in input_data.keys():
        ax.set_ylabel(input_data['y_label'])
    
    if 'title' in input_data.keys():
        ax.set_title(input_data['title'])

    if 'legend' in input_data.keys():
        ax.legend(input_data['legend'],bbox_to_anchor=(1.04,1),loc=2, borderaxespad=0)        
    
    x_axis_max = 1.1 * max(x_data)
    
    if 'zero_one_range' in input_data.keys():
        ax.set_xlim(0, min(1, x_axis_max))
    else:    
        ax.set_xlim(0, x_axis_max)
    
#    if 'zero_one_range' in input_data.keys():
#        ax.set_xlim(0, min(1,10**np.ceil(np.log10(np.max(x_data)+1e-8))))
#    else:    
#        ax.set_xlim(0, 10**np.ceil(np.log10(np.max(x_data)+1e-8)))

    return ax