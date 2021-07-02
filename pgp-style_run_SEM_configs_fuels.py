#!/usr/bin/env python3

import numpy as np
import csv
import subprocess
import os
from glob import glob
from shutil import copy2, move
from collections import OrderedDict
import pandas as pd
import os
import matplotlib
from datetime import datetime, timedelta
import copy
from helpers import get_fuel_demands, get_fuel_fractions
from end_use_fractions import add_detailed_results
from analytic_fuels import kWh_to_GGE, kWh_LHV_per_kg_H2
matplotlib.rcParams.update({'font.size': 12.5})
matplotlib.rcParams.update({'lines.linewidth': 3})


def marker_list():
    return ['o', 'v', '^', 's', 'P', '*', 'H', 'X', 'd', '<', '>']

# Based on common color blindness
# https://www.nature.com/articles/nmeth.1618/figures/2
# Skip black and reserve it for other specific lines
def color_list():
    l = [
            np.array([230, 159, 0]), # orange
            np.array([86, 180, 233]), # Sky blue
            np.array([0, 158, 115]), # Bluish green
            np.array([240, 228, 66]), # Yellow
            np.array([0, 114, 178]), # Blue
            np.array([213, 94, 0]), # Vermillion
            np.array([204, 121, 167]), # Reddish purple
    ]
    return [i/255. for i in l]



# Use Pandas to retrieve the output values b/c it handles
# fully populated tables well
def get_cap_and_costs_fuels(path, file_name):
    return get_all_cap_and_costs_fuels(path+'/'+file_name)


def get_all_cap_and_costs_fuels(file_name):
    dta = pd.read_csv(file_name, index_col=0, header=None,
                   dtype={
                        'case name':np.str,
                        'problem status':np.str,
                        #'fuel cost ($/GGE)':np.float64,
                        #'fuel demand (kWh)':np.float64,
                        #'system cost ($/kW/h)':np.float64,
                        #'capacity nuclear (kW)':np.float64,
                        #'capacity solar (kW)':np.float64,
                        #'capacity wind (kW)':np.float64,
                        #'capacity fuel electrolyzer (kW)':np.float64,
                        #'capacity fuel chem plant (kW)':np.float64,
                        #'capacity fuel h2 storage (kWh)':np.float64,
                        #'dispatch unmet demand (kW)':np.float64,
                       }).T

    return dta


# Use normal python csv functions b/c this is a sparsely populated
# csv file
def get_SEM_csv_file(file_name):

    with open(file_name, 'r') as f:
        info = list(csv.reader(f, delimiter=","))
    
    return info



# Set the values for this run based on settings dictionary
def set_case_info(cfg, **settings):

    new_cfg = []

    case_data_line = -999 # Starts really negative so the 2nd 'if' is never triggered until ready
    case_name_position = -999
    fuel_value_position = -999
    fuel_demand_position = -999
    start_month_position = -999
    end_month_position = -999
    system_reliability_position = -999
    fixed_cost_solar_position = -999
    fixed_cost_wind_position = -999
    fixed_cost_nuclear_position = -999
    fixed_cost_nat_gas_ccs_position = -999
    fixed_cost_storage_position = -999
    fixed_cost_fuel_electrolyzer_position = -999
    efficiency_fuel_electrolyzer_position = -999
    fixed_cost_fuel_chem_plant_position = -999
    fixed_cost_fuel_h2_storage_position = -999
    var_cost_fuel_chem_plant_position = -999
    var_cost_fuel_co2_position = -999
    capacity_PGP_power_position = -999
    for i, line in enumerate(cfg):

        if line[0] == 'GLOBAL_NAME':
            line[1] = settings['global_name']

        if line[0] == 'CASE_NAME':
            case_data_line = i
            case_name_position = line.index('CASE_NAME')
            fuel_value_position = line.index('FUEL_VALUE')
            fuel_demand_position = line.index('FUEL_DEMAND')
            start_month_position = line.index('START_MONTH')
            end_month_position = line.index('END_MONTH')
            system_reliability_position = line.index('SYSTEM_RELIABILITY')
            fixed_cost_solar_position = line.index('FIXED_COST_SOLAR')
            fixed_cost_wind_position = line.index('FIXED_COST_WIND')
            fixed_cost_nuclear_position = line.index('FIXED_COST_NUCLEAR')
            fixed_cost_nat_gas_ccs_position = line.index('FIXED_COST_NATGAS_CCS')
            fixed_cost_storage_position = line.index('FIXED_COST_STORAGE')
            fixed_cost_fuel_electrolyzer_position = line.index('FIXED_COST_FUEL_ELECTROLYZER')
            efficiency_fuel_electrolyzer_position = line.index('EFFICIENCY_FUEL_ELECTROLYZER')
            fixed_cost_fuel_chem_plant_position = line.index('FIXED_COST_FUEL_CHEM_PLANT')
            fixed_cost_fuel_h2_storage_position = line.index('FIXED_COST_FUEL_H2_STORAGE')
            var_cost_fuel_chem_plant_position = line.index('VAR_COST_FUEL_CHEM_PLANT')
            var_cost_fuel_co2_position = line.index('VAR_COST_FUEL_CO2')
            capacity_PGP_power_position = line.index('CAPACITY_FUEL_POWER')

            print(" --- demand pos: {}, value pos {}, fuel_demand {}x, do_demand_constraint {}, start/end month {}-{}".format(
                    fuel_demand_position, fuel_value_position, settings['fuel_demand'], settings['do_demand_constraint'], 
                    settings['start_month'], settings['end_month']))
        
        if i == case_data_line+2:
            # Set case name
            line[case_name_position] = settings['case_descrip']
            line[start_month_position] = settings['start_month']
            line[end_month_position] = settings['end_month']
            line[system_reliability_position] = settings['system_reliability']
            line[fixed_cost_solar_position] = settings['fixed_cost_solar']
            line[fixed_cost_wind_position] = settings['fixed_cost_wind']
            line[fixed_cost_nuclear_position] = settings['fixed_cost_nuclear']
            line[fixed_cost_nat_gas_ccs_position] = settings['fixed_cost_nat_gas_ccs']
            line[fixed_cost_storage_position] = settings['fixed_cost_storage']
            line[fixed_cost_fuel_electrolyzer_position] = settings['fixed_cost_fuel_electrolyzer']
            line[efficiency_fuel_electrolyzer_position] = settings['efficiency_fuel_electrolyzer']
            line[fixed_cost_fuel_chem_plant_position] = settings['fixed_cost_fuel_chem_plant']
            line[fixed_cost_fuel_h2_storage_position] = settings['fixed_cost_fuel_h2_storage']
            line[var_cost_fuel_chem_plant_position] = settings['var_cost_fuel_chem_plant']
            line[var_cost_fuel_co2_position] = settings['var_cost_fuel_co2']
            line[capacity_PGP_power_position] = settings['capacity_PGP_power']

            line[fuel_value_position] = settings['fuel_value']
            line[fuel_demand_position] = settings['fuel_demand']

        new_cfg.append(line)

    return new_cfg


def write_file(file_name, cfg):

    with open(file_name, 'w') as f:
        for line in cfg:
            to_write = ''
            for val in line:
                to_write += str(val)+','
            f.write(to_write+'\n')
        f.close()


def get_output_file_names(path):

    #print("Looking here for csv files: {}*.csv".format(path))
    files = glob(path+'*.csv')
    files.sort()
    if len(files) > 1:
        print("This many files were found matching {}*.csv: {}".format(path, len(files)))
    return files

def get_results(files, global_name):

    results = {}

    keys = []
    for f in files:
        info = get_all_cap_and_costs_fuels(f)
        if not hasattr(info, 'capacity nuclear (kW)'):
            info['capacity nuclear (kW)'] = 0.
            info['dispatch nuclear (kW)'] = 0.
            info['curtailment nuclear (kW)'] = 0.
            info['fixed cost nuclear ($/kW/h)'] = 0.
        if not hasattr(info, 'capacity natgas_ccs (kW)'):
            info['capacity natgas_ccs (kW)'] = 0.
            info['dispatch natgas_ccs (kW)'] = 0.
            info['curtailment natgas_ccs (kW)'] = 0.
            info['fixed cost natgas_ccs ($/kW/h)'] = 0.
        if not hasattr(info, 'capacity wind (kW)'):
            info['capacity wind (kW)'] = 0.
            info['dispatch wind (kW)'] = 0.
            info['curtailment wind (kW)'] = 0.
            info['fixed cost wind ($/kW/h)'] = 0.
        if not hasattr(info, 'capacity solar (kW)'):
            info['capacity solar (kW)'] = 0.
            info['dispatch solar (kW)'] = 0.
            info['curtailment solar (kW)'] = 0.
            info['fixed cost solar ($/kW/h)'] = 0.
        if not hasattr(info, 'capacity storage (kWh)'):
            info['capacity storage (kWh)'] = 0.
            info['dispatch to storage (kW)'] = 0.
            info['dispatch from storage (kW)'] = 0.
            info['energy storage (kWh)'] = 0.
            info['fixed cost storage ($/kWh/h)'] = 0.
        if not hasattr(info, 'dispatch unmet demand (kW)'):
            info['dispatch unmet demand (kW)'] = 0.
        if not hasattr(info, 'dispatch from fuel h2 storage (kW)'):
            info['dispatch from fuel h2 storage (kW)'] = \
                info['dispatch from fuel h2 storage tot (kW)'].values[0]
        if not hasattr(info, 'dispatch from fuel h2 storage tot (kW)'):
            info['dispatch from fuel h2 storage tot (kW)'] = \
                info['dispatch from fuel h2 storage (kW)'].values[0]
            info['dispatch from fuel h2 storage chem plant (kW)'] = 0.
            info['dispatch from fuel h2 storage power (kW)'] = 0.
        if not hasattr(info, 'fixed cost fuel power ($/kW/h)'):
            info['fixed cost fuel power ($/kW/h)'] = 0.
            info['efficiency fuel power conversion'] = 0.
            info['capacity fuel power (kW)'] = 0.

        #print(info)
        keys.append(info['case name'].values[0])
        results[info['case name'].values[0]] = [
                       info['problem status'].values[0],
                       float(info['fuel cost ($/GGE)'].values[0]),
                       float(info['fuel demand (kWh)'].values[0]),
                       float(info['mean demand (kW)'].values[0]),
                       float(info['system cost ($ or $/kWh)'].values[0]),
                       float(info['capacity nuclear (kW)'].values[0]),
                       float(info['capacity natgas_ccs (kW)'].values[0]),
                       float(info['dispatch natgas_ccs (kW)'].values[0]),
                       float(info['capacity natgas_ccs (kW)'].values[0]) - float(info['dispatch natgas_ccs (kW)'].values[0]), # 'curtailment natgas_ccs (kW)'
                       float(info['fixed cost natgas_ccs ($/kW/h)'].values[0]),
                       float(info['capacity solar (kW)'].values[0]),
                       float(info['capacity wind (kW)'].values[0]),
                       float(info['capacity storage (kWh)'].values[0]),
                       float(info['capacity fuel electrolyzer (kW)'].values[0]),
                       float(info['capacity fuel chem plant (kW)'].values[0]),
                       float(info['capacity fuel h2 storage (kWh)'].values[0]),
                       float(info['dispatch to fuel h2 storage (kW)'].values[0]),
                       float(info['dispatch from fuel h2 storage (kW)'].values[0]),
                       float(info['dispatch from fuel h2 storage tot (kW)'].values[0]),
                       float(info['dispatch from fuel h2 storage chem plant (kW)'].values[0]),
                       float(info['dispatch from fuel h2 storage power (kW)'].values[0]),
                       float(info['dispatch unmet demand (kW)'].values[0]),
                       float(info['dispatch nuclear (kW)'].values[0]),
                       float(info['dispatch wind (kW)'].values[0]),
                       float(info['dispatch solar (kW)'].values[0]),
                       float(info['dispatch to storage (kW)'].values[0]),
                       float(info['dispatch from storage (kW)'].values[0]),
                       float(info['energy storage (kWh)'].values[0]),
                       float(info['curtailment nuclear (kW)'].values[0]),
                       float(info['curtailment wind (kW)'].values[0]),
                       float(info['curtailment solar (kW)'].values[0]),
                       float(info['fixed cost fuel electrolyzer ($/kW/h)'].values[0]),
                       float(info['fixed cost fuel chem plant ($/kW/h)'].values[0]),
                       float(info['fixed cost fuel h2 storage ($/kWh/h)'].values[0]),
                       float(info['var cost fuel electrolyzer ($/kW/h)'].values[0]),
                       float(info['var cost fuel chem plant ($/kW/h)'].values[0]),
                       float(info['var cost fuel co2 ($/kW/h)'].values[0]),
                       float(info['fuel h2 storage (kWh)'].values[0]),
                       float(info['fuel price ($/kWh)'].values[0]),
                       float(info['mean price ($/kWh)'].values[0]),
                       float(info['max price ($/kWh)'].values[0]),
                       float(info['system reliability'].values[0]),
                       float(info['fixed cost wind ($/kW/h)'].values[0]),
                       float(info['fixed cost solar ($/kW/h)'].values[0]),
                       float(info['fixed cost nuclear ($/kW/h)'].values[0]),
                       float(info['fixed cost storage ($/kWh/h)'].values[0]),
                       float(info['fixed cost fuel electrolyzer ($/kW/h)'].values[0]),
                       float(info['efficiency fuel electrolyzer'].values[0]),
                       float(info['fixed cost fuel power ($/kW/h)'].values[0]),
                       float(info['efficiency fuel power conversion'].values[0]),
                       float(info['capacity fuel power (kW)'].values[0]),
        ]

        # Set ~zero values to zero
        for i in range(len(results[info['case name'].values[0]])):
            if i == 0:
                continue
            if results[info['case name'].values[0]][i] < 10e-10 and \
                    results[info['case name'].values[0]][i] > -10e-10:
                results[info['case name'].values[0]][i] = 0.

    print('Writing results to "resultsX/Results_{}.csv"'.format(global_name))
    ofile = open('resultsX/Results_{}.csv'.format(global_name), 'w')
    keys = sorted(keys)
    ofile.write('case name,problem status,fuel cost ($/GGE),fuel demand (kWh),mean demand (kW),system cost ($/kW/h),capacity nuclear (kW),capacity natgas_ccs (kW),dispatch natgas_ccs (kW),curtailment natgas_ccs (kW),fixed cost natgas_ccs ($/kW/h),capacity solar (kW),capacity wind (kW),capacity storage (kWh),capacity fuel electrolyzer (kW),capacity fuel chem plant (kW),capacity fuel h2 storage (kWh),dispatch to fuel h2 storage (kW),dispatch from fuel h2 storage (kW),dispatch from fuel h2 storage tot (kW),dispatch from fuel h2 storage chem plant (kW),dispatch from fuel h2 storage power (kW),dispatch unmet demand (kW),dispatch nuclear (kW),dispatch wind (kW),dispatch solar (kW),dispatch to storage (kW),dispatch from storage (kW),energy storage (kWh),curtailment nuclear (kW),curtailment wind (kW),curtailment solar (kW),fixed cost fuel electrolyzer ($/kW/h),fixed cost fuel chem plant ($/kW/h),fixed cost fuel h2 storage ($/kWh/h),var cost fuel electrolyzer ($/kW/h),var cost fuel chem plant ($/kW/h),var cost fuel co2 ($/kW/h),fuel h2 storage (kWh),fuel price ($/kWh),mean price ($/kWh),max price ($/kWh),system reliability,fixed cost wind ($/kW/h),fixed cost solar ($/kW/h),fixed cost nuclear ($/kW/h),fixed cost storage ($/kWh/h),fixed cost fuel electrolyzer ($/kW/h),efficiency fuel electrolyzer,fixed cost fuel power ($/kW/h),efficiency fuel power conversion,capacity fuel power (kW)\n')
    for key in keys:
        to_print = ''
        for info in results[key]:
            to_print += str(info)+','
        ofile.write("{},{}\n".format(key, to_print))
    ofile.close()
    return results



def simple_plot(x, ys, labels, save, logY=False, ylims=[-1,-1], **kwargs):

    print("Plot {} using x,y = {},{}".format(save, kwargs['x_label'],kwargs['y_label']))

    plt.close()
    matplotlib.rcParams["figure.figsize"] = (6.4, 4.8)
    fig, ax = plt.subplots()
    ax.set_xlabel(kwargs['x_label'])
    ax.set_ylabel(kwargs['y_label'])

    markers = marker_list()
    for y, label, mark in zip(ys, labels, markers):
        #print(label)
        #for i, j in zip(x, y):
        #    print(i, j)

        # Skip adding empty and null arrays to legend
        ary = np.array(y)
        if np.isnan( ary ).sum() == len(y) or \
                (ary == 0.0).sum() == len(y):
            #print(f"Skipping: {ary}")
            #ax.scatter([], [])
            ax.plot([], [])
            continue
        if 'h2_only' in kwargs.keys() and (label == 'chemical plant' or 'storage' in label):
            ax.plot([], [])
            continue


        if label == 'h2 storage':
            #ax.scatter(x, y, label=r'H$_{2}$ storage', marker=markers[-1], color='C7')
            ax.plot(x, y, label=r'H$_{2}$ storage', color='C7')
        else:
            #ax.scatter(x, y, label=label, marker=mark)
            ax.plot(x, y, label=label)

    if logY:
        plt.yscale('log', nonposy='clip')
        #y_min = 999
        #y_max = -999
        #for y in ys:
        #    y_tmp = y[np.nonzero(y)]
        #    y_tmp = y_tmp[np.isfinite(y_tmp)]
        #    try:
        #        if min(y_tmp) < y_min:
        #            y_min = min(y_tmp)
        #    except ValueError:
        #        continue
        #    if max(y_tmp) > y_max:
        #        y_max = max(y_tmp)

        #if not (y_min == y_max):
        #    #if 'dual' in title:
        #    #    ax.set_ylim(y_min*.5, 1.0)
        #    #    plt.tick_params(axis='y', which='minor')
        #    #    ax.yaxis.set_minor_formatter(FormatStrFormatter("%.2f"))
        #    #else:
        #    print(y_min, y_max)
        #    ax.set_ylim(y_min*.5, y_max*2)

        #    #y_tmp = y[np.nonzero(y)]
        #    #y_tmp = y_tmp[np.isfinite(y_tmp)]
        #    #ax.set_ylim(min(y_tmp)*.5, max(y_tmp)*2)

    if ylims != [-1,-1]:
        ax.set_ylim(ylims[0], ylims[1])
    
    # Add vertical bars deliniating 3 regions if this plot is included in the paper:
    # 1) cheapest fuel cost --> +5%
    # 2) cheapest + 5% --> most expensive - 5%
    # 3) most expensive - 5% --> most expensive
    #if save == 'systemCFs' and not 'Case0_NuclearFlatDemand' in save_dir:
    #if not 'Case0_NuclearFlatDemand' in save_dir:
    #    df = kwargs['df']
    #    cheapest_fuel = df.loc[1, 'fuel price ($/kWh)']
    #    most_expensive_fuel = df.loc[len(df.index)-1, 'fuel price ($/kWh)']
    #    fuel_dem_split_1 = get_threshold(df, cheapest_fuel, 1.05, kwargs['x_var'])
    #    fuel_dem_split_2 = get_threshold(df, most_expensive_fuel, 0.95, kwargs['x_var'])
    #    ax.plot(np.ones(100) * fuel_dem_split_1, np.linspace(0, ax.get_ylim()[1]*.9, 100), 'k--', label='_nolegend_')
    #    ax.plot(np.ones(100) * fuel_dem_split_2, np.linspace(0, ax.get_ylim()[1]*.9, 100), 'k--', label='_nolegend_')

    plt.xscale(kwargs['x_type'], nonposx='clip')
    if kwargs['x_type'] == 'log':
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(myLogFormat))
    ax.set_xlim(kwargs['stacked_min'], kwargs['stacked_max'])

    #plt.tight_layout()
    if not 'systemCFsEF' in save:
        plt.grid()

    if 'systemCFsEF' in save:
        ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(xmax=1, decimals=0))
        ax.set_ylabel(ax.get_ylabel(), labelpad=-2)
        plt.legend(ncol=2, loc='lower left', framealpha = 1.0)
    elif 'systemCFs' in save:
        plt.legend(ncol=3, loc='upper left', framealpha = 1.0)
    elif 'systemCosts' in save or 'powerSystemCosts' in save:
        if 'CostsExp' in save:
            plt.legend(loc='upper left', framealpha = 1.0)
        else:
            plt.legend(loc='upper right', framealpha = 1.0)
    else:
        plt.legend(loc='upper left', framealpha = 1.0)
    fig.savefig('{}/{}.png'.format(kwargs['save_dir'], save))
    fig.savefig('{}/{}.pdf'.format(kwargs['save_dir'], save))



# FIXME - just taking the last set of y values for the 2nd axis.  This could be much better...
def simple_plot_with_2nd_yaxis(x, ys, labels, y_label_1, y_label_2, save, **kwargs):

    df = kwargs['df']
    print("Plotting x,y1 = {},{} and x,y2 = {},{}".format(kwargs['x_label'],y_label_1,kwargs['x_label'],y_label_2))

    plt.close()
    matplotlib.rcParams["figure.figsize"] = (6.4, 4.8)
    fig, ax = plt.subplots()
    ax.set_xlabel(kwargs['x_label'])
    ax.set_ylabel(y_label_1)
    plt.subplots_adjust(left=0.15, right=.85)


    # First y-axis
    markers = marker_list()
    for i in range(len(ys)-1): # skip last set of y values

        # Skip adding empty and null arrays to legend
        ary = np.array(ys[i])
        if np.isnan( ary ).sum() == len(ys[i]) or \
                (ary == 0.0).sum() == len(ys[i]):
            #print(f"Skipping: {ary}")
            #ax.scatter([], [])
            ax.plot([], [])
            continue
        elif 'h2_only' in kwargs.keys() and kwargs['h2_only'] == True and labels[i] == 'chem plant':
            ax.plot([], [])
            continue


        #ax.scatter(x, ys[i], label=labels[i], marker=markers[i])
        ax.plot(x, ys[i], label=labels[i])
    plt.legend(loc='upper left', framealpha = 1.0)
    ax.set_ylim(ax.get_ylim()[0]/1.5, ax.get_ylim()[1]*1.5)
    plt.grid()
    
    # Add vertical bars deliniating 3 regions if this plot is included in the paper:
    # 1) cheapest fuel cost --> +5%
    # 2) cheapest + 5% --> most expensive - 5%
    # 3) most expensive - 5% --> most expensive
    #if 'ratiosFuelSystem' in save and not 'Case0_NuclearFlatDemand' in save_dir:
    #if not 'Case0_NuclearFlatDemand' in save_dir:
    #    cheapest_fuel = df.loc[1, 'fuel price ($/kWh)']
    #    most_expensive_fuel = df.loc[len(df.index)-1, 'fuel price ($/kWh)']
    #    fuel_dem_split_1 = get_threshold(df, cheapest_fuel, 1.05, kwargs['x_var'])
    #    fuel_dem_split_2 = get_threshold(df, most_expensive_fuel, 0.95, kwargs['x_var'])
    #    ax.plot(np.ones(100) * fuel_dem_split_1, np.linspace(0, ax.get_ylim()[1]*.9, 100), 'k--', label='_nolegend_')
    #    ax.plot(np.ones(100) * fuel_dem_split_2, np.linspace(0, ax.get_ylim()[1]*.9, 100), 'k--', label='_nolegend_')

    ax.set_ylim(0, ax.get_ylim()[1])
    
    if 'h2_only' not in kwargs.keys():
        # Second y-axis
        ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
        ax2.set_ylabel(y_label_2, color='C7')  # we already handled the x-label with ax1
        #ax2.scatter(x, ys[-1], color='C7', label=labels[-1], marker=markers[-1])
        ax2.plot(x, ys[-1], color='C7', label=labels[-1])
        ax2.tick_params(axis='y', labelcolor='C7')
        plt.legend(loc='upper right', framealpha = 1.0)
        ax2.set_ylim(0, ax2.get_ylim()[1]*1.3)

    plt.xscale(kwargs['x_type'], nonposx='clip')
    if kwargs['x_type'] == 'log':
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(myLogFormat))
    ax.set_xlim(kwargs['stacked_min'], kwargs['stacked_max'])

    if 'y_type' in kwargs.keys() and kwargs['y_type'] == 'log':
        ax.set_yscale('log', nonposy='clip')
        #ax.set_ylim(.1, ax.get_ylim()[1]*10)
        ax.set_ylim(.01, 1e3)
        if 'h2_only' not in kwargs.keys():
            ax2.set_yscale('log', nonposy='clip')
            #ax2.set_ylim(.1, ax2.get_ylim()[1]*10)
            ax2.set_ylim(.1, 1e5)

    #plt.tight_layout()
    #plt.legend()
    fig.savefig('{}/{}.png'.format(kwargs['save_dir'], save))
    fig.savefig('{}/{}.pdf'.format(kwargs['save_dir'], save))


# The addition here compared to the simple_plot is coloring/sizing the dots
def biv_curtailment_cost_plot(tot_curtailment, fuel_costs, fuel_demand, x_label, save_dir, save_name):

    print("Plotting biv_curtailment_cost_plot")

    plt.close()
    matplotlib.rcParams["figure.figsize"] = (6.4, 4.8)
    fig, ax = plt.subplots()
    ax.set_xlabel(x_label)
    ax.set_ylabel('Fuel Cost ($/kWh)')
    plt.title('Total Curtailment vs. Fuel Costs')

    sc = ax.scatter(tot_curtailment, fuel_costs, c=fuel_demand, norm=matplotlib.colors.LogNorm(), s=250)
    cbar = plt.colorbar(sc)
    cbar.ax.set_ylabel("Fuel Demand (kWh/h)")

    plt.grid()
    
    #ax.set_xlim(0., 1.0)
    #ax.set_ylim(.17, .26)

    #plt.tight_layout()

    fig.savefig('{}/{}.png'.format(save_dir, save_name))



# Poorly written, the args are all required and are below.
#x_vals, nuclear, wind, solar, x_label, y_label, 
#legend_app, stacked_min, stacked_max, save_name, save_dir):
def stacked_plot(**kwargs):

    plt.close()
    matplotlib.rcParams["figure.figsize"] = (6.4, 4.8)
    fig, ax = plt.subplots()
    ax.set_xlabel(kwargs['x_label'])
    ax.set_ylabel(kwargs['y_label'])

    colors = color_list()
    tot = np.zeros(len(kwargs['x_vals']))
    if 'stackedEndUseFraction' in kwargs["save_name"]:
        if 'ALT' in kwargs and kwargs['ALT'] == True:
            ax.fill_between(kwargs['x_vals'], tot, tot+kwargs['elec_load']*kwargs['dem_renew_frac'], color=colors[0], linewidth=0, label=f'power to electric load - renew')
            tot += kwargs['elec_load']*kwargs['dem_renew_frac']
            ax.fill_between(kwargs['x_vals'], tot, tot+kwargs['elec_load']*(1. - kwargs['dem_renew_frac']), color=colors[0], linewidth=0, alpha=0.5, label=f'power to electric load - dispatch')
            tot += kwargs['elec_load']*(1. - kwargs['dem_renew_frac'])
            ax.fill_between(kwargs['x_vals'], tot, tot+kwargs['fuel_load']*kwargs['electro_renew_frac'], color=colors[1], linewidth=0, label=f'power to flexible load - renew')
            tot += kwargs['fuel_load']*kwargs['electro_renew_frac']
            ax.fill_between(kwargs['x_vals'], tot, tot+kwargs['fuel_load']*(1. - kwargs['electro_renew_frac']), color=colors[1], linewidth=0, alpha=0.5, label=f'power to flexible load - dispatch')
            tot += kwargs['fuel_load']*(1. - kwargs['electro_renew_frac'])
            #ax.fill_between(kwargs['x_vals'], tot, tot+kwargs['battery_losses'], color='blue', linewidth=0, label=f'battery losses')
            #tot += kwargs['battery_losses']
            ax.fill_between(kwargs['x_vals'], tot, tot+kwargs['renewable_curt'], color=colors[5], linewidth=0, label=f'curtailed - renew')
            tot += kwargs['renewable_curt']
            #for ff, y in zip(kwargs['x_vals'], tot):
            #    print(ff, y)
            ax.fill_between(kwargs['x_vals'], tot, tot+kwargs['nuclear_curt'], color=colors[5], linewidth=0, alpha=0.5, label=f'unused - dispatch')
            tot += kwargs['nuclear_curt']
            #for ff, y in zip(kwargs['x_vals'], tot):
            #    print(ff, y)

            # Highlight transition region
            threshold = 0.0025
            ff_1_idx, ff_2_idx = get_two_thresholds(kwargs['df'], threshold, kwargs['x_var'])
            if 'ylim' in kwargs.keys():
                y_max = kwargs['ylim'][1]
            else:
                y_max = 9999
            #ax.fill_between(df.loc[ff_1_idx:ff_2_idx, kwargs['x_var']], 0, y_max, color=colors[-1], alpha=0.2)
            #ax.fill_between(df.loc[ff_1_idx:ff_2_idx, kwargs['x_var']], 0, y_max, facecolor='none', edgecolor='gray', hatch='....', linewidth=0, alpha=0.5)
            #ax.fill_between(xs, 0., dfs['demand (kW)'] - dfs['dispatch unmet demand (kW)'], facecolor='none', edgecolor='black', hatch='/////', label='power to electric load', lw=fblw)
    

        else:
            ax.fill_between(kwargs['x_vals'], tot, tot+kwargs['elec_load'], color=colors[0], linewidth=0, label=f'power to electric load')
            tot += kwargs['elec_load']
            ax.fill_between(kwargs['x_vals'], tot, tot+kwargs['fuel_load'], color=colors[1], linewidth=0, label=f'power to flexible load')
            tot += kwargs['fuel_load']
            #ax.fill_between(kwargs['x_vals'], tot, tot+kwargs['battery_losses'], color='blue', linewidth=0, label=f'battery losses')
            #tot += kwargs['battery_losses']
            ax.fill_between(kwargs['x_vals'], tot, tot+kwargs['renewable_curt'], color=colors[5], linewidth=0, label=f'curtailed - renew')
            tot += kwargs['renewable_curt']
            ax.fill_between(kwargs['x_vals'], tot, tot+kwargs['nuclear_curt'], color=colors[5], linewidth=0, alpha=0.5, label=f'unused - dispatch')
            tot += kwargs['nuclear_curt']

    else:
        #if not (np.isnan( kwargs['nuclear'] ).sum() == len(kwargs['nuclear']) or (kwargs['nuclear'] == 0.0).sum() == len(kwargs['nuclear'])):
        ax.fill_between(kwargs['x_vals'], 0., kwargs['nuclear'], color=colors[5], linewidth=0, label=f'dispatchable {kwargs["legend_app"]}')
        tot += kwargs['nuclear']
        if 'renewables' in kwargs.keys():
            ax.fill_between(kwargs['x_vals'], tot, tot+kwargs['renewables'], color=colors[1], linewidth=0, label=f'renewables {kwargs["legend_app"]}')
            tot += kwargs['renewables']
        else:
            ax.fill_between(kwargs['x_vals'], tot, tot+kwargs['wind'], color=colors[1], linewidth=0, label=f'wind {kwargs["legend_app"]}')
            tot += kwargs['wind']
            ax.fill_between(kwargs['x_vals'], tot, tot+kwargs['solar'], color=colors[0], linewidth=0, label=f'solar {kwargs["legend_app"]}')
            tot += kwargs['solar']
        if 'stackedGenerationElecNorm' in kwargs["save_name"]:
            ax.plot(kwargs['x_vals'], tot, 'k-', label='total available gen.')
            ax.plot(kwargs['x_vals'], np.ones(len(kwargs['x_vals'])), 'k--', label='firm electric load')
            ax.plot(kwargs['x_vals'], np.ones(len(kwargs['x_vals'])) / (1. - kwargs['x_vals']), 'k:', label='firm electric +\nflexible load')
            #for x, y in zip(kwargs['x_vals'], tot):
            #    print(x, y)

            # Highlight transition region
            threshold = 0.0025
            ff_1_idx, ff_2_idx = get_two_thresholds(kwargs['df'], threshold, kwargs['x_var'])
            if 'ylim' in kwargs.keys():
                y_max = kwargs['ylim'][1]
            else:
                y_max = 9999
            #ax.fill_between(df.loc[ff_1_idx:ff_2_idx, kwargs['x_var']], 0, y_max, color=colors[-1], alpha=0.2)
            #ax.fill_between(df.loc[ff_1_idx:ff_2_idx, kwargs['x_var']], 0, y_max, facecolor='none', edgecolor='gray', hatch='....', linewidth=0, alpha=0.5)
            #ax.fill_between(xs, 0., dfs['demand (kW)'] - dfs['dispatch unmet demand (kW)'], facecolor='none', edgecolor='black', hatch='/////', label='power to electric load', lw=fblw)




    plt.xscale(kwargs['x_type'], nonposx='clip')
    if kwargs['x_type'] == 'log':
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(myLogFormat))
    ax.set_xlim(kwargs['stacked_min'], kwargs['stacked_max'])

    if 'logy' in kwargs.keys():
        if kwargs['logy'] == True:
            plt.yscale('log', nonposy='clip')
            ax.set_ylim(min(0.1, ax.get_ylim()[0]), max(100, ax.get_ylim()[1]))

    #plt.tight_layout()

    if 'ylim' in kwargs.keys():
        ax.set_ylim(kwargs['ylim'][0], kwargs['ylim'][1])
        if 'stackedEndUseFraction' in kwargs["save_name"]:
            plt.legend(loc='upper right', ncol=1, framealpha = 1.0)
        elif 'stackedGenerationElecNorm' in kwargs["save_name"]:
            plt.legend(loc='upper left', ncol=1, framealpha = 1.0)
        else:
            plt.legend(ncol=3, framealpha = 1.0)
    else:
        plt.legend(framealpha = 1.0)
    ax.yaxis.set_ticks_position('both')
    #plt.grid()
    fig.savefig(f'{kwargs["save_dir"]}/{kwargs["save_name"]}.png')
    fig.savefig(f'{kwargs["save_dir"]}/{kwargs["save_name"]}.pdf')


def get_threshold(df, ref, threshold, var='fuel demand (kWh)'):
    prev_price = 0
    prev_dem = 0
    for idx in df.index:
        if df.loc[idx, 'fuel price ($/kWh)'] >= ref * threshold:
            now_price = df.loc[idx, 'fuel price ($/kWh)']
            now_dem = df.loc[idx, var]
            break
        prev_price = df.loc[idx, 'fuel price ($/kWh)']
        prev_dem = df.loc[idx, var]

    # price on x axis
    prev_to_threshold_frac = (ref * threshold - prev_price) / (now_price - prev_price)
    dem_threshold = prev_dem + prev_to_threshold_frac * (now_dem - prev_dem)

    return dem_threshold


def get_two_thresholds(df, threshold, var='fuel demand (kWh)'):

    elec_max = df.iloc[0]['fuel_load_cost']
    elec_min = df.iloc[-1]['fuel_load_cost']

    ff_1_idx = -999
    ff_2_idx = -999
    for idx in df.index:
        if df.loc[idx, 'fuel_load_cost'] >= elec_max + threshold:
            ff_1_idx = idx
            break

    for idx in reversed(df.index):
        if df.loc[idx, 'fuel_load_cost'] <= elec_min - threshold:
            ff_2_idx = idx
            break

    #print(f"\n\nelec_max {elec_max}, elec_min {elec_min}, ff_1_idx {ff_1_idx}, ff_2_idx {ff_2_idx}")

    return ff_1_idx, ff_2_idx

# From: https://stackoverflow.com/questions/21920233/matplotlib-log-scale-tick-label-number-formatting
def myLogFormat(y,pos):
    # Find the number of decimal places required
    decimalplaces = int(np.maximum(-np.log10(y),0))     # =0 for numbers >=1
    # Insert that number into a format string
    formatstring = '{{:.{:1d}f}}'.format(decimalplaces)
    # Return the formatted tick label
    return formatstring.format(y)


# Poorly written, the args are all required and are below.
#save_name, save_dir
def costs_plot(var='fuel demand (kWh)', **kwargs):

    df = kwargs['df']
    threshold = 0.0025
    ff_1_idx, ff_2_idx = get_two_thresholds(df, threshold, var)

    colors = color_list()
    plt.close()
    y_max = 30
    if 'h2_only' in kwargs.keys():
        if 'ALT' in kwargs.keys():
            y_max = 12
        else:
            y_max = 8
    matplotlib.rcParams["figure.figsize"] = (6.4, 4.8)
    if not 'h2_only' in kwargs.keys():
        matplotlib.rcParams["figure.figsize"] = (6.4, 6.8)
    fig, ax = plt.subplots(dpi=400)

    # The left y-axis will use $/GGE for electrofuel or $/kg for H2
    if 'h2_only' in kwargs.keys():
        conversion = kWh_LHV_per_kg_H2 # Convert for main y-axis
        conversion *= EFFICIENCY_FUEL_CHEM_CONVERSION # The cost is set based on liquid hydrocarbon
                                                      # output, so must be scaled for H2 only
        ax.set_ylabel(r'cost (\$/kg$_{H2}$)')
    else:
        conversion = kWh_to_GGE
        ax.set_ylabel(r'cost (\$/GGE)')

    ax.set_xlabel(kwargs['x_label'])
    
    appA = ''
    appB = ''
    ep = 'electric power'
    if 'ALT' in kwargs.keys():
        appA = ' (marginal cost)'
        appB = appA #'\n(marginal cost)'
        ep = 'power'


    # Electricity cost
    #ax.scatter(df[var], df['mean price ($/kWh)'], color='black', label=r'electricity cost (\$/kWh$_{e}$)', marker='v')
    #ax.plot(df[var], df['mean price ($/kWh)'], 'k--', label='power to electric\n'+r'load (\$/kWh$_{e}$)')

    # $/GGE fuel line use Dual Value
    #ax.scatter(df[var], df['fuel price ($/kWh)'], color='black', label='total electrofuel\n'+r'cost (\$/kWh$_{LHV}$)')
    lab = r'H$_{2}$ production total' if 'h2_only' in kwargs.keys() else 'electrofuel production total'
    ax.plot(df[var], df['fuel price ($/kWh)'] * conversion, 'k-', label=lab+appB)
    for ff, cost in zip(df[var], df['fuel price ($/kWh)'] * conversion):
        if round(ff,2) == 0.50:
            print("tot", ff, cost)
    #    break

    # Stacked components
    f_elec = df['fixed cost fuel electrolyzer ($/kW/h)'] * df['capacity fuel electrolyzer (kW)'] / df['fuel demand (kWh)']
    f_chem = df['fixed cost fuel chem plant ($/kW/h)'] * df['capacity fuel chem plant (kW)'] / df['fuel demand (kWh)']
    f_store = df['fixed cost fuel h2 storage ($/kWh/h)'] * df['capacity fuel h2 storage (kWh)'] / df['fuel demand (kWh)']
    v_chem = df['var cost fuel chem plant ($/kW/h)'] * df['dispatch from fuel h2 storage (kW)'] * EFFICIENCY_FUEL_CHEM_CONVERSION / df['fuel demand (kWh)']
    v_co2 = df['var cost fuel co2 ($/kW/h)'] * df['dispatch from fuel h2 storage (kW)'] * EFFICIENCY_FUEL_CHEM_CONVERSION / df['fuel demand (kWh)']
    #for ff, cost, c2 in zip(df[var], f_elec * conversion, f_elec * EFFICIENCY_FUEL_CHEM_CONVERSION):
    #    print(ff, cost, c2)

    # In PGP cases, distribute electrolyzer cost as a fraction of used H2 to each end use, same for storage
    f_elec *= conversion * (df['dispatch from fuel h2 storage chem plant (kW)'] / df['dispatch from fuel h2 storage tot (kW)'])
    f_chem *= conversion
    f_store *= conversion * (df['dispatch from fuel h2 storage chem plant (kW)'] / df['dispatch from fuel h2 storage tot (kW)'])
    f_tot = (f_elec+f_chem+f_store)
    v_chem *= conversion
    v_co2 *= conversion


    # Build stack
    lab = 'fixed cost: electrolysis plant' # if 'h2_only' in kwargs.keys() else 'fixed: electrolysis\nplant'
    ax.fill_between(df[var], 0, f_elec, label=lab, color=colors[0])
    for ff, cost in zip(df[var], f_elec):
        if round(ff,2) == 0.50:
            print("electrolysis", ff, cost)
    #    break

    if 'h2_only' not in kwargs.keys():
        ax.fill_between(df[var], f_elec, f_elec+f_chem, label='fixed cost: chemical plant', color=colors[1])
        ax.fill_between(df[var], f_elec+f_chem, f_elec+f_chem+f_store, label='fixed cost: storage', color=colors[2]) # fixed cost storage set at 2.72E-7
        ax.fill_between(df[var], f_tot, f_tot+v_chem, label='variable cost: chemical plant', color=colors[3])
        ax.fill_between(df[var], f_tot+v_chem, f_tot+v_chem+v_co2, label='variable cost: CO$_{2}$ feedstock', color=colors[4])


    ax.fill_between(df[var], f_tot+v_chem+v_co2, df['fuel price ($/kWh)'] * conversion, label=f'{ep}'+appA, color=colors[5], alpha=.8, hatch='\\\\')
    #ax.fill_between(df[var], 0, f_elec, label='fixed: electrolyzer +\ncompressor')
    #ax.fill_between(df[var], f_elec, f_elec+f_chem, label='fixed: chem plant')
    #ax.fill_between(df[var], f_elec+f_chem, f_elec+f_chem+f_store, label='fixed: storage', color='black') # fixed cost storage set at 2.72E-7
    #ax.fill_between(df[var], f_tot, f_tot+v_chem, label='var: chem plant')
    #ax.fill_between(df[var], f_tot+v_chem, f_tot+v_chem+v_co2, label='var: CO$_{2}$')
    #ax.fill_between(df[var], f_tot+v_chem+v_co2, df['fuel price ($/kWh)'], label='electric power')

    if 'ALT' in kwargs.keys():
        tot_eff_fuel_process = EFFICIENCY_FUEL_ELECTROLYZER * EFFICIENCY_FUEL_CHEM_CONVERSION
        avg_elec_cost = (df['mean price ($/kWh)'] * (1. - df[var]) + df['fuel_load_cost'] * df[var]) / tot_eff_fuel_process
        #for ff, cost, c2, c3 in zip(df[var], avg_elec_cost * conversion, avg_elec_cost * EFFICIENCY_FUEL_CHEM_CONVERSION, avg_elec_cost * tot_eff_fuel_process):
        #    print(ff, cost, c2, c3)
        ax.fill_between(df[var], f_tot+v_chem+v_co2, f_tot+v_chem+v_co2 + avg_elec_cost * conversion, label='power (system-wide cost)', hatch='////', alpha=0.3, color=colors[4])
        lab = r'H$_{2}$ production total' if 'h2_only' in kwargs.keys() else 'electrofuel production total'
        ax.plot(df[var], f_tot+v_chem+v_co2 + avg_elec_cost * conversion, color='black', linestyle='--', label=lab+' (system-wide cost)')
        for ff, cost in zip(df[var], f_tot+v_chem+v_co2 + avg_elec_cost * conversion):
            if round(ff,2) == 0.50:
                print("tot mean", ff, cost)
        #    break
        

    n = len(df.index)-1
    print(f" --- Stacked cost plot for fractional fuel demand = {round(df.loc[1, 'fuel demand (kWh)'],4)}           {round(df.loc[n, 'fuel demand (kWh)'],4)}:")
    print(f" ----- fixed cost electrolyzer          {round(f_elec[1],6)}         {round(f_elec[n],6)}")
    print(f" ----- fixed cost chem                  {round(f_chem[1],6)}         {round(f_chem[n],6)}")
    print(f" ----- fixed cost storage               {round(f_store[1],6)}         {round(f_store[n],6)}")
    print(f" ----- variable chem                    {round(v_chem[1],6)}         {round(v_chem[n],6)}")
    print(f" ----- variable CO2                     {round(v_co2[1],6)}          {round(v_co2[n],6)}")
    print(f" ----- variable electrolyzer            {round(df.loc[1, 'fuel price ($/kWh)']-(f_tot[1]+v_chem[1]+v_co2[1]),6)}             {round(df.loc[n, 'fuel price ($/kWh)']-(f_tot[n]+v_chem[n]+v_co2[n]),6)}")
    print(f" ----- TOTAL:                           {round(df.loc[1, 'fuel price ($/kWh)'],6)}           {round(df.loc[n, 'fuel price ($/kWh)'],6)}")
    print(f" ----- mean cost electricity            {round(df.loc[1, 'mean price ($/kWh)'],6)}           {round(df.loc[n, 'mean price ($/kWh)'],6)}")

    # Highlight transition region
    #ax.fill_between(df.loc[ff_1_idx:ff_2_idx, var], 0, y_max, color=colors[-1], alpha=0.15)
    #ax.fill_between(df.loc[ff_1_idx:ff_2_idx, var], 0, y_max, facecolor='none', edgecolor='gray', hatch='....', linewidth=0, alpha=0.5)


    # To print the estimated MEM electricity cost per point
    #ax.scatter(df[var], df['fuel price ($/kWh)'], color='black', label='_nolegend_')
    #ax.scatter(df[var], df['mean price ($/kWh)'], color='black', label='_nolegend_', marker='v')
    #ax.plot(df[var], df['mean price ($/kWh)'], 'k--', label='_nolegend_')
    ax.plot(df[var], df['fuel price ($/kWh)'] * conversion, 'k-', label='_nolegend_')
    if 'ALT' in kwargs.keys():
        ax.plot(df[var], f_tot+v_chem+v_co2 + avg_elec_cost * conversion, color='black', linestyle='--', label='_nolegend_')

    # Add vertical bars deliniating 3 regions:
    # 1) cheapest fuel cost --> +5%
    # 2) cheapest + 5% --> most expensive - 5%
    # 3) most expensive - 5% --> most expensive
    #if not 'Case0_NuclearFlatDemand' in save_dir:
    #    cheapest_fuel = df.loc[1, 'fuel price ($/kWh)']
    #    most_expensive_fuel = df.loc[len(df.index)-1, 'fuel price ($/kWh)']
    #    fuel_dem_split_1 = get_threshold(df, cheapest_fuel, 1.05, var)
    #    fuel_dem_split_2 = get_threshold(df, most_expensive_fuel, 0.95, var)
    #    print(f"\nSave dir {save_dir}, lower threshold {fuel_dem_split_1}, upper threshold {fuel_dem_split_2}")
    #    ax.plot(np.ones(100) * fuel_dem_split_1, np.linspace(0, y_max*.9, 100), 'k--', label='_nolegend_')
    #    ax.plot(np.ones(100) * fuel_dem_split_2, np.linspace(0, y_max*.9, 100), 'k--', label='_nolegend_')


    plt.xscale(kwargs['x_type'], nonposx='clip')
    if kwargs['x_type'] == 'log':
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(myLogFormat))

    if var == 'fuel demand (kWh)' or var == 'dispatch to fuel h2 storage (kW)':
        ax.set_xlim(df.loc[1, var], df.loc[len(df.index)-1, var])
    else:
        plt.xscale('linear')
        ax.set_xlim(0.0, 1.0)

    ax.set_ylim(0, y_max)
    #plt.grid()
    if 'h2_only' not in kwargs.keys():
        plt.legend(loc='upper right', ncol=1, framealpha = 1.0)
    else:
        plt.legend(loc='upper right', ncol=1, framealpha = 1.0)
        plt.subplots_adjust(left=0.12, right=.85)

    # 2nd y-axis for $/kWh_e
    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_ylabel(r'cost (\$/kWh$_{LHV}$)')
    ax2.set_ylim(0, ax.get_ylim()[1] / kWh_to_GGE)

    #plt.tight_layout()
    app2 = '_ALT' if 'ALT' in kwargs.keys() else ''
    ax.set_rasterized(True)
    ax2.set_rasterized(True)
    fig.savefig(f'{kwargs["save_dir"]}{kwargs["save_name"]}{app2}.png')
    fig.savefig(f'{kwargs["save_dir"]}{kwargs["save_name"]}{app2}.pdf')
    print(f'{kwargs["save_dir"]}{kwargs["save_name"]}.png')


# Poorly written, the args are all required and are below.
#save_name, save_dir
def costs_plot_alt(var='fuel demand (kWh)', **kwargs):

    df = kwargs['df']
    threshold = 0.0025
    ff_1_idx, ff_2_idx = get_two_thresholds(df, threshold, var)

    colors = color_list()
    plt.close()
    #y_max = 0.7
    y_max = 0.15
    matplotlib.rcParams["figure.figsize"] = (6.4, 4.8)
    fig, ax = plt.subplots()

    ax.set_xlabel(kwargs['x_label'])
    
    #ax.set_ylabel(r'cost (\$/kWh$_{LHV}$ or \$/kWh$_{e}$)')
    ax.set_ylabel(r'cost (\$/kWh$_{e}$)')


    # Electricity cost
    #ax.scatter(df[var], df['mean price ($/kWh)'], label=r'electricity cost (\$/kWh$_{e}$)', marker='v')
    ax.plot(df[var], df['mean price ($/kWh)'], label=r'marginal cost: firm electric load', color=colors[0])

    # Highlight transition region
    #ax.fill_between(df.loc[ff_1_idx:ff_2_idx, var], 0, y_max, color=colors[-1], alpha=0.15)
    #ax.fill_between(df.loc[ff_1_idx:ff_2_idx, var], 0, y_max, facecolor='none', edgecolor='gray', hatch='....', linewidth=0, alpha=0.5)
    ax.plot(df[var], df['mean price ($/kWh)'], label='_nolegend_', color=colors[0])
    #for ff, cost in zip(df[var], df['mean price ($/kWh)']):
    #    if round(ff, 2) == 0 or round(ff, 2) == 1:
    #        print('firm', ff, cost)

    ## $/GGE fuel line use Dual Value
    #ax.scatter(df[var], df['fuel price ($/kWh)'], label='total electrofuel\n'+r'cost (\$/kWh$_{LHV}$)')
    #ax.plot(df[var], df['fuel price ($/kWh)'], label='total electrofuel\n'+r'cost (\$/kWh$_{LHV}$)')

    tot_eff_fuel_process = EFFICIENCY_FUEL_ELECTROLYZER * EFFICIENCY_FUEL_CHEM_CONVERSION
    # Add the cost of electric power to the fuel load
    #ax.scatter(df[var], (df['fuel price ($/kWh)'] - f_tot) * tot_eff_fuel_process, label=r'fuel load electricity cost (\$/kWh$_{e}$)', marker='o')
    ax.plot(df[var], df['fuel_load_cost'], label=r'marginal cost: flexible load', color=colors[1])
    #for ff, cost in zip(df[var], df['fuel_load_cost']):
    #    if round(ff, 2) == 0 or round(ff, 2) == 1:
    #        print('flex', ff, cost)

    avg_elec_cost = df['mean price ($/kWh)'] * (1. - df[var]) + df['fuel_load_cost'] * df[var]
    ax.plot(df[var], avg_elec_cost, 'k--', label=r'system-wide cost', linewidth=2)
    #for ff, cost in zip(df[var], avg_elec_cost):
    #    if round(ff, 2) == 0 or round(ff, 2) == 1:
    #        print('mean', ff, cost)


    # Add vertical bars deliniating 3 regions:
    # 1) cheapest fuel cost --> +5%
    # 2) cheapest + 5% --> most expensive - 5%
    # 3) most expensive - 5% --> most expensive
    #if not 'Case0_NuclearFlatDemand' in save_dir:
    #    cheapest_fuel = df.loc[1, 'fuel price ($/kWh)']
    #    most_expensive_fuel = df.loc[len(df.index)-1, 'fuel price ($/kWh)']
    #    fuel_dem_split_1 = get_threshold(df, cheapest_fuel, 1.05, var)
    #    fuel_dem_split_2 = get_threshold(df, most_expensive_fuel, 0.95, var)
    #    print(f"\nSave dir {save_dir}, lower threshold {fuel_dem_split_1}, upper threshold {fuel_dem_split_2}")
    #    ax.plot(np.ones(100) * fuel_dem_split_1, np.linspace(0, y_max*.9, 100), 'k--', label='_nolegend_')
    #    ax.plot(np.ones(100) * fuel_dem_split_2, np.linspace(0, y_max*.9, 100), 'k--', label='_nolegend_')


    plt.xscale(kwargs['x_type'], nonposx='clip')
    if kwargs['x_type'] == 'log':
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(myLogFormat))

    if var == 'fuel demand (kWh)' or var == 'dispatch to fuel h2 storage (kW)':
        ax.set_xlim(df.loc[1, var], df.loc[len(df.index)-1, var])
    else:
        plt.xscale('linear')
        ax.set_xlim(0.0, 1.0)

    ax.set_ylim(0, y_max)
    ax.yaxis.set_ticks_position('both')
    #plt.grid()
    plt.legend(loc='upper left', framealpha = 1.0)


    #plt.tight_layout()
    fig.savefig(f'{kwargs["save_dir"]}{kwargs["save_name"]}.png')
    fig.savefig(f'{kwargs["save_dir"]}{kwargs["save_name"]}.pdf')
    print(f'{kwargs["save_dir"]}{kwargs["save_name"]}.png')





# Months on x-axis, avg curtailment on y, also deployment to H2 storage also
def plot_months_vs_curtailment_and_h2_storage(global_name, path, fuel_demands, save_name, save_dir):

    plt.close()
    matplotlib.rcParams['figure.figsize'] = (6,12)

    start = datetime(2016, 1, 1)
    print(f"Assumed starting date for plot_months_vs_curtailment_and_h2_storage: {start}")

    target_values = ['0.0kWh', '0.01kWh', '0.26628kWh', '10.20862kWh']

    # Set up for axes
    axs = []
    ax2s = []
    for j, target_val in enumerate(target_values):
        if j == 0:
            ax = plt.subplot(410+len(target_values))
        else:
            ax = plt.subplot(410+len(target_values)-j, sharex=axs[0])
            plt.setp(ax.get_xticklabels(), visible=False)
        ax.margins(0.1)
        axs.append(ax)

    files = glob(f'{path}{global_name}*.csv')
    for j, target_val in enumerate(target_values):
        df = 'x'
        for f in files:
            if target_val in f:
                df = pd.read_csv(f)
                break
        if type(df) == str:
            print(f"Missing a file for target value {target_val}")
            return

        axs[j].set_title(f'Fuel Demand: {target_val}')

        # FIXME - assume if len(df.index) == 8784 that we ran over all of 2016 (leap year)
        # else, return and code this later
        if len(df.index) != 8784:
            # Print colored
            print("\033[0;33mplot_months_vs_curtailment_and_h2_storage not currently coded to run over range other than all of 2016 leap year\033[0m")
            return

        # Make list of month values
        start_dt = start
        month_info = []
        for idx in df.index:
            month_info.append(start_dt.month)
            start_dt += timedelta(hours=1)
        month_info = np.array(month_info)

        
        axs[j].set_ylabel('Curtailment (kW)')


        months = [i for i in range(1, 13)]
        adj = 0.15
        alph=0.04
        max_ = 0.
        for tech, vals in {'nuclear':['red',0.], 'wind':['blue',-adj], 'solar':['orange',adj]}.items():
            axs[j].scatter(month_info+vals[1], df[f'cutailment {tech} (kW)'], color=vals[0], label=tech, alpha=alph)
            if max(df[f'cutailment {tech} (kW)']) > max_:
                max_ = max(df[f'cutailment {tech} (kW)'])
        axs[j].grid()
        axs[j].set_ylim(0, max_*1.1)

        # Second y-axis
        ax2 = axs[j].twinx()  # instantiate a second axes that shares the same x-axis
        ax2.set_ylabel('Dispatch to H2 Storage', color='brown')  # we already handled the x-label with ax1
        ax2.scatter(month_info+2*adj, df['dispatch to fuel h2 storage (kW)'], color='brown', label='Dispatch to H2 Storage', alpha=alph)
        ax2.tick_params(axis='y', labelcolor='brown')
        ax2.set_ylim(0, max(0.01, max(df['dispatch to fuel h2 storage (kW)']))*1.1)
        ax2s.append(ax2)

    plt.sca(axs[0])
    plt.xticks([i for i in range(1, 13)], ('January','February','March','April','May','June',
            'July','August','September','October','November','December'), rotation=30)

    #plt.tight_layout()
    #plt.legend()
    plt.gcf().savefig('{}/{}.png'.format(save_dir, save_name))
    matplotlib.rcParams["figure.figsize"] = (6.4, 4.8)


# Months on x-axis, avg curtailment on y, also deployment to H2 storage also
def plot_months_vs_curtailment_and_h2_storage_violin(global_name, path, fuel_demands, save_name, save_dir):

    plt.close()
    matplotlib.rcParams['figure.figsize'] = (6,12)

    start = datetime(2016, 1, 1)
    print(f"Assumed starting date for plot_months_vs_curtailment_and_h2_storage_violin: {start}")

    target_values = ['0.0kWh', '0.01kWh', '0.26628kWh', '10.20862kWh']

    # Set up for axes
    axs = []
    ax2s = []
    for j, target_val in enumerate(target_values):
        if j == 0:
            ax = plt.subplot(410+len(target_values))
        else:
            ax = plt.subplot(410+len(target_values)-j, sharex=axs[0])
            plt.setp(ax.get_xticklabels(), visible=False)
        ax.margins(0.1)
        axs.append(ax)

    files = glob(f'{path}{global_name}*.csv')
    for j, target_val in enumerate(target_values):
        df = 'x'
        for f in files:
            if target_val in f:
                df = pd.read_csv(f)
                break
        if type(df) == str:
            print(f"Missing a file for target value {target_val}")
            return

        axs[j].set_title(f'Fuel Demand: {target_val}')

        # FIXME - assume if len(df.index) == 8784 that we ran over all of 2016 (leap year)
        # else, return and code this later
        if len(df.index) != 8784:
            # Print colored
            print("\033[0;33mplot_months_vs_curtailment_and_h2_storage_violin not currently coded to run over range other than all of 2016 leap year\033[0m")
            return


        info = {'running': [], 'split': []}
        month_avgs = {
                'Wind': copy.deepcopy(info),
                'Solar': copy.deepcopy(info),
                'Nuclear': copy.deepcopy(info),
                'Dispatch to H2 Storage': copy.deepcopy(info)
        }

        prev_month = 1 # Start in January, this is not guaranteed, FIXME
        start_dt = start
        for idx in df.index:

            # Note there is a misspelling of 'curtailment' as 'cutailment' in the MEM-1.2 code long form output
            month_avgs['Nuclear']['running'].append(df.loc[idx, 'cutailment nuclear (kW)'])
            month_avgs['Wind']['running'].append(df.loc[idx, 'cutailment wind (kW)']) 
            month_avgs['Solar']['running'].append(df.loc[idx, 'cutailment solar (kW)'])
            month_avgs['Dispatch to H2 Storage']['running'].append(df.loc[idx, 'dispatch to fuel h2 storage (kW)'])

            start_dt += timedelta(hours=1)

            # If switching months, average previous, fill, and clear array
            if start_dt.month != prev_month:
                for k, vals in month_avgs.items():
                    vals['split'].append(copy.deepcopy(vals['running']))
                    vals['running'].clear()

            prev_month = start_dt.month

        axs[j].set_ylabel('Curtailment (kW)')


        months = [i for i in range(1, 13)]
        adj = 0.15
        alph=0.04
        max_ = 0.
        #for tech, vals in {'nuclear':['red',0.], 'wind':['blue',-adj], 'solar':['orange',adj]}.items():
        #    axs[j].scatter(month_info+vals[1], df[f'cutailment {tech} (kW)'], color=vals[0], label=tech, alpha=alph)
        #    if max(df[f'cutailment {tech} (kW)']) > max_:
        #        max_ = max(df[f'cutailment {tech} (kW)'])
        axs[j].grid()
        axs[j].set_ylim(0, max_*1.1)

        # Second y-axis
        ax2 = axs[j].twinx()  # instantiate a second axes that shares the same x-axis
        ax2.set_ylabel('Dispatch to H2 Storage', color='brown')  # we already handled the x-label with ax1
        parts = ax2.violinplot(month_avgs['Dispatch to H2 Storage']['split'], showmeans=True)

        # Color violin plot
        # List or parts: https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.violinplot.html
        for pc in parts['bodies']:
            pc.set_facecolor('brown')
            pc.set_edgecolor('brown')
            pc.set_alpha(0.3)
        for group in ['cmins', 'cmaxes', 'cbars', 'cmeans']:
            parts[group].set_facecolor('brown')
            parts[group].set_edgecolor('brown')
            if group != 'cmeans':
                parts[group].set_alpha(0.3)

        ax2.tick_params(axis='y', labelcolor='brown')
        ax2.set_ylim(0, max(0.01, max(df['dispatch to fuel h2 storage (kW)']))*1.1)
        ax2s.append(ax2)

    plt.sca(axs[0])
    plt.xticks([i for i in range(1, 13)], ('January','February','March','April','May','June',
            'July','August','September','October','November','December'), rotation=30)

    #plt.tight_layout()
    #plt.legend()
    plt.gcf().savefig('{}/{}.png'.format(save_dir, save_name))
    matplotlib.rcParams["figure.figsize"] = (6.4, 4.8)



def clean_files(path, global_name, results, case_file):
    files = get_output_file_names(path+'{}_2020'.format(global_name))
    print(files)

    # Try to read results, if Gurobi failed ungracefully, try running again
    # If it fails a second time, give up. (don't want to get stuck in some while loop
    # waiting for Gurobi to suceed on an impossible model)
    if len(files) == 0:
        print(f"ERROR: XXX Initial solve failed, trying again for {global_name} {case_file}")
        cnt = 0
        while cnt < 5:
            print(f"\n --- Entering retry loop: {cnt}\n")
            subprocess.call(["python", "Simple_Energy_Model.py", case_file])
            files = get_output_file_names(path+'{}_2020'.format(global_name))
            if len(files) > 0:
                break
            # Else retry up to 5 times
            cnt += 1
        if len(files) == 0:
            print(f"ERROR: XXXXXX All solves failed. Skipping {global_name} {case_file}")
            return

    # Copy output file
    if not os.path.exists(results):
        os.makedirs(results)
    move(files[-1], results)
    os.remove(case_file)
    return


def set_up_new_cfg(input_file, version, run, **settings):
    case_descrip = f'Run_{run:03}_fuelD'+str(round(settings['fuel_demand'],5))+'kWh'
    case_descrip += '_solarX'+str(round(settings['fixed_cost_solar'],4))
    case_descrip += '_windX'+str(round(settings['fixed_cost_wind'],4))
    case_descrip += '_ngccsX'+str(round(settings['fixed_cost_nat_gas_ccs'],4))
    case_descrip += '_battX'+str(round(settings['fixed_cost_storage'],4))
    case_descrip += '_electoX'+str(round(settings['fixed_cost_fuel_electrolyzer'],4))
    #case_descrip += '_elecEffX'+str(round(settings['efficiency_fuel_electrolyzer'],4))
    settings['case_descrip'] = case_descrip

    # 1st Step
    cfg = get_SEM_csv_file(input_file)
    case_name = version+'_'+case_descrip
    cfg = set_case_info(cfg, **settings)
    case_file = case_name+'.csv'
    write_file(case_file, cfg)
    return case_file



def make_scan_map(keys, ranges):

    assert(type(keys)==list and type(ranges)==list)
    assert(len(keys)==len(ranges))
    
    first = list(ranges.pop())
    first.sort(reverse=True)
    df = pd.DataFrame({keys.pop(): first})
    while True:
        df_orig = df.copy()
        if len(keys) == 0:
            break
        current_list = list(ranges.pop())
        current_list.sort(reverse=True)
        new_col = keys.pop()
        df[new_col] = current_list[-1]
        current_list = current_list[:-1]

        while True:
            if len(current_list) == 0:
                break
            to_app = df_orig.copy()
            to_app[new_col] = current_list[-1]
            current_list = current_list[:-1]
            df = df.append(to_app, ignore_index=True)

    return df


def get_vre_scan(start, end, num):
    return np.linspace(start, end, num)

if '__main__' in __name__:

    import sys
    print(f"\nRunning {sys.argv[0]}")
    print(f"Input arg list {sys.argv}")

    
    run_sem = False
    make_results_file = False
    make_plots = False
    if 'run_sem' in sys.argv:
        run_sem = True
    if 'make_results_file' in sys.argv:
        make_results_file = True
    if 'make_plots' in sys.argv:
        make_plots = True

    date = '20200209' # default
    case = 'Case6_NuclearWindSolarStorage' # default
    version = 'v3'
    multiplication_factor = 0.01 # default for step_size in new get_fuel_fractions method
    n_jobs = 1
    job_num = 1
    full_year = False # default to run over April only
    h2_only = False # if h2_only is True, costs for CO2, H2 storage, and chem plant are set to 1e-9
    fixed_solar = 1
    fixed_wind = 1
    fixed_electrolyzer = 1
    fixed_natGasCCS = 1
    include_PGP = False
    full_reliability = False
    for arg in sys.argv:
        if 'date' in arg:
            date = arg.split('_')[1]
        if 'Case' in arg:
            case = arg
        if 'version' in arg:
            version = arg.split('_')[1]
        if 'factor' in arg:
            multiplication_factor = float(arg.split('_')[1])
        if 'nJobs' in arg:
            n_jobs = int(arg.split('_')[1])
        if 'jobNum' in arg:
            job_num = int(arg.split('_')[1])
        if 'FULL_YEAR' in arg:
            full_year = True
        if 'H2_ONLY' in arg:
            h2_only = True
        if 'FIXED_SOLAR' in arg:
            fixed_solar = float(arg.split('_')[-1])
        if 'FIXED_WIND' in arg:
            fixed_wind = float(arg.split('_')[-1])
        if 'FIXED_ELECTROLYZER' in arg:
            fixed_electrolyzer = float(arg.split('_')[-1])
        if 'FIXED_NATGASCCS' in arg:
            fixed_natGasCCS = float(arg.split('_')[-1])
        if 'INCLUDE_PGP' in arg:
            include_PGP = True
        if 'FULL_RELIABILITY' in arg:
            full_reliability = True

    input_file = 'fuel_test_20201115_AllCases_EIAPrices.csv'
    #input_file = 'fuel_test_20200802_AllCases_EIAPrices_100PctReli.csv'
    if 'Case0' in case:
        input_file = 'fuel_test_20200302_Case0_NuclearFlatDemand.csv'
    version = f'{version}_{case}'
    global_name = 'fuel_test_{}_{}_{}_{}'.format(date, version, n_jobs, job_num)
    path = 'Output_Data/{}/'.format(global_name)
    results = path+'results/'
    results_search = 'Output_Data/fuel_test_{}_{}*/results/'.format(date, version)

    # Print settings:
    print(f'\nGlobal name                    {global_name}')
    print(f'Output path                    {path}')
    print(f'Results path                   {results}')
    print(f'Input File:                    {input_file}')
    print(f'Demand multiplication factor:  {round(multiplication_factor,3)}')
    print(f'H2_ONLY:                       {h2_only}')
    print(f'INCLUDE_PGP:                   {include_PGP}')
    print(f'FULL_RELIABILITY:              {full_reliability}')
    print(f'Number of jobs:                {n_jobs}')
    print(f'Job number:                    {job_num}')
    print(f'\n - RUN_SEM =          {run_sem}')
    print(f' - MAKE_RESULTS_FILE ={make_results_file}')
    print(f' - MAKE_PLOTS =       {make_plots}\n')


    # Efficiencies so I don't have to pull them from the cfgs for the moment, FIXME
    EFFICIENCY_FUEL_ELECTROLYZER=0.607 # Updated 4 March 2020 based on new values
    EFFICIENCY_FUEL_CHEM_CONVERSION=0.682

    ### DEFAULTS ###
    settings = {
        'global_name' : global_name,
        'do_demand_constraint' : True, # All true for now
        'do_renewable_scan' : False,
        'start_month' : 4,
        'end_month' : 4,
        'system_reliability' : -1, # Use 10 $/kWh
        'fixed_cost_solar' : 1 * fixed_solar,
        'fixed_cost_wind' : 1 * fixed_wind,
        'fixed_cost_nuclear' : 1,
        'fixed_cost_nat_gas_ccs' : -1,
        'fixed_cost_storage' : 1,
        'fixed_cost_fuel_electrolyzer' : 1 * fixed_electrolyzer,
        'efficiency_fuel_electrolyzer' : 1,
        'fuel_demand' : 1, # equal fuel output as electric demand
        'fuel_value' : 0,
        'fixed_cost_fuel_chem_plant' : 1,
        'fixed_cost_fuel_h2_storage' : 1,
        'var_cost_fuel_chem_plant' : 1,
        'var_cost_fuel_co2' : 1,
        'capacity_PGP_power' : 0, # fix to zero as default
    }
    if full_year:
        settings['start_month'] = 1
        settings['end_month'] = 12

    if include_PGP:
        settings['capacity_PGP_power'] = -1 # This will optimize the values

    if full_reliability:
        settings['system_reliability'] = 1 # 100% reliability


    # Adjust included techs based on desired case:
    if case == 'Case0_NuclearFlatDemand':
        settings['fixed_cost_solar'] = -1
        settings['fixed_cost_wind'] = -1
        settings['fixed_cost_storage'] = -1
    elif case == 'Case1_Nuclear':
        settings['fixed_cost_solar'] = -1
        settings['fixed_cost_wind'] = -1
        settings['fixed_cost_storage'] = -1
    elif case == 'Case2_NuclearStorage':
        settings['fixed_cost_solar'] = -1
        settings['fixed_cost_wind'] = -1
    elif case == 'Case3_WindStorage':
        settings['fixed_cost_solar'] = -1
        settings['fixed_cost_nuclear'] = -1
    elif case == 'Case4_SolarStorage':
        settings['fixed_cost_wind'] = -1
        settings['fixed_cost_nuclear'] = -1
    elif case == 'Case5_WindSolarStorage':
        settings['fixed_cost_nuclear'] = -1
    # Includes all by default
    #elif case == 'Case6_NuclearWindSolarStorage': # NatGas+CCS is off by default
    elif case == 'Case7_NatGasCCS':
        settings['fixed_cost_nuclear'] = -1
        settings['fixed_cost_nat_gas_ccs'] = 1 * fixed_natGasCCS
        settings['fixed_cost_solar'] = -1
        settings['fixed_cost_wind'] = -1
        settings['fixed_cost_storage'] = -1
    elif case == 'Case8_NatGasCCSStorage':
        settings['fixed_cost_nuclear'] = -1
        settings['fixed_cost_nat_gas_ccs'] = 1 * fixed_natGasCCS
        settings['fixed_cost_solar'] = -1
        settings['fixed_cost_wind'] = -1
    elif case == 'Case9_NatGasCCSWindSolarStorage':
        settings['fixed_cost_nuclear'] = -1
        settings['fixed_cost_nat_gas_ccs'] = 1 * fixed_natGasCCS
    else:
        print(f"Case {case} does not meet the defaults")

    # if h2_only is True, costs for CO2, H2 storage, and chem plant are set to 1e-9
    if h2_only:
        settings['fixed_cost_fuel_chem_plant'] = 1e-9
        settings['fixed_cost_fuel_h2_storage'] = 1e-9
        settings['var_cost_fuel_chem_plant'] = 1e-9
        settings['var_cost_fuel_co2'] = 1e-9

    vre_start = 0.1
    vre_end = 1.5
    vre_num = 20


 

    if run_sem:

        keys = []
        ranges = []

        if settings['do_renewable_scan']:
            vre_scan = get_vre_scan(vre_start, vre_end, vre_num)
            keys = ['fixed_cost_solar', 'fixed_cost_wind']
            ranges = [vre_scan, vre_scan]
            print("\nSetting output fuels as 10% of electric demand\n")
            settings['fuel_demand'] = 0.1
        else:
            keys = ['fuel_demand',]
            #ranges = [get_fuel_demands(0.01, 10, multiplication_factor),] # start, end, steps
            step_size = multiplication_factor
            total_eff = EFFICIENCY_FUEL_ELECTROLYZER * EFFICIENCY_FUEL_CHEM_CONVERSION
            fuel_dem = get_fuel_fractions(step_size, total_eff)
            fuel_dem = np.append(fuel_dem, [1e-6, 1e6, -1])
            fuel_dem.sort()
            ranges = [list(fuel_dem),]


        scan_map = make_scan_map(keys, ranges)
        print("Variables to scan")
        print(scan_map)
            
        # SEM runs per job
        # Make sure we always have an extra run per job to never lose jobs.
        # It is fine if the final job has fewer runs.
        runs_per_job = np.ceil(len(scan_map.index) / n_jobs)
        print(f'runs_per_job {runs_per_job}')
        min_job_idx = runs_per_job * job_num - runs_per_job
        max_job_idx = runs_per_job * job_num - 1
        print(f'min_job_idx {min_job_idx}')
        print(f'max_job_idx {max_job_idx}')


        for idx in scan_map.index:

            # Only run idx through SEM if it is the appropriate job
            if not (idx >= min_job_idx and idx <= max_job_idx):
                print(f'Skipping idx {idx}')
                continue

            print(f'Processing idx {idx}')

            for col in scan_map.columns:
                settings[col] = scan_map.loc[idx, col]

            # Deal with zero electricity case
            if scan_map.loc[idx, 'fuel_demand'] == -1:
                print(f"Fuel demand == -1 for idx {idx}")
                print(scan_map.loc[idx])
                settings['fuel_demand'] = 1e6
            
                # Set up new case file
                case_file = set_up_new_cfg(input_file.replace('.csv', '_ZERO_ELEC.csv'), version, idx, **settings)

            else:
                # Set up new case file
                case_file = set_up_new_cfg(input_file, version, idx, **settings)

            # Run MEM
            subprocess.call(["python", "Simple_Energy_Model.py", case_file])

            # Clean up working area and move files around
            clean_files(path, global_name, results, case_file)


    if make_results_file:
        base = os.getcwd()
        print(f'Checking path {base}/{results_search}')
        files = get_output_file_names(base+'/'+results_search+'fuel_test_*')
        results = get_results(files, global_name)

        # Add attribute energy use to renewable vs. dispatchable
        results_search2 = 'Output_Data/fuel_test_{}_{}*/fuel_test_{}_{}'.format(date, version, date, version)
        print(f"For detailed results from profiles checking {base+'/'+results_search2}")
        files = get_output_file_names(base+'/'+results_search2)
        df_name = 'resultsX/Results_{}.csv'.format(global_name)
        fixed = 'natgas_ccs'
        add_detailed_results(df_name, files, fixed)

    if not make_plots:
        print("Exit before plotting")
        exit()

    fixed = 'natgas_ccs'
    if case == 'Case5_WindSolarStorage':
        fixed = 'nuclear'
    print(f"\nPlotting using {fixed} as the dispatchable tech\n")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FormatStrFormatter
    df = pd.read_csv('resultsX/Results_{}_app.csv'.format(global_name), index_col=False)
    df = df.sort_values('fuel demand (kWh)', axis=0)
    df = df.reset_index()
    df['fuel load / available power'] = df['dispatch to fuel h2 storage (kW)'] / (
            df['dispatch wind (kW)'] + df['curtailment wind (kW)'] + 
            df['dispatch solar (kW)'] + df['curtailment solar (kW)'] + 
            df[f'dispatch {fixed} (kW)'] + df[f'curtailment {fixed} (kW)']
            )
    df['fuel load / total load OLD'] = df['dispatch to fuel h2 storage (kW)'] / (
            df['dispatch to fuel h2 storage (kW)'] + 1. # electric power demand = 1 
            )
    df['fuel load / total load'] = \
            (df['dispatch from fuel h2 storage chem plant (kW)'] / EFFICIENCY_FUEL_ELECTROLYZER) / \
            ( (df['dispatch from fuel h2 storage chem plant (kW)'] / EFFICIENCY_FUEL_ELECTROLYZER) + 1. # electric power demand = 1 
            )
    df.to_csv('resultsX/Results_{}_tmp.csv'.format(global_name))
    for i in range(len(df.index)):
        if df.loc[i, 'fuel demand (kWh)'] == 0.0 or df.loc[i, 'mean demand (kW)'] == 0.0:
            print(f"Dropping idx {i}: fuel {df.loc[i, 'fuel demand (kWh)']} elec {df.loc[i, 'mean demand (kW)']}")
            df = df.drop([i,])

    save_dir = f'./plots_{date}_{version}_PGPTest/'
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)


    # Make the scan plots first then assert(False)
    if settings['do_renewable_scan']:

        # VRE scanned values
        vre_scan = get_vre_scan(vre_start, vre_end, vre_num)
        print(vre_scan)

        ary = [[0 for _ in range(len(vre_scan))] for __ in range(len(vre_scan))]
        solar_costs = []
        wind_costs = []

        # Build solar and wind cost lists
        for idx in df.index:
            #print(idx, df.loc[idx,'case name'], df.loc[idx,'fuel price ($/kWh)']) 

            solar_c = df.loc[idx,'fixed cost solar ($/kW/h)']
            if solar_c not in solar_costs: solar_costs.append(solar_c)
            wind_c = df.loc[idx,'fixed cost wind ($/kW/h)']
            if wind_c not in wind_costs: wind_costs.append(wind_c)

        solar_costs.sort()
        wind_costs.sort()

        for idx in df.index:

            solar_c = df.loc[idx,'fixed cost solar ($/kW/h)']
            wind_c = df.loc[idx,'fixed cost wind ($/kW/h)']
            ary[ solar_costs.index(solar_c) ][ wind_costs.index(wind_c) ] = df.loc[idx,'fuel price ($/kWh)']

        ary2 = np.array(ary)
        fig, ax = plt.subplots()
        im = ax.imshow(ary2, origin='lower')

        round_wind_costs = [round(val,4) for val in wind_costs]
        round_solar_costs = [round(val,4) for val in solar_costs]

        plt.xticks(np.linspace(-0.5, len(round_wind_costs)-0.5, len(round_wind_costs)), round_wind_costs, rotation=90)
        plt.xlabel("Fixed Cost Wind ($/kW/h)")
        plt.yticks(np.linspace(-0.5, len(round_solar_costs)-0.5, len(round_solar_costs)), round_solar_costs)
        plt.ylabel("Fixed Cost Solar ($/kW/h)")
        cbar = ax.figure.colorbar(im)
        cbar.ax.set_ylabel("Fuel Cost ($/kWh)")
        #plt.tight_layout()
        plt.savefig(save_dir+f'renewables_scan_{len(vre_scan)}x{len(vre_scan)}.png')
        plt.clf()


        assert(False), "make_plots and do_renewable_scan only produce 2D scanning plots"



    ###########################################################################
    ###             PLOTTING                                                ###
    ###########################################################################

    # Stacked components
    # In PGP cases, distribute electrolyzer cost as a fraction of used H2 to each end use, same for storage
    f_elec = df['fixed cost fuel electrolyzer ($/kW/h)'] * df['capacity fuel electrolyzer (kW)'] * (df['dispatch from fuel h2 storage chem plant (kW)'] / df['dispatch from fuel h2 storage tot (kW)']) / df['fuel demand (kWh)']
    f_chem = df['fixed cost fuel chem plant ($/kW/h)'] * df['capacity fuel chem plant (kW)'] / df['fuel demand (kWh)']
    f_store = df['fixed cost fuel h2 storage ($/kWh/h)'] * df['capacity fuel h2 storage (kWh)'] * (df['dispatch from fuel h2 storage chem plant (kW)'] / df['dispatch from fuel h2 storage tot (kW)']) / df['fuel demand (kWh)']
    v_chem = df['var cost fuel chem plant ($/kW/h)'] * df['dispatch from fuel h2 storage chem plant (kW)'] * EFFICIENCY_FUEL_CHEM_CONVERSION / df['fuel demand (kWh)']
    v_co2 = df['var cost fuel co2 ($/kW/h)'] * df['dispatch from fuel h2 storage chem plant (kW)'] * EFFICIENCY_FUEL_CHEM_CONVERSION / df['fuel demand (kWh)']
    f_tot = f_elec+f_chem+f_store+v_chem+v_co2
    tot_eff_fuel_process = EFFICIENCY_FUEL_ELECTROLYZER * EFFICIENCY_FUEL_CHEM_CONVERSION
    df['fuel_load_cost'] = (df['fuel price ($/kWh)'] - f_tot) * tot_eff_fuel_process


    ### These should be defaults for all of them
    ### Reset them if needed
    idx_max = len(df.index)-1

    details = {
        #'fuel demand (kWh)': {
        #    'x_label' : 'fuel produced / electricity load',
        #    'app' : '_fuelDemDivElecDem',
        #    'x_lim' : [min(df['fuel demand (kWh)'].values[np.nonzero(df['fuel demand (kWh)'].values)]),
        #                max(df['fuel demand (kWh)'].values)],
        #    'x_type' : 'log',
        #    },
        #'fuel load / available power' : {
        #    'x_label' : 'fuel load / available power',
        #    'app' : '_fuelLoadDivAvailPower',
        #    'x_lim' : [0., 1.],
        #    'x_type' : 'linear',
        #    },
        'fuel load / total load' : {
            'x_label' : 'flexible load (kW) / total load (kW)',
            'app' : '',
            'x_lim' : [0., 1.],
            'x_type' : 'linear',
            },
        #'dispatch to fuel h2 storage (kW)' : {
        #    'x_label' : 'fuel load / electricity load',
        #    'app' : '_fuelLoadDivElecDem',
        #    'x_lim' : [min(df['dispatch to fuel h2 storage (kW)'].values[np.nonzero(df['dispatch to fuel h2 storage (kW)'].values)]),
        #                max(df['dispatch to fuel h2 storage (kW)'].values)],
        #    'x_type' : 'log',
        #    },
    }


    for k, m in details.items():

        kwargs = {}
        kwargs['df'] = df
        kwargs['save_dir'] = save_dir
        kwargs['stacked_min'] = m['x_lim'][0]
        kwargs['stacked_max'] = m['x_lim'][1]
        kwargs['x_vals'] = df[k]
        kwargs['x_label'] = m['x_label']
        kwargs['x_type'] = m['x_type']
        kwargs['x_var'] = k
        if h2_only:
            kwargs['h2_only'] = True


        #tot_load = df['dispatch to fuel h2 storage (kW)'] + 1. # electric power demand = 1 
        tot_load = (df['dispatch from fuel h2 storage chem plant (kW)'] / EFFICIENCY_FUEL_ELECTROLYZER) + 1. # electric power demand = 1 


        ### Fuel cost compare scatter and use to fill electricity costs in stacked
        kwargs['save_name'] = 'stackedCostPlot' + m['app']
        #costs_plot(k, **kwargs)
        kwargs['ALT'] = True
        costs_plot(k, **kwargs)
        del kwargs['ALT']
        kwargs['save_name'] = 'costPlot' + m['app']
        costs_plot_alt(k, **kwargs)
    


        ### Stacked dispatch fraction plot
        kwargs['save_name'] = 'stackedDispatchFraction' + m['app']
        tot_disp = df[f'dispatch {fixed} (kW)'] + \
                df['dispatch wind (kW)'] + \
                df['dispatch solar (kW)']
        kwargs['nuclear'] = df[f'dispatch {fixed} (kW)'] / tot_disp
        kwargs['wind'] = df['dispatch wind (kW)'] / tot_disp
        kwargs['solar'] = df['dispatch solar (kW)'] / tot_disp
        kwargs['y_label'] = 'fraction of dispatch'
        kwargs['legend_app'] = ''
        kwargs['ylim'] = [0, 1.2]
        stacked_plot(**kwargs)

        kwargs['save_name'] = 'stackedGenerationElecNorm' + m['app']
        kwargs['nuclear'] = df[f'dispatch {fixed} (kW)'] + df[f'curtailment {fixed} (kW)']
        kwargs['wind'] = df['dispatch wind (kW)'] + df['curtailment wind (kW)']
        kwargs['solar'] = df['dispatch solar (kW)'] + df['curtailment solar (kW)']
        kwargs['y_label'] = 'total available generation (kW) /\nfirm electric load (kW)'
        kwargs['legend_app'] = ''
        kwargs['ylim'] = [0, 5]
        stacked_plot(**kwargs)

    
        ### Stacked curtailment fraction plot
        del kwargs['nuclear']
        del kwargs['wind']
        del kwargs['solar']
        #kwargs['save_name'] = 'stackedEndUseFraction' + m['app']
        #tot_avail = df[f'dispatch {fixed} (kW)'] + df[f'curtailment {fixed} (kW)'] + \
        #        df['dispatch wind (kW)'] + df['curtailment wind (kW)'] + \
        #        df['dispatch solar (kW)'] + df['curtailment solar (kW)']
        #kwargs['nuclear_curt'] = df[f'curtailment {fixed} (kW)'] / tot_avail
        #kwargs['renewable_curt'] = (df['curtailment wind (kW)'] + df['curtailment solar (kW)']) / tot_avail
        #kwargs['battery_losses'] = (df['dispatch to storage (kW)'] - df['dispatch from storage (kW)']) / tot_avail
        #kwargs['fuel_load'] = df['dispatch to fuel h2 storage (kW)'] / tot_avail
        #kwargs['elec_load'] = 1. / tot_avail
        #kwargs['y_label'] = 'fraction of available power'
        #kwargs['legend_app'] = ''
        #kwargs['ylim'] = [0, 1.6]
        #stacked_plot(**kwargs)
        #del kwargs['nuclear_curt']
        #del kwargs['renewable_curt']
        #del kwargs['battery_losses']
        #del kwargs['fuel_load']
        #del kwargs['elec_load']

    
        ### Stacked curtailment fraction plot - new y-axis, Total Generation
        kwargs['save_name'] = 'stackedEndUseFractionTotGen' + m['app']
        kwargs['nuclear_curt'] = df[f'curtailment {fixed} (kW)'] / tot_load
        kwargs['renewable_curt'] = (df['curtailment wind (kW)'] + df['curtailment solar (kW)']) / tot_load
        kwargs['battery_losses'] = (df['dispatch to storage (kW)'] - df['dispatch from storage (kW)']) / tot_load
        #kwargs['fuel_load'] = df['dispatch to fuel h2 storage (kW)'] / tot_load
        kwargs['fuel_load'] = (df['dispatch from fuel h2 storage chem plant (kW)'] / EFFICIENCY_FUEL_ELECTROLYZER) / tot_load
        kwargs['elec_load'] = 1. / tot_load
        kwargs['y_label'] = 'total available generation (kW) / total load (kW)'
        kwargs['legend_app'] = ''
        kwargs['ylim'] = [0, 3]
        if 'Case1' in kwargs['save_dir']:
            kwargs['ylim'] = [0, 2]
        stacked_plot(**kwargs)
        ### Stacked curtailment fraction plot - new y-axis, Total Generation
        kwargs['save_name'] = 'stackedEndUseFractionTotGenAlt' + m['app']
        kwargs['nuclear_curt'] = df[f'curtailment {fixed} (kW)'] / tot_load
        kwargs['renewable_curt'] = (df['curtailment wind (kW)'] + df['curtailment solar (kW)']) / tot_load
        kwargs['battery_losses'] = (df['dispatch to storage (kW)'] - df['dispatch from storage (kW)']) / tot_load
        #kwargs['fuel_load'] = df['dispatch to fuel h2 storage (kW)'] / tot_load
        kwargs['fuel_load'] = (df['dispatch from fuel h2 storage chem plant (kW)'] / EFFICIENCY_FUEL_ELECTROLYZER) / tot_load
        kwargs['elec_load'] = 1. / tot_load
        kwargs['y_label'] = 'total available generation (kW) / total load (kW)'
        kwargs['legend_app'] = ''
        kwargs['ylim'] = [0, 3]
        kwargs['ALT'] = True
        kwargs['dem_renew_frac'] = df['dem_renew_frac']
        kwargs['electro_renew_frac'] = df['electro_renew_frac']
        if 'Case1' in kwargs['save_dir']:
            kwargs['ylim'] = [0, 2]
        stacked_plot(**kwargs)
        ### Stacked curtailment fraction plot - normalized by electric load
        #kwargs['save_name'] = 'stackedEndUseFractionTotGenAlt2' + m['app']
        #kwargs['nuclear_curt'] = df[f'curtailment {fixed} (kW)']
        #kwargs['renewable_curt'] = (df['curtailment wind (kW)'] + df['curtailment solar (kW)'])
        #kwargs['battery_losses'] = (df['dispatch to storage (kW)'] - df['dispatch from storage (kW)'])
        ##kwargs['fuel_load'] = df['dispatch to fuel h2 storage (kW)']
        #kwargs['fuel_load'] = (df['dispatch from fuel h2 storage chem plant (kW)'] / EFFICIENCY_FUEL_ELECTROLYZER)
        #kwargs['elec_load'] = np.ones(len(kwargs['x_vals']))
        #kwargs['y_label'] = 'total available generation (kW) / firm electric load (kW)'
        #kwargs['legend_app'] = ''
        #kwargs['ylim'] = [0, 6]
        #kwargs['ALT'] = True
        #kwargs['dem_renew_frac'] = df['dem_renew_frac']
        #kwargs['electro_renew_frac'] = df['electro_renew_frac']
        #if 'Case1' in kwargs['save_dir']:
        #    kwargs['ylim'] = [0, 2]
        #stacked_plot(**kwargs)
        del kwargs['nuclear_curt']
        del kwargs['renewable_curt']
        del kwargs['battery_losses']
        del kwargs['fuel_load']
        del kwargs['elec_load']
        del kwargs['dem_renew_frac']
        del kwargs['electro_renew_frac']
        del kwargs['ALT']

    
        # System capacities
        kwargs['y_type'] = 'linear'
        simple_plot_with_2nd_yaxis(df[k],
                [
                    df[f'capacity {fixed} (kW)'] / tot_load,
                    df['capacity wind (kW)'] / tot_load,
                    df['capacity solar (kW)'] / tot_load,
                    df['capacity storage (kWh)']/4. / tot_load,
                    df['capacity fuel electrolyzer (kW)'] / tot_load, 
                    df['capacity fuel chem plant (kW)'] / tot_load, 
                    df['capacity fuel h2 storage (kWh)'] / tot_load], # y
                ['dispatchable', 'wind', 'solar', 'battery storage',
                    'electrolyzer', 'chem plant', r'H$_{2}$ storage'], # labels
                'capacities / total load', r'H$_{2}$ storage capacity / total load (h)',
                'systemCapacities' + m['app'], **kwargs)
        del kwargs['y_type']

    
        # Fuel system capacities ratios
        tot_eff = EFFICIENCY_FUEL_ELECTROLYZER * EFFICIENCY_FUEL_CHEM_CONVERSION
        simple_plot_with_2nd_yaxis(df[k],
                # In PGP cases, distribute electrolyzer cost as a fraction of used H2 to each end use, same for storage
                [df['capacity fuel electrolyzer (kW)']*(df['dispatch from fuel h2 storage chem plant (kW)'] / df['dispatch from fuel h2 storage tot (kW)'])/df['fuel demand (kWh)'] * tot_eff, 
                    df['capacity fuel chem plant (kW)']/df['fuel demand (kWh)'] * tot_eff, 
                    df['capacity fuel h2 storage (kWh)']/df['fuel demand (kWh)'] * tot_eff], # y values
                ['electrolyzer', 'chem plant', r'H$_{2}$ storage'], # labels
                'capacity (kW) / fuel load (kW)', 'storage capacity (kWh) /\nfuel load (kW)',
                'ratiosFuelSystem' + m['app'], **kwargs)


        ## Fuel system capacity factor ratios
        ylims = [0.0, 1.]

        kwargs['df'] = df

        ## All system capacity factor ratios
        #kwargs['y_label'] = 'capacity factors'
        #simple_plot(df[k].values,
        #        [df['dispatch to fuel h2 storage (kW)'].values*EFFICIENCY_FUEL_ELECTROLYZER/df['capacity fuel electrolyzer (kW)'].values, 
        #            df['dispatch from fuel h2 storage (kW)'].values*EFFICIENCY_FUEL_CHEM_CONVERSION/df['capacity fuel chem plant (kW)'].values,
        #            df['fuel h2 storage (kWh)'].values/df['capacity fuel h2 storage (kWh)'].values,
        #            df[f'dispatch {fixed} (kW)'].values/df[f'capacity {fixed} (kW)'].values,
        #            df['dispatch wind (kW)'].values/df['capacity wind (kW)'].values,
        #            df['dispatch solar (kW)'].values/df['capacity solar (kW)'].values,
        #            df['energy storage (kWh)'].values/df['capacity storage (kWh)'].values,
        #            ], # y values 
        #        ['electrolyzer', 'chem plant', 'h2 storage',
        #            'dispatchable', 'wind', 'solar', 'battery\nstorage'], # labels
        #        'systemCFs' + m['app'], False, ylims, **kwargs)


        # EF system capacity factor ratios
        kwargs['y_label'] = 'capacity factor'
        simple_plot(df[k].values,
                [ df['dispatch to fuel h2 storage (kW)'].values*EFFICIENCY_FUEL_ELECTROLYZER/df['capacity fuel electrolyzer (kW)'].values, 
                    df['dispatch from fuel h2 storage chem plant (kW)'].values*EFFICIENCY_FUEL_CHEM_CONVERSION/df['capacity fuel chem plant (kW)'].values,
                    df['fuel h2 storage (kWh)'].values/df['capacity fuel h2 storage (kWh)'].values,
                    ], # y values 
                ['electrolysis facility', 'chemical plant', r'H$_{2}$ storage',], # labels
                'systemCFsEF' + m['app'], False, ylims, **kwargs)


        ## All system capacities
        #kwargs['y_label'] = 'capacity (kW) / total load (kW)'
        #logY = False
        #ylims=[0,2]
        #simple_plot(df[k],
        #        [#df['capacity fuel electrolyzer (kW)'], 
        #            #df['capacity fuel chem plant (kW)'],
        #            #df['capacity fuel h2 storage (kWh)'],
        #            df[f'capacity {fixed} (kW)'] / tot_load,
        #            df['capacity wind (kW)'] / tot_load,
        #            df['capacity solar (kW)'] / tot_load,
        #            df['capacity storage (kWh)']/4. / tot_load,
        #            ], # y values 
        #        [#'electrolyzer', 'chem plant', 'h2 storage',
        #            'dispatchable', 'wind', 'solar', 'battery\nstorage'], # labels
        #        'powerSystemCapacities' + m['app'], logY, ylims, **kwargs)


        # All system costs
        ylims=[0,.08]
        if 'Case1' in kwargs['save_dir']:
            ylims = [0, .12]
        kwargs['y_label'] = r'cost (\$/kWh$_{e}$ of total load)'
        logY = False
        simple_plot(df[k],
                [
                    df[f'capacity {fixed} (kW)'] * df[f'fixed cost {fixed} ($/kW/h)'] / tot_load,
                    df['capacity wind (kW)'] * df['fixed cost wind ($/kW/h)'] / tot_load,
                    df['capacity solar (kW)'] * df['fixed cost solar ($/kW/h)'] / tot_load,
                    df['capacity storage (kWh)'] * df['fixed cost storage ($/kWh/h)'] / tot_load,
                    ], # y values 
                [#'electrolyzer', 'chem plant', 'h2 storage',
                    'dispatchable', 'wind', 'solar', 'battery\nstorage'], # labels
                'powerSystemCosts' + m['app'], logY, ylims, **kwargs)


        # All system costs
        ylims=[5e-4,1]
        if 'Case1' in kwargs['save_dir']:
            ylims = [5e-4,1]
        kwargs['y_label'] = r'cost (\$/kWh$_{e}$ of electric load)'
        logY = True
        simple_plot(df[k],
                [
                    df[f'capacity {fixed} (kW)'] * df[f'fixed cost {fixed} ($/kW/h)'],
                    df['capacity wind (kW)'] * df['fixed cost wind ($/kW/h)'],
                    df['capacity solar (kW)'] * df['fixed cost solar ($/kW/h)'],
                    df['capacity storage (kWh)'] * df['fixed cost storage ($/kWh/h)'],
                    ], # y values 
                [#'electrolyzer', 'chem plant', 'h2 storage',
                    'dispatchable', 'wind', 'solar', 'battery\nstorage'], # labels
                'powerSystemCostsExp' + m['app'], logY, ylims, **kwargs)


        ## All system costs
        #kwargs['y_label'] = r'cost (\$/kWh$_{e}$ of total load)'
        #logY = False
        #ylims=[0,.12]
        #logY = True
        #ylims=[1e-5,10]
        #simple_plot(df[k],
        #        [
        #            df[f'capacity {fixed} (kW)'] * df[f'fixed cost {fixed} ($/kW/h)'] / tot_load,
        #            df['capacity wind (kW)'] * df['fixed cost wind ($/kW/h)'] / tot_load,
        #            df['capacity solar (kW)'] * df['fixed cost solar ($/kW/h)'] / tot_load,
        #            df['capacity storage (kWh)'] * df['fixed cost storage ($/kWh/h)'] / tot_load,
        #            df['capacity fuel electrolyzer (kW)'] * df['fixed cost fuel electrolyzer ($/kW/h)'] / tot_load, 
        #            df['capacity fuel chem plant (kW)'] * df['fixed cost fuel chem plant ($/kW/h)'] / tot_load, 
        #            df['capacity fuel h2 storage (kWh)'] * df['fixed cost fuel h2 storage ($/kWh/h)'] / tot_load
        #            ], # y
        #        [#'electrolyzer', 'chem plant', 'h2 storage',
        #            'dispatchable', 'wind', 'solar', 'battery\nstorage',
        #            'electrolyzer', 'chem plant', r'H$_{2}$ storage'], # labels
        #        'systemCosts' + m['app'], logY, ylims, **kwargs)


        ## Tot gen
        #ylims=[5e-2,1e2]
        #kwargs['y_label'] = 'mean total hourly generation (kW)'
        #simple_plot(df[k].values,
        #        [
        #            df[f'dispatch {fixed} (kW)'].values + df[f'curtailment {fixed} (kW)'].values,
        #            df['dispatch wind (kW)'].values + df['curtailment wind (kW)'].values,
        #            df['dispatch solar (kW)'].values + df['curtailment solar (kW)'].values,
        #            ], # y values 
        #        [#'electrolyzer', 'chem plant', 'h2 storage',
        #            'dispatchable', 'wind', 'solar'], # labels
        #        'powerSystemGen' + m['app'], True, ylims, **kwargs)


    
        ## This figure is covered by the new "stackedEndUseFraction" plot
        #### Stacked curtailment fraction plot
        #kwargs['save_name'] = 'stackedCurtailmentFraction' + m['app']
        #tot_avail = df[f'dispatch {fixed} (kW)'] + df[f'curtailment {fixed} (kW)'] + \
        #        df['dispatch wind (kW)'] + df['curtailment wind (kW)'] + \
        #        df['dispatch solar (kW)'] + df['curtailment solar (kW)']
        #kwargs['nuclear'] = df[f'curtailment {fixed} (kW)'] / tot_avail
        #kwargs['wind'] = df['curtailment wind (kW)'] / tot_avail
        #kwargs['solar'] = df['curtailment solar (kW)'] / tot_avail
        #kwargs['y_label'] = 'fraction of available power curtailed'
        #kwargs['legend_app'] = ''
        #kwargs['ylim'] = [0, 1.2]
        #stacked_plot(**kwargs)




    ## Relative curtailment based on available power
    ## This version factors out the wind CF of 0.43
    #nuclear = df[f'curtailment {fixed} (kW)']/df[f'capacity {fixed} (kW)']
    #wind = df['curtailment wind (kW)']/(df['curtailment wind (kW)']+df['dispatch wind (kW)'])
    #solar = df['curtailment solar (kW)']/(df['curtailment solar (kW)']+df['dispatch solar (kW)'])
    ##for idx, val in nuclear.items():
    ##    if np.isnan(nuclear.at[idx]):
    ##        nuclear.at[idx] = 0
    #simple_plot(save_dir, df['fuel demand (kWh)'].values,
    #        [nuclear.values, wind.values, solar.values], # y values 
    #        ['nuclear curtailment / capacity', 'wind curtailment / available power', 'solar curtailment / available power'], # labels
    #        'fuel demand (kWh)', 'curtailment of dispatch (kW) / available power (kW)', 
    #        'Relative Curtailment of Generation Capacities', 'ratiosCurtailmentDivAvailablePower')

    
    #print(df[['fuel demand (kWh)', 'fuel price ($/kWh)', 'mean price ($/kWh)', f'capacity {fixed} (kW)', 'capacity wind (kW)', 'capacity solar (kW)', 'dispatch wind (kW)', 'dispatch solar (kW)']])




    # Months on x-axis, avg curtailment on y, also deployment to H2 storage also
    #fuel_demands = get_fuel_demands(0.01, 10, 1.2) # start, end, steps
    #plot_months_vs_curtailment_and_h2_storage(global_name, path, fuel_demands, 'monthlyCurtailAndDisp', save_dir)
    #plot_months_vs_curtailment_and_h2_storage_violin(global_name, path, fuel_demands, 'monthlyCurtailAndDispViolin', save_dir)


    # Fuel price dual_value
    #ylims = [0.05, 1000]
    #simple_plot(save_dir, df['fuel demand (kWh)'].values, [df['mean price ($/kWh)'].values, df['max price ($/kWh)'].values, df['fuel price ($/kWh)'].values,], ['Mean Demand Dual ($/kWh)', 'Max Demand Dual ($/kWh)', 'Fuel Price Dual ($/kWh)',], 'fuel demand (kWh)', 'Dual Values ($/kWh)', 
    #        'fuel demand vs. dual values', 'fuelDemandVsDualValues', True, ylims)


    ## Curtailment vs. fuel cost with marker color as fuel fraction
    #tot_curtailment = (df[f'curtailment {fixed} (kW)'] + df['curtailment wind (kW)'] + \
    #        df['curtailment solar (kW)'])
    #        #/ (df[f'capacity {fixed} (kW)'] + df['capacity wind (kW)'] + \
    #        #df['capacity solar (kW)'])
    #biv_curtailment_cost_plot(tot_curtailment.loc[1:len(df.index)-1], \
    #        df['fuel price ($/kWh)'].loc[1:len(df.index)-1], df['fuel demand (kWh)'].loc[1:len(df.index)-1], \
    #        'Total Curtailment', save_dir, 'bivariateCurtailmentVsCostWithDemandMarkers')


    ## Curtailment vs. fuel cost with marker color as fuel fraction
    #tot_curtailment = (df[f'curtailment {fixed} (kW)'].fillna(0) + df['curtailment wind (kW)'].fillna(0) + \
    #        df['curtailment solar (kW)'].fillna(0)) / \
    #        (df[f'capacity {fixed} (kW)'].fillna(0) + df['capacity wind (kW)'].fillna(0) + \
    #        df['capacity solar (kW)'].fillna(0))
    #biv_curtailment_cost_plot(tot_curtailment.loc[1:len(df.index)-1], \
    #        df['fuel price ($/kWh)'].loc[1:len(df.index)-1], df['fuel demand (kWh)'].loc[1:len(df.index)-1], \
    #        'Total Curtailment/Total Capacity', save_dir, 'bivariateCurtailmentDivCapVsCostWithDemandMarkers')




    #### Stacked dispatch plot
    #kwargs['nuclear'] = df[f'dispatch {fixed} (kW)']
    #kwargs['wind'] = df['dispatch wind (kW)']
    #kwargs['solar'] = df['dispatch solar (kW)']
    #kwargs['y_label'] = 'normalized dispatch (kW)'
    #kwargs['legend_app'] = 'annual dispatch'
    #kwargs['save_name'] = 'stackedDispatchNormalized'
    #kwargs['logy'] = True
    #stacked_plot(**kwargs)
    #del kwargs['logy']



    #### Stacked generation capacity plot
    #kwargs['nuclear'] = df[f'capacity {fixed} (kW)']
    #kwargs['wind'] = df['capacity wind (kW)']
    #kwargs['solar'] = df['capacity solar (kW)']
    #kwargs['y_label'] = 'normalized capacity (kW)'
    #kwargs['legend_app'] = 'capacity'
    #kwargs['save_name'] = 'stackedCapacityNormalized'
    #kwargs['logy'] = True
    #stacked_plot(**kwargs)
    #del kwargs['logy']



    #### Stacked curtailment plot
    #kwargs['nuclear'] = df[f'curtailment {fixed} (kW)']
    #kwargs['wind'] = df['curtailment wind (kW)']
    #kwargs['solar'] = df['curtailment solar (kW)']
    #kwargs['y_label'] = 'curtailment of dispatch (kW)'
    #kwargs['legend_app'] = 'curtailment'
    #kwargs['save_name'] = 'stackedCurtailment'
    #stacked_plot(**kwargs)

    


    #### Stacked curtailment / capacity plot
    #kwargs['nuclear'] = df[f'curtailment {fixed} (kW)']/df[f'capacity {fixed} (kW)']
    #kwargs['wind'] = df['curtailment wind (kW)']/df['capacity wind (kW)']
    #kwargs['solar'] = df['curtailment solar (kW)']/df['capacity solar (kW)']
    #kwargs['nuclear'].fillna(value=0, inplace=True)
    #kwargs['wind'].fillna(value=0, inplace=True)
    #kwargs['solar'].fillna(value=0, inplace=True)
    ##kwargs['renewables'] = kwargs['wind'] + kwargs['solar']
    #kwargs['y_label'] = 'curtailment of dispatch / capacity'
    #kwargs['legend_app'] = 'curtailment/capacity'
    #kwargs['save_name'] = 'stackedCurtailmentDivCapacity'
    #stacked_plot(**kwargs)


    #### Stacked curtailment / dispatch plot
    #kwargs['nuclear'] = df[f'curtailment {fixed} (kW)']/df[f'dispatch {fixed} (kW)']
    #kwargs['wind'] = df['curtailment wind (kW)']/df['dispatch wind (kW)']
    #kwargs['solar'] = df['curtailment solar (kW)']/df['dispatch solar (kW)']
    #kwargs['nuclear'].fillna(value=0, inplace=True)
    #kwargs['wind'].fillna(value=0, inplace=True)
    #kwargs['solar'].fillna(value=0, inplace=True)
    ##kwargs['renewables'] = kwargs['wind'] + kwargs['solar']
    #kwargs['y_label'] = 'curtailment of dispatch / dispatch'
    #kwargs['legend_app'] = 'curtailment/dispatch'
    #kwargs['save_name'] = 'stackedCurtailmentDivDispatch'
    #kwargs['stacked_max'] = max(df['fuel demand (kWh)'].values)
    #stacked_plot(**kwargs)

    #simple_plot(save_dir, df['fuel demand (kWh)'].values,
    #        [df['dispatch to fuel h2 storage (kW)'].values*EFFICIENCY_FUEL_ELECTROLYZER/df['capacity fuel electrolyzer (kW)'].values, 
    #            df['dispatch from fuel h2 storage (kW)'].values*EFFICIENCY_FUEL_CHEM_CONVERSION/df['capacity fuel chem plant (kW)'].values,], # y values 
    #        ['electrolyzer capacity factor', 'chem plant capacity factor'], # labels
    #        'fuel demand (kWh)', 'Electrofuel system capacity factors', 
    #        'Electrofuel system capacity factors', 'ratiosFuelSystemCFsVsFuelCost', False, ylims)
