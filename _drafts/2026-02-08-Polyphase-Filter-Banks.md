---
layout: post
title: A Non-Trivial Polyphase Channelizer for Bluetooth LE
date:   2026-02-23 00:00:00 -1000
categories:
---

<script async src="https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-AMS_CHTML"></script>


* TOC
{:toc}

# Introduction

In previous blog post, I introduced the 
[polyphase channelizer](/2026/02/16/Polyphase-Channelizer.html),
a DSP algorithm that is incredibly efficient at heterodyning multiple channels to baseband
in parallel. I made two major assumptions about the nature of the input signal:

* The bandwidth of a channel is equal to the the input sample rate divided by the decimation factor.
* The center frequency of each channel is an integer multiple of the channel bandwidth

If these conditions are satisfied, the channelizer reduces to a filter bank with real coefficients
and an inverse FFT on the output of the filter phases.

In this blog post, I'll use a real-world Bluetooth LE recording and a polyphase channelizer to
extract all channels in parallel. There's a twist, however, in that the center frequency of the
channels is not a multiple of the channel bandwidth. With a little bit of additional math,
we can work around that too.

# A Bluetooth LE Trace

Bluetooth LE (BLE) lives in the unlicensed 2.4 GHz radio band that's also used by Wifi and many other
protocols. It has 40 channels that are each 2 MHz wide for a total bandwidth of 80 MHz. The
center frequency of physical channel 0 is a 2402 MHz, so in total, BLE occupies the range from
2401 MHz to 2481 MHz.

The 2.4 GHz radio band is very congested. To ensure that at least some packets get through, BLE
uses frequency hopping: it continously jumps from one channel to the next in some predictable
pattern. However, to establish an initial connection, there are a number of fixed management channels.

[Joshua](https://joshuawise.com) used his BladeRF SDR unit to provided me with a 5 ms recording with
the following characteristics:

* center frequency: 2.441 GHz
* sample rate: 96 MHz
* quadrature I/Q sampling

We can create a 
[waterfall plot](https://en.wikipedia.org/wiki/Waterfall_plot) 
of this, where the X-axis shows the time and the Y axis the 
[short time Fourier transform (STFT)](https://en.wikipedia.org/wiki/Short-time_Fourier_transform).

[![BLE Waterfall Plot](/assets/polyphase/ble/ble_input_data_waterfall.png)](/assets/polyphase/ble/ble_input_data_waterfall.png)
*(Click to enlarge)*

We can see a bright line at the 2441 MHz center frequency. This is a common artifact of the 
imperfect SDR hardware. It could be caused by local oscillator leakage or an imbalance between the 
I and Q channels of the quadrature AD converters, or both.

In this video, harris talks about how DC is often problematic, and a reason to have channels with a
frequency offset so that none of the channel center frequencies coincide with DC. I'm pretty sure that is
one of the reasons why.

We can also see some symmetry around the 2441 MHz line. For example, there's a short burst around
1.1 ms at 2415 Mhz and a weaker version at 2467 MHz. This weaker version isn't real either, but a
spectral mirror image that's caused by an imbalance between the I and the Q channels: their phase shift
might not be exactly 90 degrees or they might have a slightly different gain on their way to the 
ADCs.[^gram_schmidt]
This is another topic that harris talks about: if possible, use a single double-speed ADC and do
all the I/Q handling in the mathematically perfect digital domain. 

[^gram_schmidt]: You can use [Gram-Schmidt decorrelation](https://en.wikipedia.org/wiki/Gram%E2%80%93Schmidt_process)
                 to fix the I/Q vectors, supposedly, but I haven't explored that yet.

A recording of 96 Msps complex samples covers 48 channels of 2 MHz. Since BLE only has 40 active channels,
we have a little bit too much data, but that's ok. In the waterfall plot below, I've added separators that
the individual channels. The suprious 2441 MHz line is now obstructed, which is good because it shows that 
it falls on a transition band.

[![BLE Waterfall Plot with Channels](/assets/polyphase/ble/ble_input_data_waterfall_bars.png)](/assets/polyphase/ble/ble_input_data_waterfall_bars.png)
*(Click to enlarge)*

In the previous blog post, we operated under the assumption that channel center frequencies were located
at a multiple of the decimated sample rate:

$$
    F_c = \frac{F_s}{M} c, \quad c = 0, 1, \dots, M-1
$$

That's not the case here. Instead, we have the following situation:

$$
    F_c = \frac{F_s}{M} c + \frac{1}{2M}, \quad c = 0, 1, \dots, M-1
$$

**Add a drawing of channel spectrum with offset**

Concretely, instead of channel center frequencies at -2, 0, 2, 4, ... MHz, they are located at
-3, -1, 1, 3, 5, ... MHz. Having the center frequency offset at exacty half the channel width is
something we can exploit later, and harris spends the good part of his video talking about the
special case where the M is an odd number, but I will start by assuming the generic case where
the frequency offset can be anything, and later apply simplications.

# Input Complex Heterodyne

The simplest way to align the center channel frequencies to an integer multiple of the output
sample rate is to remove the offset with a complex heterodyne on the input signal.

Like this:

$$
x[n] = x'[n] \, e^{j \omega_\Delta n}
$$

This works, of course, but it undoes all the effort from last blog post where we tried very
hard to not do anything at the input sample rate.

Still, let's do it anyway and see what kind of result we get.

I've become smarter about using NumPy functions which makes the code a whole lot shorter, though not
necessarily more readable. The source code to do the input heterodyne and the
polyphase channelizer is below. I've stripped some of the comments for brevity, but
check out the code in the GitHub repo for more details.

```python
n = np.arange(len(ble_input), dtype=np.float32)

# Complex 1 MHz rotator to shift the spectrum by the half-channel offset
heterodyne_1mhz     = np.exp(1j * 2.0 * np.pi * channel_offset_hz / sample_rate_hz * n).astype(np.complex64)
# Do the heterodyne on the input signal
ble_input_pre_1mhz  = ble_input * heterodyne_1mhz

# Channel low-pass filter with a passband from 0 to 600 kHz
# and a stopband that starts at 800 kHz.
h_lpf = create_remez_lowpass_fir(
    input_sample_rate_hz     = sample_rate_hz,
    passband_hz              = 600e3,
    passband_ripple_db       = 1.0,
    stopband_hz              = 800e3,
    stopband_attenuation_db  = 50.0
    )

# Pad the filter with zeros so that the polyphase decomposition 
# is a clean 2D array.
h_lpf   = np.pad(h_lpf, (0, -len(h_lpf) % decim_factor) )

# Polyphase filter decomposition: 
# 48 rows, each row has interleaved coefficients.
h_lpf_poly  = np.reshape(
        h_lpf, ( (len(h_lpf) // decim_factor), decim_factor) 
    ).T

# Polyphase decomposition/decimation of the input signal
ble_decim_pre_1mhz  = np.flipud(
    np.reshape(
        ble_input_pre_1mhz,
        ((len(ble_input_pre_1mhz) // decim_factor), decim_factor),
    ).T
)

# Calculate the output of all polyphase filters
h_poly_out_pre_1mhz = np.array(
        [np.convolve(ble_decim_pre_1mhz[_], h_lpf_poly[_]) for _ in range(decim_factor)])

# Vectorized IFFT to calculate the output of all channels
channel_data_pre_1mhz = np.fft.ifft(h_poly_out_pre_1mhz, axis=0).astype(np.complex64)
```

After extracting the data from channel 33[^33] between 1.14 ms and 1.24 ms, we get the following:

[^33]: Channel zero is located at 2441 MHz. Channel numbers increment up to 24 the top frequency
       is reached, after which the frequency rolls over to the bottom and channel numbers continue
       to increment. That's how you end up with 33.

[![Channel 33 I/Q time plot](/assets/polyphase/ble/chan_33_time_plot_het_pre_iq.svg)](/assets/polyphase/ble/chan_33_time_plot_het_pre_iq.svg)
*(Click to enlarge)*

The active period of a packet can be derived from the amplitude of the I/Q vector (green).
And the I/Q data clearly has some structure in it.

BLE uses 
[Gaussian frequency shift keying (GFSK)](https://en.wikipedia.org/wiki/Frequency-shift_keying#Gaussian_frequency-shift_keying).
Like ordinary [frequency shift keying (FSK)](https://en.wikipedia.org/wiki/Frequency-shift_keying), 
a 0 and a 1 are coded with slightly different frequencies, but the transistion between them is just
a bit smoother for GFSK. 

Frequency is the derivative of the phase. Since I and Q are available, you can calculate the
phase as follows:

$$
\phi[n] = \arctan(\frac{q[n]}{i[n]})
$$

The derivative is simply the delta between consecutive phase samples.

In Python, we can demodulate a GFSK signal like this:

```python
angle = np.unwrap(np.angle(iq_data))
d_angle = angle[:-1] - angle[1:]
```

Here's the result:

[![Channel 33 GFSK time plot](/assets/polyphase/ble/chan_33_time_plot_het_pre_gfsk.svg)](/assets/polyphase/ble/chan_33_time_plot_het_pre_gfsk.svg)
*(Click to enlarge)*

A BLE packet starts with a 16-symbol 1010101010101010 sync word, followed by data. This definitely looks
like a valid packet.

Cool! But it costs us a table with 48 rotator values that are fed into a complex multiplier, at the input sample rate. 
In this example, the input samples are already complex, but if they were real, the input heterodyne also
forces all filter bank calculations to become complex.

Can we do better?

# Derivation of Post-Decimation Offset Correction

Here's the standard polyphase channelizer pipeline from last blog post:

![Standard polyphase channelizer](/assets/polyphase/ble/ble-polyphase_ifft.svg)

And here's the mathematical description of the pipeline, for 3 channels and a filter with 9 coefficients:

$$
\begin{alignedat}{0}
y_c[n]    & = & e^{j \frac{2 \pi}{3} c \, 0} & ( & h[0] & x[3n]   & + &  h[3] & x[3n-3] & + & h[6] & x[3n-6] & ) \\
          & + & e^{j \frac{2 \pi}{3} c \, 1} & ( & h[1] & x[3n-1] & + &  h[4] & x[3n-4] & + & h[7] & x[3n-7] & ) \\
          & + & e^{j \frac{2 \pi}{3} c \, 2} & ( & h[2] & x[3n-2] & + &  h[5] & x[3n-5] & + & h[8] & x[3n-8] & ) \\
\\
y_c[n+1]  & = & e^{j \frac{2 \pi}{3} c \, 0} & ( & h[0] & x[3n+3] & + &  h[3] & x[3n]   & + & h[6] & x[3n-3] & ) \\
          & + & e^{j \frac{2 \pi}{3} c \, 1} & ( & h[1] & x[3n+2] & + &  h[4] & x[3n-1] & + & h[7] & x[3n-4] & ) \\
          & + & e^{j \frac{2 \pi}{3} c \, 2} & ( & h[2] & x[3n+1] & + &  h[5] & x[3n-2] & + & h[8] & x[3n-5] & ) \\
\end{alignedat}
$$

Let's generalize this formula to $$M$$ channels and $$N$$ filter taps:

$$
y_c[n] = \sum_{m=0}^{M-1}  e^{j \frac{2 \pi}{M} c \, m}  \sum_{k=0}^{N-1} h[kM + m] \; x[(n - k)M - m] \\
$$

Now substitute input $$x[n]$$ with an input signal to which a complex heterodyne has been applied.

$$
x[n] = x'[n] \; e^{j \omega_{\Delta} n} 
$$

![Input heterodyne + polyphase channelizer](/assets/polyphase/ble/ble-pre_polyphase_ifft.svg)

$$
y_c[n] = \sum_{m=0}^{M-1}  e^{j \frac{2 \pi}{M} c \, m}  \sum_{k=0}^{N-1} h[kM + m] \; x'[(n - k)M - m] \; 
         \underbrace{e^{j \omega_{\Delta} ((n - k)M - m)}}_\text{offset adjust rotator}
$$

A frequency offset adjustment rotator has been introduced. 

We can split it up this exponential, extract a free-running post-rotator that only depends on decimated 
sample number $$nM$$, and move it all the way to the front:

$$
y_c[n] = \underbrace{e^{j \omega_{\Delta} Mn} }_\text{output rotator}
         \sum_{m=0}^{M-1}  e^{j \frac{2 \pi}{M} c \, m}  \sum_{k=0}^{N-1} h[kM + m] \; x'[(n - k)M - m] \; e^{j \omega_{\Delta} (- kM - m)}  
$$

Now extract a term that only depends on polyphase variable $$m$$:

$$
y_c[n] = e^{j \omega_{\Delta} Mn} \sum_{m=0}^{M-1}  
         \underbrace{e^{-j \omega_{\Delta} m} }_\text{phase adjustment}
         e^{j \frac{2 \pi}{M} c \, m}  \sum_{k=0}^{N-1} h[kM + m] \; x'[(n - k)M - m] \; e^{j \omega_{\Delta} (- kM)}  
$$

Rearrange the remaining exponential that is different for each filter coefficient $$k$$:

$$
y_c[n] = \underbrace{e^{j \omega_{\Delta} Mn}}_{\text{output rotator}} 
         \sum_{m=0}^{M-1}  
         \underbrace{e^{-j \omega_{\Delta} m}}_{\text{phase adjustment}} 
         \underbrace{e^{j \frac{2 \pi}{M} c \, m}}_{\text{IFFT}}  
         \sum_{k=0}^{N-1} h[kM + m]  
         \underbrace{e^{-j \omega_{\Delta} (kM)}}_{\text{filter adjustment}}  \; x'[(n - k)M - m]
$$


There are 3 additional terms now:

* all the filter coefficients are modified by a filter adjustment term $$ e^{-j \omega_{\Delta} (kM)} $$.
* the output of each sub-filter is multiplied by a phase adjustment term $$ e^{-j \omega_{\Delta} m}$$.
* all outputs of the IFFT are subjected to complex heterodyne $$ e^{j \omega_{\Delta} Mn}$$.

None of this is ideal, but the first 2 terms are not dependent on the sample number and can be baked 
into the design. Meanwhile the rotator at the end not only runs at a rate that is M times lower, but the 
phase step of the rotator is also M times larger.

The diagram looks like this:

[![Polyphase channelizer with decimated offset adjustment](/assets/polyphase/ble/ble-polyphase_ifft_post.svg)](/assets/polyphase/ble/ble-polyphase_ifft_post.svg)
*(Click to enlarge)*

In Python, we can use this code:

```python
# No more input heterodyne. Immediately decimate the input signal
ble_decim   = np.flipud(
    np.reshape(
        ble_input,
        ((len(ble_input) // decim_factor), decim_factor),
    ).T
)

# Calculate frequency offset
freq_offset           = channel_offset_hz / (sample_rate_hz / decim_factor)
omega_delta           = 2 * np.pi * freq_offset / decim_factor

# Modify the low pass filter coefficients
h_n                   = np.arange(len(h_lpf_poly[0]), dtype=np.float32)
h_lpf_poly_adj        = np.exp(-1j * omega_delta * decim_factor * h_n).astype(np.complex64)
h_lpf_poly_het        = h_lpf_poly * h_lpf_poly_adj

# Output of the polyphase filter
h_poly_out            = np.array([np.convolve(ble_decim[_], h_lpf_poly_het[_]) for _ in range(decim_factor)])

# Apply a phase rotation to the output of each phase
phase_nr              = np.arange(decim_factor, dtype=np.float32)
h_phase_adj           = np.exp(-1j * omega_delta * phase_nr).astype(np.complex64)
h_poly_out_phase_adj  = h_poly_out * h_phase_adj[:, None]

# IFFT...
channel_data          = np.fft.ifft(h_poly_out_phase_adj, axis=0).astype(np.complex64)

# Output rotator
sample_nr             = np.arange(channel_data.shape[1], dtype=np.float32)
heterodyne_1mhz_decim = np.exp(1j * omega_delta * decim_factor * sample_nr).astype(np.complex64)

# Heterodyne all channels
channel_data_1mhz_post  = channel_data * heterodyne_1mhz_decim[None, :]
```

The channel output samples are not identical to the previous case: there is a phase shift to 
the output I/Q samples. But after GFSK demodulation, the result is the same:

[![BLE Channel 33 decoding with 1 MHz heterodyne after decimation ](/assets/polyphase/ble/chan_33_time_plot_het_post.svg)](/assets/polyphase/ble/chan_33_time_plot_het_post.svg)
*(Click to enlarge)*

All of this seems like a whole lot of effort. We are running all operations at the output
sample rate, but the number of multiplications per output sample is now higher than the case with 
the input heterodyne! 

But remember: this is for the generic case, with random frequency offset. Let's fix that.

# Simplifying for the Half-Channel Offset Case

As mentioned at the start of this blog post, it's common to have a frequency offset that
equal to half the channel width:

$$
F_\Delta = \frac{F_s}{2 M} \\
\omega_\Delta = \frac{\omega}{2 M} = \frac{2 \pi}{2 M} = \frac{\pi}{M}
$$

The crucial observation is that 2 of our adjustment exponentionals feature a 
multiplication by $$M$$:

The filter coefficient adjustment:

$$
e^{-j \omega_\Delta (kM)} = e^{-j \frac{\pi}{M} (kM)} = e^{-j \pi k } = (-1)^k
$$

The output rotator:

$$
e^{-j \omega_\Delta (Mn)} = e^{-j \frac{\pi}{M} (Mn)} = e^{-j \pi n } = (-1)^n
$$

Awesome!  The general equation has been simplified to this:

$$
y_c[n] = (-1)^n
         \sum_{m=0}^{M-1}  
         \underbrace{e^{-j \omega_{\Delta} m}}_{\text{phase adjustment}} 
         \underbrace{e^{j \frac{2 \pi}{M} c \, m}}_{\text{IFFT}}  
         \sum_{k=0}^{N-1} h[kM + m]  
         (-1)^k
         \; x'[(n - k)M - m]
$$

The filter coefficients are real again and the complex multiplier for the output rotator
can be replaced by logic that just flips the sign bit.

[![Post-decimation frequency adjust for half-bin offset](/assets/polyphase/ble/ble-polyphase_ifft_post_half_bin.svg)](/assets/polyphase/ble/ble-polyphase_ifft_post_half_bin.svg)
*(Click to enlarge)*


This is so much better! But it's *still* possible to do better, though the requirements
become even stricter.

# The Odd Case of an Odd Number of Channels

**Ignore this section for now. It's wrong, but it should work eventually.**

To get rid of the complex filter output adjustment, we need to make it either 1 or -1.

$$
e^{-j \omega_\Delta m} = 1, -1
$$

So far, we've only considered the case where the offset is the minimum required: smaller
than the width of one channel. But that doesn't have to be the case: instead of shifting
by half the width of a channel, we can shift by half the channel width plus any number
of full channel widths. Like this:

$$
\omega_\Delta = \frac{\pi}{2M} + 2 \pi p \\ 
\omega_\Delta = \frac{\pi}{2M} + \frac{2 \pi 2M}{2M} p \\
\omega_\Delta = \frac{\pi}{2M} + \frac{2 \pi 2M-1 + 1}{2M} p \\
\omega_\Delta = \frac{\pi}{2M} + \frac{2 \pi 2M-1}{M} p + \frac{2 \pi}{2M} p \\
$$

When applied to the filter output adjustment term, the second always reduces to 1.


# References

* [Youtube - Recent Interesting and Useful Enhancements of Polyphase Filter Banks: fred harris](https://www.youtube.com/watch?v=afU9f5MuXr8)

* [Stackexchange - Understanding Polyphase Filter Banks](https://dsp.stackexchange.com/questions/96042/understanding-polyphase-filter-banks)

* [Stackexchange - How to implement Polyphase filter?](https://dsp.stackexchange.com/questions/43344/how-to-implement-polyphase-filter)

 > Making a polyphase filter implementation is quite easy; given the desired coefficients 
 > for a simple FIR filter, you distribute those same coefficients in "row to column" format 
 > into the separate polyphase FIR components

* [Bit by Bit Signal Processing Tutorials - Channelizer Tutorial](https://bxbsp.com/Tutorials.html)

* [IEEE - Digital Receivers and Transmitters Using Polyphase Filter Banks for Wireless Communications](https://ieeexplore.ieee.org/document/1193158)

  Also available on scihub.

* [Spectrometers and Polyphase Filterbanks in Radio Astronomy](https://arxiv.org/pdf/1607.03579)

  Includes discussion about PFB. However, there is [this comment on Stackexchange](https://dsp.stackexchange.com/questions/43344/how-to-implement-polyphase-filter)
  about it:

  > The technique in the paper may be misnamed (or does not fit the normal use of polyphase filtering for resampling).
  >
  > ...
  >
  > This technique is sometimes called the polyphase DFT or windowed overlap-add (WOLA) processing. 


  * [PFB introduction](https://github.com/telegraphic/pfb_introduction/blob/master/pfb_introduction.ipynb)

    Jypiter PFB notebook.

  * [The Polyphase Filter Bank Technique](https://casper.berkeley.edu/wiki/The_Polyphase_Filter_Bank_Technique)

    Explains why a filter before the FFT is useful: scalloping loss and leakage.

* [DSP related - Polyphase Filters and Filterbanks](https://www.dsprelated.com/showarticle/191.php)

  Confusing...
  
* [Multirate Digital Filters, Filter Banks, Polyphase Networks, and Applications: A Tutorial](https://home.engineering.iastate.edu/~julied/classes/ee524/articles/multirate_article.pdf)

  Very long article by P. P. Vaidyanathan.
    

* [Interpolation and A Decimation of Digital Signals - Tutorial Review](https://firmware-developments.com/WEB/DOC/REF/SRC%20CROCHIERE%2001456237.pdf)

* [POLYPHASE DECOMPOSITION](https://www.dsprelated.com/freebooks/sasp/Polyphase_Decomposition.html)

  Part of SPECTRAL AUDIO SIGNAL PROCESSING book by Julius Smith.

* [INTRODUCTION TO DIGITAL FILTERS WITH AUDIO APPLICATIONS - Julius Smith](https://www.dsprelated.com/freebooks/filters/)

* [MULTIRATE SIGNAL PROCESSING](https://eeweb.engineering.nyu.edu/iselesni/EL713/zoom/mrate.pdf)

  On page 21, says that the noble identities only work in one direction, if you move the 
  decimator to the right. Rarely the other way around.

* [Designing Anaylsis and Synthesis Filterbanks in GNU Radio](https://static.squarespace.com/static/543ae9afe4b0c3b808d72acd/543aee1fe4b09162d08633d9/543aee20e4b09162d086354a/1395369129837/rondeau_gr_filtering.pdf)

 > In the channelization process, we want those aliases. Recall that the filterbanks use 
 > the same filter with a different phase. When filtering, each of the aliased zones is 
 > processed by each arm of the filterbank, which has its own phase.

# Footnotes

