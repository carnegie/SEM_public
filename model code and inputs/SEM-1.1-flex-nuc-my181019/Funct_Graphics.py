# -*- coding: utf-8 -*-
"""
Funct_Graphics.py

Function: this file collects defined functions for plotting optimization results
    from one optimization run or mutilple runs

Functions defined
    func_graphics_dispatch_mix_1scenario()
    func_graphics_dispatch_mix_time_selection_1scenario()
    func_graphics_dispatch_mix_technology_timeseries_1scenario()
    func_graphics_dispatch_var_Nscenarios()
    func_graphics_system_results_Nscenarios()
    func_optimization_results_time_series_1scenario() -- directly callable
    func_optimization_results_system_results_Nscenarios() -- directly callable
    func_optimization_results_dispatch_var_Nscenarios() -- directly callable

History
    Jun 4-5, 2018 completely rewritten
        func_graphics_dispatch_mix_1scenario()
        func_graphics_dispatch_mix_time_selection()
        func_graphics_dispatch_var_Nscenarios()
                        
    Jun 17-18, 2018 added a new function, and updated the comments
        func_graphics_system_results_Nscenarios()

    Jun 19, 2018
        fixed some errors in func_graphics_dispatch_mix_1scenario()
        rewrote some function names
    Jun 20, 2018
        slight changes due to changes the definition of func_lines_2yaxes_plot()
        added the dual y-axes for some figures in func_graphics_system_results_Nscenarios()
        added two functions for multiple-scenario analysis
            func_optimization_results_snapshot_Nscenarios()
            func_optimization_results_dispatch_var_Nscenarios()
    Jun 21, 2018
        fixed errors caused by using the actual division than the integer division.
        added parallel axes for some figures in 
            func_graphics_dispatch_mix_1scenario()
            func_graphics_dispatch_mix_time_selection_1scenario()
            func_graphics_time_series_results_1scenario()
            func_graphics_dispatch_var_Nscenarios()
            func_optimization_results_system_results_Nscenarios()
        changed packaging functions' names
            func_graphics_time_series_results_1scenario -> func_optimization_results_time_series_1scenario
            func_optimization_results_snapshot_Nscenarios -> func_optimization_results_system_results_Nscenarios
        changed the function func_graphics_dispatch_mix_1scenario()
            from fixed ranges in time to dynamically select the weeks with the largest/smallest share of a technology
    Jun 22-23, 2018
        updated the following two functions
            func_optimization_results_system_results_Nscenarios()
            func_graphics_dispatch_mix_time_selection_1scenario()
        .. so that the selected time ranges are determined for the "extreme" weeks
        .. for a technology of interest
    Jun 23, 2018 checked the code and comments
    June 23-24, 2018 updated texts and labels on figures
    Jul 8, 2018 [kc]
        Started making changes so this code runs off of dictionaries rather
        than pickle files. This will then be called by <quicklook.py>
            
@author: Fan Tong
"""

from __future__ import division
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from Supporting_Functions import func_find_period
from Supporting_Functions import func_lines_plot
from Supporting_Functions import func_lines_2yaxes_plot
from Supporting_Functions import func_stack_plot
from Supporting_Functions import func_time_conversion
from Supporting_Functions import func_load_optimization_results
from matplotlib.backends.backend_pdf import PdfPages

#%%
#==============================================================================
# func_graphics_dispatch_mix_1scenario
#
# Purpose
#   Generate dispatch mix figures. Right now, there are N*4 figures.
#       N=3 corresponds to different temporal resolutions: hourly, daily, weekly.
#       4 corresponds to subplots for the same "information" (time scale).
#
# Input
#   A packaging dictionary variable: input_data, which contrains the following data
#       [1] dispatched_results_matrix:  dispatch mix for a particular scenario
#       [2] demand
#   the following texts
#       [3] legend_list
#       [4] title_text
#   and the following controls for graphical outputs
#       [5] SAVE_FIGURES_TO_PDF:   logical variable [0/1]
#       [6] directory_output:      a complete directory, ending with "/"
#       [7] graphics_file_name
#
#   Data dimentions
#       dispatched_results_matrix
#           ROW dimension: optimization time steps
#           COLUMN dimension: technology options (that dispatched energy)
#       demand
#           ROW dimension: optimization time steps
#           Column dimension: none
#       legend list
#           Number of STRING items: technology options (that dispatched energy)
#
# Output
#   6 figures in the console window.
#   You can choose to save them to a PDF book or not.
#
# History
#   Jun 4-5, 2018 started and finished
#   Jun 21, 2018 
#       fixed the bug caused by using the actual division rather than the default floor division.
#       updated the time selection from predefined to dynamically determined.
#
# @Fan Tong
#==============================================================================

def func_graphics_dispatch_mix_1scenario (input_data):    
    
    # -------------------------------------------------------------------------
    # Get the input data
    
    demand = input_data["demand"]
    dispatched_results_matrix = input_data["dispatched_results_matrix"]
    demand_results_matrix = input_data["demand_results_matrix"]
    directory_output = input_data["directory_output"]
    SAVE_FIGURES_TO_PDF = input_data["SAVE_FIGURES_TO_PDF"]    
    graphics_file_name = input_data["graphics_file_name"]
    legend_list_dispatch = input_data["legend_list_dispatch"]
    legend_list_demand = input_data["legend_list_demand"]    
    
    # -------------------------------------------------------------------------    
    # Create the ouput folder    
    
    if SAVE_FIGURES_TO_PDF:
        if not os.path.exists(directory_output):
            os.makedirs(directory_output)
                        
        pdf_pages = PdfPages(
            directory_output + graphics_file_name + '.pdf')

    # -------------------------------------------------------------------------
    # Define the plotting style
    
    plt.style.use('default')
    # plt.style.use('bmh')
    # plt.style.use('fivethirtyeight')
    # plt.style.use('seaborn-white')
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] =  'Helvetica ' #'Palatino' # 'Ubuntu'
    plt.rcParams['font.monospace'] = 'Helvetica Mono' #'Palatino Mono' # 'Ubuntu'
    plt.rcParams['font.size'] = 16
    plt.rcParams['axes.labelsize'] = 16
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['xtick.labelsize'] = 16
    plt.rcParams['ytick.labelsize'] = 16
    plt.rcParams['legend.fontsize'] = 14
    plt.rcParams['figure.titlesize'] = 16
    plt.rcParams['lines.linewidth'] = 2.0
    plt.rcParams['grid.color'] = 'k'
    plt.rcParams['grid.linestyle'] = ':'
    plt.rcParams['grid.linewidth'] = 0.5
    plt.rcParams['xtick.major.width'] = 2
    plt.rcParams['xtick.major.size'] = 6
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.major.width'] = 2
    plt.rcParams['ytick.major.size'] = 6
    plt.rcParams['ytick.direction'] = 'in'
    
    figsize_oneplot = (8,6)
    
    # -------------------------------------------------------------------------
    # Figures 1 Hourly time series results
    
    # Four figures: 2 (dispatch, demand) * 2 (line plots, stack plots)
    
    # -------------
    
    optimization_time_steps = demand.size
    x_data = np.arange(0, optimization_time_steps)
    
    # -------------
    
    figure1a = plt.figure(figsize=figsize_oneplot)
    ax1a = figure1a.add_subplot(111)
    
    inputs_dispatch = {
        "x_data":           x_data, 
#        "y_data":           dispatched_results_matrix/1e6,
        "y_data":           dispatched_results_matrix,
        "y2_data":          dispatched_results_matrix/np.average(demand),
#        'z_data':           demand/1e6,
        'z_data':           demand,
        'z2_data':          demand/np.average(demand),
        "ax":               ax1a,
        "x_label":          'Time (hour in the year)',
        "y_label":          '1e6 kWh',
        'y2_label':         'hourly-average demand',
        "title":            'Dispatch mix',
        "legend":           legend_list_dispatch,
        "legend_z":         'demand',
        "line_width":       2,
        "line_width_z":     0.2,
        'grid_option':      0,
        }        

    func_lines_plot(inputs_dispatch)
    
    # -------------
    
    figure1b = plt.figure(figsize=figsize_oneplot)
    ax1b = figure1b.add_subplot(111)

    inputs_dispatch["ax"] = ax1b
    func_stack_plot(inputs_dispatch)
    
    # -------------

    figure1c = plt.figure(figsize=figsize_oneplot)
    ax1c = figure1c.add_subplot(111)

    inputs_demand = {
        "x_data":           x_data, 
        "y_data":           demand_results_matrix/1e6,
        "y2_data":          demand_results_matrix/np.average(demand),
        #'z_data':           demand/1e6,
        "ax":               ax1c,
        "x_label":          'Time (hour in the year)',
#        "y_label":          '1e6 kWh',
        'y2_label':         'hourly-average demand',
        "title":            'Demand mix',
        "legend":           legend_list_demand,
        #"legend_z":         'demand',
        "line_width":       2,
        #"line_width_z":     0.2,
        'grid_option':      0,
        } 
          
    func_lines_plot(inputs_demand)
    
    # -------------
    
    figure1d = plt.figure(figsize=figsize_oneplot)
    ax1d = figure1d.add_subplot(111)

    inputs_demand["ax"] = ax1d
    
    func_stack_plot(inputs_demand) 

    # -------------

    if SAVE_FIGURES_TO_PDF:
        pdf_pages.savefig(figure1a, bbox_inches='tight')
        plt.close()
        
        pdf_pages.savefig(figure1b, bbox_inches='tight')
        plt.close()
        
        pdf_pages.savefig(figure1c, bbox_inches='tight')
        plt.close()
        
        pdf_pages.savefig(figure1d, bbox_inches='tight')
        plt.close()
        
    # -------------------------------------------------------------------------
    
    # Figures 2 Daily results
    
    # Four figures: 2 (dispatch, demand) * 2 (line plots, stack plots)

    # -------------

    temporal_scale = 24
    x_data = np.arange(0, optimization_time_steps/temporal_scale)
    
    dispatched_results_matrix2 = np.zeros(
        (int(dispatched_results_matrix.shape[0]/temporal_scale), 
        int(dispatched_results_matrix.shape[1])))

    for i in xrange(dispatched_results_matrix2.shape[1]):
        dispatched_results_matrix2 [:,i] = \
            func_time_conversion(dispatched_results_matrix[:,i],temporal_scale)

    demand_results_matrix2 = np.zeros(
        (int(demand_results_matrix.shape[0]/temporal_scale), 
        int(demand_results_matrix.shape[1])))
    
    for i in xrange(demand_results_matrix2.shape[1]):
        demand_results_matrix2 [:,i] = \
            func_time_conversion(demand_results_matrix[:,i],temporal_scale)

    # -------------

    figure2a = plt.figure(figsize=figsize_oneplot)
    ax2a = figure2a.add_subplot(111)

    inputs_dispatch = {
        "x_data":           x_data, 
        "y_data":           dispatched_results_matrix2/1e6,
        "y2_data":          dispatched_results_matrix2/np.average(demand),
        "z_data":           func_time_conversion(demand/1e6,temporal_scale),
        "z2_data":           func_time_conversion(demand/np.average(demand),temporal_scale),
        "ax":               ax2a,
        "x_label":          'Time (day in the year)',
        "y_label":          '1e6 kWh',
        "y2_label":         'hourly-average demand',
        "title":            'Dispatch mix',
        "legend":           legend_list_dispatch,
        "legend_z":         'demand',
        "line_width":       2,
        "line_width_z":     1,
        'grid_option':      0,
        }
    
    func_lines_plot(inputs_dispatch)
    
    # -------------
    
    figure2b = plt.figure(figsize=figsize_oneplot)
    ax2b = figure2b.add_subplot(111)
    inputs_dispatch['ax'] = ax2b
    
    func_stack_plot(inputs_dispatch)

    # -------------

    figure2c = plt.figure(figsize=figsize_oneplot)
    ax2c = figure2c.add_subplot(111)

    # -------------

    inputs_demand = {
        "x_data":           x_data, 
        "y_data":           demand_results_matrix2/1e6,
        "y2_data":          demand_results_matrix2/np.average(demand),
        #"z_data":           func_time_conversion(demand/1e6,temporal_scale),
        "ax":               ax2c,
        "x_label":          'Time (day in the year)',
        "y_label":          '1e6 kWh',
        "y2_label":         'hourly-average demand',
        "title":            'Demand mix',
        "legend":           legend_list_demand,
        #"legend_z":         'demand',
        "line_width":       2,
        #"line_width_z":     1,
        'grid_option':      0,
        }

    func_lines_plot(inputs_demand)
    
    # -------------

    figure2d = plt.figure(figsize=figsize_oneplot)
    ax2d = figure2d.add_subplot(111)
    inputs_demand['ax'] = ax2d
    
    func_stack_plot(inputs_demand) 
    
    # -------------
    
    if SAVE_FIGURES_TO_PDF:
        pdf_pages.savefig(figure2a, bbox_inches='tight')
        plt.close()
        
        pdf_pages.savefig(figure2b, bbox_inches='tight')
        plt.close()
        
        pdf_pages.savefig(figure2c, bbox_inches='tight')
        plt.close()
        
        pdf_pages.savefig(figure2d, bbox_inches='tight')
        plt.close()

    # -------------------------------------------------------------------------
    # Figures 3 Weekly time series results

    # Four figures: 2 (dispatch, demand) * 2 (line plots, stack plots)

    # -------------

    temporal_scale = 24 * 7
    x_data = np.arange(0, np.floor (optimization_time_steps/temporal_scale))
    
    # --------------------
    
    # Note: 
    #   (1) use floor_division to be compatiable with func_time_conversion()    
    #   (2) force type conversion to integer for slice indices
    
    dispatched_results_matrix3 = np.zeros(
        (int(np.floor(dispatched_results_matrix.shape[0]/temporal_scale)), 
        int(dispatched_results_matrix.shape[1]))
        )

    for i in xrange(dispatched_results_matrix3.shape[1]):
        dispatched_results_matrix3 [:,i] = \
            func_time_conversion(dispatched_results_matrix[:,i],temporal_scale)

    demand_results_matrix3 = np.zeros(
        (int(np.floor(demand_results_matrix.shape[0]/temporal_scale)),
        int(demand_results_matrix.shape[1]))
        )
    
    for i in xrange(demand_results_matrix3.shape[1]):
        demand_results_matrix3 [:,i] = \
            func_time_conversion(demand_results_matrix[:,i],temporal_scale)
    
    # --------------------

    figure3a = plt.figure(figsize=figsize_oneplot)
    ax3a = figure3a.add_subplot(111)

    inputs_dispatch = {
        "x_data":           x_data, 
        "y_data":           dispatched_results_matrix3/1e6,
        "y2_data":          dispatched_results_matrix3/np.average(demand),
        "z_data":           func_time_conversion(demand/1e6,temporal_scale),
        "z2_data":          func_time_conversion(demand/np.average(demand),temporal_scale),
        "ax":               ax3a,
        "x_label":          'Time (week in the year)',
        "y_label":          '1e6 kWh',
        "y2_label":         'hourly-average demand',
        "title":            'Dispatch mix',
        "legend":           legend_list_dispatch,
        "legend_z":         'demand',
        "line_width":       2,
        "line_width_z":     1,
        'grid_option':      0,
        }

    func_lines_plot(inputs_dispatch)
    
    # --------------------
    
    figure3b = plt.figure(figsize=figsize_oneplot)
    ax3b = figure3b.add_subplot(111)
    inputs_dispatch['ax'] = ax3b
    
    func_stack_plot(inputs_dispatch)

    # --------------------
    
    figure3c = plt.figure(figsize=figsize_oneplot)
    ax3c = figure3c.add_subplot(111)
    
    inputs_demand = {
        "x_data":           x_data, 
        "y_data":           demand_results_matrix3/1e6,
        "y2_data":           demand_results_matrix3/np.average(demand),
        #"z_data":           func_time_conversion(demand/1e6,temporal_scale),
        "ax":               ax3c,
        "x_label":          'Time (week in the year)',
        "y_label":          '1e6 kWh',
        "y2_label":         'hourly-average demand',
        "title":            'Demand mix',
        "legend":           legend_list_demand,
        #"legend_z":         'demand',
        "line_width":       2,
        #"line_width_z":     1,
        'grid_option':      0,
        }

    func_lines_plot(inputs_demand)
    
    # --------------------
    
    figure3d = plt.figure(figsize=figsize_oneplot)
    ax3d = figure3d.add_subplot(111)
    inputs_demand['ax'] = ax3d
    
    func_stack_plot(inputs_demand)
    
    # --------------------
    
    if SAVE_FIGURES_TO_PDF:
        pdf_pages.savefig(figure3a, bbox_inches='tight')
        plt.close()
        
        pdf_pages.savefig(figure3b, bbox_inches='tight')
        plt.close()
        
        pdf_pages.savefig(figure3c, bbox_inches='tight')
        plt.close()
        
        pdf_pages.savefig(figure3d, bbox_inches='tight')
        plt.close()
    
    # -------------------------------------------------------------------------
    
    # Write the PDF document to the disk
    
    if SAVE_FIGURES_TO_PDF:
        pdf_pages.close()


#%%
#==============================================================================
# func_graphics_dispatch_mix_time_selection_1scenario
#
# Purpose
#   Generate two time series figures (line plots and stack plots) 
#       for a mix of technologies (dispatch mix) or a mix of demands (demand mix)
#
# Input
#   A packaging dictionary variable: input_data, which contrains the following data
#       [1] mix_matrix:  dispatch mix or demand mix
#       [2] demand:      demand data
#       [3] time_range:  the time period of interest
#   the following texts
#       [3] legend_list
#       [4] title_text
#   and the following controls for graphical outputs
#       [5] SAVE_FIGURES_TO_PDF:   logical variable [0/1]
#       [6] pdf_pages:   a <PDF> object passed from the outer function
#        
#   Data dimentions
#       mix_matrix
#           ROW dimension: optimization time steps
#           COLUMN dimension: technology options or types of demands
#       demand
#           ROW dimension: optimization time steps
#           Column dimension: none
#       legend list
#           list of STRINGs: correspond to the COLUMN of mix_matrix
#
# Output
#   Generate 2 figures (line plots and stack plots)
#   The outer function will determine the file saving option.
#
# Usage
#   Show dispatch mix time series figures for a selective time period.        
#
# History
#   June 4-5, 2018 started and finished the code
#   June 22, 2018 moved (the PDF file creation and closure) to the upper function
#   June 23-24, 2018 updated texts and labels on figures        
#
# @Fan Tong
#==============================================================================

def func_graphics_dispatch_mix_time_selection_1scenario (input_data):
    
    # -------------------------------------------------------------------------
    # Get the input data
    
    demand = input_data["demand"]
    mix_matrix = input_data["mix_matrix"]
    time_range = input_data["time_range"]
    
    SAVE_FIGURES_TO_PDF = input_data["SAVE_FIGURES_TO_PDF"]
    legend_list = input_data["legend_list"]
    title_text = input_data["title_text"]
    
    # -------------------------------------------------------------------------
    
    figsize_oneplot = (8, 6)
    
    # -------------------------------------------------------------------------
    # Figures 1-2 Hourly time series results
    
    optimization_time_steps = mix_matrix.shape[0]
    x_data = np.arange(0, optimization_time_steps)    

    # -------------------------------------------------------------------------

    figure1 = plt.figure(figsize=figsize_oneplot)
    ax1 = figure1.add_subplot(111)

    input_data_1 = {
        "x_data_range":     time_range,
        "x_data":           x_data, 
        "y_data":           mix_matrix/1e6,
        "y2_data":          mix_matrix/np.average(demand),
        "ax":               ax1,
        "x_label":          'Time (hour in the year)',
        "y_label":          '1e6 kWh',
        'y2_label':         'hourly-average demand',
        "title":            title_text,
        "legend":           legend_list,
        "line_width":       2,
        'grid_option':      0,
        }
    func_lines_plot(input_data_1)
    
    # -------------------------
    
    figure2 = plt.figure(figsize=figsize_oneplot)
    ax2 = figure2.add_subplot(111)
    
    input_data_2 = {
        "x_data_range":     time_range,
        "x_data":           x_data, 
        "y_data":           mix_matrix/1e6,
        "y2_data":          mix_matrix/np.average(demand),
        "ax":               ax2,
        "x_label":          'Time (hour in the year)',
        "y_label":          '1e6 kWh',
        "y2_label":         'hourly-average demand',
        "title":            title_text,
        "legend":           legend_list,
        "line_width":       2,
        'grid_option':      0,
        }
    
    if "demand_line_for_dispatch_figure" in input_data.keys():       
        
        # line_width_z = 1/np.log(optimization_time_steps)*np.log(6)
        
        if (time_range[1] - time_range[0]) < 200:
            line_width_z = 2
        elif (time_range[1] - time_range[0]) < 1000:
            line_width_z = 1.5
        else:
            line_width_z = 1
        
        input_data_2['z_data'] = demand/1e6
        input_data_2['z2_data'] = demand/np.average(demand)
        input_data_2['legend_z'] = 'demand'
        input_data_2['line_width_z'] = line_width_z   

    func_stack_plot(input_data_2)    

    # -------------------------

    if SAVE_FIGURES_TO_PDF:
        
        pdf_pages = input_data["pdf_pages"]
        
        pdf_pages.savefig(figure1, bbox_inches='tight')
        plt.close()
        
        pdf_pages.savefig(figure2, bbox_inches='tight')
        plt.close()
   
#%%
#==============================================================================
# func_graphics_dispatch_var_Nscenarios
#
# Purpose
#   Generate 4*2 figures regarding dispatched energy from a particular technology
#       over a number of scenarios considered.
#   In each pair of figures, different axes are assumed.
#
# Input
#   A packaging dictionary variable: input_data, which contrains the following data
#       [1] dispatched_results_matrix:  
#           dispatch energy time series for the same technology
#           across a number of different scenarios
#       [2] demand
#   the following texts
#       [3] legend_list
#       [4] title_text
#   and the following controls for graphical outputs
#       [5] SAVE_FIGURES_TO_PDF:   logical variable [0/1]
#       [6] directory_output:      a complete directory, ending with "/"
#       [7] graphics_file_name        
#
#   Data dimentions
#       dispatched_results_matrix
#           ROW dimension: optimization time steps
#           COLUMN dimension: different scenarios
#       legend list
#           number of STRING items: different scenarios
#
# Output
#   4 figures in the console window.
#   You can choose to save them to a PDF book or not.
#
# History
#   June 4-5, 2018 started and finished the code
#   June 20, 2018 added "demand" input for axis labels
#   June 24, 2018 added parallel axes, thus reducing the total number of figures to 4
#        
# @Fan Tong
#==============================================================================

def func_graphics_dispatch_var_Nscenarios (input_data):

    # -------------------------------------------------------------------------
    # Get the input data
    
    demand = input_data["demand"]
    dispatched_results_matrix = input_data["dispatched_results_matrix"]
    
    legend_list = input_data["legend_list"]
    title_text = input_data["title_text"]   
    
    directory_output = input_data["directory_output"]
    SAVE_FIGURES_TO_PDF = input_data["SAVE_FIGURES_TO_PDF"]    
    graphics_file_name = input_data["graphics_file_name"]     
    
    # -------------------------------------------------------------------------
    # Create the output folder
    
    if SAVE_FIGURES_TO_PDF:
        
        if not os.path.exists(directory_output):
            os.makedirs(directory_output)
        
        pdf_pages = PdfPages(
                directory_output + graphics_file_name + '.pdf')
    
    # -------------------------------------------------------------------------
    # Define the plotting style
    
    plt.style.use('default')
    # plt.style.use('bmh')
    # plt.style.use('fivethirtyeight')
    # plt.style.use('seaborn-white')
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] =  'Helvetica ' #'Palatino' # 'Ubuntu'
    plt.rcParams['font.monospace'] = 'Helvetica Mono' #'Palatino Mono' # 'Ubuntu'
    plt.rcParams['font.size'] = 16
    plt.rcParams['axes.labelsize'] = 16
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['xtick.labelsize'] = 16
    plt.rcParams['ytick.labelsize'] = 16
    plt.rcParams['legend.fontsize'] = 14
    plt.rcParams['figure.titlesize'] = 16
    plt.rcParams['lines.linewidth'] = 2.0
    plt.rcParams['grid.color'] = 'k'
    plt.rcParams['grid.linestyle'] = ':'
    plt.rcParams['grid.linewidth'] = 0.5
    plt.rcParams['xtick.major.width'] = 2
    plt.rcParams['xtick.major.size'] = 6
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.major.width'] = 2
    plt.rcParams['ytick.major.size'] = 6
    plt.rcParams['ytick.direction'] = 'in'
    
    # -------------------------------------------------------------------------
    
    figsize_oneplot = (8,6)
    
    # -------------------------------------------------------------------------
    
    # Figure 1 Sorted time series of discharging - y axis option #1
    
    # -----------------------------
    
    optimization_time_steps = dispatched_results_matrix.shape[0]
    x_data = np.arange(0, optimization_time_steps)
    
    dispatched_results_matrix1 = np.zeros(
            dispatched_results_matrix.shape)
    
    for i in xrange(dispatched_results_matrix.shape[1]):
        dispatched_results_matrix1 [:,i] = \
            -np.sort(-np.reshape(dispatched_results_matrix[:,i], -1))
    
    # -----------------------------
    
    figure1 = plt.figure(figsize=figsize_oneplot)
    ax1 = figure1.add_subplot(111)
    
    inputs = {
            "x_data":       x_data, 
            "y_data":       dispatched_results_matrix1/1e6,
            "y2_data":      dispatched_results_matrix1/np.average(demand),
            "ax":           ax1,
            "x_label":      'Time (hour in the year)',
            "y_label":      '1e6 kWh',
            "y2_label":     'hourly-average demand',
            "title":        title_text,
            "legend":       legend_list,
            "line_width":    2,
            'grid_option':   1,
            }        
            
    func_lines_plot(inputs)
    
    if SAVE_FIGURES_TO_PDF:
        pdf_pages.savefig(figure1, bbox_inches='tight')
        plt.close()
        
#    # ---------------------------
#    
#    # Figure 1b  Sorted time series of discharging - y axis option #2
#    
#    # -----------------------------
#    
##    optimization_time_steps = dispatched_results_matrix.shape[0]
##    x_data = np.arange(0, optimization_time_steps)
##    
##    dispatched_results_matrix1 = np.zeros(
##            dispatched_results_matrix.shape)
##    
##    for i in xrange(dispatched_results_matrix.shape[1]):
##        dispatched_results_matrix1 [:,i] = \
##            -np.sort(-np.reshape(dispatched_results_matrix[:,i], -1))
#    
#    # -----------------------------
#    
#    figure1b = plt.figure(figsize=figsize_oneplot)
#    ax1b = figure1b.add_subplot(111)
#    
#    inputs = {
#            "x_data":       x_data, 
#            "y_data":       dispatched_results_matrix1/np.average(demand),
#            "ax":           ax1b,
#            "x_label":      'Time (hour in the year)',
#            "y_label":      'Dispatched energy\n(hourly-average demand)',
#            "title":        title_text,
#            "legend":       legend_list,
#            "line_width":    2,
#            'grid_option':   1,
#            }        
#            
#    func_lines_plot(inputs)
#    
#    if SAVE_FIGURES_TO_PDF:
#        pdf_pages.savefig(figure1b, bbox_inches='tight')
#        plt.close()
        
    # -------------------------------------------------------------------------
    # Figure 2. Time series of discharging - y axis option #1
    
    # -----------------------------
    
    # x_data = np.arange(0, optimization_time_steps)
    
    # -----------------------------
    
    figure2 = plt.figure(figsize=figsize_oneplot)
    ax2 = figure2.add_subplot(111)
    
    inputs = {
            "x_data":       x_data, 
            "y_data":       dispatched_results_matrix/1e6,
            "y2_data":      dispatched_results_matrix/np.average(demand),
            "ax":           ax2,
            "x_label":      'Time (hour in the year)',
            "y_label":      '1e6 kWh',
            "y2_label":     'hourly-average demand',
            "title":        title_text,
            "legend":       legend_list,
            "line_width":    1,
            'grid_option':   0,
            }
    
    func_lines_plot(inputs)
    
    if SAVE_FIGURES_TO_PDF:
        pdf_pages.savefig(figure2, bbox_inches='tight')
        plt.close()
    
#    # -------------------------
#    
#    #%% Figure 2b Time series of discharging - y axis option #2
#    
#    # -------------------------
#    
##    x_data = np.arange(0, optimization_time_steps)
#    
#    # -------------------------
#    
#    figure2b = plt.figure(figsize=figsize_oneplot)
#    ax2b = figure2b.add_subplot(111)
#    
#    inputs = {
#            "x_data":       x_data, 
#            "y_data":       dispatched_results_matrix/np.average(demand),
#            "ax":           ax2b,
#            "x_label":      'Time (hour in the year)',
#            "y_label":      'Discharged energy\n(hourly-average demand)',
#            "title":        title_text,
#            "legend":       legend_list,
#            "line_width":    1,
#            'grid_option':   0,
#            }
#    
#    func_lines_plot(inputs)
#    
#    if SAVE_FIGURES_TO_PDF:
#        pdf_pages.savefig(figure2b, bbox_inches='tight') 
#        plt.close()
    
    # -------------------------------------------------------------------------
    # Figure 3 Time series of discharging - downscale to daily - y axis option #1
    
    # -------------------------
    
    temporal_scale = 24
    x_data = np.arange(0, optimization_time_steps/temporal_scale)
    
    dispatched_results_matrix1 = np.zeros(
            (int(dispatched_results_matrix.shape[0]/temporal_scale), 
            int(dispatched_results_matrix.shape[1])))
    
    for i in xrange(dispatched_results_matrix.shape[1]):
        dispatched_results_matrix1 [:,i] = \
            func_time_conversion(dispatched_results_matrix[:,i],temporal_scale)
    
    # -------------------------
    
    figure3 = plt.figure(figsize=figsize_oneplot)
    ax3 = figure3.add_subplot(111)
    
    inputs = {
            "x_data":       x_data, 
            "y_data":       dispatched_results_matrix1/1e6,
            "y2_data":       dispatched_results_matrix1/np.average(demand),
            "ax":           ax3,
            "x_label":      'Time (day in the year)',
            "y_label":      '1e6 kWh',
            "y2_label":     'hourly-average demand',
            "title":        title_text,
            "legend":       legend_list,
            "line_width":    1,
            'grid_option':   0,
            }        
            
    func_lines_plot(inputs)
    
    if SAVE_FIGURES_TO_PDF:
        pdf_pages.savefig(figure3, bbox_inches='tight')
        plt.close()
    
#    # ---------------------------
#    # Figure 3b. Time series of discharging - downscale to daily - y axis option #2
#    
#    # -------------------------
#    
##    temporal_scale = 24
##    x_data = np.arange(0, optimization_time_steps/temporal_scale)
##    
##    dispatched_results_matrix1 = np.zeros(
##            (int(dispatched_results_matrix.shape[0]/temporal_scale), 
##            int(dispatched_results_matrix.shape[1])))
##    
##    for i in xrange(dispatched_results_matrix.shape[1]):
##        dispatched_results_matrix1 [:,i] = \
##            func_time_conversion(dispatched_results_matrix[:,i],temporal_scale)
#    
#    # -------------------------
#    
#    figure3b = plt.figure(figsize=figsize_oneplot)
#    ax3b = figure3b.add_subplot(111)
#    
#    inputs = {
#            "x_data":       x_data, 
#            "y_data":       dispatched_results_matrix1/np.average(demand),
#            "ax":           ax3b,
#            "x_label":      'Time (day in the year)',
#            "y_label":      'Discharged energy\n(hourly-average demand)',
#            "title":        title_text,
#            "legend":       legend_list,
#            "line_width":    1,
#            'grid_option':   0,
#            }        
#            
#    func_lines_plot(inputs)
#    
#    if SAVE_FIGURES_TO_PDF:
#        pdf_pages.savefig(figure3b, bbox_inches='tight')  
#        plt.close()
    
    # -----------------------------------------------------------------------------
    
    # Figure 4 Time series of discharging - downscale to weekly - y axis option #1
    
    # -------------------------
    
    temporal_scale = 24 * 7
    x_data = np.arange(0, int(np.floor(optimization_time_steps/temporal_scale)))
    
    dispatched_results_matrix1 = np.zeros(
            (int(np.floor(dispatched_results_matrix.shape[0]/temporal_scale)), 
            int(dispatched_results_matrix.shape[1])))
    
    for i in xrange(dispatched_results_matrix.shape[1]):
        dispatched_results_matrix1 [:,i] = \
            func_time_conversion(dispatched_results_matrix[:,i],temporal_scale)
    
    # -------------------------
    
    figure4 = plt.figure(figsize=figsize_oneplot)
    ax4 = figure4.add_subplot(111)
    
    inputs = {
            "x_data":       x_data, 
            "y_data":       dispatched_results_matrix1/1e6,
            "y2_data":      dispatched_results_matrix1/np.average(demand),
            "ax":           ax4,
            "x_label":      'Time (week in the year)',
            "y_label":      '1e6 kWh',
            "y2_label":      'hourly-average demand',
            "title":        title_text,
            "legend":       legend_list,
            "line_width":    1,
            'grid_option':   0,
            }        
            
    func_lines_plot(inputs)
    
    if SAVE_FIGURES_TO_PDF:
        pdf_pages.savefig(figure4, bbox_inches='tight')
        plt.close()

#    # -----------------------------------------------------------------------------
#    # Figure 4b Time series of discharging - downscale to weekly - y axis option #2
#    
#    # -------------------------
#    
##    temporal_scale = 24 * 7
##    x_data = np.arange(0, optimization_time_steps/temporal_scale)
##    
##    dispatched_results_matrix1 = np.zeros(
##            (int(dispatched_results_matrix.shape[0]/temporal_scale), 
##            int(dispatched_results_matrix.shape[1])))
##    
##    for i in xrange(dispatched_results_matrix.shape[1]):
##        dispatched_results_matrix1 [:,i] = \
##            func_time_conversion(dispatched_results_matrix[:,i],temporal_scale)
#    
#    figure4b = plt.figure(figsize=figsize_oneplot)
#    ax4b = figure4b.add_subplot(111)
#    
#    inputs = {
#            "x_data":       x_data, 
#            "y_data":       dispatched_results_matrix1/np.average(demand),
#            "ax":           ax4b,
#            "x_label":      'Time (week in the year)',
#            "y_label":      'Discharged energy\n(hourly-average demand)',
#            "title":        title_text,
#            "legend":       legend_list,
#            "line_width":    1,
#            'grid_option':   0,
#            }        
#            
#    func_lines_plot(inputs)
#    
#    if SAVE_FIGURES_TO_PDF:
#        pdf_pages.savefig(figure4b, bbox_inches='tight')
#        plt.close()
    
    # -------------------------------------------------------------------------
    # Write the PDF document to the disk
    
    if SAVE_FIGURES_TO_PDF:
        pdf_pages.close()

#%%
#==============================================================================
# func_graphics_system_results_Nscenarios
#
# Purpose
#   Generate 8 figures regarding the "most interested" system-level results for
#       a series of similar optimizations.        
#
# Input
#   A packaging dictionary variable: input_data, which contrains the following data
#       First, inputs for the optimization model   
#       [1] power_tech_index:
#       [2] demand
#       [3] assumptions_matrix
#       Second, results from the optimization model    
#       [4] storage_discharge_matrix
#       [5] storage_capacity_matrix
#       [6] storage_cycle_matrix
#       [7] storage_investment_matrix
#       [8] power_capacity_matrix
#       [9] power_dispatch_matrix
#       [10] cost_power_matrix
#       [11] cost_everything_matrix
#   and the following controls for graphical outputs
#       [12] x_label          
#       [13] SAVE_FIGURES_TO_PDF:   logical variable [0/1]
#       [14] directory_output:      a complete directory, ending with "/"
#       [15] graphics_file_name       
#
#   Data dimentions
#       assumptions_matrix <np.array> different scenarios
#       storage_***_matrix <np.array> "values" for different scenarios        
#       "_matrix" <np.ndarray>
#           ROW dimension: technology options
#           COLUMN dimension: "values" for different scenarios
#
# Output
#   8 figures in the console window.
#   You can choose to save them to a PDF book or not.
#
# History
#   June 17-18, 2018 started and finished the function
#   June 20, 2018 added parallel axes
#   June 22, 2018 added comments
#        
# @Fan Tong
#==============================================================================
        
def func_graphics_system_results_Nscenarios (input_data):

    # -------------------------------------------------------------------------
    # load the input data
        
    # supporting data
    
    power_tech_index = input_data["power_tech_index"]
    demand = input_data["demand"]
    
    # core data
    
    assumptions_matrix = input_data["assumptions_matrix"]
    storage_discharge_matrix = input_data["storage_discharge_matrix"]
    storage_capacity_matrix = input_data["storage_capacity_matrix"]
    storage_cycle_matrix = input_data["storage_cycle_matrix"]
    storage_investment_matrix = input_data["storage_investment_matrix"]
    power_capacity_matrix = input_data["power_capacity_matrix"]
    power_dispatch_matrix = input_data["power_dispatch_matrix"]
    cost_power_matrix = input_data["cost_power_matrix"]
    cost_everything_matrix = input_data["cost_everything_matrix"]
    
    # graphics-related
    
    x_label = input_data["x_label"]
    directory_output = input_data["directory_output"]
    graphics_file_name = input_data["graphics_file_name"]
    SAVE_FIGURES_TO_PDF = input_data["SAVE_FIGURES_TO_PDF"]
    
    # -------------------------------------------------------------------------
    
    # Create the output folder
    
    if SAVE_FIGURES_TO_PDF:
        
        if not os.path.exists(directory_output):
            os.makedirs(directory_output)
        
        pdf_pages = PdfPages(
                directory_output + graphics_file_name + '.pdf')
    
    # -------------------------------------------------------------------------
    
    # Define the plotting style
    
    plt.style.use('default')
    # plt.style.use('bmh')
    # plt.style.use('fivethirtyeight')
    # plt.style.use('seaborn-white')
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] =  'Helvetica ' #'Palatino' # 'Ubuntu'
    plt.rcParams['font.monospace'] = 'Helvetica Mono' #'Palatino Mono' # 'Ubuntu'
    plt.rcParams['font.size'] = 16
    plt.rcParams['axes.labelsize'] = 16
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['xtick.labelsize'] = 16
    plt.rcParams['ytick.labelsize'] = 16
    plt.rcParams['legend.fontsize'] = 14
    plt.rcParams['figure.titlesize'] = 16
    plt.rcParams['lines.linewidth'] = 2.0
    plt.rcParams['grid.color'] = 'k'
    plt.rcParams['grid.linestyle'] = ':'
    plt.rcParams['grid.linewidth'] = 0.5
    plt.rcParams['xtick.major.width'] = 2
    plt.rcParams['xtick.major.size'] = 6
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.major.width'] = 2
    plt.rcParams['ytick.major.size'] = 6
    plt.rcParams['ytick.direction'] = 'in'
      
    # -------------------------------------------------------------------------
    
    figsize_oneplot = (8,6)
    
    # -------------------------------------------------------------------------
    
    # Figure 1 Storage discharge energy
    
    figure1 = plt.figure(figsize=figsize_oneplot)
    ax1 = figure1.add_subplot(111)
    
    inputs_dispatch_1 = {
        "x_data":           assumptions_matrix, 
        "y1_data":          storage_discharge_matrix / 1e9,
        "y2_data":          storage_discharge_matrix / np.average(demand),
        "ax":               ax1,
        "x_label":          x_label,
        "y1_label":         'Storage discharge (1e9 kWh)',
        "y2_label":         'Storage discharge\n(hourly average demand)',
        "line_width":       2,
        "grid_option":      0,
        }
    
    [ax1, ax1b] = func_lines_2yaxes_plot(inputs_dispatch_1)
    
    ax1.set_xscale("log", nonposx='clip')
    ax1.set_yscale("log", nonposx='clip')
    ax1b.set_yscale("log", nonposx='clip')
    
    if SAVE_FIGURES_TO_PDF:
        pdf_pages.savefig(figure1, bbox_inches='tight')
        plt.close()
    
    # -------------------------------------------------------------------------
    
    # Figure 2 Storage capacity
    
    figure2 = plt.figure(figsize=figsize_oneplot)
    ax2 = figure2.add_subplot(111)
    
    inputs_dispatch_2 = {
        "x_data":           assumptions_matrix, 
        "y1_data":          storage_capacity_matrix / 1e9,
        "y2_data":          storage_capacity_matrix / np.average(demand),
        "ax":               ax2,
        "x_label":          x_label,
        "y1_label":         'Storage capacity (1e9 kWh)',
        "y2_label":         'Storage capacity\n(hourly average demand)',
        "line_width":       2,
        'grid_option':      0,
        }
    
    [ax2, ax2b] = func_lines_2yaxes_plot(inputs_dispatch_2)
    
    ax2.set_xscale("log", nonposx='clip')
    ax2.set_yscale("log", nonposx='clip')
    ax2b.set_yscale("log", nonposx='clip')
    
    if SAVE_FIGURES_TO_PDF:
        pdf_pages.savefig(figure2, bbox_inches='tight')
        plt.close()
    
    # -------------------------------------------------------------------------
    
    # Figure 3 Full-discharge cycles
    
    figure3 = plt.figure(figsize=figsize_oneplot)
    ax3 = figure3.add_subplot(111)
    
    inputs_dispatch_3 = {
        "x_data":           assumptions_matrix, 
        "y_data":           storage_cycle_matrix,
        "ax":               ax3,
        "x_label":          x_label,
        "y_label":          'Calculated full-discharge cycles',
        "line_width":       2,
        'grid_option':      0,
        }        
    
    ax3.set_xscale("log", nonposx='clip')
    ax3.set_yscale("log", nonposx='clip')
    
    func_lines_plot(inputs_dispatch_3)
    
    if SAVE_FIGURES_TO_PDF:
        pdf_pages.savefig(figure3, bbox_inches='tight')
        plt.close()
    
    # -------------------------------------------------------------------------
    
    # Figure 4 Storage investment
    
    figure4 = plt.figure(figsize=figsize_oneplot)
    ax4 = figure4.add_subplot(111)
    
    inputs_dispatch_4 = {
        "x_data":           assumptions_matrix, 
        "y_data":           storage_investment_matrix / 1e9,
        "ax":               ax4,
        "x_label":          x_label,
        "y_label":          'Energy storage investment (billion $)',
        "line_width":       2,
        'grid_option':      0,
        }        
    
    ax4.set_xscale("log", nonposx='clip')
    # ax4.set_yscale("log", nonposx='clip')
    
    func_lines_plot(inputs_dispatch_4)
    
    if SAVE_FIGURES_TO_PDF:
        pdf_pages.savefig(figure4, bbox_inches='tight')
        plt.close()
    
    # -------------------------------------------------------------------------
    
    # Figure 5 Power generation capacity
    
    legend_list = sorted(power_tech_index.keys(), key=lambda x: x[1])
    
    figure5 = plt.figure(figsize=figsize_oneplot)
    ax5 = figure5.add_subplot(111)
    
    inputs_dispatch_5 = {
            "x_data":       assumptions_matrix, 
            "y_data":       power_capacity_matrix.T/1e6,
            "ax":           ax5,
            "x_label":      'Time (hour in the year)',
            "y_label":      'Power generation capacity (GW)',
            "legend":       legend_list,
            "line_width":    2,
            'grid_option':   0,
            }        
            
    ax5.set_xscale("log", nonposx='clip')
    
    func_stack_plot(inputs_dispatch_5)
    
    if SAVE_FIGURES_TO_PDF:
        pdf_pages.savefig(figure5, bbox_inches='tight')
        plt.close()
    
    # -------------------------------------------------------------------------
    
    # Figure 6 Power generation dispatch mix
    
    legend_list = sorted(power_tech_index.keys(), key=lambda x: x[1])
    
    figure6 = plt.figure(figsize=figsize_oneplot)
    ax6 = figure6.add_subplot(111)
    
    inputs_dispatch_6 = {
            "x_data":        assumptions_matrix, 
            "y_data":        power_dispatch_matrix.T / np.sum(demand),
            "ax":            ax6,
            "x_label":       'Time (hour in the year)',
            "y_label":       'Power generation (share of demand)',
            "legend":        legend_list,
            "line_width":    2,
            'grid_option':   0,
            }        
            
    ax6.set_xscale("log", nonposx='clip')
    
    func_stack_plot(inputs_dispatch_6)
    
    if SAVE_FIGURES_TO_PDF:
        pdf_pages.savefig(figure6, bbox_inches='tight')
        plt.close()
    
    # -------------------------------------------------------------------------
    
    # Figure 7 Cost share - power generation
    
    legend_list = sorted(power_tech_index.keys(), key=lambda x: x[1])
    
    figure7 = plt.figure(figsize=figsize_oneplot)
    ax7 = figure7.add_subplot(111)
    
    inputs_dispatch_7 = {
            "x_data":        assumptions_matrix, 
            "y_data":        cost_power_matrix.T,
            "ax":            ax7,
            "x_label":       'Time (hour in the year)',
            "y_label":       'Cost contributions ($/kWh)',
            "legend":        legend_list,
            "line_width":    2,
            'grid_option':   0,
            }        
            
    ax7.set_xscale("log", nonposx='clip')
    # ax7.set_yscale("log", nonposx='clip')
    
    ax7.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
    
    func_stack_plot(inputs_dispatch_7)
    
    if SAVE_FIGURES_TO_PDF:
        pdf_pages.savefig(figure7, bbox_inches='tight')
        plt.close()
    
    # -------------------------------------------------------------------------
    
    # Figure 8 Cost share - "every type"
    
    legend_list = sorted(power_tech_index.keys(), key=lambda x: x[1])
    legend_list.append('storage')
    legend_list.append('unmet demand')
    legend_list.append('curtailment')
    
    figure8 = plt.figure(figsize=figsize_oneplot)
    ax8 = figure8.add_subplot(111)
    
    inputs_dispatch_8 = {
            "x_data":        assumptions_matrix, 
            "y_data":        cost_everything_matrix.T,
            "ax":            ax8,
            "x_label":       'Time (hour in the year)',
            "y_label":       'Cost contributions ($/kWh)',
            "legend":        legend_list,
            "line_width":    2,
            'grid_option':   0,
            }        
            
    ax8.set_xscale("log", nonposx='clip')
    # ax8.set_yscale("log", nonposx='clip')
    
    func_stack_plot(inputs_dispatch_8)
    
    if SAVE_FIGURES_TO_PDF:
        pdf_pages.savefig(figure8, bbox_inches='tight')
        plt.close()
    
    # -------------------------------------------------------------------------
    
    # Close the open file streams
    
    if SAVE_FIGURES_TO_PDF:
        pdf_pages.close()


#%%
# -----------------------------------------------------------------------------
# func_graphics_dispatch_mix_technology_timeseries_1scenario()
#
# Function: 
#   For a technology, find the week in which the share of demand met by this
#       technology is at maximum or minimum. Then produce 2*2 figures for each
#       such week.
# 
# Input
#   A DICT variable named input_data, with the following keys:
#    demand  -- for editing axes
#   [choice about study scopes]        
#    window_size
#    technology_data   -- the share of demand met by this technology
#    technology_of_interest -- the textual name of this technology
#   [system-level data]
#    dispatched_results_matrix <np.ndarray>
#    demand_results_matrix <np.ndarray>
#    legend_list_dispatch
#    legend_list_demand
#   [options for controling graphical output]      
#    directory_output
#    SAVE_FIGURES_TO_PDF
#    graphics_file_name_prefix
#    graphics_file_name_root
#   [output file]
#    text_file <file> -- an open file stream for outputs
# 
#   dimensions: dispatched_results_matrix, demand_results_matrix
#       row: time_steps
#       column: technology  options or demand types
#        
# Output    
#   2*2 time series figures (line plot, stack plot) * (dispatch mix, demand mix)
#   If you choose to save the files, five files will be saved.
#
# Functions called
#   func_graphics_dispatch_mix_time_selection_1scenario()
#
# History
#   June 22-23, 2018 drafted the function
#
# @ Fan Tong
# -----------------------------------------------------------------------------

def func_graphics_dispatch_mix_technology_timeseries_1scenario(input_data):

    # -------------------------------------------------------------------------
    
    # load the data
    
    demand = input_data['demand']
    
    window_size = input_data['window_size']    
    technology_data = input_data['technology_data']
    technology_of_interest = input_data['technology_of_interest']
    
    dispatched_results_matrix = input_data['dispatched_results_matrix']
    legend_list_dispatch = input_data['legend_list_dispatch']
    demand_results_matrix = input_data['demand_results_matrix']
    legend_list_demand = input_data['legend_list_demand']    
    
    directory_output = input_data['directory_output']
    SAVE_FIGURES_TO_PDF = input_data['SAVE_FIGURES_TO_PDF']
    graphics_file_name_prefix = input_data['graphics_file_name_prefix']
    graphics_file_name_root = input_data['graphics_file_name_root']
    
    text_file = input_data['text_file']

    # -------------------------------------------------------------------------
    # Define the plotting style
    
    plt.style.use('default')
    # plt.style.use('bmh')
    # plt.style.use('fivethirtyeight')
    # plt.style.use('seaborn-white')
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] =  'Helvetica ' #'Palatino' # 'Ubuntu'
    plt.rcParams['font.monospace'] = 'Helvetica Mono' #'Palatino Mono' # 'Ubuntu'
    plt.rcParams['font.size'] = 16
    plt.rcParams['axes.labelsize'] = 16
    plt.rcParams['axes.labelweight'] = 'bold'
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['xtick.labelsize'] = 16
    plt.rcParams['ytick.labelsize'] = 16
    plt.rcParams['legend.fontsize'] = 14
    plt.rcParams['figure.titlesize'] = 16
    plt.rcParams['lines.linewidth'] = 2.0
    plt.rcParams['grid.color'] = 'k'
    plt.rcParams['grid.linestyle'] = ':'
    plt.rcParams['grid.linewidth'] = 0.5
    plt.rcParams['xtick.major.width'] = 2
    plt.rcParams['xtick.major.size'] = 6
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.major.width'] = 2
    plt.rcParams['ytick.major.size'] = 6
    plt.rcParams['ytick.direction'] = 'in'
    
    # -------------------------------------------------------------------------
    
    text_file.write(technology_of_interest)
    text_file.write("\n")
    
    # -------------------------------------------------------------------------
    
    # Time period #1 and #2: maximum and minmum                
    
    study_variable_dict = {
            'window_size':      window_size,
            'data':             technology_data, 
            'print_option':     0,
            }
    
    study_variable_dict['search_option'] = 'max'
    study_output_1 = func_find_period(study_variable_dict)    
    time_range_1 = (study_output_1['left_index'], study_output_1['right_index'])
        
    title_info_1 = (
            technology_of_interest + " met {:.0f} hrs of avg. demand during hours: {}"
            .format(study_output_1['value'], time_range_1)
            )

    text_file.write(
            "{}, {}, {:.1f}\n".format(
                    study_output_1['left_index'], 
                    study_output_1['right_index'],
                    study_output_1['value'])
            )

    # ------------------------------------
    
    study_variable_dict['search_option'] = 'min'
    study_output_2 = func_find_period(study_variable_dict)
    time_range_2 = (study_output_2['left_index'], study_output_2['right_index'])

    title_info_2 = (
            technology_of_interest + " met {:.0f} hrs of avg. demand during hours: {}"
            .format(study_output_2['value'], time_range_2)
            )
    
    text_file.write(
            "{}, {}, {:.1f}\n".format(
                    study_output_2['left_index'], 
                    study_output_2['right_index'],
                    study_output_2['value'])
            )
    
    # -------------------------------------------------------------------------
    
    # Generate graphics - time period #1
    
    # ----------------------------------
    # Create the ouput folder    

    graphics_file_name_1 = \
        graphics_file_name_prefix + 'dispatch_and_demand_mix' + \
        graphics_file_name_root + "{}_{}_".format(time_range_1[0], time_range_1[1]) + \
        technology_of_interest
    
    if SAVE_FIGURES_TO_PDF:
        if not os.path.exists(directory_output):
            os.makedirs(directory_output)
                        
        pdf_pages_1 = PdfPages(
            directory_output + graphics_file_name_1 + '.pdf')    
    
    # ----------------------------------
    
    # Call the functions to do the work
    
    input_data_1a = {
            "time_range":                   time_range_1,
            "demand_line_for_dispatch_figure":  1,
            "demand":                       demand,
            "mix_matrix":                   dispatched_results_matrix,
            "pdf_pages":                    pdf_pages_1,
            "SAVE_FIGURES_TO_PDF":          SAVE_FIGURES_TO_PDF,
            "title_text":                   "dispatch mix\n" + title_info_1,
            "legend_list":                  legend_list_dispatch,        
            }
    
    func_graphics_dispatch_mix_time_selection_1scenario(input_data_1a)    
    
    input_data_1b = {
            "time_range":                   time_range_1,
            "demand":                       demand,            
            "mix_matrix":                   demand_results_matrix,
            "pdf_pages":                    pdf_pages_1,
            "SAVE_FIGURES_TO_PDF":          SAVE_FIGURES_TO_PDF,
            "title_text":                   "demand mix\n" + title_info_1,
            "legend_list":                  legend_list_demand,        
            }
    
    func_graphics_dispatch_mix_time_selection_1scenario(input_data_1b)    
    
    if SAVE_FIGURES_TO_PDF:
        pdf_pages_1.close()
    
    # -------------------------------------------------------------------------
    
    # Generate graphics - time period #2
       
    # ----------------------------------
    # Create the ouput folder 
    
    graphics_file_name_2 = \
        graphics_file_name_prefix + 'dispatch_and_demand_mix' + \
        graphics_file_name_root + "{}_{}_".format(time_range_2[0], time_range_2[1]) + \
        technology_of_interest
    
    if SAVE_FIGURES_TO_PDF:
        if not os.path.exists(directory_output):
            os.makedirs(directory_output)
                        
        pdf_pages_2 = PdfPages(
            directory_output + graphics_file_name_2 + '.pdf')
    
    # ----------------------------------
    
    # Call the functions to do the work    
    
    input_data_2a = {
            "time_range":                   time_range_2,
            "demand":                       demand,
            "demand_line_for_dispatch_figure":      1,
            "mix_matrix":                   dispatched_results_matrix,
            "pdf_pages":                    pdf_pages_2,
            "SAVE_FIGURES_TO_PDF":          SAVE_FIGURES_TO_PDF,
            "title_text":                   "dispatch mix\n" + title_info_2,
            "legend_list":                  legend_list_dispatch,        
            }
    
    func_graphics_dispatch_mix_time_selection_1scenario(input_data_2a)    
    
    input_data_2b = {
            "demand":                       demand,
            "time_range":                   time_range_2,        
            "mix_matrix":                   demand_results_matrix,
            "pdf_pages":                    pdf_pages_2,
            "SAVE_FIGURES_TO_PDF":          SAVE_FIGURES_TO_PDF,
            "title_text":                   "demand mix\n" + title_info_2,
            "legend_list":                  legend_list_demand, 
            }
    
    func_graphics_dispatch_mix_time_selection_1scenario(input_data_2b)

    # -------------------------------------------------------------------------
    
    # Close the file
          
    if SAVE_FIGURES_TO_PDF:
        pdf_pages_2.close()
        
        
#%%
# -----------------------------------------------------------------------------
# func_optimization_results_time_series_1scenario()
#
# Function: 
#   Given the locations (directories or file paths), load the data, perform the
#   the analysis, generate the figures, and save the figures to files.     
# 
# Input
#   A DICT variable named input_data, with the following keys:
#    optimization_results_file_path
#    directory_output
#    graphics_file_name_prefix
#    graphics_file_name_root
#    SAVE_FIGURES_TO_PDF
#
# Output
#   Three groups of figures. If you choose to save the files, five files will be saved.
#       1 dispatch mix and demand mix for all hourly data
#       2 dispatch mix and demand mix for selected ranges of data
#           for technology A (energy storage)
#       3 dispatch mix and demand mix for selected ranges of data
#           for technology B (wind and solar)
#
#   A text file summarizing key information from these technology-focused analyses        
#
# Functions called
#   func_graphics_dispatch_mix_1scenario()
#   func_graphics_dispatch_mix_technology_timeseries_1scenario()
#
# History
#   June 3, 2018 wrote the code
#   June 19, 2018 packaged the code into this function
#   June 20, 2018 modified the part load optimization data
#   June 22-23, 2018 modified the part dealing with selected time periods
#       called the function, func_graphics_dispatch_mix_technology_timeseries_1scenario()
#        
# -----------------------------------------------------------------------------

def func_optimization_results_time_series_1scenario(input_data):
    
    # -------------------------------------------------------------------------

    # load the input assumptions

    optimization_results_file_path = input_data["optimization_results_file_path"]
    directory_output = input_data["directory_output"]
    graphics_file_name_prefix = input_data["graphics_file_name_prefix"]
    graphics_file_name_root = input_data["graphics_file_name_root"]
    SAVE_FIGURES_TO_PDF = input_data["SAVE_FIGURES_TO_PDF"]

    # -------------------------------------------------------------------------

    # load the data    
   
    temp_dict = func_load_optimization_results(optimization_results_file_path)
    model_inputs = temp_dict['model_inputs']
    model_results = temp_dict['model_results']
    
    # -------------------------
    
    power_tech_index = model_inputs['power_tech_index']
    demand = model_inputs['demand']
    dispatched_power = model_results['dispatched_power']
    dispatched_storage_discharge = model_results['dispatched_storage_discharge']
    
    dispatched_storage_charge = model_results['dispatched_storage_charge']
    unmet_demand = model_results['unmet_demand']
    dispatched_curtailment = model_results['dispatched_curtailment']
    
    dispatched_curtailment = np.array(dispatched_curtailment)
    
    # -------------------------------------------------------------------------
    
    # Quick test to see if system balance is reached at every hour
    
    # Note the system energy equation looks as follows
    #   cvx.sum_entries(dispatched_power, axis=0).T + dispatched_storage_discharge + unmet_demand 
    #   == demand + dispatched_storage_charge
    
    system_balance = \
        np.sum(dispatched_power, axis = 0) + dispatched_storage_discharge.flatten() + \
        unmet_demand.flatten() - demand - dispatched_storage_charge.flatten()
    
    if np.abs(np.sum(system_balance)) > 1:        
         sys.exit("Value error! system energy balance broken!")
    
    # -------------------------------------------------------------------------
    
    # Prepare the data to be used later
    
    # dispatched_results_matrix
    #   row: time_steps
    #   column: technology options
    dispatched_results_matrix = np.column_stack(
            (dispatched_power.T, 
             dispatched_storage_discharge,
             unmet_demand,
             ))
    
    # demand_results_matrix
    #   row: time_steps
    #   column: demand, storage charge, curtailment 
    demand_results_matrix = np.column_stack(
            (demand, 
             dispatched_storage_charge,
             dispatched_curtailment.T)
            )
    
    legend_list_dispatch = sorted(power_tech_index.keys(), key=lambda x: x[1])
    legend_list_dispatch.append('storage')
    legend_list_dispatch.append('unmet demand')
    
    legend_list_demand = ['demand', 'storage charge', 'curtailed generation']
    
    # -------------------------------------------------------------------------
    
    # Output the "characteristic" time periods and their metrics
    
    # Representative file name
    #   storage_scenario_dispatch_and_demand_mix_1e-2_with_NG_.txt
    
    text_file_path = (
            directory_output + 
            graphics_file_name_prefix + 'dispatch_and_demand_mix' + \
            graphics_file_name_root + '.txt'
            )
    
    text_file = open(text_file_path, 'w') 
    
    # -------------------------------------------------------------------------
    
    # Figure group #1 dispatch mix and demand mix for the whole data
    #   using func_graphics_dispatch_mix_1scenario()
    
    # Right now, 12 figures will be generated.
    # 2+2 (supply+demand) figures for each time resolution
    # In total, three time resolutions (hourly, daily, weekly)
        
    graphics_file_name_1 = \
        graphics_file_name_prefix + 'dispatch_and_demand_mix' + \
        graphics_file_name_root + "{}_{}".format(0, 'end')
    
    input_data_1 = {
            "demand":                       demand,
            "dispatched_results_matrix":    dispatched_results_matrix,
            "demand_results_matrix":        demand_results_matrix,
            "directory_output":             directory_output,
            "graphics_file_name":           graphics_file_name_1,
            "SAVE_FIGURES_TO_PDF":          SAVE_FIGURES_TO_PDF,        
            "legend_list_dispatch":         legend_list_dispatch,
            "legend_list_demand":           legend_list_demand,            
            }
    
    func_graphics_dispatch_mix_1scenario(input_data_1)
    
    # -------------------------------------------------------------------------    

    # Figure group #2 dispatch mix and demand mix for selected time period
    #   technology of interest: energy storage
    #   using func_graphics_dispatch_mix_1scenario()

    technology_data = (dispatched_storage_discharge.flatten() / demand.T)
    technology_of_interest = "storage"

    input_data_2 = {
            "window_size":                  24*7,
            "demand":                       demand,
            "technology_data":              technology_data,
            "technology_of_interest":       technology_of_interest,
            
            "dispatched_results_matrix":    dispatched_results_matrix,
            "demand_results_matrix":        demand_results_matrix,
            "legend_list_dispatch":         legend_list_dispatch,
            "legend_list_demand":           legend_list_demand,
            
            "graphics_file_name_prefix":    graphics_file_name_prefix,
            "graphics_file_name_root":      graphics_file_name_root,
            "directory_output":             directory_output,
            "SAVE_FIGURES_TO_PDF":          SAVE_FIGURES_TO_PDF,
            "text_file":                    text_file,
            }

    func_graphics_dispatch_mix_technology_timeseries_1scenario(input_data_2)
    
    # -------------------------------------------------------------------------
    
    # Figure group #3 dispatch mix and demand mix for selected time period
    #   technology of interest: wind and solar
    #   using func_graphics_dispatch_mix_1scenario()
    
    technology_data = ((
            dispatched_results_matrix[:, power_tech_index['wind']] + 
            dispatched_results_matrix[:, power_tech_index['solar']]) / demand.T)
            
    technology_of_interest = "wind and solar"    

    input_data_3 = {
            "window_size":                  24*7,
            "demand":                       demand,
            "technology_data":              technology_data,
            "technology_of_interest":       technology_of_interest,
            
            "dispatched_results_matrix":    dispatched_results_matrix,
            "demand_results_matrix":        demand_results_matrix,
            "legend_list_dispatch":         legend_list_dispatch,
            "legend_list_demand":           legend_list_demand,
            
            "graphics_file_name_prefix":    graphics_file_name_prefix,
            "graphics_file_name_root":      graphics_file_name_root,
            "directory_output":             directory_output,
            "SAVE_FIGURES_TO_PDF":          SAVE_FIGURES_TO_PDF,
            "text_file":                    text_file,
            }

    func_graphics_dispatch_mix_technology_timeseries_1scenario(input_data_3)

    # -------------------------------------------------------------------------
    
    # deal with open file streams
    
    text_file.close()

#%%
# -----------------------------------------------------------------------------
# func_optimization_results_system_results_Nscenarios()
#
# Function: generate "representative" results (figures) for a set of optimization 
#   runs whose only difference was due to a change in an assumption.
#
# Input
#   A DICT variable named input_data, that has the following keys
#       optimization_results_file_path_list
#       scenario_list_number
#       SAVE_FIGURES_TO_PDF
#       graphics_file_name
#       directory_output
#       x_label
#   In a nutsheel, these input information tells where to locate the optimization
#       results, what is the distinction across different runs, where to save
#       the generated figures, and how to decorate the figures.
#
# Output
#   A PDF book containing 8 figures.
#   Read the description of func_graphics_system_results_Nscenarios() for details
#
# Functions called
#   func_graphics_system_results_Nscenarios()
#
# History
#   Jun 17, 2018 wrote the code
#   Jun 20, 2018 re-packaged into a function
#       updated the code for loading the data from files    
#
# @ Fan Tong    
# -----------------------------------------------------------------------------

def func_optimization_results_system_results_Nscenarios(input_data):

    # load the input data
    
    optimization_results_file_path_list = input_data['optimization_results_file_path_list']
    scenario_list_number = input_data['scenario_list_number']
    SAVE_FIGURES_TO_PDF = input_data['SAVE_FIGURES_TO_PDF']
    graphics_file_name = input_data['graphics_file_name']
    directory_output = input_data['directory_output']
    x_label = input_data['x_label']

    # -------------------------------------------------------------------------

    # load the data from scenario to get "power_tech_index"
    
    temp_dict = func_load_optimization_results(optimization_results_file_path_list[0])
    model_inputs = temp_dict['model_inputs']
    model_results = temp_dict['model_results']
    
    power_tech_index = model_inputs['power_tech_index']
    
    # -------------------------------------------------------------------------
    
    # prepare for the loop
    
    # 9 variables (matrix form) to be assembled
    
    storage_capacity_matrix = np.zeros([len(scenario_list_number)])
    storage_discharge_matrix = np.zeros([len(scenario_list_number)])
    storage_cycle_matrix = np.zeros([len(scenario_list_number)])
    storage_investment_matrix = np.zeros([len(scenario_list_number)])
    
    power_capacity_matrix = np.zeros([len(power_tech_index), len(scenario_list_number)])
    power_dispatch_matrix = np.zeros([len(power_tech_index), len(scenario_list_number)])
    cost_power_matrix = np.zeros([len(power_tech_index), len(scenario_list_number)])
    cost_everything_matrix = np.zeros([len(power_tech_index)+3, len(scenario_list_number)])
    
    optimum_cost_matrix = np.zeros([len(scenario_list_number)])
    
    # ----------------------
    
    # loop to extract and "combine" optimization results
    
    for scenario_idx in xrange(len(scenario_list_number)):
    
        # actually load the data
    
        # f = open(optimization_results_file_path_list[scenario_idx], 'rb')
        
        temp_dict = func_load_optimization_results(optimization_results_file_path_list[scenario_idx])
        model_inputs = temp_dict['model_inputs']
        model_results = temp_dict['model_results']
            
        # ---------------------------------------------------------------------
        
        # Energy storage
    
        storage_discharge_matrix[scenario_idx] = (
            sum(model_results["dispatched_storage_discharge"])
            )
        
        storage_capacity_matrix[scenario_idx] = (
            model_results["capacity_storage"]
            )
    
        storage_cycle_matrix[scenario_idx] = (
            sum(model_results["dispatched_storage_discharge"]) /
            model_results["capacity_storage"]
            )
        
        storage_investment_matrix[scenario_idx] = (
            model_results["capacity_storage"] * model_inputs['capital_cost_storage']
            )
    
        # ---------------------------------------------------------------------
    
        # Power generation
    
        power_capacity_matrix[:,scenario_idx] = \
            np.reshape(model_results['capacity_power'], -1)
    
        power_dispatch_matrix[:,scenario_idx] = \
            np.reshape(np.sum(model_results['dispatched_power'], axis=1), -1)
    
        power_dispatch_total = \
            np.sum(model_results['dispatched_power'], axis = 1)
    
        cost_power_matrix[:,scenario_idx] = (
            ((power_dispatch_total * model_inputs['variable_cost_power'] +
             model_results['capacity_power'] * model_inputs['fixed_cost_power'])
            / np.sum(model_inputs['demand'])))
    
        # ---------------------------------------------------------------------
    
        # Cost breakdown by "everything" (every type)
        # -- power generation technologies, storage, unmet demand, curtailment
    
        storage_discharge_total = np.sum(model_results['dispatched_storage_discharge'])
        storage_charge_total = np.sum(model_results['dispatched_storage_charge']) 
        
        cost_everything_matrix[0:len(power_tech_index),scenario_idx] = (
            cost_power_matrix[:,scenario_idx])
    
        cost_everything_matrix[len(power_tech_index)+0,scenario_idx] = (
            (storage_discharge_total * model_inputs['variable_cost_storage'] +
             storage_charge_total * model_inputs['variable_cost_storage'] +
             model_results["capacity_storage"] * model_inputs['fixed_cost_storage'])
             / np.sum(model_inputs['demand']))
    
        cost_everything_matrix[len(power_tech_index)+1,scenario_idx] = (
            np.sum(model_results['unmet_demand']) * model_inputs['unmet_demand_cost']
            / np.sum(model_inputs['demand']))
            
        cost_everything_matrix[len(power_tech_index)+2,scenario_idx] = (
            np.sum(model_results['dispatched_curtailment']) * model_inputs['curtailment_cost']
            / np.sum(model_inputs['demand']))
        
        # ---------------------------------------------------------------------
        
        # Optimal system cost
        
        optimum_cost_matrix[scenario_idx] = (
            model_results['optimum'] / np.sum(model_inputs['demand']))
    
    # -------------------------------------------------------------------------
    # Graphics
    
    # Graphics settings
    
    input_data = {
            "power_tech_index":             power_tech_index,
            "demand":                       model_inputs['demand'],
            "assumptions_matrix":           np.array(scenario_list_number),
            "storage_discharge_matrix":     storage_discharge_matrix,
            "storage_capacity_matrix":      storage_capacity_matrix,
            "storage_cycle_matrix":         storage_cycle_matrix,
            "storage_investment_matrix":    storage_investment_matrix,
            "power_capacity_matrix":        power_capacity_matrix,
            "power_dispatch_matrix":        power_dispatch_matrix,
            "cost_power_matrix":            cost_power_matrix,
            "cost_everything_matrix":       cost_everything_matrix,
            "directory_output":             directory_output,
            "graphics_file_name":           graphics_file_name,
            "SAVE_FIGURES_TO_PDF":          SAVE_FIGURES_TO_PDF,
            "x_label":                      x_label,
            }    

    # call the function to generate figures
    
    func_graphics_system_results_Nscenarios(input_data)

#%%
# -----------------------------------------------------------------------------
# func_optimization_results_dispatch_var_Nscenarios()
#
# Function: generate figures comparing dispatch variables for a technology
#   across a set of optimization runs whose only difference was due to a change
#   in an assumption.
#
# Input
#   A DICT variable named input_data, that has the following keys
#       optimization_results_file_path_list
#       scenario_list_number
#       which_technology_to_compare
#       SAVE_FIGURES_TO_PDF
#       graphics_file_name    
#       directory_output
#       title_text
#       legend_list
#   In a nutsheel, these input information tells where to locate the optimization
#       results, what is the distinction across different runs, where to save
#       the generated figures, and how to decorate the figures.
#
# Output
#   A PDF book containing 8 figures.
#   Read the description of func_graphics_dispatch_var_Nscenarios() for details
#
# Functions called
#   func_graphics_dispatch_var_Nscenarios()
#
# History
#   Jun 4, 9, 14, 2018 wrote the code
#   Jun 20, 2018 re-packaged into a function
#       updated the code for loading the data from files  
#    
# @ Fan Tong    
# -----------------------------------------------------------------------------

def func_optimization_results_dispatch_var_Nscenarios(input_data):

    # load the input data
    
    optimization_results_file_path_list = input_data['optimization_results_file_path_list']
    scenario_list_number = input_data['scenario_list_number']
    
    which_technology_to_compare = input_data['which_technology_to_compare']
    
    SAVE_FIGURES_TO_PDF = input_data['SAVE_FIGURES_TO_PDF']
    graphics_file_name = input_data['graphics_file_name']
    directory_output = input_data['directory_output']
    title_text = input_data['title_text']
    legend_list = input_data['legend_list']

    # -------------------------------------------------------------------------

    # load the data from scenario to get "power_tech_index"
    
    temp_dict = func_load_optimization_results(optimization_results_file_path_list[0])
    model_inputs = temp_dict['model_inputs']
    model_results = temp_dict['model_results']
    
    power_tech_index = model_inputs['power_tech_index']
    optimization_time_steps = len(model_inputs['demand'])
    
    # -------------------------------------------------------------------------
    
    dispatched_results_matrix = \
        np.zeros([optimization_time_steps, len(scenario_list_number)])
    
    for scenario_idx in xrange(len(scenario_list_number)):

        # actually load the data
            
        temp_dict = func_load_optimization_results(optimization_results_file_path_list[scenario_idx])
        model_inputs = temp_dict['model_inputs']
        model_results = temp_dict['model_results']
        
        if which_technology_to_compare == "storage":
            dispatched_results = model_results["dispatched_storage_discharge"]
            dispatched_results_matrix[:, scenario_idx] = \
                np.reshape(dispatched_results, -1)
        else:
            dispatched_results = model_results["dispatched_power"]
            dispatched_results_matrix[:, scenario_idx] = \
                np.reshape(dispatched_results[power_tech_index[which_technology_to_compare], :], -1)
    
    # -------------------------------------------------------------------------
    
    # Graphics
    
    input_data = {
            "demand":                       model_inputs['demand'],
            "dispatched_results_matrix":    dispatched_results_matrix,
            "directory_output":             directory_output,
            "graphics_file_name":           graphics_file_name,
            "SAVE_FIGURES_TO_PDF":          SAVE_FIGURES_TO_PDF,
            "title_text":                   title_text,
            "legend_list":                  legend_list,
            }
    
    # call the function
    
    func_graphics_dispatch_var_Nscenarios(input_data)    