---
layout: post
title: High Efficiency Filters through Decimation and Interpolation
date:   2026-09-23 00:00:00 -1000
categories:
---

<script async src="https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-AMS_CHTML"></script>


* TOC
{:toc}

# Introduction

I continue my quest to deconstruct fred harris' 
[Recent Interesting and Useful Enhancements of Polyphase Filter Banks](https://www.youtube.com/watch?v=afU9f5MuXr8)
lecture. The goal is to understand every last detail, with some additional side quests 
thrown when I feel like it.

In this blog post, I'm looking at
[his case of a narrow filter](https://youtu.be/afU9f5MuXr8?t=2949) 
with equal input and output sample rate.

[![harris presentation slide: polyphase + halfband decimation](/assets/polyphase/efficient_filter/harris_prezo_slide_1.jpg)](/assets/polyphase/efficient_filter/harris_prezo_slide_1.jpg)
*(Click to enlarge)*

# Estimation of the Number of FIR Filter Taps

The number of filter taps for a given specification depends on a number of parameters:

* sample rate $$f_s$$
* the filter transition bandwidth $$\Delta f$$
* stopband attenuation $$A_s$$ in dB
* passband ripple $$A_p$$ in dB

But that's not all: the passband ripple and stopband attenuation are only limits, the behavior
within these bands can be very different and is dependent on how the filter coefficients
were chosen. 

For the same requirements, an equiripple filter that was designed with the Remez/Parks-McClellan 
method will need a low number of coefficients than one that is designed with the least squares method.

XXXX Example XXX

Unless explicitly stated otherwise, assume that equiripple filters are used.

# Bellanger's Approximation

When evaluating different multi-rate filter architectures, the number of filter taps is one of 
the most important factors. The exact number can be obtained with a binary search, run 
the Remez algorithm with a different number of taps until requirements are met, but that's slow 
and usually overkill. 

In [Digital Processing of Signals: Theory and Practice](https://www.amazon.com/dp/0471921017), 
Maurice Bellanger came up with a simpler formula that's empirically derived by creating hundreds
filter with the Remez method. It's now called Bellanger's approximation:

$$ N \approx \frac{-2 \log_{10} ( 10 \delta_p \delta_s) }{ 3 ( \frac{ \Delta f } { f_s }) } - 1 $$

In this equation, $$ \delta_p $$ and $$ \delta_s $$ are the linear passband ripple and stopband 
attenuation respectively.

I have no intuition for linear ripple and attenuation values, so let's convert this formula to one
that uses decibels. You must be careful to use the right formulas for $$ \delta_p $$ and $$ \delta_s $$. 

Stopband attenuation compares the maximum power level in the stopband to unity:

$$ A_s = -20 \log_{10} (\delta_s) $$

$$ \delta_s = 10^{- \frac{ A_s }{ 20 }} $$

Passband ripple compares the peak-to-peak deviation around the unit gain:

$$ A_p = 20 \log_{10} ( \frac{ 1 + \delta_p }{ 1 - \delta_p } ) $$

$$ \delta_p = \frac { 10^{ \frac{ A_p }{ 20 } } - 1 } { 10^{ \frac{ A_p }{ 20 } } + 1 } $$

For small passband ripples, $$ \ln(1 + x) \approx x $$, and you can use this:

$$ A_p = 20 \log_{10}(1 + \delta_p) - 20 \log_{10}(1 - \delta_p) $$

$$ A_p \approx \frac{40}{ \ln(10) } \delta_p $$

$$ A_p \approx 17.372 \cdot \delta_p $$

and

$$ \delta_p \approx 0.0576 \cdot A_p $$

It takes a bit of reordering, but with those 2 formulas, Bellanger's approximation reduces to:

$$ N \approx \frac{ A_s - 20 \log_{10}( A_p ) + 4.78 }{ 30 ( \frac{ \Delta f}{ f_s } ) } - 1 $$


# Harris Rule of Thumb

A [key observation](https://youtu.be/afU9f5MuXr8?t=2499) about FIR filter design is that, reduced
to the absolute minimum,  the complexity[^filter_complexity] of the filter depends on 3 parameters:

[^filter_complexity]: In this blog post series, the first order indicator for filter complexity 
                      is always the number of multiplications.

* sample rate $$f_s$$
* the filter transition bandwidth $$\Delta f$$
* stopband attenuation $$A_s$$ in dB

The number of filter taps can be estimated with the Harris Rule of Thumb:

$$ N \approx \frac{f_s}{\Delta f} \frac{A_s}{22} $$

*In his YouTube lecture, he uses a divisor of 20 instead of 22 to make back of the envelope
calcutation even easier.*

Of those 3 parameters, stopband attenuation $$A_s$$ is usually a fixed design parameter
that we can't do anything about. Similarly, modern communication systems often have independent
channels packed tightly against each other with only a narrow transition band between
them, so $$\Delta f$$ is a fixed system parameter as well. And since $$\Delta f$$ is
part of the divisor, narrow transition bands tend to blow up the number of filter taps.

This leaves the sample rate $$f_s$$ as the parameter of choice to keep the number of 
filter taps in check.

One would expect passband ripple to be part of the Harris Rule of Thumb, but unless those 
requirements are stringent, stopband attenuation is the dominating factor. Harris implicitly
assume a passband ripple of around 0.1 dB.


When you start cascading multiple filters, the overall passband ripple is the multiplication 
of the passband ripple of individual filter stages. When specified in dB, that multiplication
becomes an addition. With enough stages or you demand a much lower ripple than 0.1 dB, the passband 
ripple becomes a factor. For those cases, you can use Bellanger's approximation:

$$ N \approx \frac{-2 \log_{10} ( 10 \delta_p \delta_s) }{ 3 ( \frac{ \Delta f } { f_s }) } - 1 $$


# A Naive Low Pass Filter

Let's look at the example problem that harris wants to solve:

* a low-pass filter
* input sample rate $$f_s$$ = 4 MHz
* double-sided bandwidth of the signal of interest $$\text{BW}$$ = 40 kHz
* transition bandwidth $$\Delta f$$ = 40 kHz
* stopband attenuation $$\text{A_s}$$ = 80 dB

If we fill in these numbers in his formula, we get:

$$ N = \frac{4000}{40} \frac{80}{20} = 400 $$

At 4 MHz, that's 1.6 G multiplications per second.

That's way too much but it's also overkill: since bandwidth of the signal of interest is only
40 kHz, it makes no sense keep the sample rate at 4 MHz. We can fix that by decimating the signal.

# Discussion

There are in my opinion a bunch of issues with the harris example:

* The input sample rate of 4 MHz is way too low. There is no need to use an FIR filter in
  a polyphase form. 
* He chooses a decimation factor of 50. While that is the lowest possible factor for a
  40 kHz bandwidth and 40 kHz transition band, it's far from optimal in terms of achieving
  the lowest possible number of multiplications. A decimation factor of 
  48 ($$ 3 \cdot 2^4$$) allows a architecture of 4 decimated-by-2 halfband filters followed
  by a decimate by 3 FIR filter. A few CIC filter might even have been possible.
* In this lecture, harris consistently compares his results against a theoretical worst case 
  filter complexity, where you calculate all samples in full and then perform a decimation.
  That is fine, but doing so makes late optimization seem insignificant. When you reduce
  1.6G operations to 32 M operations, a further reduction to 24 M operations seems trivial, but
  it's not if 32 M was the original baseline.

# Minimal Sample Rate Requirement for a Filtered Signal

We first need to answer the question how high of a decimation factor we can use without
corrupting low-pass filtered signal. When performing decimation, the spectrum above the ouput sample 
rate folds back onto the remaining spectrum. The low pass filter makes sure that this spectrum has 
been sufficiently attenuated, so only need to make sure that transition band frequencies don't
fold into the pass band frequency.

For that, we need a minimum sample rate 

$$f_s >= \text{BW} + \Delta f_s$$

In our example, that means: 

$$f_s >= 40 \text{kHz} + 40 \text{kHz} = 80 \text{kHz}$$

With an input sample rate of 4 MHz, this mean we can decimate by a factor of up to 50.

# Using a Decimating/Interpolating Polyphase Filter

As discussed in [Notes about Basic Polyphase Decimation Filters](/2026/01/25/Notes-on-Basic-Polyphase-Decimation.html),
an FIR filter that is followed by a decimator can be converted into a polyphase filter. The total number
of filter taps is still 400, but due to the reduction in sample rate, the number of multiplication per second
has gone by a factor of 50: 32 M multiplications per second.

This is nothing new. But harris now adds a new design requirement: 

* the output sample rate must remain 4 MHz.

To make that happen, the 80 kHz signal is interpolated back up to by a factor of 50 with
a second polyphase filter:


This doubles the number of multiplications per second from 32 M to 64 M, which is
still 25 times lower than the original 1.6 G.

# Tightening the Transition Band

If we reduce the transition band from 40 kHz to 4 kHz, the number of filter taps increases by
a factor of 10 to:

$$ N = \frac{4000}{4} \frac{80}{20} = 4000 $$

That's 16G multiplications per second for the naive implemention.

Using the same game as before, the minimum sample rate is:

$$f_s >= 40 \text{kHz} + 4 \text{kHz} = 44 \text{kHz} $$

which gives us a maximum decimation ratio of:

$$D = \frac{4000}{44} = 90 $$

The number of multiplications per second would be $$ N \cdot f_s = 176\text{M} $$, and
352 M for a 4 MHz output sample rate.

But there's an alternative: we can retain the earlier solution that uses the 40 KHz
transition band and insert additional low pass filter with a 4 kHz transition band.
This filter uses an 80 kHz sample rate, so the number of taps is just:

$$ N_{2} = \frac{80}{4} \frac{80}{20} = 80 $$

80 taps at an 80 kHz clock rate gives 6.4M multiplication per second that must be added to
the previous number of 64 M, for a total of 70.4 M, much smaller than the 352 M of the
straight decimator/interpolator.

# Old School

6 years ago, I wrote 
[Design of a Multi-Stage PDM to PCM Decimation Pipeline](/2020/12/20/Design-of-a-Multi-Stage-PDM-to-PCM-Decimation-Pipeline.html).
If I'd apply the teachings of that blog post to the problem above, I'd approach the
solution as follows:

* instead of a double-sided bandwidth 40 kHz, I'd use a passband frequency of 20 kHz.
* 





# References

* [Youtube - Recent Interesting and Useful Enhancements of Polyphase Filter Banks: fred harris](https://www.youtube.com/watch?v=afU9f5MuXr8)

* [Stackexchange - Understanding Polyphase Filter Banks](https://dsp.stackexchange.com/questions/96042/understanding-polyphase-filter-banks)

* [Analysis Channelizers with Even and Odd Indexed Bin Centers - fred harris](https://www.dsponlineconference.com/WPMC_2020_Even_and_Odd_Bin%20Centers_5.pdf)

* [IEEE - Digital Receivers and Transmitters Using Polyphase Filter Banks for Wireless Communications](https://ieeexplore.ieee.org/document/1193158)

* [Stackexachange: How many taps does an FIR filter need?](https://dsp.stackexchange.com/questions/31066/how-many-taps-does-an-fir-filter-need)

**Other blog posts in this series**


* [Notes about Basic Polyphase Decimation Filters](/2026/01/25/Notes-on-Basic-Polyphase-Decimation.html)
* [Complex Heterodynes Explained](/2026/02/07/Complex-Heterodyne.html)
* [The Stunning Efficiency and Beauty of the Polyphase Channelizer](/2026/02/16/Polyphase-Channelizer.html)
* [Polyphase Channelizers with Frequency Offset - a Bluetooth LE Example](/2026/03/05/Polyphase-Channelizer-with-Offset.html)

**Source code**

* [GitHub - Polyphase Filtering Blog Series](https://github.com/tomverbeure/polyphase_blog_series)

# Footnotes


