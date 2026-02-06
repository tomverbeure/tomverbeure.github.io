---
layout: post
title: A Complex Heterodyne Operation Explained
date:   2026-02-05 00:00:00 -1000
categories:
---

<script async src="https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-AMS_CHTML"></script>

* TOC
{:toc}

TODO:

* show with Euler identity and DTDF formula why there is a negative spectrum?
* link to graph generation script

# Introduction

In my previous blog post about [polyphase decimation](/2026/01/25/Notes-on-Basic-Polyphase-Decimation.html), 
my reason for looking at that topic was "reading up on polyphase filters and multi-rate digital signal 
processing", but to be more specific, it all started by watching 
["Recent Interesting and Useful Enchancements of Polyphase Filter Banks"](https://www.youtube.com/watch?v=afU9f5MuXr8)
a fantastic tutorial by [Fred Harris](https://en.wikipedia.org/wiki/Fredric_J._Harris).
The video is more than 90 min long and is a lot to process when your DSP knowledge is lacking.

I've watched the video a few times now, and while I kind of get what he's doing, it made me realize even 
more how skin-deep my DSP knowledge really is.

For example, the video talks about a *complex heterodyne* of the input signal, but I couldn't really 
explain how the outcome of that operation is different from mixing an input signal with a regular sinusoid. 

To fix this, I'm diving into the subject step-by-step  and blog post by blog post. The general
approach is to demonstrate concepts (to myself) by implementing them in 
[NumPy](httpsP//numpy.org) 
and plotting the results while limting the number of mathematical formulas. In the process of peeling 
that onion, new knowledge gaps will be exposed that might not be directly relevant to the video, but if 
interesting enough, I'll check those out just the same.

But that's for the future. Let's talk about the why and how of a complex heterodyne.

# Sampling with 1 ADC Creates a Real Signal

Let's create an input signal that's interesting enough to demonstrate DSP theory in practice and
trip us up if we're doing something wrong. It's a signal that you could get out of
a real-world front end with a single AD converter (ADC) that has a sampling clock
of 100 MHz.

```python
signal_pure = ( signal1_amplitude * np.sin(2 * np.pi * signal1_freq_hz * t)
              + signal2_amplitude * np.cos(2 * np.pi * signal2_freq_hz * t) )

noise_floor = np.random.normal(0.0, noise_rms, NR_SAMPLES)

oob_noise           = np.random.normal(0.0, oob_noise_rms, NR_SAMPLES)

oob_noise_cutoffs   = [ OOB_NOISE_SBF_LOW_MHZ / (SAMPLE_CLOCK_MHZ / 2.0),
                        OOB_NOISE_SBF_HIGH_MHZ / (SAMPLE_CLOCK_MHZ / 2.0) ]

oob_noise_h         = firwin( OOB_NOISE_FIR_TAPS,
                              oob_noise_cutoffs,
                              window=("kaiser", OOB_NOISE_KAISER_BETA),
                              pass_zero="bandstop" )

oob_noise_filtered  = np.convolve(oob_noise, oob_noise_h, mode="same")

signal      = signal_pure + noise_floor + oob_noise_filtered
```

The signal has the following components:

* 2 sinusoids, one at 22 MHz and one at 17 MHz. The second one has an amplitude that
  is 10 dB lower. 

  This is the signal that we're interested in.

* A tiny bit of noise across the whole spectrum

  This adds a noise floor to the overall spectrum which makes it more like 
  the real world and also makes the frequency plots more pleasing go the eye.

* Out-of-band noise that is everywhere expect in the frequency band where our
  signal lives.

  This is useful to verify that we're processing the signal the right way. If we
  don't then this noise will overlap the spectrum of the signal of interest and
  we'd notice that right away in the spectrum plot.

![Input signal time and spectrum plot](/assets/polyphase/complex_heterodyne-input_signal.svg)

In a time domain plot, we see a typical case of sinusoids interacting with each other,
resulting in some kind of beat envelope frequency. The noise is too low to be noticable
in a non-logarithmic plot.

The frequency domain amplitude plot is a more interesting. There are the 2 peaks
of different amplitude, a noise floor in the frequency band where our signal lives,
and the more prominent out-of-band noise everywhere else. 

We can also see that the negative frequency side of the spectrum is a mirror of 
the positive side. This is as it should be: to display the spectrum, we performed a 
[Discrete Time Fourier Transformation (DTFT)](https://en.wikipedia.org/wiki/Discrete-time_Fourier_transform),
which I'll call the Fourier transform from now on for brevity.

A Fourier transform determines the presence of a sinusoidal components in the signal 
under test by multiplying them by $$sin(2 \pi f_i t)$$ and $$cos(2 \pi f_i t)$$ for all 
frequency values. For each frequency, you get 2 values, let's call them $$I_i$$ and $$Q_i$$ 
so that the frequency component is $$I_i \cos(2 \pi f_i t) + Q_i \sin(2 \pi f_i t)$$. The 
amplitude of that frequency is $$\sqrt{I_i^2 + Q_i^2)}$$ and the phase is 
$$arctan(\frac{I_i}{Q_i})$$. For notational convenience, $$I_i$$ and $$Q_i$$ are often 
combined into a single complex number $$I_i + j Q_i$$.

If the Fourier transform is applied to signal that doesn't have complex values, 
as is the case when you use only 1 ADC, then the result will have
[Hermitian symmetry](https://www.dsprelated.com/freebooks/sasp/Symmetry_DTFT_Real_Signals.html):
for every complex value on the positive frequency side, the corresponding negative frequency value
will have the same real value $$I_i$$ and an inverted imaginary value $$Q_i$$. Because of this,
the amplitude is the same but the phase is inverted.

In the frequency plot above, only the amplitude is shown, hence the mirror image with
identical amplitudes left and right.

In DSP land, a signal that doesn't have imaginary component values is called a real
signal. A signal that is complex and that doesn't have a negative frequency 
components is an [analytic signal](https://en.wikipedia.org/wiki/Analytic_signal).

# Heterodyning the Signal to Baseband the Wrong Way

Let's imagine that we have multiple frequency bands, that each band has a bandwidth
of 10 MHz, and that we have channels with center frequencies at 0, 10, 20, 30
and 40 MHz. Our signal would then be part of the 20 MHz channel with a range from
15 to 25 MHz.

![Different channels](/assets/polyphase/complex_heterodyne-channels.svg)

To process a channel, we'd like to move the channel from 15 MHz to 25 MHz to the baseband 
range of -5 MHz to 5 MHz. For our case, this means that we want the 17 MHz and 22 MHz 
components to end up at -3 MHz and +2 MHz resp.

By first moving the channel to baseband before doing futher processing, we can use 
the same math operations for all channels. It also allows us to reduce the sample rate from
100 MHz to something much lower, thus reducing DSP resource requirements.

You shift the spectrum of a signal by multiplying it with a sine wave. The
multiplication of 2 signals is also called [mixing](https://en.wikipedia.org/wiki/Frequency_mixer). 
And mixing with the purpose of moving the spectrum of a signal is called 
[heterodyning](https://en.wikipedia.org/wiki/Heterodyne).

The math of heterodyning a sine wave if straightforward. Let's start with signal
$$s(t)$$ and local oscillator $$l(t)$$:

$$
s(t)= A \cos(2 \pi f_0 t) \\
l(t)= \cos(2 \pi f_c t) \\
$$

Multiply the 2 signals to get heterodyne signal $$y(t)$$:

$$
y(t) = s(t) l(t) = A \cos(2 \pi f_0 t) \cos(2 \pi f_c t) \\
$$

Use the textbook trigonometry identity:

$$
\cos \alpha \cos \beta = \frac{1}{2} \big[ \cos(\alpha + \beta) + \cos(\alpha - \beta)  \big]
$$

We get:

$$
y(t) = A \frac{1}{2} \big[ \cos(2 \pi (f_0 + f_c) t) + \cos( 2 \pi (f_0 - f_c) t) \big]
$$

What this tells us is that multiplying a signal with frequency component $$\omega_0$$
with sine wave with frequency $$\omega_c$$ will create 2 frequency components.

If we want to shift the center frequency of our channel from 20 MHz to 0 MHz, we need to
multiply with a 20 MHz sine wave. Let's do that:

```python
lo_signal       = np.sin(2 * np.pi * lo_freq_hz * t)
signal_real_het = signal * lo_signal
```

This is the resulting spectrum:

![Spectrum after real heterodyn](/assets/polyphase/complex_heterodyne-real_het.svg)

That... didn't go as we hoped. 

The spectrum got shifted down by 20 MHz to 0 MHz and to -40 MHz,
given us peaks at -3 MHz and +2MHz and -37 MHz and -42 MHz. That's what we wanted!
But since `lo_signal` is a real signal, it has a mirror image at -20 MHz. This made
the spectrum of the signal shift up +3 MHz and -2 MHz and 37 MHz and 42 MHz. 

Instead of the desired 2 peaks in the baseband, there are now 4, at -3, -2, 3 and 3 Mhz. 
We've destroyed the original signal.

Heterodyning with a real local oscillator is a common operation in the analog world, but
when this is done, the heterodyne doesn't happen to baseband but a non-zero intermediate
frequency. That is the idea of the 
[superheterodyne receiver](https://en.wikipedia.org/wiki/Superheterodyne_receiver)[^super], a huge
breakthrough in 1918 in the development of radio technology: it mixes the desired signal
to a fixed intermediate frequency (not the baseband!) and does further demodulation such
AM or FM on that fixed intermediate frequency signal.

[^super]: If you're wondering why it's called 'super': it's because the result of the
          heterodyne is a signal that is still in the supersonic frequency range, as in,
          above the audible frequency range. Before superheterodyne receivers, the radio signal
          of interested was heterodyned straight to the audio range.

# Complex Heterodyne to the Rescue

We could definitely do a superheterodyne in the digital world, but many modern modulation
schemes such as 
[QAM](https://en.wikipedia.org/wiki/Quadrature_amplitude_modulation) or 
[OFDM](https://en.wikipedia.org/wiki/Orthogonal_frequency-division_multiplexing)
rely on the ability to process the signal in the baseband.

Luckily, the solution is simple enough. The root of our troubles is the presence of a 
negative frequncy mirror frequency image for the local oscillator. If we can get rid of ,
one of those orange peak, only one spectrum image of the signal will get heterodyned into
the baseband.

This is surpringly simple: instead of a real sinusoid, we use a complex one:

$$
l(t) = e^{-j 2 \pi f_c t}
$$

This signal only has a peak in the spectrum at $$-fc$$.

Let's define the complex local oscillator signal and multiply it by
the input signal:

```python
complex_lo_signal   = np.exp(-1j * 2 * np.pi * lo_freq_hz * t)
signal_complex_het  = signal * complex_lo_signal
```

And voila:

![Complex LO and heterodyne](/assets/polyphase/complex_heterodyne-complex_lo.svg)

We had to move from real to complex numbers, but the result is worth it: the baseband
has exactly what we wanted.

# Filtering Away the Old Negative Image

The only thing that's still bothering us are the 2 peaks around -40 MHz. It needs
to go if we want to lower the sample rate by decimation.

We can do this with a low pass FIR filter. There are multiple ways to design these kind
of filter. I even wrote [a blog post](2020/10/11/Designing-Generic-FIR-Filters-with-pyFDA-and-Numpy.html) 
about it.

Here, I chose [windowing method](https://www.dsprelated.com/freebooks/sasp/Window_Method_FIR_Filter.html)
to create a 201 taps FIR filter with a passband of 5 MHz.

```python
fir_cutoff  = FIR_PASSBAND_MHZ / (SAMPLE_CLOCK_MHZ / 2.0)
h_lpf       = firwin(FIR_TAPS, fir_cutoff, window=("kaiser", FIR_KAISER_BETA), pass_zero=True)
```

The filter is applied by doing a convolution between the heterodyned signal and the filter taps in `h_lpf`:

```python
signal_het_lpf      = np.convolve(signal_complex_het, h_lpf, mode="same")
```

Note that the samples of `signal_complex_het` are complex, but the filter coefficients are real.

Here's the result:

![Complex heterodyned signal with low pass filter](/assets/polyphase/complex_heterodyne-low_pass_filter.svg)

# Decimation 

The spectrum has now been reduced to -5 MHz and 5 MHz. Since there is no mirror image, we can
reduce the sample rate from 100 MHz to 10 MHz without running into aliasing issues. So let's
do that:

```python
signal_decim    = signal_het_lpf[::DECIM_FACTOR]
```

We now have 10 times less data to deal with, but the spectrum looks just the same
as before:

![Spectrum after decimation](/assets/polyphase/complex_heterodyne-decim_fft.svg)

Success!

# Final Block Diagram

Wrapping up, we arrived at the following block diagram of operations and transformations:

![Block diagram with all operations](/assets/polyphase/complex_heterodyne-block_diagram.drawio.svg)

* The analog signal is converted to a real digital with a single channel, 100 Msps ADC 
* A mixer and a complex local oscillator heterodynes the signal to baseband. The
  signal is now complex.
* A low pass filter filters out all frequencies that don't reside in the baseband.
* A decimator brings down the sample rate from 100 MHz to 10 MHz
* The output is a complex 10 MHz sample stream.

The thing works, but is the optimal of doing things? My previous blog post about polyphase 
decimation filtering should be hint that the answer is: definitely not.

Dealing on a complex instead of real signal doubles the number of math operations
and doing a decimation at the end means that we're doing a lot of math that gets
thrown away. 

But I have a much better understanding about heterodyning now, so that's a definite
win!

In a next installment, I'll explore how this can be optimized.

# References

* [Stackexchange - How to implement Polyphase filter?](https://dsp.stackexchange.com/questions/43344/how-to-implement-polyphase-filter)

 > Making a polyphase filter implementation is quite easy; given the desired coefficients 
 > for a simple FIR filter, you distribute those same coefficients in "row to column" format 
 > into the separate polyphase FIR components

* [Stackexchange - Understanding Polyphase Filter Banks](https://dsp.stackexchange.com/questions/96042/understanding-polyphase-filter-banks)

* [Youtube - Recent Interesting and Useful Enhancements of Polyphase Filter Banks: Fred Harris](https://www.youtube.com/watch?v=afU9f5MuXr8)

  Spectularly good video.

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

