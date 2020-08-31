---
layout: post
title: PDM Microphones
date:  2020-08-29 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

I've been playing around with PDM MEMS microphones lately. They're tiny little things that are primarily used
in cell phones.

Instead of sending out the audio signal as PCM over an I2S interface, they use 1-bit pulse density modulation (PDM).

Over the past months, I've been reading on and off about different aspects of this: how PDM works, the signal
theory behind it, how to convert the data to PCM etc.

Let's be clear about it right from the start: I didn't know anything about this before reading about it, so I'm
about the opposite of an expert on any of this. If you're serious about learning about PDM signal processing
in depth, there are tons of interesting articles on the web.

I'm primarily writing everything here down for myself so that I remember the most important points that made things
understandable for me. 

# PDM Microphones

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
increasing the SNR. For the example here, that point is right around here: the maximum SNR
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

The most important things to remember about PDM microphones and sigma-delta convertors are that: 

* they use oversampling to trade off bits for clock speed
* they push the quantization noise into the frequency range above the bandwidth of the sampled
  signal of interest.
* the rate at which the noise increases with frequency depends on the order of the sigma-delta
  convertor.





The rate by which the noise goes up above 20kHz depends on the order of the sigma-delta convertor:
the higher order, the steeper the noise curve. However, also the higher order, but better noise
is pushed from the band of interest to the upper frequency regions.

Since the noise in the upper frequency regions is easy to filter, higher order sigma delta convertors
are better. In practise most contemporary PDM microphones use 4th order convertors, since higher
order convertors can have their own issues with stability.

Jypiter worksheet with delta-sigma modulator:

https://nbviewer.jupyter.org/github/ggventurini/python-deltasigma/blob/master/examples/dsdemo2.ipynb



