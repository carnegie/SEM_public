#!/usr/bin/env bash


#####################################################################################
### Make final figures for basecase scenarios in main text  (fig 2, 3, 5, 6)      ###
#####################################################################################
Date="20200805" # NatGas+CCS H2_ONLY
version="v2"
./curtailment_figures.py "date_$Date" "Case_ALL" "version_$version" $ARGS H2_ONLY

################################################################################################################
### Make final figures for scenarios without demand response mechanism (100% reliability) (fig S.9 - S.11)   ###
################################################################################################################
Date="20201116" # NatGas+CCS H2_ONLY
version="v5fullReli"
./curtailment_figures.py "date_$Date" "Case_ALL" "version_$version" $ARGS H2_ONLY


###################################################################################
### Make final figures for scenarios with PGP enabled plots  (fig S.14 - S.16)  ###
###################################################################################
Date="20201201"
version="v8pgp"
./pgp-style_curtailment_figures.py "date_$Date" "Case_ALL" "version_$version" $ARGS H2_ONLY INCLUDE_PGP


#######################################################################################
### Used for final results figures for systems making electrofuels (fig S.12, S.13) ###
#######################################################################################
Date="20200805" # NatGas+CCS
version="v5"
ARGS="make_plots"
for CASE in \
        "Case5_WindSolarStorage" \
        "Case7_NatGasCCS" \
        "Case9_NatGasCCSWindSolarStorage" \
        ; do
    ./run_SEM_configs_fuels.py "date_$Date" $CASE "version_$version" $ARGS
done


######################################################################
### Make final cost sensitivity plots (fig S.7 and S.8)            ###
######################################################################
python sensitivity_plots.py



######################################################################
### Make final dispatch figure (fig 4)                             ###
######################################################################
python helpers.py
