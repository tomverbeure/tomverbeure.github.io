---
layout: post
title: HW Implementation of a Multi-Stage PDM to PCM Decimation Pipeline
date:  2020-12-19 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

In [episode 6](/2020/12/20/Design-of-a-Multi-Stage-PDM-to-PCM-Decimation-Pipeline.html) of 
my [PDM to PCM conversion series](#references), I finally settled on a multi-stage
filter architecture.

Nothing can stop me now to implement this filter in RTL. Or is there?

So far, the filter only exists in a perfect world with double precision floating
point calculations. And while modern FPGAs like Intel's Arria 10 series have support
for floating point DSPs now, it'd be ridiculous overkill to use those for some basic
audio processing. So I first need to convert the theoretical model into a practical
one that can be implemented with just integer operations.

Once there, I will enter the warm, comfortable world of digital architecture and
writing RTL. I can't wait!

# Frequency Magnitude Plot of a Multi-Stage Decimation Filter

I was so trigger happy to push my previous blog post live that I forgot to merge
all filter stages together and plot the overall magnitude frequency response graph
before and after decimation.

Let's get that out of the way first!

When you have a decimation filter, there are 2 ways to display a transfer function:
before decimation and after decimation. Since decimation folds higher frequencies
into lower frequency bands, and thus multiple values gets merged together, it's
more useful to see the transfer function before decimation.

You don't need to do anything for a single stage decimation filter: just plot the 
frequency magnitude plot of the filter before the decimation operation.

But in the case of a multi-stage decimation filter, you need to convert the transfer
function of the downstream filters back to a higher sample rate. This is no different
than interpolating a signal to a higher sample rate (without doing any filtering.)

There are two ways to do that: in the frequency domain or in the time domain.

**Frequency Domain**

If you already have the frequency domain response for all the filter stages, you
need to 'unfold' that inform such that it spans the full original frequency range.

For example, if the input sample rate is 2.304MHz and half-band filter 2 has an input
sample rate of 96kHz (because the earlier filter stages have already decimated the input
by a factor of 24), then you need to  unfold the transfer function of this filter 24 times.

Once you've done that for all filter stages in the pipeline, you can simply add the
transfer functions for each filter together (in the dB domain).

You can see the result in the plot below:

![Transfer Functions Combined at Each Step - Freq Domain](/assets/pdm/pdm_pcm2rtl/pdm_pcm2rtl_joint_filters.svg)

*Note that the scale of the Y axis is different for the left and the right column!*

The plots in the left column have the individual transfer funtions for each filter stage 
after unfolding them back to the original input frequency. The plots in the right column 
show the cumulative effect of each additional filter step. 

You can see how each step increases the attenuation for higher frequencies until, in the
bottom right plot, only the tiny pass band is left untouched while everything else has
been attenuated by 89dB or more.

It's still necessary to check the result after decimation. For that, I alias the higher frequencies 
back onto the sampling frequency of the output, and check the frequency plot from 0 to 
24kHz, 1/2 of the 48kHz sampling rate:

![Transfer Functions Combined after Decimation](/assets/pdm/pdm_pcm2rtl/pdm_pcm2rtl_joint_filters_after_decimation.svg)

Stop band attenuation and pass band ripple are looking fine, with the pass band barely
making the 0.1dB point at 6kHz point.

**Time Domain**

Instead of doing everthing in the frequency domain, you can do all operations in the time domain, then
perform an FFT and check the frequency magnitude plot.

Once again, this is no different than an interpolation operation in the time domain, which is
done by inserting a number of zeros between impulse response samples that is equal to the cumulative 
decimation ratio minus one.

Using the example as earlier, to make up convert half-band filter 2 with a sample rate of 96kHz to 
a sample rate of 2.304MHz, you'd have to insert 23 zeros in between each impulse response coefficient.

(This increases the number of the filter taps accordingly, even if all the new coefficients are zeros.)

Inserting these zeros very simple with NumPy:

```python
def interpolate_zeros(h_in, ratio = 1):

    h_out = np.zeros(ratio * len(h_in) -1)
    h_out[::ratio] = h_in
```

Once interpolated, you need to cascade the filter stages by convolving them together.

For our 4 stage pipeline with 1 CIC filter, 2 half-band filters, and a regular FIR filter,
the final joint impulse response for the original input sample rate is calculated as follows:

```python
    cic_hb1_h           = np.convolve(cic_h, interpolate_zeros(hb1_h, 12))
    cic_hb1_hb2_h       = np.convolve(cic_hb1_h, interpolate_zeros(hb2_h, 24))
    cic_hb1_hb2_fir_h   = np.convolve(cic_hb1_hb2_h, interpolate_zeros(fir_h, 48))
```

Once there, you can create the frequency magnitude plot just like for any other given
impulse response.

For completeness, I'm showing the resulting graph. If you compare them closely to the one
generated using the frequency domain method, you'll see some minor differences due to differenes
in number sample points per graph and rounding errors. You'll also notice the the left column
doesn't have the individual filters unfolded. But other than that, they are identical,
as expected.

![Transfer Functions Combined at Each Step - Time Domain](/assets/pdm/pdm_pcm2rtl/pdm_pcm2rtl_joint_filters_alt.svg)

# CIC Bit Widths

The [formula](/2020/09/30/Moving-Average-and-CIC-Filters.html#the-size-of-the-delay-elements-in-a-cic-filter)
to calculate the width of the delay elements in a CIC filter is the following:

*nr bits = x(n) bits + roundUp(nr stages * log2(nr delay elements in comb stage * decimation ratio))*

In our case, with a decimation ratio of 12 and 4 stages, this becomes:

*nr bits = 1 + roundUp(4 * log2(1 * 12)) = 17*

The design specification required a 16-bit dynamic range, so we can drop 1 bit at the output of the
CIC filter.

CIC filters are normally implemented with integer-only operations, so the only place where
there will ever be a loss is that LSB. Rather than implementing an integer based CIC filter model in 
NumPy, I treat it as a non-recursive generic FIR filter with imprefect floating point coefficients

# Half-Band and FIR filter

Since the input is 16 bits, I'll keep the output 16 bits as well.

The question is how many bits to keep for the coefficients for the half-band and generic FIR filter.


# References

**My Blog Posts in this Series**

* [An Intuitive Look at Moving Average and CIC Filters](/2020/09/30/Moving-Average-and-CIC-Filters.html)
* [PDM Microphones and Sigma-Delta A/D Conversion](/2020/10/04/PDM-Microphones-and-Sigma-Delta-Conversion.html)
* [Designing Generic FIR Filters with pyFDA and NumPy](/2020/10/11/Designing-Generic-FIR-Filters-with-pyFDA-and-Numpy.html)
* [From Microphone Datasheet to Filter Design Specification](/2020/10/17/From-Microphone-Datasheet-to-Design-Specification.html)
* [Half-Band Filters, a Workhorse of Decimation Filters](/2020/12/15/Half-Band-Filters-A-Workhorse-of-Decimation-Filters.html)

**Filter Design**

* [Efficient Multirate Realization for Narrow Transition-Band FIR Filters](https://www.cs.tut.fi/~ts/Part4_Tor_Tapio1.pdf)

    XXX Need to study this...

**Decimation**

* [Optimum FIR Digital Filter Implementations for Decimation, Interpolation, and Narrow-Band Filtering](https://web.ece.ucsb.edu/Faculty/Rabiner/ece259/Reprints/087_optimum%20fir%20digital%20filters.pdf)

    Paper that discusses how to size cascaded filter to optimized for FIR filter complexity.

* [Seamlessly Interfacing MEMS Microphones with Blackfin Processors](https://www.analog.com/media/en/technical-documentation/application-notes/EE-350rev1.pdf)

    Analog Devices application note. C code can be found[here](https://www.analog.com/media/en/technical-documentation/application-notes/EE350v01.zip)

* [The size of an FIR filter for PDM-PCM conversion](https://www.dsprelated.com/thread/11806/the-size-of-an-fir-filter-for-pdm-pcm-conversion)

    Discussion about PDM to PCM conversion on DSPrelated.com.

* XMOS Microphone array library

    https://www.xmos.ai/download/lib_mic_array-%5buserguide%5d(3.0.1rc1).pdf

    Lots of technical info about PDM to PCM decimation.

