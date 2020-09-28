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

When these filters are used for decimation (downsampling) and interpolation (upsampling), they are even 
easier than you'd think they would be.

# Moving Average Filter: from Trivial Implementation to Cascaded Integrator Comb (CIC) Configuration

In 1980, Eugene Hogenauer published a [seminal paper](http://read.pudn.com/downloads163/ebook/744947/123.pdf) 
about how to implement cascaded moving average filters for decimation and interpolation purposes. These
filters are now known as CIC filters (short for Cascaded Integrator Comb filters).
The paper is surprisingly readable, but still contains a decent amount of math and formulas. Let's take 
things step by step here.

The most naive and trivial moving averaging filter implementation is a literal translation
of the summing math into hardware. For a length 4, it'd look like this:

![Moving Average Filter - Trivial Implementation](/assets/pdm/moving_average_filters_trivial.svg)

The implementation above averages 4 samples, requires 3 delay elements and 3 adders. The initial
division by 4 is to ensure that the filter has a unity gain. I will drop that factor going forward, just
imagine that it's there.

As expected, there are no multipliers in this design, but the 3 adders are bit difficult to accept,
especially since that number will go up for moving average filters of a longer length.

Can we do better? Of course! There is a bunch of math that stays the same from one sample to the next.

Let's look at the math below:

```
y(3) =               x(3) + x(2) + x(1) + x(0)
y(4) =        x(4) + x(3) + x(2) + x(1)
y(4) = y(3) + x(4)                      - x(0)
```

or in general:

```
y(n) = y(n-1) + x(n) - x(n-4)
```

The simple sum has been transformed into a recursive operation. In hardware, that looks like this:

![Moving Average Filter - Comb Integrator Version](/assets/pdm/moving_average_filters-comb_integrator_version.svg)

We have added 2 delay registers, a subtractor, but have saved a whole lot of adders. And these 2 delay
registers are a one-time cost for converting to a recursive configuration: if we increase
the summing length from 4 to 8, we'll only add 4 more registers to the delay line and nothing else! (But as
we shall see below, it will get even better!)

The section with the delay and the subtactor is called a "comb", the recursive part that feeds back
the previous output is called the "integrator".

It's slightly less intuitive, but you can swap the interpolator and the comb sections and get the same
calculated result. In this case, instead of having a recursive output, you continuously accumulate x, 
and subtract that accumulation later.

![Moving Average Filter - Integrator Comb Version](/assets/pdm/moving_average_filters-integrator_comb_version.svg)

Accumulate *x*:

```
a(n) = x(n) + a(n-1)
```

And let's define the output as:
```
y(n) = a(n) - a(n-4)
```

The output *y* is still the sum of the last 4 inputs:

```
y(n) = a(n) - a(n-4)
y(n) = x(n) + a(n-1) - a(n-4)
y(n) = x(n) + x(n-1) + a(n-2) - a(n-4)
y(n) = x(n) + x(n-1) + x(n-2) + a(n-3) - a(n-4)
y(n) = x(n) + x(n-1) + x(n-2) + x(n-3) + a(n-4) - a(n-4)
y(n) = x(n) + x(n-1) + x(n-2) + x(n-3) 
```

If you were really paying attention, you might have noticed that continously accumulating *x* into *a* will 
eventually result in overflowing *a*. However, as long as the delay registers have enough bits, the
comb section will automatically counteract this overflow: you'll still get the right result!

You can increase the attenuation by cascading multiple moving average filters:

![Moving Average Filter - Cascaded Combs Integrators](/assets/pdm/moving_average_filters-cascaded_integrators_and_combs.svg)

You can even rearrange the integrators and combs and group them together:

![Moving Average Filter - Rearranged Integrators and Combs](/assets/pdm/moving_average_filters-rearranged_integrators_combs.svg)


Now look back and notice how the integrator always has exactly 1 delay register, while the comb has
as many delays as the number of samples of the moving average. If you need a length of, say, 64, that's
still a lot of delay registers.

But remember that these kind of filters are primarily used for decimation and interpolation. 

Let's focus on decimation: if we decimate by a factor 4, we simply retain one output sample out of every 4
input samples.

In the example below, the downsampler at the right drops those 3 samples out of 4:

![Moving Average Filter - Decimation Trivial](/assets/pdm/moving_average_filters-decimation_trivial.svg)

But now comes the magic: we can move that downsampler from the end of the pipeline to the middle, right
between the integrator stage and the comb stage. To keep the math working, we also need divide the number
of delay elements in the comb stage by the decimation number:

![Moving Average Filter - Decimation Smart](/assets/pdm/moving_average_filters-decimation_smart.svg)


The end result is beautiful: 

**When used as part of a decimator, the moving average filter that started out as a design 
with *(n-1)* delay stages and *(n-1)* adders has been reduced to 2 delay stages, 1 adder, and 1 subtractor, as long as
the decimation ratio is the same as the length of the desired moving average filter.**

The math is trivial. 

We still continously add all new values of *x* to *a*, but instead of using and delaying every *a* value in the comb stage, 
we only use and delay every 4th *a* value:

```
a(3) = x(3) + x(2) + x(1) + x(0) + <previous values>
a(7) = x(7) + x(6) + x(5) + x(4) + x(3) + x(2) + x(1) + x(0) + <previous values>
```

And *y* subtracts the current *a* value from the one that was delayed:

```
y(7) = a(7) - a(3)
y(7) = x(7) + x(6) + x(5) + x(4)
```

# A Moving Average Filter as Decimator

We now know why moving average filters are so popular for decimation (and interpolation as well): their
CIC implementation requires almost no resources, irrespective of the decimation ratio!

However, it's not all roses: the negatives of moving average filters that were mentioned earlier, 
poor stopband attenuation and non-flat passband attenuation, didn't magically disappear. In fact,
they actually got worse: in a decimation CIC filter, the length of the moving average filter is directly
linked to decimation ratio. In most cases, that ratio is 1. Because of this, the only way to 
influence the attenuation of the stopband is by increasing the number of cascaded interpolator and
comb banks, but that, in turn, also has an impact on the pass band. 

Let's look here at 5th order CIC filter with a filter length of 4. The sample frequency is 80kHz, which
means that the incoming signal has a bandwidth from 0 to 40kHz.

![CIC Response before decimation](/assets/pdm/cic_decimation_full_range.svg)

The filter length of 4 gives a 2 lobes. Under normal circumstances, you'd say that this filter has a stopband 
attenuation of 56.77dB. However, since the decimation ratio of a CIC filter is linked to the filter length, the 
decimation ratio is 4 as well.

The output sample rate of our decimating filter will be 20kHz, and the bandwidth of the outgoing signal will
be from 0 to 10kHz.

After decimation, the signal components with a frequency that are higher than that of the outgoing signal will
alias into the frequency range of the main signals.

In the graph above, this means that the remaining signal components of the orange, the green and the red curve will
be alias under the blue curve. 

![CIC Response after decimation](/assets/pdm/cic_decimation_aliased.svg)

The blue curve is the true signal with a 10kHz bandwidth. The remaining curves are distorting the true signal. 

Forget about a stopband attenuation of 56.77dB: the real stopband attenuation of this filter is 18.49dB! And
the passband attenuation is flat either: it varies between 0 and -18.49dB as well.

If a decimating CIC filter by itself is so terrible, why, then, is it so popular?

**Because a decimating CIC filter is always used as part of a multi-stage decimation configuration!**

Nobody would use a 4x decimating CIC filter to extract a 10kHz BW output signal from a 40kHz BW input signal: the CIC
filter is just used as a first step to reduce sample rate from some high number to a lower number. And then
one or more traditional FIR filters are used to bring the sample rate to the desired output rate.

If our real signal of interest lies in the 0 to 2000Hz range, the CIC filter has reduced the aliasing of all
the signal components above 10kHz by more than 90dB, and the passband attenuation is only 0.7dB!

![CIC Response at lower frequencies](/assets/pdm/cic_decimation_lower_freqs.svg)

All that's needed now is one or two filters with a clean passband behavior from 0 to 2000Hz and with a stop band from, 
say, 3000Hz to 10000Hz. That is much less computationally intensive that a filter with the same passband
and with a stop band that ranges from 3000Hz to 40000kHz!

For example: if we wanted to use a Blackman windowed-sinc FIR with a cutoff frequences of 2500Hz, transition bandwidth of 1000Hz
and a stopband attenuation of 74dB, a sample rate of 80000Hz would require 369 coefficients. A sample rate of 20000Hz reduces that
number to only 93 coefficient. And this is for a decimation rate of only 4. In audio applications, the sample rate of
a PDM microphone often needs to be reduced from 3.072MHz to 48kHz, a ratio of 64. A CIC filter that reduces that
ratio from 64 to, say, 4, will go a long way in making the size of the FIR filter manageable.




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

* [An Economical Class of Digital Filters For Decimation and Interpolation](http://read.pudn.com/downloads163/ebook/744947/123.pdf)

    Hogenauer's original paper about CIC filters.

* [A Beginner's Guide To Cascaded Integrator-Comb (CIC) Filters](https://www.dsprelated.com/showarticle/1337.php)

    Excellent introduction to CIC filters with a tiny bit more of math.


* [Rick Lyons - Optimizing the Half-band Filters in Multistage Decimation and Interpolation](https://www.dsprelated.com/showarticle/903.php)

    Talks about how it may not be ideal to have 3 identical cascaded 2x half-band filters when
    you want to be decimate by 8. Unfortunately, it only does so qualitatively, not quantitatively.


## Filter Tools

* [FIIIR1](https://fiiir.com)

* [LeventOztruk.com](https://leventozturk.com/engineering/filter_design/)


