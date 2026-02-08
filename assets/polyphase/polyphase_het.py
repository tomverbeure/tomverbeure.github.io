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

# Low-pass FIR filter: sinc window method (via firwin)
fir_cutoff          = LPF_PASSBAND_MHZ / (SAMPLE_CLOCK_MHZ / 2.0)
h_lpf               = firwin(LPF_FIR_TAPS, fir_cutoff, window=("kaiser", LPF_KAISER_BETA), pass_zero=True)

# Real BPF
tap_idx             = np.arange(LPF_FIR_TAPS)
h_bpf_real          = h_lpf * (2.0 * np.cos(2 * np.pi * lo_freq_hz * tap_idx / sample_clock_hz))

signal_bpf_real     = np.convolve(signal, h_bpf_real, mode="same")
signal_bpf_decim_real = signal_bpf_real[::DECIM_FACTOR]

# Complex BPF
complex_lo          = np.exp(1j * 2 * np.pi * lo_freq_hz * tap_idx / sample_clock_hz)
h_bpf_complex       = h_lpf * complex_lo

signal_bpf_complex  = np.convolve(signal, h_bpf_complex, mode="same")
signal_bpf_decim_complex = signal_bpf_complex[::DECIM_FACTOR]

#============================================================
# Plot: input spectrum + BPF
#============================================================

window = np.kaiser(NR_SAMPLES, 14.0)
coherent_gain_real = np.sum(window) / 2.0
fft_vals = np.fft.fftshift(np.fft.fft(signal * window))
freqs_hz = np.fft.fftshift(np.fft.fftfreq(NR_SAMPLES, d=1.0 / sample_clock_hz))

mag = np.abs(fft_vals) / coherent_gain_real
mag_db = 20 * np.log10(np.maximum(mag, 1e-12))
mag_db -= np.max(mag_db)

bpf_fft_vals = np.fft.fftshift(np.fft.fft(h_bpf_real, n=NR_SAMPLES))
bpf_mag = np.abs(bpf_fft_vals)
bpf_mag_db = 20 * np.log10(np.maximum(bpf_mag, 1e-12))
bpf_mag_db -= np.max(bpf_mag_db)

fig_bpf, ax_bpf = plt.subplots(1, 1, figsize=(8, 4))
ax_bpf.plot(freqs_hz / 1e6, mag_db)
ax_bpf.plot(freqs_hz / 1e6, bpf_mag_db, color="tab:green")
ax_bpf.set_xlabel("Frequency (MHz)")
ax_bpf.set_ylabel("Magnitude (dB)")
ax_bpf.set_title("Spectrum of input signal and bandpass filter")
ax_bpf.grid(True)
ax_bpf.set_xlim(freqs_hz[0] / 1e6, freqs_hz[-1] / 1e6)
ax_bpf.set_ylim(-80, None)

fig_bpf.tight_layout()
fig_bpf.savefig("polyphase_het-bpf.svg", format="svg")
fig_bpf.savefig("polyphase_het-bpf.png", format="png", dpi=200)
plt.show()

#============================================================
# Plot: bandpass filtered signal spectrum
#============================================================

fig_bpf_time, ax_bpf_time = plt.subplots(1, 1, figsize=(8, 4))
window_bpf = np.kaiser(NR_SAMPLES, 14.0)
coherent_gain_bpf = np.sum(window_bpf) / 2.0
fft_bpf_vals = np.fft.fftshift(np.fft.fft(signal_bpf_real * window_bpf))
freqs_bpf_hz = np.fft.fftshift(np.fft.fftfreq(NR_SAMPLES, d=1.0 / sample_clock_hz))
mag_bpf = np.abs(fft_bpf_vals) / coherent_gain_bpf
mag_bpf_db = 20 * np.log10(np.maximum(mag_bpf, 1e-12))
mag_bpf_db -= np.max(mag_bpf_db)

ax_bpf_time.plot(freqs_bpf_hz / 1e6, mag_bpf_db)
ax_bpf_time.set_xlabel("Frequency (MHz)")
ax_bpf_time.set_ylabel("Magnitude (dB)")
ax_bpf_time.set_title("Bandpass filtered signal")
ax_bpf_time.grid(True)
ax_bpf_time.set_xlim(freqs_bpf_hz[0] / 1e6, freqs_bpf_hz[-1] / 1e6)
ax_bpf_time.set_ylim(-80, None)

fig_bpf_time.tight_layout()
fig_bpf_time.savefig("polyphase_het-signal_bfp_filtered.svg", format="svg")
fig_bpf_time.savefig("polyphase_het-signal_bfp_filtered.png", format="png", dpi=200)
plt.show()

#============================================================
# Plot: decimated bandpass filtered signal spectrum
#============================================================

sample_clock_decim_hz = sample_clock_hz / DECIM_FACTOR
window_bpf_decim = np.kaiser(len(signal_bpf_decim_real), 14.0)
coherent_gain_bpf_decim = np.sum(window_bpf_decim) / 2.0
fft_bpf_decim_vals = np.fft.fftshift(np.fft.fft(signal_bpf_decim_real * window_bpf_decim))
freqs_bpf_decim_hz = np.fft.fftshift(
    np.fft.fftfreq(len(signal_bpf_decim_real), d=1.0 / sample_clock_decim_hz)
)
mag_bpf_decim = np.abs(fft_bpf_decim_vals) / coherent_gain_bpf_decim
mag_bpf_decim_db = 20 * np.log10(np.maximum(mag_bpf_decim, 1e-12))
mag_bpf_decim_db -= np.max(mag_bpf_decim_db)

fig_bpf_decim, ax_bpf_decim = plt.subplots(1, 1, figsize=(8, 4))
ax_bpf_decim.plot(freqs_bpf_decim_hz / 1e6, mag_bpf_decim_db)
ax_bpf_decim.set_xlabel("Frequency (MHz)")
ax_bpf_decim.set_ylabel("Magnitude (dB)")
ax_bpf_decim.set_title("Decimated real bandpass filtered signal")
ax_bpf_decim.grid(True)
ax_bpf_decim.set_xlim(freqs_bpf_decim_hz[0] / 1e6, freqs_bpf_decim_hz[-1] / 1e6)
ax_bpf_decim.set_ylim(-80, None)

fig_bpf_decim.tight_layout()
fig_bpf_decim.savefig("polyphase_het-signal_bfp_filtered_decim_real.svg", format="svg")
fig_bpf_decim.savefig("polyphase_het-signal_bfp_filtered_decim_real.png", format="png", dpi=200)
plt.show()

#============================================================
# Plot: input spectrum + complex BPF
#============================================================

bpf_c_fft_vals = np.fft.fftshift(np.fft.fft(h_bpf_complex, n=NR_SAMPLES))
bpf_c_mag = np.abs(bpf_c_fft_vals)
bpf_c_mag_db = 20 * np.log10(np.maximum(bpf_c_mag, 1e-12))
bpf_c_mag_db -= np.max(bpf_c_mag_db)

fig_bpf_c, ax_bpf_c = plt.subplots(1, 1, figsize=(8, 4))
ax_bpf_c.plot(freqs_hz / 1e6, mag_db)
ax_bpf_c.plot(freqs_hz / 1e6, bpf_c_mag_db, color="tab:green")
ax_bpf_c.set_xlabel("Frequency (MHz)")
ax_bpf_c.set_ylabel("Magnitude (dB)")
ax_bpf_c.set_title("Spectrum of input signal and complex bandpass filter")
ax_bpf_c.grid(True)
ax_bpf_c.set_xlim(freqs_hz[0] / 1e6, freqs_hz[-1] / 1e6)
ax_bpf_c.set_ylim(-80, None)

fig_bpf_c.tight_layout()
fig_bpf_c.savefig("polyphase_het-bpf_complex.svg", format="svg")
fig_bpf_c.savefig("polyphase_het-bpf_complex.png", format="png", dpi=200)
plt.show()

#============================================================
# Plot: complex bandpass filtered signal spectrum
#============================================================

window_bpf_c = np.kaiser(NR_SAMPLES, 14.0)
coherent_gain_bpf_c = np.sum(window_bpf_c)
fft_bpf_c_vals = np.fft.fftshift(np.fft.fft(signal_bpf_complex * window_bpf_c))
freqs_bpf_c_hz = np.fft.fftshift(np.fft.fftfreq(NR_SAMPLES, d=1.0 / sample_clock_hz))
mag_bpf_c = np.abs(fft_bpf_c_vals) / coherent_gain_bpf_c
mag_bpf_c_db = 20 * np.log10(np.maximum(mag_bpf_c, 1e-12))
mag_bpf_c_db -= np.max(mag_bpf_c_db)

fig_bpf_c_time, ax_bpf_c_time = plt.subplots(1, 1, figsize=(8, 4))
ax_bpf_c_time.plot(freqs_bpf_c_hz / 1e6, mag_bpf_c_db)
ax_bpf_c_time.set_xlabel("Frequency (MHz)")
ax_bpf_c_time.set_ylabel("Magnitude (dB)")
ax_bpf_c_time.set_title("Complex bandpass filtered signal")
ax_bpf_c_time.grid(True)
ax_bpf_c_time.set_xlim(freqs_bpf_c_hz[0] / 1e6, freqs_bpf_c_hz[-1] / 1e6)
ax_bpf_c_time.set_ylim(-80, None)

fig_bpf_c_time.tight_layout()
fig_bpf_c_time.savefig("polyphase_het-signal_bfp_filtered_complex.svg", format="svg")
fig_bpf_c_time.savefig("polyphase_het-signal_bfp_filtered_complex.png", format="png", dpi=200)
plt.show()

#============================================================
# Plot: decimated complex bandpass filtered signal spectrum
#============================================================

window_bpf_decim_c = np.kaiser(len(signal_bpf_decim_complex), 14.0)
coherent_gain_bpf_decim_c = np.sum(window_bpf_decim_c)
fft_bpf_decim_c_vals = np.fft.fftshift(np.fft.fft(signal_bpf_decim_complex * window_bpf_decim_c))
freqs_bpf_decim_c_hz = np.fft.fftshift(
    np.fft.fftfreq(len(signal_bpf_decim_complex), d=1.0 / sample_clock_decim_hz)
)
mag_bpf_decim_c = np.abs(fft_bpf_decim_c_vals) / coherent_gain_bpf_decim_c
mag_bpf_decim_c_db = 20 * np.log10(np.maximum(mag_bpf_decim_c, 1e-12))
mag_bpf_decim_c_db -= np.max(mag_bpf_decim_c_db)

fig_bpf_decim_c, ax_bpf_decim_c = plt.subplots(1, 1, figsize=(8, 4))
ax_bpf_decim_c.plot(freqs_bpf_decim_c_hz / 1e6, mag_bpf_decim_c_db)
ax_bpf_decim_c.set_xlabel("Frequency (MHz)")
ax_bpf_decim_c.set_ylabel("Magnitude (dB)")
ax_bpf_decim_c.set_title("Decimated complex bandpass filtered signal")
ax_bpf_decim_c.grid(True)
ax_bpf_decim_c.set_xlim(freqs_bpf_decim_c_hz[0] / 1e6, freqs_bpf_decim_c_hz[-1] / 1e6)
ax_bpf_decim_c.set_ylim(-80, None)

fig_bpf_decim_c.tight_layout()
fig_bpf_decim_c.savefig("polyphase_het-signal_bfp_filtered_decim_complex.svg", format="svg")
fig_bpf_decim_c.savefig("polyphase_het-signal_bfp_filtered_decim_complex.png", format="png", dpi=200)
plt.show()
