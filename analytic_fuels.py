import numpy as np
import pandas as pd



#----------------------------------------------------------------------
# Constants & fixed discount rate
#----------------------------------------------------------------------

DISCOUNT_RATE = 0.07
HOURS_PER_YEAR = 8760 # Reference: # days per year
BtuPerkWh = 3412.14 # https://www.eia.gov/totalenergy/data/monthly/pdf/sec13_18.pdf
MWh_per_MMBtu = 0.293 # https://www.eia.gov/totalenergy/data/monthly/pdf/sec13_18.pdf
MMBtu_per_Gallon_Gasoline = 0.114 # Btu/GGE "Fuel Economy Impact Analysis of RFG". 
            #United States Environmental Protection Agency. August 14, 2007. Retrieved Aug 27, 2019.
lhvH2Conv = 33.33 # kWh LHV / kg H2
hhvH2Conv = 39.4 # kWh HHV / kg H2

MMBtu_per_barrel_2017 = 5.053 # MMBtu/barrel in 2017 per EIA, see README
Gallons_per_barrel = 42 # U.S. gallons / barrel per EIA, see README

kWh_to_GGE = 33.4
kWh_LHV_per_kg_H2 = 33.33
liters_to_gallons = 3.78541

# Wikipedia: https://en.wikipedia.org/wiki/Gasoline
# About 19.64 pounds (8.91 kg) of carbon dioxide (CO2) are produced from burning 1 U.S. gallon (3.8 liters) of gasoline that does not contain ethanol (2.36 kg/L).
co2_per_gallon_gas = 8.91/1000.


def capital_recovery_factor(discount_rate, **dic):
    dic['capital recovery factor'] = discount_rate*(1.+discount_rate)**dic['assumed lifetime'] / ((1+discount_rate)**dic['assumed lifetime'] - 1)
    return dic

def fixed_cost_per_year(**dic):
    dic['fixed cost per year'] = dic['capital cost']*dic['capital recovery factor']
    if 'capital cost (kg)' in dic.keys():
        dic['fixed cost per year (kg)'] = dic['capital cost (kg)']*dic['capital recovery factor']

    # Add fixed O&M if applicable
    if 'fixed annual OandM cost' in dic.keys():
        dic['fixed cost per year (no OandM)'] = dic['fixed cost per year']
        dic['fixed cost per year (no OandM) (kg)'] = dic['fixed cost per year (kg)']
        dic['fixed cost per year'] += dic['fixed annual OandM cost']
        dic['fixed cost per year (kg)'] += dic['fixed annual OandM cost (kg)']
    return dic

# NOTE: No difference in time value within year
def fixed_cost_per_hr(**dic):
    if not hasattr(dic, 'fixed cost per year'):
        dic = fixed_cost_per_year(**dic)
    dic['fixed cost per hr'] = dic['fixed cost per year']/HOURS_PER_YEAR
    if 'capital cost (kg)' in dic.keys():
        dic['fixed cost per hr (kg)'] = dic['fixed cost per year (kg)']/HOURS_PER_YEAR
    dic['value'] = dic['fixed cost per hr']
    return dic



#----------------------------------------------------------------------
# Cost that can be varied.
# Default values are based on cited literature
#----------------------------------------------------------------------

# "Adding engineering, construction, legal expenses and contractor’s fees, the fixed capital investment (FCI)"
# is calculated as: FCI = SF * Total Purchase Cost
# scale factor, D.H. König et al. / Fuel 159 (2015) 289–297
CHEM_PLANT_CAP_SF = 4.6

# https://www.usinflationcalculator.com/ 3 June 2020 (2019 values didn't change compared to 3 Feb 2020 values for 2020)
USD2005_to_USD2019 = 1.31
USD2008_to_USD2019 = 1.19
USD2010_to_USD2019 = 1.17
USD2015_to_USD2019 = 1.08
USD2016_to_USD2019 = 1.07

FIXED_COST_ELECTROLYZER = {
    'capital cost (kg)' : (118.0e6)*USD2010_to_USD2019/(50000/24), # 118 M$(2010) NREL H2A / 50,000 kg H2 per day; ($/kg H2 generation)
    'capital cost' : (118.0e6)*USD2010_to_USD2019/(50000/24)/lhvH2Conv, # ($/kWh LHV H2 generation)
    'assumed lifetime' : 10, # (yr)
    'capacity factor' : 1.00, # 100%
    #'value' : 1.4300E-02 # ($/h)/kW
}



FIXED_COST_COMPRESSOR = {
    'capital cost (kg)' : (2.07e6)*USD2016_to_USD2019/(58000/24), # 2.07 M$(2016) NREL H2A / 50,000 kg H2 per day; ($/kg H2 generation)
    'capital cost' : (2.07e6)*USD2016_to_USD2019/(58000/24)/lhvH2Conv, # ($/kWh LHV H2 generation)
    'assumed lifetime' : 15, # (yr)
    'capacity factor' : 1.00, # 100%
    #'value' : 1.4300E-02 # ($/h)/kW
}



FIXED_COST_H2_STORAGE = {
    'capital cost (kg)' : 7.43e6*USD2016_to_USD2019/1160000, # 7.43 M$(2016) / 1,160,000 kg usable volume H2, source NREL H2A; ($/kg H2 storage)
    'capital cost' : 7.43e6*USD2016_to_USD2019/1160000/lhvH2Conv, # ($/kWh LHV storage)
    'fixed annual OandM cost (kg)' : 582000*USD2005_to_USD2019/1160000, # 582,000 $(2005) fixed O&M for facility
    'fixed annual OandM cost' : 582000*USD2005_to_USD2019/1160000/lhvH2Conv, # 582,000 $(2005 fixed O&M for facility
    'assumed lifetime' : 30, # (yr)
    #'value' : 2.7205E-07, # $/kWh
}



FIXED_COST_CHEM_PLANT = {
    'capital cost' : ((202+32+32)*1e6*CHEM_PLANT_CAP_SF)/(690*1000)*USD2015_to_USD2019, # ($/kW generation or conversion)
    'capital cost (kg)' : ((202+32+32)*1e6*CHEM_PLANT_CAP_SF)/56300*USD2015_to_USD2019, # ($/kW generation or conversion)
            # ($202+32+32)*4.6/690MW of liquid fuel produced for FT, Hydrocracker, RWGS) = fixex costs = cap ex*multiplier, Table 3 chem plant, D.H. König et al. / Fuel 159 (2015) 289–297
    'assumed lifetime' : 30, # (yr)
            # D.H. König et al. / Fuel 159 (2015) 289–297, pg 293
    #'value' : 1.6303E-02 # ($/h)/kW
}






VAR_COST_CHEM_PLANT = {
    #'value' : 6.91E-02, # $/kWh = 18.62*(0.069+0.038+0.016+0.001)/(MMBtu_per_Gallon_Gasoline*MWh_per_MMBtu)  # Variable O&M cost ($/MWh)
                                    # order is: maintenance, taxes & incentives, utilities, clean water
    'value' : 18.62*(0.069+0.038+0.016+0.001)/(MMBtu_per_Gallon_Gasoline*MWh_per_MMBtu) * (1./1000)*USD2015_to_USD2019, # Variable O&M cost ($/kWh)
    'value( kg)' : 6.83*(0.069+0.038+0.016+0.001)*USD2015_to_USD2019, # Variable O&M cost ($/kg)
    'ref' : 'Fig 4b, cost break down of $/GGE, excluding electrolyzer and cap annual, D.H. König et al. / Fuel 159 (2015) 289–297'

}


# $/kWh liquid hydrocarbons
def var_cost_of_CO2(**dic):
    # value = CO2 cost ($/metric ton) * (236 tons hr^-1 / 690 MW of liquid hydrocarbons ) * (1 MW / 1000 kW)
    # 'table 2, CO2 tons/hr / MW liquid hydrocarbons, D.H. König et al. / Fuel 159 (2015) 289–297'
    dic['value'] = dic['co2 cost']*(236/690)*(1/1000) # $/kWh liquid hydrocarbons
    return dic


VAR_COST_CO2 = {
    'co2 cost' : 50, # $/metric ton CO2
    #'value' : 1.71E-02, # (for $50/ton) # $/kWh liquid hydrocarbons = CO2 cost ($/metric ton) * (236 tons hr^-1 / 690 MW of liquid hydrocarbons ) * (1 MW / 1000 kW)
    'ref' : 'table 2, CO2 tons/hr / MW liquid hydrocarbons, D.H. König et al. / Fuel 159 (2015) 289–297'
}


EFFICIENCY_ELECTROLYZER_COMP = {
    'value' : .607, # LHV; Calculated from NREL H2A electrolyzer full eff. and compressor; see eta_PtCompH2 in my paper
    'ref' : 'Calculated from NREL H2A electrolyzer full eff. and compressor; see eta_PtCompH2 in my paper'
}


EFFICIENCY_CHEM_CONVERSION = {
    'value' : 0.682,
    'ref' : 'table 2, eta_CCE accounts for losses when converting H2 and CO2 into liquid hydrocarbons, D.H. König et al. / Fuel 159 (2015) 289–297'
}


EFFICIENCY_CHEM_PLANT = {
    'value' : 0.659,
    'ref' : 'table 2, eta_plant = chem plant efficiency, D.H. König et al. / Fuel 159 (2015) 289–297'
}


DECAY_RATE_H2_STORAGE = {
    'value' : 1.14E-08, # fraction per hour (0.01% per year)    
    'ref' : 'Crotogino et al., 2010, p43'
}

def return_fuel_system():
    system = {
        'FIXED_COST_ELECTROLYZER' : FIXED_COST_ELECTROLYZER,
        'FIXED_COST_COMPRESSOR' : FIXED_COST_COMPRESSOR,
        'FIXED_COST_CHEM_PLANT' : FIXED_COST_CHEM_PLANT,
        'FIXED_COST_H2_STORAGE' : FIXED_COST_H2_STORAGE,
        'VAR_COST_CHEM_PLANT' : VAR_COST_CHEM_PLANT,
        'VAR_COST_CO2' : VAR_COST_CO2,
        'EFFICIENCY_ELECTROLYZER_COMP' : EFFICIENCY_ELECTROLYZER_COMP,
        'EFFICIENCY_CHEM_PLANT' : EFFICIENCY_CHEM_PLANT,
        'EFFICIENCY_CHEM_CONVERSION' : EFFICIENCY_CHEM_CONVERSION,
        'DECAY_RATE_H2_STORAGE' : DECAY_RATE_H2_STORAGE,
    }
    for vals in ['FIXED_COST_ELECTROLYZER', 'FIXED_COST_COMPRESSOR', 'FIXED_COST_CHEM_PLANT', 'FIXED_COST_H2_STORAGE']:
        system[vals] = capital_recovery_factor(DISCOUNT_RATE, **system[vals])
        system[vals] = fixed_cost_per_hr(**system[vals])
    system['VAR_COST_CO2'] = var_cost_of_CO2(**system['VAR_COST_CO2'])
    return system



def add_carbon_price(electricity_price, carbon_content, carbon_price):

    elec_plus_carbon_price = electricity_price # electricity_price ($/kWh)
    elec_plus_carbon_price += carbon_content * carbon_price # carbon_content (tons/kWh), carbon_price ($/ton)
    #print(round(electricity_price,4), round(carbon_content,8), round(carbon_price,4), round(elec_plus_carbon_price,4))

    return elec_plus_carbon_price



def get_h2_system_costs(system, electricity_price, verbose=False):
    if verbose:
        print(f"Electricity price: {electricity_price}")
    tot = 0.
    tot += system['FIXED_COST_ELECTROLYZER']['value'] / system['FIXED_COST_ELECTROLYZER']['capacity factor']
    if verbose:
        print(f" FIXED_COST_ELECTROLYZER to add: {system['FIXED_COST_ELECTROLYZER']['value'] / system['FIXED_COST_ELECTROLYZER']['capacity factor']}, new total {tot}")
    tot += system['FIXED_COST_COMPRESSOR']['value'] / system['FIXED_COST_COMPRESSOR']['capacity factor']
    if verbose:
        print(f" FIXED_COST_COMPRESSOR   to add: {system['FIXED_COST_COMPRESSOR']['value'] / system['FIXED_COST_COMPRESSOR']['capacity factor']}, new total {tot}")
    tot += electricity_price / system['EFFICIENCY_ELECTROLYZER_COMP']['value']
    if verbose:
        print(f" ELECTRICITY COSTS       to add: {electricity_price / system['EFFICIENCY_ELECTROLYZER_COMP']['value']}, new total {tot}")
    tot += system['FIXED_COST_H2_STORAGE']['value'] * 30 * 24 # 30 days x 24 hours for 1 month of storage capacity
    if verbose:
        print(f" FIXED_COST_H2_STORAGE   to add: {system['FIXED_COST_H2_STORAGE']['value'] * 30 * 24}, new total {tot}")
    return tot

def get_fuel_system_costs(system, electricity_price, verbose=False):
    if verbose:
        print(f"Electricity price: {electricity_price}")
    tot = 0.
    tot += system['FIXED_COST_ELECTROLYZER']['value'] / (system['EFFICIENCY_CHEM_CONVERSION']['value'] * system['FIXED_COST_ELECTROLYZER']['capacity factor'])
    if verbose:
        print(f" FIXED_COST_ELECTROLYZER to add: {system['FIXED_COST_ELECTROLYZER']['value'] / (system['EFFICIENCY_CHEM_CONVERSION']['value'] * system['FIXED_COST_ELECTROLYZER']['capacity factor'])}, new total {tot}")
    tot += system['FIXED_COST_COMPRESSOR']['value'] / (system['EFFICIENCY_CHEM_CONVERSION']['value'] * system['FIXED_COST_COMPRESSOR']['capacity factor'])
    if verbose:
        print(f" FIXED_COST_COMPRESSOR   to add: {system['FIXED_COST_COMPRESSOR']['value'] / (system['EFFICIENCY_CHEM_CONVERSION']['value'] * system['FIXED_COST_COMPRESSOR']['capacity factor'])}, new total {tot}")
    tot += electricity_price / (system['EFFICIENCY_ELECTROLYZER_COMP']['value'] * system['EFFICIENCY_CHEM_CONVERSION']['value'])
    if verbose:
        print(f" ELECTRICITY COSTS       to add: {electricity_price / (system['EFFICIENCY_ELECTROLYZER_COMP']['value'] * system['EFFICIENCY_CHEM_CONVERSION']['value'])}, new total {tot}")
    tot += system['FIXED_COST_H2_STORAGE']['value'] * 30 * 24 / system['EFFICIENCY_CHEM_CONVERSION']['value'] # 30 days x 24 hours for 1 month of storage capacity
    if verbose:
        print(f" FIXED_COST_H2_STORAGE   to add: {system['FIXED_COST_H2_STORAGE']['value'] * 30 * 24 / system['EFFICIENCY_CHEM_CONVERSION']['value']}, new total {tot}")
    tot += system['FIXED_COST_CHEM_PLANT']['value']
    if verbose:
        print(f" FIXED_COST_CHEM_PLANT   to add: {system['FIXED_COST_CHEM_PLANT']['value']}, new total {tot}")
    tot += system['VAR_COST_CHEM_PLANT']['value'] # Values from Konig already incorporate chem plant eff.
    if verbose:
        print(f" VAR_COST_CHEM_PLANT     to add: {system['VAR_COST_CHEM_PLANT']['value']}, new total {tot}")
    tot += system['VAR_COST_CO2']['value'] # Does not depend on chem plant eff.
    if verbose:
        print(f" VAR_COST_CO2            to add: {system['VAR_COST_CO2']['value']}, new total {tot}")
    return tot


# Calulate the break even point for refueling for a vehicle owner 
# where price of gasoline = cost of H2 as a function of the price of CO2.
# This includes the cost of dispensing H2
def calc_carbon_price_break_even(system, dispensing_h2_cost, electricity_price, elec_carbon_content, 
        gasoline_price, FCEV_mpgge, ICE_mpg, verbose=False):

    # We are solving this equation for p_co2
    # 0 = fixed_h2 + disp_h2 + (elec_0 + elec_co2*p_co2)/eta - gas_0 - gas_co2*p_co2
    # where, h2_0 = fixed_h2 + disp_h2 + elec_0/eta

    per_kg_h2_to_mpgge = 1./kWh_LHV_per_kg_H2*kWh_to_GGE/FCEV_mpgge

    h2_0 = 0
    h2_0 += system['FIXED_COST_ELECTROLYZER']['value'] / system['FIXED_COST_ELECTROLYZER']['capacity factor']
    h2_0 += system['FIXED_COST_COMPRESSOR']['value'] / system['FIXED_COST_COMPRESSOR']['capacity factor']
    h2_0 += electricity_price / system['EFFICIENCY_ELECTROLYZER_COMP']['value']
    h2_0 += system['FIXED_COST_H2_STORAGE']['value'] * 30 * 24 # 30 days x 24 hours for 1 month of storage capacity
    if verbose:
        print(f"Prod {round(h2_0,4)} $/kWh")
    h2_0 *= kWh_LHV_per_kg_H2
    if verbose:
        print(f"Prod {round(h2_0,4)} $/kg")
    h2_0 += dispensing_h2_cost
    if verbose:
        print(f"Prod + disp {round(h2_0,4)} $/kg")
    h2_0 *= per_kg_h2_to_mpgge
    if verbose:
        print(f"Prod + disp {round(h2_0,4)} $/mile\n")

    gas_0 = gasoline_price/ICE_mpg

    to_div = (elec_carbon_content * kWh_LHV_per_kg_H2 * per_kg_h2_to_mpgge / system['EFFICIENCY_ELECTROLYZER_COMP']['value'] -
            co2_per_gallon_gas/ICE_mpg)

    p_co2 = (gas_0 - h2_0) / to_div

    if verbose:
        print(f"electricity_price: {electricity_price}\nelec_carbon_content: {elec_carbon_content}\ngasoline_price: {gasoline_price}\nFCEV_mpgge: {FCEV_mpgge}\nICE_mpg: {ICE_mpg}\n")
        print(f"h2_0: {round(h2_0,4)}\ngas_0: {round(gas_0,4)}\nto_div: {round(to_div,6)}\np_co2: {round(p_co2,4)}\n")

    return p_co2, to_div




