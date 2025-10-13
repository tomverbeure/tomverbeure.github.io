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
    # Only works on my system when PyLTSpice issue #151 is fixed
    netlist = PyLTSpice.SpiceEditor(asc_filename.name)
        
r1_values   = [ '1k', '2k', '4k' ]
c1_values   = [ '1u', '3u', '5u' ]

sims = [
        { "name": "tran", "instruction": ".tran 50m startup" }, 
        { "name": "ac",   "instruction": ".ac dec 10 1 100k" } 
    ]

runner = PyLTSpice.SimRunner(output_folder=output_dir, simulator=PyLTSpice.LTspice, parallel_sims=8)

netlist.add_instructions(".meas r1_idx_val PARAM r1_idx")
netlist.add_instructions(".meas c1_idx_val PARAM c1_idx")

for sim in sims:
    sim_name        = sim["name"]
    sim_instruction = sim["instruction"]

    # This overrides the simulation instructions that were already in the .asc file
    netlist.add_instructions(sim_instruction)

    for r1_idx, r1_value in enumerate(r1_values):
        for c1_idx, c1_value in enumerate(c1_values):
            print(f"Simulating sim={sim_name} R1={r1_value}, C1={c1_value}")
    
            # Set R1 and C1 value
            netlist.set_component_value('R1', r1_value)
            netlist.set_component_value('C1', c1_value)

            # Add dummy parameters that allows to determine which R and C values
            # of r1_values and c1_values were used without relying on the fact that
            # simulations finish in the same order as they were issued.
            netlist.set_parameters(r1_idx=r1_idx)
            netlist.set_parameters(c1_idx=c1_idx)
    
            # Send a simulation to the run queue. Each simulation must have a unique
            # filename, otherwise results may be overwritten.
            run_netlist_filename = f"{asc_filename.stem}_R1={r1_value}_C1={c1_value}_{sim_name}.run.net"
            runner.run(netlist, run_filename=run_netlist_filename)

# Wait until all simulations have finished. This is just one way of doing things.
# An alternative way is to specificy a callback function the gets called when
# a simulation has completed.
runner.wait_completion()

# Create a figure with a grid of plots so that
# all R and C combinations get their own graph.
figure, ax_list = plt.subplots(len(c1_values),len(r1_values), figsize=(10,8))

for raw_filename, log_filename in runner:
    print(log_filename)

    log_info    = PyLTSpice.LTSpiceLogReader(log_filename)
    raw_info    = PyLTSpice.RawRead(raw_filename)

    # if 'time' is part of the trace names, then it contains the results of
    # a TRAN simulation, not an AC simulation.
    if 'time' in raw_info.get_trace_names():

        # Get the results that were created with .meas commands.
        rise_time   = log_info.dataset["rise_time"][0]
        start_rise  = log_info.dataset["start_rise"][0]
        end_rise    = log_info.dataset["end_rise"][0]
        print(rise_time, start_rise, end_rise)
        print(log_info.dataset)

        print(raw_info.get_trace_names())

        vin_info    = raw_info.get_trace('V(in)')
        vout_info   = raw_info.get_trace('V(out)')

        x_data      = raw_info.get_axis()
        vin_data    = vin_info.get_wave()
        vout_data   = vout_info.get_wave()

        r1_idx      = log_info.dataset["r1_idx_val"][0]
        c1_idx      = log_info.dataset["c1_idx_val"][0]
        ax          = ax_list[c1_idx][r1_idx]

        ax.set_title(f"R1={r1_values[r1_idx]}, C1={c1_values[c1_idx]}")
        ax.grid(True)

        ax.plot(x_data, vin_data)
        ax.plot(x_data, vout_data)

        # Red vertical lines show the start and end points that were used
        # to determine the rise time.
        ax.axvline(x=start_rise, color='red', linestyle='--', linewidth=1)
        ax.axvline(x=end_rise, color='red', linestyle='--', linewidth=1)

        # Put the rise time at the bottom-right of each plot.
        ax.text(0.95, 0.05, 
                    f"rise time: {round(rise_time * 1000, 1)} ms", 
                    transform=ax.transAxes, ha='right', va='bottom', 
                    bbox=dict(facecolor='white', alpha=1.0, edgecolor='black') )

figure.suptitle("Rise time of an R/C circuit")
figure.tight_layout()
plt.savefig("plot.png", dpi=100)
plt.show()

