#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import firwin

SIGNAL1_FREQ_MHZ    = 22
SIGNAL2_FREQ_MHZ    = 16
LO_FREQ_MHZ         = 18

SAMPLE_CLOCK_MHZ    = 100
NR_SAMPLES          = 2048

LABEL_OFFSET_MHZ    = 1

FIR_TAPS                = 201
FIR_PASSBAND_MHZ        = 5
FIR_KAISER_BETA         = 12.0

DECIM_FACTOR        = 10

sample_clock_hz     = SAMPLE_CLOCK_MHZ * 1e6
signal1_freq_hz     = SIGNAL1_FREQ_MHZ * 1e6
signal2_freq_hz     = SIGNAL2_FREQ_MHZ * 1e6
lo_freq_hz          = LO_FREQ_MHZ      * 1e6

signal1_amplitude   = 10 ** (  0.0 / 20.0)
signal2_amplitude   = 10 ** (-10.0 / 20.0)

t                   = np.arange(NR_SAMPLES) / sample_clock_hz
lo_signal           = np.sin(2 * np.pi * lo_freq_hz * t)

# The signal has 2 sine waves
signal_pure  = (
      signal1_amplitude * np.sin(2 * np.pi * signal1_freq_hz * t)
    + signal2_amplitude * np.cos(2 * np.pi * signal2_freq_hz * t)
        )

# Add some noise to show a real noise floor in the spectrum...
noise_rms           = 10 ** (-50.0 / 20.0)
noise               = np.random.normal(0.0, noise_rms, NR_SAMPLES)
signal              = signal_pure + noise
samples_per_cycle   = sample_clock_hz / signal1_freq_hz

nr_plot_samples     = int(round(40 * samples_per_cycle))
nr_plot_samples_iq  = int(round(80 * samples_per_cycle))

signal_real_het = signal * lo_signal

# Low-pass FIR filter: sinc window method (via firwin)
fir_cutoff          = FIR_PASSBAND_MHZ / (SAMPLE_CLOCK_MHZ / 2.0)
h_lpf               = firwin(FIR_TAPS, fir_cutoff, window=("kaiser", FIR_KAISER_BETA), pass_zero=True)

#============================================================
# First plot
#============================================================

fig, (ax_time, ax_freq, ax_het) = plt.subplots(3, 1, figsize=(8, 9))

# Time plot
ax_time.plot(t[:nr_plot_samples] * 1e6, signal[:nr_plot_samples])
ax_time.set_xlabel("Time (us)")
ax_time.set_ylabel("Amplitude")
ax_time.set_title(f"Input Signal: {SIGNAL1_FREQ_MHZ} MHz + {SIGNAL2_FREQ_MHZ} MHz")
ax_time.grid(True)
ax_time.set_xlim(t[0] * 1e6, t[nr_plot_samples - 1] * 1e6)

# Spectrum plot (input signal)
window = np.kaiser(NR_SAMPLES, 14.0)
coherent_gain_real = np.sum(window) / 2.0
coherent_gain_complex = np.sum(window)
fft_vals = np.fft.fft(signal * window)
fft_vals = np.fft.fftshift(fft_vals)
freqs_hz = np.fft.fftshift(np.fft.fftfreq(NR_SAMPLES, d=1.0 / sample_clock_hz))

mag = np.abs(fft_vals) / coherent_gain_real
mag_db = 20 * np.log10(np.maximum(mag, 1e-12))
ax_freq.plot(freqs_hz / 1e6, mag_db)

lo_fft_vals = np.fft.fftshift(np.fft.fft(lo_signal * window))
lo_mag = np.abs(lo_fft_vals) / coherent_gain_real
lo_mag_db = 20 * np.log10(np.maximum(lo_mag, 1e-12))
ax_freq.plot(freqs_hz / 1e6, lo_mag_db, color="orange")

expected_peaks = [
        ( signal1_freq_hz, False),
        (-signal1_freq_hz, False),
        ( signal2_freq_hz, True),
        (-signal2_freq_hz, True),
    ]

for expected_hz, flip_label in expected_peaks:
    bin_idx     = int(np.argmin(np.abs(freqs_hz - expected_hz)))
    freq_mhz    = freqs_hz[bin_idx] / 1e6
    ax_freq.axvline(freq_mhz, color="tab:red", linestyle="--", linewidth=1.0)

    y           = mag_db[bin_idx] - 6.0
    direction   = np.sign(freq_mhz) * (-1.0 if flip_label else 1.0)
    label_x     = freq_mhz + direction * LABEL_OFFSET_MHZ
    ha = "left" if direction > 0 else "right"
    ax_freq.text(label_x, y, f"{freq_mhz:.0f} MHz", 
                 rotation=0, va="top", ha=ha, fontsize=8, color="tab:red",)

ax_freq.set_xlabel("Frequency (MHz)")
ax_freq.set_ylabel("Magnitude (dB)")
ax_freq.set_title( f"Input Signal: {SIGNAL1_FREQ_MHZ} MHz + {SIGNAL2_FREQ_MHZ} MHz")
ax_freq.grid(True)
ax_freq.set_xlim(freqs_hz[0] / 1e6, freqs_hz[-1] / 1e6)
ax_freq.set_ylim(-80, None)

# Spectrum plot (real heterodyne)
het_fft_vals = np.fft.fftshift(np.fft.fft(signal_real_het * window))
het_mag = np.abs(het_fft_vals) / coherent_gain_real
het_mag_db = 20 * np.log10(np.maximum(het_mag, 1e-12))
ax_het.plot(freqs_hz / 1e6, het_mag_db)
ax_het.set_xlabel("Frequency (MHz)")
ax_het.set_ylabel("Magnitude (dB)")
ax_het.set_title("Real Heterodyne Spectrum")
ax_het.grid(True)
ax_het.set_xlim(freqs_hz[0] / 1e6, freqs_hz[-1] / 1e6)
ax_het.set_ylim(-80, None)

fig.tight_layout()
fig.savefig("complex_heterodyne-input_signal.svg", format="svg")
fig.savefig("complex_heterodyne-input_signal.png", format="png", dpi=200)
plt.show()

#============================================================
# Second plot
#============================================================

# Complex LO signal
# Use negative frequency to shift the signal spectrum to the left.
complex_lo_signal   = np.exp(-1j * 2 * np.pi * lo_freq_hz * t)

# Mix the signal with the complex LO signal -> complex heterodyne
signal_complex_het  = signal * complex_lo_signal

# Apply the low-pass filter
signal_het_lpf      = np.convolve(signal_complex_het, h_lpf, mode="same")

signal_decim        = signal_het_lpf[::DECIM_FACTOR]
sample_clock_decim_hz = sample_clock_hz / DECIM_FACTOR

complex_lo_fft_vals = np.fft.fftshift(np.fft.fft(complex_lo_signal * window))
complex_lo_mag      = np.abs(complex_lo_fft_vals) / coherent_gain_complex
complex_lo_mag_db   = 20 * np.log10(np.maximum(complex_lo_mag, 1e-12))

complex_het_fft_vals = np.fft.fftshift(np.fft.fft(signal_complex_het * window))
complex_het_mag = np.abs(complex_het_fft_vals) / coherent_gain_complex
complex_het_mag_db = 20 * np.log10(np.maximum(complex_het_mag, 1e-12))

het_lpf_fft_vals = np.fft.fftshift(np.fft.fft(signal_het_lpf * window))
het_lpf_mag = np.abs(het_lpf_fft_vals) / coherent_gain_complex
het_lpf_mag_db = 20 * np.log10(np.maximum(het_lpf_mag, 1e-12))

fig_lo, (ax_lo, ax_complex_het, ax_het_lpf) = plt.subplots(3, 1, figsize=(8, 9))
ax_lo.plot(freqs_hz / 1e6, mag_db, label="Input signal")
ax_lo.plot(freqs_hz / 1e6, complex_lo_mag_db, color="orange", label="Complex LO")
ax_lo.set_xlabel("Frequency (MHz)")
ax_lo.set_ylabel("Magnitude (dB)")
ax_lo.set_title("Input Signal vs Complex LO Spectrum")
ax_lo.grid(True)
ax_lo.set_xlim(freqs_hz[0] / 1e6, freqs_hz[-1] / 1e6)
ax_lo.set_ylim(-80, None)
ax_lo.legend(loc="upper right")

ax_complex_het.plot(freqs_hz / 1e6, complex_het_mag_db)
fir_fft_vals = np.fft.fftshift(np.fft.fft(h_lpf, n=NR_SAMPLES))
fir_mag = np.abs(fir_fft_vals)
fir_mag_db = 20 * np.log10(np.maximum(fir_mag, 1e-12))
ax_complex_het.plot(freqs_hz / 1e6, fir_mag_db, color="tab:green")
ax_complex_het.set_xlabel("Frequency (MHz)")
ax_complex_het.set_ylabel("Magnitude (dB)")
ax_complex_het.set_title("Complex Heterodyne Spectrum")
ax_complex_het.grid(True)
ax_complex_het.set_xlim(freqs_hz[0] / 1e6, freqs_hz[-1] / 1e6)
ax_complex_het.set_ylim(-80, None)

ax_het_lpf.plot(freqs_hz / 1e6, het_lpf_mag_db)
ax_het_lpf.set_xlabel("Frequency (MHz)")
ax_het_lpf.set_ylabel("Magnitude (dB)")
ax_het_lpf.set_title("Complex Heterodyne + LPF Spectrum")
ax_het_lpf.grid(True)
ax_het_lpf.set_xlim(freqs_hz[0] / 1e6, freqs_hz[-1] / 1e6)
ax_het_lpf.set_ylim(-80, None)

fig_lo.tight_layout()
fig_lo.savefig("complex_heterodyne-complex_lo.svg", format="svg")
fig_lo.savefig("complex_heterodyne-complex_lo.png", format="png", dpi=200)
plt.show()

#============================================================
# Third plot
#============================================================

fig_iq, ax_iq = plt.subplots(1, 1, figsize=(8, 4))
ax_iq.plot(t[:nr_plot_samples_iq] * 1e6, signal_het_lpf[:nr_plot_samples_iq].real, label="I")
ax_iq.plot(t[:nr_plot_samples_iq] * 1e6, signal_het_lpf[:nr_plot_samples_iq].imag, label="Q")
ax_iq.set_xlabel("Time (us)")
ax_iq.set_ylabel("Amplitude")
ax_iq.set_title("LPF Output I/Q (Time Domain)")
ax_iq.grid(True)
ax_iq.set_xlim(t[0] * 1e6, t[nr_plot_samples_iq - 1] * 1e6)
ax_iq.legend(loc="upper right")

fig_iq.tight_layout()
fig_iq.savefig("complex_heterodyne-iq_lpf.svg", format="svg")
fig_iq.savefig("complex_heterodyne-iq_lpf.png", format="png", dpi=200)
plt.show()

#============================================================
# Fourth plot
#============================================================

window_decim = np.kaiser(len(signal_decim), 14.0)
coherent_gain_decim = np.sum(window_decim) / 2.0
decim_fft_vals = np.fft.fftshift(np.fft.fft(signal_decim * window_decim))
decim_freqs_hz = np.fft.fftshift(
    np.fft.fftfreq(len(signal_decim), d=1.0 / sample_clock_decim_hz)
)
decim_mag = np.abs(decim_fft_vals) / coherent_gain_decim
decim_mag_db = 20 * np.log10(np.maximum(decim_mag, 1e-12))

fig_decim, ax_decim = plt.subplots(1, 1, figsize=(8, 4))
ax_decim.plot(decim_freqs_hz / 1e6, decim_mag_db)
ax_decim.set_xlabel("Frequency (MHz)")
ax_decim.set_ylabel("Magnitude (dB)")
ax_decim.set_title("Decimated Signal Spectrum")
ax_decim.grid(True)
ax_decim.set_xlim(decim_freqs_hz[0] / 1e6, decim_freqs_hz[-1] / 1e6)
ax_decim.set_ylim(-80, None)

fig_decim.tight_layout()
fig_decim.savefig("complex_heterodyne-decim_fft.svg", format="svg")
fig_decim.savefig("complex_heterodyne-decim_fft.png", format="png", dpi=200)
plt.show()


