---
layout: post
title: Tektronix AWG 2021 Spectrum Measurements
date:  2022-05-07 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Measurements

* AWG 2021 Setup:
	* FG mode
	* Freq: 2.5 MHz
	* 0.25V pk-to-pk amplitude
	* Offset 0V (!)

* R3273 Spectrum analyzer

* RBW: 100Hz
* VBW: 30Hz
* Span: 100kHz
* with DC blocker: -8.79dBm total power, -10.83dBm
* without DC blocker: -8.71dBm, peak: -10.13dBm

-> Measures: 2.501 MHz

* Freq 1MHz -> 25MHz

    No harmonics seen

* Freq 1MHz -> 6MHz

    Harmonic at 5MHz: -88.98dBm


* Change 2021 from 2.5MHz to 7kHz -> sine wave still works. Below 7kHz: no more sine wave.

* 2021: sine wave at 10kHz. Amplitude the same.

	* with DC blocker: -43.75 dBm
	* without DC blocker: -8.9 dBm

Pretty much no harmonics: -93.3 dBm at 20kHz

* 2.5 Mhz, triangle

	* with DC blocker
	* main freq: -10.95 dBm
	* See freq list on phone

* 2.5 Mhz, square wave

	* with DC blocker
	* main freq: -6.91 dBm
	* See freq list on phone

* 2.5 Mhz, sawtooth

	* with DC blocker
	* main freq: -12.77 dBm
	* See freq list on phone

* Custom waveform: 
	* 1000 points
	* 250MHz
	* sine wave
	* 100 cycles

25MHz

* Custom waveform: 
	* 1000 points
	* 250MHz
	* sine wave
	* 200 cycles

50MHz

* Custom waveform: 
	* 1000 points
	* 125MHz
	* sine wave
	* 200 cycles

- 25MHz
- Harmonics get much worse: lack of output filter results in square waveform.

Conclusion: it's better to keep the sample clock constant and reduce the number of cycles/increase the number of
samples per cycle for things like a sine wave.


* Custom waveform: 
	* 1000 points
	* 250MHz
	* Noise

- No filtering. 
- 1 MHz
- 5 MHz


33120A

* 2.5MHz, sine, 0.250Vpp
* 2.5MHz, square, 0.250Vpp
* 100kHz, triangle, 0.250Vpp
* 100kHz, sawtooth, 0.250Vpp
* 100kHz, sine, 0.250Vpp
* 100kHz, sine, 0.250Vpp
* 15MHz, sine, 0.250Vpp


FY6900

* 10kHz, sine, 0.5Vpp (1M termination) 

- On scope: 536mV, not 500mV. With 50 Ohm -> 208mV

* 100kHz, sine, 0.5Vpp (1M termination) 
* 2.5MHz, sine, 0.5Vpp (1M termination) 
* 60MHz, sine, 0.5Vpp (1M termination) 
* 15MHz, sine, 0.5Vpp (1M termination) 
* 15MHz, square, 0.5Vpp (1M termination) 
* 15MHz, triangle, 0.5Vpp (1M termination) 
* 15MHz, noise, 0.5Vpp (1M termination) 



