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
matplotlib.rcParams.update({'font.size': 12.})
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



def electro_cf_by_X(save, **kwargs):

    if 'by_month' in save:
        n = 12
        key = 'month'
    elif 'by_hour' in save:
        n = 24
        key = 'hour'
    else:
        print("\nFix your naming for electro_cf_by_X !!!")
        exit()

    plt.close()
    fig, axs = plt.subplots(figsize=(9, 3*.95), ncols=3, sharey=True)

    ims = []
    css = []
    for i, c in enumerate(cases):

        #ary = []
        #for idx in dfs[c].index:
        #    ary.append([])
        #    for i in range(n):
        #        ary[-1].
        cols = []
        for j in range(n):
            cols.append(f'electro_cf_{key}_{j}')
        m = dfs[c][cols]

        n_levels = np.arange(0,1,.1)
        c_fmt = '%1.1f'

        # transform to CST (UTC-6) from UTC
        if key == 'hour':
            new_cols = []
            for k in range(24):
                new_cols.append(f'electro_cf_hour_{(k+6)%24}')
            m2 = m[new_cols]
            im = axs[i].imshow(m2.T, aspect='auto', interpolation='none', origin='lower', vmax=1, vmin=0)
            cs = axs[i].contour(m2.T, n_levels, colors='k', linewidths=1)

        else:
            im = axs[i].imshow(m.T, aspect='auto', interpolation='none', origin='lower', vmax=1, vmin=0)
            cs = axs[i].contour(m.T, n_levels, colors='k', linewidths=1)


        ims.append(im)


        css.append(cs)
        # inline labels
        axs[i].clabel(cs, inline=1, fontsize=12, fmt=c_fmt)
        
        if key == 'hour':
            axs[i].set_title(names[c], **{'fontsize':12.5})




    if key == 'month':
        axs[0].set_yticklabels(('', 'Jan','Mar','May',
                'July','Sept','Nov'))
        axs[1].set_xlabel(kwargs['x_label'])
    if key == 'hour':
        axs[0].set_ylabel('hour of day (CST)')
    
    for i in range(3):
        axs[i].xaxis.set_major_locator(matplotlib.ticker.FixedLocator([0, 20, 40, 60, 80, 100]))
        if key == 'month':
            axs[i].set_xticklabels(['0.0', '0.2', '0.4', '0.6', '0.8', '1.0'])
        else:
            axs[i].set_xticklabels([])

    for i, c in enumerate(cases):

        #axs[i].set_title(names[c], **{'fontsize':12.5})
        add = 3 if key == 'month' else 0
        vert = 10 if key == 'month' else 21
        axs[i].text(5, vert, f'{alphas[i+add]}', fontdict=font)


    adj = 0.07
    t_adj = 0 if key == 'hour' else adj
    b_adj = adj if key == 'hour' else 0
    fig.subplots_adjust(right=0.86)
    cbar_ax = fig.add_axes([0.88, 0.17 - b_adj, 0.02, 1.-.17-.11+adj])
    cbar = fig.colorbar(ims[0], cax=cbar_ax)
    #cbar = axs[2].figure.colorbar(ims[2])
    cbar.ax.set_ylabel(f"electrolysis facility\ncapacity factor")

    #plt.subplots_adjust(top=.89, left=.11, bottom=.17, right=.91)
    # by hour gets title, by month gets x-axis labels
    plt.subplots_adjust(top=.89 + t_adj, left=.07, bottom=.17 - b_adj)
    fig.savefig('{}/{}2.png'.format(kwargs['save_dir'], save))
    fig.savefig('{}/{}2.pdf'.format(kwargs['save_dir'], save))

def simple_plot(save, logY=False, ylims=[-1,-1], **kwargs):

    plt.close()
    fig, axs = plt.subplots(figsize=(9, 3), ncols=3, sharey=True)

    colors = color_list()

    axs[0].set_ylabel(kwargs['y_label'])
    axs[1].set_xlabel(kwargs['x_label'])

    for i, c in enumerate(cases):

        #axs[i].set_title(names[c], **{'fontsize':12.5})
        add = 3 if save == 'systemCFsEF' else 0
        axs[i].text(horiz, ylims[1]*vert, f'{alphas[i+add]}', fontdict=font)
    
        axs[i].plot(dfs[c]['fuel load / total load'], dfs[c]['dispatch to fuel h2 storage (kW)']*EFFICIENCY_FUEL_ELECTROLYZER/dfs[c]['capacity fuel electrolyzer (kW)'],
                label='electrolysis facility', color=colors[1])
        if not 'h2_only' in kwargs.keys():
            axs[i].plot(dfs[c]['fuel load / total load'], dfs[c]['dispatch from fuel h2 storage (kW)']*EFFICIENCY_FUEL_CHEM_CONVERSION/dfs[c]['capacity fuel chem plant (kW)'],
                    label='chemical plant', color=colors[0])
            axs[i].plot(dfs[c]['fuel load / total load'], dfs[c]['fuel h2 storage (kWh)']/dfs[c]['capacity fuel h2 storage (kWh)'],
                    label=r'H$_{2}$ storage', color=colors[6])

        if ylims != [-1,-1]:
            axs[i].set_ylim(ylims[0], ylims[1])
        
        plt.xscale('linear')
        axs[i].set_xlim(0.0, 1.0)
        axs[i].yaxis.set_ticks_position('both')

        if 'systemCFsEF' in save:
            axs[i].yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(xmax=1, decimals=0))
            axs[i].set_ylabel(axs[i].get_ylabel(), labelpad=-2)
    #    plt.legend(ncol=2, loc='lower left', framealpha = 1.0)
    plt.subplots_adjust(top=.89, left=.11, bottom=.17, right=.91)
    for i in range(3):
        axs[i].xaxis.set_major_locator(matplotlib.ticker.FixedLocator([0.0, 0.2, 0.4, 0.6, 0.8, 1.0]))
    fig.savefig('{}/{}.png'.format(kwargs['save_dir'], save))
    fig.savefig('{}/{}.pdf'.format(kwargs['save_dir'], save))







# Poorly written, the args are all required and are below.
#x_vals, nuclear, wind, solar, x_label, y_label, 
#legend_app, stacked_min, stacked_max, save_name, save_dir):
def stacked_plot(**kwargs):



    plt.close()
    fig, axs = plt.subplots(figsize=(3.8, 3), ncols=1, sharey=True)
    axs = [axs,]
    axs[0].set_xlabel(kwargs['x_label'])
    axs[0].set_ylabel(kwargs['y_label'])

    colors = color_list()
    for i, c in enumerate(cases):

        fixed = 'natgas_ccs'
        if c == 'Case5_WindSolarStorage':
            fixed = 'nuclear'
        
        x_vals = dfs[c]['fuel load / total load']

        #if 'ALT' not in kwargs:
        #    axs[i].set_title(names[c], **{'fontsize':12.5})
        tot = np.zeros(len(x_vals))
        if 'stackedEndUseFraction' in kwargs["save_name"]:

            tot_load = dfs[c]['dispatch to fuel h2 storage (kW)'] + 1. # electric power demand = 1 
            nuclear_curt = dfs[c][f'curtailment {fixed} (kW)'] / tot_load
            renewable_curt = (dfs[c]['curtailment wind (kW)'] + dfs[c]['curtailment solar (kW)']) / tot_load
            fuel_load = dfs[c]['dispatch to fuel h2 storage (kW)'] / tot_load
            elec_load = 1. / tot_load
            dem_renew_frac = dfs[c]['dem_renew_frac']
            electro_renew_frac = dfs[c]['electro_renew_frac']
            
            if 'ALT' in kwargs and kwargs['ALT'] == True:
                y_max = 2.
                add = 3 if kwargs["save_name"] == 'stackedEndUseFractionTotGenAlt' else 0
                #axs[i].text(horiz, vert*y_max, f'{alphas[i+add]}', fontdict=font)
                axs[i].set_ylim(0, y_max)
                axs[i].fill_between(x_vals, tot, tot+elec_load*dem_renew_frac, color=colors[0], label=f'power to electric load - renew')
                tot += elec_load*dem_renew_frac
                #axs[i].fill_between(x_vals, tot, tot+elec_load*(1. - dem_renew_frac), color=colors[0], linewidth=0, alpha=0.5, label=f'power to electric load - dispatch')
                axs[i].fill_between(x_vals, tot, tot+elec_load*(1. - dem_renew_frac), color=colors[0], label=f'power to electric load - dispatch')
                tot += elec_load*(1. - dem_renew_frac)
                axs[i].fill_between(x_vals, tot, tot+fuel_load*electro_renew_frac, color=colors[1], label=f'power to flexible load - renew')
                tot += fuel_load*electro_renew_frac
                #axs[i].fill_between(x_vals, tot, tot+fuel_load*(1. - electro_renew_frac), color=colors[1], linewidth=0, alpha=0.5, label=f'power to flexible load - dispatch')
                axs[i].fill_between(x_vals, tot, tot+fuel_load*(1. - electro_renew_frac), color=colors[1], label=f'power to flexible load - dispatch')
                tot += fuel_load*(1. - electro_renew_frac)
                axs[i].fill_between(x_vals, tot, tot+renewable_curt, color=colors[5], label=f'curtailed - renew')
                tot += renewable_curt
                #axs[i].fill_between(x_vals, tot, tot+nuclear_curt, color=colors[5], linewidth=0, alpha=0.5, label=f'unused - dispatch')
                axs[i].fill_between(x_vals, tot, tot+nuclear_curt, color=colors[5], label=f'unused - dispatch')
                tot += nuclear_curt
                #if i == 2:
                #    print(i, c, "Tot avail gen / tot load")
                #    for ff, v in zip(x_vals, tot):
                #        print(ff, v)
                #        break

                if 'ylim' in kwargs.keys():
                    y_max = kwargs['ylim'][1]
                else:
                    y_max = 9999
        

            else:
                axs[i].fill_between(x_vals, tot, tot+elec_load, color=colors[0], linewidth=0, label=f'power to electric load')
                tot += elec_load
                axs[i].fill_between(x_vals, tot, tot+fuel_load, color=colors[1], linewidth=0, label=f'power to flexible load')
                tot += fuel_load
                axs[i].fill_between(x_vals, tot, tot+renewable_curt, color=colors[5], linewidth=0, label=f'curtailed - renew')
                tot += renewable_curt
                axs[i].fill_between(x_vals, tot, tot+nuclear_curt, color=colors[5], linewidth=0, alpha=0.5, label=f'unused - dispatch')
                tot += nuclear_curt

        else:
            nuclear = dfs[c][f'dispatch {fixed} (kW)'] + dfs[c][f'curtailment {fixed} (kW)']
            wind = dfs[c]['dispatch wind (kW)'] + dfs[c]['curtailment wind (kW)']
            solar = dfs[c]['dispatch solar (kW)'] + dfs[c]['curtailment solar (kW)']

            axs[i].fill_between(x_vals, 0., nuclear, color=colors[5], linewidth=0, label=f'dispatchable {kwargs["legend_app"]}')
            tot += nuclear
            if 'renewables' in kwargs.keys():
                axs[i].fill_between(x_vals, tot, tot+kwargs['renewables'], color=colors[1], linewidth=0, label=f'renewables {kwargs["legend_app"]}')
                tot += kwargs['renewables']
            else:
                axs[i].fill_between(x_vals, tot, tot+wind, color=colors[1], linewidth=0, label=f'wind {kwargs["legend_app"]}')
                tot += wind
                axs[i].fill_between(x_vals, tot, tot+solar, color=colors[0], linewidth=0, label=f'solar {kwargs["legend_app"]}')
                tot += solar
            if 'stackedGenerationElecNorm' in kwargs["save_name"]:
                axs[i].plot(x_vals, tot, 'k-', label='total available gen.')
                axs[i].plot(x_vals, np.ones(len(x_vals)), 'k--', label='firm electric load')
                axs[i].plot(x_vals, np.ones(len(x_vals)) / (1. - x_vals), 'k:', label='firm electric +\nflexible load')

                if 'ylim' in kwargs.keys():
                    y_max = kwargs['ylim'][1]
                    axs[i].set_ylim(kwargs['ylim'][0], kwargs['ylim'][1])
                    #axs[i].text(horiz, vert*kwargs['ylim'][1], f'{alphas[i]}', fontdict=font)
                else:
                    y_max = 9999

        plt.xscale('linear')
        axs[i].set_xlim(0.0, 1.0)
        axs[i].yaxis.set_ticks_position('both')


    #    if 'stackedEndUseFraction' in kwargs["save_name"]:
    #        plt.legend(loc='upper right', ncol=1, framealpha = 1.0)
    #    elif 'stackedGenerationElecNorm' in kwargs["save_name"]:
    #        plt.legend(loc='upper left', ncol=1, framealpha = 1.0)
    #    else:
    #        plt.legend(ncol=3, framealpha = 1.0)
    #else:
    #    plt.legend(framealpha = 1.0)

    plt.subplots_adjust(top=.90, left=.23, bottom=.2, right=.95)
    for i in range(1):
        axs[i].xaxis.set_major_locator(matplotlib.ticker.FixedLocator([0.0, 0.2, 0.4, 0.6, 0.8, 1.0]))
    fig.savefig(f'{kwargs["save_dir"]}/{kwargs["save_name"]}.png')
    fig.savefig(f'{kwargs["save_dir"]}/{kwargs["save_name"]}.pdf')







# Poorly written, the args are all required and are below.
#save_name, save_dir
def costs_plot(var='fuel demand (kWh)', **kwargs):

    dfs = kwargs['dfs']

    colors = color_list()
    plt.close()
    y_max = 30
    if 'h2_only' in kwargs.keys():
        if 'ALT' in kwargs.keys():
            y_max = 6
        else:
            y_max = 8
    #if not 'h2_only' in kwargs.keys():
    fig, axs = plt.subplots(figsize=(9, 3*(1. - .13)), ncols=3, sharey=True)

    # The left y-axis will use $/GGE for electrofuel or $/kg for H2
    if 'h2_only' in kwargs.keys():
        conversion = kWh_LHV_per_kg_H2 # Convert for main y-axis
        conversion *= EFFICIENCY_FUEL_CHEM_CONVERSION # The cost is set based on liquid hydrocarbon
                                                      # output, so must be scaled for H2 only
        axs[0].set_ylabel(r'cost (\$/kg$_{H2}$)')
    else:
        conversion = kWh_to_GGE
        axs[0].set_ylabel(r'cost (\$/GGE)')
    #axs[1].set_xlabel(kwargs['x_label'])

    appA = ''
    appB = ''
    ep = 'electric power'
    if 'ALT' in kwargs.keys():
        appA = ' (marginal cost)'
        appB = appA #'\n(marginal cost)'
        ep = 'power'

    axs2s = []
    for i, c in enumerate(cases):

        axs[i].set_title(names[c], **{'fontsize':12.5})
        axs[i].text(horiz, vert*y_max, f'{alphas[i]}', fontdict=font)

        # $/GGE fuel line use Dual Value
        lab = r'H$_{2}$ total' if 'h2_only' in kwargs.keys() else 'electrofuel total'
        axs[i].plot(dfs[c][var], dfs[c]['fuel price ($/kWh)'] * conversion, 'k-', label=lab+appB)

        # Stacked components
        f_elec = dfs[c]['fixed cost fuel electrolyzer ($/kW/h)'] * dfs[c]['capacity fuel electrolyzer (kW)'] / dfs[c]['fuel demand (kWh)']
        f_chem = dfs[c]['fixed cost fuel chem plant ($/kW/h)'] * dfs[c]['capacity fuel chem plant (kW)'] / dfs[c]['fuel demand (kWh)']
        f_store = dfs[c]['fixed cost fuel h2 storage ($/kWh/h)'] * dfs[c]['capacity fuel h2 storage (kWh)'] / dfs[c]['fuel demand (kWh)']
        f_tot = (f_elec+f_chem+f_store)
        v_chem = dfs[c]['var cost fuel chem plant ($/kW/h)'] * dfs[c]['dispatch from fuel h2 storage (kW)'] * EFFICIENCY_FUEL_CHEM_CONVERSION / dfs[c]['fuel demand (kWh)']
        v_co2 = dfs[c]['var cost fuel co2 ($/kW/h)'] * dfs[c]['dispatch from fuel h2 storage (kW)'] * EFFICIENCY_FUEL_CHEM_CONVERSION / dfs[c]['fuel demand (kWh)']

        f_elec *= conversion
        f_chem *= conversion
        f_store *= conversion
        f_tot *= conversion
        v_chem *= conversion
        v_co2 *= conversion



        if 'h2_only' not in kwargs.keys():
            axs[i].fill_between(dfs[c][var], f_elec, f_elec+f_chem, label='fixed cost: chemical plant', color=colors[1])
            axs[i].fill_between(dfs[c][var], f_elec+f_chem, f_elec+f_chem+f_store, label='fixed cost: storage', color=colors[2]) # fixed cost storage set at 2.72E-7
            axs[i].fill_between(dfs[c][var], f_tot, f_tot+v_chem, label='variable cost: chemical plant', color=colors[3])
            axs[i].fill_between(dfs[c][var], f_tot+v_chem, f_tot+v_chem+v_co2, label='variable cost: CO$_{2}$ feedstock', color=colors[4])


        axs[i].fill_between(dfs[c][var], f_tot+v_chem+v_co2, dfs[c]['fuel price ($/kWh)'] * conversion, label=f'{ep}'+appA, color=colors[5], alpha=0.7, linewidth=0)

        #if 'ALT' in kwargs.keys():
        #    tot_eff_fuel_process = EFFICIENCY_FUEL_ELECTROLYZER * EFFICIENCY_FUEL_CHEM_CONVERSION
        #    avg_elec_cost = (dfs[c]['mean price ($/kWh)'] * (1. - dfs[c][var]) + dfs[c]['fuel_load_cost'] * dfs[c][var]) / tot_eff_fuel_process
        #    axs[i].fill_between(dfs[c][var], f_tot+v_chem+v_co2, f_tot+v_chem+v_co2 + avg_elec_cost * conversion, label='power (system-wide cost)', hatch='//', facecolor='none', edgecolor=colors[5])
        #    lab = r'H$_{2}$ total' if 'h2_only' in kwargs.keys() else 'electrofuel total'
        #    axs[i].plot(dfs[c][var], f_tot+v_chem+v_co2 + avg_elec_cost * conversion, color='black', linestyle='--', label=lab+' (system-wide cost)')
            

        axs[i].plot(dfs[c][var], dfs[c]['fuel price ($/kWh)'] * conversion, 'k-', label='_nolegend_')
        #if 'ALT' in kwargs.keys():
        #    axs[i].plot(dfs[c][var], f_tot+v_chem+v_co2 + avg_elec_cost * conversion, color='black', linestyle='--', label='_nolegend_')

        # Build stack
        lab = 'fixed cost: electrolysis plant' # if 'h2_only' in kwargs.keys() else 'fixed: electrolysis\nplant'
        axs[i].fill_between(dfs[c][var], 0, f_elec, label=lab, color=colors[1], alpha=0.7, linewidth=0)

        plt.xscale('linear')
        axs[i].set_xlim(0.0, 1.0)

        axs[i].set_ylim(0, y_max)

        # 2nd y-axis for $/kWh_e
        ax2 = axs[i].twinx()  # instantiate a second axes that shares the same x-axis
        ax2.set_ylim(0, axs[i].get_ylim()[1] / kWh_to_GGE)
        if i < 2:
            ax2.set_yticklabels([])
        if i == 2:
            ax2.set_ylabel(r'cost (\$/kWh$_{LHV}$)')

        axs2s.append(ax2)


    #if 'h2_only' not in kwargs.keys():
    #    axs[0].legend(loc='upper left', ncol=2, framealpha = 1.0)
    #else:
    #    axs[0].legend(loc='upper left', ncol=2, framealpha = 1.0)

    #plt.subplots_adjust(top=.9, left=.07, bottom=.17, right=.91)
    plt.subplots_adjust(top=.89, left=.11, bottom=.04, right=.91)
    app2 = '_ALT' if 'ALT' in kwargs.keys() else ''
    for i in range(3):
        axs[i].xaxis.set_major_locator(matplotlib.ticker.FixedLocator([0.0, 0.2, 0.4, 0.6, 0.8, 1.0]))
        axs[i].set_xticklabels([])
    fig.savefig(f'{kwargs["save_dir"]}{kwargs["save_name"]}{app2}.png')
    fig.savefig(f'{kwargs["save_dir"]}{kwargs["save_name"]}{app2}.pdf')
    print(f'{kwargs["save_dir"]}{kwargs["save_name"]}.png')


# Poorly written, the args are all required and are below.
#save_name, save_dir
def costs_plot_alt(var='fuel demand (kWh)', **kwargs):

    dfs = kwargs['dfs']

    colors = color_list()
    plt.close()
    y_max = 0.125
    fig, axs = plt.subplots(figsize=(3.8, 3), ncols=1, sharey=True)
    axs = [axs,]

    axs[0].set_ylabel(r'electricity cost (\$/kWh$_{e}$)')
    axs[0].set_xlabel(kwargs['x_label'])

    for i, c in enumerate(cases):

        #axs[i].set_title(names[c], **{'fontsize':12.5})
        #axs[i].text(horiz, vert*y_max, f'{alphas[i]}', fontdict=font)

        # Electricity cost
        axs[i].plot(dfs[c][var], dfs[c]['mean price ($/kWh)'], label=r'marginal cost: firm electric load', color=colors[0])

        axs[i].plot(dfs[c][var], dfs[c]['mean price ($/kWh)'], label='_nolegend_', color=colors[0])

        tot_eff_fuel_process = EFFICIENCY_FUEL_ELECTROLYZER * EFFICIENCY_FUEL_CHEM_CONVERSION
        axs[i].plot(dfs[c][var], dfs[c]['fuel_load_cost'], label=r'marginal cost: flexible load', color=colors[1])
        #if i == 2:
        #    print(i, c, "marginal cost: flexible load")
        #    for ff, v in zip(dfs[c][var], dfs[c]['fuel_load_cost']):
        #        print(ff, v)
        #        break

        avg_elec_cost = dfs[c]['mean price ($/kWh)'] * (1. - dfs[c][var]) + dfs[c]['fuel_load_cost'] * dfs[c][var]
        axs[i].plot(dfs[c][var], avg_elec_cost, 'k--', label=r'system-wide cost', linewidth=2)
        
        #tot_load = 1. + dfs[c]['fuel demand (kWh)'] / (tot_eff_fuel_process)
        #alt_sys_wide = (dfs[c]['system cost ($/kW/h)'] - dfs[c]['capacity fuel electrolyzer (kW)'] * dfs[c]['fixed cost fuel electrolyzer ($/kW/h)']) / tot_load
        #axs[i].plot(dfs[c][var], alt_sys_wide, 'r:', label=r'system-wide cost', linewidth=2)


        #if i == 2:
        #    print(i, c, "system-wide costs")
        #    for ff, v in zip(dfs[c][var], avg_elec_cost):
        #        print(ff, v)
        #        break



        plt.xscale('linear')
        axs[i].set_xlim(0.0, 1.0)

        axs[i].set_ylim(0, .08)
        axs[i].yaxis.set_ticks_position('both')
        #plt.legend(loc='upper left', framealpha = 1.0)

    for i in range(1):
        axs[i].xaxis.set_major_locator(matplotlib.ticker.FixedLocator([0.0, 0.2, 0.4, 0.6, 0.8, 1.0]))
        #axs[i].set_xticklabels([])
    plt.subplots_adjust(top=.90, left=.23, bottom=.2, right=.95)
    fig.savefig(f'{kwargs["save_dir"]}{kwargs["save_name"]}.png')
    fig.savefig(f'{kwargs["save_dir"]}{kwargs["save_name"]}.pdf')
    print(f'{kwargs["save_dir"]}{kwargs["save_name"]}.png')













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
    version1 = 'v3'
    multiplication_factor = 0.01 # default for step_size in new get_fuel_fractions method
    n_jobs = 1
    job_num = 1
    full_year = False # default to run over April only
    h2_only = False # if h2_only is True, costs for CO2, H2 storage, and chem plant are set to 1e-9
    fixed_solar = 1
    fixed_wind = 1
    fixed_electrolyzer = 1
    fixed_natGasCCS = 1
    for arg in sys.argv:
        if 'date' in arg:
            date = arg.split('_')[1]
        if 'Case' in arg:
            case = arg
        if 'version' in arg:
            version1 = arg.split('_')[1]
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



    # Efficiencies so I don't have to pull them from the cfgs for the moment, FIXME
    EFFICIENCY_FUEL_ELECTROLYZER=0.607 # Updated 4 March 2020 based on new values
    EFFICIENCY_FUEL_CHEM_CONVERSION=0.682

    save_dir = f'./plots_{date}_{version1}_XXX_June21/'
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)


    cases = [
        #"Case7_NatGasCCS",
        "Case9_NatGasCCSWindSolarStorage",
        #"Case5_WindSolarStorage",
    ]
    names  = {
        #"Case7_NatGasCCS" : "Dispatch",
        "Case9_NatGasCCSWindSolarStorage" : "Dispatch+Renew+Storage",
        #"Case5_WindSolarStorage" : "Renew+Storage",
    }

    axs = []

    dfs = {}

    for case in cases:

        input_file = 'fuel_test_20200802_AllCases_EIAPrices.csv'
        #input_file = 'fuel_test_20200802_AllCases_EIAPrices_100PctReli.csv'
        if 'Case0' in case:
            input_file = 'fuel_test_20200302_Case0_NuclearFlatDemand.csv'
        version = f'{version1}_{case}'
        global_name = 'fuel_test_{}_{}_{}_{}'.format(date, version, n_jobs, job_num)
        path = 'Output_Data/{}/'.format(global_name)
        results = path+'results/'
        results_search = 'Output_Data/fuel_test_{}_{}*/results/'.format(date, version)

        # Print settings:
        print(f'\nGlobal name                    {global_name}')
        print(f'Output path                    {path}')
        print(f'Results path                   {results}')
        print(f'Demand multiplication factor:  {round(multiplication_factor,3)}')
        print(f'H2_ONLY:                       {h2_only}')
        print(f'Number of jobs:                {n_jobs}')
        print(f'Job number:                    {job_num}')
        print(f'\n - RUN_SEM =          {run_sem}')
        print(f' - MAKE_RESULTS_FILE ={make_results_file}')
        print(f' - MAKE_PLOTS =       {make_plots}\n')


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
        df['fuel load / total load'] = df['dispatch to fuel h2 storage (kW)'] / (
                df['dispatch to fuel h2 storage (kW)'] + 1. # electric power demand = 1 
                )
        df.to_csv('resultsX/Results_{}_tmp.csv'.format(global_name))
        for i in range(len(df.index)):
            if 'Case5' in global_name:
                continue
            #print(i, df.loc[i, 'case name'])
            if df.loc[i, 'fuel demand (kWh)'] == 0.0 or df.loc[i, 'mean demand (kW)'] == 0.0:
                print(f"Dropping idx {i}: fuel {df.loc[i, 'fuel demand (kWh)']} elec {df.loc[i, 'mean demand (kW)']}")
                df = df.drop([i,])

        # Stacked components
        f_elec = df['fixed cost fuel electrolyzer ($/kW/h)'] * df['capacity fuel electrolyzer (kW)'] / df['fuel demand (kWh)']
        f_chem = df['fixed cost fuel chem plant ($/kW/h)'] * df['capacity fuel chem plant (kW)'] / df['fuel demand (kWh)']
        f_store = df['fixed cost fuel h2 storage ($/kWh/h)'] * df['capacity fuel h2 storage (kWh)'] / df['fuel demand (kWh)']
        v_chem = df['var cost fuel chem plant ($/kW/h)'] * df['dispatch from fuel h2 storage (kW)'] * EFFICIENCY_FUEL_CHEM_CONVERSION / df['fuel demand (kWh)']
        v_co2 = df['var cost fuel co2 ($/kW/h)'] * df['dispatch from fuel h2 storage (kW)'] * EFFICIENCY_FUEL_CHEM_CONVERSION / df['fuel demand (kWh)']
        f_tot = f_elec+f_chem+f_store+v_chem+v_co2
        tot_eff_fuel_process = EFFICIENCY_FUEL_ELECTROLYZER * EFFICIENCY_FUEL_CHEM_CONVERSION
        df['fuel_load_cost'] = (df['fuel price ($/kWh)'] - f_tot) * tot_eff_fuel_process

        dfs[case] = df





    ###########################################################################
    ###             PLOTTING                                                ###
    ###########################################################################


    alphas = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']
    font = {
        'weight': 'bold',
        'size': 14,
        }
    horiz = 0.05
    vert = 0.88


    m = {
            'x_label' : 'flexible load (kW) / total load (kW)',
            'app' : '',
            'x_lim' : [0., 1.],
            'x_type' : 'linear',
    }
    k = 'fuel load / total load'

    kwargs = {}
    kwargs['dfs'] = dfs
    kwargs['save_dir'] = save_dir
    kwargs['stacked_min'] = m['x_lim'][0]
    kwargs['stacked_max'] = m['x_lim'][1]
    kwargs['x_label'] = m['x_label']
    kwargs['x_type'] = m['x_type']
    kwargs['x_var'] = k
    if h2_only:
        kwargs['h2_only'] = True




    ### Fuel cost compare scatter and use to fill electricity costs in stacked
    kwargs['save_name'] = 'stackedCostPlot' + m['app']
    #costs_plot(k, **kwargs)
    kwargs['ALT'] = True
    #costs_plot(k, **kwargs)
    del kwargs['ALT']
    kwargs['save_name'] = 'costPlot' + m['app']
    costs_plot_alt(k, **kwargs)
    


    kwargs['save_name'] = 'stackedGenerationElecNorm' + m['app']
    kwargs['y_label'] = 'total available generation (kW) /\nfirm load (kW)'
    kwargs['legend_app'] = ''
    kwargs['ylim'] = [0, 5]
    stacked_plot(**kwargs)

    

    
    ### Stacked curtailment fraction plot - new y-axis, Total Generation
    kwargs['save_name'] = 'stackedEndUseFractionTotGenAlt' + m['app']
    kwargs['y_label'] = 'total available generation (kW) /\ntotal load (kW)'
    kwargs['legend_app'] = ''
    kwargs['ylim'] = [0, 3]
    kwargs['ALT'] = True
    if 'Case1' in kwargs['save_dir']:
        kwargs['ylim'] = [0, 2]
    stacked_plot(**kwargs)
    del kwargs['ALT']

    

    ## Fuel system capacity factor ratios
    ylims = [0.0, 1.]

    # EF system capacity factor ratios
    kwargs['y_label'] = 'capacity factor'
    #simple_plot('systemCFsEF' + m['app'],
    #        False, ylims, **kwargs)
    #    
    #electro_cf_by_X('systemCFsEF_by_month' + m['app'],
    #        **kwargs)
    #electro_cf_by_X('systemCFsEF_by_hour' + m['app'],
    #        **kwargs)
