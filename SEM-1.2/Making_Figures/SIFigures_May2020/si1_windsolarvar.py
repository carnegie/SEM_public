#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 17:22:12 2019

@author: katherinerinaldi
"""

import csv
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

path = '/Users/jacquelinedowling/MEM_Nov2019/SEM-1.2/Input_Data/Lei_Solar_Wind/'



demand = '{}US_demand_unnormalized_FOURTY_YEARS_FROM_FOUR_YEAR_LOOP.csv'.format(path)
wind = '{}US_wind_thresh.csv'.format(path)
solar = '{}US_solar_thresh.csv'.format(path)


#this takes in the file and gets rid of all lines before BEGIN_DATA
#then it returns a pandas dataframe

def getData(filename):
    with open(filename) as file:
        reader = csv.reader(file)
        
         #read to keyword 'BEGIN_DATA'
        while True:
            line = next(reader)
            if line[0] == 'BEGIN_DATA':
                break
        
        #take all non-blank lines
        data = []
        while True:
            try:
                line = next(reader)
                if any(field.strip() for field in line):
                    data.append(line)
            except:
                break
        
#        #turn data dataframe
        df = pd.DataFrame(data)
        headers = df.iloc[0]
        data_array  = pd.DataFrame(df.values[1:], columns=headers)

        return data_array


# this makes the new 'date' column in each type of dataframe (depending on how
# the original file is formatted there are diff options)
def dateMaker(df, dataType):
    if dataType == 'wind':
        df['wind capacity']=df['wind capacity'].astype(float)
    elif dataType == 'solar':
        df['solar capacity']=df['solar capacity'].astype(float)
    elif dataType == 'demand':
        df['demand (MW)']=df['demand (MW)'].astype(float)
    df['hour']=df['hour'].astype(int)
    df['hour']=df['hour']-1
    dates=pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    df['date'] = dates
    df.set_index(['date'], inplace=True)
    
def stat_quantile(groupby_dataframe, quantile):
	output = groupby_dataframe.quantile(q = quantile)
	return output

#sorts out the data by season (winter or summer), groups by hour of day
def getSeasons(df, season, dataType):
    if dataType == 'demand':
        df_gb_month = df.groupby(df.index.month)['demand (MW)']
    elif dataType =='solar': 
        df_gb_month = df.groupby(df.index.month)['solar capacity']
    elif dataType == 'wind':
        df_gb_month= df.groupby(df.index.month)['wind capacity']
    
    if season == 'summer':
        season_df = df_gb_month.get_group(6).append(df_gb_month.get_group(7))
        season_df = season_df.append(df_gb_month.get_group(8))
    if season == 'winter':
        season_df = df_gb_month.get_group(12).append(df_gb_month.get_group(1))
        season_df = season_df.append(df_gb_month.get_group(2))
     
    season_df_gb = season_df.groupby(season_df.index.hour)    
        
    return season_df_gb

def time_shift(array, hourstoshift):

	for i in range(hourstoshift):

		row = array.iloc[0] # take stock of first row
		array = array.shift(-1) # remove first entry and shift all data up one row
		array.iloc[-1] = row # put old first row as last row

	
	array = array.values
	return array

#get the data
demand_df = getData(demand)
solar_df = getData(solar)
wind_df = getData(wind)

#turn the year month day columns into one new column called date
dateMaker(demand_df, 'demand')
dateMaker(solar_df, 'solar')
dateMaker(wind_df, 'wind')

#normalize the data (ie divide by the 39 year mean)
demand_mean = demand_df['demand (MW)'].mean()
solar_mean = solar_df['solar capacity'].mean()
wind_mean = wind_df['wind capacity'].mean()

demand_df['demand (MW)']=demand_df['demand (MW)']/demand_mean
solar_df['solar capacity']=solar_df['solar capacity']/solar_mean
wind_df['wind capacity']=wind_df['wind capacity']/wind_mean

#make y values for plotting main fig (resample to take the daily mean)
dailyMean_demand = demand_df.resample('D').mean()
dailyMean_solar = solar_df.resample('D').mean()
dailyMean_wind = wind_df.resample('D').mean()

#groups each value by day of year (can compare the same day in many diff years)
demand_gb=dailyMean_demand.groupby(dailyMean_demand.index.dayofyear)
solar_gb=dailyMean_solar.groupby(dailyMean_solar.index.dayofyear)
wind_gb=dailyMean_wind.groupby(dailyMean_wind.index.dayofyear)

#median for each day
y_demand = demand_gb.median()
y_solar = solar_gb.median()
y_wind = wind_gb.median()

#makes the 50% / 100% areas
demand_fourth_quartile = stat_quantile(demand_gb, 1)
demand_third_quartile = stat_quantile(demand_gb, 0.75)
demand_first_quartile = stat_quantile(demand_gb, 0.25)
demand_zeroth_quartile = stat_quantile(demand_gb, 0)

solar_fourth_quartile = stat_quantile(solar_gb, 1)
solar_third_quartile = stat_quantile(solar_gb, 0.75)
solar_first_quartile = stat_quantile(solar_gb, 0.25)
solar_zeroth_quartile = stat_quantile(solar_gb, 0)

wind_fourth_quartile = stat_quantile(wind_gb, 1)
wind_third_quartile = stat_quantile(wind_gb, 0.75)
wind_first_quartile = stat_quantile(wind_gb, 0.25)
wind_zeroth_quartile = stat_quantile(wind_gb, 0)

#make data for subplot 1 (hourly summer for Jun-6, July-7, August-8)
summer_demand = getSeasons(demand_df, 'summer', 'demand')
summer_solar = getSeasons(solar_df, 'summer', 'solar')
summer_wind = getSeasons(wind_df, 'summer', 'wind')

#make data for subplot 2 (hourly winter for dec-12, jan-1, and feb-2)
winter_demand = getSeasons(demand_df, 'winter', 'demand')
winter_solar = getSeasons(solar_df, 'winter', 'solar')
winter_wind = getSeasons(wind_df, 'winter', 'wind')

#make y values for subplots
y_summer_demand = time_shift(summer_demand.median(),7)
y_summer_solar = time_shift(summer_solar.median(),7)
y_summer_wind = time_shift(summer_wind.median(),7)

y_winter_demand = time_shift(winter_demand.median(),7)
y_winter_solar = time_shift(winter_solar.median(),7)
y_winter_wind = time_shift(winter_wind.median(),7)

#makes the 50% / 100% areas for summer and winter subplots
summer_demand_fourth_quartile = time_shift(stat_quantile(summer_demand, 1),7)
summer_demand_third_quartile = time_shift(stat_quantile(summer_demand, 0.75),7)
summer_demand_first_quartile = time_shift(stat_quantile(summer_demand, 0.25),7)
summer_demand_zeroth_quartile = time_shift(stat_quantile(summer_demand, 0),7)

summer_solar_fourth_quartile = time_shift(stat_quantile(summer_solar, 1),7)
summer_solar_third_quartile = time_shift(stat_quantile(summer_solar, 0.75),7)
summer_solar_first_quartile = time_shift(stat_quantile(summer_solar, 0.25),7)
summer_solar_zeroth_quartile = time_shift(stat_quantile(summer_solar, 0),7)

summer_wind_fourth_quartile = time_shift(stat_quantile(summer_wind, 1),7)
summer_wind_third_quartile = time_shift(stat_quantile(summer_wind, 0.75),7)
summer_wind_first_quartile = time_shift(stat_quantile(summer_wind, 0.25),7)
summer_wind_zeroth_quartile = time_shift(stat_quantile(summer_wind, 0),7)

winter_demand_fourth_quartile = time_shift(stat_quantile(winter_demand, 1),7)
winter_demand_third_quartile = time_shift(stat_quantile(winter_demand, 0.75),7)
winter_demand_first_quartile = time_shift(stat_quantile(winter_demand, 0.25),7)
winter_demand_zeroth_quartile = time_shift(stat_quantile(winter_demand, 0),7)

winter_solar_fourth_quartile = time_shift(stat_quantile(winter_solar, 1),7)
winter_solar_third_quartile = time_shift(stat_quantile(winter_solar, 0.75),7)
winter_solar_first_quartile = time_shift(stat_quantile(winter_solar, 0.25),7)
winter_solar_zeroth_quartile = time_shift(stat_quantile(winter_solar, 0),7)

winter_wind_fourth_quartile = time_shift(stat_quantile(winter_wind, 1),7)
winter_wind_third_quartile = time_shift(stat_quantile(winter_wind, 0.75),7)
winter_wind_first_quartile = time_shift(stat_quantile(winter_wind, 0.25),7)
winter_wind_zeroth_quartile = time_shift(stat_quantile(winter_wind, 0),7)



x_values = range(len(y_demand))
x_season_values = range(len(y_summer_demand))

#plot
    
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

#params = {'legend.fontsize': 'medium',
#          'figure.figsize': (7, 3.5), #7 3.5
#         'axes.labelsize': 'x-large',
#         'axes.titlesize':'x-large',
#         'xtick.labelsize':'large',
#         'ytick.labelsize':'large'}
#
#plt.rcParams.update(params)

gridsize = (3, 2)
fig = plt.figure(figsize=(7, 6.75))
ax1 = plt.subplot2grid(gridsize, (0, 0), colspan=2, rowspan=2)
ax2 = plt.subplot2grid(gridsize, (2, 0))
ax3 = plt.subplot2grid(gridsize, (2, 1))


ax1.plot(x_values, y_demand, color='black', linewidth='2', label='demand')
ax1.fill_between(x_values, demand_zeroth_quartile['demand (MW)'], demand_fourth_quartile['demand (MW)'], alpha = 0.2, facecolor = 'black')
ax1.fill_between(x_values, demand_first_quartile['demand (MW)'], demand_third_quartile['demand (MW)'], alpha = 0.5, facecolor = 'black')

ax1.plot(x_values, y_solar, color='orange', linewidth='2', label='solar')
ax1.fill_between(x_values, solar_zeroth_quartile['solar capacity'], solar_fourth_quartile['solar capacity'], alpha = 0.2, facecolor = 'orange', edgecolor = 'orange')
ax1.fill_between(x_values, solar_first_quartile['solar capacity'], solar_third_quartile['solar capacity'], alpha = 0.5, facecolor = 'orange', edgecolor = 'orange')

ax1.plot(x_values, y_wind, color='blue', linewidth='2', label='wind')
ax1.fill_between(x_values, wind_zeroth_quartile['wind capacity'], wind_fourth_quartile['wind capacity'], alpha = 0.2, facecolor = 'blue')
ax1.fill_between(x_values, wind_first_quartile['wind capacity'], wind_third_quartile['wind capacity'], alpha = 0.5, facecolor = 'blue')


ax1.set_ylabel('Power divided by 39-year mean', fontsize = 14, color = 'black')
ax1.set_xlim(0, 365)
ax1.set_ylim(0,3)
ax1.set_xticks(np.arange(10, 360, 31))
ax1.set_xticklabels(months, fontsize = 12)
ax1.set_xlabel('Month of year', fontsize=14)



ax2.plot(x_season_values, y_summer_demand, color='black', linewidth='2', label='demand')
ax2.fill_between(x_season_values, summer_demand_zeroth_quartile, summer_demand_fourth_quartile, alpha = 0.2, facecolor = 'black')
ax2.fill_between(x_season_values, summer_demand_first_quartile, summer_demand_third_quartile, alpha = 0.5, facecolor = 'black')

ax2.plot(x_season_values, y_summer_solar, color='orange', linewidth='2', label='solar')
ax2.fill_between(x_season_values, summer_solar_zeroth_quartile, summer_solar_fourth_quartile, alpha = 0.2, facecolor = 'orange', edgecolor='orange')
ax2.fill_between(x_season_values, summer_solar_first_quartile, summer_solar_third_quartile, alpha = 0.5, facecolor = 'orange', edgecolor='orange')

ax2.plot(x_season_values, y_summer_wind, color='blue', linewidth='2', label='wind')
ax2.fill_between(x_season_values, summer_wind_zeroth_quartile, summer_wind_fourth_quartile, alpha = 0.2, facecolor = 'blue')
ax2.fill_between(x_season_values, summer_wind_first_quartile, summer_wind_third_quartile, alpha = 0.5, facecolor = 'blue')

ax2.set_xlim(0, 23)
ax2.set_ylim(-0.2, 3.5)
ax2.set_xticks(np.arange(0,23,4))
ax2.set_ylabel('Power divided by \n 39-year mean', fontsize = 14)
ax2.set_xlabel('Hour of day (PST)', fontsize=14)
ax2.set_title('Summer', fontsize=14)

ax3.plot(x_season_values, y_winter_demand, color='black', linewidth='2', label='demand')
ax3.fill_between(x_season_values, winter_demand_zeroth_quartile, winter_demand_fourth_quartile, alpha = 0.2, facecolor = 'black')
ax3.fill_between(x_season_values, winter_demand_first_quartile, winter_demand_third_quartile, alpha = 0.5, facecolor = 'black')

ax3.plot(x_season_values, y_winter_solar, color='orange', linewidth='2', label='solar')
ax3.fill_between(x_season_values, winter_solar_zeroth_quartile, winter_solar_fourth_quartile, alpha = 0.2, facecolor = 'orange',edgecolor='orange')
ax3.fill_between(x_season_values, winter_solar_first_quartile, winter_solar_third_quartile, alpha = 0.5, facecolor = 'orange',edgecolor='orange')

ax3.plot(x_season_values, y_winter_wind, color='blue', linewidth='2', label='wind')
ax3.fill_between(x_season_values, winter_wind_zeroth_quartile, winter_wind_fourth_quartile, alpha = 0.2, facecolor = 'blue')
ax3.fill_between(x_season_values, winter_wind_first_quartile, winter_wind_third_quartile, alpha = 0.5, facecolor = 'blue')

ax3.set_xlim(0, 23)
ax3.set_ylim(-0.2, 3.5)
ax3.set_xticks(np.arange(0,23,4))
ax3.set_xlabel('Hour of day (PST)', fontsize=14)
ax3.set_title('Winter', fontsize=14)

fig.text(0.13, 0.93, 'a)', size='large')
fig.text(0.13, 0.265, 'b)', size='large')
fig.text(0.585, 0.265, 'c)', size='large')

plt.tight_layout()

#plt.savefig('{}\resource_variability.pdf'.format(path), bbox_inches='tight')
plt.savefig('si/SI_windsolarvar.pdf', bbox_inches='tight')
plt.show()