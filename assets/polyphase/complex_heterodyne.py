#! /usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import firwin

from signal_gen import SigInfo, generate_signal

SIGNAL1_FREQ_MHZ    = 22
SIGNAL2_FREQ_MHZ    = 17

SIGNAL1_AMPL_DB     = 0
SIGNAL2_AMPL_DB     = -10
FLOOR_NOISE_AMPL_DB = -50
OOB_NOISE_AMPL_DB   = -20

SAMPLE_CLOCK_MHZ    = 100
NR_SAMPLES          = 2048

LO_FREQ_MHZ         = 20

LABEL_OFFSET_MHZ    = 1

LPF_FIR_TAPS        = 201
LPF_PASSBAND_MHZ    = 5
LPF_KAISER_BETA     = 12.0

DECIM_FACTOR        = 10

# Stopband filter to create out-of-band noise
OOB_NOISE_FIR_TAPS              = 301
OOB_NOISE_STOPBAND_CENTER_MHZ   = 20
OOB_NOISE_STOPBAND_WIDTH_MHZ    = 14
OOB_NOISE_KAISER_BETA           = 14.0

sample_clock_hz     = SAMPLE_CLOCK_MHZ * 1e6
signal1_freq_hz     = SIGNAL1_FREQ_MHZ * 1e6
signal2_freq_hz     = SIGNAL2_FREQ_MHZ * 1e6
lo_freq_hz          = LO_FREQ_MHZ      * 1e6

#============================================================
# Generate test signal
#============================================================
signal_info = SigInfo(
    nr_samples         = NR_SAMPLES,
    sample_rate        = sample_clock_hz,
    frequencies_hz     = [signal1_freq_hz, signal2_freq_hz],
    amplitudes_db      = [SIGNAL1_AMPL_DB, SIGNAL2_AMPL_DB],
    stopband_center_hz = OOB_NOISE_STOPBAND_CENTER_MHZ * 1e6,
    stopband_width_hz  = OOB_NOISE_STOPBAND_WIDTH_MHZ * 1e6,
    noise_floor_db     = FLOOR_NOISE_AMPL_DB,
    oob_noise_db       = OOB_NOISE_AMPL_DB,
    oob_filter_taps    = OOB_NOISE_FIR_TAPS,
    oob_kaiser_beta    = OOB_NOISE_KAISER_BETA,
)

t, signal = generate_signal(signal_info)

#============================================================
# Perform all DSP operations
#============================================================

lo_signal           = np.sin(2 * np.pi * lo_freq_hz * t)
signal_real_het     = signal * lo_signal

# Complex LO signal
# Negative frequency to shift the signal spectrum to the left.
complex_lo_signal   = np.exp(-1j * 2 * np.pi * lo_freq_hz * t)

# Mix the signal with the complex LO signal -> complex heterodyne
signal_complex_het  = signal * complex_lo_signal

# Low-pass FIR filter: sinc window method (via firwin)
fir_cutoff          = LPF_PASSBAND_MHZ / (SAMPLE_CLOCK_MHZ / 2.0)
h_lpf               = firwin(LPF_FIR_TAPS, fir_cutoff, window=("kaiser", LPF_KAISER_BETA), pass_zero=True)

# Apply the low-pass filter
signal_het_lpf      = np.convolve(signal_complex_het, h_lpf, mode="same")

# Decimate the signal
signal_decim        = signal_het_lpf[::DECIM_FACTOR]

#============================================================
# Plot: input signal in time and frequency domain
#============================================================

samples_per_cycle   = sample_clock_hz / signal1_freq_hz

nr_plot_samples     = int(round(40 * samples_per_cycle))
nr_plot_samples_iq  = int(round(80 * samples_per_cycle))

fig, (ax_time, ax_freq) = plt.subplots(2, 1, figsize=(8, 7))

# Time plot
ax_time.plot(t[:nr_plot_samples] * 1e6, signal[:nr_plot_samples])
ax_time.set_xlabel("Time (us)")
ax_time.set_ylabel("Amplitude")
ax_time.set_title(f"Time Plot of Input Signal: {SIGNAL1_FREQ_MHZ} MHz + {SIGNAL2_FREQ_MHZ} MHz")
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
mag_db -= np.max(mag_db)
ax_freq.plot(freqs_hz / 1e6, mag_db)

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
ax_freq.set_title( f"Spectrum of Input Signal: {SIGNAL1_FREQ_MHZ} MHz + {SIGNAL2_FREQ_MHZ} MHz")
ax_freq.grid(True)
ax_freq.set_xlim(freqs_hz[0] / 1e6, freqs_hz[-1] / 1e6)
ax_freq.set_ylim(-80, None)

fig.tight_layout()
fig.savefig("complex_heterodyne-input_signal.svg", format="svg")
fig.savefig("complex_heterodyne-input_signal.png", format="png", dpi=200)
plt.show()

#============================================================
# Plot: different channels
#============================================================
fig_lo_no, ax_lo_no = plt.subplots(1, 1, figsize=(8, 4))
ax_lo_no.plot(freqs_hz / 1e6, mag_db)
ax_lo_no.set_xlabel("Frequency (MHz)")
ax_lo_no.set_ylabel("Magnitude (dB)")
ax_lo_no.set_title(f"Multiple Channels")
ax_lo_no.grid(True)
ax_lo_no.set_xlim(freqs_hz[0] / 1e6, freqs_hz[-1] / 1e6)
ax_lo_no.set_ylim(-80, None)

for freq_mhz in (-5, 5, 15, 25, 35, 45):
    ax_lo_no.axvline(freq_mhz, color="tab:red", linestyle=":", linewidth=2.0)

fig_lo_no.tight_layout()
fig_lo_no.savefig("complex_heterodyne-channels.svg", format="svg")
fig_lo_no.savefig("complex_heterodyne-channels.png", format="png", dpi=200)
plt.show()

#============================================================
# Plot: Real heterodyne spectrum
#============================================================

het_fft_vals = np.fft.fftshift(np.fft.fft(signal_real_het * window))
het_mag = np.abs(het_fft_vals) / coherent_gain_real
het_mag_db = 20 * np.log10(np.maximum(het_mag, 1e-12))
het_mag_db -= np.max(het_mag_db)

lo_fft_vals = np.fft.fftshift(np.fft.fft(lo_signal * window))
lo_mag = np.abs(lo_fft_vals) / coherent_gain_real
lo_mag_db = 20 * np.log10(np.maximum(lo_mag, 1e-12))
lo_mag_db -= np.max(lo_mag_db)

fig_het, (ax_input, ax_het) = plt.subplots(2, 1, figsize=(8, 7))
ax_input.plot(freqs_hz / 1e6, mag_db)
ax_input.plot(freqs_hz / 1e6, lo_mag_db, color="orange")
ax_input.set_xlabel("Frequency (MHz)")
ax_input.set_ylabel("Magnitude (dB)")
ax_input.set_title(f"Spectrum with Real Local Oscillator: {LO_FREQ_MHZ} MHz")
ax_input.grid(True)
ax_input.set_xlim(freqs_hz[0] / 1e6, freqs_hz[-1] / 1e6)
ax_input.set_ylim(-80, None)

for freq_mhz in (-5, 5, 15, 25, 35, 45):
    ax_input.axvline(freq_mhz, color="tab:red", linestyle=":", linewidth=2.0)

lo_expected_peaks = [
        ( lo_freq_hz, False),
        (-lo_freq_hz, False),
    ]

for expected_hz, flip_label in lo_expected_peaks:
    bin_idx     = int(np.argmin(np.abs(freqs_hz - expected_hz)))
    freq_mhz    = freqs_hz[bin_idx] / 1e6
    ax_input.axvline(freq_mhz, color="orange", linestyle="--", linewidth=1.0)

    y           = lo_mag_db[bin_idx] - 6.0
    direction   = np.sign(freq_mhz) * (-1.0 if flip_label else 1.0)
    label_x     = freq_mhz + direction * LABEL_OFFSET_MHZ
    ha = "left" if direction > 0 else "right"
    ax_input.text(label_x, y, f"{freq_mhz:.0f} MHz",
                  rotation=0, va="top", ha=ha, fontsize=8, color="orange",)

ax_het.plot(freqs_hz / 1e6, het_mag_db)
ax_het.set_xlabel("Frequency (MHz)")
ax_het.set_ylabel("Magnitude (dB)")
ax_het.set_title("Spectrum after Real Heterodyne")
ax_het.grid(True)
ax_het.set_xlim(freqs_hz[0] / 1e6, freqs_hz[-1] / 1e6)
ax_het.set_ylim(-80, None)

fig_het.tight_layout()
fig_het.savefig("complex_heterodyne-real_het.svg", format="svg")
fig_het.savefig("complex_heterodyne-real_het.png", format="png", dpi=200)
plt.show()

#============================================================
# Plot: Complex heterodyne spectrum
#============================================================

sample_clock_decim_hz = sample_clock_hz / DECIM_FACTOR

complex_lo_fft_vals = np.fft.fftshift(np.fft.fft(complex_lo_signal * window))
complex_lo_mag      = np.abs(complex_lo_fft_vals) / coherent_gain_complex
complex_lo_mag_db   = 20 * np.log10(np.maximum(complex_lo_mag, 1e-12))
complex_lo_mag_db   -= np.max(complex_lo_mag_db)

complex_het_fft_vals = np.fft.fftshift(np.fft.fft(signal_complex_het * window))
complex_het_mag = np.abs(complex_het_fft_vals) / coherent_gain_complex
complex_het_mag_db = 20 * np.log10(np.maximum(complex_het_mag, 1e-12))
complex_het_mag_db -= np.max(complex_het_mag_db)

het_lpf_fft_vals = np.fft.fftshift(np.fft.fft(signal_het_lpf * window))
het_lpf_mag = np.abs(het_lpf_fft_vals) / coherent_gain_complex
het_lpf_mag_db = 20 * np.log10(np.maximum(het_lpf_mag, 1e-12))
het_lpf_mag_db -= np.max(het_lpf_mag_db)

fir_fft_vals = np.fft.fftshift(np.fft.fft(h_lpf, n=NR_SAMPLES))
fir_mag = np.abs(fir_fft_vals)
fir_mag_db = 20 * np.log10(np.maximum(fir_mag, 1e-12))
fir_mag_db -= np.max(fir_mag_db)

fig_lo, (ax_lo, ax_complex_het) = plt.subplots(2, 1, figsize=(8, 7))
ax_lo.plot(freqs_hz / 1e6, mag_db, label="Input signal")
ax_lo.plot(freqs_hz / 1e6, complex_lo_mag_db, color="orange", label="Complex LO")
ax_lo.set_xlabel("Frequency (MHz)")
ax_lo.set_ylabel("Magnitude (dB)")
ax_lo.set_title("Spectrum of Input Signal and Complex LO")
ax_lo.grid(True)
ax_lo.set_xlim(freqs_hz[0] / 1e6, freqs_hz[-1] / 1e6)
ax_lo.set_ylim(-80, None)
ax_lo.legend(loc="upper right")

ax_complex_het.plot(freqs_hz / 1e6, complex_het_mag_db)
ax_complex_het.set_xlabel("Frequency (MHz)")
ax_complex_het.set_ylabel("Magnitude (dB)")
ax_complex_het.set_title("Complex Heterodyne Spectrum")
ax_complex_het.grid(True)
ax_complex_het.set_xlim(freqs_hz[0] / 1e6, freqs_hz[-1] / 1e6)
ax_complex_het.set_ylim(-80, None)

fig_lo.tight_layout()
fig_lo.savefig("complex_heterodyne-complex_lo.svg", format="svg")
fig_lo.savefig("complex_heterodyne-complex_lo.png", format="png", dpi=200)
plt.show()

#============================================================
# Plot: Complex heterodyne spectrum with low pass filter
#============================================================
fig_lo_lpf, (ax_complex_het_lpf, ax_het_lpf_lpf) = plt.subplots(2, 1, figsize=(8, 7))
ax_complex_het_lpf.plot(freqs_hz / 1e6, complex_het_mag_db)
ax_complex_het_lpf.plot(freqs_hz / 1e6, fir_mag_db, color="tab:green")
ax_complex_het_lpf.set_xlabel("Frequency (MHz)")
ax_complex_het_lpf.set_ylabel("Magnitude (dB)")
ax_complex_het_lpf.set_title("Spectrum of Complex Heterodyne and Low Pass Filter")
ax_complex_het_lpf.grid(True)
ax_complex_het_lpf.set_xlim(freqs_hz[0] / 1e6, freqs_hz[-1] / 1e6)
ax_complex_het_lpf.set_ylim(-80, None)

ax_het_lpf_lpf.plot(freqs_hz / 1e6, het_lpf_mag_db)
ax_het_lpf_lpf.set_xlabel("Frequency (MHz)")
ax_het_lpf_lpf.set_ylabel("Magnitude (dB)")
ax_het_lpf_lpf.set_title("Spectrum of Filtered Complex Heterodyne")
ax_het_lpf_lpf.grid(True)
ax_het_lpf_lpf.set_xlim(freqs_hz[0] / 1e6, freqs_hz[-1] / 1e6)
ax_het_lpf_lpf.set_ylim(-80, None)

fig_lo_lpf.tight_layout()
fig_lo_lpf.savefig("complex_heterodyne-low_pass_filter.svg", format="svg")
fig_lo_lpf.savefig("complex_heterodyne-low_pass_filter.png", format="png", dpi=200)
plt.show()

#============================================================
# Plot: I/Q output in time domain
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
# Plot: decimated signal
#============================================================

window_decim = np.kaiser(len(signal_decim), 14.0)
coherent_gain_decim = np.sum(window_decim) / 2.0
decim_fft_vals = np.fft.fftshift(np.fft.fft(signal_decim * window_decim))
decim_freqs_hz = np.fft.fftshift(
    np.fft.fftfreq(len(signal_decim), d=1.0 / sample_clock_decim_hz)
)
decim_mag = np.abs(decim_fft_vals) / coherent_gain_decim
decim_mag_db = 20 * np.log10(np.maximum(decim_mag, 1e-12))
decim_mag_db -= np.max(decim_mag_db)

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
