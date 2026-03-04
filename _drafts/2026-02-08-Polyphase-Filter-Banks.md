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

We can see a thin bright line at the 2441 MHz center frequency. This is a common artifact of the 
imperfect SDR hardware. It could be caused by local oscillator leakage or an imbalance between the 
I and Q channels of the quadrature AD converters, or both.

In this video, harris talks about how DC is often problematic, and a reason to have channel with an
offset so that none of the channel center frequencies coincides with DC. I'm pretty sure that is
one of the reasons why.

We can also see some symmetry around the 2441 MHz line. For example, there's a short burst around
1.1 ms at 2415 Mhz and weaker version 2467 MHz. This weaker version isn't real either, but a
spectral mirrom image that's cause by imbalance between the I and the Q channel: their phase shift
might not be exactly 90 degrees or they might have a slight different gain on their way to the ADCs.
This is another topics that harris talks about: if possible, use a single double-speed ADC and do
all the I/Q handling in the mathematically perfect digital domain.

[![BLE Waterfall Plot with Channels](/assets/polyphase/ble/ble_input_data_waterfall_bars.png)](/assets/polyphase/ble/ble_input_data_waterfall_bars.png)
*(Click to enlarge)*

[![BLE Channel 33 decoding with 1 MHz heterodyne before channelization](/assets/polyphase/ble/chan_33_time_plot_het_pre.svg)](/assets/polyphase/ble/chan_33_time_plot_het_pre.svg)
*(Click to enlarge)*

[![BLE Channel 33 decoding with 1 MHz heterodyne after decimation ](/assets/polyphase/ble/chan_33_time_plot_het_post.svg)](/assets/polyphase/ble/chan_33_time_plot_het_post.svg)
*(Click to enlarge)*

# Derivation

![polyphase, IFFT](/assets/polyphase/ble/ble-polyphase_ifft.svg)

![Input heterodyne, polyphase, IFFT](/assets/polyphase/ble/ble-pre_polyphase_ifft.svg)

Starting formula:

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

$$
y_c[n] = \sum_{m=0}^{M-1}  e^{j \frac{2 \pi}{M} c \, m}  \sum_{k=0}^{N-1} h[kM + m] \; x[Mn - kM - m] \\
y_c[n] = \sum_{m=0}^{M-1}  e^{j \frac{2 \pi}{M} c \, m}  \sum_{k=0}^{N-1} h[kM + m] \; x[(n - k)M - m] \\
$$

Input heterodyne:

$$
x[n] = x'[n] \; e^{j \omega_{\Delta} n}  
$$

Substitute $$x[n]$$:

$$
y_c[n] = \sum_{m=0}^{M-1}  e^{j \frac{2 \pi}{M} c \, m}  \sum_{k=0}^{N-1} h[kM + m] \; x'[(n - k)M - m] \; e^{j \omega_{\Delta} ((n - k)M - m)}  
$$

Extract free-running post-rotator:

$$
y_c[n] = e^{j \omega_{\Delta} Mn} \sum_{m=0}^{M-1}  e^{j \frac{2 \pi}{M} c \, m}  \sum_{k=0}^{N-1} h[kM + m] \; x'[(n - k)M - m] \; e^{j \omega_{\Delta} (- kM - m)}  
$$

Extract per phase constant:

$$
y_c[n] = e^{j \omega_{\Delta} Mn} \sum_{m=0}^{M-1}  e^{-j \omega_{\Delta} m} e^{j \frac{2 \pi}{M} c \, m}  \sum_{k=0}^{N-1} h[kM + m] \; x'[(n - k)M - m] \; e^{j \omega_{\Delta} (- kM)}  
$$

Coefficient adjustment:

$$
y_c[n] = e^{j \omega_{\Delta} Mn} \sum_{m=0}^{M-1}  e^{-j \omega_{\Delta} m} e^{j \frac{2 \pi}{M} c \, m}  \sum_{k=0}^{N-1} h[kM + m] \; e^{-j \omega_{\Delta} (kM)}  \; x'[(n - k)M - m]
$$


$$
y_c[n] = \underbrace{e^{j \omega_{\Delta} Mn}}_{\text{offset output rotator}} 
         \sum_{m=0}^{M-1}  
         \underbrace{e^{-j \omega_{\Delta} m}}_{\text{offset phase adjust}} 
         \underbrace{e^{j \frac{2 \pi}{M} c \, m}}_{\text{IFFT}}  
         \sum_{k=0}^{N-1} h[kM + m]  
         \underbrace{e^{-j \omega_{\Delta} (kM)}}_{\text{filter offset adjust}}  \; x'[(n - k)M - m]
$$


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

