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
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import copy
from helpers import get_fuel_demands, get_fuel_fractions
from end_use_fractions import add_detailed_results
from analytic_fuels import kWh_to_GGE, kWh_LHV_per_kg_H2
matplotlib.rcParams.update({'font.size': 12.5})
matplotlib.rcParams.update({'lines.linewidth': 2})


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


def get_label(label):
    if 'nominal' in label:
        return 'baseline'
    if '75%' in label:
        return '75% baseline'
    if '50%' in label:
        return '50% baseline'
    else:
        return label



# Poorly written, the args are all required and are below.
#save_name, save_dir
def costs_plot_alt_sensitivity(tgt_shifts, var='fuel demand (kWh)', **kwargs):
    cases = {
            0 : 'Case7_NatGasCCS',
            1 : 'Case9_NatGasCCSWindSolarStorage',
            2 : 'Case5_WindSolarStorage',
            }

    dfs = kwargs['dfs']

    colors = color_list()
    plt.close()
    y_max = 0.13
    fig, axs = plt.subplots(ncols=3, nrows=len(tgt_shifts), figsize=(9,1+2.*len(tgt_shifts)), sharey=True)
    if len(tgt_shifts) == 1:
        axs_new = [[]]
        for ax in axs:
            axs_new[0].append(ax)
        axs = axs_new

    

    line_types = ['solid', (0, (1, 1)), (0, (2, 1)), (0, (3, 3)), (0, (5, 5)),
            (0, (3, 1, 1, 1)),
            (0, (3, 1, 1, 1, 1, 1)),
            ]

    for j, tgt_shift in enumerate(tgt_shifts):
        for i in range(3):
            axs[j][i].set_xlim(0.0, 1.0)
            axs[j][i].xaxis.set_major_locator(matplotlib.ticker.FixedLocator([0.0, 0.2, 0.4, 0.6, 0.8, 1.0]))
            axs[j][i].set_ylim(0, y_max)
            axs[j][i].yaxis.set_ticks_position('both')
            axs[j][i].yaxis.set_major_locator(matplotlib.ticker.FixedLocator([0.00, 0.025, 0.050, 0.075, 0.100]))
            cnt = 0
            axs[j][i].plot([], [], label=r'$\bf{firm\ load}$', color='white', linewidth=0)
            for shift, df in dfs[cases[i]].items():
                if shift != 'nominal' and tgt_shift not in shift:
                    continue
                # Electricity cost
                axs[j][i].plot(df[var], df['mean price ($/kWh)'], linestyle=line_types[cnt], label=get_label(shift), color=colors[0])
                cnt += 1

            cnt = 0
            axs[j][i].plot([], [], label=r'$\bf{flexible\ load}$', color='white', linewidth=0)
            for shift, df in dfs[cases[i]].items():
                if not (shift == 'nominal' or tgt_shift in shift):
                    continue
                tot_eff_fuel_process = EFFICIENCY_FUEL_ELECTROLYZER * EFFICIENCY_FUEL_CHEM_CONVERSION
                # Add the cost of electric power to the fuel load
                axs[j][i].plot(df[var], df['fuel_load_cost'], linestyle=line_types[cnt], label=get_label(shift), color=colors[1])
                cnt += 1

            cnt = 0
            axs[j][i].plot([], [], label=r'$\bf{average\ cost}$', color='white', linewidth=0)
            for shift, df in dfs[cases[i]].items():
                if not (shift == 'nominal' or tgt_shift in shift):
                    continue
                avg_elec_cost = df['mean price ($/kWh)'] * (1. - df[var]) + df['fuel_load_cost'] * df[var]
                axs[j][i].plot(df[var], avg_elec_cost, linestyle=line_types[cnt], label=get_label(shift), color='black')
                cnt += 1


    for j in range(len(tgt_shifts)):
        axs[j][0].set_ylabel(r'cost (\$/kWh$_{e}$)')
    axs[-1][1].set_xlabel(kwargs['x_label'])
    alphas = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']
    cnt = 0
    font = {
        'weight': 'bold',
        }
    horiz = -0.08
    vert = 0.115
    vert = 0.11 if len(tgt_shifts) == 1 else 0.115
    for j, shift in enumerate(tgt_shifts):
        for i in range(3):
            axs[j][i].text(horiz, vert, f'{alphas[cnt]}', fontdict=font)
            cnt += 1
            if i < 2:
                axs[j][i].text(0.08, y_max * (.107/.12), f'$\Delta$ {shift}', ha='left', va='center')
            else:
                axs[j][i].text(0.95, y_max * (.107/.12), f'$\Delta$ {shift}', ha='right', va='center')
    axs[0][0].set_title("Dispatch")
    axs[0][1].set_title("Dispatch+Renew+Storage")
    axs[0][2].set_title("Renew+Storage")


    horiz = 0.4
    vert = 1.64 if len(tgt_shifts) == 1 else -.35
    axs[-1][1].legend(ncol=3, loc='upper center', framealpha = 1.0, bbox_to_anchor=(horiz, vert))
    #plt.tight_layout()

    t = 0.68 if len(tgt_shifts) == 1 else 0.96
    b = 0.15 if len(tgt_shifts) == 1 else 0.23
    plt.subplots_adjust(top=t, left=.1, bottom=b, right=.95)


    fig.savefig(f'{kwargs["save_dir"]}{kwargs["save_name"]}.png')
    fig.savefig(f'{kwargs["save_dir"]}{kwargs["save_name"]}.pdf')
    print(f'{kwargs["save_dir"]}{kwargs["save_name"]}.png')



def costs_plot_h2_sensitivity(tgt_shifts, var='fuel demand (kWh)', **kwargs):

    # Only for H2 cost plots
    conversion = kWh_LHV_per_kg_H2 # Convert for main y-axis
    conversion *= EFFICIENCY_FUEL_CHEM_CONVERSION # The cost is set based on liquid hydrocarbon
    conversion_div_eff_electro = conversion / EFFICIENCY_FUEL_ELECTROLYZER # The cost is set based on liquid hydrocarbon
    conversion_div_eff_electro = kWh_LHV_per_kg_H2 / EFFICIENCY_FUEL_ELECTROLYZER # The cost is set based on liquid hydrocarbon
    #tot_eff_fuel_process = EFFICIENCY_FUEL_ELECTROLYZER * EFFICIENCY_FUEL_CHEM_CONVERSION
    
    cases = {
            0 : 'Case7_NatGasCCS',
            1 : 'Case9_NatGasCCSWindSolarStorage',
            2 : 'Case5_WindSolarStorage',
            }

    dfs = kwargs['dfs']

    colors = color_list()
    plt.close()
    y_max = 8
    fig, axs = plt.subplots(ncols=3, nrows=len(tgt_shifts), figsize=(9,1+2.*len(tgt_shifts)), sharey=True)
    if len(tgt_shifts) == 1:
        axs_new = [[]]
        for ax in axs:
            axs_new[0].append(ax)
        axs = axs_new
    

    line_types = ['solid', (0, (1, 1)), (0, (2, 1)), (0, (3, 3)), (0, (5, 5)),
            (0, (3, 1, 1, 1)),
            (0, (3, 1, 1, 1, 1, 1)),
            ]

    for j, tgt_shift in enumerate(tgt_shifts):
        for i in range(3):
            axs[j][i].set_xlim(0.0, 1.0)
            axs[j][i].xaxis.set_major_locator(matplotlib.ticker.FixedLocator([0.0, 0.2, 0.4, 0.6, 0.8, 1.0]))
            axs[j][i].set_ylim(0, y_max)
            axs[j][i].yaxis.set_major_locator(matplotlib.ticker.FixedLocator([0, 2, 4, 6]))
            axs[j][i].yaxis.set_ticks_position('both')
            cnt = 0
            axs[j][i].plot([], [], label=r'$\bf{electrolysis\ facility}$'+'\n'+r'$\bf{capacity}$', color='white', linewidth=0)
            for shift, df in dfs[cases[i]].items():
                if shift != 'nominal' and tgt_shift not in shift:
                    continue
                # CapEx electrolysis plant
                f_elec = df['fixed cost fuel electrolyzer ($/kW/h)'] * df['capacity fuel electrolyzer (kW)'] / df['fuel demand (kWh)']
                f_elec *= conversion
                axs[j][i].plot(df[var], f_elec, linestyle=line_types[cnt], label=get_label(shift), color=colors[0])
                cnt += 1

            cnt = 0
            axs[j][i].plot([], [], label=r'$\bf{total\ hydrogen}$'+'\n'+r'$\bf{production\ cost}$', color='white', linewidth=0)
            for shift, df in dfs[cases[i]].items():
                if not (shift == 'nominal' or tgt_shift in shift):
                    continue
                # perfect market power cost
                #axs[j][i].plot(df[var], df['fuel price ($/kWh)'] * conversion, linestyle=line_types[cnt], label=f'flexible load: {shift}', color=colors[1])
                f_elec = df['fixed cost fuel electrolyzer ($/kW/h)'] * df['capacity fuel electrolyzer (kW)'] / df['fuel demand (kWh)']
                f_elec *= conversion
                axs[j][i].plot(df[var], f_elec + df['fuel_load_cost'] * conversion_div_eff_electro, linestyle=line_types[cnt], label=get_label(shift), color=colors[1])
                cnt += 1

            #cnt = 0
            #axs[j][i].plot([], [], label=r'$\bf{hydrogen\ total}$'+'\n'+r'$\bf{(average\ cost)}$', color='white', linewidth=0)
            #for shift, df in dfs[cases[i]].items():
            #    if not (shift == 'nominal' or tgt_shift in shift):
            #        continue
            #    f_elec = df['fixed cost fuel electrolyzer ($/kW/h)'] * df['capacity fuel electrolyzer (kW)'] / df['fuel demand (kWh)']
            #    f_elec *= conversion
            #    avg_elec_cost = df['mean price ($/kWh)'] * (1. - df[var]) + df['fuel_load_cost'] * df[var]
            #    axs[j][i].plot(df[var], f_elec + avg_elec_cost * conversion_div_eff_electro, linestyle=line_types[cnt], label=get_label(shift), color='black')
            #    cnt += 1


    for j in range(len(tgt_shifts)):
        axs[j][0].set_ylabel(r'cost (\$/kg$_{H2}$)')
    axs[-1][1].set_xlabel(kwargs['x_label'])
    alphas = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']
    cnt = 0
    font = {
        'weight': 'bold',
        }
    horiz = -0.1
    #vert = 0.11 if len(tgt_shifts) == 1 else y_max * 0.95
    vert = y_max * 0.9
    h2 = -0.2
    for j, shift in enumerate(tgt_shifts):
        for i in range(3):
            h = h2 if i == 0 else horiz
            axs[j][i].text(horiz, vert, f'{alphas[cnt]}', fontdict=font)
            cnt += 1
            if i < 2:
                axs[j][i].text(0.08, y_max * (.107/.12), f'$\Delta$ {shift}', ha='left', va='center')
            else:
                axs[j][i].text(0.95, y_max * (.107/.12), f'$\Delta$ {shift}', ha='right', va='center')
    axs[0][0].set_title("Dispatch")
    axs[0][1].set_title("Dispatch+Renew+Storage")
    axs[0][2].set_title("Renew+Storage")



    # 2nd y-axis for $/kWh_e
    ax2s = [[None for __ in range(3)] for _ in range(len(tgt_shifts))]
    for j, shift in enumerate(tgt_shifts):
        for i in reversed(range(3)):
            ax2s[j][i] = axs[j][i].twinx()  # instantiate a second axes that shares the same x-axis
            ax2s[j][i].set_ylim(0, axs[j][i].get_ylim()[1] / kWh_to_GGE)
            #ax2s[j][i].yaxis.set_ticks_position('right')
            if i < 2:
                ax2s[j][i].set_yticklabels([])
            if i == 2:
                ax2s[j][2].set_ylabel(r'cost (\$/kWh$_{LHV}$)')

    horiz = 0.5
    vert = 1.96 if len(tgt_shifts) == 1 else -0.33
    axs[-1][1].legend(ncol=2, loc='upper center', framealpha = 1.0, bbox_to_anchor=(horiz, vert))
    #plt.tight_layout()

    t = 0.59 if len(tgt_shifts) == 1 else 0.96
    b = 0.15 if len(tgt_shifts) == 1 else 0.23
    plt.subplots_adjust(top=t, left=.08, bottom=b, right=.9)




    fig.savefig(f'{kwargs["save_dir"]}{kwargs["save_name"]}.png')
    fig.savefig(f'{kwargs["save_dir"]}{kwargs["save_name"]}.pdf')
    print(f'{kwargs["save_dir"]}{kwargs["save_name"]}.png')



def prep_csv(case, f_name_base):
    fixed = 'natgas_ccs'
    if case == 'Case5_WindSolarStorage':
        fixed = 'nuclear'
    df = pd.read_csv(f'results_files/cost_sensitivity/{f_name_base}.csv', index_col=False)
    print(f'results_files/cost_sensitivity/{f_name_base}.csv')
    df = df.sort_values('fuel demand (kWh)', axis=0)
    df = df.reset_index()
    df['fuel load / available power'] = df['dispatch to fuel h2 storage (kW)'] / (
            df['dispatch wind (kW)'] + df['curtailment wind (kW)'] + 
            df['dispatch solar (kW)'] + df['curtailment solar (kW)'] + 
            df[f'dispatch {fixed} (kW)'] + df[f'curtailment {fixed} (kW)']
            )
    df['fuel load / total load'] = df['dispatch to fuel h2 storage (kW)'] / (
            df['dispatch to fuel h2 storage (kW)'] + 1. # electric power demand = 1 
            )

    # Stacked components
    f_elec = df['fixed cost fuel electrolyzer ($/kW/h)'] * df['capacity fuel electrolyzer (kW)'] / df['fuel demand (kWh)']
    f_chem = df['fixed cost fuel chem plant ($/kW/h)'] * df['capacity fuel chem plant (kW)'] / df['fuel demand (kWh)']
    f_store = df['fixed cost fuel h2 storage ($/kWh/h)'] * df['capacity fuel h2 storage (kWh)'] / df['fuel demand (kWh)']
    v_chem = df['var cost fuel chem plant ($/kW/h)'] * df['dispatch from fuel h2 storage (kW)'] * EFFICIENCY_FUEL_CHEM_CONVERSION / df['fuel demand (kWh)']
    v_co2 = df['var cost fuel co2 ($/kW/h)'] * df['dispatch from fuel h2 storage (kW)'] * EFFICIENCY_FUEL_CHEM_CONVERSION / df['fuel demand (kWh)']
    f_tot = f_elec+f_chem+f_store+v_chem+v_co2
    tot_eff_fuel_process = EFFICIENCY_FUEL_ELECTROLYZER * EFFICIENCY_FUEL_CHEM_CONVERSION
    df['fuel_load_cost'] = (df['fuel price ($/kWh)'] - f_tot) * tot_eff_fuel_process

    for i in range(len(df.index)):
        if df.loc[i, 'fuel demand (kWh)'] == 0.0 or df.loc[i, 'mean demand (kW)'] == 0.0:
            print(f"Dropping idx {i}: fuel {df.loc[i, 'fuel demand (kWh)']} elec {df.loc[i, 'mean demand (kW)']}")
            df = df.drop([i,])
    df = df.reset_index()

    df.to_csv(f'results_files/cost_sensitivity/{f_name_base}_tmp.csv', index=False)



# HERE


# Efficiencies so I don't have to pull them from the cfgs for the moment, FIXME
EFFICIENCY_FUEL_ELECTROLYZER=0.607 # Updated 4 March 2020 based on new values
EFFICIENCY_FUEL_CHEM_CONVERSION=0.682

date = '20200826'
f_map = {
        'Case7_NatGasCCS' : {
            'version' : 'v2',
            'shifts' : {
                'nominal' : '',
                'electrolysis plant 75%' : 'EL0.75',
                'electrolysis plant 50%' : 'EL0.5',
                'dispatchable 75%' : 'NG0.75',
                'dispatchable 50%' : 'NG0.5',
            },
        },
        'Case5_WindSolarStorage' : {
            'version' : 'v3',
            'shifts' : {
                'nominal' : '',
                'electrolysis plant 75%' : 'EL0.75',
                'electrolysis plant 50%' : 'EL0.5',
                'wind 75%' : 'WIND0.75',
                'wind 50%' : 'WIND0.5',
                'solar 75%' : 'SOL0.75',
                'solar 50%' : 'SOL0.5',
            },
        },
        'Case9_NatGasCCSWindSolarStorage' : {
            'version' : 'v4',
            'shifts' : {
                'nominal' : '',
                'electrolysis plant 75%' : 'EL0.75',
                'electrolysis plant 50%' : 'EL0.5',
                'wind 75%' : 'WIND0.75',
                'wind 50%' : 'WIND0.5',
                'solar 75%' : 'SOL0.75',
                'solar 50%' : 'SOL0.5',
                'dispatchable 75%' : 'NG0.75',
                'dispatchable 50%' : 'NG0.5',
            },
        },
}
prep_CSV = True
prep_CSV = False

plot = True
#plot = False

if prep_CSV:
    print("\nPreparing the csvs")
    for case, info in f_map.items():
        print(f"\n{case}")
        for shift, tag in info['shifts'].items():
            print(f"Shift: {shift}, tag {tag}")
            f_name_base = f"Results_fuel_test_{date}_{info['version']}{tag}_{case}_1_1"
            prep_csv(case, f_name_base)

    
if plot:

    print("\nPreparing the csvs")
    m = {
            'x_label' : 'flexible load (kW) / total load (kW)',
            'x_lim' : [0., 1.],
            'x_type' : 'linear',
    }

    var = 'fuel load / total load'

    df_map = OrderedDict()
    for case, info in f_map.items():
        print(f"\n{case}")
        df_map[case] = OrderedDict()
        for shift, tag in info['shifts'].items():
            print(f"Shift: {shift}, tag {tag}")
            f_name_base = f"Results_fuel_test_{date}_{info['version']}{tag}_{case}_1_1"
            df = pd.read_csv(f'results_files/cost_sensitivity/{f_name_base}_tmp.csv', index_col=False)
            print(f'results_files/cost_sensitivity/{f_name_base}_tmp.csv')
            df_map[case][shift] = df



    save_dir = f'./plots_{date}_sensitivity_XXX/'
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)


    kwargs = {}
    kwargs['dfs'] = df_map
    kwargs['save_dir'] = save_dir
    kwargs['stacked_min'] = m['x_lim'][0]
    kwargs['stacked_max'] = m['x_lim'][1]
    kwargs['x_vals'] = df[var]
    kwargs['x_label'] = m['x_label']
    kwargs['x_type'] = m['x_type']
    kwargs['x_var'] = var


    tot_load = df['dispatch to fuel h2 storage (kW)'] + 1. # electric power demand = 1 


    ### Fuel cost compare scatter and use to fill electricity costs in stacked
    #kwargs['save_name'] = 'stackedCostPlot' + m['app']
    #costs_plot(var, **kwargs)
    #kwargs['ALT'] = True
    #costs_plot(var, **kwargs)
    #del kwargs['ALT']

    shifts = ['dispatchable', 'wind', 'solar', 'electrolysis plant']
    kwargs['save_name'] = f'costPowerSensitivity_ALL'
    costs_plot_alt_sensitivity(shifts, var, **kwargs)
    kwargs['save_name'] = f'costH2Sensitivity_ALL'
    costs_plot_h2_sensitivity(shifts, var, **kwargs)
    #for shift in shifts:
    #    kwargs['save_name'] = f'costPowerSensitivity_{shift}'
    #    costs_plot_alt_sensitivity([shift,], var, **kwargs)
    #    kwargs['save_name'] = f'costH2Sensitivity_{shift}'
    #    costs_plot_h2_sensitivity([shift,], var, **kwargs)




