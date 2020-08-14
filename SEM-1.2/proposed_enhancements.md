# Proposed Enhancements to SEM

<b>TECHNICAL ENHANCEMENTS</b>

<b>-- Derived values:</b> Create separate code between core_model.py and save_basic_results.py that would calculate derived values such as curtailments for each generation technologies, carbon emissions, etc

<b>-- Storage solution check:</b> Create code that would look at the solution and make sure there was no obviously aberrant behavior of dispatch to or from storage

<b>-- Specified capacities:</b> All users to enter capacity values as option keywords in case_input.py so that (some or all) capacities are specified rather than computed.

<b>-- Command line execution:</b> Create a form of the model where you can just type "sem case_input.csv" from the command line and run SEM with that case_input.csv file. This would allow having different names for the csv files and would also let SEM run without opening Spyder or some similar front end. This is probably a first step before parallelizing SEM.

<b>-- Get SEM running on clusters:</b> Create something that would allow hundreds or thousands of simulations to be run simultaneously on a cluster.

<b>-- Cross-case quicklook output:</b> Right now, the quicklook output looks only at a single case. We need to create some standardized quicklook figures that compare dispatch, capacities, etc, across cases.

<b>MODEL ENHANCEMENTS</b>

<b>-- Ramp rate constraints:</b> This need only be done if someone wants to investigate value of ramp rate.
  
<b>-- Load shifting:</b> Represent shifting of loads in time be creating a kind of battery that can have negative charge.

<b>-- Fuels:</b> Extend SEM beyond the electricity sector to consider fuels more completely.
