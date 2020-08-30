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
the original signal. That's why most audio is sampled at 44.1 or 48kHz.

The number of bits at which the audio signal is sampled determines how closesly the sampled signal matches
the real signal. The delta between sampled and real signal is the quantization noise. For a certain number
of bits N, the signal to noise ratio follows the formula: SNR = 6.02 * N + XXX.

It is, however, possible to trade off the number of bits for clock speed. In the case of PDM microphones, 
the signal is usuall sampled at 64 times the traditional sample rate, or 48kHz * 64 = 3.072 MHz.

PDM microphones use so-called sigma delta A/D convertors that continously toggle between -1 and 1 to approximate
the original signal, while continuoulsly keeping track off the error between the output and the real value.

At the output, the PDM microphone encodes -1 as 0 and 1 as, well, 1. The average ratio of 0 and 1, the density,
represents the original analog value.

Sigma-delta convertors are complex beast. The Wikipedia article goes into a decent amount of intuitive detail
without going totally overboard on theory. 

The most important things to remember are that: 

* they use oversampling to trade off bits for clock speed

    As mentioned before PDM microphones typically have a 64x oversampling ratio

* they exhibit noise shaping 

    the noise that is introduced by having only 1 bit is such that it pushed to the frequency
    range above the bandwidth of the signal of interested.

For example, in a typical 20kHz PDM microphone, the signal to noise ratio will be >100dB in the
range between 0 and 20kHz. But once you go above 20kHz, the noise will steadily go up and 
eventually completely drown out the frequencies in the frequency band of interest.

The rate by which the noise goes up above 20kHz depends on the order of the sigma-delta convertor:
the higher order, the steeper the noise curve. However, also the higher order, but better noise
is pushed from the band of interest to the upper frequency regions.

Since the noise in the upper frequency regions is easy to filter, higher order sigma delta convertors
are better. In practise most contemporary PDM microphones use 4th order convertors, since higher
order convertors can have their own issues with stability.

Jypiter worksheet with delta-sigma modulator:

https://nbviewer.jupyter.org/github/ggventurini/python-deltasigma/blob/master/examples/dsdemo2.ipynb



