# Results files

The files contained in here are for a number of different scenarios:

## Scenarios
 - *20200805_v2* = basecase scenarios used in the main text
 - *20201201_v8pgp* = scenarios with PGP enabled
 - *20201116_v5fullReli* = scenarios with the demand response mechanism disabled (100% of firm load is supplied for all hours)
 - *20200805_v5* = hydrogen storage and chemical plant are added to produce electrofuels


## Sensitivity
Additionally, there is a folder with results from a cost sensitivity analysis with files named appropriately based on the fraction of the basecase costs attributed to each tech.

`cost_sensitivity`

The naming for the cost reductions is:
 * EL = electrolyzer
 * NG = natural gas with CCS
 * SOL = solar
 * WIND = wind

Thus, SOL0.75 means the solar capital costs were reduced to 75% of the basecase


## Dispatch curve

The dispatch curve figure (fig 4) can be recreated with the results files in `dispatch_curve`
