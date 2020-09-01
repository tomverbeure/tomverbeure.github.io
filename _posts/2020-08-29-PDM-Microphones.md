---
layout: post
title: PDM Microphones
date:  2020-08-29 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

I've been playing around with PDM MEMS microphones lately. Due to their small size, low cost, and still decent
quality, they are primarily used in cell phones. 

On Digikey, the cheapest ones are around $1. Or you can buy [a breakout board on Adafruit](https://www.adafruit.com/product/3492) 
for $5:

![Adafruit PDM MEMS Microphone](/assets/pdm/adafruit-pdm-mems-microphone.jpg)

Instead of sending out the audio signal in PCM format over an I2S interface, they use 1-bit pulse density modulation (PDM).

Over the past months, I've been reading on and off about different aspects of this: how PDM works, the signal
theory behind it, how to convert the data to PCM etc.

In this blog post, I'm writing down a summary of the things that I found. Rather than focussing on the math behind it,
I'm looking at this from an intuitive angle: I'll forget the math anyway, and there are plenty of articles online where you 
can look up the details if it's necessary.

Just to avoid misunderstandings: I didn't know anything about this before reading about it, so I'm about the opposite of 
an expert on any of this. If you're serious about learning about PDM signal processing in depth, this blog post is not for you.
I will include a list of references that may point you in the right direction.

# PDM MEMS Microphones

Humans are able to hear audio in a range from 20 to 20000Hz (though the upper range is very age dependent.)
Digital signal theory dictates that audio needs to be sampled at twice the bandwidth to accurately reproduce
the original signal. That's why most audio is recorded at 44.1 or 48kHz.

The number of bits at which the audio signal is sampled determines how closesly the sampled signal matches
the real signal. The delta between sampled and real signal is the quantization noise. For a certain number
of bits N, the signal to noise ratio follows the formula: SNR = 6.02 * N + XXX.

It is, however, possible to trade off the number of bits for clock speed. In the case of PDM microphones, 
the signal is usuall sampled at 64 times the traditional sample rate, or 48kHz * 64 = 3.072 MHz.

# From Analog Signal to PDM with a Sigma-Delta Convertor

PDM microphones use so-called sigma-delta A/D convertors that continuously toggle between -1 and 1 to approximate
the original signal, while feeding back the cumulative errors between the 1-bit output and the real input value.

The ratio of the number of -1's and 1's, the pulse density, represents the original analog value.

Here's an example of a PCM sine wave that's converted to PDM with a first order, 16x oversampling sigma-delta convertor:

![Sigma-Delta Sine Wave](/assets/pdm/sinewave_to_pdm.svg)

At the peak of the sine wave, the green output consists of primarily ones, while at the trough, the output
is primarily minus ones.

PDM microphone encodes -1 as a logic 0 and 1 as a logic 1.

Jerry Ellsworth has [great video](https://www.youtube.com/watch?v=DTCtx9eNHXE) that shows how to build a 
sigma-delta A/D convertor yourself with just 1 FF and a few capacitors and resistors.

Sigma-delta convertors are complex beasts. The [Wikipedia article](https://en.wikipedia.org/wiki/Delta-sigma_modulation)
goes into a decent amount of intuitive detail without going totally overboard on theory. 

When you reduce the number of output bits of an A/D convertor, increasing the oversampling rate doesn't
automatically reduce quantization noise. In fact, the noise is inevitable! However, if you can
push the frequency component of that noise to a range that's outside of the freqency range of the
original input signal, then it's easy later on to recover the original signal by using a
low pass filter.

It turns out that this is exactly what happens in a sigma-delta convertor! 

We can see this in the power spectral density of the PDM signal above:

![Sigma-Delta Sine Wave PSD](/assets/pdm/sinewave_pdm_psd.svg)

The bandwidth of the signal that we're interested in lays on the left size of the green dotted line. That's
where we see the main spike: this is our sine wave. Everything else is noise.

We can also see that the bandwidth of our signal is 1/16th of the total bandwith. With a perfect
low pass filter, we could remove all the noise to the right of the green line, after which we'd end
up with a SNR of 35dB. 

(Note that the input signal has an amplitude of 0.5. Increasing the amplitude
would increase the SNR of this case a little bit, but soon you run into limitations of sigma-delta
convertors that prevent you from using the full input range.)

# Higher Order Sigma Delta Convertors

A SNR of 35dB is far from stellar (it's terrible), but keep in mind that we're using a very simple 
*first order* sigma-delta convertor here. Remember how I wrote earlier that there is an error feedback
mechanism that keeps track of the difference in error between output and input? Well, it turns out that you 
can have multiple nested error feedback mechanism. If you have 2 feedback loops, you have a *second order*
convertor etc.

Let's see what happens when we use higher order convertors on our sine wave:

![Sigma-Delta Sine Waves with higher order convertors](/assets/pdm/sinewave_to_pdm_different_orders.svg)

Do you notice the difference between the different orders? Neither do I! There's no obvious
way to tell apart the PDM output of a first and a 4th order sigma-delta convertor.

But let's have a look if there were any changes in the frequency domain:

![Sigma-Delta PSD with higher order convertors](/assets/pdm/sinewave_pdm_psd_different_orders.svg)


Nice! Despite the constant oversampling rate of 16, the SNR increased from 35dB to 50.2dB!

Higher order sigma delta convertors are significantly more complex and at some point they become
difficult to keep stable. Most contemporary PDM microphones use a 4th order sigma-delta convertors.

For a given oversampling rate, there's a point where increasing the order of the convertor stops
increasing the SNR. For this example, that point is right around here: the maximum SNR
was 51dB.

# Increasing the Oversampling Rate

50dB is better than 35dB, but it's still far away from the 96dB (and up) that one expects from high-end
audio.

Luckily, we have a second parameter in our pocket to play with: oversampling rate.

Until now, I've used an oversampling rate of 16x because it makes it easier to see the frequency
range of the input signal in the frequency plot. But let's see what happens when we increase
oversampling rate of the 4th order convertor from 16 to 32 to 64:

![Sigma-Delta Sine Waves with higher oversampling rate](/assets/pdm/sinewave_to_pdm_different_osr.svg)

This time, the effect on the PDM is immediately obvious in the time domain.

And here's what happens in the frequency domain:

![Sigma-Delta PSD with higher oversampling rate](/assets/pdm/sinewave_pdm_psd_different_osr.svg)

WOW!!! Now we're talking!

An oversampling rate of 64 and a 4th order sigma-delta convertor seems to be do the trick.

And that's exactly what today's PDM microphones support.

Notice how the green vertical line shifts to the right as the oversampling rate increases.
This is, of course, expected: we are doubling the sampling rate with each step while bandwidth of
our input signal stays the same. 


# SNR Slope Depends on Sigma Delta Order

We've seen how higher order sigma-delta convertors have a much lower noise floor in the frequency
range of the sampled signal, but we overlooked that the noise increases much faster for higher
order convertors once the frequency is to the right of the green dotted line.

Here's a graph that makes this more obvious:

![Noise slope for different orders](/assets/pdm/noise_slope_different_orders.svg)

For clarity, I only show the normalized frequency range up to 0.1 instead of 0.5.

As we saw before, on the left of the green line, the noise SNR is lower for higher order convertors, but
on the right side, the SNR for higher order convertors is soon higher than for the
lower order convertors!

In other words: the slope of the SNR curve is steeper for higher order convertors.

This will be important later when we need to design a low pass filter to remove all higher
frequencies when converting back from PDM to PCM format: the low pass filter needs to be 
steeper for higher order sigma-delta convertors.

# PDM and Sigma-Delta Convertors Summary

The most important things to remember about PDM microphones and their sigma-delta convertors are that: 

* they use oversampling to trade off bits for clock speed
* they push the quantization noise into the frequency range above the bandwidth of the sampled
  signal of interest.
* the rate at which the noise increases with frequency depends on the order of the sigma-delta
  convertor.

# The Road from PDM to PCM

We now know the characteristics of PDM-encoded audio signal. 

What do we need to do to convert it to a traditional PCM code stream of samples?

There are 2 basic components:

* send the PDM signal through a low pass filter 

    This increases the number of bits per sample back to a PCM value. It also
    removes all the higher order noise.

* decimate the samples back to a lower sample rate

# The Basics of Decimation

In digital signal processing, decimation is the steps of removing N-1 number of samples for every
N samples. It's really as simple as that: you simply throw away the samples!

If you start with signal that has a bandwidth of 1.536 MHz and you decimate by a factor of 64, 
you end up with a bandwidth of 24kHz. These numbers weren't chose at random: they're bandwidths
that you get when you convert the output of a PDM microphone that is clocked at 3.072 MHz down
to a sample rate of 48 kHz.

There is one major caveat however: during that act of decimation, the signal contents in frequency 
range that gets removed doesn't just magically disappear, it folds back onto the remaining 
frequency range!

This makes total sense, because it's exactly same as the aliasing effect that happens when you
undersample a signal.

Here's a simple example in PCM format with 3 sine waves at 0.01, 0.1 and 0.28 of the normalized sampling rate.
In the second and third graph, we've decimate the signal by 2 and by 4. 

![Decimation without Filtering - 3 Sine Waves](/assets/pdm/decimation_without_filtering_regular.svg)

You can see how the sine waves at frequencies 0.01 and 0.1 stay in place, but after decimating
by 2, the one at 0.28 has moved to 0.23. And after decimating by 4, the
signal at 0.28 is now at 0.03.

It's clear that decimation without low pass filtering results in major aliasing!

If, just for fun, we made the worlds dumbest PDM sample rate downconvertor by just throwing out 
1-bit samples, we'd get something like this:

![Decimation without Filtering](/assets/pdm/decimation_without_filtering.svg)

Starting with a beautiful 102 dB, our SNR drops down to 10 dB after removing every other sample, 
and down to 4.6 dB after doing that again. Forget about a 48 kHz sample rate, even after going
down from 3.072 MHz down to 768kHz, our signal has already entry disappeared.

After the first step, the noise that's present in the original frequence range form 0.25 to 0.5 was folded onto
the range from 0 to 0.25, drowning out the original signal.

# Best Case Low Pass Filtering

It should be abundantly clear now that we need that low pass filter before we can decimate to
a lower sample rate.

Let's use the following parameters:

* Original sample rate: 3.072 MHz
* Oversample rate factor: 64
* Desired sample rate: 48 kHz
* Original signal bandwidth: 20 kHz
* Desired pass band: 0 dB
* Desired stop band: 96 dB

I chose 96 dB because that's the theoretical maximum SNR for 16-bit audio. Most PDM microphones only
have an SNR in the low sixties, so this is overly aggressive, but let's just see what we can do.

The transition from pass band to stop band will start at 20 kHz. And if we look at the graph for
a 64x oversampling, 4th order sigma-delta convertor, we see that the noise goes above 96 dB 

Since the noise starts going up immediately above 24 kHz (=48/2), we have 4 kHz to construct a filter
that goes from a pass band to the stop band. 

# FIR Filters for Decimation 

Since we're throwing away N-1 out N samples when decimating by factor N, the decimation filter doesn't
need to calculate a filter value for each incoming sample when we're using an FIR filter: it's
sufficient to calculate the output only every N samples. Since we're down


# Box Averaging Filters

As we noticed earlier: typical FIR filters require a multiplication per filter tap. Larger FPGAs
have a decent set of HW multipliers, but even then, setting up an efficient FIR structure can be
a hassle.

The multipliers are there to ensure that the filter has the right pass band, transition band, and
stop band characteristics.

But what if we just ignore some of those characteristics with the explicit goal to get rid of this
kind of mathematical complexity?

The simplest filter, then, is the box filter or moving averaging filter: it sums the last N samples,
divides the result by N and... that's it!

A box averaging filter probably one of the most common filters in digital signal processing: it's
super simple to understand and implement, and it's also an optimal filter for white noise reduction. That's
white noise doesn't have a preference to impact this sample or the other, it affects any sample
with equal chance. Because of that, there's no way you can tune this or that coefficient of the
filter coefficients in some preferential way.

Unfortunately, box filters have some major disadvantages as well: they have a very slow roll-off
from the pass band to the stop band, and the stop band attentuation is very low as well.

But one way to overcome that is by cascading multiple filters after each other.

So there are 2 parameters to play with: the size of the box (the number of samples that are averaged
together) and the number of filters that are cascaded.

Here's how that looks in terms of filter response:

![Box Filter Response](/assets/pdm/box_filter_overview.svg)

As we increase the length of the box filter, the band pass gets narrower, but the attenuation
of the stop band (the height of the second lobe) stays the same.

But when we increase the order (the number of box filters cascaded), the attenuation of the
stop band increase accordingly.

Can we use just cascaded box filters for our factor 64 decimation example? Not really:
even when 4 box filters are cascaded, the 



# References

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


