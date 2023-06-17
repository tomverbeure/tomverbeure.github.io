#! /usr/bin/env python3

from dataclasses import dataclass

import math
import numpy as np
import matplotlib.pyplot as plt

@dataclass
class Timestamp:
    ref_cnt:    float
    input_cnt:  float


# ref_freq:             the frequency of the measurement circuit
# input_freq:           the frequency of the signal to measure
# measurement_duration: duration of a single measurement, in seconds
# nr_measurements:      number of measurements that each have a duration of measurement duration
#
# Returns a list with pairs that contains the number of ref_freq counts, the number of input counts
# The numbers are fractional. 
def calc_timestamps(ref_freq, input_freq, measurement_duration, nr_measurements, ref_offset=0, random_dev=0, spread_spectrum_freq=0):
    timestamps = []

    accum_ref_cnt       = 0
    accum_input_cnt     = 0

    for m in range(nr_measurements):
        accum_ref_cnt       = (m+1) * measurement_duration * ref_freq + ref_offset + np.random.normal(scale=random_dev)
        accum_input_cnt     = (m+1) * measurement_duration * input_freq + 1 * math.sin(m * spread_spectrum_freq)

        ts =  Timestamp(accum_ref_cnt, accum_input_cnt)
        timestamps.append(ts)

    return timestamps

# timestamps: a list with (ref_clk, input_toggle) pairs.
# The input_toggle value is expected to be an integer. The ref_clk value can be fractional, but
# it's rounded down.
def linear_regression(ref_freq_hz, timestamps, input_freq_hz = None, log=False):
    sum_xy = 0
    sum_x  = 0
    sum_y  = 0
    sum_xx = 0

    results       = []
    results_delta = []

    for idx, ts in enumerate(timestamps):
        # int() because we always round down ref_clk.
        # To simulate in interpolating counter, this should be replaced by a rounding
        # down at a certain number of fractional digits.
        x = int(ts.ref_cnt)

        # Do round() instead of int() here, because calc_timestamp parameters were to chosen to generate y values 
        # that are integer. However, they're often n.99999.
        # In the real world, this will be the output of a counter and always an integer as well.
        y = round(ts.input_cnt)         

        recip = y/x * ref_freq_hz

        sum_xy += x * y
        sum_x  += x
        sum_y  += y
        sum_xx += x * x

        m = idx+1

        if m>1:
            lr = (m*sum_xy - sum_x*sum_y)/(m*sum_xx-sum_x*sum_x) * ref_freq_hz
        else:
            lr = 0

        if input_freq_hz is not None:
            recip_delta = recip - input_freq_hz
            lr_delta    = lr    - input_freq_hz

            if log:
                print("%5d: recip: %.15f lr: %.15f    recip_delta: %+.5e lr_delta: %+.5e" % (idx, recip, lr, recip_delta, lr_delta))
        else:
            if log:
                print("%5d: recip: %.15f lr: %.15f" % (idx, recip, lr))

        results.append( (recip, lr) )

    return results

def calc_single_measurement_duration(input_freq_hz, duration_s, nr_measurements):
    nr_input_cycles = input_freq_hz * duration_s
    nr_input_cycles_per_measurement = round(nr_input_cycles / nr_measurements)
    single_measurement_duration = nr_input_cycles_per_measurement / input_freq_hz

    return single_measurement_duration

def create_graph(filename, title, ref_freq_hz, input_freq_hz, duration_s, nr_measurements, spread_spectrum_freq=0):
    single_measurement_duration = calc_single_measurement_duration(input_freq_hz, duration_s, nr_measurements)
    timestamps = calc_timestamps(ref_freq_hz, input_freq_hz, single_measurement_duration, nr_measurements, ref_offset=-0.375, spread_spectrum_freq=spread_spectrum_freq)
    results = linear_regression(ref_freq_hz, timestamps, input_freq_hz)

    results_delta = []
    for r in results:
        results_delta.append( (abs(r[0]-input_freq_hz)/input_freq_hz, abs(r[1]-input_freq_hz)/input_freq_hz))

    results_delta=np.array(results_delta)
    results_delta[0,1]=None

    fig = plt.figure(figsize=(10,5))
    ax = fig.add_subplot(111)

    ax.plot(results_delta[:])

    ax.set_title(title)
    ax.set_xlabel('Samples')
    ax.set_ylabel('Error')

    desc  = "Ref Clk:      %.5fMHz\n" % (ref_freq_hz/1e6)
    desc += "Input:        %.5fMHz\n" % (input_freq_hz/1e6)
    desc += "Gate Time:    %ds\n" % (duration_s)
    desc += "Measurements: %d" % (nr_measurements)

    min_y = np.amax(results_delta, where=~np.isnan(results_delta), initial=0)

    props = dict(facecolor='wheat', alpha=1.0)
    ax.text(len(results)*70/100, min_y, desc, fontfamily='monospace', bbox=props, verticalalignment='top')

    ax.set_yscale('log')
    ax.grid(True, which='major')
    #ax.spines['left'].set_position('zero')
    #ax.spines['bottom'].set_position('zero')
    ax.xaxis.tick_bottom()
    #ax.set_ylim(-2.1, 3.1)
    ax.set_xlim(-1, len(results_delta))
    ax.legend(["reciprocal", "linear regression"], loc="lower left")
    fig.tight_layout()
    fig.savefig(filename + ".png")

    print(results_delta[:][-1])

if True:

    # Baseline
    case_nr = 1
    ref_freq_hz     = 10e6
    input_freq_hz   = 3.97163e6
    duration_s      = 1
    nr_measurements = 100

    create_graph(f"case{case_nr}", "Measurement Error", ref_freq_hz, input_freq_hz, duration_s, nr_measurements)

    # Baseline 100MHz
    case_nr += 1
    ref_freq_hz     = 100e6
    input_freq_hz   = 3.97163e6
    duration_s      = 1
    nr_measurements = 100

    create_graph(f"case{case_nr}", "Measurement Error", ref_freq_hz, input_freq_hz, duration_s, nr_measurements)

    # Baseline 60000 points
    case_nr += 1
    ref_freq_hz     = 10e6
    input_freq_hz   = 3.97163e6
    duration_s      = 1
    nr_measurements = 60000

    create_graph(f"case{case_nr}", "Measurement Error", ref_freq_hz, input_freq_hz, duration_s, nr_measurements)

    # Corner case
    case_nr += 1
    ref_freq_hz     = 10e6
    input_freq_hz   = 2.00001e6
    duration_s      = 1
    nr_measurements = 60000

    create_graph(f"case{case_nr}", "Measurement Error", ref_freq_hz, input_freq_hz, duration_s, nr_measurements)

    # Spread spectrum 
    case_nr += 1
    ref_freq_hz     = 10e6
    input_freq_hz   = 2.00001e6
    duration_s      = 1
    nr_measurements = 60000

    create_graph(f"case{case_nr}", "Measurement Error", ref_freq_hz, input_freq_hz, duration_s, nr_measurements, spread_spectrum_freq=0.001)
