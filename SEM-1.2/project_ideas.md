# Project ideas for SEM

Proposed model applications (each one could be a separate peer-reviewed paper)

<b>Scenarios development </b>

<b>--</b> ELECTRIC SECTOR ONLY: Create N baseline reference scenarios that can be used in all future techno-economic assessments (expected N in the range of 3 to 5?). Consider normalizing costs in all scenarios so that the baseline total system cost is the same in each scenario (i.e., other values could be interpreted as % change in total system cost).

<b>--</b> Markov approach to scenarios development: Choose baseline parameters representing current costs. Perform simulations where parameter values are varied randomly between 0 and today’s value. Perform cluster analysis on results to examine structures of resulting optimal energy systems. Pick representative members from each cluster to use as baseline scenarios.

<b>--</b> Expert elicitation approach to scenarios development: Ask experts to predict future costs of different technologies. Perform simulations where expert assessments of future costs are mixed and matched. Perform cluster analysis on results to examine structures of resulting optimal energy systems. Pick representative members from each cluster to use as baseline scenarios.

<b>--</b> Scenarios development FULL ELECTRICITY + FUELS: Create N baseline reference scenarios that can be used in all future techno-economic assessments (expected N in the range of 3 to 5?). Consider normalizing costs in all scenarios so that the baseline total system cost is the same in each scenario (i.e., other values could be interpreted as percent change in total system cost).

<b>--</b> Markov approach to scenarios development: Choose baseline parameters representing current costs. Perform simulations where parameter values are varied randomly between 0 and today’s value. Perform cluster analysis on results to examine structures of resulting optimal energy systems. Pick representative members from each cluster to use as baseline scenarios.

<b>--</b> Expert elicitation approach to scenarios development: Ask experts to predict future costs of different technologies. Perform simulations where expert assessments of future costs are mixed and matched. Perform cluster analysis on results to examine structures of resulting optimal energy systems. Pick representative members from each cluster to use as baseline scenarios.

<b>General project ideas</b>

<b>--</b> Review paper on assumed costs and model results for energy mix

<b>--</b> Value of innovation. Against the backdrop of the 100,000 Markov simulations (or if basins of attractions exist, then representative energy system architectures) from the previous ideas, look at the distribution of partial derivatives of system cost to each parameter value. Which innovations help a little bit in almost every possible future? Which help a lot in a narrow range of futures? What has to be true for that innovation to have high value? [Basic idea is that something like ability to time shift demand would have value in almost any conceivable future, whereas a 1% reduction of cost of CCS would only have value in futures where CCS is already playing a substantial role?]

<b>--</b> Considering a renewable plus dispatchable (e.g., natural gas) system, and assuming dispatchable nuclear technologies, how does the penetration of renewables and the dispatchable technology vary with the capital cost of nuclear? (Mengyao)
How much dispatchable near-zero emission electricity (say, from geothermal) do you need to facilitate reliance on intermittent renewable energy as a electricity source?

<b>--</b> For scenarios with high penetration of wind and solar, how much of the need for storage and/or dispatchable energy is a consequence of variability of energy supply and how much is a consequence of variability in energy demand? Consider cases with constant and variable energy production and constant and variable energy demand and estimate storage/dispatchable-energy requirements to provide reliability.

<b>--</b> Cluster analysis of wind resources. Can wind be clumped into different resource categories with similar characteristics, and then let the optimization model choose from among those categories.

<b>--</b> How does the introduction of a major carbon-neutral fuels demand shape the electric production sector? For each of the base scenarios, ramp electricity-derived fuels demand from zero to something that is similar to today’s ratio of fuel-energy-end-use to electric-energy-end-use. Make figures showing how the optimal mix of technologies varies with amount of fuels production. In each scenario, how does system cost vary with amount of fuel produced?

<b>--</b> How does the existence of a BECCS-like technology that removes CO2 from the atmosphere in a baseline mode affect the attractiveness of fossil fuels like natural gas and electricity-derived carbon-neutral fuels for the hardest to decarbonize parts of the energy system? How would the solution vary with carbon price?

<b>--</b> What are the tradeoffs between burning biomass in, say, a BECCS facility vs. using that C to make hydrocarbon fuels?

<b>--</b> What is the relative value of baseload vs. dispatchable power as a function of fixed and variable costs? For each of the base scenarios, create a plot that would have fixed cost on the x-axis and variable cost on the y-axis, where the value shown would be the reduction in system cost resulting from introducing a dispatchable power source with those cost characteristics minus the reduction in system cost resulting from introducing a constant baseload power source with those cost characteristics. (If ramp rate is in the model, it could be not a binary baseload vs. dispatchable, but consider the problem as a function of ramp rate. What is the value of being able to ramp seasons versus days versus hours?)

<b>--</b> Under what circumstances can a lower capital cost battery with lower round-trip efficiency compete with a costlier more-efficient battery? For each of the base scenarios, show market penetration and reduction in system cost as a function of battery capital cost (x-axis) and battery round-trip efficiency (y-axis).

<b>--</b> Crazy idea:  Evolution of an energy ecosystem. What if successful technologies duplicated themselves with inheritable variation, and then you allow the energy ecosystem to evolve? (Need to define trade-offs in evolutionary space.)

<b>--</b> If the dispatchable generation sector needed to use electricity-derived fuels (i.e., fuels as battery), what would the cost and performance characteristics of the fuel-based technologies need to be relative to the battery based technologies in order to compete? And how would this conclusion differ if there were a broader electricity-to-fuels market? [If there is a broader fuels market, it seems like you would never burn fuels to make electricity, since you would probably just back off of fuels production; so in a widespread electricity-to-fuels system, the value of batteries and dispatchable power could be quite low.] (Depends on fixed costs for fuel production facilities.) [Close to or identical to the fuels idea for Jackie.]

<b>--</b> What would the fixed and variable costs of solar-to-fuels need to be to compete with grid-electricity-to-fuels as a function of its fixed and variables costs?

<b>--</b> Demand management (unmet demand). Replace constant cost of not meeting demand with a cost curve representing increasing cost per kWh not delivered as a function of number of kWh of electricity not delivered. What is the benefit to overall system cost of reducing cost of unmet demand at different points in the cost curve. Should we focus on easy things (run the dishwasher later) or the hard things (keep electricity flowing to the hospitals)?

<b>--</b> Demand management (time shifting). I am not sure how to represent this in this modeling framework (maybe as some sort of battery that can hold negative charge?), but the idea is what is the value of shifting demand in time. Factors considered could be rate-based (how much demand can be shifted at a given time: similar to maximum discharge rate on a battery) or amount based (similar to battery capacity).

<b>--</b> How much dispatchable hydropower would you need to make a difference? How does system cost reduction scale with the amount of stored energy, and the instantaneous rate at which it could be delivered, and the annual mean rate of delivery?
How much pumped hydro would you need to make a difference? How would system cost reduction scale with the amount of pumped hydro storage, the maximum rate of upward pumping, and the maximum rate of generation?

<b>Regionality:</b>

<b>--</b> What is the value of continental scale and global scale electric grids? Divide world into regions (i.e., continents), sub-regions (i.e., large countries and clusters of small countries), and sub-sub-regions (e.g., ISO regions or states, smaller countries). Perform analyses where wind and solar resources are aggregated at each scales and in different regions of the globe. Compare total system cost of a large aggregated area relative to the sum of costs for separate systems for each sub-area. (Note that instead of aggregating solar it would be possible to represent in the larger area solar and wind generation in each sub area, to allow for more strategic placement of wind and solar generation facilities.)

<b>--</b> How much do optimal regional scale grids differ based on geophysical characteristics of a region? Is it possible that nuclear could win in Northern Europe but solar win in peri-saharan Africa? How different are the regional scale grids for the N baseline scenarios established above.

<b>--</b> Effect of cost and performance characteristics of regional interconnects on energy system structure. Create a regionalized form of the models with M independent regions. Vary cost and performance characteristics from those of present-day HVDC to free and perfect superconductors. How does the overall system cost and energy structure change with the cost and performance characteristics of the long-distance electricity transmission? This could be done for, say, regions within the United States or continental regions going to a global grid.

<b>--</b> Effect of cost and performance characteristics of inter-regional fuel transportation. Create a regionalized form of the models with M independent regions. Vary cost and performance characteristics of inter-regional fuel shipment. How does the overall system cost and energy structure change with the cost and performance characteristics of fuel shipment? How do things change if we now allow both inter-regional electricity transmission and fuel shipment?

<b>Transportation:</b>

<b>--</b> If we assume that fuel cars and battery cars had equal performance characteristics, how would the least-cost mix of fuel and battery cars vary as a function of fixed and variable costs of those cars, background scenario, etc? How does variability in automotive demand affect results? [Re-interpret this more broadly and think about potential deep electrification of the transportation sector.]

<b>--</b> Value of transportation efficiency gains.

<b>--</b> If we assume classes of driving ranges/vehicle masses, but add an energy penalty for the mass of fuel / electricity that needs to be carried on board, how does that affect the optimal mix of fuel vs battery cars?

<b>--</b> Does the economics of the energy system shift substantially if electric car batteries are allowed to be used for grid storage? How does variability in automotive demand affect results?
