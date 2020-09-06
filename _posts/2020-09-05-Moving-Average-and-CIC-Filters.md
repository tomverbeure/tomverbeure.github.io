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

I also want to get better at using Numerical Python (numpy) and matplotlib, it's
graph plotting package.

The best way to really learn something is by doing, so I'm taking a chapter of the
book, check if I can confirm and recreate the claimed characteristics in numpy, and
then implement it on an FPGA.

My test vehicle is a setup that takes in the data of a MEMS microphone with a single bit pulse density
modulation (PDM) output, convert that to 16-bit pulse code modulation (PCM), and send the result
to an optical SPDIF output.


# Moving Average Filters

As we noticed earlier: typical FIR filters require a multiplication per filter tap. Larger FPGAs
have a decent set of HW multipliers, but even then, setting up an efficient FIR structure can be
a hassle.

The multipliers are there to ensure that the filter has the right pass band, transition band, and
stop band characteristics.

But what if we just ignore some of those characteristics with the explicit goal to get rid of this
kind of mathematical complexity?

The simplest filter, then, is the moving averaging filter: it sums the last N samples,
divides the result by N and... that's it!

A moving average filter probably one of the most common filters in digital signal processing: it's
super simple to understand and implement, and it's also an optimal filter for white noise reduction. That's
white noise doesn't have a preference to impact this sample or the other, it affects any sample
with equal chance. Because of that, there's no way you can tune this or that coefficient of the
filter coefficients in some preferential way.

Unfortunately, moving average filters have some major disadvantages as well: they have a very slow roll-off
from the pass band to the stop band, and the stop band attentuation is very low as well.

But one way to overcome that is by cascading multiple filters after each other.

So there are 2 parameters to play with: the size of the box (the number of samples that are averaged
together) and the number of filters that are cascaded.

Here's how that looks in terms of filter response:

![Moving Average Filter Response](/assets/pdm/moving_average_filter_overview.svg)

As we increase the length of the moving average filter, the band pass gets narrower, but the attenuation
of the stop band (the height of the second lobe) stays the same.

But when we increase the order (the number of moving average filters cascaded), the attenuation of thejG
stop band increase accordingly.

Can we use just cascaded moving average filters for our factor 64 decimation example? Not at all!
Even when 4 filters are cascaded, the stop band attenuation is only -66dB. And if we want
to downsample by a factor of 64 and use a filter length of 64, the passband attenuation at 
0.01 of the normalized frequency (which corresponds to 15.36kHz of our example) is already
around -33.7! 

![Box Filter Passband](/assets/pdm/moving_average_filter_passband.svg)

With these terrible characteristics, are moving average filters even worth doing?

The answer is yes!

While the 64-length filter has that terrible pass band attenuation of -33.7dB, the attenuation of 16-length 
version of that 4th order filter at the same 0.01 is only -1.8dB. For high quality audio, the pass band
ripple should only be around 0.2dB, so -1.8dB is still way too high. 




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


