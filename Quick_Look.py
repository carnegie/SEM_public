# -*- coding: utf-8 -*-
'''
Quick_Look.py

Function: this file collects defined functions for plotting optimization results
    from one optimization run or mutilple runs

Functions defined
    plot_results_dispatch_1scenario()
    plot_results_dispatch_1scenario()
    func_graphics_dispatch_mix_technology_timeseries_1scenario()
    func_graphics_dispatch_var_Nscenarios()
    func_graphics_system_results_Nscenarios()
    call_plot_results_1scenario() -- directly callable
    func_optimization_results_system_results_Nscenarios() -- directly callable
    func_optimization_results_dispatch_var_Nscenarios() -- directly callable

History
    Jun 4-5, 2018 completely rewritten
        plot_results_dispatch_1scenario()
        func_graphics_dispatch_mix_time_selection()
        func_graphics_dispatch_var_Nscenarios()
                        
    Jun 17-18, 2018 added a new function, and updated the comments
        func_graphics_system_results_Nscenarios()

    Jun 19, 2018
        fixed some errors in plot_results_dispatch_1scenario()
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
            plot_results_dispatch_1scenario()
            plot_results_dispatch_1scenario()
            func_graphics_dispatch_results_1scenario()
            func_graphics_dispatch_var_Nscenarios()
            func_optimization_results_system_results_Nscenarios()
        changed packaging functions' names
            func_graphics_dispatch_results_1scenario -> call_plot_results_1scenario
            func_optimization_results_snapshot_Nscenarios -> func_optimization_results_system_results_Nscenarios
        changed the function plot_results_dispatch_1scenario()
            from fixed ranges in time to dynamically select the weeks with the largest/smallest share of a technology
    Jun 22-23, 2018
        updated the following two functions
            func_optimization_results_system_results_Nscenarios()
            plot_results_dispatch_1scenario()
        .. so that the selected time ranges are determined for the 'extreme' weeks
        .. for a technology of interest
    Jun 23, 2018 checked the code and comments
    June 23-24, 2018 updated texts and labels on figures
    Jul 8, 2018 [kc]
        Started making changes so this code runs off of dictionaries rather
        than pickle files. Name changed to <Quick_Look.py>
            
@author: Fan Tong
'''

#from __future__ import division  # Allows an integer divided by an integer to return a real.
#   NOTE:  THE ABOVE SEEMS TO ME TO BE BAD FORM, AS THIS IS NOT USED UNIVERSALLY.

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pickle
import copy
from cycler import cycler
from Supporting_Functions import func_find_period
from Supporting_Functions import func_lines_plot
from Supporting_Functions import func_lines_2yaxes_plot
from Supporting_Functions import func_stack_plot
from Supporting_Functions import func_scatter_plot
from Supporting_Functions import func_time_conversion
from Supporting_Functions import func_load_optimization_results
from matplotlib.backends.backend_pdf import PdfPages

from Save_Basic_Results import read_pickle_raw_results

#%%


def quick_look(global_dic, case_dic_list):
    
    verbose = global_dic['VERBOSE']
        
    if verbose:
        print ( 'pickle files read' )
        
    # --------------- define and open output files -------------------------
    
    output_dir = global_dic['OUTPUT_PATH'] + '/' + global_dic['GLOBAL_NAME']
        # Create the ouput folder    
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Define file for pdfs containing figures comparing cases
    output_all = global_dic['GLOBAL_NAME'] + '_all_cases.pdf'
    pdf_all = PdfPages(output_dir + '/' + output_all) # create and open pdf file
    # Define file for pdfs containing figures relating to individual cases
    output_each = global_dic['GLOBAL_NAME'] + '_each_case.pdf'
    pdf_each = PdfPages(output_dir + '/' + output_each) # create and open pdf file
    # Define file for text output
    output_text = global_dic['GLOBAL_NAME'] + '_text.txt'
    text_file = open(output_dir + '/' + output_text,'w')
        
    # --------------- define colors for plots --------------------- 
    color_DEMAND = 'black'
    color_NATGAS  = 'red' # not explicitly referenced but referenced through eval()
    color_NATGAS_CCS  = 'brown' # not explicitly referenced but referenced through eval()
    color_SOLAR   = 'orange' # not explicitly referenced but referenced through eval()
    color_SOLAR2   = 'orangered' # not explicitly referenced but referenced through eval()
    color_WIND    = 'blue' # not explicitly referenced but referenced through eval()
    color_WIND2    = 'darkblue' # not explicitly referenced but referenced through eval()
    color_NUCLEAR = 'green' # not explicitly referenced but referenced through eval()
    color_FUEL = 'magenta'
    color_STORAGE = 'purple'
    color_STORAGE2 = 'violet'
    color_PGP_STORAGE =  'pink'
    color_CURTAILMENT =  'lightgray'
    color_UNMET_DEMAND =  'gray' # not explicitly referenced but referenced through eval()
    color_CSP = 'yellow'
    
    num_cases = len (case_dic_list) # number of cases
    # 'SYSTEM_COMPONENTS' -- LIST OF COMPONENTS, CHOICES ARE: 'WIND','SOLAR', 'NATGAS','NATGAS_CCS','NUCLEAR','FUEL','STORAGE', 'PGP_STORAGE', 'UNMET'    
    # Loop around and make output for individual cases  
    
    # ============= CREATE LIST OF input_data DICTIONARIES FOR PLOTTING PROGRAMS =========
    
    for case_idx in range(num_cases):
        
        case_dic = case_dic_list[case_idx] # get the input data for case in question
        num_time_periods = len(case_dic['DEMAND_SERIES'])
        
        if verbose:
            print ( 'preparing case ',case_idx,' ', case_dic['CASE_NAME'])
        result_dic = read_pickle_raw_results(global_dic, case_dic) # get the results data for case in question
        
        input_data = copy.copy(case_dic) # Dictionary for input into graphing functions will be superset of case_dic and result_dic
        input_data.update(result_dic)  # input_data is now the union of case_dic and result_dic
                
        input_data['pdf_each'] = pdf_each # file handle for pdf output case by case
        input_data['text_file'] = text_file # file handle for text output case by case
        system_components = case_dic['SYSTEM_COMPONENTS']

        # results_matrix_dispatch contains time series of things that add electricity to the grid
        # where unmet_demand is considered a pure variable cost source
        
        # Now build the array of dispatch technologies to be plotted for this case
        results_matrix_dispatch = []
        legend_list_dispatch = []
        color_list_dispatch = []
        component_index_dispatch = {}

        for component in system_components:
            addfrom = ''
            if component == 'STORAGE' or component == 'STORAGE2' or component == 'PGP_STORAGE' or component == 'CSP': 
                addfrom = 'FROM_'
            if component == 'FUEL': 
                addfrom = 'TO_'
            results_matrix_dispatch.append(result_dic['DISPATCH_' + addfrom + component ])
            legend_list_dispatch.append( 'DISPATCH_' + addfrom + component +' kW' )
            color_list_dispatch.append(eval('color_' + component))
            component_index_dispatch[component] = len(results_matrix_dispatch)-1 # row index for each component
        
        max_dispatch = np.max([sum(i) for i in zip(*results_matrix_dispatch)])
        max_cost = np.max(case_dic['DEMAND_SERIES']*result_dic['PRICE'])
        input_data['max_dispatch'] = max_dispatch
        input_data['max_cost'] = max_cost
        
        input_data['NUM_TIME_PERIODS'] = num_time_periods
        input_data['PRICE'] = result_dic['PRICE']
        
        input_data['NUM_TIME_PERIODS'] = num_time_periods
        input_data['results_matrix_dispatch'] = np.transpose(np.array(results_matrix_dispatch))
        input_data['legend_list_dispatch'] = legend_list_dispatch
        input_data['component_index_dispatch'] = component_index_dispatch
        input_data['color_list_dispatch'] = color_list_dispatch
        input_data['component_list_dispatch'] = system_components

        #----------------------------------------------------------------------
        # Now build the array of demand components to be plotted for this case
        # NOTE: this should  check that all these options are in the scenario
        # The next set of things gets electricity from the grid
        results_matrix_demand = [case_dic['DEMAND_SERIES']]
        legend_list_demand = ['demand (kW)']
        color_list_demand = [color_DEMAND]
        component_index_demand = {'DEMAND':1}
        
        component_list_storage = []
        for component in system_components:
            if component == 'STORAGE':
                results_matrix_demand.append(result_dic['DISPATCH_TO_STORAGE'])
                legend_list_demand.append('dispatch to storage (kW)')
                color_list_demand.append(color_STORAGE)
                component_index_demand['STORAGE'] = len(results_matrix_demand)-1
                component_list_storage.append('STORAGE')
            elif component == 'PGP_STORAGE': 
                results_matrix_demand.append(result_dic['DISPATCH_TO_PGP_STORAGE'])
                legend_list_demand.append('dispatch to pgp storage (kW)')
                color_list_demand.append(color_PGP_STORAGE)
                component_index_demand['PGP_STORAGE'] = len(results_matrix_demand)-1
                component_list_storage.append('PGPSTORAGE')
        
        input_data['results_matrix_demand'] = np.transpose(np.array(results_matrix_demand))
        input_data['legend_list_demand'] = legend_list_demand
        input_data['component_index_demand'] = component_index_demand
        input_data['color_list_demand'] = color_list_demand
        input_data['component_list_storage'] = component_list_storage

        #----------------------------------------------------------------------
        # Now build the array of curtailment components to be plotted for this case
        
        curtailment_dic = compute_curtailment(case_dic, result_dic)
        
        results_matrix_curtailment = []
        legend_list_curtailment = []
        color_list_curtailment = []
        component_index_curtailment = {}
        
        for component in curtailment_dic.keys():
            results_matrix_curtailment.append(curtailment_dic[component])
            legend_list_curtailment.append(component + ' (kW)')
            color_list_curtailment.append(eval('color_' + component))
            component_index_curtailment[component] = len(results_matrix_curtailment)-1
            
        input_data['results_matrix_curtailment'] = np.transpose(np.array(results_matrix_curtailment))
        input_data['legend_list_curtailment'] = legend_list_curtailment
        input_data['component_index_curtailment'] = component_index_curtailment
        input_data['color_list_curtailment'] = color_list_curtailment
        input_data['component_list_curtailment'] = curtailment_dic.keys()
        
        #----------------------------------------------------------------------        
        # end of section to generate list of input_data dictionaries


        
#        prepare_plot_results_bar_1scenario (input_data) # produce single case barchart plots
        call_plot_results_1scenario (input_data) # produce single case time series plots
        
        if verbose:
            print ( 'done with call_plot_results_1scenario for case '+input_data['CASE_NAME'])
            
         
    # close files
    pdf_all.close()
    pdf_each.close()
    text_file.close()
    if verbose:
        print ( 'files closed')

#%%
def make_result_dic_list(global_dic, case_dic_list):

    result_dic_list = []
    for idx in range(len(case_dic_list)):
        result_dic = read_pickle_raw_results(global_dic,case_dic_list[idx])
        result_dic_list.append(result_dic)
    
    return result_dic_list
    
    
#%%

def call_plot_results_1scenario(input_data):
    
    # -------------------------------------------------------------------------
    num_time_periods = input_data['NUM_TIME_PERIODS']

    results_matrix_dispatch = input_data['results_matrix_dispatch']   
    component_index_dispatch = input_data['component_index_dispatch']

    component_name_dispatch = {v: k for k, v in component_index_dispatch.items()}
        
    input_data['page_title'] = 'raw output'
    plot_results_dispatch_1scenario(input_data,1)  # basic results by hour
    plot_results_price_1scenario(input_data,1)  # price results by hour
    if 'STORAGE' in input_data['SYSTEM_COMPONENTS']:
        plot_results_storage_1scenario(input_data,1)
    
    input_data['page_title'] = 'daily averaging'
    plot_results_dispatch_1scenario(input_data,min(num_time_periods,24)) # basic results by day
    plot_results_price_1scenario(input_data,min(num_time_periods,24)) # price results by day
    if 'STORAGE' in input_data['SYSTEM_COMPONENTS']:
        plot_results_storage_1scenario(input_data,min(num_time_periods,24))
    
    input_data['page_title'] = '5-day averaging'
    plot_results_dispatch_1scenario(input_data,min(num_time_periods,24*5)) # basic results by week
    plot_results_price_1scenario(input_data,min(num_time_periods,24*5)) # price results by day
    if 'STORAGE' in input_data['SYSTEM_COMPONENTS']:
        plot_results_storage_1scenario(input_data,min(num_time_periods,24*5))
    
    # -------------------------------------------------------------------------
    # Find the week where storage dispatch is at its weekly max or min use
    
    for idx in range(results_matrix_dispatch.shape[1]):
        plot_extreme_dispatch_results_1scenario(input_data, component_name_dispatch[idx],'max',min(num_time_periods,24*5))
        
    return

#%%   

def plot_extreme_dispatch_results_1scenario(input_data,component_name,search_option,window_size):
    
    component_index_dispatch = input_data['component_index_dispatch']
    component_index = component_index_dispatch[component_name]
    
    results_matrix_dispatch = input_data['results_matrix_dispatch']
    
    study_variable_dict = {
            'window_size':      window_size,
            'data':             results_matrix_dispatch[:,component_index], 
            'print_option':     0,
            'search_option':    search_option
            }
    
    study_output_1 = func_find_period(study_variable_dict)    
    start_hour = study_output_1['left_index']
    end_hour = study_output_1['right_index']
        
    input_data['page_title'] = (
            component_name + ' ('+search_option+') supplied {:.2f} kW avg to the grid during hours: {} '
            .format(study_output_1['value'],  (start_hour,end_hour))
            )
    plot_results_dispatch_1scenario(input_data,1,start_hour,end_hour)  # to storage min for 2 weeks
    plot_results_price_1scenario(input_data,1,start_hour,end_hour) # price results by day
#    if 'STORAGE' in input_data['SYSTEM_COMPONENTS']:
#        plot_results_storage_1scenario(input_data,1,start_hour,end_hour)
       
#%%


def plot_results_dispatch_1scenario (input_data, hours_to_avg = None, start_hour = None, end_hour = None ):

    # Note hours_to_average is assumed to be an integer    
    
    # -------------------------------------------------------------------------
    # Get the input data
    
    demand = input_data['DEMAND_SERIES']
    results_matrix_dispatch = copy.deepcopy(input_data['results_matrix_dispatch'])
    results_matrix_demand = copy.deepcopy(input_data['results_matrix_demand'])
    results_matrix_curtailment = copy.deepcopy(input_data['results_matrix_curtailment'])
    pdf_each = input_data['pdf_each']
    legend_list_dispatch = input_data['legend_list_dispatch']
    legend_list_demand = input_data['legend_list_demand']
    legend_list_curtailment = input_data['legend_list_curtailment']
    color_list_dispatch = input_data['color_list_dispatch']
    color_list_demand = input_data['color_list_demand']
    color_list_curtailment = input_data['color_list_curtailment']
    case_name = input_data['CASE_NAME']

    #NOTE: Averaging should occur before time subsetting
    avg_label = ''
    if hours_to_avg != None:
        if hours_to_avg > 1:
            avg_label = ' ' + str(hours_to_avg) + ' hr moving avg'
            for i in range(results_matrix_dispatch.shape[1]):
                results_matrix_dispatch [:,i] = func_time_conversion(results_matrix_dispatch[:,i],hours_to_avg)
    
            for i in range(results_matrix_demand.shape[1]):
                results_matrix_demand [:,i] = func_time_conversion(results_matrix_demand[:,i],hours_to_avg)
    
            for i in range(results_matrix_curtailment.shape[1]):
                results_matrix_curtailment [:,i] = func_time_conversion(results_matrix_curtailment[:,i],hours_to_avg)

            demand = func_time_conversion(demand,hours_to_avg)
            
    if start_hour == None:
        start_hour = 0
    if end_hour == None:
        end_hour = len(demand)

    # -------------------------------------------------------------------------    
    # -------------------------------------------------------------------------
    # Define the plotting style
    plt.close() # Just make sure nothing is open ...
    regular_font = 5
    small_font = 4
    #plt.style.use('default')
    plt.style.use('default')
    # plt.style.use('bmh')
    # plt.style.use('fivethirtyeight')
    # plt.style.use('seaborn-white')
    #plt.rcParams['font.family'] = 'serif'
    #plt.rcParams['font.serif'] =  'Helvetica ' #'Palatino' # 'Ubuntu'
    plt.rcParams['font.monospace'] = 'Helvetica Mono' #'Palatino Mono' # 'Ubuntu'
    plt.rcParams['font.size'] = regular_font
    plt.rcParams['axes.labelsize'] = regular_font
    plt.rcParams['axes.linewidth'] = 0.5
    plt.rcParams['axes.labelweight'] = 'normal'
    plt.rcParams['axes.titlesize'] = regular_font
    plt.rcParams['xtick.labelsize'] = regular_font
    plt.rcParams['ytick.labelsize'] = regular_font
    plt.rcParams['legend.fontsize'] = small_font
    plt.rcParams['figure.titlesize'] = regular_font
    plt.rcParams['lines.linewidth'] = 0.5
    plt.rcParams['grid.color'] = 'k'
    plt.rcParams['grid.linestyle'] = ':'
    plt.rcParams['grid.linewidth'] = 0.5
    plt.rcParams['xtick.major.width'] = 0.5
    plt.rcParams['xtick.major.size'] = 3
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.major.width'] = 0.5
    plt.rcParams['ytick.major.size'] = 3
    plt.rcParams['ytick.direction'] = 'in'
        
#    
    figsize_oneplot = (6.5,9)
    
    # -------------------------------------------------------------------------
    # Figures 1 Hourly time series results
    
    # Four figures: 2 (dispatch, demand) * 2 (line plots, stack plots)
    
    # -------------
    
    
    num_time_periods = demand.size
    x_data = np.arange( num_time_periods)
    
    # -------------
    figDispatch, axs = plt.subplots(3, 2,figsize=figsize_oneplot)

    axs[0,0].set_prop_cycle(cycler('color', color_list_dispatch))
    
    inputs_dispatch = {
        'x_data':           x_data[start_hour:end_hour], 
#        'y_data':           results_matrix_dispatch,
        'y_data':           results_matrix_dispatch[start_hour:end_hour],
        'z_data':           demand[start_hour:end_hour],
        'ax':               axs[0,0],
        'x_label':          'Time (hour)',
        'y_label':          'kW',
        'title':            case_name +' hour '+str(start_hour)+' to '+str(end_hour)+'\nElectricity sources '+avg_label,
# If legend is not defined, no legend appears on plot
# legend is provided by accompanying stacked area plot
#        'legend':           legend_list_dispatch,  
#        'legend_z':         'demand',
        'line_width':       0.5,
        'line_width_z':     0.2,
        'grid_option':      0,
        }        

    axs[0,0].set_ylim([0, input_data['max_dispatch']])
    
    func_lines_plot(inputs_dispatch)
    
    # -------------
    

    axs[0,1].set_prop_cycle(cycler('color', color_list_dispatch))
    
    inputs_dispatch['ax'] = axs[0,1]
 
    inputs_dispatch['legend'] = legend_list_dispatch 
    inputs_dispatch['legend_z'] = 'demand' 

    axs[0,1].set_ylim([0, input_data['max_dispatch']])

    func_stack_plot(inputs_dispatch)
    
    
    # -------------  NOW DO DEMAND ---------------------


    axs[1,0].set_prop_cycle(cycler('color', color_list_demand))

    inputs_demand = {
        'x_data':           x_data[start_hour:end_hour], 
        'y_data':           results_matrix_demand[start_hour:end_hour],
        #'z_data':           demand,
        'ax':               axs[1,0],
        'x_label':          'Time (hour)',
        'y_label':          'kW',
        'title':            case_name +' hour '+str(start_hour)+' to '+str(end_hour)+'\nElectricity sinks '+avg_label,
        
# Don't print ( legend on line plot by not having it defined in this dictionary
#        'legend':           legend_list_demand,
        #'legend_z':         'demand',
        'line_width':       0.5,
        #'line_width_z':     0.2,
        'grid_option':      0,
        } 
          
    axs[1,0].set_ylim([0, input_data['max_dispatch']])

    func_lines_plot(inputs_demand)
    
    # -------------
    

    axs[1,1].set_prop_cycle(cycler('color', color_list_demand))

    inputs_demand['ax'] = axs[1,1]
    inputs_demand['legend'] = legend_list_demand

    axs[1,1].set_ylim([0, input_data['max_dispatch']])
    
    func_stack_plot(inputs_demand) 
    
    # -------------  NOW DO CURTAILMENT ---------------------

    axs[2,0].set_prop_cycle(cycler('color', color_list_curtailment))

    inputs_curtailment = {
        'x_data':           x_data[start_hour:end_hour], 
        'y_data':           results_matrix_curtailment[start_hour:end_hour],
        #'z_data':           demand,
        'ax':               axs[2,0],
        'x_label':          'Time (hour)',
        'y_label':          'kW',
        'title':            case_name +' hour '+str(start_hour)+' to '+str(end_hour)+'\nCurtailment '+avg_label,
        
# Don't print ( legend on line plot by not having it defined in this dictionary
#        'legend':           legend_list_demand,
        #'legend_z':         'demand',
        'line_width':       0.5,
        #'line_width_z':     0.2,
        'grid_option':      0,
        } 
          
    axs[2,0].set_ylim([0, input_data['max_dispatch']])

    func_lines_plot(inputs_curtailment)
    
    # -------------
    

    axs[2,1].set_prop_cycle(cycler('color', color_list_curtailment))

    inputs_curtailment['ax'] = axs[2,1]
    inputs_curtailment['legend'] = legend_list_curtailment
    
    axs[2,1].set_ylim([0, input_data['max_dispatch']])

    func_stack_plot(inputs_curtailment) 

    # -------------
    plt.suptitle(input_data['page_title'])
    plt.tight_layout(rect=[0,0,0.75,0.975])
    pdf_each.savefig(figDispatch)

    plt.close()

       
#%%
#==============================================================================
# plot_results_price_1scenario
#

def plot_results_price_1scenario (input_data, hours_to_avg = None, start_hour = None, end_hour = None ):

    # Note hours_to_average is assumed to be an integer    
    
    # -------------------------------------------------------------------------
    # Get the input data
    
    demand = input_data['DEMAND_SERIES']
    price = copy.deepcopy(input_data['PRICE'])
    results_matrix_dispatch = copy.deepcopy(input_data['results_matrix_dispatch'])
    results_matrix_demand = copy.deepcopy(input_data['results_matrix_demand'])
    results_matrix_curtailment = copy.deepcopy(input_data['results_matrix_curtailment'])
    pdf_each = input_data['pdf_each']
    legend_list_dispatch = input_data['legend_list_dispatch']
    legend_list_demand = input_data['legend_list_demand']
    legend_list_curtailment = input_data['legend_list_curtailment']
    color_list_dispatch = input_data['color_list_dispatch']
    color_list_demand = input_data['color_list_demand']
    color_list_curtailment = input_data['color_list_curtailment']
    case_name = input_data['CASE_NAME']

    #NOTE: Averaging should occur before time subsetting
    avg_label = ''
    dispatch_cost_matrix = results_matrix_dispatch*price[:,np.newaxis]
    if hours_to_avg != None:
        if hours_to_avg > 1:
            avg_label = ' ' + str(hours_to_avg) + ' hr moving avg'
            for i in range(results_matrix_dispatch.shape[1]):
                results_matrix_dispatch [:,i] = func_time_conversion(results_matrix_dispatch[:,i],hours_to_avg)
                dispatch_cost_matrix [:,i] = func_time_conversion(dispatch_cost_matrix[:,i],hours_to_avg)
    
            price = func_time_conversion(price,hours_to_avg)
            # Note that mean price is by time, and not demand weighted

            demand = func_time_conversion(demand,hours_to_avg)
            
    if start_hour == None:
        start_hour = 0
    if end_hour == None:
        end_hour = len(demand)
    # -------------------------------------------------------------------------    
    # -------------------------------------------------------------------------
    # Define the plotting style
    plt.close() # Just make sure nothing is open ...
    regular_font = 5
    small_font = 4
    #plt.style.use('default')
    plt.style.use('default')
    # plt.style.use('bmh')
    # plt.style.use('fivethirtyeight')
    # plt.style.use('seaborn-white')
    #plt.rcParams['font.family'] = 'serif'
    #plt.rcParams['font.serif'] =  'Helvetica ' #'Palatino' # 'Ubuntu'
    plt.rcParams['font.monospace'] = 'Helvetica Mono' #'Palatino Mono' # 'Ubuntu'
    plt.rcParams['font.size'] = regular_font
    plt.rcParams['axes.labelsize'] = regular_font
    plt.rcParams['axes.linewidth'] = 0.5
    plt.rcParams['axes.labelweight'] = 'normal'
    plt.rcParams['axes.titlesize'] = regular_font
    plt.rcParams['xtick.labelsize'] = regular_font
    plt.rcParams['ytick.labelsize'] = regular_font
    plt.rcParams['legend.fontsize'] = small_font
    plt.rcParams['figure.titlesize'] = regular_font
    plt.rcParams['lines.linewidth'] = 0.5
    plt.rcParams['grid.color'] = 'k'
    plt.rcParams['grid.linestyle'] = ':'
    plt.rcParams['grid.linewidth'] = 0.5
    plt.rcParams['xtick.major.width'] = 0.5
    plt.rcParams['xtick.major.size'] = 3
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.major.width'] = 0.5
    plt.rcParams['ytick.major.size'] = 3
    plt.rcParams['ytick.direction'] = 'in'
        
#    
    figsize_oneplot = (6.5,9)
    
    # -------------------------------------------------------------------------
    # Upper left will be a time series of price, upper right will be sorted by price high to low
    
    # -------------
    
    
    num_time_periods = demand.size
    x_data = np.arange( num_time_periods)
    
    # -------------
    
    figPrice, axs = plt.subplots(3, 2,figsize=figsize_oneplot)
    
    axs[0,0].set_ylim(min(price), max(price))
    axs[0,0].set_prop_cycle(cycler('color', color_list_dispatch))
    
    input_price_a = {
        'x_data':           x_data[start_hour:end_hour], 
#        'y_data':           results_matrix_dispatch,
        #'y_data':           np.asarray(price[start_hour:end_hour]),
        'y_data':           price[start_hour:end_hour],
        'ax':               axs[0,0],
        'x_label':          'Time (hour)',
        'y_label':          '$/kWh',
        'title':            case_name +' hour '+str(start_hour)+' to '+str(end_hour)+'\nElectricity price ($/kWh) '+avg_label,
# If legend is not defined, no legend appears on plot
# legend is provided by accompanying stacked area plot
#        'legend':           legend_list_dispatch,  
#        'legend_z':         'demand',
        'line_width':       0.5,
        'line_width_z':     0.2,
        'grid_option':      0,
        'y_scale':          "log"
        }        

    func_lines_plot(input_price_a)
     
 #--------- upper right now do the same thing but sort by price from high to low.
    input_price_b = copy.copy(input_price_a)

    input_price_b['x_data']= np.arange(end_hour-start_hour)
    input_price_b['y_data']= np.sort(price[start_hour:end_hour])[::-1]
    axs[0,1].set_ylim(min(price), max(price))
    axs[0,1].set_prop_cycle(cycler('color', color_list_dispatch))
     
    input_price_b['ax'] = axs[0,1]
  
    input_price_b['x_label'] = 'hour rank: 0 = highest price'
    func_lines_plot(input_price_b)
     
# =============================================================================
# =============================================================================
# We just had two plots of price by time and price by price ranked hour order
# Now, we should show contributions to cost of electricity (dispatch * price)
# =============================================================================
# =============================================================================
     
# -------------
# =============================================================================
    
    #axs[1,0].set_ylim([0, input_data['max_cost']])
    axs[1,0].set_prop_cycle(cycler('color', color_list_dispatch))
    
    input_price_c = {
         'x_data':           x_data[start_hour:end_hour], 
 #        'y_data':           results_matrix_dispatch,
         'y_data':           dispatch_cost_matrix[start_hour:end_hour],
         'ax':               axs[1,0],
         'x_label':          'Time (hour)',
         'y_label':          '$/hr',
         'title':            case_name +' hour '+str(start_hour)+' to '+str(end_hour)+'\nCost of dispatched electricity '+avg_label,
 # If legend is not defined, no legend appears on plot
 # legend is provided by accompanying stacked area plot
         #'legend':           legend_list_dispatch,  
 #        'legend_z':         'demand',
         'line_width':       0.5,
         #'line_width_z':     0.2,
         'grid_option':      0,
         }        
    
    func_stack_plot(input_price_c)
     
     # -------------
     
 # If legend is not defined, no legend appears on plot
 # legend is provided by accompanying stacked area plot
 #        'legend':           legend_list_dispatch,  
 # 
     # Now add legend for stack plot
     
     #figure1b = plt.figure(figsize=figsize_oneplot)
    input_price_d = copy.copy(input_price_c)

    #axs[1,1].set_ylim([0, input_data['max_cost']])
    axs[1,1].set_prop_cycle(cycler('color', color_list_dispatch))
     
    sort_order = np.argsort(price[start_hour:end_hour])[::-1]
    input_price_d['ax'] = axs[1,1]
    input_price_d['x_data'] = np.arange(end_hour-start_hour)
    input_price_d['x_label'] = 'hour rank: 0 = highest price'
    input_price_d['y_data'] = results_matrix_dispatch [start_hour:end_hour][sort_order]
    input_price_d['y_label'] = 'kW'
    #input_price_d['z_data'] = demand[start_hour:end_hour],

    input_price_d['title']= case_name +' hour '+str(start_hour)+' to '+str(end_hour)+'\nDispatch sorted by electricity price '+avg_label
    input_price_d['legend'] =  legend_list_dispatch
 
    func_stack_plot(input_price_d)
     
 
 #     # -------------
           
      #figure1b = plt.figure(figsize=figsize_oneplot)
      
# #     # -------------  NOW DO DEMAND ---------------------
# # 
# #     #figure1c = plt.figure(figsize=figsize_oneplot)
# #     axs[1,0] = figPrice.add_subplot(3,2,3)
# #     axs[1,0].set_prop_cycle(cycler('color', color_list_demand))
# # 
# #     inputs_demand = {
# #         'x_data':           x_data[start_hour:end_hour], 
# #         'y_data':           results_matrix_demand[start_hour:end_hour],
# #         #'z_data':           demand,
# #         'ax':               axs[1,0],
# #         'x_label':          'Time (hour)',
# #         'y_label':          'kW',
# #         'title':            case_name +' hour '+str(start_hour)+' to '+str(end_hour)+'\nElectricity sinks '+avg_label,
# #         
# # # Don't print ( legend on line plot by not having it defined in this dictionary
# # #        'legend':           legend_list_demand,
# #         #'legend_z':         'demand',
# #         'line_width':       0.5,
# #         #'line_width_z':     0.2,
# #         'grid_option':      0,
# #         } 
# #           
# #     axs[1,0].set_ylim([0, input_data['max_dispatch']])
# # 
# #     func_lines_plot(inputs_demand)
# #     
# #     # -------------
# #     
# #     #figure1d = plt.figure(figsize=figsize_oneplot)
# #     axs[1,1] = figPrice.add_subplot(3,2,4)
# #     axs[1,1].set_prop_cycle(cycler('color', color_list_demand))
# # 
# #     inputs_demand['ax'] = axs[1,1]
# #     inputs_demand['legend'] = legend_list_demand
# # 
# #     axs[1,1].set_ylim([0, input_data['max_dispatch']])
# #     
# #     func_stack_plot(inputs_demand) 
# #     
# #     # -------------  NOW DO CURTAILMENT ---------------------
# # 
# #     #figure1c = plt.figure(figsize=figsize_oneplot)
# #     axs[2,0] = figPrice.add_subplot(3,2,5)
# #     axs[2,0].set_prop_cycle(cycler('color', color_list_curtailment))
# # 
# #     inputs_curtailment = {
# #         'x_data':           x_data[start_hour:end_hour], 
# #         'y_data':           results_matrix_curtailment[start_hour:end_hour],
# #         #'z_data':           demand,
# #         'ax':               axs[2,0],
# #         'x_label':          'Time (hour)',
# #         'y_label':          'kW',
# #         'title':            case_name +' hour '+str(start_hour)+' to '+str(end_hour)+'\nCurtailment '+avg_label,
# #         
# # # Don't print ( legend on line plot by not having it defined in this dictionary
# # #        'legend':           legend_list_demand,
# #         #'legend_z':         'demand',
# #         'line_width':       0.5,
# #         #'line_width_z':     0.2,
# #         'grid_option':      0,
# #         } 
# #           
# #     axs[2,0].set_ylim([0, input_data['max_dispatch']])
# # 
# #     func_lines_plot(inputs_curtailment)
# #     
# #     # -------------
# #     
# #     #figure1d = plt.figure(figsize=figsize_oneplot)
# #     axs[2,1] = figPrice.add_subplot(3,2,6)
# #     axs[2,1].set_prop_cycle(cycler('color', color_list_curtailment))
# # 
# #     inputs_curtailment['ax'] = axs[2,1]
# #     inputs_curtailment['legend'] = legend_list_curtailment
# #     
# #     axs[2,1].set_ylim([0, input_data['max_dispatch']])
# # 
# #     func_stack_plot(inputs_curtailment) 
# # =============================================================================
# 
# =============================================================================
    # -------------
    
    plt.suptitle(input_data['page_title'])
    plt.tight_layout(rect=[0,0,0.75,0.975])
    pdf_each.savefig(figPrice)
    #plt.close()
    
    #pdf_each.savefig(figure1b)
    #plt.close()
    
    #pdf_each.savefig(figure1c)
    #plt.close()
    
    #pdf_each.savefig(figure1d)
    plt.close()

       
#%%

#
def plot_results_storage_1scenario (input_data, hours_to_avg = None, start_hour = None, end_hour = None ):

    # Note hours_to_average is assumed to be an integer    
    
    # -------------------------------------------------------------------------
    # Get the input data
    
    # note: At this point, input_data contains both case_dic and result_dic plus additional material.
    
    # Note further that at this point, result_dic already includes storage_dic
    
    # =============================================================================
    #         storage_dic = {
    #             "max_headroom":     max_headroom,
    #             "mean_storage_time":      mean_storage_time,
    #             "max_storage_time":       max_storage_time,
    #             "elec_cost_elec_storage":   elec_cost_elec_storage,
    #             "var_cost_elec_storage":    var_cost_elec_storage,
    #             "revenue_elec_storage":     revenue_elec_storage,
    #             "net_revenue":              net_revenue.all,
    #             "net_revenue_perkWh":       net_revenue_perkWh,
    #             "storage_cost_perkWh":      storage_cost_perkWh
    #             }
    #             #  <max_headroom> how much headroom the storage needed to deliver the electricity in each hour.
    #             #  <mean_storage_time> mean storage time of electricity delivered in each hour.
    #             #  <max_storage_time> maximum storage time of electricity delivered in each hour. 
    #             
    #             #  <net_revenue> net_revenue from storage considering cost of electricity plus variable costs associated with storage.
    #             #  <cost_elec_storage> cost of electricity sold from storage in each hour
    #             #  <var_cost_storage> variable costs associated with electricity sold from storage in each hour
    #             #  <revenue_elec_storage> revenue from electricity sold from storage in each hour
    #     
    # =============================================================================
    demand = input_data['DEMAND_SERIES']

    pdf_each = input_data['pdf_each']
    
    # Catch cases where storage was not included in system
    try:
        price = copy.deepcopy(input_data['PRICE'])
        max_headroom = copy.deepcopy(input_data['max_headroom'])
        revenue_elec_storage = copy.deepcopy(input_data['net_revenue'])
        net_revenue = copy.deepcopy(input_data['net_revenue'])
        net_cost_elec_storage = copy.deepcopy(input_data['net_cost_elec_storage'])
        # note: net_revenue = revenue_elec_storage - net_cost_elec_storage
        dispatch_to_storage = copy.deepcopy(input_data['DISPATCH_TO_STORAGE'])
        dispatch_from_storage = copy.deepcopy(input_data['DISPATCH_FROM_STORAGE'])
        energy_storage = copy.deepcopy(input_data['ENERGY_STORAGE'])
    except KeyError:
        print("Storage not included in system, skipping plotting storage results from Quick_Look.plot_results_storage_1scenario")
        return

    case_name = input_data['CASE_NAME']
    
    color_list_dispatch = input_data['color_list_dispatch']


    #NOTE: Averaging should occur before time subsetting
    avg_label = ''
    if hours_to_avg != None:
        if hours_to_avg > 1:
            avg_label = ' ' + str(hours_to_avg) + ' hr moving avg'
            
            price = func_time_conversion(price,hours_to_avg)
            max_headroom = func_time_conversion(max_headroom,hours_to_avg)
            net_revenue = func_time_conversion(net_revenue,hours_to_avg)
            net_cost_elec_storage = func_time_conversion(net_cost_elec_storage,hours_to_avg)
            dispatch_to_storage = func_time_conversion(dispatch_to_storage,hours_to_avg)
            dispatch_from_storage = func_time_conversion(dispatch_from_storage,hours_to_avg)
            energy_storage = func_time_conversion(energy_storage,hours_to_avg)

            
    if start_hour == None:
        start_hour = 0
    if end_hour == None:
        end_hour = len(demand)
    # -------------------------------------------------------------------------    
    # -------------------------------------------------------------------------
    # Define the plotting style
    plt.close() # Just make sure nothing is open ...
    regular_font = 5
    small_font = 4
    #plt.style.use('default')
    plt.style.use('default')
    # plt.style.use('bmh')
    # plt.style.use('fivethirtyeight')
    # plt.style.use('seaborn-white')
    #plt.rcParams['font.family'] = 'serif'
    #plt.rcParams['font.serif'] =  'Helvetica ' #'Palatino' # 'Ubuntu'
    plt.rcParams['font.monospace'] = 'Helvetica Mono' #'Palatino Mono' # 'Ubuntu'
    plt.rcParams['font.size'] = regular_font
    plt.rcParams['axes.labelsize'] = regular_font
    plt.rcParams['axes.linewidth'] = 0.5
    plt.rcParams['axes.labelweight'] = 'normal'
    plt.rcParams['axes.titlesize'] = regular_font
    plt.rcParams['xtick.labelsize'] = regular_font
    plt.rcParams['ytick.labelsize'] = regular_font
    plt.rcParams['legend.fontsize'] = small_font
    plt.rcParams['figure.titlesize'] = regular_font
    plt.rcParams['lines.linewidth'] = 0.5
    plt.rcParams['grid.color'] = 'k'
    plt.rcParams['grid.linestyle'] = ':'
    plt.rcParams['grid.linewidth'] = 0.5
    plt.rcParams['xtick.major.width'] = 0.5
    plt.rcParams['xtick.major.size'] = 3
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.major.width'] = 0.5
    plt.rcParams['ytick.major.size'] = 3
    plt.rcParams['ytick.direction'] = 'in'
        
#    
    figsize_oneplot = (6.5,9)
    
    # -------------------------------------------------------------------------
    # Upper left will be a time series of price, upper right will be sorted by price high to low
    
    # -------------
    
    
    num_time_periods = demand.size
    x_data = np.arange( num_time_periods)
    
    # -------------
    
    figStorage, axs = plt.subplots(3, 2,figsize=figsize_oneplot)
    
    axs[0,0].set_ylim(min(price), max(price))
    axs[0,0].set_prop_cycle(cycler('color', color_list_dispatch))
    
    input_storage_a = {
        'x_data':           x_data[start_hour:end_hour], 
#        'y_data':           results_matrix_dispatch,
        #'y_data':           np.asarray(price[start_hour:end_hour]),
        'y_data':           np.transpose(np.array((energy_storage[start_hour:end_hour],
                                      max_headroom[start_hour:end_hour]))),
        'ax':               axs[0,0],
        'x_label':          'Time (hour)',
        'y_label':          'kWh',
        'title':            case_name +' hour '+str(start_hour)+' to '+str(end_hour)+'\nEnergy storage and headroom needed (kWh) '+avg_label,
# If legend is not defined, no legend appears on plot
# legend is provided by accompanying stacked area plot
#        'legend':           legend_list_dispatch,  
#        'legend_z':         'demand',
        'line_width':       0.1,
        'line_width_z':     0.2,
        'grid_option':      0,
        'y_scale':          "log"
        }        

    #    print ('input_storage_a')
    #    for key in input_storage_a.keys():
    #        print (key,input_storage_a[key])
    func_lines_plot(input_storage_a)
     
 #--------- upper right now show headroom needed sorted from high to low.
    input_storage_b = copy.copy(input_storage_a)

    input_storage_b['x_data']= np.sort(max_headroom[start_hour:end_hour])[::-1]
    input_storage_b['y_data']= 1+np.arange(end_hour-start_hour)
    #axs[0,1].set_ylim(min(price), max(price))
    axs[0,1].set_prop_cycle(cycler('color', color_list_dispatch))
     
    input_storage_b['ax'] = axs[0,1]
  
    input_storage_b['x_label'] = 'hour rank: 0 = highest price'
    
    #    print ('input_storage_b')
    #    for key in input_storage_b.keys():
    #        print (key,input_storage_b[key])

    func_lines_plot(input_storage_b)
     
# =============================================================================
# =============================================================================
# We just had two plots of price by time and price by price ranked hour order
# Now, we should show contributions to cost of electricity (dispatch * price)
# =============================================================================
# =============================================================================
     
    axs[1,0].set_ylim(min(price), max(price))
    axs[1,0].set_prop_cycle(cycler('color', color_list_dispatch))
    
    input_storage_c = {
        'x_data':           x_data[start_hour:end_hour], 
#        'x_data':           net_cost_elec_storage[start_hour:end_hour], 
#        'y_data':           results_matrix_dispatch,
        #'y_data':           np.asarray(price[start_hour:end_hour]),
        'y_data':           price[start_hour:end_hour],
        'ax':               axs[0,0],
        'x_label':          'Time (hour)',
        'y_label':          'kWh',
        'title':            case_name +' hour '+str(start_hour)+' to '+str(end_hour)+'\nSales price vs storage cost ($/kWh) '+avg_label,
# If legend is not defined, no legend appears on plot
# legend is provided by accompanying stacked area plot
#        'legend':           legend_list_dispatch,  
#        'legend_z':         'demand',
        'line_width':       0.1,
        'line_width_z':     0.2,
        'grid_option':      0,
        'y_scale':          "linear"
        }        

    func_lines_plot(input_storage_c)
    
    sort_args = np.argsort(price[start_hour:end_hour])[::-1]
     
 #--------- upper right now show headroom needed sorted from high to low.

    input_storage_d = copy.copy(input_storage_a)

    input_storage_d['x_data']= np.arange(end_hour-start_hour)
    input_storage_d['y_data']= np.transpose(np.array((dispatch_to_storage[start_hour:end_hour][sort_args],
                                      dispatch_from_storage[start_hour:end_hour][sort_args])))
    #axs[0,1].set_ylim(min(price), max(price))
    axs[1,1].set_prop_cycle(cycler('color', color_list_dispatch))
     
    input_storage_d['ax'] = axs[0,1]
  
    input_storage_d['x_label'] = 'hour rank: 0 = highest price'
    func_lines_plot(input_storage_d)
#      
#      # -------------
#      
#  # If legend is not defined, no legend appears on plot
#  # legend is provided by accompanying stacked area plot
#  #        'legend':           legend_list_dispatch,  
#  # 
#      # Now add legend for stack plot
#      
#      #figure1b = plt.figure(figsize=figsize_oneplot)
#     input_price_d = copy.copy(input_price_c)
#     axs[1,1] = figStorage.add_subplot(3,2,4)
#     #axs[1,1].set_ylim([0, input_data['max_cost']])
#     axs[1,1].set_prop_cycle(cycler('color', color_list_dispatch))
#      
#     sort_order = np.argsort(price[start_hour:end_hour])[::-1]
#     input_price_d['ax'] = axs[1,1]
#     input_price_d['x_data'] = np.arange(end_hour-start_hour)
#     input_price_d['x_label'] = 'hour rank: 0 = highest price'
#     input_price_d['y_data'] = results_matrix_dispatch [start_hour:end_hour][sort_order]
#     input_price_d['y_label'] = 'kW'
#     #input_price_d['z_data'] = demand[start_hour:end_hour],
# 
#     input_price_d['title']= case_name +' hour '+str(start_hour)+' to '+str(end_hour)+'\nDispatch sorted by electricity price '+avg_label
#     input_price_d['legend'] =  legend_list_dispatch
#  
#     func_stack_plot(input_price_d)
#      
#  
# =============================================================================
 #     # -------------
           
      #figure1b = plt.figure(figsize=figsize_oneplot)
      
# #     # -------------  NOW DO DEMAND ---------------------
# # 
# #     #figure1c = plt.figure(figsize=figsize_oneplot)
# #     axs[1,0] = figStorage.add_subplot(3,2,3)
# #     axs[1,0].set_prop_cycle(cycler('color', color_list_demand))
# # 
# #     inputs_demand = {
# #         'x_data':           x_data[start_hour:end_hour], 
# #         'y_data':           results_matrix_demand[start_hour:end_hour],
# #         #'z_data':           demand,
# #         'ax':               axs[1,0],
# #         'x_label':          'Time (hour)',
# #         'y_label':          'kW',
# #         'title':            case_name +' hour '+str(start_hour)+' to '+str(end_hour)+'\nElectricity sinks '+avg_label,
# #         
# # # Don't print ( legend on line plot by not having it defined in this dictionary
# # #        'legend':           legend_list_demand,
# #         #'legend_z':         'demand',
# #         'line_width':       0.5,
# #         #'line_width_z':     0.2,
# #         'grid_option':      0,
# #         } 
# #           
# #     axs[1,0].set_ylim([0, input_data['max_dispatch']])
# # 
# #     func_lines_plot(inputs_demand)
# #     
# #     # -------------
# #     
# #     #figure1d = plt.figure(figsize=figsize_oneplot)
# #     axs[1,1] = figStorage.add_subplot(3,2,4)
# #     axs[1,1].set_prop_cycle(cycler('color', color_list_demand))
# # 
# #     inputs_demand['ax'] = axs[1,1]
# #     inputs_demand['legend'] = legend_list_demand
# # 
# #     axs[1,1].set_ylim([0, input_data['max_dispatch']])
# #     
# #     func_stack_plot(inputs_demand) 
# #     
# #     # -------------  NOW DO CURTAILMENT ---------------------
# # 
# #     #figure1c = plt.figure(figsize=figsize_oneplot)
# #     axs[2,0] = figStorage.add_subplot(3,2,5)
# #     axs[2,0].set_prop_cycle(cycler('color', color_list_curtailment))
# # 
# #     inputs_curtailment = {
# #         'x_data':           x_data[start_hour:end_hour], 
# #         'y_data':           results_matrix_curtailment[start_hour:end_hour],
# #         #'z_data':           demand,
# #         'ax':               axs[2,0],
# #         'x_label':          'Time (hour)',
# #         'y_label':          'kW',
# #         'title':            case_name +' hour '+str(start_hour)+' to '+str(end_hour)+'\nCurtailment '+avg_label,
# #         
# # # Don't print ( legend on line plot by not having it defined in this dictionary
# # #        'legend':           legend_list_demand,
# #         #'legend_z':         'demand',
# #         'line_width':       0.5,
# #         #'line_width_z':     0.2,
# #         'grid_option':      0,
# #         } 
# #           
# #     axs[2,0].set_ylim([0, input_data['max_dispatch']])
# # 
# #     func_lines_plot(inputs_curtailment)
# #     
# #     # -------------
# #     
# #     #figure1d = plt.figure(figsize=figsize_oneplot)
# #     axs[2,1] = figStorage.add_subplot(3,2,6)
# #     axs[2,1].set_prop_cycle(cycler('color', color_list_curtailment))
# # 
# #     inputs_curtailment['ax'] = axs[2,1]
# #     inputs_curtailment['legend'] = legend_list_curtailment
# #     
# #     axs[2,1].set_ylim([0, input_data['max_dispatch']])
# # 
# #     func_stack_plot(inputs_curtailment) 
# # =============================================================================
# 
# =============================================================================
    # -------------
    
    plt.suptitle(input_data['page_title'])
    plt.tight_layout(rect=[0,0,0.75,0.975])
    pdf_each.savefig(figStorage)
    #plt.close()
    
    #pdf_each.savefig(figure1b)
    #plt.close()
    
    #pdf_each.savefig(figure1c)
    #plt.close()
    
    #pdf_each.savefig(figure1d)
    plt.close()
         
#%%
#==============================================================================
# plot_results_bar_1scenario
#
# Purpose
#   Generate dispatch mix figures. Right now, there are N*4 figures.
#       N=3 corresponds to different temporal resolutions: hourly, daily, weekly.
#       4 corresponds to subplots for the same 'information' (time scale).
#
# Input
#   A packaging dictionary variable: input_data, which contrains the following data
#       [1] results_matrix_dispatch:  dispatch mix for a particular scenario
#       [2] demand
#   the following texts
#       [3] legend_list
#       [4] title_text
#   and the following controls for graphical outputs
#       [5] SAVE_FIGURES_TO_PDF:   logical variable [0/1]
#       [6] directory_output:      a complete directory, ending with '/'
#       [7] graphics_file_name
#
#   Data dimentions
#       results_matrix_dispatch
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
#
#    Jul 9, 2018 Convert to use with the base version of the Simple Energy Model
# @Ken Caldeira
#
def plot_results_bar_1scenario (input_data):

    # Note hours_to_average is assumed to be an integer    
    
    # -------------------------------------------------------------------------
    # Get the input data
    system_components = input_data['SYSTEM_COMPONENTS']
    
    demand = input_data['DEMAND_SERIES']
    results_matrix_dispatch = copy.deepcopy(input_data['results_matrix_dispatch'])
    results_matrix_demand = copy.deepcopy(input_data['results_matrix_demand'])
    results_matrix_curtailment = copy.deepcopy(input_data['results_matrix_curtailment'])
    pdf_each = input_data['pdf_each']
    legend_list_dispatch = input_data['legend_list_dispatch']
    legend_list_demand = input_data['legend_list_demand']
    legend_list_curtailment = input_data['legend_list_curtailment']
    color_list_dispatch = input_data['color_list_dispatch']
    color_list_demand = input_data['color_list_demand']
    color_list_curtailment = input_data['color_list_curtailment']
    case_name = input_data['CASE_NAME']

    # -------------------------------------------------------------------------    
    # -------------------------------------------------------------------------
    # Define the plotting style
    plt.close() # Just make sure nothing is open ...
    regular_font = 5
    small_font = 4
    #plt.style.use('default')
    plt.style.use('default')
    # plt.style.use('bmh')
    # plt.style.use('fivethirtyeight')
    # plt.style.use('seaborn-white')
    #plt.rcParams['font.family'] = 'serif'
    #plt.rcParams['font.serif'] =  'Helvetica ' #'Palatino' # 'Ubuntu'
    plt.rcParams['font.monospace'] = 'Helvetica Mono' #'Palatino Mono' # 'Ubuntu'
    plt.rcParams['font.size'] = regular_font
    plt.rcParams['axes.labelsize'] = regular_font
    plt.rcParams['axes.linewidth'] = 0.5
    plt.rcParams['axes.labelweight'] = 'normal'
    plt.rcParams['axes.titlesize'] = regular_font
    plt.rcParams['xtick.labelsize'] = regular_font
    plt.rcParams['ytick.labelsize'] = regular_font
    plt.rcParams['legend.fontsize'] = small_font
    plt.rcParams['figure.titlesize'] = regular_font
    plt.rcParams['lines.linewidth'] = 0.5
    plt.rcParams['grid.color'] = 'k'
    plt.rcParams['grid.linestyle'] = ':'
    plt.rcParams['grid.linewidth'] = 0.5
    plt.rcParams['xtick.major.width'] = 0.5
    plt.rcParams['xtick.major.size'] = 3
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.major.width'] = 0.5
    plt.rcParams['ytick.major.size'] = 3
    plt.rcParams['ytick.direction'] = 'in'
        
#    
    figsize_oneplot = (6.5,9)
    
    # Figures are: 
    #  UL:fixed and variables [capacity and dispatch] costs (inputs) [power]
    #  Ml: generation capacity and mean generation (results)
    #  LL:fixed and variable costs (results)
    
    # UR: storage capacity [energy]
    # MR: demand, energy to storage/PGPstorage (results)
    # LR: storage cycles per year
    
    # -------------------------------------------------------------------------
    # Figures 1 Hourly time series results
    
    # Four figures: 2 (dispatch, demand) * 2 (line plots, stack plots)
    
    # -------------
    
    
    num_time_periods = demand.size
    x_data = np.arange(num_time_periods)
    
    # -------------
    
    figDispatch, axs = plt.subplots(3, 2,figsize=figsize_oneplot)
    
    # first panel is bar chart of capacity and dispatch costs
    
    axs[0,0].set_prop_cycle(cycler('color', color_list_dispatch))
    
    inputs_dispatch = {
        'x_data':           legend_list_dispatch, 
#        'y_data':           results_matrix_dispatch,
        'y_data':           results_matrix_dispatch[start_hour:end_hour],
        'z_data':           demand[start_hour:end_hour],
        'ax':               axs[0,0],
        'x_label':          'Time (hour)',
        'y_label':          'kW',
        'title':            case_name +' hour '+str(start_hour)+' to '+str(end_hour)+'\nElectricity sources '+avg_label,
# If legend is not defined, no legend appears on plot
# legend is provided by accompanying stacked area plot
#        'legend':           legend_list_dispatch,  
#        'legend_z':         'demand',
        'line_width':       0.5,
        'line_width_z':     0.2,
        'grid_option':      0,
        }        

    axs[0,0].set_ylim([0, input_data['max_dispatch']])
    
    func_lines_plot(inputs_dispatch)
    
    # -------------
    
# If legend is not defined, no legend appears on plot
# legend is provided by accompanying stacked area plot
#        'legend':           legend_list_dispatch,  
# 
    # Now add legend for stack plot

    axs[0,1].set_prop_cycle(cycler('color', color_list_dispatch))
    
    inputs_dispatch['ax'] = axs[0,1]
 
    inputs_dispatch['legend'] = legend_list_dispatch 
    inputs_dispatch['legend_z'] = 'demand' 

    axs[0,1].set_ylim([0, input_data['max_dispatch']])

    func_stack_plot(inputs_dispatch)
    
    
    # -------------  NOW DO DEMAND ---------------------

    axs[1,0].set_prop_cycle(cycler('color', color_list_demand))

    inputs_demand = {
        'x_data':           x_data[start_hour:end_hour], 
        'y_data':           results_matrix_demand[start_hour:end_hour],
        #'z_data':           demand,
        'ax':               axs[1,0],
        'x_label':          'Time (hour)',
        'y_label':          'kW',
        'title':            case_name +' hour '+str(start_hour)+' to '+str(end_hour)+'\nElectricity sinks '+avg_label,
        
# Don't print ( legend on line plot by not having it defined in this dictionary
#        'legend':           legend_list_demand,
        #'legend_z':         'demand',
        'line_width':       0.5,
        #'line_width_z':     0.2,
        'grid_option':      0,
        } 
          
    axs[1,0].set_ylim([0, input_data['max_dispatch']])

    func_lines_plot(inputs_demand)
    
    # -------------
    
    #figure1d = plt.figure(figsize=figsize_oneplot)

    axs[1,1].set_color_cycle(color_list_demand)
    axs[1,1].set_prop_cycle(cycler('color', color_list_demand))

    inputs_demand['ax'] = axs[1,1]
    inputs_demand['legend'] = legend_list_demand

    axs[1,1].set_ylim([0, input_data['max_dispatch']])
    
    func_stack_plot(inputs_demand) 
    
    # -------------  NOW DO CURTAILMENT ---------------------

    #figure1c = plt.figure(figsize=figsize_oneplot)

    axs[2,0].set_prop_cycle(cycler('color', color_list_curtailment))

    inputs_curtailment = {
        'x_data':           x_data[start_hour:end_hour], 
        'y_data':           results_matrix_curtailment[start_hour:end_hour],
        #'z_data':           demand,
        'ax':               axs[2,0],
        'x_label':          'Time (hour)',
        'y_label':          'kW',
        'title':            case_name +' hour '+str(start_hour)+' to '+str(end_hour)+'\nCurtailment '+avg_label,
        
# Don't print ( legend on line plot by not having it defined in this dictionary
#        'legend':           legend_list_demand,
        #'legend_z':         'demand',
        'line_width':       0.5,
        #'line_width_z':     0.2,
        'grid_option':      0,
        } 
          
    axs[2,0].set_ylim([0, input_data['max_dispatch']])

    func_lines_plot(inputs_curtailment)
    
    # -------------
    
    axs[2,1].set_color_cycle(color_list_curtailment)
    axs[2,1].set_prop_cycle(cycler('color', color_list_curtailment))

    inputs_curtailment['ax'] = axs[2,1]
    inputs_curtailment['legend'] = legend_list_curtailment
    
    axs[2,1].set_ylim([0, input_data['max_dispatch']])

    func_stack_plot(inputs_curtailment) 

    # -------------
    plt.suptitle(input_data['page_title'])
    plt.tight_layout(rect=[0,0,0.75,0.975])
    pdf_each.savefig(figDispatch)
    #plt.close()
    
    #pdf_each.savefig(figure1b)
    #plt.close()
    
    #pdf_each.savefig(figure1c)
    #plt.close()
    
    #pdf_each.savefig(figure1d)
    plt.close()
        
    
#%%

def get_results_matrix_column(results_matrix,component_list_index_dic,component):
    return results_matrix[:,component_list_index_dic[component]] 

          
 
#%%==============================================================================

def func_graphics_dispatch_var_Nscenarios (input_data):

    # -------------------------------------------------------------------------
    # Get the input data
    num_time_periods = input_data['NUM_TIME_PERIODS']
    
    pdf_all = input_data['pdf_all']
    demand = input_data['DEMAND_SERIES']
    results_matrix_dispatch = input_data['results_matrix_dispatch']
    time_range = input_data['time_range']
    legend_list = input_data['legend_list']
    title_text = input_data['title_text']   
    
    
    # -------------------------------------------------------------------------
    # Define the plotting style
    
    #plt.style.use('default')
    plt.style.use('default')
    # plt.style.use('bmh')
    # plt.style.use('fivethirtyeight')
    # plt.style.use('seaborn-white')
#    plt.rcParams['font.family'] = 'serif'
#    plt.rcParams['font.serif'] =  'Helvetica ' #'Palatino' # 'Ubuntu'
#    plt.rcParams['font.monospace'] = 'Helvetica Mono' #'Palatino Mono' # 'Ubuntu'
#    plt.rcParams['font.size'] = 16
#    plt.rcParams['axes.labelsize'] = 16
#    plt.rcParams['axes.labelweight'] = 'bold'
#    plt.rcParams['axes.titlesize'] = 16
#    plt.rcParams['xtick.labelsize'] = 16
#    plt.rcParams['ytick.labelsize'] = 16
#    plt.rcParams['legend.fontsize'] = 14
#    plt.rcParams['figure.titlesize'] = 16
#    plt.rcParams['lines.linewidth'] = 2.0
#    plt.rcParams['grid.color'] = 'k'
#    plt.rcParams['grid.linestyle'] = ':'
#    plt.rcParams['grid.linewidth'] = 0.5
#    plt.rcParams['xtick.major.width'] = 2
#    plt.rcParams['xtick.major.size'] = 6
#    plt.rcParams['xtick.direction'] = 'in'
#    plt.rcParams['ytick.major.width'] = 2
#    plt.rcParams['ytick.major.size'] = 6
#    plt.rcParams['ytick.direction'] = 'in'
    
    # -------------------------------------------------------------------------
    
    figsize_oneplot = (8,6)
    
    # -------------------------------------------------------------------------
    
    # Figure 1 Sorted time series of discharging - y axis option #1
    
    # -----------------------------
    
    num_time_periods = results_matrix_dispatch.shape[0]
    x_data = np.arange( num_time_periods)
    
    results_matrix_dispatch1 = np.zeros(results_matrix_dispatch.shape)
    
    for i in range(results_matrix_dispatch.shape[1]):
        results_matrix_dispatch1 [:,i] = \
            -np.sort(-np.reshape(results_matrix_dispatch[:,i], -1))
    
    # -----------------------------
    
    figure1 = plt.figure(figsize=figsize_oneplot)
    ax1 = figure1.add_subplot(1,1,1)
    
    inputs = {
            'x_data':       x_data, 
            'y_data':       results_matrix_dispatch1,
            'ax':           ax1,
            'x_label':      'Time (hour)',
            'y_label':      'kW',
            'title':        title_text,
            'legend':       legend_list,
            'line_width':    1,
            'grid_option':   1,
            }        
            
    ax1.set_ylim([0, input_data['max_dispatch']])
    
    func_lines_plot(inputs)
    
    pdf_all.savefig(figure1)
        
#    # ---------------------------
#    
#    # Figure 1b  Sorted time series of discharging - y axis option #2
#    
#    # -----------------------------
#    
##    num_time_periods = results_matrix_dispatch.shape[0]
##    x_data = np.arange(0, num_time_periods)
##    
##    results_matrix_dispatch1 = np.zeros(
##            results_matrix_dispatch.shape)
##    
##    for i in range(results_matrix_dispatch.shape[1]):
##        results_matrix_dispatch1 [:,i] = \
##            -np.sort(-np.reshape(results_matrix_dispatch[:,i], -1))
#    
#    # -----------------------------
#    
#    figure1b = plt.figure(figsize=figsize_oneplot)
#    axs[0,1] = figure1b.add_subplot(111)
#    
#    inputs = {
#            'x_data':       x_data, 
#            'y_data':       results_matrix_dispatch1/np.average(demand),
#            'ax':           axs[0,1],
#            'x_label':      'Time (hour in the year)',
#            'y_label':      'Dispatched energy\n(hourly-average demand)',
#            'title':        title_text,
#            'legend':       legend_list,
#            'line_width':    2,
#            'grid_option':   1,
#            }        
#            
#    func_lines_plot(inputs)
#    
#    if SAVE_FIGURES_TO_PDF:
#        pdf_each.savefig(figure1b)
#        plt.close()
        
    # -------------------------------------------------------------------------
    # Figure 2. Time series of discharging - y axis option #1
    
    # -----------------------------
    
    # x_data = np.arange(0, num_time_periods)
    
    # -----------------------------
    
    figure2 = plt.figure(figsize=figsize_oneplot)
    ax2 = figure2.add_subplot(111)
    
    inputs = {
            'x_data':       x_data, 
            'y_data':       results_matrix_dispatch,
            'ax':           ax2,
            'x_label':      'Time (hour in the year)',
            'y_label':      'kW',
            'title':        title_text,
            'legend':       legend_list,
            'line_width':    1,
            'grid_option':   0,
            }
    
    ax2.set_ylim([0, input_data['max_dispatch']])
    
    func_lines_plot(inputs)
    
    pdf_all.savefig(figure2)
    #plt.close()
    
#    # -------------------------
#    
#    #%% Figure 2b Time series of discharging - y axis option #2
#    
#    # -------------------------
#    
##    x_data = np.arange(0, num_time_periods)
#    
#    # -------------------------
#    
#    figure2b = plt.figure(figsize=figsize_oneplot)
#    ax2b = figure2b.add_subplot(111)
#    
#    inputs = {
#            'x_data':       x_data, 
#            'y_data':       results_matrix_dispatch/np.average(demand),
#            'ax':           ax2b,
#            'x_label':      'Time (hour in the year)',
#            'y_label':      'Discharged energy\n(hourly-average demand)',
#            'title':        title_text,
#            'legend':       legend_list,
#            'line_width':    1,
#            'grid_option':   0,
#            }
#    
#    func_lines_plot(inputs)
#    
#    if SAVE_FIGURES_TO_PDF:
#        pdf_each.savefig(figure2b) 
#        plt.close()
    
    # -------------------------------------------------------------------------
    # Figure 3 Time series of discharging - downscale to daily - y axis option #1
    
    # -------------------------
    
    temporal_scale = min(num_time_periods,24)
    x_data = np.arange( num_time_periods)
    
    results_matrix_dispatch1 = np.zeros(results_matrix_dispatch.shape)
    
    for i in range(results_matrix_dispatch.shape[1]):
        results_matrix_dispatch1 [:,i] = func_time_conversion(results_matrix_dispatch[:,i],temporal_scale)
    
    # -------------------------
    
    figure3 = plt.figure(figsize=figsize_oneplot)
    ax3 = figure3.add_subplot(111)
    
    inputs = {
            'x_data':       x_data, 
            'y_data':       results_matrix_dispatch1,
            'ax':           ax3,
            'x_label':      'Time (hour)',
            'y_label':      'kW',
            'title':        title_text,
            'legend':       legend_list,
            'line_width':    1,
            'grid_option':   0,
            }       
    
    ax3.set_ylim([0, input_data['max_dispatch']])
            
    func_lines_plot(inputs)

    pdf_all.savefig(figure3)
    #plt.close()
    
#    # ---------------------------
#    # Figure 3b. Time series of discharging - downscale to daily - y axis option #2
#    
#    # -------------------------
#    
##    temporal_scale = 24
##    x_data = np.arange(0, num_time_periods/temporal_scale)
##    
##    results_matrix_dispatch1 = np.zeros(
##            (int(results_matrix_dispatch.shape[0]/temporal_scale), 
##            int(results_matrix_dispatch.shape[1])))
##    
##    for i in range(results_matrix_dispatch.shape[1]):
##        results_matrix_dispatch1 [:,i] = \
##            func_time_conversion(results_matrix_dispatch[:,i],temporal_scale)
#    
#    # -------------------------
#    
#    figure3b = plt.figure(figsize=figsize_oneplot)
#    ax3b = figure3b.add_subplot(111)
#    
#    inputs = {
#            'x_data':       x_data, 
#            'y_data':       results_matrix_dispatch1/np.average(demand),
#            'ax':           ax3b,
#            'x_label':      'Time (day in the year)',
#            'y_label':      'Discharged energy\n(hourly-average demand)',
#            'title':        title_text,
#            'legend':       legend_list,
#            'line_width':    1,
#            'grid_option':   0,
#            }        
#            
#    func_lines_plot(inputs)
#    
#    if SAVE_FIGURES_TO_PDF:
#        pdf_each.savefig(figure3b)  
#        plt.close()
    
    # -----------------------------------------------------------------------------
    
    # Figure 4 Time series of discharging - downscale to weekly - y axis option #1
    
    # -------------------------
    
    temporal_scale = min(number_time_periods,24 * 7)
    x_data = np.arange( num_time_periods)
    
    results_matrix_dispatch1 = np.zeros(results_matrix_dispatch.shape)
    
    for i in range(results_matrix_dispatch.shape[1]):
        results_matrix_dispatch1 [:,i] = \
            func_time_conversion(results_matrix_dispatch[:,i],temporal_scale)
    
    # -------------------------
    
    figure4 = plt.figure(figsize=figsize_oneplot)
    ax4 = figure4.add_subplot(111)
    
    inputs = {
            'x_data':       x_data, 
            'y_data':       results_matrix_dispatch1,
            'ax':           ax4,
            'x_label':      'Time (week in the year)',
            'y_label':      'kW',
            'title':        title_text,
            'legend':       legend_list,
            'line_width':    1,
            'grid_option':   0,
            }        
            
    ax4.set_ylim([0, input_data['max_dispatch']])

    func_lines_plot(inputs)
    
    pdf_all.savefig(figure4)
    #plt.close()

#    # -----------------------------------------------------------------------------
#    # Figure 4b Time series of discharging - downscale to weekly - y axis option #2
#    
#    # -------------------------
#    
##    temporal_scale = 24 * 7
##    x_data = np.arange(0, num_time_periods/temporal_scale)
##    
##    results_matrix_dispatch1 = np.zeros(
##            (int(results_matrix_dispatch.shape[0]/temporal_scale), 
##            int(results_matrix_dispatch.shape[1])))
##    
##    for i in range(results_matrix_dispatch.shape[1]):
##        results_matrix_dispatch1 [:,i] = \
##            func_time_conversion(results_matrix_dispatch[:,i],temporal_scale)
#    
#    figure4b = plt.figure(figsize=figsize_oneplot)
#    ax4b = figure4b.add_subplot(111)
#    
#    inputs = {
#            'x_data':       x_data, 
#            'y_data':       results_matrix_dispatch1/np.average(demand),
#            'ax':           ax4b,
#            'x_label':      'Time (week in the year)',
#            'y_label':      'Discharged energy\n(hourly-average demand)',
#            'title':        title_text,
#            'legend':       legend_list,
#            'line_width':    1,
#            'grid_option':   0,
#            }        
#            
#    func_lines_plot(inputs)
#    
#    if SAVE_FIGURES_TO_PDF:
#        pdf_each.savefig(figure4b)
#        plt.close()
    

#%%
#==============================================================================
# func_graphics_system_results_Nscenarios
#
# Purpose
#   Generate 8 figures regarding the 'most interested' system-level results for
#       a series of similar optimizations.        
#
# Input
#   A packaging dictionary variable: input_data, which contrains the following data
#       First, inputs for the optimization model   
#       [1] component_index_dispatch:
#       [2] demand
#       [3] assumptions_matrix
#       Second, results from the optimization model    
#       [4] storage_dispatch_matrix
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
#       [14] directory_output:      a complete directory, ending with '/'
#       [15] graphics_file_name       
#
#   Data dimentions
#       assumptions_matrix <np.array> different scenarios
#       storage_***_matrix <np.array> 'values' for different scenarios        
#       '_matrix' <np.ndarray>
#           ROW dimension: technology options
#           COLUMN dimension: 'values' for different scenarios
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
    
    component_index_dispatch = input_data['component_index_dispatch']
    demand = input_data['DEMAND_SERIES']
    
    # core data
    
    assumptions_matrix = input_data['assumptions_matrix']
    storage_dispatch_matrix = input_data['storage_dispatch_matrix']
    storage_capacity_matrix = input_data['storage_capacity_matrix']
    storage_cycle_matrix = input_data['storage_cycle_matrix']
    storage_investment_matrix = input_data['storage_investment_matrix']
    power_capacity_matrix = input_data['power_capacity_matrix']
    power_dispatch_matrix = input_data['power_dispatch_matrix']
    cost_power_matrix = input_data['cost_power_matrix']
    cost_everything_matrix = input_data['cost_everything_matrix']
    
    # graphics-related
    
    x_label = input_data['x_label']
    pdf_all = input_data['pdf_all']  # handle for graphics file output for all cases
    
    # -------------------------------------------------------------------------
    
    # Create the output folder
    
    
    # Define the plotting style
    
    #plt.style.use('default')
    plt.style.use('default')
    # plt.style.use('bmh')
    # plt.style.use('fivethirtyeight')
    # plt.style.use('seaborn-white')
#    plt.rcParams['font.family'] = 'serif'
#    plt.rcParams['font.serif'] =  'Helvetica ' #'Palatino' # 'Ubuntu'
#    plt.rcParams['font.monospace'] = 'Helvetica Mono' #'Palatino Mono' # 'Ubuntu'
#    plt.rcParams['font.size'] = 16
#    plt.rcParams['axes.labelsize'] = 16
#    plt.rcParams['axes.labelweight'] = 'bold'
#    plt.rcParams['axes.titlesize'] = 16
#    plt.rcParams['xtick.labelsize'] = 16
#    plt.rcParams['ytick.labelsize'] = 16
#    plt.rcParams['legend.fontsize'] = 14
#    plt.rcParams['figure.titlesize'] = 16
#    plt.rcParams['lines.linewidth'] = 2.0
#    plt.rcParams['grid.color'] = 'k'
#    plt.rcParams['grid.linestyle'] = ':'
#    plt.rcParams['grid.linewidth'] = 0.5
#    plt.rcParams['xtick.major.width'] = 2
#    plt.rcParams['xtick.major.size'] = 6
#    plt.rcParams['xtick.direction'] = 'in'
#    plt.rcParams['ytick.major.width'] = 2
#    plt.rcParams['ytick.major.size'] = 6
#    plt.rcParams['ytick.direction'] = 'in'
      
    # -------------------------------------------------------------------------
    
    figsize_oneplot = (8,6)
    
    # -------------------------------------------------------------------------
    
    # Figure 1 Storage discharge energy
    
    figure1 = plt.figure(figsize=figsize_oneplot)
    ax1 = figure1.add_subplot(111)
    
    inputs_dispatch_1 = {
        'x_data':           assumptions_matrix, 
        'y_data':          storage_dispatch_matrix ,
        'ax':               ax1,
        'x_label':          x_label,
        'y_label':         'Storage discharge (kW)',
        'line_width':       1,
        'grid_option':      0,
        }
    
    [ax1, axs[0,1]] = func_lines_2yaxes_plot(inputs_dispatch_1)
    
    ax1.set_xscale('log', nonposx='clip')
    ax1.set_yscale('log', nonposx='clip')
    axs[0,1].set_yscale('log', nonposx='clip')
    
    pdf_all.savefig(figure1)
    #plt.close()
    
    # -------------------------------------------------------------------------
    
    # Figure 2 Storage capacity
    
    figure2 = plt.figure(figsize=figsize_oneplot)
    ax2 = figure2.add_subplot(111)
    
    inputs_dispatch_2 = {
        'x_data':           assumptions_matrix, 
        'y_data':          storage_capacity_matrix ,
        'ax':               ax2,
        'x_label':          x_label,
        'y_label':         'Storage capacity (kWh)',
        'line_width':       1,
        'grid_option':      0,
        }
    
    [ax2, ax2b] = func_lines_2yaxes_plot(inputs_dispatch_2)
    
    ax2.set_xscale('log', nonposx='clip')
    ax2.set_yscale('log', nonposx='clip')
    ax2b.set_yscale('log', nonposx='clip')
    
    pdf_all.savefig(figure2)
    #plt.close()
    
    # -------------------------------------------------------------------------
    
    # Figure 3 Full-discharge cycles
    
    figure3 = plt.figure(figsize=figsize_oneplot)
    ax3 = figure3.add_subplot(111)
    
    inputs_dispatch_3 = {
        'x_data':           assumptions_matrix, 
        'y_data':           storage_cycle_matrix,
        'ax':               ax3,
        'x_label':          x_label,
        'y_label':          'Calculated full-discharge cycles',
        'line_width':       1,
        'grid_option':      0,
        }        
    
    ax3.set_xscale('log', nonposx='clip')
    ax3.set_yscale('log', nonposx='clip')
    
    func_lines_plot(inputs_dispatch_3)
    
    pdf_all.savefig(figure3)
    #plt.close()
    
    # -------------------------------------------------------------------------
    
    # Figure 4 Storage investment
    
    figure4 = plt.figure(figsize=figsize_oneplot)
    ax4 = figure4.add_subplot(111)
    
    inputs_dispatch_4 = {
        'x_data':           assumptions_matrix, 
        'y_data':           storage_investment_matrix ,
        'ax':               ax4,
        'x_label':          x_label,
        'y_label':          'Energy storage investment (billion $)',
        'line_width':       1,
        'grid_option':      0,
        }        
    
    ax4.set_xscale('log', nonposx='clip')
    # ax4.set_yscale('log', nonposx='clip')
    
    func_lines_plot(inputs_dispatch_4)
    
    pdf_all.savefig(figure4)
    #plt.close()
    
    # -------------------------------------------------------------------------
    
    # Figure 5 Power generation capacity
    
    legend_list = sorted(component_index_dispatch.keys(), key=lambda x: x[1])
    
    figure5 = plt.figure(figsize=figsize_oneplot)
    ax5 = figure5.add_subplot(111)
    
    inputs_dispatch_5 = {
            'x_data':       assumptions_matrix, 
            'y_data':       power_capacity_matrix.T,
            'ax':           ax5,
            'x_label':      'Time (hour in the year)',
            'y_label':      'Power generation capacity (GW)',
            'legend':       legend_list,
            'line_width':    2,
            'grid_option':   0,
            }        
            
    ax5.set_xscale('log', nonposx='clip')
    
    func_stack_plot(inputs_dispatch_5)
    
    pdf_all.savefig(figure5)
    #plt.close()
    
    # -------------------------------------------------------------------------
    
    # Figure 6 Power generation dispatch mix
    
    legend_list = sorted(component_index_dispatch.keys(), key=lambda x: x[1])
    
    figure6 = plt.figure(figsize=figsize_oneplot)
    ax6 = figure6.add_subplot(111)
    
    inputs_dispatch_6 = {
            'x_data':        assumptions_matrix, 
            'y_data':        power_dispatch_matrix.T / np.sum(demand),
            'ax':            ax6,
            'x_label':       'Time (hour in the year)',
            'y_label':       'Power generation (share of demand)',
            'legend':        legend_list,
            'line_width':    2,
            'grid_option':   0,
            }        
            
    ax6.set_xscale('log', nonposx='clip')
    
    func_stack_plot(inputs_dispatch_6)
    
    pdf_all.savefig(figure6)
    #plt.close()
    
    # -------------------------------------------------------------------------
    
    # Figure 7 Cost share - power generation
    
    legend_list = sorted(component_index_dispatch.keys(), key=lambda x: x[1])
    
    figure7 = plt.figure(figsize=figsize_oneplot)
    ax7 = figure7.add_subplot(111)
    
    inputs_dispatch_7 = {
            'x_data':        assumptions_matrix, 
            'y_data':        cost_power_matrix.T,
            'ax':            ax7,
            'x_label':       'Time (hour in the year)',
            'y_label':       'Cost contributions ($/kWh)',
            'legend':        legend_list,
            'line_width':    2,
            'grid_option':   0,
            }        
            
    ax7.set_xscale('log', nonposx='clip')
    # ax7.set_yscale('log', nonposx='clip')
    
    ax7.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
    
    func_stack_plot(inputs_dispatch_7)
    
    pdf_all.savefig(figure7)
    #plt.close()
    
    # -------------------------------------------------------------------------
    
    # Figure 8 Cost share - 'every type'
    
    legend_list = sorted(component_index_dispatch.keys(), key=lambda x: x[1])
    legend_list.append('storage')
    legend_list.append('unmet demand')
    legend_list.append('curtailment')
    
    figure8 = plt.figure(figsize=figsize_oneplot)
    ax8 = figure8.add_subplot(111)
    
    inputs_dispatch_8 = {
            'x_data':        assumptions_matrix, 
            'y_data':        cost_everything_matrix.T,
            'ax':            ax8,
            'x_label':       'Time (hour in the year)',
            'y_label':       'Cost contributions ($/kWh)',
            'legend':        legend_list,
            'line_width':    2,
            'grid_option':   0,
            }        
            
    ax8.set_xscale('log', nonposx='clip')
    # ax8.set_yscale('log', nonposx='clip')
    
    func_stack_plot(inputs_dispatch_8)
    
    pdf_all.savefig(figure8)
    #plt.close()
    
    # -------------------------------------------------------------------------
    


#%%
# -----------------------------------------------------------------------------
# func_optimization_results_system_results_Nscenarios()
#
# Function: generate 'representative' results (figures) for a set of optimization 
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
    pdf_all = input_data['pdf_all']
    x_label = input_data['x_label']

    # -------------------------------------------------------------------------

    # load the data from scenario to get 'component_index_dispatch'
    
    temp_dict = func_load_optimization_results(optimization_results_file_path_list[0])
    model_inputs = temp_dict['model_inputs']
    model_results = temp_dict['model_results']
    
    component_index_dispatch = model_inputs['component_index_dispatch']
    
    # -------------------------------------------------------------------------
    
    # prepare for the loop
    
    # 9 variables (matrix form) to be assembled
    
    storage_capacity_matrix = np.zeros([len(scenario_list_number)])
    storage_dispatch_matrix = np.zeros([len(scenario_list_number)])
    storage_cycle_matrix = np.zeros([len(scenario_list_number)])
    storage_investment_matrix = np.zeros([len(scenario_list_number)])
    
    power_capacity_matrix = np.zeros([len(component_index_dispatch), len(scenario_list_number)])
    power_dispatch_matrix = np.zeros([len(component_index_dispatch), len(scenario_list_number)])
    cost_power_matrix = np.zeros([len(component_index_dispatch), len(scenario_list_number)])
    cost_everything_matrix = np.zeros([len(component_index_dispatch)+3, len(scenario_list_number)])
    
    optimum_cost_matrix = np.zeros([len(scenario_list_number)])
    
    # ----------------------
    
    # loop to extract and 'combine' optimization results
    
    for scenario_idx in range(len(scenario_list_number)):
    
        # actually load the data
    
        # f = open(optimization_results_file_path_list[scenario_idx], 'rb')
        
        temp_dict = func_load_optimization_results(optimization_results_file_path_list[scenario_idx])
        model_inputs = temp_dict['model_inputs']
        model_results = temp_dict['model_results']
            
        # ---------------------------------------------------------------------
        
        # Energy storage
    
        storage_dispatch_matrix[scenario_idx] = (
            sum(model_results['dispatch_storage'])
            )
        
        storage_capacity_matrix[scenario_idx] = (
            model_results['capacity_storage']
            )
    
        storage_cycle_matrix[scenario_idx] = (
            sum(model_results['dispatch_storage']) /
            model_results['capacity_storage']
            )
        
        storage_investment_matrix[scenario_idx] = (
            model_results['capacity_storage'] * model_inputs['capital_cost_storage']
            )
    
        # ---------------------------------------------------------------------
    
        # Power generation
    
        power_capacity_matrix[:,scenario_idx] = \
            np.reshape(model_results['capacity_power'], -1)
    
        power_dispatch_matrix[:,scenario_idx] = \
            np.reshape(np.sum(model_results['results_matrix_dispatch'], axis=1), -1)
    
        power_dispatch_total = \
            np.sum(model_results['results_matrix_dispatch'], axis = 1)
    
        cost_power_matrix[:,scenario_idx] = (
            ((power_dispatch_total * model_inputs['variable_cost_power'] +
             model_results['capacity_power'] * model_inputs['fixed_cost_power'])
            / np.sum(model_inputs['demand'])))
    
        # ---------------------------------------------------------------------
    
        # Cost breakdown by 'everything' (every type)
        # -- power generation technologies, storage, unmet demand, curtailment
    
        storage_dispatch_total = np.sum(model_results['dispatch_storage'])
        storage_charge_total = np.sum(model_results['results_matrix_demand']) 
        
        cost_everything_matrix[0:len(component_index_dispatch),scenario_idx] = (
            cost_power_matrix[:,scenario_idx])
    
        cost_everything_matrix[len(component_index_dispatch)+0,scenario_idx] = (
            (storage_dispatch_total * model_inputs['variable_cost_storage'] +
             storage_charge_total * model_inputs['variable_cost_storage'] +
             model_results['capacity_storage'] * model_inputs['fixed_cost_storage'])
             / np.sum(model_inputs['demand']))
    
        cost_everything_matrix[len(component_index_dispatch)+1,scenario_idx] = (
            np.sum(model_results['unmet_demand']) * model_inputs['unmet_demand_cost']
            / np.sum(model_inputs['demand']))
        
        # ---------------------------------------------------------------------
        
        # Optimal system cost
        
        optimum_cost_matrix[scenario_idx] = (
            model_results['optimum'] / np.sum(model_inputs['demand']))
    
    # -------------------------------------------------------------------------
    # Graphics
    
    # Graphics settings
    
    input_data = {
            'component_index_dispatch':             component_index_dispatch,
            'DEMAND_SERIES':                       model_inputs['demand'],
            'assumptions_matrix':           np.array(scenario_list_number),
            'storage_dispatch_matrix':     storage_dispatch_matrix,
            'storage_capacity_matrix':      storage_capacity_matrix,
            'storage_cycle_matrix':         storage_cycle_matrix,
            'storage_investment_matrix':    storage_investment_matrix,
            'power_capacity_matrix':        power_capacity_matrix,
            'power_dispatch_matrix':        power_dispatch_matrix,
            'cost_power_matrix':            cost_power_matrix,
            'cost_everything_matrix':       cost_everything_matrix,
            'pdf_all':                      input_data['pdf_all'],
            'x_label':                      x_label
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
#       which_technology_to_all
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
    
    which_technology_to_all = input_data['which_technology_to_all']
    
    pdf_all = input_data['pdf_all']
    title_text = input_data['title_text']
    legend_list = input_data['legend_list']

    # -------------------------------------------------------------------------

    # load the data from scenario to get 'component_index_dispatch'
    
    temp_dict = func_load_optimization_results(optimization_results_file_path_list[0])
    model_inputs = temp_dict['model_inputs']
    model_results = temp_dict['model_results']
    
    component_index_dispatch = model_inputs['component_index_dispatch']
    num_time_periods = len(model_inputs['demand'])
    
    # -------------------------------------------------------------------------
    
    results_matrix_dispatch = \
        np.zeros([num_time_periods, len(scenario_list_number)])
    
    for scenario_idx in range(len(scenario_list_number)):

        # actually load the data
            
        temp_dict = func_load_optimization_results(optimization_results_file_path_list[scenario_idx])
        model_inputs = temp_dict['model_inputs']
        model_results = temp_dict['model_results']
        
        if which_technology_to_all == 'storage':
            dispatch_results = model_results['dispatch_storage']
            results_matrix_dispatch[:, scenario_idx] = \
                np.reshape(dispatch_results, -1)
        else:
            dispatch_results = model_results['results_matrix_dispatch']
            results_matrix_dispatch[:, scenario_idx] = \
                np.reshape(dispatch_results[component_index_dispatch[which_technology_to_all], :], -1)
    
    # -------------------------------------------------------------------------
    
    # Graphics
    
    input_data_1 = {
            'DEMAND_SERIES':                       model_inputs['demand'],
            'results_matrix_dispatch':      results_matrix_dispatch,
            'directory_output':             directory_output,
            'title_text':                   title_text,
            'legend_list':                  legend_list,
            'pdf_all':                      input_data['pdf_all']
            }
    
    # call the function
    
    func_graphics_dispatch_var_Nscenarios(input_data_1)    
                
#=======================>>>> COMPUTE CURTAILMENT <<<<======================
#
#  Result of compute_curtailment is a dictionary of vectors where the keys
#  are component (i.e., technology) names
#
#
def compute_curtailment(case_dic, result_dic):
    
    system_components = case_dic['SYSTEM_COMPONENTS']        
    curtailment_dic = {}
    
    for component in system_components:
        
        if component == 'WIND':
            wind_series = np.array(case_dic['WIND_SERIES'])
            capacity_wind = np.array(result_dic['CAPACITY_WIND'])
            dispatch_wind = np.array(result_dic['DISPATCH_WIND'])
            curtailment_dic['WIND'] = wind_series * capacity_wind - dispatch_wind
        
        if component == 'WIND2':
            wind2_series = np.array(case_dic['WIND2_SERIES'])
            capacity_wind2 = np.array(result_dic['CAPACITY_WIND2'])
            dispatch_wind2 = np.array(result_dic['DISPATCH_WIND2'])
            curtailment_dic['WIND2'] = wind2_series * capacity_wind2 - dispatch_wind2
        
        elif component == 'SOLAR':
            solar_series = np.array(case_dic['SOLAR_SERIES'])
            capacity_solar = np.array(result_dic['CAPACITY_SOLAR'])
            dispatch_solar = np.array(result_dic['DISPATCH_SOLAR'])
            curtailment_dic['SOLAR'] = solar_series * capacity_solar - dispatch_solar
        
        elif component == 'SOLAR2':
            solar2_series = np.array(case_dic['SOLAR2_SERIES'])
            capacity_solar2 = np.array(result_dic['CAPACITY_SOLAR2'])
            dispatch_solar2 = np.array(result_dic['DISPATCH_SOLAR2'])
            curtailment_dic['SOLAR2'] = solar2_series * capacity_solar2 - dispatch_solar2
            
        elif component == 'NATGAS':
            curtailment_dic['NATGAS'] = np.array(result_dic['CAPACITY_NATGAS']) - np.array(result_dic['DISPATCH_NATGAS'])
            
        elif component == 'NATGAS_CCS':
            curtailment_dic['NATGAS_CCS'] = np.array(result_dic['CAPACITY_NATGAS_CCS']) - np.array(result_dic['DISPATCH_NATGAS_CCS'])
            
        elif component == 'NUCLEAR':
            curtailment_dic['NUCLEAR'] = np.array(result_dic['CAPACITY_NUCLEAR']) - np.array(result_dic['DISPATCH_NUCLEAR'])
        
    return curtailment_dic
                
                
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
