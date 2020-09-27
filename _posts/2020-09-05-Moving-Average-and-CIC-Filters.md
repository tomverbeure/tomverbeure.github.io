---
layout: post
title: An Intuitive and Practical Look at Moving Average and CIC Filters
date:  2020-09-05 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

I've been slowly working my way through 
[The Scientist and Engineer's Guide to Digital Signal Processing](http://www.dspguide.com/pdfbook.htm)
in an effort to revive some of my long forgotten DSP knowledge.

The ultimate goal is to become proficient enough in DSP to experiment with software
defined radio and audio processing.

I also want to get better at using Numerical Python (numpy) and matplotlib, its
graph plotting package.

The best way to really learn something is by doing, so I'm taking a chapter of the
book, check if I can confirm and recreate the claimed characteristics in numpy, and
then implement it on an FPGA.

My test vehicle is a setup that takes in the data of a MEMS microphone with a single bit pulse density
modulation (PDM) output, convert that to 16-bit pulse code modulation (PCM), and send the result
to an optical SPDIF output.


# Moving Average Filters

Typical FIR filters require a multiplication per filter tap. Larger FPGAs have a decent set of DSPs
(which are essentially HW accumulate-addition blocks), but even then, setting up an efficient FIR structure can be
a hassle.

The multipliers are there to ensure that the filter has the desired pass band, transition band, and
stop band characteristics.

But what if we just ignore required characteristics to get rid of this kind of mathematical complexity?

The simplest filter, then, is the moving averaging filter (also called "boxcar filter"): it sums the last 
N samples, divides the result by N and... that's it!

A moving average filter is probably one of the most common filters in digital signal processing: it's
super simple to understand and implement, and it's also an optimal filter for white noise reduction. That's
white noise doesn't have a preference to impact this sample or the other, it affects any sample
with equal chance. Because of that, there's no way you can tune this or that coefficient of the
filter coefficients in some preferential way.

Unfortunately, moving average filters have some major disadvantages as well: they have a very slow roll-off
from the pass band to the stop band, and the stop band attentuation is very low as well.

However, you can overcome the low stop band attenuation by cascading multipe filters after each other.

There are only 2 parameters to play with: the size of the box (the number of samples that are averaged
together) and the order, number of filters that are cascaded

Here's how that looks in terms of filter response:

![Moving Average Filter Response](/assets/pdm/moving_average_filter_overview.svg)

As we increase the length of the filter, the band pass gets narrower, but the attenuation of the stop 
band,the height of the second lobe, stays the same. For the first order filter, the stop band
attenuation is ~13dB, irrespective of the length of the filter.

When we increase the order, the attenuation of the stop band increases accordingly: you can just
multiple the stop band attenuation of the first order filter by the number of stages.

As mentioned earlier, another problem of the moving average filter is that its passband
behavior isn't very flat: in the frequency domain, the transfer function follows a sin(x)/x
curve, which starts out flat at the 0, becomes progressively steeper as the frequency increases.

![Box Filter Passband](/assets/pdm/moving_average_filter_passband.svg)

With these problematic characteristics, are moving average filters even worth doing?

The answer is yes!

When these filters are used for decimation (downsampling), they are even easier than you'd think they would be.

# Moving Average Implementation from Trivial to Cascaded Integrator Comb (CIC) Configuration

The most naieve and trivial moving averaging filter implementation would be a literal translation
of the math that describe averaging into hardware. It'd look something like this:

![Moving Average Filter - Trivial Implementation](/assets/pdm/moving_average_filters_trivial.svg)

The implementation above averages 8 samples, requires 7 delay elements and 7 adders. There are
no multipliers, but you're the 7 adders are bit difficult to accept. Can we do better?

Of course!

For each new sample, 



In XXX, Eugene Hogenauer published a seminal paper about how to implement cascaded moving average
filters for decimation and interpolation purposes that reduces the required hardware to 2 registers,
1 adder, and 1 subtractor.





While the 64-length filter has that terrible pass band attenuation of -33.7dB, the attenuation of 16-length 
version of that 4th order filter at the same 0.01 is only -1.8dB. For high quality audio, the pass band
ripple should only be around 0.2dB, so -1.8dB is still way too high. 






Can we use just cascaded moving average filters for our factor 64 decimation example? Not at all!
Even when 4 filters are cascaded, the stop band attenuation is only -66dB. And if we want
to downsample by a factor of 64 and use a filter length of 64, the passband attenuation at 
0.01 of the normalized frequency (which corresponds to 15.36kHz of our example) is already
around -33.7! 




# References

* [The Scientist and Engineer's Guide to Digital Signal Processing](http://www.dspguide.com/pdfbook.htm)

    Awesome book about DSP that's low on math and high on intuitive understanding. The digital version
    is free too!

## General DSP

* [dspGuru FAQs](https://dspguru.com/dsp/faqs/)
    
    FAQs about FIR, IIR, multirate (decimation, interpolation, resampling), FFT etc.
    
    Doesn't go much in detail, but really useful as a refresher.

* [TomRoelandts.com](https://tomroelandts.com/articles)

    Lots of interesting filtering related articles.

    He's also the creator [FIIIR!](https://fiiir.com/), an online tool to create a variety of filters.

* [Earlevel Engineering](https://www.earlevel.com/main/)

    Tons of articles related to audio DSP.

# Filter Design

* [Tom Roelandts - How to Create a Simple Low-Pass Filter](https://tomroelandts.com/articles/how-to-create-a-simple-low-pass-filter)

    Simple explanation, Numpy example code.

## Decimation


* [Rick Lyons - Optimizing the Half-band Filters in Multistage Decimation and Interpolation](https://www.dsprelated.com/showarticle/903.php)

    Talks about how it may not be ideal to have 3 identical cascaded 2x half-band filters when
    you want to be decimate by 8. Unfortunately, it only does so qualitatively, not quantitatively.


## Filter Tools

* [FIIIR1](https://fiiir.com)

* [LeventOztruk.com](https://leventozturk.com/engineering/filter_design/)


