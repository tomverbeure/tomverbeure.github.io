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
        
R1_values   = [ '1k', '2k', '5k', '10k' ]
C1_values   = [ '1u', '2u', '5u', '10u' ]

R1_values   = [ '1k', '2k', '4k' ]
C1_values   = [ '1u', '3u' ]

sims = [
        { "name": "tran", "instruction": ".tran 50m startup" }, 
        { "name": "ac",   "instruction": ".ac dec 10 1 100k" } 
    ]

runner = PyLTSpice.SimRunner(output_folder=output_dir, simulator=PyLTSpice.LTspice, parallel_sims=8)

for sim in sims:
    sim_name        = sim["name"]
    sim_instruction = sim["instruction"]

    netlist.add_instructions(sim_instruction)

    for R1_value in R1_values:
        for C1_value in C1_values:
            print(f"Simulating sim={sim_name} R1={R1_value}, C1={C1_value}")
    
            # Set R1 and C1 value
            netlist.set_component_value('R1', R1_value)
            netlist.set_component_value('C1', C1_value)
    
            # Run simulation
            run_netlist_filename = f"{asc_filename.stem}_R1={R1_value}_C1={C1_value}_{sim_name}.run.net"
            runner.run(netlist, run_filename=run_netlist_filename)

runner.wait_completion()

figure, axes_list = plt.subplots(len(C1_values),len(R1_values))
print(axes_list)

axes_cnt     = 0
for raw_filename, log_filename in runner:
    print(log_filename)

    log_info = PyLTSpice.LTSpiceLogReader(log_filename)
    #log_info.read_measures()

    if "rise_time" in log_info.dataset:
        print(f"rise_time = {log_info.dataset["rise_time"]}")
        print(f"start_rise = {log_info.dataset["start_rise"]}")
    
    raw_info    = PyLTSpice.RawRead(raw_filename)

    if 'time' in raw_info.get_trace_names():
        rise_time   = log_info.dataset["rise_time"][0]
        start_rise  = log_info.dataset["start_rise"][0]
        end_rise    = log_info.dataset["end_rise"][0]
        print(rise_time, start_rise, end_rise)

        print(raw_info.get_trace_names())

        vin_info    = raw_info.get_trace('V(in)')
        vout_info   = raw_info.get_trace('V(out)')

        x_data      = raw_info.get_axis()
        vin_data    = vin_info.get_wave()
        vout_data   = vout_info.get_wave()

        c1_idx  = axes_cnt % len(C1_values)
        r1_idx  = axes_cnt // len(C1_values)

        axes    = axes_list[c1_idx][r1_idx]

        axes.grid(True)

        axes.plot(x_data, vin_data)
        axes.plot(x_data, vout_data)
        axes.axvline(x=start_rise, color='red', linestyle='--', linewidth=1)
        axes.axvline(x=end_rise, color='red', linestyle='--', linewidth=1)
        axes.set_title(f"R1={R1_values[r1_idx]}, C1={C1_values[c1_idx]}")
        axes.text(0.98, 0.05, f"rise time: {round(rise_time * 1000, 1)} ms", transform=axes.transAxes, ha='right', va='bottom')

        axes_cnt    += 1

figure.suptitle("Rise time of R/C circuit")
figure.tight_layout()
plt.show()

