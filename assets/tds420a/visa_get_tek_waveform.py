#! /usr/bin/env python3

import pyvisa
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt

rm = pyvisa.ResourceManager()
g = rm.open_resource('GPIB0::1::INSTR')

# Don't repeat the command in the reply. This is easier to parse the result.
g.write("HEAD OFF")

# Encode the waveform as a comma-separated list
g.write("DATA:ENC ASCI")

# Record 500 waveform samples
g.write("HOR:RECORDL 500");

# Setup a single sequence acquisition
g.write("ACQ:STOPA SEQ")

# Don't do repetitive acquisition (~equivalent-time operation)
g.write("ACQ:REPE OFF")

# Start acquiring data
g.write("ACQ:STATE RUN")

# Request data from channel 1 only
g.write("DATA:SOURCE CH1")

# Get all waveform acquisition settings needed decode the sample points values: vdiv, number of sample points etc.
wf_params = g.query("WFMPRE?")
print(wf_params)

# Get the sample points
wf = g.query("CURV?")
print(wf)

# Convert comma separate string of signed integer values to list of integers
values = list(map(int, wf.split(",")))


# Plot
x = range(0, len(values))
plt.plot(x, values)
plt.show()


