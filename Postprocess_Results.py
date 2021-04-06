"""
Post-processing
Created by Lei at 27 March, 2018
"""

# -----------------------------------------------------------------------------

import os,sys
import pickle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import datetime
plt.ioff()

#from matplotlib import style
#style.use('ggplot')

color_natgas  = {0:"red",    1:"tomato"}
color_solar   = {0:"orange", 1:"wheat"}
color_wind    = {0:"blue",   1:"skyblue"}
color_nuclear = {0:"green",  1:"limegreen"}
color_storage = {0:"m",      1:"orchid"}

#===============================================================================
#================================================= DEFINITION SECTION ==========
#===============================================================================

def unpickle_raw_results(global_dic):
    
    verbose = global_dic["VERBOSE"]
    file_path_name = global_dic["OUTPUT_PATH"] + "/" + global_dic["GLOBAL_NAME"] + "/" + global_dic["GLOBAL_NAME"] + ".pickle"
    
    with open(file_path_name, 'rb') as db:
       global_dic, case_dic_list, result_list = pickle.load (db)
    if verbose:
        print ('data unpickled from '+file_path_name)
    return global_dic, case_dic_list, result_list 

def get_dimension_info(case_dic_list):
    FIXED_COST_NATGAS = []
    FIXED_COST_SOLAR = []
    FIXED_COST_WIND = []
    FIXED_COST_NUCLEAR = []
    FIXED_COST_STORAGE = []
    
    VAR_COST_NATGAS = []
    VAR_COST_SOLAR = []
    VAR_COST_WIND = []
    VAR_COST_NUCLEAR = []
    DECAY_RATE_STORAGE = []
    
    CHARGING_TIME_STORAGE = []
    
    num_scenarios = len(case_dic_list)
    for idx in range(num_scenarios):
        FIXED_COST_NATGAS  = np.r_[FIXED_COST_NATGAS,  case_dic_list[idx]['FIXED_COST_NATGAS']]
        FIXED_COST_SOLAR   = np.r_[FIXED_COST_SOLAR,   case_dic_list[idx]['FIXED_COST_SOLAR']]
        FIXED_COST_WIND    = np.r_[FIXED_COST_WIND,    case_dic_list[idx]['FIXED_COST_WIND']]
        FIXED_COST_NUCLEAR = np.r_[FIXED_COST_NUCLEAR, case_dic_list[idx]['FIXED_COST_NUCLEAR']]
        FIXED_COST_STORAGE = np.r_[FIXED_COST_STORAGE, case_dic_list[idx]['FIXED_COST_STORAGE']]
    
        VAR_COST_NATGAS  = np.r_[VAR_COST_NATGAS,  case_dic_list[idx]['VAR_COST_NATGAS']]
        VAR_COST_SOLAR   = np.r_[VAR_COST_SOLAR,   case_dic_list[idx]['VAR_COST_SOLAR']]
        VAR_COST_WIND    = np.r_[VAR_COST_WIND,    case_dic_list[idx]['VAR_COST_WIND']]
        VAR_COST_NUCLEAR = np.r_[VAR_COST_NUCLEAR, case_dic_list[idx]['VAR_COST_NUCLEAR']]
        DECAY_RATE_STORAGE = np.r_[DECAY_RATE_STORAGE, case_dic_list[idx]['DECAY_RATE_STORAGE']]
        
        CHARGING_TIME_STORAGE = np.r_[CHARGING_TIME_STORAGE, case_dic_list[idx]['CHARGING_TIME_STORAGE']]
        
    FIXED_COST_NATGAS_list  = np.unique(FIXED_COST_NATGAS)
    FIXED_COST_SOLAR_list   = np.unique(FIXED_COST_SOLAR)
    FIXED_COST_WIND_list    = np.unique(FIXED_COST_WIND)
    FIXED_COST_NUCLEAR_list = np.unique(FIXED_COST_NUCLEAR)
    FIXED_COST_STORAGE_list = np.unique(FIXED_COST_STORAGE)
    
    VAR_COST_NATGAS_list  = np.unique(VAR_COST_NATGAS)
    VAR_COST_SOLAR_list   = np.unique(VAR_COST_SOLAR)
    VAR_COST_WIND_list    = np.unique(VAR_COST_WIND)
    VAR_COST_NUCLEAR_list = np.unique(VAR_COST_NUCLEAR)
    DECAY_RATE_STORAGE_list = np.unique(DECAY_RATE_STORAGE)
    
    CHARGING_TIME_STORAGE_list = np.unique(CHARGING_TIME_STORAGE)
    
    cost_list = {'FIXED_COST_NATGAS':FIXED_COST_NATGAS_list,
                 'FIXED_COST_SOLAR':FIXED_COST_SOLAR_list,
                 'FIXED_COST_WIND':FIXED_COST_WIND_list,
                 'FIXED_COST_NUCLEAR':FIXED_COST_NUCLEAR_list,
                 'FIXED_COST_STORAGE':FIXED_COST_STORAGE_list,
                 'VAR_COST_NATGAS':VAR_COST_NATGAS_list,
                 'VAR_COST_SOLAR':VAR_COST_SOLAR_list,
                 'VAR_COST_WIND':VAR_COST_WIND_list,
                 'VAR_COST_NUCLEAR':VAR_COST_NUCLEAR_list,
                 'DECAY_RATE_STORAGE':DECAY_RATE_STORAGE_list,
                 'CHARGING_TIME_STORAGE':CHARGING_TIME_STORAGE_list}
    var_list = ['FIXED_COST_NATGAS',
                'FIXED_COST_SOLAR',
                'FIXED_COST_WIND',
                'FIXED_COST_NUCLEAR',
                'FIXED_COST_STORAGE',
                'VAR_COST_NATGAS',
                'VAR_COST_SOLAR',
                'VAR_COST_WIND',
                'VAR_COST_NUCLEAR',
                'DECAY_RATE_STORAGE',
                'CHARGING_TIME_STORAGE']
    
    return cost_list, var_list

#------------------------------------------------------------------------
def prepare_scalar_variables (global_dic, case_dic_list, result_list ):
    
    #verbose = global_dic['VERBOSE']
    num_scenarios    = len(case_dic_list)
    res = {}

    # put all scenarios data in one list res;
    for idx in range(num_scenarios):
        tmp = {}
        
        tmp['DEMAND']         = np.array(np.squeeze(case_dic_list[idx]['DEMAND_SERIES'])) #/ num_time_periods
        tmp['SOLAR_CAPACITY'] = np.array(np.squeeze(case_dic_list[idx]['SOLAR_SERIES']))  #/ num_time_periods
        tmp['WIND_CAPACITY']  = np.array(np.squeeze(case_dic_list[idx]['WIND_SERIES']))   #/ num_time_periods
        tmp['FIXED_COST_NATGAS']  = np.array(np.squeeze(case_dic_list[idx]['FIXED_COST_NATGAS']))
        tmp['FIXED_COST_SOLAR']   = np.array(np.squeeze(case_dic_list[idx]['FIXED_COST_SOLAR']))
        tmp['FIXED_COST_WIND']    = np.array(np.squeeze(case_dic_list[idx]['FIXED_COST_WIND']))
        tmp['FIXED_COST_NUCLEAR'] = np.array(np.squeeze(case_dic_list[idx]['FIXED_COST_NUCLEAR']))
        tmp['FIXED_COST_STORAGE'] = np.array(np.squeeze(case_dic_list[idx]['FIXED_COST_STORAGE']))
        tmp['VAR_COST_NATGAS']        = np.array(np.squeeze(case_dic_list[idx]['VAR_COST_NATGAS']))
        tmp['VAR_COST_SOLAR']         = np.array(np.squeeze(case_dic_list[idx]['VAR_COST_SOLAR']))
        tmp['VAR_COST_WIND']          = np.array(np.squeeze(case_dic_list[idx]['VAR_COST_WIND']))
        tmp['VAR_COST_NUCLEAR']       = np.array(np.squeeze(case_dic_list[idx]['VAR_COST_NUCLEAR']))
        tmp['DECAY_RATE_STORAGE']       = np.array(np.squeeze(case_dic_list[idx]['DECAY_RATE_STORAGE']))
        tmp['VAR_COST_TO_STORAGE']    = np.array(np.squeeze(case_dic_list[idx]['VAR_COST_TO_STORAGE']))
        tmp['VAR_COST_FROM_STORAGE']  = np.array(np.squeeze(case_dic_list[idx]['VAR_COST_FROM_STORAGE']))
        tmp['VAR_COST_UNMET_DEMAND']  = np.array(np.squeeze(case_dic_list[idx]['VAR_COST_UNMET_DEMAND']))
        tmp['CAPACITY_NATGAS']  = np.array(np.squeeze(result_list[idx]['CAPACITY_NATGAS']))
        tmp['CAPACITY_SOLAR']   = np.array(np.squeeze(result_list[idx]['CAPACITY_SOLAR']))
        tmp['CAPACITY_WIND']    = np.array(np.squeeze(result_list[idx]['CAPACITY_WIND']))
        tmp['CAPACITY_NUCLEAR'] = np.array(np.squeeze(result_list[idx]['CAPACITY_NUCLEAR']))
        tmp['CAPACITY_STORAGE'] = np.array(np.squeeze(result_list[idx]['CAPACITY_STORAGE']))
        tmp['DISPATCH_NATGAS']        = np.array(np.squeeze(result_list[idx]['DISPATCH_NATGAS']))       #/ num_time_periods
        tmp['DISPATCH_SOLAR']         = np.array(np.squeeze(result_list[idx]['DISPATCH_SOLAR']))        #/ num_time_periods
        tmp['DISPATCH_WIND']          = np.array(np.squeeze(result_list[idx]['DISPATCH_WIND']))         #/ num_time_periods
        tmp['DISPATCH_NUCLEAR']       = np.array(np.squeeze(result_list[idx]['DISPATCH_NUCLEAR']))      #/ num_time_periods
        tmp['DISPATCH_TO_STORAGE']    = np.array(np.squeeze(result_list[idx]['DISPATCH_TO_STORAGE']))   #/ num_time_periods
        tmp['DISPATCH_FROM_STORAGE']  = np.array(np.squeeze(result_list[idx]['DISPATCH_FROM_STORAGE'])) #/ num_time_periods
        tmp['DISPATCH_UNMET_DEMAND']  = np.array(np.squeeze(result_list[idx]['DISPATCH_UNMET_DEMAND'])) #/ num_time_periods
        tmp['DISPATCH_CURTAILMENT']   = np.array(np.squeeze(result_list[idx]['DISPATCH_CURTAILMENT']))  #/ num_time_periods
        tmp['ENERGY_STORAGE']         = np.array(np.squeeze(result_list[idx]['ENERGY_STORAGE']))        #/ num_time_periods
        tmp['SYSTEM_COST']    = np.array(np.squeeze(result_list[idx]['SYSTEM_COST']))  
        tmp['CHARGING_EFFICIENCY_STORAGE']    = np.array(np.squeeze(case_dic_list[idx]['CHARGING_EFFICIENCY_STORAGE']))
        tmp['CHARGING_TIME_STORAGE']    = np.array(np.squeeze(case_dic_list[idx]['CHARGING_TIME_STORAGE']))
        tmp['CASE_NAME'] = np.array(np.squeeze(case_dic_list[idx]['CASE_NAME']))

        res[idx] = tmp
    return res

#------------------------------------------------------------------------------
#------------------------------------------------ Plotting function -----------
#------------------------------------------------------------------------------   

def get_multicases_results(res, num_case, var, *avg_option):    
    x = []
    for idx in range(num_case):
        tmp_var = res[idx][var]
        x.append(np.array(tmp_var))
    if avg_option:
        if num_case ==1:
            x = x[0]
        y = avg_series(x, 
                       num_case,
                       avg_option[0], 
                       avg_option[1], 
                       avg_option[2],
                       avg_option[3])
        return y
    else:
        return np.array(x)

def avg_series(var, num_case, beg_step, end_step, nstep, num_return):
    x = []
    y = []
    if num_case > 1:
        for idx in range(num_case):
            hor_mean = np.mean(var[idx][beg_step-1:end_step].reshape(-1,nstep),axis=1)
            ver_mean = np.mean(var[idx][beg_step-1:end_step].reshape(-1,nstep),axis=0)
            x.append(hor_mean)
            y.append(ver_mean)
    else:
        hor_mean = np.mean(var[beg_step-1:end_step].reshape(-1,nstep),axis=1)
        ver_mean = np.mean(var[beg_step-1:end_step].reshape(-1,nstep),axis=0)
        x.append(hor_mean)
        y.append(ver_mean)
    if num_return == 1:
        return np.array(x)
    if num_return == 2:
        return np.array(y)

def cal_cost(fix_cost, capacity,
             var_cost, dispatch,
             num_case, num_time_periods,
             *battery_dispatch):
    
    cost_fix = np.array(fix_cost * capacity)
    
    cost_var = np.zeros(num_case)
    for idx in range(num_case):
        if battery_dispatch:
            cost_var_tmp = np.array(battery_dispatch[0][idx]) * np.sum(np.array(battery_dispatch[1][idx])) +\
                           np.array(battery_dispatch[2][idx]) * np.sum(np.array(battery_dispatch[3][idx]))
        else:
            cost_var_tmp = var_cost[idx] * np.sum(dispatch[idx]) 
        cost_var[idx] = cost_var_tmp
        
    cost_tot = cost_fix + cost_var
    return cost_fix, cost_var, cost_tot


# --------- stack plot1
def plot_multi_panels1(ax,case):
    ax.grid(True, color='k', linestyle='--', alpha=0.2)
    ax.set_axis_bgcolor('white')
    
    ax.stackplot(case[0], case[1], colors=case[4], baseline = 'zero', alpha = 0.5)
    ax.stackplot(case[0], case[2], labels=case[3], colors=case[4],  baseline = 'zero', alpha = 0.5)
    if len(case) == 7:
        ax.plot(case[0], np.array(case[6][0]),c='r', linewidth = '1', linestyle='-', label='charge')
        ax.plot(case[0], np.array(case[6][1]),c='g', linewidth = '1', linestyle='-', label='dispatch')
        ax.fill_between(case[0], np.array(case[6][0]), np.array(case[6][1]), facecolor='black', alpha=0.2, label='energy loss')
    y_line = np.zeros(case[2].shape[1])
    for idx in range(int(case[2].shape[0])):
        y_line = y_line + case[2][idx]
        ax.plot(case[0], y_line, c='k', linewidth = 0.5)
    
    ax.set_xlim(case[0][-1],case[0][0])
    for label in ax.xaxis.get_ticklabels():
        label.set_rotation(45)
    ax.set_xlabel(case[5]["xlabel"],fontsize=9)
    ax.set_title(case[5]["title"],fontsize=9)   
    ax.spines['right'].set_color('black')
    ax.spines['top'].set_color('black')
    ax.spines['left'].set_color('black')
    ax.spines['bottom'].set_color('black')
    
    leg = ax.legend(loc='center left', ncol=1, 
                    bbox_to_anchor=(1, 0.5), prop={'size': 5})
    leg.get_frame().set_alpha(0.4)
    
def plot_stack_multi1(case1,case2,case3,case4, case_name):
    fig, axes = plt.subplots(2,2)
    fig.subplots_adjust(top=1, left=0.0, right=1, hspace=0.5, wspace=0.35)
    ((ax1, ax2), (ax3, ax4)) = axes
    
    plot_multi_panels1(ax1,case1)
    plot_multi_panels1(ax2,case2)
    plot_multi_panels1(ax3,case3)
    plot_multi_panels1(ax4,case4)
    plt.setp(ax1.get_xticklabels(), size=7)
    plt.setp(ax2.get_xticklabels(), size=7)
    plt.setp(ax3.get_xticklabels(), size=7)
    plt.setp(ax4.get_xticklabels(), size=7)
    ax1.set_xlabel('')
    ax2.set_xlabel('')
    plt.setp(ax1.get_yticklabels(), size=7)
    plt.setp(ax2.get_yticklabels(), size=7)
    plt.setp(ax3.get_yticklabels(), size=7)
    plt.setp(ax4.get_yticklabels(), size=7)

    return fig
    plt.close(fig)

def stack_plot1(
        res,
        num_case,
        case_name,
        multipanel,
        var_dimension_list):
    
    # --- get Raw Data ---
    num_time_periods = len(res[0]['DEMAND'])

    solar_series      = get_multicases_results(res, num_case , 'SOLAR_CAPACITY')   / num_time_periods
    wind_series       = get_multicases_results(res, num_case , 'WIND_CAPACITY')    / num_time_periods
    var_dimension = get_multicases_results(res, num_case, var_dimension_list[0])
    CAPACITY_NATGAS   = get_multicases_results(res, num_case , 'CAPACITY_NATGAS')
    CAPACITY_SOLAR    = get_multicases_results(res, num_case , 'CAPACITY_SOLAR')
    CAPACITY_WIND     = get_multicases_results(res, num_case , 'CAPACITY_WIND')
    CAPACITY_NUCLEAR  = get_multicases_results(res, num_case , 'CAPACITY_NUCLEAR')
    CAPACITY_STORAGE  = get_multicases_results(res, num_case , 'CAPACITY_STORAGE')    
    FIXED_COST_NATGAS  = get_multicases_results(res, num_case, 'FIXED_COST_NATGAS')
    FIXED_COST_SOLAR   = get_multicases_results(res, num_case, 'FIXED_COST_SOLAR')
    FIXED_COST_WIND    = get_multicases_results(res, num_case, 'FIXED_COST_WIND')
    FIXED_COST_NUCLEAR = get_multicases_results(res, num_case, 'FIXED_COST_NUCLEAR')
    FIXED_COST_STORAGE = get_multicases_results(res, num_case, 'FIXED_COST_STORAGE')    
    VAR_COST_NATGAS  = get_multicases_results(res, num_case, 'VAR_COST_NATGAS')
    VAR_COST_SOLAR   = get_multicases_results(res, num_case, 'VAR_COST_SOLAR')
    VAR_COST_WIND    = get_multicases_results(res, num_case, 'VAR_COST_WIND')
    VAR_COST_NUCLEAR = get_multicases_results(res, num_case, 'VAR_COST_NUCLEAR')
    DECAY_RATE_STORAGE    = get_multicases_results(res, num_case, 'DECAY_RATE_STORAGE') 
    VAR_COST_TO_STORAGE   = get_multicases_results(res, num_case, 'VAR_COST_TO_STORAGE') 
    VAR_COST_FROM_STORAGE = get_multicases_results(res, num_case, 'VAR_COST_FROM_STORAGE')     
    DISPATCH_NATGAS       = get_multicases_results(res, num_case, 'DISPATCH_NATGAS')        / num_time_periods
    DISPATCH_SOLAR        = get_multicases_results(res, num_case, 'DISPATCH_SOLAR')         / num_time_periods
    DISPATCH_WIND         = get_multicases_results(res, num_case, 'DISPATCH_WIND')          / num_time_periods
    DISPATCH_NUCLEAR      = get_multicases_results(res, num_case, 'DISPATCH_NUCLEAR')       / num_time_periods
    DISPATCH_TO_STORAGE   = get_multicases_results(res, num_case, 'DISPATCH_TO_STORAGE')    / num_time_periods
    DISPATCH_FROM_STORAGE = get_multicases_results(res, num_case, 'DISPATCH_FROM_STORAGE')  / num_time_periods
    ENERGY_STORAGE        = get_multicases_results(res, num_case, 'ENERGY_STORAGE')         / num_time_periods

    # --- global setting ---
    order_list = FIXED_COST_NUCLEAR.argsort()  
    xaxis = var_dimension[order_list]
    
    # -plot1: capacity-
    yaxis_capacity_ne = np.zeros(num_case)
    yaxis_capacity_po = np.vstack([CAPACITY_NATGAS[order_list], 
                                   CAPACITY_SOLAR[order_list], 
                                   CAPACITY_WIND[order_list],
                                   CAPACITY_NUCLEAR[order_list],
                                   ]) #CAPACITY_STORAGE[order_list]
    labels_capacity = ["natgas", "solar", "wind", "nuclear", "storage"]
    colors_capacity = [color_natgas[1], color_solar[1], color_wind[1], color_nuclear[1], color_storage[1]]
    info_capacity = {
            "title": "Capacity mix\n(kW)",
            "xlabel": var_dimension_list[0],
            "ylabel": "Capacity (kW)",
            "fig_name": "Capacity_mix"}    

    # -plot2: total dispatch 
    dispatch_tot_natgas  = np.sum(DISPATCH_NATGAS,axis=1)
    dispatch_tot_solar   = np.sum(DISPATCH_SOLAR,axis=1)
    dispatch_tot_wind    = np.sum(DISPATCH_WIND,axis=1)
    dispatch_tot_nuclear = np.sum(DISPATCH_NUCLEAR,axis=1)
    dispatch_tot_to_storage   = np.sum(DISPATCH_TO_STORAGE,axis=1)
    dispatch_tot_from_storage = np.sum(DISPATCH_FROM_STORAGE,axis=1)
    
    curtail_tot_natgas  = CAPACITY_NATGAS - dispatch_tot_natgas
    curtail_tot_solar   = CAPACITY_SOLAR * np.sum(solar_series,axis=1) - dispatch_tot_solar
    curtail_tot_wind    = CAPACITY_WIND  * np.sum(wind_series,axis=1)  - dispatch_tot_wind
    curtail_tot_nuclear = CAPACITY_NUCLEAR - dispatch_tot_nuclear    
            
    yaxis_dispatch_ne = np.vstack([curtail_tot_natgas[order_list]   * (-1),
                                   curtail_tot_solar[order_list]    * (-1),
                                   curtail_tot_wind[order_list]     * (-1),
                                   curtail_tot_nuclear[order_list]  * (-1)
                                   ])        
    yaxis_dispatch_po = np.vstack([dispatch_tot_natgas[order_list], 
                                   dispatch_tot_solar[order_list], 
                                   dispatch_tot_wind[order_list],
                                   dispatch_tot_nuclear[order_list]])
    battery_charge = np.array([dispatch_tot_to_storage, dispatch_tot_from_storage])
    
    labels_dispatch = ["natgas", "solar", "wind", "nuclear"]
    colors_dispatch = [color_natgas[1], color_solar[1], color_wind[1], color_nuclear[1]]    
    info_dispatch = {
            "title": "Total dispatched energy\n(kWh)",
            "xlabel": var_dimension_list[0],
            "ylabel": "Total dispatch (KWh)",
            "fig_name": "Total_dispatch_mix"}   
    
    # -plot3: SYSTEM_COST
    cost_natgas  = cal_cost(FIXED_COST_NATGAS,  CAPACITY_NATGAS,  VAR_COST_NATGAS,  DISPATCH_NATGAS,  num_case, num_time_periods)
    cost_solar   = cal_cost(FIXED_COST_SOLAR,   CAPACITY_SOLAR,   VAR_COST_SOLAR,   DISPATCH_SOLAR,   num_case, num_time_periods)
    cost_wind    = cal_cost(FIXED_COST_WIND,    CAPACITY_WIND,    VAR_COST_WIND,    DISPATCH_WIND,    num_case, num_time_periods)
    cost_nuclear = cal_cost(FIXED_COST_NUCLEAR, CAPACITY_NUCLEAR, VAR_COST_NUCLEAR, DISPATCH_NUCLEAR, num_case, num_time_periods)
    cost_storage = cal_cost(FIXED_COST_STORAGE, CAPACITY_STORAGE, DECAY_RATE_STORAGE,    ENERGY_STORAGE   ,num_case, num_time_periods, 
                            VAR_COST_TO_STORAGE,  DISPATCH_TO_STORAGE,
                            VAR_COST_FROM_STORAGE,DISPATCH_FROM_STORAGE)  # now dispatch_to/from is free    
    
    yaxis_cost_ne = np.zeros(num_case)
    yaxis_cost1_po = np.vstack([cost_natgas[2][order_list], 
                                cost_solar[2][order_list], 
                                cost_wind[2][order_list],
                                cost_nuclear[2][order_list],
                                cost_storage[2][order_list]])
    labels_cost1 = ["natgas", "solar", "wind", "nuclear", "storage"]
    colors_cost1 = [color_natgas[1], color_solar[1], color_wind[1], color_nuclear[1], color_storage[1]]
    info_cost1 = {
            "title": "System cost\n($/h/kW)",
            "xlabel": var_dimension_list[0],
            "ylabel": "System cost ($/kW/h)",
            "fig_name": "System_cost_total"} 
    
    # -plot4: SYSTEM_COST
    yaxis_cost2_po = np.vstack([cost_natgas[0][order_list],
                                cost_natgas[1][order_list],
                                cost_solar[0][order_list],
                                cost_solar[1][order_list],
                                cost_wind[0][order_list],
                                cost_wind[1][order_list],
                                cost_nuclear[0][order_list],
                                cost_nuclear[1][order_list],
                                cost_storage[0][order_list],
                                cost_storage[1][order_list]]) 
    labels_cost2 = ["natgas_fix",  'natgas_var', 
                    "solar_fix",   'solar_var', 
                    "wind_fix",    'wind_var', 
                    "nuclear_fix", 'nuclear_var', 
                    "storage_fix", 'storage_var',
                    ]
    colors_cost2 = [color_natgas[1],  color_natgas[0],
                    color_solar[1],   color_solar[0], 
                    color_wind[1],    color_wind[0],
                    color_nuclear[1], color_nuclear[0], 
                    color_storage[1], color_storage[0]
                    ]
    info_cost2 = {
            "title": "System cost\n($/h/kW)",
            "xlabel": var_dimension_list[0],
            "ylabel": "System cost ($/kW/h)",
            "fig_name": "System_cost_seperate"} 
    
    plot_case1 = [xaxis, yaxis_capacity_ne, yaxis_capacity_po, labels_capacity, colors_capacity, info_capacity]
    plot_case2 = [xaxis, yaxis_dispatch_ne, yaxis_dispatch_po, labels_dispatch, colors_dispatch, info_dispatch, battery_charge] 
    plot_case3 = [xaxis, yaxis_cost_ne, yaxis_cost1_po, labels_cost1, colors_cost1, info_cost1]
    plot_case4 = [xaxis, yaxis_cost_ne, yaxis_cost2_po, labels_cost2, colors_cost2, info_cost2]   
    
    if multipanel:
        plotx = plot_stack_multi1(plot_case1, plot_case2, plot_case3, plot_case4, case_name)
    else:
        print ('please use multipanel = True!')

    return plotx




# --------- stack plot2
def plot_multi_panels2(ax,case):
    ax.grid(True, color='k', linestyle='--', alpha=0.2)
    ax.set_axis_bgcolor('white')
    
    ax.stackplot(case[0], case[1], colors=case[4], baseline = 'zero', alpha = 0.5)
    ax.stackplot(case[0], case[2], labels=case[3], colors=case[4],  baseline = 'zero', alpha = 0.5)
    ax.plot(case[0], case[5], c='k', linewidth = 1.5, linestyle = '-', label = 'DEMAND')  
    total_energy_gen = np.sum(case[2][:-1,:],axis=0)
    ax.fill_between(case[0],case[5],total_energy_gen, case[5]<total_energy_gen, alpha = 0.0)        
    
    y_line = np.zeros(case[2].shape[1])
    for idx in range(int(case[2].shape[0])):
        y_line = y_line + case[2][idx]
        ax.plot(case[0], y_line, c='grey', linewidth = 0.5)
    y_line = np.zeros(case[1].shape[1])
    for idx in range(int(case[1].shape[0])):
        y_line = y_line + case[1][idx]
        ax.plot(case[0], y_line, c='grey', linewidth = 0.5)
        
    ax.set_xlim(case[0][0],case[0][-1])
    for label in ax.xaxis.get_ticklabels():
        label.set_rotation(45)
    ax.set_xlabel(case[6]["xlabel"],fontsize=9)
    ax.set_title(case[6]["title"],fontsize=9)   
    ax.spines['right'].set_color('black')
    ax.spines['top'].set_color('black')
    ax.spines['left'].set_color('black')
    ax.spines['bottom'].set_color('black')
    
    leg = ax.legend(loc='center left', ncol=1, 
                    bbox_to_anchor=(1, 0.5), prop={'size': 5})
    leg.get_frame().set_alpha(0.4)
    
def plot_stack_multi2(case1,case2,case3, case_name):
    fig = plt.figure()
    fig.subplots_adjust(top=1, left=0.0, right=1, hspace=0.7, wspace=0.35)
    
    ax1 = plt.subplot2grid((2,2),(0,0),rowspan=1, colspan=2)
    plot_multi_panels2(ax1,case1)
    ax2 = plt.subplot2grid((2,2),(1,0),rowspan=1, colspan=1)
    plot_multi_panels2(ax2,case2)
    ax3 = plt.subplot2grid((2,2),(1,1),rowspan=1, colspan=1,sharey=ax2)
    plot_multi_panels2(ax3,case3)

    plt.setp(ax1.get_xticklabels(), size=7)
    plt.setp(ax2.get_xticklabels(), size=7)
    plt.setp(ax3.get_xticklabels(), size=7)
    plt.setp(ax1.get_yticklabels(), size=7)
    plt.setp(ax2.get_yticklabels(), size=7)
    plt.setp(ax3.get_yticklabels(), size=7)

    return fig
    plt.close(fig)
    
def stack_plot2(
        res,
        num_case,
        case_name,
        multipanel,
        var_dimension_list,
        *select_case):
    
    # --- data preparation ---
    num_time_periods = len(res[0]['DEMAND'])
    
    find_case_idx = False
    if select_case:
        var1 = get_multicases_results(res, num_case , select_case[0][0])
        var2 = get_multicases_results(res, num_case , select_case[0][1])
        print (num_case)
        for idx in range(num_case):
            if var1[idx] == select_case[1][0] and var2[idx] == select_case[1][1]:
                find_case_idx = True
                case_idx = idx
                break
        if find_case_idx: 
            print ('Find case index:', case_idx)
        else:
            print ('Error: no such case, exit')
            sys.exit(0)
        
    if find_case_idx == False:
        case_idx = 0
    
    CAPACITY_NATGAS   = get_multicases_results(res, num_case , 'CAPACITY_NATGAS')[case_idx]
    how_many_case = int(CAPACITY_NATGAS.size)
    if how_many_case > 1:
        print ("too many case for time path plot")
        sys.exit(0)
    
    num_periods_week = 24 * 7
    week1start = 1
    week2start = 183*24
    
    CASE_NAME = get_multicases_results(res, num_case , 'CASE_NAME')[case_idx]
    CAPACITY_SOLAR    = get_multicases_results(res, num_case , 'CAPACITY_SOLAR')[case_idx]
    CAPACITY_WIND     = get_multicases_results(res, num_case , 'CAPACITY_WIND')[case_idx]
    CAPACITY_NUCLEAR  = get_multicases_results(res, num_case , 'CAPACITY_NUCLEAR')[case_idx]
    demand_yr = get_multicases_results(res, num_case , 'DEMAND'   ,1,num_time_periods,24,1)[case_idx]
    demand_week1 = get_multicases_results(res, num_case , 'DEMAND'   ,week1start,week1start+num_periods_week-1,num_periods_week,2)[case_idx]
    demand_week2 = get_multicases_results(res, num_case , 'DEMAND'   ,week2start,week2start+num_periods_week-1,num_periods_week,2)[case_idx]  
    
    solar_series_yr = get_multicases_results(res, num_case , 'SOLAR_CAPACITY'   ,1,num_time_periods,24,1)[case_idx]
    solar_series_week1 = get_multicases_results(res, num_case , 'SOLAR_CAPACITY' ,week1start,week1start+num_periods_week-1,num_periods_week,2)[case_idx]
    solar_series_week2 = get_multicases_results(res, num_case , 'SOLAR_CAPACITY' ,week2start,week2start+num_periods_week-1,num_periods_week,2)[case_idx]
    
    wind_series_yr  = get_multicases_results(res, num_case , 'WIND_CAPACITY'   ,1,num_time_periods,24,1)[case_idx]
    wind_series_week1  = get_multicases_results(res, num_case , 'WIND_CAPACITY' ,week1start,week1start+num_periods_week-1,num_periods_week,2)[case_idx]
    wind_series_week2  = get_multicases_results(res, num_case , 'WIND_CAPACITY' ,week2start,week2start+num_periods_week-1,num_periods_week,2)[case_idx]
    
    DISPATCH_NATGAS_yr  = get_multicases_results(res, num_case,      'DISPATCH_NATGAS',      1,num_time_periods,24,1)[case_idx]
    DISPATCH_SOLAR_yr   = get_multicases_results(res, num_case,      'DISPATCH_SOLAR',       1,num_time_periods,24,1)[case_idx]     
    DISPATCH_WIND_yr    = get_multicases_results(res, num_case,      'DISPATCH_WIND',        1,num_time_periods,24,1)[case_idx]          
    DISPATCH_NUCLEAR_yr = get_multicases_results(res, num_case,      'DISPATCH_NUCLEAR',     1,num_time_periods,24,1)[case_idx]  
    DISPATCH_FROM_STORAGE_yr = get_multicases_results(res, num_case, 'DISPATCH_FROM_STORAGE',1,num_time_periods,24,1)[case_idx]

    DISPATCH_NATGAS_week1  = get_multicases_results(res, num_case,      'DISPATCH_NATGAS',      week1start,week1start+num_periods_week-1,num_periods_week,2)[case_idx]     
    DISPATCH_SOLAR_week1   = get_multicases_results(res, num_case,      'DISPATCH_SOLAR',       week1start,week1start+num_periods_week-1,num_periods_week,2)[case_idx]     
    DISPATCH_WIND_week1    = get_multicases_results(res, num_case,      'DISPATCH_WIND',        week1start,week1start+num_periods_week-1,num_periods_week,2)[case_idx]          
    DISPATCH_NUCLEAR_week1 = get_multicases_results(res, num_case,      'DISPATCH_NUCLEAR',     week1start,week1start+num_periods_week-1,num_periods_week,2)[case_idx]  
    DISPATCH_FROM_STORAGE_week1 = get_multicases_results(res, num_case, 'DISPATCH_FROM_STORAGE',week1start,week1start+num_periods_week-1,num_periods_week,2)[case_idx]    

    DISPATCH_NATGAS_week2  = get_multicases_results(res, num_case,      'DISPATCH_NATGAS',      week2start,week2start+num_periods_week-1,num_periods_week,2)[case_idx]     
    DISPATCH_SOLAR_week2   = get_multicases_results(res, num_case,      'DISPATCH_SOLAR',       week2start,week2start+num_periods_week-1,num_periods_week,2)[case_idx]     
    DISPATCH_WIND_week2    = get_multicases_results(res, num_case,      'DISPATCH_WIND',        week2start,week2start+num_periods_week-1,num_periods_week,2)[case_idx]          
    DISPATCH_NUCLEAR_week2 = get_multicases_results(res, num_case,      'DISPATCH_NUCLEAR',     week2start,week2start+num_periods_week-1,num_periods_week,2)[case_idx]  
    DISPATCH_FROM_STORAGE_week2 = get_multicases_results(res, num_case, 'DISPATCH_FROM_STORAGE',week2start,week2start+num_periods_week-1,num_periods_week,2)[case_idx] 

    curtail_natgas_yr  = CAPACITY_NATGAS                    - DISPATCH_NATGAS_yr
    curtail_solar_yr   = CAPACITY_SOLAR   * solar_series_yr - DISPATCH_SOLAR_yr
    curtail_wind_yr    = CAPACITY_WIND    * wind_series_yr  - DISPATCH_WIND_yr
    curtail_nuclear_yr = CAPACITY_NUCLEAR                   - DISPATCH_NUCLEAR_yr
    
    curtail_natgas_week1  = CAPACITY_NATGAS                      - DISPATCH_NATGAS_week1
    curtail_solar_week1   = CAPACITY_SOLAR   * solar_series_week1 - DISPATCH_SOLAR_week1
    curtail_wind_week1    = CAPACITY_WIND    * wind_series_week1  - DISPATCH_WIND_week1
    curtail_nuclear_week1 = CAPACITY_NUCLEAR                     - DISPATCH_NUCLEAR_week1
    
    curtail_natgas_week2  = CAPACITY_NATGAS                      - DISPATCH_NATGAS_week2
    curtail_solar_week2   = CAPACITY_SOLAR   * solar_series_week2 - DISPATCH_SOLAR_week2
    curtail_wind_week2    = CAPACITY_WIND    * wind_series_week2  - DISPATCH_WIND_week2
    curtail_nuclear_week2 = CAPACITY_NUCLEAR                     - DISPATCH_NUCLEAR_week2

    # Now plot
    xaxis_yr = np.arange(num_time_periods/24)+1
    
    yaxis_yr_ne = np.vstack([curtail_natgas_yr*(-1),
                             curtail_solar_yr*(-1),
                             curtail_wind_yr*(-1),
                             curtail_nuclear_yr*(-1),
                             curtail_natgas_yr*0.0
                             ])
        
    yaxis_yr_po = np.vstack([DISPATCH_NATGAS_yr,
                             DISPATCH_SOLAR_yr,
                             DISPATCH_WIND_yr,
                             DISPATCH_NUCLEAR_yr,
                             DISPATCH_FROM_STORAGE_yr
                             ]) 
    
    labels = ["natgas", "solar", "wind", "nuclear","dispatch"]
    colors = [color_natgas[1], color_solar[1], color_wind[1], color_nuclear[1], color_storage[1]]    
    info_yr = {
            "title": "Daily-average per hour dispatch (kWh)\n(CASE_NAME:  " + CASE_NAME + ')',
            "xlabel": "time step (day)",
            "ylabel": "",
            "fig_name": "dispatch_case"}
    
    xaxis_week = np.arange(num_periods_week)+1
    
    print (len(curtail_natgas_week1),len(curtail_solar_week1),len(curtail_wind_week1),len(curtail_nuclear_week1))
    yaxis_week1_ne = np.vstack([curtail_natgas_week1*(-1),
                               curtail_solar_week1*(-1),
                               curtail_wind_week1*(-1),
                               curtail_nuclear_week1*(-1),
                               curtail_natgas_week1*0.0
                               ])
        
    yaxis_week1_po = np.vstack([DISPATCH_NATGAS_week1,
                               DISPATCH_SOLAR_week1,
                               DISPATCH_WIND_week1,
                               DISPATCH_NUCLEAR_week1,
                               DISPATCH_FROM_STORAGE_week1
                               ]) 
    info_week1 = {
            "title": "Hourly-average per hour dispatch (kWh)\n(Day1-2)",
            "xlabel": "time step (hour)",
            "ylabel": "",
            "fig_name": "dispatch_case"}   
    
    yaxis_week2_ne = np.vstack([curtail_natgas_week2*(-1),
                               curtail_solar_week2*(-1),
                               curtail_wind_week2*(-1),
                               curtail_nuclear_week2*(-1),
                               curtail_natgas_week2*0.0
                               ])
    yaxis_week2_po = np.vstack([DISPATCH_NATGAS_week2,
                               DISPATCH_SOLAR_week2,
                               DISPATCH_WIND_week2,
                               DISPATCH_NUCLEAR_week2,
                               DISPATCH_FROM_STORAGE_week2
                               ]) 
    info_week2 = {
            "title": "Hourly-average per hour dispatch (kWh)\n(Day11-12)",
            "xlabel": "time step (hour)",
            "ylabel": "",
            "fig_name": "dispatch_case"}  
    if multipanel:
        plot_case1 = [xaxis_yr, yaxis_yr_ne,yaxis_yr_po,labels, colors, demand_yr, info_yr]
        plot_case2 = [xaxis_week, yaxis_week1_ne,yaxis_week1_po,labels, colors, demand_week1, info_week1]
        plot_case3 = [xaxis_week, yaxis_week2_ne,yaxis_week2_po,labels, colors, demand_week2, info_week2]
        ploty = plot_stack_multi2(plot_case1,plot_case2,plot_case3,case_name)
    else:
        print ('please use multipanel = True!')
    return ploty
    
# --------- contour plot
    
def plot_contour(x,y,z,levels,var_dimension):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    cs1 = ax.contourf(x,y,z,levels=levels,
                      cmap='PuBu_r',
                      extend='both')
    cs2 = ax.contour(x,y,z,levels=levels[::4],
                     colors='k',
                     linewidths=0.5, 
                     alpha=1.)
    ax.clabel(cs2, inline=1, fontsize=5)
    
    plt.colorbar(cs1, ticks=levels[::2], orientation='vertical')    
    ax.set_title('SYSTEM_COST\n($)')
    ax.set_xlabel(var_dimension[0])
    ax.set_ylabel(var_dimension[1]) 
    ax.set_xlim(x.max(),x.min())
    return fig
    plt.clf()

def create_contour_axes(x,y,z):
    
    def find_zz(x_need, y_need):
        find_z = 0.
        tot_idx = len(x)
        for idx in range(tot_idx):
            if x[idx] == x_need and y[idx] == y_need:
                find_z = z[idx]
        return find_z
    
    x_uni = np.unique(x)
    y_uni = np.unique(y)
    z2 = np.ones([ len(x_uni), len(y_uni) ])* (-9999)
    for idx_x in range( len(x_uni) ):
        for idx_y in range( len(y_uni) ):
            x_need = x_uni[idx_x]
            y_need = y_uni[idx_y]
            z2[idx_x, idx_y] = find_zz(x_need,y_need)
    z3 = np.ma.masked_values(z2, -9999)
    return x_uni, y_uni, z3

def contour_plot(res,num_case,case_name,var_dimension):
    dimension1 = get_multicases_results(res, num_case, var_dimension[0])
    dimension2 = get_multicases_results(res, num_case, var_dimension[1])
    SYSTEM_COST      = get_multicases_results(res, num_case, 'SYSTEM_COST')
    x,y,z = create_contour_axes(dimension1, dimension2, SYSTEM_COST)
    levels = np.linspace(z.min(), z.max(), 20)   
    plotz  = plot_contour(x,y,z,levels,var_dimension)
    return plotz



# --------- battery plot
    
def battery_TP(xaxis, mean_residence_time, max_residence_time, max_headroom, battery_output):
    num_time_periods = len(xaxis) * 24
    
    y1 = np.squeeze(avg_series(mean_residence_time, 1, 1,num_time_periods,24,1))
    y2 = np.squeeze(avg_series(max_residence_time,  1, 1,num_time_periods,24,1))
    y3 = np.squeeze(avg_series(max_headroom,        1, 1,num_time_periods,24,1))
    
    fig = plt.figure()
    fig.subplots_adjust(top=1, left=0.0, right=1, hspace=1.0, wspace=0.35)

    ax1 = plt.subplot2grid((3,1),(0,0),rowspan=1, colspan=1)
    ax1v = ax1.twinx()
    ln1 = ax1.stackplot(xaxis, y1, colors ='g', baseline = 'zero', alpha=0.5, labels=['Mean residence time'])
    ln2 = ax1.plot(xaxis,      y2, c = 'green', alpha=0.5,    label='Max energy storage (kWh/kW)')
    ln3 = ax1v.plot(xaxis,     y3, c = 'red',   alpha=0.5,    label='Max headroom ')
    lns = ln1+ln2+ln3
    labs = [l.get_label() for l in lns]
    leg = ax1.legend(lns, labs, loc='center left', ncol=1, 
                     bbox_to_anchor=(1.07, 0.5), prop={'size': 5})
    leg.get_frame().set_alpha(0.4)
    ax1.set_title('(Left) battery storage required to satisfy demand at each hour\n'+\
                  '(Right) maximum headroom required to satisfy demand at each hour',
                  fontsize = 10)
    ax1.set_xlabel('time step (day)')
    plt.setp(ax1.get_xticklabels(), size=7)
    plt.setp(ax1.get_yticklabels(), size=7, color='green')
    plt.setp(ax1v.get_yticklabels(), size=7, color='red')
    
    array_to_draw = y1
    for i in range(len(array_to_draw)):
        if array_to_draw[i] == 0.:
            y1[i] = -1
    ax2 = plt.subplot2grid((3,1),(2,0),rowspan=1, colspan=1)
    weights = np.ones_like(array_to_draw)/float(len(array_to_draw))
    ax2.hist(array_to_draw, 50, weights=weights, label = 'Frequency distribution of\nmean residence time')
    leg = ax2.legend(loc='center left', ncol=1, 
                     bbox_to_anchor=(1.07, 0.5), prop={'size': 5})
    ax2.set_title('Frequency of battery storage for demand at a particular hour',
                  fontsize = 10)
    ax2.set_xlabel('Battery storage (kWh/kW)')
    plt.setp(ax2.get_xticklabels(), size=7)
    plt.setp(ax2.get_yticklabels(), size=7)
    
    ax3 = plt.subplot2grid((3,1),(1,0),rowspan=1, colspan=1)
    ax3.stackplot(xaxis[::4], battery_output[0][::4], labels = ['Battery DISPATCH'])
    ax3.stackplot(xaxis[::4], battery_output[1][::4]*(-1), labels = ['Battery charge'])
    ax3.plot(xaxis[::4], battery_output[1][::4]*(battery_output[2])*(-1), c='k', linewidth=1, label = 'Energy loss from charging')
    leg = ax3.legend(loc='center left', ncol=1, 
                     bbox_to_anchor=(1.07, 0.5), prop={'size': 5})
    ax3.set_title('Battery charge and DISPATCH',
                  fontsize = 10)
    ax3.set_xlabel('time step (day)')
    #plt.show()
    #plt.savefig(case_name+'_Battery.pdf',dpi=200,bbox_inches='tight',transparent=True)
    return fig
    plt.close(fig)

def cycles_per_year(DISPATCH_FROM_STORAGE, max_headroom):
    hrt = np.transpose(np.array((max_headroom,DISPATCH_FROM_STORAGE)))
    hrt1 = hrt[hrt[:,0].argsort()]
    hrt0_unique = np.sort(np.unique(hrt1[:,0])).tolist()
    output = []
    for headroom in hrt0_unique:
        subset = hrt1[hrt1[:,0] == headroom]
        record = [
                headroom,
                np.sum(subset[:,1]), # dispatch
                0., # margingal increase in headroom
                0., # cumulative dispatch
                0., #  increase in headroom / increase in dispatch
                0. #  increase in dispatch / increase in headroom
                ]
        output.append(record)
    output = np.array(output)
    output[1:,2]=output[1:,0]-output[:-1,0] # marginal increase in headroom
    output[:,3] = np.cumsum(output[:,1]) # take cumulative sum 
    output[1:,4] = output[1:,2]/output[1:,1] # increase in headroom per kWh delivered
    output[1:,5] = output[1:,1]/output[1:,2] # increase in kWh delivered per increase in headroom
    
    headroom_table = output
    return headroom_table

def battery_simpleline(xaxis, y1, y2, co):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)    
    ax1.stackplot(xaxis[::4], y1[::4])
    ax1.stackplot(xaxis[::4], y2[::4]*(-1))
    ax1.plot(xaxis[::4], y2[::4]*(1.-co)*(-1), c='k')
    plt.show()
    plt.clf()

def battery_plot(res,
                 num_case,
                 case_name,
                 multipanels,
                 *select_case):
    
    # --- multi case plot
    num_time_periods = len(res[0]['DEMAND'])
    
    find_case_idx = False
    if select_case:
        var1 = get_multicases_results(res, num_case , select_case[0][0])
        var2 = get_multicases_results(res, num_case , select_case[0][1])
        for idx in range(num_case):
            if var1[idx] == select_case[1][0] and var2[idx] == select_case[1][1]:
                find_case_idx = True
                case_idx = idx
                break
        if find_case_idx: 
            print ('Find case index:', case_idx)
        else:
            print ('Error: no such case, exit')
            sys.exit(0)
    if find_case_idx == False:
        case_idx = 0
    
    DISPATCH_TO_STORAGE         = get_multicases_results(res, num_case, 'DISPATCH_TO_STORAGE')[case_idx]
    DISPATCH_FROM_STORAGE       = get_multicases_results(res, num_case, 'DISPATCH_FROM_STORAGE')[case_idx]
    ENERGY_STORAGE              = get_multicases_results(res, num_case, 'ENERGY_STORAGE')[case_idx]
    CHARGING_EFFICIENCY_STORAGE = get_multicases_results(res, num_case, 'CHARGING_EFFICIENCY_STORAGE')[case_idx]
    max_headroom, mean_residence_time, max_residence_time = battery_calculation(num_time_periods,
                                                                                DISPATCH_TO_STORAGE,
                                                                                DISPATCH_FROM_STORAGE,
                                                                                ENERGY_STORAGE,
                                                                                CHARGING_EFFICIENCY_STORAGE)
    aa = DISPATCH_FROM_STORAGE
    bb = DISPATCH_TO_STORAGE
    aaa = np.squeeze(avg_series(aa, 1, 1,num_time_periods,24,1))
    bbb = np.squeeze(avg_series(bb, 1, 1,num_time_periods,24,1))
    ccc = CHARGING_EFFICIENCY_STORAGE
    battery_output = [aaa, bbb, ccc]
    
    xaxis = np.arange(num_time_periods/24)+1
    plotk = battery_TP(xaxis,mean_residence_time,max_residence_time,max_headroom,battery_output)
    
    return plotk





def post_process(global_dic):
    file_path = global_dic['OUTPUT_PATH']+'/'
    scenario_name = global_dic["GLOBAL_NAME"]
    
    multipanel = True
    today = datetime.datetime.now()
    todayString = str(today.year) + str(today.month).zfill(2) + str(today.day).zfill(2) + '_' + \
        str(today.hour).zfill(2) + str(today.minute).zfill(2) + str(today.second).zfill(2)

    pp = PdfPages(global_dic['OUTPUT_PATH']+ '/'+ global_dic['GLOBAL_NAME']+ '/' + global_dic['GLOBAL_NAME'] + '_pdfBOOK_' + todayString +'.pdf')
    file_list = os.listdir(file_path)
    
    for file in file_list:
        file_name = file
        if scenario_name == 'all' or file_name == scenario_name:
            print ('deal with case:', scenario_name)
        
            global_dic,case_dic_list,result_list = unpickle_raw_results(global_dic)
            res = prepare_scalar_variables (global_dic, case_dic_list, result_list )            
            cost_list, var_list = get_dimension_info(case_dic_list)
            
            print (cost_list)
            print (var_list)
            
            num_case = len(res)
            num_var_list = len(var_list) 
            
            dimension = 0
            var_dimension = []    
            for idx in range(num_var_list):
                if cost_list[var_list[idx]].size > 1:
                    dimension = dimension+1
                    var_dimension.append( var_list[idx] )
            if dimension == 0:
                print ('only one case included')
                ploty = stack_plot2(res, num_case, file_name,multipanel, var_dimension)
                plotk = battery_plot(res,num_case,file_name, multipanel)
                pp.savefig(ploty,dpi=200,bbox_inches='tight',transparent=True)
                pp.savefig(plotk,dpi=200,bbox_inches='tight',transparent=True)
                #print ("set at least one dimension change"
                #sys.exit()
            elif dimension == 1 or dimension ==2:
                if dimension ==1 or dimension ==2:  # problem with 2D case, treat as 1D
                    print ("variation list:", var_dimension[0])
                    plotx = stack_plot1(res, num_case, file_name, multipanel, var_dimension)
                    pp.savefig(plotx,dpi=200,bbox_inches='tight',transparent=True)
                    for idx in range( len(cost_list[var_dimension[0]]) ):
                        case_name = file_name + ' - ' + case_dic_list[idx]['CASE_NAME']
                        select_case1 = [var_dimension[0], var_dimension[0]]
                        select_case2 = [cost_list[var_dimension[0]][idx], cost_list[var_dimension[0]][idx]]
                        ploty = stack_plot2(res, num_case, case_name,multipanel, var_dimension, select_case1, select_case2)
                        plotk = battery_plot(res,num_case,case_name, multipanel, select_case1, select_case2)
                        pp.savefig(ploty,dpi=200,bbox_inches='tight',transparent=True)
                        pp.savefig(plotk,dpi=200,bbox_inches='tight',transparent=True)
                else:
                    print ("variation list 1:", var_dimension[0])
                    print ("variation list 2:", var_dimension[1])
                    plotz = contour_plot(res,num_case, file_name, var_dimension)
                    pp.savefig(plotz,dpi=200,bbox_inches='tight',transparent=True)
                    for idx_1 in range( len(cost_list[var_dimension[0]])):
                        subset_res = {}
                        num_idx = 0
                        for idx_2 in range(num_case):
                            if res[idx_2][var_dimension[0]] == cost_list[var_dimension[0]][idx_1]:
                                subset_res[num_idx] = res[idx_2]
                                num_idx = num_idx + 1
                        if len(subset_res) > 1:
                            plotx = stack_plot1(subset_res, num_idx, file_name, multipanel, [var_dimension[1]])
                            pp.savefig(plotx,dpi=200,bbox_inches='tight',transparent=True)
                            for idx_3 in range( len(cost_list[var_dimension[1]]) ):
                                case_name = file_name + ' - ' + case_dic_list[idx]['CASE_NAME']
                                select_case1 = [var_dimension[0], var_dimension[1]]
                                select_case2 = [cost_list[var_dimension[0]][idx_1], cost_list[var_dimension[1]][idx_3]]
                                ploty = stack_plot2(res, num_case, case_name,multipanel, var_dimension, select_case1, select_case2)
                                plotk = battery_plot(res,num_case,case_name, multipanel, select_case1, select_case2)
                                pp.savefig(ploty,dpi=200,bbox_inches='tight',transparent=True)
                                pp.savefig(plotk,dpi=200,bbox_inches='tight',transparent=True)
                    for idx_1 in range( len(cost_list[var_dimension[1]])):
                        subset_res = {}
                        num_idx = 0
                        for idx_2 in range(num_case):
                            if res[idx_2][var_dimension[1]] == cost_list[var_dimension[1]][idx_1]:
                                subset_res[num_idx] = res[idx_2]
                                num_idx = num_idx + 1
                        if len(subset_res) > 1:
                            plotx = stack_plot1(subset_res, num_idx, file_name, multipanel, [var_dimension[0]])
                            pp.savefig(plotx,dpi=200,bbox_inches='tight',transparent=True)
                            for idx_3 in range( len(cost_list[var_dimension[0]]) ):
                                case_name = file_name + ' - ' + case_dic_list[idx]['CASE_NAME']
                                select_case1 = [var_dimension[0], var_dimension[1]]
                                select_case2 = [cost_list[var_dimension[0]][idx_3], cost_list[var_dimension[1]][idx_1]]
                                ploty = stack_plot2(res, num_case, case_name,multipanel, var_dimension, select_case1, select_case2)
                                plotk = battery_plot(res,num_case,case_name, multipanel, select_case1, select_case2)
                                pp.savefig(ploty,dpi=200,bbox_inches='tight',transparent=True)
                                pp.savefig(plotk,dpi=200,bbox_inches='tight',transparent=True)
            else:
                # if dimension > 2, then just make individual plots
                for idx in range( len(cost_list[var_dimension[0]]) ):
                    case_name = file_name + ' - ' + case_dic_list[idx]['CASE_NAME']
                    select_case1 = [var_dimension[0], var_dimension[0]]
                    select_case2 = [cost_list[var_dimension[0]][idx], cost_list[var_dimension[0]][idx]]
                    ploty = stack_plot2(res, num_case, case_name,multipanel, var_dimension, select_case1, select_case2)
                    plotk = battery_plot(res,num_case,case_name, multipanel, select_case1, select_case2)
                    pp.savefig(ploty,dpi=200,bbox_inches='tight',transparent=True)
                    pp.savefig(plotk,dpi=200,bbox_inches='tight',transparent=True)
    pp.close()


#===============================================================================
#================================================== EXECUTION SECTION ==========
#===============================================================================
"""
### this part is for individually use of post-process script
file_path = '/Users/leiduan/Desktop/File/GitHub_Desptop/Latest_Model_Code_Running/SEM-1/Output_Data/test/'
case_name = 'test.pickle'
multipanel = True
pp = PdfPages(file_path + 'postprocess_pdfBOOK.pdf')

with open(file_path+case_name, 'rb') as db:
    global_dic, case_dic_list, result_list = pickle.load (db)
    
run = True
if run:    
            res = prepare_scalar_variables (global_dic, case_dic_list, result_list )            
            cost_list, var_list = get_dimension_info(case_dic_list)
            
            num_case = len(res)
            num_var_list = len(var_list) 
            
            dimension = 0
            var_dimension = []    
            for idx in range(num_var_list):
                if cost_list[var_list[idx]].size > 1:
                    dimension = dimension+1
                    var_dimension.append( var_list[idx] )
            if dimension == 0:
                print ('only one case included')
                ploty = stack_plot2(res, num_case, case_name,multipanel, var_dimension)
                plotk = battery_plot(res,num_case,case_name, multipanel)
                pp.savefig(ploty,dpi=200,bbox_inches='tight',transparent=True)
                pp.savefig(plotk,dpi=200,bbox_inches='tight',transparent=True)
                #print ("set at least one dimension change"
                #sys.exit()
            elif dimension == 1 or dimension ==2:
                if dimension ==1:
                    print ("variation list:", var_dimension[0])
                    plotx = stack_plot1(res, num_case, case_name, multipanel, var_dimension)
                    pp.savefig(plotx,dpi=200,bbox_inches='tight',transparent=True)
                    for idx in range( len(cost_list[var_dimension[0]]) ):
                        select_case1 = [var_dimension[0], var_dimension[0]]
                        select_case2 = [cost_list[var_dimension[0]][idx], cost_list[var_dimension[0]][idx]]
                        ploty = stack_plot2(res, num_case, case_name,multipanel, var_dimension, select_case1, select_case2)
                        plotk = battery_plot(res,num_case,case_name, multipanel, select_case1, select_case2)
                        pp.savefig(ploty,dpi=200,bbox_inches='tight',transparent=True)
                        pp.savefig(plotk,dpi=200,bbox_inches='tight',transparent=True)
                else:
                    print ("variation list 1:", var_dimension[0])
                    print ("variation list 2:", var_dimension[1])
                    plotz = contour_plot(res,num_case, case_name, var_dimension)
                    pp.savefig(plotz,dpi=200,bbox_inches='tight',transparent=True)
                    for idx_1 in range( len(cost_list[var_dimension[0]])):
                        subset_res = {}
                        num_idx = 0
                        for idx_2 in range(num_case):
                            if res[idx_2][var_dimension[0]] == cost_list[var_dimension[0]][idx_1]:
                                subset_res[num_idx] = res[idx_2]
                                num_idx = num_idx + 1
                        if len(subset_res) > 1:
                            plotx = stack_plot1(subset_res, num_idx, case_name, multipanel, [var_dimension[1]])
                            pp.savefig(plotx,dpi=200,bbox_inches='tight',transparent=True)
                            for idx_3 in range( len(cost_list[var_dimension[1]]) ):
                                select_case1 = [var_dimension[0], var_dimension[1]]
                                select_case2 = [cost_list[var_dimension[0]][idx_1], cost_list[var_dimension[1]][idx_3]]
                                ploty = stack_plot2(res, num_case, case_name,multipanel, var_dimension, select_case1, select_case2)
                                plotk = battery_plot(res,num_case,case_name, multipanel, select_case1, select_case2)
                                pp.savefig(ploty,dpi=200,bbox_inches='tight',transparent=True)
                                pp.savefig(plotk,dpi=200,bbox_inches='tight',transparent=True)
                    for idx_1 in range( len(cost_list[var_dimension[1]])):
                        subset_res = {}
                        num_idx = 0
                        for idx_2 in range(num_case):
                            if res[idx_2][var_dimension[1]] == cost_list[var_dimension[1]][idx_1]:
                                subset_res[num_idx] = res[idx_2]
                                num_idx = num_idx + 1
                        if len(subset_res) > 1:
                            plotx = stack_plot1(subset_res, num_idx, case_name, multipanel, [var_dimension[0]])
                            pp.savefig(plotx,dpi=200,bbox_inches='tight',transparent=True)
                            for idx_3 in range( len(cost_list[var_dimension[0]]) ):
                                select_case1 = [var_dimension[0], var_dimension[1]]
                                select_case2 = [cost_list[var_dimension[0]][idx_3], cost_list[var_dimension[1]][idx_1]]
                                ploty = stack_plot2(res, num_case, case_name,multipanel, var_dimension, select_case1, select_case2)
                                plotk = battery_plot(res,num_case,case_name, multipanel, select_case1, select_case2)
                                pp.savefig(ploty,dpi=200,bbox_inches='tight',transparent=True)
                                pp.savefig(plotk,dpi=200,bbox_inches='tight',transparent=True)
            else:
                print ("not support larger than 2 dimensions yet")
                sys.exit()
pp.close()
#"""