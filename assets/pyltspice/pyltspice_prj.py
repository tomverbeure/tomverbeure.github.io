#! /usr/bin/env python

from pathlib import Path
import PyLTSpice 
import matplotlib.pyplot as plt

asc_filename = Path("rc_schematic.asc")
output_dir = "./pyltspice_tmp"

if False:
    # Let LTspice create a .net file from an .asc file
    PyLTSpice.LTspice.create_netlist(asc_filename.name)
    netlist_file = asc_filename.with_suffix(".net")
    netlist = PyLTSpice.SpiceEditor(netlist_file)
else:
    # Only works on my system when PyLTSpice version 5.4.4 or later.
    netlist = PyLTSpice.SpiceEditor(asc_filename.name)
        
r1_values   = [ '1k', '2k', '4k' ]
c1_values   = [ '1u', '3u', '5u' ]
vin_values  = [ '1', '6' ]

sims = [
        { "name": "tran", "instruction": ".tran 50m startup" }, 
        { "name": "ac",   "instruction": ".ac dec 10 1 100k" } 
    ]

# PyLTSpice can launch multiple simulations in parallel. 8 is a number that worked for me,
# but it depends on your machine and on the design that you're simulating.
runner = PyLTSpice.SimRunner(output_folder=output_dir, simulator=PyLTSpice.LTspice, parallel_sims=8)

# The sim_nr_val measurement is used to map the simulation results to the simulation parameters. 
netlist.add_instructions(".meas sim_nr_val PARAM sim_nr")

sim_nr = 0

sim_params = []

for sim in sims:
    sim_name        = sim["name"]
    sim_instruction = sim["instruction"]

    # This overrides the simulation instructions that were already in the .asc file
    netlist.add_instructions(sim_instruction)

    for vin_idx, vin_value in enumerate(vin_values):
        for r1_idx, r1_value in enumerate(r1_values):
            for c1_idx, c1_value in enumerate(c1_values):
                print(f"Simulating sim={sim_name} Vin={vin_value} R1={r1_value}, C1={c1_value}")
    
                # Store all simulation parameters in a list for later retrieval when
                # post-processing the results
                sim_params.append(
                        {
                            "name"      : sim_name,
                            "vin_idx"   : vin_idx,
                            "r1_idx"    : r1_idx,
                            "c1_idx"    : c1_idx,
                        })

                # Set Vin value
                netlist.set_element_model('V1', f"PWL(0 0 2000u 0 2001u { vin_value }) AC { vin_value }")
        
                # Set R1 and C1 values in the schematic
                netlist.set_component_value('R1', r1_value)
                netlist.set_component_value('C1', c1_value)
    
                # Set a sim_nr parameter in the schematic. This value will be 'measured'
                # at the end of the simulation and will allow use to link a simulation result
                # to the parameters that were used.
                # Simulations aren't guaranteed to complete in the order they were started
                # so we need to have a unique ID per simulation to map results to the input.
                netlist.set_parameters(sim_nr=sim_nr)
        
                # Send a simulation to the run queue. Each simulation must have a unique
                # filename, otherwise multiple simulators running parallel will trample on each
                # other and overwrite different results. 
                # sim_nr is an incrementing value and thus guaranteed to be unique, but also add 
                # the other parameters. This make it easier to debug.
                run_netlist_filename = f"{asc_filename.stem}_sim_nr={sim_nr}_vin={vin_value}_r1={r1_value}_c1={c1_value}_{sim_name}.run.net"
                runner.run(netlist, run_filename=run_netlist_filename)
    
                sim_nr += 1

# Wait until all simulations have finished. This is just one way of doing things.
# An alternative way is to specify a callback function that gets called when
# a simulation has completed.
runner.wait_completion()

# Create 2 figures, one for each value of Vin.
# Each figure has a subplot for each combinations of R and C.
vin_figures    = []

for _ in vin_values:
    figure, ax_list = plt.subplots(len(c1_values),len(r1_values), figsize=(10,8))
    vin_figures.append( { "figure": figure, "ax_list": ax_list })

# Post-process all the simulation results...
for raw_filename, log_filename in runner:
    print(log_filename)

    # Extract all the data from the log and raw result files.
    log_info    = PyLTSpice.LTSpiceLogReader(log_filename)
    raw_info    = PyLTSpice.RawRead(raw_filename)

    print(raw_info.get_trace_names())

    # if 'time' is part of the trace_names, then it contains the results of
    # a TRAN simulation, not an AC simulation.
    if 'time' in raw_info.get_trace_names():

        # Get the results that were created with .meas commands.
        rise_time   = log_info.dataset["rise_time"][0]
        start_rise  = log_info.dataset["start_rise"][0]
        end_rise    = log_info.dataset["end_rise"][0]
        print(rise_time, start_rise, end_rise)
        print(log_info.dataset)

        vin_info    = raw_info.get_trace('V(in)')
        vout_info   = raw_info.get_trace('V(out)')

        x_data      = raw_info.get_axis()
        vin_data    = vin_info.get_wave()
        vout_data   = vout_info.get_wave()

        sim_nr      = log_info.dataset["sim_nr_val"][0]
        vin_idx     = sim_params[sim_nr]["vin_idx"]
        r1_idx      = sim_params[sim_nr]["r1_idx"]
        c1_idx      = sim_params[sim_nr]["c1_idx"]

        ax          = vin_figures[vin_idx]["ax_list"][c1_idx][r1_idx]

        ax.set_title(f"R1={r1_values[r1_idx]}, C1={c1_values[c1_idx]}")
        ax.grid(True)

        ax.plot(x_data, vin_data)
        ax.plot(x_data, vout_data)

        # Only do rise/fall times for Vin == 1V
        if vin_idx == 0:
            # Red vertical lines show the start and end points that were used
            # to determine the rise time.
            ax.axvline(x=start_rise, color='red', linestyle='--', linewidth=1)
            ax.axvline(x=end_rise, color='red', linestyle='--', linewidth=1)
    
            # Put the rise time at the bottom-right of each plot.
            ax.text(0.95, 0.05, 
                        f"rise time: {round(rise_time * 1000, 1)} ms", 
                        transform=ax.transAxes, ha='right', va='bottom', 
                        bbox=dict(facecolor='white', alpha=1.0, edgecolor='black') )

for vin_idx, vin_figure in enumerate(vin_figures):
    figure = vin_figure["figure"]
    figure.suptitle(f"Rise time of an R/C circuit - Vin={ vin_values[vin_idx] }")
    figure.tight_layout()
    figure.savefig(f"plot_vin_{ vin_values[vin_idx] }.png", dpi=100)

plt.show()
