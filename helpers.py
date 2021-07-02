#!/usr/bin/env python3

import numpy as np
import os
from glob import glob
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def get_fuel_demands(start, end, steps):
    fuel_demands = [0., start,]
    while True:
        if fuel_demands[-1] > end:
            break
        fuel_demands.append(round(fuel_demands[-1]*steps,5))
    return fuel_demands

def get_fuel_fractions(step_size, total_eff):

    ffs = np.arange(0.0, 1.0, step_size)
    fuel_dem = (ffs / (1.0 - ffs)) * total_eff
    #for ff, dem in zip(ffs, fuel_dem):
    #    print(ff, dem)

    return fuel_dem


def plot_peak_demand_grid(out_file_dir, out_file_name, tgt_fuel_dems, case, techs, save_dir, set_max=-1, ldc=False):

    # Open out file as df
    f_name = out_file_dir + out_file_name.replace('fuelDXXX', f'fuelD0.0')
    full_file_name = glob(f_name)
    assert(len(full_file_name) == 1)
    df = pd.read_csv(full_file_name[0])

    # Find the idx to center to time series upon
    center_idx = find_centering_hour_idx(df, case)

    plt.close()
    matplotlib.rcParams["figure.figsize"] = (7, 8)
    matplotlib.rcParams["font.size"] = 9
    matplotlib.rcParams['lines.linewidth'] = 0.5
    matplotlib.rcParams['hatch.linewidth'] = 0.5
    axs = []
    for j, dem in enumerate(reversed(tgt_fuel_dems)):


        i = len(tgt_fuel_dems) - j + 1
        this_file = out_file_dir + out_file_name.replace('fuelDXXX', f'fuelD{dem}')
        if j == 0:
            axs.append( plt.subplot(7, 2, 2 * i - 1) )
            axs[-1].set_xlabel('Hours')
        else:
            axs.append( plt.subplot(7, 2, 2 * i - 1, sharex=axs[0]) )
            plt.setp(axs[-1].get_xticklabels(), visible=False)
        axs[-1].set_ylabel('power (kW)')

        ndays = 7 # days on each side of peak
        plot_peak_demand_system(axs[-1], dem, center_idx, this_file, info[0], save_dir, case, ndays, set_max)
        
        if j == 0:
            axs.append( plt.subplot(7, 2, 2 * i, sharey=axs[-1]) )
            plt.setp(axs[-1].get_yticklabels(), visible=False)
            axs[-1].set_xlabel('Fraction of time')
        else:
            axs.append( plt.subplot(7, 2, 2 * i, sharey=axs[-1], sharex=axs[1]) )
            plt.setp(axs[-1].get_yticklabels(), visible=False)
            plt.setp(axs[-1].get_xticklabels(), visible=False)
        plot_peak_demand_system(axs[-1], dem, center_idx, this_file, info[0], save_dir, case, ndays, set_max, True)

    plt.tight_layout()
    horiz = -1.1 if case != 'Case6_NuclearWindSolarStorage' else -1.1
    horiz = -1.2 # AGU
    vert = 2
    handles, labels = plt.gca().get_legend_handles_labels()
    if len(handles) > 9:
        vert = 2.2
    plt.legend(ncol=3, loc='upper left', bbox_to_anchor=(horiz, vert))
    plt.subplots_adjust(top=1)
    fig = plt.gcf()
    fig.savefig(f"{save_dir}/{case}.png")
    fig.savefig(f"{save_dir}/pdf/{case}.pdf")


def plot_peak_demand_select(out_file_dir, out_file_name, tgt_fuel_dems, case, techs, save_dir, set_max=-1, plot_min_region=False):

    # Open out file as df
    f_name = out_file_dir + out_file_name.replace('fuelDXXX', f'fuelD0.0').replace('Run_','Run_101')
    print(f_name)
    full_file_name = glob(f_name)
    assert(len(full_file_name) == 1)
    df = pd.read_csv(full_file_name[0])
    print(full_file_name[0])
    print(f"Max demand: { np.max( df['demand (kW)'] ) }")
    print(f"Mean demand: { np.mean( df['demand (kW)'].mean() ) }")
    print( f"Number of hours with unmet demand: {np.where( df['dispatch unmet demand (kW)'] > 0., 1, 0 ).sum()}")
    print( f"Max hourly unmet demand: { np.max( df['dispatch unmet demand (kW)'] ) }")
    print( f"Max hourly unmet demand frac of peak val: { np.max( df['dispatch unmet demand (kW)'] )/np.max( df['demand (kW)'] ) }")
    print( f"Sum unmet demand: { np.sum( df['dispatch unmet demand (kW)'] ) }")
    print( f"Unmet demand fraction: { np.sum( df['dispatch unmet demand (kW)'] )/len(df.index) }")

    # Find the idx to center to time series upon
    #center_idx = find_centering_hour_idx(df, case)
    center_idx = df['demand (kW)'].idxmax()
    if plot_min_region:
        center_idx = df['demand (kW)'].idxmin()
    print(f"center_idx {center_idx}")
    center_idx = [4821,] # Use same as Case 1
    if plot_min_region:
        center_idx = [2529,] # Use same as Case 1
    print(f"center_idx NEW {center_idx}")

    plt.close()
    matplotlib.rcParams["figure.figsize"] = (7, 3.5)
    matplotlib.rcParams["font.size"] = 9
    matplotlib.rcParams['lines.linewidth'] = 1
    matplotlib.rcParams['hatch.linewidth'] = 0.5
    axs = []
    for j, dem in enumerate(tgt_fuel_dems):


        i = len(tgt_fuel_dems) - j + 1
        this_file = out_file_dir + out_file_name.replace('fuelDXXX', f'fuelD{dem}')
        #print(this_file)
        if j == 0:
            axs.append( plt.subplot(1, len(tgt_fuel_dems), j+1) )
            axs[-1].set_ylabel('power\n(% annual mean firm load)')
            axs[-1].yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(xmax=1, decimals=0))
        else:
            axs.append( plt.subplot(1, len(tgt_fuel_dems), j+1, sharey=axs[0]) )
            plt.setp(axs[-1].get_yticklabels(), visible=False)
        axs[-1].set_xlabel('Hours')

        plot_peak_demand_system(axs[-1], dem, center_idx, this_file, techs, save_dir, case, 1, set_max)
        

    #plt.tight_layout()
    horiz = -3.65
    horiz = -3.85
    vert = 1.35
    if "Case5" in case or "Case6" in case:
        vert = 1.45

    handles, labels = plt.gca().get_legend_handles_labels()
    #if len(handles) > 9:
    #    vert = 1.2
    plt.legend(ncol=3, loc='upper left', bbox_to_anchor=(horiz, vert))
    plt.subplots_adjust(top=.75, bottom=.17, right=0.97, left=.12)
    fig = plt.gcf()
    app = '' if not plot_min_region else '_min'
    fig.savefig(f"{save_dir}/{case}_select{app}.png")
    fig.savefig(f"{save_dir}/pdf/{case}_select{app}.pdf")


def find_centering_hour_idx(df, case):

    fourtyEightHrs = []
    lowest_val = 999
    lowest_idx = 999
    for idx in df.index:
        fourtyEightHrs.append( df.loc[idx, 'cutailment solar (kW)'] + df.loc[idx, 'cutailment wind (kW)'] + df.loc[idx, 'cutailment nuclear (kW)'] )
        if len(fourtyEightHrs) > 48:
            fourtyEightHrs.pop(0) # Get rid of oldes val
            mean = np.mean(fourtyEightHrs)
            if mean < lowest_val:
                lowest_val = mean
                lowest_idx = idx
    return [lowest_idx - 24,]


# From list of hours as n hours from year start, find datetimes
def get_start_datetime(xs, mod=99):

    dts = []
    xsx = []

    dt = datetime(2017, 1, 1, 1)
    first_hr = dt + timedelta(hours=xs.values[0])
    #print(f"First hour of x-axis {first_hr}")

    # Set for Central Standard Time (CST) from UTC
    if mod != 99:
        first_hr += timedelta(hours=-6)
        
    for i in range(len(xs)):
        if mod == 99 and first_hr.hour % mod == 0:
            dts.append(first_hr.strftime("%Y-%m-%d"))
            xsx.append(xs.values[0] + i)
        elif first_hr.hour % mod == 0:
            dts.append(first_hr.strftime("%H:00"))
            xsx.append(xs.values[0] + i)
        first_hr += timedelta(hours=1)
    return dts, xsx


def print_flexible_CFs(df):
    
    to_flex = df['dispatch to fuel h2 storage (kW)']

    m = np.max(to_flex)
    n_max = (to_flex == m).sum()/8760.
    n_zero = (to_flex == 0.0).sum()/8760.
    cf = np.sum(to_flex) / 8760. / m
    print(f"{round(n_max*100,1)}%,{round((1. - n_max - n_zero)*100,1)}%,{round(n_zero*100,1)}%,{round(cf*100,1)}%")




def plot_peak_demand_system(ax, dem, center_idx, out_file_name, techs, save_dir, case, days, set_max=-1, ldc=False):

    # Open out file as df
    full_file_name = glob(out_file_name)
    assert(len(full_file_name) == 1), f"\n\nYour file list is: {full_file_name}"
    df = pd.read_csv(full_file_name[0])
    #print(full_file_name[0])

    print_flexible_CFs(df)

    assert(len(center_idx) == 1), f"\n\nThere are multiple instances of peak demand value, {center_idx}\n\n"
    peak_idx = center_idx[0]

    lo = peak_idx - int(24*days)
    hi = peak_idx + int(24*days)
    if hi > len(df.index):
        lo = lo - (hi - len(df.index))
        hi = hi - (hi - len(df.index))
    dfs = df.iloc[lo:hi]
    if ldc:
        dfs = dfs.sort_values('demand (kW)', ascending=False)
        #ax.set_xlabel('Fraction of time')
        xs = np.linspace(0, 1, len(dfs.index))
    else:
        xs = dfs['time (hr)']

    if 'natgas_ccs' in techs:
        disp = 'natgas_ccs'
    #if 'nuclear' in techs:
    else:
        disp = 'nuclear' 
    cap_disp = np.max(df[f'dispatch {disp} (kW)'])

    fblw = 0.25
    if days < 7:
        fblw = .75
    fblw2 = 1.5

    bottom = np.zeros(len(xs))
    if 'solar' in techs:
        ax.fill_between(xs, bottom, bottom + dfs['dispatch solar (kW)'], color='orange', alpha=0.4, label='power from solar', lw=fblw)
        bottom += dfs['dispatch solar (kW)'].values
    if 'wind' in techs:
        ax.fill_between(xs, bottom, bottom + dfs['dispatch wind (kW)'], color='blue', alpha=0.2, label='power from wind', lw=fblw)
        bottom += dfs['dispatch wind (kW)'].values
    if disp in techs:
        ax.fill_between(xs, bottom, bottom + dfs[f'dispatch {disp} (kW)'], color='tan', alpha=0.5, label='power from natural gas', lw=fblw)
        bottom += dfs[f'dispatch {disp} (kW)'].values
    if 'storage' in techs:
        ax.fill_between(xs, bottom, bottom + dfs['dispatch from storage (kW)'], color='magenta', alpha=0.2, label='power from storage', lw=fblw)
        bottom += dfs['dispatch from storage (kW)'].values

    bottom2 = np.zeros(len(xs))
    ax.fill_between(xs, 0., dfs['demand (kW)'] - dfs['dispatch unmet demand (kW)'], facecolor='none', edgecolor='dimgray', hatch='/////', label='power to firm load', lw=fblw2)
    bottom2 += dfs['demand (kW)'] - dfs['dispatch unmet demand (kW)']
    ax.fill_between(xs, bottom2, bottom2 + dfs['dispatch to fuel h2 storage (kW)'], facecolor='none', edgecolor='magenta', hatch='xxxx', label='power to flexible load', lw=fblw2)
    bottom2 += dfs['dispatch to fuel h2 storage (kW)']
    if 'storage' in techs:
        ax.fill_between(xs, bottom2, bottom2 + dfs['dispatch to storage (kW)'], facecolor='none', edgecolor='magenta', hatch='xxxxx', label='power to storage', lw=fblw)
        bottom2 += dfs['dispatch to storage (kW)']
    ax.fill_between(xs, dfs['demand (kW)'] - dfs['dispatch unmet demand (kW)'], dfs['demand (kW)'], color='red', alpha=0.8, label='demand response reductions', lw=fblw)
    #ax.fill_between(xs, bottom2, bottom2 + dfs['dispatch unmet demand (kW)'], facecolor='none', edgecolor='red', hatch='|||||', label='Unmet demand')


    ax.plot(xs, dfs['demand (kW)'], 'k-', linewidth=fblw2, label='firm load')

    bottom3 = np.zeros(len(xs))
    lab = 'cap.'
    if 'solar' in techs:
        lab += ' solar'
        ax.plot(xs, bottom3 + dfs['dispatch solar (kW)'] + dfs['cutailment solar (kW)'], 'y-', linewidth=fblw, label=lab)
        bottom3 += dfs['dispatch solar (kW)'] + dfs['cutailment solar (kW)']
        lab = lab.replace('solar', 'sol.')
    if 'wind' in techs:
        if 'solar' in techs:
            lab += ' + wind'
        else:
            lab += ' wind'
        ax.plot(xs, bottom3 + dfs['dispatch wind (kW)'] + dfs['cutailment wind (kW)'], 'b-', linewidth=fblw, label=lab)
        bottom3 += dfs['dispatch wind (kW)'] + dfs['cutailment wind (kW)']
    if disp in techs:
        if 'solar' in techs or 'wind' in techs:
            lab += ' + disp.'
        else:
            lab = 'natural gas capacity'
        ax.plot(xs, bottom3 + np.ones(len(xs))*cap_disp, 'b-', linewidth=fblw2, label=lab)

    if set_max == -1:
        set_max = ax.get_ylim()[1]
    ax.set_ylim(0, set_max)
    if ldc:
        ax.set_xlim(0, 1)
    else:
        ax.set_xlim(lo, hi-1)

    # Make x-axis datetime
    if not ldc:
        if days <= 1: # Labels every 3 hours
            mod = 6 if days == 1 else 3
            dts, xsx = get_start_datetime(xs, mod)
            plt.xticks(xsx, dts, rotation=90)
        elif days < 7: # we have more room, rotate less
            dts, xsx = get_start_datetime(xs)
            plt.xticks(xsx, dts, rotation=30)
        else:
            dts, xsx = get_start_datetime(xs)
            plt.xticks(xsx, dts, rotation=90)
        ax.set_xlabel(None)
    
    # BAD HARDCODED FUEL FRACTIONS MAPPED TO DEMAND VALUES
    ffs = {
            '0.02179' : '0.05', # new FF w/ 103 cases 
            '0.07305' : '0.15', # new FF w/ 103 cases 
            '0.13799' : '0.25',
            '0.17742' : '0.30',
            '0.22291' : '0.35', # new FF w/ 103 cases 
            '0.27598' : '0.40', 
    }


    # Add fuel demand value
    ax.text(0.03, 0.97, f'flexible frac: {ffs[dem]}',
        verticalalignment='top', horizontalalignment='left',
        transform=ax.transAxes,fontsize=9
    )





if '__main__' in __name__:

    save_dir = 'out_plots'
    save_dir = 'out_plots11'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        os.makedirs(save_dir+'/pdf')

    date = '20200311_v8' # 2016 figs used in 20200526_fuels_paper_II_20200526_kc.docx
    date = '20200608_v1'
    date = '20200725_v5'
    date = '20200803_v2'
    date = '20200805_v2'
    #date = '20201116_v5fullReli'
    #base = 'Output_Data/'
    base = 'results_files/dispatch_curve/' # For committed files
    cases = {
            #"Case0_NuclearFlatDemand" : [['nuclear',], -1],
            #"Case1_Nuclear" : [['nuclear',], 2, 2],
            #"Case2_NuclearStorage" : [['nuclear','storage'], 2, 2],
            #"Case3_WindStorage" : [['wind', 'storage'], 6, 5],
            #"Case4_SolarStorage" : [['solar', 'storage'], 5, 8],
            "Case5_WindSolarStorage" : [['wind', 'solar', 'storage'], 3, 3.5],
            #"Case6_NuclearWindSolarStorage" : [['nuclear', 'wind', 'solar', 'storage'], 3, 2.5],
            "Case7_NatGasCCS" : [['natgas_ccs',], 2, 2],
            "Case9_NatGasCCSWindSolarStorage" : [['natgas_ccs',], 2, 2],
    }

    #possible_dem_vals = get_fuel_demands(0.01, 10, 1.2) # start, end, steps

    tgt_fuel_dems = [
            '0.012',
            '0.02489',
            '0.05161',
            '0.07432',
            '0.10702',
            '0.2219',
            #'0.31954',
            #'1.14497',
            #'10.20862',
    ]
    tgt_fuel_dems_select = [
            '0.02179', # new FF w/ 103 cases 
            '0.07305', # new FF w/ 103 cases 
            #'0.13799',
            '0.17742',
            #'0.22291', # new FF w/ 103 cases 
            '0.27598', 
    ]

    for case, info in cases.items():

        print(f"Plotting for {case} with techs {info[0]} and max = {info[1]} or {info[2]}")
        #for idx, dem in enumerate(reversed(possible_dem_vals)):
        #    if str(dem) not in tgt_fuel_dems:
        #        continue
        #out_file_dir = f'{base}fuel_test_{date}_{case}*/'
        out_file_dir = f'{base}fuel_test_{date}_{case}/' # For committed files
        out_file_name = f'fuel_test_{date}_{case}_*Run_*_fuelDXXXkWh_*.csv'
        #plot_peak_demand_grid(out_file_dir, out_file_name, tgt_fuel_dems, case, info[0], save_dir, info[1], True)
        plot_peak_demand_select(out_file_dir, out_file_name, tgt_fuel_dems_select, case, info[0], save_dir, info[2])
        plot_min_region = True
        #plot_peak_demand_select(out_file_dir, out_file_name, tgt_fuel_dems_select, case, info[0], save_dir, info[2], plot_min_region)




