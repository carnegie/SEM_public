#!/usr/bin/env bash


Date="20200725" # Good nuclear
version="v5"
#Date="20200802" # Nuclear zero unmet demand
#version="v3"
Date="20200803" # NatGas+CCS
version="v2"
#ARGS="run_sem make_results_file"
#ARGS="make_results_file"
ARGS="run_sem make_results_file make_plots"
ARGS="make_plots"
ARGS="make_results_file"
ARGS="make_plots"




#Date="20200805" # NatGas+CCS H2_ONLY
#version="v2"
#for CASE in \
#        "Case5_WindSolarStorage" \
#        "Case7_NatGasCCS" \
#        "Case9_NatGasCCSWindSolarStorage" \
#        ; do
#    #./run_SEM_configs_fuels.py "date_$Date" $CASE "version_$version" $ARGS H2_ONLY
#    ./curtailment_figures.py "date_$Date" $CASE "version_$version" $ARGS H2_ONLY
#done

#######################################################################
#### Used for final results figures for systems making electrofuels ###
#######################################################################
#Date="20200805" # NatGas+CCS
#version="v5"
#ARGS="make_plots"
#for CASE in \
#        "Case5_WindSolarStorage" \
#        "Case7_NatGasCCS" \
#        "Case9_NatGasCCSWindSolarStorage" \
#        ; do
#    ./run_SEM_configs_fuels.py "date_$Date" $CASE "version_$version" $ARGS
#    #./curtailment_figures.py "date_$Date" $CASE "version_$version" $ARGS
#done


##Date="20200805" # NatGas+CCS H2_ONLY
##version="v2"
##./curtailment_figures.py "date_$Date" "Case_ALL" "version_$version" $ARGS H2_ONLY

#ARGS="make_plots"
#Date="20201116" # NatGas+CCS H2_ONLY
##./run_SEM_configs_fuels.py "date_$Date" "Case9_NatGasCCSWindSolarStorage" "version_v1" $ARGS H2_ONLY
##./run_SEM_configs_fuels.py "date_$Date" "Case5_WindSolarStorage" "version_v2" $ARGS H2_ONLY
#./XXX_run_SEM_configs_fuels.py "date_$Date" "Case5_WindSolarStorage" "version_v2" $ARGS H2_ONLY
##./run_SEM_configs_fuels.py "date_$Date" "Case5_WindSolarStorage" "version_v3" $ARGS H2_ONLY
##./run_SEM_configs_fuels.py "date_$Date" "Case9_NatGasCCSWindSolarStorage" "version_v4" $ARGS H2_ONLY


Date="20201116"
ARGS="make_plots"
version="v5fullReli"
version="v6pgp"
version="v7pgp"
#for CASE in \
#        "Case5_WindSolarStorage" \
#        "Case7_NatGasCCS" \
#        "Case9_NatGasCCSWindSolarStorage" \
#        ; do
#    #./run_SEM_configs_fuels.py "date_$Date" $CASE "version_$version" $ARGS
#    ./pgp-style_curtailment_figures.py "date_$Date" $CASE "version_$version" $ARGS H2_ONLY INCLUDE_PGP
#    #./pgp-style_curtailment_figures.py "date_$Date" $CASE "version_$version" $ARGS H2_ONLY
#done

version="v7pgp"
#./pgp-style_curtailment_figures.py "date_$Date" "Case_ALL" "version_$version" $ARGS H2_ONLY INCLUDE_PGP

Date="20201201"
version="v8pgp"
#./pgp-style_curtailment_figures.py "date_$Date" "Case_ALL" "version_$version" $ARGS H2_ONLY INCLUDE_PGP

Date="20200805" # NatGas+CCS H2_ONLY
version="v2"
#./curtailment_figures.py "date_$Date" "Case_ALL" "version_$version" $ARGS H2_ONLY
./singles_curtailment_figures.py "date_$Date" "Case_ALL" "version_$version" $ARGS H2_ONLY
