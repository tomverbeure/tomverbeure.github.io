#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

SIGNAL1_FREQ_MHZ    = 21
SIGNAL2_FREQ_MHZ    = 19
LO_FREQ_MHZ         = 20

SAMPLE_CLOCK_MHZ    = 100
NR_SAMPLES          = 1024

LABEL_OFFSET_MHZ    = 1

sample_clock_hz     = SAMPLE_CLOCK_MHZ * 1e6
signal1_freq_hz     = SIGNAL1_FREQ_MHZ * 1e6
signal2_freq_hz     = SIGNAL2_FREQ_MHZ * 1e6

signal1_amplitude   = 1.0
signal2_amplitude   = 10 ** (-10.0 / 20.0)

t = np.arange(NR_SAMPLES) / sample_clock_hz

# The real signal has 2 peak
signal  = (
      signal1_amplitude * np.sin(2 * np.pi * signal1_freq_hz * t)
    + signal2_amplitude * np.cos(2 * np.pi * signal2_freq_hz * t)
        )

# Add some noise to show a real noise floor in the spectrum...
noise_rms       = 10 ** (-50.0 / 20.0)
noise           = np.random.normal(0.0, noise_rms, NR_SAMPLES)
signal_noisy    = signal + noise

samples_per_cycle = sample_clock_hz / signal1_freq_hz
nr_plot_samples = int(round(20 * samples_per_cycle))

fig, (ax_time, ax_freq) = plt.subplots(2, 1, figsize=(8, 6))

ax_time.plot(t[:nr_plot_samples] * 1e6, signal_noisy[:nr_plot_samples])
ax_time.set_xlabel("Time (us)")
ax_time.set_ylabel("Amplitude")
ax_time.set_title(f"Input Signal: {SIGNAL1_FREQ_MHZ} MHz + {SIGNAL2_FREQ_MHZ} MHz")
ax_time.grid(True)
ax_time.set_xlim(t[0] * 1e6, t[nr_plot_samples - 1] * 1e6)

window = np.kaiser(NR_SAMPLES, 14.0)
fft_vals = np.fft.fft(signal_noisy * window)
fft_vals = np.fft.fftshift(fft_vals)
freqs_hz = np.fft.fftshift(np.fft.fftfreq(NR_SAMPLES, d=1.0 / sample_clock_hz))

mag = np.abs(fft_vals)
mag_db = 20 * np.log10(np.maximum(mag, 1e-12))
ax_freq.plot(freqs_hz / 1e6, mag_db)

expected_peaks = [
    (signal1_freq_hz, False),
    (-signal1_freq_hz, False),
    (signal2_freq_hz, True),
    (-signal2_freq_hz, True),
]

for expected_hz, flip_label in expected_peaks:
    bin_idx = int(np.argmin(np.abs(freqs_hz - expected_hz)))
    freq_mhz = freqs_hz[bin_idx] / 1e6
    ax_freq.axvline(freq_mhz, color="tab:red", linestyle="--", linewidth=1.0)
    y = mag_db[bin_idx] - 6.0
    direction = np.sign(freq_mhz) * (-1.0 if flip_label else 1.0)
    label_x = freq_mhz + direction * LABEL_OFFSET_MHZ
    ha = "left" if direction > 0 else "right"
    ax_freq.text(
        label_x,
        y,
        f"{freq_mhz:.0f} MHz",
        rotation=0,
        va="top",
        ha=ha,
        fontsize=8,
        color="tab:red",
    )
ax_freq.set_xlabel("Frequency (MHz)")
ax_freq.set_ylabel("Magnitude (dB)")
ax_freq.set_title(
    f"Input Signal: {SIGNAL1_FREQ_MHZ} MHz + {SIGNAL2_FREQ_MHZ} MHz"
)
ax_freq.grid(True)
ax_freq.set_xlim(freqs_hz[0] / 1e6, freqs_hz[-1] / 1e6)

fig.tight_layout()
fig.savefig("complex_heterodyne-input_signal.svg", format="svg")
fig.savefig("complex_heterodyne-input_signal.png", format="png", dpi=200)
plt.show()
